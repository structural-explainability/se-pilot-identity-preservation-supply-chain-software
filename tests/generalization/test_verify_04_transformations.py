"""Tests for transformation-plan Freeze 02 verification."""

from hashlib import sha256
from pathlib import Path

import pytest

import preservation_test.generalization.verification.verify_04_transformations as verify_module


def _make_java_route_planned(transformations_path: Path) -> None:
    """Convert the Java test route into a valid planned runtime route."""
    _replace_once(
        transformations_path,
        "planned_routes = 1",
        "planned_routes = 2",
    )
    _replace_once(
        transformations_path,
        "unsupported_routes = 1",
        "unsupported_routes = 0",
    )
    _replace_once(
        transformations_path,
        'status = "unsupported_pre_execution"',
        'status = "planned"',
    )
    _replace_once(
        transformations_path,
        "validation_required = false",
        (
            "validation_required = true\n"
            "command_argv = ["
            '"bin/java.exe", "-jar", "bin/java-converter.jar", '
            '"source.json", "target.json"]\n'
            "validation_command_argv = "
            '["bin/validator.exe", "validate"]'
        ),
    )


def _sha256(data: bytes) -> str:
    """Return the SHA-256 digest for test bytes."""
    return sha256(data).hexdigest()


def _write_file(
    repository_root: Path,
    relative_path: str,
    data: bytes,
) -> tuple[str, str]:
    """Write one repository file and return its path and SHA-256."""
    path = repository_root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)

    return relative_path, _sha256(data)


def _replace_once(
    path: Path,
    old: str,
    new: str,
) -> None:
    """Replace one expected occurrence in a test artifact."""
    text = path.read_text(encoding="utf-8")

    assert old in text

    path.write_text(
        text.replace(old, new, 1),
        encoding="utf-8",
    )


def _write_sources_record(
    repository_root: Path,
    *,
    source_path: str,
    source_sha256: str,
) -> Path:
    """Write the minimal 04-sources.toml required by stage 04."""
    path = repository_root / "generalization" / "04-sources.toml"
    path.parent.mkdir(parents=True, exist_ok=True)

    path.write_text(
        "\n".join(
            [
                "[[source]]",
                'study_id = "source-a"',
                f'preserved_path = "{source_path}"',
                f'preserved_sha256 = "{source_sha256}"',
                "",
            ]
        ),
        encoding="utf-8",
    )

    return path


def _write_transformations(
    repository_root: Path,
    *,
    sources_path: Path,
    corpus_path: Path,
    source_path: str,
    source_sha256: str,
    native_path: str,
    native_sha256: str,
    java_converter_path: str,
    java_converter_sha256: str,
    java_path: str,
    java_sha256: str,
    validator_path: str,
    validator_sha256: str,
) -> Path:
    """Write a valid minimal 05-transformations.toml."""
    code_path, code_sha256 = _write_file(
        repository_root,
        "src/test_transformations_code.py",
        b'"""Test transformation provenance file."""\n',
    )

    path = repository_root / "generalization" / "05-transformations.toml"

    text = "\n".join(
        [
            "[transformations]",
            'sources_record = "generalization/04-sources.toml"',
            f'sources_record_sha256 = "{_sha256(sources_path.read_bytes())}"',
            'corpus_record = "generalization/03-corpus.toml"',
            f'corpus_record_sha256 = "{_sha256(corpus_path.read_bytes())}"',
            "members = 1",
            "converters = 2",
            "matrix_rows = 2",
            "planned_routes = 1",
            "unsupported_routes = 1",
            'execution_state = "not_started"',
            "transformation_outputs_examined = false",
            "",
            "[target_validator]",
            'name = "test validator"',
            'version = "1.0.0"',
            f'artifact_path = "{validator_path}"',
            f'artifact_sha256 = "{validator_sha256}"',
            "",
            "[transformations_code_sha256]",
            f'"{code_path}" = "{code_sha256}"',
            "",
            "[[converter]]",
            'id = "native"',
            'name = "native converter"',
            'version = "1.0.0"',
            f'artifact_path = "{native_path}"',
            f'artifact_sha256 = "{native_sha256}"',
            'runtime = "native executable"',
            "",
            "[[converter]]",
            'id = "java-converter"',
            'name = "Java converter"',
            'version = "1.0.0"',
            f'artifact_path = "{java_converter_path}"',
            f'artifact_sha256 = "{java_converter_sha256}"',
            'runtime = "repo-local Java executable"',
            f'runtime_artifact_path = "{java_path}"',
            'runtime_version = "21.0.0"',
            f'runtime_sha256 = "{java_sha256}"',
            "",
            "[[route]]",
            'route_id = "source-a--native"',
            'study_id = "source-a"',
            'converter_id = "native"',
            f'source_path = "{source_path}"',
            f'source_sha256 = "{source_sha256}"',
            'status = "planned"',
            "validation_required = true",
            'command_argv = ["bin/native.exe", "convert"]',
            ('validation_command_argv = ["bin/validator.exe", "validate"]'),
            "",
            "[[route]]",
            'route_id = "source-a--java-converter"',
            'study_id = "source-a"',
            'converter_id = "java-converter"',
            f'source_path = "{source_path}"',
            f'source_sha256 = "{source_sha256}"',
            'status = "unsupported_pre_execution"',
            "validation_required = false",
            'unsupported_reason = "unsupported for test source"',
            "",
        ]
    )

    path.write_text(text, encoding="utf-8")

    return path


def _prepare_valid_repository(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> tuple[Path, dict[str, Path]]:
    """Create one valid 04 -> 05 transformation-verification fixture."""
    source_path, source_sha256 = _write_file(
        tmp_path,
        "generalization/sources/source-a.spdx.json",
        b'{"name": "source-a"}\n',
    )

    corpus_path = tmp_path / "generalization" / "03-corpus.toml"
    corpus_path.parent.mkdir(parents=True, exist_ok=True)
    corpus_path.write_text(
        '[[member]]\nstudy_id = "source-a"\n',
        encoding="utf-8",
    )

    sources_path = _write_sources_record(
        tmp_path,
        source_path=source_path,
        source_sha256=source_sha256,
    )

    native_path, native_sha256 = _write_file(
        tmp_path,
        "bin/native.exe",
        b"native-converter\n",
    )

    java_converter_path, java_converter_sha256 = _write_file(
        tmp_path,
        "bin/java-converter.jar",
        b"java-converter\n",
    )

    java_path, java_sha256 = _write_file(
        tmp_path,
        "bin/java.exe",
        b"java-runtime\n",
    )

    validator_path, validator_sha256 = _write_file(
        tmp_path,
        "bin/validator.exe",
        b"validator\n",
    )

    transformations_path = _write_transformations(
        tmp_path,
        sources_path=sources_path,
        corpus_path=corpus_path,
        source_path=source_path,
        source_sha256=source_sha256,
        native_path=native_path,
        native_sha256=native_sha256,
        java_converter_path=java_converter_path,
        java_converter_sha256=java_converter_sha256,
        java_path=java_path,
        java_sha256=java_sha256,
        validator_path=validator_path,
        validator_sha256=validator_sha256,
    )

    monkeypatch.setattr(
        verify_module,
        "verify_03_sources",
        lambda repository_root: sources_path,
    )

    artifacts = {
        "corpus": corpus_path,
        "sources": sources_path,
        "transformations": transformations_path,
        "native": tmp_path / native_path,
        "java_converter": tmp_path / java_converter_path,
        "java": tmp_path / java_path,
        "validator": tmp_path / validator_path,
    }

    return transformations_path, artifacts


def test_verify_04_transformations_accepts_valid_plan(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A complete internally consistent pre-execution plan passes."""
    transformations_path, _ = _prepare_valid_repository(
        tmp_path,
        monkeypatch,
    )

    result = verify_module.verify_04_transformations(tmp_path)

    assert result == transformations_path


def test_verify_04_transformations_propagates_sources_failure(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Failure of stage 03 blocks transformation verification."""

    def fail_sources(repository_root: Path) -> Path:
        raise verify_module.SourcesVerificationError("source verification failed")

    monkeypatch.setattr(
        verify_module,
        "verify_03_sources",
        fail_sources,
    )

    with pytest.raises(
        verify_module.TransformationsVerificationError,
        match="source verification failed",
    ):
        verify_module.verify_04_transformations(tmp_path)


def test_verify_04_transformations_rejects_missing_plan(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """05-transformations.toml must exist."""
    transformations_path, artifacts = _prepare_valid_repository(
        tmp_path,
        monkeypatch,
    )
    transformations_path.unlink()

    assert artifacts["sources"].is_file()

    with pytest.raises(
        verify_module.TransformationsVerificationError,
        match="transformation matrix not found",
    ):
        verify_module.verify_04_transformations(tmp_path)


def test_verify_04_transformations_rejects_changed_sources_record(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """05 must still identify the exact 04-sources.toml bytes."""
    _, artifacts = _prepare_valid_repository(
        tmp_path,
        monkeypatch,
    )

    with artifacts["sources"].open("a", encoding="utf-8") as handle:
        handle.write("\n# changed\n")

    with pytest.raises(
        verify_module.TransformationsVerificationError,
        match="sources record hash mismatch",
    ):
        verify_module.verify_04_transformations(tmp_path)


def test_verify_04_transformations_rejects_changed_corpus_record(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """05 must still identify the exact 03-corpus.toml bytes."""
    _, artifacts = _prepare_valid_repository(
        tmp_path,
        monkeypatch,
    )

    with artifacts["corpus"].open("a", encoding="utf-8") as handle:
        handle.write("\n# changed\n")

    with pytest.raises(
        verify_module.TransformationsVerificationError,
        match="corpus record hash mismatch",
    ):
        verify_module.verify_04_transformations(tmp_path)


def test_verify_04_transformations_rejects_converter_hash_mismatch(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Each converter must remain byte-identical to its frozen artifact."""
    _, artifacts = _prepare_valid_repository(
        tmp_path,
        monkeypatch,
    )

    artifacts["native"].write_bytes(b"tampered-native-converter\n")

    with pytest.raises(
        verify_module.TransformationsVerificationError,
        match="converter native hash mismatch",
    ):
        verify_module.verify_04_transformations(tmp_path)


def test_verify_04_transformations_rejects_runtime_hash_mismatch(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A recorded converter runtime must remain byte-identical."""
    _, artifacts = _prepare_valid_repository(
        tmp_path,
        monkeypatch,
    )

    artifacts["java"].write_bytes(b"tampered-java-runtime\n")

    with pytest.raises(
        verify_module.TransformationsVerificationError,
        match="converter java-converter runtime hash mismatch",
    ):
        verify_module.verify_04_transformations(tmp_path)


def test_verify_04_transformations_requires_complete_runtime_identity(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Runtime path, version, and SHA-256 must be declared together."""
    transformations_path, _ = _prepare_valid_repository(
        tmp_path,
        monkeypatch,
    )

    text = transformations_path.read_text(encoding="utf-8")
    lines = [
        line for line in text.splitlines() if not line.startswith("runtime_sha256 = ")
    ]
    transformations_path.write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
    )

    with pytest.raises(
        verify_module.TransformationsVerificationError,
        match="runtime path, version, and SHA-256 must be recorded together",
    ):
        verify_module.verify_04_transformations(tmp_path)


def test_verify_04_transformations_rejects_validator_hash_mismatch(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The frozen target validator must remain byte-identical."""
    _, artifacts = _prepare_valid_repository(
        tmp_path,
        monkeypatch,
    )

    artifacts["validator"].write_bytes(b"tampered-validator\n")

    with pytest.raises(
        verify_module.TransformationsVerificationError,
        match="target validator hash mismatch",
    ):
        verify_module.verify_04_transformations(tmp_path)


def test_verify_04_transformations_rejects_route_source_mismatch(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Each route must use the source path and hash recorded in 04."""
    transformations_path, _ = _prepare_valid_repository(
        tmp_path,
        monkeypatch,
    )

    _replace_once(
        transformations_path,
        ('source_path = "generalization/sources/source-a.spdx.json"'),
        ('source_path = "generalization/sources/not-source-a.spdx.json"'),
    )

    with pytest.raises(
        verify_module.TransformationsVerificationError,
        match="source path/hash does not match 04-sources.toml",
    ):
        verify_module.verify_04_transformations(tmp_path)


def test_verify_04_transformations_rejects_incorrect_route_id(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Route IDs must be determined by study ID and converter ID."""
    transformations_path, _ = _prepare_valid_repository(
        tmp_path,
        monkeypatch,
    )

    _replace_once(
        transformations_path,
        'route_id = "source-a--native"',
        'route_id = "wrong-route-id"',
    )

    with pytest.raises(
        verify_module.TransformationsVerificationError,
        match="does not equal expected route id",
    ):
        verify_module.verify_04_transformations(tmp_path)


def test_verify_04_transformations_rejects_incomplete_cross_product(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Every preserved source must have one route per converter."""
    transformations_path, _ = _prepare_valid_repository(
        tmp_path,
        monkeypatch,
    )

    text = transformations_path.read_text(encoding="utf-8")
    marker = '[[route]]\nroute_id = "source-a--java-converter"'
    start = text.index(marker)

    transformations_path.write_text(
        text[:start],
        encoding="utf-8",
    )

    with pytest.raises(
        verify_module.TransformationsVerificationError,
        match="transformation matrix is not the complete cross-product",
    ):
        verify_module.verify_04_transformations(tmp_path)


def test_verify_04_transformations_requires_planned_command(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A planned route must contain an executable command."""
    transformations_path, _ = _prepare_valid_repository(
        tmp_path,
        monkeypatch,
    )

    _replace_once(
        transformations_path,
        'command_argv = ["bin/native.exe", "convert"]\n',
        "",
    )

    with pytest.raises(
        verify_module.TransformationsVerificationError,
        match="is planned but has no command_argv",
    ):
        verify_module.verify_04_transformations(tmp_path)


def test_verify_04_transformations_requires_planned_validation_command(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Every planned route must contain its target-validation command."""
    transformations_path, _ = _prepare_valid_repository(
        tmp_path,
        monkeypatch,
    )

    _replace_once(
        transformations_path,
        ('validation_command_argv = ["bin/validator.exe", "validate"]\n'),
        "",
    )

    with pytest.raises(
        verify_module.TransformationsVerificationError,
        match="is planned but has no validation_command_argv",
    ):
        verify_module.verify_04_transformations(tmp_path)


def test_verify_04_transformations_rejects_command_on_unsupported_route(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """An unsupported route must not contain an executable command."""
    transformations_path, _ = _prepare_valid_repository(
        tmp_path,
        monkeypatch,
    )

    _replace_once(
        transformations_path,
        'status = "unsupported_pre_execution"\n',
        (
            'status = "unsupported_pre_execution"\n'
            'command_argv = ["bin/java.exe", "-jar"]\n'
        ),
    )

    with pytest.raises(
        verify_module.TransformationsVerificationError,
        match="is unsupported but has command_argv",
    ):
        verify_module.verify_04_transformations(tmp_path)


def test_verify_04_transformations_requires_unsupported_reason(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Every unsupported route must state its pre-execution reason."""
    transformations_path, _ = _prepare_valid_repository(
        tmp_path,
        monkeypatch,
    )

    _replace_once(
        transformations_path,
        'unsupported_reason = "unsupported for test source"\n',
        "",
    )

    with pytest.raises(
        verify_module.TransformationsVerificationError,
        match="unsupported_reason must be a non-empty string",
    ):
        verify_module.verify_04_transformations(tmp_path)


def test_verify_04_transformations_rejects_planned_count_mismatch(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Summary planned-route count must match route records."""
    transformations_path, _ = _prepare_valid_repository(
        tmp_path,
        monkeypatch,
    )

    _replace_once(
        transformations_path,
        "planned_routes = 1",
        "planned_routes = 2",
    )

    with pytest.raises(
        verify_module.TransformationsVerificationError,
        match=r"\[transformations\]\.planned_routes",
    ):
        verify_module.verify_04_transformations(tmp_path)


def test_verify_04_transformations_requires_not_started_state(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Freeze 02 preparation cannot claim transformation execution started."""
    transformations_path, _ = _prepare_valid_repository(
        tmp_path,
        monkeypatch,
    )

    _replace_once(
        transformations_path,
        'execution_state = "not_started"',
        'execution_state = "started"',
    )

    with pytest.raises(
        verify_module.TransformationsVerificationError,
        match="execution_state must be 'not_started'",
    ):
        verify_module.verify_04_transformations(tmp_path)


def test_verify_04_transformations_requires_outputs_unexamined(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Freeze 02 requires held-out transformation outputs to remain unseen."""
    transformations_path, _ = _prepare_valid_repository(
        tmp_path,
        monkeypatch,
    )

    _replace_once(
        transformations_path,
        "transformation_outputs_examined = false",
        "transformation_outputs_examined = true",
    )

    with pytest.raises(
        verify_module.TransformationsVerificationError,
        match="transformation_outputs_examined must be false",
    ):
        verify_module.verify_04_transformations(tmp_path)


def test_verify_04_transformations_rejects_wrong_native_converter_command(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A native planned route must invoke its recorded converter artifact."""
    transformations_path, _ = _prepare_valid_repository(
        tmp_path,
        monkeypatch,
    )

    _replace_once(
        transformations_path,
        'command_argv = ["bin/native.exe", "convert"]',
        'command_argv = ["bin/not-native.exe", "convert"]',
    )

    with pytest.raises(
        verify_module.TransformationsVerificationError,
        match="does not invoke the recorded converter artifact",
    ):
        verify_module.verify_04_transformations(tmp_path)


def test_verify_04_transformations_rejects_wrong_runtime_command(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A runtime-based route must invoke its recorded runtime artifact."""
    transformations_path, _ = _prepare_valid_repository(
        tmp_path,
        monkeypatch,
    )
    _make_java_route_planned(transformations_path)

    _replace_once(
        transformations_path,
        (
            'command_argv = ["bin/java.exe", "-jar", '
            '"bin/java-converter.jar", "source.json", "target.json"]'
        ),
        (
            'command_argv = ["bin/not-java.exe", "-jar", '
            '"bin/java-converter.jar", "source.json", "target.json"]'
        ),
    )

    with pytest.raises(
        verify_module.TransformationsVerificationError,
        match="does not invoke the recorded converter runtime",
    ):
        verify_module.verify_04_transformations(tmp_path)


def test_verify_04_transformations_requires_runtime_converter_artifact(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A runtime-based route must reference its recorded converter artifact."""
    transformations_path, _ = _prepare_valid_repository(
        tmp_path,
        monkeypatch,
    )
    _make_java_route_planned(transformations_path)

    _replace_once(
        transformations_path,
        (
            'command_argv = ["bin/java.exe", "-jar", '
            '"bin/java-converter.jar", "source.json", "target.json"]'
        ),
        (
            'command_argv = ["bin/java.exe", "-jar", '
            '"bin/not-the-converter.jar", "source.json", "target.json"]'
        ),
    )

    with pytest.raises(
        verify_module.TransformationsVerificationError,
        match="does not reference the recorded converter artifact",
    ):
        verify_module.verify_04_transformations(tmp_path)


def test_verify_04_transformations_rejects_wrong_validator_command(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A planned route must invoke its recorded target validator."""
    transformations_path, _ = _prepare_valid_repository(
        tmp_path,
        monkeypatch,
    )

    _replace_once(
        transformations_path,
        ('validation_command_argv = ["bin/validator.exe", "validate"]'),
        ('validation_command_argv = ["bin/not-validator.exe", "validate"]'),
    )

    with pytest.raises(
        verify_module.TransformationsVerificationError,
        match="does not invoke the recorded target validator",
    ):
        verify_module.verify_04_transformations(tmp_path)
