"""r627 bm-a merge resolver: HEAD(f10cb2fc7) vs origin/main(5e86daa1a), base=12da12955^..merge-base.

Merge stage numbering in a MERGE: :2: = ours (local bm-a), :3: = theirs (origin).
merge_lane_views resolve convention (r351): --stage2 = base_side = ORIGIN,
--stage3 = replay_side = LOCAL (same-second tie -> origin, r140 canon). So we
pass the SWAPPED blobs. Laws: R208/R216 take-new, r188 union via resolve canon,
R31 lane-owner authority, r378 bm-a host authority (dashboard faces), r185
parse-before-add, r405 blob-from-stage, r289 indent probe (inside resolve).
"""
import subprocess, json, re, sys, os

def stage(n, path):
    r = subprocess.run(['git', 'show', f':{n}:{path}'], capture_output=True)
    if r.returncode != 0:
        sys.exit(f'FATAL no :{n}:{path}: {r.stderr.decode("utf-8","replace")[:150]}')
    return r.stdout

TS_PAT = re.compile(r'"(?:generated|generated_at|updated|updated_at|ts|scan_ts|last_run)"\s*:\s*"([^"]+)"')

PAIRS = [
    ('docs/daily_report/REPORT-2026-10-03.json', 'docs/daily_report/REPORT-2026-10-03.md'),
    ('docs/live_usage/LIVE-2026-10-03.json', 'docs/live_usage/LIVE-2026-10-03.md'),
    ('docs/live_usage/LIVE-latest.json', 'docs/live_usage/LIVE-latest.md'),
]
RESOLVE_FACES = [
    'results/compute_audit.json',
    'results/regime_state.json',
    'results/token_usage.json',
    'results/update_status.json',
    'results/futures_update_status.json',
    'results/lhb_update_status.json',
]
TAKE_OURS = [
    'results/dashboard_status.json',
    'results/dashboard_status.js',
]
TS_NEW = [
    'results/fundamental_b_layer_filter.json',
    'results/scorecard_v1.json',
    'results/strategy_scorecard.json',
]

verdicts = {}

for js, md in PAIRS:
    b2, b3 = stage(2, js), stage(3, js)
    t2 = TS_PAT.search(b2.decode('utf-8', 'replace'))
    t3 = TS_PAT.search(b3.decode('utf-8', 'replace'))
    v2, v3 = (t2.group(1) if t2 else ''), (t3.group(1) if t3 else '')
    winner = 2 if v2 >= v3 else 3
    verdicts[js] = winner
    verdicts[md] = winner
    print(f'{js}: ours={v2} theirs={v3} -> take {"OURS" if winner == 2 else "THEIRS"}')
    for p, wb in ((js, b2 if winner == 2 else b3), (md, blob_md if (blob_md := stage(winner, md)) is not None else b'')):
        with open(p, 'wb') as f:
            f.write(wb)
        if p.endswith('.json'):
            json.loads(wb.decode('utf-8', 'replace'))

for p in TS_NEW:
    b2, b3 = stage(2, p), stage(3, p)
    t2 = TS_PAT.search(b2.decode('utf-8', 'replace'))
    t3 = TS_PAT.search(b3.decode('utf-8', 'replace'))
    v2, v3 = (t2.group(1) if t2 else ''), (t3.group(1) if t3 else '')
    winner = 2 if v2 >= v3 else 3
    verdicts[p] = winner
    wb = b2 if winner == 2 else b3
    with open(p, 'wb') as f:
        f.write(wb)
    json.loads(wb.decode('utf-8', 'replace'))
    print(f'{p}: ours={v2} theirs={v3} -> take {"OURS" if winner == 2 else "THEIRS"}')

for p in TAKE_OURS:
    wb = stage(2, p)
    with open(p, 'wb') as f:
        f.write(wb)
    if p.endswith('.json'):
        json.loads(wb.decode('utf-8', 'replace'))
    verdicts[p] = 2
    print(f'{p}: take OURS (bm-a host authority, r378 guard)')

for p in RESOLVE_FACES:
    s1 = p + '.s1.tmp'
    s2 = p + '.s2.tmp'
    s3 = p + '.s3.tmp'
    with open(s1, 'wb') as f: f.write(stage(1, p))
    with open(s2, 'wb') as f: f.write(stage(3, p))  # origin -> base_side
    with open(s3, 'wb') as f: f.write(stage(2, p))  # local  -> replay_side
    r = subprocess.run([sys.executable, 'scripts/merge_lane_views.py', 'resolve',
                        p, '--stage1', s1, '--stage2', s2, '--stage3', s3,
                        '--out', p], capture_output=True)
    out = (r.stdout + r.stderr).decode('utf-8', 'replace')
    print(out.strip())
    if r.returncode != 0:
        sys.exit(f'FATAL resolve {p} rc={r.returncode}')
    for tmp in (s1, s2, s3):
        os.remove(tmp)
    verdicts[p] = 'resolve-union'

print('RESOLVER DONE')
