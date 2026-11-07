"""freeze_04_reference.py - Run the Python reference arm of the Freeze 04 anchor-policy comparison.

Before the Freeze 04 freeze, use the checks only:

    uv run --frozen python comparison/freeze_04_reference.py --self-test

After the Freeze 04 freeze:

    uv run --frozen python comparison/freeze_04_reference.py --run

Input:
    comparison/prepared/freeze_02.json

Output:
    comparison/results/freeze_04/reference.json

For every source occurrence in every completed route, the arm classifies
correspondence under two anchor policies:

    baseline    every algorithm spelling present in the prepared anchors
    restricted  exactly SHA-256, SHA-384 and SHA-512, as spelled

A source occurrence is classified by its admitted anchors and the target
occurrences that share one of them (equal algorithm and equal value):

    no_source_anchor    no admitted anchor
    no_matching_target  no target shares an admitted anchor
    authorized          exactly one target shares an admitted anchor
    ambiguous           more than one target shares an admitted anchor

This arm reads only the prepared JSON. It does not call the evaluator.
It writes nothing during --self-test.
"""

import argparse
import hashlib
import json
from pathlib import Path
import tempfile
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "comparison" / "prepared" / "freeze_02.json"
OUTPUT = ROOT / "comparison" / "results" / "freeze_04" / "reference.json"

EVIDENCE_COMMIT = "e1befa159faff965b32a47975ac355bb6a9ccb18"
PREPARED_SHA256 = "17eaa9518e1754a860319532d8e66a317978d3a41fb711a8e47318c23f7699f7"

POLICY_NAMES = ("baseline", "restricted")
RESTRICTED_ALGORITHMS = ("SHA-256", "SHA-384", "SHA-512")

JsonObject = dict[str, Any]


def sha256(content: bytes) -> str:
    """Return the SHA-256 digest of the given bytes."""
    return hashlib.sha256(content).hexdigest()


def is_admitted(policy: str, algorithm: str) -> bool:
    """Return whether a policy admits an anchor algorithm spelling."""
    if policy == "baseline":
        return True
    if policy == "restricted":
        return algorithm in RESTRICTED_ALGORITHMS
    raise ValueError(f"Unknown policy: {policy}")


def classify_source(
    policy: str,
    source: JsonObject,
    target_index: dict[tuple[str, str], list[int]],
    target_pointers: list[str],
) -> JsonObject:
    """Classify one source occurrence under one policy and keep its trace."""
    admitted: list[str] = []
    excluded: list[str] = []
    shared: dict[int, list[str]] = {}

    for algorithm, value in source["anchors"]:
        if not is_admitted(policy, algorithm):
            excluded.append(algorithm)
            continue
        admitted.append(algorithm)
        for position in target_index.get((algorithm, value), []):
            algorithms = shared.setdefault(position, [])
            if algorithm not in algorithms:
                algorithms.append(algorithm)

    candidates = [
        {
            "pointer": target_pointers[position],
            "shared_algorithms": sorted(shared[position]),
        }
        for position in sorted(shared)
    ]

    if not admitted:
        classification = "no_source_anchor"
    elif not candidates:
        classification = "no_matching_target"
    elif len(candidates) == 1:
        classification = "authorized"
    else:
        classification = "ambiguous"

    return {
        "admitted_algorithms": sorted(admitted),
        "excluded_algorithms": sorted(excluded),
        "candidates": candidates,
        "classification": classification,
    }


def classify_route(route: JsonObject) -> list[JsonObject]:
    """Classify every source occurrence of one completed route under both policies."""
    target_pointers = [target["pointer"] for target in route["target_rows"]]
    target_index: dict[tuple[str, str], list[int]] = {}
    for position, target in enumerate(route["target_rows"]):
        for algorithm, value in target["anchors"]:
            positions = target_index.setdefault((algorithm, value), [])
            if position not in positions:
                positions.append(position)

    records = []
    for source in route["source_rows"]:
        records.append(
            {
                "pointer": source["pointer"],
                "baseline": classify_source(
                    "baseline", source, target_index, target_pointers
                ),
                "restricted": classify_source(
                    "restricted", source, target_index, target_pointers
                ),
            }
        )
    return records


def count_classes(records: list[JsonObject]) -> dict[str, dict[str, int]]:
    """Count classifications per policy."""
    counts: dict[str, dict[str, int]] = {}
    for policy in POLICY_NAMES:
        policy_counts: dict[str, int] = {}
        for record in records:
            label = record[policy]["classification"]
            policy_counts[label] = policy_counts.get(label, 0) + 1
        counts[policy] = dict(sorted(policy_counts.items()))
    return counts


def compare_with_prepared(route: JsonObject, records: list[JsonObject]) -> JsonObject:
    """Compare the baseline arm with the correspondences prepared from the evaluator."""
    prepared = {item["source_pointer"]: item for item in route["correspondences"]}
    status_mismatches = 0
    candidate_mismatches = 0
    for record in records:
        expected = prepared[record["pointer"]]
        actual = record["baseline"]
        if actual["classification"] != expected["status"]:
            status_mismatches += 1
        actual_pointers = sorted(item["pointer"] for item in actual["candidates"])
        if actual_pointers != sorted(expected["candidate_target_pointers"]):
            candidate_mismatches += 1
    return {
        "sources": len(records),
        "prepared_correspondences": len(prepared),
        "status_mismatches": status_mismatches,
        "candidate_mismatches": candidate_mismatches,
    }


def analyze(prepared: JsonObject) -> list[JsonObject]:
    """Analyze every route in the prepared input."""
    routes = []
    for route in prepared["routes"]:
        if route["status"] != "completed":
            routes.append(
                {
                    "route_id": route["route_id"],
                    "status": route["status"],
                    "analysis_status": "no_completed_conversion",
                }
            )
            continue

        records = classify_route(route)
        routes.append(
            {
                "route_id": route["route_id"],
                "status": route["status"],
                "analysis_status": "evaluated",
                "counts": count_classes(records),
                "agreement_with_prepared_baseline": compare_with_prepared(
                    route, records
                ),
                "records": records,
            }
        )
    return routes


def total_counts(routes: list[JsonObject]) -> JsonObject:
    """Sum classification counts and prepared-agreement counts across routes."""
    classes: dict[str, dict[str, int]] = {name: {} for name in POLICY_NAMES}
    sources = status_mismatches = candidate_mismatches = 0
    for route in routes:
        if route["analysis_status"] != "evaluated":
            continue
        for policy in POLICY_NAMES:
            for label, number in route["counts"][policy].items():
                classes[policy][label] = classes[policy].get(label, 0) + number
        agreement = route["agreement_with_prepared_baseline"]
        sources += agreement["sources"]
        status_mismatches += agreement["status_mismatches"]
        candidate_mismatches += agreement["candidate_mismatches"]
    return {
        "classifications": {
            policy: dict(sorted(classes[policy].items())) for policy in POLICY_NAMES
        },
        "sources": sources,
        "baseline_status_mismatches_with_prepared": status_mismatches,
        "baseline_candidate_mismatches_with_prepared": candidate_mismatches,
    }


def read_prepared() -> tuple[bytes, JsonObject]:
    """Read the prepared input and verify its pins."""
    content = INPUT.read_bytes()
    if sha256(content) != PREPARED_SHA256:
        raise ValueError(f"Prepared input digest differs from the pin: {INPUT}")
    prepared = json.loads(content)
    if prepared["evidence_commit"] != EVIDENCE_COMMIT:
        raise ValueError(f"Unexpected evidence commit in {INPUT}")
    return content, prepared


def synthetic_prepared() -> JsonObject:
    """Build a small prepared-style input with one case per required control."""

    def source(number: int, anchors: list[list[str]]) -> JsonObject:
        return {"pointer": f"/components/{number}", "anchors": anchors}

    def target(number: int, anchors: list[list[str]]) -> JsonObject:
        return {"pointer": f"/packages/{number}", "anchors": anchors}

    def correspondence(number: int, status: str, targets: list[int]) -> JsonObject:
        return {
            "source_pointer": f"/components/{number}",
            "status": status,
            "candidate_target_pointers": [f"/packages/{item}" for item in targets],
        }

    route_a = {
        "route_id": "route-a",
        "status": "completed",
        "source_rows": [
            source(0, [["SHA-256", "a1"]]),
            source(1, [["SHA-256", "b1"]]),
            source(2, [["SHA-256", "c1"]]),
            source(3, []),
            source(4, [["SHA-1", "d1"]]),
            source(5, [["SHA-1", "e1"], ["SHA-256", "e2"]]),
            source(6, [["SHA-384", "f1"]]),
            source(7, [["SHA-384", "g1"]]),
        ],
        "target_rows": [
            target(0, [["SHA-256", "a1"]]),
            target(1, [["SHA-256", "c1"]]),
            target(2, [["SHA-256", "c1"]]),
            target(3, [["SHA-1", "d1"]]),
            target(4, [["SHA-256", "e2"]]),
            target(5, [["SHA-1", "e1"]]),
            target(6, [["SHA384", "f1"]]),
            target(7, [["SHA-384", "g1"]]),
        ],
        "correspondences": [
            correspondence(0, "authorized", [0]),
            correspondence(1, "no_matching_target", []),
            correspondence(2, "ambiguous", [1, 2]),
            correspondence(3, "no_source_anchor", []),
            correspondence(4, "authorized", [3]),
            correspondence(5, "ambiguous", [4, 5]),
            correspondence(6, "no_matching_target", []),
            correspondence(7, "authorized", [7]),
        ],
    }
    route_b = {
        "route_id": "route-b",
        "status": "completed",
        "source_rows": [source(0, [["SHA-256", "a1"]])],
        "target_rows": [],
        "correspondences": [correspondence(0, "no_matching_target", [])],
    }
    return {"routes": [route_a, route_b]}


SYNTHETIC_EXPECTED = {
    ("route-a", "/components/0"): ("authorized", "authorized"),
    ("route-a", "/components/1"): ("no_matching_target", "no_matching_target"),
    ("route-a", "/components/2"): ("ambiguous", "ambiguous"),
    ("route-a", "/components/3"): ("no_source_anchor", "no_source_anchor"),
    ("route-a", "/components/4"): ("authorized", "no_source_anchor"),
    ("route-a", "/components/5"): ("ambiguous", "authorized"),
    ("route-a", "/components/6"): ("no_matching_target", "no_matching_target"),
    ("route-a", "/components/7"): ("authorized", "authorized"),
    ("route-b", "/components/0"): ("no_matching_target", "no_matching_target"),
}


def self_test() -> None:
    """Check the synthetic controls, then compare the baseline with the prepared input."""
    for route in analyze(synthetic_prepared()):
        for record in route["records"]:
            key = (route["route_id"], record["pointer"])
            expected = SYNTHETIC_EXPECTED[key]
            actual = (
                record["baseline"]["classification"],
                record["restricted"]["classification"],
            )
            if actual != expected:
                raise AssertionError(f"{key}: expected {expected}, got {actual}")

    sample = analyze(synthetic_prepared())[0]["records"][5]
    if [c["pointer"] for c in sample["baseline"]["candidates"]] != [
        "/packages/4",
        "/packages/5",
    ]:
        raise AssertionError(
            "Unexpected baseline candidates for the SHA-1 and SHA-256 case"
        )
    if sample["restricted"]["excluded_algorithms"] != ["SHA-1"]:
        raise AssertionError(
            "Expected SHA-1 to be excluded under the restricted policy"
        )
    if sample["restricted"]["candidates"][0]["shared_algorithms"] != ["SHA-256"]:
        raise AssertionError(
            "Unexpected supporting anchor for the restricted candidate"
        )

    print("Reference synthetic checks passed.")

    _content, prepared = read_prepared()
    totals = total_counts(analyze(prepared))
    print(f"Prepared sources checked: {totals['sources']}")
    print(
        "Baseline status mismatches with prepared evaluator correspondences: "
        f"{totals['baseline_status_mismatches_with_prepared']}"
    )
    print(
        "Baseline candidate mismatches with prepared evaluator correspondences: "
        f"{totals['baseline_candidate_mismatches_with_prepared']}"
    )
    if (
        totals["baseline_status_mismatches_with_prepared"]
        or totals["baseline_candidate_mismatches_with_prepared"]
    ):
        raise AssertionError("Baseline arm disagrees with the prepared correspondences")


def run() -> None:
    """Write the reference classifications once."""
    if OUTPUT.exists():
        raise FileExistsError(f"Reference evidence already exists: {OUTPUT}")

    content, prepared = read_prepared()
    routes = analyze(prepared)
    report = {
        "schema_version": 1,
        "arm": "reference",
        "evidence_commit": EVIDENCE_COMMIT,
        "prepared_input": "comparison/prepared/freeze_02.json",
        "prepared_sha256": sha256(content),
        "script_sha256": sha256(Path(__file__).read_bytes()),
        "policies": {
            "baseline": "every algorithm spelling present in the prepared anchors",
            "restricted": list(RESTRICTED_ALGORITHMS),
        },
        "totals": total_counts(routes),
        "routes": routes,
    }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=OUTPUT.parent) as temporary:
        pending = Path(temporary) / "reference.json"
        with pending.open("w", encoding="utf-8", newline="\n") as stream:
            json.dump(report, stream, ensure_ascii=False, indent=2, allow_nan=False)
            stream.write("\n")
        # Same-volume hard link: publish atomically and refuse an existing file.
        OUTPUT.hardlink_to(pending)

    print(OUTPUT)


def main() -> None:
    """Entry point for the reference arm."""
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
