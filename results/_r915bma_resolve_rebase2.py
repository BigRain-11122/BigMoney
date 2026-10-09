# -*- coding: utf-8 -*-
# r915 bm-a rebase resolve leg-2: engine daemon live faces (EngineTick churn race
# mid-rebase window). law: history jsonl = line-union zero-loss; face/state json
# = newest-ts wins (daemon live-face law, newer-wins r910 family).
import json, subprocess

GIT = r'C:\Program Files\Git\cmd\git.exe'
P = 'results/saturation_engine/history_bm-a.jsonl'
FACE = 'results/saturation_engine/face_bm-a.json'
STATE = 'results/saturation_engine/state_bm-a.json'

def show(stage, path):
    r = subprocess.run([GIT, 'show', f':{stage}:{path}'], capture_output=True)
    return r.stdout.decode('utf-8').splitlines() if r.returncode == 0 else []

ours, theirs, wt = show(2, P), show(3, P), \
    open(P, encoding='utf-8').read().splitlines()
seen, union = set(), []
for ln in ours + theirs + wt:
    if ln.strip() and ln not in seen:
        seen.add(ln)
        union.append(ln)

def ts_key(ln):
    try:
        return json.loads(ln).get('ts', '') or json.loads(ln).get('time', '')
    except Exception:
        return ''

union_sorted = sorted(union, key=ts_key)
assert set(ours) <= set(union) and set(theirs) <= set(union) and set(wt) <= set(union)
open(P, 'w', encoding='utf-8', newline='').write('\n'.join(union_sorted) + '\n')
print('history union: %d lines (ours %d / theirs %d / worktree %d)'
      % (len(union_sorted), len(ours), len(theirs), len(wt)))

for path in (FACE, STATE):
    cands = []
    for src in (show(2, path), show(3, path),
                open(path, encoding='utf-8').read().splitlines()):
        try:
            d = json.loads('\n'.join(src))
        except Exception:
            continue
        cands.append((str(d.get('ts') or d.get('time') or ''), d, src))
    assert cands, path
    best = max(cands, key=lambda c: c[0])
    open(path, 'w', encoding='utf-8', newline='') \
        .write('\n'.join(best[2]) + '\n')
    print('%s: newest-ts=%s (candidates %d)' % (path, best[0][:19] or 'n/a', len(cands)))
