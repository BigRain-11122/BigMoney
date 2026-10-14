# r949 bm-b restore worker v2 (ASCII-only per PS5.1 GBK pit law)
# v2 law compliance (r948 forensics addendum):
#  (1) tree-kill via taskkill /T (shim PID kill orphans the real git - r948 law)
#  (2) honest lock removal: -ErrorAction Stop + re-Test-Path verify (no silent 'cleared' lies)
#  (3) ssh fail-fast: ConnectTimeout + ServerAlive probes -> dead GFW-night stalls die <60s
#  (4) multi-pass retry loop with sleep windows (network self-heal), global 110min deadline
#  (5) per-face 600s cap; idempotent; detached (survives round/runner kills)
# NOTE: 'data' ADDED r949 late-finding: data/ IS tracked in HEAD (minute_feed/zt_pool forward
#       archives live in git = recoverable to r946 cutoff via checkout; zero clobber risk -
#       status shows no ' M'/untracked under data/, only ' D'). 'config' added: destroyed face
#       discovered via saturation_engine import crash (engine dead-by-config since incident).
$ErrorActionPreference = 'Continue'
$bm = 'C:\Fluxgroup\FluxGroup\quant\bigmoney'
$log = "$bm\results\_r949bmb_restore_worker_v2.log"
function W([string]$m) { Add-Content -Path $log -Value ("{0} {1}" -f (Get-Date -Format s), $m) -Encoding UTF8 }

$env:GIT_SSH_COMMAND = 'ssh -o ConnectTimeout=20 -o ServerAliveInterval=15 -o ServerAliveCountMax=2'

W "worker v2 start pid=$PID"
$deadline = (Get-Date).AddMinutes(110)
$faces = @('config','fleet','docs','engine','firm','knowledge','legacy','live','data')
$pending = @($faces)
$pass = 0
while ($pending.Count -gt 0 -and $pass -lt 6 -and ((Get-Date) -lt $deadline)) {
    $pass++
    W "pass $pass pending: $($pending -join ',')"
    $still = @()
    foreach ($f in $pending) {
        if ((Get-Date) -gt $deadline) { W "deadline hit, deferring: $($pending -join ',')"; break }
        W "checkout face: $f"
        $p = Start-Process -FilePath git -ArgumentList 'checkout','HEAD','--',$f -WorkingDirectory $bm -PassThru -WindowStyle Hidden
        if (-not $p.WaitForExit(600000)) {
            W "FACE $f TIMEOUT-600s tree-killing pid=$($p.Id)"
            & taskkill /PID $p.Id /T /F 2>&1 | Out-Null
            Start-Sleep 2
            $l = "$bm\.git\index.lock"
            if (Test-Path $l) {
                try { Remove-Item $l -Force -ErrorAction Stop } catch { W "LOCK REMOVE FAILED (honest): $($_.Exception.Message)" }
                if (Test-Path $l) { W "LOCK STILL PRESENT (honest) - aborting run to avoid rc128 cascade"; W "worker v2 abort"; exit 1 }
                W "index.lock removed+verified"
            }
            $still += $f
        } elseif ($p.ExitCode -eq 0) {
            W "FACE $f rc=0 OK"
        } else {
            W "FACE $f rc=$($p.ExitCode) (retry queued)"
            $still += $f
        }
    }
    $pending = @($still | Select-Object -Unique)
    if (($pending.Count -gt 0) -and ($pass -lt 6) -and ((Get-Date) -lt $deadline)) { W "sleep 180s (network heal window)"; Start-Sleep 180 }
}
$d = (git -C $bm status --porcelain | Select-String '^ D').Count
W "final D-count=$d"
if ($pending.Count -eq 0) { W "ALL FACES RESTORED" } else { W "worker v2 done UNRESOLVED: $($pending -join ',')" }
W "worker v2 done"
