# -*- coding: utf-8 -*-
# r650 bm-b merge-conflict resolver: 14 UU S6 regen faces
# 5 tool-covered faces -> merge_lane_views resolve (single-source recipes)
# 9 snapshot faces -> take-new-by-ts (r649 attrition grading; ours 05:50-53 vs theirs 05:47-49 expected)
import subprocess, json, sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

def git(*a):
    p = subprocess.run(['git'] + list(a), capture_output=True)
    return p.returncode, p.stdout.decode('utf-8', 'replace'), p.stderr.decode('utf-8', 'replace')

TOOL_FACES = [
    'results/compute_audit.json',
    'results/regime_state.json',
    'results/lhb_update_status.json',
    'results/futures_update_status.json',
    'results/token_usage.json',
]
SNAP_FACES = [
    'docs/daily_report/REPORT-2026-10-04.json',
    'docs/daily_report/REPORT-2026-10-04.md',
    'docs/live_usage/LIVE-2026-10-04.json',
    'docs/live_usage/LIVE-2026-10-04.md',
    'docs/live_usage/LIVE-latest.json',
    'docs/live_usage/LIVE-latest.md',
    'results/_attrition_guard_scan.json',
    'results/fundamental_b_layer_filter.json',
]

fails = 0
for f in TOOL_FACES:
    r = subprocess.run([sys.executable, 'scripts/merge_lane_views.py', 'resolve', f],
                       capture_output=True)
    out = (r.stdout or b'').decode('utf-8', 'replace') + (r.stderr or b'').decode('utf-8', 'replace')
    last = [l for l in out.strip().splitlines() if l.strip()][-2:]
    print('[tool]', f, 'rc=%d' % r.returncode, '|', ' ; '.join(last)[:200])
    if r.returncode != 0:
        fails += 1
        continue
    rc, _, err = git('add', f)
    if rc != 0:
        print('  add failed:', err[:200]); fails += 1

def find_ts(obj, depth=0):
    """recursively find first ts-like string field"""
    if depth > 4 or obj is None: return None
    if isinstance(obj, dict):
        for k in ('ts', 'generated_at', 'updated', 'updated_at', 'scan_time', 'time', 'asof', 'generated'):
            v = obj.get(k)
            if isinstance(v, str) and len(v) >= 10: return v
        for v in obj.values():
            r = find_ts(v, depth + 1)
            if r: return r
    elif isinstance(obj, list):
        for v in obj[:5]:
            r = find_ts(v, depth + 1)
            if r: return r
    return None

for f in SNAP_FACES:
    rc2, ours, _ = git('show', ':2:' + f)
    rc3, theirs, _ = git('show', ':3:' + f)
    if rc2 != 0 and rc3 != 0:
        print('[snap]', f, 'NO STAGES'); fails += 1; continue
    if rc3 != 0:
        side, why = 'ours', 'theirs missing'
    elif rc2 != 0:
        side, why = 'theirs', 'ours missing'
    else:
        ts_o = ts_t = None
        if f.endswith('.json'):
            try: ts_o = find_ts(json.loads(ours))
            except Exception: ts_o = None
            try: ts_t = find_ts(json.loads(theirs))
            except Exception: ts_t = None
        if ts_o and ts_t:
            side, why = ('ours' if ts_o >= ts_t else 'theirs'), f'ours {ts_o} vs theirs {ts_t}'
        else:
            # md twins / no-ts: pair with json twin verdict; default ours (my 05:50-53 derives vs bm-c 05:47-49)
            side, why = 'ours', 'no-ts/md-twin default ours (S6 derive 05:50-53 newer)'
    rc, _, err = git('checkout', ('--ours' if side == 'ours' else '--theirs'), f)
    if rc != 0:
        print('[snap]', f, 'checkout fail', err[:150]); fails += 1; continue
    rc, _, err = git('add', f)
    if rc != 0:
        print('[snap]', f, 'add fail', err[:150]); fails += 1; continue
    print('[snap]', f, '->', side, '|', why)

print('resolver done, fails =', fails)
sys.exit(1 if fails else 0)
