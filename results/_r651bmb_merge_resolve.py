# -*- coding: utf-8 -*-
# r651 bm-b merge-conflict resolver: 14 UU S6 regen faces (r650 lineage recipe)
# 5 tool-covered faces -> merge_lane_views resolve (single-source recipes)
# 9 snapshot faces -> take-new-by-ts (ours S6 06:08-06:11 vs bm-a r661 06:00-06:06 expected)
import subprocess, json, sys, io
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
    'results/update_status.json',
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
    if depth > 4 or obj is None:
        return None
    if isinstance(obj, dict):
        for k in ('ts', 'generated_at', 'updated', 'updated_at', 'scan_time', 'time', 'asof', 'generated'):
            v = obj.get(k)
            if isinstance(v, str) and len(v) >= 10:
                return v
        for v in obj.values():
            r = find_ts(v, depth + 1)
            if r:
                return r
    elif isinstance(obj, list):
        for v in obj[:5]:
            r = find_ts(v, depth + 1)
            if r:
                return r
    return None

verdicts = {}
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
            # md twin: follow its json twin verdict; fallback ours (our S6 derive 06:08-11 newer)
            twin = f[:-3] + '.json' if f.endswith('.md') else None
            if twin and twin in verdicts:
                side, why = verdicts[twin], 'md-twin follows json verdict'
            else:
                side, why = 'ours', 'no-ts/md-twin default ours (S6 derive 06:08-11 newer)'
    verdicts[f] = side
    rc, _, err = git('checkout', ('--ours' if side == 'ours' else '--theirs'), f)
    if rc != 0:
        print('[snap]', f, 'checkout fail', err[:150]); fails += 1; continue
    rc, _, err = git('add', f)
    if rc != 0:
        print('[snap]', f, 'add fail', err[:150]); fails += 1; continue
    print('[snap]', f, '->', side, '|', why)

# parse-verify all resolved json faces staged clean (r644 law: content check not rc-only)
bad = 0
for f in TOOL_FACES + [x for x in SNAP_FACES if x.endswith('.json')]:
    rc, txt, _ = git('show', ':' + f)
    if rc != 0:
        continue
    try:
        json.loads(txt)
    except Exception as e:
        print('PARSE-FAIL', f, repr(e)[:100]); bad += 1
print('resolver done, fails =', fails, 'parse_fail =', bad)
sys.exit(1 if (fails or bad) else 0)
