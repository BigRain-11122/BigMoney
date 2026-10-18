# r1017 bm-b S7 self-heal check (ASCII only). Zero-window: schtasks via Invoke-SilentExe.
$ErrorActionPreference = 'Continue'
Set-Location C:\Fluxgroup\FluxGroup\quant\bigmoney

function TaskState([string]$name) {
    $out = & powershell -NoProfile -ExecutionPolicy Bypass -File Tools\Invoke-SilentExe.ps1 -ExePath schtasks.exe -Arguments "/query /tn $name /fo csv /nh" 2>$null
    if (-not $out -or ($out -join '').Trim().Length -eq 0) { return 'MISSING' }
    $line = ($out | Select-Object -Last 1)
    if ("$line" -match 'ERROR|not found|找不到') { return 'MISSING' }
    $parts = "$line" -split '","'
    if ($parts.Count -ge 4) { return ($parts[3]).Trim('"') }
    return 'PRESENT'
}

$report = @()
foreach ($t in @('Bigmoney-IterationLoop', 'Bigmoney-LoopWatchdog', 'Bigmoney-SatEngine-bm-b', 'Bigmoney-ContentLoop')) {
    $s = TaskState $t
    $report += "task $t = $s"
    if ($s -eq 'MISSING') {
        $reg = @{
            'Bigmoney-IterationLoop'   = { & Tools\register_loop_task.ps1 }
            'Bigmoney-LoopWatchdog'    = { & Tools\register_watchdog_task.ps1 -Force }
            'Bigmoney-SatEngine-bm-b'  = { & Tools\register_satengine_task.ps1 }
            'Bigmoney-ContentLoop'     = { & Tools\register_content_loop_task.ps1 }
        }[$t]
        if ($reg) { & $reg | Out-Null; $report += "  -> re-registered: $t now = $(TaskState $t)" }
    }
}

function ClawCheck([string]$hook, [string]$canonical, [string]$regScript) {
    $h = if (Test-Path $hook) { (Get-Content $hook -Raw) -replace "`r", "" } else { '' }
    $c = (Get-Content $canonical -Raw) -replace "`r", ""
    if ($h -ne $c) {
        & $regScript | Out-Null
        $h2 = (Get-Content $hook -Raw) -replace "`r", ""
        if ($h2 -eq $c) { return 'REINSTALLED' }
        return 'MISMATCH-UNFIXED'
    }
    return 'OK'
}
$pc = ClawCheck '.git\hooks\pre-commit' 'Tools\git-hooks\pre-commit' 'Tools\register_precommit_claw.ps1'
$pp = ClawCheck '.git\hooks\pre-push' 'Tools\git-hooks\pre-push' 'Tools\register_prepush_claw.ps1'
$report += "claw pre-commit = $pc"
$report += "claw pre-push = $pp"
$report | ForEach-Object { Write-Output $_ }
