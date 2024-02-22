import typing

from puyapy import (
    Application,
    Bytes,
    GlobalState,
    Txn,
    UInt64,
    arc4,
    op,
    subroutine,
    urange,
)


# Size_32: typing.TypeAlias = typing.Literal[32]


Bytes32: typing.TypeAlias = arc4.StaticBytes[typing.Literal[32]]
BytesDynamic: typing.TypeAlias = arc4.DynamicBytes
BytesDynamic2: typing.TypeAlias = arc4.DynamicArray[arc4.Byte]
Branch: typing.TypeAlias = arc4.StaticBytes[typing.Literal[33]]
Path: typing.TypeAlias = arc4.StaticArray[Branch, typing.Literal[3]]

TREE_DEPTH = 3
RIGHT_SIBLING_PREFIX = 170


class MerkleTree(arc4.ARC4Contract):
    def __init__(self) -> None:
        self.root = GlobalState(Bytes32)
        self.size = GlobalState(UInt64)

    @subroutine
    def calc_init_root(self) -> Bytes32:
        result = Bytes.from_hex("e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855")
        for _i in urange(TREE_DEPTH):
            result = op.sha256(result + result)
        return Bytes32(result)

    @arc4.abimethod
    def create(self) -> None:
        self.root.value = self.calc_init_root()

    @subroutine
    def is_right_sibling(self, elem: Branch) -> bool:
        return elem[0].bytes == op.itob(RIGHT_SIBLING_PREFIX)[7]

    @subroutine
    def calc_root(self, leaf: Bytes32, path: Path) -> Bytes32:
        result = leaf.bytes
        for branch in path:
            if self.is_right_sibling(branch):
                result = op.sha256(result + op.extract(branch.bytes, 1, 32))
            else:
                result = op.sha256(op.extract(branch.bytes, 1, 32) + result)
        return Bytes32(result)

    @arc4.abimethod
    def delete_application(self) -> None:
        assert Txn.sender == Application(0).creator

    @subroutine
    def verify(self, data: Bytes, path: Path) -> None:
        assert self.root.value == self.calc_root(Bytes32(op.sha256(data)), path)

    @arc4.abimethod
    def append_leaf(self, data: Bytes, path: Path) -> None:
        assert data.length
        assert self.root.value == self.calc_root(
            Bytes32(
                Bytes.from_hex("e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855")
            ),
            path,
        )
        self.root.value = self.calc_root(Bytes32(op.sha256(data)), path)
        self.size.value += 1

    @arc4.abimethod
    def update_leaf(self, old_data: Bytes, new_data: Bytes, path: Path) -> None:
        assert new_data.length
        assert self.root.value == self.calc_root(Bytes32(old_data), path)
        self.root.value = self.calc_root(Bytes32(op.sha256(new_data)), path)
