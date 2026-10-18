# r1054 probe4: read council case file from group origin (append-only table face)
import subprocess, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
GRP = r'C:\Users\sjs20\Desktop\FluxGroup'
p = subprocess.run(['git','-C',GRP,'fetch','origin'],capture_output=True)
p = subprocess.run(['git','-C',GRP,'show','origin/main:cph4/council/C-20261018-02-全流程梳理冲突对账案.md'],capture_output=True)
txt = p.stdout.decode('utf-8','replace') if p.returncode==0 else 'ABSENT rc=%d' % p.returncode
lines = txt.splitlines()
print('total_lines=%d' % len(lines))
print('\n'.join(lines[:55]))
print('...TAIL...')
print('\n'.join(lines[-40:]))
