from __future__ import annotations

import typing

import mypy.nodes
import mypy.types

from puya.awst.nodes import (
    CompiledReference,
    Literal,
)
from puya.awst_build.eb.base import (
    ExpressionBuilder,
    IntermediateExpressionBuilder,
)
from puya.awst_build.eb.contracts import (
    ContractTypeExpressionBuilder,
)
from puya.awst_build.eb.var_factory import var_expression
from puya.log import get_logger
from puya.models import CompiledReferenceField

if typing.TYPE_CHECKING:
    from collections.abc import Sequence

    from puya.parse import SourceLocation

logger = get_logger(__name__)


class LogicSigReferenceExpressionBuilder(IntermediateExpressionBuilder):
    def __init__(
        self,
        fullname: str,
        location: SourceLocation,
    ):
        super().__init__(location)
        self.fullname = fullname


class GetCompiledProgramExpressionBuilder(IntermediateExpressionBuilder):
    def __init__(self, location: SourceLocation, field: CompiledReferenceField):
        super().__init__(location)
        self.field = field

    def call(
        self,
        args: Sequence[ExpressionBuilder | Literal],
        arg_kinds: list[mypy.nodes.ArgKind],
        arg_names: list[str | None],
        location: SourceLocation,
    ) -> ExpressionBuilder:
        match args:
            case [
                ContractTypeExpressionBuilder(type_info=mypy.nodes.TypeInfo(fullname=fullname)),
                *template_values,
            ] if self.field != CompiledReferenceField.account:
                template_names = arg_names[1:]
            case [
                LogicSigReferenceExpressionBuilder(fullname=fullname),
                *template_values,
            ] if self.field == CompiledReferenceField.account:
                template_names = arg_names[1:]
            case _:
                fullname = ""
                template_names = []
                template_values = []
                logger.error("Invalid program reference", location=location)
        template_vars = dict[str, int | bytes]()
        for template_name, template_value in zip(template_names, template_values, strict=True):
            if (
                isinstance(template_name, str)
                and isinstance(template_value, Literal)
                and isinstance(template_value.value, int | bytes)
            ):
                template_vars[template_name] = template_value.value
            else:
                logger.error("Invalid template argument", location=template_value.source_location)
        return var_expression(
            CompiledReference(
                artifact=fullname,
                field=self.field,
                template_variables=template_vars,
                source_location=location,
            )
        )
