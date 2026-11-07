#Requires -Version 7.0

<#
============================================================
freeze_03.ps1
============================================================

WHAT: Check, establish, or verify Freeze 03 for the kernel
      missing-value comparison.

WHEN: After the completed Freeze 02 baseline and before the
      formal kernel comparison.

HOW: Run from the repository root with exactly one switch:

     .\freeze_03.ps1 -Check
     .\freeze_03.ps1 -Establish
     .\freeze_03.ps1 -Verify

-Check      Runs the L4 synthetic checks, preparation checks,
            and freeze prerequisites apart from clean-tree.

            The preparation self-test also reads the pinned
            baseline evidence in memory and prints its counts.

-Establish  Requires a clean committed tree and absent comparison
            output directories. Creates the freeze record once.
            Review and commit the record before execution.

-Verify     Verifies the established apparatus and Freeze 02.
            Permits comparison outputs after establishment.

RECORD: contracts/FREEZE_03_KERNEL_MISSING_VALUES.md

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
        uv run --no-project comparison/freeze_03_run_l4.py --self-test
        if ($LASTEXITCODE -ne 0) {
            throw "L4 synthetic checks failed."
        }

        uv run --frozen python comparison/freeze_03_prepare.py --self-test
        if ($LASTEXITCODE -ne 0) {
            throw "Comparison preparation checks failed."
        }

        uv run --frozen python comparison/freeze_03_control.py --check
        if ($LASTEXITCODE -ne 0) {
            throw "Freeze 03 checks failed."
        }
    }

    if ($Establish) {
        uv run --frozen python comparison/freeze_03_control.py --establish
        if ($LASTEXITCODE -ne 0) {
            throw "Freeze 03 creation failed."
        }
    }

    if ($Verify) {
        uv run --frozen python comparison/freeze_03_control.py --verify
        if ($LASTEXITCODE -ne 0) {
            throw "Freeze 03 verification failed."
        }
    }
}
finally {
    Pop-Location
}
