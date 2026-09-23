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
    [int]$RoundTimeoutMinutes = 25
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
$lock = Join-Path $logDir 'round.lock'
if (Test-Path $lock) {
    $age = ((Get-Date) - (Get-Item $lock).LastWriteTime).TotalMinutes
    if ($age -lt $LockMaxAgeMinutes) { Log "skip: previous round still running (age=$([int]$age)min)"; Beat 'skip (round in flight)'; exit 0 }
    Log "stale round lock expired (age=$([int]$age)min) - taking over"
}
Set-Content -Path $lock -Value $stamp -Encoding UTF8

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
