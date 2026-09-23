# Money auto-guardian watchdog.
# Checks every invocation: if no `python run.py auto` process is alive, start a detached one.
# PAUSE: create file state\watchdog_pause to suppress auto-restart
#        (e.g. before manual arena/league/evolve runs or code maintenance).
# RESUME: delete that file; next scheduled check (<=5 min) pulls the guardian back up.
# Scheduled task "MoneyAutoGuardian" runs this script at logon and every 5 minutes.
$ErrorActionPreference = 'Stop'
$Root  = 'C:\Users\sjs20\Desktop\Money'
$Py    = 'C:\Users\sjs20\AppData\Local\Programs\Python\Python314\python.exe'
$Log   = Join-Path $Root 'logs\watchdog.log'
$Pause = Join-Path $Root 'state\watchdog_pause'

function Write-WdLog([string]$msg) {
    try {
        Add-Content -Path $Log -Value ("{0} {1}" -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'), $msg)
    } catch { }
}

try {
    if (Test-Path $Pause) { Write-WdLog 'paused (state\watchdog_pause exists), skip'; return }
    if (-not (Test-Path $Py)) { Write-WdLog "python not found: $Py"; return }

    # --- rolling backup of state.json (~every 30 min, keep newest 48 = 24h) ---
    $BkDir = Join-Path $Root 'state\backups'
    $StateFile = Join-Path $Root 'state\state.json'
    if (Test-Path $StateFile) {
        $latest = Get-ChildItem $BkDir -Filter 'state_*.json' -ErrorAction SilentlyContinue |
                  Sort-Object LastWriteTime -Descending | Select-Object -First 1
        if (-not $latest -or ((Get-Date) - $latest.LastWriteTime).TotalMinutes -ge 30) {
            New-Item $BkDir -ItemType Directory -Force | Out-Null
            Copy-Item $StateFile (Join-Path $BkDir ("state_{0}.json" -f (Get-Date -Format 'yyyyMMdd_HHmm'))) -Force
            Get-ChildItem $BkDir -Filter 'state_*.json' | Sort-Object LastWriteTime -Descending |
                Select-Object -Skip 48 | Remove-Item -Force -ErrorAction SilentlyContinue
        }
    }

    $alive = @(Get-CimInstance Win32_Process -Filter "Name = 'python.exe'" |
        Where-Object { $_.CommandLine -match 'run\.py\s+auto' })
    if ($alive.Count -gt 0) { return }   # single-guardian rule: never start a second one

    $stamp  = Get-Date -Format 'yyyyMMdd_HHmmss'
    $stdout = Join-Path $Root ("logs\watchdog_start_$stamp.out")
    $stderr = Join-Path $Root ("logs\watchdog_start_$stamp.err")
    Start-Process -FilePath $Py -ArgumentList 'run.py','auto' `
        -WorkingDirectory $Root -WindowStyle Hidden `
        -RedirectStandardOutput $stdout -RedirectStandardError $stderr
    Write-WdLog "guardian was down -> started detached (stdout=$stdout)"
} catch {
    Write-WdLog ("watchdog error: " + $_.Exception.Message)
}
