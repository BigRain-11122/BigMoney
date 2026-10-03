"""r619 bm-b: probe UU conflict sides for the 9 UNKNOWN files (ts/machine ownership)."""
import subprocess, re, sys

def blob(side, path):
    r = subprocess.run(['git', 'show', f':{side}:{path}'], capture_output=True)
    if r.returncode != 0:
        return None
    return r.stdout.decode('utf-8', 'replace')

paths = [
    'docs/daily_report/REPORT-2026-10-03.json',
    'docs/live_usage/LIVE-latest.json',
    'results/_attrition_guard_scan.json',
    'results/scorecard_v1.json',
    'results/strategy_scorecard.json',
    'results/dashboard_status.json',
    'results/update_status.json',
    'results/token_usage.json',
    'results/regime_state.json',
    'results/compute_audit.json',
]
TS_RE = re.compile(r'"(generated|generated_at|updated|updated_at|ts|scan_ts|cutoff|asof|as_of|last_run|evidence_cutoff)"\s*:\s*"([^"]{4,40})"')
M_RE = re.compile(r'"machine"\s*:\s*"([^"]+)"')

for p in paths:
    print('=' * 8, p)
    for side in (2, 3):
        t = blob(side, p)
        if t is None:
            print(f'  :{side}: <missing>')
            continue
        ts = TS_RE.findall(t)
        m = M_RE.findall(t)
        first_ts = ts[:4] if ts else []
        print(f'  :{side}: len={len(t)} ts={first_ts} machine={m[:3]}')
