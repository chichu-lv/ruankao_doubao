$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $projectRoot
$runtime = Join-Path $projectRoot '.runtime\python'
$python = Join-Path $runtime 'python.exe'
if (-not (Test-Path -LiteralPath $python)) {
    New-Item -ItemType Directory -Force -Path $runtime | Out-Null
    Expand-Archive -LiteralPath (Join-Path $projectRoot 'vendor\python-windows-amd64.zip') -DestinationPath $runtime -Force
}
$env:PYTHONUTF8 = '1'
& $python -X utf8 scripts/bootstrap_local.py --offline @args
exit $LASTEXITCODE
