# -*- coding: utf-8 -*-
"""r568 bm-b rebase conflict resolver: same-day idempotent regen faces take
wall-clock-newer side (origin, bm-a r568 closeout ran AFTER my 09:59-10:05
S6 chain) via git checkout --ours; pool_core_samples.jsonl = r294
conflict-region union (base + ours-new + theirs-new, domain-limited dedupe,
never global)."""
import subprocess, sys

def stage(n, path):
    return subprocess.check_output(['git', 'show', f':{n}:{path}'])

PATH = 'results/pool_core_samples.jsonl'
b1 = stage(1, PATH)
b2 = stage(2, PATH)
b3 = stage(3, PATH)
eol = '\r\n' if b'\r\n' in b2 else '\n'

def lines(b):
    t = b.decode('utf-8')
    t = t.replace('\r\n', '\n').rstrip('\n')
    return t.split('\n') if t else []

base, ours, theirs = lines(b1), lines(b2), lines(b3)
nb = len(base)

def tail_new(side):
    if side[:nb] == base:
        return side[nb:]
    print('WARN: side does not extend base cleanly; using whole side as new')
    return side

ours_new = tail_new(ours)
theirs_new = tail_new(theirs)
seen = set(ours_new)
extra = [l for l in theirs_new if l not in seen]
out = base + ours_new + extra
data = eol.join(out) + eol if out else ''
open(PATH, 'wb').write(data.encode('utf-8'))
print(f'pool_core_samples union: base={nb} ours_new={len(ours_new)} '
      f'theirs_new={len(theirs_new)} extra_kept={len(extra)} total={len(out)} '
      f'eol={"CRLF" if eol == chr(13)+chr(10) else "LF"}')

REGEN = [
    'docs/daily_report/REPORT-2026-10-02.json',
    'docs/daily_report/REPORT-2026-10-02.md',
    'docs/live_usage/LIVE-2026-10-02.json',
    'docs/live_usage/LIVE-2026-10-02.md',
    'docs/live_usage/LIVE-latest.json',
    'docs/live_usage/LIVE-latest.md',
    'results/astock_daily_update_status.json',
    'results/compute_audit.json',
    'results/dashboard_status.js',
    'results/dashboard_status.json',
    'results/etf_daily_pull_status.json',
    'results/fundamental_b_layer_filter.json',
    'results/futures_update_status.json',
    'results/lhb_update_status.json',
    'results/p1d_gates.json',
    'results/regime_state.json',
    'results/scorecard_v1.json',
    'results/strategy_scorecard.json',
    'results/token_usage.json',
    'results/update_status.json',
]
for p in REGEN:
    r = subprocess.run(['git', 'checkout', '--ours', '--', p], capture_output=True)
    if r.returncode != 0:
        sys.exit(f'checkout --ours FAIL {p}: {r.stderr.decode("utf-8","replace")}')
    print(f'regen take-origin-newer: {p}')
print('RESOLVE_OK')
