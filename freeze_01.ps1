# ============================================================
# freeze_01.ps1
# ============================================================
# Create the first commitment/evaluator freeze record.
#
# Run after the pre-freeze state has been reviewed, tested,
# and committed.
#
# This script records the existing committed state.
# It does not decide whether the study is ready to freeze.
#
# This first freeze is write-once. If frozen scientific
# artifacts later change, record the freeze break rather than
# silently replacing this record.

$ErrorActionPreference = "Stop"

$FreezeFile = "contracts/FREEZE_01_COMMITMENT_EVALUATOR.md"

$FrozenFiles = @(
    "contracts/schema.md"
    "contracts/sources.toml"
    "contracts/commitments.toml"
    "src/preservation_test/evaluator/purl_canonical.py"
    "src/preservation_test/evaluator/formats.py"
    "src/preservation_test/evaluator/evaluate.py"
    "docs/en/run.md"
)

# ------------------------------------------------------------
# Require repository root.
# ------------------------------------------------------------

if (-not (Test-Path ".git")) {
    throw "Run freeze_01.ps1 from the repository root."
}

# ------------------------------------------------------------
# Do not overwrite the first freeze.
# ------------------------------------------------------------

if (Test-Path $FreezeFile) {
    throw "$FreezeFile already exists. The first freeze must not be overwritten."
}

# ------------------------------------------------------------
# Require a clean committed state.
# ------------------------------------------------------------

$GitStatus = git status --porcelain

if ($LASTEXITCODE -ne 0) {
    throw "Could not determine Git working-tree status."
}

if ($GitStatus) {
    Write-Host ""
    Write-Host "FREEZE NOT CREATED."
    Write-Host ""
    Write-Host "The working tree is not clean."
    Write-Host "Review and commit the pre-freeze state first."
    Write-Host ""
    git status --short
    exit 1
}

# ------------------------------------------------------------
# Verify every frozen file exists.
# ------------------------------------------------------------

foreach ($File in $FrozenFiles) {
    if (-not (Test-Path $File)) {
        throw "Frozen file not found: $File"
    }
}

# ------------------------------------------------------------
# Capture freeze identity.
# ------------------------------------------------------------

$Timestamp = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
$Commit = (git rev-parse HEAD).Trim()

if ($LASTEXITCODE -ne 0 -or -not $Commit) {
    throw "Could not determine the current Git commit."
}

# ------------------------------------------------------------
# Calculate SHA-256 hashes.
# ------------------------------------------------------------

$HashLines = foreach ($File in $FrozenFiles) {
    $Hash = (Get-FileHash -Algorithm SHA256 $File).Hash.ToLowerInvariant()
    "- ``$Hash``  ``$File``"
}

# ------------------------------------------------------------
# Construct freeze record.
# ------------------------------------------------------------

$Lines = @(
    "# First Commitment/Evaluator Freeze"
    ""
    "**Status:** FROZEN"
    ""
    "**Frozen (UTC):** $Timestamp"
    ""
    "**Frozen content commit:** ``$Commit``"
    ""
    "## Purpose"
    ""
    "This freeze was explicitly created by the researcher after review of the"
    "pre-execution commitment, implementation, tests, and protocol."
    ""
    "It fixes the initial ``representation_preservation`` commitment and the"
    "scientific implementation used for subsequent engineering validation."
    ""
    "The pilot was motivated in part by previously known preservation failures,"
    "including the general failure shape reported in cyclonedx-cli #424."
    ""
    "Accordingly, the initial commitment and evaluator are not a blind first test"
    "of that historical case. Previously known cases are engineering validation"
    "evidence, not held-out evidence of generalization."
    ""
    "The files listed below define the frozen representation-preservation"
    "commitment, its authoritative provenance, its interpretation rules, its"
    "implementation, and its adjudication protocol."
    ""
    "Any case used as evidence of generalization must not have been examined"
    "before the applicable generalization freeze."
    ""
    "## Frozen Artifacts"
    ""
)

foreach ($File in $FrozenFiles) {
    $Lines += "- ``$File``"
}

$Lines += @(
    ""
    "## Frozen Content Hashes"
    ""
)

$Lines += $HashLines

$Lines += @(
    ""
    "## Post-Freeze Testing"
    ""
    "Additional tests may be added after this freeze without breaking it if they"
    "only verify the behavior of the frozen artifacts."
    ""
    "If a new test reveals that a frozen artifact must change, the freeze is"
    "broken. The defect must be recorded, corrected against the authoritative"
    "sources, and followed by a new explicit commitment/evaluator freeze before"
    "generalization execution."
    ""
    "A recorded-and-continued edit is not permitted. Changes to frozen scientific"
    "content require an explicit new freeze."
    ""
    "## Engineering Validation"
    ""
    "Cases whose failure shape or relevant behavior was known during study design"
    "remain engineering validation evidence even when executed after this freeze."
    ""
    "Successful reproduction of such cases does not constitute evidence of"
    "generalization."
    ""
    "## Freeze-Break Log"
    ""
    "None."
    ""
)

# ------------------------------------------------------------
# Write UTF-8 without BOM using LF line endings.
# ------------------------------------------------------------

$Content = ($Lines -join "`n") + "`n"
$Encoding = [System.Text.UTF8Encoding]::new($false)

[System.IO.File]::WriteAllText(
    (Join-Path (Get-Location) $FreezeFile),
    $Content,
    $Encoding
)

Write-Host ""
Write-Host "First commitment/evaluator freeze created:"
Write-Host "  $FreezeFile"
Write-Host ""
Write-Host "Frozen content commit:"
Write-Host "  $Commit"
Write-Host ""
Write-Host "Frozen UTC:"
Write-Host "  $Timestamp"
Write-Host ""
Write-Host "Review the freeze record, then commit it."
