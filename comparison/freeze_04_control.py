"""freeze_04_control.py - Check, establish, or verify Freeze 04 for the IdentityOps comparison.

From the repository root:

    uv run --frozen python comparison/freeze_04_control.py --check
    uv run --frozen python comparison/freeze_04_control.py --establish
    uv run --frozen python comparison/freeze_04_control.py --verify

The PowerShell wrapper also runs the three arm self-tests.

Development runs of both arms preceded this freeze. The specification
records that chronology. Establishment requires a clean committed tree
and an absent Freeze 04 output directory. Verification permits later output.
"""

import argparse
from datetime import UTC, datetime
import os
from pathlib import Path
import re
import subprocess

from preservation_test.generalization.freeze_02 import contained, verify_06_freeze_02
from preservation_test.generalization.utils.hashing import sha256_file

ROOT = Path(__file__).resolve().parents[1]

RECORD = "contracts/FREEZE_04_IDENTITYOPS_COMPARISON.md"
FREEZE_02_RECORD = "contracts/FREEZE_02_GENERALIZATION.md"
FREEZE_03_RECORD = "contracts/FREEZE_03_KERNEL_MISSING_VALUES.md"
MAPPING = "comparison/freeze_04_operation_mapping.md"
SPECIFICATION = "comparison/freeze_04_specification.md"
REFERENCE = "comparison/freeze_04_reference.py"
IDENTITYOPS = "comparison/freeze_04_identityops.py"
BASELINE_PROGRAM = "comparison/freeze_04_baseline.ido"
RESTRICTED_PROGRAM = "comparison/freeze_04_restricted.ido"
COMPARE = "comparison/freeze_04_compare.py"
SELF = "comparison/freeze_04_control.py"
WRAPPER = "freeze_04.ps1"

PREPARED = "comparison/prepared/freeze_02.json"

EVIDENCE_COMMIT = "e1befa159faff965b32a47975ac355bb6a9ccb18"
IDENTITYOPS_COMMIT = "7060cd084801e72f2c31175afef035d057979e8a"
PREPARED_SHA256 = "17eaa9518e1754a860319532d8e66a317978d3a41fb711a8e47318c23f7699f7"

INVENTORY = (
    MAPPING,
    SPECIFICATION,
    REFERENCE,
    IDENTITYOPS,
    BASELINE_PROGRAM,
    RESTRICTED_PROGRAM,
    COMPARE,
    SELF,
    WRAPPER,
    FREEZE_02_RECORD,
    FREEZE_03_RECORD,
)
OUTPUT_DIRECTORY = "comparison/results/freeze_04"

HASH_LINE = re.compile(
    r"^- `([0-9a-f]{64})`  `([^`]+)`[ \t]*$",
    re.MULTILINE,
)
COMMIT_LINE = re.compile(
    r"^\*\*Frozen content commit:\*\* `([0-9a-f]{40})`[ \t]*$",
    re.MULTILINE,
)


def git(root: Path, *args: str) -> str:
    """Run Git in the repository and return its stripped text output."""
    return subprocess.check_output(["git", *args], cwd=root, text=True).strip()


def require_ancestor(root: Path, commit: str) -> None:
    """Require the supplied commit to exist and be an ancestor of HEAD."""
    result = subprocess.run(
        ["git", "merge-base", "--is-ancestor", commit, "HEAD"],
        cwd=root,
        check=False,
    )
    if result.returncode != 0:
        raise ValueError(
            f"Commit is unavailable or is not an ancestor of HEAD: {commit}"
        )


def pin(text: str, name: str, length: int) -> str:
    """Read one literal lowercase hexadecimal assignment of the given length."""
    pattern = rf'^{name} = "([0-9a-f]{{{length}}})"[ \t]*\r?$'
    found = re.findall(pattern, text, flags=re.MULTILINE)
    if len(found) != 1:
        raise ValueError(f"Expected exactly one {name} assignment, found {len(found)}")
    return found[0]


def check_pins(root: Path) -> None:
    """Check the evidence, input, and IdentityOps pins across the apparatus."""
    reference = contained(root, REFERENCE).read_text(encoding="utf-8")
    identityops = contained(root, IDENTITYOPS).read_text(encoding="utf-8")
    specification = contained(root, SPECIFICATION).read_text(encoding="utf-8")

    for relative, text in ((REFERENCE, reference), (IDENTITYOPS, identityops)):
        if pin(text, "EVIDENCE_COMMIT", 40) != EVIDENCE_COMMIT:
            raise ValueError(f"{relative}: evidence commit mismatch")
        if pin(text, "PREPARED_SHA256", 64) != PREPARED_SHA256:
            raise ValueError(f"{relative}: prepared input digest mismatch")

    if pin(identityops, "IDENTITYOPS_COMMIT", 40) != IDENTITYOPS_COMMIT:
        raise ValueError(f"{IDENTITYOPS}: IdentityOps commit mismatch")

    dependency_pin = f"se-identity-ops.git@{IDENTITYOPS_COMMIT}"
    if identityops.count(dependency_pin) != 1:
        raise ValueError(f"{IDENTITYOPS}: expected one pinned IdentityOps dependency")

    for value in (EVIDENCE_COMMIT, IDENTITYOPS_COMMIT, PREPARED_SHA256, RECORD):
        if value not in specification:
            raise ValueError(f"{SPECIFICATION}: required value is missing: {value}")


def check_prepared(root: Path) -> None:
    """Require the prepared input to match its pinned digest."""
    if sha256_file(contained(root, PREPARED)) != PREPARED_SHA256:
        raise ValueError(f"Prepared input digest differs from the pin: {PREPARED}")


def check_inputs(root: Path) -> None:
    """Check establishing prerequisites apart from the clean-tree requirement."""
    verify_06_freeze_02(root)

    for relative in INVENTORY:
        if not contained(root, relative).is_file():
            raise ValueError(f"Required artifact missing: {relative}")

    check_pins(root)
    check_prepared(root)
    require_ancestor(root, EVIDENCE_COMMIT)

    if contained(root, OUTPUT_DIRECTORY).exists():
        raise ValueError(
            f"Comparison output directory already exists: {OUTPUT_DIRECTORY}"
        )


def check_clean(root: Path) -> None:
    """Require a clean tree, including untracked files."""
    if git(root, "status", "--porcelain", "--untracked-files=all"):
        raise ValueError("Commit the complete preparation state before Freeze 04")


def render(root: Path) -> str:
    """Create the record text and current artifact digests."""
    head = git(root, "rev-parse", "HEAD")
    timestamp = datetime.now(UTC).isoformat()
    hashes = "\n".join(
        f"- `{sha256_file(contained(root, path))}`  `{path}`"
        for path in sorted(INVENTORY)
    )

    return f"""# Freeze 04. IdentityOps Comparison

## Scope

This record freezes the IdentityOps comparison under two anchor-algorithm policies.

The mapping records the operation-to-language decisions.
The specification records the encoding, schemas, controls, commands,
and reporting rules.

See [Operation Mapping](../comparison/freeze_04_operation_mapping.md)
and [Specification](../comparison/freeze_04_specification.md).

## Chronology

The comparison design and both arms were developed after the Freeze 03 report.
Development runs of both arms on the prepared input preceded this freeze.
Their counts and their agreement are recorded in the specification.

At establishment, `comparison/results/freeze_04/` was absent.
The frozen commands create the formal outputs.

## Pinned Inputs and Implementations

- Baseline evidence commit: `{EVIDENCE_COMMIT}`
- Prepared input SHA-256: `{PREPARED_SHA256}`
- IdentityOps commit: `{IDENTITYOPS_COMMIT}`

## Outputs

- Reference arm: `comparison/results/freeze_04/reference.json`
- Anchor table: `comparison/results/freeze_04/anchors.csv`
- IdentityOps arm: `comparison/results/freeze_04/identityops.json`
- Transitions: `comparison/results/freeze_04/transitions.json`

The inventory below covers the execution apparatus.
The generated outputs are preserved after execution.

## Verification

Verification checks every listed digest, the declared pins,
the prepared input digest, commit ancestry, and Freeze 02 integrity.
It permits comparison outputs after establishment.

```powershell
.\\freeze_04.ps1 -Verify
```

The pre-execution content commit identifies the preparation state.
The protocol requires separate review and commitment of this record
before formal execution.
Record generation does not perform that commitment.

## Frozen Content Hashes

**Status:** FROZEN

**Frozen (UTC):** {timestamp}

**Frozen content commit:** `{head}`

{hashes}
"""


def verify(root: Path) -> str:
    """Verify the established apparatus and return the record digest."""
    root = root.resolve()
    record = contained(root, RECORD)
    if not record.is_file():
        raise ValueError("Freeze 04 has not been established")

    text = record.read_text(encoding="utf-8")
    if "**Status:** FROZEN" not in text:
        raise ValueError("Freeze 04 record is missing its frozen status")

    commits = COMMIT_LINE.findall(text)
    if len(commits) != 1:
        raise ValueError("Freeze 04 must state exactly one content commit")

    entries = HASH_LINE.findall(text)
    hashes = {path: digest for digest, path in entries}
    if len(hashes) != len(entries):
        raise ValueError("Freeze 04 contains duplicate artifact paths")

    if set(hashes) != set(INVENTORY):
        raise ValueError(
            "Freeze 04 inventory mismatch: "
            f"missing={sorted(set(INVENTORY) - set(hashes))}, "
            f"extra={sorted(set(hashes) - set(INVENTORY))}"
        )

    for path, expected in hashes.items():
        actual = sha256_file(contained(root, path))
        if actual != expected:
            raise ValueError(f"Freeze 04 hash mismatch: {path}")

    verify_06_freeze_02(root)
    check_pins(root)
    check_prepared(root)
    require_ancestor(root, EVIDENCE_COMMIT)
    require_ancestor(root, commits[0])

    return sha256_file(record)


def establish(root: Path) -> None:
    """Establish the freeze once from a clean committed preparation state."""
    root = root.resolve()
    record = contained(root, RECORD)
    if record.exists():
        raise ValueError("Freeze 04 already exists")

    check_clean(root)
    check_inputs(root)

    pending = record.with_suffix(".pending")
    with pending.open("x", encoding="utf-8", newline="\n") as handle:
        handle.write(render(root))

    try:
        os.link(pending, record)
    finally:
        pending.unlink()

    verify(root)
    print(
        "Freeze 04 written and verified. "
        "Review and commit the record before formal execution."
    )


def main() -> None:
    """Dispatch the explicitly requested freeze operation."""
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--establish", action="store_true")
    mode.add_argument("--verify", action="store_true")
    args = parser.parse_args()

    if args.check:
        if contained(ROOT, RECORD).exists():
            raise ValueError("Freeze 04 already exists")
        check_inputs(ROOT)
        print("Freeze 04 checks passed. No comparison artifacts were written.")
    elif args.establish:
        establish(ROOT)
    else:
        print(f"Freeze 04 verified: {verify(ROOT)}")


if __name__ == "__main__":
    main()
