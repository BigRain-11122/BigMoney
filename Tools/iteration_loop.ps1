# Bigmoney iteration loop - OS-scheduled headless round launcher.
# Ported 2026-09-23 from the proven Biggame pattern
# (C:\Fluxgroup\MiniGame\BiuNiYiXia\Tools\iteration_loop.ps1, rounds 000+ live evidence).
# The durable session cron only fires while a Codely CLI window is open - proven
# dead overnight (8.8h, zero beats). This OS task is the only 10-min channel that
# survives closed windows. Every beat: guards -> spawn ONE headless codely round
# (Tools\iteration_prompt.txt driven) -> heartbeat. Round budget v2 = liveness-
# gated: hard cap $RoundTimeoutMinutes (240) + silence kill $RoundSilenceMinutes
# (25 min of ZERO output = hang); overlap prevented by round.lock + task-level
# MultipleInstances=IgnoreNew.
#
# v2 (2026-10-18 liveness-budget surgery, bm-a fleet-ops seat, CEO order
# "solve it at the root"): the 2026-09-23 port carried a 25-min wall-clock
# kill from the MiniGame short-round pattern. Every legitimate long round
# (absorb chains, W-cycle splices, TTS batches) that crossed 25 min was
# tree-killed mid-flight -> the fleet-wide "dead window" epidemic (50+
# absorb generations on bm-c, r995/996/998 on bm-b, r1047 on bm-a; evidence
# run_20261018_064801.log 07:13:02 ROUND TIMEOUT). v2 kills only on
# EVIDENCE: $RoundSilenceMinutes of zero output activity (true hang) or the
# $RoundTimeoutMinutes hard cap. Productive long rounds survive.
#
# F-20261017-01 fix batch (2026-10-18 r1089 bm-c, D-20261018-01 assigned
# BigMoney self-fix; 2026-10-17 18:22-21:02 lane-starvation root cause):
# (1) kills are RECURSIVE TREE kills (old code stopped one level deep --
# grandchildren survived, kept counting into the cloud cap and starved the
# lane 3h) + post-kill self-check logs ZOMBIE_SURVIVOR rows; (2) the
# cloud-cap probes (here + spawn_gate.ps1) apply an AGE FILTER: headless
# -p faces older than the round budget x2 are HUNG, excluded from the cap
# and logged as ZOMBIE_HEADLESS_FACE rows -- cap slots stay with real live
# rounds.
#
# ENCODING RULE: this file must stay PURE ASCII. powershell.exe 5.1 decodes
# BOM-less .ps1 as ANSI/GBK and swallows quote bytes after multibyte sequences.
# All Chinese content lives in Tools\iteration_prompt.txt (UTF-8, read at runtime
# with explicit -Encoding UTF8).
#
# Self-heal recipe (run from an agent round when Get-ScheduledTask
# Bigmoney-IterationLoop is missing - path-agnostic, works on any machine):
#   powershell -NoProfile -ExecutionPolicy Bypass -File Tools\register_loop_task.ps1
param(
    [string]$Project = (Split-Path -Parent $PSScriptRoot),
    [int]$LockMaxAgeMinutes = 40,
    [int]$RoundTimeoutMinutes = 240,
    [int]$RoundSilenceMinutes = 25,
    [switch]$LockProbeOnly
)
$ErrorActionPreference = 'Continue'
Set-Location $Project
$logDir = Join-Path $Project 'logs\iteration-loop'
New-Item -ItemType Directory -Force $logDir | Out-Null
$stamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$runLog = Join-Path $logDir "run_$stamp.log"
$roundOut = Join-Path $logDir "round_$stamp.out"
$roundErr = Join-Path $logDir "round_$stamp.err"
$heart = Join-Path $Project 'logs\probe-heartbeat.txt'

function Log([string]$m) {
    $line = "$(Get-Date -Format 'HH:mm:ss') $m"
    Write-Output $line
    Add-Content -Path $runLog -Value $line -Encoding UTF8
}
function Beat([string]$m) {
    Add-Content -Path $heart -Value "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') iteration: $m" -Encoding UTF8
}

# F-20261017-01 fix 1 (recursive tree kill) + fix 3 (post-kill self-check).
# The 2026-10-17 starvation: one-level kill left deep-tree survivors which
# kept counting into the cloud cap. Collect the descendant chain
# breadth-first (seen-set guards PID-reuse cycles, 256-node bound), kill
# deepest-first, then re-scan: any survivor logs a ZOMBIE_SURVIVOR row for
# the audit lane (fix 3 -- child-clear verification, never silent).
function Kill-RoundTree([int]$rootPid) {
    $seen = @{}
    $frontier = @($rootPid)
    $ordered = @()
    while ($frontier.Count -gt 0 -and $ordered.Count -lt 256) {
        $next = @()
        foreach ($pp in $frontier) {
            $kids = @(Get-CimInstance Win32_Process -Filter "ParentProcessId=$pp" -ErrorAction SilentlyContinue)
            foreach ($k in $kids) {
                if (-not $seen.ContainsKey($k.ProcessId)) {
                    $seen[$k.ProcessId] = $true
                    $ordered += $k.ProcessId
                    $next += $k.ProcessId
                }
            }
        }
        $frontier = $next
    }
    if ($ordered.Count -gt 1) { [array]::Reverse($ordered) }
    foreach ($procId in $ordered) { Stop-Process -Id $procId -Force -ErrorAction SilentlyContinue }
    Stop-Process -Id $rootPid -Force -ErrorAction SilentlyContinue
    return ,$ordered
}
function Stop-RoundTreeChecked([int]$rootPid, [string]$why) {
    $killed = Kill-RoundTree $rootPid
    Log "kill tree ($why): root=$rootPid descendants_killed=$($killed.Count)"
    Start-Sleep -Seconds 2
    $survivors = 0
    foreach ($procId in $killed) {
        if (Get-Process -Id $procId -ErrorAction SilentlyContinue) {
            $survivors++
            Log "ZOMBIE_SURVIVOR pid=$procId survived tree-kill ($why) -- audit lane face"
        }
    }
    if ($survivors -eq 0) { Log "kill tree self-check ($why): 0 survivors (child-clear verified)" }
    return $survivors
}

# ---- single-instance: previous headless round still alive? ----
# D-20260925-03 group lock standard (update_daily.py T-04 F1 precedent):
# lock line "pid=<n> <stamp>" -- live pid => skip at ANY age (no double
# executor), dead pid => immediate takeover (no 40-min dead lag), legacy
# bare stamp => mtime fallback. Grab is atomic (FileStream CreateNew), so
# a concurrent launcher loses the race and skips instead of double-running.
# -LockProbeOnly: report the decision to stdout, mutate nothing, exit 0
# (selftest harness Tools\loop_lock_selftest.ps1 drives a sandbox copy).
$lock = Join-Path $logDir 'round.lock'
$lockPid = 0
$lockAlive = $false
if (Test-Path $lock) {
    $raw = Get-Content -Path $lock -Raw -ErrorAction SilentlyContinue
    if ($raw -and $raw -match 'pid=(\d+)') { $lockPid = [int]$Matches[1] }
    if ($lockPid -gt 0 -and (Get-Process -Id $lockPid -ErrorAction SilentlyContinue)) { $lockAlive = $true }
    $age = ((Get-Date) - (Get-Item $lock).LastWriteTime).TotalMinutes
    if ($LockProbeOnly) {
        if ($lockAlive) { Write-Output "probe: SKIP pid=$lockPid alive age=$([int]$age)min" }
        elseif ($lockPid -gt 0) { Write-Output "probe: TAKE pid=$lockPid dead age=$([int]$age)min" }
        elseif ($age -lt $LockMaxAgeMinutes) { Write-Output "probe: SKIP legacy-fresh age=$([int]$age)min" }
        else { Write-Output "probe: TAKE legacy-stale age=$([int]$age)min" }
        exit 0
    }
    if ($lockAlive) { Log "skip: previous round still running (pid=$lockPid alive, age=$([int]$age)min)"; Beat 'skip (round in flight)'; exit 0 }
    if ($lockPid -gt 0) { Log "lock pid=$lockPid dead (age=$([int]$age)min) - taking over" }
    elseif ($age -ge $LockMaxAgeMinutes) { Log "stale round lock expired (age=$([int]$age)min) - taking over" }
    else { Log "skip: previous round still running (age=$([int]$age)min)"; Beat 'skip (round in flight)'; exit 0 }
    Remove-Item $lock -Force -ErrorAction SilentlyContinue
}
try {
    $fs = New-Object System.IO.FileStream($lock, [System.IO.FileMode]::CreateNew, [System.IO.FileAccess]::Write)
    $sw = New-Object System.IO.StreamWriter($fs)
    $sw.Write("pid=$PID $stamp")
    $sw.Dispose(); $fs.Dispose()
} catch {
    if ($LockProbeOnly) { Write-Output 'probe: SKIP race-lost'; exit 0 }
    Log 'skip: lock grabbed concurrently by another launcher'; Beat 'skip (race lost)'; exit 0
}
if ($LockProbeOnly) { Write-Output "probe: TAKE grabbed pid=$PID"; Remove-Item $lock -Force -ErrorAction SilentlyContinue; exit 0 }

try {
    Log "iteration round start $stamp"

    # O-20261007-2315 idle hard-trigger bookkeeping leg (runs every round,
    # AI-independent counting: probes GREEN-IDLE gate per resource-chain 8.2,
    # detects backlog claims, maintains heartbeat idle_rounds/agenda_starved).
    # Verdict lands in results/idle_trigger.<machine>.json for the round to
    # consume same-round (claim a backlog line / declare --worked). Failures
    # never kill the round: bookkeeping is best-effort, disclosed in the log.
    try {
        $idleOut = & python (Join-Path $Project 'Tools\idle_trigger.py') 2>&1
        Log "idle_trigger: $idleOut"
    } catch { Log "idle_trigger error: $_" }

    # T17 (tech queue r829, bm-c): structural S0.5 orders_ack diff scan
    # (round-start face of the FLEET-OPS sec.3 receipt-closure double-scan;
    # unacked -> exit 3, names + JSON face land in
    # results/orders_ack_scan.<machine>.json for the round session to
    # consume as P0 dispatch debt; stale legacy-format acks = soft notes).
    # Read-only; failures never kill the round (best-effort, logged).
    try {
        $oasOut = & python (Join-Path $Project 'Tools\orders_ack_scan.py') 2>&1
        Log "orders_ack_scan: $oasOut"
    } catch { Log "orders_ack_scan error: $_" }

    $codelyPath = (Get-Command codely -ErrorAction SilentlyContinue).Source
    if (-not $codelyPath) { Log 'FATAL: codely not on PATH for this context'; Beat 'error codely missing'; exit 2 }
    Log "codely=$codelyPath"

    # Round prompt (Chinese) lives outside this file - see ENCODING RULE above.
    $promptFile = Join-Path $Project 'Tools\iteration_prompt.txt'
    if (-not (Test-Path $promptFile)) { Log 'FATAL: iteration_prompt.txt missing'; Beat 'error prompt file missing'; exit 2 }
    $prompt = (Get-Content -Raw -Encoding UTF8 $promptFile).Trim()
    if ($prompt.Length -lt 50) { Log 'FATAL: iteration_prompt.txt too short'; Beat 'error prompt file empty'; exit 2 }

    # C-20261015-03 sec.3 spawn-gate preflight (cloud concurrency cap v1.0,
    # O-20261015-1800/1834): before igniting a cloud LLM session, count live
    # AUTONOMOUS codely faces only (headless -p prompt rounds). C-20261016-05
    # exemption fix: interactive Cowork windows (--experimental-acp) are
    # exempt per O-20261015-1800 sec.2 - counting them starved every round
    # whenever two chat windows were open. >=2 live => this tick yields with
    # a ledger line; next grid slot auto-retries. Fail-open per spec: probe
    # crash never blocks the line.
    # F-20261017-01 fix 2 (age filter): headless -p faces older than the
    # round budget x2 ($RoundTimeoutMinutes x2 = 480min default) are HUNG,
    # not workload: excluded from the cap + logged as ZOMBIE_HEADLESS_FACE
    # rows (2026-10-17 root cause: timeout-surviving faces ate the cap and
    # starved the lane ~3h; cap slots stay with real live rounds).
    try {
        $capBudgetMin = 2 * $RoundTimeoutMinutes
        $faces = @(Get-CimInstance Win32_Process -Filter "Name='codely.exe'" -ErrorAction SilentlyContinue |
            Where-Object { $_.CommandLine -match ' -p "' })
        $zombies = @($faces | Where-Object { $_.CreationDate -and ((Get-Date) - $_.CreationDate).TotalMinutes -gt $capBudgetMin })
        $live = $faces.Count - $zombies.Count
        foreach ($z in $zombies) {
            $ageMin = [int]((Get-Date) - $z.CreationDate).TotalMinutes
            Log "ZOMBIE_HEADLESS_FACE pid=$($z.ProcessId) age_min=$ageMin over_budget_x2=${capBudgetMin}min -- excluded from cloud cap (F-20261017-01 fix 2)"
        }
        if ($zombies.Count -gt 0) {
            Add-Content -Path (Join-Path $logDir 'zombie_faces.log') -Value ("$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') | ZOMBIE_HEADLESS_FACES excluded=$($zombies.Count) counted_live=$live") -Encoding ASCII
        }
        if ($live -ge 2) {
            Log "CLOUD_CAP_DEFER live=$live zombies_excluded=$($zombies.Count) (cloud cap v1.0 C-20261015-03 sec.2)"
            Add-Content -Path (Join-Path $logDir 'cloud_cap_defer.log') -Value ("$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') | CLOUD_CAP_DEFER live=$live zombies_excluded=$($zombies.Count)") -Encoding ASCII
            Beat "cloud cap defer live=$live"
            exit 0
        }
        Log "cloud-cap preflight OK live=$live zombies_excluded=$($zombies.Count)"
    } catch { Log "cloud-cap preflight probe failed (fail-open): $_" }

    # Single-line prompt, no embedded double quotes (Start-Process argument passing).
    if ($prompt.Contains('"')) { $prompt = $prompt.Replace('"', "'") }
    $argLine = '-y -p "' + $prompt + '"'

    # O-20261015-1834 spawn-gate preflight (C-20261015-03 sec.3 spec): cloud
    # concurrency cap check BEFORE igniting this round's codely session.
    # DEFER (rc=3) = yield this grid slot to the per-machine cap (<=2 live
    # autonomous cloud sessions); the next PT10M fire retries automatically.
    # Fail-open: probe faults never skip a round (gate exits 0 = GO).
    $gate = & (Join-Path $PSScriptRoot 'spawn_gate.ps1') -Lane 'bigmoney-loop'
    $gateRc = $LASTEXITCODE
    Log "spawn_gate: rc=$gateRc $gate"
    if ($gateRc -eq 3) {
        Log 'skip: cloud concurrency cap defer - next grid slot retries'
        Beat 'skip (cloud cap defer)'
        exit 0
    }

    Log "spawning headless round (hard-cap ${RoundTimeoutMinutes}min, silence-kill ${RoundSilenceMinutes}min, prompt_chars=$($prompt.Length), out=$roundOut)"
    # T0 CLOUD-OFF guard (CEO 2026-10-20): automation is local-only; never spawn the cloud CLI.
    $__co = $PSScriptRoot
    while ($__co -and -not (Test-Path (Join-Path $__co 'cph4\fleet\CLOUD-OFF-LOCAL-ONLY-v1.md'))) { $__co = Split-Path -Parent $__co }
    if ($__co) {
        $__cl = Join-Path $__co 'media\logs\cloud-off-suppressed.log'
        $__cd = Split-Path -Parent $__cl
        if (-not (Test-Path $__cd)) { New-Item -ItemType Directory -Force -Path $__cd | Out-Null }
        Add-Content -Path $__cl -Value ((Get-Date -Format 'yyyy-MM-dd HH:mm:ss') + ' | ' + [System.IO.Path]::GetFileName($PSCommandPath) + ' | suppressed cloud round (T0)') -Encoding UTF8
        exit 0
    }
    $p = Start-Process -FilePath $codelyPath -ArgumentList $argLine -WorkingDirectory $Project -PassThru -NoNewWindow -RedirectStandardOutput $roundOut -RedirectStandardError $roundErr
    $null = $p.Handle   # materialize handle so ExitCode is readable
    # v2 liveness budget: poll in 30s slices. "Activity" = the round's stdout/stderr
    # redirect files gaining bytes. Kill ONLY on evidence of a hang (silent for
    # $RoundSilenceMinutes) or the $RoundTimeoutMinutes hard cap. A productive
    # long round streams tool output continuously and is never killed by wall
    # clock alone (the 25-min guillotine that caused the dead-window epidemic
    # is gone; see v2 header note).
    $startAt = Get-Date
    $lastMove = Get-Date
    $lastSize = -1L
    while (-not $p.WaitForExit(30000)) {
        $size = 0L
        foreach ($f in @($roundOut, $roundErr)) {
            try { $fi = Get-Item $f -ErrorAction SilentlyContinue; if ($fi) { $size += $fi.Length } } catch { }
        }
        if ($size -ne $lastSize) { $lastSize = $size; $lastMove = Get-Date }
        $silentMin = ((Get-Date) - $lastMove).TotalMinutes
        $totalMin = ((Get-Date) - $startAt).TotalMinutes
        if ($silentMin -ge $RoundSilenceMinutes) {
            Log "ROUND SILENCE-KILL: no output for $([int]$silentMin)min (total $([int]$totalMin)min) - killing headless process tree"
            try { $null = Stop-RoundTreeChecked $p.Id 'silence-kill' } catch { Log "kill failed: $_" }
            Beat "round silence-killed (no output $([int]$silentMin)min, total $([int]$totalMin)min)"
            exit 3
        }
        if ($totalMin -ge $RoundTimeoutMinutes) {
            Log "ROUND HARD-CAP after ${RoundTimeoutMinutes}min - killing headless process tree"
            try { $null = Stop-RoundTreeChecked $p.Id 'hard-cap' } catch { Log "kill failed: $_" }
            Beat "round hard-cap killed (age over ${RoundTimeoutMinutes}min)"
            exit 3
        }
    }
    $p.Refresh()
    Log "headless round finished exit=$($p.ExitCode) (ran $([int]((Get-Date) - $startAt).TotalMinutes)min)"

    # T6 (tech queue r812, bm-c): structural idle_trigger --auto declare leg.
    # Deterministic same-round clear of the two-read idle streak: pool shard
    # claims by this machine, or session commits touching non-bookkeeping
    # faces. Backstop for the hand --claimed/--worked semantic on non-bm-a
    # carrier machines; failures never kill the round (best-effort, logged).
    try {
        $idleAutoOut = & python (Join-Path $Project 'Tools\idle_trigger.py') --auto 2>&1
        Log "idle_trigger --auto: $idleAutoOut"
    } catch { Log "idle_trigger --auto error: $_" }

    Beat "round done exit=$($p.ExitCode)"
    exit $p.ExitCode
}
finally {
    Remove-Item $lock -Force -ErrorAction SilentlyContinue
}
