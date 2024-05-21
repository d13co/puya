import copy
from collections.abc import Iterable

import algosdk.error
import pytest
from _pytest.mark import ParameterSet
from algokit_utils import Program
from algosdk.v2client.algod import AlgodClient
from puya.context import CompileContext
from puya.ir.types_ import AVMBytesEncoding
from puya.models import CompiledContract, CompiledLogicSignature
from puya.options import PuyaOptions
from puya.teal.models import Byte, Int, TealProgram, TemplateVar
from puya.teal.output import emit_teal
from puya.ussemble.main import assemble_program
from puya.ussemble.template import get_template_vars

from tests.utils import (
    PuyaExample,
    compile_src_from_options,
    get_all_examples,
)


def get_test_cases() -> Iterable[ParameterSet]:
    for example in get_all_examples():
        marks = [pytest.mark.localnet]
        if example.name == "stress_tests":
            marks.append(pytest.mark.slow)
        yield ParameterSet.param(example, marks=marks, id=example.id)


def pytest_generate_tests(metafunc: pytest.Metafunc) -> None:
    metafunc.parametrize("case", get_test_cases())


@pytest.mark.parametrize("optimization_level", [0, 1, 2])
def test_assemble_matches_algod(
    algod_client: AlgodClient, case: PuyaExample, optimization_level: int
) -> None:
    compile_result = compile_src_from_options(
        PuyaOptions(
            paths=(case.path,),
            optimization_level=optimization_level,
            template_vars_path=case.template_vars_path,
            debug_level=0,
            output_teal=False,
            output_arc32=False,
            match_algod_bytecode=True,
        )
    )
    for artifacts in compile_result.teal.values():
        for artifact in artifacts:
            match artifact:
                case CompiledContract(approval_program=approval, clear_program=clear):
                    assemble_and_compare_program(
                        compile_result.context,
                        algod_client,
                        approval,
                        f"{artifact.metadata.name}-approval",
                    )
                    assemble_and_compare_program(
                        compile_result.context,
                        algod_client,
                        clear,
                        f"{artifact.metadata.name}-clear",
                    )
                case CompiledLogicSignature(program=logic_sig):
                    assemble_and_compare_program(
                        compile_result.context,
                        algod_client,
                        logic_sig,
                        f"{artifact.metadata.name}-logicsig",
                    )


@pytest.mark.parametrize("optimization_level", [0, 1, 2])
def test_assemble(case: PuyaExample, optimization_level: int) -> None:
    compile_result = compile_src_from_options(
        PuyaOptions(
            paths=(case.path,),
            optimization_level=optimization_level,
            template_vars_path=case.template_vars_path,
            debug_level=0,
            output_teal=False,
            output_arc32=False,
        )
    )
    for artifacts in compile_result.teal.values():
        for artifact in artifacts:
            match artifact:
                case CompiledContract(approval_program=approval, clear_program=clear):
                    puya_assemble_program(
                        compile_result.context,
                        approval,
                    )
                    puya_assemble_program(
                        compile_result.context,
                        clear,
                    )
                case CompiledLogicSignature(program=logic_sig):
                    puya_assemble_program(
                        compile_result.context,
                        logic_sig,
                    )


def puya_assemble_program(
    context: CompileContext,
    program: TealProgram,
) -> bytes:
    return assemble_program(context, program, get_template_vars(context.options)).bytecode


def _value_as_tmpl_str(value: int | bytes | str) -> str:
    match value:
        case int(int_value):
            return str(int_value)
        case bytes(bytes_value):
            return f"0x{bytes_value.hex()}"
        case str(str_value):
            return repr(str_value)


def assemble_and_compare_program(
    context: CompileContext,
    algod_client: AlgodClient,
    program: TealProgram,
    name: str,
) -> None:
    puya_program = puya_assemble_program(context, program)
    program = _replace_template_variables(context.options, program)
    teal_src = emit_teal(context, program)
    algod_program = Program(teal_src, algod_client).raw_binary

    expected = algod_program.hex()
    actual = puya_program.hex()
    if expected != actual:
        # attempt to decompile both to compare, but revert to byte code if puya can't
        # even be disassembled
        try:
            puya_dis = algod_client.disassemble(puya_program)["result"]
        except algosdk.error.AlgodHTTPError:
            pass
        else:
            expected = algod_client.disassemble(algod_program)["result"]
            actual = puya_dis
    assert actual == expected, f"{name} bytecode does not match algod bytecode"


def _replace_template_variables(options: PuyaOptions, program: TealProgram) -> TealProgram:
    program = copy.deepcopy(program)
    template_vars = get_template_vars(options)
    for sub in program.all_subroutines:
        for block in sub.blocks:
            for op_idx, op in enumerate(block.ops):
                match op:
                    case TemplateVar(op_code="int", name=name, source_location=loc):
                        value = template_vars[name]
                        assert isinstance(value, int)
                        op = Int(value=value, source_location=loc)
                    case TemplateVar(op_code="byte", name=name, source_location=loc):
                        value = template_vars[name]
                        assert isinstance(value, bytes)
                        op = Byte(
                            value=value, encoding=AVMBytesEncoding.base16, source_location=loc
                        )
                    case _:
                        continue
                block.ops[op_idx] = op

    return program
