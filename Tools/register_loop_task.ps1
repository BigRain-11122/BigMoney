# Registers the Bigmoney 10-minute OS iteration loop.
# PATH-AGNOSTIC (any machine, any folder): every path is derived from this
# script's own location - zero edits needed on a new machine.
# Pure ASCII (see iteration_loop.ps1 ENCODING RULE). Idempotent via -Force.
# Re-registering refreshes the task definition - safe to re-run for self-heal.
#
# D-20260928-03(1) per-machine pinned phase (three-machine stagger):
# round starts are pinned per machine_id so the three machines' S0
# pull-rebases / S6 shared-file write bursts / S7 pushes land on distinct
# minute positions instead of registration-time-random clustering (the
# 26-UU add/add storm root cause, F-20260927-06). Pins are chosen away
# from the fleet-wide autofill tick git-write window (:X0:02 +/-1min,
# r331): bm-a=8 (keeps its live phase, zero re-registration churn),
# bm-b=2, bm-c=5 -> round starts spread 4/3/3 minutes apart. The
# same-machine residual window at the tick boundary is guarded by the
# autofill pre-add mid-op leg (D-20260928-02). Phase drift self-heals:
# re-running this script no-ops when the live trigger phase matches the
# pin, re-registers when it drifted. Unknown machines keep the legacy
# 8-minute walk (registration-time phase).
$Project = Split-Path -Parent $PSScriptRoot
$launcher = Join-Path $Project 'Tools\iteration_loop.ps1'
$vbs = Join-Path $Project 'Tools\InvisibleRunner.vbs'
if (-not (Test-Path $launcher)) { Write-Output "FATAL: $launcher missing"; exit 1 }
if (-not (Test-Path $vbs)) { Write-Output "FATAL: $vbs missing"; exit 1 }
$a = New-ScheduledTaskAction -Execute 'wscript.exe' `
    -Argument ('//B //nologo "' + $vbs + '" powershell.exe -NoProfile -ExecutionPolicy Bypass -File "' + $launcher + '"') `
    -WorkingDirectory $Project
# per-machine pin (D-20260928-03(1))
$mid = ''
try {
    $mid = (Get-Content (Join-Path $Project 'fleet\machine.json') -Raw `
        -ErrorAction Stop | ConvertFrom-Json).machine_id
} catch {}
$pinMap = @{ 'bm-a' = 8; 'bm-b' = 2; 'bm-c' = 5 }
$pin = -1
if ($pinMap.ContainsKey($mid)) { $pin = [int]$pinMap[$mid] }
if ($pin -ge 0) {
    $start = Get-Date -Minute 0 -Second 0
    while ($start.Minute % 10 -ne $pin) { $start = $start.AddMinutes(1) }
    while ($start -le (Get-Date)) { $start = $start.AddMinutes(10) }
} else {
    $start = Get-Date -Minute 0 -Second 0
    while ($start -le (Get-Date)) { $start = $start.AddMinutes(8) }
}
# phase verify: schtasks stays the EXISTENCE canon (R49); CIM reads the
# trigger StartBoundary for metadata only. Any CIM fault falls through
# to a harmless idempotent re-register.
# Disabled-state heal (MSG-20260928-1622 root cause, T-107 scope): a
# 15-min-style time-limit kill can leave the task DISABLED -- that is a
# ROUND-level event, never a task-level verdict, so the self-heal check
# re-registers (re-enables + refreshes settings incl. the 35-min limit)
# instead of leaving the loop dead until a human notices.
# U060 zero-window law: bare schtasks from a windowless session host = one
# desktop console flash per launch; route through the CreateNoWindow helper
# (Tools\Invoke-SilentExe.ps1). Existence semantics unchanged: stdout rows
# present = task exists, empty + exit 1 = missing (R49 schtasks canon kept).
$exists = & (Join-Path $PSScriptRoot 'Invoke-SilentExe.ps1') -Exe schtasks -ArgString '/query /tn "Bigmoney-IterationLoop"'
$disabledHeal = $false
if ($exists) {
    try {
        if ((Get-ScheduledTask -TaskName 'Bigmoney-IterationLoop' -ErrorAction Stop).State -eq 'Disabled') {
            $disabledHeal = $true
            Write-Output "disabled-state heal: task left Disabled (time-limit kill family, MSG-20260928-1622) -> re-register re-enables + refreshes settings"
        }
    } catch {}
}
if ($exists -and -not $disabledHeal -and $pin -ge 0) {
    try {
        $sb = (Get-ScheduledTask -TaskName 'Bigmoney-IterationLoop' `
              -ErrorAction Stop).Triggers[0].StartBoundary
        if ($sb -match 'T\d{2}:(\d{2}):') {
            $cur = [int]$Matches[1] % 10
            if ($cur -eq $pin) {
                Write-Output "phase ok: machine=$mid pin=$pin current=$cur (no-op, first fire stays $start)"
                exit 0
            }
            Write-Output "phase drift: machine=$mid pin=$pin current=$cur -> re-registering"
        }
    } catch {}
}
$t = New-ScheduledTaskTrigger -Once -At $start -RepetitionInterval (New-TimeSpan -Minutes 10) -RepetitionDuration (New-TimeSpan -Days 3650)
$s = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Minutes 35)
Register-ScheduledTask -TaskName 'Bigmoney-IterationLoop' -Action $a -Trigger $t -Settings $s -Force | Out-Null
Write-Output "registered Bigmoney-IterationLoop (project=$Project, machine=$mid, pin=$pin), first fire $start"
