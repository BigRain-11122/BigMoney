import json, glob
from collections import Counter

c = Counter()
opens = []
for t in glob.glob('fleet/tasks/*.json'):
    j = json.load(open(t, encoding='utf-8-sig'))
    s = j.get('status', '?')
    c[s] += 1
    if s == 'open':
        opens.append((t, j.get('claimed_by', '?'), j.get('title', j.get('subject', ''))[:80]))
print(dict(c))
for o in opens:
    print('OPEN:', o)

# S3 saturation engine check (bm-b)
import subprocess
r = subprocess.run(['python', 'scripts/saturation_engine.py', 'status'],
                    capture_output=True, text=True, encoding='utf-8', errors='replace',
                    creationflags=0x08000000)
print('SAT-ENGINE rc=%s' % r.returncode)
print((r.stdout or '')[-800:])
if r.returncode != 0:
    print('SAT-STDERR:', (r.stderr or '')[-400:])
