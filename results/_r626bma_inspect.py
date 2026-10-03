# -*- coding: utf-8 -*-
"""r626 bm-a rebase-conflict stage inspector (repr-first discipline, bytes via git)."""
import subprocess, json

def stage(path, n):
    r = subprocess.run(['git', 'show', f':{n}:{path}'], capture_output=True)
    return r.stdout

def probe_ts(obj, depth=0):
    """Deep-scan for ts-like keys (r311/D-09 law); return list of (path, value)."""
    hits = []
    if depth > 6:
        return hits
    if isinstance(obj, dict):
        for k, v in obj.items():
            kk = str(k).lower().replace('_', '').replace('-', '')
            if isinstance(v, str) and ('ts' in kk or 'at' in kk or 'generated' in kk or 'updated' in kk) and v[:2] == '20':
                hits.append((k, v))
            elif isinstance(v, (dict, list)):
                hits.extend(probe_ts(v, depth + 1))
    elif isinstance(obj, list):
        for it in obj[:3] + (obj[-1:] if len(obj) > 3 else []):
            if isinstance(it, (dict, list)):
                hits.extend(probe_ts(it, depth + 1))
    return hits

files = [
    'results/_attrition_guard_scan.json',
    'results/fundamental_b_layer_filter.json',
    'docs/daily_report/REPORT-2026-10-03.json',
    'docs/live_usage/LIVE-2026-10-03.json',
    'docs/live_usage/LIVE-latest.json',
]
for f in files:
    b2, b3 = stage(f, 2), stage(f, 3)
    print('=' * 20, f)
    try:
        o2, o3 = json.loads(b2), json.loads(b3)
        print('stage2 top keys:', list(o2.keys())[:12] if isinstance(o2, dict) else type(o2).__name__)
        print('stage2 ts probes:', probe_ts(o2)[:6])
        print('stage3 ts probes:', probe_ts(o3)[:6])
        if f.endswith('_attrition_guard_scan.json'):
            print('stage2 bytes:', len(b2), 'stage3 bytes:', len(b3))
            print('stage2 repr head:', repr(b2[:400]))
            print('stage3 repr head:', repr(b3[:400]))
    except Exception as e:
        print('parse fail:', e, '| s2 head:', repr(b2[:120]), '| s3 head:', repr(b3[:120]))
