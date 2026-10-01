"""r311 bm-c rebase conflict resolver (r296/r298/r294 recipe).

Full-rewrite re-derive faces -> take origin (--ours in rebase).
Append-only pool_core_samples.jsonl -> conflict-region union, dedupe
by full-row identity within the region ONLY (r294 domain law: never
global-dedupe an append-only ledger).
"""
import subprocess
import os

REWRITE = [
    'docs/daily_report/REPORT-2026-10-01.md',
    'docs/daily_report/REPORT-2026-10-01.json',
    'docs/live_usage/LIVE-2026-10-01.json',
    'docs/live_usage/LIVE-2026-10-01.md',
    'docs/live_usage/LIVE-latest.json',
    'docs/live_usage/LIVE-latest.md',
    'results/_attrition_guard_scan.json',
    'results/dashboard_status.js',
    'results/dashboard_status.json',
    'results/fundamental_b_layer_filter.json',
    'results/futures_update_status.json',
    'results/lhb_update_status.json',
    'results/scorecard_v1.json',
    'results/strategy_scorecard.json',
    'results/token_usage.json',
]
for f in REWRITE:
    r = subprocess.run(['git', 'checkout', '--ours', '--', f], capture_output=True, text=True)
    assert r.returncode == 0, (f, r.stderr)
    subprocess.run(['git', 'add', f], check=True)
print('rewrite faces -> origin side:', len(REWRITE))

# pool_core_samples.jsonl: conflict-region union
FP = 'results/pool_core_samples.jsonl'
lines = open(FP, encoding='utf-8').read().splitlines()
try:
    a = lines.index('<<<<<<< HEAD')
    m = lines.index('=======')
    b = next(i for i, l in enumerate(lines) if l.startswith('>>>>>>> '))
except ValueError:
    raise SystemExit('markers not found -- unexpected shape')
base = lines[:a]
ours = [l for l in lines[a + 1:m] if l.strip()]
theirs = [l for l in lines[m + 1:b] if l.strip()]
tail = lines[b + 1:]
seen = set()
merged = []
for l in base + ours + theirs:
    if l in seen:
        continue
    seen.add(l)
    merged.append(l)
out = '\n'.join(merged) + '\n'
open(FP, 'w', encoding='utf-8', newline='').write(out)
subprocess.run(['git', 'add', FP], check=True)
print('pool_core_samples union: base', len(base), 'origin-side', len(ours),
      'mine', len(theirs), '-> total', len(merged))
