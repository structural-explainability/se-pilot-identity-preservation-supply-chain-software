#Requires -Version 7.0

<#
============================================================
freeze_04.ps1
============================================================

WHAT: Check, establish, or verify Freeze 04 for the
      IdentityOps comparison.

WHEN: After the completed Freeze 03 evidence and before the
      formal Freeze 04 arms are run.

HOW: Run from the repository root with exactly one switch:

     .\freeze_04.ps1 -Check
     .\freeze_04.ps1 -Establish
     .\freeze_04.ps1 -Verify

-Check      Runs the self-tests of the reference arm, the
            IdentityOps arm, and the comparison, then the
            freeze prerequisites apart from clean-tree.

            The self-tests also read the pinned prepared input
            and check both arms against it in memory.

-Establish  Requires a clean committed tree and an absent
            comparison output directory. Creates the freeze
            record once. Review and commit the record before
            execution.

-Verify     Verifies the established apparatus and Freeze 02.
            Permits comparison outputs after establishment.

RECORD: contracts/FREEZE_04_IDENTITYOPS_COMPARISON.md

The script invokes uv and may populate dependency caches.
The Check operation creates no formal comparison artifacts.
Git commits and pushes are separate operations.
============================================================
#>

param(
    [switch]$Check,
    [switch]$Establish,
    [switch]$Verify
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
$PSNativeCommandUseErrorActionPreference = $false

if (@(@($Check, $Establish, $Verify) | Where-Object { $_ }).Count -ne 1) {
    throw "Use exactly one of -Check, -Establish or -Verify."
}

Push-Location $PSScriptRoot

try {
    if ($Check) {
        uv run --frozen python comparison/freeze_04_reference.py --self-test
        if ($LASTEXITCODE -ne 0) {
            throw "Reference arm checks failed."
        }

        uv run --no-project comparison/freeze_04_identityops.py --self-test
        if ($LASTEXITCODE -ne 0) {
            throw "IdentityOps arm checks failed."
        }

        uv run --frozen python comparison/freeze_04_compare.py --self-test
        if ($LASTEXITCODE -ne 0) {
            throw "Comparison checks failed."
        }

        uv run --frozen python comparison/freeze_04_control.py --check
        if ($LASTEXITCODE -ne 0) {
            throw "Freeze 04 checks failed."
        }
    }

    if ($Establish) {
        uv run --frozen python comparison/freeze_04_control.py --establish
        if ($LASTEXITCODE -ne 0) {
            throw "Freeze 04 creation failed."
        }
    }

    if ($Verify) {
        uv run --frozen python comparison/freeze_04_control.py --verify
        if ($LASTEXITCODE -ne 0) {
            throw "Freeze 04 verification failed."
        }
    }
}
finally {
    Pop-Location
}
