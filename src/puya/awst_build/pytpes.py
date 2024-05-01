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
    _registry: typing.Final = dict[str, "PyType"]()

    @property
    @abc.abstractmethod
    def wtype(self) -> wtypes.WType | None:
        """The WType that this type represents, if any."""

    def register(self) -> None:
        existing_entry = self._registry.get(self.name)
        if existing_entry is None:
            self._registry[self.name] = self
        elif existing_entry is self:
            logger.debug(f"Duplicate registration of {self}")
        else:
            raise InternalError(f"Duplicate mapping of {self.name}")

    @classmethod
    def from_name(cls, name: str) -> PyType | None:
        return cls._registry.get(name)


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


@typing.final
@attrs.frozen
class GenericType(PyType, abc.ABC):
    """Represents a typing.Generic type with unknown parameters"""

    _parameterise: Parameterise
    _instances: typing.Final = dict[TypeArgs, PyType]()

    def __attrs_post_init__(self) -> None:
        self.register()

    @property
    def wtype(self) -> typing.Never:
        raise CodeError("Generic type usage requires parameters")

    def parameterise(
        self, args: Sequence[PyType | TypingLiteralValue], source_location: SourceLocation | None
    ) -> PyType:
        return lazy_setdefault(
            self._instances,
            key=tuple(args),
            default=lambda args_: self._parameterise(self, args_, source_location),
        )


@attrs.frozen
class TupleType(PyType):
    items: tuple[PyType, ...] = attrs.field(validator=attrs.validators.min_len(1))
    wtype: wtypes.WType


@attrs.frozen(init=False)
class StructType(PyType):
    fields: Mapping[str, PyType] = attrs.field(
        converter=immutabledict, validator=[attrs.validators.min_len(1)]
    )
    wtype: wtypes.WStructType | wtypes.ARC4Struct
    source_location: SourceLocation | None

    @cached_property
    def names(self) -> Sequence[str]:
        return tuple(self.fields.keys())

    @cached_property
    def types(self) -> Sequence[PyType]:
        return tuple(self.fields.values())

    def __init__(
        self,
        kind: type[wtypes.WStructType | wtypes.ARC4Struct],
        name: str,
        fields: Mapping[str, PyType],
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
        wtype = kind.from_name_and_fields(
            python_name=name,
            fields=field_wtypes,
            source_location=source_location,
        )
        self.__attrs_init__(
            name=name,
            alias=name,
            wtype=wtype,
            fields=fields,
            source_location=source_location,
        )
        self.register()


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


_TTupleItemWType = typing.TypeVar("_TTupleItemWType", wtypes.WType, wtypes.ARC4Type)


def _make_tuple_parameterise(
    typ: Callable[[Iterable[_TTupleItemWType], SourceLocation | None], wtypes.WType],
    guard: Callable[[TypeArg, SourceLocation | None], tuple[PyType, _TTupleItemWType]],
) -> Parameterise:
    def parameterise(
        self: GenericType, args: TypeArgs, source_location: SourceLocation | None
    ) -> TupleType:
        py_types = []
        item_wtypes = list[_TTupleItemWType]()
        for arg in args:
            item_pytype, item_wtype = guard(arg, source_location)
            py_types.append(item_pytype)
            item_wtypes.append(item_wtype)

        name = f"{self.name}[{', '.join(pyt.name for pyt in py_types)}]"
        alias = f"{self.alias}[{', '.join(pyt.alias for pyt in py_types)}]"
        return TupleType(
            name=name,
            alias=alias,
            items=tuple(py_types),
            wtype=typ(item_wtypes, source_location),
        )

    return parameterise


def _is_valid_native_tuple_element_type(
    arg: TypeArg, source_location: SourceLocation | None
) -> tuple[PyType, wtypes.WType]:
    if not isinstance(arg, PyType):
        raise CodeError("typing.Literal cannot be used as tuple type parameter", source_location)
    item_wtype = arg.wtype
    if item_wtype is None:
        raise CodeError(f"Type {arg.alias} is not allowed in a tuple", source_location)
    return arg, item_wtype


def _is_valid_arc4_tuple_element_type(
    arg: TypeArg, source_location: SourceLocation | None
) -> tuple[PyType, wtypes.ARC4Type]:
    py_type, item_wtype = _is_valid_native_tuple_element_type(arg, source_location)
    if not isinstance(item_wtype, wtypes.ARC4Type):
        raise CodeError(
            f"Invalid type for {constants.CLS_ARC4_TUPLE}:"
            f" {py_type.alias} is not an ARC4 encoded type",
            source_location,
        )
    return py_type, item_wtype


GenericTupleType: typing.Final = GenericType(
    name="builtins.tuple",
    alias="tuple",
    parameterise=_make_tuple_parameterise(wtypes.WTuple, _is_valid_native_tuple_element_type),
)

GenericARC4TupleType: typing.Final = GenericType(
    name=constants.CLS_ARC4_TUPLE,
    alias=constants.CLS_ARC4_TUPLE,
    parameterise=_make_tuple_parameterise(wtypes.ARC4Tuple, _is_valid_arc4_tuple_element_type),
)
