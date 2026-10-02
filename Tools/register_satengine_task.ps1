# Registers the Bigmoney saturation engine task (Bigmoney-SatEngine-bm-b,
# T-2026-10-01-141 s1, SATURATION_ENGINE_LAW v1.0 / O-20261001-1410).
# Runs scripts\saturation_engine.py tick every 60s: local perpetual queue
# -> PreIgnitionChecks -> detached shard ignite (idle-to-ignite <= tick
# cadence, zero claim round-trips), py% CEO face row write, sec.2 batched
# ledger flush. Engine burns NEVER touch runnable_pool.json (law sec.1).
# PATH-AGNOSTIC + idempotent via -Force + pure ASCII.
# PRINCIPAL SINGLE-SOURCE (D-20261002-02 group adjudication, r576 bm-b):
# ALL lane task registration scripts use the DEFAULT principal as the
# single source. S4U proven uninstallable in this environment (bm-a
# live-fire 0x80070005 from unelevated hosts) -- the S4U-first +
# fallback two-path (bm-b r521) is retired: a single default-principal
# path means unelevated heal contexts never leave the engine task DEAD.
# Survives-logoff explicitly abandoned: 1-min fire + watchdog mutual
# coverage replace it. Deviation from the 2026-09-29 user S4U order is
# reported to CEO for re-adjudication via the D-20261002-02 row; an
# elevated window can switch back to S4U (option (a)).
# Task name stays 'Bigmoney-SatEngine-bm-b' (fleet-shared local name; bm-b
# runs it live -- renaming here would orphan bm-b's task = double-engine).
# NOTE (r576): the LIVE task on bm-b remains S4U-registered (healthy,
# registered from an elevated window, zero console flash). Conversion to
# default principal happens at the next natural heal cycle (task-missing
# repair path) -- no proactive re-registration this round: converting a
# healthy 60s-cadence task to InteractiveToken would reintroduce the
# desktop console-flash the 2026-09-29 user order forbids, pending the
# CEO re-adjudication the D-20261002-02 row itself carries.
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
Write-Output "registered Bigmoney-SatEngine-bm-b (project=$Project, logon=default per D-20261002-02, cadence=60s), first fire $start"
