# Registers the Bigmoney saturation engine task (Bigmoney-SatEngine-bm-b,
# T-2026-10-01-141 s1, SATURATION_ENGINE_LAW v1.0 / O-20261001-1410).
# Runs scripts\saturation_engine.py tick every 60s: local perpetual queue
# -> PreIgnitionChecks -> detached shard ignite (idle-to-ignite <= tick
# cadence, zero claim round-trips), py% CEO face row write, sec.2 batched
# ledger flush. Engine burns NEVER touch runnable_pool.json (law sec.1).
# PATH-AGNOSTIC + idempotent via -Force + pure ASCII.
# PRINCIPAL LAW (bm-a live-fire 2026-10-01 15:3x): S4U principal requires
# elevation on this lane (Register-ScheduledTask 0x80070005 access denied,
# script then printed a false success) -> default principal per the proven
# unelevated family (register_loop_task/pool_worker/dispatcher). Headless
# window suppression is unaffected: InvisibleRunner.vbs + wscript //B owns
# that face. -ErrorAction Stop gates the success line (no false-success).
# Task name stays 'Bigmoney-SatEngine-bm-b' (fleet-shared local name; bm-b
# runs it live -- renaming here would orphan bm-b's task = double-engine).
$Project = Split-Path -Parent $PSScriptRoot
$eng = Join-Path $Project 'scripts\saturation_engine.py'
$vbs = Join-Path $Project 'Tools\InvisibleRunner.vbs'
if (-not (Test-Path $eng)) { Write-Output "FATAL: $eng missing"; exit 1 }
if (-not (Test-Path $vbs)) { Write-Output "FATAL: $vbs missing"; exit 1 }
$a = New-ScheduledTaskAction -Execute 'wscript.exe' `
    -Argument ('//B //nologo "' + $vbs + '" python.exe "' + $eng + '" tick') `
    -WorkingDirectory $Project
$start = Get-Date -Minute 0 -Second 0
while ($start -le (Get-Date)) { $start = $start.AddMinutes(1) }
$t = New-ScheduledTaskTrigger -Once -At $start -RepetitionInterval (New-TimeSpan -Minutes 1) -RepetitionDuration (New-TimeSpan -Days 3650)
$s = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Minutes 10)
Register-ScheduledTask -TaskName 'Bigmoney-SatEngine-bm-b' -Action $a -Trigger $t -Settings $s -Force -ErrorAction Stop | Out-Null
Write-Output "registered Bigmoney-SatEngine-bm-b (project=$Project, logon=default, cadence=60s), first fire $start"
