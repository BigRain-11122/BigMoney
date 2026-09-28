# Registers the Bigmoney pool worker (O-20260928-2210 compute sharing,
# T-113 s4 onboarding face). PATH-AGNOSTIC (any machine, any folder):
# every path derives from this script's own location -- zero edits on a
# new worker machine (fleet machine OR external worker such as BG-B /
# BG-C; their onboarding goes through the GROUP dispatch per the order,
# this script is the technical face that dispatch lands).
# Pure ASCII. Idempotent via -Force (re-register refreshes settings).
# Silent: VBS invisible launcher wrapping pythonw (no console window,
# U060 law). Worker priority = BelowNormal (host's own loop P0 stays
# first, O-2210 yielding law); the runner subprocess is additionally
# forced to BelowNormal by pool_worker itself (double guard).
# Single-instance: pool_worker takes a PID lock internally; the task
# additionally carries MultipleInstances=IgnoreNew.
$Project = Split-Path -Parent $PSScriptRoot
$worker = Join-Path $Project 'Tools\pool_worker.py'
$vbs = Join-Path $Project 'Tools\InvisibleRunner.vbs'
if (-not (Test-Path $worker)) { Write-Output "FATAL: $worker missing"; exit 1 }
if (-not (Test-Path $vbs)) { Write-Output "FATAL: $vbs missing"; exit 1 }
$pyw = (Join-Path (Split-Path -Parent (Get-Command python).Source) 'pythonw.exe')
if (-not (Test-Path $pyw)) { $pyw = (Get-Command pythonw.exe -ErrorAction Stop).Source }
$a = New-ScheduledTaskAction -Execute 'wscript.exe' `
    -Argument ('//B //nologo "' + $vbs + '" "' + $pyw + '" "' + $worker + '"') `
    -WorkingDirectory $Project
# 15-min cadence, off the fleet loop pins (bm-a=8/bm-b=2/bm-c=5):
# worker sweeps land on :07/:22/:37/:52-style phases, away from loop
# S0 pull-rebase windows. Stagger per machine keeps first-writer-wins
# claim files from colliding across machines.
$mid = ''
try {
    $mid = (Get-Content (Join-Path $Project 'fleet\machine.json') -Raw `
        -ErrorAction Stop | ConvertFrom-Json).machine_id
} catch {}
$pinMap = @{ 'bm-a' = 7; 'bm-b' = 12; 'bm-c' = 17 }
$pin = 4
if ($pinMap.ContainsKey($mid)) { $pin = [int]$pinMap[$mid] }
# BUGFIX (r188 bm-c live-fire): Minute%15 domain is 0..14 -- a pin of 17
# can never satisfy "-ne 17" -> infinite first-fire loop on the first
# pin>14 machine. Normalize pin to its phase residue first (17->2 =
# :02/:17/:32/:47 sweeps, distinct from loop pin :05 and other workers).
$phase = $pin % 15
$start = Get-Date -Minute 0 -Second 0
while ($start.Minute % 15 -ne $phase) { $start = $start.AddMinutes(1) }
while ($start -le (Get-Date)) { $start = $start.AddMinutes(15) }
$t = New-ScheduledTaskTrigger -Once -At $start -RepetitionInterval (New-TimeSpan -Minutes 15) -RepetitionDuration (New-TimeSpan -Days 3650)
# ExecutionTimeLimit generous: a shard burn may legitimately run long; a
# killed worker leaves a stale claim which another machine lawfully
# takes over after 20 min (fleet stale law) -- never silent loss.
$s = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -MultipleInstances IgnoreNew -Priority 8 -ExecutionTimeLimit (New-TimeSpan -Minutes 120)
Register-ScheduledTask -TaskName 'Bigmoney-PoolWorker' -Action $a -Trigger $t -Settings $s -Force | Out-Null
Write-Output "registered Bigmoney-PoolWorker (project=$Project, machine=$mid, cadence 15min, first fire $start, priority 8=below-normal)"
