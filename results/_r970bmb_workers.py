# r970 bm-b worker liveness census (salvage/v5/backfill + index-pack child).
# CIM query via script file (PS inline-quote swallow law, pit-ps family).
import subprocess, re
NO_WINDOW = 0x08000000
ps = r'''
$rows = Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -match 'salvage|restore_driver|backfill_ext_slots|index-pack' } | Select-Object ProcessId, Name, CommandLine
$rows | ForEach-Object { Write-Output ("PID=" + $_.ProcessId + " NAME=" + $_.Name + " CMD=" + ($_.CommandLine -replace '\s+',' ').Substring(0, [Math]::Min(150, $_.CommandLine.Length))) }
'''
p = subprocess.run(['powershell', '-NoProfile', '-Command', ps], capture_output=True,
                   creationflags=NO_WINDOW, timeout=90)
out = p.stdout.decode('utf-8', 'replace')
open(r'C:\Fluxgroup\FluxGroup\quant\bigmoney\results\_r970bmb_workers.txt', 'w',
     encoding='utf-8', errors='replace').write(out)
print('RC=%d BYTES=%d' % (p.returncode, len(out)))
