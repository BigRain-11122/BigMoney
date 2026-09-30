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
# S4U law (2026-09-29 bm-b lane rule, watchdog register script same pattern):
# lane tasks register S4U, never InteractiveToken -- headless children, no black window.
$p = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -LogonType S4U
Register-ScheduledTask -TaskName 'Bigmoney-Autofill' -Action $a -Trigger $t -Settings $s -Principal $p -Force | Out-Null
Write-Output "registered Bigmoney-Autofill (project=$Project, logon=S4U, cadence=2min), first fire $start"
