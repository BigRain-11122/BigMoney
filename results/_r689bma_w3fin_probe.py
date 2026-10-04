import subprocess, glob, os
# r689 bm-a probe: pid 32480 (W3 judge-finalize detached spawn from r688) liveness
# r659 law: CSV full-scan form; r661 law: cross-verify before consuming
r = subprocess.run(['tasklist', '/FO', 'CSV'], capture_output=True)
lines = r.stdout.decode('gbk', 'replace').splitlines()
hit = [l for l in lines if ',\"32480\",' in l]
print('PID 32480:', 'ALIVE' if hit else 'NOT-FOUND')
if hit: print(hit[0])

# second form: CIM full query
r2 = subprocess.run(['powershell', '-NoProfile', '-Command',
                     'Get-CimInstance Win32_Process | Where-Object ProcessId -eq 32480 | Select-Object ProcessId,Name,CommandLine | ConvertTo-Json'],
                    capture_output=True)
out = r2.stdout.decode('gbk', 'replace').strip()
print('CIM form:', out if out else 'NOT-FOUND')

# artifacts: w3_judge.json (finalize product) + any r688 finalize logs
for pat in ('results/mass_trial/w3_judge.json',):
    print(pat, 'EXISTS' if os.path.exists(pat) else 'absent', os.path.getsize(pat) if os.path.exists(pat) else '')
for f in sorted(glob.glob('results/_r688*')) + sorted(glob.glob('results/mass_trial/*finalize*')) + sorted(glob.glob('logs/*w3*finalize*')):
    print('file:', f, os.path.getsize(f))
