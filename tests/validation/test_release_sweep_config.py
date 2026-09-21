"""Tests for the CycloneDX CLI issue #424 release-sweep configuration."""

from pathlib import Path
import tomllib
from typing import Any

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]

CONFIG_FILE = (
    REPOSITORY_ROOT / "validation" / "cyclonedx-cli-424-release-sweep" / "releases.toml"
)


def load_config() -> dict[str, Any]:
    """Load the release-sweep TOML configuration."""

    with CONFIG_FILE.open("rb") as handle:
        return tomllib.load(handle)


def test_release_sweep_config_exists() -> None:
    """The release-sweep configuration should be committed."""

    assert CONFIG_FILE.is_file()


def test_release_sweep_uses_frozen_source_and_commitment() -> None:
    """The sweep should use the established source and frozen commitment."""

    config = load_config()
    sweep = config["sweep"]

    assert sweep["source_file"] == ("validation/cyclonedx-cli-424/source.spdx.json")
    assert sweep["commitment_id"] == "purl_preservation_v1"
    assert sweep["freeze_file"] == ("contracts/FREEZE_01_COMMITMENT_EVALUATOR.md")


def test_release_versions_are_unique() -> None:
    """Each CLI release should appear exactly once."""

    config = load_config()
    releases = config["release"]

    versions = [release["version"] for release in releases]

    assert len(versions) == len(set(versions))


def test_release_versions_are_in_expected_order() -> None:
    """The release sweep should preserve the declared release sequence."""

    config = load_config()
    releases = config["release"]

    versions = [release["version"] for release in releases]

    assert versions == [
        "0.29.0",
        "0.29.1",
        "0.29.2",
        "0.30.0",
        "0.31.0",
        "0.32.0",
        "0.33.0",
        "0.33.1",
    ]


def test_each_release_has_required_fields() -> None:
    """Every release should define the complete sweep specification."""

    config = load_config()
    releases = config["release"]

    required_fields = {
        "version",
        "tag",
        "library_version",
        "dependent_library_includes_purl_fix",
        "expected_verdict",
    }

    for release in releases:
        assert required_fields <= release.keys()


def test_expected_verdict_matches_library_fix_status() -> None:
    """Expected verdict should follow execution state and library-fix boundary."""

    config = load_config()
    releases = config["release"]

    for release in releases:
        if release["expected_execution"] != "completed":
            assert release["expected_verdict"] == ""
        elif release["dependent_library_includes_purl_fix"]:
            assert release["expected_verdict"] == "PRESERVED"
        else:
            assert release["expected_verdict"] == "VIOLATED_RELOCATED"


def test_noncompleted_releases_have_no_expected_verdict() -> None:
    """A release that does not complete transformation has no preservation verdict."""

    config = load_config()
    releases = config["release"]

    for release in releases:
        if release["expected_execution"] != "completed":
            assert release["expected_verdict"] == ""


def test_known_boundary_releases_are_declared_correctly() -> None:
    """The established 0.31.0 to 0.32.0 boundary should remain explicit."""

    config = load_config()
    releases = {release["version"]: release for release in config["release"]}

    pre_fix = releases["0.31.0"]

    assert pre_fix["library_version"] == "11.0.0"
    assert pre_fix["dependent_library_includes_purl_fix"] is False
    assert pre_fix["expected_verdict"] == "VIOLATED_RELOCATED"

    post_fix = releases["0.32.0"]

    assert post_fix["library_version"] == "12.1.1"
    assert post_fix["dependent_library_includes_purl_fix"] is True
    assert post_fix["expected_verdict"] == "PRESERVED"


def test_tags_match_release_versions() -> None:
    """Each release tag should correspond to its configured version."""

    config = load_config()
    releases = config["release"]

    for release in releases:
        assert release["tag"] == f"v{release['version']}"
