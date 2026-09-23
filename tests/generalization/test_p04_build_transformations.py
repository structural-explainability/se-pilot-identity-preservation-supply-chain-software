"""Tests for p04 pre-outcome transformation-matrix construction."""

from pathlib import Path

from preservation_test.generalization.p04_build_transformations import (
    PLANNED,
    UNSUPPORTED,
    Converter,
    Source,
    _cdx2spdx_route,
    _protobom_route,
    _syft_route,
)


def _source(
    *,
    standard: str,
    version: str,
) -> Source:
    return Source(
        study_id=f"gen-{standard}-test",
        preserved_path=f"generalization/sources/source.{standard}.json",
        preserved_sha256="a" * 64,
        source_standard=standard,
        source_spec_version=version,
    )


def _converter(
    *,
    converter_id: str,
    artifact_path: Path,
) -> Converter:
    return Converter(
        converter_id=converter_id,
        name=converter_id,
        version="1.0.0",
        artifact_path=artifact_path,
        artifact_sha256="b" * 64,
        documentation="https://example.org",
        runtime="test",
    )


def test_protobom_marks_cyclonedx_1_3_unsupported(
    tmp_path: Path,
) -> None:
    source = _source(
        standard="cyclonedx",
        version="1.3",
    )
    converter = _converter(
        converter_id="protobom",
        artifact_path=tmp_path / "sbom-convert.exe",
    )

    route = _protobom_route(source, converter)

    assert route.status == UNSUPPORTED
    assert route.direction == "cyclonedx_to_spdx"
    assert route.target_standard == "spdx"
    assert route.command_argv == ()
    assert "outside documented protobom" in route.unsupported_reason


def test_protobom_plans_spdx_2_3_route(
    tmp_path: Path,
) -> None:
    source = _source(
        standard="spdx",
        version="SPDX-2.3",
    )
    converter = _converter(
        converter_id="protobom",
        artifact_path=tmp_path / "sbom-convert.exe",
    )

    route = _protobom_route(source, converter)

    assert route.status == PLANNED
    assert route.direction == "spdx_to_cyclonedx"
    assert route.target_standard == "cyclonedx"
    assert route.target_spec_version == "1.4"
    assert route.command_argv


def test_cdx2spdx_marks_spdx_source_unsupported(
    tmp_path: Path,
) -> None:
    source = _source(
        standard="spdx",
        version="SPDX-2.3",
    )
    converter = _converter(
        converter_id="cdx2spdx",
        artifact_path=tmp_path / "cdx2spdx.jar",
    )

    route = _cdx2spdx_route(source, converter)

    assert route.status == UNSUPPORTED
    assert route.direction == "spdx_to_cyclonedx"
    assert route.command_argv == ()
    assert "CycloneDX-to-SPDX conversion only" in route.unsupported_reason


def test_cdx2spdx_keeps_cyclonedx_route_as_planned_attempt(
    tmp_path: Path,
) -> None:
    source = _source(
        standard="cyclonedx",
        version="1.2",
    )
    converter = _converter(
        converter_id="cdx2spdx",
        artifact_path=tmp_path / "cdx2spdx.jar",
    )

    route = _cdx2spdx_route(source, converter)

    assert route.status == PLANNED
    assert route.direction == "cyclonedx_to_spdx"
    assert route.target_standard == "spdx"
    assert route.command_argv


def test_syft_plans_cyclonedx_to_spdx(
    tmp_path: Path,
) -> None:
    source = _source(
        standard="cyclonedx",
        version="1.3",
    )
    converter = _converter(
        converter_id="syft",
        artifact_path=tmp_path / "syft.exe",
    )

    route = _syft_route(source, converter)

    assert route.status == PLANNED
    assert route.direction == "cyclonedx_to_spdx"
    assert route.target_standard == "spdx"
    assert route.target_spec_version == "SPDX-2.3"
    assert route.command_argv


def test_syft_plans_spdx_to_cyclonedx(
    tmp_path: Path,
) -> None:
    source = _source(
        standard="spdx",
        version="SPDX-2.3",
    )
    converter = _converter(
        converter_id="syft",
        artifact_path=tmp_path / "syft.exe",
    )

    route = _syft_route(source, converter)

    assert route.status == PLANNED
    assert route.direction == "spdx_to_cyclonedx"
    assert route.target_standard == "cyclonedx"
    assert route.target_spec_version == "1.6"
    assert route.command_argv
