"""Minimal deterministic TOML writer for screening outputs.

Supports strings, booleans, integers, and lists of those. In a table or an
array-of-tables row, a dict value is written as a sub-table after the row's
scalar keys (e.g. [candidate.screening]). None values are omitted. Output uses
LF line endings and is byte-identical across reruns on identical inputs.
"""

from pathlib import Path
import re
from typing import Any

_BARE_KEY = re.compile(r"^[A-Za-z0-9_-]+$")
_ESCAPES = {
    "\\": "\\\\",
    '"': '\\"',
    "\b": "\\b",
    "\t": "\\t",
    "\n": "\\n",
    "\f": "\\f",
    "\r": "\\r",
}


def toml_key(key: str) -> str:
    """Render a key, quoting it when it is not a bare key."""
    return key if _BARE_KEY.match(key) else toml_string(key)


def toml_string(value: str) -> str:
    """Render a TOML basic string."""
    parts: list[str] = []
    for char in value:
        if char in _ESCAPES:
            parts.append(_ESCAPES[char])
        elif ord(char) < 0x20 or ord(char) == 0x7F:
            parts.append(f"\\u{ord(char):04X}")
        else:
            parts.append(char)
    return '"' + "".join(parts) + '"'


def toml_value(value: Any) -> str:
    """Render a supported TOML value."""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, str):
        return toml_string(value)
    if isinstance(value, list | tuple):
        return "[" + ", ".join(toml_value(item) for item in value) + "]"
    if isinstance(value, dict):
        if not value:
            return "{}"
        items = ", ".join(f"{toml_key(k)} = {toml_value(v)}" for k, v in value.items())
        return "{ " + items + " }"
    raise TypeError(f"unsupported TOML value: {value!r}")


def _pairs(table: dict[str, Any]) -> list[str]:
    return [
        f"{toml_key(key)} = {toml_value(value)}"
        for key, value in table.items()
        if value is not None and not isinstance(value, dict)
    ]


def _subtables(prefix: str, table: dict[str, Any]) -> list[str]:
    lines: list[str] = []
    for key, value in table.items():
        if isinstance(value, dict):
            name = f"{prefix}.{toml_key(key)}"
            lines += [f"[{name}]", *_pairs(value), *_subtables(name, value)]
    return lines


def render_document(
    header: list[str],
    tables: dict[str, dict[str, Any]],
    arrays: dict[str, list[dict[str, Any]]],
) -> str:
    """Render comment header, tables, then arrays of tables."""
    lines = [f"# {line}".rstrip() for line in header]
    for name, table in tables.items():
        key = toml_key(name)
        lines += ["", f"[{key}]", "", *_pairs(table), *_subtables(key, table)]
    for name, rows in arrays.items():
        key = toml_key(name)
        for row in rows:
            lines += ["", f"[[{key}]]", *_pairs(row), *_subtables(key, row)]
    return "\n".join(lines) + "\n"


def write_new_file(path: Path, text: str) -> None:
    """Write text with LF endings, refusing to overwrite an existing file."""
    if path.exists():
        raise FileExistsError(f"refusing to overwrite {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="\n") as handle:
        handle.write(text)
