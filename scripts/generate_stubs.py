#!/usr/bin/env python3
import builtins
import copy
import json
import keyword
import subprocess
import textwrap
import typing
from collections.abc import Iterable, Sequence
from pathlib import Path

import attrs
from puya import log
from puya.awst_build import pytypes
from puya.awst_build.intrinsic_models import FunctionOpMapping
from puya.awst_build.utils import snake_case

from scripts.transform_lang_spec import (
    ArgEnum,
    Immediate,
    ImmediateKind,
    LanguageSpec,
    Op,
    StackType,
    StackValue,
)

logger = log.get_logger(__name__)
INDENT = " " * 4
VCS_ROOT = Path(__file__).parent.parent


def _get_imported_name(typ: pytypes.PyType) -> str:
    return typ.name.rsplit(".", maxsplit=1)[-1]


PYTYPE_REFERENCES = [
    pytypes.AccountType,
    pytypes.ApplicationType,
    pytypes.AssetType,
    pytypes.BigUIntType,
    pytypes.BytesType,
    pytypes.UInt64Type,
]
PYTYPE_TO_LITERAL: dict[pytypes.PyType, type[int | str | bytes] | None] = {
    pytypes.BytesType: bytes,
    pytypes.UInt64Type: int,
    pytypes.AccountType: None,  # could be str
    pytypes.BigUIntType: int,
    pytypes.BoolType: None,  # already a Python type
    # below are covered transitively with respect to STACK_TYPE_MAPPING
    pytypes.ApplicationType: None,  # maybe could be int? but also covered transitively anyway
    pytypes.AssetType: None,  # same as above
}
STACK_TYPE_MAPPING: dict[StackType, Sequence[pytypes.PyType]] = {
    StackType.address_or_index: [pytypes.AccountType, pytypes.UInt64Type],
    StackType.application: [pytypes.ApplicationType, pytypes.UInt64Type],
    StackType.asset: [pytypes.AssetType, pytypes.UInt64Type],
    StackType.bytes: [pytypes.BytesType],
    StackType.bytes_8: [pytypes.BytesType],
    StackType.bytes_32: [pytypes.BytesType],
    StackType.bytes_33: [pytypes.BytesType],
    StackType.bytes_64: [pytypes.BytesType],
    StackType.bytes_80: [pytypes.BytesType],
    StackType.bool: [pytypes.BoolType, pytypes.UInt64Type],
    StackType.uint64: [pytypes.UInt64Type],
    StackType.any: [pytypes.BytesType, pytypes.UInt64Type],
    StackType.box_name: [pytypes.BytesType],  # TODO: should this be another type..?
    StackType.address: [pytypes.AccountType],
    StackType.bigint: [pytypes.BigUIntType],
    StackType.state_key: [pytypes.BytesType],  # TODO: should this be another type..?
}

BYTES_LITERAL = "bytes"
UINT64_LITERAL = "int"
STUB_NAMESPACE = "op"
ALGORAND_OP_URL = "https://developer.algorand.org/docs/get-details/dapps/avm/teal/opcodes/v10/"


class OpCodeGroup(typing.Protocol):
    def includes_op(self, op: str) -> bool: ...


@attrs.define(kw_only=True)
class RenamedOpCode:
    name: str
    stack_aliases: dict[str, list[str]] = attrs.field(factory=dict)
    """ops that are aliases for other ops that take stack values instead of immediates"""
    op: str

    def includes_op(self, op: str) -> bool:
        return self.op == op or op in self.stack_aliases


@attrs.define(kw_only=True)
class MergedOpCodes:
    name: str
    doc: str
    ops: dict[str, dict[str, list[str]]]

    def includes_op(self, op: str) -> bool:
        return op in self.ops or any(op in alias_dict for alias_dict in self.ops.values())


@attrs.define(kw_only=True)
class GroupedOpCodes:
    name: str
    """ops that are aliases for other ops that take stack values instead of immediates"""
    doc: str
    ops: dict[str, str] = attrs.field(factory=dict)
    """ops to include in group, mapped to their new name"""

    def includes_op(self, op: str) -> bool:
        return op in self.ops


GROUPED_OP_CODES = [
    GroupedOpCodes(
        name="AppGlobal",
        doc="Get or modify Global app state",
        ops={
            "app_global_get": "get",
            "app_global_get_ex": "get_ex",
            "app_global_del": "delete",
            "app_global_put": "put",
        },
    ),
    GroupedOpCodes(
        name="Scratch",
        doc="Load or store scratch values",
        ops={"loads": "load", "stores": "store"},
    ),
    GroupedOpCodes(
        name="AppLocal",
        doc="Get or modify Local app state",
        ops={
            "app_local_get": "get",
            "app_local_get_ex": "get_ex",
            "app_local_del": "delete",
            "app_local_put": "put",
        },
    ),
    GroupedOpCodes(
        name="Box",
        doc="Get or modify box state",
        ops={
            "box_create": "create",
            "box_del": "delete",
            "box_extract": "extract",
            "box_get": "get",
            "box_len": "length",
            "box_put": "put",
            "box_replace": "replace",
            "box_resize": "resize",
            "box_splice": "splice",
        },
    ),
    GroupedOpCodes(
        name="EllipticCurve",
        doc="Elliptic Curve functions",
        ops={
            "ec_add": "add",
            "ec_map_to": "map_to",
            "ec_multi_scalar_mul": "scalar_mul_multi",
            "ec_pairing_check": "pairing_check",
            "ec_scalar_mul": "scalar_mul",
            "ec_subgroup_check": "subgroup_check",
        },
    ),
    GroupedOpCodes(
        name="ITxnCreate",
        doc="Create inner transactions",
        ops={
            "itxn_begin": "begin",
            "itxn_next": "next",
            "itxn_submit": "submit",
            "itxn_field": "set",
        },
    ),
]
MERGED_OP_CODES = [
    MergedOpCodes(
        name="Txn",
        doc="Get values for the current executing transaction",
        ops={
            "txn": {},
            "txnas": {
                "txna": ["F", "I"],
            },
        },
    ),
    MergedOpCodes(
        name="GTxn",
        doc="Get values for transactions in the current group",
        ops={
            "gtxns": {
                "gtxn": ["F", "T"],
            },
            # field is immediate, first stack arg is txn index, second stack arg is array index
            "gtxnsas": {
                "gtxnsa": ["F", "A", "I"],  # group index on stack
                "gtxna": ["F", "T", "I"],  # no stack args
                "gtxnas": ["F", "T", "A"],  # array index on stack
            },
        },
    ),
    MergedOpCodes(
        name="ITxn",
        doc="Get values for the last inner transaction",
        ops={
            "itxn": {},
            "itxnas": {
                "itxna": ["F", "I"],
            },
        },
    ),
    MergedOpCodes(
        name="GITxn",
        doc="Get values for inner transaction in the last group submitted",
        ops={
            "gitxn": {},
            "gitxnas": {
                "gitxna": ["T", "F", "I"],
            },
        },
    ),
    MergedOpCodes(
        name="Global",
        doc="Get Global values",
        ops={"global": {}},
    ),
]
RENAMED_OP_CODES = [
    RenamedOpCode(
        name="arg",
        op="args",
        stack_aliases={"arg": ["N"]},
    ),
    RenamedOpCode(
        name="extract",
        op="extract3",
        stack_aliases={
            "extract": ["A", "S", "L"],
        },
    ),
    RenamedOpCode(
        name="replace",
        op="replace3",
        stack_aliases={
            "replace2": ["A", "S", "B"],
        },
    ),
    RenamedOpCode(
        name="substring",
        op="substring3",
        stack_aliases={
            "substring": ["A", "S", "E"],
        },
    ),
    RenamedOpCode(
        name="gload",
        op="gloadss",
        stack_aliases={
            "gload": ["T", "I"],
            "gloads": ["A", "I"],
        },
    ),
    RenamedOpCode(
        name="gaid",
        op="gaids",
        stack_aliases={"gaid": ["T"]},
    ),
    RenamedOpCode(
        name="exit",
        op="return",
    ),
]
OPCODE_GROUPS: list[OpCodeGroup] = [
    *GROUPED_OP_CODES,
    *MERGED_OP_CODES,
    *RENAMED_OP_CODES,
]


EXCLUDED_OPCODES = {
    # low level flow control
    "bnz",
    "bz",
    "b",
    "callsub",
    "retsub",
    "proto",
    "switch",
    "match",
    # low level stack manipulation
    "intc",
    *[f"intc_{i}" for i in range(4)],
    "bytec",
    *[f"bytec_{i}" for i in range(4)],
    "pushbytes",
    "pushbytess",
    "pushint",
    "pushints",
    "frame_dig",
    "frame_bury",
    "bury",
    "cover",
    "dig",
    "dup",
    "dup2",
    "dupn",
    "pop",
    "popn",
    "swap",
    "uncover",
    # program scratch slot read/modification (for current program)
    "load",
    "loads",
    "store",
    "stores",
    # maninuplates what other low level ops point to
    "intcblock",
    "bytecblock",
    # implicit immediates, covered by optimiser and/or assembler
    "arg_0",
    "arg_1",
    "arg_2",
    "arg_3",
    # have a higher level abstraction that supersedes it
    "log",
}


# which ops to treat as properties in the generated stubs
PROPERTY_OPS = {
    "global": {"exclude": ["opcode_budget"]},
    "txn": {"exclude": list[str]()},
}


@attrs.define
class TypedName:
    name: str
    type: StackType | ImmediateKind | str
    doc: str | None


@attrs.define(kw_only=True)
class FunctionDef:
    name: str
    doc: list[str]
    is_property: bool
    args: list[TypedName] = attrs.field(factory=list)
    returns: list[TypedName] = attrs.field(factory=list)
    op_mappings: list[FunctionOpMapping] = attrs.field(factory=list)

    @property
    def has_any_arg(self) -> bool:
        return any(r.type == StackType.any for r in self.args)

    @returns.validator
    def _no_any_return(self, _attribute: object, returns: list[TypedName]) -> None:
        if any(r.type == StackType.any for r in returns):
            # functions with any returns should have already been transformed
            raise ValueError(f"Unexpected function {self.name} with any return")


@attrs.define
class ClassDef:
    name: str
    doc: str
    methods: list[FunctionDef] = attrs.field()
    ops: list[str]


def main() -> None:
    spec_path = VCS_ROOT / "langspec.puya.json"

    lang_spec_json = json.loads(spec_path.read_text(encoding="utf-8"))
    lang_spec = LanguageSpec.from_json(lang_spec_json)

    function_defs = list[FunctionDef]()
    class_defs = list[ClassDef]()
    enums_to_build = dict[str, bool]()
    for op in lang_spec.ops.values():
        if not is_simple_op(op):
            logger.info(f"Ignoring: {op.name}")
            continue
        overriding_immediate = get_overriding_immediate(op)
        if overriding_immediate:
            class_defs.append(
                build_class_from_overriding_immediate(
                    lang_spec,
                    op,
                    class_name=get_python_enum_class(op.name),
                    class_doc=" ".join(op.doc),
                    immediate=overriding_immediate,
                    aliases=[],
                )
            )
        else:
            for immediate in op.immediate_args:
                if immediate.immediate_type == ImmediateKind.arg_enum and (
                    immediate.modifies_stack_input is None
                    and immediate.modifies_stack_output is None
                ):
                    assert immediate.arg_enum is not None
                    enums_to_build[immediate.arg_enum] = True
            function_defs.extend(build_operation_methods(op, op.name, []))
    for merged in MERGED_OP_CODES:
        class_defs.append(build_merged_ops(lang_spec, merged))
    for grouped in GROUPED_OP_CODES:
        class_defs.append(build_grouped_ops(lang_spec, grouped, enums_to_build))
    for aliased in RENAMED_OP_CODES:
        function_defs.extend(build_aliased_ops(lang_spec, aliased))
    function_defs.sort(key=lambda x: x.name)
    class_defs.sort(key=lambda x: x.name)

    enum_names = list(enums_to_build.keys())
    output_stub(lang_spec, enum_names, function_defs, class_defs)
    output_awst_data(lang_spec, enum_names, function_defs, class_defs)


def sub_types(type_name: StackType, *, covariant: bool) -> Sequence[pytypes.PyType]:
    try:
        typs = STACK_TYPE_MAPPING[type_name]
    except KeyError as ex:
        raise NotImplementedError(
            f"Could not map stack type {type_name} to an algopy type"
        ) from ex
    else:
        last_index = None if covariant else 1
        return typs[:last_index]


_NON_SIMPLE_OPS: typing.Final = frozenset(
    {
        *EXCLUDED_OPCODES,
        *dir(builtins),
        *keyword.kwlist,  # TODO: maybe consider softkwlist too?
    }
)


def is_simple_op(op: Op) -> bool:
    return not (
        op.name in _NON_SIMPLE_OPS
        or not op.name.isidentifier()
        or any(g.includes_op(op.name) for g in OPCODE_GROUPS)  # handled separately
    )


def immediate_kind_to_type(kind: ImmediateKind) -> type[int | str]:
    match kind:
        case ImmediateKind.uint8 | ImmediateKind.int8 | ImmediateKind.uint64:
            return int
        case ImmediateKind.arg_enum:
            return str
        case _:
            raise ValueError(f"Unexpected ImmediateKind: {kind}")


def get_python_type(
    typ: StackType | ImmediateKind | str, *, covariant: bool, any_as: str | None
) -> str:
    match typ:
        case StackType() as stack_type:
            if any_as and stack_type == StackType.any:
                return any_as
            ptypes_ = sub_types(stack_type, covariant=covariant)
            names = [_get_imported_name(wt) for wt in ptypes_]
            if covariant:
                for pt in ptypes_:
                    lit_t = PYTYPE_TO_LITERAL[pt]
                    if lit_t is not None:
                        lit_name = lit_t.__name__
                        if lit_name not in names:
                            names.append(lit_name)
            return " | ".join(names)
        case ImmediateKind() as immediate_kind:
            return immediate_kind_to_type(immediate_kind).__name__
        case _:
            return typ


def build_method_stub(function: FunctionDef, prefix: str = "") -> Iterable[str]:
    signature = list[str]()
    doc = function.doc[:]
    signature.append(f"def {function.name}(")
    args = list[str]()
    for arg in function.args:
        python_type = get_python_type(arg.type, covariant=True, any_as=None)
        args.append(f"{arg.name}: {python_type}")
        if arg.doc:
            doc.append(f":param {python_type} {arg.name}: {arg.doc}")
    if function.args:
        args.append("/")  # TODO: remove once we support kwargs
    signature.append(", ".join(args))

    return_types = [
        get_python_type(ret.type, covariant=False, any_as=None) for ret in function.returns
    ]
    return_docs = [r.doc for r in function.returns if r.doc is not None]
    match return_types:
        case []:
            returns = "None"
        case [returns]:
            pass
        case _:
            returns = f"tuple[{', '.join(return_types)}]"
    if return_docs:
        if doc:
            doc.append(f":returns {returns}: {return_docs[0]}")
            doc.extend(return_docs[1:])
        else:
            doc = return_docs
    signature.append(f") -> {returns}:")
    teal_ops = sorted({op.op_code for op in function.op_mappings})
    teal_op_desc = ", ".join(_get_algorand_doc(teal_op) for teal_op in teal_ops)
    doc.append("")
    doc.append(f"Native TEAL opcode: {teal_op_desc}")
    body = list[str]()
    if doc:
        body.append('"""')
        body.extend(doc)
        body.append('"""')
    else:
        body.append("...")

    yield prefix + "".join(signature)
    yield from [textwrap.indent(line, prefix=prefix + INDENT) for line in body]


def build_stub_class(klass: ClassDef) -> Iterable[str]:
    ops = [f"{_get_algorand_doc(op)}" for op in klass.ops]
    docstring = "\n".join(
        [
            INDENT + '"""',
            INDENT + klass.doc,
            INDENT + f"Native TEAL op{'s' if len(ops) > 1 else ''}: {', '.join(ops)}",
            INDENT + '"""',
        ]
    )
    method_preamble = f"{INDENT}@staticmethod"
    yield f"class {klass.name}:"
    yield docstring
    for method in klass.methods:
        if method.is_property:
            yield from build_class_var_stub(method, INDENT)
        else:
            yield method_preamble
            yield from build_method_stub(method, prefix=INDENT)
        yield ""


def build_class_var_stub(function: FunctionDef, indent: str) -> Iterable[str]:
    return_types = [
        get_python_type(ret.type, covariant=False, any_as=None) for ret in function.returns
    ]
    return_docs = [r.doc for r in function.returns if r.doc is not None]
    doc = return_docs if return_docs else function.doc[:]
    match return_types:
        case []:
            returns = "None"
        case [returns]:
            pass
        case _:
            returns = f"tuple[{', '.join(return_types)}]"
    yield f"{indent}{function.name}: typing.Final[{returns}] = ..."
    yield f'{indent}"""'
    for doc_line in doc:
        yield f"{indent}{doc_line}"
    yield f'{indent}"""'


def _get_modified_stack_value(alias: Op) -> StackValue:
    immediate = get_overriding_immediate(alias)
    assert immediate
    if immediate.modifies_stack_input is not None:
        return alias.stack_inputs[immediate.modifies_stack_input]
    else:
        assert immediate.modifies_stack_output is not None
        return alias.stack_outputs[immediate.modifies_stack_output]


AliasT: typing.TypeAlias = tuple[Op, list[str]]


def build_class_from_overriding_immediate(
    spec: LanguageSpec,
    op: Op,
    class_name: str,
    class_doc: str,
    immediate: Immediate,
    aliases: list[AliasT],
) -> ClassDef:
    assert immediate.arg_enum
    logger.info(f"Using overriding immediate for {op.name}")

    arg_enum_values = spec.arg_enums[immediate.arg_enum]

    # copy inputs so they can be mutated safely
    op = copy.deepcopy(op)
    aliases = copy.deepcopy(aliases)

    # obtain a list of stack values that will be modified for each enum
    stacks_to_modify = [_get_modified_stack_value(o) for o, _ in [(op, None), *aliases]]

    # build a method for each arg enum value
    methods = list[FunctionDef]()
    class_ops = {op.name}
    for value in arg_enum_values:
        stack_type = value.stack_type
        assert stack_type

        for stack_to_modify in stacks_to_modify:
            stack_to_modify.stack_type = stack_type
            stack_to_modify.doc = value.doc

        method = build_operation_method(
            op, snake_case(value.name), aliases, const_immediate_value=(immediate, value)
        )

        for op_mapping in method.op_mappings:
            class_ops.add(op_mapping.op_code)

        methods.append(method)

    return ClassDef(name=class_name, doc=class_doc, methods=methods, ops=sorted(class_ops))


def get_op_doc(op: Op) -> list[str]:
    doc = [d.replace("\\", "\\\\") for d in op.doc]

    return doc


def map_typed_names(
    values: Iterable[StackValue], replace_any_with: StackType | None = None
) -> Iterable[TypedName]:
    yield from (
        TypedName(
            name=arg.name.lower(),
            type=(
                replace_any_with
                if arg.stack_type == StackType.any and replace_any_with
                else arg.stack_type
            ),
            doc=arg.doc,
        )
        for arg in values
    )


def get_python_enum_class(arg_enum: str) -> str:
    # don't change acronyms
    if arg_enum.isupper():
        return arg_enum
    return snake_case(arg_enum).replace("_", " ").title().replace(" ", "")


def get_op_args(op: Op, replace_any_with: StackType | None) -> Iterable[TypedName]:
    for immediate in op.immediate_args:
        arg_type: ImmediateKind | str = immediate.immediate_type
        if immediate.immediate_type == ImmediateKind.arg_enum:
            assert immediate.arg_enum, "Arg enum expected"
            arg_type = get_python_enum_class(immediate.arg_enum)

        yield TypedName(
            name=immediate.name.lower(),
            type=arg_type,
            doc=immediate.doc,
        )

    yield from map_typed_names(op.stack_inputs, replace_any_with=replace_any_with)


def get_op_returns(op: Op, replace_any_with: StackType | None) -> Iterable[TypedName]:
    if op.halts:
        yield TypedName(name="", type="typing.Never", doc="Halts program")
    else:
        yield from map_typed_names(op.stack_outputs, replace_any_with=replace_any_with)


def get_overriding_immediate(op: Op) -> Immediate | None:
    return next(
        (
            immediate
            for immediate in op.immediate_args
            if immediate.modifies_stack_input is not None
            or immediate.modifies_stack_output is not None
        ),
        None,
    )


def build_enum(spec: LanguageSpec, arg_enum: str) -> Iterable[str]:
    values = spec.arg_enums[arg_enum]
    enum_name = get_python_enum_class(arg_enum)
    yield f"class {enum_name}(str):"
    yield f'{INDENT}"""Available values for the `{arg_enum}` enum"""'
    for value in values:
        yield f"{INDENT}{value.name}: {enum_name} = ..."
    yield ""


def build_function_op_mapping(
    op: Op,
    arg_map: list[str],
    signature_args: list[TypedName],
    any_as: StackType | None = None,
    const_immediate_value: tuple[Immediate, ArgEnum] | None = None,
) -> FunctionOpMapping:
    if arg_map:
        arg_name_map = {n: signature_args[idx].name for idx, n in enumerate(arg_map)}
    else:
        arg_name_map = {n.name.upper(): n.name for n in signature_args}
    # replace immediate reference to arg enum with a constant enum value
    result_ptypes = [
        sub_types(
            any_as if o.stack_type == StackType.any and any_as else o.stack_type,
            covariant=False,
        )[0]
        for o in op.stack_outputs
    ]
    if not result_ptypes:
        result_typ = pytypes.NoneType
    elif len(op.stack_outputs) == 1:
        (result_typ,) = result_ptypes
    else:
        result_typ = pytypes.GenericTupleType.parameterise(result_ptypes, source_location=None)

    return FunctionOpMapping(
        op_code=op.name,
        immediates={
            (
                const_immediate_value[1].name
                if (const_immediate_value and const_immediate_value[0] == arg)
                else arg_name_map[arg.name]
            ): (
                None
                if (const_immediate_value and const_immediate_value[0] == arg)
                else immediate_kind_to_type(arg.immediate_type)
            )
            for arg in op.immediate_args
        },
        stack_inputs={
            arg_name_map[arg.name]: tuple(
                sub_types(
                    any_as if arg.stack_type == StackType.any and any_as else arg.stack_type,
                    covariant=True,
                )
            )
            for arg in op.stack_inputs
        },
        result=result_typ,
    )


def build_operation_method(
    op: Op,
    op_function_name: str,
    aliases: list[AliasT],
    replace_any_with: StackType | None = None,
    const_immediate_value: tuple[Immediate, ArgEnum] | None = None,
) -> FunctionDef:
    args = list(get_op_args(op, replace_any_with))
    function_returns = list(get_op_returns(op, replace_any_with))

    # python stub args can be different to mapping args, due to immediate args
    # that are inferred based on the method/property used
    function_args = args.copy()
    # remove immediate arg from signature
    if const_immediate_value:
        doc = []
        immediate_arg_index = op.immediate_args.index(const_immediate_value[0])
        function_args.pop(immediate_arg_index)
    else:
        doc = get_op_doc(op)
    proto_function = FunctionDef(
        name=op_function_name,
        doc=doc,
        is_property=_op_is_stub_property(op.name, op_function_name),
        args=function_args,
        returns=function_returns,
        op_mappings=[
            build_function_op_mapping(
                op,
                alias_args,
                args,
                any_as=replace_any_with,
                const_immediate_value=const_immediate_value,
            )
            for op, alias_args in [(op, list[str]()), *aliases]
        ],
    )

    return proto_function


def _op_is_stub_property(op_name: str, op_function_name: str) -> bool:
    try:
        property_op = PROPERTY_OPS[op_name]
    except KeyError:
        return False
    return op_function_name not in property_op["exclude"]


def build_operation_methods(
    op: Op, op_function_name: str, aliases: list[AliasT]
) -> Iterable[FunctionDef]:
    logger.info(f"Mapping {op.name} to {op_function_name}")

    if StackType.any in (s.stack_type for s in op.stack_outputs):
        logger.info(f"Found any output for {op.name}")
        yield build_operation_method(
            op,
            op_function_name + "_bytes",
            aliases,
            replace_any_with=StackType.bytes,
        )
        yield build_operation_method(
            op,
            op_function_name + "_uint64",
            aliases,
            replace_any_with=StackType.uint64,
        )
    else:
        yield build_operation_method(op, op_function_name, aliases)


def build_aliased_ops(spec: LanguageSpec, group: RenamedOpCode) -> Iterable[FunctionDef]:
    op = spec.ops[group.op]
    aliases = [
        (spec.ops[stack_alias], arg_map) for stack_alias, arg_map in group.stack_aliases.items()
    ]
    methods = build_operation_methods(op, group.name, aliases)
    return methods


def build_merged_ops(spec: LanguageSpec, group: MergedOpCodes) -> ClassDef:
    merge_methods = dict[str, FunctionDef]()

    for other_op_name, alias_dict in group.ops.items():
        aliases = [(spec.ops[alias_op], arg_map) for alias_op, arg_map in alias_dict.items()]
        other_op = spec.ops[other_op_name]
        overriding_immediate = get_overriding_immediate(other_op)
        assert overriding_immediate
        other_class = build_class_from_overriding_immediate(
            spec,
            other_op,
            class_name=group.name,
            class_doc=group.doc,
            immediate=overriding_immediate,
            aliases=aliases,
        )
        for method in other_class.methods:
            merge_methods[method.name] = method

    methods = list(merge_methods.values())
    return ClassDef(name=group.name, doc=group.doc, methods=methods, ops=sorted(group.ops))


def build_grouped_ops(
    spec: LanguageSpec, group: GroupedOpCodes, enums_to_build: dict[str, bool]
) -> ClassDef:
    methods = list[FunctionDef]()
    for rename_op_name, python_name in group.ops.items():
        rename_op = spec.ops[rename_op_name]
        rename_immediate = get_overriding_immediate(rename_op)
        if rename_immediate:
            rename_class = build_class_from_overriding_immediate(
                spec,
                rename_op,
                class_name=group.name,
                class_doc=group.doc,
                immediate=rename_immediate,
                aliases=[],
            )
            # when grouping an op with immediate overrides, treat python_name as a prefix
            for method in rename_class.methods:
                method.name = f"{python_name}_{method.name}"
            methods.extend(rename_class.methods)

        else:
            methods.extend(build_operation_methods(rename_op, python_name, aliases=[]))
        for arg in rename_op.immediate_args:
            if arg.immediate_type == ImmediateKind.arg_enum and (
                arg.modifies_stack_input is None and arg.modifies_stack_output is None
            ):
                assert arg.arg_enum is not None
                enums_to_build[arg.arg_enum] = True

    class_def = ClassDef(
        name=group.name,
        doc=group.doc,
        methods=methods,
        ops=sorted(group.ops),
    )
    return class_def


def pytype_repr(typ: pytypes.PyType) -> str:
    match typ:
        case pytypes.BoolType:
            return "pytypes.BoolType"
        case pytypes.UInt64Type:
            return "pytypes.UInt64Type"
        case pytypes.AccountType:
            return "pytypes.AccountType"
        case pytypes.ApplicationType:
            return "pytypes.ApplicationType"
        case pytypes.AssetType:
            return "pytypes.AssetType"
        case pytypes.BytesType:
            return "pytypes.BytesType"
        case pytypes.BigUIntType:
            return "pytypes.BigUIntType"
        case pytypes.TupleType(generic=pytypes.GenericTupleType, items=tuple_items) if len(
            tuple_items
        ) > 1:
            item_strs = [pytype_repr(item) for item in tuple_items]
            return (
                f"pytypes.GenericTupleType.parameterise("
                f"({', '.join(item_strs)}), source_location=None)"
            )
    raise ValueError(f"Unexpected pytype: {typ}")


def build_op_specification_body(function: FunctionDef) -> Iterable[str]:
    if function.is_property:
        assert len(function.op_mappings) == 1
        (op_mapping,) = function.op_mappings
        assert len(op_mapping.immediates) == 1
        (immediate,) = op_mapping.immediates
        yield (
            f"{function.name}=PropertyOpMapping("
            f"{op_mapping.op_code!r}, {immediate!r}, {pytype_repr(op_mapping.result)},"
            f"),"
        )
    else:
        assert len(function.op_mappings) >= 1
        yield f"{function.name}=("
        for op_mapping in function.op_mappings:
            yield f"FunctionOpMapping({op_mapping.op_code!r},"
            if op_mapping.immediates:
                yield " immediates=dict("
                for idx, (name_or_value, literal_type_or_none) in enumerate(
                    op_mapping.immediates.items()
                ):
                    if idx:
                        yield ", "
                    if literal_type_or_none is None:
                        val_repr = repr(literal_type_or_none)
                    else:
                        val_repr = literal_type_or_none.__name__

                    yield f"{name_or_value}={val_repr}"
                yield "),"
            if op_mapping.stack_inputs:
                yield " stack_inputs=dict("
                for idx, (arg_name, allowed_types) in enumerate(op_mapping.stack_inputs.items()):
                    if idx:
                        yield ", "
                    yield f"{arg_name}="
                    if len(allowed_types) == 1:
                        yield f"({pytype_repr(*allowed_types)},)"
                    else:
                        yield "("
                        for idx2, allowed_type in enumerate(allowed_types):
                            if idx2:
                                yield ","
                            yield pytype_repr(allowed_type)
                        yield ")"
                yield "),"
            if op_mapping.result is not pytypes.NoneType:
                yield f" result={pytype_repr(op_mapping.result)},"
            yield "),"
        yield "),"


def build_awst_data(
    lang_spec: LanguageSpec,
    enums: list[str],
    function_ops: list[FunctionDef],
    class_ops: list[ClassDef],
) -> Iterable[str]:
    yield "import typing"
    yield "from collections.abc import Mapping, Sequence"
    yield "from puya.awst_build import pytypes"
    yield (
        "from puya.awst_build.intrinsic_models import"
        " FunctionOpMapping, ImmediateArgMapping, PropertyOpMapping"
    )
    yield "ENUM_CLASSES: typing.Final[Mapping[str, Mapping[str, str]]] = dict("
    for enum_name in enums:
        yield f"{get_python_enum_class(enum_name)}=dict("
        for enum_value in lang_spec.arg_enums[enum_name]:
            # enum names currently match enum immediate values
            yield f'{enum_value.name}="{enum_value.name}",'
        yield "),"
    yield ")"
    yield ""
    yield "FUNC_TO_AST_MAPPER: typing.Final[Mapping[str, Sequence[FunctionOpMapping]]] = dict("
    for function_op in function_ops:
        yield "".join(build_op_specification_body(function_op))
    yield ")"

    yield (
        "NAMESPACE_CLASSES: "
        "typing.Final[Mapping[str, Mapping[str, PropertyOpMapping | Sequence[FunctionOpMapping]]]]"
        " = dict("
    )
    for class_op in class_ops:
        yield f"{class_op.name}=dict("
        for method in class_op.methods:
            yield "".join(build_op_specification_body(method))
        yield "),"
    yield ")"


def output_stub(
    lang_spec: LanguageSpec,
    enums: list[str],
    function_ops: list[FunctionDef],
    class_ops: list[ClassDef],
) -> None:
    references = ", ".join(map(_get_imported_name, PYTYPE_REFERENCES))
    stub: list[str] = [
        "import typing",
        "",
        f"from algopy import {references}",
    ]

    for arg_enum in enums:
        stub.extend(build_enum(lang_spec, arg_enum))

    for function in function_ops:
        stub.extend(build_method_stub(function))

    for class_op in class_ops:
        stub.extend(build_stub_class(class_op))

    stub_out_path = VCS_ROOT / "stubs" / "algopy-stubs" / f"{STUB_NAMESPACE}.pyi"
    stub_out_path.write_text("\n".join(stub), encoding="utf-8")
    subprocess.run(["black", str(stub_out_path)], check=True, cwd=VCS_ROOT)


def output_awst_data(
    lang_spec: LanguageSpec,
    enums: list[str],
    function_ops: list[FunctionDef],
    class_ops: list[ClassDef],
) -> None:
    awst_data = build_awst_data(lang_spec, enums, function_ops, class_ops)

    awst_data_path = VCS_ROOT / "src" / "puya" / "awst_build" / "intrinsic_data.py"
    awst_data_path.write_text("\n".join(awst_data), encoding="utf-8")
    subprocess.run(["black", str(awst_data_path)], check=True, cwd=VCS_ROOT)
    subprocess.run(["ruff", "check", "--fix", str(awst_data_path)], check=False, cwd=VCS_ROOT)


def _get_algorand_doc(op: str) -> str:
    return f"[`{op}`]({ALGORAND_OP_URL}#{op})"


if __name__ == "__main__":
    main()
