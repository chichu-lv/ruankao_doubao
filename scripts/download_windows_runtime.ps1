# Git installations only. The complete offline ZIP already contains these files.
# Uses only Windows PowerShell and official Python/PyPI downloads, not system Python.
$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
$projectRoot = Split-Path -Parent $PSScriptRoot
$manifest = Get-Content -Raw -Encoding UTF8 -LiteralPath (Join-Path $projectRoot 'deployment\offline\windows-runtime-v1.json') | ConvertFrom-Json
$vendor = Join-Path $projectRoot 'vendor'
$wheelhouse = Join-Path $vendor 'wheels-windows'
New-Item -ItemType Directory -Force -Path $wheelhouse | Out-Null
$archive = Join-Path $vendor 'python-windows-amd64.zip'
if (-not (Test-Path -LiteralPath $archive)) {
    Invoke-WebRequest -UseBasicParsing -Uri $manifest.python_url -OutFile "$archive.download"
    Move-Item -LiteralPath "$archive.download" -Destination $archive
}
foreach ($wheel in $manifest.wheels) {
    $target = Join-Path $wheelhouse $wheel.filename
    if (Test-Path -LiteralPath $target) { continue }
    $release = Invoke-RestMethod -Uri "https://pypi.org/pypi/$($wheel.package)/$($wheel.version)/json"
    $match = @($release.urls | Where-Object { $_.filename -eq $wheel.filename })
    if ($match.Count -ne 1) { throw "Required Windows wheel not found: $($wheel.filename)" }
    Invoke-WebRequest -UseBasicParsing -Uri $match[0].url -OutFile "$target.download"
    Move-Item -LiteralPath "$target.download" -Destination $target
}
Write-Output 'Windows runtime downloaded. Next: scripts\start_windows.cmd'
