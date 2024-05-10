from __future__ import annotations

import contextlib
import operator
import typing
from functools import reduce

import attrs
import mypy.nodes
import mypy.types

from puya import log
from puya.awst import wtypes
from puya.awst.nodes import (
    TXN_FIELDS_BY_IMMEDIATE,
    ARC4Decode,
    BytesConstant,
    BytesEncoding,
    CompiledReference,
    CreateInnerTransaction,
    Expression,
    InnerTransactionField,
    IntegerConstant,
    Literal,
    MethodConstant,
    SingleEvaluation,
    SubmitInnerTransaction,
    TupleExpression,
    TxnField,
    TxnFields,
    UInt64Constant,
)
from puya.awst_build import constants
from puya.awst_build.arc4_utils import get_arc4_method_config, get_func_types
from puya.awst_build.eb.arc4._utils import (
    ARC4Signature,
    arc4_tuple_from_items,
    expect_arc4_operand_wtype,
    get_arc4_args_and_signature,
)
from puya.awst_build.eb.arc4.base import ARC4FromLogBuilder
from puya.awst_build.eb.base import (
    ExpressionBuilder,
    GenericClassExpressionBuilder,
    IntermediateExpressionBuilder,
    TypeClassExpressionBuilder,
)
from puya.awst_build.eb.subroutine import BaseClassSubroutineInvokerExpressionBuilder
from puya.awst_build.eb.transaction.fields import get_field_python_name
from puya.awst_build.eb.transaction.inner_params import get_field_expr
from puya.awst_build.eb.var_factory import var_expression
from puya.awst_build.utils import get_decorators_by_fullname
from puya.errors import CodeError, InternalError
from puya.models import (
    ARC4MethodConfig,
    CompiledReferenceField,
    OnCompletionAction,
    TransactionType,
)

if typing.TYPE_CHECKING:
    from collections.abc import Sequence

    from puya.awst_build.context import ASTConversionModuleContext
    from puya.parse import SourceLocation


logger = log.get_logger(__name__)
_APP_TRANSACTION_FIELDS = {
    get_field_python_name(field): field
    for field in (
        TXN_FIELDS_BY_IMMEDIATE[immediate]
        for immediate in (
            "ApplicationID",
            "OnCompletion",
            "ApprovalProgram",
            "ClearStateProgram",
            "GlobalNumUint",
            "GlobalNumByteSlice",
            "LocalNumUint",
            "LocalNumByteSlice",
            "ExtraProgramPages",
            "Fee",
            "Sender",
            "Note",
            "RekeyTo",
        )
    )
}


@attrs.frozen
class _ABICallExpr:
    method: ExpressionBuilder | Literal
    abi_args: Sequence[ExpressionBuilder | Literal]
    transaction_kwargs: dict[str, ExpressionBuilder | Literal]


class ABICallGenericClassExpressionBuilder(GenericClassExpressionBuilder):
    def call(
        self,
        args: Sequence[ExpressionBuilder | Literal],
        arg_kinds: list[mypy.nodes.ArgKind],
        arg_names: list[str | None],
        location: SourceLocation,
    ) -> ExpressionBuilder:
        return ABICallClassExpressionBuilder(None, self.source_location).call(
            args, arg_kinds, arg_names, location
        )

    def index_multiple(
        self, indexes: Sequence[ExpressionBuilder | Literal], location: SourceLocation
    ) -> TypeClassExpressionBuilder:
        try:
            (index,) = indexes
        except ValueError as ex:
            raise CodeError("Expected a single type arg", location) from ex
        match index:
            case TypeClassExpressionBuilder() as type_class:
                wtype = type_class.produces()
            case _:
                raise CodeError("Invalid type parameter", index.source_location)
        return ABICallClassExpressionBuilder(wtype, location)


class ARC4ClientClassExpressionBuilder(IntermediateExpressionBuilder):
    def __init__(
        self,
        context: ASTConversionModuleContext,
        source_location: SourceLocation,
        type_info: mypy.nodes.TypeInfo,
    ):
        super().__init__(source_location)
        self.context = context
        self.type_info = type_info

    def member_access(self, name: str, location: SourceLocation) -> ExpressionBuilder | Literal:
        return ARC4ClientMethodExpressionBuilder(self.context, self.type_info, name, location)


class ARC4ClientMethodExpressionBuilder(IntermediateExpressionBuilder):
    def __init__(
        self,
        context: ASTConversionModuleContext,
        type_info: mypy.nodes.TypeInfo,
        name: str,
        location: SourceLocation,
    ):
        super().__init__(location)
        self.context = context
        self.type_info = type_info
        self.name = name

    def call(
        self,
        args: Sequence[ExpressionBuilder | Literal],
        arg_kinds: list[mypy.nodes.ArgKind],
        arg_names: list[str | None],
        location: SourceLocation,
    ) -> ExpressionBuilder:
        raise CodeError(
            f"Can't invoke client methods directly, use {constants.CLS_ARC4_ABI_CALL}", location
        )


class ABICallClassExpressionBuilder(TypeClassExpressionBuilder):
    def __init__(self, result_wtype: wtypes.WType | None, source_location: SourceLocation) -> None:
        super().__init__(source_location)
        self.result_wtype = result_wtype
        app_itxn_wtype = wtypes.WInnerTransaction.from_type(TransactionType.appl)
        if _is_typed(result_wtype):
            self.wtype: wtypes.WInnerTransaction | wtypes.WTuple = wtypes.WTuple.from_types(
                (result_wtype, app_itxn_wtype)
            )
        else:
            self.wtype = app_itxn_wtype

    def produces(self) -> wtypes.WType:
        return self.wtype

    def call(
        self,
        args: Sequence[ExpressionBuilder | Literal],
        arg_kinds: list[mypy.nodes.ArgKind],
        arg_names: list[str | None],
        location: SourceLocation,
    ) -> ExpressionBuilder:
        abi_call_expr = _extract_abi_call_args(args, arg_kinds, arg_names, location)
        transaction_kwargs = abi_call_expr.transaction_kwargs
        method = abi_call_expr.method

        declared_result_wtype = self.result_wtype
        artifact = ""
        arc4_config: ARC4MethodConfig | None = None
        match method:
            case Literal(value=str(method_str)):
                arc4_args, signature = get_arc4_args_and_signature(
                    method_str, abi_call_expr.abi_args, location
                )
                if declared_result_wtype is not None:
                    # this will be validated against signature below, by comparing
                    # the generated method_selector against the supplied method_str
                    signature = attrs.evolve(signature, return_type=declared_result_wtype)
                elif signature.return_type is None:
                    signature = attrs.evolve(signature, return_type=wtypes.void_wtype)
                if not signature.method_selector.startswith(method_str):
                    raise CodeError(
                        f"Method selector from args '{signature.method_selector}' "
                        f"does not match provided method selector: '{method_str}'",
                        method.source_location,
                    )
            case (
                ARC4ClientMethodExpressionBuilder() | BaseClassSubroutineInvokerExpressionBuilder()
            ) as eb:
                artifact = eb.type_info.fullname
                method_data = _get_arc4_method_data(eb.context, eb.type_info, eb.name, location)
                signature = method_data.signature
                arc4_config = method_data.config
                declared_result_wtype = method_data.return_wtype
                num_args = len(abi_call_expr.abi_args)
                num_types = len(signature.arg_types)
                if num_types != num_args:
                    raise CodeError(
                        f"Number of arguments ({num_args})"
                        f" does not match signature ({num_types})",
                        location,
                    )
                arc4_args = [
                    expect_arc4_operand_wtype(arg, wtype)
                    for arg, wtype in zip(abi_call_expr.abi_args, signature.arg_types, strict=True)
                ]
            case _:
                raise CodeError(
                    "First argument must reference an ARC4 method by name, selector or method",
                    location,
                )

        _add_default_args(transaction_kwargs, arc4_config, artifact, location)
        _validate_transaction_kwargs(transaction_kwargs, arc4_config, location)
        return var_expression(
            _create_abi_call_expr(
                signature,
                arc4_args,
                declared_result_wtype,
                transaction_kwargs,
                location,
            )
        )


_CREATE_OR_UPDATE_ARGS = {
    "approval_program": CompiledReferenceField.approval,
    "clear_state_program": CompiledReferenceField.clear_state,
}
_CREATE_ARGS = {
    "global_num_bytes": CompiledReferenceField.global_bytes,
    "global_num_uint": CompiledReferenceField.global_uints,
    "local_num_bytes": CompiledReferenceField.local_bytes,
    "local_num_uint": CompiledReferenceField.local_uints,
    "extra_program_pages": CompiledReferenceField.extra_program_pages,
}


def _validate_transaction_kwargs(
    transaction_kwargs: dict[str, ExpressionBuilder | Literal],
    arc4_config: ARC4MethodConfig | None,
    location: SourceLocation,
) -> None:
    # note these values may be None which indicates their value is unknown at compile time
    on_complete = _get_singular_on_complete(transaction_kwargs, arc4_config)
    is_creating = _is_creating(transaction_kwargs)

    # programs provided when known not to be creating or updating
    if is_creating is False and on_complete not in (None, OnCompletionAction.UpdateApplication):
        for arg_name in _CREATE_OR_UPDATE_ARGS:
            try:
                arg = transaction_kwargs[arg_name]
            except KeyError:
                continue
            logger.error(
                f"{arg_name} provided but transaction is not"
                f" creating or updating an application",
                location=arg.source_location,
            )

    # programs not provided when creating or updating
    elif is_creating or on_complete == OnCompletionAction.UpdateApplication:
        for arg_name in _CREATE_OR_UPDATE_ARGS:
            if arg_name not in transaction_kwargs:
                logger.error(
                    f"{arg_name} not provided but transaction is"
                    f" creating or updating an application",
                    location=location,
                )

    # app allocation args provided when known not to be creating
    if is_creating is False:
        for arg_name in _CREATE_ARGS:
            try:
                arg = transaction_kwargs[arg_name]
            except KeyError:
                continue
            logger.error(
                f"{arg_name} provided but transaction is not creating an application",
                location=arg.source_location,
            )

    # app_id not provided but method doesn't support creating
    if (
        is_creating
        and arc4_config
        and not arc4_config.allow_create
        and not arc4_config.require_create
    ):
        logger.error("app_id not provided but method does not support creating", location=location)
        logger.info("ARC4 method definition", location=arc4_config.source_location)

    # on_complete not valid for arc4_config
    if (
        on_complete is not None
        and arc4_config
        and on_complete not in arc4_config.allowed_completion_types
    ):
        arg = transaction_kwargs["on_completion"]
        logger.error(
            "on_completion value is not supported by ARC4 method being called",
            location=arg.source_location,
        )
        logger.info("ARC4 method definition", location=arc4_config.source_location)


def _add_default_args(
    transaction_kwargs: dict[str, ExpressionBuilder | Literal],
    arc4_config: ARC4MethodConfig | None,
    artifact: str,
    location: SourceLocation,
) -> None:
    on_complete = _get_singular_on_complete(transaction_kwargs, arc4_config)
    default_args = dict[str, Expression]()
    if on_complete:
        default_args["on_completion"] = UInt64Constant(
            source_location=location, value=on_complete.value, teal_alias=on_complete.name
        )
    if artifact:
        is_creating = _is_creating(transaction_kwargs)
        if is_creating or on_complete == OnCompletionAction.UpdateApplication:
            for arg, field in _CREATE_OR_UPDATE_ARGS.items():
                default_args[arg] = CompiledReference(
                    artifact=artifact,
                    field=field,
                    source_location=location,
                    template_variables={},  # TODO: need to add to stubs
                )
        if is_creating:
            for arg, field in _CREATE_ARGS.items():
                default_args[arg] = CompiledReference(
                    artifact=artifact,
                    field=field,
                    source_location=location,
                )

    for arg, expr in default_args.items():
        if arg not in transaction_kwargs:
            transaction_kwargs[arg] = var_expression(expr)


def _get_arc4_signature_and_return_wtype(
    context: ASTConversionModuleContext,
    type_info: mypy.nodes.TypeInfo,
    member_name: str,
    location: SourceLocation,
) -> tuple[ARC4Signature, wtypes.WType]:
    dec = type_info.get_method(member_name)
    if isinstance(dec, mypy.nodes.Decorator):
        decorators = get_decorators_by_fullname(context, dec)
        abimethod_dec = decorators.get(constants.ABIMETHOD_DECORATOR)
        if abimethod_dec is not None:
            func_def = dec.func
            arc4_method_config = get_arc4_method_config(context, abimethod_dec, func_def)
            func_wtypes = get_func_types(context, func_def, location).values()
            *_, return_wtype = func_wtypes
            *arc4_arg_types, arc4_return_type = (
                (
                    wtypes.avm_to_arc4_equivalent_type(func_type)
                    if wtypes.has_arc4_equivalent_type(func_type)
                    else func_type
                )
                for func_type in func_wtypes
            )
            return (
                ARC4Signature(arc4_method_config.name, arc4_arg_types, arc4_return_type),
                return_wtype,
            )
    raise CodeError(f"'{type_info.fullname}.{member_name}' is not a valid ARC4 method", location)


def _is_typed(wtype: wtypes.WType | None) -> typing.TypeGuard[wtypes.WType]:
    return wtype is not None and wtype is not wtypes.void_wtype


def _create_abi_call_expr(
    signature: ARC4Signature,
    abi_args: Sequence[Expression],
    declared_result_wtype: wtypes.WType | None,
    transaction_kwargs: dict[str, ExpressionBuilder | Literal],
    location: SourceLocation,
) -> Expression:
    if signature.return_type is None:
        raise InternalError("Expected ARC4Signature.return_type to be defined", location)
    abi_arg_exprs: list[Expression] = [
        MethodConstant(
            value=signature.method_selector,
            source_location=location,
        )
    ]
    asset_exprs = list[Expression]()
    account_exprs = list[Expression]()
    application_exprs = list[Expression]()

    def append_ref_arg(ref_list: list[Expression], arg_expr: Expression) -> None:
        # asset refs start at 0, account and application start at 1
        implicit_offset = 0 if ref_list is asset_exprs else 1
        # TODO: what about references that are used more than once?
        ref_index = len(ref_list)
        ref_list.append(arg_expr)
        abi_arg_exprs.append(
            BytesConstant(
                value=(ref_index + implicit_offset).to_bytes(length=1),
                encoding=BytesEncoding.base16,
                source_location=arg_expr.source_location,
            )
        )

    for arg_expr, wtype in zip(abi_args, signature.arg_types, strict=True):
        match wtype:
            case wtypes.ARC4Type():
                abi_arg_exprs.append(arg_expr)
            case wtypes.asset_wtype:
                append_ref_arg(asset_exprs, arg_expr)
            case wtypes.account_wtype:
                append_ref_arg(account_exprs, arg_expr)
            case wtypes.application_wtype:
                append_ref_arg(application_exprs, arg_expr)
            case wtypes.WGroupTransaction():
                raise CodeError(
                    "Transaction arguments are not supported for contract to contract calls",
                    arg_expr.source_location,
                )
            case _:
                raise CodeError("Invalid argument type", arg_expr.source_location)

    fields: dict[TxnField, Expression] = {
        TxnFields.fee: UInt64Constant(
            value=0,
            source_location=location,
        ),
        TxnFields.type: UInt64Constant(
            value=TransactionType.appl.value,
            teal_alias=TransactionType.appl.name,
            source_location=location,
        ),
    }
    if len(abi_arg_exprs) > 15:
        packed_arg_slice = slice(15, None)
        args_to_pack = abi_arg_exprs[packed_arg_slice]
        abi_arg_exprs[packed_arg_slice] = [
            arc4_tuple_from_items(args_to_pack, _combine_locs(args_to_pack))
        ]

    _add_array_exprs(fields, TxnFields.app_args, abi_arg_exprs)
    _add_array_exprs(fields, TxnFields.accounts, account_exprs)
    _add_array_exprs(fields, TxnFields.apps, application_exprs)
    _add_array_exprs(fields, TxnFields.assets, asset_exprs)
    for field_python_name, field in _APP_TRANSACTION_FIELDS.items():
        try:
            value = transaction_kwargs.pop(field_python_name)
        except KeyError:
            continue
        field, field_expr = get_field_expr(field_python_name, value)
        fields[field] = field_expr

    if transaction_kwargs:
        bad_args = "', '".join(transaction_kwargs)
        raise CodeError(f"Unknown arguments: '{bad_args}'", location)

    create_itxn = CreateInnerTransaction(
        fields=fields,
        wtype=wtypes.WInnerTransactionFields.from_type(TransactionType.appl),
        source_location=location,
    )
    itxn = SubmitInnerTransaction(
        itxns=(create_itxn,),
        source_location=location,
        wtype=wtypes.WInnerTransaction.from_type(TransactionType.appl),
    )

    if not _is_typed(declared_result_wtype):
        return itxn
    itxn_tmp = SingleEvaluation(itxn)
    last_log = InnerTransactionField(
        source_location=location,
        itxn=itxn_tmp,
        field=TxnFields.last_log,
        wtype=TxnFields.last_log.wtype,
    )
    abi_result = ARC4FromLogBuilder.abi_expr_from_log(signature.return_type, last_log, location)
    # the declared result wtype may be different to the arc4 signature return wtype
    # due to automatic conversion of ARC4 -> native types
    if declared_result_wtype != signature.return_type:
        if (
            wtypes.has_arc4_equivalent_type(declared_result_wtype)
            and wtypes.avm_to_arc4_equivalent_type(declared_result_wtype) == signature.return_type
        ):
            abi_result = ARC4Decode(
                value=abi_result,
                wtype=declared_result_wtype,
                source_location=location,
            )
        else:
            raise InternalError("Return type does not match signature type", location)

    return TupleExpression.from_items(
        (
            abi_result,
            itxn_tmp,
        ),
        location,
    )


def _add_array_exprs(
    fields: dict[TxnField, Expression], field: TxnField, exprs: list[Expression]
) -> None:
    if exprs:
        fields[field] = TupleExpression.from_items(exprs, _combine_locs(exprs))


def _combine_locs(exprs: Sequence[Expression]) -> SourceLocation:
    return reduce(operator.add, (a.source_location for a in exprs))


def _extract_abi_call_args(
    args: Sequence[ExpressionBuilder | Literal],
    arg_kinds: list[mypy.nodes.ArgKind],
    arg_names: list[str | None],
    location: SourceLocation,
) -> _ABICallExpr:
    method: ExpressionBuilder | Literal | None = None
    abi_args = list[ExpressionBuilder | Literal]()
    kwargs = dict[str, ExpressionBuilder | Literal]()
    for i in range(len(args)):
        arg_kind = arg_kinds[i]
        arg_name = arg_names[i]
        arg = args[i]
        if arg_kind == mypy.nodes.ArgKind.ARG_POS and i == 0:
            method = arg
        elif arg_kind == mypy.nodes.ArgKind.ARG_POS:
            abi_args.append(arg)
        elif arg_kind == mypy.nodes.ArgKind.ARG_NAMED:
            if arg_name is None:
                raise InternalError(f"Expected named argument at pos {i}", location)
            kwargs[arg_name] = arg
        else:
            raise CodeError(f"Unexpected argument kind for '{arg_name}'", location)
    if method is None:
        raise CodeError("Missing required method positional argument", location)
    return _ABICallExpr(method=method, abi_args=abi_args, transaction_kwargs=kwargs)


@attrs.frozen(kw_only=True)
class ABIMethodData:
    signature: ARC4Signature
    return_wtype: wtypes.WType
    config: ARC4MethodConfig


def _get_arc4_method_data(
    context: ASTConversionModuleContext,
    type_info: mypy.nodes.TypeInfo,
    member_name: str,
    location: SourceLocation,
) -> ABIMethodData:
    dec = type_info.get_method(member_name)
    if isinstance(dec, mypy.nodes.Decorator):
        decorators = get_decorators_by_fullname(context, dec)
        abimethod_dec = decorators.get(constants.ABIMETHOD_DECORATOR)
        if abimethod_dec is not None:
            func_def = dec.func
            arc4_method_config = get_arc4_method_config(context, abimethod_dec, func_def)
            func_wtypes = get_func_types(context, func_def, location).values()
            *_, return_wtype = func_wtypes
            *arc4_arg_types, arc4_return_type = (
                (
                    wtypes.avm_to_arc4_equivalent_type(func_type)
                    if wtypes.has_arc4_equivalent_type(func_type)
                    else func_type
                )
                for func_type in func_wtypes
            )
            return ABIMethodData(
                signature=ARC4Signature(arc4_method_config.name, arc4_arg_types, arc4_return_type),
                return_wtype=return_wtype,
                config=arc4_method_config,
            )
    raise CodeError(f"'{type_info.fullname}.{member_name}' is not a valid ARC4 method", location)


def _get_singular_on_complete(
    args: dict[str, ExpressionBuilder | Literal], config: ARC4MethodConfig | None
) -> OnCompletionAction | None:
    """Returns OnComplete value if it is constant or can be inferred from config"""
    on_complete: OnCompletionAction | None = None
    arg = args.get("on_completion")
    if isinstance(arg, ExpressionBuilder):
        value = arg.rvalue()
        if isinstance(value, IntegerConstant):
            on_complete = OnCompletionAction(value.value)
    elif arg is None and config:
        with contextlib.suppress(ValueError):
            (on_complete,) = config.allowed_completion_types
    return on_complete


def _is_creating(args: dict[str, ExpressionBuilder | Literal]) -> bool | None:
    """Returns true if no app_id specified, or is specified as a constant zero"""
    arg = args.get("app_id")
    match arg:
        case None:
            return True
        case Literal(value=app_id):
            return app_id == 0
        case ExpressionBuilder() as eb:
            value = eb.rvalue()
            if isinstance(value, IntegerConstant):
                return value.value == 0
    return None
