# ============================================================
# install_generalization_tools.ps1
# ============================================================
# Install the exact repo-local converter toolchain used to
# prepare Freeze 02.
#
# Nothing is installed globally and nothing is taken from PATH.
#
# Installed under:
#   bin/generalization/
#
# These files are later hashed and recorded in
# generalization/05-transformations.toml.

$ErrorActionPreference = "Stop"

# ============================================================
# PINNED TOOLCHAIN
# ============================================================

$SyftVersion = "1.52.0"
$SbomConvertVersion = "0.0.8"
$Cdx2SpdxVersion = "0.1.5"
$JavaVersion = "21.0.12.1+1"
$SbomUtilityVersion = "0.19.2"

# ============================================================
# TOOL SOURCES
# ============================================================

$GitHubApiBaseUrl = "https://api.github.com/repos"
$MavenCentralBaseUrl = "https://repo1.maven.org/maven2"
$AdoptiumApiBaseUrl = "https://api.adoptium.net/v3/binary/version"

$SyftRepository = "anchore/syft"
$SbomConvertRepository = "protobom/sbom-convert"
$SbomUtilityRepository = "CycloneDX/sbom-utility"

$Cdx2SpdxMavenGroupPath = "org/spdx/cdx2spdx"

$DownloadUserAgent = "se-pilot-generalization-tool-installer"

# ============================================================
# LOCAL TOOLCHAIN PATHS
# ============================================================

$Root = (Get-Location).Path
$ToolDir = Join-Path $Root "bin\generalization"
$TempDir = Join-Path $ToolDir "_download"

$SyftExe = Join-Path $ToolDir "syft.exe"
$SbomConvertExe = Join-Path $ToolDir "sbom-convert.exe"
$Cdx2SpdxJar = Join-Path $ToolDir "cdx2spdx.jar"
$SbomUtilityExe = Join-Path $ToolDir "sbom-utility.exe"
$JavaDir = Join-Path $ToolDir "jdk-$JavaVersion"
$JavaExe = Join-Path $JavaDir "bin\java.exe"

if (-not (Test-Path ".git")) {
    throw "Run this script from the repository root."
}

# Rebuild the repo-local toolchain from the pinned versions.
if (Test-Path $ToolDir) {
    Remove-Item -Recurse -Force $ToolDir
}

New-Item -ItemType Directory -Force $ToolDir | Out-Null
New-Item -ItemType Directory -Force $TempDir | Out-Null


function Get-GitHubReleaseAsset {
    param (
        [Parameter(Mandatory)]
        [string] $Repository,

        [Parameter(Mandatory)]
        [string] $Tag,

        [Parameter(Mandatory)]
        [string] $AssetPattern,

        [Parameter(Mandatory)]
        [string] $Destination
    )

    $Headers = @{
        "User-Agent" = $DownloadUserAgent
    }

    $ReleaseUrl = "$GitHubApiBaseUrl/$Repository/releases/tags/$Tag"

    $Release = Invoke-RestMethod `
        -Uri $ReleaseUrl `
        -Headers $Headers

    $Matches = @(
        $Release.assets |
            Where-Object { $_.name -match $AssetPattern }
    )

    if ($Matches.Count -ne 1) {
        $Available = ($Release.assets.name | Sort-Object) -join "`n  "

        throw @"
Expected exactly one release asset for:
  repository: $Repository
  tag:        $Tag
  pattern:    $AssetPattern

Found: $($Matches.Count)

Available assets:
  $Available
"@
    }

    Write-Host "download: $($Matches[0].name)"

    Invoke-WebRequest `
        -Uri $Matches[0].browser_download_url `
        -OutFile $Destination
}


function Expand-ToolArchive {
    param (
        [Parameter(Mandatory)]
        [string] $Archive,

        [Parameter(Mandatory)]
        [string] $Destination
    )

    New-Item -ItemType Directory -Force $Destination | Out-Null

    if ($Archive.EndsWith(".zip")) {
        Expand-Archive `
            -Path $Archive `
            -DestinationPath $Destination `
            -Force
        return
    }

    if ($Archive.EndsWith(".tar.gz")) {
        tar -xzf $Archive -C $Destination

        if ($LASTEXITCODE -ne 0) {
            throw "tar extraction failed: $Archive"
        }

        return
    }

    throw "Unsupported archive type: $Archive"
}


function Copy-SingleExecutable {
    param (
        [Parameter(Mandatory)]
        [string] $SearchRoot,

        [Parameter(Mandatory)]
        [string] $ExecutableName,

        [Parameter(Mandatory)]
        [string] $Destination
    )

    $Matches = @(
        Get-ChildItem `
            -Path $SearchRoot `
            -Recurse `
            -File `
            -Filter $ExecutableName
    )

    if ($Matches.Count -ne 1) {
        throw (
            "Expected exactly one $ExecutableName under $SearchRoot; " +
            "found $($Matches.Count)"
        )
    }

    Copy-Item `
        -Path $Matches[0].FullName `
        -Destination $Destination
}


# ============================================================
# Syft
# ============================================================

$SyftArchive = Join-Path $TempDir "syft.zip"
$SyftExtract = Join-Path $TempDir "syft"

Get-GitHubReleaseAsset `
    -Repository $SyftRepository `
    -Tag "v$SyftVersion" `
    -AssetPattern "^syft_$([regex]::Escape($SyftVersion))_windows_amd64\.zip$" `
    -Destination $SyftArchive

Expand-ToolArchive `
    -Archive $SyftArchive `
    -Destination $SyftExtract

Copy-SingleExecutable `
    -SearchRoot $SyftExtract `
    -ExecutableName "syft.exe" `
    -Destination $SyftExe


# ============================================================
# Protobom sbom-convert
# ============================================================

$SbomArchive = Join-Path $TempDir "sbom-convert-archive"
$SbomExtract = Join-Path $TempDir "sbom-convert"

$Headers = @{
    "User-Agent" = $DownloadUserAgent
}

$SbomRelease = Invoke-RestMethod `
    -Uri "$GitHubApiBaseUrl/$SbomConvertRepository/releases/tags/v$SbomConvertVersion" `
    -Headers $Headers

$SbomAssets = @(
    $SbomRelease.assets |
        Where-Object {
            $_.name -match "(?i)windows" -and
            $_.name -match "(amd64|x86_64)" -and
            (
                $_.name.EndsWith(".zip") -or
                $_.name.EndsWith(".tar.gz")
            )
        }
)

if ($SbomAssets.Count -ne 1) {
    $Available = ($SbomRelease.assets.name | Sort-Object) -join "`n  "

    throw @"
Expected exactly one Windows x64 sbom-convert archive.

Found: $($SbomAssets.Count)

Available assets:
  $Available
"@
}

$SbomArchive = Join-Path $TempDir $SbomAssets[0].name

Write-Host "download: $($SbomAssets[0].name)"

Invoke-WebRequest `
    -Uri $SbomAssets[0].browser_download_url `
    -OutFile $SbomArchive

Expand-ToolArchive `
    -Archive $SbomArchive `
    -Destination $SbomExtract

Copy-SingleExecutable `
    -SearchRoot $SbomExtract `
    -ExecutableName "sbom-convert.exe" `
    -Destination $SbomConvertExe

# ============================================================
# CycloneDX sbom-utility
# ============================================================

$SbomUtilityArchive = Join-Path $TempDir "sbom-utility.zip"
$SbomUtilityExtract = Join-Path $TempDir "sbom-utility"

Get-GitHubReleaseAsset `
    -Repository $SbomUtilityRepository `
    -Tag "v$SbomUtilityVersion" `
    -AssetPattern "^sbom-utility-v$([regex]::Escape($SbomUtilityVersion))-windows-amd64\.zip$" `
    -Destination $SbomUtilityArchive

Expand-ToolArchive `
    -Archive $SbomUtilityArchive `
    -Destination $SbomUtilityExtract

Copy-SingleExecutable `
    -SearchRoot $SbomUtilityExtract `
    -ExecutableName "sbom-utility.exe" `
    -Destination $SbomUtilityExe

# ============================================================
# SPDX cdx2spdx
# ============================================================

$Cdx2SpdxUrl = (
    "$MavenCentralBaseUrl/$Cdx2SpdxMavenGroupPath/" +
    "$Cdx2SpdxVersion/" +
    "cdx2spdx-$Cdx2SpdxVersion-jar-with-dependencies.jar"
)

Write-Host "download: cdx2spdx-$Cdx2SpdxVersion-jar-with-dependencies.jar"

Invoke-WebRequest `
    -Uri $Cdx2SpdxUrl `
    -OutFile $Cdx2SpdxJar


# ============================================================
# Portable Eclipse Temurin JDK
# ============================================================

$JavaArchive = Join-Path $TempDir "temurin-jdk.zip"
$JavaExtract = Join-Path $TempDir "temurin-jdk"

$EncodedJavaVersion = $JavaVersion.Replace("+", "%2B")

$JavaUrl = (
    "$AdoptiumApiBaseUrl/" +
    "jdk-$EncodedJavaVersion/windows/x64/jdk/hotspot/normal/adoptium"
)

Write-Host "download: Eclipse Temurin JDK $JavaVersion"

Invoke-WebRequest `
    -Uri $JavaUrl `
    -OutFile $JavaArchive

Expand-Archive `
    -Path $JavaArchive `
    -DestinationPath $JavaExtract `
    -Force

$ExtractedJdk = @(
    Get-ChildItem $JavaExtract -Directory
)

if ($ExtractedJdk.Count -ne 1) {
    throw (
        "Expected exactly one extracted JDK directory; " +
        "found $($ExtractedJdk.Count)"
    )
}

Move-Item `
    -Path $ExtractedJdk[0].FullName `
    -Destination $JavaDir

if (-not (Test-Path $JavaExe)) {
    throw "Portable Java executable not found: $JavaExe"
}


# ============================================================
# Cleanup
# ============================================================

Remove-Item -Recurse -Force $TempDir


# ============================================================
# Verification
# ============================================================

Write-Host ""
Write-Host "Installed generalization toolchain:"
Write-Host ""

Get-FileHash $SyftExe -Algorithm SHA256 |
    Select-Object Path, Hash |
    Format-Table -AutoSize

Get-FileHash $SbomConvertExe -Algorithm SHA256 |
    Select-Object Path, Hash |
    Format-Table -AutoSize

Get-FileHash $SbomUtilityExe -Algorithm SHA256 |
    Select-Object Path, Hash |
    Format-Table -AutoSize

Get-FileHash $Cdx2SpdxJar -Algorithm SHA256 |
    Select-Object Path, Hash |
    Format-Table -AutoSize

Get-FileHash $JavaExe -Algorithm SHA256 |
    Select-Object Path, Hash |
    Format-Table -AutoSize

Write-Host ""
Write-Host "Versions:"
Write-Host "  Syft:         $SyftVersion"
Write-Host "  sbom-convert: $SbomConvertVersion"
Write-Host "  sbom-utility: $SbomUtilityVersion"
Write-Host "  cdx2spdx:     $Cdx2SpdxVersion"
Write-Host "  Java:         $JavaVersion"

Write-Host ""
Write-Host "Toolchain ready:"
Write-Host "  bin\generalization\syft.exe"
Write-Host "  bin\generalization\sbom-convert.exe"
Write-Host "  bin\generalization\sbom-utility.exe"
Write-Host "  bin\generalization\cdx2spdx.jar"
Write-Host "  bin\generalization\jdk-$JavaVersion\bin\java.exe"
