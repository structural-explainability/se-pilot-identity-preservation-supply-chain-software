#Requires -Version 7.0

<#
============================================================
freeze_02.ps1
============================================================
Create the generalization freeze after all pre-freeze
scientific and integrity checks pass.
Establish Freeze 02 only after the pre-freeze state is committed.
Review and commit the generated record before formal execution.

Run with:

.\freeze_02.ps1
============================================================
#>

$ErrorActionPreference = "Stop"
$PSNativeCommandUseErrorActionPreference = $true

Push-Location $PSScriptRoot

$Status = git status --porcelain --untracked-files=all
if ($Status) {
    throw "Working tree is not clean. Commit the final pre-freeze state first."
}

try {
    uv run --frozen python -m preservation_test.generalization.freeze_02 --establish

    if ($LASTEXITCODE -ne 0) {
        throw "Freeze 02 creation failed."
    }
}
finally {
    Pop-Location
}

# freeze_02.py adds status, UTC time, pre-freeze commit, and the SHA-256
# inventory to the draft record. It refuses an already established freeze.
