$tasks = & 'C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney\Tools\Invoke-SilentExe.ps1' -Exe schtasks -ArgString '/query /fo csv' -StdoutOnly
$tasks | Select-String -Pattern 'Bigmoney|SatEngine|Autofill|Dispatcher|Sentinel|IdleTrigger|LoopWatch' | ForEach-Object { ($_.Line -split '"",""')[0] }
