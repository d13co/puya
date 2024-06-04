from __future__ import annotations

import types
import typing

import algopy_testing.primitives as algopy
from algopy_testing.constants import ARC4_RETURN_PREFIX, BITS_IN_BYTE, UINT64_SIZE, UINT512_SIZE
from algopy_testing.utils import as_bytes, as_int, as_int64, as_int512, int_to_bytes

if typing.TYPE_CHECKING:
    from collections.abc import Callable

_P = typing.ParamSpec("_P")
_R = typing.TypeVar("_R")


def abimethod(
    fn: Callable[_P, _R] | None = None,
) -> Callable[_P, _R] | Callable[[Callable[_P, _R]], Callable[_P, _R]]:
    def decorator(fn: Callable[_P, _R]) -> Callable[_P, _R]:
        def wrapped(*args: _P.args, **kwargs: _P.kwargs) -> _R:
            return fn(*args, **kwargs)

        return wrapped

    if fn is None:
        return decorator
    else:
        return decorator(fn)


class ARC4Contract:
    pass


class String:
    pass


_TBitSize = typing.TypeVar("_TBitSize", bound=int)
_RETURN_PREFIX = algopy.Bytes(ARC4_RETURN_PREFIX)


class _ABIEncoded(typing.Protocol):
    @classmethod
    def from_bytes(cls, value: algopy.Bytes | bytes, /) -> typing.Self:
        """Construct an instance from the underlying bytes (no validation)"""
        ...

    @property
    def bytes(self) -> algopy.Bytes:
        """Get the underlying Bytes"""
        ...

    @classmethod
    def from_log(cls, log: algopy.Bytes, /) -> typing.Self:
        """Load an ABI type from application logs,
        checking for the ABI return prefix `0x151f7c75`"""
        ...


class _UIntN(_ABIEncoded, typing.Protocol):
    def __init__(self, value: algopy.BigUInt | algopy.UInt64 | int = 0, /) -> None: ...

    # ~~~ https://docs.python.org/3/reference/datamodel.html#basic-customization ~~~
    # TODO: mypy suggests due to Liskov below should be other: object
    #       need to consider ramifications here, ignoring it for now
    def __eq__(  # type: ignore[override]
        self,
        other: UIntN[_TBitSize] | BigUIntN[_TBitSize] | algopy.UInt64 | algopy.BigUInt | int,
    ) -> bool: ...
    def __ne__(  # type: ignore[override]
        self,
        other: UIntN[_TBitSize] | BigUIntN[_TBitSize] | algopy.UInt64 | algopy.BigUInt | int,
    ) -> bool: ...
    def __le__(
        self,
        other: UIntN[_TBitSize] | BigUIntN[_TBitSize] | algopy.UInt64 | algopy.BigUInt | int,
    ) -> bool: ...
    def __lt__(
        self,
        other: UIntN[_TBitSize] | BigUIntN[_TBitSize] | algopy.UInt64 | algopy.BigUInt | int,
    ) -> bool: ...
    def __ge__(
        self,
        other: UIntN[_TBitSize] | BigUIntN[_TBitSize] | algopy.UInt64 | algopy.BigUInt | int,
    ) -> bool: ...
    def __gt__(
        self,
        other: UIntN[_TBitSize] | BigUIntN[_TBitSize] | algopy.UInt64 | algopy.BigUInt | int,
    ) -> bool: ...
    def __bool__(self) -> bool:
        """Returns `True` if not equal to zero"""
        ...

    @classmethod
    def from_log(cls, log: algopy.Bytes, /) -> typing.Self:
        """Load an ABI type from application logs,
        checking for the ABI return prefix `0x151f7c75`"""
        if log[slice(0, 4)] == _RETURN_PREFIX:
            return cls.from_bytes(log[slice(4, len(log))])
        raise ValueError("ABI return prefix not found")


# https://stackoverflow.com/a/75395800
class _UIntNMeta(type(_UIntN), typing.Generic[_TBitSize]):  # type: ignore  # noqa: PGH003
    __concrete__: dict[type[_TBitSize], type] = {}  # noqa: RUF012

    def __getitem__(cls, key_t: type[_TBitSize]) -> type:
        cache = cls.__concrete__
        if c := cache.get(key_t, None):
            return c
        cache[key_t] = c = types.new_class(
            f"{cls.__name__}[{key_t.__name__}]", (cls,), {}, lambda ns: ns.update(_t=key_t)
        )
        return c


class UIntN(_UIntN, typing.Generic[_TBitSize], metaclass=_UIntNMeta):
    """An ARC4 UInt consisting of the number of bits specified.

    Max Size: 64 bits"""

    _t: type[_TBitSize]
    __bit_size: int
    __max_bytes_len: int
    __max_int: int
    __value: bytes  # underlying 'bytes' value representing the UIntN

    def __init__(self, value: algopy.BigUInt | algopy.UInt64 | int = 0, /) -> None:
        self.__bit_size = as_int(typing.get_args(self._t)[0], max=UINT64_SIZE)
        self.__max_int = 2**self.__bit_size - 1
        value = as_int(value, max=self.__max_int)

        self.__max_bytes_len = self.__bit_size // BITS_IN_BYTE
        bytes_value = int_to_bytes(value, self.__max_bytes_len)
        self.__value = as_bytes(bytes_value, max_size=self.__max_bytes_len)

    @classmethod
    def from_bytes(cls, value: algopy.Bytes | bytes, /) -> typing.Self:
        """Construct an instance from the underlying bytes (no validation)"""
        value = as_bytes(value)
        result = cls(int.from_bytes(value))
        if len(value) > result.__max_bytes_len:  # noqa: SLF001
            raise ValueError(
                f"expected at most {result.__max_bytes_len} bytes, got: {len(value)}"  # noqa: SLF001
            )
        return result

    @property
    def bytes(self) -> algopy.Bytes:
        """Get the underlying Bytes"""
        return algopy.Bytes(self.__value)

    @property
    def native(self) -> algopy.UInt64:
        """Return the UInt64 representation of the value after ARC4 decoding"""
        return algopy.UInt64(int.from_bytes(self.__value))

    def __eq__(self, other: object) -> bool:
        return as_int64(self.native) == as_int(other, max=None)

    def __ne__(self, other: object) -> bool:
        return as_int64(self.native) != as_int(other, max=None)

    def __le__(self, other: object) -> bool:
        return as_int64(self.native) <= as_int(other, max=None)

    def __lt__(self, other: object) -> bool:
        return as_int64(self.native) < as_int(other, max=None)

    def __ge__(self, other: object) -> bool:
        return as_int64(self.native) >= as_int(other, max=None)

    def __gt__(self, other: object) -> bool:
        return as_int64(self.native) > as_int(other, max=None)

    def __bool__(self) -> bool:
        return bool(self.native)


class BigUIntN(_UIntN, typing.Generic[_TBitSize], metaclass=_UIntNMeta):
    """An ARC4 UInt consisting of the number of bits specified.

    Max size: 512 bits"""

    _t: type[_TBitSize]
    __bit_size: int
    __max_bytes_len: int
    __max_int: int
    __value: bytes  # underlying 'bytes' value representing the BigUIntN

    def __init__(self, value: algopy.BigUInt | algopy.UInt64 | int = 0, /) -> None:
        self.__bit_size = as_int(typing.get_args(self._t)[0], max=UINT512_SIZE)
        self.__max_int = 2**self.__bit_size - 1
        value = as_int(value, max=self.__max_int)

        self.__max_bytes_len = self.__bit_size // BITS_IN_BYTE
        bytes_value = int_to_bytes(value, self.__max_bytes_len)
        self.__value = as_bytes(bytes_value, max_size=self.__max_bytes_len)

    @classmethod
    def from_bytes(cls, value: algopy.Bytes | bytes, /) -> typing.Self:
        """Construct an instance from the underlying bytes (no validation)"""
        value = as_bytes(value)
        result = cls(int.from_bytes(value))
        if len(value) > result.__max_bytes_len:  # noqa: SLF001
            raise ValueError(
                f"expected at most {result.__max_bytes_len} bytes, got: {len(value)}"  # noqa: SLF001
            )
        return result

    @property
    def bytes(self) -> algopy.Bytes:
        """Get the underlying Bytes"""
        return algopy.Bytes(self.__value)

    @property
    def native(self) -> algopy.BigUInt:
        """Return the UInt64 representation of the value after ARC4 decoding"""
        return algopy.BigUInt.from_bytes(self.__value)

    def __eq__(self, other: object) -> bool:
        return as_int512(self.native) == as_int(other, max=None)

    def __ne__(self, other: object) -> bool:
        return as_int512(self.native) != as_int(other, max=None)

    def __le__(self, other: object) -> bool:
        return as_int512(self.native) <= as_int(other, max=None)

    def __lt__(self, other: object) -> bool:
        return as_int512(self.native) < as_int(other, max=None)

    def __ge__(self, other: object) -> bool:
        return as_int512(self.native) >= as_int(other, max=None)

    def __gt__(self, other: object) -> bool:
        return as_int512(self.native) > as_int(other, max=None)

    def __bool__(self) -> bool:
        return bool(self.native)


UInt8: typing.TypeAlias = UIntN[typing.Literal[8]]
"""An ARC4 UInt8"""

UInt16: typing.TypeAlias = UIntN[typing.Literal[16]]
"""An ARC4 UInt16"""

UInt32: typing.TypeAlias = UIntN[typing.Literal[32]]
"""An ARC4 UInt32"""

UInt64: typing.TypeAlias = UIntN[typing.Literal[64]]
"""An ARC4 UInt64"""

UInt128: typing.TypeAlias = BigUIntN[typing.Literal[128]]
"""An ARC4 UInt128"""

UInt256: typing.TypeAlias = BigUIntN[typing.Literal[256]]
"""An ARC4 UInt256"""

UInt512: typing.TypeAlias = BigUIntN[typing.Literal[512]]
"""An ARC4 UInt512"""