from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Self, TypeVar

import algosdk

from algopy_testing.primitives.bytes import Bytes
from algopy_testing.utils import as_string

if TYPE_CHECKING:
    from algopy_testing.models.application import Application
    from algopy_testing.models.asset import Asset
    from algopy_testing.primitives.uint64 import UInt64

T = TypeVar("T")


@dataclass
class Account:
    _public_key: str
    balance: UInt64 | None = None
    min_balance: UInt64 | None = None
    auth_address: Account | None = None
    total_num_uint: UInt64 | None = None
    total_num_byte_slice: Bytes | None = None
    total_extra_app_pages: UInt64 | None = None
    total_apps_created: UInt64 | None = None
    total_apps_opted_in: UInt64 | None = None
    total_assets_created: UInt64 | None = None
    total_assets: UInt64 | None = None
    total_boxes: UInt64 | None = None
    total_box_bytes: UInt64 | None = None

    def __init__(self, value: str | Bytes = algosdk.constants.ZERO_ADDRESS, /):
        if not isinstance(value, str | Bytes):
            raise TypeError("Invalid value for AccountProtocol")
        self._public_key = as_string(value)

    def __repr__(self) -> str:
        return self._public_key

    def __str__(self) -> str:
        return self._public_key

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Account):
            return self._public_key == other._public_key
        return self._public_key == as_string(other)

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __bool__(self) -> bool:
        return self._public_key != algosdk.constants.ZERO_ADDRESS

    def is_opted_in(self, asset_or_app: Asset | Application, /) -> bool:
        raise NotImplementedError(
            "The 'is_opted_in' method is being executed in a python testing context. "
            "Please mock this method in according to your python testing framework of choice."
        )

    @classmethod
    def from_bytes(cls, value: Bytes | bytes) -> Self:
        return cls(as_string(value))

    @property
    def bytes(self) -> Bytes:
        return Bytes(self._public_key.encode("utf-8"))