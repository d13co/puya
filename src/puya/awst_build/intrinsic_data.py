import typing
from collections.abc import Mapping, Sequence

from immutabledict import immutabledict

from puya.awst import wtypes
from puya.awst_build.intrinsic_models import (
    FunctionOpMapping,
    ImmediateArgMapping,
)

ENUM_CLASSES: typing.Final = immutabledict[str, Mapping[str, str]](
    {
        "algopy.op.Base64": {"URLEncoding": "URLEncoding", "StdEncoding": "StdEncoding"},
        "algopy.op.ECDSA": {"Secp256k1": "Secp256k1", "Secp256r1": "Secp256r1"},
        "algopy.op.VrfVerify": {"VrfAlgorand": "VrfAlgorand"},
        "algopy.op.EC": {
            "BN254g1": "BN254g1",
            "BN254g2": "BN254g2",
            "BLS12_381g1": "BLS12_381g1",
            "BLS12_381g2": "BLS12_381g2",
        },
    }
)

STUB_TO_AST_MAPPER: typing.Final = immutabledict[str, Sequence[FunctionOpMapping]](
    {
        "algopy.op.addw": (
            FunctionOpMapping(
                op_code="addw",
                stack_inputs={"a": (wtypes.uint64_wtype,), "b": (wtypes.uint64_wtype,)},
                stack_outputs=(wtypes.uint64_wtype, wtypes.uint64_wtype),
            ),
        ),
        "algopy.op.app_opted_in": (
            FunctionOpMapping(
                op_code="app_opted_in",
                stack_inputs={
                    "a": (wtypes.account_wtype, wtypes.uint64_wtype),
                    "b": (wtypes.application_wtype, wtypes.uint64_wtype),
                },
                stack_outputs=(wtypes.bool_wtype,),
            ),
        ),
        "algopy.op.arg": (
            FunctionOpMapping(
                op_code="args",
                stack_inputs={"a": (wtypes.uint64_wtype,)},
                stack_outputs=(wtypes.bytes_wtype,),
            ),
            FunctionOpMapping(
                op_code="arg",
                immediates=(ImmediateArgMapping("a", int),),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.balance": (
            FunctionOpMapping(
                op_code="balance",
                stack_inputs={"a": (wtypes.account_wtype, wtypes.uint64_wtype)},
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.base64_decode": (
            FunctionOpMapping(
                op_code="base64_decode",
                immediates=(ImmediateArgMapping("e", str),),
                stack_inputs={"a": (wtypes.bytes_wtype,)},
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.bitlen": (
            FunctionOpMapping(
                op_code="bitlen",
                stack_inputs={"a": (wtypes.bytes_wtype, wtypes.uint64_wtype)},
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.bsqrt": (
            FunctionOpMapping(
                op_code="bsqrt",
                stack_inputs={"a": (wtypes.biguint_wtype,)},
                stack_outputs=(wtypes.biguint_wtype,),
            ),
        ),
        "algopy.op.btoi": (
            FunctionOpMapping(
                op_code="btoi",
                stack_inputs={"a": (wtypes.bytes_wtype,)},
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.bzero": (
            FunctionOpMapping(
                op_code="bzero",
                stack_inputs={"a": (wtypes.uint64_wtype,)},
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.concat": (
            FunctionOpMapping(
                op_code="concat",
                stack_inputs={"a": (wtypes.bytes_wtype,), "b": (wtypes.bytes_wtype,)},
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.divmodw": (
            FunctionOpMapping(
                op_code="divmodw",
                stack_inputs={
                    "a": (wtypes.uint64_wtype,),
                    "b": (wtypes.uint64_wtype,),
                    "c": (wtypes.uint64_wtype,),
                    "d": (wtypes.uint64_wtype,),
                },
                stack_outputs=(
                    wtypes.uint64_wtype,
                    wtypes.uint64_wtype,
                    wtypes.uint64_wtype,
                    wtypes.uint64_wtype,
                ),
            ),
        ),
        "algopy.op.divw": (
            FunctionOpMapping(
                op_code="divw",
                stack_inputs={
                    "a": (wtypes.uint64_wtype,),
                    "b": (wtypes.uint64_wtype,),
                    "c": (wtypes.uint64_wtype,),
                },
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.ecdsa_pk_decompress": (
            FunctionOpMapping(
                op_code="ecdsa_pk_decompress",
                immediates=(ImmediateArgMapping("v", str),),
                stack_inputs={"a": (wtypes.bytes_wtype,)},
                stack_outputs=(wtypes.bytes_wtype, wtypes.bytes_wtype),
            ),
        ),
        "algopy.op.ecdsa_pk_recover": (
            FunctionOpMapping(
                op_code="ecdsa_pk_recover",
                immediates=(ImmediateArgMapping("v", str),),
                stack_inputs={
                    "a": (wtypes.bytes_wtype,),
                    "b": (wtypes.uint64_wtype,),
                    "c": (wtypes.bytes_wtype,),
                    "d": (wtypes.bytes_wtype,),
                },
                stack_outputs=(wtypes.bytes_wtype, wtypes.bytes_wtype),
            ),
        ),
        "algopy.op.ecdsa_verify": (
            FunctionOpMapping(
                op_code="ecdsa_verify",
                immediates=(ImmediateArgMapping("v", str),),
                stack_inputs={
                    "a": (wtypes.bytes_wtype,),
                    "b": (wtypes.bytes_wtype,),
                    "c": (wtypes.bytes_wtype,),
                    "d": (wtypes.bytes_wtype,),
                    "e": (wtypes.bytes_wtype,),
                },
                stack_outputs=(wtypes.bool_wtype,),
            ),
        ),
        "algopy.op.ed25519verify": (
            FunctionOpMapping(
                op_code="ed25519verify",
                stack_inputs={
                    "a": (wtypes.bytes_wtype,),
                    "b": (wtypes.bytes_wtype,),
                    "c": (wtypes.bytes_wtype,),
                },
                stack_outputs=(wtypes.bool_wtype,),
            ),
        ),
        "algopy.op.ed25519verify_bare": (
            FunctionOpMapping(
                op_code="ed25519verify_bare",
                stack_inputs={
                    "a": (wtypes.bytes_wtype,),
                    "b": (wtypes.bytes_wtype,),
                    "c": (wtypes.bytes_wtype,),
                },
                stack_outputs=(wtypes.bool_wtype,),
            ),
        ),
        "algopy.op.err": (FunctionOpMapping(op_code="err"),),
        "algopy.op.exit": (
            FunctionOpMapping(op_code="return", stack_inputs={"a": (wtypes.uint64_wtype,)}),
        ),
        "algopy.op.exp": (
            FunctionOpMapping(
                op_code="exp",
                stack_inputs={"a": (wtypes.uint64_wtype,), "b": (wtypes.uint64_wtype,)},
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.expw": (
            FunctionOpMapping(
                op_code="expw",
                stack_inputs={"a": (wtypes.uint64_wtype,), "b": (wtypes.uint64_wtype,)},
                stack_outputs=(wtypes.uint64_wtype, wtypes.uint64_wtype),
            ),
        ),
        "algopy.op.extract": (
            FunctionOpMapping(
                op_code="extract3",
                stack_inputs={
                    "a": (wtypes.bytes_wtype,),
                    "b": (wtypes.uint64_wtype,),
                    "c": (wtypes.uint64_wtype,),
                },
                stack_outputs=(wtypes.bytes_wtype,),
            ),
            FunctionOpMapping(
                op_code="extract",
                immediates=(ImmediateArgMapping("b", int), ImmediateArgMapping("c", int)),
                stack_inputs={"a": (wtypes.bytes_wtype,)},
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.extract_uint16": (
            FunctionOpMapping(
                op_code="extract_uint16",
                stack_inputs={"a": (wtypes.bytes_wtype,), "b": (wtypes.uint64_wtype,)},
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.extract_uint32": (
            FunctionOpMapping(
                op_code="extract_uint32",
                stack_inputs={"a": (wtypes.bytes_wtype,), "b": (wtypes.uint64_wtype,)},
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.extract_uint64": (
            FunctionOpMapping(
                op_code="extract_uint64",
                stack_inputs={"a": (wtypes.bytes_wtype,), "b": (wtypes.uint64_wtype,)},
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.gaid": (
            FunctionOpMapping(
                op_code="gaids",
                stack_inputs={"a": (wtypes.uint64_wtype,)},
                stack_outputs=(wtypes.application_wtype,),
            ),
            FunctionOpMapping(
                op_code="gaid",
                immediates=(ImmediateArgMapping("a", int),),
                stack_outputs=(wtypes.application_wtype,),
            ),
        ),
        "algopy.op.getbit": (
            FunctionOpMapping(
                op_code="getbit",
                stack_inputs={
                    "a": (wtypes.bytes_wtype, wtypes.uint64_wtype),
                    "b": (wtypes.uint64_wtype,),
                },
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.getbyte": (
            FunctionOpMapping(
                op_code="getbyte",
                stack_inputs={"a": (wtypes.bytes_wtype,), "b": (wtypes.uint64_wtype,)},
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.gload_bytes": (
            FunctionOpMapping(
                op_code="gloadss",
                stack_inputs={"a": (wtypes.uint64_wtype,), "b": (wtypes.uint64_wtype,)},
                stack_outputs=(wtypes.bytes_wtype,),
            ),
            FunctionOpMapping(
                op_code="gload",
                immediates=(ImmediateArgMapping("a", int), ImmediateArgMapping("b", int)),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
            FunctionOpMapping(
                op_code="gloads",
                immediates=(ImmediateArgMapping("b", int),),
                stack_inputs={"a": (wtypes.uint64_wtype,)},
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.gload_uint64": (
            FunctionOpMapping(
                op_code="gloadss",
                stack_inputs={"a": (wtypes.uint64_wtype,), "b": (wtypes.uint64_wtype,)},
                stack_outputs=(wtypes.uint64_wtype,),
            ),
            FunctionOpMapping(
                op_code="gload",
                immediates=(ImmediateArgMapping("a", int), ImmediateArgMapping("b", int)),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
            FunctionOpMapping(
                op_code="gloads",
                immediates=(ImmediateArgMapping("b", int),),
                stack_inputs={"a": (wtypes.uint64_wtype,)},
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.itob": (
            FunctionOpMapping(
                op_code="itob",
                stack_inputs={"a": (wtypes.uint64_wtype,)},
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.keccak256": (
            FunctionOpMapping(
                op_code="keccak256",
                stack_inputs={"a": (wtypes.bytes_wtype,)},
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.min_balance": (
            FunctionOpMapping(
                op_code="min_balance",
                stack_inputs={"a": (wtypes.account_wtype, wtypes.uint64_wtype)},
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.mulw": (
            FunctionOpMapping(
                op_code="mulw",
                stack_inputs={"a": (wtypes.uint64_wtype,), "b": (wtypes.uint64_wtype,)},
                stack_outputs=(wtypes.uint64_wtype, wtypes.uint64_wtype),
            ),
        ),
        "algopy.op.replace": (
            FunctionOpMapping(
                op_code="replace3",
                stack_inputs={
                    "a": (wtypes.bytes_wtype,),
                    "b": (wtypes.uint64_wtype,),
                    "c": (wtypes.bytes_wtype,),
                },
                stack_outputs=(wtypes.bytes_wtype,),
            ),
            FunctionOpMapping(
                op_code="replace2",
                immediates=(ImmediateArgMapping("b", int),),
                stack_inputs={"a": (wtypes.bytes_wtype,), "c": (wtypes.bytes_wtype,)},
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.select_bytes": (
            FunctionOpMapping(
                op_code="select",
                stack_inputs={
                    "a": (wtypes.bytes_wtype,),
                    "b": (wtypes.bytes_wtype,),
                    "c": (wtypes.bool_wtype, wtypes.uint64_wtype),
                },
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.select_uint64": (
            FunctionOpMapping(
                op_code="select",
                stack_inputs={
                    "a": (wtypes.uint64_wtype,),
                    "b": (wtypes.uint64_wtype,),
                    "c": (wtypes.bool_wtype, wtypes.uint64_wtype),
                },
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.setbit_bytes": (
            FunctionOpMapping(
                op_code="setbit",
                stack_inputs={
                    "a": (wtypes.bytes_wtype,),
                    "b": (wtypes.uint64_wtype,),
                    "c": (wtypes.uint64_wtype,),
                },
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.setbit_uint64": (
            FunctionOpMapping(
                op_code="setbit",
                stack_inputs={
                    "a": (wtypes.uint64_wtype,),
                    "b": (wtypes.uint64_wtype,),
                    "c": (wtypes.uint64_wtype,),
                },
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.setbyte": (
            FunctionOpMapping(
                op_code="setbyte",
                stack_inputs={
                    "a": (wtypes.bytes_wtype,),
                    "b": (wtypes.uint64_wtype,),
                    "c": (wtypes.uint64_wtype,),
                },
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.sha256": (
            FunctionOpMapping(
                op_code="sha256",
                stack_inputs={"a": (wtypes.bytes_wtype,)},
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.sha3_256": (
            FunctionOpMapping(
                op_code="sha3_256",
                stack_inputs={"a": (wtypes.bytes_wtype,)},
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.sha512_256": (
            FunctionOpMapping(
                op_code="sha512_256",
                stack_inputs={"a": (wtypes.bytes_wtype,)},
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.shl": (
            FunctionOpMapping(
                op_code="shl",
                stack_inputs={"a": (wtypes.uint64_wtype,), "b": (wtypes.uint64_wtype,)},
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.shr": (
            FunctionOpMapping(
                op_code="shr",
                stack_inputs={"a": (wtypes.uint64_wtype,), "b": (wtypes.uint64_wtype,)},
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.sqrt": (
            FunctionOpMapping(
                op_code="sqrt",
                stack_inputs={"a": (wtypes.uint64_wtype,)},
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.substring": (
            FunctionOpMapping(
                op_code="substring3",
                stack_inputs={
                    "a": (wtypes.bytes_wtype,),
                    "b": (wtypes.uint64_wtype,),
                    "c": (wtypes.uint64_wtype,),
                },
                stack_outputs=(wtypes.bytes_wtype,),
            ),
            FunctionOpMapping(
                op_code="substring",
                immediates=(ImmediateArgMapping("b", int), ImmediateArgMapping("c", int)),
                stack_inputs={"a": (wtypes.bytes_wtype,)},
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.vrf_verify": (
            FunctionOpMapping(
                op_code="vrf_verify",
                immediates=(ImmediateArgMapping("s", str),),
                stack_inputs={
                    "a": (wtypes.bytes_wtype,),
                    "b": (wtypes.bytes_wtype,),
                    "c": (wtypes.bytes_wtype,),
                },
                stack_outputs=(wtypes.bytes_wtype, wtypes.bool_wtype),
            ),
        ),
        "algopy.op.AcctParamsGet.acct_balance": (
            FunctionOpMapping(
                op_code="acct_params_get",
                immediates=("AcctBalance",),
                stack_inputs={"a": (wtypes.account_wtype, wtypes.uint64_wtype)},
                stack_outputs=(wtypes.uint64_wtype, wtypes.bool_wtype),
            ),
        ),
        "algopy.op.AcctParamsGet.acct_min_balance": (
            FunctionOpMapping(
                op_code="acct_params_get",
                immediates=("AcctMinBalance",),
                stack_inputs={"a": (wtypes.account_wtype, wtypes.uint64_wtype)},
                stack_outputs=(wtypes.uint64_wtype, wtypes.bool_wtype),
            ),
        ),
        "algopy.op.AcctParamsGet.acct_auth_addr": (
            FunctionOpMapping(
                op_code="acct_params_get",
                immediates=("AcctAuthAddr",),
                stack_inputs={"a": (wtypes.account_wtype, wtypes.uint64_wtype)},
                stack_outputs=(wtypes.account_wtype, wtypes.bool_wtype),
            ),
        ),
        "algopy.op.AcctParamsGet.acct_total_num_uint": (
            FunctionOpMapping(
                op_code="acct_params_get",
                immediates=("AcctTotalNumUint",),
                stack_inputs={"a": (wtypes.account_wtype, wtypes.uint64_wtype)},
                stack_outputs=(wtypes.uint64_wtype, wtypes.bool_wtype),
            ),
        ),
        "algopy.op.AcctParamsGet.acct_total_num_byte_slice": (
            FunctionOpMapping(
                op_code="acct_params_get",
                immediates=("AcctTotalNumByteSlice",),
                stack_inputs={"a": (wtypes.account_wtype, wtypes.uint64_wtype)},
                stack_outputs=(wtypes.uint64_wtype, wtypes.bool_wtype),
            ),
        ),
        "algopy.op.AcctParamsGet.acct_total_extra_app_pages": (
            FunctionOpMapping(
                op_code="acct_params_get",
                immediates=("AcctTotalExtraAppPages",),
                stack_inputs={"a": (wtypes.account_wtype, wtypes.uint64_wtype)},
                stack_outputs=(wtypes.uint64_wtype, wtypes.bool_wtype),
            ),
        ),
        "algopy.op.AcctParamsGet.acct_total_apps_created": (
            FunctionOpMapping(
                op_code="acct_params_get",
                immediates=("AcctTotalAppsCreated",),
                stack_inputs={"a": (wtypes.account_wtype, wtypes.uint64_wtype)},
                stack_outputs=(wtypes.uint64_wtype, wtypes.bool_wtype),
            ),
        ),
        "algopy.op.AcctParamsGet.acct_total_apps_opted_in": (
            FunctionOpMapping(
                op_code="acct_params_get",
                immediates=("AcctTotalAppsOptedIn",),
                stack_inputs={"a": (wtypes.account_wtype, wtypes.uint64_wtype)},
                stack_outputs=(wtypes.uint64_wtype, wtypes.bool_wtype),
            ),
        ),
        "algopy.op.AcctParamsGet.acct_total_assets_created": (
            FunctionOpMapping(
                op_code="acct_params_get",
                immediates=("AcctTotalAssetsCreated",),
                stack_inputs={"a": (wtypes.account_wtype, wtypes.uint64_wtype)},
                stack_outputs=(wtypes.uint64_wtype, wtypes.bool_wtype),
            ),
        ),
        "algopy.op.AcctParamsGet.acct_total_assets": (
            FunctionOpMapping(
                op_code="acct_params_get",
                immediates=("AcctTotalAssets",),
                stack_inputs={"a": (wtypes.account_wtype, wtypes.uint64_wtype)},
                stack_outputs=(wtypes.uint64_wtype, wtypes.bool_wtype),
            ),
        ),
        "algopy.op.AcctParamsGet.acct_total_boxes": (
            FunctionOpMapping(
                op_code="acct_params_get",
                immediates=("AcctTotalBoxes",),
                stack_inputs={"a": (wtypes.account_wtype, wtypes.uint64_wtype)},
                stack_outputs=(wtypes.uint64_wtype, wtypes.bool_wtype),
            ),
        ),
        "algopy.op.AcctParamsGet.acct_total_box_bytes": (
            FunctionOpMapping(
                op_code="acct_params_get",
                immediates=("AcctTotalBoxBytes",),
                stack_inputs={"a": (wtypes.account_wtype, wtypes.uint64_wtype)},
                stack_outputs=(wtypes.uint64_wtype, wtypes.bool_wtype),
            ),
        ),
        "algopy.op.AppGlobal.get_bytes": (
            FunctionOpMapping(
                op_code="app_global_get",
                stack_inputs={"a": (wtypes.bytes_wtype,)},
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.AppGlobal.get_uint64": (
            FunctionOpMapping(
                op_code="app_global_get",
                stack_inputs={"a": (wtypes.bytes_wtype,)},
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.AppGlobal.get_ex_bytes": (
            FunctionOpMapping(
                op_code="app_global_get_ex",
                stack_inputs={
                    "a": (wtypes.application_wtype, wtypes.uint64_wtype),
                    "b": (wtypes.bytes_wtype,),
                },
                stack_outputs=(wtypes.bytes_wtype, wtypes.bool_wtype),
            ),
        ),
        "algopy.op.AppGlobal.get_ex_uint64": (
            FunctionOpMapping(
                op_code="app_global_get_ex",
                stack_inputs={
                    "a": (wtypes.application_wtype, wtypes.uint64_wtype),
                    "b": (wtypes.bytes_wtype,),
                },
                stack_outputs=(wtypes.uint64_wtype, wtypes.bool_wtype),
            ),
        ),
        "algopy.op.AppGlobal.delete": (
            FunctionOpMapping(op_code="app_global_del", stack_inputs={"a": (wtypes.bytes_wtype,)}),
        ),
        "algopy.op.AppGlobal.put": (
            FunctionOpMapping(
                op_code="app_global_put",
                stack_inputs={
                    "a": (wtypes.bytes_wtype,),
                    "b": (wtypes.bytes_wtype, wtypes.uint64_wtype),
                },
            ),
        ),
        "algopy.op.AppLocal.get_bytes": (
            FunctionOpMapping(
                op_code="app_local_get",
                stack_inputs={
                    "a": (wtypes.account_wtype, wtypes.uint64_wtype),
                    "b": (wtypes.bytes_wtype,),
                },
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.AppLocal.get_uint64": (
            FunctionOpMapping(
                op_code="app_local_get",
                stack_inputs={
                    "a": (wtypes.account_wtype, wtypes.uint64_wtype),
                    "b": (wtypes.bytes_wtype,),
                },
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.AppLocal.get_ex_bytes": (
            FunctionOpMapping(
                op_code="app_local_get_ex",
                stack_inputs={
                    "a": (wtypes.account_wtype, wtypes.uint64_wtype),
                    "b": (wtypes.application_wtype, wtypes.uint64_wtype),
                    "c": (wtypes.bytes_wtype,),
                },
                stack_outputs=(wtypes.bytes_wtype, wtypes.bool_wtype),
            ),
        ),
        "algopy.op.AppLocal.get_ex_uint64": (
            FunctionOpMapping(
                op_code="app_local_get_ex",
                stack_inputs={
                    "a": (wtypes.account_wtype, wtypes.uint64_wtype),
                    "b": (wtypes.application_wtype, wtypes.uint64_wtype),
                    "c": (wtypes.bytes_wtype,),
                },
                stack_outputs=(wtypes.uint64_wtype, wtypes.bool_wtype),
            ),
        ),
        "algopy.op.AppLocal.delete": (
            FunctionOpMapping(
                op_code="app_local_del",
                stack_inputs={
                    "a": (wtypes.account_wtype, wtypes.uint64_wtype),
                    "b": (wtypes.bytes_wtype,),
                },
            ),
        ),
        "algopy.op.AppLocal.put": (
            FunctionOpMapping(
                op_code="app_local_put",
                stack_inputs={
                    "a": (wtypes.account_wtype, wtypes.uint64_wtype),
                    "b": (wtypes.bytes_wtype,),
                    "c": (wtypes.bytes_wtype, wtypes.uint64_wtype),
                },
            ),
        ),
        "algopy.op.AppParamsGet.app_approval_program": (
            FunctionOpMapping(
                op_code="app_params_get",
                immediates=("AppApprovalProgram",),
                stack_inputs={"a": (wtypes.application_wtype, wtypes.uint64_wtype)},
                stack_outputs=(wtypes.bytes_wtype, wtypes.bool_wtype),
            ),
        ),
        "algopy.op.AppParamsGet.app_clear_state_program": (
            FunctionOpMapping(
                op_code="app_params_get",
                immediates=("AppClearStateProgram",),
                stack_inputs={"a": (wtypes.application_wtype, wtypes.uint64_wtype)},
                stack_outputs=(wtypes.bytes_wtype, wtypes.bool_wtype),
            ),
        ),
        "algopy.op.AppParamsGet.app_global_num_uint": (
            FunctionOpMapping(
                op_code="app_params_get",
                immediates=("AppGlobalNumUint",),
                stack_inputs={"a": (wtypes.application_wtype, wtypes.uint64_wtype)},
                stack_outputs=(wtypes.uint64_wtype, wtypes.bool_wtype),
            ),
        ),
        "algopy.op.AppParamsGet.app_global_num_byte_slice": (
            FunctionOpMapping(
                op_code="app_params_get",
                immediates=("AppGlobalNumByteSlice",),
                stack_inputs={"a": (wtypes.application_wtype, wtypes.uint64_wtype)},
                stack_outputs=(wtypes.uint64_wtype, wtypes.bool_wtype),
            ),
        ),
        "algopy.op.AppParamsGet.app_local_num_uint": (
            FunctionOpMapping(
                op_code="app_params_get",
                immediates=("AppLocalNumUint",),
                stack_inputs={"a": (wtypes.application_wtype, wtypes.uint64_wtype)},
                stack_outputs=(wtypes.uint64_wtype, wtypes.bool_wtype),
            ),
        ),
        "algopy.op.AppParamsGet.app_local_num_byte_slice": (
            FunctionOpMapping(
                op_code="app_params_get",
                immediates=("AppLocalNumByteSlice",),
                stack_inputs={"a": (wtypes.application_wtype, wtypes.uint64_wtype)},
                stack_outputs=(wtypes.uint64_wtype, wtypes.bool_wtype),
            ),
        ),
        "algopy.op.AppParamsGet.app_extra_program_pages": (
            FunctionOpMapping(
                op_code="app_params_get",
                immediates=("AppExtraProgramPages",),
                stack_inputs={"a": (wtypes.application_wtype, wtypes.uint64_wtype)},
                stack_outputs=(wtypes.uint64_wtype, wtypes.bool_wtype),
            ),
        ),
        "algopy.op.AppParamsGet.app_creator": (
            FunctionOpMapping(
                op_code="app_params_get",
                immediates=("AppCreator",),
                stack_inputs={"a": (wtypes.application_wtype, wtypes.uint64_wtype)},
                stack_outputs=(wtypes.account_wtype, wtypes.bool_wtype),
            ),
        ),
        "algopy.op.AppParamsGet.app_address": (
            FunctionOpMapping(
                op_code="app_params_get",
                immediates=("AppAddress",),
                stack_inputs={"a": (wtypes.application_wtype, wtypes.uint64_wtype)},
                stack_outputs=(wtypes.account_wtype, wtypes.bool_wtype),
            ),
        ),
        "algopy.op.AssetHoldingGet.asset_balance": (
            FunctionOpMapping(
                op_code="asset_holding_get",
                immediates=("AssetBalance",),
                stack_inputs={
                    "a": (wtypes.account_wtype, wtypes.uint64_wtype),
                    "b": (wtypes.asset_wtype, wtypes.uint64_wtype),
                },
                stack_outputs=(wtypes.uint64_wtype, wtypes.bool_wtype),
            ),
        ),
        "algopy.op.AssetHoldingGet.asset_frozen": (
            FunctionOpMapping(
                op_code="asset_holding_get",
                immediates=("AssetFrozen",),
                stack_inputs={
                    "a": (wtypes.account_wtype, wtypes.uint64_wtype),
                    "b": (wtypes.asset_wtype, wtypes.uint64_wtype),
                },
                stack_outputs=(wtypes.bool_wtype, wtypes.bool_wtype),
            ),
        ),
        "algopy.op.AssetParamsGet.asset_total": (
            FunctionOpMapping(
                op_code="asset_params_get",
                immediates=("AssetTotal",),
                stack_inputs={"a": (wtypes.asset_wtype, wtypes.uint64_wtype)},
                stack_outputs=(wtypes.uint64_wtype, wtypes.bool_wtype),
            ),
        ),
        "algopy.op.AssetParamsGet.asset_decimals": (
            FunctionOpMapping(
                op_code="asset_params_get",
                immediates=("AssetDecimals",),
                stack_inputs={"a": (wtypes.asset_wtype, wtypes.uint64_wtype)},
                stack_outputs=(wtypes.uint64_wtype, wtypes.bool_wtype),
            ),
        ),
        "algopy.op.AssetParamsGet.asset_default_frozen": (
            FunctionOpMapping(
                op_code="asset_params_get",
                immediates=("AssetDefaultFrozen",),
                stack_inputs={"a": (wtypes.asset_wtype, wtypes.uint64_wtype)},
                stack_outputs=(wtypes.bool_wtype, wtypes.bool_wtype),
            ),
        ),
        "algopy.op.AssetParamsGet.asset_unit_name": (
            FunctionOpMapping(
                op_code="asset_params_get",
                immediates=("AssetUnitName",),
                stack_inputs={"a": (wtypes.asset_wtype, wtypes.uint64_wtype)},
                stack_outputs=(wtypes.bytes_wtype, wtypes.bool_wtype),
            ),
        ),
        "algopy.op.AssetParamsGet.asset_name": (
            FunctionOpMapping(
                op_code="asset_params_get",
                immediates=("AssetName",),
                stack_inputs={"a": (wtypes.asset_wtype, wtypes.uint64_wtype)},
                stack_outputs=(wtypes.bytes_wtype, wtypes.bool_wtype),
            ),
        ),
        "algopy.op.AssetParamsGet.asset_url": (
            FunctionOpMapping(
                op_code="asset_params_get",
                immediates=("AssetURL",),
                stack_inputs={"a": (wtypes.asset_wtype, wtypes.uint64_wtype)},
                stack_outputs=(wtypes.bytes_wtype, wtypes.bool_wtype),
            ),
        ),
        "algopy.op.AssetParamsGet.asset_metadata_hash": (
            FunctionOpMapping(
                op_code="asset_params_get",
                immediates=("AssetMetadataHash",),
                stack_inputs={"a": (wtypes.asset_wtype, wtypes.uint64_wtype)},
                stack_outputs=(wtypes.bytes_wtype, wtypes.bool_wtype),
            ),
        ),
        "algopy.op.AssetParamsGet.asset_manager": (
            FunctionOpMapping(
                op_code="asset_params_get",
                immediates=("AssetManager",),
                stack_inputs={"a": (wtypes.asset_wtype, wtypes.uint64_wtype)},
                stack_outputs=(wtypes.account_wtype, wtypes.bool_wtype),
            ),
        ),
        "algopy.op.AssetParamsGet.asset_reserve": (
            FunctionOpMapping(
                op_code="asset_params_get",
                immediates=("AssetReserve",),
                stack_inputs={"a": (wtypes.asset_wtype, wtypes.uint64_wtype)},
                stack_outputs=(wtypes.account_wtype, wtypes.bool_wtype),
            ),
        ),
        "algopy.op.AssetParamsGet.asset_freeze": (
            FunctionOpMapping(
                op_code="asset_params_get",
                immediates=("AssetFreeze",),
                stack_inputs={"a": (wtypes.asset_wtype, wtypes.uint64_wtype)},
                stack_outputs=(wtypes.account_wtype, wtypes.bool_wtype),
            ),
        ),
        "algopy.op.AssetParamsGet.asset_clawback": (
            FunctionOpMapping(
                op_code="asset_params_get",
                immediates=("AssetClawback",),
                stack_inputs={"a": (wtypes.asset_wtype, wtypes.uint64_wtype)},
                stack_outputs=(wtypes.account_wtype, wtypes.bool_wtype),
            ),
        ),
        "algopy.op.AssetParamsGet.asset_creator": (
            FunctionOpMapping(
                op_code="asset_params_get",
                immediates=("AssetCreator",),
                stack_inputs={"a": (wtypes.asset_wtype, wtypes.uint64_wtype)},
                stack_outputs=(wtypes.account_wtype, wtypes.bool_wtype),
            ),
        ),
        "algopy.op.Block.blk_seed": (
            FunctionOpMapping(
                op_code="block",
                immediates=("BlkSeed",),
                stack_inputs={"a": (wtypes.uint64_wtype,)},
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.Block.blk_timestamp": (
            FunctionOpMapping(
                op_code="block",
                immediates=("BlkTimestamp",),
                stack_inputs={"a": (wtypes.uint64_wtype,)},
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.Box.create": (
            FunctionOpMapping(
                op_code="box_create",
                stack_inputs={"a": (wtypes.bytes_wtype,), "b": (wtypes.uint64_wtype,)},
                stack_outputs=(wtypes.bool_wtype,),
            ),
        ),
        "algopy.op.Box.delete": (
            FunctionOpMapping(
                op_code="box_del",
                stack_inputs={"a": (wtypes.bytes_wtype,)},
                stack_outputs=(wtypes.bool_wtype,),
            ),
        ),
        "algopy.op.Box.extract": (
            FunctionOpMapping(
                op_code="box_extract",
                stack_inputs={
                    "a": (wtypes.bytes_wtype,),
                    "b": (wtypes.uint64_wtype,),
                    "c": (wtypes.uint64_wtype,),
                },
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.Box.get": (
            FunctionOpMapping(
                op_code="box_get",
                stack_inputs={"a": (wtypes.bytes_wtype,)},
                stack_outputs=(wtypes.bytes_wtype, wtypes.bool_wtype),
            ),
        ),
        "algopy.op.Box.length": (
            FunctionOpMapping(
                op_code="box_len",
                stack_inputs={"a": (wtypes.bytes_wtype,)},
                stack_outputs=(wtypes.uint64_wtype, wtypes.bool_wtype),
            ),
        ),
        "algopy.op.Box.put": (
            FunctionOpMapping(
                op_code="box_put",
                stack_inputs={"a": (wtypes.bytes_wtype,), "b": (wtypes.bytes_wtype,)},
            ),
        ),
        "algopy.op.Box.replace": (
            FunctionOpMapping(
                op_code="box_replace",
                stack_inputs={
                    "a": (wtypes.bytes_wtype,),
                    "b": (wtypes.uint64_wtype,),
                    "c": (wtypes.bytes_wtype,),
                },
            ),
        ),
        "algopy.op.Box.resize": (
            FunctionOpMapping(
                op_code="box_resize",
                stack_inputs={"a": (wtypes.bytes_wtype,), "b": (wtypes.uint64_wtype,)},
            ),
        ),
        "algopy.op.Box.splice": (
            FunctionOpMapping(
                op_code="box_splice",
                stack_inputs={
                    "a": (wtypes.bytes_wtype,),
                    "b": (wtypes.uint64_wtype,),
                    "c": (wtypes.uint64_wtype,),
                    "d": (wtypes.bytes_wtype,),
                },
            ),
        ),
        "algopy.op.EllipticCurve.add": (
            FunctionOpMapping(
                op_code="ec_add",
                immediates=(ImmediateArgMapping("g", str),),
                stack_inputs={"a": (wtypes.bytes_wtype,), "b": (wtypes.bytes_wtype,)},
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.EllipticCurve.map_to": (
            FunctionOpMapping(
                op_code="ec_map_to",
                immediates=(ImmediateArgMapping("g", str),),
                stack_inputs={"a": (wtypes.bytes_wtype,)},
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.EllipticCurve.scalar_mul_multi": (
            FunctionOpMapping(
                op_code="ec_multi_scalar_mul",
                immediates=(ImmediateArgMapping("g", str),),
                stack_inputs={"a": (wtypes.bytes_wtype,), "b": (wtypes.bytes_wtype,)},
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.EllipticCurve.pairing_check": (
            FunctionOpMapping(
                op_code="ec_pairing_check",
                immediates=(ImmediateArgMapping("g", str),),
                stack_inputs={"a": (wtypes.bytes_wtype,), "b": (wtypes.bytes_wtype,)},
                stack_outputs=(wtypes.bool_wtype,),
            ),
        ),
        "algopy.op.EllipticCurve.scalar_mul": (
            FunctionOpMapping(
                op_code="ec_scalar_mul",
                immediates=(ImmediateArgMapping("g", str),),
                stack_inputs={"a": (wtypes.bytes_wtype,), "b": (wtypes.bytes_wtype,)},
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.EllipticCurve.subgroup_check": (
            FunctionOpMapping(
                op_code="ec_subgroup_check",
                immediates=(ImmediateArgMapping("g", str),),
                stack_inputs={"a": (wtypes.bytes_wtype,)},
                stack_outputs=(wtypes.bool_wtype,),
            ),
        ),
        "algopy.op.GITxn.sender": (
            FunctionOpMapping(
                op_code="gitxn",
                immediates=(ImmediateArgMapping("t", int), "Sender"),
                stack_outputs=(wtypes.account_wtype,),
            ),
        ),
        "algopy.op.GITxn.fee": (
            FunctionOpMapping(
                op_code="gitxn",
                immediates=(ImmediateArgMapping("t", int), "Fee"),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.GITxn.first_valid": (
            FunctionOpMapping(
                op_code="gitxn",
                immediates=(ImmediateArgMapping("t", int), "FirstValid"),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.GITxn.first_valid_time": (
            FunctionOpMapping(
                op_code="gitxn",
                immediates=(ImmediateArgMapping("t", int), "FirstValidTime"),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.GITxn.last_valid": (
            FunctionOpMapping(
                op_code="gitxn",
                immediates=(ImmediateArgMapping("t", int), "LastValid"),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.GITxn.note": (
            FunctionOpMapping(
                op_code="gitxn",
                immediates=(ImmediateArgMapping("t", int), "Note"),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.GITxn.lease": (
            FunctionOpMapping(
                op_code="gitxn",
                immediates=(ImmediateArgMapping("t", int), "Lease"),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.GITxn.receiver": (
            FunctionOpMapping(
                op_code="gitxn",
                immediates=(ImmediateArgMapping("t", int), "Receiver"),
                stack_outputs=(wtypes.account_wtype,),
            ),
        ),
        "algopy.op.GITxn.amount": (
            FunctionOpMapping(
                op_code="gitxn",
                immediates=(ImmediateArgMapping("t", int), "Amount"),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.GITxn.close_remainder_to": (
            FunctionOpMapping(
                op_code="gitxn",
                immediates=(ImmediateArgMapping("t", int), "CloseRemainderTo"),
                stack_outputs=(wtypes.account_wtype,),
            ),
        ),
        "algopy.op.GITxn.vote_pk": (
            FunctionOpMapping(
                op_code="gitxn",
                immediates=(ImmediateArgMapping("t", int), "VotePK"),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.GITxn.selection_pk": (
            FunctionOpMapping(
                op_code="gitxn",
                immediates=(ImmediateArgMapping("t", int), "SelectionPK"),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.GITxn.vote_first": (
            FunctionOpMapping(
                op_code="gitxn",
                immediates=(ImmediateArgMapping("t", int), "VoteFirst"),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.GITxn.vote_last": (
            FunctionOpMapping(
                op_code="gitxn",
                immediates=(ImmediateArgMapping("t", int), "VoteLast"),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.GITxn.vote_key_dilution": (
            FunctionOpMapping(
                op_code="gitxn",
                immediates=(ImmediateArgMapping("t", int), "VoteKeyDilution"),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.GITxn.type": (
            FunctionOpMapping(
                op_code="gitxn",
                immediates=(ImmediateArgMapping("t", int), "Type"),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.GITxn.type_enum": (
            FunctionOpMapping(
                op_code="gitxn",
                immediates=(ImmediateArgMapping("t", int), "TypeEnum"),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.GITxn.xfer_asset": (
            FunctionOpMapping(
                op_code="gitxn",
                immediates=(ImmediateArgMapping("t", int), "XferAsset"),
                stack_outputs=(wtypes.asset_wtype,),
            ),
        ),
        "algopy.op.GITxn.asset_amount": (
            FunctionOpMapping(
                op_code="gitxn",
                immediates=(ImmediateArgMapping("t", int), "AssetAmount"),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.GITxn.asset_sender": (
            FunctionOpMapping(
                op_code="gitxn",
                immediates=(ImmediateArgMapping("t", int), "AssetSender"),
                stack_outputs=(wtypes.account_wtype,),
            ),
        ),
        "algopy.op.GITxn.asset_receiver": (
            FunctionOpMapping(
                op_code="gitxn",
                immediates=(ImmediateArgMapping("t", int), "AssetReceiver"),
                stack_outputs=(wtypes.account_wtype,),
            ),
        ),
        "algopy.op.GITxn.asset_close_to": (
            FunctionOpMapping(
                op_code="gitxn",
                immediates=(ImmediateArgMapping("t", int), "AssetCloseTo"),
                stack_outputs=(wtypes.account_wtype,),
            ),
        ),
        "algopy.op.GITxn.group_index": (
            FunctionOpMapping(
                op_code="gitxn",
                immediates=(ImmediateArgMapping("t", int), "GroupIndex"),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.GITxn.tx_id": (
            FunctionOpMapping(
                op_code="gitxn",
                immediates=(ImmediateArgMapping("t", int), "TxID"),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.GITxn.application_id": (
            FunctionOpMapping(
                op_code="gitxn",
                immediates=(ImmediateArgMapping("t", int), "ApplicationID"),
                stack_outputs=(wtypes.application_wtype,),
            ),
        ),
        "algopy.op.GITxn.on_completion": (
            FunctionOpMapping(
                op_code="gitxn",
                immediates=(ImmediateArgMapping("t", int), "OnCompletion"),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.GITxn.application_args": (
            FunctionOpMapping(
                op_code="gitxnas",
                immediates=(ImmediateArgMapping("t", int), "ApplicationArgs"),
                stack_inputs={"a": (wtypes.uint64_wtype,)},
                stack_outputs=(wtypes.bytes_wtype,),
            ),
            FunctionOpMapping(
                op_code="gitxna",
                immediates=(
                    ImmediateArgMapping("t", int),
                    "ApplicationArgs",
                    ImmediateArgMapping("a", int),
                ),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.GITxn.num_app_args": (
            FunctionOpMapping(
                op_code="gitxn",
                immediates=(ImmediateArgMapping("t", int), "NumAppArgs"),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.GITxn.accounts": (
            FunctionOpMapping(
                op_code="gitxnas",
                immediates=(ImmediateArgMapping("t", int), "Accounts"),
                stack_inputs={"a": (wtypes.uint64_wtype,)},
                stack_outputs=(wtypes.account_wtype,),
            ),
            FunctionOpMapping(
                op_code="gitxna",
                immediates=(
                    ImmediateArgMapping("t", int),
                    "Accounts",
                    ImmediateArgMapping("a", int),
                ),
                stack_outputs=(wtypes.account_wtype,),
            ),
        ),
        "algopy.op.GITxn.num_accounts": (
            FunctionOpMapping(
                op_code="gitxn",
                immediates=(ImmediateArgMapping("t", int), "NumAccounts"),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.GITxn.approval_program": (
            FunctionOpMapping(
                op_code="gitxn",
                immediates=(ImmediateArgMapping("t", int), "ApprovalProgram"),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.GITxn.clear_state_program": (
            FunctionOpMapping(
                op_code="gitxn",
                immediates=(ImmediateArgMapping("t", int), "ClearStateProgram"),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.GITxn.rekey_to": (
            FunctionOpMapping(
                op_code="gitxn",
                immediates=(ImmediateArgMapping("t", int), "RekeyTo"),
                stack_outputs=(wtypes.account_wtype,),
            ),
        ),
        "algopy.op.GITxn.config_asset": (
            FunctionOpMapping(
                op_code="gitxn",
                immediates=(ImmediateArgMapping("t", int), "ConfigAsset"),
                stack_outputs=(wtypes.asset_wtype,),
            ),
        ),
        "algopy.op.GITxn.config_asset_total": (
            FunctionOpMapping(
                op_code="gitxn",
                immediates=(ImmediateArgMapping("t", int), "ConfigAssetTotal"),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.GITxn.config_asset_decimals": (
            FunctionOpMapping(
                op_code="gitxn",
                immediates=(ImmediateArgMapping("t", int), "ConfigAssetDecimals"),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.GITxn.config_asset_default_frozen": (
            FunctionOpMapping(
                op_code="gitxn",
                immediates=(ImmediateArgMapping("t", int), "ConfigAssetDefaultFrozen"),
                stack_outputs=(wtypes.bool_wtype,),
            ),
        ),
        "algopy.op.GITxn.config_asset_unit_name": (
            FunctionOpMapping(
                op_code="gitxn",
                immediates=(ImmediateArgMapping("t", int), "ConfigAssetUnitName"),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.GITxn.config_asset_name": (
            FunctionOpMapping(
                op_code="gitxn",
                immediates=(ImmediateArgMapping("t", int), "ConfigAssetName"),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.GITxn.config_asset_url": (
            FunctionOpMapping(
                op_code="gitxn",
                immediates=(ImmediateArgMapping("t", int), "ConfigAssetURL"),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.GITxn.config_asset_metadata_hash": (
            FunctionOpMapping(
                op_code="gitxn",
                immediates=(ImmediateArgMapping("t", int), "ConfigAssetMetadataHash"),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.GITxn.config_asset_manager": (
            FunctionOpMapping(
                op_code="gitxn",
                immediates=(ImmediateArgMapping("t", int), "ConfigAssetManager"),
                stack_outputs=(wtypes.account_wtype,),
            ),
        ),
        "algopy.op.GITxn.config_asset_reserve": (
            FunctionOpMapping(
                op_code="gitxn",
                immediates=(ImmediateArgMapping("t", int), "ConfigAssetReserve"),
                stack_outputs=(wtypes.account_wtype,),
            ),
        ),
        "algopy.op.GITxn.config_asset_freeze": (
            FunctionOpMapping(
                op_code="gitxn",
                immediates=(ImmediateArgMapping("t", int), "ConfigAssetFreeze"),
                stack_outputs=(wtypes.account_wtype,),
            ),
        ),
        "algopy.op.GITxn.config_asset_clawback": (
            FunctionOpMapping(
                op_code="gitxn",
                immediates=(ImmediateArgMapping("t", int), "ConfigAssetClawback"),
                stack_outputs=(wtypes.account_wtype,),
            ),
        ),
        "algopy.op.GITxn.freeze_asset": (
            FunctionOpMapping(
                op_code="gitxn",
                immediates=(ImmediateArgMapping("t", int), "FreezeAsset"),
                stack_outputs=(wtypes.asset_wtype,),
            ),
        ),
        "algopy.op.GITxn.freeze_asset_account": (
            FunctionOpMapping(
                op_code="gitxn",
                immediates=(ImmediateArgMapping("t", int), "FreezeAssetAccount"),
                stack_outputs=(wtypes.account_wtype,),
            ),
        ),
        "algopy.op.GITxn.freeze_asset_frozen": (
            FunctionOpMapping(
                op_code="gitxn",
                immediates=(ImmediateArgMapping("t", int), "FreezeAssetFrozen"),
                stack_outputs=(wtypes.bool_wtype,),
            ),
        ),
        "algopy.op.GITxn.assets": (
            FunctionOpMapping(
                op_code="gitxnas",
                immediates=(ImmediateArgMapping("t", int), "Assets"),
                stack_inputs={"a": (wtypes.uint64_wtype,)},
                stack_outputs=(wtypes.asset_wtype,),
            ),
            FunctionOpMapping(
                op_code="gitxna",
                immediates=(
                    ImmediateArgMapping("t", int),
                    "Assets",
                    ImmediateArgMapping("a", int),
                ),
                stack_outputs=(wtypes.asset_wtype,),
            ),
        ),
        "algopy.op.GITxn.num_assets": (
            FunctionOpMapping(
                op_code="gitxn",
                immediates=(ImmediateArgMapping("t", int), "NumAssets"),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.GITxn.applications": (
            FunctionOpMapping(
                op_code="gitxnas",
                immediates=(ImmediateArgMapping("t", int), "Applications"),
                stack_inputs={"a": (wtypes.uint64_wtype,)},
                stack_outputs=(wtypes.application_wtype,),
            ),
            FunctionOpMapping(
                op_code="gitxna",
                immediates=(
                    ImmediateArgMapping("t", int),
                    "Applications",
                    ImmediateArgMapping("a", int),
                ),
                stack_outputs=(wtypes.application_wtype,),
            ),
        ),
        "algopy.op.GITxn.num_applications": (
            FunctionOpMapping(
                op_code="gitxn",
                immediates=(ImmediateArgMapping("t", int), "NumApplications"),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.GITxn.global_num_uint": (
            FunctionOpMapping(
                op_code="gitxn",
                immediates=(ImmediateArgMapping("t", int), "GlobalNumUint"),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.GITxn.global_num_byte_slice": (
            FunctionOpMapping(
                op_code="gitxn",
                immediates=(ImmediateArgMapping("t", int), "GlobalNumByteSlice"),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.GITxn.local_num_uint": (
            FunctionOpMapping(
                op_code="gitxn",
                immediates=(ImmediateArgMapping("t", int), "LocalNumUint"),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.GITxn.local_num_byte_slice": (
            FunctionOpMapping(
                op_code="gitxn",
                immediates=(ImmediateArgMapping("t", int), "LocalNumByteSlice"),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.GITxn.extra_program_pages": (
            FunctionOpMapping(
                op_code="gitxn",
                immediates=(ImmediateArgMapping("t", int), "ExtraProgramPages"),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.GITxn.nonparticipation": (
            FunctionOpMapping(
                op_code="gitxn",
                immediates=(ImmediateArgMapping("t", int), "Nonparticipation"),
                stack_outputs=(wtypes.bool_wtype,),
            ),
        ),
        "algopy.op.GITxn.logs": (
            FunctionOpMapping(
                op_code="gitxnas",
                immediates=(ImmediateArgMapping("t", int), "Logs"),
                stack_inputs={"a": (wtypes.uint64_wtype,)},
                stack_outputs=(wtypes.bytes_wtype,),
            ),
            FunctionOpMapping(
                op_code="gitxna",
                immediates=(ImmediateArgMapping("t", int), "Logs", ImmediateArgMapping("a", int)),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.GITxn.num_logs": (
            FunctionOpMapping(
                op_code="gitxn",
                immediates=(ImmediateArgMapping("t", int), "NumLogs"),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.GITxn.created_asset_id": (
            FunctionOpMapping(
                op_code="gitxn",
                immediates=(ImmediateArgMapping("t", int), "CreatedAssetID"),
                stack_outputs=(wtypes.asset_wtype,),
            ),
        ),
        "algopy.op.GITxn.created_application_id": (
            FunctionOpMapping(
                op_code="gitxn",
                immediates=(ImmediateArgMapping("t", int), "CreatedApplicationID"),
                stack_outputs=(wtypes.application_wtype,),
            ),
        ),
        "algopy.op.GITxn.last_log": (
            FunctionOpMapping(
                op_code="gitxn",
                immediates=(ImmediateArgMapping("t", int), "LastLog"),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.GITxn.state_proof_pk": (
            FunctionOpMapping(
                op_code="gitxn",
                immediates=(ImmediateArgMapping("t", int), "StateProofPK"),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.GITxn.approval_program_pages": (
            FunctionOpMapping(
                op_code="gitxnas",
                immediates=(ImmediateArgMapping("t", int), "ApprovalProgramPages"),
                stack_inputs={"a": (wtypes.uint64_wtype,)},
                stack_outputs=(wtypes.bytes_wtype,),
            ),
            FunctionOpMapping(
                op_code="gitxna",
                immediates=(
                    ImmediateArgMapping("t", int),
                    "ApprovalProgramPages",
                    ImmediateArgMapping("a", int),
                ),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.GITxn.num_approval_program_pages": (
            FunctionOpMapping(
                op_code="gitxn",
                immediates=(ImmediateArgMapping("t", int), "NumApprovalProgramPages"),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.GITxn.clear_state_program_pages": (
            FunctionOpMapping(
                op_code="gitxnas",
                immediates=(ImmediateArgMapping("t", int), "ClearStateProgramPages"),
                stack_inputs={"a": (wtypes.uint64_wtype,)},
                stack_outputs=(wtypes.bytes_wtype,),
            ),
            FunctionOpMapping(
                op_code="gitxna",
                immediates=(
                    ImmediateArgMapping("t", int),
                    "ClearStateProgramPages",
                    ImmediateArgMapping("a", int),
                ),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.GITxn.num_clear_state_program_pages": (
            FunctionOpMapping(
                op_code="gitxn",
                immediates=(ImmediateArgMapping("t", int), "NumClearStateProgramPages"),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.GTxn.sender": (
            FunctionOpMapping(
                op_code="gtxns",
                immediates=("Sender",),
                stack_inputs={"a": (wtypes.uint64_wtype,)},
                stack_outputs=(wtypes.account_wtype,),
            ),
            FunctionOpMapping(
                op_code="gtxn",
                immediates=(ImmediateArgMapping("a", int), "Sender"),
                stack_outputs=(wtypes.account_wtype,),
            ),
        ),
        "algopy.op.GTxn.fee": (
            FunctionOpMapping(
                op_code="gtxns",
                immediates=("Fee",),
                stack_inputs={"a": (wtypes.uint64_wtype,)},
                stack_outputs=(wtypes.uint64_wtype,),
            ),
            FunctionOpMapping(
                op_code="gtxn",
                immediates=(ImmediateArgMapping("a", int), "Fee"),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.GTxn.first_valid": (
            FunctionOpMapping(
                op_code="gtxns",
                immediates=("FirstValid",),
                stack_inputs={"a": (wtypes.uint64_wtype,)},
                stack_outputs=(wtypes.uint64_wtype,),
            ),
            FunctionOpMapping(
                op_code="gtxn",
                immediates=(ImmediateArgMapping("a", int), "FirstValid"),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.GTxn.first_valid_time": (
            FunctionOpMapping(
                op_code="gtxns",
                immediates=("FirstValidTime",),
                stack_inputs={"a": (wtypes.uint64_wtype,)},
                stack_outputs=(wtypes.uint64_wtype,),
            ),
            FunctionOpMapping(
                op_code="gtxn",
                immediates=(ImmediateArgMapping("a", int), "FirstValidTime"),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.GTxn.last_valid": (
            FunctionOpMapping(
                op_code="gtxns",
                immediates=("LastValid",),
                stack_inputs={"a": (wtypes.uint64_wtype,)},
                stack_outputs=(wtypes.uint64_wtype,),
            ),
            FunctionOpMapping(
                op_code="gtxn",
                immediates=(ImmediateArgMapping("a", int), "LastValid"),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.GTxn.note": (
            FunctionOpMapping(
                op_code="gtxns",
                immediates=("Note",),
                stack_inputs={"a": (wtypes.uint64_wtype,)},
                stack_outputs=(wtypes.bytes_wtype,),
            ),
            FunctionOpMapping(
                op_code="gtxn",
                immediates=(ImmediateArgMapping("a", int), "Note"),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.GTxn.lease": (
            FunctionOpMapping(
                op_code="gtxns",
                immediates=("Lease",),
                stack_inputs={"a": (wtypes.uint64_wtype,)},
                stack_outputs=(wtypes.bytes_wtype,),
            ),
            FunctionOpMapping(
                op_code="gtxn",
                immediates=(ImmediateArgMapping("a", int), "Lease"),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.GTxn.receiver": (
            FunctionOpMapping(
                op_code="gtxns",
                immediates=("Receiver",),
                stack_inputs={"a": (wtypes.uint64_wtype,)},
                stack_outputs=(wtypes.account_wtype,),
            ),
            FunctionOpMapping(
                op_code="gtxn",
                immediates=(ImmediateArgMapping("a", int), "Receiver"),
                stack_outputs=(wtypes.account_wtype,),
            ),
        ),
        "algopy.op.GTxn.amount": (
            FunctionOpMapping(
                op_code="gtxns",
                immediates=("Amount",),
                stack_inputs={"a": (wtypes.uint64_wtype,)},
                stack_outputs=(wtypes.uint64_wtype,),
            ),
            FunctionOpMapping(
                op_code="gtxn",
                immediates=(ImmediateArgMapping("a", int), "Amount"),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.GTxn.close_remainder_to": (
            FunctionOpMapping(
                op_code="gtxns",
                immediates=("CloseRemainderTo",),
                stack_inputs={"a": (wtypes.uint64_wtype,)},
                stack_outputs=(wtypes.account_wtype,),
            ),
            FunctionOpMapping(
                op_code="gtxn",
                immediates=(ImmediateArgMapping("a", int), "CloseRemainderTo"),
                stack_outputs=(wtypes.account_wtype,),
            ),
        ),
        "algopy.op.GTxn.vote_pk": (
            FunctionOpMapping(
                op_code="gtxns",
                immediates=("VotePK",),
                stack_inputs={"a": (wtypes.uint64_wtype,)},
                stack_outputs=(wtypes.bytes_wtype,),
            ),
            FunctionOpMapping(
                op_code="gtxn",
                immediates=(ImmediateArgMapping("a", int), "VotePK"),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.GTxn.selection_pk": (
            FunctionOpMapping(
                op_code="gtxns",
                immediates=("SelectionPK",),
                stack_inputs={"a": (wtypes.uint64_wtype,)},
                stack_outputs=(wtypes.bytes_wtype,),
            ),
            FunctionOpMapping(
                op_code="gtxn",
                immediates=(ImmediateArgMapping("a", int), "SelectionPK"),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.GTxn.vote_first": (
            FunctionOpMapping(
                op_code="gtxns",
                immediates=("VoteFirst",),
                stack_inputs={"a": (wtypes.uint64_wtype,)},
                stack_outputs=(wtypes.uint64_wtype,),
            ),
            FunctionOpMapping(
                op_code="gtxn",
                immediates=(ImmediateArgMapping("a", int), "VoteFirst"),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.GTxn.vote_last": (
            FunctionOpMapping(
                op_code="gtxns",
                immediates=("VoteLast",),
                stack_inputs={"a": (wtypes.uint64_wtype,)},
                stack_outputs=(wtypes.uint64_wtype,),
            ),
            FunctionOpMapping(
                op_code="gtxn",
                immediates=(ImmediateArgMapping("a", int), "VoteLast"),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.GTxn.vote_key_dilution": (
            FunctionOpMapping(
                op_code="gtxns",
                immediates=("VoteKeyDilution",),
                stack_inputs={"a": (wtypes.uint64_wtype,)},
                stack_outputs=(wtypes.uint64_wtype,),
            ),
            FunctionOpMapping(
                op_code="gtxn",
                immediates=(ImmediateArgMapping("a", int), "VoteKeyDilution"),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.GTxn.type": (
            FunctionOpMapping(
                op_code="gtxns",
                immediates=("Type",),
                stack_inputs={"a": (wtypes.uint64_wtype,)},
                stack_outputs=(wtypes.bytes_wtype,),
            ),
            FunctionOpMapping(
                op_code="gtxn",
                immediates=(ImmediateArgMapping("a", int), "Type"),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.GTxn.type_enum": (
            FunctionOpMapping(
                op_code="gtxns",
                immediates=("TypeEnum",),
                stack_inputs={"a": (wtypes.uint64_wtype,)},
                stack_outputs=(wtypes.uint64_wtype,),
            ),
            FunctionOpMapping(
                op_code="gtxn",
                immediates=(ImmediateArgMapping("a", int), "TypeEnum"),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.GTxn.xfer_asset": (
            FunctionOpMapping(
                op_code="gtxns",
                immediates=("XferAsset",),
                stack_inputs={"a": (wtypes.uint64_wtype,)},
                stack_outputs=(wtypes.asset_wtype,),
            ),
            FunctionOpMapping(
                op_code="gtxn",
                immediates=(ImmediateArgMapping("a", int), "XferAsset"),
                stack_outputs=(wtypes.asset_wtype,),
            ),
        ),
        "algopy.op.GTxn.asset_amount": (
            FunctionOpMapping(
                op_code="gtxns",
                immediates=("AssetAmount",),
                stack_inputs={"a": (wtypes.uint64_wtype,)},
                stack_outputs=(wtypes.uint64_wtype,),
            ),
            FunctionOpMapping(
                op_code="gtxn",
                immediates=(ImmediateArgMapping("a", int), "AssetAmount"),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.GTxn.asset_sender": (
            FunctionOpMapping(
                op_code="gtxns",
                immediates=("AssetSender",),
                stack_inputs={"a": (wtypes.uint64_wtype,)},
                stack_outputs=(wtypes.account_wtype,),
            ),
            FunctionOpMapping(
                op_code="gtxn",
                immediates=(ImmediateArgMapping("a", int), "AssetSender"),
                stack_outputs=(wtypes.account_wtype,),
            ),
        ),
        "algopy.op.GTxn.asset_receiver": (
            FunctionOpMapping(
                op_code="gtxns",
                immediates=("AssetReceiver",),
                stack_inputs={"a": (wtypes.uint64_wtype,)},
                stack_outputs=(wtypes.account_wtype,),
            ),
            FunctionOpMapping(
                op_code="gtxn",
                immediates=(ImmediateArgMapping("a", int), "AssetReceiver"),
                stack_outputs=(wtypes.account_wtype,),
            ),
        ),
        "algopy.op.GTxn.asset_close_to": (
            FunctionOpMapping(
                op_code="gtxns",
                immediates=("AssetCloseTo",),
                stack_inputs={"a": (wtypes.uint64_wtype,)},
                stack_outputs=(wtypes.account_wtype,),
            ),
            FunctionOpMapping(
                op_code="gtxn",
                immediates=(ImmediateArgMapping("a", int), "AssetCloseTo"),
                stack_outputs=(wtypes.account_wtype,),
            ),
        ),
        "algopy.op.GTxn.group_index": (
            FunctionOpMapping(
                op_code="gtxns",
                immediates=("GroupIndex",),
                stack_inputs={"a": (wtypes.uint64_wtype,)},
                stack_outputs=(wtypes.uint64_wtype,),
            ),
            FunctionOpMapping(
                op_code="gtxn",
                immediates=(ImmediateArgMapping("a", int), "GroupIndex"),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.GTxn.tx_id": (
            FunctionOpMapping(
                op_code="gtxns",
                immediates=("TxID",),
                stack_inputs={"a": (wtypes.uint64_wtype,)},
                stack_outputs=(wtypes.bytes_wtype,),
            ),
            FunctionOpMapping(
                op_code="gtxn",
                immediates=(ImmediateArgMapping("a", int), "TxID"),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.GTxn.application_id": (
            FunctionOpMapping(
                op_code="gtxns",
                immediates=("ApplicationID",),
                stack_inputs={"a": (wtypes.uint64_wtype,)},
                stack_outputs=(wtypes.application_wtype,),
            ),
            FunctionOpMapping(
                op_code="gtxn",
                immediates=(ImmediateArgMapping("a", int), "ApplicationID"),
                stack_outputs=(wtypes.application_wtype,),
            ),
        ),
        "algopy.op.GTxn.on_completion": (
            FunctionOpMapping(
                op_code="gtxns",
                immediates=("OnCompletion",),
                stack_inputs={"a": (wtypes.uint64_wtype,)},
                stack_outputs=(wtypes.uint64_wtype,),
            ),
            FunctionOpMapping(
                op_code="gtxn",
                immediates=(ImmediateArgMapping("a", int), "OnCompletion"),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.GTxn.application_args": (
            FunctionOpMapping(
                op_code="gtxnsas",
                immediates=("ApplicationArgs",),
                stack_inputs={"a": (wtypes.uint64_wtype,), "b": (wtypes.uint64_wtype,)},
                stack_outputs=(wtypes.bytes_wtype,),
            ),
            FunctionOpMapping(
                op_code="gtxnsa",
                immediates=("ApplicationArgs", ImmediateArgMapping("b", int)),
                stack_inputs={"a": (wtypes.uint64_wtype,)},
                stack_outputs=(wtypes.bytes_wtype,),
            ),
            FunctionOpMapping(
                op_code="gtxna",
                immediates=(
                    ImmediateArgMapping("a", int),
                    "ApplicationArgs",
                    ImmediateArgMapping("b", int),
                ),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
            FunctionOpMapping(
                op_code="gtxnas",
                immediates=(ImmediateArgMapping("a", int), "ApplicationArgs"),
                stack_inputs={"b": (wtypes.uint64_wtype,)},
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.GTxn.num_app_args": (
            FunctionOpMapping(
                op_code="gtxns",
                immediates=("NumAppArgs",),
                stack_inputs={"a": (wtypes.uint64_wtype,)},
                stack_outputs=(wtypes.uint64_wtype,),
            ),
            FunctionOpMapping(
                op_code="gtxn",
                immediates=(ImmediateArgMapping("a", int), "NumAppArgs"),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.GTxn.accounts": (
            FunctionOpMapping(
                op_code="gtxnsas",
                immediates=("Accounts",),
                stack_inputs={"a": (wtypes.uint64_wtype,), "b": (wtypes.uint64_wtype,)},
                stack_outputs=(wtypes.account_wtype,),
            ),
            FunctionOpMapping(
                op_code="gtxnsa",
                immediates=("Accounts", ImmediateArgMapping("b", int)),
                stack_inputs={"a": (wtypes.uint64_wtype,)},
                stack_outputs=(wtypes.account_wtype,),
            ),
            FunctionOpMapping(
                op_code="gtxna",
                immediates=(
                    ImmediateArgMapping("a", int),
                    "Accounts",
                    ImmediateArgMapping("b", int),
                ),
                stack_outputs=(wtypes.account_wtype,),
            ),
            FunctionOpMapping(
                op_code="gtxnas",
                immediates=(ImmediateArgMapping("a", int), "Accounts"),
                stack_inputs={"b": (wtypes.uint64_wtype,)},
                stack_outputs=(wtypes.account_wtype,),
            ),
        ),
        "algopy.op.GTxn.num_accounts": (
            FunctionOpMapping(
                op_code="gtxns",
                immediates=("NumAccounts",),
                stack_inputs={"a": (wtypes.uint64_wtype,)},
                stack_outputs=(wtypes.uint64_wtype,),
            ),
            FunctionOpMapping(
                op_code="gtxn",
                immediates=(ImmediateArgMapping("a", int), "NumAccounts"),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.GTxn.approval_program": (
            FunctionOpMapping(
                op_code="gtxns",
                immediates=("ApprovalProgram",),
                stack_inputs={"a": (wtypes.uint64_wtype,)},
                stack_outputs=(wtypes.bytes_wtype,),
            ),
            FunctionOpMapping(
                op_code="gtxn",
                immediates=(ImmediateArgMapping("a", int), "ApprovalProgram"),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.GTxn.clear_state_program": (
            FunctionOpMapping(
                op_code="gtxns",
                immediates=("ClearStateProgram",),
                stack_inputs={"a": (wtypes.uint64_wtype,)},
                stack_outputs=(wtypes.bytes_wtype,),
            ),
            FunctionOpMapping(
                op_code="gtxn",
                immediates=(ImmediateArgMapping("a", int), "ClearStateProgram"),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.GTxn.rekey_to": (
            FunctionOpMapping(
                op_code="gtxns",
                immediates=("RekeyTo",),
                stack_inputs={"a": (wtypes.uint64_wtype,)},
                stack_outputs=(wtypes.account_wtype,),
            ),
            FunctionOpMapping(
                op_code="gtxn",
                immediates=(ImmediateArgMapping("a", int), "RekeyTo"),
                stack_outputs=(wtypes.account_wtype,),
            ),
        ),
        "algopy.op.GTxn.config_asset": (
            FunctionOpMapping(
                op_code="gtxns",
                immediates=("ConfigAsset",),
                stack_inputs={"a": (wtypes.uint64_wtype,)},
                stack_outputs=(wtypes.asset_wtype,),
            ),
            FunctionOpMapping(
                op_code="gtxn",
                immediates=(ImmediateArgMapping("a", int), "ConfigAsset"),
                stack_outputs=(wtypes.asset_wtype,),
            ),
        ),
        "algopy.op.GTxn.config_asset_total": (
            FunctionOpMapping(
                op_code="gtxns",
                immediates=("ConfigAssetTotal",),
                stack_inputs={"a": (wtypes.uint64_wtype,)},
                stack_outputs=(wtypes.uint64_wtype,),
            ),
            FunctionOpMapping(
                op_code="gtxn",
                immediates=(ImmediateArgMapping("a", int), "ConfigAssetTotal"),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.GTxn.config_asset_decimals": (
            FunctionOpMapping(
                op_code="gtxns",
                immediates=("ConfigAssetDecimals",),
                stack_inputs={"a": (wtypes.uint64_wtype,)},
                stack_outputs=(wtypes.uint64_wtype,),
            ),
            FunctionOpMapping(
                op_code="gtxn",
                immediates=(ImmediateArgMapping("a", int), "ConfigAssetDecimals"),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.GTxn.config_asset_default_frozen": (
            FunctionOpMapping(
                op_code="gtxns",
                immediates=("ConfigAssetDefaultFrozen",),
                stack_inputs={"a": (wtypes.uint64_wtype,)},
                stack_outputs=(wtypes.bool_wtype,),
            ),
            FunctionOpMapping(
                op_code="gtxn",
                immediates=(ImmediateArgMapping("a", int), "ConfigAssetDefaultFrozen"),
                stack_outputs=(wtypes.bool_wtype,),
            ),
        ),
        "algopy.op.GTxn.config_asset_unit_name": (
            FunctionOpMapping(
                op_code="gtxns",
                immediates=("ConfigAssetUnitName",),
                stack_inputs={"a": (wtypes.uint64_wtype,)},
                stack_outputs=(wtypes.bytes_wtype,),
            ),
            FunctionOpMapping(
                op_code="gtxn",
                immediates=(ImmediateArgMapping("a", int), "ConfigAssetUnitName"),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.GTxn.config_asset_name": (
            FunctionOpMapping(
                op_code="gtxns",
                immediates=("ConfigAssetName",),
                stack_inputs={"a": (wtypes.uint64_wtype,)},
                stack_outputs=(wtypes.bytes_wtype,),
            ),
            FunctionOpMapping(
                op_code="gtxn",
                immediates=(ImmediateArgMapping("a", int), "ConfigAssetName"),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.GTxn.config_asset_url": (
            FunctionOpMapping(
                op_code="gtxns",
                immediates=("ConfigAssetURL",),
                stack_inputs={"a": (wtypes.uint64_wtype,)},
                stack_outputs=(wtypes.bytes_wtype,),
            ),
            FunctionOpMapping(
                op_code="gtxn",
                immediates=(ImmediateArgMapping("a", int), "ConfigAssetURL"),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.GTxn.config_asset_metadata_hash": (
            FunctionOpMapping(
                op_code="gtxns",
                immediates=("ConfigAssetMetadataHash",),
                stack_inputs={"a": (wtypes.uint64_wtype,)},
                stack_outputs=(wtypes.bytes_wtype,),
            ),
            FunctionOpMapping(
                op_code="gtxn",
                immediates=(ImmediateArgMapping("a", int), "ConfigAssetMetadataHash"),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.GTxn.config_asset_manager": (
            FunctionOpMapping(
                op_code="gtxns",
                immediates=("ConfigAssetManager",),
                stack_inputs={"a": (wtypes.uint64_wtype,)},
                stack_outputs=(wtypes.account_wtype,),
            ),
            FunctionOpMapping(
                op_code="gtxn",
                immediates=(ImmediateArgMapping("a", int), "ConfigAssetManager"),
                stack_outputs=(wtypes.account_wtype,),
            ),
        ),
        "algopy.op.GTxn.config_asset_reserve": (
            FunctionOpMapping(
                op_code="gtxns",
                immediates=("ConfigAssetReserve",),
                stack_inputs={"a": (wtypes.uint64_wtype,)},
                stack_outputs=(wtypes.account_wtype,),
            ),
            FunctionOpMapping(
                op_code="gtxn",
                immediates=(ImmediateArgMapping("a", int), "ConfigAssetReserve"),
                stack_outputs=(wtypes.account_wtype,),
            ),
        ),
        "algopy.op.GTxn.config_asset_freeze": (
            FunctionOpMapping(
                op_code="gtxns",
                immediates=("ConfigAssetFreeze",),
                stack_inputs={"a": (wtypes.uint64_wtype,)},
                stack_outputs=(wtypes.account_wtype,),
            ),
            FunctionOpMapping(
                op_code="gtxn",
                immediates=(ImmediateArgMapping("a", int), "ConfigAssetFreeze"),
                stack_outputs=(wtypes.account_wtype,),
            ),
        ),
        "algopy.op.GTxn.config_asset_clawback": (
            FunctionOpMapping(
                op_code="gtxns",
                immediates=("ConfigAssetClawback",),
                stack_inputs={"a": (wtypes.uint64_wtype,)},
                stack_outputs=(wtypes.account_wtype,),
            ),
            FunctionOpMapping(
                op_code="gtxn",
                immediates=(ImmediateArgMapping("a", int), "ConfigAssetClawback"),
                stack_outputs=(wtypes.account_wtype,),
            ),
        ),
        "algopy.op.GTxn.freeze_asset": (
            FunctionOpMapping(
                op_code="gtxns",
                immediates=("FreezeAsset",),
                stack_inputs={"a": (wtypes.uint64_wtype,)},
                stack_outputs=(wtypes.asset_wtype,),
            ),
            FunctionOpMapping(
                op_code="gtxn",
                immediates=(ImmediateArgMapping("a", int), "FreezeAsset"),
                stack_outputs=(wtypes.asset_wtype,),
            ),
        ),
        "algopy.op.GTxn.freeze_asset_account": (
            FunctionOpMapping(
                op_code="gtxns",
                immediates=("FreezeAssetAccount",),
                stack_inputs={"a": (wtypes.uint64_wtype,)},
                stack_outputs=(wtypes.account_wtype,),
            ),
            FunctionOpMapping(
                op_code="gtxn",
                immediates=(ImmediateArgMapping("a", int), "FreezeAssetAccount"),
                stack_outputs=(wtypes.account_wtype,),
            ),
        ),
        "algopy.op.GTxn.freeze_asset_frozen": (
            FunctionOpMapping(
                op_code="gtxns",
                immediates=("FreezeAssetFrozen",),
                stack_inputs={"a": (wtypes.uint64_wtype,)},
                stack_outputs=(wtypes.bool_wtype,),
            ),
            FunctionOpMapping(
                op_code="gtxn",
                immediates=(ImmediateArgMapping("a", int), "FreezeAssetFrozen"),
                stack_outputs=(wtypes.bool_wtype,),
            ),
        ),
        "algopy.op.GTxn.assets": (
            FunctionOpMapping(
                op_code="gtxnsas",
                immediates=("Assets",),
                stack_inputs={"a": (wtypes.uint64_wtype,), "b": (wtypes.uint64_wtype,)},
                stack_outputs=(wtypes.asset_wtype,),
            ),
            FunctionOpMapping(
                op_code="gtxnsa",
                immediates=("Assets", ImmediateArgMapping("b", int)),
                stack_inputs={"a": (wtypes.uint64_wtype,)},
                stack_outputs=(wtypes.asset_wtype,),
            ),
            FunctionOpMapping(
                op_code="gtxna",
                immediates=(
                    ImmediateArgMapping("a", int),
                    "Assets",
                    ImmediateArgMapping("b", int),
                ),
                stack_outputs=(wtypes.asset_wtype,),
            ),
            FunctionOpMapping(
                op_code="gtxnas",
                immediates=(ImmediateArgMapping("a", int), "Assets"),
                stack_inputs={"b": (wtypes.uint64_wtype,)},
                stack_outputs=(wtypes.asset_wtype,),
            ),
        ),
        "algopy.op.GTxn.num_assets": (
            FunctionOpMapping(
                op_code="gtxns",
                immediates=("NumAssets",),
                stack_inputs={"a": (wtypes.uint64_wtype,)},
                stack_outputs=(wtypes.uint64_wtype,),
            ),
            FunctionOpMapping(
                op_code="gtxn",
                immediates=(ImmediateArgMapping("a", int), "NumAssets"),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.GTxn.applications": (
            FunctionOpMapping(
                op_code="gtxnsas",
                immediates=("Applications",),
                stack_inputs={"a": (wtypes.uint64_wtype,), "b": (wtypes.uint64_wtype,)},
                stack_outputs=(wtypes.application_wtype,),
            ),
            FunctionOpMapping(
                op_code="gtxnsa",
                immediates=("Applications", ImmediateArgMapping("b", int)),
                stack_inputs={"a": (wtypes.uint64_wtype,)},
                stack_outputs=(wtypes.application_wtype,),
            ),
            FunctionOpMapping(
                op_code="gtxna",
                immediates=(
                    ImmediateArgMapping("a", int),
                    "Applications",
                    ImmediateArgMapping("b", int),
                ),
                stack_outputs=(wtypes.application_wtype,),
            ),
            FunctionOpMapping(
                op_code="gtxnas",
                immediates=(ImmediateArgMapping("a", int), "Applications"),
                stack_inputs={"b": (wtypes.uint64_wtype,)},
                stack_outputs=(wtypes.application_wtype,),
            ),
        ),
        "algopy.op.GTxn.num_applications": (
            FunctionOpMapping(
                op_code="gtxns",
                immediates=("NumApplications",),
                stack_inputs={"a": (wtypes.uint64_wtype,)},
                stack_outputs=(wtypes.uint64_wtype,),
            ),
            FunctionOpMapping(
                op_code="gtxn",
                immediates=(ImmediateArgMapping("a", int), "NumApplications"),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.GTxn.global_num_uint": (
            FunctionOpMapping(
                op_code="gtxns",
                immediates=("GlobalNumUint",),
                stack_inputs={"a": (wtypes.uint64_wtype,)},
                stack_outputs=(wtypes.uint64_wtype,),
            ),
            FunctionOpMapping(
                op_code="gtxn",
                immediates=(ImmediateArgMapping("a", int), "GlobalNumUint"),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.GTxn.global_num_byte_slice": (
            FunctionOpMapping(
                op_code="gtxns",
                immediates=("GlobalNumByteSlice",),
                stack_inputs={"a": (wtypes.uint64_wtype,)},
                stack_outputs=(wtypes.uint64_wtype,),
            ),
            FunctionOpMapping(
                op_code="gtxn",
                immediates=(ImmediateArgMapping("a", int), "GlobalNumByteSlice"),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.GTxn.local_num_uint": (
            FunctionOpMapping(
                op_code="gtxns",
                immediates=("LocalNumUint",),
                stack_inputs={"a": (wtypes.uint64_wtype,)},
                stack_outputs=(wtypes.uint64_wtype,),
            ),
            FunctionOpMapping(
                op_code="gtxn",
                immediates=(ImmediateArgMapping("a", int), "LocalNumUint"),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.GTxn.local_num_byte_slice": (
            FunctionOpMapping(
                op_code="gtxns",
                immediates=("LocalNumByteSlice",),
                stack_inputs={"a": (wtypes.uint64_wtype,)},
                stack_outputs=(wtypes.uint64_wtype,),
            ),
            FunctionOpMapping(
                op_code="gtxn",
                immediates=(ImmediateArgMapping("a", int), "LocalNumByteSlice"),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.GTxn.extra_program_pages": (
            FunctionOpMapping(
                op_code="gtxns",
                immediates=("ExtraProgramPages",),
                stack_inputs={"a": (wtypes.uint64_wtype,)},
                stack_outputs=(wtypes.uint64_wtype,),
            ),
            FunctionOpMapping(
                op_code="gtxn",
                immediates=(ImmediateArgMapping("a", int), "ExtraProgramPages"),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.GTxn.nonparticipation": (
            FunctionOpMapping(
                op_code="gtxns",
                immediates=("Nonparticipation",),
                stack_inputs={"a": (wtypes.uint64_wtype,)},
                stack_outputs=(wtypes.bool_wtype,),
            ),
            FunctionOpMapping(
                op_code="gtxn",
                immediates=(ImmediateArgMapping("a", int), "Nonparticipation"),
                stack_outputs=(wtypes.bool_wtype,),
            ),
        ),
        "algopy.op.GTxn.logs": (
            FunctionOpMapping(
                op_code="gtxnsas",
                immediates=("Logs",),
                stack_inputs={"a": (wtypes.uint64_wtype,), "b": (wtypes.uint64_wtype,)},
                stack_outputs=(wtypes.bytes_wtype,),
            ),
            FunctionOpMapping(
                op_code="gtxnsa",
                immediates=("Logs", ImmediateArgMapping("b", int)),
                stack_inputs={"a": (wtypes.uint64_wtype,)},
                stack_outputs=(wtypes.bytes_wtype,),
            ),
            FunctionOpMapping(
                op_code="gtxna",
                immediates=(ImmediateArgMapping("a", int), "Logs", ImmediateArgMapping("b", int)),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
            FunctionOpMapping(
                op_code="gtxnas",
                immediates=(ImmediateArgMapping("a", int), "Logs"),
                stack_inputs={"b": (wtypes.uint64_wtype,)},
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.GTxn.num_logs": (
            FunctionOpMapping(
                op_code="gtxns",
                immediates=("NumLogs",),
                stack_inputs={"a": (wtypes.uint64_wtype,)},
                stack_outputs=(wtypes.uint64_wtype,),
            ),
            FunctionOpMapping(
                op_code="gtxn",
                immediates=(ImmediateArgMapping("a", int), "NumLogs"),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.GTxn.created_asset_id": (
            FunctionOpMapping(
                op_code="gtxns",
                immediates=("CreatedAssetID",),
                stack_inputs={"a": (wtypes.uint64_wtype,)},
                stack_outputs=(wtypes.asset_wtype,),
            ),
            FunctionOpMapping(
                op_code="gtxn",
                immediates=(ImmediateArgMapping("a", int), "CreatedAssetID"),
                stack_outputs=(wtypes.asset_wtype,),
            ),
        ),
        "algopy.op.GTxn.created_application_id": (
            FunctionOpMapping(
                op_code="gtxns",
                immediates=("CreatedApplicationID",),
                stack_inputs={"a": (wtypes.uint64_wtype,)},
                stack_outputs=(wtypes.application_wtype,),
            ),
            FunctionOpMapping(
                op_code="gtxn",
                immediates=(ImmediateArgMapping("a", int), "CreatedApplicationID"),
                stack_outputs=(wtypes.application_wtype,),
            ),
        ),
        "algopy.op.GTxn.last_log": (
            FunctionOpMapping(
                op_code="gtxns",
                immediates=("LastLog",),
                stack_inputs={"a": (wtypes.uint64_wtype,)},
                stack_outputs=(wtypes.bytes_wtype,),
            ),
            FunctionOpMapping(
                op_code="gtxn",
                immediates=(ImmediateArgMapping("a", int), "LastLog"),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.GTxn.state_proof_pk": (
            FunctionOpMapping(
                op_code="gtxns",
                immediates=("StateProofPK",),
                stack_inputs={"a": (wtypes.uint64_wtype,)},
                stack_outputs=(wtypes.bytes_wtype,),
            ),
            FunctionOpMapping(
                op_code="gtxn",
                immediates=(ImmediateArgMapping("a", int), "StateProofPK"),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.GTxn.approval_program_pages": (
            FunctionOpMapping(
                op_code="gtxnsas",
                immediates=("ApprovalProgramPages",),
                stack_inputs={"a": (wtypes.uint64_wtype,), "b": (wtypes.uint64_wtype,)},
                stack_outputs=(wtypes.bytes_wtype,),
            ),
            FunctionOpMapping(
                op_code="gtxnsa",
                immediates=("ApprovalProgramPages", ImmediateArgMapping("b", int)),
                stack_inputs={"a": (wtypes.uint64_wtype,)},
                stack_outputs=(wtypes.bytes_wtype,),
            ),
            FunctionOpMapping(
                op_code="gtxna",
                immediates=(
                    ImmediateArgMapping("a", int),
                    "ApprovalProgramPages",
                    ImmediateArgMapping("b", int),
                ),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
            FunctionOpMapping(
                op_code="gtxnas",
                immediates=(ImmediateArgMapping("a", int), "ApprovalProgramPages"),
                stack_inputs={"b": (wtypes.uint64_wtype,)},
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.GTxn.num_approval_program_pages": (
            FunctionOpMapping(
                op_code="gtxns",
                immediates=("NumApprovalProgramPages",),
                stack_inputs={"a": (wtypes.uint64_wtype,)},
                stack_outputs=(wtypes.uint64_wtype,),
            ),
            FunctionOpMapping(
                op_code="gtxn",
                immediates=(ImmediateArgMapping("a", int), "NumApprovalProgramPages"),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.GTxn.clear_state_program_pages": (
            FunctionOpMapping(
                op_code="gtxnsas",
                immediates=("ClearStateProgramPages",),
                stack_inputs={"a": (wtypes.uint64_wtype,), "b": (wtypes.uint64_wtype,)},
                stack_outputs=(wtypes.bytes_wtype,),
            ),
            FunctionOpMapping(
                op_code="gtxnsa",
                immediates=("ClearStateProgramPages", ImmediateArgMapping("b", int)),
                stack_inputs={"a": (wtypes.uint64_wtype,)},
                stack_outputs=(wtypes.bytes_wtype,),
            ),
            FunctionOpMapping(
                op_code="gtxna",
                immediates=(
                    ImmediateArgMapping("a", int),
                    "ClearStateProgramPages",
                    ImmediateArgMapping("b", int),
                ),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
            FunctionOpMapping(
                op_code="gtxnas",
                immediates=(ImmediateArgMapping("a", int), "ClearStateProgramPages"),
                stack_inputs={"b": (wtypes.uint64_wtype,)},
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.GTxn.num_clear_state_program_pages": (
            FunctionOpMapping(
                op_code="gtxns",
                immediates=("NumClearStateProgramPages",),
                stack_inputs={"a": (wtypes.uint64_wtype,)},
                stack_outputs=(wtypes.uint64_wtype,),
            ),
            FunctionOpMapping(
                op_code="gtxn",
                immediates=(ImmediateArgMapping("a", int), "NumClearStateProgramPages"),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.Global.min_txn_fee": (
            FunctionOpMapping(
                op_code="global", immediates=("MinTxnFee",), stack_outputs=(wtypes.uint64_wtype,)
            ),
        ),
        "algopy.op.Global.min_balance": (
            FunctionOpMapping(
                op_code="global", immediates=("MinBalance",), stack_outputs=(wtypes.uint64_wtype,)
            ),
        ),
        "algopy.op.Global.max_txn_life": (
            FunctionOpMapping(
                op_code="global", immediates=("MaxTxnLife",), stack_outputs=(wtypes.uint64_wtype,)
            ),
        ),
        "algopy.op.Global.zero_address": (
            FunctionOpMapping(
                op_code="global",
                immediates=("ZeroAddress",),
                stack_outputs=(wtypes.account_wtype,),
            ),
        ),
        "algopy.op.Global.group_size": (
            FunctionOpMapping(
                op_code="global", immediates=("GroupSize",), stack_outputs=(wtypes.uint64_wtype,)
            ),
        ),
        "algopy.op.Global.logic_sig_version": (
            FunctionOpMapping(
                op_code="global",
                immediates=("LogicSigVersion",),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.Global.round": (
            FunctionOpMapping(
                op_code="global", immediates=("Round",), stack_outputs=(wtypes.uint64_wtype,)
            ),
        ),
        "algopy.op.Global.latest_timestamp": (
            FunctionOpMapping(
                op_code="global",
                immediates=("LatestTimestamp",),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.Global.current_application_id": (
            FunctionOpMapping(
                op_code="global",
                immediates=("CurrentApplicationID",),
                stack_outputs=(wtypes.application_wtype,),
            ),
        ),
        "algopy.op.Global.creator_address": (
            FunctionOpMapping(
                op_code="global",
                immediates=("CreatorAddress",),
                stack_outputs=(wtypes.account_wtype,),
            ),
        ),
        "algopy.op.Global.current_application_address": (
            FunctionOpMapping(
                op_code="global",
                immediates=("CurrentApplicationAddress",),
                stack_outputs=(wtypes.account_wtype,),
            ),
        ),
        "algopy.op.Global.group_id": (
            FunctionOpMapping(
                op_code="global", immediates=("GroupID",), stack_outputs=(wtypes.bytes_wtype,)
            ),
        ),
        "algopy.op.Global.opcode_budget": (
            FunctionOpMapping(
                op_code="global",
                immediates=("OpcodeBudget",),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.Global.caller_application_id": (
            FunctionOpMapping(
                op_code="global",
                immediates=("CallerApplicationID",),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.Global.caller_application_address": (
            FunctionOpMapping(
                op_code="global",
                immediates=("CallerApplicationAddress",),
                stack_outputs=(wtypes.account_wtype,),
            ),
        ),
        "algopy.op.Global.asset_create_min_balance": (
            FunctionOpMapping(
                op_code="global",
                immediates=("AssetCreateMinBalance",),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.Global.asset_opt_in_min_balance": (
            FunctionOpMapping(
                op_code="global",
                immediates=("AssetOptInMinBalance",),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.Global.genesis_hash": (
            FunctionOpMapping(
                op_code="global", immediates=("GenesisHash",), stack_outputs=(wtypes.bytes_wtype,)
            ),
        ),
        "algopy.op.ITxn.sender": (
            FunctionOpMapping(
                op_code="itxn", immediates=("Sender",), stack_outputs=(wtypes.account_wtype,)
            ),
        ),
        "algopy.op.ITxn.fee": (
            FunctionOpMapping(
                op_code="itxn", immediates=("Fee",), stack_outputs=(wtypes.uint64_wtype,)
            ),
        ),
        "algopy.op.ITxn.first_valid": (
            FunctionOpMapping(
                op_code="itxn", immediates=("FirstValid",), stack_outputs=(wtypes.uint64_wtype,)
            ),
        ),
        "algopy.op.ITxn.first_valid_time": (
            FunctionOpMapping(
                op_code="itxn",
                immediates=("FirstValidTime",),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.ITxn.last_valid": (
            FunctionOpMapping(
                op_code="itxn", immediates=("LastValid",), stack_outputs=(wtypes.uint64_wtype,)
            ),
        ),
        "algopy.op.ITxn.note": (
            FunctionOpMapping(
                op_code="itxn", immediates=("Note",), stack_outputs=(wtypes.bytes_wtype,)
            ),
        ),
        "algopy.op.ITxn.lease": (
            FunctionOpMapping(
                op_code="itxn", immediates=("Lease",), stack_outputs=(wtypes.bytes_wtype,)
            ),
        ),
        "algopy.op.ITxn.receiver": (
            FunctionOpMapping(
                op_code="itxn", immediates=("Receiver",), stack_outputs=(wtypes.account_wtype,)
            ),
        ),
        "algopy.op.ITxn.amount": (
            FunctionOpMapping(
                op_code="itxn", immediates=("Amount",), stack_outputs=(wtypes.uint64_wtype,)
            ),
        ),
        "algopy.op.ITxn.close_remainder_to": (
            FunctionOpMapping(
                op_code="itxn",
                immediates=("CloseRemainderTo",),
                stack_outputs=(wtypes.account_wtype,),
            ),
        ),
        "algopy.op.ITxn.vote_pk": (
            FunctionOpMapping(
                op_code="itxn", immediates=("VotePK",), stack_outputs=(wtypes.bytes_wtype,)
            ),
        ),
        "algopy.op.ITxn.selection_pk": (
            FunctionOpMapping(
                op_code="itxn", immediates=("SelectionPK",), stack_outputs=(wtypes.bytes_wtype,)
            ),
        ),
        "algopy.op.ITxn.vote_first": (
            FunctionOpMapping(
                op_code="itxn", immediates=("VoteFirst",), stack_outputs=(wtypes.uint64_wtype,)
            ),
        ),
        "algopy.op.ITxn.vote_last": (
            FunctionOpMapping(
                op_code="itxn", immediates=("VoteLast",), stack_outputs=(wtypes.uint64_wtype,)
            ),
        ),
        "algopy.op.ITxn.vote_key_dilution": (
            FunctionOpMapping(
                op_code="itxn",
                immediates=("VoteKeyDilution",),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.ITxn.type": (
            FunctionOpMapping(
                op_code="itxn", immediates=("Type",), stack_outputs=(wtypes.bytes_wtype,)
            ),
        ),
        "algopy.op.ITxn.type_enum": (
            FunctionOpMapping(
                op_code="itxn", immediates=("TypeEnum",), stack_outputs=(wtypes.uint64_wtype,)
            ),
        ),
        "algopy.op.ITxn.xfer_asset": (
            FunctionOpMapping(
                op_code="itxn", immediates=("XferAsset",), stack_outputs=(wtypes.asset_wtype,)
            ),
        ),
        "algopy.op.ITxn.asset_amount": (
            FunctionOpMapping(
                op_code="itxn", immediates=("AssetAmount",), stack_outputs=(wtypes.uint64_wtype,)
            ),
        ),
        "algopy.op.ITxn.asset_sender": (
            FunctionOpMapping(
                op_code="itxn", immediates=("AssetSender",), stack_outputs=(wtypes.account_wtype,)
            ),
        ),
        "algopy.op.ITxn.asset_receiver": (
            FunctionOpMapping(
                op_code="itxn",
                immediates=("AssetReceiver",),
                stack_outputs=(wtypes.account_wtype,),
            ),
        ),
        "algopy.op.ITxn.asset_close_to": (
            FunctionOpMapping(
                op_code="itxn", immediates=("AssetCloseTo",), stack_outputs=(wtypes.account_wtype,)
            ),
        ),
        "algopy.op.ITxn.group_index": (
            FunctionOpMapping(
                op_code="itxn", immediates=("GroupIndex",), stack_outputs=(wtypes.uint64_wtype,)
            ),
        ),
        "algopy.op.ITxn.tx_id": (
            FunctionOpMapping(
                op_code="itxn", immediates=("TxID",), stack_outputs=(wtypes.bytes_wtype,)
            ),
        ),
        "algopy.op.ITxn.application_id": (
            FunctionOpMapping(
                op_code="itxn",
                immediates=("ApplicationID",),
                stack_outputs=(wtypes.application_wtype,),
            ),
        ),
        "algopy.op.ITxn.on_completion": (
            FunctionOpMapping(
                op_code="itxn", immediates=("OnCompletion",), stack_outputs=(wtypes.uint64_wtype,)
            ),
        ),
        "algopy.op.ITxn.application_args": (
            FunctionOpMapping(
                op_code="itxnas",
                immediates=("ApplicationArgs",),
                stack_inputs={"a": (wtypes.uint64_wtype,)},
                stack_outputs=(wtypes.bytes_wtype,),
            ),
            FunctionOpMapping(
                op_code="itxna",
                immediates=("ApplicationArgs", ImmediateArgMapping("a", int)),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.ITxn.num_app_args": (
            FunctionOpMapping(
                op_code="itxn", immediates=("NumAppArgs",), stack_outputs=(wtypes.uint64_wtype,)
            ),
        ),
        "algopy.op.ITxn.accounts": (
            FunctionOpMapping(
                op_code="itxnas",
                immediates=("Accounts",),
                stack_inputs={"a": (wtypes.uint64_wtype,)},
                stack_outputs=(wtypes.account_wtype,),
            ),
            FunctionOpMapping(
                op_code="itxna",
                immediates=("Accounts", ImmediateArgMapping("a", int)),
                stack_outputs=(wtypes.account_wtype,),
            ),
        ),
        "algopy.op.ITxn.num_accounts": (
            FunctionOpMapping(
                op_code="itxn", immediates=("NumAccounts",), stack_outputs=(wtypes.uint64_wtype,)
            ),
        ),
        "algopy.op.ITxn.approval_program": (
            FunctionOpMapping(
                op_code="itxn",
                immediates=("ApprovalProgram",),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.ITxn.clear_state_program": (
            FunctionOpMapping(
                op_code="itxn",
                immediates=("ClearStateProgram",),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.ITxn.rekey_to": (
            FunctionOpMapping(
                op_code="itxn", immediates=("RekeyTo",), stack_outputs=(wtypes.account_wtype,)
            ),
        ),
        "algopy.op.ITxn.config_asset": (
            FunctionOpMapping(
                op_code="itxn", immediates=("ConfigAsset",), stack_outputs=(wtypes.asset_wtype,)
            ),
        ),
        "algopy.op.ITxn.config_asset_total": (
            FunctionOpMapping(
                op_code="itxn",
                immediates=("ConfigAssetTotal",),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.ITxn.config_asset_decimals": (
            FunctionOpMapping(
                op_code="itxn",
                immediates=("ConfigAssetDecimals",),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.ITxn.config_asset_default_frozen": (
            FunctionOpMapping(
                op_code="itxn",
                immediates=("ConfigAssetDefaultFrozen",),
                stack_outputs=(wtypes.bool_wtype,),
            ),
        ),
        "algopy.op.ITxn.config_asset_unit_name": (
            FunctionOpMapping(
                op_code="itxn",
                immediates=("ConfigAssetUnitName",),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.ITxn.config_asset_name": (
            FunctionOpMapping(
                op_code="itxn",
                immediates=("ConfigAssetName",),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.ITxn.config_asset_url": (
            FunctionOpMapping(
                op_code="itxn", immediates=("ConfigAssetURL",), stack_outputs=(wtypes.bytes_wtype,)
            ),
        ),
        "algopy.op.ITxn.config_asset_metadata_hash": (
            FunctionOpMapping(
                op_code="itxn",
                immediates=("ConfigAssetMetadataHash",),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.ITxn.config_asset_manager": (
            FunctionOpMapping(
                op_code="itxn",
                immediates=("ConfigAssetManager",),
                stack_outputs=(wtypes.account_wtype,),
            ),
        ),
        "algopy.op.ITxn.config_asset_reserve": (
            FunctionOpMapping(
                op_code="itxn",
                immediates=("ConfigAssetReserve",),
                stack_outputs=(wtypes.account_wtype,),
            ),
        ),
        "algopy.op.ITxn.config_asset_freeze": (
            FunctionOpMapping(
                op_code="itxn",
                immediates=("ConfigAssetFreeze",),
                stack_outputs=(wtypes.account_wtype,),
            ),
        ),
        "algopy.op.ITxn.config_asset_clawback": (
            FunctionOpMapping(
                op_code="itxn",
                immediates=("ConfigAssetClawback",),
                stack_outputs=(wtypes.account_wtype,),
            ),
        ),
        "algopy.op.ITxn.freeze_asset": (
            FunctionOpMapping(
                op_code="itxn", immediates=("FreezeAsset",), stack_outputs=(wtypes.asset_wtype,)
            ),
        ),
        "algopy.op.ITxn.freeze_asset_account": (
            FunctionOpMapping(
                op_code="itxn",
                immediates=("FreezeAssetAccount",),
                stack_outputs=(wtypes.account_wtype,),
            ),
        ),
        "algopy.op.ITxn.freeze_asset_frozen": (
            FunctionOpMapping(
                op_code="itxn",
                immediates=("FreezeAssetFrozen",),
                stack_outputs=(wtypes.bool_wtype,),
            ),
        ),
        "algopy.op.ITxn.assets": (
            FunctionOpMapping(
                op_code="itxnas",
                immediates=("Assets",),
                stack_inputs={"a": (wtypes.uint64_wtype,)},
                stack_outputs=(wtypes.asset_wtype,),
            ),
            FunctionOpMapping(
                op_code="itxna",
                immediates=("Assets", ImmediateArgMapping("a", int)),
                stack_outputs=(wtypes.asset_wtype,),
            ),
        ),
        "algopy.op.ITxn.num_assets": (
            FunctionOpMapping(
                op_code="itxn", immediates=("NumAssets",), stack_outputs=(wtypes.uint64_wtype,)
            ),
        ),
        "algopy.op.ITxn.applications": (
            FunctionOpMapping(
                op_code="itxnas",
                immediates=("Applications",),
                stack_inputs={"a": (wtypes.uint64_wtype,)},
                stack_outputs=(wtypes.application_wtype,),
            ),
            FunctionOpMapping(
                op_code="itxna",
                immediates=("Applications", ImmediateArgMapping("a", int)),
                stack_outputs=(wtypes.application_wtype,),
            ),
        ),
        "algopy.op.ITxn.num_applications": (
            FunctionOpMapping(
                op_code="itxn",
                immediates=("NumApplications",),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.ITxn.global_num_uint": (
            FunctionOpMapping(
                op_code="itxn", immediates=("GlobalNumUint",), stack_outputs=(wtypes.uint64_wtype,)
            ),
        ),
        "algopy.op.ITxn.global_num_byte_slice": (
            FunctionOpMapping(
                op_code="itxn",
                immediates=("GlobalNumByteSlice",),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.ITxn.local_num_uint": (
            FunctionOpMapping(
                op_code="itxn", immediates=("LocalNumUint",), stack_outputs=(wtypes.uint64_wtype,)
            ),
        ),
        "algopy.op.ITxn.local_num_byte_slice": (
            FunctionOpMapping(
                op_code="itxn",
                immediates=("LocalNumByteSlice",),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.ITxn.extra_program_pages": (
            FunctionOpMapping(
                op_code="itxn",
                immediates=("ExtraProgramPages",),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.ITxn.nonparticipation": (
            FunctionOpMapping(
                op_code="itxn",
                immediates=("Nonparticipation",),
                stack_outputs=(wtypes.bool_wtype,),
            ),
        ),
        "algopy.op.ITxn.logs": (
            FunctionOpMapping(
                op_code="itxnas",
                immediates=("Logs",),
                stack_inputs={"a": (wtypes.uint64_wtype,)},
                stack_outputs=(wtypes.bytes_wtype,),
            ),
            FunctionOpMapping(
                op_code="itxna",
                immediates=("Logs", ImmediateArgMapping("a", int)),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.ITxn.num_logs": (
            FunctionOpMapping(
                op_code="itxn", immediates=("NumLogs",), stack_outputs=(wtypes.uint64_wtype,)
            ),
        ),
        "algopy.op.ITxn.created_asset_id": (
            FunctionOpMapping(
                op_code="itxn", immediates=("CreatedAssetID",), stack_outputs=(wtypes.asset_wtype,)
            ),
        ),
        "algopy.op.ITxn.created_application_id": (
            FunctionOpMapping(
                op_code="itxn",
                immediates=("CreatedApplicationID",),
                stack_outputs=(wtypes.application_wtype,),
            ),
        ),
        "algopy.op.ITxn.last_log": (
            FunctionOpMapping(
                op_code="itxn", immediates=("LastLog",), stack_outputs=(wtypes.bytes_wtype,)
            ),
        ),
        "algopy.op.ITxn.state_proof_pk": (
            FunctionOpMapping(
                op_code="itxn", immediates=("StateProofPK",), stack_outputs=(wtypes.bytes_wtype,)
            ),
        ),
        "algopy.op.ITxn.approval_program_pages": (
            FunctionOpMapping(
                op_code="itxnas",
                immediates=("ApprovalProgramPages",),
                stack_inputs={"a": (wtypes.uint64_wtype,)},
                stack_outputs=(wtypes.bytes_wtype,),
            ),
            FunctionOpMapping(
                op_code="itxna",
                immediates=("ApprovalProgramPages", ImmediateArgMapping("a", int)),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.ITxn.num_approval_program_pages": (
            FunctionOpMapping(
                op_code="itxn",
                immediates=("NumApprovalProgramPages",),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.ITxn.clear_state_program_pages": (
            FunctionOpMapping(
                op_code="itxnas",
                immediates=("ClearStateProgramPages",),
                stack_inputs={"a": (wtypes.uint64_wtype,)},
                stack_outputs=(wtypes.bytes_wtype,),
            ),
            FunctionOpMapping(
                op_code="itxna",
                immediates=("ClearStateProgramPages", ImmediateArgMapping("a", int)),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.ITxn.num_clear_state_program_pages": (
            FunctionOpMapping(
                op_code="itxn",
                immediates=("NumClearStateProgramPages",),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.ITxnCreate.begin": (FunctionOpMapping(op_code="itxn_begin"),),
        "algopy.op.ITxnCreate.next": (FunctionOpMapping(op_code="itxn_next"),),
        "algopy.op.ITxnCreate.submit": (FunctionOpMapping(op_code="itxn_submit"),),
        "algopy.op.ITxnCreate.set_sender": (
            FunctionOpMapping(
                op_code="itxn_field",
                immediates=("Sender",),
                stack_inputs={"a": (wtypes.account_wtype,)},
            ),
        ),
        "algopy.op.ITxnCreate.set_fee": (
            FunctionOpMapping(
                op_code="itxn_field",
                immediates=("Fee",),
                stack_inputs={"a": (wtypes.uint64_wtype,)},
            ),
        ),
        "algopy.op.ITxnCreate.set_note": (
            FunctionOpMapping(
                op_code="itxn_field",
                immediates=("Note",),
                stack_inputs={"a": (wtypes.bytes_wtype,)},
            ),
        ),
        "algopy.op.ITxnCreate.set_receiver": (
            FunctionOpMapping(
                op_code="itxn_field",
                immediates=("Receiver",),
                stack_inputs={"a": (wtypes.account_wtype,)},
            ),
        ),
        "algopy.op.ITxnCreate.set_amount": (
            FunctionOpMapping(
                op_code="itxn_field",
                immediates=("Amount",),
                stack_inputs={"a": (wtypes.uint64_wtype,)},
            ),
        ),
        "algopy.op.ITxnCreate.set_close_remainder_to": (
            FunctionOpMapping(
                op_code="itxn_field",
                immediates=("CloseRemainderTo",),
                stack_inputs={"a": (wtypes.account_wtype,)},
            ),
        ),
        "algopy.op.ITxnCreate.set_vote_pk": (
            FunctionOpMapping(
                op_code="itxn_field",
                immediates=("VotePK",),
                stack_inputs={"a": (wtypes.bytes_wtype,)},
            ),
        ),
        "algopy.op.ITxnCreate.set_selection_pk": (
            FunctionOpMapping(
                op_code="itxn_field",
                immediates=("SelectionPK",),
                stack_inputs={"a": (wtypes.bytes_wtype,)},
            ),
        ),
        "algopy.op.ITxnCreate.set_vote_first": (
            FunctionOpMapping(
                op_code="itxn_field",
                immediates=("VoteFirst",),
                stack_inputs={"a": (wtypes.uint64_wtype,)},
            ),
        ),
        "algopy.op.ITxnCreate.set_vote_last": (
            FunctionOpMapping(
                op_code="itxn_field",
                immediates=("VoteLast",),
                stack_inputs={"a": (wtypes.uint64_wtype,)},
            ),
        ),
        "algopy.op.ITxnCreate.set_vote_key_dilution": (
            FunctionOpMapping(
                op_code="itxn_field",
                immediates=("VoteKeyDilution",),
                stack_inputs={"a": (wtypes.uint64_wtype,)},
            ),
        ),
        "algopy.op.ITxnCreate.set_type": (
            FunctionOpMapping(
                op_code="itxn_field",
                immediates=("Type",),
                stack_inputs={"a": (wtypes.bytes_wtype,)},
            ),
        ),
        "algopy.op.ITxnCreate.set_type_enum": (
            FunctionOpMapping(
                op_code="itxn_field",
                immediates=("TypeEnum",),
                stack_inputs={"a": (wtypes.uint64_wtype,)},
            ),
        ),
        "algopy.op.ITxnCreate.set_xfer_asset": (
            FunctionOpMapping(
                op_code="itxn_field",
                immediates=("XferAsset",),
                stack_inputs={"a": (wtypes.asset_wtype, wtypes.uint64_wtype)},
            ),
        ),
        "algopy.op.ITxnCreate.set_asset_amount": (
            FunctionOpMapping(
                op_code="itxn_field",
                immediates=("AssetAmount",),
                stack_inputs={"a": (wtypes.uint64_wtype,)},
            ),
        ),
        "algopy.op.ITxnCreate.set_asset_sender": (
            FunctionOpMapping(
                op_code="itxn_field",
                immediates=("AssetSender",),
                stack_inputs={"a": (wtypes.account_wtype,)},
            ),
        ),
        "algopy.op.ITxnCreate.set_asset_receiver": (
            FunctionOpMapping(
                op_code="itxn_field",
                immediates=("AssetReceiver",),
                stack_inputs={"a": (wtypes.account_wtype,)},
            ),
        ),
        "algopy.op.ITxnCreate.set_asset_close_to": (
            FunctionOpMapping(
                op_code="itxn_field",
                immediates=("AssetCloseTo",),
                stack_inputs={"a": (wtypes.account_wtype,)},
            ),
        ),
        "algopy.op.ITxnCreate.set_application_id": (
            FunctionOpMapping(
                op_code="itxn_field",
                immediates=("ApplicationID",),
                stack_inputs={"a": (wtypes.application_wtype, wtypes.uint64_wtype)},
            ),
        ),
        "algopy.op.ITxnCreate.set_on_completion": (
            FunctionOpMapping(
                op_code="itxn_field",
                immediates=("OnCompletion",),
                stack_inputs={"a": (wtypes.uint64_wtype,)},
            ),
        ),
        "algopy.op.ITxnCreate.set_application_args": (
            FunctionOpMapping(
                op_code="itxn_field",
                immediates=("ApplicationArgs",),
                stack_inputs={"a": (wtypes.bytes_wtype,)},
            ),
        ),
        "algopy.op.ITxnCreate.set_accounts": (
            FunctionOpMapping(
                op_code="itxn_field",
                immediates=("Accounts",),
                stack_inputs={"a": (wtypes.account_wtype,)},
            ),
        ),
        "algopy.op.ITxnCreate.set_approval_program": (
            FunctionOpMapping(
                op_code="itxn_field",
                immediates=("ApprovalProgram",),
                stack_inputs={"a": (wtypes.bytes_wtype,)},
            ),
        ),
        "algopy.op.ITxnCreate.set_clear_state_program": (
            FunctionOpMapping(
                op_code="itxn_field",
                immediates=("ClearStateProgram",),
                stack_inputs={"a": (wtypes.bytes_wtype,)},
            ),
        ),
        "algopy.op.ITxnCreate.set_rekey_to": (
            FunctionOpMapping(
                op_code="itxn_field",
                immediates=("RekeyTo",),
                stack_inputs={"a": (wtypes.account_wtype,)},
            ),
        ),
        "algopy.op.ITxnCreate.set_config_asset": (
            FunctionOpMapping(
                op_code="itxn_field",
                immediates=("ConfigAsset",),
                stack_inputs={"a": (wtypes.asset_wtype, wtypes.uint64_wtype)},
            ),
        ),
        "algopy.op.ITxnCreate.set_config_asset_total": (
            FunctionOpMapping(
                op_code="itxn_field",
                immediates=("ConfigAssetTotal",),
                stack_inputs={"a": (wtypes.uint64_wtype,)},
            ),
        ),
        "algopy.op.ITxnCreate.set_config_asset_decimals": (
            FunctionOpMapping(
                op_code="itxn_field",
                immediates=("ConfigAssetDecimals",),
                stack_inputs={"a": (wtypes.uint64_wtype,)},
            ),
        ),
        "algopy.op.ITxnCreate.set_config_asset_default_frozen": (
            FunctionOpMapping(
                op_code="itxn_field",
                immediates=("ConfigAssetDefaultFrozen",),
                stack_inputs={"a": (wtypes.bool_wtype, wtypes.uint64_wtype)},
            ),
        ),
        "algopy.op.ITxnCreate.set_config_asset_unit_name": (
            FunctionOpMapping(
                op_code="itxn_field",
                immediates=("ConfigAssetUnitName",),
                stack_inputs={"a": (wtypes.bytes_wtype,)},
            ),
        ),
        "algopy.op.ITxnCreate.set_config_asset_name": (
            FunctionOpMapping(
                op_code="itxn_field",
                immediates=("ConfigAssetName",),
                stack_inputs={"a": (wtypes.bytes_wtype,)},
            ),
        ),
        "algopy.op.ITxnCreate.set_config_asset_url": (
            FunctionOpMapping(
                op_code="itxn_field",
                immediates=("ConfigAssetURL",),
                stack_inputs={"a": (wtypes.bytes_wtype,)},
            ),
        ),
        "algopy.op.ITxnCreate.set_config_asset_metadata_hash": (
            FunctionOpMapping(
                op_code="itxn_field",
                immediates=("ConfigAssetMetadataHash",),
                stack_inputs={"a": (wtypes.bytes_wtype,)},
            ),
        ),
        "algopy.op.ITxnCreate.set_config_asset_manager": (
            FunctionOpMapping(
                op_code="itxn_field",
                immediates=("ConfigAssetManager",),
                stack_inputs={"a": (wtypes.account_wtype,)},
            ),
        ),
        "algopy.op.ITxnCreate.set_config_asset_reserve": (
            FunctionOpMapping(
                op_code="itxn_field",
                immediates=("ConfigAssetReserve",),
                stack_inputs={"a": (wtypes.account_wtype,)},
            ),
        ),
        "algopy.op.ITxnCreate.set_config_asset_freeze": (
            FunctionOpMapping(
                op_code="itxn_field",
                immediates=("ConfigAssetFreeze",),
                stack_inputs={"a": (wtypes.account_wtype,)},
            ),
        ),
        "algopy.op.ITxnCreate.set_config_asset_clawback": (
            FunctionOpMapping(
                op_code="itxn_field",
                immediates=("ConfigAssetClawback",),
                stack_inputs={"a": (wtypes.account_wtype,)},
            ),
        ),
        "algopy.op.ITxnCreate.set_freeze_asset": (
            FunctionOpMapping(
                op_code="itxn_field",
                immediates=("FreezeAsset",),
                stack_inputs={"a": (wtypes.asset_wtype, wtypes.uint64_wtype)},
            ),
        ),
        "algopy.op.ITxnCreate.set_freeze_asset_account": (
            FunctionOpMapping(
                op_code="itxn_field",
                immediates=("FreezeAssetAccount",),
                stack_inputs={"a": (wtypes.account_wtype,)},
            ),
        ),
        "algopy.op.ITxnCreate.set_freeze_asset_frozen": (
            FunctionOpMapping(
                op_code="itxn_field",
                immediates=("FreezeAssetFrozen",),
                stack_inputs={"a": (wtypes.bool_wtype, wtypes.uint64_wtype)},
            ),
        ),
        "algopy.op.ITxnCreate.set_assets": (
            FunctionOpMapping(
                op_code="itxn_field",
                immediates=("Assets",),
                stack_inputs={"a": (wtypes.uint64_wtype,)},
            ),
        ),
        "algopy.op.ITxnCreate.set_applications": (
            FunctionOpMapping(
                op_code="itxn_field",
                immediates=("Applications",),
                stack_inputs={"a": (wtypes.uint64_wtype,)},
            ),
        ),
        "algopy.op.ITxnCreate.set_global_num_uint": (
            FunctionOpMapping(
                op_code="itxn_field",
                immediates=("GlobalNumUint",),
                stack_inputs={"a": (wtypes.uint64_wtype,)},
            ),
        ),
        "algopy.op.ITxnCreate.set_global_num_byte_slice": (
            FunctionOpMapping(
                op_code="itxn_field",
                immediates=("GlobalNumByteSlice",),
                stack_inputs={"a": (wtypes.uint64_wtype,)},
            ),
        ),
        "algopy.op.ITxnCreate.set_local_num_uint": (
            FunctionOpMapping(
                op_code="itxn_field",
                immediates=("LocalNumUint",),
                stack_inputs={"a": (wtypes.uint64_wtype,)},
            ),
        ),
        "algopy.op.ITxnCreate.set_local_num_byte_slice": (
            FunctionOpMapping(
                op_code="itxn_field",
                immediates=("LocalNumByteSlice",),
                stack_inputs={"a": (wtypes.uint64_wtype,)},
            ),
        ),
        "algopy.op.ITxnCreate.set_extra_program_pages": (
            FunctionOpMapping(
                op_code="itxn_field",
                immediates=("ExtraProgramPages",),
                stack_inputs={"a": (wtypes.uint64_wtype,)},
            ),
        ),
        "algopy.op.ITxnCreate.set_nonparticipation": (
            FunctionOpMapping(
                op_code="itxn_field",
                immediates=("Nonparticipation",),
                stack_inputs={"a": (wtypes.bool_wtype, wtypes.uint64_wtype)},
            ),
        ),
        "algopy.op.ITxnCreate.set_state_proof_pk": (
            FunctionOpMapping(
                op_code="itxn_field",
                immediates=("StateProofPK",),
                stack_inputs={"a": (wtypes.bytes_wtype,)},
            ),
        ),
        "algopy.op.ITxnCreate.set_approval_program_pages": (
            FunctionOpMapping(
                op_code="itxn_field",
                immediates=("ApprovalProgramPages",),
                stack_inputs={"a": (wtypes.bytes_wtype,)},
            ),
        ),
        "algopy.op.ITxnCreate.set_clear_state_program_pages": (
            FunctionOpMapping(
                op_code="itxn_field",
                immediates=("ClearStateProgramPages",),
                stack_inputs={"a": (wtypes.bytes_wtype,)},
            ),
        ),
        "algopy.op.JsonRef.json_string": (
            FunctionOpMapping(
                op_code="json_ref",
                immediates=("JSONString",),
                stack_inputs={"a": (wtypes.bytes_wtype,), "b": (wtypes.bytes_wtype,)},
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.JsonRef.json_uint64": (
            FunctionOpMapping(
                op_code="json_ref",
                immediates=("JSONUint64",),
                stack_inputs={"a": (wtypes.bytes_wtype,), "b": (wtypes.bytes_wtype,)},
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.JsonRef.json_object": (
            FunctionOpMapping(
                op_code="json_ref",
                immediates=("JSONObject",),
                stack_inputs={"a": (wtypes.bytes_wtype,), "b": (wtypes.bytes_wtype,)},
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.Scratch.load_bytes": (
            FunctionOpMapping(
                op_code="loads",
                stack_inputs={"a": (wtypes.uint64_wtype,)},
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.Scratch.load_uint64": (
            FunctionOpMapping(
                op_code="loads",
                stack_inputs={"a": (wtypes.uint64_wtype,)},
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.Scratch.store": (
            FunctionOpMapping(
                op_code="stores",
                stack_inputs={
                    "a": (wtypes.uint64_wtype,),
                    "b": (wtypes.bytes_wtype, wtypes.uint64_wtype),
                },
            ),
        ),
        "algopy.op.Txn.sender": (
            FunctionOpMapping(
                op_code="txn", immediates=("Sender",), stack_outputs=(wtypes.account_wtype,)
            ),
        ),
        "algopy.op.Txn.fee": (
            FunctionOpMapping(
                op_code="txn", immediates=("Fee",), stack_outputs=(wtypes.uint64_wtype,)
            ),
        ),
        "algopy.op.Txn.first_valid": (
            FunctionOpMapping(
                op_code="txn", immediates=("FirstValid",), stack_outputs=(wtypes.uint64_wtype,)
            ),
        ),
        "algopy.op.Txn.first_valid_time": (
            FunctionOpMapping(
                op_code="txn", immediates=("FirstValidTime",), stack_outputs=(wtypes.uint64_wtype,)
            ),
        ),
        "algopy.op.Txn.last_valid": (
            FunctionOpMapping(
                op_code="txn", immediates=("LastValid",), stack_outputs=(wtypes.uint64_wtype,)
            ),
        ),
        "algopy.op.Txn.note": (
            FunctionOpMapping(
                op_code="txn", immediates=("Note",), stack_outputs=(wtypes.bytes_wtype,)
            ),
        ),
        "algopy.op.Txn.lease": (
            FunctionOpMapping(
                op_code="txn", immediates=("Lease",), stack_outputs=(wtypes.bytes_wtype,)
            ),
        ),
        "algopy.op.Txn.receiver": (
            FunctionOpMapping(
                op_code="txn", immediates=("Receiver",), stack_outputs=(wtypes.account_wtype,)
            ),
        ),
        "algopy.op.Txn.amount": (
            FunctionOpMapping(
                op_code="txn", immediates=("Amount",), stack_outputs=(wtypes.uint64_wtype,)
            ),
        ),
        "algopy.op.Txn.close_remainder_to": (
            FunctionOpMapping(
                op_code="txn",
                immediates=("CloseRemainderTo",),
                stack_outputs=(wtypes.account_wtype,),
            ),
        ),
        "algopy.op.Txn.vote_pk": (
            FunctionOpMapping(
                op_code="txn", immediates=("VotePK",), stack_outputs=(wtypes.bytes_wtype,)
            ),
        ),
        "algopy.op.Txn.selection_pk": (
            FunctionOpMapping(
                op_code="txn", immediates=("SelectionPK",), stack_outputs=(wtypes.bytes_wtype,)
            ),
        ),
        "algopy.op.Txn.vote_first": (
            FunctionOpMapping(
                op_code="txn", immediates=("VoteFirst",), stack_outputs=(wtypes.uint64_wtype,)
            ),
        ),
        "algopy.op.Txn.vote_last": (
            FunctionOpMapping(
                op_code="txn", immediates=("VoteLast",), stack_outputs=(wtypes.uint64_wtype,)
            ),
        ),
        "algopy.op.Txn.vote_key_dilution": (
            FunctionOpMapping(
                op_code="txn",
                immediates=("VoteKeyDilution",),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.Txn.type": (
            FunctionOpMapping(
                op_code="txn", immediates=("Type",), stack_outputs=(wtypes.bytes_wtype,)
            ),
        ),
        "algopy.op.Txn.type_enum": (
            FunctionOpMapping(
                op_code="txn", immediates=("TypeEnum",), stack_outputs=(wtypes.uint64_wtype,)
            ),
        ),
        "algopy.op.Txn.xfer_asset": (
            FunctionOpMapping(
                op_code="txn", immediates=("XferAsset",), stack_outputs=(wtypes.asset_wtype,)
            ),
        ),
        "algopy.op.Txn.asset_amount": (
            FunctionOpMapping(
                op_code="txn", immediates=("AssetAmount",), stack_outputs=(wtypes.uint64_wtype,)
            ),
        ),
        "algopy.op.Txn.asset_sender": (
            FunctionOpMapping(
                op_code="txn", immediates=("AssetSender",), stack_outputs=(wtypes.account_wtype,)
            ),
        ),
        "algopy.op.Txn.asset_receiver": (
            FunctionOpMapping(
                op_code="txn", immediates=("AssetReceiver",), stack_outputs=(wtypes.account_wtype,)
            ),
        ),
        "algopy.op.Txn.asset_close_to": (
            FunctionOpMapping(
                op_code="txn", immediates=("AssetCloseTo",), stack_outputs=(wtypes.account_wtype,)
            ),
        ),
        "algopy.op.Txn.group_index": (
            FunctionOpMapping(
                op_code="txn", immediates=("GroupIndex",), stack_outputs=(wtypes.uint64_wtype,)
            ),
        ),
        "algopy.op.Txn.tx_id": (
            FunctionOpMapping(
                op_code="txn", immediates=("TxID",), stack_outputs=(wtypes.bytes_wtype,)
            ),
        ),
        "algopy.op.Txn.application_id": (
            FunctionOpMapping(
                op_code="txn",
                immediates=("ApplicationID",),
                stack_outputs=(wtypes.application_wtype,),
            ),
        ),
        "algopy.op.Txn.on_completion": (
            FunctionOpMapping(
                op_code="txn", immediates=("OnCompletion",), stack_outputs=(wtypes.uint64_wtype,)
            ),
        ),
        "algopy.op.Txn.application_args": (
            FunctionOpMapping(
                op_code="txnas",
                immediates=("ApplicationArgs",),
                stack_inputs={"a": (wtypes.uint64_wtype,)},
                stack_outputs=(wtypes.bytes_wtype,),
            ),
            FunctionOpMapping(
                op_code="txna",
                immediates=("ApplicationArgs", ImmediateArgMapping("a", int)),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.Txn.num_app_args": (
            FunctionOpMapping(
                op_code="txn", immediates=("NumAppArgs",), stack_outputs=(wtypes.uint64_wtype,)
            ),
        ),
        "algopy.op.Txn.accounts": (
            FunctionOpMapping(
                op_code="txnas",
                immediates=("Accounts",),
                stack_inputs={"a": (wtypes.uint64_wtype,)},
                stack_outputs=(wtypes.account_wtype,),
            ),
            FunctionOpMapping(
                op_code="txna",
                immediates=("Accounts", ImmediateArgMapping("a", int)),
                stack_outputs=(wtypes.account_wtype,),
            ),
        ),
        "algopy.op.Txn.num_accounts": (
            FunctionOpMapping(
                op_code="txn", immediates=("NumAccounts",), stack_outputs=(wtypes.uint64_wtype,)
            ),
        ),
        "algopy.op.Txn.approval_program": (
            FunctionOpMapping(
                op_code="txn", immediates=("ApprovalProgram",), stack_outputs=(wtypes.bytes_wtype,)
            ),
        ),
        "algopy.op.Txn.clear_state_program": (
            FunctionOpMapping(
                op_code="txn",
                immediates=("ClearStateProgram",),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.Txn.rekey_to": (
            FunctionOpMapping(
                op_code="txn", immediates=("RekeyTo",), stack_outputs=(wtypes.account_wtype,)
            ),
        ),
        "algopy.op.Txn.config_asset": (
            FunctionOpMapping(
                op_code="txn", immediates=("ConfigAsset",), stack_outputs=(wtypes.asset_wtype,)
            ),
        ),
        "algopy.op.Txn.config_asset_total": (
            FunctionOpMapping(
                op_code="txn",
                immediates=("ConfigAssetTotal",),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.Txn.config_asset_decimals": (
            FunctionOpMapping(
                op_code="txn",
                immediates=("ConfigAssetDecimals",),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.Txn.config_asset_default_frozen": (
            FunctionOpMapping(
                op_code="txn",
                immediates=("ConfigAssetDefaultFrozen",),
                stack_outputs=(wtypes.bool_wtype,),
            ),
        ),
        "algopy.op.Txn.config_asset_unit_name": (
            FunctionOpMapping(
                op_code="txn",
                immediates=("ConfigAssetUnitName",),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.Txn.config_asset_name": (
            FunctionOpMapping(
                op_code="txn", immediates=("ConfigAssetName",), stack_outputs=(wtypes.bytes_wtype,)
            ),
        ),
        "algopy.op.Txn.config_asset_url": (
            FunctionOpMapping(
                op_code="txn", immediates=("ConfigAssetURL",), stack_outputs=(wtypes.bytes_wtype,)
            ),
        ),
        "algopy.op.Txn.config_asset_metadata_hash": (
            FunctionOpMapping(
                op_code="txn",
                immediates=("ConfigAssetMetadataHash",),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.Txn.config_asset_manager": (
            FunctionOpMapping(
                op_code="txn",
                immediates=("ConfigAssetManager",),
                stack_outputs=(wtypes.account_wtype,),
            ),
        ),
        "algopy.op.Txn.config_asset_reserve": (
            FunctionOpMapping(
                op_code="txn",
                immediates=("ConfigAssetReserve",),
                stack_outputs=(wtypes.account_wtype,),
            ),
        ),
        "algopy.op.Txn.config_asset_freeze": (
            FunctionOpMapping(
                op_code="txn",
                immediates=("ConfigAssetFreeze",),
                stack_outputs=(wtypes.account_wtype,),
            ),
        ),
        "algopy.op.Txn.config_asset_clawback": (
            FunctionOpMapping(
                op_code="txn",
                immediates=("ConfigAssetClawback",),
                stack_outputs=(wtypes.account_wtype,),
            ),
        ),
        "algopy.op.Txn.freeze_asset": (
            FunctionOpMapping(
                op_code="txn", immediates=("FreezeAsset",), stack_outputs=(wtypes.asset_wtype,)
            ),
        ),
        "algopy.op.Txn.freeze_asset_account": (
            FunctionOpMapping(
                op_code="txn",
                immediates=("FreezeAssetAccount",),
                stack_outputs=(wtypes.account_wtype,),
            ),
        ),
        "algopy.op.Txn.freeze_asset_frozen": (
            FunctionOpMapping(
                op_code="txn",
                immediates=("FreezeAssetFrozen",),
                stack_outputs=(wtypes.bool_wtype,),
            ),
        ),
        "algopy.op.Txn.assets": (
            FunctionOpMapping(
                op_code="txnas",
                immediates=("Assets",),
                stack_inputs={"a": (wtypes.uint64_wtype,)},
                stack_outputs=(wtypes.asset_wtype,),
            ),
            FunctionOpMapping(
                op_code="txna",
                immediates=("Assets", ImmediateArgMapping("a", int)),
                stack_outputs=(wtypes.asset_wtype,),
            ),
        ),
        "algopy.op.Txn.num_assets": (
            FunctionOpMapping(
                op_code="txn", immediates=("NumAssets",), stack_outputs=(wtypes.uint64_wtype,)
            ),
        ),
        "algopy.op.Txn.applications": (
            FunctionOpMapping(
                op_code="txnas",
                immediates=("Applications",),
                stack_inputs={"a": (wtypes.uint64_wtype,)},
                stack_outputs=(wtypes.application_wtype,),
            ),
            FunctionOpMapping(
                op_code="txna",
                immediates=("Applications", ImmediateArgMapping("a", int)),
                stack_outputs=(wtypes.application_wtype,),
            ),
        ),
        "algopy.op.Txn.num_applications": (
            FunctionOpMapping(
                op_code="txn",
                immediates=("NumApplications",),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.Txn.global_num_uint": (
            FunctionOpMapping(
                op_code="txn", immediates=("GlobalNumUint",), stack_outputs=(wtypes.uint64_wtype,)
            ),
        ),
        "algopy.op.Txn.global_num_byte_slice": (
            FunctionOpMapping(
                op_code="txn",
                immediates=("GlobalNumByteSlice",),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.Txn.local_num_uint": (
            FunctionOpMapping(
                op_code="txn", immediates=("LocalNumUint",), stack_outputs=(wtypes.uint64_wtype,)
            ),
        ),
        "algopy.op.Txn.local_num_byte_slice": (
            FunctionOpMapping(
                op_code="txn",
                immediates=("LocalNumByteSlice",),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.Txn.extra_program_pages": (
            FunctionOpMapping(
                op_code="txn",
                immediates=("ExtraProgramPages",),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.Txn.nonparticipation": (
            FunctionOpMapping(
                op_code="txn", immediates=("Nonparticipation",), stack_outputs=(wtypes.bool_wtype,)
            ),
        ),
        "algopy.op.Txn.logs": (
            FunctionOpMapping(
                op_code="txnas",
                immediates=("Logs",),
                stack_inputs={"a": (wtypes.uint64_wtype,)},
                stack_outputs=(wtypes.bytes_wtype,),
            ),
            FunctionOpMapping(
                op_code="txna",
                immediates=("Logs", ImmediateArgMapping("a", int)),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.Txn.num_logs": (
            FunctionOpMapping(
                op_code="txn", immediates=("NumLogs",), stack_outputs=(wtypes.uint64_wtype,)
            ),
        ),
        "algopy.op.Txn.created_asset_id": (
            FunctionOpMapping(
                op_code="txn", immediates=("CreatedAssetID",), stack_outputs=(wtypes.asset_wtype,)
            ),
        ),
        "algopy.op.Txn.created_application_id": (
            FunctionOpMapping(
                op_code="txn",
                immediates=("CreatedApplicationID",),
                stack_outputs=(wtypes.application_wtype,),
            ),
        ),
        "algopy.op.Txn.last_log": (
            FunctionOpMapping(
                op_code="txn", immediates=("LastLog",), stack_outputs=(wtypes.bytes_wtype,)
            ),
        ),
        "algopy.op.Txn.state_proof_pk": (
            FunctionOpMapping(
                op_code="txn", immediates=("StateProofPK",), stack_outputs=(wtypes.bytes_wtype,)
            ),
        ),
        "algopy.op.Txn.approval_program_pages": (
            FunctionOpMapping(
                op_code="txnas",
                immediates=("ApprovalProgramPages",),
                stack_inputs={"a": (wtypes.uint64_wtype,)},
                stack_outputs=(wtypes.bytes_wtype,),
            ),
            FunctionOpMapping(
                op_code="txna",
                immediates=("ApprovalProgramPages", ImmediateArgMapping("a", int)),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.Txn.num_approval_program_pages": (
            FunctionOpMapping(
                op_code="txn",
                immediates=("NumApprovalProgramPages",),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.Txn.clear_state_program_pages": (
            FunctionOpMapping(
                op_code="txnas",
                immediates=("ClearStateProgramPages",),
                stack_inputs={"a": (wtypes.uint64_wtype,)},
                stack_outputs=(wtypes.bytes_wtype,),
            ),
            FunctionOpMapping(
                op_code="txna",
                immediates=("ClearStateProgramPages", ImmediateArgMapping("a", int)),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.Txn.num_clear_state_program_pages": (
            FunctionOpMapping(
                op_code="txn",
                immediates=("NumClearStateProgramPages",),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
    }
)
