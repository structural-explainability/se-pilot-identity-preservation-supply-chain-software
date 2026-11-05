# ============================================================
# freeze_02.ps1
# ============================================================
# Create the generalization freeze after all pre-freeze
# scientific and integrity checks pass.
# Establish Freeze 02 only after the pre-freeze state is committed.
# Review and commit the generated record before formal execution.

$ErrorActionPreference = "Stop"
$PSNativeCommandUseErrorActionPreference = $true

Push-Location $PSScriptRoot

# Require clean committed state, correct repository, etc.
# ...

try {
    uv run --frozen python -m preservation_test.generalization.freeze_02 --establish

    if ($LASTEXITCODE -ne 0) {
        throw "Freeze 02 creation failed."
    }
}
finally {
    Pop-Location
}

# Only after Python verification passes:
# - capture HEAD
# - capture UTC timestamp
# - hash frozen artifacts
# - construct FREEZE_02_GENERALIZATION.md
# - write it without overwriting an existing freeze
