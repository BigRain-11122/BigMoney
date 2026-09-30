# Registers the Bigmoney watchdog task (Bigmoney-LoopWatchdog).
# Runs Tools\watchdog.ps1 every 30 min: heals the iteration-loop task, kicks
# stalled rounds, revives dead background chains (margin pull / P-1c batch).
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
$start = Get-Date -Minute 0 -Second 0
while ($start -le (Get-Date)) { $start = $start.AddMinutes(20) }
$t = New-ScheduledTaskTrigger -Once -At $start -RepetitionInterval (New-TimeSpan -Minutes 30) -RepetitionDuration (New-TimeSpan -Days 3650)
$s = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Minutes 10)
# S4U law (2026-09-29 user order, bm-b lane rule): all lane scheduled tasks
# on this machine register S4U, never InteractiveToken -- survives logoff and
# child console windows stay invisible (no desktop flash).
$p = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -LogonType S4U
Register-ScheduledTask -TaskName 'Bigmoney-LoopWatchdog' -Action $a -Trigger $t -Settings $s -Principal $p -Force | Out-Null
Write-Output "registered Bigmoney-LoopWatchdog (project=$Project, logon=S4U), first fire $start"
