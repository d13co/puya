from __future__ import annotations

import enum
import itertools
import typing as t
from abc import ABC, abstractmethod
from collections.abc import Iterator, Mapping, Sequence
from functools import cached_property

import attrs
from immutabledict import immutabledict

from puya.awst import wtypes
from puya.awst.wtypes import WType
from puya.errors import CodeError, InternalError

if t.TYPE_CHECKING:
    import decimal

    from puya.awst.visitors import (
        ExpressionVisitor,
        ModuleStatementVisitor,
        StatementVisitor,
    )
    from puya.models import ARC4MethodConfig
    from puya.parse import SourceLocation
    from puya.utils import StableSet

T = t.TypeVar("T")

ConstantValue: t.TypeAlias = int | str | bytes | bool


@attrs.frozen
class Node:
    source_location: SourceLocation


@attrs.frozen
class Statement(Node, ABC):
    @abstractmethod
    def accept(self, visitor: StatementVisitor[T]) -> T: ...


@attrs.frozen
class Expression(Node, ABC):
    wtype: WType

    @abstractmethod
    def accept(self, visitor: ExpressionVisitor[T]) -> T: ...


@attrs.frozen(init=False)
class ExpressionStatement(Statement):
    expr: Expression

    def __init__(self, expr: Expression):
        self.__attrs_init__(expr=expr, source_location=expr.source_location)

    def accept(self, visitor: StatementVisitor[T]) -> T:
        return visitor.visit_expression_statement(self)


@attrs.frozen(repr=False)
class _ExpressionHasWType:
    instances: tuple[WType, ...]
    types: tuple[type[WType], ...]

    def __call__(
        self,
        inst: Node,
        attr: attrs.Attribute,  # type: ignore[type-arg]
        value: Expression,
    ) -> None:
        """
        We use a callable class to be able to change the ``__repr__``.
        """
        wtype = value.wtype
        if wtype in self.instances:
            return
        for allowed_t in self.types:
            if isinstance(wtype, allowed_t):
                return
        raise InternalError(
            f"{type(inst).__name__}.{attr.name}: expression of WType {wtype} received,"
            f" expected {' or '.join(self._names)}"
        )

    def __repr__(self) -> str:
        return f"<expression_has_wtype validator for type {' | '.join(self._names)}>"

    @property
    def _names(self) -> Iterator[str]:
        for inst in self.instances:
            yield inst.name
        for typ in self.types:
            yield typ.__name__


def expression_has_wtype(*one_of_these: WType | type[WType]) -> _ExpressionHasWType:
    instances = []
    types = list[type[WType]]()
    for item in one_of_these:
        if isinstance(item, type):
            types.append(item)
        else:
            instances.append(item)
    return _ExpressionHasWType(instances=tuple(instances), types=tuple(types))


@attrs.frozen(repr=False)
class _WTypeIsOneOf:
    instances: tuple[WType, ...]
    types: tuple[type[WType], ...]

    def __call__(
        self,
        inst: Node,
        attr: attrs.Attribute,  # type: ignore[type-arg]
        value: WType,
    ) -> None:
        """
        We use a callable class to be able to change the ``__repr__``.
        """
        wtype = value
        if wtype in self.instances:
            return
        for allowed_t in self.types:
            if isinstance(wtype, allowed_t):
                return
        raise InternalError(
            f"{type(inst).__name__}.{attr.name}: set to {wtype},"
            f" expected {' or '.join(self._names)}"
        )

    def __repr__(self) -> str:
        return f"<expression_has_wtype validator for type {' | '.join(self._names)}>"

    @property
    def _names(self) -> Iterator[str]:
        for inst in self.instances:
            yield inst.name
        for typ in self.types:
            yield typ.__name__


def wtype_is_one_of(*one_of_these: WType | type[WType]) -> _WTypeIsOneOf:
    instances = []
    types = list[type[WType]]()
    for item in one_of_these:
        if isinstance(item, type):
            types.append(item)
        else:
            instances.append(item)
    return _WTypeIsOneOf(instances=tuple(instances), types=tuple(types))


wtype_is_uint64 = expression_has_wtype(wtypes.uint64_wtype)
wtype_is_biguint = expression_has_wtype(wtypes.biguint_wtype)
wtype_is_bool = expression_has_wtype(wtypes.bool_wtype)
wtype_is_bytes = expression_has_wtype(wtypes.bytes_wtype)


@attrs.frozen
class Literal(Node):
    """These shouldn't appear in the final AWST.

    They are temporarily constructed during evaluation of sub-expressions, when we encounter
    a literal in the native language (ie Python), and don't have the context to give it a wtype yet

    For example, consider the int literal 42 (randomly selected by fair roll of D100) in the
    following:

        x = algopy.UInt(42)
        x += 42
        y = algopy.BigUInt(42)
        z = algopy.InnerTransactionGroup.sender(42)


    The "type" of 42 in each of these is different.
    For BigUInt, since we know the value at compile time, we wouldn't want to emit a
        push 42
        itob
    Since we can just encode it ourselves and push the result to the stack instead.
    For InnerTransactionGroup.sender - this is actually not of any type, it must end up as a
    literal in the TEAL code itself.
    The type when adding to x should resolve to the UInt64 type, but only because it's in the
    context of an augmented assignment.

    So when we are visiting and arbitrary expression and encounter just a literal expression,
    we need the surrounding context. To avoid having to repeat the transformation of the mypy
    node in every context we could encounter one, we just return this Literal type instead,
    which has no wtype. But it must be resolved before being used at the "outermost level"
    of the current expression/statement, thus this Literal should not end up in the final AWST.

    See also: require_non_literal, for a quick way to ensure that we do indeed have an expression
    in cases where any Literals should have already been resolved.
    """

    value: ConstantValue


@attrs.frozen
class Block(Statement):
    body: Sequence[Statement] = attrs.field(converter=tuple[Statement, ...])
    description: str | None = None

    def accept(self, visitor: StatementVisitor[T]) -> T:
        return visitor.visit_block(self)


@attrs.frozen
class IfElse(Statement):
    condition: Expression = attrs.field(validator=[wtype_is_bool])
    if_branch: Block
    else_branch: Block | None

    def accept(self, visitor: StatementVisitor[T]) -> T:
        return visitor.visit_if_else(self)


@attrs.frozen
class Switch(Statement):
    value: Expression
    cases: Mapping[Expression, Block] = attrs.field(converter=immutabledict)
    default_case: Block | None

    def accept(self, visitor: StatementVisitor[T]) -> T:
        return visitor.visit_switch(self)


@attrs.frozen
class WhileLoop(Statement):
    condition: Expression = attrs.field(validator=[wtype_is_bool])
    loop_body: Block

    def accept(self, visitor: StatementVisitor[T]) -> T:
        return visitor.visit_while_loop(self)


@attrs.frozen
class BreakStatement(Statement):
    def accept(self, visitor: StatementVisitor[T]) -> T:
        return visitor.visit_break_statement(self)


@attrs.frozen
class ContinueStatement(Statement):
    def accept(self, visitor: StatementVisitor[T]) -> T:
        return visitor.visit_continue_statement(self)


@attrs.frozen
class AssertStatement(Statement):
    condition: Expression = attrs.field(validator=[wtype_is_bool])
    comment: str | None

    def accept(self, visitor: StatementVisitor[T]) -> T:
        return visitor.visit_assert_statement(self)


@attrs.frozen
class ReturnStatement(Statement):
    value: Expression | None

    def accept(self, visitor: StatementVisitor[T]) -> T:
        return visitor.visit_return_statement(self)


def _validate_literal(value: object, wtype: WType, source_location: SourceLocation) -> None:
    if not wtype.is_valid_literal(value):
        raise CodeError(f"Invalid {wtype} value: {value!r}", source_location)


def literal_validator(wtype: WType) -> t.Callable[[Node, object, t.Any], None]:
    def validate(node: Node, _attribute: object, value: object) -> None:
        if not isinstance(node, Node):
            raise InternalError(
                f"literal_validator used on type {type(node).__name__}, expected Node"
            )
        _validate_literal(value, wtype, node.source_location)

    return validate


@attrs.frozen(kw_only=True)
class IntegerConstant(Expression):
    wtype: WType = attrs.field(
        validator=[
            wtype_is_one_of(
                wtypes.uint64_wtype,
                wtypes.biguint_wtype,
                wtypes.ARC4UIntN,
            )
        ]
    )
    value: int = attrs.field()
    teal_alias: str | None = None

    @value.validator
    def check(self, _attribute: object, value: int) -> None:
        _validate_literal(value, self.wtype, self.source_location)

    def accept(self, visitor: ExpressionVisitor[T]) -> T:
        return visitor.visit_integer_constant(self)


@attrs.frozen
class DecimalConstant(Expression):
    wtype: wtypes.ARC4UFixedNxM
    value: decimal.Decimal = attrs.field()

    @value.validator
    def check(self, _attribute: object, value: int) -> None:
        _validate_literal(value, self.wtype, self.source_location)

    def accept(self, visitor: ExpressionVisitor[T]) -> T:
        return visitor.visit_decimal_constant(self)


def UInt64Constant(  # noqa: N802
    *, source_location: SourceLocation, value: int, teal_alias: str | None = None
) -> IntegerConstant:
    return IntegerConstant(
        source_location=source_location,
        value=value,
        wtype=wtypes.uint64_wtype,
        teal_alias=teal_alias,
    )


def BigUIntConstant(  # noqa: N802
    *, source_location: SourceLocation, value: int
) -> IntegerConstant:
    return IntegerConstant(
        source_location=source_location,
        value=value,
        wtype=wtypes.biguint_wtype,
    )


@attrs.frozen
class BoolConstant(Expression):
    wtype: WType = attrs.field(default=wtypes.bool_wtype, init=False)
    value: bool = attrs.field(validator=[literal_validator(wtypes.bool_wtype)])

    def accept(self, visitor: ExpressionVisitor[T]) -> T:
        return visitor.visit_bool_constant(self)


@enum.unique
class BytesEncoding(enum.StrEnum):
    unknown = enum.auto()
    base16 = enum.auto()
    base32 = enum.auto()
    base64 = enum.auto()
    utf8 = enum.auto()


@attrs.frozen
class BytesConstant(Expression):
    wtype: WType = attrs.field(default=wtypes.bytes_wtype, init=False)
    value: bytes = attrs.field(validator=[literal_validator(wtypes.bytes_wtype)])
    encoding: BytesEncoding = attrs.field(default=BytesEncoding.utf8)

    def accept(self, visitor: ExpressionVisitor[T]) -> T:
        return visitor.visit_bytes_constant(self)


@attrs.frozen
class StringConstant(Expression):
    wtype: WType = attrs.field(default=wtypes.string_wtype, init=False)
    value: str = attrs.field(validator=[literal_validator(wtypes.string_wtype)])

    def accept(self, visitor: ExpressionVisitor[T]) -> T:
        return visitor.visit_string_constant(self)


@attrs.frozen
class TemplateVar(Expression):
    wtype: WType
    name: str

    def accept(self, visitor: ExpressionVisitor[T]) -> T:
        return visitor.visit_template_var(self)


@attrs.frozen
class MethodConstant(Expression):
    wtype: WType = attrs.field(default=wtypes.bytes_wtype, init=False)
    value: str

    def accept(self, visitor: ExpressionVisitor[T]) -> T:
        return visitor.visit_method_constant(self)


@attrs.frozen
class AddressConstant(Expression):
    wtype: WType = attrs.field(default=wtypes.account_wtype, init=False)
    value: str = attrs.field(validator=[literal_validator(wtypes.account_wtype)])

    def accept(self, visitor: ExpressionVisitor[T]) -> T:
        return visitor.visit_address_constant(self)


@attrs.frozen
class ARC4Encode(Expression):
    value: Expression
    wtype: wtypes.ARC4Type = attrs.field(
        validator=wtype_is_one_of(
            wtypes.ARC4UIntN,
            wtypes.ARC4UFixedNxM,
            wtypes.ARC4Tuple,
            wtypes.arc4_string_wtype,
            wtypes.arc4_bool_wtype,
            wtypes.arc4_dynamic_bytes,
            wtypes.arc4_address_type,
        )
    )

    def accept(self, visitor: ExpressionVisitor[T]) -> T:
        return visitor.visit_arc4_encode(self)


@attrs.frozen
class Copy(Expression):
    """
    Create a new copy of 'value'
    """

    value: Expression

    def accept(self, visitor: ExpressionVisitor[T]) -> T:
        return visitor.visit_copy(self)


@attrs.frozen
class ArrayConcat(Expression):
    """
    Given 'left' or 'right' that is logically an array - concat it with the other value which is
    an iterable type with the same element type
    """

    left: Expression
    right: Expression

    def accept(self, visitor: ExpressionVisitor[T]) -> T:
        return visitor.visit_array_concat(self)


@attrs.frozen
class ArrayPop(Expression):
    base: Expression

    def accept(self, visitor: ExpressionVisitor[T]) -> T:
        return visitor.visit_array_pop(self)


@attrs.frozen
class ArrayExtend(Expression):
    """
    Given 'base' that is logically an array - extend it with 'other' which is an iterable type with
    the same element type
    """

    base: Expression
    other: Expression

    def accept(self, visitor: ExpressionVisitor[T]) -> T:
        return visitor.visit_array_extend(self)


@attrs.frozen
class ARC4Decode(Expression):
    value: Expression

    def accept(self, visitor: ExpressionVisitor[T]) -> T:
        return visitor.visit_arc4_decode(self)


CompileTimeConstantExpression: t.TypeAlias = (
    IntegerConstant
    | DecimalConstant
    | BoolConstant
    | BytesConstant
    | AddressConstant
    | MethodConstant
)


@attrs.define
class IntrinsicCall(Expression):
    op_code: str
    immediates: Sequence[str | int] = attrs.field(default=(), converter=tuple[str | int, ...])
    stack_args: Sequence[Expression] = attrs.field(default=(), converter=tuple[Expression, ...])

    def accept(self, visitor: ExpressionVisitor[T]) -> T:
        return visitor.visit_intrinsic_call(self)


WTypes: t.TypeAlias = Sequence[WType | type[WType]]


@attrs.frozen(kw_only=True)
class TxnField:
    wtype: WType
    additional_input_wtypes: WTypes = ()
    """Other wtypes that are valid as inputs e.g. UInt64 for an Application field"""
    immediate: str
    num_values: int = attrs.field(default=1, validator=attrs.validators.ge(1))
    is_inner_param: bool = True

    @property
    def is_array(self) -> bool:
        return self.num_values > 1

    def valid_type(self, wtype: WType) -> bool:
        all_types = (self.wtype, *self.additional_input_wtypes)
        wtype_types = tuple(x for x in all_types if isinstance(x, type))
        return wtype in all_types or isinstance(wtype, wtype_types)

    @property
    def type_desc(self) -> str:
        return " | ".join(map(str, (self.wtype, *self.additional_input_wtypes)))

    @classmethod
    def uint64(cls, immediate: str, *, is_inner_param: bool = True) -> TxnField:
        return cls(
            wtype=wtypes.uint64_wtype,
            immediate=immediate,
            is_inner_param=is_inner_param,
        )

    @classmethod
    def bytes_(
        cls,
        immediate: str,
        *,
        is_inner_param: bool = True,
        num_values: int = 1,
        additional_input_wtypes: WTypes = (),
    ) -> TxnField:
        return cls(
            wtype=wtypes.bytes_wtype,
            immediate=immediate,
            is_inner_param=is_inner_param,
            num_values=num_values,
            additional_input_wtypes=additional_input_wtypes,
        )

    @classmethod
    def bool_(cls, immediate: str) -> TxnField:
        return cls(
            wtype=wtypes.bool_wtype,
            immediate=immediate,
            additional_input_wtypes=(wtypes.uint64_wtype,),
        )

    @classmethod
    def account(cls, immediate: str, *, num_values: int = 1) -> TxnField:
        return cls(
            wtype=wtypes.account_wtype,
            immediate=immediate,
            num_values=num_values,
            additional_input_wtypes=(wtypes.bytes_wtype,),
        )

    @classmethod
    def asset(
        cls, immediate: str, *, is_inner_param: bool = True, num_values: int = 1
    ) -> TxnField:
        return cls(
            wtype=wtypes.asset_wtype,
            immediate=immediate,
            is_inner_param=is_inner_param,
            num_values=num_values,
            additional_input_wtypes=(wtypes.uint64_wtype,),
        )

    @classmethod
    def application(
        cls, immediate: str, *, is_inner_param: bool = True, num_values: int = 1
    ) -> TxnField:
        return cls(
            wtype=wtypes.application_wtype,
            immediate=immediate,
            is_inner_param=is_inner_param,
            num_values=num_values,
            additional_input_wtypes=(wtypes.uint64_wtype,),
        )


class TxnFields:
    approval_program_pages = TxnField.bytes_("ApprovalProgramPages", num_values=4)
    clear_state_program_pages = TxnField.bytes_("ClearStateProgramPages", num_values=4)
    fee = TxnField.uint64("Fee")
    type = TxnField.uint64("TypeEnum")
    app_args = TxnField.bytes_(
        immediate="ApplicationArgs",
        num_values=16,
        additional_input_wtypes=(
            wtypes.biguint_wtype,
            wtypes.account_wtype,
            wtypes.ARC4Type,
        ),
    )
    accounts = TxnField.account("Accounts", num_values=4)
    assets = TxnField.asset("Assets", num_values=8)
    apps = TxnField.application("Applications", num_values=8)
    last_log = TxnField.bytes_("LastLog", is_inner_param=False)


TXN_FIELDS = [
    TxnField.account("Sender"),
    TxnFields.fee,
    TxnField.uint64("FirstValid", is_inner_param=False),
    TxnField.uint64("FirstValidTime", is_inner_param=False),
    TxnField.uint64("LastValid", is_inner_param=False),
    TxnField.bytes_("Note", additional_input_wtypes=(wtypes.string_wtype,)),
    TxnField.bytes_("Lease", is_inner_param=False),
    TxnField.account("Receiver"),
    TxnField.uint64("Amount"),
    TxnField.account("CloseRemainderTo"),
    TxnField.bytes_("VotePK"),
    TxnField.bytes_("SelectionPK"),
    TxnField.uint64("VoteFirst"),
    TxnField.uint64("VoteLast"),
    TxnField.uint64("VoteKeyDilution"),
    TxnField.bytes_("Type"),
    TxnFields.type,
    TxnField.asset("XferAsset"),
    TxnField.uint64("AssetAmount"),
    TxnField.account("AssetSender"),
    TxnField.account("AssetReceiver"),
    TxnField.account("AssetCloseTo"),
    TxnField.uint64("GroupIndex", is_inner_param=False),
    TxnField.bytes_("TxID", is_inner_param=False),
    # v2
    TxnField.application("ApplicationID"),
    TxnField.uint64("OnCompletion"),
    TxnField.uint64("NumAppArgs", is_inner_param=False),
    TxnField.uint64("NumAccounts", is_inner_param=False),
    TxnField.bytes_("ApprovalProgram"),
    TxnField.bytes_("ClearStateProgram"),
    TxnField.account("RekeyTo"),
    TxnField.asset("ConfigAsset"),
    TxnField.uint64("ConfigAssetTotal"),
    TxnField.uint64("ConfigAssetDecimals"),
    TxnField.bool_("ConfigAssetDefaultFrozen"),
    TxnField.bytes_("ConfigAssetUnitName", additional_input_wtypes=(wtypes.string_wtype,)),
    TxnField.bytes_("ConfigAssetName", additional_input_wtypes=(wtypes.string_wtype,)),
    TxnField.bytes_("ConfigAssetURL", additional_input_wtypes=(wtypes.string_wtype,)),
    TxnField.bytes_("ConfigAssetMetadataHash"),
    TxnField.account("ConfigAssetManager"),
    TxnField.account("ConfigAssetReserve"),
    TxnField.account("ConfigAssetFreeze"),
    TxnField.account("ConfigAssetClawback"),
    TxnField.asset("FreezeAsset"),
    TxnField.account("FreezeAssetAccount"),
    TxnField.bool_("FreezeAssetFrozen"),
    # v3
    TxnField.uint64("NumAssets", is_inner_param=False),
    TxnField.uint64("NumApplications", is_inner_param=False),
    TxnField.uint64("GlobalNumUint"),
    TxnField.uint64("GlobalNumByteSlice"),
    TxnField.uint64("LocalNumUint"),
    TxnField.uint64("LocalNumByteSlice"),
    # v4
    TxnField.uint64("ExtraProgramPages"),
    # v5
    TxnField.bool_("Nonparticipation"),
    TxnField.uint64("NumLogs", is_inner_param=False),
    TxnField.asset("CreatedAssetID", is_inner_param=False),
    TxnField.application("CreatedApplicationID", is_inner_param=False),
    # v6
    TxnFields.last_log,
    TxnField.bytes_("StateProofPK"),
    # v7
    TxnField.uint64("NumApprovalProgramPages", is_inner_param=False),
    TxnField.uint64("NumClearStateProgramPages", is_inner_param=False),
    # array fields
    # TODO: allow configuring as these are consensus values
    # v2
    TxnFields.app_args,
    TxnFields.accounts,
    # v3
    TxnFields.assets,
    TxnFields.apps,
    # v5
    TxnField.bytes_("Logs", num_values=32, is_inner_param=False),
    # v7
    TxnFields.approval_program_pages,
    TxnFields.clear_state_program_pages,
]
TXN_FIELDS_BY_IMMEDIATE = {f.immediate: f for f in TXN_FIELDS}
INNER_PARAM_TXN_FIELDS = [f for f in TXN_FIELDS if f.is_inner_param]


@attrs.define
class CreateInnerTransaction(Expression):
    wtype: wtypes.WInnerTransactionFields
    fields: Mapping[TxnField, Expression] = attrs.field(converter=immutabledict)

    def accept(self, visitor: ExpressionVisitor[T]) -> T:
        return visitor.visit_create_inner_transaction(self)


@attrs.define
class UpdateInnerTransaction(Expression):
    itxn: Expression = attrs.field(validator=expression_has_wtype(wtypes.WInnerTransactionFields))
    fields: Mapping[TxnField, Expression] = attrs.field(converter=immutabledict)
    wtype: WType = attrs.field(default=wtypes.void_wtype, init=False)

    def accept(self, visitor: ExpressionVisitor[T]) -> T:
        return visitor.visit_update_inner_transaction(self)


@attrs.define(init=False)
class CheckedMaybe(Expression):
    """Allows evaluating a maybe type i.e. tuple[_T, bool] as _T, but with the assertion that
    the 2nd bool element is true"""

    expr: Expression
    comment: str

    def __init__(self, expr: Expression, comment: str) -> None:
        match expr.wtype:
            case wtypes.WTuple(types=(wtype, wtypes.bool_wtype)):
                pass
            case _:
                raise InternalError(
                    f"{type(self).__name__}.expr: expression of WType {expr.wtype} received,"
                    f" expected tuple[_T, bool]"
                )
        self.__attrs_init__(
            source_location=expr.source_location,
            expr=expr,
            comment=comment,
            wtype=wtype,
        )

    @classmethod
    def from_tuple_items(
        cls,
        expr: Expression,
        check: Expression,
        source_location: SourceLocation,
        comment: str,
    ) -> CheckedMaybe:
        if check.wtype != wtypes.bool_wtype:
            raise InternalError(
                "Check condition for CheckedMaybe should be a boolean", source_location
            )
        tuple_expr = TupleExpression.from_items((expr, check), source_location)
        return CheckedMaybe(expr=tuple_expr, comment=comment)

    def accept(self, visitor: ExpressionVisitor[T]) -> T:
        return visitor.visit_checked_maybe(self)


def lvalue_expr_validator(_instance: object, _attribute: object, value: Expression) -> None:
    if not value.wtype.lvalue:
        raise CodeError(
            f'expression with type "{value.wtype}" can not be assigned to a variable',
            value.source_location,
        )


@attrs.frozen
class TupleExpression(Expression):
    items: Sequence[Expression] = attrs.field(converter=tuple[Expression, ...])
    wtype: wtypes.WTuple

    @classmethod
    def from_items(cls, items: Sequence[Expression], location: SourceLocation) -> TupleExpression:
        return cls(
            items=items,
            wtype=wtypes.WTuple.from_types(i.wtype for i in items),
            source_location=location,
        )

    def accept(self, visitor: ExpressionVisitor[T]) -> T:
        return visitor.visit_tuple_expression(self)


@attrs.frozen(init=False)
class TupleItemExpression(Expression):
    """Represents tuple element access.

    Note: this is its own item (vs IndexExpression) for two reasons:
    1. It's not a valid lvalue (tuples are immutable)
    2. The index must always be a literal, and can be negative
    """

    base: Expression
    index: int

    def __init__(self, base: Expression, index: int, source_location: SourceLocation) -> None:
        base_wtype = base.wtype
        if not isinstance(base_wtype, wtypes.WTuple | wtypes.ARC4Tuple):
            raise InternalError(
                f"Tuple item expression should be for a tuple type, got {base_wtype}",
                source_location,
            )
        try:
            wtype = base_wtype.types[index]
        except IndexError as ex:
            raise CodeError("invalid index into tuple expression", source_location) from ex
        self.__attrs_init__(
            source_location=source_location,
            base=base,
            index=index,
            wtype=wtype,
        )

    def accept(self, visitor: ExpressionVisitor[T]) -> T:
        return visitor.visit_tuple_item_expression(self)


@attrs.frozen
class VarExpression(Expression):
    name: str

    def accept(self, visitor: ExpressionVisitor[T]) -> T:
        return visitor.visit_var_expression(self)


@attrs.define
class InnerTransactionField(Expression):
    itxn: Expression = attrs.field(validator=expression_has_wtype(wtypes.WInnerTransaction))
    field: TxnField
    array_index: Expression | None = attrs.field(default=None)

    @array_index.validator
    def _validate_array_index(self, _attribute: object, value: Expression | None) -> None:
        has_array = value is not None
        if has_array != self.field.is_array:
            raise InternalError(
                f"Inconsistent field and array_index combination: "
                f"{self.field} and {'' if has_array else 'no '} array provided",
                self.source_location,
            )

    def accept(self, visitor: ExpressionVisitor[T]) -> T:
        return visitor.visit_inner_transaction_field(self)


@attrs.define
class SubmitInnerTransaction(Expression):
    wtype: WType = attrs.field()
    itxns: tuple[Expression, ...] = attrs.field(
        validator=attrs.validators.deep_iterable(
            member_validator=expression_has_wtype(wtypes.WInnerTransactionFields)
        )
    )

    @wtype.validator
    def _validate_wtype(self, _attribute: object, value: WType) -> None:
        match value:
            case wtypes.WTuple(types=types):
                if any(not isinstance(t, wtypes.WInnerTransaction) for t in types) or len(
                    types
                ) != len(self.itxns):
                    raise InternalError(f"Expected a tuple[WInnerTransaction, ...] got: {value}")
            case wtypes.WInnerTransaction():
                num_params = len(self.itxns)
                if num_params != 1:
                    raise InternalError(
                        f"Expected a tuple[WInnerTransaction, ...] of length: {num_params}"
                    )
            case _:
                raise InternalError(f"Expected a WTuple or single WInnerTransaction, got: {value}")

    def accept(self, visitor: ExpressionVisitor[T]) -> T:
        return visitor.visit_submit_inner_transaction(self)


@attrs.frozen
class FieldExpression(Expression):
    base: Expression = attrs.field(
        validator=expression_has_wtype(wtypes.WStructType, wtypes.ARC4Struct)
    )
    name: str

    def accept(self, visitor: ExpressionVisitor[T]) -> T:
        return visitor.visit_field_expression(self)


@attrs.frozen
class IndexExpression(Expression):
    base: Expression = attrs.field(
        validator=expression_has_wtype(
            wtypes.bytes_wtype,
            wtypes.ARC4StaticArray,
            wtypes.ARC4DynamicArray,
            # NOTE: tuples (native or arc4) use TupleItemExpression instead
        )
    )
    index: Expression = attrs.field(validator=expression_has_wtype(wtypes.uint64_wtype))

    def accept(self, visitor: ExpressionVisitor[T]) -> T:
        return visitor.visit_index_expression(self)


@attrs.frozen
class SliceExpression(Expression):

    base: Expression = attrs.field(
        validator=expression_has_wtype(
            wtypes.bytes_wtype,
            wtypes.WTuple,
        )
    )

    begin_index: Expression | None
    end_index: Expression | None

    def accept(self, visitor: ExpressionVisitor[T]) -> T:
        return visitor.visit_slice_expression(self)


@attrs.frozen
class IntersectionSliceExpression(Expression):
    """
    Returns the intersection of the slice indexes and the base
    """

    base: Expression = attrs.field(
        validator=expression_has_wtype(
            wtypes.bytes_wtype,
            wtypes.WTuple,
        )
    )

    begin_index: Expression | int | None
    end_index: Expression | int | None

    def accept(self, visitor: ExpressionVisitor[T]) -> T:
        return visitor.visit_intersection_slice_expression(self)


@attrs.frozen
class AppStateExpression(Expression):
    field_name: str

    def accept(self, visitor: ExpressionVisitor[T]) -> T:
        return visitor.visit_app_state_expression(self)


@attrs.frozen
class AppAccountStateExpression(Expression):
    field_name: str
    account: Expression = attrs.field(
        validator=[expression_has_wtype(wtypes.account_wtype, wtypes.uint64_wtype)]
    )

    def accept(self, visitor: ExpressionVisitor[T]) -> T:
        return visitor.visit_app_account_state_expression(self)


@attrs.frozen(init=False, eq=False, hash=False)  # use identity equality
class SingleEvaluation(Expression):
    """caveat emptor"""

    source: Expression

    def __init__(self, source: Expression):
        self.__attrs_init__(
            source=source,
            source_location=source.source_location,
            wtype=source.wtype,
        )

    def __eq__(self, other: object) -> bool:
        return id(self) == id(other)

    def __hash__(self) -> int:
        return id(self)

    def accept(self, visitor: ExpressionVisitor[T]) -> T:
        return visitor.visit_single_evaluation(self)


@attrs.frozen
class ReinterpretCast(Expression):
    """Convert an expression to an AVM equivalent type.

    Note: the validation of this isn't done until IR construction"""

    expr: Expression

    def accept(self, visitor: ExpressionVisitor[T]) -> T:
        return visitor.visit_reinterpret_cast(self)


# Expression types that are valid on the left hand side of assignment *statements*
# Note that some of these can be recursive/nested, eg:
# obj.field[index].another_field = 123
Lvalue = (
    VarExpression
    | FieldExpression
    | IndexExpression
    | TupleExpression
    | AppStateExpression
    | AppAccountStateExpression
)


@attrs.frozen
class NewArray(Expression):
    wtype: wtypes.WArray | wtypes.ARC4Array
    values: Sequence[Expression] = attrs.field(default=(), converter=tuple[Expression, ...])

    @values.validator
    def _check_element_types(self, _attribute: object, value: tuple[Expression, ...]) -> None:
        if any(expr.wtype != self.wtype.element_type for expr in value):
            raise ValueError(
                f"All array elements should have array type: {self.wtype.element_type}"
            )

    def accept(self, visitor: ExpressionVisitor[T]) -> T:
        return visitor.visit_new_array(self)


@attrs.frozen
class ConditionalExpression(Expression):
    """A "ternary" operator with conditional evaluation - the true and false expressions must only
    be evaluated if they will be the result of expression.
    """

    condition: Expression = attrs.field(validator=[wtype_is_bool])
    true_expr: Expression
    false_expr: Expression

    def __attrs_post_init__(self) -> None:
        if self.true_expr.wtype != self.false_expr.wtype:
            raise ValueError(
                f"true and false expressions of conditional have differing types:"
                f" {self.true_expr.wtype} and {self.false_expr.wtype}"
            )

    def accept(self, visitor: ExpressionVisitor[T]) -> T:
        return visitor.visit_conditional_expression(self)


@attrs.frozen
class AssignmentStatement(Statement):
    """
    A single assignment statement e.g. `a = 1`.

    Multi-assignment statements like `a = b = 1` should be split in the AST pass.

    Will validate that target and value are of the same type, and that said type is usable
    as an l-value.
    """

    target: Lvalue
    value: Expression = attrs.field(validator=[lvalue_expr_validator])

    def __attrs_post_init__(self) -> None:
        if self.value.wtype != self.target.wtype:
            raise CodeError(
                f"Assignment target type {self.target.wtype}"
                f" differs from expression value type {self.value.wtype}",
                self.source_location,
            )

    def accept(self, visitor: StatementVisitor[T]) -> T:
        return visitor.visit_assignment_statement(self)


@attrs.frozen(init=False)
class AssignmentExpression(Expression):
    """
    This both assigns value to target and returns the target as the result of the expression.

    Note that tuple expressions aren't valid here as the target, but tuple variables obviously are.

    Will validate that target and value are of the same type, and that said type is usable
    as an l-value.
    """

    target: Lvalue  # annoyingly, we can't do Lvalue "minus" TupleExpression
    value: Expression = attrs.field(validator=[lvalue_expr_validator])

    def __init__(self, value: Expression, target: Lvalue, source_location: SourceLocation):
        if isinstance(target, TupleExpression):
            raise CodeError(
                "Tuple unpacking in assignment expressions is not supported",
                target.source_location,
            )
        if value.wtype != target.wtype:
            raise CodeError(
                f"Assignment target type {target.wtype}"
                f" differs from expression value type {value.wtype}",
                source_location,
            )
        self.__attrs_init__(
            source_location=source_location,
            target=target,
            value=value,
            wtype=target.wtype,
        )

    def accept(self, visitor: ExpressionVisitor[T]) -> T:
        return visitor.visit_assignment_expression(self)


class EqualityComparison(enum.StrEnum):
    eq = "=="
    ne = "!="


class NumericComparison(enum.StrEnum):
    eq = "=="  # 😩 why can't Python have enum inheritance
    ne = "!="
    lt = "<"
    lte = "<="
    gt = ">"
    gte = ">="


numeric_comparable = expression_has_wtype(
    wtypes.uint64_wtype,
    wtypes.biguint_wtype,
    wtypes.bool_wtype,
    wtypes.asset_wtype,
    wtypes.application_wtype,
)


@attrs.frozen
class NumericComparisonExpression(Expression):
    """Compare two numeric types.

    Any type promotion etc should be done at the source language level,
    this operation expects both arguments to already be in the same type.
    This is to insulate against language-specific differences in type promotion rules,
    or equality comparisons with bool, and so on.
    """

    wtype: WType = attrs.field(default=wtypes.bool_wtype, init=False)

    # TODO: make these names consistent with other expressions
    lhs: Expression = attrs.field(validator=[numeric_comparable])
    operator: NumericComparison
    rhs: Expression = attrs.field(validator=[numeric_comparable])

    def __attrs_post_init__(self) -> None:
        if self.lhs.wtype != self.rhs.wtype:
            raise InternalError(
                "numeric comparison between different wtypes:"
                f" {self.lhs.wtype} and {self.rhs.wtype}",
                self.source_location,
            )

    def accept(self, visitor: ExpressionVisitor[T]) -> T:
        return visitor.visit_numeric_comparison_expression(self)


bytes_comparable = expression_has_wtype(
    wtypes.bytes_wtype, wtypes.account_wtype, wtypes.string_wtype
)


@attrs.frozen
class BytesComparisonExpression(Expression):
    wtype: WType = attrs.field(default=wtypes.bool_wtype, init=False)

    lhs: Expression = attrs.field(validator=[bytes_comparable])
    operator: EqualityComparison
    rhs: Expression = attrs.field(validator=[bytes_comparable])

    def __attrs_post_init__(self) -> None:
        if self.lhs.wtype != self.rhs.wtype:
            raise InternalError(
                "bytes comparison between different wtypes:"
                f" {self.lhs.wtype} and {self.rhs.wtype}",
                self.source_location,
            )

    def accept(self, visitor: ExpressionVisitor[T]) -> T:
        return visitor.visit_bytes_comparison_expression(self)


@attrs.frozen
class ContractReference:
    module_name: str
    class_name: str

    @property
    def full_name(self) -> str:
        return ".".join((self.module_name, self.class_name))


@attrs.frozen
class InstanceSubroutineTarget:
    name: str


@attrs.frozen
class BaseClassSubroutineTarget:
    base_class: ContractReference
    name: str


@attrs.frozen
class FreeSubroutineTarget:
    module_name: str  # module name the subroutine resides in
    name: str  # name of the subroutine within the module


@attrs.frozen
class CallArg:
    name: str | None  # if None, then passed positionally
    value: Expression


SubroutineTarget = FreeSubroutineTarget | InstanceSubroutineTarget | BaseClassSubroutineTarget


@attrs.frozen
class SubroutineCallExpression(Expression):
    target: SubroutineTarget
    args: Sequence[CallArg] = attrs.field(converter=tuple[CallArg, ...])

    def accept(self, visitor: ExpressionVisitor[T]) -> T:
        return visitor.visit_subroutine_call_expression(self)


@enum.unique
class UInt64BinaryOperator(enum.StrEnum):
    add = "+"
    sub = "-"
    mult = "*"
    floor_div = "//"
    mod = "%"
    pow = "**"
    lshift = "<<"
    rshift = ">>"
    bit_or = "|"
    bit_xor = "^"
    bit_and = "&"
    # unsupported:
    # / aka ast.Div
    # @ aka ast.MatMult


@enum.unique
class BigUIntBinaryOperator(enum.StrEnum):
    add = "+"
    sub = "-"
    mult = "*"
    floor_div = "//"
    mod = "%"
    bit_or = "|"
    bit_xor = "^"
    bit_and = "&"
    # unsupported:
    # ** aka ast.Pow
    # / aka ast.Div
    # @ aka ast.MatMult
    # << aka ast.LShift
    # >> aka ast.RShift


@enum.unique
class BytesBinaryOperator(enum.StrEnum):
    add = "+"
    bit_or = "|"
    bit_xor = "^"
    bit_and = "&"


@enum.unique
class BytesUnaryOperator(enum.StrEnum):
    bit_invert = "~"


@enum.unique
class UInt64UnaryOperator(enum.StrEnum):
    bit_invert = "~"


@attrs.frozen
class UInt64UnaryOperation(Expression):
    op: UInt64UnaryOperator
    expr: Expression = attrs.field(validator=[wtype_is_uint64])
    wtype: WType = attrs.field(default=wtypes.uint64_wtype, init=False)

    def accept(self, visitor: ExpressionVisitor[T]) -> T:
        return visitor.visit_uint64_unary_operation(self)


@attrs.frozen
class BytesUnaryOperation(Expression):
    op: BytesUnaryOperator
    expr: Expression = attrs.field(validator=[wtype_is_bytes])
    wtype: WType = attrs.field(default=wtypes.bytes_wtype, init=False)

    def accept(self, visitor: ExpressionVisitor[T]) -> T:
        return visitor.visit_bytes_unary_operation(self)


@attrs.frozen
class UInt64BinaryOperation(Expression):
    left: Expression = attrs.field(validator=[wtype_is_uint64])
    op: UInt64BinaryOperator
    right: Expression = attrs.field(validator=[wtype_is_uint64])
    wtype: WType = attrs.field(default=wtypes.uint64_wtype, init=False)

    def accept(self, visitor: ExpressionVisitor[T]) -> T:
        return visitor.visit_uint64_binary_operation(self)


@attrs.frozen
class BigUIntBinaryOperation(Expression):
    left: Expression = attrs.field(validator=[wtype_is_biguint])
    op: BigUIntBinaryOperator
    right: Expression = attrs.field(validator=[wtype_is_biguint])
    wtype: WType = attrs.field(default=wtypes.biguint_wtype, init=False)

    def accept(self, visitor: ExpressionVisitor[T]) -> T:
        return visitor.visit_biguint_binary_operation(self)


@attrs.frozen
class BytesBinaryOperation(Expression):
    left: Expression = attrs.field(
        validator=[expression_has_wtype(wtypes.bytes_wtype, wtypes.string_wtype)]
    )
    op: BytesBinaryOperator
    right: Expression = attrs.field(
        validator=[expression_has_wtype(wtypes.bytes_wtype, wtypes.string_wtype)]
    )
    wtype: WType = attrs.field(init=False)

    @right.validator
    def _check_right(self, _attribute: object, right: Expression) -> None:
        if right.wtype != self.left.wtype:
            raise CodeError(
                f"Bytes operation on differing types,"
                f" lhs is {self.left.wtype}, rhs is {self.right.wtype}",
                self.source_location,
            )

    @wtype.default
    def _wtype_factory(self) -> wtypes.WType:
        return self.left.wtype

    def accept(self, visitor: ExpressionVisitor[T]) -> T:
        return visitor.visit_bytes_binary_operation(self)


@enum.unique
class BinaryBooleanOperator(enum.StrEnum):
    and_ = "and"
    or_ = "or"


@attrs.frozen
class BooleanBinaryOperation(Expression):
    left: Expression = attrs.field(validator=[wtype_is_bool])
    op: BinaryBooleanOperator
    right: Expression = attrs.field(validator=[wtype_is_bool])
    wtype: WType = attrs.field(default=wtypes.bool_wtype, init=False)

    def accept(self, visitor: ExpressionVisitor[T]) -> T:
        return visitor.visit_boolean_binary_operation(self)


@attrs.frozen
class Not(Expression):
    expr: Expression = attrs.field(validator=[wtype_is_bool])
    wtype: WType = attrs.field(default=wtypes.bool_wtype, init=False)

    def accept(self, visitor: ExpressionVisitor[T]) -> T:
        return visitor.visit_not_expression(self)


@attrs.frozen
class Contains(Expression):
    item: Expression
    sequence: Expression
    wtype: WType = attrs.field(default=wtypes.bool_wtype, init=False)

    def __attrs_post_init__(self) -> None:
        if self.sequence.wtype == wtypes.bytes_wtype:
            raise InternalError(
                "Use IsSubstring for 'in' or 'not in' checks with Bytes", self.source_location
            )
        # TODO: this type handling here probably isn't scalable
        if isinstance(self.sequence.wtype, wtypes.WArray):
            if self.sequence.wtype.element_type != self.item.wtype:
                raise CodeError(
                    f"array element type {self.sequence.wtype.element_type}"
                    f" differs from {self.item.wtype}",
                    self.source_location,
                )
        elif isinstance(self.sequence.wtype, wtypes.WTuple):
            if self.item.wtype not in self.sequence.wtype.types:
                raise CodeError(
                    f"{self.sequence.wtype} does not have element with type {self.item.wtype}",
                    self.source_location,
                )
        else:
            raise CodeError(
                f"Type doesn't support in/not in checks: {self.sequence.wtype}",
                self.source_location,
            )

    def accept(self, visitor: ExpressionVisitor[T]) -> T:
        return visitor.visit_contains_expression(self)


@attrs.frozen
class UInt64AugmentedAssignment(Statement):
    target: Lvalue = attrs.field(validator=[wtype_is_uint64])
    op: UInt64BinaryOperator
    value: Expression = attrs.field(validator=[wtype_is_uint64])

    def accept(self, visitor: StatementVisitor[T]) -> T:
        return visitor.visit_uint64_augmented_assignment(self)


@attrs.frozen
class BigUIntAugmentedAssignment(Statement):
    target: Lvalue = attrs.field(validator=[wtype_is_biguint])
    op: BigUIntBinaryOperator
    value: Expression = attrs.field(validator=[wtype_is_biguint])

    def accept(self, visitor: StatementVisitor[T]) -> T:
        return visitor.visit_biguint_augmented_assignment(self)


@attrs.frozen
class BytesAugmentedAssignment(Statement):
    target: Lvalue = attrs.field(
        validator=[expression_has_wtype(wtypes.bytes_wtype, wtypes.string_wtype)]
    )
    op: BytesBinaryOperator
    value: Expression = attrs.field(
        validator=[expression_has_wtype(wtypes.bytes_wtype, wtypes.string_wtype)]
    )

    @value.validator
    def _check_value(self, _attribute: object, value: Expression) -> None:
        if value.wtype != self.target.wtype:
            raise CodeError(
                f"Augmented assignment of differing types,"
                f" expected {self.target.wtype}, got {value.wtype}",
                value.source_location,
            )

    def accept(self, visitor: StatementVisitor[T]) -> T:
        return visitor.visit_bytes_augmented_assignment(self)


@attrs.frozen
class Range(Node):
    start: Expression = attrs.field(validator=[wtype_is_uint64])
    stop: Expression = attrs.field(validator=[wtype_is_uint64])
    step: Expression = attrs.field(validator=[wtype_is_uint64])


@attrs.frozen
class OpUp(Node):
    n: Expression


@attrs.frozen(init=False)
class Enumeration(Expression):
    expr: Expression | Range

    def __init__(self, expr: Expression | Range, source_location: SourceLocation):
        item_wtype = expr.wtype if isinstance(expr, Expression) else wtypes.uint64_wtype
        wtype = wtypes.WTuple.from_types([wtypes.uint64_wtype, item_wtype])
        self.__attrs_init__(
            expr=expr,
            source_location=source_location,
            wtype=wtype,
        )

    def accept(self, visitor: ExpressionVisitor[T]) -> T:
        return visitor.visit_enumeration(self)


@attrs.frozen(init=False)
class Reversed(Expression):
    expr: Expression | Range

    def accept(self, visitor: ExpressionVisitor[T]) -> T:
        return visitor.visit_reversed(self)

    def __init__(self, expr: Expression | Range, source_location: SourceLocation):
        wtype = expr.wtype if isinstance(expr, Expression) else wtypes.uint64_wtype

        self.__attrs_init__(
            expr=expr,
            source_location=source_location,
            wtype=wtype,
        )


@attrs.frozen
class ForInLoop(Statement):
    sequence: Expression | Range
    items: Lvalue  # item variable(s)
    loop_body: Block

    def accept(self, visitor: StatementVisitor[T]) -> T:
        return visitor.visit_for_in_loop(self)


StateExpression: t.TypeAlias = AppStateExpression | AppAccountStateExpression


@attrs.frozen
class StateGet(Expression):
    """
    Get value or default if unset - note that for get without a default,
    can just use the underlying StateExpression
    """

    field: StateExpression
    default: Expression = attrs.field()
    wtype: WType = attrs.field(init=False)

    @default.validator
    def _check_default(self, _attribute: object, default: Expression) -> None:
        if self.field.wtype != default.wtype:
            raise CodeError(
                "Default state value should match storage type", default.source_location
            )

    @wtype.default
    def _wtype_factory(self) -> WType:
        return self.field.wtype

    def accept(self, visitor: ExpressionVisitor[T]) -> T:
        return visitor.visit_state_get(self)


@attrs.frozen
class StateGetEx(Expression):
    field: StateExpression
    wtype: wtypes.WTuple = attrs.field(init=False)

    @wtype.default
    def _wtype_factory(self) -> wtypes.WTuple:
        return wtypes.WTuple.from_types((self.field.wtype, wtypes.bool_wtype))

    def accept(self, visitor: ExpressionVisitor[T]) -> T:
        return visitor.visit_state_get_ex(self)


@attrs.frozen
class StateExists(Expression):
    field: StateExpression
    wtype: WType = attrs.field(default=wtypes.bool_wtype, init=False)

    def accept(self, visitor: ExpressionVisitor[T]) -> T:
        return visitor.visit_state_exists(self)


@attrs.frozen
class StateDelete(Statement):
    field: StateExpression

    def accept(self, visitor: StatementVisitor[T]) -> T:
        return visitor.visit_state_delete(self)


@attrs.frozen
class NewStruct(Expression):
    wtype: wtypes.WStructType | wtypes.ARC4Struct
    values: Mapping[str, Expression] = attrs.field(converter=immutabledict)

    @values.validator
    def _validate_values(self, _instance: object, values: Mapping[str, Expression]) -> None:
        if values.keys() != self.wtype.fields.keys():
            raise CodeError("Invalid argument(s)", self.source_location)
        for field_name, field_value in self.values.items():
            expected_wtype = self.wtype.fields[field_name]
            if field_value.wtype != expected_wtype:
                raise CodeError("Invalid argument type(s)", self.source_location)

    def accept(self, visitor: ExpressionVisitor[T]) -> T:
        return visitor.visit_new_struct(self)


@attrs.frozen
class ModuleStatement(Node, ABC):
    name: str

    @abstractmethod
    def accept(self, visitor: ModuleStatementVisitor[T]) -> T: ...


@attrs.frozen
class ConstantDeclaration(ModuleStatement):
    value: ConstantValue

    def accept(self, visitor: ModuleStatementVisitor[T]) -> T:
        return visitor.visit_constant_declaration(self)


@attrs.frozen
class SubroutineArgument(Node):
    name: str
    wtype: WType


@attrs.frozen
class Function(ModuleStatement, ABC):
    module_name: str
    args: Sequence[SubroutineArgument] = attrs.field(converter=tuple[SubroutineArgument, ...])
    return_type: WType
    body: Block
    docstring: str | None

    @property
    @abstractmethod
    def full_name(self) -> str: ...


@attrs.frozen
class Subroutine(Function):
    @property
    def full_name(self) -> str:
        return ".".join((self.module_name, self.name))

    def accept(self, visitor: ModuleStatementVisitor[T]) -> T:
        return visitor.visit_subroutine(self)


@attrs.frozen
class ContractMethod(Function):
    class_name: str
    abimethod_config: ARC4MethodConfig | None

    @property
    def full_name(self) -> str:
        return ".".join((self.module_name, self.class_name, self.name))

    def accept(self, visitor: ModuleStatementVisitor[T]) -> T:
        return visitor.visit_contract_method(self)


@enum.unique
class AppStateKind(enum.Enum):
    app_global = enum.auto()
    account_local = enum.auto()


@attrs.frozen
class AppStateDefinition(Node):
    member_name: str
    kind: AppStateKind
    key: bytes
    key_encoding: BytesEncoding
    storage_wtype: WType
    description: str | None


@attrs.frozen
class LogicSignature(ModuleStatement):
    module_name: str
    program: Subroutine = attrs.field()

    @program.validator
    def _validate_program(self, _instance: object, program: Subroutine) -> None:
        if program.args:
            raise CodeError(
                "logicsig should not take any args",
                program.args[0].source_location,
            )
        if program.return_type not in (wtypes.uint64_wtype, wtypes.bool_wtype):
            raise CodeError(
                "Invalid return type for logicsig method, should be either bool or UInt64.",
                program.source_location,
            )

    @property
    def full_name(self) -> str:
        return ".".join((self.module_name, self.name))

    def accept(self, visitor: ModuleStatementVisitor[T]) -> T:
        return visitor.visit_logic_signature(self)


@attrs.frozen(kw_only=True)
class StateTotals:
    global_uints: int | None = None
    local_uints: int | None = None
    global_bytes: int | None = None
    local_bytes: int | None = None


@attrs.frozen
class ContractFragment(ModuleStatement):
    # note: it's a fragment because it needs to be stitched together with bases,
    #       assuming it's not abstract (in which case it should remain a fragment?)
    module_name: str
    name_override: str | None
    is_abstract: bool
    is_arc4: bool
    bases: Sequence[ContractReference] = attrs.field(converter=tuple[ContractReference, ...])
    init: ContractMethod | None = attrs.field()
    approval_program: ContractMethod | None = attrs.field()
    clear_program: ContractMethod | None = attrs.field()
    subroutines: Sequence[ContractMethod] = attrs.field(converter=tuple[ContractMethod, ...])
    app_state: Mapping[str, AppStateDefinition]
    reserved_scratch_space: StableSet[int]
    state_totals: StateTotals | None
    docstring: str | None
    # note: important that symtable comes last so default factory has access to all other fields
    symtable: Mapping[str, ContractMethod | AppStateDefinition] = attrs.field(init=False)

    @symtable.default
    def _symtable_factory(self) -> Mapping[str, ContractMethod | AppStateDefinition]:
        result: dict[str, ContractMethod | AppStateDefinition] = {**self.app_state}
        all_subs = itertools.chain(
            filter(None, (self.init, self.approval_program, self.clear_program)),
            self.subroutines,
        )
        for sub in all_subs:
            if sub.name in result:
                raise CodeError(
                    f"Duplicate symbol {sub.name} in contract {self.full_name}",
                    sub.source_location,
                )
            result[sub.name] = sub
        return result

    @init.validator
    def check_init(self, _attribute: object, init: ContractMethod | None) -> None:
        if init is not None:
            if init.return_type != wtypes.void_wtype:
                raise CodeError("init methods cannot return a value", init.source_location)
            if init.args:
                raise CodeError(
                    "init method should take no arguments (other than self)",
                    init.source_location,
                )
            if init.abimethod_config is not None:
                raise CodeError(
                    "init method should not be marked as an ABI method", init.source_location
                )

    @approval_program.validator
    def check_approval(self, _attribute: object, approval: ContractMethod | None) -> None:
        if approval is not None:
            if approval.args:
                raise CodeError(
                    "approval method should not take any args (other than self)",
                    approval.source_location,
                )
            if approval.return_type not in (wtypes.uint64_wtype, wtypes.bool_wtype):
                raise CodeError(
                    "Invalid return type for approval method, should be either bool or UInt64.",
                    approval.source_location,
                )
            if approval.abimethod_config:
                raise CodeError(
                    "approval method should not be marked as an ABI method",
                    approval.source_location,
                )

    @clear_program.validator
    def check_clear(self, _attribute: object, clear: ContractMethod | None) -> None:
        if clear is not None:
            if clear.args:
                raise CodeError(
                    "clear-state method should not take any args (other than self)",
                    clear.source_location,
                )
            if clear.return_type not in (wtypes.uint64_wtype, wtypes.bool_wtype):
                raise CodeError(
                    "Invalid return type for clear-state method, should be either bool or UInt64.",
                    clear.source_location,
                )
            if clear.abimethod_config:
                raise CodeError(
                    "clear-state method should not be marked as an ABI method",
                    clear.source_location,
                )

    @property
    def full_name(self) -> str:
        return ".".join((self.module_name, self.name))

    def accept(self, visitor: ModuleStatementVisitor[T]) -> T:
        return visitor.visit_contract_fragment(self)


@attrs.frozen
class StructureField(Node):
    name: str
    wtype: WType


@attrs.frozen
class StructureDefinition(ModuleStatement):
    fields: Sequence[StructureField] = attrs.field(converter=tuple[StructureField, ...])
    wtype: WType
    docstring: str | None

    def accept(self, visitor: ModuleStatementVisitor[T]) -> T:
        return visitor.visit_structure_definition(self)


@attrs.frozen
class Module:
    name: str
    source_file_path: str
    body: Sequence[ModuleStatement] = attrs.field(converter=tuple[ModuleStatement, ...])

    @cached_property
    def symtable(self) -> Mapping[str, ModuleStatement]:
        return {stmt.name: stmt for stmt in self.body}
