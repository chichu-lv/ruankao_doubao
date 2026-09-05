# End-to-end public download on real Windows, with no Git/Python/uv on PATH.
$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
$root = Split-Path -Parent $PSScriptRoot
$revision = $env:GITHUB_SHA
if ($revision -notmatch '^[0-9a-f]{40}$') { throw 'Run in CI with a published source commit.' }
$testRoot = Join-Path ([IO.Path]::GetTempPath()) ('ap-public-' + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $testRoot | Out-Null
$destination = Join-Path $testRoot '新用户 公开安装'
$launcher = Join-Path $testRoot 'install.ps1'
# Fetch the launcher anonymously too, instead of relying on the runner checkout.
Invoke-WebRequest -UseBasicParsing -Uri "https://raw.githubusercontent.com/chichu-lv/ruankao_doubao/$revision/scripts/install_public_windows.ps1" -OutFile $launcher
$originalPath = $env:PATH
try {
    $env:PATH = @($env:SystemRoot, (Join-Path $env:SystemRoot 'System32'), (Join-Path $env:SystemRoot 'System32\WindowsPowerShell\v1.0')) -join ';'
    foreach ($command in @('git', 'python', 'python3', 'uv')) {
        if (Get-Command $command -ErrorAction SilentlyContinue) { throw "Unexpected preinstalled tool: $command" }
    }
    $powershell = Join-Path $env:SystemRoot 'System32\WindowsPowerShell\v1.0\powershell.exe'
    & $powershell -NoProfile -ExecutionPolicy Bypass -File $launcher -Destination $destination -Revision $revision -FetchOnly
    if ($LASTEXITCODE -ne 0) { throw 'Public source download failed.' }
    if (Test-Path (Join-Path $destination '.git')) { throw 'Unexpected Git checkout.' }
    $receiptPath = Join-Path $destination 'dist\bootstrap\public-source.json'
    $before = Get-Content -Raw -Encoding UTF8 -LiteralPath $receiptPath
    if (($before | ConvertFrom-Json).source_commit -ne $revision) { throw 'Wrong source snapshot.' }
    # Full runtime download and all six health checks, using only downloaded code.
    & $powershell -NoProfile -ExecutionPolicy Bypass -File $launcher -Destination $destination -Revision $revision
    if ($LASTEXITCODE -ne 0) { throw 'Public installation failed.' }
    $bootstrap = Get-Content -Raw -Encoding UTF8 -LiteralPath (Join-Path $destination 'dist\bootstrap\local-bootstrap-result.json') | ConvertFrom-Json
    if ($bootstrap.status -notin @('PASS', 'PARTIAL') -or $bootstrap.healthchecks.Count -ne 6) { throw 'Incomplete local health checks.' }
    if (@($bootstrap.healthchecks | Where-Object { $_.returncode -ne 0 }).Count) { throw 'A health check failed.' }
    $manifest = Get-Content -Raw -Encoding UTF8 -LiteralPath (Join-Path $destination 'dist\doubao-skills\build-manifest.json') | ConvertFrom-Json
    $skills = @(Get-ChildItem -LiteralPath (Join-Path $destination 'dist\doubao-skills') -Filter '*.zip')
    if ($skills.Count -ne 9) { throw 'Nine skill ZIPs were not built.' }
    $sentinel = Join-Path $destination 'keep-user-file.txt'
    Set-Content -Encoding UTF8 -LiteralPath $sentinel -Value 'preserve-user-data'
    & $powershell -NoProfile -ExecutionPolicy Bypass -File $launcher -Destination $destination -Revision $revision -PrepareOnly
    if ($LASTEXITCODE -ne 0) { throw 'Resume failed.' }
    if ((Get-Content -Raw -Encoding UTF8 -LiteralPath $receiptPath) -ne $before) { throw 'Resume replaced source receipt.' }
    if ((Get-Content -Raw -Encoding UTF8 -LiteralPath $sentinel).Trim() -ne 'preserve-user-data') { throw 'User data changed.' }
    # Also exercise the actual user-facing default main URL, not only a pinned commit.
    $mainDestination = Join-Path $testRoot '默认 main 来源'
    & $powershell -NoProfile -ExecutionPolicy Bypass -File $launcher -Destination $mainDestination -FetchOnly
    if ($LASTEXITCODE -ne 0) { throw 'Default main source download failed.' }
    $mainReceipt = Get-Content -Raw -Encoding UTF8 -LiteralPath (Join-Path $mainDestination 'dist\bootstrap\public-source.json') | ConvertFrom-Json
    if ($mainReceipt.source_ref -ne 'main' -or $null -ne $mainReceipt.source_commit) { throw 'Default main provenance is incorrect.' }
    if (Test-Path (Join-Path $mainDestination '.git')) { throw 'Default main unexpectedly requires Git.' }
    $result = [ordered]@{status='PASS'; source_commit=$revision; source_kind='public_source_zip'; git_on_path=$false; python_on_path=$false;
        anonymous_download=$true; default_main_download=$true; chinese_space_path=$true; skill_count=$skills.Count; bootstrap=$bootstrap;
        repeat_preserves_source_and_user_file=$true; doubao_windows_gui='NOT_TESTED'; baidu_windows_client='NOT_TESTED'}
    $output = Join-Path $root 'dist\acceptance\windows-public-install.json'
    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $output) | Out-Null
    $result | ConvertTo-Json -Depth 10 | Set-Content -Encoding UTF8 -LiteralPath $output
    Write-Output ($result | ConvertTo-Json -Depth 10)
} finally {
    $env:PATH = $originalPath
}
