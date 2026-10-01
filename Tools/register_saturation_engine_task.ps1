# Registers the Bigmoney saturation engine task (Bigmoney-SaturationEngine,
# T-141 s1, law firm/SATURATION_ENGINE_LAW.md): 1-min repetition ->
# Tools\saturation_engine.py run (resident supervisor, IgnoreNew single
# instance). InvisibleRunner.vbs WAITS on the python process, so the task
# instance stays Running for the engine's lifetime and IgnoreNew skips
# re-fires; engine death = next 1-min trigger restarts it (law sec.4
# self-restart). ExecutionTimeLimit is deliberately 7 days (NOT the 3-min
# dispatcher default): the engine is resident; the inner watchdog thread
# (STALL_EXIT_S=300s) is the primary hang defense, the task limit is the
# backup reaper. Disabled-state heal + schtasks existence canon per
# register_dispatcher_task.ps1 precedent (R49 CIM pit). Pure ASCII,
# path-agnostic, idempotent.
$Project = Split-Path -Parent $PSScriptRoot
$se = Join-Path $Project 'Tools\saturation_engine.py'
$vbs = Join-Path $Project 'Tools\InvisibleRunner.vbs'
if (-not (Test-Path $se)) { Write-Output "FATAL: $se missing"; exit 1 }
if (-not (Test-Path $vbs)) { Write-Output "FATAL: $vbs missing"; exit 1 }
$a = New-ScheduledTaskAction -Execute 'wscript.exe' `
    -Argument ('//B //nologo "' + $vbs + '" python.exe "' + $se + '" run') `
    -WorkingDirectory $Project
$exists = schtasks /query /tn 'Bigmoney-SaturationEngine' 2>$null
$disabledHeal = $false
if ($exists) {
    try {
        if ((Get-ScheduledTask -TaskName 'Bigmoney-SaturationEngine' -ErrorAction Stop).State -eq 'Disabled') {
            $disabledHeal = $true
            Write-Output "disabled-state heal: task left Disabled -> re-register re-enables"
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
$s = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Days 7)
Register-ScheduledTask -TaskName 'Bigmoney-SaturationEngine' -Action $a -Trigger $t -Settings $s -Force | Out-Null
Write-Output "registered Bigmoney-SaturationEngine (project=$Project), 1-min repetition, first fire $start"
