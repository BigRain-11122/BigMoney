# -*- coding: utf-8 -*-
"""r305 bm-c pull-rebase wave2 resolver: 19 UU regen faces -> origin(:2:) wholesale (r296-3 canon).
All are full-rewrite regeneration faces (no append-only in batch); this round's S6 chain
re-derives every one of them. Evidence -> results/_r305bmc_resolve_evidence2.json
"""
import subprocess, json, hashlib

def blob(stage, path):
    return subprocess.check_output(['git', 'show', f':{stage}:{path}'])

paths = [
    'docs/daily_report/REPORT-2026-10-01.json',
    'docs/daily_report/REPORT-2026-10-01.md',
    'docs/live_usage/LIVE-2026-10-01.json',
    'docs/live_usage/LIVE-2026-10-01.md',
    'docs/live_usage/LIVE-latest.json',
    'docs/live_usage/LIVE-latest.md',
    'results/_attrition_guard_scan.json',
    'results/compute_audit.json',
    'results/daily_scorecard.json',
    'results/dashboard_status.js',
    'results/dashboard_status.json',
    'results/fundamental_b_layer_filter.json',
    'results/futures_update_status.json',
    'results/lhb_update_status.json',
    'results/prospect_promotion/_summary.json',
    'results/regime_state.json',
    'results/scorecard_v1.json',
    'results/strategy_scorecard.json',
    'results/update_status.json',
]
ev = {}
for p in paths:
    b2, b3 = blob(2, p), blob(3, p)
    with open(p, 'wb') as f:
        f.write(b2)
    ev[p] = {'action': 'origin-take(:2:)', 'sha2': hashlib.sha256(b2).hexdigest()[:12],
             'sha3_bm_c_r304': hashlib.sha256(b3).hexdigest()[:12],
             'jsonl_appendonly': p.endswith('.jsonl')}
# marker check across resolved set
bad = []
for p in paths:
    t = open(p, 'rb').read()
    if b'<<<<<<<' in t or b'>>>>>>>' in t or b'|||||||' in t:
        bad.append(p)
ev['_marker_check_clean'] = not bad
ev['_marker_files'] = bad
json.dump(ev, open('results/_r305bmc_resolve_evidence2.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print(json.dumps({'resolved': len(paths), 'markers_clean': not bad}, ensure_ascii=False))
