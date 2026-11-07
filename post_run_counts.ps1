#Requires -Version 7.0

<#
============================================================
post_run_counts.ps1
============================================================

WHAT: Count evaluator verdicts and UNANCHORABLE reasons by route.
WHEN: After the formal Freeze 02 run; read-only; may be re-run at any time.
WHY:  Freeze 02 requires UNANCHORABLE results to be reported
      in full, including their count and fraction by route.
      It also resolves B1 (the detail text of the unhashed SPDX source PURL).
HOW:  Run from the repository root:

      .\post_run_counts.ps1

TOOLS: uv (locked environment), Python standard library only.
SKILLS: none.
OBS:  Reads only generalization/results/*/*/evaluation.json.
      Writes nothing.
      Does not run a converter or the evaluator.
      For SPDX sources, prints every record (6 source PURL observations in total).
CUSTOM: none.
#>

$ErrorActionPreference = "Stop"
$PSNativeCommandUseErrorActionPreference = $true

@'
import json
from collections import Counter
from pathlib import Path

VERDICTS = [
    "PRESERVED",
    "VIOLATED_DROPPED",
    "VIOLATED_RELOCATED",
    "VIOLATED_ALTERED",
    "UNSUPPORTED",
    "UNANCHORABLE",
    "NOT_APPLICABLE",
    "UNDERDETERMINED",
]

results_root = Path("generalization/results")
paths = sorted(results_root.glob("*/*/evaluation.json"))

print(f"evaluation.json files found: {len(paths)}")
print()

converter_totals = {}
converter_reasons = {}
overall = Counter()

for path in paths:
    source_id = path.parent.parent.name
    converter = path.parent.name
    document = json.loads(path.read_text(encoding="utf-8-sig"))
    records = document["results"]

    verdicts = Counter(record["verdict"] for record in records)
    total = len(records)
    unanchorable = verdicts.get("UNANCHORABLE", 0)
    fraction = (100.0 * unanchorable / total) if total else 0.0

    print(f"ROUTE {source_id}--{converter}")
    print(f"  records: {total}")

    for verdict in VERDICTS:
        print(f"  {verdict}: {verdicts.get(verdict, 0)}")

    for verdict in sorted(set(verdicts) - set(VERDICTS)):
        print(f"  OTHER VERDICT {verdict}: {verdicts[verdict]}")

    print(f"  UNANCHORABLE fraction: {unanchorable}/{total} = {fraction:.1f}%")

    reasons = Counter(
        record["detail"] for record in records if record["verdict"] == "UNANCHORABLE"
    )

    for reason, count in sorted(reasons.items()):
        print(f"  reason ({count}): {reason}")

    if source_id.startswith("gen-spdx-"):
        for record in records:
            print(
                f"  record: {record['ref']} | {record['verdict']} "
                f"| {record['purl']} | {record['detail']}"
            )

    print()

    converter_totals.setdefault(converter, Counter()).update(verdicts)
    converter_reasons.setdefault(converter, Counter()).update(reasons)
    overall.update(verdicts)

print("BY CONVERTER")

for converter in sorted(converter_totals):
    counts = converter_totals[converter]
    print(f"  {converter}: records={sum(counts.values())}", end="")

    for verdict in VERDICTS:
        print(f" {verdict}={counts.get(verdict, 0)}", end="")

    print()

print()
print("UNANCHORABLE REASONS BY CONVERTER")

for converter in sorted(converter_reasons):
    for reason, count in sorted(converter_reasons[converter].items()):
        print(f"  {converter}: ({count}) {reason}")

print()
print("OVERALL")
print(f"  records: {sum(overall.values())}")

for verdict in VERDICTS:
    print(f"  {verdict}: {overall.get(verdict, 0)}")
'@ | uv run --locked python -
