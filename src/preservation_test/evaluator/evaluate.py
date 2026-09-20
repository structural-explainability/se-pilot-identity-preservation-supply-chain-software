"""Generic representation-preservation evaluator.

The evaluator reads a typed commitment, anchors source and target components,
and classifies preservation outcomes.

It contains no SPDX- or CycloneDX-specific field knowledge and no special
cases for particular bugs, tools, packages, or artifacts.
"""

import argparse
from collections import Counter
import json
from pathlib import Path
import tomllib
from typing import Any

from preservation_test.evaluator import formats
from preservation_test.evaluator.purl_canonical import coordinates


def _anchor_index(
    components: list[formats.Component],
) -> dict[tuple[str, str], list[formats.Component]]:
    """Index target components by normalized content-hash anchor."""
    index: dict[tuple[str, str], list[formats.Component]] = {}

    for component in components:
        for anchor in component.anchors:
            index.setdefault(anchor, []).append(component)

    return index


def _anchored_targets(
    component: formats.Component,
    target_index: dict[tuple[str, str], list[formats.Component]],
) -> list[formats.Component]:
    """Return distinct target components reached through source anchors."""
    matches: dict[int, formats.Component] = {}

    for anchor in component.anchors:
        for target in target_index.get(anchor, []):
            matches[id(target)] = target

    return list(matches.values())


def _result(
    ref: str,
    verdict: str,
    purl: str | None,
    detail: str = "",
) -> dict[str, str | None]:
    """Build one evaluator result."""
    return {
        "ref": ref,
        "verdict": verdict,
        "purl": purl,
        "detail": detail,
    }


def evaluate(
    source_doc: dict[str, Any],
    target_doc: dict[str, Any],
    commitment: dict[str, Any],
) -> dict[str, Any]:
    """Evaluate one representation-preservation commitment."""
    source_format, source_components = formats.load(source_doc)
    target_format, target_components = formats.load(target_doc)

    if commitment.get("kind") != "representation_preservation":
        raise ValueError(
            "evaluate() supports only representation_preservation commitments"
        )

    representable_formats = set(commitment["representable_in"])
    target_supports_identifier = target_format in representable_formats

    target_index = _anchor_index(target_components)
    results: list[dict[str, str | None]] = []

    for source_component in source_components:
        source_purls = source_component.canonical_purls

        if not source_purls:
            results.append(
                _result(
                    source_component.ref,
                    "NOT_APPLICABLE",
                    None,
                    "source component has no canonical purl",
                )
            )
            continue

        if not target_supports_identifier:
            for purl in sorted(source_purls):
                results.append(
                    _result(
                        source_component.ref,
                        "UNSUPPORTED",
                        purl,
                        f"target format {target_format} does not support "
                        "the required purl representation",
                    )
                )
            continue

        if len(source_purls) > 1:
            for purl in sorted(source_purls):
                results.append(
                    _result(
                        source_component.ref,
                        "UNDERDETERMINED",
                        purl,
                        "multiple canonical source purls require a "
                        "source-grounded selection rule",
                    )
                )
            continue

        if not source_component.anchors:
            for purl in sorted(source_purls):
                results.append(
                    _result(
                        source_component.ref,
                        "UNANCHORABLE",
                        purl,
                        "source component has no usable content-hash anchor",
                    )
                )
            continue

        target_matches = _anchored_targets(source_component, target_index)

        if not target_matches:
            for purl in sorted(source_purls):
                results.append(
                    _result(
                        source_component.ref,
                        "UNANCHORABLE",
                        purl,
                        "no target component shares a declared content-hash anchor",
                    )
                )
            continue

        if len(target_matches) > 1:
            for purl in sorted(source_purls):
                results.append(
                    _result(
                        source_component.ref,
                        "UNANCHORABLE",
                        purl,
                        "content-hash anchors resolve to multiple target components",
                    )
                )
            continue

        target_component = target_matches[0]
        target_canonical = target_component.canonical_purls
        target_other = target_component.other_purls

        target_coordinates = {
            value
            for purl in target_canonical
            if (value := coordinates(purl)) is not None
        }

        for purl in sorted(source_purls):
            if purl in target_canonical:
                verdict = "PRESERVED"
                detail = ""

            elif purl in target_other:
                verdict = "VIOLATED_RELOCATED"
                detail = "purl is present in the target but not in its canonical slot"

            elif coordinates(purl) in target_coordinates:
                verdict = "VIOLATED_ALTERED"
                detail = (
                    "target canonical purl has the same reduced coordinates "
                    "but differs from the source canonical purl"
                )

            else:
                verdict = "VIOLATED_DROPPED"
                detail = "purl is absent from the anchored target component"

            results.append(
                _result(
                    source_component.ref,
                    verdict,
                    purl,
                    detail,
                )
            )

    return {
        "source_format": source_format,
        "target_format": target_format,
        "commitment": commitment["id"],
        "results": results,
    }


def summarize(
    report: dict[str, Any],
) -> tuple[Counter[str], list[dict[str, str | None]]]:
    """Summarize verdict counts and preservation violations."""
    counts = Counter(str(result["verdict"]) for result in report["results"])

    findings = [
        result
        for result in report["results"]
        if str(result["verdict"]).startswith("VIOLATED_")
    ]

    return counts, findings


def load_commitment(path: Path, commitment_id: str) -> dict[str, Any]:
    """Load one commitment by identifier."""
    with path.open("rb") as file:
        data = tomllib.load(file)

    for commitment in data.get("commitment", []):
        if commitment["id"] == commitment_id:
            return commitment

    raise KeyError(commitment_id)


def main() -> None:
    """Run the representation-preservation evaluator."""
    parser = argparse.ArgumentParser(
        description="representation_preservation evaluator"
    )

    parser.add_argument("source")
    parser.add_argument("target")
    parser.add_argument(
        "--commitment-file",
        type=Path,
        default=Path("contracts/commitments.toml"),
    )
    parser.add_argument(
        "--commitment-id",
        default="purl_preservation_v1",
    )
    parser.add_argument("--json", action="store_true")

    args = parser.parse_args()

    commitment = load_commitment(
        args.commitment_file,
        args.commitment_id,
    )

    with Path(args.source).open(encoding="utf-8") as file:
        source_doc = json.load(file)

    with Path(args.target).open(encoding="utf-8") as file:
        target_doc = json.load(file)

    report = evaluate(
        source_doc,
        target_doc,
        commitment,
    )

    if args.json:
        print(json.dumps(report, indent=2))
        return

    counts, findings = summarize(report)

    print(
        f"# {report['source_format']} -> "
        f"{report['target_format']}  "
        f"({report['commitment']})"
    )

    verdict_order = [
        "PRESERVED",
        "VIOLATED_DROPPED",
        "VIOLATED_RELOCATED",
        "VIOLATED_ALTERED",
        "UNSUPPORTED",
        "UNDERDETERMINED",
        "UNANCHORABLE",
        "NOT_APPLICABLE",
    ]

    for verdict in verdict_order:
        if counts.get(verdict):
            print(f"  {verdict:20s} {counts[verdict]}")

    if findings:
        print("\n# findings (violations):")

        for result in findings:
            print(
                f"  [{result['verdict']}] "
                f"{result['ref']}  "
                f"{result['purl']}\n"
                f"      {result['detail']}"
            )


if __name__ == "__main__":
    main()
