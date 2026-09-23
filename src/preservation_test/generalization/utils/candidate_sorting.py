"""Deterministic ordering and census selection.

Inventory order is (repository, repository_relative_path). Within a
selection unit (source_standard + subject), the member is the eligible
candidate with the lowest source SHA-256; identical content at several paths
is tie-broken by (repository, repository_relative_path).
"""

from dataclasses import dataclass
from itertools import groupby

from preservation_test.generalization.models.candidate import Candidate
from preservation_test.generalization.utils.candidate_ids import unit_key


@dataclass(frozen=True)
class SelectedUnit:
    """One selected corpus member and the eligible candidates it represents."""

    unit: str
    member: Candidate
    collapsed: tuple[Candidate, ...]


def inventory_order(candidates: list[Candidate]) -> list[Candidate]:
    """Return candidates in deterministic inventory order."""
    return sorted(
        candidates,
        key=lambda item: (item.repository, item.repository_relative_path),
    )


def _unit(candidate: Candidate) -> str:
    return unit_key(candidate.source_standard, candidate.subject)


def _within_unit(candidate: Candidate) -> tuple[str, str, str]:
    return (
        candidate.sha256,
        candidate.repository,
        candidate.repository_relative_path,
    )


def select_census(candidates: list[Candidate]) -> list[SelectedUnit]:
    """Select one candidate per eligible unit; every eligible unit is selected."""
    eligible = sorted(
        (item for item in candidates if item.screening.eligible),
        key=lambda item: (_unit(item), _within_unit(item)),
    )
    selected: list[SelectedUnit] = []
    for unit, group in groupby(eligible, key=_unit):
        members = list(group)
        selected.append(
            SelectedUnit(unit=unit, member=members[0], collapsed=tuple(members[1:]))
        )
    return selected
