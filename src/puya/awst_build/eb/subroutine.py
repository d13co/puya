import typing
from collections.abc import Sequence

import mypy.nodes
import mypy.types

from puya import log
from puya.awst.nodes import (
    BaseClassSubroutineTarget,
    CallArg,
    FreeSubroutineTarget,
    InstanceSubroutineTarget,
    Literal,
    SubroutineCallExpression,
)
from puya.awst_build import pytypes
from puya.awst_build.context import ASTConversionModuleContext
from puya.awst_build.eb.base import (
    FunctionBuilder,
    NodeBuilder,
)
from puya.awst_build.eb.var_factory import var_expression
from puya.awst_build.utils import require_instance_builder
from puya.errors import CodeError
from puya.parse import SourceLocation

logger = log.get_logger(__name__)


class SubroutineInvokerExpressionBuilder(FunctionBuilder):
    def __init__(
        self,
        context: ASTConversionModuleContext,
        target: InstanceSubroutineTarget | BaseClassSubroutineTarget | FreeSubroutineTarget,
        location: SourceLocation,
        func_type: pytypes.FuncType,
    ):
        super().__init__(func_type, location)
        self.context = context
        self.target = target
        self.func_type = func_type

    @typing.override
    def call(
        self,
        args: Sequence[NodeBuilder | Literal],
        arg_typs: Sequence[pytypes.PyType],
        arg_kinds: list[mypy.nodes.ArgKind],
        arg_names: list[str | None],
        location: SourceLocation,
    ) -> NodeBuilder:
        call_args = list[CallArg]()
        for arg, arg_name, arg_kind in zip(args, arg_names, arg_kinds, strict=True):
            if arg_kind.is_star():
                raise CodeError(
                    "argument unpacking at call site not currently supported", arg.source_location
                )
            call_args.append(CallArg(name=arg_name, value=require_instance_builder(arg).rvalue()))

        func_type = self.func_type
        # TODO: type check fully, not just num args... requires matching keyword positions
        if len(args) != len(func_type.args):
            logger.error("incorrect number of arguments to subroutine call", location=location)
        result_pytyp = func_type.ret_type

        call_expr = SubroutineCallExpression(
            source_location=location,
            target=self.target,
            args=call_args,
            wtype=result_pytyp.wtype,
        )
        return var_expression(call_expr)


class BaseClassSubroutineInvokerExpressionBuilder(SubroutineInvokerExpressionBuilder):
    def call(
        self,
        args: Sequence[NodeBuilder | Literal],
        arg_typs: Sequence[pytypes.PyType],
        arg_kinds: list[mypy.nodes.ArgKind],
        arg_names: list[str | None],
        location: SourceLocation,
    ) -> NodeBuilder:
        from puya.awst_build.eb.contracts import ContractSelfExpressionBuilder

        if not args and isinstance(args[0], ContractSelfExpressionBuilder):
            raise CodeError(
                "First argument when calling a base class method directly should be self",
                args[0].source_location,
            )
        return super().call(args[1:], arg_typs[1:], arg_kinds[1:], arg_names[1:], location)
