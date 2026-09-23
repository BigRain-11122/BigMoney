# Registers Windows scheduled task "MoneyAutoGuardian" for the Money auto-guardian:
#   trigger 1: at user logon
#   trigger 2: every 5 minutes (missed starts catch up via StartWhenAvailable)
# Each run invokes tools\watchdog.ps1 which starts `python run.py auto` only if
# no guardian is alive (single-guardian rule) and state\watchdog_pause does not exist.
# Re-runnable: simply run again to (re)create the task.

$ErrorActionPreference = 'Stop'
$Root = 'C:\Users\sjs20\Desktop\Money'
$Script = Join-Path $Root 'tools\watchdog.ps1'
if (-not (Test-Path $Script)) { throw "watchdog.ps1 not found: $Script" }

$action   = New-ScheduledTaskAction -Execute 'powershell.exe' `
    -Argument ('-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File "{0}"' -f $Script)
$atLogon  = New-ScheduledTaskTrigger -AtLogOn -User $env:USERNAME
$every5   = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1) `
    -RepetitionInterval (New-TimeSpan -Minutes 5) -RepetitionDuration ([TimeSpan]::FromDays(3650))
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries `
    -StartWhenAvailable -ExecutionTimeLimit (New-TimeSpan -Minutes 10) `
    -MultipleInstances IgnoreNew

Register-ScheduledTask -TaskName 'MoneyAutoGuardian' -Action $action `
    -Trigger @($atLogon, $every5) -Settings $settings -Force `
    -Description 'Money quant system guardian watchdog: auto-start python run.py auto when down' | Out-Null

Write-Host "Scheduled task 'MoneyAutoGuardian' registered for user $env:USERNAME."
