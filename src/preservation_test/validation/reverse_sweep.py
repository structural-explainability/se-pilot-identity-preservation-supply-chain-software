"""Run the exploratory CycloneDX-to-SPDX release sweep.

Run from the root project folder with:

uv run python -m preservation_test.validation.reverse_sweep

The sweep records observed execution, preservation, anchoring, applicability,
and limitation outcomes. It does not compare preservation verdicts against
predeclared expectations.
"""

from collections import Counter
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tomllib
from typing import Any
import urllib.request

from preservation_test.evaluator import formats

REPOSITORY_ROOT = Path(__file__).resolve().parents[3]

DEFAULT_CONFIG_FILE = (
    REPOSITORY_ROOT / "validation" / "cyclonedx-cli-reverse-sweep" / "releases.toml"
)

CYCLONEDX_CLI_REPOSITORY = "https://github.com/CycloneDX/cyclonedx-cli"
CYCLONEDX_CLI_ASSET_NAME = "cyclonedx-win-x64.exe"

EVALUATOR_MODULE = "preservation_test.evaluator.evaluate"

FREEZE_FILE = REPOSITORY_ROOT / "contracts" / "FREEZE_01_COMMITMENT_EVALUATOR.md"

COMMITMENT_ID = "purl_preservation_v1"

COMMAND_TIMEOUT_SECONDS = 300


@dataclass(frozen=True)
class SweepConfig:
    """Configuration shared by every release in the reverse sweep."""

    sweep_id: str
    direction: str
    expectation_role: str
    evidence_role: str

    source_repository: str
    source_path: str
    source_branch: str
    source_commit: str
    source_file: Path
    source_sha256: str

    artifact_directory: Path
    results_file: Path
    binary_directory: Path


@dataclass(frozen=True)
class ReleaseSpec:
    """One explicitly selected CycloneDX CLI release."""

    version: str
    tag: str
    library_version: str
    dependent_library_includes_purl_fix: bool


def resolve_repository_path(value: str) -> Path:
    """Resolve a repository-relative path."""
    return REPOSITORY_ROOT / value


def load_configuration(
    config_file: Path,
) -> tuple[SweepConfig, list[ReleaseSpec]]:
    """Load the exploratory reverse-sweep configuration."""
    with config_file.open("rb") as handle:
        document = tomllib.load(handle)

    sweep = document["sweep"]

    config_directory = config_file.parent

    config = SweepConfig(
        sweep_id=str(sweep["id"]),
        direction=str(sweep["direction"]),
        expectation_role=str(sweep["expectation_role"]),
        evidence_role=str(sweep["evidence_role"]),
        source_repository=str(sweep["source_repository"]),
        source_path=str(sweep["source_path"]),
        source_branch=str(sweep["source_branch"]),
        source_commit=str(sweep["source_commit"]),
        source_file=resolve_repository_path(str(sweep["source_file"])),
        source_sha256=str(sweep["source_sha256"]).upper(),
        artifact_directory=config_directory / "artifacts",
        results_file=config_directory / "results.json",
        binary_directory=REPOSITORY_ROOT / "bin" / "cyclonedx-cli-reverse-sweep",
    )

    releases = [
        ReleaseSpec(
            version=str(item["version"]),
            tag=str(item["tag"]),
            library_version=str(item["library_version"]),
            dependent_library_includes_purl_fix=bool(
                item["dependent_library_includes_purl_fix"]
            ),
        )
        for item in document["release"]
    ]

    return config, releases


def verify_configuration(config: SweepConfig) -> None:
    """Verify the declared role and direction of the exploratory sweep."""
    if config.direction != "cyclonedx_to_spdx":
        raise ValueError("Reverse sweep requires direction='cyclonedx_to_spdx'.")

    if config.expectation_role != "exploratory":
        raise ValueError("Reverse sweep requires expectation_role='exploratory'.")

    if config.evidence_role != "engineering_validation":
        raise ValueError(
            "Reverse sweep requires evidence_role='engineering_validation'."
        )


def calculate_sha256(path: Path) -> str:
    """Calculate the uppercase SHA-256 digest of a file."""
    digest = hashlib.sha256()

    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)

    return digest.hexdigest().upper()


def load_json_file(path: Path) -> dict[str, Any]:
    """Load one JSON document."""
    with path.open(
        "r",
        encoding="utf-8-sig",
    ) as handle:
        document = json.load(handle)

    if not isinstance(document, dict):
        raise TypeError(f"Expected JSON object: {path}")

    return document


def verify_source(
    config: SweepConfig,
) -> tuple[dict[str, Any], list[formats.Component]]:
    """Verify the preserved CycloneDX source and return normalized components."""
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

    document = load_json_file(config.source_file)

    format_name, components = formats.load(document)

    if format_name != "cyclonedx":
        raise RuntimeError(
            "Reverse-sweep source is not recognized as CycloneDX.\n"
            f"Observed format: {format_name}"
        )

    return document, components


def verify_freeze() -> None:
    """Verify that the frozen commitment/evaluator record exists."""
    if not FREEZE_FILE.is_file():
        raise FileNotFoundError(f"Freeze record does not exist: {FREEZE_FILE}")


def build_download_url(release: ReleaseSpec) -> str:
    """Build the GitHub release-asset URL."""
    repository = CYCLONEDX_CLI_REPOSITORY.rstrip("/")

    return f"{repository}/releases/download/{release.tag}/{CYCLONEDX_CLI_ASSET_NAME}"


def download_file(
    url: str,
    destination: Path,
) -> None:
    """Download one release asset atomically unless already present."""
    if destination.is_file():
        return

    destination.parent.mkdir(parents=True, exist_ok=True)

    temporary = destination.with_name(f"{destination.name}.tmp")

    if temporary.exists():
        temporary.unlink()

    request = urllib.request.Request(
        url,
        headers={"User-Agent": "se-pilot-identity-preservation-reverse-sweep"},
    )

    try:
        with (
            urllib.request.urlopen(
                request,
                timeout=COMMAND_TIMEOUT_SECONDS,
            ) as response,
            temporary.open("wb") as output,
        ):
            while block := response.read(1024 * 1024):
                output.write(block)

        temporary.replace(destination)

    except Exception:
        if temporary.exists():
            temporary.unlink()

        raise


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
) -> str:
    """Return the version string reported by a CLI executable."""
    completed = run_command(
        [str(executable), "--version"],
        COMMAND_TIMEOUT_SECONDS,
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


def prepare_executable(
    release: ReleaseSpec,
    executable: Path,
    download_url: str,
) -> str:
    """Download and verify a release executable, retrying once if corrupted."""
    download_file(download_url, executable)

    try:
        reported_version = get_cli_version(executable)

    except RuntimeError:
        if executable.exists():
            executable.unlink()

        download_file(download_url, executable)
        reported_version = get_cli_version(executable)

    verify_cli_version(release, reported_version)

    return reported_version


def run_transformation(
    executable: Path,
    source_file: Path,
    target_file: Path,
) -> None:
    """Transform the preserved CycloneDX source to SPDX JSON."""
    target_file.parent.mkdir(parents=True, exist_ok=True)

    if target_file.exists():
        target_file.unlink()

    run_command(
        [
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
        ],
        COMMAND_TIMEOUT_SECONDS,
    )

    if not target_file.is_file():
        raise RuntimeError(f"CLI did not create the expected target: {target_file}")


def verify_target(target_file: Path) -> dict[str, Any]:
    """Parse the generated target and verify that it is SPDX JSON."""
    try:
        document = load_json_file(target_file)
    except (json.JSONDecodeError, UnicodeDecodeError) as error:
        raise RuntimeError(
            f"Generated target is not valid JSON: {target_file}"
        ) from error

    spdx_version = str(document.get("spdxVersion", ""))

    if not spdx_version.startswith("SPDX-2"):
        raise RuntimeError(
            "Generated target is not recognized as SPDX 2.x JSON.\n"
            f"Target: {target_file}\n"
            f"Observed spdxVersion: {spdx_version or 'missing'}"
        )

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
            EVALUATOR_MODULE,
            str(config.source_file),
            str(target_file),
            "--commitment-id",
            COMMITMENT_ID,
            "--json",
        ],
        COMMAND_TIMEOUT_SECONDS,
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


def get_evaluator_results(
    evaluator_result: dict[str, Any],
) -> list[dict[str, Any]]:
    """Return the evaluator result records."""
    results = evaluator_result.get("results")

    if not isinstance(results, list):
        raise TypeError("Evaluator result does not contain a results list.")

    return [item for item in results if isinstance(item, dict)]


def verdict_component_refs(
    results: list[dict[str, Any]],
    verdict: str,
) -> set[str]:
    """Return component refs receiving one specified verdict."""
    return {str(item.get("ref")) for item in results if item.get("verdict") == verdict}


def violation_component_refs(
    results: list[dict[str, Any]],
) -> set[str]:
    """Return component refs receiving any preservation-violation verdict."""
    return {
        str(item.get("ref"))
        for item in results
        if str(item.get("verdict", "")).startswith("VIOLATED_")
    }


def evaluable_component_refs(
    results: list[dict[str, Any]],
) -> set[str]:
    """Return component refs that reached a preservation verdict."""
    refs: set[str] = set()

    for item in results:
        verdict = str(item.get("verdict", ""))

        if verdict == "PRESERVED" or verdict.startswith("VIOLATED_"):
            refs.add(str(item.get("ref")))

    return refs


def fraction(
    numerator: int,
    denominator: int,
) -> float | None:
    """Return a fraction, or None when its denominator is zero."""
    if denominator == 0:
        return None

    return numerator / denominator


def summarize_outcomes(
    source_components: list[formats.Component],
    evaluator_result: dict[str, Any],
) -> dict[str, Any]:
    """Summarize coverage and observed evaluator outcomes."""
    results = get_evaluator_results(evaluator_result)

    verdict_counts = Counter(str(item.get("verdict")) for item in results)

    total_source_components = len(source_components)

    applicable_components = sum(
        1 for component in source_components if component.canonical_purls
    )

    not_applicable_components = total_source_components - applicable_components

    evaluable_refs = evaluable_component_refs(results)
    preserved_refs = verdict_component_refs(results, "PRESERVED")
    violation_refs = violation_component_refs(results)
    unanchorable_refs = verdict_component_refs(results, "UNANCHORABLE")
    underdetermined_refs = verdict_component_refs(
        results,
        "UNDERDETERMINED",
    )
    unsupported_refs = verdict_component_refs(results, "UNSUPPORTED")

    evaluable_components = len(evaluable_refs)
    preserved_components = len(preserved_refs)
    violated_components = len(violation_refs)
    unanchorable_components = len(unanchorable_refs)
    underdetermined_components = len(underdetermined_refs)
    unsupported_components = len(unsupported_refs)

    violation_counts = {
        verdict: count
        for verdict, count in sorted(verdict_counts.items())
        if verdict.startswith("VIOLATED_")
    }

    return {
        "total_source_components": total_source_components,
        "applicable_components": applicable_components,
        "not_applicable_components": not_applicable_components,
        "evaluable_components": evaluable_components,
        "preserved_components": preserved_components,
        "violated_components": violated_components,
        "unanchorable_components": unanchorable_components,
        "underdetermined_components": underdetermined_components,
        "unsupported_components": unsupported_components,
        "evaluable_fraction_of_applicable": fraction(
            evaluable_components,
            applicable_components,
        ),
        "unanchorable_fraction_of_applicable": fraction(
            unanchorable_components,
            applicable_components,
        ),
        "underdetermined_fraction_of_applicable": fraction(
            underdetermined_components,
            applicable_components,
        ),
        "preserved_fraction_among_evaluable": fraction(
            preserved_components,
            evaluable_components,
        ),
        "violation_fraction_among_evaluable": fraction(
            violated_components,
            evaluable_components,
        ),
        "verdict_counts": dict(sorted(verdict_counts.items())),
        "violation_counts": violation_counts,
        "result_count": len(results),
    }


def failed_execution_summary(
    *,
    release: ReleaseSpec,
    download_url: str,
    executable: Path,
    reported_version: str,
    observed_execution: str,
    error: Exception,
    target_file: Path,
) -> dict[str, Any]:
    """Build the aggregate record for a release that did not complete."""
    target_sha256 = calculate_sha256(target_file) if target_file.is_file() else None

    return {
        "version": release.version,
        "tag": release.tag,
        "library_version": release.library_version,
        "dependent_library_includes_purl_fix": (
            release.dependent_library_includes_purl_fix
        ),
        "download_url": download_url,
        "reported_version": reported_version,
        "executable_sha256": calculate_sha256(executable),
        "observed_execution": observed_execution,
        "target_sha256": target_sha256,
        "target_spdx_version": None,
        "coverage": None,
        "error": str(error),
    }


def summarize_release(
    *,
    release: ReleaseSpec,
    download_url: str,
    executable: Path,
    reported_version: str,
    target_file: Path,
    target_document: dict[str, Any],
    evaluator_result: dict[str, Any],
    source_components: list[formats.Component],
) -> dict[str, Any]:
    """Build the aggregate exploratory result for one completed release."""
    coverage = summarize_outcomes(
        source_components,
        evaluator_result,
    )

    return {
        "version": release.version,
        "tag": release.tag,
        "library_version": release.library_version,
        "dependent_library_includes_purl_fix": (
            release.dependent_library_includes_purl_fix
        ),
        "download_url": download_url,
        "reported_version": reported_version,
        "executable_sha256": calculate_sha256(executable),
        "observed_execution": "completed",
        "target_sha256": calculate_sha256(target_file),
        "target_spdx_version": target_document.get("spdxVersion"),
        "coverage": coverage,
        "error": None,
    }


def run_release(
    config: SweepConfig,
    release: ReleaseSpec,
    source_components: list[formats.Component],
) -> dict[str, Any]:
    """Download, execute, evaluate, and summarize one release."""
    executable = config.binary_directory / f"cyclonedx-cli-{release.version}.exe"

    release_directory = config.artifact_directory / release.version

    target_file = release_directory / "target.spdx.json"

    result_file = release_directory / "result.json"

    download_url = build_download_url(release)

    print(
        f"[{release.version}] "
        f"Spdx.Interop {release.library_version} "
        "expectation_role=exploratory"
    )

    reported_version = prepare_executable(
        release,
        executable,
        download_url,
    )

    try:
        run_transformation(
            executable,
            config.source_file,
            target_file,
        )

    except RuntimeError as error:
        summary = failed_execution_summary(
            release=release,
            download_url=download_url,
            executable=executable,
            reported_version=reported_version,
            observed_execution="transformation_failed",
            error=error,
            target_file=target_file,
        )

        print(f"[{release.version}] execution=transformation_failed")

        return summary

    try:
        target_document = verify_target(target_file)

    except RuntimeError as error:
        summary = failed_execution_summary(
            release=release,
            download_url=download_url,
            executable=executable,
            reported_version=reported_version,
            observed_execution="invalid_target",
            error=error,
            target_file=target_file,
        )

        print(f"[{release.version}] execution=invalid_target")

        return summary

    evaluator_result = run_evaluator(
        config,
        target_file,
        result_file,
    )

    summary = summarize_release(
        release=release,
        download_url=download_url,
        executable=executable,
        reported_version=reported_version,
        target_file=target_file,
        target_document=target_document,
        evaluator_result=evaluator_result,
        source_components=source_components,
    )

    coverage = summary["coverage"]

    if not isinstance(coverage, dict):
        raise TypeError("Completed release has no coverage summary.")

    verdict_counts = coverage["verdict_counts"]

    print(
        f"[{release.version}] "
        "execution=completed "
        f"evaluable="
        f"{coverage['evaluable_components']}/"
        f"{coverage['applicable_components']} "
        f"PRESERVED={verdict_counts.get('PRESERVED', 0)} "
        f"VIOLATED={coverage['violated_components']} "
        f"UNANCHORABLE={verdict_counts.get('UNANCHORABLE', 0)} "
        f"UNDERDETERMINED={verdict_counts.get('UNDERDETERMINED', 0)}"
    )

    return summary


def write_results(
    config: SweepConfig,
    releases: list[dict[str, Any]],
    source_components: list[formats.Component],
) -> None:
    """Write the complete aggregate exploratory sweep result."""
    source_applicable_components = sum(
        1 for component in source_components if component.canonical_purls
    )

    document = {
        "sweep_id": config.sweep_id,
        "direction": config.direction,
        "expectation_role": config.expectation_role,
        "evidence_role": config.evidence_role,
        "commitment": COMMITMENT_ID,
        "freeze_file": str(FREEZE_FILE.relative_to(REPOSITORY_ROOT)).replace("\\", "/"),
        "source": {
            "repository": config.source_repository,
            "path": config.source_path,
            "branch": config.source_branch,
            "commit": config.source_commit,
            "local_file": str(config.source_file.relative_to(REPOSITORY_ROOT)).replace(
                "\\", "/"
            ),
            "sha256": config.source_sha256,
            "total_components": len(source_components),
            "applicable_components": source_applicable_components,
        },
        "known_evaluator_limitations": [
            (
                "For SPDX 2.3 targets, the frozen adapter recognizes "
                "canonical PURLs in PACKAGE-MANAGER/purl ExternalRef "
                "records but does not enumerate noncanonical SPDX "
                "locations containing PURL-like values. A PURL preserved "
                "outside the recognized canonical SPDX representation may "
                "therefore be classified as VIOLATED_DROPPED rather than "
                "VIOLATED_RELOCATED."
            )
        ],
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
    """Run the complete exploratory reverse release sweep."""
    config, releases = load_configuration(DEFAULT_CONFIG_FILE)

    verify_configuration(config)

    _, source_components = verify_source(config)

    verify_freeze()

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
        summaries.append(
            run_release(
                config,
                release,
                source_components,
            )
        )

    write_results(
        config,
        summaries,
        source_components,
    )

    print()
    print(f"Results: {config.results_file.relative_to(REPOSITORY_ROOT)}")

    completed = sum(
        1 for item in summaries if item["observed_execution"] == "completed"
    )

    print(f"Completed transformations: {completed}/{len(summaries)}")

    print("Exploratory sweep complete; no preservation verdicts were predeclared.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
