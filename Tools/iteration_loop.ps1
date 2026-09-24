# Bigmoney iteration loop - OS-scheduled headless round launcher.
# Ported 2026-09-23 from the proven Biggame pattern
# (E:\Minigame\BiuNiYiXia\Tools\iteration_loop.ps1, rounds 000+ live evidence).
# The durable session cron only fires while a Codely CLI window is open - proven
# dead overnight (8.8h, zero beats). This OS task is the only 10-min channel that
# survives closed windows. Every beat: guards -> spawn ONE headless codely round
# (Tools\iteration_prompt.txt driven) -> heartbeat. Round budget 25 min; overlap
# prevented by round.lock + task-level MultipleInstances=IgnoreNew.
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
    [int]$RoundTimeoutMinutes = 25,
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

    $codelyPath = (Get-Command codely -ErrorAction SilentlyContinue).Source
    if (-not $codelyPath) { Log 'FATAL: codely not on PATH for this context'; Beat 'error codely missing'; exit 2 }
    Log "codely=$codelyPath"

    # Round prompt (Chinese) lives outside this file - see ENCODING RULE above.
    $promptFile = Join-Path $Project 'Tools\iteration_prompt.txt'
    if (-not (Test-Path $promptFile)) { Log 'FATAL: iteration_prompt.txt missing'; Beat 'error prompt file missing'; exit 2 }
    $prompt = (Get-Content -Raw -Encoding UTF8 $promptFile).Trim()
    if ($prompt.Length -lt 50) { Log 'FATAL: iteration_prompt.txt too short'; Beat 'error prompt file empty'; exit 2 }

    # Single-line prompt, no embedded double quotes (Start-Process argument passing).
    if ($prompt.Contains('"')) { $prompt = $prompt.Replace('"', "'") }
    $argLine = '-y -p "' + $prompt + '"'
    Log "spawning headless round (budget ${RoundTimeoutMinutes}min, prompt_chars=$($prompt.Length), out=$roundOut)"
    $p = Start-Process -FilePath $codelyPath -ArgumentList $argLine -WorkingDirectory $Project -PassThru -NoNewWindow -RedirectStandardOutput $roundOut -RedirectStandardError $roundErr
    $null = $p.Handle   # materialize handle so ExitCode is readable
    if (-not $p.WaitForExit($RoundTimeoutMinutes * 60 * 1000)) {
        Log "ROUND TIMEOUT after ${RoundTimeoutMinutes}min - killing headless process tree"
        try {
            Get-CimInstance Win32_Process -Filter "ParentProcessId=$($p.Id)" -ErrorAction SilentlyContinue |
                ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }
            Stop-Process -Id $p.Id -Force -ErrorAction SilentlyContinue
        } catch { Log "kill failed: $_" }
        Beat "round timeout killed (age over ${RoundTimeoutMinutes}min)"
        exit 3
    }
    $p.Refresh()
    Log "headless round finished exit=$($p.ExitCode)"
    Beat "round done exit=$($p.ExitCode)"
    exit $p.ExitCode
}
finally {
    Remove-Item $lock -Force -ErrorAction SilentlyContinue
}
