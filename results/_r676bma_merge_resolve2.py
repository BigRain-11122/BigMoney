# _r676bma_merge_resolve2.py -- second wave (bm-c r470), same policy family
import json, subprocess, sys

def sh(args):
    r = subprocess.run(args, capture_output=True)
    if r.returncode != 0:
        print('FAIL', args, r.stderr.decode('utf-8', 'replace')[:200]); sys.exit(1)

OURS = ['results/dashboard_status.json', 'results/dashboard_status.js',
        'results/strategy_scorecard.json', 'results/scorecard_v1.json']
THEIRS = ['results/compute_audit.json', 'results/regime_state.json',
          'results/_attrition_guard_scan.json', 'results/t35_open_fill_verify.json',
          'results/prospect_paper/_summary.json', 'results/prospect_promotion/_summary.json']
for f in OURS:
    sh(['git', 'checkout', '--ours', f]); sh(['git', 'add', f]); print('OURS  ', f)
for f in THEIRS:
    sh(['git', 'checkout', '--theirs', f]); sh(['git', 'add', f]); print('THEIRS', f)

# token_usage per-key union -> r466 whole-face fallback
ours = subprocess.run(['git', 'show', 'HEAD:results/token_usage.json'], capture_output=True).stdout
theirs = subprocess.run(['git', 'show', 'MERGE_HEAD:results/token_usage.json'], capture_output=True).stdout
o = json.loads(ours.decode('utf-8')); t = json.loads(theirs.decode('utf-8'))
om, tm = o.get('machines', {}), t.get('machines', {})
def ts_of(v):
    if not isinstance(v, dict): return ''
    for k in ('ts', 'last_seen', 'updated'):
        if isinstance(v.get(k), str): return v[k]
    return ''
side_pick = 0; merged = {}
for k in sorted(set(om) | set(tm)):
    a, b = om.get(k), tm.get(k)
    if a is None: merged[k] = b; side_pick += 1; continue
    if b is None: merged[k] = a; continue
    ta_n = ts_of(a).replace('T', ' ')[:19]; tb_n = ts_of(b).replace('T', ' ')[:19]
    if tb_n > ta_n: merged[k] = b; side_pick += 1
    else: merged[k] = a
if side_pick == 0:
    no = str(o.get('ts', '') or o.get('generated', '')).replace('T', ' ')[:19]
    nt = str(t.get('ts', '') or t.get('generated', '')).replace('T', ' ')[:19]
    pick = o if no >= nt else t
    print(f'r456-fallback: side_pick=0 -> whole-face ts ours={no} theirs={nt} -> '
          f'{"OURS" if pick is o else "THEIRS"}')
    out = pick
else:
    o['machines'] = merged; out = o
    print('UNION token_usage.json side_pick=', side_pick)
open('results/token_usage.json', 'w', encoding='utf-8', newline='\n').write(
    json.dumps(out, ensure_ascii=False, indent=1))
json.load(open('results/token_usage.json', encoding='utf-8'))
sh(['git', 'add', 'results/token_usage.json'])
print('RESOLVE2 DONE')
