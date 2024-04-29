from __future__ import annotations

import typing

import attrs

from puya.awst import wtypes
from puya.awst_build import constants
from puya.errors import InternalError


class PyType(typing.Protocol):
    @property
    def name(self) -> str:
        """The fully qualified type name"""

    @property
    def alias(self) -> str:
        """The short name, for display purposes"""

    @property
    def wtype(self) -> wtypes.WType | None:
        """The WType that this type represents, if any"""

    @property
    def parameters(self) -> tuple[PyType, ...]:
        """Type parameters. May be empty."""


SIMPLE_TYPES = dict[str, "SimplePyType"]()


@attrs.frozen
class SimplePyType(PyType):
    name: str
    alias: str
    wtype: wtypes.WType | None
    parameters: tuple[PyType, ...] = attrs.field(default=(), init=False)

    def __attrs_post_init__(self) -> None:
        if self.name in SIMPLE_TYPES:
            raise InternalError(f"Duplicate mapping of {self.name}")
        SIMPLE_TYPES[self.name] = self


NoneType: typing.Final = SimplePyType(
    name="builtins.None",
    alias="None",
    wtype=wtypes.void_wtype,
)
BoolType: typing.Final = SimplePyType(
    name="builtins.bool",
    alias="bool",
    wtype=wtypes.bool_wtype,
)
UInt64Type: typing.Final = SimplePyType(
    name=constants.CLS_UINT64,
    alias=constants.CLS_UINT64_ALIAS,
    wtype=wtypes.uint64_wtype,
)
BigUIntType: typing.Final = SimplePyType(
    name=constants.CLS_BIGUINT,
    alias=constants.CLS_BIGUINT_ALIAS,
    wtype=wtypes.biguint_wtype,
)
