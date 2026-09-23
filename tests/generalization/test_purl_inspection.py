"""Tests for preservation_test.generalization.utils.purl_inspection."""

import pytest

from preservation_test.generalization.utils import purl_inspection

HASH = "a" * 64


def component(purl=None, with_hash=False, name="c"):
    item = {"bom-ref": name, "name": name}
    if purl is not None:
        item["purl"] = purl
    if with_hash:
        item["hashes"] = [{"alg": "SHA-256", "content": HASH}]
    return item


def cdx(components):
    return {"bomFormat": "CycloneDX", "specVersion": "1.4", "components": components}


def test_purl_type_extracts_type_segment():
    assert purl_inspection.purl_type("pkg:npm/lib@1") == "npm"
    assert purl_inspection.purl_type("pkg:Maven/g/a@1") == "maven"
    assert purl_inspection.purl_type("pkg:golang/github.com/x/y@v1") == "golang"


def test_assign_ecosystem_rule():
    assign = purl_inspection.assign_ecosystem
    assert assign({}) == purl_inspection.ECOSYSTEM_NONE
    assert assign({"npm": 3, "maven": 1}) == "npm"
    assert assign({"npm": 2, "maven": 2}) == "maven"  # tie broken lexically
    assert assign({"a": 1, "b": 1, "c": 1}) == purl_inspection.ECOSYSTEM_MIXED
    # two types, top covers exactly half: "under half" is strict, so not mixed
    assert assign({"npm": 1, "maven": 1}) == "maven"


def test_inspect_source_counts_purls_and_anchors():
    document = cdx(
        [
            component(purl="pkg:npm/lib@1", with_hash=True),
            component(purl="pkg:pypi/x@1", with_hash=False),
            component(purl=None, with_hash=True),
        ]
    )
    result = purl_inspection.inspect_source(document)
    assert result.adapter_format == "cyclonedx"
    assert result.purl_count == 2
    assert result.eligible_purl_count == 1  # only the anchored PURL
    assert result.purl_type_counts == {"npm": 1, "pypi": 1}


def test_inspect_source_empty_components():
    result = purl_inspection.inspect_source(cdx([]))
    assert result.purl_count == 0
    assert result.eligible_purl_count == 0
    assert result.purl_type_counts == {}


def test_inspect_source_raises_on_unloadable_document():
    with pytest.raises(purl_inspection.AdapterLoadError):
        purl_inspection.inspect_source({"neither": "spdx nor cyclonedx"})
