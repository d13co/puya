import typing

import mypy.nodes
import mypy.types

from puya import log
from puya.awst import wtypes
from puya.awst.nodes import (
    AppStateExpression,
    BaseClassSubroutineTarget,
    BoxProxyField,
    InstanceSubroutineTarget,
)
from puya.awst_build import pytypes
from puya.awst_build.context import ASTConversionModuleContext
from puya.awst_build.contract_data import AppStorageDeclaration
from puya.awst_build.eb.app_account_state import AppAccountStateExpressionBuilder
from puya.awst_build.eb.app_state import AppStateExpressionBuilder
from puya.awst_build.eb.base import ExpressionBuilder, InstanceBuilder, TypeBuilder
from puya.awst_build.eb.box import (
    BoxMapProxyExpressionBuilder,
    BoxProxyExpressionBuilder,
    BoxRefProxyExpressionBuilder,
)
from puya.awst_build.eb.subroutine import (
    BaseClassSubroutineInvokerExpressionBuilder,
    SubroutineInvokerExpressionBuilder,
)
from puya.awst_build.eb.var_factory import var_expression
from puya.awst_build.utils import qualified_class_name
from puya.errors import CodeError, InternalError
from puya.parse import SourceLocation

logger = log.get_logger(__name__)


class ContractTypeExpressionBuilder(TypeBuilder):
    def __init__(
        self,
        context: ASTConversionModuleContext,
        type_info: mypy.nodes.TypeInfo,
        location: SourceLocation,
    ):
        typ = context.require_ptype(type_info.fullname, location)  # TODO: pass this in
        typ_typ = pytypes.TypeType(typ)
        super().__init__(typ_typ, location)
        self.context = context
        self._type_info = type_info

    def member_access(self, name: str, location: SourceLocation) -> ExpressionBuilder:
        type_info = self._type_info
        cref = qualified_class_name(type_info)
        sym_node = type_info.names.get(name)
        node = sym_node.node if sym_node else None
        typing.assert_type(node, mypy.nodes.SymbolNode | None)

        func_type: mypy.types.Type | None
        match node:
            case None:
                raise CodeError(f"Unknown member {name!r} of {cref.full_name!r}", location)
            case mypy.nodes.Decorator(type=func_type):
                pass
            case mypy.nodes.FuncBase(type=func_type):
                pass
            case _:
                raise CodeError("Only methods can be accessed statically", location)

        if func_type is None:
            raise CodeError("", location)

        func_pytyp = self.context.type_to_pytype(func_type, source_location=location)
        if not isinstance(func_pytyp, pytypes.FuncType):
            raise CodeError(f"Couldn't resolve signature of {name!r}", location)

        target = BaseClassSubroutineTarget(cref, name)
        return BaseClassSubroutineInvokerExpressionBuilder(
            context=self.context,
            location=location,
            target=target,
            func_type=func_pytyp,
        )


class ContractSelfExpressionBuilder(InstanceBuilder):
    def __init__(
        self,
        context: ASTConversionModuleContext,
        type_info: mypy.nodes.TypeInfo,
        location: SourceLocation,
    ):
        super().__init__(location)
        self.context = context
        self._type_info = type_info

    def member_access(self, name: str, location: SourceLocation) -> ExpressionBuilder:
        state_decl = self.context.state_defs(qualified_class_name(self._type_info)).get(name)
        if state_decl is not None:
            return _builder_for_storage_access(state_decl, location)

        sym_node = self._type_info.get(name)
        if sym_node is None or sym_node.node is None:
            raise CodeError(f"Unknown member: {name}", location)
        match sym_node.node:
            # matching types taken from mypy.nodes.TypeInfo.get_method
            case mypy.nodes.FuncBase(type=func_type) | mypy.nodes.Decorator(
                type=func_type
            ) if func_type is not None:
                func_pytype = self.context.type_to_pytype(func_type, source_location=location)
                if not isinstance(func_pytype, pytypes.FuncType):
                    raise CodeError(f"Couldn't resolve signature of {name!r}", location)

                return SubroutineInvokerExpressionBuilder(
                    context=self.context,
                    target=InstanceSubroutineTarget(name=name),
                    location=location,
                    func_type=func_pytype,
                )
            case _:
                raise CodeError(
                    f"Non-storage member {name!r} has unsupported function type", location
                )


def _builder_for_storage_access(
    storage_decl: AppStorageDeclaration, location: SourceLocation
) -> ExpressionBuilder:
    match storage_decl.typ:
        case pytypes.BoxRefType:
            return BoxRefProxyExpressionBuilder(
                BoxProxyField(
                    source_location=storage_decl.source_location,
                    wtype=wtypes.box_ref_proxy_type,
                    field_name=storage_decl.member_name,
                )
            )
        case pytypes.PyType(generic=pytypes.GenericBoxType):
            return BoxProxyExpressionBuilder(
                BoxProxyField(
                    source_location=storage_decl.source_location,
                    wtype=wtypes.WBoxProxy.from_content_type(
                        storage_decl.definition.storage_wtype
                    ),
                    field_name=storage_decl.member_name,
                )
            )
        case pytypes.PyType(generic=pytypes.GenericBoxMapType):
            if storage_decl.definition.key_wtype is None:
                raise InternalError("BoxMap should have key WType", location)
            return BoxMapProxyExpressionBuilder(
                BoxProxyField(
                    source_location=storage_decl.source_location,
                    wtype=wtypes.WBoxMapProxy.from_key_and_content_type(
                        storage_decl.definition.key_wtype, storage_decl.definition.storage_wtype
                    ),
                    field_name=storage_decl.member_name,
                )
            )
        case pytypes.PyType(generic=pytypes.GenericLocalStateType):
            return AppAccountStateExpressionBuilder(storage_decl, location)
        case pytypes.PyType(generic=pytypes.GenericGlobalStateType):
            return AppStateExpressionBuilder(storage_decl, location)
        case _:
            return var_expression(
                AppStateExpression(
                    key=storage_decl.key,
                    field_name=storage_decl.member_name,
                    wtype=storage_decl.definition.storage_wtype,
                    source_location=location,
                )
            )
