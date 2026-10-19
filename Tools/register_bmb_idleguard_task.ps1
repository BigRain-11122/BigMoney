# Registers BmbIdleGuard (5-min idle guard per cadence v2 2026-10-19 11:53 CEO order; was 10-min, O-20261018-2236-bm-c sec.3.1 bm-b leg).
# Mirrors bm-a r1068 register_idleguard_task.ps1 (interim face until the canon
# cph4/fleet/idle-guard-kit/ lands on group origin, then canon-adopt <=1 round).
# Runs Tools\bmb_idleguard.pyw via SYS_PY pythonw (windowless GUI subsystem =
# zero desktop window even under default principal). Idempotent via -Force,
# pure ASCII. S4U via proven XML flip (S4U LAW, register_loop_task.ps1 note).
$Project = Split-Path -Parent $PSScriptRoot
$pyw = Join-Path $Project 'Tools\bmb_idleguard.pyw'
$syspy = 'C:\Program Files\Python311\pythonw.exe'
if (-not (Test-Path $pyw)) { Write-Output "FATAL: $pyw missing"; exit 1 }
if (-not (Test-Path $syspy)) { Write-Output "FATAL: $syspy missing"; exit 1 }
$a = New-ScheduledTaskAction -Execute $syspy -Argument ('"' + $pyw + '"') -WorkingDirectory $Project
$start = Get-Date -Second 0
while ($start -le (Get-Date)) { $start = $start.AddMinutes(5) }
$t = New-ScheduledTaskTrigger -Once -At $start -RepetitionInterval (New-TimeSpan -Minutes 5) -RepetitionDuration (New-TimeSpan -Days 3650)
$s = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Minutes 5)
Register-ScheduledTask -TaskName 'BmbIdleGuard' -Action $a -Trigger $t -Settings $s -Force -ErrorAction Stop | Out-Null
try {
    $x = Export-ScheduledTask -TaskName 'BmbIdleGuard'
    $x2 = $x -replace '<LogonType>[^<]*</LogonType>','<LogonType>S4U</LogonType>' -replace '<StartWhenAvailable>true</StartWhenAvailable>','<StartWhenAvailable>false</StartWhenAvailable>'
    Register-ScheduledTask -TaskName 'BmbIdleGuard' -Xml $x2 -Force -ErrorAction Stop | Out-Null
    Write-Output "registered BmbIdleGuard (logon=S4U via XML flip, SWA=false), first fire $start"
} catch {
    Write-Output "WARN: S4U XML flip failed ($($_.Exception.Message)) -> task left at default principal (pythonw zero-window guarantee holds), first fire $start"
}
