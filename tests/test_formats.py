"""Tests for SBOM format adapters."""

from preservation_test.evaluator import formats


def test_spdx23_requires_package_manager_purl_external_ref() -> None:
    document: dict[str, object] = {
        "spdxVersion": "SPDX-2.3",
        "packages": [
            {
                "SPDXID": "SPDXRef-A",
                "externalRefs": [
                    {
                        "referenceCategory": "OTHER",
                        "referenceType": "purl",
                        "referenceLocator": "pkg:pypi/example@1.0",
                    }
                ],
            }
        ],
    }

    _, components = formats.load(document)

    assert components[0].canonical_purls == set()


def test_spdx23_reads_canonical_purl_external_ref() -> None:
    document: dict[str, object] = {
        "spdxVersion": "SPDX-2.3",
        "packages": [
            {
                "SPDXID": "SPDXRef-A",
                "externalRefs": [
                    {
                        "referenceCategory": "PACKAGE-MANAGER",
                        "referenceType": "purl",
                        "referenceLocator": "pkg:pypi/Example@1.0",
                    }
                ],
            }
        ],
    }

    _, components = formats.load(document)

    assert components[0].canonical_purls == {
        "pkg:pypi/example@1.0",
    }


def test_cyclonedx_property_purl_is_noncanonical() -> None:
    document: dict[str, object] = {
        "bomFormat": "CycloneDX",
        "specVersion": "1.6",
        "components": [
            {
                "name": "A",
                "properties": [
                    {
                        "name": "example:purl",
                        "value": "pkg:pypi/example@1.0",
                    }
                ],
            }
        ],
    }

    _, components = formats.load(document)

    assert components[0].canonical_purls == set()
    assert components[0].other_purls == {
        "pkg:pypi/example@1.0",
    }


def test_cyclonedx_component_purl_is_canonical() -> None:
    document: dict[str, object] = {
        "bomFormat": "CycloneDX",
        "specVersion": "1.6",
        "components": [
            {
                "name": "A",
                "purl": "pkg:pypi/Example@1.0",
            }
        ],
    }

    _, components = formats.load(document)

    assert components[0].canonical_purls == {
        "pkg:pypi/example@1.0",
    }


def test_spdx30_does_not_treat_external_identifier_as_canonical_purl() -> None:
    document: dict[str, object] = {
        "spdxVersion": "SPDX-3.0.1",
        "@graph": [
            {
                "spdxId": "SPDXRef-A",
                "name": "A",
                "externalIdentifier": [
                    {
                        "externalIdentifierType": "packageUrl",
                        "identifier": "pkg:pypi/example@1.0",
                    }
                ],
            }
        ],
    }

    _, components = formats.load(document)

    assert components == []


def test_spdx30_reads_package_url_as_canonical_purl() -> None:
    document: dict[str, object] = {
        "spdxVersion": "SPDX-3.0.1",
        "@graph": [
            {
                "spdxId": "SPDXRef-A",
                "name": "A",
                "packageUrl": "pkg:pypi/Requests@2.31.0",
                "verifiedUsing": [
                    {
                        "algorithm": "SHA256",
                        "hashValue": (
                            "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
                            "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
                        ),
                    }
                ],
            }
        ],
    }

    format_name, components = formats.load(document)

    assert format_name == "spdx-3.0"
    assert len(components) == 1
    assert components[0].ref == "SPDXRef-A"
    assert components[0].canonical_purls == {
        "pkg:pypi/requests@2.31.0",
    }
    assert components[0].anchors == {
        (
            "SHA-256",
            "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        )
    }
