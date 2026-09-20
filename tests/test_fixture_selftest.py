"""Tests for the integrated synthetic engineering fixture."""

from preservation_test.fixtures import build_and_selftest


def test_fixture_selftest_passes() -> None:
    """Verify the complete synthetic verdict scenario."""
    assert build_and_selftest.run_selftest()
