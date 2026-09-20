"""Tests for the representation-preservation evaluator."""

from preservation_test.evaluator import evaluate as evaluator


def fake_sha256(character: str) -> str:
    """Return a deterministic synthetic SHA-256-shaped value."""
    return character * 64


def source_package(
    ref: str,
    hash_character: str,
    purls: list[str] | None = None,
) -> dict[str, object]:
    """Build one synthetic SPDX 2.3 package."""
    package: dict[str, object] = {
        "SPDXID": ref,
        "name": ref,
        "checksums": [
            {
                "algorithm": "SHA256",
                "checksumValue": fake_sha256(hash_character),
            }
        ],
    }

    if purls is not None:
        package["externalRefs"] = [
            {
                "referenceCategory": "PACKAGE-MANAGER",
                "referenceType": "purl",
                "referenceLocator": purl,
            }
            for purl in purls
        ]

    return package


def target_component(
    name: str,
    hash_character: str,
    *,
    purl: str | None = None,
    property_purl: str | None = None,
) -> dict[str, object]:
    """Build one synthetic CycloneDX component."""
    component: dict[str, object] = {
        "name": name,
        "hashes": [
            {
                "alg": "SHA-256",
                "content": fake_sha256(hash_character),
            }
        ],
    }

    if purl is not None:
        component["purl"] = purl

    if property_purl is not None:
        component["properties"] = [
            {
                "name": "example:source-purl",
                "value": property_purl,
            }
        ]

    return component


def make_source(*packages: dict[str, object]) -> dict[str, object]:
    """Build an SPDX 2.3 document."""
    return {
        "spdxVersion": "SPDX-2.3",
        "SPDXID": "SPDXRef-DOCUMENT",
        "packages": list(packages),
    }


def make_target(*components: dict[str, object]) -> dict[str, object]:
    """Build a CycloneDX document."""
    return {
        "bomFormat": "CycloneDX",
        "specVersion": "1.6",
        "components": list(components),
    }


def make_commitment() -> dict[str, object]:
    """Build the minimal commitment required by the evaluator."""
    return {
        "id": "purl_preservation_v1",
        "kind": "representation_preservation",
        "identifier": "purl",
        "representable_in": ["spdx-2.3", "spdx-3.0", "cyclonedx"],
        "cardinality": "single_source_or_source_grounded_selection",
    }


def verdicts(report: dict[str, object]) -> list[str]:
    """Return verdicts from an evaluator report."""
    results = report["results"]
    assert isinstance(results, list)

    return [str(result["verdict"]) for result in results if isinstance(result, dict)]


def test_preserved() -> None:
    source = make_source(
        source_package(
            "SPDXRef-A",
            "a",
            ["pkg:pypi/requests@2.31.0"],
        )
    )
    target = make_target(
        target_component(
            "A",
            "a",
            purl="pkg:pypi/requests@2.31.0",
        )
    )

    report = evaluator.evaluate(source, target, make_commitment())

    assert verdicts(report) == ["PRESERVED"]


def test_relocated() -> None:
    purl = "pkg:deb/debian/tzdata@2025b-0"

    source = make_source(
        source_package(
            "SPDXRef-B",
            "b",
            [purl],
        )
    )
    target = make_target(
        target_component(
            "B",
            "b",
            property_purl=purl,
        )
    )

    report = evaluator.evaluate(source, target, make_commitment())

    assert verdicts(report) == ["VIOLATED_RELOCATED"]


def test_dropped() -> None:
    source = make_source(
        source_package(
            "SPDXRef-C",
            "c",
            ["pkg:maven/org.apache/log@2.20"],
        )
    )
    target = make_target(
        target_component(
            "C",
            "c",
        )
    )

    report = evaluator.evaluate(source, target, make_commitment())

    assert verdicts(report) == ["VIOLATED_DROPPED"]


def test_altered() -> None:
    source = make_source(
        source_package(
            "SPDXRef-D",
            "d",
            ["pkg:npm/left-pad@1.3.0"],
        )
    )
    target = make_target(
        target_component(
            "D",
            "d",
            purl="pkg:npm/left-pad@1.2.0",
        )
    )

    report = evaluator.evaluate(source, target, make_commitment())

    assert verdicts(report) == ["VIOLATED_ALTERED"]


def test_unanchorable_when_no_target_hash_matches() -> None:
    source = make_source(
        source_package(
            "SPDXRef-E",
            "e",
            ["pkg:gem/rails@7.0"],
        )
    )
    target = make_target(
        target_component(
            "E",
            "z",
            purl="pkg:gem/rails@7.0",
        )
    )

    report = evaluator.evaluate(source, target, make_commitment())

    assert verdicts(report) == ["UNANCHORABLE"]


def test_not_applicable_when_source_has_no_purl() -> None:
    source = make_source(
        source_package(
            "SPDXRef-F",
            "f",
        )
    )
    target = make_target(
        target_component(
            "F",
            "f",
        )
    )

    report = evaluator.evaluate(source, target, make_commitment())

    assert verdicts(report) == ["NOT_APPLICABLE"]


def test_underdetermined_when_source_has_multiple_purls() -> None:
    source = make_source(
        source_package(
            "SPDXRef-G",
            "g",
            [
                "pkg:pypi/example@1.0",
                "pkg:pypi/example@1.0?repository_url=https://example.invalid",
            ],
        )
    )
    target = make_target(
        target_component(
            "G",
            "g",
            purl="pkg:pypi/example@1.0",
        )
    )

    report = evaluator.evaluate(source, target, make_commitment())

    assert verdicts(report) == [
        "UNDERDETERMINED",
        "UNDERDETERMINED",
    ]


def test_unanchorable_when_anchor_matches_multiple_targets() -> None:
    source = make_source(
        source_package(
            "SPDXRef-H",
            "h",
            ["pkg:golang/example.org/h@1.0.0"],
        )
    )
    target = make_target(
        target_component(
            "H1",
            "h",
            purl="pkg:golang/example.org/h@1.0.0",
        ),
        target_component(
            "H2",
            "h",
            purl="pkg:golang/example.org/h@1.0.0",
        ),
    )

    report = evaluator.evaluate(source, target, make_commitment())

    assert verdicts(report) == ["UNANCHORABLE"]


def test_unsupported_when_target_format_is_not_representable() -> None:
    commitment = make_commitment()
    commitment["representable_in"] = ["spdx-2.3"]

    source = make_source(
        source_package(
            "SPDXRef-I",
            "i",
            ["pkg:pypi/example@1.0"],
        )
    )
    target = make_target(
        target_component(
            "I",
            "i",
            purl="pkg:pypi/example@1.0",
        )
    )

    report = evaluator.evaluate(source, target, commitment)

    assert verdicts(report) == ["UNSUPPORTED"]
