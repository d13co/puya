from __future__ import annotations

import abc
import typing

import attrs

from puya.awst import wtypes
from puya.awst_build import constants
from puya.errors import CodeError

if typing.TYPE_CHECKING:
    from collections.abc import Sequence

    from puya.parse import SourceLocation


@attrs.frozen
class PyType(abc.ABC):
    name: str
    """The fully qualified type name"""
    alias: str
    """The short name, for display purposes"""
    is_arc4: bool
    """Is this type ARC4 encoded?"""

    @property
    @abc.abstractmethod
    def wtype(self) -> wtypes.WType | None:
        """The WType that this type represents, if any."""


@attrs.frozen
class _SimpleType(PyType):
    wtype: wtypes.WType


@attrs.frozen
class TupleType(PyType):
    items: tuple[PyType, ...] = attrs.field(validator=attrs.validators.min_len(1))
    wtype: wtypes.WTuple


NoneType: typing.Final = _SimpleType(
    name="builtins.None",
    alias="None",
    wtype=wtypes.void_wtype,
    is_arc4=False,
)
BoolType: typing.Final = _SimpleType(
    name="builtins.bool",
    alias="bool",
    wtype=wtypes.bool_wtype,
    is_arc4=False,
)
UInt64Type: typing.Final = _SimpleType(
    name=constants.CLS_UINT64,
    alias=constants.CLS_UINT64_ALIAS,
    wtype=wtypes.uint64_wtype,
    is_arc4=False,
)
BigUIntType: typing.Final = _SimpleType(
    name=constants.CLS_BIGUINT,
    alias=constants.CLS_BIGUINT_ALIAS,
    wtype=wtypes.biguint_wtype,
    is_arc4=False,
)
BytesType: typing.Final = _SimpleType(
    name=constants.CLS_BYTES,
    alias=constants.CLS_BYTES_ALIAS,
    wtype=wtypes.bytes_wtype,
    is_arc4=False,
)
StringType: typing.Final = _SimpleType(
    name=constants.CLS_STRING,
    alias=constants.CLS_STRING_ALIAS,
    wtype=wtypes.string_wtype,
    is_arc4=False,
)
AccountType: typing.Final = _SimpleType(
    name=constants.CLS_ACCOUNT,
    alias=constants.CLS_ACCOUNT_ALIAS,
    wtype=wtypes.account_wtype,
    is_arc4=False,
)
AssetType: typing.Final = _SimpleType(
    name=constants.CLS_ASSET,
    alias=constants.CLS_ASSET_ALIAS,
    wtype=wtypes.asset_wtype,
    is_arc4=False,
)
ApplicationType: typing.Final = _SimpleType(
    name=constants.CLS_APPLICATION,
    alias=constants.CLS_APPLICATION_ALIAS,
    wtype=wtypes.application_wtype,
    is_arc4=False,
)
ARC4StringType: typing.Final = _SimpleType(
    name=constants.CLS_ARC4_STRING,
    alias=constants.CLS_ARC4_STRING,
    wtype=wtypes.arc4_string_wtype,
    is_arc4=True,
)
ARC4BoolType: typing.Final = _SimpleType(
    name=constants.CLS_ARC4_BOOL,
    alias=constants.CLS_ARC4_BOOL,
    wtype=wtypes.arc4_bool_wtype,
    is_arc4=True,
)
ARC4ByteType: typing.Final = _SimpleType(
    name=constants.CLS_ARC4_BYTE,
    alias=constants.CLS_ARC4_BYTE,
    wtype=wtypes.arc4_byte_type,
    is_arc4=True,
)
ARC4DynamicBytesType: typing.Final = _SimpleType(
    name=constants.CLS_ARC4_DYNAMIC_BYTES,
    alias=constants.CLS_ARC4_DYNAMIC_BYTES,
    wtype=wtypes.arc4_byte_type,
    is_arc4=True,
)
ARC4AddressType: typing.Final = _SimpleType(
    name=constants.CLS_ARC4_ADDRESS,
    alias=constants.CLS_ARC4_ADDRESS,
    wtype=wtypes.arc4_address_type,
    is_arc4=True,
)


@attrs.frozen
class GenericType(PyType, abc.ABC):
    @property
    def wtype(self) -> typing.Never:
        raise CodeError("Generic type usage requires parameters")

    @abc.abstractmethod
    def parameterise(
        self, args: Sequence[PyType], source_location: SourceLocation | None
    ) -> PyType:
        """Create a concrete type"""


@attrs.frozen
class _GenericTupleType(GenericType):
    name: str = attrs.field(default="builtins.tuple", init=False)
    alias: str = attrs.field(default="tuple", init=False)
    is_arc4: bool = attrs.field(default=False, init=False)

    @typing.override
    def parameterise(
        self, args: Sequence[PyType], source_location: SourceLocation | None
    ) -> TupleType:
        if not args:
            raise CodeError("Empty tuples are not supported", source_location)
        if NoneType in args:
            raise CodeError(f"{NoneType.alias} is not allowed in tuples", source_location)
        name = f"{self.name}[{', '.join(i.name for i in args)}]"
        alias = f"{self.alias}[{', '.join(i.alias for i in args)}]"
        item_wtypes = []
        for i in args:
            item_wtype = i.wtype
            if item_wtype is None:
                raise CodeError(f"Type {i.alias} is not allowed in a tuple", source_location)
            item_wtypes.append(item_wtype)
        return TupleType(
            name=name,
            alias=alias,
            items=tuple(args),
            wtype=wtypes.WTuple.from_types(item_wtypes),
            is_arc4=self.is_arc4,
        )


@attrs.frozen
class _GenericARC4TupleType(_GenericTupleType):
    name: str = attrs.field(default=constants.CLS_ARC4_TUPLE, init=False)
    alias: str = attrs.field(default=constants.CLS_ARC4_TUPLE, init=False)
    is_arc4: bool = attrs.field(default=True, init=False)

    @typing.override
    def parameterise(
        self, args: Sequence[PyType], source_location: SourceLocation | None
    ) -> TupleType:
        for i in args:
            if not i.is_arc4:
                raise CodeError(
                    f"{self.name} can only contain ARC4 encoded items", source_location
                )
        return super().parameterise(args, source_location)
