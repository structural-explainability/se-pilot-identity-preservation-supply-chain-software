#Requires -Version 7.0

<#
============================================================
sit.ps1 (CUSTOM-GET-SITUATED as the EXPERIMENT ADVANCES)
============================================================
Updated: 2026-11-07

Situate the locked project environment, lint, test, and build docs.
For Python tooling repos only.

This script does NOT update uv.lock.
Dependency upgrades must be performed deliberately outside SIT.

Run with:
.\sit.ps1
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# CUSTOM: Check native command exit codes explicitly.
# WHY: Required checks must stop on failure; uv audit remains advisory.
$PSNativeCommandUseErrorActionPreference = $false

# ============================================================
# Verify and synchronize the locked Python environment.
#
# SIT must not update uv.lock.
# ============================================================

uv lock --check
if ($LASTEXITCODE -ne 0) {
    throw "Dependency lockfile verification failed."
}

uv sync --locked
if ($LASTEXITCODE -ne 0) {
    throw "Locked environment synchronization failed."
}

# CUSTOM: The Freeze 03 kernel comparison declares its dependency in
# comparison/run_l4.py.
# Install that declaration into the project environment
# so VS Code and the repository ty check resolve the same pinned kernel.
uv pip install --python .\.venv\Scripts\python.exe -r .\comparison\run_l4.py
if ($LASTEXITCODE -ne 0) {
    throw "Comparison dependency setup failed."
}

# ============================================================
# Update and run repository hooks.
# ============================================================

uv run --locked prek install -f
if ($LASTEXITCODE -ne 0) {
    throw "Repository hook installation failed."
}

# DO NOT RUN THIS:
# uv run --locked prek update --freeze --cooldown-days 7

# ============================================================
# Audit/fix GitHub configuration when GitHub CLI is available.
# ============================================================

if (Get-Command gh -ErrorAction SilentlyContinue) {
    gh auth status *> $null

    if ($LASTEXITCODE -eq 0) {
        uv run --locked zizmor --gh-token (gh auth token) --fix=all .github/
        if ($LASTEXITCODE -ne 0) {
            throw "GitHub configuration audit failed."
        }
    }
}

# ============================================================
# Stage generated or automatically corrected files.
# ============================================================

git add -A
if ($LASTEXITCODE -ne 0) {
    throw "Staging repository changes failed."
}

# ============================================================
# Run repository checks.
# ============================================================

uv run --locked prek run --all-files
if ($LASTEXITCODE -ne 0) {
    throw "Repository hooks failed or modified files. Review changes, stage them, and rerun SIT."
}

# Repeat because the first pass may modify files.
# CUSTOM: A failing first pass now stops SIT for review.
uv run --locked prek run --all-files
if ($LASTEXITCODE -ne 0) {
    throw "Second repository hook pass failed or modified files. Review changes, stage them, and rerun SIT."
}

# ============================================================
# Run common chores.
# Ruff also formats Python code embedded in supported Markdown.
# ============================================================

# DO NOT RUN WITH FIX FLAGS
# uv run --locked ruff format .
# uv run --locked ruff check . --fix

uv run --locked ruff format --check .
if ($LASTEXITCODE -ne 0) {
    throw "Ruff formatting check failed."
}

uv run --locked ruff check .
if ($LASTEXITCODE -ne 0) {
    throw "Ruff lint check failed."
}

uv run --locked ty check
if ($LASTEXITCODE -ne 0) {
    throw "Python type checking failed."
}

uv run --locked python -m pytest
if ($LASTEXITCODE -ne 0) {
    throw "Python tests failed."
}

uv run --locked python -m zensical build
if ($LASTEXITCODE -ne 0) {
    throw "Documentation build failed."
}

# ============================================================
# Audit locked dependencies.
# Advisory only: findings are reported but do not modify uv.lock.
# ============================================================

uv audit --frozen
if ($LASTEXITCODE -ne 0) {
    Write-Warning "Dependency audit returned exit code $LASTEXITCODE. Review its output; this audit is advisory."
}

# ============================================================
# Complete the Pre-Freeze-03 checks.
# ============================================================

# CUSTOM: The kernel dependency was installed after uv sync above.
# Repository-wide Ruff and ty checks above include comparison/.
# The Freeze 03 check runs both comparison self-tests and verifies
# the freeze prerequisites, including Freeze 02 integrity.
# It does not establish Freeze 03.
.\freeze_03.ps1 -Check

Write-Host ""
Write-Host "All required checks passed. Review any warnings above."
Write-Host "The dependency lockfile was verified and was not updated."
