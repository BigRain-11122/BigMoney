# FleetBridge.ps1 - one-shot fleet repair carried by a product lane (2026-11-06, master).
#
# WHY this lives in a product repo:
#   All three Windows boxes have FORKED group-repo checkouts (local commits that are on
#   no remote ref), and the poke worker only does `git merge --ff-only`, so a push to
#   origin/main can never reach them. No SSH / WinRM / SMB credentials exist, so the only
#   deterministic, repo-delivered execution face is an already-ENABLED product loop that
#   pulls its own repo (MiniGameEngineTick on bm-c, Bigmoney-IterationLoop on bm-b).
#
# WHAT it does (one thing only, reversible, pushes nothing):
#   1. fetch origin main in the group root repo
#   2. keep local commits alive on a local salvage branch
#   3. update ONLY the root repo's Tools/ directory to origin/main content
#      (no reset, no history rewrite, no generated-state files, no commit, no push)
#   4. write a receipt to %TEMP% and a marker, then stay silent forever (runs once)
#
# SAFETY: everything is wrapped; any failure exits 0 and never disturbs the host lane.
# NOTE: this file is PURE ASCII on purpose - powershell.exe 5.1 decodes BOM-less .ps1 as
#       ANSI/GBK and can swallow quote bytes after multibyte sequences.
param([string]$Repo = (Split-Path -Parent $PSScriptRoot))

$ErrorActionPreference = 'Continue'
$log = Join-Path $env:TEMP 'fluxgroup-fleet-bridge.log'
$marker = Join-Path $env:TEMP 'fluxgroup-fleet-bridge.done'

function FB-Log([string]$m) {
    try { Add-Content -Path $log -Value ((Get-Date -Format s) + ' | ' + $m) -Encoding UTF8 } catch { }
}

if (Test-Path $marker) { exit 0 }

# Resolve the group root: gaming/MiniGame -> group root is two levels up.
# Fall back to known absolute layouts per machine; never guess beyond that.
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
if (-not $root) { FB-Log 'skip: group root not found'; Set-Content -Path $marker -Value 'no-root' -Encoding UTF8; exit 0 }
if (-not (Test-Path (Join-Path $root '.git'))) { FB-Log ('skip: no .git at ' + $root); exit 0 }

try {
    $git = 'git'
    $before = (& $git -C $root rev-parse --short HEAD 2>&1 | Select-Object -First 1)
    $branch = (& $git -C $root rev-parse --abbrev-ref HEAD 2>&1 | Select-Object -First 1)
    FB-Log ('start root=' + $root + ' head=' + $before + ' branch=' + $branch)

    & $git -C $root fetch --quiet origin main 2>&1 | Out-Null
    $om = (& $git -C $root rev-parse --short origin/main 2>&1 | Select-Object -First 1)
    if (-not $om -or $om -notmatch '^[0-9a-f]{6,}') { FB-Log 'skip: origin/main unavailable'; exit 0 }

    $fork = (& $git -C $root rev-list --left-right --count 'HEAD...origin/main' 2>&1 | Select-Object -First 1)
    FB-Log ('fork(ahead/behind)=' + $fork + ' origin_main=' + $om)

    # Preserve local commits on a local-only branch (never pushed).
    & $git -C $root branch -f salvage-auto-20261106 HEAD 2>&1 | Out-Null

    # Only Tools/: master-owned code, nodes never write it.
    & $git -C $root checkout origin/main -- Tools 2>&1 | Out-Null
    & $git -C $root reset -q -- Tools 2>&1 | Out-Null

    $wk = Join-Path $root 'Tools\fleet-poke-worker.ps1'
    $ok = $false
    if (Test-Path $wk) { $ok = [bool](Select-String -Path $wk -Pattern 'enable_tasks' -SimpleMatch -Quiet) }
    $rosterOk = [bool](Select-String -Path (Join-Path $root 'Tools\fleet-nodes.json') -Pattern 'enable_tasks' -SimpleMatch -Quiet)
    FB-Log ('done worker_has_enable=' + $ok + ' roster_has_enable=' + $rosterOk + ' tools_at=' + $om)
    Set-Content -Path $marker -Value ('done ' + (Get-Date -Format s) + ' ' + $root) -Encoding UTF8
    exit 0
} catch {
    FB-Log ('fail: ' + [string]$_.Exception.Message)
    exit 0
}