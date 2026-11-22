# Registers the strategy-bench scheduler (Bigmoney-StrategyBench).
# Law: O-20261122-2230 sec.2 -- one pending cell per tick, every 20 minutes, silent.
# Zero-window (U060): hosted through wscript + Tools\InvisibleRunner.vbs, never a console.
# Idempotent (-Force), path-agnostic, pure ASCII.
# Principal: S4U first (2026-09-29 user order: every lane task must be S4U, no
# InteractiveToken); if the host is unelevated and S4U is refused, fall back to the
# default principal and say so loudly (D-20261002-02 records the same refusal on
# other machines) -- refusing to register at all is the failure this script exists to
# prevent: the bench sat unregistered from 2026-11-22 22:30 to 2026-11-23 04:30.
param([int]$IntervalMinutes = 20)
$Project = Split-Path -Parent $PSScriptRoot
$hub = Join-Path $Project 'scripts\bench_hub.py'
$vbs = Join-Path $Project 'Tools\InvisibleRunner.vbs'
$benchDir = Join-Path $Project 'results\bench'
if (-not (Test-Path $hub)) { Write-Output "FATAL: $hub missing"; exit 1 }
if (-not (Test-Path $vbs)) { Write-Output "FATAL: $vbs missing"; exit 1 }
if (-not (Test-Path $benchDir)) {
    New-Item -ItemType Directory -Path $benchDir -Force | Out-Null
    Write-Output "created $benchDir"
}
$action = New-ScheduledTaskAction -Execute 'wscript.exe' `
    -Argument ('//B //nologo "' + $vbs + '" python.exe "' + $hub + '" run-one') `
    -WorkingDirectory $Project
$start = (Get-Date).AddMinutes(1)
$start = $start.AddSeconds(-$start.Second)
$trigger = New-ScheduledTaskTrigger -Once -At $start `
    -RepetitionInterval (New-TimeSpan -Minutes $IntervalMinutes) `
    -RepetitionDuration (New-TimeSpan -Days 3650)
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries `
    -StartWhenAvailable -MultipleInstances IgnoreNew `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 15)
$principal = New-ScheduledTaskPrincipal -UserId ("$env:USERDOMAIN\$env:USERNAME") `
    -LogonType S4U -RunLevel Limited
$landed = 'S4U'
try {
    Register-ScheduledTask -TaskName 'Bigmoney-StrategyBench' -Action $action -Trigger $trigger `
        -Settings $settings -Principal $principal -Force -ErrorAction Stop | Out-Null
} catch {
    $why = ($_.Exception.Message -replace '\s+', ' ').Trim()
    Write-Output "S4U refused ($why) -- falling back to the default principal (D-20261002-02)"
    Register-ScheduledTask -TaskName 'Bigmoney-StrategyBench' -Action $action -Trigger $trigger `
        -Settings $settings -Force -ErrorAction Stop | Out-Null
    $landed = 'DEFAULT_PRINCIPAL'
    $backlog = Join-Path $Project 'fleet\task-s4u-backlog.md'
    if (Test-Path (Split-Path -Parent $backlog)) {
        Add-Content -Path $backlog -Encoding UTF8 -Value ("- 2026-11-23 Bigmoney-StrategyBench registered with the default principal: S4U refused ({0}); needs an elevated window to convert." -f $why)
    }
}
$t = Get-ScheduledTask -TaskName 'Bigmoney-StrategyBench' -ErrorAction Stop
Write-Output ("registered Bigmoney-StrategyBench (project={0}, principal={1}, cadence={2}m, first fire {3}, LogonType={4})" -f `
    $Project, $landed, $IntervalMinutes, $start.ToString('yyyy-MM-dd HH:mm'), $t.Principal.LogonType)
