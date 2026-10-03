import subprocess

# 1) running burns?
r = subprocess.run(['powershell', '-NoProfile', '-Command',
                    "Get-CimInstance Win32_Process -Filter \"Name='python.exe'\" | "
                    "Where-Object {$_.CommandLine -match 'fund_.*_p1.py run --nulls'} | "
                    "Select-Object ProcessId,CreationDate,CommandLine | ConvertTo-Json"],
                   capture_output=True, text=True)
print('RUNNING NULLS BURNS:', r.stdout.strip()[:800] or '(none)')

# 2) which runners did r626d (6c2a6742f) touch?
r2 = subprocess.run(['git', 'show', '--stat', '--format=', '6c2a6742f'],
                    capture_output=True, text=True, encoding='utf-8', errors='replace')
print('--- r626d touched files:')
print(r2.stdout.strip())

# 3) current runner sha16s
import hashlib
for name in ('fund_value_p1', 'fund_quality_p1', 'fund_divlowvol_p1'):
    fp = rf'scripts\{name}.py'
    h = hashlib.sha256(open(fp, 'rb').read()).hexdigest()[:16]
    print(name, 'current sha16:', h)
