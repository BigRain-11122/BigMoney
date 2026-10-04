import json, os, glob

# staging + checkpoint progress
stage = 'data/fund_statement_export/_staging'
if os.path.isdir(stage):
    files = sorted(glob.glob(os.path.join(stage, '*.parquet')))
    print('staging parquet:', len(files))
    for f in files[:5]:
        print(' ', os.path.basename(f), os.path.getsize(f))
else:
    print('staging dir missing')

# look for checkpoint/state files
for pat in ['data/fund_statement_export/*.json',
            'results/fund_statement_*.json',
            'data/fund_statement_export/_staging/*.json']:
    for f in glob.glob(pat):
        print('---', f, os.path.getsize(f))

# any live python refresh process? check via tasklist snapshot instead
import subprocess
r = subprocess.run(['powershell', '-NoProfile', '-Command',
                    "Get-CimInstance Win32_Process -Filter \"Name='python.exe'\" | "
                    "Where-Object {$_.CommandLine -like '*fund_statement*'} | "
                    "Select-Object ProcessId,CreationDate | ConvertTo-Json"],
                   capture_output=True)
print('refresh procs:', r.stdout.decode('utf-8', errors='replace').strip() or 'NONE')
