"""Unit tests for the forward engineering-validation release sweep."""

import json
from pathlib import Path
import subprocess

import pytest

from preservation_test.validation import release_sweep


def make_config(
    tmp_path: Path,
    *,
    source_sha256: str = "",
) -> release_sweep.SweepConfig:
    """Build a minimal release-sweep configuration for unit tests."""
    source_file = tmp_path / "source.spdx.json"
    source_file.write_text('{"spdxVersion": "SPDX-2.3"}\n', encoding="utf-8")

    if not source_sha256:
        source_sha256 = release_sweep.calculate_sha256(source_file)

    freeze_file = tmp_path / "FREEZE.md"
    freeze_file.write_text("frozen\n", encoding="utf-8")

    return release_sweep.SweepConfig(
        repository="https://github.com/CycloneDX/cyclonedx-cli",
        asset_name="cyclonedx-win-x64.exe",
        source_file=source_file,
        source_sha256=source_sha256,
        commitment_id="purl_preservation_v1",
        freeze_file=freeze_file,
        evaluator_module="preservation_test.evaluator.evaluate",
        artifact_directory=tmp_path / "artifacts",
        results_file=tmp_path / "results.json",
        binary_directory=tmp_path / "bin",
        example_component="tzdata",
        example_ref="SPDXRef-tzdata",
        example_source_purl="pkg:deb/debian/tzdata@1",
        command_timeout_seconds=30,
    )


def make_release(
    *,
    expected_execution: str = "completed",
    expected_verdict: str = "PRESERVED",
) -> release_sweep.ReleaseSpec:
    """Build one release specification for unit tests."""
    return release_sweep.ReleaseSpec(
        version="0.32.0",
        tag="v0.32.0",
        library_version="12.1.1",
        dependent_library_includes_purl_fix=True,
        expected_execution=expected_execution,
        expected_verdict=expected_verdict,
    )


def test_classify_transformation_failure_source_parse() -> None:
    error = RuntimeError(
        "could not be converted to CycloneDX.Spdx.Models.v2_3.ExternalRefCategory"
    )

    assert (
        release_sweep.classify_transformation_failure(error) == "source_parse_failure"
    )


def test_classify_transformation_failure_generic() -> None:
    error = RuntimeError("conversion failed")

    assert (
        release_sweep.classify_transformation_failure(error) == "transformation_failed"
    )


def test_calculate_sha256_is_uppercase(tmp_path: Path) -> None:
    path = tmp_path / "example.txt"
    path.write_text("abc", encoding="utf-8")

    observed = release_sweep.calculate_sha256(path)

    assert observed == (
        "BA7816BF8F01CFEA414140DE5DAE2223B00361A396177A9CB410FF61F20015AD"
    )


def test_verify_source_accepts_matching_digest(tmp_path: Path) -> None:
    config = make_config(tmp_path)

    release_sweep.verify_source(config)


def test_verify_source_rejects_missing_source(tmp_path: Path) -> None:
    config = make_config(tmp_path)
    config.source_file.unlink()

    with pytest.raises(FileNotFoundError, match="Preserved source does not exist"):
        release_sweep.verify_source(config)


def test_verify_source_rejects_digest_mismatch(tmp_path: Path) -> None:
    config = make_config(
        tmp_path,
        source_sha256="0" * 64,
    )

    with pytest.raises(RuntimeError, match="SHA-256 does not match"):
        release_sweep.verify_source(config)


def test_verify_freeze_accepts_existing_record(tmp_path: Path) -> None:
    config = make_config(tmp_path)

    release_sweep.verify_freeze(config)


def test_verify_freeze_rejects_missing_record(tmp_path: Path) -> None:
    config = make_config(tmp_path)
    config.freeze_file.unlink()

    with pytest.raises(FileNotFoundError, match="Freeze record does not exist"):
        release_sweep.verify_freeze(config)


def test_build_download_url() -> None:
    config = release_sweep.SweepConfig(
        repository="https://github.com/CycloneDX/cyclonedx-cli/",
        asset_name="cyclonedx-win-x64.exe",
        source_file=Path("source.json"),
        source_sha256="ABC",
        commitment_id="purl_preservation_v1",
        freeze_file=Path("FREEZE.md"),
        evaluator_module="example.evaluator",
        artifact_directory=Path("artifacts"),
        results_file=Path("results.json"),
        binary_directory=Path("bin"),
        example_component="example",
        example_ref="SPDXRef-example",
        example_source_purl="pkg:example/example@1",
        command_timeout_seconds=30,
    )
    release = make_release()

    assert release_sweep.build_download_url(config, release) == (
        "https://github.com/CycloneDX/cyclonedx-cli/"
        "releases/download/v0.32.0/cyclonedx-win-x64.exe"
    )


def test_run_command_returns_success(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    expected = subprocess.CompletedProcess(
        args=["example"],
        returncode=0,
        stdout="ok\n",
        stderr="",
    )

    def fake_run(
        arguments: list[str],
        **_: object,
    ) -> subprocess.CompletedProcess[str]:
        assert arguments == ["example"]
        return expected

    monkeypatch.setattr(release_sweep.subprocess, "run", fake_run)

    observed = release_sweep.run_command(["example"], 10)

    assert observed is expected


def test_run_command_reports_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    completed = subprocess.CompletedProcess(
        args=["example"],
        returncode=7,
        stdout="stdout text",
        stderr="stderr text",
    )

    monkeypatch.setattr(
        release_sweep.subprocess,
        "run",
        lambda *_args, **_kwargs: completed,
    )

    with pytest.raises(RuntimeError, match="Exit code: 7"):
        release_sweep.run_command(["example"], 10)


def test_get_cli_version(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    completed = subprocess.CompletedProcess(
        args=[],
        returncode=0,
        stdout="0.32.0+build\n",
        stderr="",
    )

    monkeypatch.setattr(
        release_sweep,
        "run_command",
        lambda _arguments, _timeout: completed,
    )

    observed = release_sweep.get_cli_version(
        tmp_path / "cyclonedx-cli.exe",
        30,
    )

    assert observed == "0.32.0+build"


def test_verify_cli_version_accepts_prefix() -> None:
    release_sweep.verify_cli_version(
        make_release(),
        "0.32.0+abcdef",
    )


def test_verify_cli_version_rejects_wrong_version() -> None:
    with pytest.raises(RuntimeError, match="Unexpected version"):
        release_sweep.verify_cli_version(
            make_release(),
            "0.31.0",
        )


def test_run_transformation_builds_expected_command(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    executable = tmp_path / "cyclonedx-cli.exe"
    source_file = tmp_path / "source.spdx.json"
    target_file = tmp_path / "nested" / "target.cdx.json"

    source_file.write_text("{}", encoding="utf-8")

    observed_arguments: list[str] = []

    def fake_run_command(
        arguments: list[str],
        _timeout_seconds: int,
    ) -> subprocess.CompletedProcess[str]:
        observed_arguments.extend(arguments)
        target_file.write_text(
            '{"bomFormat": "CycloneDX"}',
            encoding="utf-8",
        )
        return subprocess.CompletedProcess(
            args=arguments,
            returncode=0,
            stdout="",
            stderr="",
        )

    monkeypatch.setattr(
        release_sweep,
        "run_command",
        fake_run_command,
    )

    release_sweep.run_transformation(
        executable,
        source_file,
        target_file,
        30,
    )

    assert observed_arguments == [
        str(executable),
        "convert",
        "--input-format",
        "spdxjson",
        "--input-file",
        str(source_file),
        "--output-format",
        "json",
        "--output-file",
        str(target_file),
    ]


def test_run_transformation_requires_target(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setattr(
        release_sweep,
        "run_command",
        lambda arguments, timeout: subprocess.CompletedProcess(
            args=arguments,
            returncode=0,
            stdout="",
            stderr="",
        ),
    )

    with pytest.raises(RuntimeError, match="did not create"):
        release_sweep.run_transformation(
            tmp_path / "cyclonedx-cli.exe",
            tmp_path / "source.spdx.json",
            tmp_path / "target.cdx.json",
            30,
        )


def test_verify_target_accepts_cyclonedx(tmp_path: Path) -> None:
    target = tmp_path / "target.cdx.json"
    target.write_text(
        json.dumps(
            {
                "bomFormat": "CycloneDX",
                "specVersion": "1.6",
            }
        ),
        encoding="utf-8",
    )

    observed = release_sweep.verify_target(target)

    assert observed["bomFormat"] == "CycloneDX"
    assert observed["specVersion"] == "1.6"


def test_verify_target_rejects_other_json(tmp_path: Path) -> None:
    target = tmp_path / "target.json"
    target.write_text(
        '{"bomFormat": "SomethingElse"}',
        encoding="utf-8",
    )

    with pytest.raises(RuntimeError, match="not CycloneDX"):
        release_sweep.verify_target(target)


def test_run_evaluator_writes_json(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    config = make_config(tmp_path)
    result_file = tmp_path / "nested" / "result.json"

    completed = subprocess.CompletedProcess(
        args=[],
        returncode=0,
        stdout='{"results": [{"ref": "SPDXRef-example"}]}',
        stderr="",
    )

    monkeypatch.setattr(
        release_sweep,
        "run_command",
        lambda _arguments, _timeout: completed,
    )

    observed = release_sweep.run_evaluator(
        config,
        tmp_path / "target.cdx.json",
        result_file,
    )

    assert observed == {"results": [{"ref": "SPDXRef-example"}]}
    assert json.loads(result_file.read_text(encoding="utf-8")) == observed


def test_run_evaluator_rejects_non_json(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    config = make_config(tmp_path)

    completed = subprocess.CompletedProcess(
        args=[],
        returncode=0,
        stdout="not json",
        stderr="diagnostic",
    )

    monkeypatch.setattr(
        release_sweep,
        "run_command",
        lambda _arguments, _timeout: completed,
    )

    with pytest.raises(RuntimeError, match="did not emit valid JSON"):
        release_sweep.run_evaluator(
            config,
            tmp_path / "target.cdx.json",
            tmp_path / "result.json",
        )


def test_get_example_result() -> None:
    evaluator_result = {
        "results": [
            {
                "ref": "SPDXRef-example",
                "verdict": "PRESERVED",
            }
        ]
    }

    observed = release_sweep.get_example_result(
        evaluator_result,
        "SPDXRef-example",
    )

    assert observed["verdict"] == "PRESERVED"


def test_get_example_result_requires_results_list() -> None:
    with pytest.raises(TypeError, match="results list"):
        release_sweep.get_example_result(
            {"results": "wrong"},
            "SPDXRef-example",
        )


def test_get_example_result_requires_exactly_one_match() -> None:
    evaluator_result = {
        "results": [
            {"ref": "SPDXRef-other", "verdict": "PRESERVED"},
        ]
    }

    with pytest.raises(RuntimeError, match="found 0"):
        release_sweep.get_example_result(
            evaluator_result,
            "SPDXRef-example",
        )


def test_get_applicable_results_excludes_not_applicable() -> None:
    evaluator_result = {
        "results": [
            {"ref": "A", "verdict": "PRESERVED"},
            {"ref": "B", "verdict": "NOT_APPLICABLE"},
            {"ref": "C", "verdict": "VIOLATED_RELOCATED"},
        ]
    }

    observed = release_sweep.get_applicable_results(evaluator_result)

    assert [item["ref"] for item in observed] == ["A", "C"]


def test_get_applicable_results_requires_results_list() -> None:
    with pytest.raises(TypeError, match="results list"):
        release_sweep.get_applicable_results({"results": None})


def test_summarize_release_reports_matching_results(
    tmp_path: Path,
) -> None:
    config = make_config(tmp_path)
    release = make_release()

    executable = tmp_path / "cyclonedx-cli.exe"
    executable.write_bytes(b"binary")

    target_file = tmp_path / "target.cdx.json"
    target_file.write_text(
        '{"bomFormat": "CycloneDX", "specVersion": "1.6"}',
        encoding="utf-8",
    )

    evaluator_result = {
        "results": [
            {
                "ref": config.example_ref,
                "verdict": "PRESERVED",
                "purl": config.example_source_purl,
                "detail": "",
            },
            {
                "ref": "SPDXRef-other",
                "verdict": "NOT_APPLICABLE",
                "purl": None,
                "detail": "",
            },
        ]
    }

    summary = release_sweep.summarize_release(
        config=config,
        release=release,
        download_url="https://example.invalid/tool.exe",
        executable=executable,
        reported_version="0.32.0",
        target_file=target_file,
        target_document={
            "bomFormat": "CycloneDX",
            "specVersion": "1.6",
        },
        evaluator_result=evaluator_result,
    )

    assert summary["observed_verdict"] == "PRESERVED"
    assert summary["matches_expected"] is True
    assert summary["all_applicable_match_expected"] is True
    assert summary["applicable_result_count"] == 1
    assert summary["applicable_verdicts"] == ["PRESERVED"]
    assert summary["mismatches"] == []


def test_summarize_release_records_mismatch(
    tmp_path: Path,
) -> None:
    config = make_config(tmp_path)
    release = make_release(expected_verdict="PRESERVED")

    executable = tmp_path / "cyclonedx-cli.exe"
    executable.write_bytes(b"binary")

    target_file = tmp_path / "target.cdx.json"
    target_file.write_text(
        '{"bomFormat": "CycloneDX"}',
        encoding="utf-8",
    )

    evaluator_result = {
        "results": [
            {
                "ref": config.example_ref,
                "verdict": "VIOLATED_RELOCATED",
                "purl": config.example_source_purl,
                "detail": "wrong slot",
            }
        ]
    }

    summary = release_sweep.summarize_release(
        config=config,
        release=release,
        download_url="https://example.invalid/tool.exe",
        executable=executable,
        reported_version="0.32.0",
        target_file=target_file,
        target_document={"bomFormat": "CycloneDX"},
        evaluator_result=evaluator_result,
    )

    assert summary["matches_expected"] is False
    assert summary["all_applicable_match_expected"] is False
    assert summary["mismatches"] == [
        {
            "ref": config.example_ref,
            "verdict": "VIOLATED_RELOCATED",
            "purl": config.example_source_purl,
            "detail": "wrong slot",
        }
    ]


def test_write_results(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setattr(
        release_sweep,
        "REPOSITORY_ROOT",
        tmp_path,
    )

    config = make_config(tmp_path)

    releases = [
        {
            "matches_expected": True,
            "all_applicable_match_expected": True,
        }
    ]

    release_sweep.write_results(config, releases)

    document = json.loads(config.results_file.read_text(encoding="utf-8"))

    assert document["sweep_id"] == "cyclonedx-cli-424-release-sweep"
    assert document["evidence_role"] == "engineering_validation"
    assert document["commitment"] == "purl_preservation_v1"
    assert document["all_releases_match_expected"] is True
    assert document["releases"] == releases
