import json
import subprocess

def stage(side, path):
    out = subprocess.run(['git', 'show', f':{side}:{path}'], capture_output=True)
    return out.stdout

files_probe = [
    ('results/compute_audit.json', ['ts', 'history']),
    ('results/regime_state.json', ['ts', 'generated', 'history', 'transitions', 'state']),
    ('results/runnable_pool.json', ['ts', 'generated', 'updated_at']),
    ('results/scorecard_v1.json', ['generated', 'ts']),
    ('results/strategy_scorecard.json', ['generated', 'ts']),
    ('results/token_usage.json', ['ts', 'generated']),
    ('results/update_status.json', ['ts', 'generated']),
    ('results/futures_update_status.json', ['ts', 'generated']),
    ('results/lhb_update_status.json', ['ts', 'generated']),
    ('results/fundamental_b_layer_filter.json', ['ts', 'generated', 'updated_at']),
    ('results/dashboard_status.json', ['ts', 'generated']),
    ('docs/daily_report/REPORT-2026-09-29.json', ['generated', 'ts']),
    ('docs/live_usage/LIVE-2026-09-29.json', ['generated', 'ts']),
    ('docs/live_usage/LIVE-latest.json', ['generated', 'ts']),
]

for path, keys in files_probe:
    print('=====', path)
    for side, label in ((2, 'ours(bm-c)'), (3, 'theirs(bm-b)')):
        raw = stage(side, path)
        try:
            d = json.loads(raw)
            probe = {k: d.get(k) for k in keys if k in d}
            extra = ''
            if 'history' in d and isinstance(d['history'], list):
                extra = f" history_len={len(d['history'])} last_ts={d['history'][-1].get('ts') if d['history'] and isinstance(d['history'][-1], dict) else '?'}"
            if 'transitions' in d and isinstance(d['transitions'], list):
                extra += f" transitions_len={len(d['transitions'])}"
            if 'entries' in d:
                e = d['entries']
                if isinstance(e, dict):
                    extra += f" entries={len(e)}"
                elif isinstance(e, list):
                    extra += f" entries={len(e)}"
            print(f'  {label}: {json.dumps(probe, ensure_ascii=False, default=str)[:220]}{extra}')
        except Exception as ex:
            print(f'  {label}: JSON FAIL {ex}; head bytes: {raw[:80]!r}')
