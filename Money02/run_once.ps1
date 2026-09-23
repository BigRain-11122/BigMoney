# One-shot entry for the 10-minute OS tick (MoneyQuantTick).
# Hard watchdog: a tick that cannot finish in 9 minutes gets killed so the
# 10-minute cadence never stacks up (per user order: hang -> self-recover).
# NOTE: stdout/stderr must go to SEPARATE files (same-file redirect crashes
# Start-Process silently in PS5.1 - root cause of the 2026-09-19 stalled loop).
Set-Location $PSScriptRoot
New-Item -ItemType Directory -Force -Path "$PSScriptRoot\logs" | Out-Null
$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONUNBUFFERED = "1"
$ts = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
$stamp = Get-Date -Format "yyyyMMdd_HHmmss"
$out = "$PSScriptRoot\logs\tick_$stamp.out"
$err = "$PSScriptRoot\logs\tick_$stamp.err"

$p = $null
try {
    $p = Start-Process python -ArgumentList "`"$PSScriptRoot\run_tick.py`"" -PassThru -NoNewWindow -RedirectStandardOutput $out -RedirectStandardError $err
} catch {
    "[$ts] START-FAIL: $($_.Exception.Message)" | Add-Content "$PSScriptRoot\logs\tick.log"
}

if ($p) {
    if (-not $p.WaitForExit(540000)) {
        "[$ts] WATCHDOG: killing hung tick pid=$($p.Id)" | Add-Content "$PSScriptRoot\logs\tick.log"
        & taskkill /F /T /PID $p.Id 2>$null
    }
} else {
    "[$ts] START-FAIL: no process handle" | Add-Content "$PSScriptRoot\logs\tick.log"
}

if (Test-Path $out) { Get-Content $out | Add-Content "$PSScriptRoot\logs\tick.log" }
if (Test-Path $err) { Get-Content $err | Add-Content "$PSScriptRoot\logs\tick.log" }
if (-not (Test-Path $out)) { "[$ts] ERROR: tick produced no output at all" | Add-Content "$PSScriptRoot\logs\tick.log" }
Remove-Item $out, $err -Force -ErrorAction SilentlyContinue
