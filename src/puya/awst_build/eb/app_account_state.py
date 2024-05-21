import typing
from collections.abc import Sequence

import mypy.nodes
import mypy.types

from puya.awst import wtypes
from puya.awst.nodes import (
    AppAccountStateExpression,
    Expression,
    IntegerConstant,
    Literal,
    StateDelete,
    StateExists,
    StateGet,
    StateGetEx,
    Statement,
)
from puya.awst_build import constants, pytypes
from puya.awst_build.contract_data import AppStorageDeclaration
from puya.awst_build.eb._storage import (
    StorageProxyDefinitionBuilder,
    extract_description,
    extract_key_override,
)
from puya.awst_build.eb.base import (
    ExpressionBuilder,
    GenericClassExpressionBuilder,
    IntermediateExpressionBuilder,
    TypeClassExpressionBuilder,
)
from puya.awst_build.eb.bool import BoolExpressionBuilder
from puya.awst_build.eb.tuple import TupleExpressionBuilder
from puya.awst_build.eb.value_proxy import ValueProxyExpressionBuilder
from puya.awst_build.eb.var_factory import var_expression
from puya.awst_build.utils import convert_literal_to_expr, expect_operand_wtype, get_arg_mapping
from puya.errors import CodeError
from puya.parse import SourceLocation


class AppAccountStateClassExpressionBuilder(TypeClassExpressionBuilder):
    def __init__(self, typ: pytypes.PyType, location: SourceLocation) -> None:
        assert isinstance(typ, pytypes.StorageProxyType)
        assert typ.generic == pytypes.GenericLocalStateType
        self._storage_pytype = typ.content
        super().__init__(typ.wtype, location)

    @typing.override
    def call(
        self,
        args: Sequence[ExpressionBuilder | Literal],
        arg_typs: Sequence[pytypes.PyType],
        arg_kinds: list[mypy.nodes.ArgKind],
        arg_names: list[str | None],
        location: SourceLocation,
    ) -> ExpressionBuilder:
        return _init(
            args=args,
            arg_names=arg_names,
            location=location,
            storage_wtype=self._storage_pytype.wtype,
        )


class AppAccountStateGenericClassExpressionBuilder(GenericClassExpressionBuilder):
    @typing.override
    def call(
        self,
        args: Sequence[ExpressionBuilder | Literal],
        arg_typs: Sequence[pytypes.PyType],
        arg_kinds: list[mypy.nodes.ArgKind],
        arg_names: list[str | None],
        location: SourceLocation,
    ) -> ExpressionBuilder:
        return _init(args=args, arg_names=arg_names, location=location, storage_wtype=None)


def _init(
    args: Sequence[ExpressionBuilder | Literal],
    arg_names: list[str | None],
    location: SourceLocation,
    *,
    storage_wtype: wtypes.WType | None,
) -> ExpressionBuilder:
    type_arg_name = "type_"
    arg_mapping = get_arg_mapping(
        positional_arg_names=[type_arg_name],
        args=zip(arg_names, args, strict=True),
        location=location,
    )
    try:
        type_arg = arg_mapping.pop(type_arg_name)
    except KeyError as ex:
        raise CodeError("Required positional argument missing", location) from ex

    key_arg = arg_mapping.pop("key", None)
    descr_arg = arg_mapping.pop("description", None)
    if arg_mapping:
        raise CodeError(f"Unrecognised keyword argument(s): {", ".join(arg_mapping)}", location)

    match type_arg:
        case TypeClassExpressionBuilder() as typ_class_eb:
            argument_wtype = typ_class_eb.produces()
        case _:
            raise CodeError("First argument must be a type reference", location)
    if storage_wtype is not None and argument_wtype != storage_wtype:
        raise CodeError(
            "App account state explicit type annotation does not match first argument"
            " - suggest to remove the explicit type annotation,"
            " it shouldn't be required",
            location,
        )

    key_override = extract_key_override(key_arg, location, is_prefix=False)
    description = extract_description(descr_arg)
    return AppAccountStateProxyDefinitionBuilder(
        location=location,
        key_override=key_override,
        description=description,
    )


class AppAccountStateExpressionBuilder(IntermediateExpressionBuilder):
    def __init__(self, state_decl: AppStorageDeclaration, location: SourceLocation):
        assert state_decl.typ.generic is pytypes.GenericLocalStateType
        super().__init__(location)
        self.state_decl = state_decl

    def index(
        self, index: ExpressionBuilder | Literal, location: SourceLocation
    ) -> ExpressionBuilder:
        expr = _build_field(self.state_decl, index, location)
        return AppAccountStateForAccountExpressionBuilder(expr)

    def contains(
        self, item: ExpressionBuilder | Literal, location: SourceLocation
    ) -> ExpressionBuilder:
        exists_expr = StateExists(
            field=_build_field(self.state_decl, item, location), source_location=location
        )
        return BoolExpressionBuilder(exists_expr)

    def member_access(self, name: str, location: SourceLocation) -> ExpressionBuilder | Literal:
        match name:
            case "get":
                return AppAccountStateGetMethodBuilder(self.state_decl, location)
            case "maybe":
                return AppAccountStateMaybeMethodBuilder(self.state_decl, location)
        return super().member_access(name, location)


class AppAccountStateGetMethodBuilder(IntermediateExpressionBuilder):
    def __init__(self, state_decl: AppStorageDeclaration, location: SourceLocation):
        super().__init__(location)
        self.state_decl = state_decl

    def call(
        self,
        args: Sequence[ExpressionBuilder | Literal],
        arg_typs: Sequence[pytypes.PyType],
        arg_kinds: list[mypy.nodes.ArgKind],
        arg_names: list[str | None],
        location: SourceLocation,
    ) -> ExpressionBuilder:
        if len(args) != 2:
            raise CodeError(f"Expected 2 arguments, got {len(args)}", location)
        if arg_names[0] == "default":
            default_arg, item = args
        else:
            item, default_arg = args
        default_expr = expect_operand_wtype(
            default_arg, target_wtype=self.state_decl.definition.storage_wtype
        )
        expr = StateGet(
            field=_build_field(self.state_decl, item, location),
            default=default_expr,
            source_location=location,
        )

        return var_expression(expr)


class AppAccountStateMaybeMethodBuilder(IntermediateExpressionBuilder):
    def __init__(self, state_decl: AppStorageDeclaration, location: SourceLocation):
        super().__init__(location)
        self.state_decl = state_decl

    def call(
        self,
        args: Sequence[ExpressionBuilder | Literal],
        arg_typs: Sequence[pytypes.PyType],
        arg_kinds: list[mypy.nodes.ArgKind],
        arg_names: list[str | None],
        location: SourceLocation,
    ) -> ExpressionBuilder:
        match args:
            case [item]:
                field = _build_field(self.state_decl, item, location)
                app_local_get_ex = StateGetEx(field=field, source_location=location)
                return TupleExpressionBuilder(app_local_get_ex)
            case _:
                raise CodeError("Invalid/unhandled arguments", location)


class AppAccountStateForAccountExpressionBuilder(ValueProxyExpressionBuilder):
    def __init__(self, expr: AppAccountStateExpression):
        self.__field = expr
        self.wtype = expr.wtype
        super().__init__(expr)

    def delete(self, location: SourceLocation) -> Statement:
        return StateDelete(field=self.__field, source_location=location)


class AppAccountStateProxyDefinitionBuilder(StorageProxyDefinitionBuilder):
    python_name = constants.CLS_LOCAL_STATE_ALIAS
    is_prefix = False


def _build_field(
    state_decl: AppStorageDeclaration, index: ExpressionBuilder | Literal, location: SourceLocation
) -> AppAccountStateExpression:
    index_expr = convert_literal_to_expr(index, wtypes.uint64_wtype)
    match index_expr:
        case IntegerConstant(value=account_offset):
            # https://developer.algorand.org/docs/get-details/dapps/smart-contracts/apps/#resource-availability
            # Note that the sender address is implicitly included in the array,
            # but doesn't count towards the limit of 4, so the <= 4 below is correct
            # and intended
            if not (0 <= account_offset <= 4):
                raise CodeError(
                    "Account index should be between 0 and 4 inclusive", index.source_location
                )
        case Expression(wtype=(wtypes.uint64_wtype | wtypes.account_wtype)):
            pass
        case _:
            raise CodeError(
                "Invalid index argument - must be either an Address or a UInt64",
                index.source_location,
            )
    return AppAccountStateExpression(
        key=state_decl.key,
        field_name=state_decl.member_name,
        account=index_expr,
        wtype=state_decl.definition.storage_wtype,
        source_location=location,
    )
