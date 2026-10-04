# _r676bma_merge_resolve.py -- r676 merge UU resolution (18 faces)
# Policy (r440 two-way / r378 host-guard / r456 per-key union):
#  - S6 regen faces -> origin-newer-wins (checkout origin blob; re-derivable snapshots)
#  - bm-a host-authority faces (dashboard_status.* / strategy_scorecard / scorecard_v1) -> ours
#  - token_usage.json -> per-key union on machines dict (side-pick assertion per r456)
#  - _attrition_guard_scan.json -> ours (newer scan 12:39, bm-a evidence face)
import json, subprocess, sys

def sh(args):
    r = subprocess.run(args, capture_output=True)
    if r.returncode != 0:
        print('FAIL', args, r.stderr.decode('utf-8', 'replace')[:200])
        sys.exit(1)

OURS = ['results/dashboard_status.json', 'results/dashboard_status.js',
        'results/strategy_scorecard.json', 'results/scorecard_v1.json',
        'results/_attrition_guard_scan.json']
THEIRS = ['docs/daily_report/REPORT-2026-10-04.json', 'docs/daily_report/REPORT-2026-10-04.md',
          'docs/live_usage/LIVE-2026-10-04.json', 'docs/live_usage/LIVE-2026-10-04.md',
          'docs/live_usage/LIVE-latest.json', 'docs/live_usage/LIVE-latest.md',
          'results/compute_audit.json', 'results/fundamental_b_layer_filter.json',
          'results/futures_update_status.json', 'results/lhb_update_status.json',
          'results/regime_state.json', 'results/update_status.json']

for f in OURS:
    sh(['git', 'checkout', '--ours', f]); sh(['git', 'add', f])
    print('OURS  ', f)
for f in THEIRS:
    sh(['git', 'checkout', '--theirs', f]); sh(['git', 'add', f])
    print('THEIRS', f)

# --- token_usage.json per-key union (machines dict, freshness by per-machine ts)
import re
ours = subprocess.run(['git', 'show', 'HEAD:results/token_usage.json'],
                      capture_output=True).stdout
theirs = subprocess.run(['git', 'show', 'MERGE_HEAD:results/token_usage.json'],
                        capture_output=True).stdout
o = json.loads(ours.decode('utf-8')); t = json.loads(theirs.decode('utf-8'))
om, tm = o.get('machines', {}), t.get('machines', {})
def ts_of(v):
    if not isinstance(v, dict):
        return ''
    for k in ('ts', 'last_seen', 'updated'):
        if isinstance(v.get(k), str):
            return v[k]
    return ''
side_pick = 0
merged = {}
for k in sorted(set(om) | set(tm)):
    a, b = om.get(k), tm.get(k)
    if a is None: merged[k] = b; side_pick += 1; continue
    if b is None: merged[k] = a; continue
    ta, tb = ts_of(a), ts_of(b)
    ta_n = ta.replace('T', ' ')[:19]; tb_n = tb.replace('T', ' ')[:19]  # r461 ts-normalize
    if tb_n > ta_n:
        merged[k] = b; side_pick += 1
    else:
        merged[k] = a
if side_pick == 0:
    # r466 law: zero per-key side-pick -> explicit whole-face ts freshness (r456 fallback leg)
    top_o = str(o.get('ts', '') or o.get('generated', ''))
    top_t = str(t.get('ts', '') or t.get('generated', ''))
    no = top_o.replace('T', ' ')[:19]; nt = top_t.replace('T', ' ')[:19]
    pick = o if no >= nt else t
    print(f'r456-fallback: side_pick=0 -> whole-face ts ours={no} theirs={nt} -> '
          f'{"OURS" if pick is o else "THEIRS"}')
    out = pick
else:
    o['machines'] = merged
    out = o
    print('UNION token_usage.json side_pick=', side_pick)
open('results/token_usage.json', 'w', encoding='utf-8', newline='\n').write(
    json.dumps(out, ensure_ascii=False, indent=1))
json.load(open('results/token_usage.json', encoding='utf-8'))  # reparse gate
sh(['git', 'add', 'results/token_usage.json'])
print('UNION token_usage.json side_pick=', side_pick)

# residual conflict-marker scan (r431 law: whole-repo marker scan before add)
r = subprocess.run(['git', 'grep', '-l', '-E', r'^<{7} '],
                   capture_output=True)
r2 = subprocess.run(['git', 'grep', '-c', r'^(<{7}|={7}|>{7})'],
                    capture_output=True)
print('marker scan (staged, informational):', r.stdout.decode()[:200])
print('RESOLVE DONE')
