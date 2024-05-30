from __future__ import annotations

import abc
import enum
import typing

import typing_extensions

from puya.awst.nodes import (
    ContractReference,
    Expression,
    FieldExpression,
    Literal,
    Lvalue,
    Range,
    Statement,
    TupleExpression,
)
from puya.awst_build import pytypes
from puya.errors import CodeError, InternalError

if typing.TYPE_CHECKING:
    from collections.abc import Sequence

    import mypy.nodes
    import mypy.types

    from puya.awst_build.contract_data import AppStorageDeclaration
    from puya.parse import SourceLocation

__all__ = [
    "Iteration",
    "BuilderComparisonOp",
    "BuilderUnaryOp",
    "BuilderBinaryOp",
    "NodeBuilder",
    "CallableBuilder",
    "StorageProxyConstructorResult",
    "FunctionBuilder",
    "IntermediateExpressionBuilder",
    "TypeBuilder",
    "GenericTypeBuilder",
    "InstanceExpressionBuilder",
    "NotIterableInstanceExpressionBuilder",
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
class BuilderUnaryOp(enum.StrEnum):
    positive = "+"
    negative = "-"
    bit_invert = "~"


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


class NodeBuilder(abc.ABC):
    def __init__(self, location: SourceLocation):
        self.source_location = location

    @property
    @abc.abstractmethod
    def pytype(self) -> pytypes.PyType | None: ...

    @property
    def _type_description(self) -> str:
        if self.pytype is None:
            return type(self).__name__
        return str(self.pytype)

    def member_access(self, name: str, location: SourceLocation) -> NodeBuilder | Literal:
        """Handle self.name"""
        raise CodeError(
            f"{self._type_description} does not support member access {name}", location
        )

    @abc.abstractmethod
    def bool_eval(self, location: SourceLocation, *, negate: bool = False) -> NodeBuilder:
        """Handle boolean-ness evaluation, possibly inverted (ie "not" unary operator)"""

    @abc.abstractmethod
    def rvalue(self) -> Expression:
        """Produce an expression for use as an intermediary"""

    @abc.abstractmethod
    def lvalue(self) -> Lvalue:
        """Produce an expression for the target of an assignment"""

    @abc.abstractmethod
    def delete(self, location: SourceLocation) -> Statement:
        """Handle del operator statement"""
        # TODO: consider making a DeleteStatement which e.g. handles AppAccountStateExpression

    @abc.abstractmethod
    def unary_op(self, op: BuilderUnaryOp, location: SourceLocation) -> NodeBuilder: ...

    def compare(
        self, other: NodeBuilder | Literal, op: BuilderComparisonOp, location: SourceLocation
    ) -> NodeBuilder:
        """handle self {op} other"""
        if self.pytype is None:
            raise CodeError(
                f"expression is not a value type, so comparison with {op.value} is not supported",
                location,
            )
        return NotImplemented

    def binary_op(
        self,
        other: NodeBuilder | Literal,
        op: BuilderBinaryOp,
        location: SourceLocation,
        *,
        reverse: bool,
    ) -> NodeBuilder:
        """handle self {op} other"""
        if self.pytype is None:
            raise CodeError(
                f"expression is not a value type,"
                f" so operations such as {op.value} are not supported",
                location,
            )
        return NotImplemented

    def augmented_assignment(
        self, op: BuilderBinaryOp, rhs: NodeBuilder | Literal, location: SourceLocation
    ) -> Statement:
        if self.pytype is None:
            raise CodeError(
                f"expression is not a value type,"
                f" so operations such as {op.value}= are not supported",
                location,
            )
        raise CodeError(
            f"{self._type_description} does not support augmented assignment", location
        )

    @abc.abstractmethod
    def contains(self, item: NodeBuilder | Literal, location: SourceLocation) -> NodeBuilder:
        """Handle item in self"""
        raise CodeError("expression is not iterable", self.source_location)

    @abc.abstractmethod
    def iterate(self) -> Iteration:
        """Produce target of ForInLoop"""
        raise CodeError("expression is not iterable", self.source_location)

    @abc.abstractmethod
    def index(self, index: NodeBuilder | Literal, location: SourceLocation) -> NodeBuilder:
        """Handle self[index]"""
        raise CodeError("expression is not a collection", self.source_location)

    @abc.abstractmethod
    def slice_index(
        self,
        begin_index: NodeBuilder | Literal | None,
        end_index: NodeBuilder | Literal | None,
        stride: NodeBuilder | Literal | None,
        location: SourceLocation,
    ) -> NodeBuilder:
        """Handle self[begin_index:end_index:stride]"""
        raise CodeError("expression is not a collection", self.source_location)


class CallableBuilder(NodeBuilder, abc.ABC):
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


class IntermediateExpressionBuilder(NodeBuilder, abc.ABC):
    """Never valid as an assignment source OR target"""

    @typing.override
    def rvalue(self) -> Expression:
        raise CodeError(
            f"{self._type_description} is not valid as an rvalue", self.source_location
        )

    @typing.override
    def lvalue(self) -> Lvalue:
        raise CodeError(
            f"{self._type_description} is not valid as an lvalue", self.source_location
        )

    @typing.override
    def delete(self, location: SourceLocation) -> Statement:
        raise CodeError(
            f"{self._type_description} is not valid as del target", self.source_location
        )

    @typing.override
    def unary_op(self, op: BuilderUnaryOp, location: SourceLocation) -> NodeBuilder:
        return self._not_a_value(location)

    @typing.final
    @typing.override
    def contains(self, item: NodeBuilder | Literal, location: SourceLocation) -> NodeBuilder:
        return super().contains(item, location)

    @typing.final
    @typing.override
    def iterate(self) -> Iteration:
        return super().iterate()

    @typing.final
    @typing.override
    def index(self, index: NodeBuilder | Literal, location: SourceLocation) -> NodeBuilder:
        return super().index(index, location)

    @typing.final
    @typing.override
    def slice_index(
        self,
        begin_index: NodeBuilder | Literal | None,
        end_index: NodeBuilder | Literal | None,
        stride: NodeBuilder | Literal | None,
        location: SourceLocation,
    ) -> NodeBuilder:
        return super().slice_index(begin_index, end_index, stride, location)

    def _not_a_value(self, location: SourceLocation) -> typing.Never:
        raise CodeError(f"{self._type_description} is not a value", location)


class FunctionBuilder(IntermediateExpressionBuilder, CallableBuilder, abc.ABC):
    @property
    def pytype(self) -> None:  # TODO: give function type
        return None

    @typing.override
    def bool_eval(self, location: SourceLocation, *, negate: bool = False) -> NodeBuilder:
        from puya.awst_build.eb._utils import bool_eval_to_constant

        return bool_eval_to_constant(value=True, location=location, negate=negate)


class StorageProxyConstructorResult(NodeBuilder, abc.ABC):
    @typing.override
    @property
    @abc.abstractmethod
    def pytype(self) -> pytypes.StorageProxyType | pytypes.StorageMapProxyType: ...

    @property
    @abc.abstractmethod
    def initial_value(self) -> Expression | None: ...

    @abc.abstractmethod
    def build_definition(
        self,
        member_name: str,
        defined_in: ContractReference,
        typ: pytypes.PyType,
        location: SourceLocation,
    ) -> AppStorageDeclaration: ...


_TPyType_co = typing_extensions.TypeVar(
    "_TPyType_co", bound=pytypes.PyType, default=pytypes.PyType, covariant=True
)


class TypeBuilder(
    IntermediateExpressionBuilder, typing.Generic[_TPyType_co], CallableBuilder, abc.ABC
):
    # TODO: better error messages for rvalue/lvalue/delete

    def __init__(self, pytype: _TPyType_co, location: SourceLocation):
        super().__init__(location)
        self._pytype = pytype

    @property
    def pytype(self) -> pytypes.TypeType:
        return pytypes.TypeType(self._pytype)

    @typing.final
    def produces(self) -> _TPyType_co:
        return self._pytype

    @typing.override
    def bool_eval(self, location: SourceLocation, *, negate: bool = False) -> NodeBuilder:
        from puya.awst_build.eb._utils import bool_eval_to_constant

        return bool_eval_to_constant(value=True, location=location, negate=negate)


class GenericTypeBuilder(IntermediateExpressionBuilder, CallableBuilder, abc.ABC):
    @typing.override
    @property
    def pytype(self) -> None:  # TODO: ??
        return None

    @typing.override
    def member_access(self, name: str, location: SourceLocation) -> NodeBuilder | Literal:
        raise CodeError(
            f"Cannot access member {name} without specifying class type parameters first",
            location,
        )

    @typing.override
    def bool_eval(self, location: SourceLocation, *, negate: bool = False) -> NodeBuilder:
        from puya.awst_build.eb._utils import bool_eval_to_constant

        return bool_eval_to_constant(value=True, location=location, negate=negate)


class InstanceExpressionBuilder(NodeBuilder, typing.Generic[_TPyType_co], abc.ABC):

    def __init__(self, pytype: _TPyType_co, expr: Expression):
        super().__init__(expr.source_location)
        if expr.wtype != pytype.wtype:
            raise InternalError(
                f"Invalid WType of {str(self.pytype)!r} expression for: {expr.wtype}",
                expr.source_location,
            )
        self._pytype = pytype
        self.__expr = expr

    @typing.override
    @typing.final
    @property
    def pytype(self) -> _TPyType_co:
        return self._pytype

    @property
    def expr(self) -> Expression:
        return self.__expr

    @typing.override
    @typing.final
    def lvalue(self) -> Lvalue:
        resolved = self.rvalue()
        return _validate_lvalue(self._pytype, resolved)

    @typing.override
    def rvalue(self) -> Expression:
        return self.expr

    @typing.override
    def delete(self, location: SourceLocation) -> Statement:
        raise CodeError(f"{self.pytype} is not valid as del target", location)

    @typing.override
    def member_access(self, name: str, location: SourceLocation) -> NodeBuilder | Literal:
        raise CodeError(f"Unrecognised member of {self.pytype}: {name}", location)

    @typing.override
    def unary_op(self, op: BuilderUnaryOp, location: SourceLocation) -> NodeBuilder:
        raise CodeError(f"{self.pytype} does not support unary {op.value!r} operator", location)


class NotIterableInstanceExpressionBuilder(InstanceExpressionBuilder[_TPyType_co], abc.ABC):
    @typing.final
    @typing.override
    def contains(self, item: NodeBuilder | Literal, location: SourceLocation) -> NodeBuilder:
        return super().contains(item, location)

    @typing.final
    @typing.override
    def iterate(self) -> Iteration:
        return super().iterate()

    @typing.final
    @typing.override
    def index(self, index: NodeBuilder | Literal, location: SourceLocation) -> NodeBuilder:
        return super().index(index, location)

    @typing.final
    @typing.override
    def slice_index(
        self,
        begin_index: NodeBuilder | Literal | None,
        end_index: NodeBuilder | Literal | None,
        stride: NodeBuilder | Literal | None,
        location: SourceLocation,
    ) -> NodeBuilder:
        return super().slice_index(begin_index, end_index, stride, location)


def _validate_lvalue(typ: pytypes.PyType, resolved: Expression) -> Lvalue:
    if typ == pytypes.NoneType:
        raise CodeError(
            "None indicates an empty return and cannot be assigned",
            resolved.source_location,
        )
    if not isinstance(resolved, Lvalue):  # type: ignore[arg-type,misc]
        raise CodeError(
            "expression is not valid as an assignment target", resolved.source_location
        )
    if isinstance(resolved, FieldExpression):
        if resolved.base.wtype.immutable:
            raise CodeError(
                "expression is not valid as an assignment target - object is immutable",
                resolved.source_location,
            )
    elif isinstance(resolved, TupleExpression):
        assert isinstance(typ, pytypes.TupleType)
        for item_typ, item in zip(typ.items, resolved.items, strict=True):
            _validate_lvalue(item_typ, item)
    return typing.cast(Lvalue, resolved)
