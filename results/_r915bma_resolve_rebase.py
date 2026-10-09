# -*- coding: utf-8 -*-
# r915 bm-a rebase resolve: pool_core_samples.jsonl line-union (r910 bloodline
# |A u B| zero-loss), rename/rename quarantine pairs = keep BOTH sides (bm-c
# 124800 set + bm-a 131148 set, zero-loss law), root delete/delete = deleted.
import json, subprocess

GIT = r'C:\Program Files\Git\cmd\git.exe'

def show(stage):
    r = subprocess.run([GIT, 'show', f':{stage}:results/pool_core_samples.jsonl'],
                       capture_output=True)
    assert r.returncode == 0, r.stderr.decode('utf-8', 'replace')
    return r.stdout.decode('utf-8').splitlines()

base, ours, theirs = show(1), show(2), show(3)
seen, union = set(), []
for ln in ours + theirs:
    if ln.strip() and ln not in seen:
        seen.add(ln)
        union.append(ln)

def ts_key(ln):
    try:
        return json.loads(ln).get('ts', '')
    except Exception:
        return ''

union_sorted = sorted(union, key=ts_key)  # stable: preserves first-seen order within equal ts
assert set(ours) <= set(union) and set(theirs) <= set(union), 'union lost lines'
assert len(union_sorted) == len(union)
open('results/pool_core_samples.jsonl', 'w', encoding='utf-8', newline='') \
    .write('\n'.join(union_sorted) + '\n')
print('pool_core_samples union: %d lines (base %d / ours %d / theirs %d, zero-loss asserted)'
      % (len(union_sorted), len(base), len(ours), len(theirs)))
