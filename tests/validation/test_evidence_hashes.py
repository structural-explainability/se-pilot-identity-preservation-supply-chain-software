# tests/validation/test_evidence_hashes.py
import hashlib
import json
import pathlib

import pytest

SWEEPS = ["cyclonedx-cli-424-release-sweep", "cyclonedx-cli-reverse-sweep"]


@pytest.mark.parametrize("sweep", SWEEPS)
def test_retained_targets_match_recorded_hashes(sweep):
    root = pathlib.Path("validation") / sweep
    results = json.loads((root / "results.json").read_text(encoding="utf-8"))
    for release in results["releases"]:
        expected = release.get("target_sha256")
        if not expected:
            continue
        [target] = (root / "artifacts" / release["version"]).glob("target.*")
        observed = hashlib.sha256(target.read_bytes()).hexdigest().upper()
        assert observed == expected.upper(), target
