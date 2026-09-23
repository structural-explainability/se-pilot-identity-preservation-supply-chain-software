"""Tests for preservation_test.generalization.utils.source_detection."""

import json

from preservation_test.generalization.utils import source_detection
from preservation_test.generalization.utils.sampling_config import FormatsSpec

SourceFormat = source_detection.SourceFormat


def cdx(spec="1.4"):
    return {"bomFormat": "CycloneDX", "specVersion": spec, "components": []}


def spdx(version="SPDX-2.3"):
    return {"spdxVersion": version, "packages": []}


def test_parse_json_object_success():
    result = source_detection.parse_json_object(b'{"a": 1}')
    assert result.document == {"a": 1}
    assert result.error is None
    assert result.has_utf8_bom is False


def test_parse_json_object_utf8_bom():
    result = source_detection.parse_json_object(b"\xef\xbb\xbf{}")
    assert result.document == {}
    assert result.has_utf8_bom is True
    assert result.error is None


def test_parse_json_object_parse_failure():
    assert source_detection.parse_json_object(b"{nope").error == "json_parse_failure"
    assert source_detection.parse_json_object(b"\xff\xfe").error == "json_parse_failure"


def test_parse_json_object_not_an_object():
    assert source_detection.parse_json_object(b"[]").error == "not_json_object"
    assert source_detection.parse_json_object(b"42").error == "not_json_object"


def test_detect_cyclonedx():
    assert source_detection.detect_source_format(cdx("1.2")) == SourceFormat(
        "cyclonedx", "1.2"
    )
    assert source_detection.detect_source_format(
        {"bomFormat": "CycloneDX"}
    ) == SourceFormat("cyclonedx", None)


def test_detect_spdx_2x():
    assert source_detection.detect_source_format(spdx("SPDX-2.3")) == SourceFormat(
        "spdx", "SPDX-2.3"
    )
    assert source_detection.detect_source_format(spdx("SPDX-2.2")) == SourceFormat(
        "spdx", "SPDX-2.2"
    )


def test_detect_jsonld_spdx_vs_other():
    spdx3 = {"@context": "https://spdx.org/rdf/3.0.1/spdx-context.jsonld", "@graph": []}
    assert source_detection.detect_source_format(spdx3).standard == "spdx-3-jsonld"
    other = {"@context": "https://schema.org", "@graph": []}
    assert source_detection.detect_source_format(other).standard == "other-jsonld"


def test_detect_unknown():
    assert source_detection.detect_source_format({"hello": 1}).standard == "unknown"


def test_format_in_scope():
    formats = FormatsSpec(("SPDX-2.3",), ("1.2", "1.6"), "json")
    in_scope = source_detection.format_in_scope
    assert in_scope(SourceFormat("cyclonedx", "1.2"), formats)
    assert not in_scope(SourceFormat("cyclonedx", "1.7"), formats)
    assert in_scope(SourceFormat("spdx", "SPDX-2.3"), formats)
    assert not in_scope(SourceFormat("spdx", "SPDX-2.2"), formats)
    assert not in_scope(SourceFormat("cyclonedx", None), formats)
    assert not in_scope(SourceFormat("spdx-3-jsonld", "x"), formats)


def test_serialization_of():
    of = source_detection.serialization_of
    parse = source_detection.parse_json_object
    assert of(parse(b"{bad")) == "unparseable"
    assert of(parse(json.dumps({"@graph": []}).encode())) == "json-ld"
    assert of(parse(b"{}")) == "json"
    assert of(parse(b"[]")) == "json"


def test_expected_adapter_format_mapping():
    assert source_detection.EXPECTED_ADAPTER_FORMAT["cyclonedx"] == "cyclonedx"
    assert source_detection.EXPECTED_ADAPTER_FORMAT["spdx"] == "spdx-2.3"


def test_sbom_standards_membership():
    assert "cyclonedx" in source_detection.SBOM_STANDARDS
    assert "spdx" in source_detection.SBOM_STANDARDS
    assert "spdx-3-jsonld" in source_detection.SBOM_STANDARDS
    assert "unknown" not in source_detection.SBOM_STANDARDS
