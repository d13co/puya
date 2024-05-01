from __future__ import annotations

import abc
import typing
from collections.abc import Callable, Iterable, Mapping, Sequence
from functools import cached_property

import attrs
from immutabledict import immutabledict

from puya import log
from puya.awst import wtypes
from puya.awst_build import constants
from puya.errors import CodeError, InternalError
from puya.parse import SourceLocation
from puya.utils import lazy_setdefault

logger = log.get_logger(__name__)


@attrs.frozen(kw_only=True)
class PyType(abc.ABC):
    name: str
    """The fully qualified type name"""
    alias: str
    """The short name, for display purposes"""

    @property
    @abc.abstractmethod
    def wtype(self) -> wtypes.WType | None:
        """The WType that this type represents, if any."""

    def register(self) -> None:
        existing_entry = _type_registry.get(self.name)
        if existing_entry is None:
            _type_registry[self.name] = self
        elif existing_entry is self:
            logger.debug(f"Duplicate registration of {self}")
        else:
            raise InternalError(f"Duplicate mapping of {self.name}")

    @classmethod
    def from_name(cls, name: str) -> PyType | None:
        return _type_registry.get(name)


# Registry used for lookups from mypy types.
# Would be nice to make it a PyType class-var, but needs to be Final
# for mypy, and Final with an initialiser isn't picked up as a ClassVar by attrs yet,
# and ClassVar[Final[...]] is forbidden by the typing spec
_type_registry: typing.Final = dict[str, PyType]()

# https://typing.readthedocs.io/en/latest/spec/literal.html#legal-and-illegal-parameterizations
# We don't support enums as typing.Literal parameters. MyPy encodes these as str values with
# an additional "fallback" data member, but we don't need that complication.
# mypy.types.LiteralValue also includes float, noting its invalid as a parameterization, but
# we exclude this here.
# None types are also encoded as their own type, but we have them as values here.
TypingLiteralValue: typing.TypeAlias = int | bytes | str | bool | None
TypeArg: typing.TypeAlias = PyType | TypingLiteralValue
TypeArgs: typing.TypeAlias = tuple[TypeArg, ...]
Parameterise: typing.TypeAlias = Callable[["GenericType", TypeArgs, SourceLocation | None], PyType]

# Just a cache. Would be better as a class-var on GenericType, but see note on _type_registry
_generic_instances: typing.Final = dict[TypeArgs, PyType]()


@typing.final
@attrs.frozen
class GenericType(PyType, abc.ABC):
    """Represents a typing.Generic type with unknown parameters"""

    _parameterise: Parameterise

    def __attrs_post_init__(self) -> None:
        self.register()

    @property
    def wtype(self) -> typing.Never:
        raise CodeError("Generic type usage requires parameters")

    def parameterise(
        self, args: Sequence[PyType | TypingLiteralValue], source_location: SourceLocation | None
    ) -> PyType:
        return lazy_setdefault(
            _generic_instances,
            key=tuple(args),
            default=lambda args_: self._parameterise(self, args_, source_location),
        )


@attrs.frozen
class TupleType(PyType):
    generic: GenericType
    items: tuple[PyType, ...] = attrs.field(validator=attrs.validators.min_len(1))
    wtype: wtypes.WType


@attrs.frozen
class ArrayType(PyType):
    generic: GenericType
    items: PyType
    wtype: wtypes.WType


@attrs.frozen
class StorageProxyType(PyType):
    generic: GenericType | None
    content: PyType
    wtype: wtypes.WType


@attrs.frozen
class StorageMapProxyType(PyType):
    generic: GenericType
    key: PyType
    content: PyType
    wtype: wtypes.WType


@typing.final
@attrs.frozen(init=False)
class StructType(PyType):
    metaclass: str
    fields: Mapping[str, PyType] = attrs.field(
        converter=immutabledict, validator=[attrs.validators.min_len(1)]
    )
    frozen: bool
    wtype: wtypes.WType
    source_location: SourceLocation | None

    @cached_property
    def names(self) -> Sequence[str]:
        return tuple(self.fields.keys())

    @cached_property
    def types(self) -> Sequence[PyType]:
        return tuple(self.fields.values())

    def __init__(
        self,
        metaclass: str,
        typ: Callable[[Mapping[str, wtypes.WType], bool, SourceLocation | None], wtypes.WType],
        *,
        name: str,
        fields: Mapping[str, PyType],
        frozen: bool,
        source_location: SourceLocation | None,
    ):
        field_wtypes = {}
        for field_name, field_pytype in fields.items():
            field_wtype = field_pytype.wtype
            if field_wtype is None:
                raise CodeError(
                    f"Type {field_pytype.alias} is not allowed in a struct", source_location
                )
            field_wtypes[field_name] = field_wtype
        wtype = typ(field_wtypes, frozen, source_location)
        self.__attrs_init__(
            metaclass=metaclass,
            name=name,
            alias=name,
            wtype=wtype,
            fields=fields,
            frozen=frozen,
            source_location=source_location,
        )
        self.register()

    @classmethod
    def native(
        cls,
        *,
        name: str,
        fields: Mapping[str, PyType],
        frozen: bool,
        source_location: SourceLocation | None,
    ) -> typing.Self:
        return cls(
            metaclass=constants.STRUCT_BASE,
            typ=wtypes.WStructType,
            name=name,
            fields=fields,
            frozen=frozen,
            source_location=source_location,
        )

    @classmethod
    def arc4(
        cls,
        *,
        name: str,
        fields: Mapping[str, PyType],
        frozen: bool,
        source_location: SourceLocation | None,
    ) -> typing.Self:
        return cls(
            metaclass=constants.CLS_ARC4_STRUCT_META,
            typ=wtypes.ARC4Struct,
            name=name,
            fields=fields,
            frozen=frozen,
            source_location=source_location,
        )


@typing.final
@attrs.frozen
class _SimpleType(PyType):
    wtype: wtypes.WType

    def __attrs_post_init__(self) -> None:
        self.register()


NoneType: typing.Final = _SimpleType(
    name="builtins.None",
    alias="None",
    wtype=wtypes.void_wtype,
)
BoolType: typing.Final = _SimpleType(
    name="builtins.bool",
    alias="bool",
    wtype=wtypes.bool_wtype,
)
UInt64Type: typing.Final = _SimpleType(
    name=constants.CLS_UINT64,
    alias=constants.CLS_UINT64_ALIAS,
    wtype=wtypes.uint64_wtype,
)
BigUIntType: typing.Final = _SimpleType(
    name=constants.CLS_BIGUINT,
    alias=constants.CLS_BIGUINT_ALIAS,
    wtype=wtypes.biguint_wtype,
)
BytesType: typing.Final = _SimpleType(
    name=constants.CLS_BYTES,
    alias=constants.CLS_BYTES_ALIAS,
    wtype=wtypes.bytes_wtype,
)
StringType: typing.Final = _SimpleType(
    name=constants.CLS_STRING,
    alias=constants.CLS_STRING_ALIAS,
    wtype=wtypes.string_wtype,
)
AccountType: typing.Final = _SimpleType(
    name=constants.CLS_ACCOUNT,
    alias=constants.CLS_ACCOUNT_ALIAS,
    wtype=wtypes.account_wtype,
)
AssetType: typing.Final = _SimpleType(
    name=constants.CLS_ASSET,
    alias=constants.CLS_ASSET_ALIAS,
    wtype=wtypes.asset_wtype,
)
ApplicationType: typing.Final = _SimpleType(
    name=constants.CLS_APPLICATION,
    alias=constants.CLS_APPLICATION_ALIAS,
    wtype=wtypes.application_wtype,
)
ARC4StringType: typing.Final = _SimpleType(
    name=constants.CLS_ARC4_STRING,
    alias=constants.CLS_ARC4_STRING,
    wtype=wtypes.arc4_string_wtype,
)
ARC4BoolType: typing.Final = _SimpleType(
    name=constants.CLS_ARC4_BOOL,
    alias=constants.CLS_ARC4_BOOL,
    wtype=wtypes.arc4_bool_wtype,
)
ARC4ByteType: typing.Final = _SimpleType(
    name=constants.CLS_ARC4_BYTE,
    alias=constants.CLS_ARC4_BYTE,
    wtype=wtypes.arc4_byte_type,
)
ARC4DynamicBytesType: typing.Final = _SimpleType(
    name=constants.CLS_ARC4_DYNAMIC_BYTES,
    alias=constants.CLS_ARC4_DYNAMIC_BYTES,
    wtype=wtypes.arc4_byte_type,
)
ARC4AddressType: typing.Final = _SimpleType(
    name=constants.CLS_ARC4_ADDRESS,
    alias=constants.CLS_ARC4_ADDRESS,
    wtype=wtypes.arc4_address_type,
)

GenericARC4UIntNType: typing.Final = GenericType(
    name=constants.CLS_ARC4_UINTN,
    alias=constants.CLS_ARC4_UINTN,
    parameterise=NotImplemented,
)
GenericARC4BigUIntNType: typing.Final = GenericType(
    name=constants.CLS_ARC4_BIG_UINTN,
    alias=constants.CLS_ARC4_BIG_UINTN,
    parameterise=NotImplemented,
)
GenericARC4UFixedNxMType: typing.Final = GenericType(
    name=constants.CLS_ARC4_UFIXEDNXM,
    alias=constants.CLS_ARC4_UFIXEDNXM,
    parameterise=NotImplemented,
)
GenericARC4BigUFixedNxMType: typing.Final = GenericType(
    name=constants.CLS_ARC4_BIG_UFIXEDNXM,
    alias=constants.CLS_ARC4_BIG_UFIXEDNXM,
    parameterise=NotImplemented,
)


def _make_tuple_parameterise(
    typ: Callable[[Iterable[wtypes.WType], SourceLocation | None], wtypes.WType]
) -> Parameterise:
    def parameterise(
        self: GenericType, args: TypeArgs, source_location: SourceLocation | None
    ) -> TupleType:
        py_types = []
        item_wtypes = []
        for arg in args:
            if not isinstance(arg, PyType):
                raise CodeError(
                    "typing.Literal cannot be used as tuple type parameter", source_location
                )
            item_wtype = arg.wtype
            if item_wtype is None:
                raise CodeError(f"Type {arg.alias} is not allowed in a tuple", source_location)
            py_types.append(arg)
            item_wtypes.append(item_wtype)

        name = f"{self.name}[{', '.join(pyt.name for pyt in py_types)}]"
        alias = f"{self.alias}[{', '.join(pyt.alias for pyt in py_types)}]"
        return TupleType(
            generic=self,
            name=name,
            alias=alias,
            items=tuple(py_types),
            wtype=typ(item_wtypes, source_location),
        )

    return parameterise


GenericTupleType: typing.Final = GenericType(
    name="builtins.tuple",
    alias="tuple",
    parameterise=_make_tuple_parameterise(wtypes.WTuple),
)

GenericARC4TupleType: typing.Final = GenericType(
    name=constants.CLS_ARC4_TUPLE,
    alias=constants.CLS_ARC4_TUPLE,
    parameterise=_make_tuple_parameterise(wtypes.ARC4Tuple),
)

GenericArrayType: typing.Final = GenericType(
    name=constants.CLS_ARRAY,
    alias=constants.CLS_ARRAY_ALIAS,
    parameterise=NotImplemented,
)

GenericARC4DynamicArrayType: typing.Final = GenericType(
    name=constants.CLS_ARC4_DYNAMIC_ARRAY,
    alias=constants.CLS_ARC4_DYNAMIC_ARRAY,
    parameterise=NotImplemented,
)
GenericARC4StaticArrayType: typing.Final = GenericType(
    name=constants.CLS_ARC4_STATIC_ARRAY,
    alias=constants.CLS_ARC4_STATIC_ARRAY,
    parameterise=NotImplemented,
)


def _make_storage_parameterise(key_type: wtypes.WType) -> Parameterise:
    def parameterise(
        self: GenericType, args: TypeArgs, source_location: SourceLocation | None
    ) -> StorageProxyType:
        try:
            (arg,) = args
        except ValueError:
            raise CodeError(
                f"Expected a single type parameter, got {len(args)} parameters", source_location
            ) from None
        if not isinstance(arg, PyType):
            raise CodeError(
                f"typing.Literal cannot be used to parameterise {self.alias}", source_location
            )

        name = f"{self.name}[{arg.name}]"
        alias = f"{self.alias}[{arg.alias}]"
        return StorageProxyType(
            generic=self,
            name=name,
            alias=alias,
            content=arg,
            wtype=key_type,
        )

    return parameterise


def _parameterise_storage_map(
    self: GenericType, args: TypeArgs, source_location: SourceLocation | None
) -> StorageMapProxyType:
    try:
        key, content = args
    except ValueError:
        raise CodeError(
            f"Expected two type parameter, got {len(args)} parameters", source_location
        ) from None
    if not isinstance(key, PyType):
        raise CodeError(
            f"typing.Literal cannot be used to parameterise {self.alias}", source_location
        )
    if not isinstance(content, PyType):
        raise CodeError(
            f"typing.Literal cannot be used to parameterise {self.alias}", source_location
        )

    name = f"{self.name}[{key.name}, {content.name}]"
    alias = f"{self.alias}[{key.alias}, {content.alias}]"
    return StorageMapProxyType(
        generic=self,
        name=name,
        alias=alias,
        key=key,
        content=content,
        wtype=wtypes.box_key,  # TODO: maybe bytes since it will just be the prefix?
    )


GenericGlobalStateType: typing.Final = GenericType(
    name=constants.CLS_GLOBAL_STATE,
    alias=constants.CLS_GLOBAL_STATE_ALIAS,
    parameterise=_make_storage_parameterise(wtypes.state_key),
)
GenericLocalStateType: typing.Final = GenericType(
    name=constants.CLS_LOCAL_STATE,
    alias=constants.CLS_LOCAL_STATE_ALIAS,
    parameterise=_make_storage_parameterise(wtypes.state_key),
)
GenericBoxType: typing.Final = GenericType(
    name=constants.CLS_BOX_PROXY,
    alias=constants.CLS_BOX_PROXY_ALIAS,
    parameterise=_make_storage_parameterise(wtypes.box_key),
)
BoxRefType: typing.Final = StorageProxyType(
    name=constants.CLS_BOX_REF_PROXY,
    alias=constants.CLS_BOX_REF_PROXY_ALIAS,
    content=BytesType,
    wtype=wtypes.box_key,
    generic=None,
)
GenericBoxMapType: typing.Final = GenericType(
    name=constants.CLS_BOX_MAP_PROXY,
    alias=constants.CLS_BOX_MAP_PROXY_ALIAS,
    parameterise=_parameterise_storage_map,
)
