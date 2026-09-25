#Requires -Version 7.0

<#
============================================================
sit.ps1 (CUSTOM-FREEZE-ALL-PY-SRC-REPOS)
============================================================
Updated: 2026-09-25

Situate the locked project environment, lint, test, and build docs.
For Python tooling repos only.

This script does NOT update uv.lock.
Dependency upgrades must be performed deliberately outside SIT.

Run with:
.\sit.ps1
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# ============================================================
# Precheck: pyproject.toml must use [dependency-groups], not the
# old [project.optional-dependencies].
# ============================================================

if (Test-Path "pyproject.toml") {
    $pyproject = Get-Content "pyproject.toml" -Raw

    if ($pyproject -match '(?m)^\[project\.optional-dependencies\]') {
        Write-Host ""
        Write-Host "ERROR: pyproject.toml uses the old [project.optional-dependencies] table." -ForegroundColor Red
        Write-Host ""
        Write-Host "This repo has not been migrated to [dependency-groups]." -ForegroundColor Yellow
        Write-Host ""
        Write-Host "FIX: open pyproject.toml and rename this one line:" -ForegroundColor Cyan
        Write-Host "    [project.optional-dependencies]   ->   [dependency-groups]" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Then run .\sit.ps1 again." -ForegroundColor Cyan
        Write-Host ""
        exit 1
    }
}

# ============================================================
# Verify and synchronize the locked Python environment.
#
# SIT must not update uv.lock.
# ============================================================

uv lock --check
uv sync --locked

# ============================================================
# Update and run repository hooks.
# ============================================================

uv run --locked prek install -f
uv run --locked prek update --freeze --cooldown-days 7

# ============================================================
# Audit/fix GitHub configuration when GitHub CLI is available.
# ============================================================

if (Get-Command gh -ErrorAction SilentlyContinue) {
    gh auth status *> $null

    if ($LASTEXITCODE -eq 0) {
        uv run --locked zizmor --gh-token (gh auth token) --fix=all .github/
    }
}

# ============================================================
# Stage generated or automatically corrected files.
# ============================================================

git add -A

# ============================================================
# Run repository checks.
# ============================================================

uv run --locked prek run --all-files
# Repeat because the first pass may modify files.
uv run --locked prek run --all-files

# ============================================================
# Run common chores.
# Ruff also formats Python code embedded in supported Markdown.
# ============================================================

uv run --locked ruff format .
uv run --locked ruff check . --fix
uv run --locked ty check
uv run --locked python -m pytest
uv run --locked python -m zensical build

# ============================================================
# Audit locked dependencies.
# Advisory only: findings are reported but do not modify uv.lock.
# ============================================================

uv audit --frozen

Write-Host ""
Write-Host "All commands executed successfully. Review any warnings above."
Write-Host "The dependency lockfile was verified and was not updated."
