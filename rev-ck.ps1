uv run python -c @'
from pathlib import Path
import json

root = Path("validation/cyclonedx-cli-reverse-sweep/artifacts")

versions = [
    "0.29.0",
    "0.29.1",
    "0.29.2",
    "0.30.0",
    "0.31.0",
    "0.32.0",
    "0.33.0",
    "0.33.1",
]

populations = {}

for version in versions:
    path = root / version / "result.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    refs = {item["ref"] for item in data["results"]}
    populations[version] = refs
    print(f"{version}: {len(refs)} refs")

baseline_version = versions[0]
baseline = populations[baseline_version]

print()
for version in versions[1:]:
    refs = populations[version]
    added = refs - baseline
    missing = baseline - refs

    print(
        f"{version}: "
        f"same={refs == baseline} "
        f"added={len(added)} "
        f"missing={len(missing)}"
    )

    if added:
        print("  added:")
        for ref in sorted(added):
            print(f"    {ref}")

    if missing:
        print("  missing:")
        for ref in sorted(missing):
            print(f"    {ref}")
'@
