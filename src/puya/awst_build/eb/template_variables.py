import typing
from collections.abc import Sequence

import mypy.nodes

from puya.awst.nodes import Literal, TemplateVar
from puya.awst_build import pytypes
from puya.awst_build.eb._utils import bool_eval_to_constant
from puya.awst_build.eb.base import (
    CallableBuilder,
    InstanceBuilder,
    NodeBuilder,
)
from puya.awst_build.eb.var_factory import var_expression
from puya.awst_build.utils import get_arg_mapping
from puya.errors import CodeError
from puya.parse import SourceLocation


class TemplateVariableExpressionBuilder(
    InstanceBuilder[pytypes.PseudoGenericFunctionType], CallableBuilder
):
    def __init__(self, typ: pytypes.PyType, source_location: SourceLocation) -> None:
        assert isinstance(typ, pytypes.PseudoGenericFunctionType)
        super().__init__(typ, source_location)

    @typing.override
    def rvalue(self) -> typing.Never:
        raise CodeError("TemplateVar acts as a function, not an instance")

    @typing.override
    def bool_eval(self, location: SourceLocation, *, negate: bool = False) -> InstanceBuilder:
        return bool_eval_to_constant(value=True, location=location, negate=negate)

    @typing.override
    def call(
        self,
        args: Sequence[NodeBuilder | Literal],
        arg_typs: Sequence[pytypes.PyType],
        arg_kinds: list[mypy.nodes.ArgKind],
        arg_names: list[str | None],
        location: SourceLocation,
    ) -> NodeBuilder:
        var_name_arg_name = "variable_name"
        arg_mapping = get_arg_mapping(
            positional_arg_names=[var_name_arg_name],
            args=zip(arg_names, args, strict=True),
            location=location,
        )

        try:
            var_name = arg_mapping.pop(var_name_arg_name)
        except KeyError as ex:
            raise CodeError("Required positional argument missing", location) from ex

        prefix_arg = arg_mapping.pop("prefix", None)
        if arg_mapping:
            raise CodeError(
                f"Unrecognised keyword argument(s): {", ".join(arg_mapping)}", location
            )
        match prefix_arg:
            case Literal(value=str(prefix_value)):
                pass
            case None:
                prefix_value = "TMPL_"
            case _:
                raise CodeError("Invalid value for prefix argument", location)

        match var_name:
            case Literal(value=str(str_value)):
                return var_expression(
                    TemplateVar(
                        name=prefix_value + str_value,
                        wtype=self.pytype.return_type.wtype,
                        source_location=location,
                    )
                )
            case _:
                raise CodeError(
                    "TemplateVars must be declared using a string literal for the variable name"
                )
