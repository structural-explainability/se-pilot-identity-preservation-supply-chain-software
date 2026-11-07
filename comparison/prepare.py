"""Prepare component occurrences and hash correspondences for the comparison.

From the repository root, before the comparison freeze:

    uv run --frozen python comparison/prepare.py --self-test

The self-test runs synthetic checks, then prepares the committed evidence
in memory.
It verifies the evidence commit and document digests, prints
correspondence status counts, and prints probe-status counts by route.
It writes nothing.

After the separate comparison freeze:

    uv run --frozen python comparison/prepare.py --prepare

Formal output:

    comparison/prepared/freeze_02.json

The output contains route metadata, occurrence rows, and source-to-target
correspondences. Evaluation verdicts are reserved for later scoring.
"""

import argparse
from collections.abc import Iterator
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import tomllib
from typing import Any

from preservation_test.evaluator import evaluate, formats, purl_canonical

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_COMMIT = "e1befa159faff965b32a47975ac355bb6a9ccb18"
PLAN_PATH = "generalization/05-transformations.toml"
RUN_PATH = "generalization/results/run.json"
OUTPUT_PATH = ROOT / "comparison" / "prepared" / "freeze_02.json"

JsonObject = dict[str, Any]


def git_bytes(path: str) -> bytes:
    """Read the exact bytes of a file in the committed evidence snapshot."""
    return subprocess.check_output(
        ["git", "show", f"{EVIDENCE_COMMIT}:{path}"],
        cwd=ROOT,
    )


def digest(content: bytes) -> str:
    """Compute the SHA-256 digest of the given content."""
    return hashlib.sha256(content).hexdigest()


def check_imported_pilot_code() -> None:
    """Ensure the pilot modules actually imported match the evidence commit."""
    for module in (formats, evaluate, purl_canonical):
        path = Path(module.__file__).resolve()
        relative_path = path.relative_to(ROOT).as_posix()
        if path.read_bytes() != git_bytes(relative_path):
            raise ValueError(
                f"Imported pilot code differs from commit: {relative_path}"
            )


def read_document(path: str, expected_sha256: str) -> JsonObject:
    """Read a JSON document from the committed evidence snapshot and verify its SHA-256 digest."""
    content = git_bytes(path)
    if digest(content) != expected_sha256:
        raise ValueError(f"Document SHA-256 mismatch: {path}")
    return json.loads(content)


def object_items(value: object) -> Iterator[tuple[int, JsonObject]]:
    """Retain original array indices, including when non-objects are skipped."""
    if isinstance(value, list):
        for index, item in enumerate(value):
            if isinstance(item, dict):
                yield index, item


def cdx_locations(
    items: object,
    parent: str = "/components",
) -> Iterator[tuple[str, JsonObject]]:
    """Visit exactly the component tree exposed by the frozen CDX adapter."""
    for index, item in object_items(items):
        pointer = f"{parent}/{index}"
        yield pointer, item
        yield from cdx_locations(item.get("components"), f"{pointer}/components")


def locations(
    document: JsonObject,
    format_name: str,
) -> Iterator[tuple[str, JsonObject]]:
    """Yield locations of components or packages within the document based on the format."""
    if format_name == "cyclonedx":
        yield from cdx_locations(document.get("components"))
    elif format_name == "spdx-2.3":
        for index, item in object_items(document.get("packages")):
            yield f"/packages/{index}", item
    else:
        raise ValueError(f"Format outside this Freeze 02 comparison: {format_name}")


def canonical_slots(item: JsonObject, format_name: str) -> list[Any]:
    """Capture original canonical-slot values before the adapter filters them."""
    if format_name == "cyclonedx":
        return [item["purl"]] if "purl" in item else []

    values = []
    for _, reference in object_items(item.get("externalRefs")):
        if (
            reference.get("referenceCategory") == "PACKAGE-MANAGER"
            and reference.get("referenceType") == "purl"
        ):
            # A declared PURL reference with no locator is malformed.
            values.append(reference.get("referenceLocator"))
    return values


def extract(
    route_id: str,
    side: str,
    path: str,
    document: JsonObject,
) -> tuple[list[formats.Component], list[JsonObject]]:
    """Extract components and their canonical slot information from the document."""
    format_name, components = formats.load(document)
    rows = []

    for component, (pointer, item) in zip(
        components, locations(document, format_name), strict=True
    ):
        raw = canonical_slots(item, format_name)
        parsed = [purl_canonical.canonical(value) for value in raw]
        canonical_values = sorted({value for value in parsed if value is not None})
        malformed = any(value is None for value in parsed)
        multiple = len(canonical_values) > 1

        if set(canonical_values) != component.canonical_purls:
            raise ValueError(f"Adapter and location disagree: {path}#{pointer}")

        if malformed:
            status = "malformed"
        elif multiple:
            status = "multiple"
        elif canonical_values:
            status = "observed"
        else:
            status = "missing"

        rows.append(
            {
                "route_id": route_id,
                "side": side,
                "document_path": path,
                "pointer": pointer,
                "ref": component.ref,
                "anchors": sorted(component.anchors),
                "raw_purls": raw,
                "normalized_purls": canonical_values,
                "has_malformed_value": malformed,
                "has_multiple_canonical_values": multiple,
                "probe_status": status,
                "canonical_purl": canonical_values[0] if status == "observed" else None,
            }
        )

    return components, rows


def prepare_route(
    route_id: str,
    source_path: str,
    source_document: JsonObject,
    target_path: str,
    target_document: JsonObject,
) -> JsonObject:
    """Prepare a route by extracting source and target components, indexing targets, and determining correspondences."""
    sources, source_rows = extract(route_id, "source", source_path, source_document)
    targets, target_rows = extract(route_id, "target", target_path, target_document)

    # Index all target occurrences, including malformed and multiple-PURL rows.
    # Filtering here could turn an ambiguous hash match into a unique one.
    index = evaluate._anchor_index(targets)
    pointer_by_object = {
        id(component): row["pointer"]
        for component, row in zip(targets, target_rows, strict=True)
    }

    correspondences = []
    for source, row in zip(sources, source_rows, strict=True):
        matches = evaluate._anchored_targets(source, index)
        pointers = sorted(pointer_by_object[id(target)] for target in matches)

        if not source.anchors:
            status = "no_source_anchor"
        elif not pointers:
            status = "no_matching_target"
        elif len(pointers) > 1:
            status = "ambiguous"
        else:
            status = "authorized"

        correspondences.append(
            {
                "source_pointer": row["pointer"],
                "status": status,
                "candidate_target_pointers": pointers,
                "authorized_target_pointer": pointers[0]
                if status == "authorized"
                else None,
            }
        )

    return {
        "source_rows": source_rows,
        "target_rows": target_rows,
        "correspondences": correspondences,
    }


def build_preparation() -> JsonObject:
    """Build the preparation data structure by validating the plan and run, and collecting route information."""
    check_imported_pilot_code()
    plan_bytes = git_bytes(PLAN_PATH)
    run_bytes = git_bytes(RUN_PATH)
    plan = tomllib.loads(plan_bytes.decode("utf-8"))
    run = json.loads(run_bytes)

    if run["mode"] != "formal" or run["status"] != "finished":
        raise ValueError(f"Expected a finished formal run in {RUN_PATH}")
    if digest(plan_bytes) != run["plan_sha256"]:
        raise ValueError(f"Plan SHA-256 differs from {RUN_PATH}")

    plan_ids = [route["route_id"] for route in plan["route"]]
    run_ids = [route["route_id"] for route in run["routes"]]
    if len(set(plan_ids)) != len(plan_ids) or sorted(plan_ids) != sorted(run_ids):
        raise ValueError("Plan and run route inventories disagree")

    planned = {route["route_id"]: route for route in plan["route"]}
    routes = []

    for entry in run["routes"]:
        route_id = entry["route_id"]
        spec = planned[route_id]
        if spec["status"] == "unsupported_pre_execution":
            if entry.get("outcome") != "unsupported_pre_execution":
                raise ValueError(f"Unsupported route status mismatch: {route_id}")
            routes.append({"route_id": route_id, "status": spec["status"]})
            continue

        execution_path = entry["execution_path"]
        if execution_path != spec["execution_path"]:
            raise ValueError(f"Execution path mismatch: {route_id}")
        execution = json.loads(git_bytes(execution_path))
        outcome = execution["execution_outcome"]
        if execution["route_id"] != route_id or outcome != entry["execution_outcome"]:
            raise ValueError(f"Execution record mismatch: {execution_path}")

        route = {
            "route_id": route_id,
            "status": outcome,
            "execution_path": execution_path,
            "validation_outcome": execution["validation_outcome"],
            "evaluation_outcome": execution["evaluation_outcome"],
        }
        if outcome == "completed":
            source_path = spec["source_path"]
            target_path = execution["evidence_paths"]["target_path"]
            if target_path != spec["target_path"]:
                raise ValueError(f"Target path mismatch: {route_id}")
            if execution["source_sha256"] != spec["source_sha256"]:
                raise ValueError(f"Source digest mismatch: {route_id}")

            source = read_document(source_path, spec["source_sha256"])
            target = read_document(target_path, execution["target_sha256"])
            route.update(
                prepare_route(route_id, source_path, source, target_path, target)
            )

        routes.append(route)

    return {
        "schema_version": 1,
        "evidence_commit": EVIDENCE_COMMIT,
        "plan_sha256": digest(plan_bytes),
        "run_sha256": digest(run_bytes),
        "freeze_02_sha256": run["freeze_02_sha256"],
        "routes": routes,
    }


def write_preparation() -> None:
    """Publish a complete JSON file once, after preparation succeeds."""
    if OUTPUT_PATH.exists():
        raise FileExistsError(f"Prepared evidence already exists: {OUTPUT_PATH}")

    preparation = build_preparation()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=OUTPUT_PATH.parent) as temporary:
        pending = Path(temporary) / "freeze_02.json"
        with pending.open("w", encoding="utf-8", newline="\n") as stream:
            json.dump(
                preparation, stream, ensure_ascii=False, indent=2, allow_nan=False
            )
            stream.write("\n")
        # Same-volume hard link: publish atomically and refuse an existing file.
        OUTPUT_PATH.hardlink_to(pending)

    print(OUTPUT_PATH)


def self_test() -> None:
    """Exercise occurrence identity, missingness, and pre-filter matching."""

    def item(name: str, anchor: str, **fields: Any) -> JsonObject:
        return {
            "name": name,
            "hashes": [{"alg": "SHA-256", "content": anchor * 64}],
            **fields,
        }

    observed = "pkg:npm/example@1.0.0"
    source = {
        "bomFormat": "CycloneDX",
        "components": [
            item("first", "a"),
            item(
                "nested-parent", "b", components=[item("control", "c", purl=observed)]
            ),
        ],
    }
    target = {
        "bomFormat": "CycloneDX",
        "metadata": {"component": item("outside-scope", "a")},
        "components": [
            item("duplicate-ref", "a"),
            item("duplicate-ref", "b"),
            item("third", "d"),
            item("control", "c", purl=observed),
            item("malformed", "b", purl="broken"),
        ],
    }

    result = prepare_route("synthetic", "source.json", source, "target.json", target)
    source_rows = result["source_rows"]
    target_rows = result["target_rows"]
    missing_sources = [
        r["pointer"] for r in source_rows if r["probe_status"] == "missing"
    ]
    missing_targets = [
        r["pointer"] for r in target_rows if r["probe_status"] == "missing"
    ]
    matches = {r["source_pointer"]: r for r in result["correspondences"]}

    assert len(missing_sources) * len(missing_targets) == 6
    assert (
        sum(
            matches[p]["authorized_target_pointer"] in missing_targets
            for p in missing_sources
        )
        == 1
    )
    assert matches["/components/1"]["candidate_target_pointers"] == [
        "/components/1",
        "/components/4",
    ]
    assert matches["/components/1"]["status"] == "ambiguous"
    assert (
        matches["/components/1/components/0"]["authorized_target_pointer"]
        == "/components/3"
    )
    assert target_rows[4]["probe_status"] == "malformed"

    package = {
        "SPDXID": "SPDXRef-example",
        "externalRefs": [
            {
                "referenceCategory": "PACKAGE-MANAGER",
                "referenceType": "purl",
                "referenceLocator": value,
            }
            for value in (observed, "pkg:npm/another@2.0.0")
        ],
    }
    _, rows = extract(
        "synthetic",
        "source",
        "source.spdx.json",
        {"spdxVersion": "SPDX-2.3", "packages": [package]},
    )
    assert rows[0]["pointer"] == "/packages/0"
    assert rows[0]["probe_status"] == "multiple"
    print("Synthetic preparation checks passed.")

    preparation = build_preparation()
    statuses = {}
    source_total = 0

    for route in preparation["routes"]:
        for correspondence in route.get("correspondences", []):
            status = correspondence["status"]
            statuses[status] = statuses.get(status, 0) + 1
            source_total += 1

    print(f"Evidence commit {preparation['evidence_commit']} prepared in memory.")
    print(f"Source rows: {source_total}")

    for status in sorted(statuses):
        print(f"  {status}: {statuses[status]}")

    print()
    print("Probe status by route:")

    for route in preparation["routes"]:
        if "source_rows" not in route:
            continue

        source_status = {}
        for row in route["source_rows"]:
            source_status[row["probe_status"]] = (
                source_status.get(row["probe_status"], 0) + 1
            )

        target_status = {}
        for row in route["target_rows"]:
            target_status[row["probe_status"]] = (
                target_status.get(row["probe_status"], 0) + 1
            )

        source_missing_count = source_status.get("missing", 0)
        target_missing_count = target_status.get("missing", 0)
        print(f"  {route['route_id']}")
        print(f"    source: {dict(sorted(source_status.items()))}")
        print(f"    target: {dict(sorted(target_status.items()))}")
        print(
            "    missing source x missing target = "
            f"{source_missing_count * target_missing_count}"
        )


def main() -> None:
    """Parse command-line arguments and execute the appropriate mode."""
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--prepare", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        self_test()
    else:
        write_preparation()


if __name__ == "__main__":
    main()
