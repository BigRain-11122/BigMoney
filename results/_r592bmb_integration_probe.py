# -*- coding: utf-8 -*-
# r592 bm-b integration probe: AA-face enumeration (my commit vs origin's 4 new commits)
import subprocess, json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

def sh(*args):
    return subprocess.run(list(args), capture_output=True).stdout

# my commit's file set (5d6e6da5c vs its parent 35193dcd1)
mine = sh('git', 'diff', '--name-only', '35193dcd1', '5d6e6da5c').decode('utf-8', errors='replace').splitlines()
# origin's new commits file set (35193dcd1..origin/main)
theirs = sh('git', 'diff', '--name-only', '35193dcd1', 'origin/main').decode('utf-8', errors='replace').splitlines()
aa = sorted(set(mine) & set(theirs))
print('my files:', len(mine), '| their files:', len(theirs), '| AA overlap:', len(aa))
for f in aa:
    print('AA:', f)
# union candidates: append-only jsonl in AA?
for f in aa:
    if f.endswith('.jsonl'):
        print('JSONL-IN-AA (union needed):', f)
# ts comparison for key shared faces
for f in ['results/strategy_scorecard.json', 'results/compute_audit.json', 'results/dashboard_status.json']:
    o = sh('git', 'show', 'origin/main:' + f).decode('utf-8', errors='replace')
    l = open(f, encoding='utf-8', errors='replace').read()
    import re
    def ts(t):
        m = re.search(r'"generated":\s*"([^"]+)"', t) or re.search(r'"ts":\s*"([^"]+)"', t)
        return m.group(1) if m else '?'
    print(f, '| origin ts:', ts(o), '| local ts:', ts(l))
