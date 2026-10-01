# Registers the Bigmoney saturation engine task (Bigmoney-SatEngine-bm-b,
# T-2026-10-01-141 s1, SATURATION_ENGINE_LAW v1.0 / O-20261001-1410).
# Runs scripts\saturation_engine.py tick every 60s: local perpetual queue
# -> PreIgnitionChecks -> detached shard ignite (idle-to-ignite <= tick
# cadence, zero claim round-trips), py% CEO face row write, sec.2 batched
# ledger flush. Engine burns NEVER touch runnable_pool.json (law sec.1).
# PATH-AGNOSTIC + idempotent via -Force + pure ASCII.
# S4U law (2026-09-29 bm-b lane rule): lane tasks register S4U, never
# InteractiveToken -- headless children, no black window.
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
$p = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -LogonType S4U
Register-ScheduledTask -TaskName 'Bigmoney-SatEngine-bm-b' -Action $a -Trigger $t -Settings $s -Principal $p -Force | Out-Null
Write-Output "registered Bigmoney-SatEngine-bm-b (project=$Project, logon=S4U, cadence=60s), first fire $start"
