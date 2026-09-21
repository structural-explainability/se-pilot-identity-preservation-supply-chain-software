$ErrorActionPreference = "Stop"

$root = "validation/cyclonedx-cli-reverse-sweep"
$versions = @(
    "0.31.0",
    "0.32.0"
)

$outputDir = Join-Path $root "validation-checks"
New-Item -ItemType Directory -Force -Path $outputDir | Out-Null

$summary = @()

foreach ($version in $versions) {
    $target = Join-Path $root "artifacts/$version/target.spdx.json"
    $log = Join-Path $outputDir "spdx-validator-$version.txt"

    Write-Host "Validating $version ..."

    $lines = & uvx --from spdx-tools pyspdxtools -i $target 2>&1
    $exitCode = $LASTEXITCODE

    $lines | Set-Content -Path $log -Encoding utf8

    $counts = [ordered]@{
        version                         = $version
        exit_code                       = $exitCode
        invalid_external_document_ref   = 0
        invalid_internal_spdx_id        = 0
        missing_external_document_ref   = 0
        license_expression              = 0
        other_validation_issue          = 0
    }

    foreach ($line in $lines) {
        $text = [string]$line

        if ($text -match '^ERROR:root:The document is invalid') {
            continue
        }

        if (
            $text -match '^the external document reference part of spdx_id must only contain'
        ) {
            $counts.invalid_external_document_ref++
            continue
        }

        if (
            $text -match '^the internal SPDX id part of spdx_id must only contain'
        ) {
            $counts.invalid_internal_spdx_id++
            continue
        }

        if (
            $text -match '^did not find the external document reference'
        ) {
            $counts.missing_external_document_ref++
            continue
        }

        if (
            $text -match '^A license exception symbol can only be used'
        ) {
            $counts.license_expression++
            continue
        }

        if ($text.Trim()) {
            $counts.other_validation_issue++
        }
    }

    $summary += [pscustomobject]$counts
}

$summary |
    Format-Table -AutoSize

$summary |
    ConvertTo-Json |
    Set-Content `
        -Path (Join-Path $outputDir "spdx-validator-summary.json") `
        -Encoding utf8
