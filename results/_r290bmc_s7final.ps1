# r290 bm-c S7 final batch (in-process)
Move-Item fleet\inbox\MSG-20260930-2150-bmb-ALL-p2null-s2-burned-harvest-flips-merge-fix.md fleet\inbox\processed\ -Force
Write-Host "inbox processed count: $((Get-ChildItem fleet\inbox\processed -Filter 'MSG-20260930-2*.md').Count)"

# S7 orders double-scan (round-start + closeout)
$orders = Get-ChildItem fleet\orders\ -Filter O-*.md | Select-Object -ExpandProperty Name
$ack = (Get-Content fleet\machines\bm-c.json -Raw | ConvertFrom-Json).orders_ack
$diff = $orders | Where-Object { $ack -notcontains $_ }
Write-Host "S7 orders double-scan diff: $($diff.Count)"

# attrition ledger tripwire
python scripts\attrition_ledger_guard.py scan 2>&1 | Select-Object -Last 2
Write-Host "attrition rc=$LASTEXITCODE"

# schtasks status (R49: schtasks not Get-ScheduledTask)
schtasks /query /tn "Bigmoney-IterationLoop" 2>&1 | Select-Object -Last 3
schtasks /query /tn "Bigmoney-LoopWatchdog" 2>&1 | Select-Object -Last 3

# self-heal registers (idempotent, in-process per zero-window law)
& Tools\register_loop_task.ps1 2>&1 | Select-Object -Last 2
& Tools\register_watchdog_task.ps1 2>&1 | Select-Object -Last 2
& Tools\register_precommit_claw.ps1 2>&1 | Select-Object -Last 2
