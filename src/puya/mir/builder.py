import typing
from collections.abc import Mapping

import attrs

from puya import log
from puya.algo_constants import MAX_APP_PAGE_SIZE
from puya.errors import CodeError, InternalError
from puya.ir import models as ir
from puya.ir.types_ import AVMBytesEncoding
from puya.ir.visitor import IRVisitor
from puya.mir import models
from puya.mir.context import ProgramMIRContext
from puya.models import CompiledReferenceField
from puya.parse import SourceLocation
from puya.utils import Address, biguint_bytes_eval, sha512_256_hash

logger = log.get_logger(__name__)


@attrs.define
class MemoryIRBuilder(IRVisitor[None]):
    context: ProgramMIRContext = attrs.field(on_setattr=attrs.setters.frozen)
    current_subroutine: ir.Subroutine
    is_main: bool
    current_ops: list[models.BaseOp] = attrs.field(factory=list)
    active_op: ir.Op | ir.ControlOp | None = None
    next_block: ir.BasicBlock | None = None

    def _add_op(self, op: models.BaseOp) -> None:
        self.current_ops.append(op)

    def _get_block_name(self, block: ir.BasicBlock) -> str:
        assert block in self.current_subroutine.body
        comment = (block.comment or "block").replace(" ", "_")
        subroutine_name = self.context.subroutine_names[self.current_subroutine]
        return f"{subroutine_name}_{comment}@{block.id}"

    def visit_assignment(self, ass: ir.Assignment) -> None:
        ass.source.accept(self)
        # right most target is top of stack
        for target in reversed(ass.targets):
            try:
                param_idx = self.current_subroutine.parameters.index(target)
            except ValueError:
                self._add_op(
                    models.StoreVirtual(
                        local_id=target.local_id,
                        source_location=ass.source_location,
                        atype=target.atype,
                    )
                )
            else:
                index = param_idx - len(self.current_subroutine.parameters)
                self._add_op(
                    models.StoreParam(
                        local_id=target.local_id,
                        index=index,
                        source_location=ass.source_location,
                        atype=target.atype,
                    )
                )

    def visit_register(self, reg: ir.Register) -> None:
        try:
            param_idx = self.current_subroutine.parameters.index(reg)
        except ValueError:
            self._add_op(
                models.LoadVirtual(
                    local_id=reg.local_id,
                    source_location=(self.active_op or reg).source_location,
                    atype=reg.atype,
                )
            )
        else:
            index = param_idx - len(self.current_subroutine.parameters)
            self._add_op(
                models.LoadParam(
                    local_id=reg.local_id,
                    index=index,
                    source_location=(self.active_op or reg).source_location,
                    atype=reg.atype,
                )
            )

    def visit_template_var(self, deploy_var: ir.TemplateVar) -> None:
        self._add_op(
            models.PushTemplateVar(
                name=deploy_var.name,
                atype=deploy_var.atype,
                source_location=deploy_var.source_location,
            )
        )

    def visit_uint64_constant(self, const: ir.UInt64Constant) -> None:
        self._add_op(
            models.PushInt(
                const.value if not const.teal_alias else const.teal_alias,
                source_location=const.source_location,
            )
        )

    def visit_biguint_constant(self, const: ir.BigUIntConstant) -> None:
        big_uint_bytes = biguint_bytes_eval(const.value)
        self._add_op(
            models.PushBytes(
                big_uint_bytes,
                source_location=const.source_location,
                comment=str(const.value),
                encoding=AVMBytesEncoding.base16,
            )
        )

    def visit_bytes_constant(self, const: ir.BytesConstant) -> None:
        self._add_op(
            models.PushBytes(
                const.value, encoding=const.encoding, source_location=const.source_location
            )
        )

    def visit_address_constant(self, const: ir.AddressConstant) -> None:
        self._add_op(
            models.PushAddress(
                const.value,
                source_location=const.source_location,
            )
        )

    def visit_method_constant(self, const: ir.MethodConstant) -> None:
        self._add_op(
            models.PushMethod(
                const.value,
                source_location=const.source_location,
            )
        )

    def visit_compiled_reference(self, const: ir.CompiledReference) -> None:
        match const.field:
            case CompiledReferenceField.approval | CompiledReferenceField.clear_state:
                program_id = f"{const.artifact}.{const.field.name}"
                program = _assemble_program_bytes(
                    self.context, program_id, const.template_variables, const.source_location
                )
                self._add_op(
                    models.PushBytes(
                        value=program,
                        encoding=AVMBytesEncoding.base64,
                        source_location=const.source_location,
                    )
                )
            case CompiledReferenceField.account:
                program = _assemble_program_bytes(
                    self.context, const.artifact, const.template_variables, const.source_location
                )
                address_public_key = sha512_256_hash(b"Program" + program)
                self._add_op(
                    models.PushAddress(
                        value=Address.from_public_key(address_public_key).address,
                        source_location=const.source_location,
                    )
                )
            case CompiledReferenceField.extra_program_pages:
                total_bytes = 0
                for field in (CompiledReferenceField.approval, CompiledReferenceField.clear_state):
                    program_id = f"{const.artifact}.{field.name}"
                    program = _assemble_program_bytes(
                        self.context, program_id, const.template_variables, const.source_location
                    )
                    total_bytes += len(program)
                extra_pages = (total_bytes - 1) // MAX_APP_PAGE_SIZE
                self._add_op(
                    models.PushInt(
                        value=extra_pages,
                        source_location=const.source_location,
                    )
                )
            case (
                CompiledReferenceField.global_uints
                | CompiledReferenceField.global_bytes
                | CompiledReferenceField.local_uints
                | CompiledReferenceField.local_bytes
            ) as state_field:
                total = _get_state_total(
                    self.context, const.artifact, state_field, const.source_location
                )
                self._add_op(
                    models.PushInt(
                        value=total,
                        source_location=const.source_location,
                    )
                )
            case _:
                typing.assert_never(const.field)

    def visit_intrinsic_op(self, intrinsic: ir.Intrinsic) -> None:
        discard_results = intrinsic is self.active_op
        for arg in intrinsic.args:
            arg.accept(self)
        produces = len(intrinsic.op_signature.returns)
        self._add_op(
            models.IntrinsicOp(
                op_code=intrinsic.op.code,
                immediates=intrinsic.immediates,
                source_location=intrinsic.source_location,
                consumes=len(intrinsic.op_signature.args),
                produces=produces,
                comment=intrinsic.comment,
            )
        )
        if discard_results and produces:
            self._add_op(models.Pop(produces))

    def visit_invoke_subroutine(self, callsub: ir.InvokeSubroutine) -> None:
        discard_results = callsub is self.active_op
        target = callsub.target

        callsub_op = models.CallSub(
            target=self.context.subroutine_names[target],
            parameters=len(target.parameters),
            returns=len(target.returns),
            source_location=callsub.source_location,
        )

        # prepare args
        for arg in callsub.args:
            arg.accept(self)

        # call sub
        self._add_op(callsub_op)

        if discard_results and target.returns:
            num_returns = len(target.returns)
            self._add_op(models.Pop(num_returns))

    def visit_conditional_branch(self, branch: ir.ConditionalBranch) -> None:
        branch.condition.accept(self)
        if self.next_block is branch.zero:
            other = branch.zero
            self._add_op(
                models.BranchNonZero(
                    immediates=[self._get_block_name(branch.non_zero)],
                    source_location=branch.source_location,
                )
            )
        else:
            other = branch.non_zero
            self._add_op(
                models.BranchZero(
                    immediates=[self._get_block_name(branch.zero)],
                    source_location=branch.source_location,
                )
            )
        self._add_op(
            models.Branch(
                immediates=[self._get_block_name(other)], source_location=branch.source_location
            )
        )

    def visit_goto(self, goto: ir.Goto) -> None:
        self._add_op(
            models.Branch(
                immediates=[self._get_block_name(goto.target)],
                source_location=goto.source_location,
            )
        )

    def visit_goto_nth(self, goto_nth: ir.GotoNth) -> None:
        block_labels = [self._get_block_name(block) for block in goto_nth.blocks]
        goto_nth.value.accept(self)
        self._add_op(
            models.Switch(immediates=block_labels, source_location=goto_nth.source_location)
        )
        goto_nth.default.accept(self)

    def visit_switch(self, switch: ir.Switch) -> None:
        blocks = list[str]()
        for case, block in switch.cases.items():
            case.accept(self)
            block_name = self._get_block_name(block)
            blocks.append(block_name)
        switch.value.accept(self)

        self._add_op(models.Match(immediates=blocks, source_location=switch.source_location))
        switch.default.accept(self)

    def visit_subroutine_return(self, retsub: ir.SubroutineReturn) -> None:
        for r in retsub.result:
            r.accept(self)
        self._add_op(
            models.IntrinsicOp(
                op_code="return",
                source_location=retsub.source_location,
                consumes=len(retsub.result),
                produces=0,
            )
            if self.is_main
            else models.RetSub(source_location=retsub.source_location, returns=len(retsub.result))
        )

    def visit_program_exit(self, exit_: ir.ProgramExit) -> None:
        exit_.result.accept(self)
        self._add_op(
            models.IntrinsicOp(
                op_code="return",
                source_location=exit_.source_location,
                consumes=0,
                produces=0,
            )
        )

    def visit_fail(self, fail: ir.Fail) -> None:
        self._add_op(
            models.IntrinsicOp(
                op_code="err",
                comment=fail.comment,
                source_location=fail.source_location,
                consumes=0,
                produces=0,
            )
        )

    def lower_block_to_teal(
        self, block: ir.BasicBlock, next_block: ir.BasicBlock | None
    ) -> models.MemoryBasicBlock:
        self.next_block = next_block
        self.current_ops = list[models.BaseOp]()
        for op in block.all_ops:
            assert not isinstance(op, ir.Phi)
            self.active_op = op
            op.accept(self)
        if (
            next_block is not None
            and self.current_ops
            and isinstance((last_op := self.current_ops[-1]), models.IntrinsicOp)
            and last_op.op_code == "b"
            and last_op.immediates[0] == (next_block_name := self._get_block_name(next_block))
        ):
            self.current_ops[-1] = models.Comment(
                f"Implicit fall through to {next_block_name}",
                source_location=last_op.source_location,
            )

        block_name = self._get_block_name(block)
        predecessors = [self._get_block_name(b) for b in block.predecessors]
        successors = [self._get_block_name(b) for b in block.successors]
        return models.MemoryBasicBlock(
            block_name=block_name,
            ops=self.current_ops,
            predecessors=predecessors,
            successors=successors,
            source_location=block.source_location,
        )

    def visit_value_tuple(self, tup: ir.ValueTuple) -> None:
        _unexpected_node(tup)

    def visit_itxn_constant(self, const: ir.ITxnConstant) -> None:
        _unexpected_node(const)

    def visit_inner_transaction_field(self, field: ir.InnerTransactionField) -> None:
        _unexpected_node(field)

    def visit_phi(self, phi: ir.Phi) -> None:
        _unexpected_node(phi)

    def visit_phi_argument(self, arg: ir.PhiArgument) -> None:
        _unexpected_node(arg)


def _unexpected_node(node: ir.IRVisitable) -> typing.Never:
    raise InternalError(
        f"Encountered node of type {type(node).__name__!r} during codegen"
        f" - should have been eliminated in prior stages",
        node.source_location,
    )


def _get_state_total(
    context: ProgramMIRContext,
    contract: str,
    field: typing.Literal[
        CompiledReferenceField.global_uints,
        CompiledReferenceField.global_bytes,
        CompiledReferenceField.local_uints,
        CompiledReferenceField.local_bytes,
    ],
    loc: SourceLocation | None,
) -> int:
    try:
        contract_ir = context.all_contracts[contract]
    except KeyError as ex:
        raise InternalError(f"Unknown contract reference: {contract}", loc) from ex
    totals = contract_ir.metadata.state_totals
    total = attrs.asdict(totals).get(field.name)
    if not isinstance(total, int):
        raise InternalError(f"Invalid state total field: {field.name}", loc)
    return total


def _assemble_program_bytes(
    context: ProgramMIRContext,
    program_id: str,
    template_vars: Mapping[str, int | bytes],
    loc: SourceLocation | None,
) -> bytes:
    from puya.mir.main import program_ir_to_mir
    from puya.teal.main import mir_to_teal
    from puya.ussemble.main import assemble_program, get_template_vars

    try:
        program_ir = context.all_programs[program_id]
    except KeyError as ex:
        raise CodeError(f"Unknown program reference: {program_id}", loc) from ex

    try:
        program_index = context.current_assembles.index(program_id)
    except ValueError:
        pass
    else:
        chain = " -> ".join(context.current_assembles[program_index:] + [program_id])
        raise CodeError(f"Self referencing program cycle detected: {chain}", loc)
    context.current_assembles.append(program_id)
    context = attrs.evolve(
        context,
        options=attrs.evolve(
            context.options,
            output_teal=False,
            output_memory_ir=False,
            output_bytecode=False,
        ),
    )
    program_mir = program_ir_to_mir(context, program_ir, None)
    program_teal = mir_to_teal(context, program_mir)
    template_vars = {
        **get_template_vars(context),
        **template_vars,
    }
    context.current_assembles.pop()
    return assemble_program(context, program_teal, template_vars).bytecode
