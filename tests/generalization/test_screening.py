"""Source-only screening tests against a synthetic git repository."""

import json
from pathlib import Path
import subprocess
import tomllib

import pytest

from preservation_test.generalization import p01_build_candidates, p02_build_corpus
from preservation_test.generalization.utils.hashing import (
    normalize_sha256,
    sha256_bytes,
)
from preservation_test.generalization.utils.purl_inspection import assign_ecosystem
from preservation_test.generalization.utils.sampling_config import (
    SamplingConfigError,
    load_sampling_config,
)
from preservation_test.generalization.utils.toml_writer import toml_string, toml_value

HASH = "a" * 64


def _cdx(spec: str, name: str, version: str, purl: str, with_hash: bool) -> dict:
    component: dict = {"bom-ref": "c1", "name": "lib", "purl": purl}
    if with_hash:
        component["hashes"] = [{"alg": "SHA-256", "content": HASH}]
    return {
        "bomFormat": "CycloneDX",
        "specVersion": spec,
        "metadata": {
            "component": {"group": "org.example", "name": name, "version": version}
        },
        "components": [component],
    }


def _spdx(version: str) -> dict:
    return {
        "spdxVersion": version,
        "SPDXID": "SPDXRef-DOCUMENT",
        "documentDescribes": ["SPDXRef-app"],
        "packages": [
            {
                "SPDXID": "SPDXRef-app",
                "name": "app",
                "versionInfo": "2.0",
                "checksums": [{"algorithm": "SHA256", "checksumValue": HASH}],
                "externalRefs": [
                    {
                        "referenceCategory": "PACKAGE-MANAGER",
                        "referenceType": "purl",
                        "referenceLocator": "pkg:npm/app@2.0",
                    }
                ],
            }
        ],
    }


FILES: dict[str, bytes] = {
    "a/bom.1.3.json": json.dumps(
        _cdx("1.3", "demo", "1.0", "pkg:maven/x/lib@1", True)
    ).encode(),
    "a/bom.1.4.json": json.dumps(
        _cdx("1.4", "demo", "1.0", "pkg:maven/x/lib@1", True)
    ).encode(),
    "b/nohash.json": json.dumps(
        _cdx("1.4", "other", "1.0", "pkg:npm/lib@1", False)
    ).encode(),
    "c/future.json": json.dumps(
        _cdx("1.7", "future", "1.0", "pkg:npm/lib@1", True)
    ).encode(),
    "d/excluded.json": json.dumps(
        _cdx("1.4", "skip-me", "9", "pkg:npm/lib@1", True)
    ).encode(),
    "e/sbom.spdx.json": json.dumps(_spdx("SPDX-2.3")).encode(),
    "f/old.spdx.json": json.dumps(_spdx("SPDX-2.2")).encode(),
    "g/broken.json": b"{not json",
    "h/list.json": b"[]",
    "i/readme.md": b"not a candidate",
}


def _git(cwd: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=cwd, check=True, capture_output=True, text=True
    ).stdout.strip()


@pytest.fixture
def frame(tmp_path: Path) -> tuple[Path, Path, str]:
    clone_root = tmp_path / "clones"
    repo = clone_root / "examples"
    repo.mkdir(parents=True)
    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "t@example.org")
    _git(repo, "config", "user.name", "t")
    _git(repo, "config", "core.autocrlf", "false")
    _git(repo, "remote", "add", "origin", "https://github.com/Example/examples.git")
    for path, data in FILES.items():
        target = repo / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "fixture")
    return tmp_path, clone_root, _git(repo, "rev-parse", "HEAD")


def _config_text(revision: str, extra: str = "") -> str:
    return f"""
schema_version = 1
sampling_id = "test"
[sampling_frame]
[[sampling_frame.repository]]
name = "Example/examples"
url = "https://github.com/Example/examples.git"
revision = "{revision}"
[sampling_frame.enumeration]
path_filter = "*.json"
content_source = "git blob at fixed revision"
[formats]
spdx_versions = ["SPDX-2.3"]
cyclonedx_spec_versions = ["1.2", "1.3", "1.4", "1.5", "1.6"]
serialization = "json"
[unit]
selection_unit = "source_standard + subject"
one_document_per_unit = "lowest source SHA-256 among eligible documents for the same source_standard and subject"
[selection]
method = "census-of-eligible-units"
[selection_boundary]
transform_before_selection_complete = false
[[validation_exclusion]]
kind = "subject"
value = "org.example/skip-me@9"
reason = "used-in-engineering-validation"
provenance = "test"
{extra}
"""


def test_candidate_and_corpus_pipeline_end_to_end(frame, monkeypatch):
    tmp_path, clone_root, revision = frame
    config_path = tmp_path / "01.toml"
    config_path.write_text(_config_text(revision), encoding="utf-8")

    # The synthetic repository is intentionally independent of this
    # repository's real engineering-validation exclusion inventory.
    monkeypatch.setattr(
        p01_build_candidates,
        "missing_exclusions",
        lambda config, derived: [],
    )

    candidates_out = tmp_path / "02.toml"
    corpus_out = tmp_path / "03.toml"

    p01_args = [
        "--config",
        str(config_path),
        "--clone-root",
        str(clone_root),
        "--out",
        str(candidates_out),
    ]
    assert p01_build_candidates.main(p01_args) == 0

    p02_args = [
        "--config",
        str(config_path),
        "--candidates",
        str(candidates_out),
        "--out",
        str(corpus_out),
    ]
    assert p02_build_corpus.main(p02_args) == 0

    candidates = {
        row["repository_relative_path"]: row
        for row in tomllib.loads(candidates_out.read_text(encoding="utf-8"))[
            "candidate"
        ]
    }
    assert "i/readme.md" not in candidates
    assert candidates["b/nohash.json"]["screening"]["exclusion_reasons"] == [
        "no_component_with_canonical_purl_and_anchor"
    ]
    assert candidates["c/future.json"]["screening"]["exclusion_reasons"] == [
        "format_not_in_scope"
    ]
    assert candidates["f/old.spdx.json"]["screening"]["exclusion_reasons"] == [
        "format_not_in_scope"
    ]
    assert candidates["d/excluded.json"]["screening"]["exclusion_reasons"] == [
        "validation_subject"
    ]
    assert candidates["g/broken.json"]["screening"]["exclusion_reasons"] == [
        "json_parse_failure"
    ]
    assert candidates["h/list.json"]["screening"]["exclusion_reasons"] == [
        "not_json_object"
    ]
    assert candidates["e/sbom.spdx.json"]["subject"] == "app@2.0"
    assert candidates["e/sbom.spdx.json"]["package_ecosystem"] == "npm"
    assert candidates["e/sbom.spdx.json"]["purl_types"] == ["npm"]
    assert candidates["e/sbom.spdx.json"]["eligible_purl_count"] == 1
    assert candidates["b/nohash.json"]["purl_count"] == 1
    assert candidates["b/nohash.json"]["eligible_purl_count"] == 0
    assert candidates["g/broken.json"]["source_format"] == "unparseable"
    excluded = candidates["d/excluded.json"]["screening"]
    assert excluded["used_in_engineering_validation"] is True
    assert excluded["known_preservation_defect"] is False
    assert candidates["a/bom.1.3.json"]["screening"]["eligible"] is True
    assert candidates["a/bom.1.3.json"]["sha256"] == sha256_bytes(
        FILES["a/bom.1.3.json"]
    )

    corpus = tomllib.loads(corpus_out.read_text(encoding="utf-8"))
    members = {member["unit"]: member for member in corpus["member"]}
    assert set(members) == {"cyclonedx | org.example/demo@1.0", "spdx | app@2.0"}
    demo = members["cyclonedx | org.example/demo@1.0"]
    expected = min(
        ("a/bom.1.3.json", "a/bom.1.4.json"), key=lambda p: sha256_bytes(FILES[p])
    )
    assert demo["repository_relative_path"] == expected
    assert len(demo["collapsed_candidate_ids"]) == 1

    assert p01_build_candidates.main(p01_args) == 2
    assert p02_build_corpus.main(p02_args) == 2


def test_config_rejects_placeholders(frame):
    tmp_path, _, revision = frame
    text = _config_text(revision).replace(
        'value = "org.example/skip-me@9"', 'value = "..."'
    )
    path = tmp_path / "bad.toml"
    path.write_text(text, encoding="utf-8")
    with pytest.raises(SamplingConfigError):
        load_sampling_config(path)


def test_config_rejects_short_revision(frame):
    tmp_path, _, revision = frame
    path = tmp_path / "bad.toml"
    path.write_text(_config_text(revision[:12]), encoding="utf-8")
    with pytest.raises(SamplingConfigError):
        load_sampling_config(path)


def test_ecosystem_rule():
    assert assign_ecosystem({}) == "none"
    assert assign_ecosystem({"npm": 2, "maven": 2}) == "maven"
    assert assign_ecosystem({"npm": 1, "maven": 1, "pypi": 1}) == "mixed"


def test_toml_writer_escapes():
    assert toml_string('a"b\\c\n') == '"a\\"b\\\\c\\n"'
    assert toml_value({"a.b": 1}) == '{ "a.b" = 1 }'
    assert toml_value([True, 3, "x"]) == '[true, 3, "x"]'


def test_normalize_sha256():
    assert normalize_sha256(HASH.upper()) == HASH
    with pytest.raises(ValueError):
        normalize_sha256("abc")
