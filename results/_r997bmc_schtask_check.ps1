# _r997bmc_schtask_check.ps1 -- S7 quad self-heal leg (raw output, zh-CN label safe)
$r1 = & 'Tools\Invoke-SilentExe.ps1' -Exe schtasks -ArgString '/query /tn Bigmoney-IterationLoop /fo LIST'
Write-Output "=== LOOP task raw ==="
$r1 | ForEach-Object { Write-Output $_ }
$r2 = & 'Tools\Invoke-SilentExe.ps1' -Exe schtasks -ArgString '/query /tn Bigmoney-LoopWatchdog /fo LIST'
Write-Output "=== WATCHDOG task raw ==="
$r2 | ForEach-Object { Write-Output $_ }
