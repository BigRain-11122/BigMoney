# Registers bm-b-MemoryBudgetGate: nightly 21:47 memory-budget-gate run
# (fleet rollout leg of O-20261015-1230 / D-20261015-04: deterministic gate
# keeps global CODELY.md <=40KB/<=60 entries; zero LLM zero token).
# Pattern = register_satengine_task.ps1 (D-20261002-02 single default-principal
# path; wscript //B InvisibleRunner chain). Idempotent via -Force. Pure ASCII.
$gate = Join-Path $env:USERPROFILE '.codely-cli\memory-budget-gate.py'
$codely = Join-Path $env:USERPROFILE '.codely-cli\CODELY.md'
$vbs = Join-Path $PSScriptRoot 'InvisibleRunner.vbs'
foreach ($p in @($gate, $codely, $vbs)) {
    if (-not (Test-Path $p)) { Write-Output "FATAL: $p missing"; exit 1 }
}
$a = New-ScheduledTaskAction -Execute 'wscript.exe' `
    -Argument ('//B //nologo "' + $vbs + '" python.exe "' + $gate + '" --path "' + $codely + '"') `
    -WorkingDirectory $env:USERPROFILE
$t = New-ScheduledTaskTrigger -Daily -At '21:47'
$s = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries `
    -StartWhenAvailable -MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Minutes 10)
Register-ScheduledTask -TaskName 'bm-b-MemoryBudgetGate' -Action $a -Trigger $t -Settings $s -Force -ErrorAction Stop | Out-Null
Write-Output "registered bm-b-MemoryBudgetGate (daily 21:47, gate=$gate)"
