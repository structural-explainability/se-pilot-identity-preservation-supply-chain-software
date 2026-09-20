"""Format adapters for supported SBOM representations.

Each adapter maps a concrete SBOM representation into the generic Component
model consumed by the preservation evaluator.

Format adapters know representation-specific JSON structure. They do not know
about particular bugs, packages, converters, or historical artifacts.
"""

from dataclasses import dataclass, field

from preservation_test.evaluator.purl_canonical import canonical


@dataclass
class Component:
    """Normalized component information required by the evaluator."""

    ref: str
    anchors: set[tuple[str, str]] = field(default_factory=set)
    canonical_purls: set[str] = field(default_factory=set)
    other_purls: set[str] = field(default_factory=set)


def _norm_alg(value: object) -> str:
    """Normalize supported hash algorithm labels."""
    if not isinstance(value, str):
        return ""

    algorithm = value.upper().replace("_", "-")

    aliases = {
        "SHA256": "SHA-256",
        "SHA512": "SHA-512",
        "SHA1": "SHA-1",
    }

    return aliases.get(algorithm, algorithm)


def _looks_like_purl(value: object) -> bool:
    """Return whether a value has the lexical shape of a PURL."""
    return isinstance(value, str) and value.strip().lower().startswith("pkg:")


def detect_format(doc: dict[str, object]) -> str:
    """Detect the supported SBOM representation."""
    bom_format = doc.get("bomFormat")
    spdx_version = str(doc.get("spdxVersion", ""))

    if bom_format == "CycloneDX":
        return "cyclonedx"

    if spdx_version.startswith("SPDX-3"):
        return "spdx-3.0"

    if spdx_version.startswith("SPDX-2"):
        return "spdx-2.3"

    if "packages" in doc:
        return "spdx-2.3"

    raise ValueError("could not detect supported SBOM format")


def load_spdx23(doc: dict[str, object]) -> list[Component]:
    """Load SPDX 2.3 package records."""
    components: list[Component] = []

    packages = doc.get("packages", [])
    if not isinstance(packages, list):
        return components

    for package in packages:
        if not isinstance(package, dict):
            continue

        component = Component(
            ref=str(package.get("SPDXID") or package.get("name") or "?")
        )

        checksums = package.get("checksums", [])
        if isinstance(checksums, list):
            for checksum in checksums:
                if not isinstance(checksum, dict):
                    continue

                algorithm = _norm_alg(checksum.get("algorithm"))
                value = str(checksum.get("checksumValue") or "").lower()

                if algorithm and value:
                    component.anchors.add((algorithm, value))

        external_refs = package.get("externalRefs", [])
        if isinstance(external_refs, list):
            for external_ref in external_refs:
                if not isinstance(external_ref, dict):
                    continue

                if (
                    external_ref.get("referenceCategory") == "PACKAGE-MANAGER"
                    and external_ref.get("referenceType") == "purl"
                ):
                    purl = canonical(external_ref.get("referenceLocator"))
                    if purl:
                        component.canonical_purls.add(purl)

        components.append(component)

    return components


def load_spdx30(doc: dict[str, object]) -> list[Component]:
    """Load SPDX 3.0 software package records."""
    components: list[Component] = []

    elements = doc.get("@graph", doc.get("elements", []))
    if not isinstance(elements, list):
        return components

    for element in elements:
        if not isinstance(element, dict):
            continue

        # The initial pilot evaluates package records carrying packageUrl or
        # usable verification hashes.
        if "packageUrl" not in element and "verifiedUsing" not in element:
            continue

        component = Component(
            ref=str(element.get("spdxId") or element.get("name") or "?")
        )

        verified_using = element.get("verifiedUsing", [])
        if isinstance(verified_using, list):
            for verification in verified_using:
                if not isinstance(verification, dict):
                    continue

                algorithm = _norm_alg(verification.get("algorithm"))
                value = str(verification.get("hashValue") or "").lower()

                if algorithm and value:
                    component.anchors.add((algorithm, value))

        purl = canonical(element.get("packageUrl"))
        if purl:
            component.canonical_purls.add(purl)

        components.append(component)

    return components


def _iter_components(items: object):
    """Yield CycloneDX components recursively."""
    if not isinstance(items, list):
        return

    for component in items:
        if not isinstance(component, dict):
            continue

        yield component
        yield from _iter_components(component.get("components"))


def load_cyclonedx(doc: dict[str, object]) -> list[Component]:
    """Load CycloneDX component records."""
    components: list[Component] = []

    for item in _iter_components(doc.get("components")):
        component = Component(ref=str(item.get("bom-ref") or item.get("name") or "?"))

        hashes = item.get("hashes", [])
        if isinstance(hashes, list):
            for item_hash in hashes:
                if not isinstance(item_hash, dict):
                    continue

                algorithm = _norm_alg(item_hash.get("alg"))
                value = str(item_hash.get("content") or "").lower()

                if algorithm and value:
                    component.anchors.add((algorithm, value))

        purl = canonical(item.get("purl"))
        if purl:
            component.canonical_purls.add(purl)

        properties = item.get("properties", [])
        if isinstance(properties, list):
            for prop in properties:
                if not isinstance(prop, dict):
                    continue

                value = prop.get("value")
                if _looks_like_purl(value):
                    other_purl = canonical(value)
                    if other_purl:
                        component.other_purls.add(other_purl)

        components.append(component)

    return components


def load(doc: dict[str, object]) -> tuple[str, list[Component]]:
    """Load a supported SBOM into normalized components."""
    format_name = detect_format(doc)

    loaders = {
        "spdx-2.3": load_spdx23,
        "spdx-3.0": load_spdx30,
        "cyclonedx": load_cyclonedx,
    }

    return format_name, loaders[format_name](doc)
