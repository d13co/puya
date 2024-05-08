from collections.abc import Mapping, Sequence
from functools import cached_property

import attrs

from puya.context import CompileContext
from puya.ir import models as ir
from puya.mir import models
from puya.mir.vla import VariableLifetimeAnalysis
from puya.utils import attrs_extend


@attrs.define
class MIRContext(CompileContext):
    all_artifacts: Sequence[ir.ModuleArtifact]

    @cached_property
    def all_programs(self) -> Mapping[str, ir.Program]:
        return {p.id: p for artifact in self.all_artifacts for p in artifact.all_programs()}

    @cached_property
    def all_contracts(self) -> Mapping[str, ir.Contract]:
        return {c.metadata.full_name: c for c in self.all_artifacts if isinstance(c, ir.Contract)}


@attrs.define(kw_only=True)
class ProgramMIRContext(MIRContext):
    program: ir.Program
    subroutine_names: Mapping[ir.Subroutine, str] = attrs.field(init=False)
    current_assembles: list[str] = attrs.field(factory=list)

    @subroutine_names.default
    def _get_short_subroutine_names(self) -> dict[ir.Subroutine, str]:
        """Return a mapping of unique TEAL names for all subroutines in program, while attempting
        to use the shortest name possible"""
        names = dict[ir.Subroutine, str]()
        names[self.program.main] = "main"
        seen_names = set(names.values())
        for subroutine in self.program.subroutines:
            name: str
            if subroutine.method_name not in seen_names:
                name = subroutine.method_name
            elif (
                subroutine.class_name is not None
                and (class_prefixed := f"{subroutine.class_name}.{subroutine.method_name}")
                not in seen_names
            ):
                name = class_prefixed
            else:
                name = subroutine.full_name
            assert name not in seen_names
            names[subroutine] = name
            seen_names.add(name)

        return names

    def for_subroutine(self, subroutine: models.MemorySubroutine) -> "SubroutineCodeGenContext":
        return attrs_extend(SubroutineCodeGenContext, self, subroutine=subroutine)


@attrs.define(frozen=False)
class SubroutineCodeGenContext(ProgramMIRContext):
    subroutine: models.MemorySubroutine
    _vla: VariableLifetimeAnalysis | None = None

    @property
    def vla(self) -> VariableLifetimeAnalysis:
        if self._vla is None:
            self._vla = VariableLifetimeAnalysis.analyze(self.subroutine)
        return self._vla

    def invalidate_vla(self) -> None:
        self._vla = None
