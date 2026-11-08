# Registers Bigmoney-MoneyflowPull -- the task-carried moneyflow puller.
#
# Why: update_moneyflow.spawn_detached() uses DETACHED_PROCESS, which does not
# escape the creator's job object. A pull seeded from an interactive CLI window
# dies with that window; the r1417 window found the checkpoint frozen at
# done=758/5226 for 54 minutes while the gate still reported "spawned detached
# refresh". This task RUNS the pull in the foreground, so the task instance
# itself is the carrier: it stays Running until the pull ends and no window
# closing can reach it.
#
# Cadence 20 min with MultipleInstances IgnoreNew => a running pull is never
# duplicated (the runner also refuses when the panel lock is alive), and after
# a crash the next tick resumes from the checkpoint.
# ExecutionTimeLimit 7h: a first pull is 5,226 symbols x ~2.5s + jitter.
#
# PATH-AGNOSTIC + idempotent via -Force + pure ASCII. Principal = default per
# D-20261002-02 (S4U uninstallable on unelevated hosts; deviation stays on the
# D-20261002-02 row for CEO re-adjudication).
$Project = Split-Path -Parent $PSScriptRoot
$runner = Join-Path $Project 'Tools\moneyflow_pull_task.py'
$vbs = Join-Path $Project 'Tools\InvisibleRunner.vbs'
if (-not (Test-Path $runner)) { Write-Output "FATAL: $runner missing"; exit 1 }
if (-not (Test-Path $vbs)) { Write-Output "FATAL: $vbs missing"; exit 1 }
$a = New-ScheduledTaskAction -Execute 'wscript.exe' `
    -Argument ('//B //nologo "' + $vbs + '" python.exe "' + $runner + '"') `
    -WorkingDirectory $Project
$start = Get-Date -Minute 0 -Second 0
while ($start -le (Get-Date)) { $start = $start.AddMinutes(20) }
$t = New-ScheduledTaskTrigger -Once -At $start -RepetitionInterval (New-TimeSpan -Minutes 20) -RepetitionDuration (New-TimeSpan -Days 3650)
$s = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Hours 7)
Register-ScheduledTask -TaskName 'Bigmoney-MoneyflowPull' -Action $a -Trigger $t -Settings $s -Force | Out-Null
Write-Output "registered Bigmoney-MoneyflowPull (project=$Project, cadence=20min, limit=7h), first fire $start"