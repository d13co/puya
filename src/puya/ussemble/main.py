import contextlib
from collections.abc import Iterable, Mapping
from pathlib import Path

import attrs

from puya.context import CompileContext
from puya.errors import PuyaError
from puya.parse import SourceLocation
from puya.teal import models as teal
from puya.ussemble.build import lower_ops
from puya.ussemble.context import AssembleContext
from puya.ussemble.optimize import optimize_ops
from puya.ussemble.output import AssembleVisitor
from puya.ussemble.validate import validate_labels
from puya.utils import attrs_extend


@attrs.frozen
class AssembledProgram:
    bytecode: bytes
    source_map: dict[int, SourceLocation]


def assemble_program(
    ctx: CompileContext, program: teal.TealProgram, template_variables: Mapping[str, int | bytes]
) -> AssembledProgram:
    assemble_ctx = attrs_extend(
        AssembleContext,
        ctx,
        template_variables=template_variables,
    )
    avm_ops = lower_ops(assemble_ctx, program)
    validate_labels(avm_ops)
    avm_ops = optimize_ops(assemble_ctx, avm_ops)

    return AssembledProgram(
        bytecode=AssembleVisitor.assemble(assemble_ctx, avm_ops),
        source_map={},
    )


def get_template_vars(context: CompileContext) -> Mapping[str, int | bytes]:
    options = context.options
    return {
        **_load_template_vars(options.template_vars_path),
        **_parse_template_vars(options.template_vars),
    }


def _load_template_vars(path: Path | None) -> Mapping[str, int | bytes]:
    if path is None:
        return {}
    return _parse_template_vars(
        line for line in path.read_text().splitlines() if not line.strip().startswith("#")
    )


def _parse_template_vars(template_vars: Iterable[str]) -> dict[str, int | bytes]:
    return dict(map(_parse_template_var, template_vars))


def _parse_template_var(var: str) -> tuple[str, int | bytes]:
    value: int | bytes | None = None
    try:
        name, value_str = var.split("=", maxsplit=1)
    except ValueError:
        name = None
    else:
        if value_str.startswith('"') and value_str.endswith('"'):
            value = value_str[1:-1].encode("utf8")
        elif value_str.startswith("0x"):
            with contextlib.suppress(ValueError):
                value = bytes.fromhex(value_str[2:])
        elif value_str and value_str[0].isdigit():
            with contextlib.suppress(ValueError):
                value = int(value_str)
    if value is None or name is None:
        raise PuyaError(f"Invalid template var definition: {var}")
    return name, value
