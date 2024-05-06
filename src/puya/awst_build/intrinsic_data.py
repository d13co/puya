import typing
from collections.abc import Mapping, Sequence

from immutabledict import immutabledict

from puya.awst import wtypes
from puya.awst_build.intrinsic_models import FunctionOpMapping, ImmediateArgMapping

ENUM_CLASSES: typing.Final = immutabledict[str, Mapping[str, str]](
    {
        "algopy.op.Base64": {
            "URLEncoding": "URLEncoding",
            "StdEncoding": "StdEncoding",
        },
        "algopy.op.ECDSA": {
            "Secp256k1": "Secp256k1",
            "Secp256r1": "Secp256r1",
        },
        "algopy.op.VrfVerify": {
            "VrfAlgorand": "VrfAlgorand",
        },
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
                "addw",
                stack_inputs=dict(a=(wtypes.uint64_wtype,), b=(wtypes.uint64_wtype,)),
                stack_outputs=(
                    wtypes.uint64_wtype,
                    wtypes.uint64_wtype,
                ),
            ),
        ),
        "algopy.op.app_opted_in": (
            FunctionOpMapping(
                "app_opted_in",
                stack_inputs=dict(
                    a=(wtypes.account_wtype, wtypes.uint64_wtype),
                    b=(wtypes.application_wtype, wtypes.uint64_wtype),
                ),
                stack_outputs=(wtypes.bool_wtype,),
            ),
        ),
        "algopy.op.arg": (
            FunctionOpMapping(
                "args",
                stack_inputs=dict(a=(wtypes.uint64_wtype,)),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
            FunctionOpMapping(
                "arg",
                immediates=(ImmediateArgMapping("a", int),),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.balance": (
            FunctionOpMapping(
                "balance",
                stack_inputs=dict(a=(wtypes.account_wtype, wtypes.uint64_wtype)),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.base64_decode": (
            FunctionOpMapping(
                "base64_decode",
                immediates=(ImmediateArgMapping("e", str),),
                stack_inputs=dict(a=(wtypes.bytes_wtype,)),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.bitlen": (
            FunctionOpMapping(
                "bitlen",
                stack_inputs=dict(a=(wtypes.bytes_wtype, wtypes.uint64_wtype)),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.bsqrt": (
            FunctionOpMapping(
                "bsqrt",
                stack_inputs=dict(a=(wtypes.biguint_wtype,)),
                stack_outputs=(wtypes.biguint_wtype,),
            ),
        ),
        "algopy.op.btoi": (
            FunctionOpMapping(
                "btoi",
                stack_inputs=dict(a=(wtypes.bytes_wtype,)),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.bzero": (
            FunctionOpMapping(
                "bzero",
                stack_inputs=dict(a=(wtypes.uint64_wtype,)),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.concat": (
            FunctionOpMapping(
                "concat",
                stack_inputs=dict(a=(wtypes.bytes_wtype,), b=(wtypes.bytes_wtype,)),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.divmodw": (
            FunctionOpMapping(
                "divmodw",
                stack_inputs=dict(
                    a=(wtypes.uint64_wtype,),
                    b=(wtypes.uint64_wtype,),
                    c=(wtypes.uint64_wtype,),
                    d=(wtypes.uint64_wtype,),
                ),
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
                "divw",
                stack_inputs=dict(
                    a=(wtypes.uint64_wtype,), b=(wtypes.uint64_wtype,), c=(wtypes.uint64_wtype,)
                ),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.ecdsa_pk_decompress": (
            FunctionOpMapping(
                "ecdsa_pk_decompress",
                immediates=(ImmediateArgMapping("v", str),),
                stack_inputs=dict(a=(wtypes.bytes_wtype,)),
                stack_outputs=(
                    wtypes.bytes_wtype,
                    wtypes.bytes_wtype,
                ),
            ),
        ),
        "algopy.op.ecdsa_pk_recover": (
            FunctionOpMapping(
                "ecdsa_pk_recover",
                immediates=(ImmediateArgMapping("v", str),),
                stack_inputs=dict(
                    a=(wtypes.bytes_wtype,),
                    b=(wtypes.uint64_wtype,),
                    c=(wtypes.bytes_wtype,),
                    d=(wtypes.bytes_wtype,),
                ),
                stack_outputs=(
                    wtypes.bytes_wtype,
                    wtypes.bytes_wtype,
                ),
            ),
        ),
        "algopy.op.ecdsa_verify": (
            FunctionOpMapping(
                "ecdsa_verify",
                immediates=(ImmediateArgMapping("v", str),),
                stack_inputs=dict(
                    a=(wtypes.bytes_wtype,),
                    b=(wtypes.bytes_wtype,),
                    c=(wtypes.bytes_wtype,),
                    d=(wtypes.bytes_wtype,),
                    e=(wtypes.bytes_wtype,),
                ),
                stack_outputs=(wtypes.bool_wtype,),
            ),
        ),
        "algopy.op.ed25519verify": (
            FunctionOpMapping(
                "ed25519verify",
                stack_inputs=dict(
                    a=(wtypes.bytes_wtype,), b=(wtypes.bytes_wtype,), c=(wtypes.bytes_wtype,)
                ),
                stack_outputs=(wtypes.bool_wtype,),
            ),
        ),
        "algopy.op.ed25519verify_bare": (
            FunctionOpMapping(
                "ed25519verify_bare",
                stack_inputs=dict(
                    a=(wtypes.bytes_wtype,), b=(wtypes.bytes_wtype,), c=(wtypes.bytes_wtype,)
                ),
                stack_outputs=(wtypes.bool_wtype,),
            ),
        ),
        "algopy.op.err": (
            FunctionOpMapping(
                "err",
            ),
        ),
        "algopy.op.exit": (
            FunctionOpMapping(
                "return",
                stack_inputs=dict(a=(wtypes.uint64_wtype,)),
            ),
        ),
        "algopy.op.exp": (
            FunctionOpMapping(
                "exp",
                stack_inputs=dict(a=(wtypes.uint64_wtype,), b=(wtypes.uint64_wtype,)),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.expw": (
            FunctionOpMapping(
                "expw",
                stack_inputs=dict(a=(wtypes.uint64_wtype,), b=(wtypes.uint64_wtype,)),
                stack_outputs=(
                    wtypes.uint64_wtype,
                    wtypes.uint64_wtype,
                ),
            ),
        ),
        "algopy.op.extract": (
            FunctionOpMapping(
                "extract3",
                stack_inputs=dict(
                    a=(wtypes.bytes_wtype,), b=(wtypes.uint64_wtype,), c=(wtypes.uint64_wtype,)
                ),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
            FunctionOpMapping(
                "extract",
                immediates=(ImmediateArgMapping("b", int), ImmediateArgMapping("c", int)),
                stack_inputs=dict(a=(wtypes.bytes_wtype,)),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.extract_uint16": (
            FunctionOpMapping(
                "extract_uint16",
                stack_inputs=dict(a=(wtypes.bytes_wtype,), b=(wtypes.uint64_wtype,)),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.extract_uint32": (
            FunctionOpMapping(
                "extract_uint32",
                stack_inputs=dict(a=(wtypes.bytes_wtype,), b=(wtypes.uint64_wtype,)),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.extract_uint64": (
            FunctionOpMapping(
                "extract_uint64",
                stack_inputs=dict(a=(wtypes.bytes_wtype,), b=(wtypes.uint64_wtype,)),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.gaid": (
            FunctionOpMapping(
                "gaids",
                stack_inputs=dict(a=(wtypes.uint64_wtype,)),
                stack_outputs=(wtypes.application_wtype,),
            ),
            FunctionOpMapping(
                "gaid",
                immediates=(ImmediateArgMapping("a", int),),
                stack_outputs=(wtypes.application_wtype,),
            ),
        ),
        "algopy.op.getbit": (
            FunctionOpMapping(
                "getbit",
                stack_inputs=dict(
                    a=(wtypes.bytes_wtype, wtypes.uint64_wtype), b=(wtypes.uint64_wtype,)
                ),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.getbyte": (
            FunctionOpMapping(
                "getbyte",
                stack_inputs=dict(a=(wtypes.bytes_wtype,), b=(wtypes.uint64_wtype,)),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.gload_bytes": (
            FunctionOpMapping(
                "gloadss",
                stack_inputs=dict(a=(wtypes.uint64_wtype,), b=(wtypes.uint64_wtype,)),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
            FunctionOpMapping(
                "gload",
                immediates=(ImmediateArgMapping("a", int), ImmediateArgMapping("b", int)),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
            FunctionOpMapping(
                "gloads",
                immediates=(ImmediateArgMapping("b", int),),
                stack_inputs=dict(a=(wtypes.uint64_wtype,)),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.gload_uint64": (
            FunctionOpMapping(
                "gloadss",
                stack_inputs=dict(a=(wtypes.uint64_wtype,), b=(wtypes.uint64_wtype,)),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
            FunctionOpMapping(
                "gload",
                immediates=(ImmediateArgMapping("a", int), ImmediateArgMapping("b", int)),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
            FunctionOpMapping(
                "gloads",
                immediates=(ImmediateArgMapping("b", int),),
                stack_inputs=dict(a=(wtypes.uint64_wtype,)),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.itob": (
            FunctionOpMapping(
                "itob",
                stack_inputs=dict(a=(wtypes.uint64_wtype,)),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.keccak256": (
            FunctionOpMapping(
                "keccak256",
                stack_inputs=dict(a=(wtypes.bytes_wtype,)),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.min_balance": (
            FunctionOpMapping(
                "min_balance",
                stack_inputs=dict(a=(wtypes.account_wtype, wtypes.uint64_wtype)),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.mulw": (
            FunctionOpMapping(
                "mulw",
                stack_inputs=dict(a=(wtypes.uint64_wtype,), b=(wtypes.uint64_wtype,)),
                stack_outputs=(
                    wtypes.uint64_wtype,
                    wtypes.uint64_wtype,
                ),
            ),
        ),
        "algopy.op.replace": (
            FunctionOpMapping(
                "replace3",
                stack_inputs=dict(
                    a=(wtypes.bytes_wtype,), b=(wtypes.uint64_wtype,), c=(wtypes.bytes_wtype,)
                ),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
            FunctionOpMapping(
                "replace2",
                immediates=(ImmediateArgMapping("b", int),),
                stack_inputs=dict(a=(wtypes.bytes_wtype,), c=(wtypes.bytes_wtype,)),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.select_bytes": (
            FunctionOpMapping(
                "select",
                stack_inputs=dict(
                    a=(wtypes.bytes_wtype,),
                    b=(wtypes.bytes_wtype,),
                    c=(wtypes.bool_wtype, wtypes.uint64_wtype),
                ),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.select_uint64": (
            FunctionOpMapping(
                "select",
                stack_inputs=dict(
                    a=(wtypes.uint64_wtype,),
                    b=(wtypes.uint64_wtype,),
                    c=(wtypes.bool_wtype, wtypes.uint64_wtype),
                ),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.setbit_bytes": (
            FunctionOpMapping(
                "setbit",
                stack_inputs=dict(
                    a=(wtypes.bytes_wtype,), b=(wtypes.uint64_wtype,), c=(wtypes.uint64_wtype,)
                ),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.setbit_uint64": (
            FunctionOpMapping(
                "setbit",
                stack_inputs=dict(
                    a=(wtypes.uint64_wtype,), b=(wtypes.uint64_wtype,), c=(wtypes.uint64_wtype,)
                ),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.setbyte": (
            FunctionOpMapping(
                "setbyte",
                stack_inputs=dict(
                    a=(wtypes.bytes_wtype,), b=(wtypes.uint64_wtype,), c=(wtypes.uint64_wtype,)
                ),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.sha256": (
            FunctionOpMapping(
                "sha256",
                stack_inputs=dict(a=(wtypes.bytes_wtype,)),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.sha3_256": (
            FunctionOpMapping(
                "sha3_256",
                stack_inputs=dict(a=(wtypes.bytes_wtype,)),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.sha512_256": (
            FunctionOpMapping(
                "sha512_256",
                stack_inputs=dict(a=(wtypes.bytes_wtype,)),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.shl": (
            FunctionOpMapping(
                "shl",
                stack_inputs=dict(a=(wtypes.uint64_wtype,), b=(wtypes.uint64_wtype,)),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.shr": (
            FunctionOpMapping(
                "shr",
                stack_inputs=dict(a=(wtypes.uint64_wtype,), b=(wtypes.uint64_wtype,)),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.sqrt": (
            FunctionOpMapping(
                "sqrt",
                stack_inputs=dict(a=(wtypes.uint64_wtype,)),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.substring": (
            FunctionOpMapping(
                "substring3",
                stack_inputs=dict(
                    a=(wtypes.bytes_wtype,), b=(wtypes.uint64_wtype,), c=(wtypes.uint64_wtype,)
                ),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
            FunctionOpMapping(
                "substring",
                immediates=(ImmediateArgMapping("b", int), ImmediateArgMapping("c", int)),
                stack_inputs=dict(a=(wtypes.bytes_wtype,)),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.vrf_verify": (
            FunctionOpMapping(
                "vrf_verify",
                immediates=(ImmediateArgMapping("s", str),),
                stack_inputs=dict(
                    a=(wtypes.bytes_wtype,), b=(wtypes.bytes_wtype,), c=(wtypes.bytes_wtype,)
                ),
                stack_outputs=(
                    wtypes.bytes_wtype,
                    wtypes.bool_wtype,
                ),
            ),
        ),
        "algopy.op.AcctParamsGet.acct_balance": (
            FunctionOpMapping(
                "acct_params_get",
                immediates=("AcctBalance",),
                stack_inputs=dict(a=(wtypes.account_wtype, wtypes.uint64_wtype)),
                stack_outputs=(
                    wtypes.uint64_wtype,
                    wtypes.bool_wtype,
                ),
            ),
        ),
        "algopy.op.AcctParamsGet.acct_min_balance": (
            FunctionOpMapping(
                "acct_params_get",
                immediates=("AcctMinBalance",),
                stack_inputs=dict(a=(wtypes.account_wtype, wtypes.uint64_wtype)),
                stack_outputs=(
                    wtypes.uint64_wtype,
                    wtypes.bool_wtype,
                ),
            ),
        ),
        "algopy.op.AcctParamsGet.acct_auth_addr": (
            FunctionOpMapping(
                "acct_params_get",
                immediates=("AcctAuthAddr",),
                stack_inputs=dict(a=(wtypes.account_wtype, wtypes.uint64_wtype)),
                stack_outputs=(
                    wtypes.account_wtype,
                    wtypes.bool_wtype,
                ),
            ),
        ),
        "algopy.op.AcctParamsGet.acct_total_num_uint": (
            FunctionOpMapping(
                "acct_params_get",
                immediates=("AcctTotalNumUint",),
                stack_inputs=dict(a=(wtypes.account_wtype, wtypes.uint64_wtype)),
                stack_outputs=(
                    wtypes.uint64_wtype,
                    wtypes.bool_wtype,
                ),
            ),
        ),
        "algopy.op.AcctParamsGet.acct_total_num_byte_slice": (
            FunctionOpMapping(
                "acct_params_get",
                immediates=("AcctTotalNumByteSlice",),
                stack_inputs=dict(a=(wtypes.account_wtype, wtypes.uint64_wtype)),
                stack_outputs=(
                    wtypes.uint64_wtype,
                    wtypes.bool_wtype,
                ),
            ),
        ),
        "algopy.op.AcctParamsGet.acct_total_extra_app_pages": (
            FunctionOpMapping(
                "acct_params_get",
                immediates=("AcctTotalExtraAppPages",),
                stack_inputs=dict(a=(wtypes.account_wtype, wtypes.uint64_wtype)),
                stack_outputs=(
                    wtypes.uint64_wtype,
                    wtypes.bool_wtype,
                ),
            ),
        ),
        "algopy.op.AcctParamsGet.acct_total_apps_created": (
            FunctionOpMapping(
                "acct_params_get",
                immediates=("AcctTotalAppsCreated",),
                stack_inputs=dict(a=(wtypes.account_wtype, wtypes.uint64_wtype)),
                stack_outputs=(
                    wtypes.uint64_wtype,
                    wtypes.bool_wtype,
                ),
            ),
        ),
        "algopy.op.AcctParamsGet.acct_total_apps_opted_in": (
            FunctionOpMapping(
                "acct_params_get",
                immediates=("AcctTotalAppsOptedIn",),
                stack_inputs=dict(a=(wtypes.account_wtype, wtypes.uint64_wtype)),
                stack_outputs=(
                    wtypes.uint64_wtype,
                    wtypes.bool_wtype,
                ),
            ),
        ),
        "algopy.op.AcctParamsGet.acct_total_assets_created": (
            FunctionOpMapping(
                "acct_params_get",
                immediates=("AcctTotalAssetsCreated",),
                stack_inputs=dict(a=(wtypes.account_wtype, wtypes.uint64_wtype)),
                stack_outputs=(
                    wtypes.uint64_wtype,
                    wtypes.bool_wtype,
                ),
            ),
        ),
        "algopy.op.AcctParamsGet.acct_total_assets": (
            FunctionOpMapping(
                "acct_params_get",
                immediates=("AcctTotalAssets",),
                stack_inputs=dict(a=(wtypes.account_wtype, wtypes.uint64_wtype)),
                stack_outputs=(
                    wtypes.uint64_wtype,
                    wtypes.bool_wtype,
                ),
            ),
        ),
        "algopy.op.AcctParamsGet.acct_total_boxes": (
            FunctionOpMapping(
                "acct_params_get",
                immediates=("AcctTotalBoxes",),
                stack_inputs=dict(a=(wtypes.account_wtype, wtypes.uint64_wtype)),
                stack_outputs=(
                    wtypes.uint64_wtype,
                    wtypes.bool_wtype,
                ),
            ),
        ),
        "algopy.op.AcctParamsGet.acct_total_box_bytes": (
            FunctionOpMapping(
                "acct_params_get",
                immediates=("AcctTotalBoxBytes",),
                stack_inputs=dict(a=(wtypes.account_wtype, wtypes.uint64_wtype)),
                stack_outputs=(
                    wtypes.uint64_wtype,
                    wtypes.bool_wtype,
                ),
            ),
        ),
        "algopy.op.AppGlobal.get_bytes": (
            FunctionOpMapping(
                "app_global_get",
                stack_inputs=dict(a=(wtypes.bytes_wtype,)),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.AppGlobal.get_uint64": (
            FunctionOpMapping(
                "app_global_get",
                stack_inputs=dict(a=(wtypes.bytes_wtype,)),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.AppGlobal.get_ex_bytes": (
            FunctionOpMapping(
                "app_global_get_ex",
                stack_inputs=dict(
                    a=(wtypes.application_wtype, wtypes.uint64_wtype), b=(wtypes.bytes_wtype,)
                ),
                stack_outputs=(
                    wtypes.bytes_wtype,
                    wtypes.bool_wtype,
                ),
            ),
        ),
        "algopy.op.AppGlobal.get_ex_uint64": (
            FunctionOpMapping(
                "app_global_get_ex",
                stack_inputs=dict(
                    a=(wtypes.application_wtype, wtypes.uint64_wtype), b=(wtypes.bytes_wtype,)
                ),
                stack_outputs=(
                    wtypes.uint64_wtype,
                    wtypes.bool_wtype,
                ),
            ),
        ),
        "algopy.op.AppGlobal.delete": (
            FunctionOpMapping(
                "app_global_del",
                stack_inputs=dict(a=(wtypes.bytes_wtype,)),
            ),
        ),
        "algopy.op.AppGlobal.put": (
            FunctionOpMapping(
                "app_global_put",
                stack_inputs=dict(
                    a=(wtypes.bytes_wtype,), b=(wtypes.bytes_wtype, wtypes.uint64_wtype)
                ),
            ),
        ),
        "algopy.op.AppLocal.get_bytes": (
            FunctionOpMapping(
                "app_local_get",
                stack_inputs=dict(
                    a=(wtypes.account_wtype, wtypes.uint64_wtype), b=(wtypes.bytes_wtype,)
                ),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.AppLocal.get_uint64": (
            FunctionOpMapping(
                "app_local_get",
                stack_inputs=dict(
                    a=(wtypes.account_wtype, wtypes.uint64_wtype), b=(wtypes.bytes_wtype,)
                ),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.AppLocal.get_ex_bytes": (
            FunctionOpMapping(
                "app_local_get_ex",
                stack_inputs=dict(
                    a=(wtypes.account_wtype, wtypes.uint64_wtype),
                    b=(wtypes.application_wtype, wtypes.uint64_wtype),
                    c=(wtypes.bytes_wtype,),
                ),
                stack_outputs=(
                    wtypes.bytes_wtype,
                    wtypes.bool_wtype,
                ),
            ),
        ),
        "algopy.op.AppLocal.get_ex_uint64": (
            FunctionOpMapping(
                "app_local_get_ex",
                stack_inputs=dict(
                    a=(wtypes.account_wtype, wtypes.uint64_wtype),
                    b=(wtypes.application_wtype, wtypes.uint64_wtype),
                    c=(wtypes.bytes_wtype,),
                ),
                stack_outputs=(
                    wtypes.uint64_wtype,
                    wtypes.bool_wtype,
                ),
            ),
        ),
        "algopy.op.AppLocal.delete": (
            FunctionOpMapping(
                "app_local_del",
                stack_inputs=dict(
                    a=(wtypes.account_wtype, wtypes.uint64_wtype), b=(wtypes.bytes_wtype,)
                ),
            ),
        ),
        "algopy.op.AppLocal.put": (
            FunctionOpMapping(
                "app_local_put",
                stack_inputs=dict(
                    a=(wtypes.account_wtype, wtypes.uint64_wtype),
                    b=(wtypes.bytes_wtype,),
                    c=(wtypes.bytes_wtype, wtypes.uint64_wtype),
                ),
            ),
        ),
        "algopy.op.AppParamsGet.app_approval_program": (
            FunctionOpMapping(
                "app_params_get",
                immediates=("AppApprovalProgram",),
                stack_inputs=dict(a=(wtypes.application_wtype, wtypes.uint64_wtype)),
                stack_outputs=(
                    wtypes.bytes_wtype,
                    wtypes.bool_wtype,
                ),
            ),
        ),
        "algopy.op.AppParamsGet.app_clear_state_program": (
            FunctionOpMapping(
                "app_params_get",
                immediates=("AppClearStateProgram",),
                stack_inputs=dict(a=(wtypes.application_wtype, wtypes.uint64_wtype)),
                stack_outputs=(
                    wtypes.bytes_wtype,
                    wtypes.bool_wtype,
                ),
            ),
        ),
        "algopy.op.AppParamsGet.app_global_num_uint": (
            FunctionOpMapping(
                "app_params_get",
                immediates=("AppGlobalNumUint",),
                stack_inputs=dict(a=(wtypes.application_wtype, wtypes.uint64_wtype)),
                stack_outputs=(
                    wtypes.uint64_wtype,
                    wtypes.bool_wtype,
                ),
            ),
        ),
        "algopy.op.AppParamsGet.app_global_num_byte_slice": (
            FunctionOpMapping(
                "app_params_get",
                immediates=("AppGlobalNumByteSlice",),
                stack_inputs=dict(a=(wtypes.application_wtype, wtypes.uint64_wtype)),
                stack_outputs=(
                    wtypes.uint64_wtype,
                    wtypes.bool_wtype,
                ),
            ),
        ),
        "algopy.op.AppParamsGet.app_local_num_uint": (
            FunctionOpMapping(
                "app_params_get",
                immediates=("AppLocalNumUint",),
                stack_inputs=dict(a=(wtypes.application_wtype, wtypes.uint64_wtype)),
                stack_outputs=(
                    wtypes.uint64_wtype,
                    wtypes.bool_wtype,
                ),
            ),
        ),
        "algopy.op.AppParamsGet.app_local_num_byte_slice": (
            FunctionOpMapping(
                "app_params_get",
                immediates=("AppLocalNumByteSlice",),
                stack_inputs=dict(a=(wtypes.application_wtype, wtypes.uint64_wtype)),
                stack_outputs=(
                    wtypes.uint64_wtype,
                    wtypes.bool_wtype,
                ),
            ),
        ),
        "algopy.op.AppParamsGet.app_extra_program_pages": (
            FunctionOpMapping(
                "app_params_get",
                immediates=("AppExtraProgramPages",),
                stack_inputs=dict(a=(wtypes.application_wtype, wtypes.uint64_wtype)),
                stack_outputs=(
                    wtypes.uint64_wtype,
                    wtypes.bool_wtype,
                ),
            ),
        ),
        "algopy.op.AppParamsGet.app_creator": (
            FunctionOpMapping(
                "app_params_get",
                immediates=("AppCreator",),
                stack_inputs=dict(a=(wtypes.application_wtype, wtypes.uint64_wtype)),
                stack_outputs=(
                    wtypes.account_wtype,
                    wtypes.bool_wtype,
                ),
            ),
        ),
        "algopy.op.AppParamsGet.app_address": (
            FunctionOpMapping(
                "app_params_get",
                immediates=("AppAddress",),
                stack_inputs=dict(a=(wtypes.application_wtype, wtypes.uint64_wtype)),
                stack_outputs=(
                    wtypes.account_wtype,
                    wtypes.bool_wtype,
                ),
            ),
        ),
        "algopy.op.AssetHoldingGet.asset_balance": (
            FunctionOpMapping(
                "asset_holding_get",
                immediates=("AssetBalance",),
                stack_inputs=dict(
                    a=(wtypes.account_wtype, wtypes.uint64_wtype),
                    b=(wtypes.asset_wtype, wtypes.uint64_wtype),
                ),
                stack_outputs=(
                    wtypes.uint64_wtype,
                    wtypes.bool_wtype,
                ),
            ),
        ),
        "algopy.op.AssetHoldingGet.asset_frozen": (
            FunctionOpMapping(
                "asset_holding_get",
                immediates=("AssetFrozen",),
                stack_inputs=dict(
                    a=(wtypes.account_wtype, wtypes.uint64_wtype),
                    b=(wtypes.asset_wtype, wtypes.uint64_wtype),
                ),
                stack_outputs=(
                    wtypes.bool_wtype,
                    wtypes.bool_wtype,
                ),
            ),
        ),
        "algopy.op.AssetParamsGet.asset_total": (
            FunctionOpMapping(
                "asset_params_get",
                immediates=("AssetTotal",),
                stack_inputs=dict(a=(wtypes.asset_wtype, wtypes.uint64_wtype)),
                stack_outputs=(
                    wtypes.uint64_wtype,
                    wtypes.bool_wtype,
                ),
            ),
        ),
        "algopy.op.AssetParamsGet.asset_decimals": (
            FunctionOpMapping(
                "asset_params_get",
                immediates=("AssetDecimals",),
                stack_inputs=dict(a=(wtypes.asset_wtype, wtypes.uint64_wtype)),
                stack_outputs=(
                    wtypes.uint64_wtype,
                    wtypes.bool_wtype,
                ),
            ),
        ),
        "algopy.op.AssetParamsGet.asset_default_frozen": (
            FunctionOpMapping(
                "asset_params_get",
                immediates=("AssetDefaultFrozen",),
                stack_inputs=dict(a=(wtypes.asset_wtype, wtypes.uint64_wtype)),
                stack_outputs=(
                    wtypes.bool_wtype,
                    wtypes.bool_wtype,
                ),
            ),
        ),
        "algopy.op.AssetParamsGet.asset_unit_name": (
            FunctionOpMapping(
                "asset_params_get",
                immediates=("AssetUnitName",),
                stack_inputs=dict(a=(wtypes.asset_wtype, wtypes.uint64_wtype)),
                stack_outputs=(
                    wtypes.bytes_wtype,
                    wtypes.bool_wtype,
                ),
            ),
        ),
        "algopy.op.AssetParamsGet.asset_name": (
            FunctionOpMapping(
                "asset_params_get",
                immediates=("AssetName",),
                stack_inputs=dict(a=(wtypes.asset_wtype, wtypes.uint64_wtype)),
                stack_outputs=(
                    wtypes.bytes_wtype,
                    wtypes.bool_wtype,
                ),
            ),
        ),
        "algopy.op.AssetParamsGet.asset_url": (
            FunctionOpMapping(
                "asset_params_get",
                immediates=("AssetURL",),
                stack_inputs=dict(a=(wtypes.asset_wtype, wtypes.uint64_wtype)),
                stack_outputs=(
                    wtypes.bytes_wtype,
                    wtypes.bool_wtype,
                ),
            ),
        ),
        "algopy.op.AssetParamsGet.asset_metadata_hash": (
            FunctionOpMapping(
                "asset_params_get",
                immediates=("AssetMetadataHash",),
                stack_inputs=dict(a=(wtypes.asset_wtype, wtypes.uint64_wtype)),
                stack_outputs=(
                    wtypes.bytes_wtype,
                    wtypes.bool_wtype,
                ),
            ),
        ),
        "algopy.op.AssetParamsGet.asset_manager": (
            FunctionOpMapping(
                "asset_params_get",
                immediates=("AssetManager",),
                stack_inputs=dict(a=(wtypes.asset_wtype, wtypes.uint64_wtype)),
                stack_outputs=(
                    wtypes.account_wtype,
                    wtypes.bool_wtype,
                ),
            ),
        ),
        "algopy.op.AssetParamsGet.asset_reserve": (
            FunctionOpMapping(
                "asset_params_get",
                immediates=("AssetReserve",),
                stack_inputs=dict(a=(wtypes.asset_wtype, wtypes.uint64_wtype)),
                stack_outputs=(
                    wtypes.account_wtype,
                    wtypes.bool_wtype,
                ),
            ),
        ),
        "algopy.op.AssetParamsGet.asset_freeze": (
            FunctionOpMapping(
                "asset_params_get",
                immediates=("AssetFreeze",),
                stack_inputs=dict(a=(wtypes.asset_wtype, wtypes.uint64_wtype)),
                stack_outputs=(
                    wtypes.account_wtype,
                    wtypes.bool_wtype,
                ),
            ),
        ),
        "algopy.op.AssetParamsGet.asset_clawback": (
            FunctionOpMapping(
                "asset_params_get",
                immediates=("AssetClawback",),
                stack_inputs=dict(a=(wtypes.asset_wtype, wtypes.uint64_wtype)),
                stack_outputs=(
                    wtypes.account_wtype,
                    wtypes.bool_wtype,
                ),
            ),
        ),
        "algopy.op.AssetParamsGet.asset_creator": (
            FunctionOpMapping(
                "asset_params_get",
                immediates=("AssetCreator",),
                stack_inputs=dict(a=(wtypes.asset_wtype, wtypes.uint64_wtype)),
                stack_outputs=(
                    wtypes.account_wtype,
                    wtypes.bool_wtype,
                ),
            ),
        ),
        "algopy.op.Block.blk_seed": (
            FunctionOpMapping(
                "block",
                immediates=("BlkSeed",),
                stack_inputs=dict(a=(wtypes.uint64_wtype,)),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.Block.blk_timestamp": (
            FunctionOpMapping(
                "block",
                immediates=("BlkTimestamp",),
                stack_inputs=dict(a=(wtypes.uint64_wtype,)),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.Box.create": (
            FunctionOpMapping(
                "box_create",
                stack_inputs=dict(a=(wtypes.bytes_wtype,), b=(wtypes.uint64_wtype,)),
                stack_outputs=(wtypes.bool_wtype,),
            ),
        ),
        "algopy.op.Box.delete": (
            FunctionOpMapping(
                "box_del",
                stack_inputs=dict(a=(wtypes.bytes_wtype,)),
                stack_outputs=(wtypes.bool_wtype,),
            ),
        ),
        "algopy.op.Box.extract": (
            FunctionOpMapping(
                "box_extract",
                stack_inputs=dict(
                    a=(wtypes.bytes_wtype,), b=(wtypes.uint64_wtype,), c=(wtypes.uint64_wtype,)
                ),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.Box.get": (
            FunctionOpMapping(
                "box_get",
                stack_inputs=dict(a=(wtypes.bytes_wtype,)),
                stack_outputs=(
                    wtypes.bytes_wtype,
                    wtypes.bool_wtype,
                ),
            ),
        ),
        "algopy.op.Box.length": (
            FunctionOpMapping(
                "box_len",
                stack_inputs=dict(a=(wtypes.bytes_wtype,)),
                stack_outputs=(
                    wtypes.uint64_wtype,
                    wtypes.bool_wtype,
                ),
            ),
        ),
        "algopy.op.Box.put": (
            FunctionOpMapping(
                "box_put",
                stack_inputs=dict(a=(wtypes.bytes_wtype,), b=(wtypes.bytes_wtype,)),
            ),
        ),
        "algopy.op.Box.replace": (
            FunctionOpMapping(
                "box_replace",
                stack_inputs=dict(
                    a=(wtypes.bytes_wtype,), b=(wtypes.uint64_wtype,), c=(wtypes.bytes_wtype,)
                ),
            ),
        ),
        "algopy.op.Box.resize": (
            FunctionOpMapping(
                "box_resize",
                stack_inputs=dict(a=(wtypes.bytes_wtype,), b=(wtypes.uint64_wtype,)),
            ),
        ),
        "algopy.op.Box.splice": (
            FunctionOpMapping(
                "box_splice",
                stack_inputs=dict(
                    a=(wtypes.bytes_wtype,),
                    b=(wtypes.uint64_wtype,),
                    c=(wtypes.uint64_wtype,),
                    d=(wtypes.bytes_wtype,),
                ),
            ),
        ),
        "algopy.op.EllipticCurve.add": (
            FunctionOpMapping(
                "ec_add",
                immediates=(ImmediateArgMapping("g", str),),
                stack_inputs=dict(a=(wtypes.bytes_wtype,), b=(wtypes.bytes_wtype,)),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.EllipticCurve.map_to": (
            FunctionOpMapping(
                "ec_map_to",
                immediates=(ImmediateArgMapping("g", str),),
                stack_inputs=dict(a=(wtypes.bytes_wtype,)),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.EllipticCurve.scalar_mul_multi": (
            FunctionOpMapping(
                "ec_multi_scalar_mul",
                immediates=(ImmediateArgMapping("g", str),),
                stack_inputs=dict(a=(wtypes.bytes_wtype,), b=(wtypes.bytes_wtype,)),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.EllipticCurve.pairing_check": (
            FunctionOpMapping(
                "ec_pairing_check",
                immediates=(ImmediateArgMapping("g", str),),
                stack_inputs=dict(a=(wtypes.bytes_wtype,), b=(wtypes.bytes_wtype,)),
                stack_outputs=(wtypes.bool_wtype,),
            ),
        ),
        "algopy.op.EllipticCurve.scalar_mul": (
            FunctionOpMapping(
                "ec_scalar_mul",
                immediates=(ImmediateArgMapping("g", str),),
                stack_inputs=dict(a=(wtypes.bytes_wtype,), b=(wtypes.bytes_wtype,)),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.EllipticCurve.subgroup_check": (
            FunctionOpMapping(
                "ec_subgroup_check",
                immediates=(ImmediateArgMapping("g", str),),
                stack_inputs=dict(a=(wtypes.bytes_wtype,)),
                stack_outputs=(wtypes.bool_wtype,),
            ),
        ),
        "algopy.op.GITxn.sender": (
            FunctionOpMapping(
                "gitxn",
                immediates=(ImmediateArgMapping("t", int), "Sender"),
                stack_outputs=(wtypes.account_wtype,),
            ),
        ),
        "algopy.op.GITxn.fee": (
            FunctionOpMapping(
                "gitxn",
                immediates=(ImmediateArgMapping("t", int), "Fee"),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.GITxn.first_valid": (
            FunctionOpMapping(
                "gitxn",
                immediates=(ImmediateArgMapping("t", int), "FirstValid"),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.GITxn.first_valid_time": (
            FunctionOpMapping(
                "gitxn",
                immediates=(ImmediateArgMapping("t", int), "FirstValidTime"),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.GITxn.last_valid": (
            FunctionOpMapping(
                "gitxn",
                immediates=(ImmediateArgMapping("t", int), "LastValid"),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.GITxn.note": (
            FunctionOpMapping(
                "gitxn",
                immediates=(ImmediateArgMapping("t", int), "Note"),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.GITxn.lease": (
            FunctionOpMapping(
                "gitxn",
                immediates=(ImmediateArgMapping("t", int), "Lease"),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.GITxn.receiver": (
            FunctionOpMapping(
                "gitxn",
                immediates=(ImmediateArgMapping("t", int), "Receiver"),
                stack_outputs=(wtypes.account_wtype,),
            ),
        ),
        "algopy.op.GITxn.amount": (
            FunctionOpMapping(
                "gitxn",
                immediates=(ImmediateArgMapping("t", int), "Amount"),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.GITxn.close_remainder_to": (
            FunctionOpMapping(
                "gitxn",
                immediates=(ImmediateArgMapping("t", int), "CloseRemainderTo"),
                stack_outputs=(wtypes.account_wtype,),
            ),
        ),
        "algopy.op.GITxn.vote_pk": (
            FunctionOpMapping(
                "gitxn",
                immediates=(ImmediateArgMapping("t", int), "VotePK"),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.GITxn.selection_pk": (
            FunctionOpMapping(
                "gitxn",
                immediates=(ImmediateArgMapping("t", int), "SelectionPK"),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.GITxn.vote_first": (
            FunctionOpMapping(
                "gitxn",
                immediates=(ImmediateArgMapping("t", int), "VoteFirst"),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.GITxn.vote_last": (
            FunctionOpMapping(
                "gitxn",
                immediates=(ImmediateArgMapping("t", int), "VoteLast"),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.GITxn.vote_key_dilution": (
            FunctionOpMapping(
                "gitxn",
                immediates=(ImmediateArgMapping("t", int), "VoteKeyDilution"),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.GITxn.type": (
            FunctionOpMapping(
                "gitxn",
                immediates=(ImmediateArgMapping("t", int), "Type"),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.GITxn.type_enum": (
            FunctionOpMapping(
                "gitxn",
                immediates=(ImmediateArgMapping("t", int), "TypeEnum"),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.GITxn.xfer_asset": (
            FunctionOpMapping(
                "gitxn",
                immediates=(ImmediateArgMapping("t", int), "XferAsset"),
                stack_outputs=(wtypes.asset_wtype,),
            ),
        ),
        "algopy.op.GITxn.asset_amount": (
            FunctionOpMapping(
                "gitxn",
                immediates=(ImmediateArgMapping("t", int), "AssetAmount"),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.GITxn.asset_sender": (
            FunctionOpMapping(
                "gitxn",
                immediates=(ImmediateArgMapping("t", int), "AssetSender"),
                stack_outputs=(wtypes.account_wtype,),
            ),
        ),
        "algopy.op.GITxn.asset_receiver": (
            FunctionOpMapping(
                "gitxn",
                immediates=(ImmediateArgMapping("t", int), "AssetReceiver"),
                stack_outputs=(wtypes.account_wtype,),
            ),
        ),
        "algopy.op.GITxn.asset_close_to": (
            FunctionOpMapping(
                "gitxn",
                immediates=(ImmediateArgMapping("t", int), "AssetCloseTo"),
                stack_outputs=(wtypes.account_wtype,),
            ),
        ),
        "algopy.op.GITxn.group_index": (
            FunctionOpMapping(
                "gitxn",
                immediates=(ImmediateArgMapping("t", int), "GroupIndex"),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.GITxn.tx_id": (
            FunctionOpMapping(
                "gitxn",
                immediates=(ImmediateArgMapping("t", int), "TxID"),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.GITxn.application_id": (
            FunctionOpMapping(
                "gitxn",
                immediates=(ImmediateArgMapping("t", int), "ApplicationID"),
                stack_outputs=(wtypes.application_wtype,),
            ),
        ),
        "algopy.op.GITxn.on_completion": (
            FunctionOpMapping(
                "gitxn",
                immediates=(ImmediateArgMapping("t", int), "OnCompletion"),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.GITxn.application_args": (
            FunctionOpMapping(
                "gitxnas",
                immediates=(ImmediateArgMapping("t", int), "ApplicationArgs"),
                stack_inputs=dict(a=(wtypes.uint64_wtype,)),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
            FunctionOpMapping(
                "gitxna",
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
                "gitxn",
                immediates=(ImmediateArgMapping("t", int), "NumAppArgs"),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.GITxn.accounts": (
            FunctionOpMapping(
                "gitxnas",
                immediates=(ImmediateArgMapping("t", int), "Accounts"),
                stack_inputs=dict(a=(wtypes.uint64_wtype,)),
                stack_outputs=(wtypes.account_wtype,),
            ),
            FunctionOpMapping(
                "gitxna",
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
                "gitxn",
                immediates=(ImmediateArgMapping("t", int), "NumAccounts"),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.GITxn.approval_program": (
            FunctionOpMapping(
                "gitxn",
                immediates=(ImmediateArgMapping("t", int), "ApprovalProgram"),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.GITxn.clear_state_program": (
            FunctionOpMapping(
                "gitxn",
                immediates=(ImmediateArgMapping("t", int), "ClearStateProgram"),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.GITxn.rekey_to": (
            FunctionOpMapping(
                "gitxn",
                immediates=(ImmediateArgMapping("t", int), "RekeyTo"),
                stack_outputs=(wtypes.account_wtype,),
            ),
        ),
        "algopy.op.GITxn.config_asset": (
            FunctionOpMapping(
                "gitxn",
                immediates=(ImmediateArgMapping("t", int), "ConfigAsset"),
                stack_outputs=(wtypes.asset_wtype,),
            ),
        ),
        "algopy.op.GITxn.config_asset_total": (
            FunctionOpMapping(
                "gitxn",
                immediates=(ImmediateArgMapping("t", int), "ConfigAssetTotal"),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.GITxn.config_asset_decimals": (
            FunctionOpMapping(
                "gitxn",
                immediates=(ImmediateArgMapping("t", int), "ConfigAssetDecimals"),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.GITxn.config_asset_default_frozen": (
            FunctionOpMapping(
                "gitxn",
                immediates=(ImmediateArgMapping("t", int), "ConfigAssetDefaultFrozen"),
                stack_outputs=(wtypes.bool_wtype,),
            ),
        ),
        "algopy.op.GITxn.config_asset_unit_name": (
            FunctionOpMapping(
                "gitxn",
                immediates=(ImmediateArgMapping("t", int), "ConfigAssetUnitName"),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.GITxn.config_asset_name": (
            FunctionOpMapping(
                "gitxn",
                immediates=(ImmediateArgMapping("t", int), "ConfigAssetName"),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.GITxn.config_asset_url": (
            FunctionOpMapping(
                "gitxn",
                immediates=(ImmediateArgMapping("t", int), "ConfigAssetURL"),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.GITxn.config_asset_metadata_hash": (
            FunctionOpMapping(
                "gitxn",
                immediates=(ImmediateArgMapping("t", int), "ConfigAssetMetadataHash"),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.GITxn.config_asset_manager": (
            FunctionOpMapping(
                "gitxn",
                immediates=(ImmediateArgMapping("t", int), "ConfigAssetManager"),
                stack_outputs=(wtypes.account_wtype,),
            ),
        ),
        "algopy.op.GITxn.config_asset_reserve": (
            FunctionOpMapping(
                "gitxn",
                immediates=(ImmediateArgMapping("t", int), "ConfigAssetReserve"),
                stack_outputs=(wtypes.account_wtype,),
            ),
        ),
        "algopy.op.GITxn.config_asset_freeze": (
            FunctionOpMapping(
                "gitxn",
                immediates=(ImmediateArgMapping("t", int), "ConfigAssetFreeze"),
                stack_outputs=(wtypes.account_wtype,),
            ),
        ),
        "algopy.op.GITxn.config_asset_clawback": (
            FunctionOpMapping(
                "gitxn",
                immediates=(ImmediateArgMapping("t", int), "ConfigAssetClawback"),
                stack_outputs=(wtypes.account_wtype,),
            ),
        ),
        "algopy.op.GITxn.freeze_asset": (
            FunctionOpMapping(
                "gitxn",
                immediates=(ImmediateArgMapping("t", int), "FreezeAsset"),
                stack_outputs=(wtypes.asset_wtype,),
            ),
        ),
        "algopy.op.GITxn.freeze_asset_account": (
            FunctionOpMapping(
                "gitxn",
                immediates=(ImmediateArgMapping("t", int), "FreezeAssetAccount"),
                stack_outputs=(wtypes.account_wtype,),
            ),
        ),
        "algopy.op.GITxn.freeze_asset_frozen": (
            FunctionOpMapping(
                "gitxn",
                immediates=(ImmediateArgMapping("t", int), "FreezeAssetFrozen"),
                stack_outputs=(wtypes.bool_wtype,),
            ),
        ),
        "algopy.op.GITxn.assets": (
            FunctionOpMapping(
                "gitxnas",
                immediates=(ImmediateArgMapping("t", int), "Assets"),
                stack_inputs=dict(a=(wtypes.uint64_wtype,)),
                stack_outputs=(wtypes.asset_wtype,),
            ),
            FunctionOpMapping(
                "gitxna",
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
                "gitxn",
                immediates=(ImmediateArgMapping("t", int), "NumAssets"),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.GITxn.applications": (
            FunctionOpMapping(
                "gitxnas",
                immediates=(ImmediateArgMapping("t", int), "Applications"),
                stack_inputs=dict(a=(wtypes.uint64_wtype,)),
                stack_outputs=(wtypes.application_wtype,),
            ),
            FunctionOpMapping(
                "gitxna",
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
                "gitxn",
                immediates=(ImmediateArgMapping("t", int), "NumApplications"),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.GITxn.global_num_uint": (
            FunctionOpMapping(
                "gitxn",
                immediates=(ImmediateArgMapping("t", int), "GlobalNumUint"),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.GITxn.global_num_byte_slice": (
            FunctionOpMapping(
                "gitxn",
                immediates=(ImmediateArgMapping("t", int), "GlobalNumByteSlice"),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.GITxn.local_num_uint": (
            FunctionOpMapping(
                "gitxn",
                immediates=(ImmediateArgMapping("t", int), "LocalNumUint"),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.GITxn.local_num_byte_slice": (
            FunctionOpMapping(
                "gitxn",
                immediates=(ImmediateArgMapping("t", int), "LocalNumByteSlice"),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.GITxn.extra_program_pages": (
            FunctionOpMapping(
                "gitxn",
                immediates=(ImmediateArgMapping("t", int), "ExtraProgramPages"),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.GITxn.nonparticipation": (
            FunctionOpMapping(
                "gitxn",
                immediates=(ImmediateArgMapping("t", int), "Nonparticipation"),
                stack_outputs=(wtypes.bool_wtype,),
            ),
        ),
        "algopy.op.GITxn.logs": (
            FunctionOpMapping(
                "gitxnas",
                immediates=(ImmediateArgMapping("t", int), "Logs"),
                stack_inputs=dict(a=(wtypes.uint64_wtype,)),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
            FunctionOpMapping(
                "gitxna",
                immediates=(ImmediateArgMapping("t", int), "Logs", ImmediateArgMapping("a", int)),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.GITxn.num_logs": (
            FunctionOpMapping(
                "gitxn",
                immediates=(ImmediateArgMapping("t", int), "NumLogs"),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.GITxn.created_asset_id": (
            FunctionOpMapping(
                "gitxn",
                immediates=(ImmediateArgMapping("t", int), "CreatedAssetID"),
                stack_outputs=(wtypes.asset_wtype,),
            ),
        ),
        "algopy.op.GITxn.created_application_id": (
            FunctionOpMapping(
                "gitxn",
                immediates=(ImmediateArgMapping("t", int), "CreatedApplicationID"),
                stack_outputs=(wtypes.application_wtype,),
            ),
        ),
        "algopy.op.GITxn.last_log": (
            FunctionOpMapping(
                "gitxn",
                immediates=(ImmediateArgMapping("t", int), "LastLog"),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.GITxn.state_proof_pk": (
            FunctionOpMapping(
                "gitxn",
                immediates=(ImmediateArgMapping("t", int), "StateProofPK"),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.GITxn.approval_program_pages": (
            FunctionOpMapping(
                "gitxnas",
                immediates=(ImmediateArgMapping("t", int), "ApprovalProgramPages"),
                stack_inputs=dict(a=(wtypes.uint64_wtype,)),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
            FunctionOpMapping(
                "gitxna",
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
                "gitxn",
                immediates=(ImmediateArgMapping("t", int), "NumApprovalProgramPages"),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.GITxn.clear_state_program_pages": (
            FunctionOpMapping(
                "gitxnas",
                immediates=(ImmediateArgMapping("t", int), "ClearStateProgramPages"),
                stack_inputs=dict(a=(wtypes.uint64_wtype,)),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
            FunctionOpMapping(
                "gitxna",
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
                "gitxn",
                immediates=(ImmediateArgMapping("t", int), "NumClearStateProgramPages"),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.GTxn.sender": (
            FunctionOpMapping(
                "gtxns",
                immediates=("Sender",),
                stack_inputs=dict(a=(wtypes.uint64_wtype,)),
                stack_outputs=(wtypes.account_wtype,),
            ),
            FunctionOpMapping(
                "gtxn",
                immediates=(ImmediateArgMapping("a", int), "Sender"),
                stack_outputs=(wtypes.account_wtype,),
            ),
        ),
        "algopy.op.GTxn.fee": (
            FunctionOpMapping(
                "gtxns",
                immediates=("Fee",),
                stack_inputs=dict(a=(wtypes.uint64_wtype,)),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
            FunctionOpMapping(
                "gtxn",
                immediates=(ImmediateArgMapping("a", int), "Fee"),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.GTxn.first_valid": (
            FunctionOpMapping(
                "gtxns",
                immediates=("FirstValid",),
                stack_inputs=dict(a=(wtypes.uint64_wtype,)),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
            FunctionOpMapping(
                "gtxn",
                immediates=(ImmediateArgMapping("a", int), "FirstValid"),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.GTxn.first_valid_time": (
            FunctionOpMapping(
                "gtxns",
                immediates=("FirstValidTime",),
                stack_inputs=dict(a=(wtypes.uint64_wtype,)),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
            FunctionOpMapping(
                "gtxn",
                immediates=(ImmediateArgMapping("a", int), "FirstValidTime"),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.GTxn.last_valid": (
            FunctionOpMapping(
                "gtxns",
                immediates=("LastValid",),
                stack_inputs=dict(a=(wtypes.uint64_wtype,)),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
            FunctionOpMapping(
                "gtxn",
                immediates=(ImmediateArgMapping("a", int), "LastValid"),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.GTxn.note": (
            FunctionOpMapping(
                "gtxns",
                immediates=("Note",),
                stack_inputs=dict(a=(wtypes.uint64_wtype,)),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
            FunctionOpMapping(
                "gtxn",
                immediates=(ImmediateArgMapping("a", int), "Note"),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.GTxn.lease": (
            FunctionOpMapping(
                "gtxns",
                immediates=("Lease",),
                stack_inputs=dict(a=(wtypes.uint64_wtype,)),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
            FunctionOpMapping(
                "gtxn",
                immediates=(ImmediateArgMapping("a", int), "Lease"),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.GTxn.receiver": (
            FunctionOpMapping(
                "gtxns",
                immediates=("Receiver",),
                stack_inputs=dict(a=(wtypes.uint64_wtype,)),
                stack_outputs=(wtypes.account_wtype,),
            ),
            FunctionOpMapping(
                "gtxn",
                immediates=(ImmediateArgMapping("a", int), "Receiver"),
                stack_outputs=(wtypes.account_wtype,),
            ),
        ),
        "algopy.op.GTxn.amount": (
            FunctionOpMapping(
                "gtxns",
                immediates=("Amount",),
                stack_inputs=dict(a=(wtypes.uint64_wtype,)),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
            FunctionOpMapping(
                "gtxn",
                immediates=(ImmediateArgMapping("a", int), "Amount"),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.GTxn.close_remainder_to": (
            FunctionOpMapping(
                "gtxns",
                immediates=("CloseRemainderTo",),
                stack_inputs=dict(a=(wtypes.uint64_wtype,)),
                stack_outputs=(wtypes.account_wtype,),
            ),
            FunctionOpMapping(
                "gtxn",
                immediates=(ImmediateArgMapping("a", int), "CloseRemainderTo"),
                stack_outputs=(wtypes.account_wtype,),
            ),
        ),
        "algopy.op.GTxn.vote_pk": (
            FunctionOpMapping(
                "gtxns",
                immediates=("VotePK",),
                stack_inputs=dict(a=(wtypes.uint64_wtype,)),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
            FunctionOpMapping(
                "gtxn",
                immediates=(ImmediateArgMapping("a", int), "VotePK"),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.GTxn.selection_pk": (
            FunctionOpMapping(
                "gtxns",
                immediates=("SelectionPK",),
                stack_inputs=dict(a=(wtypes.uint64_wtype,)),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
            FunctionOpMapping(
                "gtxn",
                immediates=(ImmediateArgMapping("a", int), "SelectionPK"),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.GTxn.vote_first": (
            FunctionOpMapping(
                "gtxns",
                immediates=("VoteFirst",),
                stack_inputs=dict(a=(wtypes.uint64_wtype,)),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
            FunctionOpMapping(
                "gtxn",
                immediates=(ImmediateArgMapping("a", int), "VoteFirst"),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.GTxn.vote_last": (
            FunctionOpMapping(
                "gtxns",
                immediates=("VoteLast",),
                stack_inputs=dict(a=(wtypes.uint64_wtype,)),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
            FunctionOpMapping(
                "gtxn",
                immediates=(ImmediateArgMapping("a", int), "VoteLast"),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.GTxn.vote_key_dilution": (
            FunctionOpMapping(
                "gtxns",
                immediates=("VoteKeyDilution",),
                stack_inputs=dict(a=(wtypes.uint64_wtype,)),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
            FunctionOpMapping(
                "gtxn",
                immediates=(ImmediateArgMapping("a", int), "VoteKeyDilution"),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.GTxn.type": (
            FunctionOpMapping(
                "gtxns",
                immediates=("Type",),
                stack_inputs=dict(a=(wtypes.uint64_wtype,)),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
            FunctionOpMapping(
                "gtxn",
                immediates=(ImmediateArgMapping("a", int), "Type"),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.GTxn.type_enum": (
            FunctionOpMapping(
                "gtxns",
                immediates=("TypeEnum",),
                stack_inputs=dict(a=(wtypes.uint64_wtype,)),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
            FunctionOpMapping(
                "gtxn",
                immediates=(ImmediateArgMapping("a", int), "TypeEnum"),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.GTxn.xfer_asset": (
            FunctionOpMapping(
                "gtxns",
                immediates=("XferAsset",),
                stack_inputs=dict(a=(wtypes.uint64_wtype,)),
                stack_outputs=(wtypes.asset_wtype,),
            ),
            FunctionOpMapping(
                "gtxn",
                immediates=(ImmediateArgMapping("a", int), "XferAsset"),
                stack_outputs=(wtypes.asset_wtype,),
            ),
        ),
        "algopy.op.GTxn.asset_amount": (
            FunctionOpMapping(
                "gtxns",
                immediates=("AssetAmount",),
                stack_inputs=dict(a=(wtypes.uint64_wtype,)),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
            FunctionOpMapping(
                "gtxn",
                immediates=(ImmediateArgMapping("a", int), "AssetAmount"),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.GTxn.asset_sender": (
            FunctionOpMapping(
                "gtxns",
                immediates=("AssetSender",),
                stack_inputs=dict(a=(wtypes.uint64_wtype,)),
                stack_outputs=(wtypes.account_wtype,),
            ),
            FunctionOpMapping(
                "gtxn",
                immediates=(ImmediateArgMapping("a", int), "AssetSender"),
                stack_outputs=(wtypes.account_wtype,),
            ),
        ),
        "algopy.op.GTxn.asset_receiver": (
            FunctionOpMapping(
                "gtxns",
                immediates=("AssetReceiver",),
                stack_inputs=dict(a=(wtypes.uint64_wtype,)),
                stack_outputs=(wtypes.account_wtype,),
            ),
            FunctionOpMapping(
                "gtxn",
                immediates=(ImmediateArgMapping("a", int), "AssetReceiver"),
                stack_outputs=(wtypes.account_wtype,),
            ),
        ),
        "algopy.op.GTxn.asset_close_to": (
            FunctionOpMapping(
                "gtxns",
                immediates=("AssetCloseTo",),
                stack_inputs=dict(a=(wtypes.uint64_wtype,)),
                stack_outputs=(wtypes.account_wtype,),
            ),
            FunctionOpMapping(
                "gtxn",
                immediates=(ImmediateArgMapping("a", int), "AssetCloseTo"),
                stack_outputs=(wtypes.account_wtype,),
            ),
        ),
        "algopy.op.GTxn.group_index": (
            FunctionOpMapping(
                "gtxns",
                immediates=("GroupIndex",),
                stack_inputs=dict(a=(wtypes.uint64_wtype,)),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
            FunctionOpMapping(
                "gtxn",
                immediates=(ImmediateArgMapping("a", int), "GroupIndex"),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.GTxn.tx_id": (
            FunctionOpMapping(
                "gtxns",
                immediates=("TxID",),
                stack_inputs=dict(a=(wtypes.uint64_wtype,)),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
            FunctionOpMapping(
                "gtxn",
                immediates=(ImmediateArgMapping("a", int), "TxID"),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.GTxn.application_id": (
            FunctionOpMapping(
                "gtxns",
                immediates=("ApplicationID",),
                stack_inputs=dict(a=(wtypes.uint64_wtype,)),
                stack_outputs=(wtypes.application_wtype,),
            ),
            FunctionOpMapping(
                "gtxn",
                immediates=(ImmediateArgMapping("a", int), "ApplicationID"),
                stack_outputs=(wtypes.application_wtype,),
            ),
        ),
        "algopy.op.GTxn.on_completion": (
            FunctionOpMapping(
                "gtxns",
                immediates=("OnCompletion",),
                stack_inputs=dict(a=(wtypes.uint64_wtype,)),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
            FunctionOpMapping(
                "gtxn",
                immediates=(ImmediateArgMapping("a", int), "OnCompletion"),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.GTxn.application_args": (
            FunctionOpMapping(
                "gtxnsas",
                immediates=("ApplicationArgs",),
                stack_inputs=dict(a=(wtypes.uint64_wtype,), b=(wtypes.uint64_wtype,)),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
            FunctionOpMapping(
                "gtxnsa",
                immediates=("ApplicationArgs", ImmediateArgMapping("b", int)),
                stack_inputs=dict(a=(wtypes.uint64_wtype,)),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
            FunctionOpMapping(
                "gtxna",
                immediates=(
                    ImmediateArgMapping("a", int),
                    "ApplicationArgs",
                    ImmediateArgMapping("b", int),
                ),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
            FunctionOpMapping(
                "gtxnas",
                immediates=(ImmediateArgMapping("a", int), "ApplicationArgs"),
                stack_inputs=dict(b=(wtypes.uint64_wtype,)),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.GTxn.num_app_args": (
            FunctionOpMapping(
                "gtxns",
                immediates=("NumAppArgs",),
                stack_inputs=dict(a=(wtypes.uint64_wtype,)),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
            FunctionOpMapping(
                "gtxn",
                immediates=(ImmediateArgMapping("a", int), "NumAppArgs"),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.GTxn.accounts": (
            FunctionOpMapping(
                "gtxnsas",
                immediates=("Accounts",),
                stack_inputs=dict(a=(wtypes.uint64_wtype,), b=(wtypes.uint64_wtype,)),
                stack_outputs=(wtypes.account_wtype,),
            ),
            FunctionOpMapping(
                "gtxnsa",
                immediates=("Accounts", ImmediateArgMapping("b", int)),
                stack_inputs=dict(a=(wtypes.uint64_wtype,)),
                stack_outputs=(wtypes.account_wtype,),
            ),
            FunctionOpMapping(
                "gtxna",
                immediates=(
                    ImmediateArgMapping("a", int),
                    "Accounts",
                    ImmediateArgMapping("b", int),
                ),
                stack_outputs=(wtypes.account_wtype,),
            ),
            FunctionOpMapping(
                "gtxnas",
                immediates=(ImmediateArgMapping("a", int), "Accounts"),
                stack_inputs=dict(b=(wtypes.uint64_wtype,)),
                stack_outputs=(wtypes.account_wtype,),
            ),
        ),
        "algopy.op.GTxn.num_accounts": (
            FunctionOpMapping(
                "gtxns",
                immediates=("NumAccounts",),
                stack_inputs=dict(a=(wtypes.uint64_wtype,)),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
            FunctionOpMapping(
                "gtxn",
                immediates=(ImmediateArgMapping("a", int), "NumAccounts"),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.GTxn.approval_program": (
            FunctionOpMapping(
                "gtxns",
                immediates=("ApprovalProgram",),
                stack_inputs=dict(a=(wtypes.uint64_wtype,)),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
            FunctionOpMapping(
                "gtxn",
                immediates=(ImmediateArgMapping("a", int), "ApprovalProgram"),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.GTxn.clear_state_program": (
            FunctionOpMapping(
                "gtxns",
                immediates=("ClearStateProgram",),
                stack_inputs=dict(a=(wtypes.uint64_wtype,)),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
            FunctionOpMapping(
                "gtxn",
                immediates=(ImmediateArgMapping("a", int), "ClearStateProgram"),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.GTxn.rekey_to": (
            FunctionOpMapping(
                "gtxns",
                immediates=("RekeyTo",),
                stack_inputs=dict(a=(wtypes.uint64_wtype,)),
                stack_outputs=(wtypes.account_wtype,),
            ),
            FunctionOpMapping(
                "gtxn",
                immediates=(ImmediateArgMapping("a", int), "RekeyTo"),
                stack_outputs=(wtypes.account_wtype,),
            ),
        ),
        "algopy.op.GTxn.config_asset": (
            FunctionOpMapping(
                "gtxns",
                immediates=("ConfigAsset",),
                stack_inputs=dict(a=(wtypes.uint64_wtype,)),
                stack_outputs=(wtypes.asset_wtype,),
            ),
            FunctionOpMapping(
                "gtxn",
                immediates=(ImmediateArgMapping("a", int), "ConfigAsset"),
                stack_outputs=(wtypes.asset_wtype,),
            ),
        ),
        "algopy.op.GTxn.config_asset_total": (
            FunctionOpMapping(
                "gtxns",
                immediates=("ConfigAssetTotal",),
                stack_inputs=dict(a=(wtypes.uint64_wtype,)),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
            FunctionOpMapping(
                "gtxn",
                immediates=(ImmediateArgMapping("a", int), "ConfigAssetTotal"),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.GTxn.config_asset_decimals": (
            FunctionOpMapping(
                "gtxns",
                immediates=("ConfigAssetDecimals",),
                stack_inputs=dict(a=(wtypes.uint64_wtype,)),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
            FunctionOpMapping(
                "gtxn",
                immediates=(ImmediateArgMapping("a", int), "ConfigAssetDecimals"),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.GTxn.config_asset_default_frozen": (
            FunctionOpMapping(
                "gtxns",
                immediates=("ConfigAssetDefaultFrozen",),
                stack_inputs=dict(a=(wtypes.uint64_wtype,)),
                stack_outputs=(wtypes.bool_wtype,),
            ),
            FunctionOpMapping(
                "gtxn",
                immediates=(ImmediateArgMapping("a", int), "ConfigAssetDefaultFrozen"),
                stack_outputs=(wtypes.bool_wtype,),
            ),
        ),
        "algopy.op.GTxn.config_asset_unit_name": (
            FunctionOpMapping(
                "gtxns",
                immediates=("ConfigAssetUnitName",),
                stack_inputs=dict(a=(wtypes.uint64_wtype,)),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
            FunctionOpMapping(
                "gtxn",
                immediates=(ImmediateArgMapping("a", int), "ConfigAssetUnitName"),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.GTxn.config_asset_name": (
            FunctionOpMapping(
                "gtxns",
                immediates=("ConfigAssetName",),
                stack_inputs=dict(a=(wtypes.uint64_wtype,)),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
            FunctionOpMapping(
                "gtxn",
                immediates=(ImmediateArgMapping("a", int), "ConfigAssetName"),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.GTxn.config_asset_url": (
            FunctionOpMapping(
                "gtxns",
                immediates=("ConfigAssetURL",),
                stack_inputs=dict(a=(wtypes.uint64_wtype,)),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
            FunctionOpMapping(
                "gtxn",
                immediates=(ImmediateArgMapping("a", int), "ConfigAssetURL"),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.GTxn.config_asset_metadata_hash": (
            FunctionOpMapping(
                "gtxns",
                immediates=("ConfigAssetMetadataHash",),
                stack_inputs=dict(a=(wtypes.uint64_wtype,)),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
            FunctionOpMapping(
                "gtxn",
                immediates=(ImmediateArgMapping("a", int), "ConfigAssetMetadataHash"),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.GTxn.config_asset_manager": (
            FunctionOpMapping(
                "gtxns",
                immediates=("ConfigAssetManager",),
                stack_inputs=dict(a=(wtypes.uint64_wtype,)),
                stack_outputs=(wtypes.account_wtype,),
            ),
            FunctionOpMapping(
                "gtxn",
                immediates=(ImmediateArgMapping("a", int), "ConfigAssetManager"),
                stack_outputs=(wtypes.account_wtype,),
            ),
        ),
        "algopy.op.GTxn.config_asset_reserve": (
            FunctionOpMapping(
                "gtxns",
                immediates=("ConfigAssetReserve",),
                stack_inputs=dict(a=(wtypes.uint64_wtype,)),
                stack_outputs=(wtypes.account_wtype,),
            ),
            FunctionOpMapping(
                "gtxn",
                immediates=(ImmediateArgMapping("a", int), "ConfigAssetReserve"),
                stack_outputs=(wtypes.account_wtype,),
            ),
        ),
        "algopy.op.GTxn.config_asset_freeze": (
            FunctionOpMapping(
                "gtxns",
                immediates=("ConfigAssetFreeze",),
                stack_inputs=dict(a=(wtypes.uint64_wtype,)),
                stack_outputs=(wtypes.account_wtype,),
            ),
            FunctionOpMapping(
                "gtxn",
                immediates=(ImmediateArgMapping("a", int), "ConfigAssetFreeze"),
                stack_outputs=(wtypes.account_wtype,),
            ),
        ),
        "algopy.op.GTxn.config_asset_clawback": (
            FunctionOpMapping(
                "gtxns",
                immediates=("ConfigAssetClawback",),
                stack_inputs=dict(a=(wtypes.uint64_wtype,)),
                stack_outputs=(wtypes.account_wtype,),
            ),
            FunctionOpMapping(
                "gtxn",
                immediates=(ImmediateArgMapping("a", int), "ConfigAssetClawback"),
                stack_outputs=(wtypes.account_wtype,),
            ),
        ),
        "algopy.op.GTxn.freeze_asset": (
            FunctionOpMapping(
                "gtxns",
                immediates=("FreezeAsset",),
                stack_inputs=dict(a=(wtypes.uint64_wtype,)),
                stack_outputs=(wtypes.asset_wtype,),
            ),
            FunctionOpMapping(
                "gtxn",
                immediates=(ImmediateArgMapping("a", int), "FreezeAsset"),
                stack_outputs=(wtypes.asset_wtype,),
            ),
        ),
        "algopy.op.GTxn.freeze_asset_account": (
            FunctionOpMapping(
                "gtxns",
                immediates=("FreezeAssetAccount",),
                stack_inputs=dict(a=(wtypes.uint64_wtype,)),
                stack_outputs=(wtypes.account_wtype,),
            ),
            FunctionOpMapping(
                "gtxn",
                immediates=(ImmediateArgMapping("a", int), "FreezeAssetAccount"),
                stack_outputs=(wtypes.account_wtype,),
            ),
        ),
        "algopy.op.GTxn.freeze_asset_frozen": (
            FunctionOpMapping(
                "gtxns",
                immediates=("FreezeAssetFrozen",),
                stack_inputs=dict(a=(wtypes.uint64_wtype,)),
                stack_outputs=(wtypes.bool_wtype,),
            ),
            FunctionOpMapping(
                "gtxn",
                immediates=(ImmediateArgMapping("a", int), "FreezeAssetFrozen"),
                stack_outputs=(wtypes.bool_wtype,),
            ),
        ),
        "algopy.op.GTxn.assets": (
            FunctionOpMapping(
                "gtxnsas",
                immediates=("Assets",),
                stack_inputs=dict(a=(wtypes.uint64_wtype,), b=(wtypes.uint64_wtype,)),
                stack_outputs=(wtypes.asset_wtype,),
            ),
            FunctionOpMapping(
                "gtxnsa",
                immediates=("Assets", ImmediateArgMapping("b", int)),
                stack_inputs=dict(a=(wtypes.uint64_wtype,)),
                stack_outputs=(wtypes.asset_wtype,),
            ),
            FunctionOpMapping(
                "gtxna",
                immediates=(
                    ImmediateArgMapping("a", int),
                    "Assets",
                    ImmediateArgMapping("b", int),
                ),
                stack_outputs=(wtypes.asset_wtype,),
            ),
            FunctionOpMapping(
                "gtxnas",
                immediates=(ImmediateArgMapping("a", int), "Assets"),
                stack_inputs=dict(b=(wtypes.uint64_wtype,)),
                stack_outputs=(wtypes.asset_wtype,),
            ),
        ),
        "algopy.op.GTxn.num_assets": (
            FunctionOpMapping(
                "gtxns",
                immediates=("NumAssets",),
                stack_inputs=dict(a=(wtypes.uint64_wtype,)),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
            FunctionOpMapping(
                "gtxn",
                immediates=(ImmediateArgMapping("a", int), "NumAssets"),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.GTxn.applications": (
            FunctionOpMapping(
                "gtxnsas",
                immediates=("Applications",),
                stack_inputs=dict(a=(wtypes.uint64_wtype,), b=(wtypes.uint64_wtype,)),
                stack_outputs=(wtypes.application_wtype,),
            ),
            FunctionOpMapping(
                "gtxnsa",
                immediates=("Applications", ImmediateArgMapping("b", int)),
                stack_inputs=dict(a=(wtypes.uint64_wtype,)),
                stack_outputs=(wtypes.application_wtype,),
            ),
            FunctionOpMapping(
                "gtxna",
                immediates=(
                    ImmediateArgMapping("a", int),
                    "Applications",
                    ImmediateArgMapping("b", int),
                ),
                stack_outputs=(wtypes.application_wtype,),
            ),
            FunctionOpMapping(
                "gtxnas",
                immediates=(ImmediateArgMapping("a", int), "Applications"),
                stack_inputs=dict(b=(wtypes.uint64_wtype,)),
                stack_outputs=(wtypes.application_wtype,),
            ),
        ),
        "algopy.op.GTxn.num_applications": (
            FunctionOpMapping(
                "gtxns",
                immediates=("NumApplications",),
                stack_inputs=dict(a=(wtypes.uint64_wtype,)),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
            FunctionOpMapping(
                "gtxn",
                immediates=(ImmediateArgMapping("a", int), "NumApplications"),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.GTxn.global_num_uint": (
            FunctionOpMapping(
                "gtxns",
                immediates=("GlobalNumUint",),
                stack_inputs=dict(a=(wtypes.uint64_wtype,)),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
            FunctionOpMapping(
                "gtxn",
                immediates=(ImmediateArgMapping("a", int), "GlobalNumUint"),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.GTxn.global_num_byte_slice": (
            FunctionOpMapping(
                "gtxns",
                immediates=("GlobalNumByteSlice",),
                stack_inputs=dict(a=(wtypes.uint64_wtype,)),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
            FunctionOpMapping(
                "gtxn",
                immediates=(ImmediateArgMapping("a", int), "GlobalNumByteSlice"),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.GTxn.local_num_uint": (
            FunctionOpMapping(
                "gtxns",
                immediates=("LocalNumUint",),
                stack_inputs=dict(a=(wtypes.uint64_wtype,)),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
            FunctionOpMapping(
                "gtxn",
                immediates=(ImmediateArgMapping("a", int), "LocalNumUint"),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.GTxn.local_num_byte_slice": (
            FunctionOpMapping(
                "gtxns",
                immediates=("LocalNumByteSlice",),
                stack_inputs=dict(a=(wtypes.uint64_wtype,)),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
            FunctionOpMapping(
                "gtxn",
                immediates=(ImmediateArgMapping("a", int), "LocalNumByteSlice"),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.GTxn.extra_program_pages": (
            FunctionOpMapping(
                "gtxns",
                immediates=("ExtraProgramPages",),
                stack_inputs=dict(a=(wtypes.uint64_wtype,)),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
            FunctionOpMapping(
                "gtxn",
                immediates=(ImmediateArgMapping("a", int), "ExtraProgramPages"),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.GTxn.nonparticipation": (
            FunctionOpMapping(
                "gtxns",
                immediates=("Nonparticipation",),
                stack_inputs=dict(a=(wtypes.uint64_wtype,)),
                stack_outputs=(wtypes.bool_wtype,),
            ),
            FunctionOpMapping(
                "gtxn",
                immediates=(ImmediateArgMapping("a", int), "Nonparticipation"),
                stack_outputs=(wtypes.bool_wtype,),
            ),
        ),
        "algopy.op.GTxn.logs": (
            FunctionOpMapping(
                "gtxnsas",
                immediates=("Logs",),
                stack_inputs=dict(a=(wtypes.uint64_wtype,), b=(wtypes.uint64_wtype,)),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
            FunctionOpMapping(
                "gtxnsa",
                immediates=("Logs", ImmediateArgMapping("b", int)),
                stack_inputs=dict(a=(wtypes.uint64_wtype,)),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
            FunctionOpMapping(
                "gtxna",
                immediates=(ImmediateArgMapping("a", int), "Logs", ImmediateArgMapping("b", int)),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
            FunctionOpMapping(
                "gtxnas",
                immediates=(ImmediateArgMapping("a", int), "Logs"),
                stack_inputs=dict(b=(wtypes.uint64_wtype,)),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.GTxn.num_logs": (
            FunctionOpMapping(
                "gtxns",
                immediates=("NumLogs",),
                stack_inputs=dict(a=(wtypes.uint64_wtype,)),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
            FunctionOpMapping(
                "gtxn",
                immediates=(ImmediateArgMapping("a", int), "NumLogs"),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.GTxn.created_asset_id": (
            FunctionOpMapping(
                "gtxns",
                immediates=("CreatedAssetID",),
                stack_inputs=dict(a=(wtypes.uint64_wtype,)),
                stack_outputs=(wtypes.asset_wtype,),
            ),
            FunctionOpMapping(
                "gtxn",
                immediates=(ImmediateArgMapping("a", int), "CreatedAssetID"),
                stack_outputs=(wtypes.asset_wtype,),
            ),
        ),
        "algopy.op.GTxn.created_application_id": (
            FunctionOpMapping(
                "gtxns",
                immediates=("CreatedApplicationID",),
                stack_inputs=dict(a=(wtypes.uint64_wtype,)),
                stack_outputs=(wtypes.application_wtype,),
            ),
            FunctionOpMapping(
                "gtxn",
                immediates=(ImmediateArgMapping("a", int), "CreatedApplicationID"),
                stack_outputs=(wtypes.application_wtype,),
            ),
        ),
        "algopy.op.GTxn.last_log": (
            FunctionOpMapping(
                "gtxns",
                immediates=("LastLog",),
                stack_inputs=dict(a=(wtypes.uint64_wtype,)),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
            FunctionOpMapping(
                "gtxn",
                immediates=(ImmediateArgMapping("a", int), "LastLog"),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.GTxn.state_proof_pk": (
            FunctionOpMapping(
                "gtxns",
                immediates=("StateProofPK",),
                stack_inputs=dict(a=(wtypes.uint64_wtype,)),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
            FunctionOpMapping(
                "gtxn",
                immediates=(ImmediateArgMapping("a", int), "StateProofPK"),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.GTxn.approval_program_pages": (
            FunctionOpMapping(
                "gtxnsas",
                immediates=("ApprovalProgramPages",),
                stack_inputs=dict(a=(wtypes.uint64_wtype,), b=(wtypes.uint64_wtype,)),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
            FunctionOpMapping(
                "gtxnsa",
                immediates=("ApprovalProgramPages", ImmediateArgMapping("b", int)),
                stack_inputs=dict(a=(wtypes.uint64_wtype,)),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
            FunctionOpMapping(
                "gtxna",
                immediates=(
                    ImmediateArgMapping("a", int),
                    "ApprovalProgramPages",
                    ImmediateArgMapping("b", int),
                ),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
            FunctionOpMapping(
                "gtxnas",
                immediates=(ImmediateArgMapping("a", int), "ApprovalProgramPages"),
                stack_inputs=dict(b=(wtypes.uint64_wtype,)),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.GTxn.num_approval_program_pages": (
            FunctionOpMapping(
                "gtxns",
                immediates=("NumApprovalProgramPages",),
                stack_inputs=dict(a=(wtypes.uint64_wtype,)),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
            FunctionOpMapping(
                "gtxn",
                immediates=(ImmediateArgMapping("a", int), "NumApprovalProgramPages"),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.GTxn.clear_state_program_pages": (
            FunctionOpMapping(
                "gtxnsas",
                immediates=("ClearStateProgramPages",),
                stack_inputs=dict(a=(wtypes.uint64_wtype,), b=(wtypes.uint64_wtype,)),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
            FunctionOpMapping(
                "gtxnsa",
                immediates=("ClearStateProgramPages", ImmediateArgMapping("b", int)),
                stack_inputs=dict(a=(wtypes.uint64_wtype,)),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
            FunctionOpMapping(
                "gtxna",
                immediates=(
                    ImmediateArgMapping("a", int),
                    "ClearStateProgramPages",
                    ImmediateArgMapping("b", int),
                ),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
            FunctionOpMapping(
                "gtxnas",
                immediates=(ImmediateArgMapping("a", int), "ClearStateProgramPages"),
                stack_inputs=dict(b=(wtypes.uint64_wtype,)),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.GTxn.num_clear_state_program_pages": (
            FunctionOpMapping(
                "gtxns",
                immediates=("NumClearStateProgramPages",),
                stack_inputs=dict(a=(wtypes.uint64_wtype,)),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
            FunctionOpMapping(
                "gtxn",
                immediates=(ImmediateArgMapping("a", int), "NumClearStateProgramPages"),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.Global.min_txn_fee": (
            FunctionOpMapping(
                "global",
                immediates=("MinTxnFee",),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.Global.min_balance": (
            FunctionOpMapping(
                "global",
                immediates=("MinBalance",),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.Global.max_txn_life": (
            FunctionOpMapping(
                "global",
                immediates=("MaxTxnLife",),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.Global.zero_address": (
            FunctionOpMapping(
                "global",
                immediates=("ZeroAddress",),
                stack_outputs=(wtypes.account_wtype,),
            ),
        ),
        "algopy.op.Global.group_size": (
            FunctionOpMapping(
                "global",
                immediates=("GroupSize",),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.Global.logic_sig_version": (
            FunctionOpMapping(
                "global",
                immediates=("LogicSigVersion",),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.Global.round": (
            FunctionOpMapping(
                "global",
                immediates=("Round",),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.Global.latest_timestamp": (
            FunctionOpMapping(
                "global",
                immediates=("LatestTimestamp",),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.Global.current_application_id": (
            FunctionOpMapping(
                "global",
                immediates=("CurrentApplicationID",),
                stack_outputs=(wtypes.application_wtype,),
            ),
        ),
        "algopy.op.Global.creator_address": (
            FunctionOpMapping(
                "global",
                immediates=("CreatorAddress",),
                stack_outputs=(wtypes.account_wtype,),
            ),
        ),
        "algopy.op.Global.current_application_address": (
            FunctionOpMapping(
                "global",
                immediates=("CurrentApplicationAddress",),
                stack_outputs=(wtypes.account_wtype,),
            ),
        ),
        "algopy.op.Global.group_id": (
            FunctionOpMapping(
                "global",
                immediates=("GroupID",),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.Global.opcode_budget": (
            FunctionOpMapping(
                "global",
                immediates=("OpcodeBudget",),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.Global.caller_application_id": (
            FunctionOpMapping(
                "global",
                immediates=("CallerApplicationID",),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.Global.caller_application_address": (
            FunctionOpMapping(
                "global",
                immediates=("CallerApplicationAddress",),
                stack_outputs=(wtypes.account_wtype,),
            ),
        ),
        "algopy.op.Global.asset_create_min_balance": (
            FunctionOpMapping(
                "global",
                immediates=("AssetCreateMinBalance",),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.Global.asset_opt_in_min_balance": (
            FunctionOpMapping(
                "global",
                immediates=("AssetOptInMinBalance",),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.Global.genesis_hash": (
            FunctionOpMapping(
                "global",
                immediates=("GenesisHash",),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.ITxn.sender": (
            FunctionOpMapping(
                "itxn",
                immediates=("Sender",),
                stack_outputs=(wtypes.account_wtype,),
            ),
        ),
        "algopy.op.ITxn.fee": (
            FunctionOpMapping(
                "itxn",
                immediates=("Fee",),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.ITxn.first_valid": (
            FunctionOpMapping(
                "itxn",
                immediates=("FirstValid",),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.ITxn.first_valid_time": (
            FunctionOpMapping(
                "itxn",
                immediates=("FirstValidTime",),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.ITxn.last_valid": (
            FunctionOpMapping(
                "itxn",
                immediates=("LastValid",),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.ITxn.note": (
            FunctionOpMapping(
                "itxn",
                immediates=("Note",),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.ITxn.lease": (
            FunctionOpMapping(
                "itxn",
                immediates=("Lease",),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.ITxn.receiver": (
            FunctionOpMapping(
                "itxn",
                immediates=("Receiver",),
                stack_outputs=(wtypes.account_wtype,),
            ),
        ),
        "algopy.op.ITxn.amount": (
            FunctionOpMapping(
                "itxn",
                immediates=("Amount",),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.ITxn.close_remainder_to": (
            FunctionOpMapping(
                "itxn",
                immediates=("CloseRemainderTo",),
                stack_outputs=(wtypes.account_wtype,),
            ),
        ),
        "algopy.op.ITxn.vote_pk": (
            FunctionOpMapping(
                "itxn",
                immediates=("VotePK",),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.ITxn.selection_pk": (
            FunctionOpMapping(
                "itxn",
                immediates=("SelectionPK",),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.ITxn.vote_first": (
            FunctionOpMapping(
                "itxn",
                immediates=("VoteFirst",),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.ITxn.vote_last": (
            FunctionOpMapping(
                "itxn",
                immediates=("VoteLast",),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.ITxn.vote_key_dilution": (
            FunctionOpMapping(
                "itxn",
                immediates=("VoteKeyDilution",),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.ITxn.type": (
            FunctionOpMapping(
                "itxn",
                immediates=("Type",),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.ITxn.type_enum": (
            FunctionOpMapping(
                "itxn",
                immediates=("TypeEnum",),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.ITxn.xfer_asset": (
            FunctionOpMapping(
                "itxn",
                immediates=("XferAsset",),
                stack_outputs=(wtypes.asset_wtype,),
            ),
        ),
        "algopy.op.ITxn.asset_amount": (
            FunctionOpMapping(
                "itxn",
                immediates=("AssetAmount",),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.ITxn.asset_sender": (
            FunctionOpMapping(
                "itxn",
                immediates=("AssetSender",),
                stack_outputs=(wtypes.account_wtype,),
            ),
        ),
        "algopy.op.ITxn.asset_receiver": (
            FunctionOpMapping(
                "itxn",
                immediates=("AssetReceiver",),
                stack_outputs=(wtypes.account_wtype,),
            ),
        ),
        "algopy.op.ITxn.asset_close_to": (
            FunctionOpMapping(
                "itxn",
                immediates=("AssetCloseTo",),
                stack_outputs=(wtypes.account_wtype,),
            ),
        ),
        "algopy.op.ITxn.group_index": (
            FunctionOpMapping(
                "itxn",
                immediates=("GroupIndex",),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.ITxn.tx_id": (
            FunctionOpMapping(
                "itxn",
                immediates=("TxID",),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.ITxn.application_id": (
            FunctionOpMapping(
                "itxn",
                immediates=("ApplicationID",),
                stack_outputs=(wtypes.application_wtype,),
            ),
        ),
        "algopy.op.ITxn.on_completion": (
            FunctionOpMapping(
                "itxn",
                immediates=("OnCompletion",),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.ITxn.application_args": (
            FunctionOpMapping(
                "itxnas",
                immediates=("ApplicationArgs",),
                stack_inputs=dict(a=(wtypes.uint64_wtype,)),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
            FunctionOpMapping(
                "itxna",
                immediates=("ApplicationArgs", ImmediateArgMapping("a", int)),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.ITxn.num_app_args": (
            FunctionOpMapping(
                "itxn",
                immediates=("NumAppArgs",),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.ITxn.accounts": (
            FunctionOpMapping(
                "itxnas",
                immediates=("Accounts",),
                stack_inputs=dict(a=(wtypes.uint64_wtype,)),
                stack_outputs=(wtypes.account_wtype,),
            ),
            FunctionOpMapping(
                "itxna",
                immediates=("Accounts", ImmediateArgMapping("a", int)),
                stack_outputs=(wtypes.account_wtype,),
            ),
        ),
        "algopy.op.ITxn.num_accounts": (
            FunctionOpMapping(
                "itxn",
                immediates=("NumAccounts",),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.ITxn.approval_program": (
            FunctionOpMapping(
                "itxn",
                immediates=("ApprovalProgram",),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.ITxn.clear_state_program": (
            FunctionOpMapping(
                "itxn",
                immediates=("ClearStateProgram",),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.ITxn.rekey_to": (
            FunctionOpMapping(
                "itxn",
                immediates=("RekeyTo",),
                stack_outputs=(wtypes.account_wtype,),
            ),
        ),
        "algopy.op.ITxn.config_asset": (
            FunctionOpMapping(
                "itxn",
                immediates=("ConfigAsset",),
                stack_outputs=(wtypes.asset_wtype,),
            ),
        ),
        "algopy.op.ITxn.config_asset_total": (
            FunctionOpMapping(
                "itxn",
                immediates=("ConfigAssetTotal",),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.ITxn.config_asset_decimals": (
            FunctionOpMapping(
                "itxn",
                immediates=("ConfigAssetDecimals",),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.ITxn.config_asset_default_frozen": (
            FunctionOpMapping(
                "itxn",
                immediates=("ConfigAssetDefaultFrozen",),
                stack_outputs=(wtypes.bool_wtype,),
            ),
        ),
        "algopy.op.ITxn.config_asset_unit_name": (
            FunctionOpMapping(
                "itxn",
                immediates=("ConfigAssetUnitName",),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.ITxn.config_asset_name": (
            FunctionOpMapping(
                "itxn",
                immediates=("ConfigAssetName",),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.ITxn.config_asset_url": (
            FunctionOpMapping(
                "itxn",
                immediates=("ConfigAssetURL",),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.ITxn.config_asset_metadata_hash": (
            FunctionOpMapping(
                "itxn",
                immediates=("ConfigAssetMetadataHash",),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.ITxn.config_asset_manager": (
            FunctionOpMapping(
                "itxn",
                immediates=("ConfigAssetManager",),
                stack_outputs=(wtypes.account_wtype,),
            ),
        ),
        "algopy.op.ITxn.config_asset_reserve": (
            FunctionOpMapping(
                "itxn",
                immediates=("ConfigAssetReserve",),
                stack_outputs=(wtypes.account_wtype,),
            ),
        ),
        "algopy.op.ITxn.config_asset_freeze": (
            FunctionOpMapping(
                "itxn",
                immediates=("ConfigAssetFreeze",),
                stack_outputs=(wtypes.account_wtype,),
            ),
        ),
        "algopy.op.ITxn.config_asset_clawback": (
            FunctionOpMapping(
                "itxn",
                immediates=("ConfigAssetClawback",),
                stack_outputs=(wtypes.account_wtype,),
            ),
        ),
        "algopy.op.ITxn.freeze_asset": (
            FunctionOpMapping(
                "itxn",
                immediates=("FreezeAsset",),
                stack_outputs=(wtypes.asset_wtype,),
            ),
        ),
        "algopy.op.ITxn.freeze_asset_account": (
            FunctionOpMapping(
                "itxn",
                immediates=("FreezeAssetAccount",),
                stack_outputs=(wtypes.account_wtype,),
            ),
        ),
        "algopy.op.ITxn.freeze_asset_frozen": (
            FunctionOpMapping(
                "itxn",
                immediates=("FreezeAssetFrozen",),
                stack_outputs=(wtypes.bool_wtype,),
            ),
        ),
        "algopy.op.ITxn.assets": (
            FunctionOpMapping(
                "itxnas",
                immediates=("Assets",),
                stack_inputs=dict(a=(wtypes.uint64_wtype,)),
                stack_outputs=(wtypes.asset_wtype,),
            ),
            FunctionOpMapping(
                "itxna",
                immediates=("Assets", ImmediateArgMapping("a", int)),
                stack_outputs=(wtypes.asset_wtype,),
            ),
        ),
        "algopy.op.ITxn.num_assets": (
            FunctionOpMapping(
                "itxn",
                immediates=("NumAssets",),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.ITxn.applications": (
            FunctionOpMapping(
                "itxnas",
                immediates=("Applications",),
                stack_inputs=dict(a=(wtypes.uint64_wtype,)),
                stack_outputs=(wtypes.application_wtype,),
            ),
            FunctionOpMapping(
                "itxna",
                immediates=("Applications", ImmediateArgMapping("a", int)),
                stack_outputs=(wtypes.application_wtype,),
            ),
        ),
        "algopy.op.ITxn.num_applications": (
            FunctionOpMapping(
                "itxn",
                immediates=("NumApplications",),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.ITxn.global_num_uint": (
            FunctionOpMapping(
                "itxn",
                immediates=("GlobalNumUint",),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.ITxn.global_num_byte_slice": (
            FunctionOpMapping(
                "itxn",
                immediates=("GlobalNumByteSlice",),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.ITxn.local_num_uint": (
            FunctionOpMapping(
                "itxn",
                immediates=("LocalNumUint",),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.ITxn.local_num_byte_slice": (
            FunctionOpMapping(
                "itxn",
                immediates=("LocalNumByteSlice",),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.ITxn.extra_program_pages": (
            FunctionOpMapping(
                "itxn",
                immediates=("ExtraProgramPages",),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.ITxn.nonparticipation": (
            FunctionOpMapping(
                "itxn",
                immediates=("Nonparticipation",),
                stack_outputs=(wtypes.bool_wtype,),
            ),
        ),
        "algopy.op.ITxn.logs": (
            FunctionOpMapping(
                "itxnas",
                immediates=("Logs",),
                stack_inputs=dict(a=(wtypes.uint64_wtype,)),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
            FunctionOpMapping(
                "itxna",
                immediates=("Logs", ImmediateArgMapping("a", int)),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.ITxn.num_logs": (
            FunctionOpMapping(
                "itxn",
                immediates=("NumLogs",),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.ITxn.created_asset_id": (
            FunctionOpMapping(
                "itxn",
                immediates=("CreatedAssetID",),
                stack_outputs=(wtypes.asset_wtype,),
            ),
        ),
        "algopy.op.ITxn.created_application_id": (
            FunctionOpMapping(
                "itxn",
                immediates=("CreatedApplicationID",),
                stack_outputs=(wtypes.application_wtype,),
            ),
        ),
        "algopy.op.ITxn.last_log": (
            FunctionOpMapping(
                "itxn",
                immediates=("LastLog",),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.ITxn.state_proof_pk": (
            FunctionOpMapping(
                "itxn",
                immediates=("StateProofPK",),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.ITxn.approval_program_pages": (
            FunctionOpMapping(
                "itxnas",
                immediates=("ApprovalProgramPages",),
                stack_inputs=dict(a=(wtypes.uint64_wtype,)),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
            FunctionOpMapping(
                "itxna",
                immediates=("ApprovalProgramPages", ImmediateArgMapping("a", int)),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.ITxn.num_approval_program_pages": (
            FunctionOpMapping(
                "itxn",
                immediates=("NumApprovalProgramPages",),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.ITxn.clear_state_program_pages": (
            FunctionOpMapping(
                "itxnas",
                immediates=("ClearStateProgramPages",),
                stack_inputs=dict(a=(wtypes.uint64_wtype,)),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
            FunctionOpMapping(
                "itxna",
                immediates=("ClearStateProgramPages", ImmediateArgMapping("a", int)),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.ITxn.num_clear_state_program_pages": (
            FunctionOpMapping(
                "itxn",
                immediates=("NumClearStateProgramPages",),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.ITxnCreate.begin": (
            FunctionOpMapping(
                "itxn_begin",
            ),
        ),
        "algopy.op.ITxnCreate.next": (
            FunctionOpMapping(
                "itxn_next",
            ),
        ),
        "algopy.op.ITxnCreate.submit": (
            FunctionOpMapping(
                "itxn_submit",
            ),
        ),
        "algopy.op.ITxnCreate.set_sender": (
            FunctionOpMapping(
                "itxn_field",
                immediates=("Sender",),
                stack_inputs=dict(a=(wtypes.account_wtype,)),
            ),
        ),
        "algopy.op.ITxnCreate.set_fee": (
            FunctionOpMapping(
                "itxn_field",
                immediates=("Fee",),
                stack_inputs=dict(a=(wtypes.uint64_wtype,)),
            ),
        ),
        "algopy.op.ITxnCreate.set_note": (
            FunctionOpMapping(
                "itxn_field",
                immediates=("Note",),
                stack_inputs=dict(a=(wtypes.bytes_wtype,)),
            ),
        ),
        "algopy.op.ITxnCreate.set_receiver": (
            FunctionOpMapping(
                "itxn_field",
                immediates=("Receiver",),
                stack_inputs=dict(a=(wtypes.account_wtype,)),
            ),
        ),
        "algopy.op.ITxnCreate.set_amount": (
            FunctionOpMapping(
                "itxn_field",
                immediates=("Amount",),
                stack_inputs=dict(a=(wtypes.uint64_wtype,)),
            ),
        ),
        "algopy.op.ITxnCreate.set_close_remainder_to": (
            FunctionOpMapping(
                "itxn_field",
                immediates=("CloseRemainderTo",),
                stack_inputs=dict(a=(wtypes.account_wtype,)),
            ),
        ),
        "algopy.op.ITxnCreate.set_vote_pk": (
            FunctionOpMapping(
                "itxn_field",
                immediates=("VotePK",),
                stack_inputs=dict(a=(wtypes.bytes_wtype,)),
            ),
        ),
        "algopy.op.ITxnCreate.set_selection_pk": (
            FunctionOpMapping(
                "itxn_field",
                immediates=("SelectionPK",),
                stack_inputs=dict(a=(wtypes.bytes_wtype,)),
            ),
        ),
        "algopy.op.ITxnCreate.set_vote_first": (
            FunctionOpMapping(
                "itxn_field",
                immediates=("VoteFirst",),
                stack_inputs=dict(a=(wtypes.uint64_wtype,)),
            ),
        ),
        "algopy.op.ITxnCreate.set_vote_last": (
            FunctionOpMapping(
                "itxn_field",
                immediates=("VoteLast",),
                stack_inputs=dict(a=(wtypes.uint64_wtype,)),
            ),
        ),
        "algopy.op.ITxnCreate.set_vote_key_dilution": (
            FunctionOpMapping(
                "itxn_field",
                immediates=("VoteKeyDilution",),
                stack_inputs=dict(a=(wtypes.uint64_wtype,)),
            ),
        ),
        "algopy.op.ITxnCreate.set_type": (
            FunctionOpMapping(
                "itxn_field",
                immediates=("Type",),
                stack_inputs=dict(a=(wtypes.bytes_wtype,)),
            ),
        ),
        "algopy.op.ITxnCreate.set_type_enum": (
            FunctionOpMapping(
                "itxn_field",
                immediates=("TypeEnum",),
                stack_inputs=dict(a=(wtypes.uint64_wtype,)),
            ),
        ),
        "algopy.op.ITxnCreate.set_xfer_asset": (
            FunctionOpMapping(
                "itxn_field",
                immediates=("XferAsset",),
                stack_inputs=dict(a=(wtypes.asset_wtype, wtypes.uint64_wtype)),
            ),
        ),
        "algopy.op.ITxnCreate.set_asset_amount": (
            FunctionOpMapping(
                "itxn_field",
                immediates=("AssetAmount",),
                stack_inputs=dict(a=(wtypes.uint64_wtype,)),
            ),
        ),
        "algopy.op.ITxnCreate.set_asset_sender": (
            FunctionOpMapping(
                "itxn_field",
                immediates=("AssetSender",),
                stack_inputs=dict(a=(wtypes.account_wtype,)),
            ),
        ),
        "algopy.op.ITxnCreate.set_asset_receiver": (
            FunctionOpMapping(
                "itxn_field",
                immediates=("AssetReceiver",),
                stack_inputs=dict(a=(wtypes.account_wtype,)),
            ),
        ),
        "algopy.op.ITxnCreate.set_asset_close_to": (
            FunctionOpMapping(
                "itxn_field",
                immediates=("AssetCloseTo",),
                stack_inputs=dict(a=(wtypes.account_wtype,)),
            ),
        ),
        "algopy.op.ITxnCreate.set_application_id": (
            FunctionOpMapping(
                "itxn_field",
                immediates=("ApplicationID",),
                stack_inputs=dict(a=(wtypes.application_wtype, wtypes.uint64_wtype)),
            ),
        ),
        "algopy.op.ITxnCreate.set_on_completion": (
            FunctionOpMapping(
                "itxn_field",
                immediates=("OnCompletion",),
                stack_inputs=dict(a=(wtypes.uint64_wtype,)),
            ),
        ),
        "algopy.op.ITxnCreate.set_application_args": (
            FunctionOpMapping(
                "itxn_field",
                immediates=("ApplicationArgs",),
                stack_inputs=dict(a=(wtypes.bytes_wtype,)),
            ),
        ),
        "algopy.op.ITxnCreate.set_accounts": (
            FunctionOpMapping(
                "itxn_field",
                immediates=("Accounts",),
                stack_inputs=dict(a=(wtypes.account_wtype,)),
            ),
        ),
        "algopy.op.ITxnCreate.set_approval_program": (
            FunctionOpMapping(
                "itxn_field",
                immediates=("ApprovalProgram",),
                stack_inputs=dict(a=(wtypes.bytes_wtype,)),
            ),
        ),
        "algopy.op.ITxnCreate.set_clear_state_program": (
            FunctionOpMapping(
                "itxn_field",
                immediates=("ClearStateProgram",),
                stack_inputs=dict(a=(wtypes.bytes_wtype,)),
            ),
        ),
        "algopy.op.ITxnCreate.set_rekey_to": (
            FunctionOpMapping(
                "itxn_field",
                immediates=("RekeyTo",),
                stack_inputs=dict(a=(wtypes.account_wtype,)),
            ),
        ),
        "algopy.op.ITxnCreate.set_config_asset": (
            FunctionOpMapping(
                "itxn_field",
                immediates=("ConfigAsset",),
                stack_inputs=dict(a=(wtypes.asset_wtype, wtypes.uint64_wtype)),
            ),
        ),
        "algopy.op.ITxnCreate.set_config_asset_total": (
            FunctionOpMapping(
                "itxn_field",
                immediates=("ConfigAssetTotal",),
                stack_inputs=dict(a=(wtypes.uint64_wtype,)),
            ),
        ),
        "algopy.op.ITxnCreate.set_config_asset_decimals": (
            FunctionOpMapping(
                "itxn_field",
                immediates=("ConfigAssetDecimals",),
                stack_inputs=dict(a=(wtypes.uint64_wtype,)),
            ),
        ),
        "algopy.op.ITxnCreate.set_config_asset_default_frozen": (
            FunctionOpMapping(
                "itxn_field",
                immediates=("ConfigAssetDefaultFrozen",),
                stack_inputs=dict(a=(wtypes.bool_wtype, wtypes.uint64_wtype)),
            ),
        ),
        "algopy.op.ITxnCreate.set_config_asset_unit_name": (
            FunctionOpMapping(
                "itxn_field",
                immediates=("ConfigAssetUnitName",),
                stack_inputs=dict(a=(wtypes.bytes_wtype,)),
            ),
        ),
        "algopy.op.ITxnCreate.set_config_asset_name": (
            FunctionOpMapping(
                "itxn_field",
                immediates=("ConfigAssetName",),
                stack_inputs=dict(a=(wtypes.bytes_wtype,)),
            ),
        ),
        "algopy.op.ITxnCreate.set_config_asset_url": (
            FunctionOpMapping(
                "itxn_field",
                immediates=("ConfigAssetURL",),
                stack_inputs=dict(a=(wtypes.bytes_wtype,)),
            ),
        ),
        "algopy.op.ITxnCreate.set_config_asset_metadata_hash": (
            FunctionOpMapping(
                "itxn_field",
                immediates=("ConfigAssetMetadataHash",),
                stack_inputs=dict(a=(wtypes.bytes_wtype,)),
            ),
        ),
        "algopy.op.ITxnCreate.set_config_asset_manager": (
            FunctionOpMapping(
                "itxn_field",
                immediates=("ConfigAssetManager",),
                stack_inputs=dict(a=(wtypes.account_wtype,)),
            ),
        ),
        "algopy.op.ITxnCreate.set_config_asset_reserve": (
            FunctionOpMapping(
                "itxn_field",
                immediates=("ConfigAssetReserve",),
                stack_inputs=dict(a=(wtypes.account_wtype,)),
            ),
        ),
        "algopy.op.ITxnCreate.set_config_asset_freeze": (
            FunctionOpMapping(
                "itxn_field",
                immediates=("ConfigAssetFreeze",),
                stack_inputs=dict(a=(wtypes.account_wtype,)),
            ),
        ),
        "algopy.op.ITxnCreate.set_config_asset_clawback": (
            FunctionOpMapping(
                "itxn_field",
                immediates=("ConfigAssetClawback",),
                stack_inputs=dict(a=(wtypes.account_wtype,)),
            ),
        ),
        "algopy.op.ITxnCreate.set_freeze_asset": (
            FunctionOpMapping(
                "itxn_field",
                immediates=("FreezeAsset",),
                stack_inputs=dict(a=(wtypes.asset_wtype, wtypes.uint64_wtype)),
            ),
        ),
        "algopy.op.ITxnCreate.set_freeze_asset_account": (
            FunctionOpMapping(
                "itxn_field",
                immediates=("FreezeAssetAccount",),
                stack_inputs=dict(a=(wtypes.account_wtype,)),
            ),
        ),
        "algopy.op.ITxnCreate.set_freeze_asset_frozen": (
            FunctionOpMapping(
                "itxn_field",
                immediates=("FreezeAssetFrozen",),
                stack_inputs=dict(a=(wtypes.bool_wtype, wtypes.uint64_wtype)),
            ),
        ),
        "algopy.op.ITxnCreate.set_assets": (
            FunctionOpMapping(
                "itxn_field",
                immediates=("Assets",),
                stack_inputs=dict(a=(wtypes.uint64_wtype,)),
            ),
        ),
        "algopy.op.ITxnCreate.set_applications": (
            FunctionOpMapping(
                "itxn_field",
                immediates=("Applications",),
                stack_inputs=dict(a=(wtypes.uint64_wtype,)),
            ),
        ),
        "algopy.op.ITxnCreate.set_global_num_uint": (
            FunctionOpMapping(
                "itxn_field",
                immediates=("GlobalNumUint",),
                stack_inputs=dict(a=(wtypes.uint64_wtype,)),
            ),
        ),
        "algopy.op.ITxnCreate.set_global_num_byte_slice": (
            FunctionOpMapping(
                "itxn_field",
                immediates=("GlobalNumByteSlice",),
                stack_inputs=dict(a=(wtypes.uint64_wtype,)),
            ),
        ),
        "algopy.op.ITxnCreate.set_local_num_uint": (
            FunctionOpMapping(
                "itxn_field",
                immediates=("LocalNumUint",),
                stack_inputs=dict(a=(wtypes.uint64_wtype,)),
            ),
        ),
        "algopy.op.ITxnCreate.set_local_num_byte_slice": (
            FunctionOpMapping(
                "itxn_field",
                immediates=("LocalNumByteSlice",),
                stack_inputs=dict(a=(wtypes.uint64_wtype,)),
            ),
        ),
        "algopy.op.ITxnCreate.set_extra_program_pages": (
            FunctionOpMapping(
                "itxn_field",
                immediates=("ExtraProgramPages",),
                stack_inputs=dict(a=(wtypes.uint64_wtype,)),
            ),
        ),
        "algopy.op.ITxnCreate.set_nonparticipation": (
            FunctionOpMapping(
                "itxn_field",
                immediates=("Nonparticipation",),
                stack_inputs=dict(a=(wtypes.bool_wtype, wtypes.uint64_wtype)),
            ),
        ),
        "algopy.op.ITxnCreate.set_state_proof_pk": (
            FunctionOpMapping(
                "itxn_field",
                immediates=("StateProofPK",),
                stack_inputs=dict(a=(wtypes.bytes_wtype,)),
            ),
        ),
        "algopy.op.ITxnCreate.set_approval_program_pages": (
            FunctionOpMapping(
                "itxn_field",
                immediates=("ApprovalProgramPages",),
                stack_inputs=dict(a=(wtypes.bytes_wtype,)),
            ),
        ),
        "algopy.op.ITxnCreate.set_clear_state_program_pages": (
            FunctionOpMapping(
                "itxn_field",
                immediates=("ClearStateProgramPages",),
                stack_inputs=dict(a=(wtypes.bytes_wtype,)),
            ),
        ),
        "algopy.op.JsonRef.json_string": (
            FunctionOpMapping(
                "json_ref",
                immediates=("JSONString",),
                stack_inputs=dict(a=(wtypes.bytes_wtype,), b=(wtypes.bytes_wtype,)),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.JsonRef.json_uint64": (
            FunctionOpMapping(
                "json_ref",
                immediates=("JSONUint64",),
                stack_inputs=dict(a=(wtypes.bytes_wtype,), b=(wtypes.bytes_wtype,)),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.JsonRef.json_object": (
            FunctionOpMapping(
                "json_ref",
                immediates=("JSONObject",),
                stack_inputs=dict(a=(wtypes.bytes_wtype,), b=(wtypes.bytes_wtype,)),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.Scratch.load_bytes": (
            FunctionOpMapping(
                "loads",
                stack_inputs=dict(a=(wtypes.uint64_wtype,)),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.Scratch.load_uint64": (
            FunctionOpMapping(
                "loads",
                stack_inputs=dict(a=(wtypes.uint64_wtype,)),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.Scratch.store": (
            FunctionOpMapping(
                "stores",
                stack_inputs=dict(
                    a=(wtypes.uint64_wtype,), b=(wtypes.bytes_wtype, wtypes.uint64_wtype)
                ),
            ),
        ),
        "algopy.op.Txn.sender": (
            FunctionOpMapping(
                "txn",
                immediates=("Sender",),
                stack_outputs=(wtypes.account_wtype,),
            ),
        ),
        "algopy.op.Txn.fee": (
            FunctionOpMapping(
                "txn",
                immediates=("Fee",),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.Txn.first_valid": (
            FunctionOpMapping(
                "txn",
                immediates=("FirstValid",),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.Txn.first_valid_time": (
            FunctionOpMapping(
                "txn",
                immediates=("FirstValidTime",),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.Txn.last_valid": (
            FunctionOpMapping(
                "txn",
                immediates=("LastValid",),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.Txn.note": (
            FunctionOpMapping(
                "txn",
                immediates=("Note",),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.Txn.lease": (
            FunctionOpMapping(
                "txn",
                immediates=("Lease",),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.Txn.receiver": (
            FunctionOpMapping(
                "txn",
                immediates=("Receiver",),
                stack_outputs=(wtypes.account_wtype,),
            ),
        ),
        "algopy.op.Txn.amount": (
            FunctionOpMapping(
                "txn",
                immediates=("Amount",),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.Txn.close_remainder_to": (
            FunctionOpMapping(
                "txn",
                immediates=("CloseRemainderTo",),
                stack_outputs=(wtypes.account_wtype,),
            ),
        ),
        "algopy.op.Txn.vote_pk": (
            FunctionOpMapping(
                "txn",
                immediates=("VotePK",),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.Txn.selection_pk": (
            FunctionOpMapping(
                "txn",
                immediates=("SelectionPK",),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.Txn.vote_first": (
            FunctionOpMapping(
                "txn",
                immediates=("VoteFirst",),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.Txn.vote_last": (
            FunctionOpMapping(
                "txn",
                immediates=("VoteLast",),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.Txn.vote_key_dilution": (
            FunctionOpMapping(
                "txn",
                immediates=("VoteKeyDilution",),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.Txn.type": (
            FunctionOpMapping(
                "txn",
                immediates=("Type",),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.Txn.type_enum": (
            FunctionOpMapping(
                "txn",
                immediates=("TypeEnum",),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.Txn.xfer_asset": (
            FunctionOpMapping(
                "txn",
                immediates=("XferAsset",),
                stack_outputs=(wtypes.asset_wtype,),
            ),
        ),
        "algopy.op.Txn.asset_amount": (
            FunctionOpMapping(
                "txn",
                immediates=("AssetAmount",),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.Txn.asset_sender": (
            FunctionOpMapping(
                "txn",
                immediates=("AssetSender",),
                stack_outputs=(wtypes.account_wtype,),
            ),
        ),
        "algopy.op.Txn.asset_receiver": (
            FunctionOpMapping(
                "txn",
                immediates=("AssetReceiver",),
                stack_outputs=(wtypes.account_wtype,),
            ),
        ),
        "algopy.op.Txn.asset_close_to": (
            FunctionOpMapping(
                "txn",
                immediates=("AssetCloseTo",),
                stack_outputs=(wtypes.account_wtype,),
            ),
        ),
        "algopy.op.Txn.group_index": (
            FunctionOpMapping(
                "txn",
                immediates=("GroupIndex",),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.Txn.tx_id": (
            FunctionOpMapping(
                "txn",
                immediates=("TxID",),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.Txn.application_id": (
            FunctionOpMapping(
                "txn",
                immediates=("ApplicationID",),
                stack_outputs=(wtypes.application_wtype,),
            ),
        ),
        "algopy.op.Txn.on_completion": (
            FunctionOpMapping(
                "txn",
                immediates=("OnCompletion",),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.Txn.application_args": (
            FunctionOpMapping(
                "txnas",
                immediates=("ApplicationArgs",),
                stack_inputs=dict(a=(wtypes.uint64_wtype,)),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
            FunctionOpMapping(
                "txna",
                immediates=("ApplicationArgs", ImmediateArgMapping("a", int)),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.Txn.num_app_args": (
            FunctionOpMapping(
                "txn",
                immediates=("NumAppArgs",),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.Txn.accounts": (
            FunctionOpMapping(
                "txnas",
                immediates=("Accounts",),
                stack_inputs=dict(a=(wtypes.uint64_wtype,)),
                stack_outputs=(wtypes.account_wtype,),
            ),
            FunctionOpMapping(
                "txna",
                immediates=("Accounts", ImmediateArgMapping("a", int)),
                stack_outputs=(wtypes.account_wtype,),
            ),
        ),
        "algopy.op.Txn.num_accounts": (
            FunctionOpMapping(
                "txn",
                immediates=("NumAccounts",),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.Txn.approval_program": (
            FunctionOpMapping(
                "txn",
                immediates=("ApprovalProgram",),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.Txn.clear_state_program": (
            FunctionOpMapping(
                "txn",
                immediates=("ClearStateProgram",),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.Txn.rekey_to": (
            FunctionOpMapping(
                "txn",
                immediates=("RekeyTo",),
                stack_outputs=(wtypes.account_wtype,),
            ),
        ),
        "algopy.op.Txn.config_asset": (
            FunctionOpMapping(
                "txn",
                immediates=("ConfigAsset",),
                stack_outputs=(wtypes.asset_wtype,),
            ),
        ),
        "algopy.op.Txn.config_asset_total": (
            FunctionOpMapping(
                "txn",
                immediates=("ConfigAssetTotal",),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.Txn.config_asset_decimals": (
            FunctionOpMapping(
                "txn",
                immediates=("ConfigAssetDecimals",),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.Txn.config_asset_default_frozen": (
            FunctionOpMapping(
                "txn",
                immediates=("ConfigAssetDefaultFrozen",),
                stack_outputs=(wtypes.bool_wtype,),
            ),
        ),
        "algopy.op.Txn.config_asset_unit_name": (
            FunctionOpMapping(
                "txn",
                immediates=("ConfigAssetUnitName",),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.Txn.config_asset_name": (
            FunctionOpMapping(
                "txn",
                immediates=("ConfigAssetName",),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.Txn.config_asset_url": (
            FunctionOpMapping(
                "txn",
                immediates=("ConfigAssetURL",),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.Txn.config_asset_metadata_hash": (
            FunctionOpMapping(
                "txn",
                immediates=("ConfigAssetMetadataHash",),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.Txn.config_asset_manager": (
            FunctionOpMapping(
                "txn",
                immediates=("ConfigAssetManager",),
                stack_outputs=(wtypes.account_wtype,),
            ),
        ),
        "algopy.op.Txn.config_asset_reserve": (
            FunctionOpMapping(
                "txn",
                immediates=("ConfigAssetReserve",),
                stack_outputs=(wtypes.account_wtype,),
            ),
        ),
        "algopy.op.Txn.config_asset_freeze": (
            FunctionOpMapping(
                "txn",
                immediates=("ConfigAssetFreeze",),
                stack_outputs=(wtypes.account_wtype,),
            ),
        ),
        "algopy.op.Txn.config_asset_clawback": (
            FunctionOpMapping(
                "txn",
                immediates=("ConfigAssetClawback",),
                stack_outputs=(wtypes.account_wtype,),
            ),
        ),
        "algopy.op.Txn.freeze_asset": (
            FunctionOpMapping(
                "txn",
                immediates=("FreezeAsset",),
                stack_outputs=(wtypes.asset_wtype,),
            ),
        ),
        "algopy.op.Txn.freeze_asset_account": (
            FunctionOpMapping(
                "txn",
                immediates=("FreezeAssetAccount",),
                stack_outputs=(wtypes.account_wtype,),
            ),
        ),
        "algopy.op.Txn.freeze_asset_frozen": (
            FunctionOpMapping(
                "txn",
                immediates=("FreezeAssetFrozen",),
                stack_outputs=(wtypes.bool_wtype,),
            ),
        ),
        "algopy.op.Txn.assets": (
            FunctionOpMapping(
                "txnas",
                immediates=("Assets",),
                stack_inputs=dict(a=(wtypes.uint64_wtype,)),
                stack_outputs=(wtypes.asset_wtype,),
            ),
            FunctionOpMapping(
                "txna",
                immediates=("Assets", ImmediateArgMapping("a", int)),
                stack_outputs=(wtypes.asset_wtype,),
            ),
        ),
        "algopy.op.Txn.num_assets": (
            FunctionOpMapping(
                "txn",
                immediates=("NumAssets",),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.Txn.applications": (
            FunctionOpMapping(
                "txnas",
                immediates=("Applications",),
                stack_inputs=dict(a=(wtypes.uint64_wtype,)),
                stack_outputs=(wtypes.application_wtype,),
            ),
            FunctionOpMapping(
                "txna",
                immediates=("Applications", ImmediateArgMapping("a", int)),
                stack_outputs=(wtypes.application_wtype,),
            ),
        ),
        "algopy.op.Txn.num_applications": (
            FunctionOpMapping(
                "txn",
                immediates=("NumApplications",),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.Txn.global_num_uint": (
            FunctionOpMapping(
                "txn",
                immediates=("GlobalNumUint",),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.Txn.global_num_byte_slice": (
            FunctionOpMapping(
                "txn",
                immediates=("GlobalNumByteSlice",),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.Txn.local_num_uint": (
            FunctionOpMapping(
                "txn",
                immediates=("LocalNumUint",),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.Txn.local_num_byte_slice": (
            FunctionOpMapping(
                "txn",
                immediates=("LocalNumByteSlice",),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.Txn.extra_program_pages": (
            FunctionOpMapping(
                "txn",
                immediates=("ExtraProgramPages",),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.Txn.nonparticipation": (
            FunctionOpMapping(
                "txn",
                immediates=("Nonparticipation",),
                stack_outputs=(wtypes.bool_wtype,),
            ),
        ),
        "algopy.op.Txn.logs": (
            FunctionOpMapping(
                "txnas",
                immediates=("Logs",),
                stack_inputs=dict(a=(wtypes.uint64_wtype,)),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
            FunctionOpMapping(
                "txna",
                immediates=("Logs", ImmediateArgMapping("a", int)),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.Txn.num_logs": (
            FunctionOpMapping(
                "txn",
                immediates=("NumLogs",),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.Txn.created_asset_id": (
            FunctionOpMapping(
                "txn",
                immediates=("CreatedAssetID",),
                stack_outputs=(wtypes.asset_wtype,),
            ),
        ),
        "algopy.op.Txn.created_application_id": (
            FunctionOpMapping(
                "txn",
                immediates=("CreatedApplicationID",),
                stack_outputs=(wtypes.application_wtype,),
            ),
        ),
        "algopy.op.Txn.last_log": (
            FunctionOpMapping(
                "txn",
                immediates=("LastLog",),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.Txn.state_proof_pk": (
            FunctionOpMapping(
                "txn",
                immediates=("StateProofPK",),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.Txn.approval_program_pages": (
            FunctionOpMapping(
                "txnas",
                immediates=("ApprovalProgramPages",),
                stack_inputs=dict(a=(wtypes.uint64_wtype,)),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
            FunctionOpMapping(
                "txna",
                immediates=("ApprovalProgramPages", ImmediateArgMapping("a", int)),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.Txn.num_approval_program_pages": (
            FunctionOpMapping(
                "txn",
                immediates=("NumApprovalProgramPages",),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
        "algopy.op.Txn.clear_state_program_pages": (
            FunctionOpMapping(
                "txnas",
                immediates=("ClearStateProgramPages",),
                stack_inputs=dict(a=(wtypes.uint64_wtype,)),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
            FunctionOpMapping(
                "txna",
                immediates=("ClearStateProgramPages", ImmediateArgMapping("a", int)),
                stack_outputs=(wtypes.bytes_wtype,),
            ),
        ),
        "algopy.op.Txn.num_clear_state_program_pages": (
            FunctionOpMapping(
                "txn",
                immediates=("NumClearStateProgramPages",),
                stack_outputs=(wtypes.uint64_wtype,),
            ),
        ),
    }
)
