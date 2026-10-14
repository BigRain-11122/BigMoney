# r947 bm-b restore worker (ASCII-only per PS5.1 GBK pit law)
# Purpose: continue lazy-blob checkout of faces lost in 2026-10-14 git-loss incident.
# Survives round kills (launched detached). Idempotent: safe to re-run.
$ErrorActionPreference = 'Continue'
$bm = 'C:\Fluxgroup\FluxGroup\quant\bigmoney'
$log = "$bm\results\_r947bmb_restore_worker.log"
function W([string]$m) { Add-Content -Path $log -Value ("{0} {1}" -f (Get-Date -Format s), $m) -Encoding UTF8 }

W "worker start pid=$PID"
if (Test-Path "$bm\.git\index.lock") {
    $age = ((Get-Date) - (Get-Item "$bm\.git\index.lock").LastWriteTime).TotalSeconds
    if ($age -gt 120) { Remove-Item "$bm\.git\index.lock" -Force; W "stale index.lock removed (age ${age}s)" }
}

# Phase 1: faces, one face per checkout so each lazy-blob batch stays small
$faces = @('fleet','.gitignore','CODELY.md','HQ-FEEDBACK.md','docs','engine','firm','knowledge','legacy','live')
foreach ($f in $faces) {
    W "checkout face: $f"
    $p = Start-Process -FilePath git -ArgumentList 'checkout','HEAD','--',$f -WorkingDirectory $bm -PassThru -WindowStyle Hidden
    if (-not $p.WaitForExit(900000)) {
        W "FACE $f TIMEOUT-900s killing pid=$($p.Id)"
        Stop-Process -Id $p.Id -Force -ErrorAction SilentlyContinue
        Start-Sleep 2
        if (Test-Path "$bm\.git\index.lock") { Remove-Item "$bm\.git\index.lock" -Force; W "lock cleared after kill" }
        # one retry per face
        $p2 = Start-Process -FilePath git -ArgumentList 'checkout','HEAD','--',$f -WorkingDirectory $bm -PassThru -WindowStyle Hidden
        if (-not $p2.WaitForExit(900000)) { W "FACE $f retry timeout, giving up this run"; Stop-Process -Id $p2.Id -Force -ErrorAction SilentlyContinue; if (Test-Path "$bm\.git\index.lock"){Remove-Item "$bm\.git\index.lock" -Force} }
        else { W "FACE $f retry rc=$($p2.ExitCode)" }
    } else { W "FACE $f rc=$($p.ExitCode)" }
}

# Phase 2: status snapshot
$d = (git -C $bm status --porcelain | Select-String '^ D').Count
W "post-checkout D-count=$d (target: only pre-r834 historic deletions if any)"
W "worker done"
