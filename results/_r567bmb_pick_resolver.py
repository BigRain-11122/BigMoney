# -*- coding: utf-8 -*-
"""r567 bm-b rebase-pick conflict resolver (r501 net-route manual pick, r523 active-burn window).

Faces (all S6/telemetry derive faces, same-window dual-write vs bm-a r568 chain):
  whole-rewrite JSON envelopes (take MY d7a1be6fb side = wall-clock newer 09:33-09:40
    vs bm-a r567 chain ~09:01-09:1x, r505 newer-side law):
    - results/lhb_update_status.json
    - results/regime_state.json
    - results/scorecard_v1.json
    - results/strategy_scorecard.json
  append-only jsonl (LINE-SET UNION, dedupe domain = new-line set only, r294/r312-3):
    - results/pool_core_samples.jsonl
    - results/paper/marks/marks-20261002.jsonl
"""
import subprocess, sys

REPO = '.'

def show(rev, path):
    return subprocess.check_output(['git', 'show', f'{rev}:{path}'], errors='replace')

MINE = 'd7a1be6fb'      # my closeout pick (wall-clock newer derive faces)
ORIGIN = 'ed52184e6'    # bm-a r568 surgical (origin side)

WHOLE_REWRITE = [
    'results/lhb_update_status.json',
    'results/regime_state.json',
    'results/scorecard_v1.json',
    'results/strategy_scorecard.json',
]
UNION = [
    'results/pool_core_samples.jsonl',
    'results/paper/marks/marks-20261002.jsonl',
]

import json
for p in WHOLE_REWRITE:
    t = show(MINE, p)
    # sanity: parseable JSON, no markers
    assert '<<<<<<<' not in t and '>>>>>>>' not in t, f'{p}: marker in source blob?!'
    json.loads(t)
    open(p, 'wb').write(t.encode('utf-8'))
    print(f'resolved (whole-rewrite, take mine={MINE} newer side): {p}')

for p in UNION:
    mine_lines = show(MINE, p).splitlines()
    orig_lines = show(ORIGIN, p).splitlines()
    base = show('551ced1b1', p).splitlines()
    base_set = set(base)
    mine_new = [l for l in mine_lines if l not in base_set]
    orig_new = [l for l in orig_lines if l not in base_set]
    # union: origin full + my new lines not already in origin (append-only, r294 dedupe domain = new-line sets)
    orig_set = set(orig_lines)
    merged = list(orig_lines) + [l for l in mine_new if l not in orig_set]
    out = '\n'.join(merged) + ('\n' if merged else '')
    assert '<<<<<<<' not in out and '>>>>>>>' not in out
    # jsonl parse check (each line must be valid json or empty)
    for i, l in enumerate(merged):
        if l.strip():
            json.loads(l)
    open(p, 'wb').write(out.encode('utf-8'))
    print(f'resolved (jsonl line-union: origin {len(orig_lines)} lines + mine-new {len([l for l in mine_new if l not in orig_set])} = {len(merged)}): {p}')

print('RESOLVER_OK')
