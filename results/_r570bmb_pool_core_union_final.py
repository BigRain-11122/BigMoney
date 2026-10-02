# -*- coding: utf-8 -*-
"""r570 bm-b FINAL union of pool_core_samples.jsonl across ALL git versions.

The r569-closeout corruption (733fcca4f) inserted a 71-line pretty blob
AND truncated ~1429 legitimate dict rows. Definitive reconstruction per
r294 domain law: union every dict row from EVERY commit that ever touched
the file (git log --all, commit-time ascending) + the current working
file; byte-exact lines, line-identity dedup, natural chronological order.
"""
import json
import subprocess

REPO = r'C:\Fluxgroup\FluxGroup\quant\bigmoney'
FP = REPO + r'\results\pool_core_samples.jsonl'

def sh(*a):
    return subprocess.check_output(['git', '-C', REPO] + list(a)).decode('utf-8', 'replace')

log = sh('log', '--all', '--format=%H %ct', '--',
         'results/pool_core_samples.jsonl').strip().splitlines()
commits = sorted(log, key=lambda x: int(x.split()[1]))
print(f'file versions in history: {len(commits)}')

seen, ordered, per_ver = set(), [], {}
for line in commits:
    sha = line.split()[0]
    try:
        raw = sh('show', f'{sha}:results/pool_core_samples.jsonl')
    except Exception:
        continue
    n = 0
    for l in raw.splitlines():
        l = l.strip()
        if not l:
            continue
        try:
            r = json.loads(l)
        except Exception:
            continue
        if not isinstance(r, dict):
            continue
        n += 1
        if l not in seen:
            seen.add(l)
            ordered.append(l)
    per_ver[sha[:9]] = n

raw_new = open(FP, 'rb').read()
eol = '\r\n' if raw_new.count(b'\r\n') * 2 > raw_new.count(b'\n') else '\n'
cur = []
for l in raw_new.decode('utf-8').splitlines():
    l = l.strip()
    if not l:
        continue
    try:
        r = json.loads(l)
    except Exception:
        continue
    if isinstance(r, dict):
        cur.append(l)
cur_new = 0
for l in cur:
    if l not in seen:
        seen.add(l)
        ordered.append(l)
        cur_new += 1

for l in ordered:
    assert isinstance(json.loads(l), dict)
machines = {}
for l in ordered:
    m = json.loads(l).get('machine_id', '?')
    machines[m] = machines.get(m, 0) + 1
open(FP, 'wb').write((eol.join(ordered) + eol).encode('utf-8'))
print(f'FINAL UNION: {len(ordered)} dict rows '
      f'(history versions {len(per_ver)} + current-new {cur_new}); '
      f'machine coverage: {machines}; '
      f'eol={"CRLF" if eol == chr(13)+chr(10) else "LF"}')
