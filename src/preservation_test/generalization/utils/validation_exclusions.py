"""Derive engineering-validation exclusions mechanically from this repository.

Every SBOM JSON under validation/ and the synthetic fixtures contributes its
SHA-256 and, where resolvable from source metadata, its subject key. The
sampling specification must list all of them. It may list more, but not
fewer.
"""

from dataclasses import dataclass
from pathlib import Path

from preservation_test.generalization.utils.hashing import sha256_file
from preservation_test.generalization.utils.sampling_config import SamplingConfig
from preservation_test.generalization.utils.source_detection import (
    SBOM_STANDARDS,
    detect_source_format,
    parse_json_object,
)
from preservation_test.generalization.utils.subject_resolution import (
    METHOD_PATH,
    resolve_subject,
)

VALIDATION_ROOTS = (
    Path("validation"),
    Path("src/preservation_test/fixtures"),
)
REASON = "used-in-engineering-validation"


@dataclass(frozen=True)
class DerivedExclusion:
    """One exclusion required by an engineering-validation artifact."""

    kind: str
    value: str
    provenance: str


def derive_validation_exclusions(repository_root: Path) -> list[DerivedExclusion]:
    """Return the SHA-256 and subject exclusions implied by validation artifacts."""
    derived: dict[tuple[str, str], DerivedExclusion] = {}

    for root in VALIDATION_ROOTS:
        base = repository_root / root
        if not base.is_dir():
            continue
        for path in sorted(base.rglob("*.json")):
            parsed = parse_json_object(path.read_bytes())
            if parsed.document is None:
                continue
            source_format = detect_source_format(parsed.document)
            if source_format.standard not in SBOM_STANDARDS:
                continue

            provenance = path.relative_to(repository_root).as_posix()
            digest = sha256_file(path)
            derived.setdefault(
                ("sha256", digest),
                DerivedExclusion("sha256", digest, provenance),
            )

            subject = resolve_subject(
                parsed.document, source_format.standard, "validation", provenance
            )
            if subject.method != METHOD_PATH:
                derived.setdefault(
                    ("subject", subject.key),
                    DerivedExclusion("subject", subject.key, provenance),
                )

    return sorted(derived.values(), key=lambda item: (item.kind, item.value))


def missing_exclusions(
    config: SamplingConfig,
    derived: list[DerivedExclusion],
) -> list[DerivedExclusion]:
    """Return derived exclusions that the sampling specification does not list."""
    declared = {(item.kind, item.value) for item in config.validation_exclusions}
    return [item for item in derived if (item.kind, item.value) not in declared]


def render_exclusion_entries(derived: list[DerivedExclusion]) -> str:
    """Render derived exclusions as [[validation_exclusion]] TOML entries."""
    blocks = [
        "\n".join(
            [
                "[[validation_exclusion]]",
                f'kind = "{item.kind}"',
                f'value = "{item.value}"',
                f'reason = "{REASON}"',
                f'provenance = "{item.provenance}"',
            ]
        )
        for item in derived
    ]
    return "\n\n".join(blocks) + "\n"
