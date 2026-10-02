# Registers the Bigmoney watchdog task (Bigmoney-LoopWatchdog).
# Runs Tools\watchdog.ps1: heals the iteration-loop task, kicks stalled
# rounds, revives dead background chains (margin pull / P-1c batch).
# O-2026-09-30-2340 knife-1 (bm-b r483): cadence 30 -> 2 min. Pool-empty
# exemption honored by body behavior: every C1-C7 probe is a cheap idempotent
# shell check (<1s CPU) and the watchdog never launches pool-eating work when
# the pool is empty -- a 2-min pass in pool-empty state costs ~nothing.
# PATH-AGNOSTIC + idempotent via -Force + pure ASCII. Zero-token by design
# (pure shell checks + relaunches, never invokes codely).
$Project = Split-Path -Parent $PSScriptRoot
$wd = Join-Path $Project 'Tools\watchdog.ps1'
$vbs = Join-Path $Project 'Tools\InvisibleRunner.vbs'
if (-not (Test-Path $wd)) { Write-Output "FATAL: $wd missing"; exit 1 }
if (-not (Test-Path $vbs)) { Write-Output "FATAL: $vbs missing"; exit 1 }
$a = New-ScheduledTaskAction -Execute 'wscript.exe' `
    -Argument ('//B //nologo "' + $vbs + '" powershell.exe -NoProfile -ExecutionPolicy Bypass -File "' + $wd + '"') `
    -WorkingDirectory $Project
$start = Get-Date -Second 0
while ($start -le (Get-Date)) { $start = $start.AddMinutes(2) }
$t = New-ScheduledTaskTrigger -Once -At $start -RepetitionInterval (New-TimeSpan -Minutes 2) -RepetitionDuration (New-TimeSpan -Days 3650)
$s = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Minutes 10)
# PRINCIPAL SINGLE-SOURCE (D-20261002-02 group adjudication, r576 bm-b):
# ALL lane task registration scripts use the DEFAULT principal as the
# single source (S4U proven uninstallable in this environment -- bm-a
# live-fire 0x80070005 from unelevated hosts; an S4U-only honest-fail
# left tasks DEAD, breaking self-healing). Survives-logoff explicitly
# abandoned: cadence fire + watchdog mutual coverage replace it.
# Deviation from the 2026-09-29 user S4U order reported to CEO for
# re-adjudication via the D-20261002-02 row.
# No-false-success gate kept (r521 law): -ErrorAction Stop + honest rc=1.
Register-ScheduledTask -TaskName 'Bigmoney-LoopWatchdog' -Action $a -Trigger $t -Settings $s -Force -ErrorAction Stop | Out-Null
Write-Output "registered Bigmoney-LoopWatchdog (project=$Project, logon=default per D-20261002-02), first fire $start"
