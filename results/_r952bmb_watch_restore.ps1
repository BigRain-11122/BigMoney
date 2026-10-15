# r952 bm-b restore watcher v3 (ASCII-only per PS5.1 GBK pit law)
# Mission: (1) wait for orphan push (r951 C2 payload -> machine/bm-b-r951) to finish
#          (2) then run worker v2 (idempotent multi-pass checkout of 9 faces)
#          (3) write end-state marker for next round consumption
# Detached process: survives runner kills. No commit, no push (next round closes git bookkeeping
# once lazy-fetch of the full blob set completes and the repo warms up).
$ErrorActionPreference = 'Continue'
$bm = 'C:\Fluxgroup\FluxGroup\quant\bigmoney'
$log = "$bm\results\_r952bmb_watch_restore.log"
$v2log = "$bm\results\_r949bmb_restore_worker_v2.log"
function W([string]$m) { Add-Content -Path $log -Value ("{0} {1}" -f (Get-Date -Format s), $m) -Encoding UTF8 }

W "watcher v3 start pid=$PID"
$deadline = (Get-Date).AddMinutes(150)
$waited = 0
# phase 1: wait for push chain (git.exe with push + bm-b-r951 in cmdline) to exit
while (((Get-Date) -lt $deadline)) {
    $push = Get-CimInstance Win32_Process -Filter "name='git.exe'" -ErrorAction SilentlyContinue |
        Where-Object { $_.CommandLine -and $_.CommandLine -like '*push*bm-b-r951*' }
    if (-not $push) { W "phase1 done: push chain exited after ~$waited min of watch"; break }
    Start-Sleep 60
    $waited++
    if (($waited % 15) -eq 0) { W "still waiting: push alive, waited=$waited min" }
}
if ((Get-Date) -ge $deadline) { W "phase1 deadline 150min hit - push still alive? ending watch (next round re-arms)" }

# phase 2: run worker v2 checkout faces (idempotent; re-runs are no-ops on healed faces)
W "phase2: launching worker v2 checkout faces"
& powershell -NoProfile -ExecutionPolicy Bypass -File "$bm\results\_r949bmb_restore_worker_v2.ps1" *>$null
W "phase2: worker v2 returned"

# phase 3: classify end state from v2 log tail
$tail = Get-Content -Path $v2log -Tail 6 -ErrorAction SilentlyContinue
$all = ($tail | Select-String 'ALL FACES RESTORED').Count -gt 0
$dcount = ($tail | Select-String 'final D-count=(\d+)' | ForEach-Object { $_.Matches[0].Groups[1].Value } | Select-Object -Last 1)
if ($all) {
    W "END-STATE: ALL FACES RESTORED (D-count=$dcount)"
    Set-Content -Path "$bm\results\_r952bmb_faces_marker.txt" -Value ("ALL_FACES_RESTORED dcount=" + $dcount + " ts=" + (Get-Date -Format s)) -Encoding ASCII
} else {
    W ("END-STATE: UNRESOLVED faces remain (D-count=" + $dcount + ") - see v2 log")
    Set-Content -Path "$bm\results\_r952bmb_faces_marker.txt" -Value ("UNRESOLVED dcount=" + $dcount + " ts=" + (Get-Date -Format s)) -Encoding ASCII
}
W "watcher v3 done"
