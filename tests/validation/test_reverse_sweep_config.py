"""Validate the frozen reverse-sweep configuration."""

from pathlib import Path
import tomllib
from typing import Any

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]

CONFIG_FILE = (
    REPOSITORY_ROOT / "validation" / "cyclonedx-cli-reverse-sweep" / "releases.toml"
)


def load_config() -> dict[str, Any]:
    """Load the reverse-sweep TOML configuration."""
    with CONFIG_FILE.open("rb") as handle:
        return tomllib.load(handle)


def test_reverse_sweep_configuration_exists() -> None:
    """The authoritative reverse-sweep configuration must exist."""
    assert CONFIG_FILE.is_file()


def test_reverse_sweep_metadata_is_exploratory() -> None:
    """The reverse sweep must remain exploratory engineering validation."""
    document = load_config()
    sweep = document["sweep"]

    assert sweep["id"] == "cyclonedx-cli-reverse-sweep"
    assert sweep["direction"] == "cyclonedx_to_spdx"
    assert sweep["expectation_role"] == "exploratory"
    assert sweep["evidence_role"] == "engineering_validation"


def test_reverse_sweep_source_is_frozen() -> None:
    """The selected source must have immutable provenance and a digest."""
    document = load_config()
    sweep = document["sweep"]

    assert sweep["source_repository"] == ("https://github.com/CycloneDX/bom-examples")
    assert sweep["source_path"] == "SBOM/dropwizard-1.3.15/bom.json"
    assert sweep["source_commit"] == "ed522d1f051c364e045b87c20665003a0c4ea777"
    assert sweep["source_file"] == (
        "validation/cyclonedx-cli-reverse-sweep/source.cdx.json"
    )
    assert sweep["source_sha256"] == (
        "35C6FDDC1622B52B493E8C95A197B37088063A2FF294566CE58296DBE364D0D1"
    )


def test_reverse_sweep_release_set_is_fixed() -> None:
    """The exploratory sweep must use the declared release series."""
    document = load_config()
    releases = document["release"]

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


def test_reverse_sweep_tags_match_versions() -> None:
    """Every configured release tag must correspond to its version."""
    document = load_config()

    for release in document["release"]:
        assert release["tag"] == f"v{release['version']}"


def test_reverse_sweep_library_versions_are_declared() -> None:
    """Every CLI release must record its dependent library version."""
    document = load_config()

    library_versions = {
        release["version"]: release["library_version"]
        for release in document["release"]
    }

    assert library_versions == {
        "0.29.0": "10.0.0",
        "0.29.1": "10.0.1",
        "0.29.2": "10.0.2",
        "0.30.0": "11.0.0",
        "0.31.0": "11.0.0",
        "0.32.0": "12.1.1",
        "0.33.0": "12.1.1",
        "0.33.1": "12.1.2",
    }


def test_reverse_sweep_fix_boundary_is_historical_metadata() -> None:
    """The recorded dependent-library boundary must match release history."""
    document = load_config()

    includes_fix = {
        release["version"]: release["dependent_library_includes_purl_fix"]
        for release in document["release"]
    }

    assert includes_fix == {
        "0.29.0": False,
        "0.29.1": False,
        "0.29.2": False,
        "0.30.0": False,
        "0.31.0": False,
        "0.32.0": True,
        "0.33.0": True,
        "0.33.1": True,
    }


def test_reverse_sweep_has_no_predeclared_verdicts() -> None:
    """Exploratory reverse releases must not predeclare preservation verdicts."""
    document = load_config()

    for release in document["release"]:
        assert "expected_verdict" not in release
        assert "expected_execution" not in release


def test_reverse_sweep_release_schema_is_exact() -> None:
    """Release records must contain only the declared exploratory fields."""
    document = load_config()

    expected_fields = {
        "version",
        "tag",
        "library_version",
        "dependent_library_includes_purl_fix",
    }

    for release in document["release"]:
        assert set(release) == expected_fields
