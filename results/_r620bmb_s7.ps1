# r620 bm-b S7 self-heal + closeout checks (schtasks via Invoke-SilentExe per R49; claws via installer idempotency)
$ErrorActionPreference = 'Continue'
$log = 'results\_r620bmb_s7.log'
Set-Content -Path $log -Value "S7 r620 bm-b start $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"

# 1. Bigmoney-IterationLoop register (idempotent, in-process, zero-window per U060)
& Tools\register_loop_task.ps1
Add-Content -Path $log -Value "register_loop_task exit=$LASTEXITCODE"

# 2. Bigmoney-LoopWatchdog (idempotent rebuild if missing)
& Tools\register_watchdog_task.ps1 -Force
Add-Content -Path $log -Value "register_watchdog_task exit=$LASTEXITCODE"

# 3. pre-commit claw (install if missing/differs)
& Tools\register_precommit_claw.ps1
Add-Content -Path $log -Value "precommit_claw exit=$LASTEXITCODE"

# 4. pre-push claw (install if missing/differs)
& Tools\register_prepush_claw.ps1
Add-Content -Path $log -Value "prepush_claw exit=$LASTEXITCODE"

# 5. task presence probe (schtasks query via silent wrapper)
$q = & Tools\Invoke-SilentExe.ps1 -Exe schtasks.exe -ArgString "/query /tn Bigmoney-IterationLoop /fo LIST"
Add-Content -Path $log -Value ($q -join ' | ')
$q2 = & Tools\Invoke-SilentExe.ps1 -Exe schtasks.exe -ArgString "/query /tn Bigmoney-LoopWatchdog /fo LIST"
Add-Content -Path $log -Value ($q2 -join ' | ')

# 6. attrition ledger guard scan
$g = & Tools\Invoke-SilentExe.ps1 -Exe python.exe -ArgString "scripts\attrition_ledger_guard.py scan"
Add-Content -Path $log -Value ($g -join ' | ')
Add-Content -Path $log -Value "attrition_guard rc=$LASTEXITCODE"
Write-Host "S7 checks done; see $log"
