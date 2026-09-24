# Registers the Bigmoney autofill task (Bigmoney-Autofill, C8 leg).
# Runs Tools\autofill.py tick every 10 min: O-20260924-2100 s2.2 fill
# latency hard target (ready pool shard -> running <= 10 min), zero-LLM
# deterministic. PATH-AGNOSTIC + idempotent via -Force + pure ASCII.
$Project = Split-Path -Parent $PSScriptRoot
$af = Join-Path $Project 'Tools\autofill.py'
$vbs = Join-Path $Project 'Tools\InvisibleRunner.vbs'
if (-not (Test-Path $af)) { Write-Output "FATAL: $af missing"; exit 1 }
if (-not (Test-Path $vbs)) { Write-Output "FATAL: $vbs missing"; exit 1 }
$a = New-ScheduledTaskAction -Execute 'wscript.exe' `
    -Argument ('//B //nologo "' + $vbs + '" python.exe "' + $af + '" tick') `
    -WorkingDirectory $Project
$start = Get-Date -Minute 0 -Second 0
while ($start -le (Get-Date)) { $start = $start.AddMinutes(10) }
$t = New-ScheduledTaskTrigger -Once -At $start -RepetitionInterval (New-TimeSpan -Minutes 10) -RepetitionDuration (New-TimeSpan -Days 3650)
$s = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Minutes 5)
Register-ScheduledTask -TaskName 'Bigmoney-Autofill' -Action $a -Trigger $t -Settings $s -Force | Out-Null
Write-Output "registered Bigmoney-Autofill (project=$Project), first fire $start"
