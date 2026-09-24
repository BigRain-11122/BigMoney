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
# C7 (O-20260924-1626): watermark closed-loop -- judgment becomes disposal.
#   RED = >=3 trailing watermark samples with py<70% while runnable work exists
#   (open tickets / bandit open). Actions: zombie python kill (3-check guarded,
#   known-batch whitelist only), escalation file results\watermark_red.json for
#   dashboards + round-report P0 first line, queue-lane diagnosis. -C7Only runs
#   ONLY the C7 leg with overridable paths/thresholds (injection acceptance
#   tests use it; production schtasks calls pass no args).

param(
    [switch]$C7Only,
    [string]$WmFile = '',
    [string]$RedFile = '',
    [string]$PyStateFile = '',
    [double]$ZombieAgeMin = 45,
    [double]$ZombieCpuDeltaSec = 5.0,
    [int]$MinRedSamples = 3,
    [string[]]$ZombieLanes = @()
)

$ErrorActionPreference = 'Continue'
$Project = Split-Path -Parent $PSScriptRoot
$LogsDir = Join-Path $Project 'logs'
$WdLog = Join-Path $LogsDir 'watchdog.log'
$Lock = Join-Path $LogsDir 'watchdog.lock'

function Log([string]$msg) {
    $line = ("{0} {1}" -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'), $msg)
    Add-Content -Path $WdLog -Value $line -Encoding ASCII
}

# ---- C7: watermark closed-loop (judgment -> disposal) ----
# Zombie = python process older than $ZombieAgeMin whose accumulated CPU grew
# less than $ZombieCpuDeltaSec since the previous watchdog tick. 3-check guard:
#   (1) known checkpoint-able batch lane only (whitelist below; unknown lanes
#       and interactive-session processes are NEVER killed -- conservative);
#   (2) interactive-session guard: command lines containing codely/claude/node
#       are exempt even if they also match a batch lane;
#   (3) every kill + resume routing is logged (watchdog.log + red-flag file).
# Resume routing: killed lanes are revived by their OWN existing healers
# (S6 gates re-spawn, C4/C5 own the pull/p1c chains) -- C7 never duplicates a
# relaunch, it only clears the stuck process so the checkpoint machinery takes over.
function Invoke-C7 {
    param(
        [string]$ProjectDir,
        [string]$LogsDirIn,
        [string]$WmFileIn = '',
        [string]$RedFileIn = '',
        [string]$PyStateIn = '',
        [double]$AgeMin = 45,
        [double]$CpuDeltaSec = 5.0,
        [int]$MinSamples = 3,
        [string[]]$ZombieLanesIn = @()
    )
    if (-not $WmFileIn) { $WmFileIn = Join-Path $ProjectDir 'results\watermark.jsonl' }
    if (-not $RedFileIn) { $RedFileIn = Join-Path $ProjectDir 'results\watermark_red.json' }
    if (-not $PyStateIn) { $PyStateIn = Join-Path $LogsDirIn 'watchdog_py_state.json' }
    $MyIdC7 = ''
    $mf = Join-Path $ProjectDir 'fleet\machine.json'
    if (Test-Path $mf) { try { $MyIdC7 = (Get-Content $mf -Raw | ConvertFrom-Json).machine_id } catch { $MyIdC7 = '' } }

    # -- sample C7: read trailing watermark samples, decide RED --
    $red = $false
    $lane = 'insufficient_history'
    $killed = @()
    $pySeries = @()
    if (Test-Path $WmFileIn) {
        $lines = @(Get-Content $WmFileIn -Tail 8 | Where-Object { $_ -match 'py_cpu_pct' })
        if ($lines.Count -ge $MinSamples) {
            $tail = @($lines | Select-Object -Last $MinSamples)
            $allLow = $true
            $hasWork = $false
            foreach ($l in $tail) {
                try {
                    $s = $l | ConvertFrom-Json
                    $pySeries += ('{0}' -f [double]$s.py_cpu_pct)
                    if ([double]$s.py_cpu_pct -ge 70) { $allLow = $false }
                    if ([int]$s.open_tickets -gt 0 -or [int]$s.bandit_open -gt 0) { $hasWork = $true }
                } catch { $allLow = $false }
            }
            if ($allLow -and $hasWork) {
                $red = $true
                $lane = 'runnable-work-idle-low-cpu (escalate: round-report P0 + dashboard red; GM waiver per O-1612)'
            } else {
                $lane = 'healthy'
            }
        }
    }

    # -- zombie sweep (every tick, independent of RED: disposal = judgment) --
    $prev = $null
    if (Test-Path $PyStateIn) {
        try { $prev = Get-Content $PyStateIn -Raw | ConvertFrom-Json } catch { $prev = $null }
    }
    $cur = @{}
    $zombieLanes = @('backfill_ext_slots','p1c_stock_ic_batch','t18_deep_axis','update_moneyflow','lof_census','nav_backfill','c7_zombie_test')
    if ($ZombieLanesIn.Count -gt 0) { $zombieLanes = $ZombieLanesIn }   # test lane narrowing (injection safety)
    $interactiveGuard = @('codely','claude','node')
    $procs = Get-CimInstance Win32_Process -Filter "Name='python.exe' or Name='pythonw.exe'" -ErrorAction SilentlyContinue
    foreach ($p in $procs) {
        $gp = Get-Process -Id $p.ProcessId -ErrorAction SilentlyContinue
        # r100 pitfall law: Get-Process can transiently return empty for a live
        # separated process -- CPU sample via CIM second opinion before judging.
        $cpu = -1.0
        if ($gp -and $null -ne $gp.CPU) { $cpu = [double]$gp.CPU }
        elseif ($p) { try { $cpu = [math]::Round([double]$p.KernelModeTime / 10000000 + [double]$p.UserModeTime / 10000000, 3) } catch { $cpu = -1.0 } }
        $pidStr = [string]$p.ProcessId
        $cur[$pidStr] = $cpu
        $cmd = [string]$p.CommandLine
        $interactive = $false
        foreach ($g in $interactiveGuard) { if ($cmd -like ('*' + $g + '*')) { $interactive = $true } }
        $knownLane = $null
        foreach ($zl in $zombieLanes) { if ($cmd -like ('*' + $zl + '*')) { $knownLane = $zl } }
        $prevCpu = $null
        if ($prev) {
            $prop = $prev.PSObject.Properties[$pidStr]
            if ($prop) { $prevCpu = [double]$prop.Value }
        }
        if (-not $knownLane) { continue }           # check 1: whitelist only
        if ($interactive) { continue }              # check 2: session guard
        $ageNowMin = 0.0
        try { $ageNowMin = ((Get-Date) - $p.CreationDate).TotalMinutes } catch { continue }
        if ($ageNowMin -le $AgeMin) { continue }     # age gate
        if ($null -eq $prevCpu -or $cpu -lt 0) { continue }  # need two samples
        if (($cpu - $prevCpu) -lt $CpuDeltaSec) {
            Log ('C7 ZOMBIE KILL pid=' + $pidStr + ' lane=' + $knownLane + (' age={0:N0}min cpu_delta={1:N2}s (3-check passed)' -f $ageNowMin, ($cpu - $prevCpu)) + ' resume=existing-healers(S6/C4/C5)')
            try {
                Stop-Process -Id $p.ProcessId -Force -ErrorAction Stop
                $killed += ('pid=' + $pidStr + ' lane=' + $knownLane)
            } catch { Log ('C7 kill FAILED pid=' + $pidStr + ' : ' + $_.Exception.Message) }
        }
    }
    try { $cur | ConvertTo-Json -Depth 3 | Set-Content -Path $PyStateIn -Encoding ASCII } catch { Log ('C7 state write failed: ' + $_.Exception.Message) }

    # -- red-flag file (always written: dashboards read live state) --
    $out = [ordered]@{
        ts      = (Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
        machine = $MyIdC7
        red     = $red
        lane    = $lane
        py_series_tail = @($pySeries)
        zombies_killed  = @($killed)
        order_ref = 'O-20260924-1626 R1/R2/R3'
    }
    try { $out | ConvertTo-Json -Depth 4 | Set-Content -Path $RedFileIn -Encoding ASCII } catch { Log ('C7 red-file write failed: ' + $_.Exception.Message) }
    if ($red) {
        Log ('C7 WATERMARK RED lane=' + $lane + ' py_tail=' + ($pySeries -join ','))
    } else {
        Log ('C7 watermark ' + $lane + ' py_tail=' + ($pySeries -join ','))
    }
}

# -C7Only: injection-acceptance path -- run ONLY the C7 leg (no lock taken,
# no C1-C6 touched, all paths/thresholds overridable from the command line).
if ($C7Only) {
    Invoke-C7 -ProjectDir (Split-Path -Parent $PSScriptRoot) -LogsDirIn (Join-Path (Split-Path -Parent $PSScriptRoot) 'logs') `
        -WmFileIn $WmFile -RedFileIn $RedFile -PyStateIn $PyStateFile -AgeMin $ZombieAgeMin -CpuDeltaSec $ZombieCpuDeltaSec -MinSamples $MinRedSamples -ZombieLanesIn $ZombieLanes
    exit 0
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

    # ---- C8: autofill task heal (T-36, O-20260924-2100 s2.2) ----
    $afInfo = schtasks /query /tn 'Bigmoney-Autofill' 2>$null
    if ($LASTEXITCODE -ne 0) {
        Log 'C8 autofill task MISSING -> re-registering'
        $regAf = Join-Path $Project 'Tools\register_autofill_task.ps1'
        if (Test-Path $regAf) {
            powershell -NoProfile -ExecutionPolicy Bypass -File $regAf | Out-Null
            Log ('C8 autofill re-register exit={0}' -f $LASTEXITCODE)
        } else {
            Log 'C8 autofill register script absent -> skip (pre-T-36 clone)'
        }
    } else {
        Log 'C8 autofill task present'
    }

    # ---- C9: post-review daily leg (T-37, O-20260924-2115 s2) ----
    # Once per day: if the review ledger has no row dated today, run the
    # deterministic reviewer (zero-LLM). Read-only gate on ledger mtime.
    $prLedger = Join-Path $Project 'results\post_review.jsonl'
    $prRun = $false
    if (Test-Path $prLedger) {
        $lastLine = Get-Content $prLedger -Tail 1 -ErrorAction SilentlyContinue
        if ($lastLine -match '"ts": "(\d{4}-\d{2}-\d{2})') {
            if ($Matches[1] -ne (Get-Date -Format 'yyyy-MM-dd')) { $prRun = $true }
        } else { $prRun = $true }
    } else { $prRun = $true }
    if ($prRun -and (Test-Path (Join-Path $Project 'Tools\post_review.py'))) {
        Log 'C9 post-review ledger stale/absent -> running reviewer'
        python (Join-Path $Project 'Tools\post_review.py') 'run' 2>&1 | Out-Null
        Log ('C9 reviewer exit={0}' -f $LASTEXITCODE)
    } else {
        Log 'C9 post-review fresh (today) or reviewer absent -> no action'
    }

    # ---- C7: watermark closed-loop (O-20260924-1626 R1/R2/R3) ----
    Invoke-C7 -ProjectDir $Project -LogsDirIn $LogsDir -AgeMin $ZombieAgeMin -CpuDeltaSec $ZombieCpuDeltaSec -MinSamples $MinRedSamples
} catch {
    Log ('EXCEPTION: ' + $_.Exception.Message)
} finally {
    Remove-Item $Lock -ErrorAction SilentlyContinue
}
exit 0
