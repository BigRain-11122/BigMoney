# r937 bm-b S7 mechanical batch: attrition guard + task claws + git hooks
$ErrorActionPreference = 'Continue'
# 1) attrition ledger guard
$out = & cmd /c "python scripts\attrition_ledger_guard.py scan" 2>&1
Write-Output ("### attrition rc={0}" -f $LASTEXITCODE)
if ($LASTEXITCODE -ne 0) { $out | Select-Object -Last 5 | Write-Output }
# 2) loop task idempotent re-register (pin bm-b=2)
& Tools\register_loop_task.ps1
Write-Output "### loop_task done (internal output above = sentinel)"
# 3) watchdog idempotent re-register
& Tools\register_watchdog_task.ps1
Write-Output "### watchdog done"
# 4) pre-commit claw
& Tools\register_precommit_claw.ps1
Write-Output "### precommit_claw done"
# 5) pre-push claw
& Tools\register_prepush_claw.ps1
Write-Output "### prepush_claw done"
