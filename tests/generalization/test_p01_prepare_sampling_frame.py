"""Tests for p01 sampling-frame preparation."""

from pathlib import Path
import subprocess

from preservation_test.generalization import p01_prepare_sampling_frame


def _git(cwd: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args],
        cwd=cwd,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def _config_text(url: str, revision: str) -> str:
    return f"""
schema_version = 1
sampling_id = "test-sampling"

[sampling_frame]

[[sampling_frame.repository]]
name = "Example/examples"
url = "{url}"
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
kind = "sha256"
value = "{"a" * 64}"
reason = "synthetic-test-exclusion"
provenance = "test"
"""


def test_prepare_sampling_frame_clones_exact_revision_detached(
    tmp_path: Path,
) -> None:
    remote = tmp_path / "remote"
    remote.mkdir()

    _git(remote, "init", "-q")
    _git(remote, "config", "user.email", "test@example.org")
    _git(remote, "config", "user.name", "test")
    _git(remote, "config", "core.autocrlf", "false")

    source = remote / "example.json"
    source.write_bytes(b'{"example": true}')

    _git(remote, "add", "-A")
    _git(remote, "commit", "-q", "-m", "fixture")

    revision = _git(remote, "rev-parse", "HEAD")

    config = tmp_path / "01-sampling.toml"
    config.write_text(
        _config_text(remote.as_uri(), revision),
        encoding="utf-8",
    )

    clone_root = tmp_path / "clones"

    result = p01_prepare_sampling_frame.main(
        [
            "--config",
            str(config),
            "--clone-root",
            str(clone_root),
        ]
    )

    assert result == 0

    clone = clone_root / "examples"

    assert clone.is_dir()
    assert _git(clone, "rev-parse", "HEAD") == revision
    assert _git(clone, "rev-parse", "--abbrev-ref", "HEAD") == "HEAD"


def test_prepare_sampling_frame_is_idempotent(
    tmp_path: Path,
) -> None:
    remote = tmp_path / "remote"
    remote.mkdir()

    _git(remote, "init", "-q")
    _git(remote, "config", "user.email", "test@example.org")
    _git(remote, "config", "user.name", "test")

    (remote / "example.json").write_bytes(b"{}")

    _git(remote, "add", "-A")
    _git(remote, "commit", "-q", "-m", "fixture")

    revision = _git(remote, "rev-parse", "HEAD")

    config = tmp_path / "01-sampling.toml"
    config.write_text(
        _config_text(remote.as_uri(), revision),
        encoding="utf-8",
    )

    clone_root = tmp_path / "clones"

    args = [
        "--config",
        str(config),
        "--clone-root",
        str(clone_root),
    ]

    assert p01_prepare_sampling_frame.main(args) == 0
    assert p01_prepare_sampling_frame.main(args) == 0

    clone = clone_root / "examples"

    assert _git(clone, "rev-parse", "HEAD") == revision
    assert _git(clone, "rev-parse", "--abbrev-ref", "HEAD") == "HEAD"
