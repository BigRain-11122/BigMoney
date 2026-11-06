# FleetBridge.ps1 - keep the GROUP ROOT's Tools/ in sync with origin/main (2026-11-06).
#
# WHY (measured, not assumed):
#   Every Windows box has a FORKED group-repo checkout (local commits that are on no
#   remote ref), and the poke worker only does `git merge --ff-only`, so a push to
#   origin/main can never reach them. Consequence: every tool fix stalls on the master
#   and the fleet silently keeps running months-old code. No SSH / WinRM / SMB credentials
#   exist, so the only deterministic repo-delivered execution face is an already-ENABLED
#   product loop that pulls its own repo (MiniGameEngineTick on bm-c, Bigmoney-
#   IterationLoop on bm-b). This script lets that loop carry the code plane.
#
# WHAT (idempotent, repeatable, pushes nothing):
#   1. git fetch origin main in the group root
#   2. if the worktree Tools/ already equals origin/main's Tools/ -> exit silently
#   3. otherwise: keep local commits alive on a local salvage branch, then update ONLY
#      Tools/ to origin/main (no reset, no history rewrite, no generated state, no
#      commit, no push)
#   4. append one log line to %TEMP%
#
# SAFETY: Tools/ is master-owned code and nodes never write it, so overwriting it cannot
#   destroy node work. Everything is wrapped; any failure exits 0.
# NOTE: PURE ASCII on purpose - powershell.exe 5.1 decodes a BOM-less .ps1 as ANSI/GBK
#   and can swallow quote bytes after multibyte sequences.
param([string]$Repo = (Split-Path -Parent $PSScriptRoot))

$ErrorActionPreference = 'Continue'
$log = Join-Path $env:TEMP 'fluxgroup-fleet-bridge.log'

function FB-Log([string]$m) {
    try {
        if ((Get-Item $log -ErrorAction SilentlyContinue).Length -gt 512KB) {
            Set-Content -Path $log -Value ((Get-Date -Format s) + ' | rotated') -Encoding UTF8
        }
        Add-Content -Path $log -Value ((Get-Date -Format s) + ' | ' + $m) -Encoding UTF8
    } catch { }
}

# Resolve the group root: <root>/gaming/MiniGame -> two levels up.
# Fall back to known per-machine layouts; never guess beyond that list.
$root = $null
$cands = @(
    (Split-Path -Parent (Split-Path -Parent $Repo)),
    (Split-Path -Parent $Repo),
    'K:\Fluxgroup\FluxGroup',
    'C:\Fluxgroup\FluxGroup',
    'C:\Users\sjs20\Desktop\FluxGroup'
)
foreach ($c in $cands) {
    if ($c -and (Test-Path (Join-Path $c 'Tools\fleet-poke-worker.ps1'))) { $root = $c; break }
}
if (-not $root) { FB-Log 'skip: group root not found'; exit 0 }
if (-not (Test-Path (Join-Path $root '.git'))) { FB-Log ('skip: no .git at ' + $root); exit 0 }

try {
    $git = 'git'
    & $git -C $root fetch --quiet origin main 2>&1 | Out-Null
    $om = (& $git -C $root rev-parse --short origin/main 2>&1 | Select-Object -First 1)
    if (-not $om -or $om -notmatch '^[0-9a-f]{6,}') { FB-Log 'skip: origin/main unavailable'; exit 0 }

    # Already in sync? (worktree Tools/ == origin/main Tools/) -> nothing to do.
    & $git -C $root diff --quiet origin/main -- Tools 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) { exit 0 }

    $before = (& $git -C $root rev-parse --short HEAD 2>&1 | Select-Object -First 1)
    $branch = (& $git -C $root rev-parse --abbrev-ref HEAD 2>&1 | Select-Object -First 1)
    $fork = (& $git -C $root rev-list --left-right --count 'HEAD...origin/main' 2>&1 | Select-Object -First 1)
    FB-Log ('sync Tools/ <- ' + $om + ' head=' + $before + ' branch=' + $branch + ' fork=' + $fork)

    # Preserve local commits on a local-only branch (never pushed). Idempotent.
    $hasSalvage = (& $git -C $root rev-parse --verify --quiet salvage-auto-20261106 2>&1)
    if (-not $hasSalvage) { & $git -C $root branch salvage-auto-20261106 HEAD 2>&1 | Out-Null }

    & $git -C $root checkout origin/main -- Tools 2>&1 | Out-Null
    & $git -C $root reset -q -- Tools 2>&1 | Out-Null

    $wk = Join-Path $root 'Tools\fleet-poke-worker.ps1'
    $ok = $false
    if (Test-Path $wk) { $ok = [bool](Select-String -Path $wk -Pattern 'enable_tasks' -SimpleMatch -Quiet) }
    FB-Log ('done worker_has_enable=' + $ok + ' tools_at=' + $om)
    exit 0
} catch {
    FB-Log ('fail: ' + [string]$_.Exception.Message)
    exit 0
}