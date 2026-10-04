import subprocess, json

def sh(args):
    r = subprocess.run(args, capture_output=True)
    return r.returncode, (r.stdout + r.stderr).decode('utf-8', errors='replace')

# 1. is staging gitignored?
for p in ['data/fund_statement_export/_staging/cashflow_20050331.parquet',
          'data/ah_panel/ah_panel.csv']:
    rc, out = sh(['git', 'check-ignore', '-v', p])
    print('check-ignore', p, '->', out.strip() or 'NOT IGNORED')

# 2. git status on data/ (untracked too)
rc, out = sh(['git', 'status', '--porcelain=v1'])
data_lines = [l for l in out.splitlines() if '/data/' in l or l.strip().startswith('data/')]
print('data faces in status:', len(data_lines))
for l in data_lines[:10]:
    print('  ', l)

# 3. detached processes alive?
r = subprocess.run(['powershell', '-NoProfile', '-Command',
                   "Get-CimInstance Win32_Process -Filter \"Name='python.exe'\" | "
                   "Where-Object {$_.CommandLine -like '*ah_panel*'} | Measure-Object | Select-Object -ExpandProperty Count"],
                   capture_output=True)
print('ah_panel procs:', r.stdout.decode('utf-8', errors='replace').strip())
r = subprocess.run(['powershell', '-NoProfile', '-Command',
                   "Get-CimInstance Win32_Process -Filter \"Name='python.exe'\" | "
                   "Where-Object {$_.CommandLine -like '*update_fund_statements*'} | Measure-Object | Select-Object -ExpandProperty Count"],
                   capture_output=True)
print('fund_statements procs:', r.stdout.decode('utf-8', errors='replace').strip())
