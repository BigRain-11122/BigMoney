# r999 bm-b mini-chain (guard legs only; full S6 deferred to r1000:
# r998 full-chain faces <2h fresh, round budget consumed by S0 estate surgery + audition gate).
$ErrorActionPreference = 'Continue'
Set-Location C:\Fluxgroup\FluxGroup\quant\bigmoney
$log = 'results\_r999bmb_s6_log.txt'
"MINI-CHAIN r999 $(Get-Date -Format HH:mm:ss) (guards only; full S6 -> r1000)" | Add-Content $log -Encoding UTF8
function Step([string]$name, [string[]]$argv) {
    $out = & python @argv 2>&1
    $rc = $LASTEXITCODE
    $oline = ''
    foreach ($o in $out) { $s = "$o"; if ($s.Trim()) { $oline = $s.Trim(); break } }
    $line = "rc=$rc $name :: $oline"
    Add-Content $log $line -Encoding UTF8
    Write-Output $line
    return $rc
}
$satRc = Step 'sat_engine_status' @('scripts\saturation_engine.py','status')
if ($satRc -eq 1) {
    Write-Output 'SAT_ENGINE_DEAD -> reregister + tick'
    & Tools\register_satengine_task.ps1
    Step 'sat_engine_tick_after_repair' @('scripts\saturation_engine.py','tick')
}
Step 'smoke_test' @('-m','smoke_test')
Step 'py_watermark' @('scripts\py_watermark.py','probe')
Step 'attrition_scan' @('scripts\attrition_ledger_guard.py','scan')
Write-Output "mini-chain end $(Get-Date -Format HH:mm:ss)"
"mini-chain end $(Get-Date -Format HH:mm:ss)" | Add-Content $log -Encoding UTF8
