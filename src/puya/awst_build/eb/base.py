# ruff: noqa: ARG002
from __future__ import annotations

import abc
import enum
import typing

import typing_extensions

from puya.awst.nodes import (
    ContractReference,
    Expression,
    FieldExpression,
    IndexExpression,
    Literal,
    Lvalue,
    Range,
    ReinterpretCast,
    Statement,
    TupleExpression,
    TupleItemExpression,
)
from puya.awst_build import pytypes
from puya.errors import CodeError, InternalError

if typing.TYPE_CHECKING:
    from collections.abc import Sequence

    import mypy.nodes
    import mypy.types

    from puya.awst import wtypes
    from puya.awst_build.contract_data import AppStorageDeclaration
    from puya.parse import SourceLocation

__all__ = [
    "Iteration",
    "BuilderComparisonOp",
    "BuilderBinaryOp",
    "NodeBuilder",
    "CallableBuilder",
    "FunctionBuilder",
    "TypeBuilder",
    "GenericTypeBuilder",
    "InstanceBuilder",
    "StateProxyDefinitionBuilder",
    "ValueExpressionBuilder",
]

Iteration: typing.TypeAlias = Expression | Range


@enum.unique
class BuilderComparisonOp(enum.StrEnum):
    eq = "=="
    ne = "!="
    lt = "<"
    lte = "<="
    gt = ">"
    gte = ">="


@enum.unique
class BuilderBinaryOp(enum.StrEnum):
    add = "+"
    sub = "-"
    mult = "*"
    div = "/"
    floor_div = "//"
    mod = "%"
    pow = "**"
    mat_mult = "@"
    lshift = "<<"
    rshift = ">>"
    bit_or = "|"
    bit_xor = "^"
    bit_and = "&"


_TPyType = typing_extensions.TypeVar(
    "_TPyType", bound=pytypes.PyType, default=pytypes.PyType, covariant=True
)


class NodeBuilder(typing.Generic[_TPyType], abc.ABC):
    def __init__(self, typ: _TPyType, location: SourceLocation):
        self._pytype = typ
        self._source_location = location

    @typing.final
    @property
    def pytype(self) -> _TPyType:
        return self._pytype

    @typing.final
    @property
    def source_location(self) -> SourceLocation:
        return self._source_location

    def __str__(self) -> str:
        return str(self.pytype)

    @abc.abstractmethod
    def member_access(self, name: str, location: SourceLocation) -> NodeBuilder | Literal:
        """Handle self.name"""

    @abc.abstractmethod
    def bool_eval(self, location: SourceLocation, *, negate: bool = False) -> InstanceBuilder:
        """Handle boolean-ness evaluation, possibly inverted (ie "not" unary operator)"""


class CallableBuilder(NodeBuilder[_TPyType], abc.ABC):
    @abc.abstractmethod
    def call(
        self,
        args: Sequence[NodeBuilder | Literal],
        arg_typs: Sequence[pytypes.PyType],
        arg_kinds: list[mypy.nodes.ArgKind],
        arg_names: list[str | None],
        location: SourceLocation,
    ) -> NodeBuilder:
        """Handle self(args...)"""


class FunctionBuilder(CallableBuilder[pytypes.FuncType], abc.ABC):
    @typing.override
    def member_access(self, name: str, location: SourceLocation) -> NodeBuilder | Literal:
        raise CodeError(f"{self} is a function and does not support member access", location)

    def bool_eval(self, location: SourceLocation, *, negate: bool = False) -> InstanceBuilder:
        from puya.awst_build.eb._utils import bool_eval_to_constant

        return bool_eval_to_constant(value=True, location=location, negate=negate)


class TypeBuilder(CallableBuilder[pytypes.TypeType], abc.ABC):
    @typing.override
    def member_access(self, name: str, location: SourceLocation) -> NodeBuilder | Literal:
        """Handle self.name"""
        raise CodeError(f"{self.pytype.typ} does not support static member access", location)

    def bool_eval(self, location: SourceLocation, *, negate: bool = False) -> InstanceBuilder:
        from puya.awst_build.eb._utils import bool_eval_to_constant

        return bool_eval_to_constant(value=True, location=location, negate=negate)


class GenericTypeBuilder(TypeBuilder, abc.ABC):
    @typing.override
    def call(
        self,
        args: Sequence[NodeBuilder | Literal],
        arg_typs: Sequence[pytypes.PyType],
        arg_kinds: list[mypy.nodes.ArgKind],
        arg_names: list[str | None],
        location: SourceLocation,
    ) -> NodeBuilder:
        raise CodeError("Generic type usage requires parameters", location)

    @typing.override
    def member_access(self, name: str, location: SourceLocation) -> NodeBuilder | Literal:
        raise CodeError("Generic type usage requires parameters", location)


class InstanceBuilder(NodeBuilder[_TPyType], abc.ABC):
    @abc.abstractmethod
    def rvalue(self) -> Expression:
        """Produce an expression for use as an intermediary"""

    @abc.abstractmethod
    def lvalue(self) -> Lvalue:
        """Produce an expression for the target of an assignment"""

    def delete(self, location: SourceLocation) -> Statement:
        raise CodeError(f"{self} is not valid as del target", location)

    @typing.override
    def member_access(self, name: str, location: SourceLocation) -> NodeBuilder | Literal:
        raise CodeError(f"Unrecognised member of {self}: {name}", location)

    def unary_plus(self, location: SourceLocation) -> InstanceBuilder:
        raise CodeError(f"{self} does not support unary plus operator", location)

    def unary_minus(self, location: SourceLocation) -> InstanceBuilder:
        raise CodeError(f"{self} does not support unary minus operator", location)

    def bitwise_invert(self, location: SourceLocation) -> InstanceBuilder:
        raise CodeError(f"{self} does not support bitwise inversion", location)

    def compare(
        self, other: InstanceBuilder | Literal, op: BuilderComparisonOp, location: SourceLocation
    ) -> InstanceBuilder:
        return NotImplemented

    def binary_op(
        self,
        other: InstanceBuilder | Literal,
        op: BuilderBinaryOp,
        location: SourceLocation,
        *,
        reverse: bool,
    ) -> InstanceBuilder:
        return NotImplemented

    def augmented_assignment(
        self, op: BuilderBinaryOp, rhs: InstanceBuilder | Literal, location: SourceLocation
    ) -> Statement:
        raise CodeError(f"{self} does not support augmented assignment", location)


class ContainerBuilder(InstanceBuilder[_TPyType], abc.ABC):
    @abc.abstractmethod
    def index(self, index: InstanceBuilder | Literal, location: SourceLocation) -> InstanceBuilder:
        """Handle self[index]"""
        raise CodeError(f"{self} does not support indexing", location)

    @abc.abstractmethod
    def slice_index(  # TODO: maybe roll into index, have a Slice EB ??
        self,
        begin_index: InstanceBuilder | Literal | None,
        end_index: InstanceBuilder | Literal | None,
        stride: InstanceBuilder | Literal | None,
        location: SourceLocation,
    ) -> InstanceBuilder:
        """Handle self[begin_index:end_index:stride]"""
        raise CodeError(f"{self} does not support slicing", location)

    @abc.abstractmethod
    def contains(
        self, item: InstanceBuilder | Literal, location: SourceLocation
    ) -> InstanceBuilder:
        """Handle `elem in self`"""
        raise CodeError(f"{self} does not support in/not in checks", location)

    @abc.abstractmethod
    def iterate(self) -> Iteration:
        """handle for ... in self"""
        raise CodeError(f"{self} does not support iteration", self.source_location)


class StateProxyDefinitionBuilder(NodeBuilder[pytypes.StorageProxyType], abc.ABC):
    @abc.abstractmethod
    def build_definition(
        self,
        member_name: str,
        defined_in: ContractReference,
        typ: pytypes.PyType,
        location: SourceLocation,
    ) -> AppStorageDeclaration: ...


class ValueExpressionBuilder(InstanceBuilder[_TPyType], abc.ABC):

    def __init__(self, typ: _TPyType, expr: Expression):
        if expr.wtype != typ.wtype:
            raise InternalError(
                f"Invalid type of expression for {typ}: {expr.wtype}",
                expr.source_location,
            )
        super().__init__(typ, expr.source_location)
        self.__expr = expr

    @property
    def expr(self) -> Expression:
        return self.__expr

    @property
    def wtype(self) -> wtypes.WType:  # TODO: YEET ME
        return self.pytype.wtype

    @typing.override
    def lvalue(self) -> Lvalue:
        resolved = self.rvalue()
        return _validate_lvalue(resolved)

    @typing.override
    def rvalue(self) -> Expression:
        return self.expr


def _validate_lvalue(resolved: Expression) -> Lvalue:
    if isinstance(resolved, TupleItemExpression):
        raise CodeError("Tuple items cannot be reassigned", resolved.source_location)
    if not isinstance(resolved, Lvalue):  # type: ignore[arg-type,misc]
        raise CodeError(
            f"{resolved.wtype.stub_name} expression is not valid as assignment target",
            resolved.source_location,
        )
    if isinstance(resolved, IndexExpression | FieldExpression) and resolved.base.wtype.immutable:
        raise CodeError(
            "expression is not valid as assignment target"
            f" ({resolved.base.wtype.stub_name} is immutable)",
            resolved.source_location,
        )
    if isinstance(resolved, ReinterpretCast):
        _validate_lvalue(resolved.expr)
    elif isinstance(resolved, TupleExpression):
        for item in resolved.items:
            _validate_lvalue(item)
    return typing.cast(Lvalue, resolved)
