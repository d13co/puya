from __future__ import annotations

import abc
import contextlib
import typing

import attrs

from puya import log
from puya.awst import wtypes
from puya.awst_build import constants
from puya.errors import CodeError, InternalError

if typing.TYPE_CHECKING:
    from collections.abc import Sequence

    from puya.parse import SourceLocation


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


@attrs.frozen
class GenericType(PyType, abc.ABC):
    """Represents a typing.Generic type with unknown parameters"""

    def __attrs_post_init__(self) -> None:
        self.register()

    @property
    def wtype(self) -> typing.Never:
        raise CodeError("Generic type usage requires parameters")

    @abc.abstractmethod
    def parameterise(
        self, args: Sequence[PyType | TypingLiteralValue], source_location: SourceLocation | None
    ) -> PyType:
        """Create a concrete type"""


@attrs.frozen
class TupleType(PyType):
    items: tuple[PyType, ...] = attrs.field(validator=attrs.validators.min_len(1))
    wtype: wtypes.WTuple | wtypes.ARC4Tuple


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


@attrs.frozen
class _GenericTupleType(GenericType, abc.ABC):
    name: str = attrs.field(default="builtins.tuple", init=False)
    alias: str = attrs.field(default="tuple", init=False)

    _instances: typing.Final = dict[tuple[PyType | TypingLiteralValue, ...], TupleType]()

    @typing.override
    def parameterise(
        self, args_: Sequence[PyType | TypingLiteralValue], source_location: SourceLocation | None
    ) -> TupleType:
        args = tuple(args_)
        with contextlib.suppress(KeyError):
            return self._instances[args]

        py_types, item_wtypes = zip(
            *_validate_tuple_type_args(args_, source_location), strict=True
        )
        name = f"{self.name}[{', '.join(i.name for i in py_types)}]"
        alias = f"{self.alias}[{', '.join(i.alias for i in py_types)}]"
        self._instances[args] = result = TupleType(
            name=name,
            alias=alias,
            items=py_types,
            wtype=wtypes.WTuple.from_types(item_wtypes),
        )
        return result


@attrs.frozen
class _GenericARC4TupleType(GenericType):
    name: str = attrs.field(default=constants.CLS_ARC4_TUPLE, init=False)
    alias: str = attrs.field(default=constants.CLS_ARC4_TUPLE, init=False)

    _instances: typing.Final = dict[tuple[PyType | TypingLiteralValue, ...], TupleType]()

    @typing.override
    def parameterise(
        self, args_: Sequence[PyType | TypingLiteralValue], source_location: SourceLocation | None
    ) -> TupleType:
        args = tuple(args_)
        with contextlib.suppress(KeyError):
            return self._instances[args]

        py_types, item_wtypes = zip(
            *_validate_tuple_type_args(args_, source_location), strict=True
        )
        name = f"{self.name}[{', '.join(i.name for i in py_types)}]"
        alias = f"{self.alias}[{', '.join(i.alias for i in py_types)}]"

        item_wtypes_arc4 = []
        for w in item_wtypes:
            if not isinstance(w, wtypes.ARC4Type):
                raise CodeError(
                    f"{self.name} can only contain ARC4 encoded items", source_location
                )
            item_wtypes_arc4.append(w)
        self._instances[args] = result = TupleType(
            name=name,
            alias=alias,
            items=py_types,
            wtype=wtypes.ARC4Tuple.from_types(item_wtypes_arc4),
        )
        return result


def _validate_tuple_type_args(
    args: Sequence[PyType | TypingLiteralValue], source_location: SourceLocation | None
) -> Sequence[tuple[PyType, wtypes.WType]]:
    if not args:
        raise CodeError("Empty tuples are not supported", source_location)
    if NoneType in args:
        raise CodeError(f"{NoneType.alias} is not allowed in tuples", source_location)
    result = []
    for i in args:
        if not isinstance(i, PyType):
            raise CodeError(
                "typing.Literal cannot be used as tuple type parameter", source_location
            )
        item_wtype = i.wtype
        if item_wtype is None:
            raise CodeError(f"Type {i.alias} is not allowed in a tuple", source_location)
        result.append((i, item_wtype))
    return result
