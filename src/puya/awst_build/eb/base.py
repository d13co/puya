from __future__ import annotations

import abc
import enum
import typing

import typing_extensions

from puya.awst.nodes import (
    BytesConstant,
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
from puya.awst_build.contract_data import AppStorageDeclaration
from puya.errors import CodeError, InternalError

if typing.TYPE_CHECKING:
    from collections.abc import Sequence

    import mypy.nodes
    import mypy.types

    from puya.awst import wtypes
    from puya.parse import SourceLocation

__all__ = [
    "Iteration",
    "BuilderComparisonOp",
    "BuilderBinaryOp",
    "ExpressionBuilder",
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


class ExpressionBuilder(abc.ABC):
    def __init__(self, location: SourceLocation):
        self.source_location = location

    @property
    @abc.abstractmethod
    def pytype(self) -> pytypes.PyType: ...

    def __str__(self) -> str:
        return str(self.pytype)

    @abc.abstractmethod
    def member_access(self, name: str, location: SourceLocation) -> ExpressionBuilder | Literal:
        """Handle self.name"""
        raise CodeError(f"{self} does not support member access {name}", location)


class CallableBuilder(ExpressionBuilder, abc.ABC):
    @abc.abstractmethod
    def call(
        self,
        args: Sequence[ExpressionBuilder | Literal],
        arg_typs: Sequence[pytypes.PyType],
        arg_kinds: list[mypy.nodes.ArgKind],
        arg_names: list[str | None],
        location: SourceLocation,
    ) -> ExpressionBuilder:
        """Handle self(args...)"""


class FunctionBuilder(CallableBuilder, abc.ABC):
    def __init__(self, typ: pytypes.FuncType, location: SourceLocation):
        super().__init__(location)
        self._pytype = typ

    @property
    def pytype(self) -> pytypes.FuncType:
        return self._pytype

    @typing.override
    def member_access(self, name: str, location: SourceLocation) -> ExpressionBuilder | Literal:
        raise CodeError(f"{self} is a function and does not support member access", location)


class TypeBuilder(CallableBuilder, abc.ABC):
    def __init__(self, typ: pytypes.TypeType, location: SourceLocation):
        super().__init__(location)
        self._pytype = typ

    @typing.override
    @property
    def pytype(self) -> pytypes.TypeType:
        return self._pytype

    @typing.override
    def member_access(self, name: str, location: SourceLocation) -> ExpressionBuilder | Literal:
        """Handle self.name"""
        raise CodeError(f"{self.pytype.typ} does not support static member access", location)


class GenericTypeBuilder(TypeBuilder, abc.ABC):
    @typing.override
    def call(
        self,
        args: Sequence[ExpressionBuilder | Literal],
        arg_typs: Sequence[pytypes.PyType],
        arg_kinds: list[mypy.nodes.ArgKind],
        arg_names: list[str | None],
        location: SourceLocation,
    ) -> ExpressionBuilder:
        raise CodeError("Generic type usage requires parameters", location)

    @typing.override
    def member_access(self, name: str, location: SourceLocation) -> ExpressionBuilder | Literal:
        raise CodeError("Generic type usage requires parameters", location)


class InstanceBuilder(ExpressionBuilder, abc.ABC):
    @abc.abstractmethod
    def rvalue(self) -> Expression:
        """Produce an expression for use as an intermediary"""

    @abc.abstractmethod
    def lvalue(self) -> Lvalue:
        """Produce an expression for the target of an assignment"""

    @abc.abstractmethod
    def delete(self, location: SourceLocation) -> Statement:
        """Handle del operator statement"""

    @abc.abstractmethod
    def bool_eval(self, location: SourceLocation, *, negate: bool = False) -> InstanceBuilder:
        """Handle boolean-ness evaluation, possibly inverted (ie "not" unary operator)"""

    @abc.abstractmethod
    def unary_plus(self, location: SourceLocation) -> InstanceBuilder:
        """Handle +self"""

    @abc.abstractmethod
    def unary_minus(self, location: SourceLocation) -> InstanceBuilder:
        """Handle -self"""

    @abc.abstractmethod
    def bitwise_invert(self, location: SourceLocation) -> InstanceBuilder:
        """Handle ~self"""

    @abc.abstractmethod
    def compare(
        self, other: InstanceBuilder | Literal, op: BuilderComparisonOp, location: SourceLocation
    ) -> InstanceBuilder:
        """handle self {comparison op} other"""

    @abc.abstractmethod
    def binary_op(
        self,
        other: InstanceBuilder | Literal,
        op: BuilderBinaryOp,
        location: SourceLocation,
        *,
        reverse: bool,
    ) -> InstanceBuilder:
        """handle self {binary op} other"""

    @abc.abstractmethod
    def augmented_assignment(
        self, op: BuilderBinaryOp, rhs: InstanceBuilder | Literal, location: SourceLocation
    ) -> Statement:
        """Handle self {binary op}= rhs"""

    @abc.abstractmethod
    def index(self, index: InstanceBuilder | Literal, location: SourceLocation) -> InstanceBuilder:
        """Handle self[index]"""

    @abc.abstractmethod
    def slice_index(  # TODO: roll into index, have a Slice EB
        self,
        begin_index: InstanceBuilder | Literal | None,
        end_index: InstanceBuilder | Literal | None,
        stride: InstanceBuilder | Literal | None,
        location: SourceLocation,
    ) -> InstanceBuilder:
        """Handle self[begin_index:end_index:stride]"""

    @abc.abstractmethod
    def contains(
        self, item: InstanceBuilder | Literal, location: SourceLocation
    ) -> InstanceBuilder:
        """Handle `elem in self`"""

    @abc.abstractmethod
    def iterate(self) -> Iteration:
        """handle for ... in self"""


class StateProxyDefinitionBuilder(InstanceBuilder, abc.ABC):
    def __init__(
        self,
        location: SourceLocation,
        storage: wtypes.WType,
        key_override: BytesConstant | None,
        description: str | None,
        initial_value: Expression | None = None,
    ):
        super().__init__(location)
        self.storage = storage
        self.key_override = key_override
        self.description = description
        self.initial_value = initial_value

    def build_definition(
        self,
        member_name: str,
        defined_in: ContractReference,
        typ: pytypes.PyType,
        location: SourceLocation,
    ) -> AppStorageDeclaration:
        return AppStorageDeclaration(
            description=self.description,
            member_name=member_name,
            key_override=self.key_override,
            source_location=location,
            typ=typ,
            defined_in=defined_in,
        )


_TPyType = typing_extensions.TypeVar("_TPyType", bound=pytypes.PyType, default=pytypes.PyType)


class ValueExpressionBuilder(InstanceBuilder, typing.Generic[_TPyType], abc.ABC):

    def __init__(self, typ: _TPyType, expr: Expression):
        if expr.wtype != typ.wtype:
            raise InternalError(
                f"Invalid type of expression for {typ}: {expr.wtype}",
                expr.source_location,
            )
        super().__init__(expr.source_location)
        self._pytype = typ
        self.__expr = expr

    @property
    def expr(self) -> Expression:
        return self.__expr

    @typing.override
    @property
    def pytype(self) -> _TPyType:
        return self._pytype

    @typing.override
    def lvalue(self) -> Lvalue:
        resolved = self.rvalue()
        return _validate_lvalue(resolved)

    @typing.override
    def rvalue(self) -> Expression:
        return self.expr

    @typing.override
    def delete(self, location: SourceLocation) -> Statement:
        raise CodeError(f"{self} is not valid as del target", location)

    @typing.override
    def index(self, index: InstanceBuilder | Literal, location: SourceLocation) -> InstanceBuilder:
        raise CodeError(f"{self} does not support indexing", location)

    @typing.override
    def member_access(self, name: str, location: SourceLocation) -> ExpressionBuilder | Literal:
        raise CodeError(f"Unrecognised member of {self}: {name}", location)

    @typing.override
    def iterate(self) -> Iteration:
        """Produce target of ForInLoop"""
        raise CodeError(f"{self} does not support iteration", self.source_location)

    @typing.override
    def unary_plus(self, location: SourceLocation) -> InstanceBuilder:
        raise CodeError(f"{self} does not support unary plus operator", location)

    @typing.override
    def unary_minus(self, location: SourceLocation) -> InstanceBuilder:
        raise CodeError(f"{self} does not support unary minus operator", location)

    @typing.override
    def bitwise_invert(self, location: SourceLocation) -> InstanceBuilder:
        raise CodeError(f"{self} does not support bitwise inversion", location)

    @typing.override
    def contains(
        self, item: InstanceBuilder | Literal, location: SourceLocation
    ) -> InstanceBuilder:
        raise CodeError(f"{self} does not support in/not in checks", location)

    @typing.override
    def compare(
        self, other: InstanceBuilder | Literal, op: BuilderComparisonOp, location: SourceLocation
    ) -> InstanceBuilder:
        return NotImplemented

    @typing.override
    def binary_op(
        self,
        other: InstanceBuilder | Literal,
        op: BuilderBinaryOp,
        location: SourceLocation,
        *,
        reverse: bool,
    ) -> InstanceBuilder:
        return NotImplemented

    @typing.override
    def augmented_assignment(
        self, op: BuilderBinaryOp, rhs: InstanceBuilder | Literal, location: SourceLocation
    ) -> Statement:
        raise CodeError(f"{self} does not support augmented assignment", location)

    @typing.override
    def slice_index(
        self,
        begin_index: InstanceBuilder | Literal | None,
        end_index: InstanceBuilder | Literal | None,
        stride: InstanceBuilder | Literal | None,
        location: SourceLocation,
    ) -> InstanceBuilder:
        raise CodeError(f"{self} does not support slicing", location)


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
