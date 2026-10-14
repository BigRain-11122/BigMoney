# r935 bm-b S7 hygiene: watchdog query via silent wrapper + claw content checks (ASCII)
$ErrorActionPreference = "Continue"
& .\Tools\Invoke-SilentExe.ps1 -Exe schtasks -ArgString "/query /tn Bigmoney-LoopWatchdog" | Select-Object -Last 1

$preCommitOk = $false
$prePushOk = $false
if (Test-Path .\.git\hooks\pre-commit) {
    $a = (Get-Content .\.git\hooks\pre-commit -Raw) -replace "`r", ""
    $b = (Get-Content .\Tools\git-hooks\pre-commit -Raw) -replace "`r", ""
    $preCommitOk = ($a -eq $b)
}
if (Test-Path .\.git\hooks\pre-push) {
    $c = (Get-Content .\.git\hooks\pre-push -Raw) -replace "`r", ""
    $d = (Get-Content .\Tools\git-hooks\pre-push -Raw) -replace "`r", ""
    $prePushOk = ($c -eq $d)
}
Write-Output ("precommit claw content match: " + $preCommitOk)
Write-Output ("prepush claw content match: " + $prePushOk)
if (-not $preCommitOk) { & .\Tools\register_precommit_claw.ps1 }
if (-not $prePushOk) { & .\Tools\register_prepush_claw.ps1 }
