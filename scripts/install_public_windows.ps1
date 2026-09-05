# Public-source installation using only Windows PowerShell. No Git or GitHub login.
[CmdletBinding()]
param(
    [string]$Destination = (Join-Path $env:LOCALAPPDATA 'ArchitectPass'),
    [ValidatePattern('^(main|[0-9a-f]{40})$')][string]$Revision = 'main',
    [switch]$FetchOnly,
    [switch]$PrepareOnly
)
$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
$repository = 'https://github.com/chichu-lv/ruankao_doubao'
$destinationPath = [IO.Path]::GetFullPath($Destination)
$receiptPath = Join-Path $destinationPath 'dist\bootstrap\public-source.json'
$required = @('README.md', 'VERSION', 'pyproject.toml', 'scripts\start_windows.ps1',
              'scripts\download_windows_runtime.ps1', 'deployment\doubao\bootstrap-v1.md')
if (Test-Path -LiteralPath $destinationPath) {
    if (-not (Test-Path -LiteralPath $receiptPath -PathType Leaf)) {
        throw "Destination already exists without an installation receipt. Choose a new empty destination; existing files were not changed: $destinationPath"
    }
    $receipt = Get-Content -Raw -Encoding UTF8 -LiteralPath $receiptPath | ConvertFrom-Json
    if ($receipt.repository -ne $repository -or $receipt.source_ref -ne $Revision) {
        throw 'Existing installation belongs to another source/ref. Use a new destination; this command does not overwrite or upgrade it.'
    }
} else {
    New-Item -ItemType Directory -Path $destinationPath | Out-Null
    $downloadRoot = Join-Path $destinationPath '.install-download'
    New-Item -ItemType Directory -Path $downloadRoot | Out-Null
    $sourceUrl = if ($Revision -eq 'main') {
        'https://codeload.github.com/chichu-lv/ruankao_doubao/zip/refs/heads/main'
    } else {
        "https://codeload.github.com/chichu-lv/ruankao_doubao/zip/$Revision"
    }
    $archive = Join-Path $downloadRoot 'source.zip'
    Invoke-WebRequest -UseBasicParsing -Uri $sourceUrl -OutFile $archive
    $expanded = Join-Path $downloadRoot 'expanded'
    Expand-Archive -LiteralPath $archive -DestinationPath $expanded
    $roots = @(Get-ChildItem -LiteralPath $expanded -Directory)
    if ($roots.Count -ne 1) { throw 'Expected exactly one project directory in the source ZIP.' }
    foreach ($relative in $required) {
        if (-not (Test-Path -LiteralPath (Join-Path $roots[0].FullName $relative) -PathType Leaf)) {
            throw "Source archive is missing a required file: $relative"
        }
    }
    Get-ChildItem -LiteralPath $roots[0].FullName -Force | Move-Item -Destination $destinationPath
    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $receiptPath) | Out-Null
    $receipt = [ordered]@{
        schema_version = 1; repository = $repository; source_ref = $Revision
        source_url = $sourceUrl; source_kind = 'public_source_zip'
        source_commit = $(if ($Revision -eq 'main') { $null } else { $Revision })
        installed_version = (Get-Content -Raw -LiteralPath (Join-Path $destinationPath 'VERSION')).Trim()
        downloaded_at = [DateTimeOffset]::UtcNow.ToString('o')
        note = 'Source receipt, not a Doubao deployment result. Re-running resumes this snapshot; it does not update or overwrite user state.'
    }
    $receipt | ConvertTo-Json | Set-Content -Encoding UTF8 -LiteralPath $receiptPath
}
foreach ($relative in $required) {
    if (-not (Test-Path -LiteralPath (Join-Path $destinationPath $relative) -PathType Leaf)) {
        throw "Installation source is incomplete: $relative"
    }
}
Write-Output "PROJECT_ROOT=$destinationPath"
Write-Output "SOURCE_RECEIPT=$receiptPath"
if ($FetchOnly) {
    Write-Output 'SOURCE_READY: read README.md and deployment/doubao/bootstrap-v1.md before deployment.'
    exit 0
}
$powershell = Join-Path $env:SystemRoot 'System32\WindowsPowerShell\v1.0\powershell.exe'
& $powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $destinationPath 'scripts\download_windows_runtime.ps1')
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
$arguments = @('-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', (Join-Path $destinationPath 'scripts\start_windows.ps1'))
if ($PrepareOnly) { $arguments += '--prepare-only' }
& $powershell @arguments
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
Write-Output 'LOCAL_RUNTIME_READY: continue the Doubao bootstrap for skills, accounts, materials and state. Local runtime success is not full deployment success.'
exit 0
