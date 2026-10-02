# -*- coding: utf-8 -*-
"""r570 bm-a surgical push (r532 live-write face + r530 assertion template).

Local: 2 unpushed commits (closeout + ride r570c) on base cd2e57af6.
Origin moved: W71 finalize (bm-c), pool_core_samples fleet repair (bm-b),
consumer guards, CODELY lesson, W72 full burn rides (bm-b).

Payload resolution rules (per family law):
- pool_core_samples.jsonl: origin-new (bm-b full-git-version union repair)
  as base + union-append my valid dict rows not present (live W73 burn
  samples never committed -> not in any git version -> must survive).
- CODELY.md: append-face union (my r570 pitfall line + origin's r570 lesson).
- Same-day idempotent derive faces (docs/daily_report, live_usage,
  dashboard, audit/status jsons, scorecard): wall-clock-new side (mine
  regenerated 10:42-45, after origin's 10:3x regen).
- Identical-content moves (inbox processed MSGs): take mine (same bytes).
- Files origin did NOT touch: take mine verbatim.

Assertions: payload count, deletion-set empty vs origin, post-push ls-tree.
"""
import subprocess, sys, os, json

REPO = os.getcwd()

def git(*a):
    r = subprocess.run(['git'] + list(a), capture_output=True)
    if r.returncode != 0:
        print('GIT FAIL', a[:4], '->', r.stderr.decode('utf-8', 'replace')[:400])
        sys.exit(1)
    return r.stdout.decode('utf-8', 'replace')

git('fetch', 'origin')
ORIGIN = git('rev-parse', 'origin/main').strip()
BASE = 'cd2e57af6'
print('origin tip:', ORIGIN[:10])

# my payload file set (2 unpushed commits vs BASE)
mine_files = set(l for l in git('diff', '--name-only', BASE, 'HEAD').splitlines() if l.strip())
origin_files = set(l for l in git('diff', '--name-only', BASE, ORIGIN).splitlines() if l.strip())
both = mine_files & origin_files
print('payload files (mine):', len(mine_files), '| origin-touched overlap:', len(both))
open('results/_r570bma_surg_files.txt', 'w', encoding='utf-8').write(
    'MINE-ONLY:\n' + '\n'.join(sorted(mine_files - origin_files)) +
    '\n\nOVERLAP:\n' + '\n'.join(sorted(both)))
for f in sorted(both):
    print('OVERLAP:', f)

# --- resolution map ---
# 1. pool_core_samples: origin + union of my new rows
pcs = 'results/pool_core_samples.jsonl'
origin_text = git('show', ORIGIN + ':' + pcs)
# git show through this helper gives translated text; use raw bytes for fidelity
raw = subprocess.check_output(['git', 'show', ORIGIN + ':' + pcs])
origin_bytes = raw
origin_lines = raw.decode('utf-8').splitlines()
origin_set = set(origin_lines)
loc_lines = open(pcs, encoding='utf-8').read().splitlines()
new_rows = []
for ln in loc_lines:
    s = ln.strip()
    if not s:
        continue
    try:
        r = json.loads(s)
    except Exception:
        continue
    if isinstance(r, dict) and s not in origin_set:
        new_rows.append(s)
print('pool_core_samples: origin rows', len(origin_lines), '+ my-new', len(new_rows))
eol = '\r\n' if raw.decode('utf-8').count('\r\n') * 2 > raw.decode('utf-8').count('\n') else '\n'
out = raw.decode('utf-8')
if not out.endswith('\n'):
    out += eol
for r in new_rows:
    out += r + eol if r + eol not in out else ''
open(pcs, 'wb').write(out.encode('utf-8'))
final = open(pcs, encoding='utf-8').read().splitlines()
cnt = 0
for ln in final:
    s = ln.strip()
    if not s:
        continue
    assert isinstance(json.loads(s), dict), 'non-dict row in resolved pcs'
    cnt += 1
print('resolved pcs rows:', cnt, '(origin', len(origin_lines), '+', len(new_rows), ')')
print('STAGE1_OK')
