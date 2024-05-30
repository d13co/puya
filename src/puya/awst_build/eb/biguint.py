from __future__ import annotations

import typing

import attrs
import mypy.nodes

from puya import log
from puya.awst import wtypes
from puya.awst.nodes import (
    BigUIntAugmentedAssignment,
    BigUIntBinaryOperation,
    BigUIntBinaryOperator,
    BigUIntConstant,
    Expression,
    Literal,
    NumericComparison,
    NumericComparisonExpression,
    ReinterpretCast,
    Statement,
)
from puya.awst_build import pytypes
from puya.awst_build.eb._base import (
    NotIterableInstanceExpressionBuilder,
)
from puya.awst_build.eb._utils import uint64_to_biguint
from puya.awst_build.eb.bool import BoolExpressionBuilder
from puya.awst_build.eb.bytes import BytesExpressionBuilder
from puya.awst_build.eb.bytes_backed import BytesBackedClassExpressionBuilder
from puya.awst_build.eb.interface import (
    BuilderBinaryOp,
    BuilderComparisonOp,
    BuilderUnaryOp,
    InstanceBuilder,
    NodeBuilder,
)
from puya.awst_build.utils import convert_literal_to_builder
from puya.errors import CodeError

if typing.TYPE_CHECKING:
    from collections.abc import Sequence

    import mypy.types

    from puya.parse import SourceLocation

logger = log.get_logger(__name__)


class BigUIntClassExpressionBuilder(BytesBackedClassExpressionBuilder):
    def __init__(self, location: SourceLocation):
        super().__init__(pytypes.BigUIntType, location)

    @typing.override
    def call(
        self,
        args: Sequence[NodeBuilder | Literal],
        arg_typs: Sequence[pytypes.PyType],
        arg_kinds: list[mypy.nodes.ArgKind],
        arg_names: list[str | None],
        location: SourceLocation,
    ) -> InstanceBuilder:
        match args:
            case []:
                value: Expression = BigUIntConstant(value=0, source_location=location)
            case [Literal(value=int(int_value))]:
                value = BigUIntConstant(value=int_value, source_location=location)
            case [NodeBuilder() as eb]:
                value = uint64_to_biguint(eb, location)
            case _:
                logger.error("Invalid/unhandled arguments", location=location)
                # dummy value to continue with
                value = BigUIntConstant(value=0, source_location=location)
        return BigUIntExpressionBuilder(value)


class BigUIntExpressionBuilder(NotIterableInstanceExpressionBuilder):
    def __init__(self, expr: Expression):
        super().__init__(pytypes.BigUIntType, expr)

    def member_access(self, name: str, location: SourceLocation) -> NodeBuilder | Literal:
        match name:
            case "bytes":
                return BytesExpressionBuilder(
                    ReinterpretCast(
                        source_location=location, wtype=wtypes.bytes_wtype, expr=self.expr
                    )
                )
        return super().member_access(name, location)

    def bool_eval(self, location: SourceLocation, *, negate: bool = False) -> InstanceBuilder:
        cmp_expr = NumericComparisonExpression(
            lhs=self.expr,
            operator=NumericComparison.eq if negate else NumericComparison.ne,
            # TODO: does this source location make sense?
            rhs=BigUIntConstant(value=0, source_location=location),
            source_location=location,
        )
        return BoolExpressionBuilder(cmp_expr)

    def unary_op(self, op: BuilderUnaryOp, location: SourceLocation) -> InstanceBuilder:
        if op == BuilderUnaryOp.positive:
            # unary + is allowed, but for the current types it has no real impact
            # so just expand the existing expression to include the unary operator
            return BigUIntExpressionBuilder(attrs.evolve(self.expr, source_location=location))
        return super().unary_op(op, location)

    def compare(
        self, other: InstanceBuilder | Literal, op: BuilderComparisonOp, location: SourceLocation
    ) -> InstanceBuilder:
        other = convert_literal_to_builder(other, self.pytype)
        if other.pytype == self.pytype:
            other_expr = other.rvalue()
        elif other.pytype == pytypes.UInt64Type:
            other_expr = uint64_to_biguint(other, location)
        else:
            return NotImplemented
        cmp_expr = NumericComparisonExpression(
            source_location=location,
            lhs=self.expr,
            operator=NumericComparison(op.value),
            rhs=other_expr,
        )
        return BoolExpressionBuilder(cmp_expr)

    def binary_op(
        self,
        other: InstanceBuilder | Literal,
        op: BuilderBinaryOp,
        location: SourceLocation,
        *,
        reverse: bool,
    ) -> InstanceBuilder:
        other = convert_literal_to_builder(other, self.pytype)
        if other.pytype == self.pytype:
            other_expr = other.rvalue()
        elif other.pytype == pytypes.UInt64Type:
            other_expr = uint64_to_biguint(other, location)
        else:
            return NotImplemented
        lhs = self.expr
        rhs = other_expr
        if reverse:
            (lhs, rhs) = (rhs, lhs)
        biguint_op = _translate_biguint_math_operator(op, location)
        bin_op_expr = BigUIntBinaryOperation(
            source_location=location, left=lhs, op=biguint_op, right=rhs
        )
        return BigUIntExpressionBuilder(bin_op_expr)

    def augmented_assignment(
        self, op: BuilderBinaryOp, rhs: InstanceBuilder | Literal, location: SourceLocation
    ) -> Statement:
        rhs = convert_literal_to_builder(rhs, self.pytype)
        if rhs.pytype == self.pytype:
            value = rhs.rvalue()
        elif rhs.pytype == pytypes.UInt64Type:
            value = uint64_to_biguint(rhs, location)
        else:
            raise CodeError(
                f"Invalid operand type {rhs.pytype} for {op.value}= with {self.pytype}", location
            )
        target = self.lvalue()
        biguint_op = _translate_biguint_math_operator(op, location)
        return BigUIntAugmentedAssignment(
            source_location=location,
            target=target,
            value=value,
            op=biguint_op,
        )


def _translate_biguint_math_operator(
    operator: BuilderBinaryOp, loc: SourceLocation
) -> BigUIntBinaryOperator:
    if operator is BuilderBinaryOp.div:
        logger.error(
            (
                "To maintain semantic compatibility with Python, "
                "only the truncating division operator (//) is supported "
            ),
            location=loc,
        )
        # continue traversing code to generate any further errors
        operator = BuilderBinaryOp.floor_div
    try:
        return BigUIntBinaryOperator(operator.value)
    except ValueError as ex:
        raise CodeError(f"Unsupported BigUInt math operator {operator.value!r}", loc) from ex
