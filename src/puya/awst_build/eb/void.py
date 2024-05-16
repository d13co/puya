import typing
from collections.abc import Sequence

import mypy.nodes

from puya.awst.nodes import Literal
from puya.awst_build import pytypes
from puya.awst_build.eb._utils import bool_eval_to_constant
from puya.awst_build.eb.base import ExpressionBuilder, TypeBuilder, ValueExpressionBuilder
from puya.errors import CodeError
from puya.parse import SourceLocation


class VoidTypeExpressionBuilder(TypeBuilder):
    def __init__(self, location: SourceLocation):
        super().__init__(pytypes.TypeType(pytypes.NoneType), location)

    @typing.override
    def call(
        self,
        args: Sequence[ExpressionBuilder | Literal],
        arg_typs: Sequence[pytypes.PyType],
        arg_kinds: list[mypy.nodes.ArgKind],
        arg_names: list[str | None],
        location: SourceLocation,
    ) -> ExpressionBuilder:
        # shouldn't even be able to get here really
        raise CodeError("None is not usable as a value", location)


class VoidExpressionBuilder(ValueExpressionBuilder):
    def __init__(self, expr: Expression):
        super().__init__(pytypes.NoneType, expr)

    def bool_eval(self, location: SourceLocation, *, negate: bool = False) -> ExpressionBuilder:
        return bool_eval_to_constant(value=True, location=location, negate=negate)

    def lvalue(self) -> typing.Never:
        raise CodeError(
            "None indicates an empty return and cannot be assigned", self.source_location
        )
