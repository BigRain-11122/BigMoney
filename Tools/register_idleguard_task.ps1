# Registers BmaIdleGuard (10-min idle guard, O-20261018-2236-bm-c sec.3.1 bm-a leg).
# Runs Tools\bma_idleguard.pyw via SYS_PY pythonw (windowless). Idempotent via -Force,
# pure ASCII, S4U via proven XML flip (see register_watchdog_task.ps1 S4U LAW note).
$Project = Split-Path -Parent $PSScriptRoot
$pyw = Join-Path $Project 'Tools\bma_idleguard.pyw'
$syspy = "$env:LOCALAPPDATA\Programs\Python\Python314\pythonw.exe"
if (-not (Test-Path $pyw)) { Write-Output "FATAL: $pyw missing"; exit 1 }
if (-not (Test-Path $syspy)) { Write-Output "FATAL: $syspy missing"; exit 1 }
$a = New-ScheduledTaskAction -Execute $syspy -Argument ('"' + $pyw + '"') -WorkingDirectory $Project
$start = Get-Date -Second 0
while ($start -le (Get-Date)) { $start = $start.AddMinutes(10) }
$t = New-ScheduledTaskTrigger -Once -At $start -RepetitionInterval (New-TimeSpan -Minutes 10) -RepetitionDuration (New-TimeSpan -Days 3650)
$s = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Minutes 5)
Register-ScheduledTask -TaskName 'BmaIdleGuard' -Action $a -Trigger $t -Settings $s -Force -ErrorAction Stop | Out-Null
try {
    $x = Export-ScheduledTask -TaskName 'BmaIdleGuard'
    $x2 = $x -replace '<LogonType>[^<]*</LogonType>','<LogonType>S4U</LogonType>' -replace '<StartWhenAvailable>true</StartWhenAvailable>','<StartWhenAvailable>false</StartWhenAvailable>'
    Register-ScheduledTask -TaskName 'BmaIdleGuard' -Xml $x2 -Force -ErrorAction Stop | Out-Null
    Write-Output "registered BmaIdleGuard (logon=S4U via XML flip, SWA=false), first fire $start"
} catch {
    Write-Output "WARN: S4U XML flip failed ($($_.Exception.Message)) -> task left at default principal, first fire $start"
}
