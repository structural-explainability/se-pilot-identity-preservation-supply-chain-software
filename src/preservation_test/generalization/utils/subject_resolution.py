"""Resolve the subject of a source document from source metadata only.

Subject keys:
- CycloneDX: metadata.component as '<group>/<name>@<version>'
  (group and version omitted when absent).
- SPDX 2.3: the single package described by the document, via
  documentDescribes or DESCRIBES/DESCRIBED_BY relationships with the
  document SPDXID, as '<name>@<versionInfo>' (version omitted when absent).
- Otherwise: 'path:<repository>/<parent-directory>'.

Keys are compared exactly. They are recorded for every candidate so that the
rule's behavior is auditable.
"""

from dataclasses import dataclass
from pathlib import PurePosixPath
from typing import Any

from preservation_test.generalization.utils.source_detection import (
    STANDARD_CYCLONEDX,
    STANDARD_SPDX,
)

METHOD_CYCLONEDX = "cyclonedx-metadata-component"
METHOD_SPDX = "spdx-describes"
METHOD_PATH = "path-parent"


@dataclass(frozen=True)
class Subject:
    """Resolved subject key and the rule branch that produced it."""

    key: str
    method: str


def _text(value: object) -> str | None:
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None


def _name_version(name: str, version: str | None) -> str:
    return f"{name}@{version}" if version else name


def _cyclonedx_subject(document: dict[str, Any]) -> str | None:
    metadata = document.get("metadata")
    if not isinstance(metadata, dict):
        return None
    component = metadata.get("component")
    if not isinstance(component, dict):
        return None
    name = _text(component.get("name"))
    if name is None:
        return None
    group = _text(component.get("group"))
    qualified = f"{group}/{name}" if group else name
    return _name_version(qualified, _text(component.get("version")))


def _spdx_described_ids(document: dict[str, Any]) -> set[str]:
    document_id = _text(document.get("SPDXID")) or "SPDXRef-DOCUMENT"
    described: set[str] = set()

    describes = document.get("documentDescribes")
    if isinstance(describes, list):
        described.update(item for item in describes if isinstance(item, str))

    relationships = document.get("relationships")
    if isinstance(relationships, list):
        for relationship in relationships:
            if not isinstance(relationship, dict):
                continue
            kind = relationship.get("relationshipType")
            element = relationship.get("spdxElementId")
            related = relationship.get("relatedSpdxElement")
            if (
                kind == "DESCRIBES"
                and element == document_id
                and isinstance(related, str)
            ):
                described.add(related)
            if (
                kind == "DESCRIBED_BY"
                and related == document_id
                and isinstance(element, str)
            ):
                described.add(element)
    return described


def _spdx_subject(document: dict[str, Any]) -> str | None:
    described = _spdx_described_ids(document)
    if len(described) != 1:
        return None
    (described_id,) = described

    packages = document.get("packages")
    if not isinstance(packages, list):
        return None
    for package in packages:
        if isinstance(package, dict) and package.get("SPDXID") == described_id:
            name = _text(package.get("name"))
            if name is None:
                return None
            return _name_version(name, _text(package.get("versionInfo")))
    return None


def path_subject(repository: str, path: str) -> Subject:
    """Return the fallback subject for a repository-relative path."""
    parent = PurePosixPath(path).parent.as_posix()
    return Subject(key=f"path:{repository}/{parent}", method=METHOD_PATH)


def resolve_subject(
    document: dict[str, Any] | None,
    source_standard: str,
    repository: str,
    path: str,
) -> Subject:
    """Resolve a subject using the predeclared rule."""
    if document is not None:
        if source_standard == STANDARD_CYCLONEDX:
            key = _cyclonedx_subject(document)
            if key is not None:
                return Subject(key=key, method=METHOD_CYCLONEDX)
        if source_standard == STANDARD_SPDX:
            key = _spdx_subject(document)
            if key is not None:
                return Subject(key=key, method=METHOD_SPDX)
    return path_subject(repository, path)
