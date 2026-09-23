"""Source-side PURL and anchor inspection using the frozen format adapters.

Only the Freeze 01 source adapter (formats.load) is applied, and only to the
source document. No target document exists at this stage and the evaluator's
comparison logic is never called.
"""

from collections import Counter
from dataclasses import dataclass
from typing import Any

from preservation_test.evaluator import formats

ECOSYSTEM_NONE = "none"
ECOSYSTEM_MIXED = "mixed"


class AdapterLoadError(RuntimeError):
    """Raised when the frozen adapter cannot load a source document."""


@dataclass(frozen=True)
class PurlInspection:
    """Source-side component counts under the frozen adapter."""

    adapter_format: str
    purl_count: int
    eligible_purl_count: int
    purl_type_counts: dict[str, int]


def purl_type(canonical_purl: str) -> str:
    """Return the type segment of a canonical PURL ('pkg:<type>/...')."""
    body = canonical_purl.removeprefix("pkg:")
    return body.split("/", 1)[0].lower()


def inspect_source(document: dict[str, Any]) -> PurlInspection:
    """Load the source with the frozen adapter and count relevant components."""
    try:
        adapter_format, components = formats.load(document)
    # WHY: any adapter failure is recorded as a screening fact, not raised.
    except Exception as error:
        raise AdapterLoadError(f"{type(error).__name__}: {error}") from error

    type_counts: Counter[str] = Counter()
    for component in components:
        for purl in component.canonical_purls:
            type_counts[purl_type(purl)] += 1

    return PurlInspection(
        adapter_format=adapter_format,
        # Canonical source PURLs across all components.
        purl_count=sum(len(c.canonical_purls) for c in components),
        # Canonical source PURLs on components that also carry a content-hash
        # anchor, i.e. PURLs the frozen evaluator could anchor.
        eligible_purl_count=sum(
            len(c.canonical_purls) for c in components if c.anchors
        ),
        purl_type_counts=dict(sorted(type_counts.items())),
    )


def assign_ecosystem(purl_type_counts: dict[str, int]) -> str:
    """Apply the predeclared package_ecosystem reporting rule.

    The PURL type with the most canonical source PURLs; ties broken lexically;
    'mixed' when the top type covers under half of canonical source PURLs.
    """
    total = sum(purl_type_counts.values())
    if total == 0:
        return ECOSYSTEM_NONE
    top_type, top_count = min(
        purl_type_counts.items(), key=lambda item: (-item[1], item[0])
    )
    if top_count * 2 < total:
        return ECOSYSTEM_MIXED
    return top_type
