from __future__ import annotations

import typing

import mypy.nodes

from puya import log
from puya.awst.nodes import Expression, IntrinsicCall, Literal, MethodConstant
from puya.awst_build.constants import ARC4_SIGNATURE_ALIAS
from puya.awst_build.eb.base import ExpressionBuilder, IntermediateExpressionBuilder
from puya.awst_build.eb.bytes import BytesExpressionBuilder
from puya.awst_build.eb.var_factory import var_expression
from puya.awst_build.intrinsic_models import FunctionOpMapping, PropertyOpMapping
from puya.awst_build.utils import convert_literal, get_arg_mapping
from puya.errors import CodeError
from puya.utils import StableSet

if typing.TYPE_CHECKING:
    from collections.abc import Mapping, Sequence

    from puya.awst_build import pytypes
    from puya.parse import SourceLocation

logger = log.get_logger(__name__)


class Arc4SignatureBuilder(IntermediateExpressionBuilder):
    @typing.override
    def call(
        self,
        args: Sequence[ExpressionBuilder | Literal],
        arg_typs: Sequence[pytypes.PyType],
        arg_kinds: list[mypy.nodes.ArgKind],
        arg_names: list[str | None],
        location: SourceLocation,
    ) -> ExpressionBuilder:
        match args:
            case [Literal(value=str(str_value))]:
                pass
            case _:
                logger.error(f"Unexpected args for {ARC4_SIGNATURE_ALIAS}", location=location)
                str_value = ""  # dummy value to keep evaluating
        return BytesExpressionBuilder(
            MethodConstant(
                value=str_value,
                source_location=location,
            )
        )


class IntrinsicEnumClassExpressionBuilder(IntermediateExpressionBuilder):
    def __init__(self, type_name: str, data: Mapping[str, str], location: SourceLocation) -> None:
        super().__init__(location)
        self._type_name = type_name
        self._data = data

    @typing.override
    def call(
        self,
        args: Sequence[ExpressionBuilder | Literal],
        arg_typs: Sequence[pytypes.PyType],
        arg_kinds: list[mypy.nodes.ArgKind],
        arg_names: list[str | None],
        location: SourceLocation,
    ) -> ExpressionBuilder:
        raise CodeError("Cannot instantiate enumeration type", location)

    @typing.override
    def member_access(self, name: str, location: SourceLocation) -> ExpressionBuilder | Literal:
        value = self._data.get(name)
        if value is None:
            raise CodeError(f"Unknown member {name!r} of {self._type_name!r}", location)
        return Literal(value=value, source_location=location)


class IntrinsicNamespaceClassExpressionBuilder(IntermediateExpressionBuilder):
    def __init__(
        self,
        type_name: str,
        data: Mapping[str, PropertyOpMapping | Sequence[FunctionOpMapping]],
        location: SourceLocation,
    ) -> None:
        super().__init__(location)
        self._type_name = type_name
        self._data = data

    @typing.override
    def member_access(self, name: str, location: SourceLocation) -> ExpressionBuilder:
        mapping = self._data.get(name)
        if mapping is None:
            raise CodeError(f"Unknown member {name!r} of {self._type_name!r}", location)
        if isinstance(mapping, PropertyOpMapping):
            intrinsic_expr = IntrinsicCall(
                op_code=mapping.op_code,
                immediates=[mapping.immediate],
                wtype=mapping.typ.wtype,
                source_location=location,
            )
            return var_expression(intrinsic_expr)
        else:
            fullname = ".".join((self._type_name, name))
            return IntrinsicFunctionExpressionBuilder(fullname, mapping, location)


class IntrinsicFunctionExpressionBuilder(IntermediateExpressionBuilder):
    def __init__(
        self, fullname: str, mappings: Sequence[FunctionOpMapping], location: SourceLocation
    ) -> None:
        assert mappings
        self._fullname = fullname
        self._mappings = mappings
        super().__init__(location)

    @typing.override
    def call(
        self,
        args: Sequence[ExpressionBuilder | Literal],
        arg_typs: Sequence[pytypes.PyType],
        arg_kinds: list[mypy.nodes.ArgKind],
        arg_names: list[str | None],
        location: SourceLocation,
    ) -> ExpressionBuilder:
        primary_mapping = self._mappings[0]  # TODO: remove this assumption
        func_arg_names = (*primary_mapping.literal_arg_names, *primary_mapping.stack_inputs.keys())

        resolved_args: list[Expression | Literal] = [
            a.rvalue() if isinstance(a, ExpressionBuilder) else a for a in args
        ]
        arg_mapping = get_arg_mapping(
            func_arg_names, args=zip(arg_names, resolved_args, strict=False), location=location
        )
        intrinsic_expr = _map_call(
            self._mappings, callee=self._fullname, node_location=location, args=arg_mapping
        )
        return var_expression(intrinsic_expr)


def _best_op_mapping(
    op_mappings: Sequence[FunctionOpMapping], args: dict[str, Expression | Literal]
) -> FunctionOpMapping:
    """Find op mapping that matches as many arguments to immediate args as possible"""
    literal_arg_names = {arg_name for arg_name, arg in args.items() if isinstance(arg, Literal)}
    for op_mapping in sorted(op_mappings, key=lambda om: len(om.literal_arg_names), reverse=True):
        if literal_arg_names.issuperset(op_mapping.literal_arg_names):
            return op_mapping
    # fall back to first, let argument mapping handle logging errors
    return op_mappings[0]


def _map_call(
    ast_mapper: Sequence[FunctionOpMapping],
    callee: str,
    node_location: SourceLocation,
    args: dict[str, Expression | Literal],
) -> IntrinsicCall:
    if len(ast_mapper) == 1:
        (op_mapping,) = ast_mapper
    else:
        op_mapping = _best_op_mapping(ast_mapper, args)

    args = args.copy()  # make a copy since we're going to mutate

    immediates = list[str | int]()
    for immediate in op_mapping.immediates.items():
        match immediate:
            case value, None:
                immediates.append(value)
            case arg_name, literal_type:
                arg_in = args.pop(arg_name, None)
                if arg_in is None:
                    logger.error(f"Missing expected argument {arg_name}", location=node_location)
                elif not (
                    isinstance(arg_in, Literal)
                    and isinstance(arg_value := arg_in.value, literal_type)
                ):
                    logger.error(
                        f"Argument must be a literal {literal_type.__name__} value",
                        location=arg_in.source_location,
                    )
                else:
                    assert isinstance(arg_value, int | str)
                    immediates.append(arg_value)

    stack_args = list[Expression]()
    for arg_name, allowed_pytypes in op_mapping.stack_inputs.items():
        allowed_types = StableSet.from_iter(  # TODO: use PyTypes instead
            pt.wtype for pt in allowed_pytypes
        )
        arg_in = args.pop(arg_name, None)
        if arg_in is None:
            logger.error(f"Missing expected argument {arg_name}", location=node_location)
        elif isinstance(arg_in, Expression):
            # TODO this is identity based, match types instead?
            if arg_in.wtype not in allowed_types:
                logger.error(
                    f'Invalid argument type "{arg_in.wtype}"'
                    f' for argument "{arg_name}" when calling {callee}',
                    location=arg_in.source_location,
                )
            stack_args.append(arg_in)
        else:
            literal_value = arg_in.value
            for allowed_type in allowed_types:
                if allowed_type.is_valid_literal(literal_value):
                    literal_expr = convert_literal(arg_in, allowed_type)
                    stack_args.append(literal_expr)
                    break
            else:
                logger.error(
                    f"Unhandled literal type '{type(literal_value).__name__}' for argument",
                    location=arg_in.source_location,
                )

    for arg_node in args.values():
        logger.error("Unexpected argument", location=arg_node.source_location)

    return IntrinsicCall(
        op_code=op_mapping.op_code,
        wtype=op_mapping.result.wtype,
        immediates=immediates,
        stack_args=stack_args,
        source_location=node_location,
    )
