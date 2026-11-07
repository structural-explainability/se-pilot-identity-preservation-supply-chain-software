"""freeze_04_compare.py - Compare the two Freeze 04 arms and summarize the policy transitions.

Before the Freeze 04 freeze, use the checks only:

    uv run --frozen python comparison/freeze_04_compare.py --self-test

After the Freeze 04 freeze and after both arms have run:

    uv run --frozen python comparison/freeze_04_compare.py --run

Input:
    comparison/results/freeze_04/reference.json
    comparison/results/freeze_04/identityops.json

Output:
    comparison/results/freeze_04/transitions.json

The comparison reports, per arm, how each source occurrence moves from its
baseline class to its restricted class, and where the two arms disagree.
It reads only the two arm outputs. The record lists every source occurrence
with its baseline and restricted classes in each arm.
"""

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import tempfile
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / "comparison" / "results" / "freeze_04"
REFERENCE = DIRECTORY / "reference.json"
IDENTITYOPS = DIRECTORY / "identityops.json"
OUTPUT = DIRECTORY / "transitions.json"

CLASSES = ("authorized", "ambiguous", "no_matching_target", "no_source_anchor")
EXAMPLE_LIMIT = 20

JsonObject = dict[str, Any]


def sha256(content: bytes) -> str:
    """Return the SHA-256 digest of the given bytes."""
    return hashlib.sha256(content).hexdigest()


def candidate_pointers(record: JsonObject) -> list[str]:
    """Return the candidate target pointers of one policy record."""
    return [candidate["pointer"] for candidate in record["candidates"]]


def evaluated_records(report: JsonObject) -> dict[tuple[str, str], JsonObject]:
    """Index the per-occurrence records of one arm by route and pointer."""
    records: dict[tuple[str, str], JsonObject] = {}
    for route in report["routes"]:
        if route.get("analysis_status") != "evaluated":
            continue
        for record in route["records"]:
            records[(route["route_id"], record["pointer"])] = record
    return records


def transition_matrix(records: dict[tuple[str, str], JsonObject]) -> JsonObject:
    """Count baseline-to-restricted class pairs over the given records."""
    pairs = Counter(
        (record["baseline"]["classification"], record["restricted"]["classification"])
        for record in records.values()
    )
    matrix = {
        before: {after: pairs.get((before, after), 0) for after in CLASSES}
        for before in CLASSES
    }
    changed = sum(count for (before, after), count in pairs.items() if before != after)
    return {"matrix": matrix, "occurrences": sum(pairs.values()), "changed": changed}


def route_matrices(
    records: dict[tuple[str, str], JsonObject],
) -> dict[str, JsonObject]:
    """Count transitions per route."""
    by_route: dict[str, dict[tuple[str, str], JsonObject]] = {}
    for (route_id, pointer), record in records.items():
        by_route.setdefault(route_id, {})[(route_id, pointer)] = record
    return {
        route_id: transition_matrix(route_records)
        for route_id, route_records in sorted(by_route.items())
    }


def change_causes(records: dict[tuple[str, str], JsonObject]) -> list[JsonObject]:
    """Count changed occurrences by transition and excluded algorithm set."""
    causes: Counter[tuple[str, str, tuple[str, ...]]] = Counter()
    for record in records.values():
        before = record["baseline"]["classification"]
        after = record["restricted"]["classification"]
        if before == after:
            continue
        # Dropped algorithms are admitted under baseline and not under restricted.
        restricted_admitted = set(record["restricted"]["admitted_algorithms"])
        dropped = tuple(
            sorted(set(record["baseline"]["admitted_algorithms"]) - restricted_admitted)
        )
        causes[(before, after, dropped)] += 1
    return [
        {
            "baseline": before,
            "restricted": after,
            "dropped_algorithms": list(dropped),
            "occurrences": count,
        }
        for (before, after, dropped), count in sorted(causes.items())
    ]


def ambiguity_persistence(records: dict[tuple[str, str], JsonObject]) -> JsonObject:
    """Check whether occurrences ambiguous under both policies keep their candidates."""
    both = 0
    same = 0
    for record in records.values():
        if (
            record["baseline"]["classification"] == "ambiguous"
            and record["restricted"]["classification"] == "ambiguous"
        ):
            both += 1
            if candidate_pointers(record["baseline"]) == candidate_pointers(
                record["restricted"]
            ):
                same += 1
    return {"ambiguous_in_both_policies": both, "same_candidate_set": same}


def disagreements(
    first: dict[tuple[str, str], JsonObject],
    second: dict[tuple[str, str], JsonObject],
) -> JsonObject:
    """Compare the two arms occurrence by occurrence."""
    missing_in_second = sorted(set(first) - set(second))
    missing_in_first = sorted(set(second) - set(first))
    counts = {"classification": 0, "candidates": 0, "algorithms": 0}
    examples: list[JsonObject] = []

    for key in sorted(set(first) & set(second)):
        for policy in ("baseline", "restricted"):
            a = first[key][policy]
            b = second[key][policy]
            differences = []
            if a["classification"] != b["classification"]:
                counts["classification"] += 1
                differences.append("classification")
            if a["candidates"] != b["candidates"]:
                counts["candidates"] += 1
                differences.append("candidates")
            if (
                a["admitted_algorithms"] != b["admitted_algorithms"]
                or a["excluded_algorithms"] != b["excluded_algorithms"]
            ):
                counts["algorithms"] += 1
                differences.append("algorithms")
            if differences and len(examples) < EXAMPLE_LIMIT:
                examples.append(
                    {
                        "route_id": key[0],
                        "pointer": key[1],
                        "policy": policy,
                        "differences": differences,
                    }
                )

    return {
        "occurrences_compared": len(set(first) & set(second)),
        "missing_in_identityops": [
            list(key) for key in missing_in_second[:EXAMPLE_LIMIT]
        ],
        "missing_in_reference": [list(key) for key in missing_in_first[:EXAMPLE_LIMIT]],
        "missing_count": len(missing_in_second) + len(missing_in_first),
        "differences": counts,
        "examples": examples,
    }


def occurrence_transitions(
    first: dict[tuple[str, str], JsonObject],
    second: dict[tuple[str, str], JsonObject],
) -> list[JsonObject]:
    """List every source occurrence with its classes under both policies per arm."""

    def classes(records: dict[tuple[str, str], JsonObject], key: tuple[str, str]):
        record = records.get(key)
        if record is None:
            return None
        return [
            record["baseline"]["classification"],
            record["restricted"]["classification"],
        ]

    return [
        {
            "route_id": key[0],
            "pointer": key[1],
            "reference": classes(first, key),
            "identityops": classes(second, key),
        }
        for key in sorted(set(first) | set(second))
    ]


def compare(reference: JsonObject, identityops: JsonObject) -> JsonObject:
    """Build the transition record from the two arm outputs."""
    for field in ("evidence_commit", "prepared_sha256"):
        if reference[field] != identityops[field]:
            raise ValueError(f"The arms disagree on {field}")

    first = evaluated_records(reference)
    second = evaluated_records(identityops)

    return {
        "arms": {
            "reference": transition_matrix(first),
            "identityops": transition_matrix(second),
        },
        "causes": {
            "reference": change_causes(first),
            "identityops": change_causes(second),
        },
        "ambiguity_persistence": {
            "reference": ambiguity_persistence(first),
            "identityops": ambiguity_persistence(second),
        },
        "routes": {
            "reference": route_matrices(first),
            "identityops": route_matrices(second),
        },
        "agreement": disagreements(first, second),
        "occurrences": occurrence_transitions(first, second),
    }


def synthetic_arm(shift: bool) -> JsonObject:
    """Build a one-route arm output; shift moves one occurrence's classification."""

    def policy(label: str, admitted: list[str], candidates: list[str]) -> JsonObject:
        return {
            "admitted_algorithms": admitted,
            "excluded_algorithms": [],
            "candidates": [
                {"pointer": pointer, "shared_algorithms": admitted}
                for pointer in candidates
            ],
            "classification": label,
        }

    records = [
        {
            "pointer": "/components/0",
            "baseline": policy("authorized", ["SHA-256"], ["/packages/0"]),
            "restricted": policy("authorized", ["SHA-256"], ["/packages/0"]),
        },
        {
            "pointer": "/components/1",
            "baseline": policy("authorized", ["SHA-1"], ["/packages/1"]),
            "restricted": policy("no_source_anchor", [], []),
        },
        {
            "pointer": "/components/2",
            "baseline": policy(
                "ambiguous", ["SHA-256"], ["/packages/2", "/packages/3"]
            ),
            "restricted": policy(
                "authorized" if shift else "ambiguous",
                ["SHA-256"],
                ["/packages/2"] if shift else ["/packages/2", "/packages/3"],
            ),
        },
    ]
    return {
        "evidence_commit": "synthetic",
        "prepared_sha256": "synthetic",
        "routes": [
            {
                "route_id": "route-a",
                "status": "completed",
                "analysis_status": "evaluated",
                "records": records,
            },
            {
                "route_id": "route-b",
                "status": "failed",
                "analysis_status": "no_completed_conversion",
            },
        ],
    }


def self_test() -> None:
    """Check the comparison on small arm outputs with known answers."""
    same = compare(synthetic_arm(False), synthetic_arm(False))
    if same["arms"]["reference"]["changed"] != 1:
        raise AssertionError("Expected one changed occurrence")
    if same["arms"]["reference"]["matrix"]["authorized"]["no_source_anchor"] != 1:
        raise AssertionError("Expected one authorized to no_source_anchor transition")
    if same["causes"]["reference"] != [
        {
            "baseline": "authorized",
            "restricted": "no_source_anchor",
            "dropped_algorithms": ["SHA-1"],
            "occurrences": 1,
        }
    ]:
        raise AssertionError("Unexpected change causes")
    if same["ambiguity_persistence"]["reference"] != {
        "ambiguous_in_both_policies": 1,
        "same_candidate_set": 1,
    }:
        raise AssertionError("Unexpected ambiguity persistence")
    if same["agreement"]["differences"] != {
        "classification": 0,
        "candidates": 0,
        "algorithms": 0,
    }:
        raise AssertionError("Identical arms must not disagree")
    if same["agreement"]["missing_count"] != 0:
        raise AssertionError("Identical arms must cover the same occurrences")
    if same["occurrences"][1] != {
        "route_id": "route-a",
        "pointer": "/components/1",
        "reference": ["authorized", "no_source_anchor"],
        "identityops": ["authorized", "no_source_anchor"],
    }:
        raise AssertionError("Unexpected occurrence transition")
    if len(same["occurrences"]) != 3:
        raise AssertionError("Expected one transition per evaluated occurrence")

    different = compare(synthetic_arm(False), synthetic_arm(True))
    if different["agreement"]["differences"]["classification"] != 1:
        raise AssertionError("Expected a classification disagreement")
    if different["agreement"]["differences"]["candidates"] != 1:
        raise AssertionError("Expected a candidate disagreement")
    if different["agreement"]["examples"][0]["differences"] != [
        "classification",
        "candidates",
    ]:
        raise AssertionError("Unexpected disagreement example")

    print("Comparison synthetic checks passed.")


def run() -> None:
    """Write the transition record once."""
    if OUTPUT.exists():
        raise FileExistsError(f"Transition record already exists: {OUTPUT}")

    reference_bytes = REFERENCE.read_bytes()
    identityops_bytes = IDENTITYOPS.read_bytes()
    record = {
        "schema_version": 1,
        "script_sha256": sha256(Path(__file__).read_bytes()),
        "inputs": {
            "reference": {
                "path": "comparison/results/freeze_04/reference.json",
                "sha256": sha256(reference_bytes),
            },
            "identityops": {
                "path": "comparison/results/freeze_04/identityops.json",
                "sha256": sha256(identityops_bytes),
            },
        },
        **compare(json.loads(reference_bytes), json.loads(identityops_bytes)),
    }

    with tempfile.TemporaryDirectory(dir=DIRECTORY) as temporary:
        pending = Path(temporary) / "transitions.json"
        with pending.open("w", encoding="utf-8", newline="\n") as stream:
            json.dump(record, stream, ensure_ascii=False, indent=2, allow_nan=False)
            stream.write("\n")
        # Same-volume hard link: publish atomically and refuse an existing file.
        OUTPUT.hardlink_to(pending)

    print(OUTPUT)


def main() -> None:
    """Entry point for the arm comparison."""
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--self-test", action="store_true")
    mode.add_argument("--run", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        self_test()
    else:
        run()


if __name__ == "__main__":
    main()
