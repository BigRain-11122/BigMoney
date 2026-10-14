$names = @('Bigmoney-IterationLoop', 'Bigmoney-LoopWatchdog', 'HQ-WT-Park', 'HQ-bm-c-Sentinel')
foreach ($n in $names) {
    $out = & 'K:\Fluxgroup\FluxGroup\quant\bigmoney\Tools\Invoke-SilentExe.ps1' -Exe schtasks -ArgString ("/query /tn " + $n)
    if ($LASTEXITCODE -eq 0) {
        $status = ($out | Select-String -Pattern 'Ready|Running').Line
        Write-Output ("PRESENT " + $n + " | " + $status)
    } else {
        Write-Output ("MISSING " + $n)
    }
}
