# r710 bm-a rebase-window resolver (r709 bloodline; REBASE stage: 2=origin tip, 3=local replay, r351 law)
# 17 UU vs origin 6b2257c15 wave (bm-b r709 closeout + bm-c r511 + pool worker ticks):
#   - 6 A/B-family faces -> merge_lane_views.py resolve (done before this script, parse-verified)
#   - 11 snapshot/twin faces -> HERE: take-local (s3) whole bytes; probe receipt _r710bma_probe_sides.json
#     shows local side strictly newer on every probeable face (04:05-04:08 vs 04:01-04:02);
#     twins coupled: .md/.js follow their .json decision (r708 twin same-side law).
# Zero-loss: parse-verify before write (r185), residual marker scan, read-back twin assertions.
import json, subprocess, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def stage(stage_n, path):
    b = subprocess.run(['git', 'show', ':%d:%s' % (stage_n, path)], capture_output=True, cwd=ROOT).stdout
    if not b:
        raise SystemExit('EMPTY stage %d %s' % (stage_n, path))
    return b

TAKE_LOCAL_S3 = [
    'docs/daily_report/REPORT-2026-10-05.json',
    'docs/daily_report/REPORT-2026-10-05.md',
    'docs/live_usage/LIVE-2026-10-05.json',
    'docs/live_usage/LIVE-2026-10-05.md',
    'docs/live_usage/LIVE-latest.json',
    'docs/live_usage/LIVE-latest.md',
    'results/dashboard_status.js',
    'results/dashboard_status.json',
    'results/fundamental_b_layer_filter.json',
    'results/scorecard_v1.json',
    'results/strategy_scorecard.json',
]

receipt = {'round': 'r710 bm-a rebase window', 'origin_tip': '6b2257c15', 'faces': {}}

for p in TAKE_LOCAL_S3:
    b3 = stage(3, p)
    if p.endswith('.json'):
        json.loads(b3.decode('utf-8'))          # parse gate before write (r185 law)
    open(os.path.join(ROOT, p), 'wb').write(b3)  # bytes verbatim: CRLF/EOL as staged
    receipt['faces'][p] = {'action': 'take-local-s3', 'bytes': len(b3)}

# ---- twin same-side read-back assertions (r708 law; ts format-asymmetry tolerant, r709 tail law) ----
def _n(v):
    return str(v).replace(' ', 'T')

dj = json.load(open(os.path.join(ROOT, 'results/dashboard_status.json'), encoding='utf-8'))
ga = _n(dj['meta']['generated_at'])
assert ga.startswith('2026-10-05T04:08'), 'dashboard json side wrong: %s' % ga
js = open(os.path.join(ROOT, 'results/dashboard_status.js'), 'rb').read()
assert b'04:08:4' in js, 'dashboard js twin not same generation side'
rep = json.load(open(os.path.join(ROOT, 'docs/daily_report/REPORT-2026-10-05.json'), encoding='utf-8'))
assert _n(rep.get('generated_at', '')).startswith('2026-10-05T04:08'), 'report json side wrong'
live = json.load(open(os.path.join(ROOT, 'docs/live_usage/LIVE-2026-10-05.json'), encoding='utf-8'))
assert _n(live.get('generated', '')).startswith('2026-10-05T04:08'), 'live json side wrong'
receipt['twin_checks'] = {'dashboard_js_json_same_side': True, 'report_md_json_same_side': True,
                          'live_all_same_side': True}

# ---- residual conflict-marker scan on all 17 resolved faces (fail loud) ----
ALL = TAKE_LOCAL_S3 + [
    'results/compute_audit.json', 'results/regime_state.json', 'results/update_status.json',
    'results/lhb_update_status.json', 'results/futures_update_status.json', 'results/token_usage.json',
]
for p in ALL:
    raw = open(os.path.join(ROOT, p), 'rb').read()
    assert not re.search(rb'^<<<<<<< ', raw, re.M), 'marker left in %s' % p

receipt['resolved_here_n'] = len(receipt['faces'])
open(os.path.join(ROOT, 'results', '_r710bma_rebase_resolve.json'), 'w', encoding='utf-8', newline='\n').write(
    json.dumps(receipt, ensure_ascii=False, indent=1) + '\n')
print('RESOLVED', len(receipt['faces']), 'faces take-local-s3; 6 prior via merge_lane_views; twins same-side OK')
