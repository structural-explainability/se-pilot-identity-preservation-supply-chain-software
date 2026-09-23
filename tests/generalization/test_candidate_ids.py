"""Tests for preservation_test.generalization.utils.candidate_ids."""

from preservation_test.generalization.utils import candidate_ids

HASH_A = "a" * 64


def test_candidate_id_joins_repository_and_path():
    assert candidate_ids.candidate_id("Owner/repo", "a/b.json") == "Owner/repo:a/b.json"


def test_unit_key_uses_separator():
    key = candidate_ids.unit_key("cyclonedx", "org.x/app@1.0")
    assert key == "cyclonedx" + candidate_ids.UNIT_SEPARATOR + "org.x/app@1.0"
    assert key == "cyclonedx | org.x/app@1.0"


def test_study_id_uses_twelve_hex_prefix():
    assert candidate_ids.study_id("spdx", HASH_A) == "gen-spdx-aaaaaaaaaaaa"
    assert candidate_ids.study_id("cyclonedx", "0123456789abcdef" * 4) == (
        "gen-cyclonedx-0123456789ab"
    )


def test_study_id_distinguishes_standards_and_digests():
    other = "b" * 64
    assert candidate_ids.study_id("spdx", HASH_A) != candidate_ids.study_id(
        "cyclonedx", HASH_A
    )
    assert candidate_ids.study_id("spdx", HASH_A) != candidate_ids.study_id(
        "spdx", other
    )
