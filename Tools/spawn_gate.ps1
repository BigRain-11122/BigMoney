# Cloud session spawn-gate preflight -- C-20261015-03 sec.3 spec
# (O-20261015-1800 concurrency cap v1.0 + O-20261015-1834 hard deadline
# 24:00 enforcement). Counts live codely.exe bodies before any wrapper
# ignites a new cloud LLM session; >= $Cap -> DEFER + one ledger row
# (next scheduled grid slot retries automatically -- no retry logic here).
# FAIL-OPEN BY LAW: probe explosion = GO (never blocks the production
# line). CEO interactive window / direct-order fast lane is exempt at the
# CALLER's discretion (this gate is for autonomous-lane wrappers only).
# F-20261017-01 fix 2 (2026-10-18 r1089 bm-c, D-20261018-01 assigned
# BigMoney self-fix): AGE FILTER -- headless -p faces older than
# $ZombieAgeMinutes (default = iteration_loop round budget 240min x2) are
# HUNG, not workload: excluded from the cap and reported as zombies
# (2026-10-17 root cause: timeout-surviving faces ate the cap and starved
# the lane ~3h; cap slots stay with real live rounds).
# Pure ASCII (iteration_loop.ps1 ENCODING RULE family).
# Selftest lanes: -ProbeOnly reports and mutates nothing; -Cap 99 forces
# the GO branch; -Cap 0 + -Ledger <selftest path> forces the DEFER branch
# without touching the production ledger.
param(
    [int]$Cap = 2,
    [int]$ZombieAgeMinutes = 480,
    [switch]$ProbeOnly,
    [string]$Lane = 'bigmoney-loop',
    [string]$Ledger = ''
)
$ErrorActionPreference = 'Continue'
if (-not $Ledger) { $Ledger = Join-Path (Split-Path -Parent $PSScriptRoot) 'results\cloud_cap_ledger.jsonl' }
$live = -1
$zombies = 0
try {
    # C-20261016-05 exemption fix: count AUTONOMOUS faces only (headless
    # prompt rounds, cmdline carries ' -p "'). Interactive Cowork windows
    # (--experimental-acp) are exempt per O-20261015-1800 sec.2; counting
    # them starved every loop round while two chat windows were open
    # (live=5 with 4 interactive, 10-16 23:35-00:45 all-round defer).
    $all = @(Get-CimInstance Win32_Process -Filter "Name='codely.exe'" -ErrorAction Stop)
    $faces = @($all | Where-Object { $_.CommandLine -match ' -p "' })
    $zombies = @($faces | Where-Object { $_.CreationDate -and ((Get-Date) - $_.CreationDate).TotalMinutes -gt $ZombieAgeMinutes }).Count
    $live = $faces.Count - $zombies
} catch {
    Write-Output "SPAWN-GATE GO live=probe-fault fail-open lane=$Lane ($($_.Exception.Message))"
    exit 0
}
if ($ProbeOnly) { Write-Output "SPAWN-GATE PROBE live=$live cap=$Cap zombies=$zombies lane=$Lane"; exit 0 }
if ($live -lt $Cap) {
    if ($zombies -gt 0) { Write-Output "SPAWN-GATE GO live=$live cap=$Cap zombies=$zombies lane=$Lane (F-20261017-01 age filter: hung faces excluded from cap)" }
    else { Write-Output "SPAWN-GATE GO live=$live cap=$Cap lane=$Lane" }
    exit 0
}
try {
    $dir = Split-Path -Parent $Ledger
    if ($dir -and -not (Test-Path $dir)) { New-Item -ItemType Directory -Force $dir | Out-Null }
    Add-Content -Path $Ledger -Value "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') | CLOUD_CAP_DEFER live=$live cap=$Cap zombies=$zombies lane=$Lane" -Encoding UTF8
} catch { Write-Output "SPAWN-GATE DEFER ledger-append fault (logged to stdout only) live=$live" }
Write-Output "SPAWN-GATE DEFER live=$live cap=$Cap zombies=$zombies lane=$Lane (ledger row appended)"
exit 3
