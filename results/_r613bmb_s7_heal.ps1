# r613 bm-b S7 self-heal: loop pin + watchdog + claws (in-process, idempotent)
& 'Tools\register_loop_task.ps1'
$wd = & 'Tools\Invoke-SilentExe.ps1' -Exe schtasks -Args '/query','/tn','Bigmoney-LoopWatchdog'
if (-not $wd) { & 'Tools\register_watchdog_task.ps1'; Write-Host 'WATCHDOG: REBUILT' }
else { Write-Host 'WATCHDOG: alive' }
$pc = Test-Path .git\hooks\pre-commit
$pp = Test-Path .git\hooks\pre-push
if (-not $pc) { & 'Tools\register_precommit_claw.ps1' }
if (-not $pp) { & 'Tools\register_prepush_claw.ps1' }
Write-Host "CLAWS: pre-commit=$pc pre-push=$pp"
