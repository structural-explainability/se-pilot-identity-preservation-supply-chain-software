"""Tests for PURL canonicalization rules."""

from preservation_test.evaluator.purl_canonical import canonical, coordinates, same


def test_canonical_normalizes_pypi_name() -> None:
    assert canonical("pkg:pypi/Requests@2.31.0") == "pkg:pypi/requests@2.31.0"


def test_same_uses_canonical_form() -> None:
    assert same(
        "pkg:pypi/Requests@2.31.0",
        "pkg:pypi/requests@2.31.0",
    )


def test_invalid_purl_returns_none() -> None:
    assert canonical("not-a-purl") is None


def test_coordinates_drop_version_and_qualifiers() -> None:
    assert coordinates(
        "pkg:pypi/example@1.0?repository_url=https://example.invalid"
    ) == (
        "pypi",
        "",
        "example",
    )
