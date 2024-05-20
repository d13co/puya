import typing

from puya.errors import CodeError, InternalError
from puya.models import OnCompletionAction, TransactionType
from puya.teal import models as teal
from puya.ussemble import models
from puya.ussemble.context import AssembleContext
from puya.utils import Address, sha512_256_hash

TEAL_ALIASES = {
    **{e.name: e.value for e in OnCompletionAction},
    **{e.name: e.value for e in TransactionType},
}


def lower_ops(ctx: AssembleContext, program: teal.TealProgram) -> list[models.Node]:
    avm_ops = list[models.Node]()
    for subroutine in program.all_subroutines:
        for block in subroutine.blocks:
            avm_ops.append(models.Label(name=block.label))
            for op in block.ops:
                avm_op = lower_op(ctx, op)
                avm_ops.append(avm_op)
    return avm_ops


def lower_op(ctx: AssembleContext, op: teal.TealOp) -> models.AVMOp:
    match op:
        case teal.Int(value=int(int_value)):
            return models.PushInt(int_value)
        case teal.Int(value=str(int_alias)):
            try:
                int_value = TEAL_ALIASES[int_alias]
            except KeyError as ex:
                raise InternalError(f"Unknown teal alias: {int_alias}", op.source_location) from ex
            return models.PushInt(int_value)
        case teal.Byte(value=bytes_value):
            return models.PushBytes(bytes_value)
        case teal.Method(value=method_value):
            bytes_value = sha512_256_hash(method_value.encode("utf8"))[:4]
            return models.PushBytes(bytes_value)
        case teal.Address(value=address_value, source_location=loc):
            address = Address.parse(address_value)
            if not address.is_valid:
                raise InternalError(f"Invalid address literal: {address_value}", loc)
            return models.PushBytes(address.public_key)
        case teal.TemplateVar(name=name, op_code=op_code, source_location=loc):
            try:
                value = ctx.template_variables[name]
            except KeyError as ex:
                raise CodeError(f"Template value not defined: {name}", loc) from ex
            else:
                match value, op_code:
                    case int(int_value), "int":
                        return models.PushInt(int_value)
                    case bytes(byte_value), "byte":
                        return models.PushBytes(byte_value)
                    case _:
                        raise CodeError(f"Invalid template value type: {name}", loc)
        case teal.CallSub(target=label_id, op_code=op_code):
            return models.Jump(op_code=op_code, label=models.Label(name=label_id))
        case teal.TealOp(
            op_code="b" | "bz" | "bnz" as op_code, immediates=immediates, source_location=loc
        ):
            try:
                (maybe_label_id,) = immediates
            except ValueError:
                maybe_label_id = None
            if not isinstance(maybe_label_id, str):
                raise InternalError(
                    f"Invalid op code: {op.teal()}",
                    loc,
                )
            return models.Jump(op_code=op_code, label=models.Label(name=maybe_label_id))
        case teal.TealOp(
            op_code="switch" | "match" as op_code,
            immediates=immediates,
            source_location=loc,
        ):
            labels = list[str]()
            for maybe_label in immediates:
                if not isinstance(maybe_label, str):
                    raise InternalError(
                        f"Invalid op code: {op.teal()}",
                        loc,
                    )
                labels.append(maybe_label)
            return models.MultiJump(
                op_code=op_code,
                labels=[models.Label(label) for label in labels],
            )
        case teal.TealOp(op_code=op_code, immediates=immediates):
            return models.Intrinsic(op_code=op_code, immediates=immediates)
        case _:
            typing.assert_never()
