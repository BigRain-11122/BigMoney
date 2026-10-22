# Registers the T-35 intraday marks lane task (Bigmoney-IntradayMarks).
# Runs scripts\update_intraday_marks.py through the hidden wscript chain.
#
# Why this exists (r1155 bm-b): t35_open_fill_verify returned rc=1 on
# 2026-10-22 with "marks file for 2026-10-22 missing" while the task list held
# NO marks task at all -- the lane only produced evidence on days when the
# iteration loop happened to fire inside 09:30-15:10. Marks are append-only and
# never backdated, so a day without an intraday tick is an evidence gap that can
# never be healed. The script's own clock gate makes every out-of-window fire a
# legal no-op exit 0 (no network), so a 10-minute cadence is safe around the
# clock.
#
# PATH-AGNOSTIC + idempotent via -Force + pure ASCII + S4U via XML flip
# (same recipe and the same honest-fail behavior as register_watchdog_task.ps1).
$Project = Split-Path -Parent $PSScriptRoot
$py = Join-Path $Project 'scripts\update_intraday_marks.py'
$vbs = Join-Path $Project 'Tools\InvisibleRunner.vbs'
if (-not (Test-Path $py)) { Write-Output "FATAL: $py missing"; exit 1 }
if (-not (Test-Path $vbs)) { Write-Output "FATAL: $vbs missing"; exit 1 }
$a = New-ScheduledTaskAction -Execute 'wscript.exe' `
    -Argument ('//B //nologo "' + $vbs + '" python.exe "' + $py + '"') `
    -WorkingDirectory $Project
$start = Get-Date -Second 0
while ($start -le (Get-Date)) { $start = $start.AddMinutes(10) }
$t = New-ScheduledTaskTrigger -Once -At $start -RepetitionInterval (New-TimeSpan -Minutes 10) -RepetitionDuration (New-TimeSpan -Days 3650)
$s = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Minutes 10)
Register-ScheduledTask -TaskName 'Bigmoney-IntradayMarks' -Action $a -Trigger $t -Settings $s -Force -ErrorAction Stop | Out-Null
try {
    $x = Export-ScheduledTask -TaskName 'Bigmoney-IntradayMarks'
    $x2 = $x -replace '<LogonType>[^<]*</LogonType>','<LogonType>S4U</LogonType>' -replace '<StartWhenAvailable>true</StartWhenAvailable>','<StartWhenAvailable>false</StartWhenAvailable>'
    Register-ScheduledTask -TaskName 'Bigmoney-IntradayMarks' -Xml $x2 -Force -ErrorAction Stop | Out-Null
    Write-Output "registered Bigmoney-IntradayMarks (project=$Project, logon=S4U via XML flip, SWA=false), first fire $start"
} catch {
    Write-Output "WARN: S4U XML flip failed ($($_.Exception.Message)) -> task left at default principal (LogonType regression face: manual S4U re-pass needed), first fire $start"
}