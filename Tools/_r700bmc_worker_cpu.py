"""r700 bm-c worker CPU probe (script-file form; inline quoting pit)."""
import json
import subprocess
import time

PS = ('Get-Process -Id 24488,27748,12820 | Select-Object Id,'
      '@{n="c";e={[math]::Round($_.TotalProcessorTime.TotalSeconds,1)}} '
      '| ConvertTo-Json -Compress')


def snap():
    r = subprocess.run(["powershell", "-NoProfile", "-Command", PS],
                       capture_output=True, text=True, encoding="utf-8",
                       errors="replace")
    return {x["Id"]: x["c"] for x in json.loads(r.stdout)}


a = snap()
time.sleep(8)
b = snap()
for pid in a:
    d = b.get(pid, 0) - a[pid]
    print("worker %d cpu %.1f -> %.1f (delta %.1fs/8s)"
          % (pid, a[pid], b.get(pid, 0), d))
