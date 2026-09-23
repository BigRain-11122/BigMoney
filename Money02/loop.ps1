# Manual continuous mode: tick every 10 minutes (same logic as the OS task).
param([int]$IntervalMinutes = 10)
Set-Location $PSScriptRoot
New-Item -ItemType Directory -Force -Path "$PSScriptRoot\logs" | Out-Null
while ($true) {
    $ts = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    "[$ts] tick" | Add-Content "$PSScriptRoot\logs\loop.log"
    $env:PYTHONIOENCODING = "utf-8"
    & python "$PSScriptRoot\run_tick.py" *>> "$PSScriptRoot\logs\loop.log"
    Start-Sleep -Seconds ($IntervalMinutes * 60)
}
