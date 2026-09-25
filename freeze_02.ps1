# ============================================================
# freeze_02.ps1
# ============================================================
# Create the generalization freeze after all pre-freeze
# scientific and integrity checks pass.

$ErrorActionPreference = "Stop"

# Require clean committed state, correct repository, etc.
# ...

uv run python -m preservation_test.generalization.verification.verify_05_freeze_02

if ($LASTEXITCODE -ne 0) {
    throw "Freeze 02 verification failed."
}

# Only after Python verification passes:
# - capture HEAD
# - capture UTC timestamp
# - hash frozen artifacts
# - construct FREEZE_02_GENERALIZATION.md
# - write it without overwriting an existing freeze
