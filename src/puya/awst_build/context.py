import contextlib
from collections.abc import Iterator, Sequence

import attrs
import mypy.nodes
import mypy.types

from puya import log
from puya.awst import wtypes
from puya.awst.nodes import ConstantValue, ContractReference
from puya.awst_build import pytypes
from puya.awst_build.contract_data import AppStorageDeclaration
from puya.context import CompileContext
from puya.errors import CodeError, InternalError, log_exceptions
from puya.parse import SourceLocation
from puya.utils import attrs_extend

logger = log.get_logger(__name__)


@attrs.frozen(kw_only=True)
class ASTConversionContext(CompileContext):
    constants: dict[str, ConstantValue] = attrs.field(factory=dict)
    type_map: dict[str, pytypes.StructType] = attrs.field(factory=dict)
    state_defs: dict[ContractReference, dict[str, AppStorageDeclaration]] = attrs.field(
        factory=dict
    )

    def for_module(self, current_module: mypy.nodes.MypyFile) -> "ASTConversionModuleContext":
        return attrs_extend(ASTConversionModuleContext, self, current_module=current_module)


@attrs.frozen(kw_only=True)
class ASTConversionModuleContext(ASTConversionContext):
    current_module: mypy.nodes.MypyFile

    @property
    def module_name(self) -> str:
        return self.current_module.fullname

    @property
    def module_path(self) -> str:
        return self.current_module.path

    def node_location(
        self,
        node: mypy.nodes.Context,
        module_src: mypy.nodes.TypeInfo | None = None,
    ) -> SourceLocation:
        if not module_src:
            module_path = self.module_path
        else:
            module_name = module_src.module_name
            try:
                module_path = self.module_paths[module_name]
            except KeyError as ex:
                raise CodeError(f"Could not find module '{module_name}'") from ex
        loc = SourceLocation.from_mypy(file=module_path, node=node)
        lines = self.try_get_source(loc).code
        if loc.line > 1:
            prior_code = self.try_get_source(
                SourceLocation(file=module_path, line=1, end_line=loc.line - 1)
            ).code
            unchop = 0
            for line in reversed(prior_code or ()):
                if not line.strip().startswith("#"):
                    break
                unchop += 1
            if unchop:
                loc = attrs.evolve(loc, line=loc.line - unchop)
        if loc.end_line is not None and loc.end_line != loc.line:
            chop = 0
            for line in reversed(lines or ()):
                l_stripped = line.lstrip()
                if l_stripped and not l_stripped.startswith("#"):
                    break
                chop += 1
            if chop:
                loc = attrs.evolve(loc, end_line=loc.end_line - chop)
        return loc

    def _maybe_convert_location(
        self, location: mypy.nodes.Context | SourceLocation
    ) -> SourceLocation:
        if isinstance(location, mypy.nodes.Context):
            return self.node_location(location)
        return location

    def error(self, msg: str, location: mypy.nodes.Context | SourceLocation) -> None:
        logger.error(msg, location=self._maybe_convert_location(location))

    def info(self, msg: str, location: mypy.nodes.Context | SourceLocation) -> None:
        logger.info(msg, location=self._maybe_convert_location(location))

    def warning(self, msg: str, location: mypy.nodes.Context | SourceLocation) -> None:
        logger.warning(msg, location=self._maybe_convert_location(location))

    @contextlib.contextmanager
    def log_exceptions(
        self, fallback_location: mypy.nodes.Context | SourceLocation
    ) -> Iterator[None]:
        with log_exceptions(self._maybe_convert_location(fallback_location)):
            yield

    def mypy_expr_node_type(self, expr: mypy.nodes.Expression) -> wtypes.WType:
        mypy_type = self.get_mypy_expr_type(expr)
        return self.type_to_wtype(mypy_type, source_location=self.node_location(expr))

    def get_mypy_expr_type(self, expr: mypy.nodes.Expression) -> mypy.types.Type:
        try:
            typ = self.parse_result.manager.all_types[expr]
        except KeyError as ex:
            raise InternalError(
                "MyPy Expression to MyPy Type lookup failed", self.node_location(expr)
            ) from ex
        return mypy.types.get_proper_type(typ)

    def type_to_wtype(
        self, typ: mypy.types.Type, *, source_location: SourceLocation | mypy.nodes.Context
    ) -> wtypes.WType:
        pytype = self.type_to_pytype(typ, source_location=source_location)
        if pytype.wtype is None:
            raise InternalError(
                "fixme, need to use pytype instead", self._maybe_convert_location(source_location)
            )
        return pytype.wtype

    def type_to_pytype(
        self, typ: mypy.types.Type, *, source_location: SourceLocation | mypy.nodes.Context
    ) -> pytypes.PyType:
        loc = self._maybe_convert_location(source_location)
        proper_type = mypy.types.get_proper_type(typ)
        match proper_type:
            case mypy.types.NoneType() | mypy.types.PartialType(type=None):
                return pytypes.NoneType
            case mypy.types.LiteralType(fallback=fallback):
                return self.type_to_pytype(fallback, source_location=loc)
            case mypy.types.TupleType(items=items, partial_fallback=true_type):
                types = [self.type_to_pytype(it, source_location=loc) for it in items]
                generic = pytypes.PyType.from_name(true_type.type.fullname)
                if not isinstance(generic, pytypes.GenericType):
                    raise CodeError(f"Unknown tuple base type: {true_type.type.fullname}", loc)
                return generic.parameterise(types, loc)
            case mypy.types.Instance() as inst:
                return self._resolve_type_from_name_and_args(
                    type_fullname=inst.type.fullname,
                    inst_args=inst.args,
                    loc=loc,
                )
            case mypy.types.UninhabitedType():
                raise CodeError("Cannot resolve empty type", loc)
            case mypy.types.UnionType(items=items):
                if not items:
                    raise CodeError("Cannot resolve empty type", loc)
                if len(items) > 1:
                    raise CodeError("Type unions are unsupported at this location", loc)
                return self.type_to_pytype(items[0], source_location=loc)
            case mypy.types.AnyType():
                # TODO: look at type_of_any to improve error message
                raise CodeError("Any type is not supported", loc)
            case _:
                raise CodeError(f"Unable to resolve mypy type {typ!r} to known algopy type", loc)

    def _resolve_type_from_name_and_args(
        self, type_fullname: str, inst_args: Sequence[mypy.types.Type] | None, loc: SourceLocation
    ) -> pytypes.PyType:
        if type_fullname in self.type_map:
            return self.type_map[type_fullname]

        result = pytypes.PyType.from_name(type_fullname)
        if result is None:
            raise CodeError(f"Unknown type: {type_fullname}", loc)
        if inst_args:
            if not isinstance(result, pytypes.GenericType):
                raise CodeError(f"{result.alias} does not take generic parameters", loc)
            type_args_resolved = list[pytypes.TypeArg]()
            for idx, ta in enumerate(inst_args):
                if isinstance(ta, mypy.types.AnyType):
                    raise CodeError(
                        f"Unresolved generic type parameter for {type_fullname} at index {idx}",
                        loc,
                    )
                if isinstance(ta, mypy.types.NoneType):
                    type_args_resolved.append(None)
                elif isinstance(ta, mypy.types.LiteralType):
                    if isinstance(ta.value, float):
                        raise CodeError(
                            f"float value encountered in typing.Literal: {ta.value}", loc
                        )
                    type_args_resolved.append(ta.value)
                else:
                    type_args_resolved.append(self.type_to_pytype(ta, source_location=loc))
            result = result.parameterise(type_args_resolved, loc)
        return result
