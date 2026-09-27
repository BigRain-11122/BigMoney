import json, subprocess, re, sys

ROOT = r'K:\Fluxgroup\FluxGroup\quant\bigmoney'

def side_blob(path, stage):
    r = subprocess.run(['git', 'show', f':{stage}:{path}'], capture_output=True)
    assert r.returncode == 0 and r.stdout.strip(), (path, stage, r.returncode)
    return r.stdout

def parse_ts(obj):
    # find any plausible timestamp, top-level or one level deep
    if not isinstance(obj, dict):
        return None
    for k in ('ts', 'updated_at', 'updated', 'generated', 'generated_at', 'asof', 'last_run'):
        v = obj.get(k)
        if isinstance(v, str) and re.match(r'^\d{4}-\d{2}-\d{2}', v):
            return v
    for v in obj.values():
        if isinstance(v, dict):
            t = parse_ts(v)
            if t:
                return t
    return None

def jload(b):
    return json.loads(b.decode('utf-8-sig'))

conflicts = subprocess.run(['git', 'diff', '--name-only', '--diff-filter=U'],
                           capture_output=True, text=True).stdout.strip().split('\n')
assert conflicts and conflicts[0], 'no UU files?'

report = []
# twin pairs: decide side by json ts, apply to both members
TWIN_PAIRS = [
    ('docs/daily_report/REPORT-2026-09-27.json', 'docs/daily_report/REPORT-2026-09-27.md'),
    ('results/dashboard_status.json', 'results/dashboard_status.js'),
]

handled = set()

def take_side(path, ours, theirs, prefer='fresher'):
    o = jload(ours) if path.endswith('.json') else None
    t = jload(theirs) if path.endswith('.json') else None
    if o is not None and t is not None:
        to, tt = parse_ts(o), parse_ts(t)
        if to and tt and to != tt:
            keep = 'ours' if (to > tt) == (prefer == 'fresher') else 'theirs'
        elif o == t:
            keep = 'theirs'  # content equal, either fine
        else:
            keep = 'theirs' if prefer in ('fresher', 'mine') else 'ours'
            if to and tt and to == tt and o != t:
                keep = 'theirs'  # same-ts deterministic re-derive: mine (later run)
    else:
        keep = prefer
    blob = ours if keep == 'ours' else theirs
    with open(path, 'wb') as f:
        f.write(blob)
    report.append(f'{path}: keep={keep} ts_ours={parse_ts(jload(ours)) if path.endswith(".json") else "?"} ts_theirs={parse_ts(jload(theirs)) if path.endswith(".json") else "?"}')
    return keep

# 1. compute_audit: ts-key union, no cap, latest fresher
p = 'results/compute_audit.json'
a, b = jload(side_blob(p, 2)), jload(side_blob(p, 3))
ma = {r['ts']: r for r in a['history']}
mb = {r['ts']: r for r in b['history']}
diverge = [ts for ts in (set(ma) & set(mb)) if ma[ts] != mb[ts]]
assert not diverge, f'same-ts diverge: {diverge}'
rows = [ma[ts] if ts in ma else mb[ts] for ts in sorted(set(ma) | set(mb))]
latest = a['latest'] if a['latest']['ts'] > b['latest']['ts'] else b['latest']
merged = {'latest': latest, 'history': rows}
with open(p, 'w', encoding='utf-8', newline='\n') as f:
    f.write(json.dumps(merged, ensure_ascii=False, indent=1) + '\n')
d2 = json.load(open(p, encoding='utf-8'))
assert len(d2['history']) == len(rows)
report.append(f'{p}: UNION {len(ma)}|{len(mb)}->{len(rows)} diverge=0 latest={latest["ts"]}')
handled.add(p)

# 2. autofill_state: last_tick max-ts (r109 law)
p = 'results/autofill_state.json'
a, b = jload(side_blob(p, 2)), jload(side_blob(p, 3))
ta, tb = a.get('last_tick', ''), b.get('last_tick', '')
keep_b = str(tb) >= str(ta)
merged = b if keep_b else a
with open(p, 'w', encoding='utf-8', newline='\n') as f:
    f.write(json.dumps(merged, ensure_ascii=False, indent=1) + '\n')
report.append(f'{p}: last_tick max-ts keep={"theirs" if keep_b else "ours"} ({ta} vs {tb})')
handled.add(p)

# 3. x2_watch_log.jsonl: append-only line union by key, ts-sorted
p = 'results/x2_watch_log.jsonl'
la = [l for l in side_blob(p, 2).decode('utf-8-sig').splitlines() if l.strip()]
lb = [l for l in side_blob(p, 3).decode('utf-8-sig').splitlines() if l.strip()]
seen, out = set(), []
for l in sorted(set(la) | set(lb)):
    try:
        ts = json.loads(l).get('ts', '')
    except Exception:
        ts = ''
    key = (ts, l[:120])
    if key in seen:
        continue
    seen.add(key)
    out.append(l)
with open(p, 'w', encoding='utf-8', newline='\n') as f:
    f.write('\n'.join(out) + '\n')
report.append(f'{p}: line-union {len(la)}|{len(lb)}->{len(out)}')
handled.add(p)

# 4. twin pairs: side by json ts, both members
for jp, mp in TWIN_PAIRS:
    jo, jt = jload(side_blob(jp, 2)), jload(side_blob(jp, 3))
    to, tt = parse_ts(jo), parse_ts(jt)
    keep = 'theirs' if (not to or (tt and tt >= to)) else 'ours'
    for path in (jp, mp):
        blob = side_blob(path, 2) if keep == 'ours' else side_blob(path, 3)
        with open(path, 'wb') as f:
            f.write(blob)
    report.append(f'{jp}+{mp}: twin same-side keep={keep} (ts {to} vs {tt})')
    handled.add(jp)
    handled.add(mp)

# 5. remaining files: fresher-ts JSON take
for path in conflicts:
    if path in handled or not path:
        continue
    ours, theirs = side_blob(path, 2), side_blob(path, 3)
    take_side(path, ours, theirs, prefer='fresher')

print('\n'.join(report))
print(f'--- resolved {len(conflicts)} UU files')

# final verify: every json parses, no conflict markers anywhere
import os
bad = []
for path in conflicts:
    if path.endswith('.json'):
        try:
            json.load(open(path, encoding='utf-8-sig'))
        except Exception as e:
            bad.append((path, str(e)[:60]))
    raw = open(path, 'rb').read()
    if b'<<<<<<<' in raw or b'>>>>>>>' in raw:
        bad.append((path, 'conflict-markers'))
assert not bad, bad
print('ALL PARSE-OK, ZERO MARKERS')
