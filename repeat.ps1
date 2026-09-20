# ============================================================
# find-text.ps1
# ============================================================

$pattern = "Finite conformance"
$extensions = @("*.cff", "*.json", "*.md", "*.toml")

$files = Get-ChildItem `
    -Path . `
    -Recurse `
    -File `
    -Include $extensions

$matches = $files | Select-String `
    -SimpleMatch `
    -Pattern $pattern `
    -Context 3,3

foreach ($match in $matches) {
    Write-Host ""
    Write-Host "=== $($match.Path):$($match.LineNumber) ==="
    $match.Context.PreContext
    Write-Host "> $($match.Line)"
    $match.Context.PostContext
}

exit 0
