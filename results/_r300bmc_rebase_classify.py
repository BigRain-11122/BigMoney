# r300 rebase resolver: classify 18 UU files (stage2=origin-base, stage3=my commit during rebase)
import json, subprocess, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

FILES = [
    'docs/daily_report/REPORT-2026-10-01.json',
    'docs/daily_report/REPORT-2026-10-01.md',
    'docs/live_usage/LIVE-2026-10-01.json',
    'docs/live_usage/LIVE-2026-10-01.md',
    'docs/live_usage/LIVE-latest.json',
    'docs/live_usage/LIVE-latest.md',
    'results/_attrition_guard_scan.json',
    'results/compute_audit.json',
    'results/dashboard_status.js',
    'results/dashboard_status.json',
    'results/fundamental_b_layer_filter.json',
    'results/futures_update_status.json',
    'results/lhb_update_status.json',
    'results/regime_state.json',
    'results/scorecard_v1.json',
    'results/strategy_scorecard.json',
    'results/token_usage.json',
    'results/update_status.json',
]

META_KEYS = {'ts', 'generated', 'generated_at', 'generated_at_local', 'elapsed_sec', 'elapsed_s',
             'machine', 'host_machine', 'updated', 'wall_clock', 'duration_sec', 'last_run',
             'heartbeat_epoch_utc', 'clock_read', 'generated_by', 'author'}


def blob(stage, path):
    r = subprocess.run(['git', 'show', f':{stage}:{path}'], capture_output=True)
    return r.stdout.decode('utf-8', errors='replace')


def strip_meta(obj):
    if isinstance(obj, dict):
        return {k: strip_meta(v) for k, v in sorted(obj.items()) if k not in META_KEYS}
    if isinstance(obj, list):
        return [strip_meta(x) for x in obj]
    return obj


for path in FILES:
    b2, b3 = blob(2, path), blob(3, path)
    if path.endswith('.json') or path.endswith('.js') and path.startswith('results/dashboard'):
        try:
            j2, j3 = json.loads(b2), json.loads(b3)
            same_meta_stripped = strip_meta(j2) == strip_meta(j3)
            # report differing top-level keys for the unequal ones
            diffkeys = [k for k in set(list(j2.keys()) + list(j3.keys()))
                        if strip_meta(j2.get(k)) != strip_meta(j3.get(k))]
            print(f'{path} | equal_except_meta={same_meta_stripped} | diff_keys={diffkeys[:6]}')
        except Exception as e:
            print(f'{path} | JSON_ERR {e.args[0][:40]}')
    else:
        # md text: report line-diff count
        l2, l3 = b2.splitlines(), b3.splitlines()
        import difflib
        delta = sum(1 for _ in difflib.unified_diff(l2, l3, lineterm='')) - 2
        print(f'{path} | text_delta_lines={max(delta, 0)}')
