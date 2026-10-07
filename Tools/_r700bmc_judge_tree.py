"""r700 bm-c judge tree probe: children of 4572, python CPU, RAM face."""
import subprocess
import time

PS = r"""
$kids = Get-CimInstance Win32_Process -Filter "ParentProcessId=4572" | Select-Object ProcessId,Name,CommandLine
$kids | ConvertTo-Json -Compress
"---ALLPY---"
Get-Process python*,pythonw* -ErrorAction SilentlyContinue | Select-Object Id,ProcessName,@{n='cpusec';e={[math]::Round($_.TotalProcessorTime.TotalSeconds,1)}},@{n='wsMB';e={[math]::Round($_.WorkingSet64/1MB)}} | ConvertTo-Json -Compress
"---GAME---"
Get-Process | Where-Object {$_.ProcessName -match 'ACBlack|game|Game'} | Select-Object Id,ProcessName | ConvertTo-Json -Compress
"""
r = subprocess.run(["powershell", "-NoProfile", "-Command", PS],
                   capture_output=True, text=True, encoding="utf-8",
                   errors="replace")
print(r.stdout[:1500])
