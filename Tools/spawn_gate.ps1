# Cloud session spawn-gate preflight -- C-20261015-03 sec.3 spec
# (O-20261015-1800 concurrency cap v1.0 + O-20261015-1834 hard deadline
# 24:00 enforcement). Counts live codely.exe bodies before any wrapper
# ignites a new cloud LLM session; >= $Cap -> DEFER + one ledger row
# (next scheduled grid slot retries automatically -- no retry logic here).
# FAIL-OPEN BY LAW: probe explosion = GO (never blocks the production
# line). CEO interactive window / direct-order fast lane is exempt at the
# CALLER's discretion (this gate is for autonomous-lane wrappers only).
# Pure ASCII (iteration_loop.ps1 ENCODING RULE family).
# Selftest lanes: -ProbeOnly reports and mutates nothing; -Cap 99 forces
# the GO branch; -Cap 0 + -Ledger <selftest path> forces the DEFER branch
# without touching the production ledger.
param(
    [int]$Cap = 2,
    [switch]$ProbeOnly,
    [string]$Lane = 'bigmoney-loop',
    [string]$Ledger = ''
)
$ErrorActionPreference = 'Continue'
if (-not $Ledger) { $Ledger = Join-Path (Split-Path -Parent $PSScriptRoot) 'results\cloud_cap_ledger.jsonl' }
$live = -1
try {
    $live = @(Get-CimInstance Win32_Process -Filter "Name='codely.exe'" -ErrorAction Stop).Count
} catch {
    Write-Output "SPAWN-GATE GO live=probe-fault fail-open lane=$Lane ($($_.Exception.Message))"
    exit 0
}
if ($ProbeOnly) { Write-Output "SPAWN-GATE PROBE live=$live cap=$Cap lane=$Lane"; exit 0 }
if ($live -lt $Cap) {
    Write-Output "SPAWN-GATE GO live=$live cap=$Cap lane=$Lane"
    exit 0
}
try {
    $dir = Split-Path -Parent $Ledger
    if ($dir -and -not (Test-Path $dir)) { New-Item -ItemType Directory -Force $dir | Out-Null }
    Add-Content -Path $Ledger -Value "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') | CLOUD_CAP_DEFER live=$live cap=$Cap lane=$Lane" -Encoding UTF8
} catch { Write-Output "SPAWN-GATE DEFER ledger-append fault (logged to stdout only) live=$live" }
Write-Output "SPAWN-GATE DEFER live=$live cap=$Cap lane=$Lane (ledger row appended)"
exit 3
