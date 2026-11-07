# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "se-interpretive-kernel @ git+https://github.com/structural-explainability/se-interpretive-kernel.git@e895ace0129e321eaf6912718c341ce3eb1644eb",
# ]
# ///

"""Run the Freeze 02 L4 missing-value comparison.

Before the comparison freeze, use synthetic records only:

    uv run --no-project comparison/run_l4.py --self-test

After the comparison freeze and the formal preparation step:

    uv run --no-project comparison/run_l4.py --run

Input:
    comparison/prepared/freeze_02.json

Output:
    comparison/results/l4/run.json

Frame IDs are scoped to one route. Each consists of the document side and
the JSON Pointer emitted by comparison/prepare.py.
"""

import argparse
from collections import Counter
import hashlib
from itertools import combinations
import json
from pathlib import Path
import tempfile
from typing import Any

from se_interpretive_kernel.generated import generated
from se_interpretive_kernel.loader import Absent, MissingPolicy, Observed, load_artifact
from se_interpretive_kernel.partition import Partition

HERE = Path(__file__).resolve().parent
INPUT = HERE / "prepared" / "freeze_02.json"
OUTPUT = HERE / "results" / "l4" / "run.json"

EVIDENCE_COMMIT = "e1befa159faff965b32a47975ac355bb6a9ccb18"
KERNEL_COMMIT = "e895ace0129e321eaf6912718c341ce3eb1644eb"
PROBE = "canonical_purl"
POLICIES = (MissingPolicy.DISTINCT, MissingPolicy.SHARED)

JsonObject = dict[str, Any]


def sha256(data: bytes) -> str:
    """Return the SHA-256 digest of the supplied bytes."""
    return hashlib.sha256(data).hexdigest()


def eligible_frames(
    route: JsonObject, side: str
) -> tuple[dict[str, str | None], dict[str, int]]:
    """Keep observed and missing probe cells. Count excluded occurrences."""
    frames: dict[str, str | None] = {}
    excluded: Counter[str] = Counter()
    seen: set[str] = set()

    for row in route[f"{side}_rows"]:
        if row["route_id"] != route["route_id"] or row["side"] != side:
            raise ValueError(f"Occurrence belongs to the wrong route or side: {row}")

        frame = f"{side}:{row['pointer']}"
        if frame in seen:
            raise ValueError(f"Duplicate occurrence in {route['route_id']}: {frame}")
        seen.add(frame)

        status = row["probe_status"]
        if status in ("malformed", "multiple"):
            excluded[status] += 1
            continue

        value = row[PROBE]
        if status == "missing" and value is None:
            frames[frame] = None
        elif status == "observed" and isinstance(value, str) and value:
            frames[frame] = value
        else:
            raise ValueError(f"Inconsistent prepared probe cell: {frame}, {status!r}")

    return frames, dict(sorted(excluded.items()))


def authorized_pairs(
    route: JsonObject,
    sources: dict[str, str | None],
    targets: dict[str, str | None],
) -> set[tuple[str, str]]:
    """Restrict the independently prepared authorizations to eligible endpoints."""
    pairs = set()
    for record in route["correspondences"]:
        if record["status"] == "authorized":
            source = f"source:{record['source_pointer']}"
            target = f"target:{record['authorized_target_pointer']}"
            if source in sources and target in targets:
                pairs.add((source, target))
    return pairs


def closure_report(artifact, regime: Partition) -> tuple[JsonObject, dict[str, int]]:
    """Record generated output blocks and their originating missing frames."""
    closure = generated(artifact, [PROBE], regime)
    missing_by_output: dict[Absent, list[str]] = {}
    for frame in artifact.frames:
        output = artifact.interpret(PROBE, frame)
        if isinstance(output, Absent):
            missing_by_output.setdefault(output, []).append(frame)

    labels = {}
    blocks = []
    for label, block in enumerate(closure.blocks()):
        observed = sorted(item.text for item in block if isinstance(item, Observed))
        missing_groups = [
            sorted(missing_by_output[item])
            for item in block
            if isinstance(item, Absent)
        ]
        for value in observed:
            labels[value] = label
        blocks.append(
            {
                "observed_purls": observed,
                # Each inner list denotes one missing output. SHARED may
                # associate several frame locations with that one output.
                "missing_output_frame_groups": sorted(missing_groups),
            }
        )

    return {"block_count": len(blocks), "blocks": blocks}, labels


def observed_closure_changes(
    distinct: dict[str, int],
    shared: dict[str, int],
) -> JsonObject:
    """Compare partitions on unordered pairs of distinct observed PURL values."""
    if distinct.keys() != shared.keys():
        raise ValueError("Policies produced different observed PURL carriers")

    gained = lost = 0
    witness = None
    for left, right in combinations(sorted(distinct), 2):
        before = distinct[left] == distinct[right]
        after = shared[left] == shared[right]
        if before != after:
            gained += int(after)
            lost += int(before)
            if witness is None:
                witness = {
                    "left_purl": left,
                    "right_purl": right,
                    "distinct_identifies": before,
                    "shared_identifies": after,
                }

    size = len(distinct)
    return {
        "observed_values": size,
        "observed_value_pairs": size * (size - 1) // 2,
        "identifications_gained_under_shared": gained,
        "identifications_lost_under_shared": lost,
        "first_changed_pair": witness,
    }


def compare_route(route: JsonObject) -> JsonObject:
    """Compare direct agreements and generated identifications under both policies."""
    route_id = route["route_id"]
    sources, source_exclusions = eligible_frames(route, "source")
    targets, target_exclusions = eligible_frames(route, "target")
    cells = sources | targets
    authorized = authorized_pairs(route, sources, targets)

    source_missing = sum(value is None for value in sources.values())
    target_missing = sum(value is None for value in targets.values())
    expected_changes = source_missing * target_missing
    observed_pairs = (len(sources) - source_missing) * (len(targets) - target_missing)

    result = {
        "route_id": route_id,
        "status": "completed",
        "source_document": route["source_rows"][0]["document_path"]
        if route["source_rows"]
        else None,
        "target_document": route["target_rows"][0]["document_path"]
        if route["target_rows"]
        else None,
        "eligible_sources": len(sources),
        "eligible_targets": len(targets),
        "source_exclusions": source_exclusions,
        "target_exclusions": target_exclusions,
        "missing_sources": source_missing,
        "missing_targets": target_missing,
        "eligible_source_target_pairs": len(sources) * len(targets),
        "eligible_authorized_pairs": len(authorized),
    }

    if not cells:
        result["analysis_status"] = "no_eligible_frames"
        result["two_missing_prediction"] = "unevaluable"
        result["observed_value_control"] = "unevaluable"
        return result

    rows = [{"frame": frame, PROBE: value} for frame, value in cells.items()]
    regime = Partition.from_pairs(tuple(cells), sorted(authorized))

    outputs = {}
    closures = {}
    labels = {}
    for policy in POLICIES:
        loaded = load_artifact(rows, "frame", [PROBE], policy=policy, label=route_id)
        if loaded.missing_counts[PROBE] != source_missing + target_missing:
            raise ValueError(
                f"Kernel missing count differs from prepared count: {route_id}"
            )

        name = policy.value
        outputs[name] = {
            frame: loaded.artifact.interpret(PROBE, frame) for frame in cells
        }
        closures[name], labels[name] = closure_report(loaded.artifact, regime)

    # Iterate the full source x target product without storing it.
    distinct = outputs["distinct"]
    shared = outputs["shared"]
    agreements = {"distinct": 0, "shared": 0}
    changed = authorized_changed = observed_changed = unexpected = 0
    first_change = first_authorized_change = first_unexpected = None

    for source, source_value in sources.items():
        for target, target_value in targets.items():
            before = distinct[source] == distinct[target]
            after = shared[source] == shared[target]
            agreements["distinct"] += int(before)
            agreements["shared"] += int(after)

            both_missing = source_value is None and target_value is None
            differs = before != after
            deviates = (before or not after) if both_missing else differs
            if not differs and not deviates:
                continue

            is_authorized = (source, target) in authorized
            witness = {
                "source_frame": source,
                "target_frame": target,
                "source_purl": source_value,
                "target_purl": target_value,
                "hash_authorized": is_authorized,
                "distinct_agrees": before,
                "shared_agrees": after,
            }
            if differs:
                changed += 1
                first_change = first_change or witness
                if is_authorized:
                    authorized_changed += 1
                    first_authorized_change = first_authorized_change or witness
                if source_value is not None and target_value is not None:
                    observed_changed += 1
            if deviates:
                unexpected += 1
                first_unexpected = first_unexpected or witness

    result.update(
        {
            "analysis_status": "evaluated",
            "direct_agreements": agreements,
            "expected_direct_changes": expected_changes,
            "actual_direct_changes": changed,
            "change_count_matches_product": changed == expected_changes,
            "changed_hash_authorized_pairs": authorized_changed,
            "first_changed_pair": first_change,
            "first_changed_hash_authorized_pair": first_authorized_change,
            "unexpected_direct_outcomes": unexpected,
            "first_unexpected_direct_outcome": first_unexpected,
            "observed_source_target_pairs": observed_pairs,
            "changed_observed_source_target_pairs": observed_changed,
            "generated_closures": closures,
            "observed_closure_comparison": observed_closure_changes(
                labels["distinct"], labels["shared"]
            ),
        }
    )

    # Report contrary evidence as an outcome. Preserve the comparison result.
    if unexpected:
        result["direct_policy_pattern"] = "contradicted"
    else:
        result["direct_policy_pattern"] = "as_expected"

    if expected_changes == 0:
        result["two_missing_prediction"] = "unevaluable"
    else:
        # The two-missing clause is distinct from the observed-value control.
        missing_distinct = {distinct[f] for f in sources if sources[f] is None}
        target_distinct = {distinct[f] for f in targets if targets[f] is None}
        missing_shared = {shared[f] for f in cells if cells[f] is None}
        met = missing_distinct.isdisjoint(target_distinct) and len(missing_shared) == 1
        result["two_missing_prediction"] = "met" if met else "contradicted"

    if observed_pairs == 0:
        result["observed_value_control"] = "unevaluable"
    else:
        result["observed_value_control"] = (
            "met" if observed_changed == 0 else "contradicted"
        )

    return result


def self_test() -> None:
    """Exercise both kernel policies and an actual change in generated closure."""

    def row(side: str, index: int, value: str | None) -> JsonObject:
        return {
            "route_id": "synthetic",
            "side": side,
            "document_path": f"{side}.json",
            "pointer": f"/components/{index}",
            "probe_status": "missing" if value is None else "observed",
            PROBE: value,
        }

    a = "pkg:npm/example-a@1"
    b = "pkg:npm/example-b@1"
    route = {
        "route_id": "synthetic",
        "source_rows": [row("source", i, v) for i, v in enumerate([None, None, a, b])],
        "target_rows": [
            row("target", i, v) for i, v in enumerate([None, None, None, a])
        ],
        "correspondences": [
            {
                "source_pointer": f"/components/{s}",
                "status": "authorized",
                "authorized_target_pointer": f"/components/{t}",
            }
            for s, t in [(0, 0), (2, 1), (3, 2)]
        ],
    }

    result = compare_route(route)
    expected = {
        "eligible_source_target_pairs": 16,
        "actual_direct_changes": 6,
        "changed_hash_authorized_pairs": 1,
        "observed_source_target_pairs": 2,
        "changed_observed_source_target_pairs": 0,
        "unexpected_direct_outcomes": 0,
        "two_missing_prediction": "met",
        "observed_value_control": "met",
    }
    for field, value in expected.items():
        if result[field] != value:
            raise AssertionError(f"{field}: expected {value!r}, got {result[field]!r}")

    if result["direct_agreements"] != {"distinct": 1, "shared": 7}:
        raise AssertionError("Unexpected direct agreement counts")
    if (
        result["observed_closure_comparison"]["identifications_gained_under_shared"]
        != 1
    ):
        raise AssertionError("Expected SHARED to link observed PURLs A and B")

    # Removing missing source cells makes the two-missing clause unevaluable.
    route["source_rows"] = route["source_rows"][2:]
    route["correspondences"] = route["correspondences"][1:]
    result = compare_route(route)
    if (
        result["two_missing_prediction"] != "unevaluable"
        or result["actual_direct_changes"]
    ):
        raise AssertionError("Zero two-missing pairs must be reported as unevaluable")

    print("L4 synthetic checks passed.")


def run() -> None:
    """Read the prepared Freeze 02 input and write the formal L4 comparison report."""
    if OUTPUT.exists():
        raise FileExistsError(f"L4 evidence already exists: {OUTPUT}")

    content = INPUT.read_bytes()
    prepared = json.loads(content)
    if (
        prepared["schema_version"] != 1
        or prepared["evidence_commit"] != EVIDENCE_COMMIT
    ):
        raise ValueError(f"Unexpected preparation schema or evidence commit in {INPUT}")

    routes = []
    seen = set()
    for route in prepared["routes"]:
        route_id = route["route_id"]
        if route_id in seen:
            raise ValueError(f"Duplicate prepared route: {route_id}")
        seen.add(route_id)

        if route["status"] == "completed":
            routes.append(compare_route(route))
        else:
            routes.append(
                {
                    "route_id": route_id,
                    "status": route["status"],
                    "analysis_status": "no_completed_conversion",
                }
            )

    report = {
        "schema_version": 1,
        "hypothesis": "L4",
        "probe": PROBE,
        "evidence_commit": EVIDENCE_COMMIT,
        "kernel_commit": KERNEL_COMMIT,
        "prepared_input": "comparison/prepared/freeze_02.json",
        "prepared_sha256": sha256(content),
        "runner_sha256": sha256(Path(__file__).read_bytes()),
        "freeze_02_sha256": prepared["freeze_02_sha256"],
        "frame_regime": "equivalence closure of eligible hash-authorized pairs within route",
        "routes": routes,
    }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=OUTPUT.parent) as temp:
        pending = Path(temp) / "run.json"
        with pending.open("w", encoding="utf-8", newline="\n") as stream:
            json.dump(report, stream, ensure_ascii=False, indent=2, allow_nan=False)
            stream.write("\n")
        OUTPUT.hardlink_to(pending)

    print(OUTPUT)


def main() -> None:
    """Entry point for the L4 comparison runner."""
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
