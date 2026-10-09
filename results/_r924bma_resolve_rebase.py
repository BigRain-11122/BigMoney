# -*- coding: utf-8 -*-
# r924 bm-a rebase UU resolver (r918/r907 canon): attrition take-newer assert-mine,
# compute_audit rolling-history full-json dedupe UNION zero-loss, token_usage
# per-machine sections union newer-wins, generic deep-ts take-newer for the
# 6 generated product faces (daily_scorecard/dashboard x2/paper_export x2/scorecard x2/strategy).
import subprocess, json, sys, re, io
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

def show(stage, path):
    return subprocess.run(['git', 'show', f':{stage}:{path}'], capture_output=True).stdout

def find_ts(obj, depth=0):
    # deep timestamp probe: common keys, top-level first
    prio = ['ts', 'generated', 'updated', 'asof', 'export_date', 'date']
    for k in prio:
        if isinstance(obj, dict) and k in obj and isinstance(obj[k], (str, int)):
            return str(obj[k]), k
    if isinstance(obj, dict) and depth < 2:
        for v in obj.values():
            r = find_ts(v, depth + 1)
            if r[0]:
                return r
    return None, None

UU = [
    'results/_attrition_guard_scan.json',
    'results/compute_audit.json',
    'results/daily_scorecard.json',
    'results/dashboard_status.js',
    'results/dashboard_status.json',
    'results/paper_export/export-2026-10-08.json',
    'results/paper_export/latest.json',
    'results/scorecard_v1.json',
    'results/strategy_scorecard.json',
    'results/token_usage.json',
]

for path in UU:
    if path == 'results/compute_audit.json':
        continue  # handled by union below
    if path == 'results/token_usage.json':
        continue  # handled by sections union below
    if path == 'results/_attrition_guard_scan.json':
        mine = show(3, path); theirs = show(2, path)
        ma = json.loads(mine.decode('utf-8')); ta = json.loads(theirs.decode('utf-8'))
        if ma['ts'] >= ta['ts']:
            win, wsrc, wts = mine, 'MINE', ma['ts']
        else:
            win, wsrc, wts = theirs, 'THEIRS(origin)', ta['ts']
        wj = json.loads(win.decode('utf-8'))
        assert wj.get('rc') == 0 and wj.get('active_loss') is False, f"winner attrition not CLEAN: {wsrc}"
        open(path, 'wb').write(win)
        print('attrition: take', wsrc, 'ts', wts, 'rc0 CLEAN')
        continue
    if path.endswith('.js'):
        mine = show(3, path).decode('utf-8', errors='replace')
        theirs = show(2, path).decode('utf-8', errors='replace')
        m = re.findall(r'"generated":\s*"([^"]+)"', mine)
        t = re.findall(r'"generated":\s*"([^"]+)"', theirs)
        assert m and t, f"dashboard.js generated ts not found: {m} {t}"
        if m[0] >= t[0]:
            win, wsrc, wts = mine, 'MINE', m[0]
        else:
            win, wsrc, wts = theirs, 'THEIRS(origin)', t[0]
        open(path, 'w', encoding='utf-8', newline='').write(win)
        print('dashboard_status.js: take', wsrc, 'generated', wts)
        continue
    mine = show(3, path); theirs = show(2, path)
    ma = json.loads(mine.decode('utf-8')); ta = json.loads(theirs.decode('utf-8'))
    mts, mk = find_ts(ma); tts, tk = find_ts(ta)
    if mts is None or tts is None:
        open(path, 'wb').write(mine)
        print(path, ': no ts probe -> take MINE (successor face)')
        continue
    if mts >= tts:
        open(path, 'wb').write(mine)
        print(path, ': take MINE', mk, mts, '(theirs', tk, tts, ')')
    else:
        open(path, 'wb').write(theirs)
        print(path, ': take THEIRS (origin newer)', tk, tts, '(mine', mk, mts, ')')

# token_usage: per-machine sections union, newer section wins per key; generated = max
mt = json.loads(show(3, 'results/token_usage.json').decode('utf-8'))
tt = json.loads(show(2, 'results/token_usage.json').decode('utf-8'))
mm, tm = mt.get('machines', {}), tt.get('machines', {})
out_m = {}
for k in sorted(set(mm) | set(tm)):
    a, b = mm.get(k), tm.get(k)
    if a is None: out_m[k] = b; continue
    if b is None: out_m[k] = a; continue
    ats = str(a.get('ts') or a.get('updated') or '')
    bts = str(b.get('ts') or b.get('updated') or '')
    out_m[k] = a if ats >= bts else b
out_tk = dict(mt)
out_tk['machines'] = out_m
out_tk['generated'] = max(mt.get('generated', ''), tt.get('generated', ''))
open('results/token_usage.json', 'w', encoding='utf-8', newline='').write(
    json.dumps(out_tk, ensure_ascii=False, indent=1))
print('token_usage: sections union machines', sorted(set(mm) | set(tm)),
      'generated', out_tk['generated'])

# compute_audit: rolling-history full-json dedupe UNION, sorted by ts, latest = newer side
ca = json.loads(show(2, 'results/compute_audit.json').decode('utf-8'))
cb = json.loads(show(3, 'results/compute_audit.json').decode('utf-8'))
seen = {}
for h in ca['history'] + cb['history']:
    k = json.dumps(h, sort_keys=True, ensure_ascii=False)
    if k not in seen:
        seen[k] = h
hist = sorted(seen.values(), key=lambda h: h.get('ts', ''))
ka = {json.dumps(h, sort_keys=True, ensure_ascii=False) for h in ca['history']}
kb = {json.dumps(h, sort_keys=True, ensure_ascii=False) for h in cb['history']}
assert ka | kb <= {json.dumps(h, sort_keys=True, ensure_ascii=False) for h in hist}, "union zero-loss assert failed"
latest = cb['latest'] if str(cb['latest'].get('ts', '')) >= str(ca['latest'].get('ts', '')) else ca['latest']
out = {'history': hist, 'latest': latest}
open('results/compute_audit.json', 'w', encoding='utf-8', newline='').write(
    json.dumps(out, ensure_ascii=False, indent=1))
print('compute_audit: union', len(ca['history']), '+', len(cb['history']), '->', len(hist),
      '(origin-only', len(ka - kb), 'mine-only', len(kb - ka), ') latest ts', latest.get('ts'))
print('RESOLVED', len(UU), 'faces, zero-loss asserts PASS')
