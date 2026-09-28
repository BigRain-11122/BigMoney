# Registers the Bigmoney resident dispatcher task (Bigmoney-ResidentDispatcher,
# T-108 D2, O-20260928-1630): 1-min repetition -> Tools\resident_dispatcher.py
# run (2 inner 30s cycles per fire) -> closes pool-ready -> burn-start
# ignition to <=60s. The 10-min Bigmoney-Autofill task (C8 baseline) stays
# untouched; the dispatcher only ADDS a fast pre-check lane that invokes the
# EXISTING autofill tick engine (reuse-not-rewrite law).
# PATH-AGNOSTIC + idempotent + pure ASCII (register_loop_task.ps1 precedent).
# Disabled-state heal (MSG-20260928-1622 root cause, T-107/T-108 family law):
# a time-limit kill must never leave the task Disabled -- a round-level event
# is never a task-level verdict, so a Disabled task re-registers (re-enables).
# No minute pin: the 1-min cadence has no stagger space; git-window safety is
# owned by the dispatcher's index.lock/rebase-marker pre-check guards.
$Project = Split-Path -Parent $PSScriptRoot
$rd = Join-Path $Project 'Tools\resident_dispatcher.py'
$vbs = Join-Path $Project 'Tools\InvisibleRunner.vbs'
if (-not (Test-Path $rd)) { Write-Output "FATAL: $rd missing"; exit 1 }
if (-not (Test-Path $vbs)) { Write-Output "FATAL: $vbs missing"; exit 1 }
$a = New-ScheduledTaskAction -Execute 'wscript.exe' `
    -Argument ('//B //nologo "' + $vbs + '" python.exe "' + $rd + '" run') `
    -WorkingDirectory $Project
# existence canon = schtasks (R49: Get-ScheduledTask CIM reads can transiently
# false-negative while a task instance is running); Disabled heal via CIM with
# CIM-fault fallthrough to a harmless idempotent re-register.
$exists = schtasks /query /tn 'Bigmoney-ResidentDispatcher' 2>$null
$disabledHeal = $false
if ($exists) {
    try {
        if ((Get-ScheduledTask -TaskName 'Bigmoney-ResidentDispatcher' -ErrorAction Stop).State -eq 'Disabled') {
            $disabledHeal = $true
            Write-Output "disabled-state heal: task left Disabled (time-limit kill family, MSG-20260928-1622) -> re-register re-enables"
        }
    } catch {}
}
if ($exists -and -not $disabledHeal) {
    Write-Output "task present + enabled: no-op (idempotent)"
    exit 0
}
$start = Get-Date -Second 0
$start = $start.AddMinutes(1)
$t = New-ScheduledTaskTrigger -Once -At $start -RepetitionInterval (New-TimeSpan -Minutes 1) -RepetitionDuration (New-TimeSpan -Days 3650)
$s = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Minutes 3)
Register-ScheduledTask -TaskName 'Bigmoney-ResidentDispatcher' -Action $a -Trigger $t -Settings $s -Force | Out-Null
Write-Output "registered Bigmoney-ResidentDispatcher (project=$Project), 1-min repetition, first fire $start"
