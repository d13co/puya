import functools
from collections.abc import Callable

import puya.awst_build.eb.arc4.dynamic_bytes
from puya.awst import wtypes
from puya.awst.nodes import Expression
from puya.awst_build import constants, pytypes
from puya.awst_build.eb import (
    app_account_state,
    app_state,
    arc4,
    array,
    biguint,
    bool as bool_,
    box,
    bytes as bytes_,
    ensure_budget,
    intrinsics,
    log,
    named_int_constants,
    string,
    struct,
    template_variables,
    transaction,
    tuple as tuple_,
    uint64,
    unsigned_builtins,
    void,
)
from puya.awst_build.eb.base import ExpressionBuilder
from puya.awst_build.eb.reference_types import account, application, asset
from puya.errors import InternalError
from puya.parse import SourceLocation

__all__ = [
    "get_type_builder",
    "var_expression",
]

ExpressionBuilderFromSourceFactory = Callable[[SourceLocation], ExpressionBuilder]
ExpressionBuilderFromWTypeAndSourceFactory = Callable[
    [wtypes.WType, SourceLocation], ExpressionBuilder
]
ExpressionBuilderFromPyTypeAndSourceFactory = Callable[
    [pytypes.PyType, SourceLocation], ExpressionBuilder
]
ExpressionBuilderFromExpressionFactory = Callable[[Expression], ExpressionBuilder]
CLS_NAME_TO_BUILDER: dict[str, ExpressionBuilderFromSourceFactory] = {
    constants.ARC4_SIGNATURE: intrinsics.Arc4SignatureBuilder,
    constants.ENSURE_BUDGET: ensure_budget.EnsureBudgetBuilder,
    constants.LOG: log.LogBuilder,
    constants.EMIT: arc4.EmitBuilder,
    constants.CLS_ARC4_ABI_CALL: arc4.ABICallGenericClassExpressionBuilder,
    constants.CLS_TEMPLATE_VAR_METHOD: (
        template_variables.GenericTemplateVariableExpressionBuilder
    ),
    constants.SUBMIT_TXNS: transaction.SubmitInnerTransactionExpressionBuilder,
    **{
        enum_name: functools.partial(
            named_int_constants.NamedIntegerConstsTypeBuilder,
            enum_name=enum_name,
            data=enum_data,
        )
        for enum_name, enum_data in constants.NAMED_INT_CONST_ENUM_DATA.items()
    },
}
PYTYPE_TO_TYPE_BUILDER: dict[pytypes.PyType | None, ExpressionBuilderFromSourceFactory] = {
    pytypes.NoneType: void.VoidTypeExpressionBuilder,
    pytypes.BoolType: bool_.BoolClassExpressionBuilder,
    pytypes.GenericTupleType: tuple_.GenericTupleTypeExpressionBuilder,
    pytypes.reversedGenericType: functools.partial(
        unsigned_builtins.ReversedFunctionExpressionBuilder, None
    ),
    pytypes.urangeType: unsigned_builtins.UnsignedRangeBuilder,
    pytypes.uenumerateGenericType: functools.partial(
        unsigned_builtins.UnsignedEnumerateBuilder, None
    ),
    pytypes.OpUpFeeSourceType: ensure_budget.OpUpFeeSourceClassBuilder,
    pytypes.GenericBoxType: box.BoxClassGenericExpressionBuilder,
    pytypes.BoxRefType: box.BoxRefClassExpressionBuilder,
    pytypes.GenericBoxMapType: box.BoxMapClassGenericExpressionBuilder,
    pytypes.GenericLocalStateType: app_account_state.AppAccountStateClassExpressionBuilder,
    pytypes.GenericGlobalStateType: app_state.AppStateClassExpressionBuilder,
    pytypes.ARC4AddressType: arc4.AddressClassExpressionBuilder,
    pytypes.ARC4BoolType: arc4.ARC4BoolClassExpressionBuilder,
    pytypes.ARC4ByteType: arc4.ByteClassExpressionBuilder,
    pytypes.GenericARC4DynamicArrayType: arc4.DynamicArrayGenericClassExpressionBuilder,
    pytypes.GenericARC4StaticArrayType: arc4.StaticArrayGenericClassExpressionBuilder,
    pytypes.ARC4StringType: arc4.StringClassExpressionBuilder,
    pytypes.GenericARC4TupleType: arc4.ARC4TupleGenericClassExpressionBuilder,
    pytypes.ARC4DynamicBytesType: puya.awst_build.eb.arc4.DynamicBytesClassExpressionBuilder,
    pytypes.AccountType: account.AccountClassExpressionBuilder,
    pytypes.GenericArrayType: array.ArrayGenericClassExpressionBuilder,
    pytypes.AssetType: asset.AssetClassExpressionBuilder,
    pytypes.ApplicationType: application.ApplicationClassExpressionBuilder,
    pytypes.BigUIntType: biguint.BigUIntClassExpressionBuilder,
    pytypes.BytesType: bytes_.BytesClassExpressionBuilder,
    pytypes.StringType: string.StringClassExpressionBuilder,
    pytypes.UInt64Type: uint64.UInt64ClassExpressionBuilder,
    **{
        gtxn_pytyp: functools.partial(
            transaction.GroupTransactionClassExpressionBuilder, wtype=gtxn_pytyp.wtype
        )
        for gtxn_pytyp in (
            pytypes.GroupTransactionBaseType,
            *pytypes.GroupTransactionTypes.values(),
        )
    },
    **{
        itxn_fieldset_pytyp: functools.partial(
            transaction.InnerTxnParamsClassExpressionBuilder, wtype=itxn_fieldset_pytyp.wtype
        )
        for itxn_fieldset_pytyp in pytypes.InnerTransactionFieldsetTypes.values()
    },
    **{
        itxn_result_pytyp: functools.partial(
            transaction.InnerTransactionClassExpressionBuilder, wtype=itxn_result_pytyp
        )
        for itxn_result_pytyp in pytypes.InnerTransactionResultTypes.values()
    },
}
PYTYPE_GENERIC_TO_TYPE_BUILDER: dict[
    pytypes.PyType | None, ExpressionBuilderFromPyTypeAndSourceFactory
] = {
    pytypes.uenumerateGenericType: unsigned_builtins.UnsignedEnumerateBuilder,
    pytypes.reversedGenericType: unsigned_builtins.ReversedFunctionExpressionBuilder,
    pytypes.GenericTemplateVarType: template_variables.TemplateVariableExpressionBuilder,
    pytypes.GenericABICallWithReturnType: arc4.ABICallClassExpressionBuilder,
    pytypes.GenericBoxType: box.BoxClassExpressionBuilder,
    pytypes.GenericBoxMapType: box.BoxMapClassExpressionBuilder,
    pytypes.GenericARC4TupleType: arc4.ARC4TupleClassExpressionBuilder,
    pytypes.GenericTupleType: tuple_.TupleTypeExpressionBuilder,
    pytypes.GenericArrayType: array.ArrayClassExpressionBuilder,
    pytypes.GenericARC4UFixedNxMType: arc4.UFixedNxMClassExpressionBuilder,
    pytypes.GenericARC4BigUFixedNxMType: arc4.UFixedNxMClassExpressionBuilder,
    pytypes.GenericARC4UIntNType: arc4.UIntNClassExpressionBuilder,
    pytypes.GenericARC4BigUIntNType: arc4.UIntNClassExpressionBuilder,
    pytypes.GenericARC4DynamicArrayType: arc4.DynamicArrayClassExpressionBuilder,
    pytypes.GenericARC4StaticArrayType: arc4.StaticArrayClassExpressionBuilder,
}
PYTYPE_BASE_TO_TYPE_BUILDER: dict[
    pytypes.PyType | None, ExpressionBuilderFromPyTypeAndSourceFactory
] = {
    pytypes.ARC4StructBaseType: arc4.ARC4StructClassExpressionBuilder,
    pytypes.StructBaseType: struct.StructSubclassExpressionBuilder,
}
WTYPE_TO_BUILDER: dict[
    wtypes.WType | type[wtypes.WType], ExpressionBuilderFromExpressionFactory
] = {
    wtypes.ARC4DynamicArray: arc4.DynamicArrayExpressionBuilder,
    wtypes.ARC4Struct: arc4.ARC4StructExpressionBuilder,
    wtypes.ARC4StaticArray: arc4.StaticArrayExpressionBuilder,
    wtypes.ARC4Tuple: arc4.ARC4TupleExpressionBuilder,
    wtypes.ARC4UFixedNxM: arc4.UFixedNxMExpressionBuilder,
    wtypes.ARC4UIntN: arc4.UIntNExpressionBuilder,
    wtypes.WArray: array.ArrayExpressionBuilder,
    wtypes.WStructType: struct.StructExpressionBuilder,
    wtypes.WTuple: tuple_.TupleExpressionBuilder,
    wtypes.arc4_bool_wtype: arc4.ARC4BoolExpressionBuilder,
    wtypes.arc4_string_wtype: arc4.StringExpressionBuilder,
    wtypes.arc4_dynamic_bytes: arc4.DynamicBytesExpressionBuilder,
    wtypes.arc4_address_type: arc4.AddressExpressionBuilder,
    wtypes.account_wtype: account.AccountExpressionBuilder,
    wtypes.application_wtype: application.ApplicationExpressionBuilder,
    wtypes.asset_wtype: asset.AssetExpressionBuilder,
    wtypes.biguint_wtype: biguint.BigUIntExpressionBuilder,
    wtypes.bool_wtype: bool_.BoolExpressionBuilder,
    wtypes.bytes_wtype: bytes_.BytesExpressionBuilder,
    wtypes.string_wtype: string.StringExpressionBuilder,
    wtypes.uint64_wtype: uint64.UInt64ExpressionBuilder,
    wtypes.void_wtype: void.VoidExpressionBuilder,
    wtypes.WGroupTransaction: transaction.GroupTransactionExpressionBuilder,
    wtypes.WInnerTransaction: transaction.InnerTransactionExpressionBuilder,
    wtypes.WInnerTransactionFields: transaction.InnerTxnParamsExpressionBuilder,
    wtypes.WBoxProxy: box.BoxProxyExpressionBuilder,
    wtypes.WBoxMapProxy: box.BoxMapProxyExpressionBuilder,
    wtypes.box_ref_proxy_type: box.BoxRefProxyExpressionBuilder,
}


def get_type_builder(python_type: str, source_location: SourceLocation) -> ExpressionBuilder:
    try:
        type_class = CLS_NAME_TO_BUILDER[python_type]
    except KeyError as ex:
        raise InternalError(f"Unhandled algopy name: {python_type}", source_location) from ex
    else:
        return type_class(source_location)


def var_expression(expr: Expression) -> ExpressionBuilder:
    try:
        builder = WTYPE_TO_BUILDER[expr.wtype]
    except KeyError:
        try:
            builder = WTYPE_TO_BUILDER[type(expr.wtype)]
        except KeyError:
            raise InternalError(
                f"Unable to map wtype {expr.wtype!r} to expression builder", expr.source_location
            ) from None
    return builder(expr)
