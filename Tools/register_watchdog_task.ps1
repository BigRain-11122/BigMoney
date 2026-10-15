# Registers the Bigmoney watchdog task (Bigmoney-LoopWatchdog).
# Runs Tools\watchdog.ps1: heals the iteration-loop task, kicks stalled
# rounds, revives dead background chains (margin pull / P-1c batch).
# O-2026-09-30-2340 knife-1 (bm-b r483): cadence 30 -> 2 min. Pool-empty
# exemption honored by body behavior: every C1-C7 probe is a cheap idempotent
# shell check (<1s CPU) and the watchdog never launches pool-eating work when
# the pool is empty -- a 2-min pass in pool-empty state costs ~nothing.
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
$start = Get-Date -Second 0
while ($start -le (Get-Date)) { $start = $start.AddMinutes(2) }
$t = New-ScheduledTaskTrigger -Once -At $start -RepetitionInterval (New-TimeSpan -Minutes 2) -RepetitionDuration (New-TimeSpan -Days 3650)
$s = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Minutes 10)
# S4U LAW (2026-10-15 09:16 re-adjudication of the 2026-09-29 CEO order):
# lane tasks on this machine are S4U-registered; InteractiveToken is the
# regression face (desktop black-window root cause; watchdog regressed via
# this recipe's default principal, recaptured r981). D-20261002-02 is
# superseded as the registration DEFAULT; its honest-fail concern survives:
# this host's Register-ScheduledTask has no -LogonType parameter (WinPS 5.1
# PSScheduledTask module face, r981 live-fire), so S4U is applied via the
# proven XML flip (register default, export, patch LogonType + SWA=false,
# re-register from XML). Flip failure leaves the task alive at default
# principal and reports the regression honestly (no false success, r521).
Register-ScheduledTask -TaskName 'Bigmoney-LoopWatchdog' -Action $a -Trigger $t -Settings $s -Force -ErrorAction Stop | Out-Null
try {
    $x = Export-ScheduledTask -TaskName 'Bigmoney-LoopWatchdog'
    $x2 = $x -replace '<LogonType>[^<]*</LogonType>','<LogonType>S4U</LogonType>' -replace '<StartWhenAvailable>true</StartWhenAvailable>','<StartWhenAvailable>false</StartWhenAvailable>'
    Register-ScheduledTask -TaskName 'Bigmoney-LoopWatchdog' -Xml $x2 -Force -ErrorAction Stop | Out-Null
    Write-Output "registered Bigmoney-LoopWatchdog (project=$Project, logon=S4U via XML flip, SWA=false), first fire $start"
} catch {
    Write-Output "WARN: S4U XML flip failed ($($_.Exception.Message)) -> task left at default principal (LogonType regression face: manual S4U re-pass needed), first fire $start"
}
