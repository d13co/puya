import abc
from collections.abc import Sequence

import mypy.nodes

from puya.awst.nodes import BytesConstant, BytesEncoding, Expression, Literal, ReinterpretCast
from puya.awst_build import pytypes
from puya.awst_build.eb.base import (
    FunctionBuilder,
    InstanceBuilder,
    NodeBuilder,
    TypeBuilder,
)
from puya.awst_build.eb.var_factory import var_expression
from puya.errors import CodeError
from puya.parse import SourceLocation


class FromBytesBuilder(FunctionBuilder):
    def __init__(self, cls_type: pytypes.TypeType, location: SourceLocation):
        func_typ = pytypes.FuncType(
            name=f"{cls_type.typ}.from_bytes",
            bound_arg_types=[cls_type],
            args=[
                pytypes.FuncArg(name="value", types=[pytypes.BytesType], kind=mypy.nodes.ARG_POS)
            ],
            ret_type=cls_type.typ,
        )
        super().__init__(func_typ, location)

    def call(
        self,
        args: Sequence[NodeBuilder | Literal],
        arg_typs: Sequence[pytypes.PyType],
        arg_kinds: list[mypy.nodes.ArgKind],
        arg_names: list[str | None],
        location: SourceLocation,
    ) -> NodeBuilder:
        match args:
            case [Literal(value=bytes(bytes_val), source_location=literal_loc)]:
                arg: Expression = BytesConstant(
                    value=bytes_val, encoding=BytesEncoding.unknown, source_location=literal_loc
                )
            case [InstanceBuilder(pytype=pytypes.BytesType) as eb]:
                arg = eb.rvalue()
            case _:
                raise CodeError("Invalid/unhandled arguments", location)
        return var_expression(
            ReinterpretCast(source_location=location, wtype=self.pytype.ret_type.wtype, expr=arg)
        )


class BytesBackedClassExpressionBuilder(TypeBuilder, abc.ABC):
    def member_access(self, name: str, location: SourceLocation) -> NodeBuilder:
        match name:
            case "from_bytes":
                return FromBytesBuilder(self.pytype, location)
            case _:
                raise CodeError(
                    f"{name} is not a valid class or static method on {self.pytype.typ}", location
                )
