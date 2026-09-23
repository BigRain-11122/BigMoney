# watchdog.ps1 -- machine-local self-heal layer (zero-token, pure shell).
# PURPOSE: heal the healer. The 10-min iteration loop already self-heals its
# own ROUNDS (round.lock + 25min cap + orphan rescue). This watchdog covers
# the cases NO round can fix:
#   C1  Bigmoney-IterationLoop task deleted/corrupted  -> re-register (chicken-egg: task gone = no round can heal it)
#   C2  loop stalls (no fire for 45+ min)              -> kick with schtasks /run
#   C3  fresh reboot, grid not caught up               -> kick with schtasks /run
#   C4  margin/ext-slots pull chain dead + gates FAIL  -> relaunch backfill_ext_slots.py all (checkpoint resume, LANE OWNER ONLY)
#   C5  P-1c stock IC batch chain dead + unfinished    -> relaunch phase chain (checkpoint resume, LANE OWNER ONLY)
#   C6  watchdog task self-re-registration (mutual heal: rounds heal loop+watchdog via S7, watchdog heals both too)
# Rules: idempotent; NEVER blocks (always exit 0); all decisions logged to
# logs\watchdog.log; task-existence via schtasks /query only (transient CIM
# trap documented 2026-09-23); single instance via 15-min-stale lock file.
# PATH-AGNOSTIC: all paths derived from this file's location. Pure ASCII.

$ErrorActionPreference = 'Continue'
$Project = Split-Path -Parent $PSScriptRoot
$LogsDir = Join-Path $Project 'logs'
$WdLog = Join-Path $LogsDir 'watchdog.log'
$Lock = Join-Path $LogsDir 'watchdog.lock'

function Log([string]$msg) {
    $line = ("{0} {1}" -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'), $msg)
    Add-Content -Path $WdLog -Value $line -Encoding ASCII
}

# ---- single instance (stale lock takeover after 15 min) ----
if (Test-Path $Lock) {
    $age = (Get-Date) - (Get-Item $Lock).LastWriteTime
    if ($age.TotalMinutes -lt 15) { exit 0 }
}
Set-Content -Path $Lock -Value (Get-Date -Format 'yyyy-MM-dd HH:mm:ss') -Encoding ASCII

try {
    # ---- C1/C2/C3: iteration loop task heal ----
    $taskName = 'Bigmoney-IterationLoop'
    $taskInfo = schtasks /query /tn $taskName 2>$null
    $taskExists = $LASTEXITCODE -eq 0
    if (-not $taskExists) {
        Log 'C1 loop task MISSING -> re-registering'
        $reg = Join-Path $Project 'Tools\register_loop_task.ps1'
        powershell -NoProfile -ExecutionPolicy Bypass -File $reg | Out-Null
        Log ('C1 re-register exit={0}' -f $LASTEXITCODE)
    } else {
        Log 'C1 loop task present'
    }

    $lastActivity = Get-Date '2000-01-01'
    Get-ChildItem (Join-Path $LogsDir 'iteration-loop') -Filter 'run_*.log' -ErrorAction SilentlyContinue |
        ForEach-Object { if ($_.LastWriteTime -gt $lastActivity) { $lastActivity = $_.LastWriteTime } }
    Get-ChildItem (Join-Path $LogsDir 'iteration-loop') -Filter 'round_*.out' -ErrorAction SilentlyContinue |
        ForEach-Object { if ($_.LastWriteTime -gt $lastActivity) { $lastActivity = $_.LastWriteTime } }
    $idleMin = ((Get-Date) - $lastActivity).TotalMinutes
    $uptime = (Get-Date) - (Get-CimInstance Win32_OperatingSystem).LastBootUpTime
    $bootedRecently = $uptime.TotalMinutes -lt 30

    if ($idleMin -gt 45) {
        Log ('C2 loop idle {0:N0} min -> kicking task' -f $idleMin)
        schtasks /run /tn $taskName | Out-Null
        Log ('C2 kick exit={0}' -f $LASTEXITCODE)
    } elseif ($bootedRecently -and $idleMin -gt 20) {
        Log ('C3 fresh boot ({0:N0} min uptime) + idle {1:N0} min -> kicking task' -f $uptime.TotalMinutes, $idleMin)
        schtasks /run /tn $taskName | Out-Null
        Log ('C3 kick exit={0}' -f $LASTEXITCODE)
    } else {
        Log ('C2/C3 loop healthy (last activity {0:N0} min ago, uptime {1:N0} min)' -f $idleMin, $uptime.TotalMinutes)
    }

    # ---- process liveness helper (CommandLine match over python processes) ----
    function Test-ProcAlive([string]$needle) {
        $procs = Get-CimInstance Win32_Process -Filter "Name like '%python%'" -ErrorAction SilentlyContinue
        foreach ($p in $procs) {
            if ($p.CommandLine -and ($p.CommandLine -like ('*' + $needle + '*'))) { return $true }
        }
        return $false
    }

    # ---- lane ownership guard (C4/C5) ----
    # C4 ext-slots pull + C5 P-1c batch chains are bm-b lanes (MSG-2155 claim lock;
    # P-1c batch owner per r49/r50). Synced status/checkpoint files exist on EVERY
    # machine, but the gitignored data caches live on the OWNER only: on non-owners
    # gates always fail (no local data), and a relaunch would duplicate EM pulls /
    # batch runs from scratch and clobber tracked status files the owner writes.
    # Non-owners log and skip both. If a lane ever migrates, update $BatchLaneOwner
    # in the same commit that moves the lane.
    $MyId = ''
    $mf = Join-Path $Project 'fleet\machine.json'
    if (Test-Path $mf) {
        try { $MyId = (Get-Content $mf -Raw | ConvertFrom-Json).machine_id } catch { $MyId = '' }
    }
    $BatchLaneOwner = 'bm-b'
    $OwnBatchLanes = ($MyId -eq $BatchLaneOwner)

    # ---- C4: margin/ext-slots pull chain (lane owner only) ----
    if (-not $OwnBatchLanes) {
        Log ('C4 skipped on ' + $MyId + ': ext-slots pull lane owned by ' + $BatchLaneOwner)
    } else {
    $backfillAlive = Test-ProcAlive 'backfill_ext_slots'
    if ($backfillAlive) {
        Log 'C4 ext-slots pull chain ALIVE -> no action'
    } else {
        $gates = Join-Path $Project 'scripts\p1d_ext_slots_ic.py'
        if (Test-Path $gates) {
            python $gates gates 2>$null | Out-Null
            $g = $LASTEXITCODE
            if ($g -eq 0) {
                Log 'C4 pull chain dead but ALL GATES PASS (complete for real) -> no action'
            } elseif ($g -eq 2) {
                Log 'C4 pull chain dead + gates FAIL (exit 2) -> relaunching backfill_ext_slots.py all'
                $py = Join-Path $Project 'scripts\backfill_ext_slots.py'
                Start-Process -WindowStyle Hidden -FilePath 'pythonw.exe' `
                    -ArgumentList ('"' + $py + '" all') -WorkingDirectory $Project
                Log 'C4 relaunch issued'
            } else {
                Log ('C4 gates exit={0} (unknown) -> NO action (honest no-op)' -f $g)
            }
        } else {
            Log 'C4 gates script missing -> skip'
        }
    }
    }

    # ---- C5: P-1c stock IC batch chain (lane owner only) ----
    if (-not $OwnBatchLanes) {
        Log ('C5 skipped on ' + $MyId + ': P-1c batch lane owned by ' + $BatchLaneOwner)
    } else {
    $p1cAlive = Test-ProcAlive 'p1c_stock_ic_batch'
    $finalJson = Join-Path $Project 'results\shortline\p1c_stock_ic.json'
    if ($p1cAlive) {
        Log 'C5 P-1c batch chain ALIVE -> no action'
    } elseif (Test-Path $finalJson) {
        # r61: the GTJA-leg finalize predates the WQ leg, so the final JSON
        # alone is no longer completeness proof. Complete = meta.wq_complete
        # true (finalize writes it once all 82 WQ checkpoints aggregate).
        $wqComplete = $false
        try { $wqComplete = [bool]((Get-Content $finalJson -Raw | ConvertFrom-Json).meta.wq_complete) } catch { $wqComplete = $false }
        if ($wqComplete) {
            Log 'C5 P-1c final JSON present + wq_complete (batch complete) -> no action'
        } else {
            $runner = Join-Path $Project 'scripts\p1c_stock_ic_batch.py'
            $chainLog = Join-Path $LogsDir 'p1c_chain_watchdog.log'
            $phases = 'run-wq', 'finalize'
            Log 'C5 P-1c WQ leg unfinished (final JSON pre-wq) -> resuming from run-wq'
            $chainCmd = ($phases | ForEach-Object { 'python -u "' + $runner + '" ' + $_ }) -join ' >> "' + $chainLog + '" 2>&1 && '
            $chainCmd = 'cmd /c "' + $chainCmd + ' >> "' + $chainLog + '" 2>&1"'
            Start-Process -WindowStyle Hidden -FilePath 'cmd.exe' -ArgumentList $chainCmd -WorkingDirectory $Project
            Log 'C5 resume chain issued'
        }
    } else {
        $nullsJson = Join-Path $Project 'results\shortline\p1c_nulls.json'
        $partialDir = Join-Path $Project 'results\shortline\p1c_partial'
        $hasWork = (Test-Path $nullsJson) -or (Test-Path $partialDir)
        if (-not $hasWork) {
            Log 'C5 P-1c not started (no nulls/checkpoints) -> NOT reviving (rounds own initial launch)'
        } else {
            $runner = Join-Path $Project 'scripts\p1c_stock_ic_batch.py'
            $chainLog = Join-Path $LogsDir 'p1c_chain_watchdog.log'
            if (Test-Path $nullsJson) {
                $phases = 'run-gtja', 'run-wq', 'finalize'
                Log 'C5 P-1c chain dead mid-batch (nulls done) -> resuming from run-gtja'
            } else {
                $phases = 'run-nulls', 'run-gtja', 'run-wq', 'finalize'
                Log 'C5 P-1c chain dead mid-batch (nulls incomplete) -> resuming from run-nulls'
            }
            $chainCmd = ($phases | ForEach-Object { 'python -u "' + $runner + '" ' + $_ }) -join ' >> "' + $chainLog + '" 2>&1 && '
            $chainCmd = 'cmd /c "' + $chainCmd + ' >> "' + $chainLog + '" 2>&1"'
            Start-Process -WindowStyle Hidden -FilePath 'cmd.exe' -ArgumentList $chainCmd -WorkingDirectory $Project
            Log 'C5 resume chain issued'
        }
    }
    }

    # ---- C6: watchdog task self-heal (idempotent -Force) ----
    $wdInfo = schtasks /query /tn 'Bigmoney-LoopWatchdog' 2>$null
    if ($LASTEXITCODE -ne 0) {
        Log 'C6 watchdog task MISSING -> re-registering'
        $regWd = Join-Path $Project 'Tools\register_watchdog_task.ps1'
        powershell -NoProfile -ExecutionPolicy Bypass -File $regWd | Out-Null
        Log ('C6 watchdog re-register exit={0}' -f $LASTEXITCODE)
    } else {
        Log 'C6 watchdog task present'
    }
} catch {
    Log ('EXCEPTION: ' + $_.Exception.Message)
} finally {
    Remove-Item $Lock -ErrorAction SilentlyContinue
}
exit 0
