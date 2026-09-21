"""Unit tests for the reverse exploratory engineering-validation sweep."""

from dataclasses import replace
import json
from pathlib import Path
import subprocess

import pytest

from preservation_test.evaluator.formats import Component
from preservation_test.validation import reverse_sweep


def make_config(
    tmp_path: Path,
    *,
    source_sha256: str = "",
) -> reverse_sweep.SweepConfig:
    """Build a temporary reverse-sweep configuration for unit tests."""
    config, _ = reverse_sweep.load_configuration(reverse_sweep.DEFAULT_CONFIG_FILE)

    source_file = tmp_path / "source.cdx.json"
    source_file.write_text(
        json.dumps(
            {
                "bomFormat": "CycloneDX",
                "specVersion": "1.2",
                "components": [],
            }
        ),
        encoding="utf-8",
    )

    if not source_sha256:
        source_sha256 = reverse_sweep.calculate_sha256(source_file)

    return replace(
        config,
        source_file=source_file,
        source_sha256=source_sha256,
        artifact_directory=tmp_path / "artifacts",
        results_file=tmp_path / "results.json",
        binary_directory=tmp_path / "bin",
    )


def make_release() -> reverse_sweep.ReleaseSpec:
    """Build one exploratory reverse release specification."""
    return reverse_sweep.ReleaseSpec(
        version="0.32.0",
        tag="v0.32.0",
        library_version="12.1.1",
        dependent_library_includes_purl_fix=True,
    )


def make_source_components() -> list[Component]:
    """Build source components for reverse-sweep summary tests."""
    return [
        Component(
            ref="A",
            anchors={("sha256", "a")},
            canonical_purls={"pkg:maven/example/a@1"},
            other_purls=set(),
        ),
        Component(
            ref="B",
            anchors={("sha256", "b")},
            canonical_purls={"pkg:maven/example/b@1"},
            other_purls=set(),
        ),
        Component(
            ref="C",
            anchors={("sha256", "c")},
            canonical_purls={"pkg:maven/example/c@1"},
            other_purls=set(),
        ),
        Component(
            ref="D",
            anchors={("sha256", "d")},
            canonical_purls={"pkg:maven/example/d@1"},
            other_purls=set(),
        ),
        Component(
            ref="E",
            anchors={("sha256", "e")},
            canonical_purls=set(),
            other_purls=set(),
        ),
    ]


def test_calculate_sha256_is_uppercase(tmp_path: Path) -> None:
    """SHA-256 output must use the recorded uppercase representation."""
    path = tmp_path / "example.txt"
    path.write_text("abc", encoding="utf-8")

    observed = reverse_sweep.calculate_sha256(path)

    assert observed == (
        "BA7816BF8F01CFEA414140DE5DAE2223B00361A396177A9CB410FF61F20015AD"
    )


def test_verify_source_accepts_matching_source(tmp_path: Path) -> None:
    """The preserved reverse source should verify when unchanged."""
    config = make_config(tmp_path)

    reverse_sweep.verify_source(config)


def test_verify_source_rejects_missing_source(tmp_path: Path) -> None:
    """A missing frozen source must stop the sweep."""
    config = make_config(tmp_path)
    config.source_file.unlink()

    with pytest.raises(FileNotFoundError):
        reverse_sweep.verify_source(config)


def test_verify_source_rejects_digest_mismatch(tmp_path: Path) -> None:
    """A changed reverse source must stop the sweep."""
    config = make_config(
        tmp_path,
        source_sha256="0" * 64,
    )

    with pytest.raises(RuntimeError, match="SHA-256"):
        reverse_sweep.verify_source(config)


def test_verify_freeze_accepts_frozen_record() -> None:
    """The configured frozen-apparatus record must exist."""
    reverse_sweep.verify_freeze()


def test_build_download_url() -> None:
    """Release downloads must use the selected immutable tag."""
    observed = reverse_sweep.build_download_url(
        make_release(),
    )

    assert observed.endswith("/releases/download/v0.32.0/cyclonedx-win-x64.exe")


def test_run_command_returns_success(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Successful external commands should return captured output."""
    expected = subprocess.CompletedProcess(
        args=["example"],
        returncode=0,
        stdout="ok\n",
        stderr="",
    )

    monkeypatch.setattr(
        reverse_sweep.subprocess,
        "run",
        lambda *_args, **_kwargs: expected,
    )

    observed = reverse_sweep.run_command(
        ["example"],
        10,
    )

    assert observed is expected


def test_run_command_reports_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Failed external commands must be surfaced as runtime errors."""
    completed = subprocess.CompletedProcess(
        args=["example"],
        returncode=7,
        stdout="stdout text",
        stderr="stderr text",
    )

    monkeypatch.setattr(
        reverse_sweep.subprocess,
        "run",
        lambda *_args, **_kwargs: completed,
    )

    with pytest.raises(RuntimeError, match="Exit code: 7"):
        reverse_sweep.run_command(
            ["example"],
            10,
        )


def test_get_cli_version(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """CLI version reporting should be normalized to stripped text."""
    completed = subprocess.CompletedProcess(
        args=[],
        returncode=0,
        stdout="0.32.0+build\n",
        stderr="",
    )

    monkeypatch.setattr(
        reverse_sweep,
        "run_command",
        lambda _arguments, _timeout: completed,
    )

    observed = reverse_sweep.get_cli_version(
        tmp_path / "cyclonedx-cli.exe",
    )

    assert observed == "0.32.0+build"


def test_verify_cli_version_accepts_prefix() -> None:
    """Build metadata may follow the configured release version."""
    reverse_sweep.verify_cli_version(
        make_release(),
        "0.32.0+abcdef",
    )


def test_verify_cli_version_rejects_wrong_version() -> None:
    """A binary from the wrong release must be rejected."""
    with pytest.raises(RuntimeError, match="Unexpected version"):
        reverse_sweep.verify_cli_version(
            make_release(),
            "0.31.0",
        )


def test_run_transformation_builds_reverse_command(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """The reverse sweep must invoke CycloneDX-to-SPDX conversion."""
    executable = tmp_path / "cyclonedx-cli.exe"
    source_file = tmp_path / "source.cdx.json"
    target_file = tmp_path / "nested" / "target.spdx.json"

    source_file.write_text("{}", encoding="utf-8")

    observed_arguments: list[str] = []

    def fake_run_command(
        arguments: list[str],
        _timeout_seconds: int,
    ) -> subprocess.CompletedProcess[str]:
        observed_arguments.extend(arguments)
        target_file.write_text(
            '{"spdxVersion": "SPDX-2.3"}',
            encoding="utf-8",
        )

        return subprocess.CompletedProcess(
            args=arguments,
            returncode=0,
            stdout="",
            stderr="",
        )

    monkeypatch.setattr(
        reverse_sweep,
        "run_command",
        fake_run_command,
    )

    reverse_sweep.run_transformation(
        executable,
        source_file,
        target_file,
    )

    assert observed_arguments == [
        str(executable),
        "convert",
        "--input-format",
        "json",
        "--input-file",
        str(source_file),
        "--output-format",
        "spdxjson",
        "--output-file",
        str(target_file),
    ]


def test_run_transformation_requires_target(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """A successful process without an output file is still a failure."""
    monkeypatch.setattr(
        reverse_sweep,
        "run_command",
        lambda arguments, timeout: subprocess.CompletedProcess(
            args=arguments,
            returncode=0,
            stdout="",
            stderr="",
        ),
    )

    with pytest.raises(RuntimeError, match="did not create"):
        reverse_sweep.run_transformation(
            tmp_path / "cyclonedx-cli.exe",
            tmp_path / "source.cdx.json",
            tmp_path / "target.spdx.json",
        )


def test_verify_target_accepts_spdx23(tmp_path: Path) -> None:
    """Generated SPDX 2.x JSON should be accepted."""
    target = tmp_path / "target.spdx.json"
    target.write_text(
        json.dumps(
            {
                "spdxVersion": "SPDX-2.3",
                "packages": [],
            }
        ),
        encoding="utf-8",
    )

    observed = reverse_sweep.verify_target(target)

    assert observed["spdxVersion"] == "SPDX-2.3"


def test_verify_target_rejects_non_spdx(tmp_path: Path) -> None:
    """A generated non-SPDX document must be rejected."""
    target = tmp_path / "target.json"
    target.write_text(
        '{"bomFormat": "CycloneDX"}',
        encoding="utf-8",
    )

    with pytest.raises(RuntimeError):
        reverse_sweep.verify_target(target)


def test_run_evaluator_writes_result(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Frozen evaluator output should be preserved verbatim as JSON."""
    config = make_config(tmp_path)
    result_file = tmp_path / "nested" / "result.json"

    completed = subprocess.CompletedProcess(
        args=[],
        returncode=0,
        stdout=json.dumps(
            {
                "source_format": "cyclonedx",
                "target_format": "spdx-2.3",
                "commitment": "purl_preservation_v1",
                "results": [],
            }
        ),
        stderr="",
    )

    monkeypatch.setattr(
        reverse_sweep,
        "run_command",
        lambda _arguments, _timeout: completed,
    )

    observed = reverse_sweep.run_evaluator(
        config,
        tmp_path / "target.spdx.json",
        result_file,
    )

    assert observed["source_format"] == "cyclonedx"
    assert observed["target_format"] == "spdx-2.3"

    persisted = json.loads(result_file.read_text(encoding="utf-8"))

    assert persisted == observed


def test_run_evaluator_rejects_non_json(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Non-JSON evaluator output must stop the sweep."""
    config = make_config(tmp_path)

    completed = subprocess.CompletedProcess(
        args=[],
        returncode=0,
        stdout="not json",
        stderr="diagnostic",
    )

    monkeypatch.setattr(
        reverse_sweep,
        "run_command",
        lambda _arguments, _timeout: completed,
    )

    with pytest.raises(RuntimeError, match="valid JSON"):
        reverse_sweep.run_evaluator(
            config,
            tmp_path / "target.spdx.json",
            tmp_path / "result.json",
        )


# def test_summarize_release_counts_outcomes(
#     tmp_path: Path,
# ) -> None:
#     """Summary counts must keep coverage and verdict classes distinct."""
#     release = make_release()

#     executable = tmp_path / "cyclonedx-cli.exe"
#     executable.write_bytes(b"binary")

#     target_file = tmp_path / "target.spdx.json"
#     target_file.write_text(
#         '{"spdxVersion": "SPDX-2.3"}',
#         encoding="utf-8",
#     )

#     evaluator_result = {
#         "results": [
#             {
#                 "ref": "A",
#                 "verdict": "PRESERVED",
#                 "purl": "pkg:maven/example/a@1",
#                 "detail": "",
#             },
#             {
#                 "ref": "B",
#                 "verdict": "VIOLATED_DROPPED",
#                 "purl": "pkg:maven/example/b@1",
#                 "detail": "missing",
#             },
#             {
#                 "ref": "C",
#                 "verdict": "UNANCHORABLE",
#                 "purl": "pkg:maven/example/c@1",
#                 "detail": "no anchor",
#             },
#             {
#                 "ref": "D",
#                 "verdict": "UNDERDETERMINED",
#                 "purl": "pkg:maven/example/d@1",
#                 "detail": "multiple values",
#             },
#             {
#                 "ref": "E",
#                 "verdict": "NOT_APPLICABLE",
#                 "purl": None,
#                 "detail": "",
#             },
#         ]
#     }

#     summary = reverse_sweep.summarize_release(
#         release=release,
#         download_url="https://example.invalid/tool.exe",
#         executable=executable,
#         reported_version="0.32.0",
#         target_file=target_file,
#         target_document={"spdxVersion": "SPDX-2.3"},
#         evaluator_result=evaluator_result,
#         source_components=make_source_components(),
#     )

#     assert summary["applicable_components"] == 4
#     assert summary["not_applicable_components"] == 1
#     assert summary["evaluable_components"] == 2

#     assert summary["preserved_components"] == 1
#     assert summary["violated_components"] == 1
#     assert summary["unanchorable_components"] == 1
#     assert summary["underdetermined_components"] == 1

#     assert summary["evaluable_fraction_of_applicable"] == pytest.approx(0.5)
#     assert summary["preserved_fraction_among_evaluable"] == pytest.approx(0.5)
#     assert summary["violation_fraction_among_evaluable"] == pytest.approx(0.5)

#     assert summary["verdict_counts"] == {
#         "NOT_APPLICABLE": 1,
#         "PRESERVED": 1,
#         "UNDERDETERMINED": 1,
#         "UNANCHORABLE": 1,
#         "VIOLATED_DROPPED": 1,
#     }

#     assert summary["violation_counts"] == {
#         "VIOLATED_DROPPED": 1,
#     }


def test_write_results(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Aggregate output must retain the exploratory evidence role."""
    monkeypatch.setattr(
        reverse_sweep,
        "REPOSITORY_ROOT",
        tmp_path,
    )

    freeze_file = tmp_path / "contracts" / "FREEZE_01_COMMITMENT_EVALUATOR.md"
    freeze_file.parent.mkdir(parents=True, exist_ok=True)
    freeze_file.write_text("frozen\n", encoding="utf-8")

    monkeypatch.setattr(
        reverse_sweep,
        "FREEZE_FILE",
        freeze_file,
    )

    config = make_config(tmp_path)

    releases = [
        {
            "version": "0.32.0",
            "observed_execution": "completed",
        }
    ]

    reverse_sweep.write_results(
        config,
        releases,
        source_components=make_source_components(),
    )

    document = json.loads(config.results_file.read_text(encoding="utf-8"))

    assert document["sweep_id"] == "cyclonedx-cli-reverse-sweep"
    assert document["direction"] == "cyclonedx_to_spdx"
    assert document["expectation_role"] == "exploratory"
    assert document["evidence_role"] == "engineering_validation"
    assert document["commitment"] == "purl_preservation_v1"
    assert document["releases"] == releases
