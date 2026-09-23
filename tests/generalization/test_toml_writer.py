"""Tests for preservation_test.generalization.utils.toml_writer."""

import tomllib

import pytest

from preservation_test.generalization.utils import toml_writer


def test_toml_string_round_trips_specials():
    value = 'q"b\\t\tnl\ncr\rctrl\x01del\x7f'
    parsed = tomllib.loads(f"k = {toml_writer.toml_string(value)}")
    assert parsed["k"] == value


def test_toml_key_quotes_only_when_needed():
    assert toml_writer.toml_key("plain_key-1") == "plain_key-1"
    assert toml_writer.toml_key("a.b") == '"a.b"'
    assert toml_writer.toml_key("src/x.py") == '"src/x.py"'


def test_toml_value_scalars_and_lists():
    assert toml_writer.toml_value(True) == "true"
    assert toml_writer.toml_value(False) == "false"
    assert toml_writer.toml_value(7) == "7"
    assert toml_writer.toml_value("x") == '"x"'
    assert toml_writer.toml_value(["a", "b"]) == '["a", "b"]'
    assert toml_writer.toml_value(("a", 1)) == '["a", 1]'


def test_toml_value_inline_tables():
    assert toml_writer.toml_value({}) == "{}"
    assert toml_writer.toml_value({"x": 1}) == "{ x = 1 }"
    assert toml_writer.toml_value({"a.b": 1}) == '{ "a.b" = 1 }'


def test_toml_value_rejects_unsupported():
    with pytest.raises(TypeError):
        toml_writer.toml_value(1.5)
    with pytest.raises(TypeError):
        toml_writer.toml_value(None)


def test_render_document_shape_and_round_trip():
    text = toml_writer.render_document(
        header=["title", ""],
        tables={"meta": {"id": "x", "skip": None, "n": 2}},
        arrays={
            "row": [
                {"id": "r1", "tags": ["a"], "screening": {"ok": True, "why": []}},
                {"id": "r2", "tags": [], "screening": {"ok": False, "why": ["no"]}},
            ]
        },
    )
    assert "\r" not in text
    assert text.endswith("\n")
    assert text.startswith("# title\n")
    parsed = tomllib.loads(text)
    assert parsed["meta"] == {"id": "x", "n": 2}  # None omitted
    assert parsed["row"][0]["screening"] == {"ok": True, "why": []}
    assert parsed["row"][1]["screening"]["why"] == ["no"]


def test_render_document_is_deterministic():
    kwargs = {
        "header": ["h"],
        "tables": {"meta": {"a": 1, "b": "two"}},
        "arrays": {"row": [{"id": "r1", "screening": {"ok": True}}]},
    }
    assert toml_writer.render_document(**kwargs) == toml_writer.render_document(
        **kwargs
    )


def test_write_new_file_writes_lf_and_refuses_overwrite(tmp_path):
    path = tmp_path / "sub" / "out.toml"
    toml_writer.write_new_file(path, "a = 1\n")
    assert path.read_bytes() == b"a = 1\n"  # LF, no rewrite
    with pytest.raises(FileExistsError):
        toml_writer.write_new_file(path, "a = 2\n")
    assert path.read_bytes() == b"a = 1\n"
