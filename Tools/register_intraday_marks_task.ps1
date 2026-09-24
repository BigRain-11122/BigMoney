# Registers the Bigmoney intraday-marks task (T-35 d2, O-20260924-2045).
# Runs scripts\update_intraday_marks.py every 10 min inside the trading
# window (09:25 start, ~5h45m repetition span MON-FRI): script-side gates
# make every tick safe (intraday mark 09:30-15:00, settle face once at
# 15:00+, out-of-window = legal no-op). PATH-AGNOSTIC + idempotent via
# -Force + pure ASCII.
$Project = Split-Path -Parent $PSScriptRoot
$im = Join-Path $Project 'scripts\update_intraday_marks.py'
$vbs = Join-Path $Project 'Tools\InvisibleRunner.vbs'
if (-not (Test-Path $im)) { Write-Output "FATAL: $im missing"; exit 1 }
if (-not (Test-Path $vbs)) { Write-Output "FATAL: $vbs missing"; exit 1 }
$a = New-ScheduledTaskAction -Execute 'wscript.exe' `
    -Argument ('//B //nologo "' + $vbs + '" python.exe "' + $im + '"') `
    -WorkingDirectory $Project
# weekly 09:25 trigger + 10-min repetition spanning to 15:10 (the script
# self-gates exact 09:30/15:00 boundaries and no-ops outside them)
$base = (Get-Date).Date.AddHours(9).AddMinutes(25)
if ($base -le (Get-Date)) { $base = $base.AddDays(1) }
$t = New-ScheduledTaskTrigger -Weekly -At $base -DaysOfWeek Monday,Tuesday,Wednesday,Thursday,Friday
$rep = New-ScheduledTaskTrigger -Once -At $base `
    -RepetitionInterval (New-TimeSpan -Minutes 10) `
    -RepetitionDuration (New-TimeSpan -Hours 5 -Minutes 45)
$t.Repetition = $rep.Repetition
$s = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Minutes 5)
Register-ScheduledTask -TaskName 'Bigmoney-IntradayMarks' -Action $a -Trigger $t -Settings $s -Force | Out-Null
Write-Output "registered Bigmoney-IntradayMarks (project=$Project), first fire $base"
