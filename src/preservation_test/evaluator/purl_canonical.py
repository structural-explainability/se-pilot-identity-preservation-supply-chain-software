"""Canonical PURL comparison for the same_when rule.

Canonicalization is delegated to the Package URL reference implementation
rather than reimplemented locally.
"""

from packageurl import PackageURL


def canonical(purl_str: object) -> str | None:
    """Return the canonical PURL string, or None when parsing fails."""
    if not isinstance(purl_str, str) or not purl_str:
        return None

    value = purl_str.strip()
    if not value.lower().startswith("pkg:"):
        return None

    try:
        return PackageURL.from_string(value).to_string()
    except TypeError, ValueError:
        return None


def same(a: object, b: object) -> bool:
    """Return whether two PURLs have the same canonical representation."""
    canonical_a = canonical(a)
    canonical_b = canonical(b)

    return canonical_a is not None and canonical_a == canonical_b


def coordinates(purl_str: object) -> tuple[str, str, str] | None:
    """Return type, namespace, and name with version and qualifiers omitted.

    This reduced tuple is used only to distinguish an altered PURL from a
    completely absent PURL after the source and target components have already
    been independently anchored.
    """
    if not isinstance(purl_str, str):
        return None

    try:
        purl = PackageURL.from_string(purl_str)
    except TypeError, ValueError:
        return None

    return (
        purl.type,
        (purl.namespace or "").lower(),
        purl.name,
    )
