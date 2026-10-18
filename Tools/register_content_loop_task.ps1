# Registers Bigmoney-ContentLoop (CONTENT-OS-LOOP drama-line carrier, bm-b host,
# O-20261018-2144-bm-c sec.2.1 P1 <=10-20 first code). 20-min cadence per
# CONTENT-OS-LOOP-BLUEPRINT-v1 sec.3. Mirrors register_loop_task.ps1 pattern:
# wscript hidden chain (U060 zero-window law), S4U via proven XML flip (S4U
# LAW), pin minute%20==12 so fetch/push windows sit 10min away from the bm-b
# iteration-loop pin (:X2) -- no same-minute git-op collision. Pure ASCII.
# Idempotent via -Force; re-register refreshes the definition.
$Project = Split-Path -Parent $PSScriptRoot
$launcher = Join-Path $Project 'Tools\content_loop.ps1'
$vbs = Join-Path $Project 'Tools\InvisibleRunner.vbs'
if (-not (Test-Path $launcher)) { Write-Output "FATAL: $launcher missing"; exit 1 }
if (-not (Test-Path $vbs)) { Write-Output "FATAL: $vbs missing"; exit 1 }
$a = New-ScheduledTaskAction -Execute 'wscript.exe' `
    -Argument ('//B //nologo "' + $vbs + '" powershell.exe -NoProfile -ExecutionPolicy Bypass -File "' + $launcher + '"') `
    -WorkingDirectory $Project
$pin = 12
$start = Get-Date -Minute 0 -Second 0
while ($start.Minute % 20 -ne $pin) { $start = $start.AddMinutes(1) }
while ($start -le (Get-Date)) { $start = $start.AddMinutes(20) }
$t = New-ScheduledTaskTrigger -Once -At $start -RepetitionInterval (New-TimeSpan -Minutes 20) -RepetitionDuration (New-TimeSpan -Days 3650)
$s = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Minutes 35)
Register-ScheduledTask -TaskName 'Bigmoney-ContentLoop' -Action $a -Trigger $t -Settings $s -Force -ErrorAction Stop | Out-Null
try {
    $x = Export-ScheduledTask -TaskName 'Bigmoney-ContentLoop'
    $x2 = $x -replace '<LogonType>[^<]*</LogonType>','<LogonType>S4U</LogonType>' -replace '<StartWhenAvailable>true</StartWhenAvailable>','<StartWhenAvailable>false</StartWhenAvailable>'
    Register-ScheduledTask -TaskName 'Bigmoney-ContentLoop' -Xml $x2 -Force -ErrorAction Stop | Out-Null
    Write-Output "registered Bigmoney-ContentLoop (logon=S4U via XML flip, SWA=false, pin=$pin), first fire $start"
} catch {
    Write-Output "WARN: S4U XML flip failed ($($_.Exception.Message)) -> task left at default principal (wscript hidden chain zero-window guarantee holds), first fire $start"
}
