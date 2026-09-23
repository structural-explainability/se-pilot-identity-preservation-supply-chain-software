"""Step p02: build the corpus (03-corpus.toml) from 01 and 02.

    read 01-sampling.toml
    read 02-candidates.toml
    verify their hashes/provenance
    take eligible candidates only
    group by source_standard + subject
    choose lowest SHA-256 within each unit
    select every resulting unit
    write 03-corpus.toml
    refuse overwrite

Provenance verified before selection:
- 02-candidates.toml records the SHA-256 of the 01-sampling.toml it was
  built from; that must equal the current file's SHA-256.
- 02-candidates.toml records the same sampling_id and the same declared
  repositories at the same pinned revisions, and every candidate comes
  from one of those repositories at its pinned revision.

The one refusal inside selection: if the lowest SHA-256 within a unit is
shared by more than one candidate, the rule does not determine a member,
and the step refuses rather than choosing.

No clone, converter, or evaluator is used. Converter capability belongs to
the transformation matrix, after the corpus exists.

Usage (relative paths resolve against the repository root):

    uv run python -m preservation_test.generalization.p02_build_corpus
"""

import argparse
from collections import Counter, defaultdict
from pathlib import Path
import sys

from preservation_test.generalization.models.candidate import Candidate
from preservation_test.generalization.utils.candidate_ids import unit_key
from preservation_test.generalization.utils.candidate_sorting import (
    SelectedUnit,
    select_census,
)
from preservation_test.generalization.utils.candidates_record import (
    CandidatesRecord,
    CandidatesRecordError,
    load_candidates_record,
)
from preservation_test.generalization.utils.hashing import sha256_bytes
from preservation_test.generalization.utils.sampling_config import (
    SamplingConfig,
    SamplingConfigError,
    load_sampling_config,
)
from preservation_test.generalization.utils.screening import (
    corpus_row,
    provenance_fields,
    relative_to_root,
    screening_code_hashes,
)
from preservation_test.generalization.utils.toml_writer import (
    render_document,
    write_new_file,
)

REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
THIS_STEP = Path(__file__).resolve()
STEP_MODULE = f"preservation_test.generalization.{THIS_STEP.stem}"

DEFAULT_CONFIG = Path("generalization/01-sampling.toml")
DEFAULT_CANDIDATES = Path("generalization/02-candidates.toml")
DEFAULT_OUT = Path("generalization/03-corpus.toml")

EXIT_OK = 0
EXIT_REFUSED = 2


class CorpusRefusal(RuntimeError):
    """Raised when the corpus cannot be built from 01 and 02."""


def _resolve(path: Path) -> Path:
    return path if path.is_absolute() else REPOSITORY_ROOT / path


def verify_provenance(config: SamplingConfig, record: CandidatesRecord) -> None:
    """Require that 02-candidates.toml was built from this 01-sampling.toml."""
    header = record.screening
    problems: list[str] = []

    if header.get("sampling_config_sha256") != config.sha256:
        problems.append(
            "02-candidates.toml was built from a different 01-sampling.toml "
            f"(recorded {header.get('sampling_config_sha256')}, "
            f"current {config.sha256}); rebuild candidates"
        )
    if header.get("sampling_id") != config.sampling_id:
        problems.append("sampling_id differs from 01-sampling.toml")

    declared = [f"{r.name}@{r.revision}" for r in config.repositories]
    if header.get("repositories") != declared:
        problems.append("recorded repositories differ from the declared sampling frame")

    revisions = {r.name: r.revision for r in config.repositories}
    outside = sorted(
        c.id
        for c in record.candidates
        if revisions.get(c.repository) != c.repository_revision
    )
    if outside:
        problems.append(f"candidates outside the declared frame: {outside}")

    if problems:
        raise CorpusRefusal("provenance not verified:\n  " + "\n  ".join(problems))


def verify_selection_contract(config: SamplingConfig) -> None:
    """Require the declared selection contract implemented by this step."""
    problems: list[str] = []

    if config.selection_method != "census-of-eligible-units":
        problems.append(
            "selection method must be 'census-of-eligible-units', "
            f"not {config.selection_method!r}"
        )

    if config.selection_unit != "source_standard + subject":
        problems.append(
            "selection unit must be 'source_standard + subject', "
            f"not {config.selection_unit!r}"
        )

    if problems:
        raise CorpusRefusal(
            "selection contract does not match p02 implementation:\n  "
            + "\n  ".join(problems)
        )


def refuse_undetermined_units(candidates: tuple[Candidate, ...]) -> None:
    """Refuse units whose lowest SHA-256 is shared by more than one candidate."""
    lowest: dict[str, str] = {}
    members: dict[str, list[Candidate]] = defaultdict(list)
    for candidate in candidates:
        if not candidate.screening.eligible:
            continue
        unit = unit_key(candidate.source_standard, candidate.subject)
        members[unit].append(candidate)
        lowest[unit] = min(lowest.get(unit, candidate.sha256), candidate.sha256)

    tied = [
        f"{unit}: {sorted(c.id for c in group if c.sha256 == lowest[unit])}"
        for unit, group in sorted(members.items())
        if sum(1 for c in group if c.sha256 == lowest[unit]) > 1
    ]
    if tied:
        raise CorpusRefusal(
            "lowest SHA-256 is shared within a unit; the rule does not "
            "determine a member:\n  " + "\n  ".join(tied)
        )


def render_corpus(
    config: SamplingConfig,
    record: CandidatesRecord,
    selected: list[SelectedUnit],
) -> str:
    """Render 03-corpus.toml."""
    eligible = sum(1 for c in record.candidates if c.screening.eligible)
    return render_document(
        header=[
            "03-corpus.toml",
            f"Generated by {STEP_MODULE}.",
            "Census of eligible selection units from 01-sampling.toml + 02-candidates.toml.",
            "Do not edit by hand.",
        ],
        tables={
            "corpus": {
                **provenance_fields(config, REPOSITORY_ROOT),
                "candidates_record": relative_to_root(record.path, REPOSITORY_ROOT),
                "candidates_record_sha256": record.sha256,
                "selection_method": config.selection_method,
                "selection_unit": config.selection_unit,
                "within_unit_rule": config.one_document_per_unit,
                "screened_candidates": len(record.candidates),
                "eligible_candidates": eligible,
                "members": len(selected),
            },
            "corpus_code_sha256": screening_code_hashes(
                REPOSITORY_ROOT, extra=(THIS_STEP,)
            ),
        },
        arrays={"member": [corpus_row(unit) for unit in selected]},
    )


def build_corpus(config_path: Path, candidates_path: Path, out: Path) -> int:
    """Run step p02 and write 03-corpus.toml."""
    shown = relative_to_root(out, REPOSITORY_ROOT)
    if out.exists():
        sys.stderr.write(f"CORPUS NOT BUILT.\nrefusing to overwrite {shown}\n")
        return EXIT_REFUSED

    try:
        config = load_sampling_config(config_path)
        record = load_candidates_record(candidates_path)
        verify_selection_contract(config)
        verify_provenance(config, record)
        refuse_undetermined_units(record.candidates)
    except (
        OSError,
        SamplingConfigError,
        CandidatesRecordError,
        CorpusRefusal,
    ) as error:
        sys.stderr.write(f"CORPUS NOT BUILT.\n{error}\n")
        return EXIT_REFUSED

    selected = select_census(list(record.candidates))
    text = render_corpus(config, record, selected)
    write_new_file(out, text)

    print(f"wrote {shown} (sha256 {sha256_bytes(text.encode('utf-8'))})")
    print(
        f"eligible candidates: {sum(1 for c in record.candidates if c.screening.eligible)}"
    )
    print(f"members: {len(selected)}")
    for standard, count in sorted(
        Counter(u.member.source_standard for u in selected).items()
    ):
        print(f"  {standard}: {count}")
    return EXIT_OK


def main(argv: list[str] | None = None) -> int:
    """Parse arguments and run step p02."""
    parser = argparse.ArgumentParser(
        description="Step p02: build 03-corpus.toml from 01 and 02."
    )
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--candidates", type=Path, default=DEFAULT_CANDIDATES)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args(argv)
    return build_corpus(
        _resolve(args.config), _resolve(args.candidates), _resolve(args.out)
    )


if __name__ == "__main__":
    raise SystemExit(main())
