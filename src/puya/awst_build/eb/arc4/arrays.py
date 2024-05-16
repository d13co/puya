from __future__ import annotations

import typing
from abc import ABC

from puya import arc4_util, log
from puya.algo_constants import ENCODED_ADDRESS_LENGTH
from puya.awst import wtypes
from puya.awst.nodes import (
    AddressConstant,
    ArrayConcat,
    ArrayExtend,
    ArrayPop,
    BytesComparisonExpression,
    CheckedMaybe,
    EqualityComparison,
    Expression,
    ExpressionStatement,
    IndexExpression,
    IntrinsicCall,
    Literal,
    NewArray,
    NumericComparison,
    NumericComparisonExpression,
    ReinterpretCast,
    SingleEvaluation,
    Statement,
    TupleExpression,
    UInt64BinaryOperation,
    UInt64BinaryOperator,
    UInt64Constant,
)
from puya.awst_build import intrinsic_factory, pytypes
from puya.awst_build.eb._utils import bool_eval_to_constant, get_bytes_expr, get_bytes_expr_builder
from puya.awst_build.eb.arc4._utils import expect_arc4_operand_wtype
from puya.awst_build.eb.arc4.base import (
    CopyBuilder,
    arc4_bool_bytes,
    arc4_compare_bytes,
    get_integer_literal_value,
)
from puya.awst_build.eb.base import (
    BuilderBinaryOp,
    BuilderComparisonOp,
    FunctionBuilder,
    InstanceBuilder,
    Iteration,
    NodeBuilder,
    TypeBuilder,
    ValueExpressionBuilder,
)
from puya.awst_build.eb.bool import BoolExpressionBuilder
from puya.awst_build.eb.bytes_backed import BytesBackedClassExpressionBuilder
from puya.awst_build.eb.reference_types.account import AccountExpressionBuilder
from puya.awst_build.eb.uint64 import UInt64ExpressionBuilder
from puya.awst_build.eb.var_factory import var_expression
from puya.awst_build.eb.void import VoidExpressionBuilder
from puya.awst_build.utils import expect_operand_wtype, require_expression_builder
from puya.errors import CodeError, InternalError

if typing.TYPE_CHECKING:
    from collections.abc import Sequence

    import mypy.nodes

    from puya.parse import SourceLocation

logger = log.get_logger(__name__)


class DynamicArrayClassExpressionBuilder(BytesBackedClassExpressionBuilder):
    def __init__(self, location: SourceLocation, wtype: wtypes.ARC4DynamicArray | None = None):
        super().__init__(location)
        self.wtype = wtype

    def produces(self) -> wtypes.ARC4Type:
        if not self.wtype:
            raise InternalError(
                "Cannot resolve wtype of generic EB until the index method is called with the "
                "generic type parameter."
            )
        return self.wtype

    def index(self, index: NodeBuilder | Literal, location: SourceLocation) -> NodeBuilder:
        return self.index_multiple([index], location)

    def index_multiple(
        self, indexes: Sequence[NodeBuilder | Literal], location: SourceLocation
    ) -> NodeBuilder:
        match indexes:
            case [TypeBuilder() as eb]:
                element_wtype = eb.produces()
                self.wtype = arc4_util.make_dynamic_array_wtype(element_wtype, location)
                return self
            case _:
                raise CodeError("Invalid/unhandled arguments", location)

    def call(
        self,
        args: Sequence[NodeBuilder | Literal],
        arg_typs: Sequence[pytypes.PyType],
        arg_kinds: list[mypy.nodes.ArgKind],
        arg_names: list[str | None],
        location: SourceLocation,
    ) -> NodeBuilder:
        non_literal_args = [
            require_expression_builder(a, msg="Array arguments must be non literals").rvalue()
            for a in args
        ]
        wtype = self.wtype
        if wtype is None:
            if non_literal_args:
                element_wtype = non_literal_args[0].wtype
                wtype = arc4_util.make_dynamic_array_wtype(element_wtype, location)
            else:
                raise CodeError(
                    "Empty arrays require a type annotation to be instantiated", location
                )

        for a in non_literal_args:
            expect_operand_wtype(a, wtype.element_type)

        return DynamicArrayExpressionBuilder(
            NewArray(
                source_location=location,
                values=tuple(non_literal_args),
                wtype=wtype,
            )
        )


class StaticArrayClassExpressionBuilder(BytesBackedClassExpressionBuilder):
    def __init__(self, location: SourceLocation, wtype: wtypes.ARC4StaticArray | None = None):
        super().__init__(location)
        self.wtype = wtype

    def produces(self) -> wtypes.WType:
        if not self.wtype:
            raise InternalError(
                "Cannot resolve wtype of generic EB until the index method is called with the "
                "generic type parameter."
            )
        return self.wtype

    def index(self, index: NodeBuilder | Literal, location: SourceLocation) -> NodeBuilder:
        return self.index_multiple([index], location)

    def index_multiple(
        self, indexes: Sequence[NodeBuilder | Literal], location: SourceLocation
    ) -> NodeBuilder:
        match indexes:
            case [TypeBuilder() as item_type, array_size]:
                array_size_ = get_integer_literal_value(array_size, "Array size")
                element_wtype = item_type.produces()
                self.wtype = arc4_util.make_static_array_wtype(
                    element_wtype, array_size_, location
                )
                return self
            case _:
                raise CodeError(
                    "Invalid type arguments for StaticArray. "
                    "Expected StaticArray[ItemType, typing.Literal[n]]",
                    location,
                )

    def call(
        self,
        args: Sequence[NodeBuilder | Literal],
        arg_typs: Sequence[pytypes.PyType],
        arg_kinds: list[mypy.nodes.ArgKind],
        arg_names: list[str | None],
        location: SourceLocation,
    ) -> NodeBuilder:
        non_literal_args = [
            require_expression_builder(a, msg="Array arguments must be non literals").rvalue()
            for a in args
        ]
        wtype = self.wtype
        if wtype is None:
            if non_literal_args:
                element_wtype = non_literal_args[0].wtype
                array_size = len(non_literal_args)
                wtype = arc4_util.make_static_array_wtype(element_wtype, array_size, location)
            else:
                raise CodeError(
                    "Empty arrays require a type annotation to be instantiated", location
                )
        elif wtype.array_size != len(non_literal_args):
            raise CodeError(
                f"StaticArray should be initialized with {wtype.array_size} values",
                location,
            )

        for a in non_literal_args:
            expect_operand_wtype(a, wtype.element_type)

        return StaticArrayExpressionBuilder(
            NewArray(
                source_location=location,
                values=tuple(non_literal_args),
                wtype=wtype,
            )
        )


class AddressClassExpressionBuilder(StaticArrayClassExpressionBuilder):
    wtype: wtypes.ARC4StaticArray

    def __init__(self, location: SourceLocation):
        super().__init__(location=location, wtype=wtypes.arc4_address_type)

    @typing.override
    def call(
        self,
        args: Sequence[NodeBuilder | Literal],
        arg_typs: Sequence[pytypes.PyType],
        arg_kinds: list[mypy.nodes.ArgKind],
        arg_names: list[str | None],
        location: SourceLocation,
    ) -> NodeBuilder:
        match args:
            case []:
                const_op = intrinsic_factory.zero_address(location, as_type=self.wtype)
                return AddressExpressionBuilder(const_op)
            case [InstanceBuilder(pytype=pytypes.AccountType) as eb]:
                address_bytes: Expression = get_bytes_expr(eb.rvalue())
            case [Literal(value=str(addr_value))]:
                if not wtypes.valid_address(addr_value):
                    raise CodeError(
                        f"Invalid address value. Address literals should be"
                        f" {ENCODED_ADDRESS_LENGTH} characters and not include base32 padding",
                        location,
                    )
                address_bytes = AddressConstant(value=addr_value, source_location=location)
            case [InstanceBuilder(pytype=pytypes.BytesType) as eb]:
                value = eb.rvalue()
                address_bytes_temp = SingleEvaluation(value)
                is_correct_length = NumericComparisonExpression(
                    operator=NumericComparison.eq,
                    source_location=location,
                    lhs=UInt64Constant(value=32, source_location=location),
                    rhs=intrinsic_factory.bytes_len(address_bytes_temp, location),
                )
                address_bytes = CheckedMaybe.from_tuple_items(
                    expr=address_bytes_temp,
                    check=is_correct_length,
                    source_location=location,
                    comment="Address length is 32 bytes",
                )
            case _:
                raise CodeError(
                    "Address constructor expects a single argument of type"
                    f" {wtypes.account_wtype} or {wtypes.bytes_wtype}, or a string literal",
                    location=location,
                )
        assert self.wtype, "wtype should not be None"
        return StaticArrayExpressionBuilder(
            ReinterpretCast(expr=address_bytes, wtype=self.wtype, source_location=location)
        )

    def index_multiple(
        self, indexes: Sequence[NodeBuilder | Literal], location: SourceLocation
    ) -> NodeBuilder:
        raise CodeError(
            "Address does not support type arguments",
            location,
        )


class ARC4ArrayExpressionBuilder(ValueExpressionBuilder[pytypes.ArrayType], ABC):
    def __init__(self, typ: pytypes.PyType, expr: Expression):
        assert isinstance(typ, pytypes.ArrayType)
        super().__init__(typ, expr)

    @typing.override
    def iterate(self) -> Iteration:
        if not self.pytype.wtype.element_type.immutable:
            logger.error(
                "Cannot directly iterate an ARC4 array of mutable objects,"
                " construct a for-loop over the indexes via urange(<array>.length) instead",
                location=self.source_location,
            )
        return self.rvalue()

    @typing.override
    def index(self, index: NodeBuilder | Literal, location: SourceLocation) -> NodeBuilder:
        if isinstance(index, Literal) and isinstance(index.value, int) and index.value < 0:
            index_expr: Expression = UInt64BinaryOperation(
                left=expect_operand_wtype(
                    self.member_access("length", index.source_location), wtypes.uint64_wtype
                ),
                op=UInt64BinaryOperator.sub,
                right=UInt64Constant(
                    value=abs(index.value), source_location=index.source_location
                ),
                source_location=index.source_location,
            )
        else:
            index_expr = expect_operand_wtype(index, wtypes.uint64_wtype)
        return var_expression(
            IndexExpression(
                source_location=location,
                base=self.expr,
                index=index_expr,
                wtype=self.wtype.element_type,
            )
        )

    @typing.override
    def member_access(self, name: str, location: SourceLocation) -> NodeBuilder | Literal:
        match name:
            case "bytes":
                return get_bytes_expr_builder(self.expr)
            case "copy":
                return CopyBuilder(self.expr, location)
            case _:
                return super().member_access(name, location)

    @typing.override
    def compare(
        self, other: InstanceBuilder | Literal, op: BuilderComparisonOp, location: SourceLocation
    ) -> NodeBuilder:
        return arc4_compare_bytes(self, op, other, location)


class DynamicArrayExpressionBuilder(ARC4ArrayExpressionBuilder):
    @typing.override
    def member_access(self, name: str, location: SourceLocation) -> NodeBuilder | Literal:
        match name:
            case "length":
                return UInt64ExpressionBuilder(
                    IntrinsicCall(
                        op_code="extract_uint16",
                        stack_args=[self.expr, UInt64Constant(value=0, source_location=location)],
                        source_location=location,
                        wtype=wtypes.uint64_wtype,
                    )
                )
            case "append":
                return AppendExpressionBuilder(self.expr, location)
            case "extend":
                return ExtendExpressionBuilder(self.expr, location)
            case "pop":
                return PopExpressionBuilder(self.expr, location)
            case _:
                return super().member_access(name, location)

    @typing.override
    def augmented_assignment(
        self, op: BuilderBinaryOp, rhs: InstanceBuilder | Literal, location: SourceLocation
    ) -> Statement:
        match op:
            case BuilderBinaryOp.add:
                return ExpressionStatement(
                    expr=ArrayExtend(
                        base=self.expr,
                        other=match_array_concat_arg(
                            (rhs,),
                            self.wtype.element_type,
                            source_location=location,
                            msg="Array concat expects array or tuple of the same element type. "
                            f"Element type: {self.wtype.element_type}",
                        ),
                        source_location=location,
                        wtype=wtypes.arc4_string_wtype,
                    )
                )
            case _:
                return super().augmented_assignment(op, rhs, location)

    @typing.override
    def binary_op(
        self,
        other: InstanceBuilder | Literal,
        op: BuilderBinaryOp,
        location: SourceLocation,
        *,
        reverse: bool,
    ) -> InstanceBuilder:
        match op:
            case BuilderBinaryOp.add:
                lhs = self.expr
                rhs = match_array_concat_arg(
                    (other,),
                    self.wtype.element_type,
                    source_location=location,
                    msg="Array concat expects array or tuple of the same element type. "
                    f"Element type: {self.wtype.element_type}",
                )

                if reverse:
                    (lhs, rhs) = (rhs, lhs)
                return DynamicArrayExpressionBuilder(
                    ArrayConcat(
                        left=lhs,
                        right=rhs,
                        source_location=location,
                        wtype=self.wtype,
                    )
                )

            case _:
                return super().binary_op(other, op, location, reverse=reverse)

    @typing.override
    def bool_eval(self, location: SourceLocation, *, negate: bool = False) -> InstanceBuilder:
        return arc4_bool_bytes(
            expr=self.expr,
            false_bytes=b"\x00\x00",
            location=location,
            negate=negate,
        )


class AppendExpressionBuilder(FunctionBuilder):
    def __init__(self, expr: Expression, location: SourceLocation):
        super().__init__(location)
        self.expr = expr
        if not isinstance(expr.wtype, wtypes.ARC4DynamicArray):
            raise InternalError(
                "AppendExpressionBuilder can only be instantiated with an arc4.DynamicArray"
            )
        self.wtype: wtypes.ARC4DynamicArray = expr.wtype

    @typing.override
    def call(
        self,
        args: Sequence[NodeBuilder | Literal],
        arg_typs: Sequence[pytypes.PyType],
        arg_kinds: list[mypy.nodes.ArgKind],
        arg_names: list[str | None],
        location: SourceLocation,
    ) -> NodeBuilder:

        args_expr = [expect_arc4_operand_wtype(a, self.wtype.element_type) for a in args]
        args_tuple = TupleExpression.from_items(args_expr, location)
        return VoidExpressionBuilder(
            ArrayExtend(
                base=self.expr,
                other=args_tuple,
                source_location=location,
                wtype=wtypes.void_wtype,
            )
        )


class PopExpressionBuilder(FunctionBuilder):
    def __init__(self, expr: Expression, location: SourceLocation):
        super().__init__(location)
        self.expr = expr
        if not isinstance(expr.wtype, wtypes.ARC4DynamicArray):
            raise InternalError(
                "AppendExpressionBuilder can only be instantiated with an arc4.DynamicArray"
            )
        self.wtype: wtypes.ARC4DynamicArray = expr.wtype

    @typing.override
    def call(
        self,
        args: Sequence[NodeBuilder | Literal],
        arg_typs: Sequence[pytypes.PyType],
        arg_kinds: list[mypy.nodes.ArgKind],
        arg_names: list[str | None],
        location: SourceLocation,
    ) -> NodeBuilder:
        match args:
            case []:
                return var_expression(
                    ArrayPop(
                        base=self.expr, source_location=location, wtype=self.wtype.element_type
                    )
                )
            case _:
                raise CodeError("Invalid/Unhandled arguments", location)


class ExtendExpressionBuilder(FunctionBuilder):
    def __init__(self, expr: Expression, location: SourceLocation):
        super().__init__(location)
        self.expr = expr
        if not isinstance(expr.wtype, wtypes.ARC4DynamicArray):
            raise InternalError(
                "AppendExpressionBuilder can only be instantiated with an arc4.DynamicArray"
            )
        self.wtype: wtypes.ARC4DynamicArray = expr.wtype

    @typing.override
    def call(
        self,
        args: Sequence[NodeBuilder | Literal],
        arg_typs: Sequence[pytypes.PyType],
        arg_kinds: list[mypy.nodes.ArgKind],
        arg_names: list[str | None],
        location: SourceLocation,
    ) -> NodeBuilder:
        other = match_array_concat_arg(
            args,
            self.wtype.element_type,
            source_location=location,
            msg="Extend expects an arc4.StaticArray or arc4.DynamicArray of the same element "
            f"type. Expected array or tuple of {self.wtype.element_type}",
        )
        return VoidExpressionBuilder(
            ArrayExtend(
                base=self.expr,
                other=other,
                source_location=location,
                wtype=wtypes.void_wtype,
            )
        )


def match_array_concat_arg(
    args: Sequence[NodeBuilder | Literal],
    element_type: wtypes.WType,
    *,
    source_location: SourceLocation,
    msg: str,
) -> Expression:
    match args:
        case (NodeBuilder() as eb,):
            expr = eb.rvalue()
            match expr:
                case Expression(wtype=wtypes.ARC4Array() as array_wtype) as array_ex:
                    if array_wtype.element_type == element_type:
                        return array_ex
                case Expression(wtype=wtypes.WTuple() as tuple_wtype) as tuple_ex:
                    if all(et == element_type for et in tuple_wtype.types):
                        return tuple_ex
    raise CodeError(msg, source_location)


class StaticArrayExpressionBuilder(ARC4ArrayExpressionBuilder):
    def __init__(self, expr: Expression):
        assert isinstance(expr.wtype, wtypes.ARC4StaticArray)
        self.wtype: wtypes.ARC4StaticArray = expr.wtype
        super().__init__(expr)

    def member_access(self, name: str, location: SourceLocation) -> NodeBuilder | Literal:
        match name:
            case "length":
                return UInt64ExpressionBuilder(
                    UInt64Constant(value=self.wtype.array_size, source_location=location)
                )
            case _:
                return super().member_access(name, location)

    def bool_eval(self, location: SourceLocation, *, negate: bool = False) -> NodeBuilder:
        if self.wtype.alias != "address":
            return bool_eval_to_constant(
                value=self.wtype.array_size > 0, location=location, negate=negate
            )
        else:
            cmp_with_zero_expr = BytesComparisonExpression(
                lhs=get_bytes_expr(self.expr),
                operator=EqualityComparison.eq if negate else EqualityComparison.ne,
                rhs=intrinsic_factory.zero_address(location, as_type=wtypes.bytes_wtype),
                source_location=location,
            )

            return BoolExpressionBuilder(cmp_with_zero_expr)

    def compare(
        self, other: NodeBuilder | Literal, op: BuilderComparisonOp, location: SourceLocation
    ) -> NodeBuilder:
        if self.wtype.alias != "address":
            return super().compare(other, op=op, location=location)
        match other:
            case Literal(value=str(str_value), source_location=literal_loc):
                rhs = get_bytes_expr(AddressConstant(value=str_value, source_location=literal_loc))
            case NodeBuilder(value_type=wtypes.account_wtype):
                rhs = get_bytes_expr(other.rvalue())
            case _:
                return super().compare(other, op=op, location=location)
        cmp_expr = BytesComparisonExpression(
            source_location=location,
            lhs=get_bytes_expr(self.expr),
            operator=EqualityComparison(op.value),
            rhs=rhs,
        )
        return BoolExpressionBuilder(cmp_expr)


class AddressExpressionBuilder(StaticArrayExpressionBuilder):
    def member_access(self, name: str, location: SourceLocation) -> NodeBuilder | Literal:
        match name:
            case "native":
                return AccountExpressionBuilder(
                    ReinterpretCast(
                        expr=self.expr, wtype=wtypes.account_wtype, source_location=location
                    )
                )
            case _:
                return super().member_access(name, location)
