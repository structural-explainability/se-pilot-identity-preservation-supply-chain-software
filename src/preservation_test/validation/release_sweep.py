"""Run the CycloneDX CLI issue #424 engineering-validation release sweep.

Run from root project folder with:

uv run python -m preservation_test.validation.release_sweep

"""

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tomllib
from typing import Any
import urllib.request

REPOSITORY_ROOT = Path(__file__).resolve().parents[3]

DEFAULT_CONFIG_FILE = (
    REPOSITORY_ROOT / "validation" / "cyclonedx-cli-424-release-sweep" / "releases.toml"
)


@dataclass(frozen=True)
class SweepConfig:
    """Configuration shared by every release in the sweep."""

    repository: str
    asset_name: str
    source_file: Path
    source_sha256: str
    commitment_id: str
    freeze_file: Path
    evaluator_module: str
    artifact_directory: Path
    results_file: Path
    binary_directory: Path
    example_component: str
    example_ref: str
    example_source_purl: str
    command_timeout_seconds: int


@dataclass(frozen=True)
class ReleaseSpec:
    """One explicitly selected CycloneDX CLI release."""

    version: str
    tag: str
    library_version: str
    dependent_library_includes_purl_fix: bool
    expected_execution: str
    expected_verdict: str


def resolve_repository_path(value: str) -> Path:
    """Resolve a repository-relative path."""

    return REPOSITORY_ROOT / value


def load_configuration(
    config_file: Path,
) -> tuple[SweepConfig, list[ReleaseSpec]]:
    """Load the release-sweep configuration."""

    with config_file.open("rb") as handle:
        document = tomllib.load(handle)

    sweep = document["sweep"]

    config = SweepConfig(
        repository=str(sweep["repository"]),
        asset_name=str(sweep["asset_name"]),
        source_file=resolve_repository_path(str(sweep["source_file"])),
        source_sha256=str(sweep["source_sha256"]).upper(),
        commitment_id=str(sweep["commitment_id"]),
        freeze_file=resolve_repository_path(str(sweep["freeze_file"])),
        evaluator_module=str(sweep["evaluator_module"]),
        artifact_directory=resolve_repository_path(str(sweep["artifact_directory"])),
        results_file=resolve_repository_path(str(sweep["results_file"])),
        binary_directory=resolve_repository_path(str(sweep["binary_directory"])),
        example_component=str(sweep["example_component"]),
        example_ref=str(sweep["example_ref"]),
        example_source_purl=str(sweep["example_source_purl"]),
        command_timeout_seconds=int(sweep["command_timeout_seconds"]),
    )

    releases = [
        ReleaseSpec(
            version=str(item["version"]),
            tag=str(item["tag"]),
            library_version=str(item["library_version"]),
            dependent_library_includes_purl_fix=bool(
                item["dependent_library_includes_purl_fix"]
            ),
            expected_execution=str(item["expected_execution"]),
            expected_verdict=str(item["expected_verdict"]),
        )
        for item in document["release"]
    ]

    return config, releases


def classify_transformation_failure(error: RuntimeError) -> str:
    """Classify a failed historical CLI transformation."""

    message = str(error)

    if (
        "could not be converted to "
        "CycloneDX.Spdx.Models.v2_3.ExternalRefCategory" in message
    ):
        return "source_parse_failure"

    return "transformation_failed"


def calculate_sha256(path: Path) -> str:
    """Calculate the uppercase SHA-256 digest of a file."""

    digest = hashlib.sha256()

    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)

    return digest.hexdigest().upper()


def verify_source(config: SweepConfig) -> None:
    """Verify that the preserved source is unchanged."""

    if not config.source_file.is_file():
        raise FileNotFoundError(
            f"Preserved source does not exist: {config.source_file}"
        )

    observed_sha256 = calculate_sha256(config.source_file)

    if observed_sha256 != config.source_sha256:
        raise RuntimeError(
            "Preserved source SHA-256 does not match releases.toml.\n"
            f"Expected: {config.source_sha256}\n"
            f"Observed: {observed_sha256}"
        )


def verify_freeze(config: SweepConfig) -> None:
    """Verify that the configured freeze record exists."""

    if not config.freeze_file.is_file():
        raise FileNotFoundError(f"Freeze record does not exist: {config.freeze_file}")


def build_download_url(
    config: SweepConfig,
    release: ReleaseSpec,
) -> str:
    """Build the GitHub release-asset URL."""

    repository = config.repository.rstrip("/")

    return f"{repository}/releases/download/{release.tag}/{config.asset_name}"


def download_file(
    url: str,
    destination: Path,
) -> None:
    """Download one release asset unless it is already present."""

    if destination.is_file():
        return

    destination.parent.mkdir(parents=True, exist_ok=True)

    request = urllib.request.Request(
        url,
        headers={"User-Agent": "se-pilot-identity-preservation-release-sweep"},
    )

    with (
        urllib.request.urlopen(request) as response,
        destination.open("wb") as output,
    ):
        while block := response.read(1024 * 1024):
            output.write(block)


def run_command(
    arguments: list[str],
    timeout_seconds: int,
) -> subprocess.CompletedProcess[str]:
    """Run an external command and report failures with captured output."""

    completed = subprocess.run(
        arguments,
        check=False,
        capture_output=True,
        text=True,
        timeout=timeout_seconds,
        cwd=REPOSITORY_ROOT,
    )

    if completed.returncode != 0:
        command = " ".join(arguments)

        raise RuntimeError(
            "External command failed.\n"
            f"Exit code: {completed.returncode}\n"
            f"Command: {command}\n"
            f"stdout:\n{completed.stdout}\n"
            f"stderr:\n{completed.stderr}"
        )

    return completed


def get_cli_version(
    executable: Path,
    timeout_seconds: int,
) -> str:
    """Return the version string reported by a CLI executable."""

    completed = run_command(
        [str(executable), "--version"],
        timeout_seconds,
    )

    return completed.stdout.strip()


def verify_cli_version(
    release: ReleaseSpec,
    reported_version: str,
) -> None:
    """Confirm that the executable reports the selected release version."""

    if not reported_version.startswith(release.version):
        raise RuntimeError(
            f"Unexpected version for {release.tag}.\n"
            f"Expected prefix: {release.version}\n"
            f"Observed: {reported_version}"
        )


def run_transformation(
    executable: Path,
    source_file: Path,
    target_file: Path,
    timeout_seconds: int,
) -> None:
    """Transform the preserved SPDX source to CycloneDX JSON."""

    target_file.parent.mkdir(parents=True, exist_ok=True)

    if target_file.exists():
        target_file.unlink()

    run_command(
        [
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
        ],
        timeout_seconds,
    )

    if not target_file.is_file():
        raise RuntimeError(f"CLI did not create the expected target: {target_file}")


def verify_target(target_file: Path) -> dict[str, Any]:
    """Parse the generated target and verify that it is CycloneDX JSON."""

    with target_file.open(
        "r",
        encoding="utf-8-sig",
    ) as handle:
        document: dict[str, Any] = json.load(handle)

    if document.get("bomFormat") != "CycloneDX":
        raise RuntimeError(f"Generated target is not CycloneDX: {target_file}")

    return document


def run_evaluator(
    config: SweepConfig,
    target_file: Path,
    result_file: Path,
) -> dict[str, Any]:
    """Run the frozen evaluator and preserve its complete JSON output."""

    completed = run_command(
        [
            sys.executable,
            "-m",
            config.evaluator_module,
            str(config.source_file),
            str(target_file),
            "--json",
        ],
        config.command_timeout_seconds,
    )

    try:
        result: dict[str, Any] = json.loads(completed.stdout)
    except json.JSONDecodeError as error:
        raise RuntimeError(
            "Evaluator did not emit valid JSON.\n"
            f"stdout:\n{completed.stdout}\n"
            f"stderr:\n{completed.stderr}"
        ) from error

    result_file.parent.mkdir(parents=True, exist_ok=True)

    result_file.write_text(
        json.dumps(result, indent=2) + "\n",
        encoding="utf-8",
    )

    return result


def get_example_result(
    evaluator_result: dict[str, Any],
    example_ref: str,
) -> dict[str, Any]:
    """Return the evaluator result for the historical example component."""

    results = evaluator_result.get("results")

    if not isinstance(results, list):
        raise TypeError("Evaluator result does not contain a results list.")

    matches = [
        item
        for item in results
        if isinstance(item, dict) and item.get("ref") == example_ref
    ]

    if len(matches) != 1:
        raise RuntimeError(
            "Expected exactly one evaluator result for historical "
            f"example ref {example_ref!r}; found {len(matches)}."
        )

    return matches[0]


def get_applicable_results(
    evaluator_result: dict[str, Any],
) -> list[dict[str, Any]]:
    """Return evaluator results to which the commitment applies."""

    results = evaluator_result.get("results")

    if not isinstance(results, list):
        raise TypeError("Evaluator result does not contain a results list.")

    return [
        item
        for item in results
        if isinstance(item, dict) and item.get("verdict") != "NOT_APPLICABLE"
    ]


def summarize_release(
    *,
    config: SweepConfig,
    release: ReleaseSpec,
    download_url: str,
    executable: Path,
    reported_version: str,
    target_file: Path,
    target_document: dict[str, Any],
    evaluator_result: dict[str, Any],
) -> dict[str, Any]:
    """Build the aggregate result for one release."""

    example_result = get_example_result(
        evaluator_result,
        config.example_ref,
    )

    observed_verdict = str(example_result.get("verdict"))

    applicable_results = get_applicable_results(evaluator_result)

    applicable_verdicts = sorted(
        {str(item.get("verdict")) for item in applicable_results}
    )

    mismatches = [
        {
            "ref": item.get("ref"),
            "verdict": item.get("verdict"),
            "purl": item.get("purl"),
            "detail": item.get("detail"),
        }
        for item in applicable_results
        if item.get("verdict") != release.expected_verdict
    ]

    return {
        "version": release.version,
        "tag": release.tag,
        "library_version": release.library_version,
        "download_url": download_url,
        "reported_version": reported_version,
        "executable_sha256": calculate_sha256(executable),
        "target_sha256": calculate_sha256(target_file),
        "target_bom_format": target_document.get("bomFormat"),
        "target_spec_version": target_document.get("specVersion"),
        "expected_verdict": release.expected_verdict,
        "observed_verdict": observed_verdict,
        "matches_expected": observed_verdict == release.expected_verdict,
        "all_applicable_match_expected": len(mismatches) == 0,
        "applicable_verdicts": applicable_verdicts,
        "applicable_result_count": len(applicable_results),
        "mismatches": mismatches,
    }


def run_release(
    config: SweepConfig,
    release: ReleaseSpec,
) -> dict[str, Any]:
    """Download, execute, evaluate, and summarize one release."""

    executable = config.binary_directory / f"cyclonedx-cli-{release.version}.exe"

    release_directory = config.artifact_directory / release.version

    target_file = release_directory / "target.cdx.json"
    result_file = release_directory / "result.json"

    download_url = build_download_url(config, release)

    print(
        f"[{release.version}] "
        f"Spdx.Interop {release.library_version} "
        f"expected_execution={release.expected_execution} "
        f"expected_verdict={release.expected_verdict or 'none'}"
    )

    download_file(download_url, executable)

    reported_version = get_cli_version(
        executable,
        config.command_timeout_seconds,
    )

    verify_cli_version(release, reported_version)

    executable_sha256 = calculate_sha256(executable)

    try:
        run_transformation(
            executable,
            config.source_file,
            target_file,
            config.command_timeout_seconds,
        )
    except RuntimeError as error:
        observed_execution = classify_transformation_failure(error)

        matches_expected = observed_execution == release.expected_execution

        summary = {
            "version": release.version,
            "tag": release.tag,
            "library_version": release.library_version,
            "dependent_library_includes_purl_fix": (
                release.dependent_library_includes_purl_fix
            ),
            "download_url": download_url,
            "reported_version": reported_version,
            "executable_sha256": executable_sha256,
            "expected_execution": release.expected_execution,
            "observed_execution": observed_execution,
            "expected_verdict": release.expected_verdict or None,
            "observed_verdict": None,
            "matches_expected": matches_expected,
            "all_applicable_match_expected": matches_expected,
            "target_sha256": None,
            "target_bom_format": None,
            "target_spec_version": None,
            "applicable_verdicts": [],
            "applicable_result_count": 0,
            "mismatches": [],
            "error": str(error),
        }

        print(
            f"[{release.version}] "
            f"execution={observed_execution} "
            f"match={matches_expected}"
        )

        return summary

    target_document = verify_target(target_file)

    evaluator_result = run_evaluator(
        config,
        target_file,
        result_file,
    )

    summary = summarize_release(
        config=config,
        release=release,
        download_url=download_url,
        executable=executable,
        reported_version=reported_version,
        target_file=target_file,
        target_document=target_document,
        evaluator_result=evaluator_result,
    )

    summary["dependent_library_includes_purl_fix"] = (
        release.dependent_library_includes_purl_fix
    )
    summary["expected_execution"] = release.expected_execution
    summary["observed_execution"] = "completed"

    execution_matches = release.expected_execution == "completed"

    summary["matches_expected"] = execution_matches and summary["matches_expected"]

    print(
        f"[{release.version}] "
        f"execution=completed "
        f"observed={summary['observed_verdict']} "
        f"match={summary['matches_expected']}"
    )

    return summary


def write_results(
    config: SweepConfig,
    releases: list[dict[str, Any]],
) -> None:
    """Write the complete aggregate sweep result."""

    matches_expected = all(
        bool(item["matches_expected"]) and bool(item["all_applicable_match_expected"])
        for item in releases
    )

    document = {
        "sweep_id": "cyclonedx-cli-424-release-sweep",
        "evidence_role": "engineering_validation",
        "source_file": str(config.source_file.relative_to(REPOSITORY_ROOT)).replace(
            "\\", "/"
        ),
        "source_sha256": config.source_sha256,
        "commitment": config.commitment_id,
        "freeze_file": str(config.freeze_file.relative_to(REPOSITORY_ROOT)).replace(
            "\\", "/"
        ),
        "example_component": config.example_component,
        "example_ref": config.example_ref,
        "example_source_purl": config.example_source_purl,
        "all_releases_match_expected": matches_expected,
        "releases": releases,
    }

    config.results_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    config.results_file.write_text(
        json.dumps(document, indent=2) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    """Run the complete deterministic release sweep."""

    config, releases = load_configuration(DEFAULT_CONFIG_FILE)

    verify_source(config)
    verify_freeze(config)

    config.binary_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    config.artifact_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    summaries: list[dict[str, Any]] = []

    for release in releases:
        summaries.append(run_release(config, release))

    write_results(config, summaries)

    all_match = all(
        bool(item["matches_expected"]) and bool(item["all_applicable_match_expected"])
        for item in summaries
    )

    print()
    print(f"Results: {config.results_file.relative_to(REPOSITORY_ROOT)}")

    if not all_match:
        print("Release sweep found unexpected behavior.")
        return 1

    print("All releases matched the declared expectations.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
