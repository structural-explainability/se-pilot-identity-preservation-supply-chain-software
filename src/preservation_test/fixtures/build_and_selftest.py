"""Build and run synthetic representation-preservation engineering tests.

The synthetic SBOMs exercise each verdict currently implemented by the
representation-preservation evaluator.

These fixtures are engineering tests, not generalization evidence and not
historical validation artifacts.
"""

import json
from pathlib import Path
import sys

from preservation_test.evaluator import evaluate as evaluator

FIXTURE_DIR = Path(__file__).parent
REPO_ROOT = Path(__file__).parents[3]
COMMITMENT_FILE = REPO_ROOT / "contracts" / "commitments.toml"


def fake_sha256(character: str) -> str:
    """Return a deterministic synthetic SHA-256-shaped value."""
    return character * 64


def build_source() -> dict[str, object]:
    """Build the synthetic SPDX 2.3 source SBOM."""
    return {
        "spdxVersion": "SPDX-2.3",
        "SPDXID": "SPDXRef-DOCUMENT",
        "packages": [
            {
                "SPDXID": "SPDXRef-A",
                "name": "A",
                "checksums": [
                    {
                        "algorithm": "SHA256",
                        "checksumValue": fake_sha256("a"),
                    }
                ],
                "externalRefs": [
                    {
                        "referenceCategory": "PACKAGE-MANAGER",
                        "referenceType": "purl",
                        "referenceLocator": "pkg:pypi/Requests@2.31.0",
                    }
                ],
            },
            {
                "SPDXID": "SPDXRef-B",
                "name": "B",
                "checksums": [
                    {
                        "algorithm": "SHA256",
                        "checksumValue": fake_sha256("b"),
                    }
                ],
                "externalRefs": [
                    {
                        "referenceCategory": "PACKAGE-MANAGER",
                        "referenceType": "purl",
                        "referenceLocator": "pkg:deb/debian/tzdata@2025b-0",
                    }
                ],
            },
            {
                "SPDXID": "SPDXRef-C",
                "name": "C",
                "checksums": [
                    {
                        "algorithm": "SHA256",
                        "checksumValue": fake_sha256("c"),
                    }
                ],
                "externalRefs": [
                    {
                        "referenceCategory": "PACKAGE-MANAGER",
                        "referenceType": "purl",
                        "referenceLocator": "pkg:maven/org.apache/log@2.20",
                    }
                ],
            },
            {
                "SPDXID": "SPDXRef-D",
                "name": "D",
                "checksums": [
                    {
                        "algorithm": "SHA256",
                        "checksumValue": fake_sha256("d"),
                    }
                ],
                "externalRefs": [
                    {
                        "referenceCategory": "PACKAGE-MANAGER",
                        "referenceType": "purl",
                        "referenceLocator": "pkg:npm/left-pad@1.3.0",
                    }
                ],
            },
            {
                "SPDXID": "SPDXRef-E",
                "name": "E",
                "checksums": [
                    {
                        "algorithm": "SHA256",
                        "checksumValue": fake_sha256("e"),
                    }
                ],
                "externalRefs": [
                    {
                        "referenceCategory": "PACKAGE-MANAGER",
                        "referenceType": "purl",
                        "referenceLocator": "pkg:gem/rails@7.0",
                    }
                ],
            },
            {
                "SPDXID": "SPDXRef-F",
                "name": "F",
                "checksums": [
                    {
                        "algorithm": "SHA256",
                        "checksumValue": fake_sha256("f"),
                    }
                ],
            },
            {
                "SPDXID": "SPDXRef-G",
                "name": "G",
                "checksums": [
                    {
                        "algorithm": "SHA256",
                        "checksumValue": fake_sha256("g"),
                    }
                ],
                "externalRefs": [
                    {
                        "referenceCategory": "PACKAGE-MANAGER",
                        "referenceType": "purl",
                        "referenceLocator": "pkg:pypi/example@1.0",
                    },
                    {
                        "referenceCategory": "PACKAGE-MANAGER",
                        "referenceType": "purl",
                        "referenceLocator": "pkg:pypi/example@1.0?repository_url=https://example.invalid",
                    },
                ],
            },
            {
                "SPDXID": "SPDXRef-H",
                "name": "H",
                "checksums": [
                    {
                        "algorithm": "SHA256",
                        "checksumValue": fake_sha256("h"),
                    }
                ],
                "externalRefs": [
                    {
                        "referenceCategory": "PACKAGE-MANAGER",
                        "referenceType": "purl",
                        "referenceLocator": "pkg:golang/example.org/h@1.0.0",
                    }
                ],
            },
        ],
    }


def build_target() -> dict[str, object]:
    """Build the synthetic CycloneDX target SBOM."""
    return {
        "bomFormat": "CycloneDX",
        "specVersion": "1.6",
        "components": [
            # A: preserved.
            {
                "name": "A",
                "hashes": [
                    {
                        "alg": "SHA-256",
                        "content": fake_sha256("a"),
                    }
                ],
                "purl": "pkg:pypi/requests@2.31.0",
            },
            # B: relocated to a noncanonical properties entry.
            {
                "name": "B",
                "hashes": [
                    {
                        "alg": "SHA-256",
                        "content": fake_sha256("b"),
                    }
                ],
                "properties": [
                    {
                        "name": "example:source-purl",
                        "value": "pkg:deb/debian/tzdata@2025b-0",
                    }
                ],
            },
            # C: dropped.
            {
                "name": "C",
                "hashes": [
                    {
                        "alg": "SHA-256",
                        "content": fake_sha256("c"),
                    }
                ],
            },
            # D: altered after anchoring.
            {
                "name": "D",
                "hashes": [
                    {
                        "alg": "SHA-256",
                        "content": fake_sha256("d"),
                    }
                ],
                "purl": "pkg:npm/left-pad@1.2.0",
            },
            # E: no shared anchor.
            {
                "name": "E",
                "hashes": [
                    {
                        "alg": "SHA-256",
                        "content": fake_sha256("z"),
                    }
                ],
                "purl": "pkg:gem/rails@7.0",
            },
            # F: source has no PURL.
            {
                "name": "F",
                "hashes": [
                    {
                        "alg": "SHA-256",
                        "content": fake_sha256("f"),
                    }
                ],
            },
            # G: source cardinality is already underdetermined, so target
            # content must not determine the verdict.
            {
                "name": "G",
                "hashes": [
                    {
                        "alg": "SHA-256",
                        "content": fake_sha256("g"),
                    }
                ],
                "purl": "pkg:pypi/example@1.0",
            },
            # H1/H2: the same source hash resolves to two target components.
            {
                "name": "H1",
                "hashes": [
                    {
                        "alg": "SHA-256",
                        "content": fake_sha256("h"),
                    }
                ],
                "purl": "pkg:golang/example.org/h@1.0.0",
            },
            {
                "name": "H2",
                "hashes": [
                    {
                        "alg": "SHA-256",
                        "content": fake_sha256("h"),
                    }
                ],
                "purl": "pkg:golang/example.org/h@1.0.0",
            },
        ],
    }


def write_fixture(path: Path, document: dict[str, object]) -> None:
    """Write one synthetic fixture document."""
    path.write_text(
        json.dumps(document, indent=2) + "\n",
        encoding="utf-8",
    )


def check_expected_verdicts(
    report: dict[str, object],
    expected: dict[str, str],
) -> bool:
    """Check expected primary verdicts for synthetic source components."""
    results = report["results"]
    if not isinstance(results, list):
        raise TypeError("report results must be a list")

    by_ref: dict[str, set[str]] = {}

    for result in results:
        if not isinstance(result, dict):
            continue

        ref = str(result["ref"])
        verdict = str(result["verdict"])
        by_ref.setdefault(ref, set()).add(verdict)

    ok = True

    print("verdict check (source -> target):")

    for ref, expected_verdict in expected.items():
        actual = by_ref.get(ref, set())
        passed = actual == {expected_verdict}

        if not passed:
            ok = False

        mark = "ok " if passed else "XX "

        print(f"  {mark}{ref}: expected {expected_verdict:20s} got {sorted(actual)}")

    return ok


def check_unsupported(
    source: dict[str, object],
    target: dict[str, object],
    commitment: dict[str, object],
) -> bool:
    """Verify the unsupported-target refusal branch."""
    unsupported_commitment = dict(commitment)
    unsupported_commitment["representable_in"] = ["spdx-2.3"]

    report = evaluator.evaluate(
        source,
        target,
        unsupported_commitment,
    )

    results = report["results"]
    if not isinstance(results, list):
        raise TypeError("report results must be a list")

    unsupported = [
        result
        for result in results
        if isinstance(result, dict) and result.get("verdict") == "UNSUPPORTED"
    ]

    passed = bool(unsupported)
    mark = "ok " if passed else "XX "

    print(
        f"  {mark}UNSUPPORTED branch fires when target format is not "
        f"representable ({len(unsupported)} PURLs refused)"
    )

    return passed


def write_fixtures() -> None:
    """Write the synthetic SPDX and CycloneDX fixture files."""
    write_fixture(
        FIXTURE_DIR / "source.spdx.json",
        build_source(),
    )
    write_fixture(
        FIXTURE_DIR / "target.cdx.json",
        build_target(),
    )


def run_selftest() -> bool:
    """Exercise all implemented representation-preservation verdict classes."""
    source = build_source()
    target = build_target()

    commitment = evaluator.load_commitment(
        COMMITMENT_FILE,
        "purl_preservation_v1",
    )

    report = evaluator.evaluate(
        source,
        target,
        commitment,
    )

    expected = {
        "SPDXRef-A": "PRESERVED",
        "SPDXRef-B": "VIOLATED_RELOCATED",
        "SPDXRef-C": "VIOLATED_DROPPED",
        "SPDXRef-D": "VIOLATED_ALTERED",
        "SPDXRef-E": "UNANCHORABLE",
        "SPDXRef-F": "NOT_APPLICABLE",
        "SPDXRef-G": "UNDERDETERMINED",
        "SPDXRef-H": "UNANCHORABLE",
    }

    verdicts_ok = check_expected_verdicts(
        report,
        expected,
    )

    unsupported_ok = check_unsupported(
        source,
        target,
        commitment,
    )

    return verdicts_ok and unsupported_ok


def main() -> int:
    """Write fixtures and run the integrated engineering self-test."""
    write_fixtures()

    ok = run_selftest()

    print()
    print("SELF-TEST", "PASSED" if ok else "FAILED")

    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
