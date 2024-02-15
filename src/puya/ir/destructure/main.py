from pathlib import Path

import structlog

from puya.context import CompileContext
from puya.ir import models
from puya.ir.destructure.coalesce_locals import coalesce_locals
from puya.ir.destructure.optimize import post_ssa_optimizer
from puya.ir.destructure.parcopy import sequentialize_parallel_copies
from puya.ir.destructure.remove_phi import convert_contract_to_cssa, remove_phi_nodes
from puya.ir.to_text_visitor import output_contract_ir_to_path

logger = structlog.get_logger(__name__)


def destructure_ssa(
    context: CompileContext, contract_ir: models.Contract, contract_ir_base_path: Path
) -> models.Contract:
    contract_ir = convert_contract_to_cssa(context, contract_ir)
    if context.options.output_destructured_ir:
        output_contract_ir_to_path(contract_ir, contract_ir_base_path.with_suffix(".d1-cssa.ir"))
    contract_ir = remove_phi_nodes(context, contract_ir)
    if context.options.output_destructured_ir:
        output_contract_ir_to_path(
            contract_ir, contract_ir_base_path.with_suffix(".d2-phi_gone.ir")
        )
    contract_ir = sequentialize_parallel_copies(context, contract_ir)
    if context.options.output_destructured_ir:
        output_contract_ir_to_path(
            contract_ir, contract_ir_base_path.with_suffix(".d3-phi_gone_seq.ir")
        )
    contract_ir = coalesce_locals(context, contract_ir)
    if context.options.output_destructured_ir:
        output_contract_ir_to_path(
            contract_ir, contract_ir_base_path.with_suffix(".d4-coalesced.ir")
        )
    if context.options.optimization_level > 0:
        contract_ir = post_ssa_optimizer(context, contract_ir)
    return contract_ir
