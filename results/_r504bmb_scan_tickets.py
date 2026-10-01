"""r504 S2 helper: scan ticket statuses from origin/main (read-only)."""
import subprocess, json, sys

out = subprocess.check_output(['git', 'ls-tree', '--name-only', 'origin/main', 'fleet/tasks/'],
                              encoding='utf-8')
files = [x for x in out.split() if x.endswith('.json')]
open_t, claimed, bad = [], [], []
for f in files:
    c = subprocess.check_output(['git', 'show', 'origin/main:' + f], encoding='utf-8')
    try:
        t = json.loads(c)
    except json.JSONDecodeError:
        bad.append(f.split('/')[-1])
        continue
    s = t.get('status', '?')
    if s == 'open':
        open_t.append((f.split('/')[-1], t.get('title', '')[:80]))
    elif s == 'claimed':
        claimed.append((f.split('/')[-1], t.get('claimed_by', '?')))
print('OPEN:')
for x in open_t:
    print(' ', x[0], '|', x[1])
print('CLAIMED:', [x[0] + '@' + x[1] for x in claimed])
print('UNPARSEABLE:', bad)
