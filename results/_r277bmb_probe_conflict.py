# r277 bm-b: rebase-2 conflict family probe (shapes + ts candidates both sides)
import json, subprocess

def blob(stage, path):
    r = subprocess.run(['git', 'show', f':{stage}:{path}'], capture_output=True)
    return r.stdout

def flat_ts(obj):
    """r267 law: recursive flatten, normalize T<->space (r265), collect ts-like strings."""
    out = []
    stack = [('', obj)]
    while stack:
        k, v = stack.pop()
        if isinstance(v, dict):
            for kk, vv in v.items():
                stack.append((kk, vv))
        elif isinstance(v, str) and ('ts' in k.lower() or 'generated' in k.lower()
                                     or 'updated' in k.lower() or k in ('asof', 'date')):
            n = v.replace('T', ' ').replace('+08:00', '').strip()
            if len(n) >= 10:
                out.append((k, n))
    return out

files = [
    'docs/daily_report/REPORT-2026-09-26.json',
    'results/daily_scorecard.json',
    'results/dashboard_status.json',
    'results/fundamental_b_layer_filter.json',
    'results/futures_update_status.json',
    'results/heat_update_status.json',
    'results/lhb_update_status.json',
    'results/regime_state.json',
    'results/scorecard_v1.json',
    'results/strategy_scorecard.json',
    'results/token_usage.json',
    'results/update_status.json',
    'results/compute_audit.json',
    'results/autofill_state.json',
]
for p in files:
    try:
        a = json.loads(blob(2, p).decode('utf-8-sig'))
        b = json.loads(blob(3, p).decode('utf-8-sig'))
    except Exception as e:
        print(p, 'PARSE FAIL', e)
        continue
    ta, tb = flat_ts(a), flat_ts(b)
    ma = max((v for _, v in ta), default=None)
    mb = max((v for _, v in tb), default=None)
    lists_a = {k: len(v) for k, v in a.items() if isinstance(v, list)} if isinstance(a, dict) else {}
    print(p)
    print('  :2(origin) ts-max=%s lists=%s' % (ma, lists_a))
    print('  :3(mine)   ts-max=%s lists=%s' % (mb, {k: len(v) for k, v in b.items() if isinstance(v, list)} if isinstance(b, dict) else {}))
