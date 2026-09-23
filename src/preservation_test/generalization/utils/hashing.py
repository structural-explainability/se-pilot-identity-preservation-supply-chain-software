"""SHA-256 helpers for generalization corpus construction.

Digests are lowercase hexadecimal. Comparisons against recorded values
normalize case so that uppercase digests recorded elsewhere in the
repository still compare correctly.
"""

from hashlib import sha256
from pathlib import Path

_HEX = frozenset("0123456789abcdef")


def sha256_bytes(data: bytes) -> str:
    """Return the lowercase SHA-256 digest of raw bytes."""
    return sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    """Return the lowercase SHA-256 digest of a file's exact bytes."""
    digest = sha256()
    with path.open("rb") as handle:
        while block := handle.read(1024 * 1024):
            digest.update(block)
    return digest.hexdigest()


def normalize_sha256(value: str) -> str:
    """Validate and lowercase a SHA-256 hex digest."""
    text = value.strip().lower()
    if len(text) != 64 or not set(text) <= _HEX:
        raise ValueError(f"not a SHA-256 hex digest: {value!r}")
    return text
