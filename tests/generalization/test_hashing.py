"""Tests for preservation_test.generalization.utils.hashing."""

import pytest

from preservation_test.generalization.utils import hashing

HASH_A = "a" * 64
# SHA-256 of b"abc", a published test vector.
ABC = "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"


def test_sha256_bytes_known_vector():
    assert hashing.sha256_bytes(b"abc") == ABC
    assert hashing.sha256_bytes(b"") == (
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    )


def test_sha256_file_matches_bytes(tmp_path):
    path = tmp_path / "x.bin"
    path.write_bytes(b"abc")
    assert hashing.sha256_file(path) == ABC


def test_sha256_file_large_multiblock(tmp_path):
    data = b"\x00\x01\x02\x03" * 500_000  # exceeds the 1 MiB read block
    path = tmp_path / "big.bin"
    path.write_bytes(data)
    assert hashing.sha256_file(path) == hashing.sha256_bytes(data)


def test_normalize_sha256_accepts_and_lowercases():
    assert hashing.normalize_sha256("  " + HASH_A.upper() + " ") == HASH_A
    assert hashing.normalize_sha256(HASH_A) == HASH_A


@pytest.mark.parametrize("bad", ["", "abc", "g" * 64, HASH_A + "0", HASH_A[:-1]])
def test_normalize_sha256_rejects(bad):
    with pytest.raises(ValueError):
        hashing.normalize_sha256(bad)
