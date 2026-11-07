# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "se-identity-ops @ git+https://github.com/structural-explainability/se-identity-ops.git@7060cd084801e72f2c31175afef035d057979e8a",
# ]
# ///

"""freeze_04_identityops.py - Run the IdentityOps arm of the Freeze 04 anchor-policy comparison.

Before the Freeze 04 freeze:

    uv run --no-project comparison/freeze_04_identityops.py --self-test
    uv run --no-project comparison/freeze_04_identityops.py --print-table-digest

After the Freeze 04 freeze:

    uv run --no-project comparison/freeze_04_identityops.py --run

Input:
    comparison/prepared/freeze_02.json
    comparison/freeze_04_baseline.ido
    comparison/freeze_04_restricted.ido

Output:
    comparison/results/freeze_04/anchors.csv
    comparison/results/freeze_04/identityops.json

The adapter writes one table with one row per occurrence and one column per
anchor algorithm spelling. Each value carries its route identifier, so a
regime relates occurrences only within one route.

Each IdentityOps program declares one regime per admitted algorithm spelling.
IdentityOps computes the within-algorithm relations and the coverage checks.
This script then performs the work the language does not express:

    - combine the target candidates across the declared regimes,
    - count candidates per source occurrence,
    - apply the exactly-one authorization rule, and
    - write the per-occurrence classifications and anchor traces.

The pinned IdentityOps version has no construct for those four steps.
"""

import argparse
import csv
import hashlib
import json
from pathlib import Path
import re
import tempfile
from typing import Any

from se_identity_ops import parse, run_program
from se_identity_ops.interpreter import Run

ROOT = Path(__file__).resolve().parents[1]
COMPARISON = ROOT / "comparison"
INPUT = COMPARISON / "prepared" / "freeze_02.json"
OUTPUT_DIRECTORY = COMPARISON / "results" / "freeze_04"
TABLE_OUTPUT = OUTPUT_DIRECTORY / "anchors.csv"
REPORT_OUTPUT = OUTPUT_DIRECTORY / "identityops.json"

EVIDENCE_COMMIT = "e1befa159faff965b32a47975ac355bb6a9ccb18"
IDENTITYOPS_COMMIT = "7060cd084801e72f2c31175afef035d057979e8a"
PREPARED_SHA256 = "17eaa9518e1754a860319532d8e66a317978d3a41fb711a8e47318c23f7699f7"

PROGRAMS = {
    "baseline": COMPARISON / "freeze_04_baseline.ido",
    "restricted": COMPARISON / "freeze_04_restricted.ido",
}

# Regime name, anchor algorithm spelling, in the order the programs declare them.
REGIMES = (
    ("md5", "MD5"),
    ("sha1", "SHA-1"),
    ("sha256", "SHA-256"),
    ("sha384_hyphen", "SHA-384"),
    ("sha384_plain", "SHA384"),
    ("sha512", "SHA-512"),
    ("sha3_256", "SHA3-256"),
    ("sha3_384", "SHA3-384"),
    ("sha3_512", "SHA3-512"),
)
POLICY_REGIMES = {
    "baseline": (
        "md5",
        "sha1",
        "sha256",
        "sha384_hyphen",
        "sha384_plain",
        "sha512",
        "sha3_256",
        "sha3_384",
        "sha3_512",
    ),
    "restricted": ("sha256", "sha384_hyphen", "sha512"),
}

JsonObject = dict[str, Any]


def sha256(content: bytes) -> str:
    """Return the SHA-256 digest of the given bytes."""
    return hashlib.sha256(content).hexdigest()


def read_prepared() -> tuple[bytes, JsonObject]:
    """Read the prepared input and verify its pins."""
    content = INPUT.read_bytes()
    if sha256(content) != PREPARED_SHA256:
        raise ValueError(f"Prepared input digest differs from the pin: {INPUT}")
    prepared = json.loads(content)
    if prepared["evidence_commit"] != EVIDENCE_COMMIT:
        raise ValueError(f"Unexpected evidence commit in {INPUT}")
    return content, prepared


def build_table(prepared: JsonObject) -> list[JsonObject]:
    """Build one occurrence per row for every completed route.

    Each row has frame, route_id, side, pointer, and one value per algorithm
    spelling. A value is the route identifier, a vertical bar, and the anchor
    value. It is empty when the occurrence has no anchor of that spelling.
    """
    spellings = [spelling for _name, spelling in REGIMES]
    rows: list[JsonObject] = []
    for route in prepared["routes"]:
        if route["status"] != "completed":
            continue
        for side, key in (("source", "source_rows"), ("target", "target_rows")):
            for occurrence in route[key]:
                values = {spelling: "" for spelling in spellings}
                for algorithm, value in occurrence["anchors"]:
                    if algorithm not in values:
                        raise ValueError(f"Unlisted anchor algorithm: {algorithm}")
                    values[algorithm] = f"{route['route_id']}|{value}"
                rows.append(
                    {
                        "frame": f"f{len(rows) + 1:06d}",
                        "route_id": route["route_id"],
                        "side": side,
                        "pointer": occurrence["pointer"],
                        "values": values,
                    }
                )
    return rows


def table_bytes(rows: list[JsonObject]) -> bytes:
    """Serialize the table as UTF-8 CSV with newline row endings."""
    header = ["frame", "route_id", "side", "pointer"] + [
        f"anchor_{spelling}" for _name, spelling in REGIMES
    ]
    with tempfile.TemporaryFile("w+", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream, lineterminator="\n")
        writer.writerow(header)
        for row in rows:
            writer.writerow(
                [row["frame"], row["route_id"], row["side"], row["pointer"]]
                + [row["values"][spelling] for _name, spelling in REGIMES]
            )
        stream.seek(0)
        return stream.read().encode("utf-8")


def program_pin(program_text: str) -> str:
    """Read the table digest a program declares."""
    found = re.findall(r'^\s+sha256 "([0-9a-f]{64})"', program_text, flags=re.MULTILINE)
    if len(found) != 1:
        raise ValueError("Expected exactly one source digest in the program")
    return found[0]


def retarget_program(program_text: str, file_name: str, digest: str) -> str:
    """Point a program at another table file and digest, keeping its declarations."""
    text, file_count = re.subn(
        r'^(\s+file )"[^"]*"', rf'\1"{file_name}"', program_text, flags=re.MULTILINE
    )
    text, digest_count = re.subn(
        r'^(\s+sha256 )"[0-9a-f]{64}"', rf'\1"{digest}"', text, flags=re.MULTILINE
    )
    if file_count != 1 or digest_count != 1:
        raise ValueError("Expected exactly one source file and digest in the program")
    return text


def classify(
    policy: str, run: Run, rows: list[JsonObject]
) -> dict[tuple[str, str], JsonObject]:
    """Classify every source occurrence from the relations IdentityOps computed."""
    spelling_of = dict(REGIMES)
    declared = POLICY_REGIMES[policy]
    by_frame = {row["frame"]: row for row in rows}

    members: dict[str, dict[str, tuple[str, ...]]] = {}
    for regime in declared:
        in_class: dict[str, tuple[str, ...]] = {}
        for group in run.same_classes(regime):
            ordered = tuple(sorted(group))
            for frame in group:
                in_class[frame] = ordered
        members[regime] = in_class

    results: dict[tuple[str, str], JsonObject] = {}
    for row in rows:
        if row["side"] != "source":
            continue

        admitted = []
        shared: dict[str, list[str]] = {}
        for regime in declared:
            spelling = spelling_of[regime]
            if not row["values"][spelling]:
                continue
            admitted.append(spelling)
            for frame in members[regime][row["frame"]]:
                other = by_frame[frame]
                if other["side"] != "target":
                    continue
                algorithms = shared.setdefault(frame, [])
                if spelling not in algorithms:
                    algorithms.append(spelling)

        excluded = [
            spelling
            for regime, spelling in REGIMES
            if regime not in declared and row["values"][spelling]
        ]
        candidates = [
            {
                "pointer": by_frame[frame]["pointer"],
                "shared_algorithms": sorted(shared[frame]),
            }
            for frame in sorted(shared)
        ]

        if not admitted:
            classification = "no_source_anchor"
        elif not candidates:
            classification = "no_matching_target"
        elif len(candidates) == 1:
            classification = "authorized"
        else:
            classification = "ambiguous"

        results[(row["route_id"], row["pointer"])] = {
            "admitted_algorithms": sorted(admitted),
            "excluded_algorithms": sorted(excluded),
            "candidates": candidates,
            "classification": classification,
        }
    return results


def execute(
    policy: str, program_path: Path, base_directory: Path, rows: list[JsonObject]
) -> tuple[dict[tuple[str, str], JsonObject], list[Any]]:
    """Run one IdentityOps program and classify from its relations."""
    program = parse(program_path.read_text(encoding="utf-8"), program_path.name)
    run = run_program(program, base_directory)
    results = run.to_dict()["results"]
    if not isinstance(results, list):
        raise TypeError("Expected the IdentityOps results to be a list")
    return classify(policy, run, rows), results


def route_records(
    prepared: JsonObject,
    classified: dict[str, dict[tuple[str, str], JsonObject]],
) -> list[JsonObject]:
    """Assemble per-route records in the same shape as the reference arm."""
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

        records = []
        counts: dict[str, dict[str, int]] = {"baseline": {}, "restricted": {}}
        for source in route["source_rows"]:
            key = (route["route_id"], source["pointer"])
            record: JsonObject = {"pointer": source["pointer"]}
            for policy in ("baseline", "restricted"):
                record[policy] = classified[policy][key]
                label = record[policy]["classification"]
                counts[policy][label] = counts[policy].get(label, 0) + 1
            records.append(record)
        routes.append(
            {
                "route_id": route["route_id"],
                "status": route["status"],
                "analysis_status": "evaluated",
                "counts": {
                    policy: dict(sorted(counts[policy].items()))
                    for policy in ("baseline", "restricted")
                },
                "records": records,
            }
        )
    return routes


def synthetic_prepared() -> JsonObject:
    """Build a small prepared-style input with one case per required control."""

    def source(number: int, anchors: list[list[str]]) -> JsonObject:
        return {"pointer": f"/components/{number}", "anchors": anchors}

    def target(number: int, anchors: list[list[str]]) -> JsonObject:
        return {"pointer": f"/packages/{number}", "anchors": anchors}

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
    }
    route_b = {
        "route_id": "route-b",
        "status": "completed",
        "source_rows": [source(0, [["SHA-256", "a1"]])],
        "target_rows": [],
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


def run_both_policies(
    rows: list[JsonObject], directory: Path
) -> tuple[dict[str, dict[tuple[str, str], JsonObject]], dict[str, list[Any]]]:
    """Write the table, retarget both programs, and run them from one directory."""
    content = table_bytes(rows)
    (directory / "anchors.csv").write_bytes(content)
    digest = sha256(content)

    classified: dict[str, dict[tuple[str, str], JsonObject]] = {}
    operation_results: dict[str, list[Any]] = {}
    for policy, program_path in PROGRAMS.items():
        text = retarget_program(
            program_path.read_text(encoding="utf-8"), "anchors.csv", digest
        )
        retargeted = directory / program_path.name
        retargeted.write_text(text, encoding="utf-8", newline="\n")
        classified[policy], operation_results[policy] = execute(
            policy, retargeted, directory, rows
        )
    return classified, operation_results


def self_test() -> None:
    """Check the synthetic controls and that the programs pin the real table."""
    rows = build_table(synthetic_prepared())
    with tempfile.TemporaryDirectory() as temporary:
        classified, _results = run_both_policies(rows, Path(temporary))
    for key, expected in SYNTHETIC_EXPECTED.items():
        actual = (
            classified["baseline"][key]["classification"],
            classified["restricted"][key]["classification"],
        )
        if actual != expected:
            raise AssertionError(f"{key}: expected {expected}, got {actual}")

    sample = classified["restricted"][("route-a", "/components/5")]
    if sample["excluded_algorithms"] != ["SHA-1"]:
        raise AssertionError(
            "Expected SHA-1 to be excluded under the restricted policy"
        )
    if sample["candidates"] != [
        {"pointer": "/packages/4", "shared_algorithms": ["SHA-256"]}
    ]:
        raise AssertionError(
            "Unexpected restricted candidate for the SHA-1 and SHA-256 case"
        )

    print("IdentityOps synthetic checks passed.")

    _content, prepared = read_prepared()
    digest = sha256(table_bytes(build_table(prepared)))
    for policy, program_path in PROGRAMS.items():
        pinned = program_pin(program_path.read_text(encoding="utf-8"))
        if pinned != digest:
            raise AssertionError(
                f"{program_path.name} pins {pinned}, but the prepared table is {digest}"
            )
    print(f"Both programs pin the prepared table digest {digest}.")

    for policy, program_path in PROGRAMS.items():
        declared = re.findall(
            r"^regime (\w+) on ",
            program_path.read_text(encoding="utf-8"),
            flags=re.MULTILINE,
        )
        if tuple(declared) != POLICY_REGIMES[policy]:
            raise AssertionError(
                f"{program_path.name} declares {declared}, "
                f"but the script combines {list(POLICY_REGIMES[policy])}"
            )
    print("Each program declares the regimes the script combines.")


def run() -> None:
    """Write the table and the IdentityOps classifications once."""
    for existing in (TABLE_OUTPUT, REPORT_OUTPUT):
        if existing.exists():
            raise FileExistsError(f"IdentityOps evidence already exists: {existing}")

    content, prepared = read_prepared()
    rows = build_table(prepared)

    OUTPUT_DIRECTORY.mkdir(parents=True, exist_ok=True)
    table = table_bytes(rows)
    for program_path in PROGRAMS.values():
        if program_pin(program_path.read_text(encoding="utf-8")) != sha256(table):
            raise ValueError(f"{program_path.name} does not pin the prepared table")

    TABLE_OUTPUT.write_bytes(table)
    classified: dict[str, dict[tuple[str, str], JsonObject]] = {}
    operation_results: dict[str, list[Any]] = {}
    for policy, program_path in PROGRAMS.items():
        classified[policy], operation_results[policy] = execute(
            policy, program_path, COMPARISON, rows
        )

    report = {
        "schema_version": 1,
        "arm": "identityops",
        "evidence_commit": EVIDENCE_COMMIT,
        "identityops_commit": IDENTITYOPS_COMMIT,
        "prepared_input": "comparison/prepared/freeze_02.json",
        "prepared_sha256": sha256(content),
        "script_sha256": sha256(Path(__file__).read_bytes()),
        "table": {
            "path": "comparison/results/freeze_04/anchors.csv",
            "sha256": sha256(table),
            "rows": len(rows),
        },
        "programs": {
            policy: {
                "path": f"comparison/{path.name}",
                "sha256": sha256(path.read_bytes()),
                "regimes": list(POLICY_REGIMES[policy]),
            }
            for policy, path in PROGRAMS.items()
        },
        "identityops_results": operation_results,
        "routes": route_records(prepared, classified),
    }

    with tempfile.TemporaryDirectory(dir=OUTPUT_DIRECTORY) as temporary:
        pending = Path(temporary) / "identityops.json"
        with pending.open("w", encoding="utf-8", newline="\n") as stream:
            json.dump(report, stream, ensure_ascii=False, indent=2, allow_nan=False)
            stream.write("\n")
        # Same-volume hard link: publish atomically and refuse an existing file.
        REPORT_OUTPUT.hardlink_to(pending)

    print(REPORT_OUTPUT)


def main() -> None:
    """Entry point for the IdentityOps arm."""
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--self-test", action="store_true")
    mode.add_argument("--print-table-digest", action="store_true")
    mode.add_argument("--run", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        self_test()
    elif args.print_table_digest:
        _content, prepared = read_prepared()
        print(sha256(table_bytes(build_table(prepared))))
    else:
        run()


if __name__ == "__main__":
    main()
