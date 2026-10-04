# r703 bm-b: UU face probe -- base/ours/theirs ts + ledger keys for all 19 conflict files
import subprocess, io, json

FILES = [
    'docs/daily_report/REPORT-2026-10-05.json', 'docs/daily_report/REPORT-2026-10-05.md',
    'docs/live_usage/LIVE-2026-10-05.json', 'docs/live_usage/LIVE-2026-10-05.md',
    'docs/live_usage/LIVE-latest.json', 'docs/live_usage/LIVE-latest.md',
    'results/_attrition_guard_scan.json', 'results/compute_audit.json',
    'results/dashboard_status.js', 'results/dashboard_status.json',
    'results/fundamental_b_layer_filter.json', 'results/futures_update_status.json',
    'results/lhb_update_status.json', 'results/regime_state.json',
    'results/scorecard_v1.json', 'results/strategy_scorecard.json',
    'results/token_usage.json', 'results/update_status.json', 'results/runnable_pool.json',
]

TS_KEYS = ['generated', 'ts', 'updated', 'updated_at', 'as_of', 'cutoff', 'scan_ts', 'verdict_ts']


def blob(stage, path):
    return subprocess.run(['git', 'show', ':%d:%s' % (stage, path)], capture_output=True).stdout


def pick_ts(obj):
    out = {}
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, str) and any(t in k.lower() for t in ('ts', 'time', 'date', 'generated', 'updated', 'as_of', 'cutoff')) and len(v) > 8:
                out[k] = v
    return out


def main():
    o = io.open('results/_r703bmb_uu_probe.txt', 'w', encoding='utf-8')
    for path in FILES:
        b1, b2, b3 = blob(1, path), blob(2, path), blob(3, path)
        same_12 = (b1 == b2)
        same_13 = (b1 == b3)
        line = '%s | bytes b/o/t=%d/%d/%d | ours==base:%s theirs==base:%s' % (path, len(b1), len(b2), len(b3), same_12, same_13)
        if path.endswith('.json'):
            try:
                j1, j2, j3 = json.loads(b2.decode('utf-8')), None, None
                j2 = json.loads(b2.decode('utf-8')); j3 = json.loads(b3.decode('utf-8'))
                t1 = pick_ts(j1); t3 = pick_ts(j3)
                line += ' | ours_ts=%s theirs_ts=%s' % (json.dumps(t1, ensure_ascii=False)[:180], json.dumps(t3, ensure_ascii=False)[:180])
                for k in ('history', 'launches', 'transitions', 'entries'):
                    if isinstance(j1, dict) and k in j1 and isinstance(j2, dict) and k in j2 and isinstance(j3, dict) and k in j3:
                        line += ' | %s len b/o/t=%s/%s/%s' % (k, len(j1.get(k, [])), len(j2.get(k, [])), len(j3.get(k, [])))
            except Exception as e:
                line += ' | json_err=%r' % (e,)
        o.write(line + '\n')
    o.close()
    print('probe written')

if __name__ == '__main__':
    main()
