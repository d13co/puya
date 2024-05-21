import contextlib
from collections.abc import Iterable, Mapping
from pathlib import Path

from puya.errors import PuyaError
from puya.options import PuyaOptions


def get_template_vars(options: PuyaOptions) -> Mapping[str, int | bytes]:
    """Gets template values from puya options"""
    return dict(
        (
            *_load_template_vars(options.template_vars_path, options.template_vars_prefix).items(),
            *_parse_template_vars(options.template_vars, options.template_vars_prefix).items(),
        )
    )


def _load_template_vars(path: Path | None, prefix: str) -> Mapping[str, int | bytes]:
    """Load template vars from specified path, using provided prefix by default"""
    if path is None:
        return {}
    # extract config from file, but leave values unparsed
    template_vars = dict(
        map(
            _split_template_line,
            (line for line in path.read_text().splitlines() if not line.strip().startswith("#")),
        )
    )
    # use prefix override if present in file
    if (prefix_override := _pop_prefix_from_vars(template_vars, path)) is not None:
        prefix = prefix_override
    return {prefix + name: _parse_template_value(value) for name, value in template_vars.items()}


def _pop_prefix_from_vars(template_vars: dict[str, str], path: Path) -> str | None:
    try:
        template_prefix = template_vars.pop("prefix")
    except KeyError:
        return None
    parsed_prefix = _parse_str(template_prefix)
    if parsed_prefix is None:
        raise PuyaError(
            f"Invalid template configuration ({path}),"
            f' prefix must be a string e.g. prefix="TMPL_"'
        )
    return parsed_prefix


def _parse_template_vars(template_vars: Iterable[str], prefix: str) -> dict[str, int | bytes]:
    return {
        prefix + name: _parse_template_value(value)
        for name, value in map(_split_template_line, template_vars)
    }


def _split_template_line(line: str) -> tuple[str, str]:
    try:
        name, value_str = line.split("=", maxsplit=1)
    except ValueError as ex:
        raise PuyaError(f"Invalid template var definition: {line=!r}") from ex
    return name, value_str


def _parse_str(value: str) -> str | None:
    if value.startswith('"') and value.endswith('"'):
        return value[1:-1]
    else:
        return None


def _parse_bytes(value_str: str) -> bytes | None:
    value = None
    if value_str.startswith("0x"):
        with contextlib.suppress(ValueError):
            value = bytes.fromhex(value_str[2:])
    return value


def _parse_int(value_str: str) -> int | None:
    try:
        return int(value_str)
    except ValueError:
        return None


def _parse_template_value(value_str: str) -> int | bytes:
    value: int | bytes | None
    if (str_ := _parse_str(value_str)) is not None:
        value = str_.encode("utf8")
    elif (bytes_ := _parse_bytes(value_str)) is not None:
        value = bytes_
    else:
        value = _parse_int(value_str)
    if value is None:
        raise PuyaError(f"Invalid template var definition: {value_str}")
    return value
