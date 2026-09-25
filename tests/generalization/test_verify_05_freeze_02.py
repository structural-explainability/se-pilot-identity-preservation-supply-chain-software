"""Tests for the final pre-Freeze-02 verification gate."""

from pathlib import Path

import pytest

import preservation_test.generalization.verification.verify_05_freeze_02 as verify_module


def test_verify_05_freeze_02_runs_all_verifiers_in_order(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The final gate invokes every prerequisite verifier in order."""
    calls: list[str] = []

    monkeypatch.setattr(
        verify_module,
        "verify_01_freeze_01",
        lambda repository_root: calls.append("01"),
    )
    monkeypatch.setattr(
        verify_module,
        "verify_02_corpus",
        lambda repository_root: calls.append("02"),
    )
    monkeypatch.setattr(
        verify_module,
        "verify_03_sources",
        lambda repository_root: calls.append("03"),
    )
    monkeypatch.setattr(
        verify_module,
        "verify_04_transformations",
        lambda repository_root: calls.append("04"),
    )

    verify_module.verify_05_freeze_02(tmp_path)

    assert calls == ["01", "02", "03", "04"]


@pytest.mark.parametrize(
    ("failing_stage", "message"),
    [
        ("verify_01_freeze_01", "Freeze 01 verification failed"),
        ("verify_02_corpus", "corpus verification failed"),
        ("verify_03_sources", "source verification failed"),
        ("verify_04_transformations", "transformation verification failed"),
    ],
)
def test_verify_05_freeze_02_propagates_stage_failure(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    failing_stage: str,
    message: str,
) -> None:
    """Any prerequisite failure prevents Freeze 02 verification."""
    calls: list[str] = []

    stages = [
        "verify_01_freeze_01",
        "verify_02_corpus",
        "verify_03_sources",
        "verify_04_transformations",
    ]

    for stage in stages:
        if stage == failing_stage:

            def fail(
                repository_root: Path,
                *,
                error_message: str = message,
            ) -> None:
                raise RuntimeError(error_message)

            monkeypatch.setattr(
                verify_module,
                stage,
                fail,
            )

        else:

            def succeed(
                repository_root: Path,
                *,
                stage_name: str = stage,
            ) -> None:
                calls.append(stage_name)

            monkeypatch.setattr(
                verify_module,
                stage,
                succeed,
            )

    with pytest.raises(RuntimeError, match=message):
        verify_module.verify_05_freeze_02(tmp_path)

    failing_index = stages.index(failing_stage)

    assert calls == stages[:failing_index]


def test_main_verifies_repository_root_and_reports_success(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """The module entry point uses the repository root and reports success."""
    received: list[Path] = []

    monkeypatch.setattr(
        verify_module,
        "verify_05_freeze_02",
        lambda repository_root: received.append(repository_root),
    )

    verify_module.main()

    assert received == [verify_module.REPOSITORY_ROOT]
    assert capsys.readouterr().out == "Freeze 02 prerequisites verified.\n"
