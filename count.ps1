<#
============================================================
count.ps1
============================================================

USE ONLY PRIOR TO FREEZE 02.

Count canonical PURL occurrences in the preserved SPDX held-out sources.

This is a source-only characterization step.

It reads only the already-preserved SPDX source files used by the
SPDX-to-CycloneDX direction:

- generalization/sources/gen-spdx-e38ee905f9c0.spdx.json
- generalization/sources/gen-spdx-0d278129197b.spdx.json

It does not:

- run a converter;
- invoke the frozen evaluator;
- inspect any held-out transformation output; or
- modify any experimental artifact.

The reported TOTAL for "canonical PURL occurrences" is recorded in
contracts/FREEZE_02_GENERALIZATION.md before Freeze 02 is established.

Run from the repository root:

.\count.ps1
#>

$ErrorActionPreference = "Stop"
$PSNativeCommandUseErrorActionPreference = $true

@'
import json
from pathlib import Path

paths = [
    Path("generalization/sources/gen-spdx-e38ee905f9c0.spdx.json"),
    Path("generalization/sources/gen-spdx-0d278129197b.spdx.json"),
]

total_purls = 0
total_packages = 0
total_exactly_one = 0
total_exactly_one_with_hash = 0

for path in paths:
    document = json.loads(path.read_text(encoding="utf-8-sig"))

    purl_count = 0
    package_count = 0
    exactly_one_count = 0
    exactly_one_with_hash_count = 0

    for package in document.get("packages", []):
        purls = [
            ref.get("referenceLocator")
            for ref in package.get("externalRefs", [])
            if ref.get("referenceCategory") == "PACKAGE-MANAGER"
            and ref.get("referenceType") == "purl"
            and isinstance(ref.get("referenceLocator"), str)
        ]

        if purls:
            package_count += 1
            purl_count += len(purls)

        if len(purls) == 1:
            exactly_one_count += 1

            if package.get("checksums"):
                exactly_one_with_hash_count += 1

    total_purls += purl_count
    total_packages += package_count
    total_exactly_one += exactly_one_count
    total_exactly_one_with_hash += exactly_one_with_hash_count

    print(path.name)
    print(f"  packages with canonical PURL: {package_count}")
    print(f"  canonical PURL occurrences:   {purl_count}")
    print(f"  packages with exactly one:    {exactly_one_count}")
    print(f"  exactly one + content hash:   {exactly_one_with_hash_count}")
    print()

print("TOTAL")
print(f"  packages with canonical PURL: {total_packages}")
print(f"  canonical PURL occurrences:   {total_purls}")
print(f"  packages with exactly one:    {total_exactly_one}")
print(f"  exactly one + content hash:   {total_exactly_one_with_hash}")
'@ | uv run --locked python -
