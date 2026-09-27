import subprocess
import glob
import os
import json

# 1. check pids alive
for pid in [41360, 44968]:
    r = subprocess.run(['powershell', '-NoProfile', '-Command',
                        "Get-Process -Id %d -ErrorAction SilentlyContinue | Select-Object Id,ProcessName,CPU | ConvertTo-Json" % pid],
                       capture_output=True)
    out = r.stdout.decode('utf-8', errors='replace').strip()
    print('pid', pid, '->', out if out else 'NOT RUNNING')

# 2. autofill log tail for SINA
logs = glob.glob('logs/autofill_SINA*') + glob.glob('logs/*SINA*')
print('sina logs:', logs)
for lg in logs[-2:]:
    with open(lg, encoding='utf-8', errors='replace') as f:
        lines = f.read().splitlines()
    print('==', lg, len(lines), 'lines, tail:')
    for l in lines[-10:]:
        print('  ', l[:180])

# 3. results of sina construct census
for pat in ['results/sina_construct*', 'results/*sina*']:
    for f in sorted(glob.glob(pat)):
        print('result file:', f, os.path.getsize(f), 'B', 'mtime', os.path.getmtime(f))
