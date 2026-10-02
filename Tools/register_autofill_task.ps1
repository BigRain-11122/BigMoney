# Registers the Bigmoney autofill task (Bigmoney-Autofill, C8 leg).
# Runs Tools\autofill.py tick every 2 min: O-20260930-2340 claim-to-
# saturation law (CEO order -- fill latency tightened from the O-20260924-2100
# s2.2 10-min cadence; no-op ticks stay pure-local + cheap, git fetch only
# rides claim flows). ExecutionTimeLimit 15 min: one saturation-chain tick =
# up to 8 launches x (~12s claim + 25s ramp wait) can exceed 5 min.
# Zero-LLM deterministic. PATH-AGNOSTIC + idempotent via -Force + pure ASCII.
$Project = Split-Path -Parent $PSScriptRoot
$af = Join-Path $Project 'Tools\autofill.py'
$vbs = Join-Path $Project 'Tools\InvisibleRunner.vbs'
if (-not (Test-Path $af)) { Write-Output "FATAL: $af missing"; exit 1 }
if (-not (Test-Path $vbs)) { Write-Output "FATAL: $vbs missing"; exit 1 }
$a = New-ScheduledTaskAction -Execute 'wscript.exe' `
    -Argument ('//B //nologo "' + $vbs + '" python.exe "' + $af + '" tick') `
    -WorkingDirectory $Project
$start = Get-Date -Minute 0 -Second 0
while ($start -le (Get-Date)) { $start = $start.AddMinutes(2) }
$t = New-ScheduledTaskTrigger -Once -At $start -RepetitionInterval (New-TimeSpan -Minutes 2) -RepetitionDuration (New-TimeSpan -Days 3650)
$s = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Minutes 15)
# PRINCIPAL SINGLE-SOURCE (D-20261002-02 group adjudication, r576 bm-b):
# ALL lane task registration scripts use the DEFAULT principal as the
# single source. S4U proven uninstallable in this environment (bm-a
# live-fire 0x80070005 from unelevated hosts) -- an S4U-only script
# left the task DEAD on honest-fail, breaking self-healing. Survives-
# logoff explicitly abandoned: cadence fire + watchdog mutual coverage
# replace it. Deviation from the 2026-09-29 user S4U order is reported
# to CEO for re-adjudication via the D-20261002-02 row; an elevated
# window can switch back to S4U (option (a)).
Register-ScheduledTask -TaskName 'Bigmoney-Autofill' -Action $a -Trigger $t -Settings $s -Force | Out-Null
Write-Output "registered Bigmoney-Autofill (project=$Project, logon=default per D-20261002-02, cadence=2min), first fire $start"
