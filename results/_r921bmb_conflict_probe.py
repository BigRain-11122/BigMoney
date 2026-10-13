import subprocess, json, sys


def stage_blob(path, stage):
    r = subprocess.run(['git', 'show', f':{stage}:{path}'], capture_output=True)
    if r.returncode != 0:
        return None
    try:
        return json.loads(r.stdout.decode('utf-8'))
    except Exception:
        return {'_raw_len': len(r.stdout), '_head': r.stdout[:120].decode('utf-8', 'replace')}


faces = [
    'fleet/machine-health.json',
    'results/_attrition_guard_scan.json',
    'results/_r686bmb_d19_check.json',
    'results/compute_audit.json',
    'results/d19_watermark.json',
    'results/daily_scorecard.json',
    'results/dashboard_status.js',
    'results/dashboard_status.json',
    'results/fundamental_b_layer_filter.json',
    'results/futures_update_status.json',
    'results/lhb_update_status.json',
    'results/paper_export/latest.json',
    'results/regime_state.json',
    'results/scorecard_v1.json',
    'results/strategy_scorecard.json',
]


def find_ts(obj, depth=0):
    """Recursively find timestamp-like keys."""
    hits = []
    if depth > 3 or not isinstance(obj, dict):
        return hits
    for k, v in obj.items():
        kl = str(k).lower()
        if isinstance(v, str) and ('ts' in kl or 'time' in kl or 'date' in kl or 'updated' in kl or 'generated' in kl):
            if len(v) >= 8:
                hits.append((k, v))
        elif isinstance(v, dict):
            sub = find_ts(v, depth + 1)
            for sk, sv in sub:
                hits.append((k + '.' + sk, sv))
    return hits[:6]


for p in faces:
    ours = stage_blob(p, 2)
    theirs = stage_blob(p, 3)
    print('=' * 20, p)
    if ours is None or theirs is None:
        print('  side-missing ours=', ours is not None, 'theirs=', theirs is not None)
        continue
    ot = find_ts(ours)
    tt = find_ts(theirs)
    print('  OURS   ts:', ot)
    print('  THEIRS ts:', tt)
