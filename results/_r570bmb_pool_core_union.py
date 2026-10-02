# -*- coding: utf-8 -*-
"""r570 bm-b: FULL union reconstruction of pool_core_samples.jsonl.

The r569-closeout union face (733fcca4f) truncated 1429 legitimate dict
rows to ~7 (kept only blob + post-blob appends). Reconstruct per r294
domain law: union ALL dict rows across every version of the file in the
corruption window (3bc52e65f .. origin/main), byte-exact, ordered
(older-version-first base, then rows new to each later version).
"""
import json
import subprocess

REPO = r'C:\Fluxgroup\FluxGroup\quant\bigmoney'
FP = REPO + r'\results\pool_core_samples.jsonl'
WIN_LO = '3bc52e65f'

def sh(*a):
    return subprocess.check_output(['git', '-C', REPO] + list(a)).decode('utf-8', 'replace')

def dict_rows(sha):
    try:
        raw = sh('show', f'{sha}:results/pool_core_samples.jsonl')
    except Exception:
        return None
    rows = []
    for l in raw.splitlines():
        l = l.strip()
        if not l:
            continue
        try:
            r = json.loads(l)
        except Exception:
            continue
        if isinstance(r, dict):
            rows.append(l)
    return rows

# --- enumerate every commit touching the file in the window -----------------
log = sh('log', '--format=%H %ct', WIN_LO + '..origin/main', '--',
         'results/pool_core_samples.jsonl').strip().splitlines()
# ascending by commit time (oldest first)
commits = sorted(log, key=lambda x: int(x.split()[1]))
print(f'versions in window: {len(commits)}')

seen = set()
ordered = []
counts = {}
for line in commits:
    sha = line.split()[0]
    rows = dict_rows(sha)
    if rows is None:
        continue
    counts[sha[:9]] = len(rows)
    for l in rows:
        if l not in seen:
            seen.add(l)
            ordered.append(l)

# --- also include the current working-file dict rows -------------------------
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
for l in cur:
    if l not in seen:
        seen.add(l)
        ordered.append(l)

for l in ordered:
    assert isinstance(json.loads(l), dict)
data = eol.join(ordered) + eol
open(FP, 'wb').write(data.encode('utf-8'))
print('per-version dict-row counts:', counts)
print(f'UNION: {len(ordered)} dict rows written '
      f'(>= max single-version count {max(counts.values()) if counts else 0}); '
      f'junk/blob excluded; eol={"CRLF" if eol == chr(13)+chr(10) else "LF"}')
