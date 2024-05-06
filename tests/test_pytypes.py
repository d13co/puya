import re

import pytest

from puya.awst_build import pytypes
from tests import VCS_ROOT

_STUB_SUFFIX = ".pyi"


def stub_class_names_and_predefined_aliases() -> list[str]:
    stubs_dir = VCS_ROOT / "stubs" / "algopy-stubs"
    result = []

    for pyi_path in stubs_dir.rglob(f"*{_STUB_SUFFIX}"):
        assert pyi_path.is_file()
        rel_path = pyi_path.relative_to(stubs_dir).with_suffix("")
        module_name = "algopy." + ".".join(rel_path.parts).removesuffix(".__init__")
        with pyi_path.open() as fp:
            for ln in fp:
                m = re.match(r"class ([^_][^:(]+)", ln)
                if m:
                    (class_name,) = m.groups()
                    result.append(".".join((module_name, class_name)))
    return result


@pytest.mark.parametrize(
    "fullname",
    stub_class_names_and_predefined_aliases(),
    ids=str,
)
def test_stub_class_names_lookup(fullname: str) -> None:
    assert pytypes.lookup(fullname) is not None, f"{fullname} is missing from pytypes"
