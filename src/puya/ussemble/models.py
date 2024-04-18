import abc
from collections.abc import Mapping, Sequence

import attrs

from puya.ussemble.visitor import AVMVisitor, T


class Node:
    @abc.abstractmethod
    def accept(self, visitor: AVMVisitor[T]) -> T: ...


@attrs.frozen
class AVMOp(Node):
    op_code: str


@attrs.frozen
class IntBlock(AVMOp):
    op_code: str = attrs.field(default="intcblock", init=False)
    constants: Mapping[int, int]

    def accept(self, visitor: AVMVisitor[T]) -> T:
        return visitor.visit_int_block(self)


@attrs.frozen
class BytesBlock(AVMOp):
    op_code: str = attrs.field(default="bytecblock", init=False)
    constants: Mapping[bytes, int]

    def accept(self, visitor: AVMVisitor[T]) -> T:
        return visitor.visit_bytes_block(self)


@attrs.frozen
class IntC(AVMOp):
    op_code: str = attrs.field(default="intc", init=False)
    index: int

    def accept(self, visitor: AVMVisitor[T]) -> T:
        return visitor.visit_intc(self)


@attrs.frozen
class PushInt(AVMOp):
    op_code: str = attrs.field(default="pushint", init=False)
    value: int

    def accept(self, visitor: AVMVisitor[T]) -> T:
        return visitor.visit_push_int(self)


@attrs.frozen
class PushInts(AVMOp):
    op_code: str = attrs.field(default="pushints", init=False)
    values: list[int]

    def accept(self, visitor: AVMVisitor[T]) -> T:
        return visitor.visit_push_ints(self)


@attrs.frozen
class BytesC(AVMOp):
    op_code: str = attrs.field(default="bytec", init=False)
    index: int

    def accept(self, visitor: AVMVisitor[T]) -> T:
        return visitor.visit_bytesc(self)


@attrs.frozen
class PushBytes(AVMOp):
    op_code: str = attrs.field(default="pushbytes", init=False)
    value: bytes

    def accept(self, visitor: AVMVisitor[T]) -> T:
        return visitor.visit_push_bytes(self)


@attrs.frozen
class PushBytess(AVMOp):
    op_code: str = attrs.field(default="pushbytess", init=False)
    values: list[bytes]

    def accept(self, visitor: AVMVisitor[T]) -> T:
        return visitor.visit_push_bytess(self)


@attrs.frozen
class Label(Node):
    name: str

    def accept(self, visitor: AVMVisitor[T]) -> T:
        return visitor.visit_label(self)


@attrs.frozen
class Jump(AVMOp):
    label: Label

    def accept(self, visitor: AVMVisitor[T]) -> T:
        return visitor.visit_jump(self)


@attrs.frozen
class MultiJump(AVMOp):
    labels: list[Label]

    def accept(self, visitor: AVMVisitor[T]) -> T:
        return visitor.visit_multi_jump(self)


@attrs.frozen
class Intrinsic(AVMOp):
    immediates: Sequence[int | str]

    def accept(self, visitor: AVMVisitor[T]) -> T:
        return visitor.visit_intrinsic(self)
