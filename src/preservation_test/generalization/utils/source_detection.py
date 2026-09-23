"""Detect the source standard and specification version of a candidate.

This is deliberately independent of the frozen evaluator's detect_format,
which routes every SPDX 2.x document to the SPDX 2.3 adapter and cannot
recognize SPDX 3.0.1 JSON-LD. Scope decisions are made here, from declared
document metadata, before any frozen adapter is applied.
"""

from dataclasses import dataclass
import json
from typing import Any

from preservation_test.generalization.utils.sampling_config import FormatsSpec

UTF8_BOM = b"\xef\xbb\xbf"

STANDARD_CYCLONEDX = "cyclonedx"
STANDARD_SPDX = "spdx"
STANDARD_SPDX3_JSONLD = "spdx-3-jsonld"
STANDARD_OTHER_JSONLD = "other-jsonld"
STANDARD_UNKNOWN = "unknown"

SBOM_STANDARDS = frozenset({STANDARD_CYCLONEDX, STANDARD_SPDX, STANDARD_SPDX3_JSONLD})

SERIALIZATION_JSON = "json"
SERIALIZATION_JSONLD = "json-ld"
SERIALIZATION_UNPARSEABLE = "unparseable"

# Frozen adapter format names expected for each in-scope standard.
EXPECTED_ADAPTER_FORMAT = {
    STANDARD_CYCLONEDX: "cyclonedx",
    STANDARD_SPDX: "spdx-2.3",
}


@dataclass(frozen=True)
class ParsedJson:
    """Result of parsing candidate bytes as a JSON object."""

    document: dict[str, Any] | None
    has_utf8_bom: bool
    error: str | None


@dataclass(frozen=True)
class SourceFormat:
    """Declared source standard and specification version."""

    standard: str
    spec_version: str | None


def parse_json_object(data: bytes) -> ParsedJson:
    """Parse candidate bytes as a UTF-8 JSON object.

    A leading UTF-8 byte-order mark is tolerated and recorded.
    """
    has_bom = data.startswith(UTF8_BOM)
    try:
        document = json.loads(data.decode("utf-8-sig"))
    except UnicodeDecodeError, json.JSONDecodeError:
        return ParsedJson(
            document=None, has_utf8_bom=has_bom, error="json_parse_failure"
        )
    if not isinstance(document, dict):
        return ParsedJson(document=None, has_utf8_bom=has_bom, error="not_json_object")
    return ParsedJson(document=document, has_utf8_bom=has_bom, error=None)


def detect_source_format(document: dict[str, Any]) -> SourceFormat:
    """Classify a parsed document by its own declared format metadata."""
    if document.get("bomFormat") == "CycloneDX":
        version = document.get("specVersion")
        return SourceFormat(
            STANDARD_CYCLONEDX, str(version) if version is not None else None
        )

    if "spdxVersion" in document:
        return SourceFormat(STANDARD_SPDX, str(document.get("spdxVersion")))

    if "@context" in document or "@graph" in document:
        context = json.dumps(document.get("@context", ""), sort_keys=True).lower()
        standard = STANDARD_SPDX3_JSONLD if "spdx" in context else STANDARD_OTHER_JSONLD
        return SourceFormat(standard, None)

    return SourceFormat(STANDARD_UNKNOWN, None)


def format_in_scope(source_format: SourceFormat, formats: FormatsSpec) -> bool:
    """Return whether the declared standard and version are in scope."""
    if source_format.spec_version is None:
        return False
    if source_format.standard == STANDARD_CYCLONEDX:
        return source_format.spec_version in formats.cyclonedx_spec_versions
    if source_format.standard == STANDARD_SPDX:
        return source_format.spec_version in formats.spdx_versions
    return False


def serialization_of(parsed: ParsedJson) -> str:
    """Return the observed serialization of a candidate."""
    if parsed.error == "json_parse_failure":
        return SERIALIZATION_UNPARSEABLE
    document = parsed.document
    if document is not None and ("@context" in document or "@graph" in document):
        return SERIALIZATION_JSONLD
    return SERIALIZATION_JSON
