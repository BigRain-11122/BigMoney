# r711 bm-b merge resolver (r710 bloodline, MERGE_MODE stage: 2=ours 3=theirs)
# Faces: 17 UU vs origin/main 217264532 (bm-c r514 S6 same-family regen wave)
# Decisions:
#   - snapshot/derive faces: embedded-ts newer-wins (r709 format-asymmetry law), tie/missing -> theirs (r140 canon)
#   - token_usage.json: machines per-key max-union (r456/r704 lineage, zero cross-machine count loss)
#     + top-level scalars from newer side
#   - md/js twins follow their json twin (r708/r510 twin same-side law)
#   - compute_audit.json / regime_state.json: rolling-ledger union (history/transitions) + ours latest/state (r188/R208)
# Zero-loss assertions: parse-verify-then-write (r185), read-back marker scan (r506 residual law),
# union length >= max(both) per key.
import json, subprocess, sys, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MERGE_TIP = '217264532'

def side(stage, path):
    r = subprocess.run(['git', 'show', ':%d:%s' % (stage, path)], capture_output=True, cwd=ROOT)
    if r.returncode != 0 or not r.stdout:
        return None
    return r.stdout

TS_KEYS = ('generated_at', 'updated', 'generated', 'now', 'ts', 'asof', 'as_of', 'last_run', 'scan_ts')

def norm_ts(s):
    return s.strip().replace(' ', 'T')

def probe_ts(obj, depth=0, max_depth=2):
    if not isinstance(obj, dict) or depth > max_depth:
        return None
    for k in TS_KEYS:
        v = obj.get(k)
        if isinstance(v, str) and len(v) >= 8:
            return norm_ts(v)
    for v in obj.values():
        if isinstance(v, dict):
            t = probe_ts(v, depth + 1, max_depth)
            if t:
                return t
    return None

SNAPSHOTS = [
    'docs/daily_report/REPORT-2026-10-05.json',
    'docs/live_usage/LIVE-2026-10-05.json',
    'docs/live_usage/LIVE-latest.json',
    'results/dashboard_status.json',
    'results/fundamental_b_layer_filter.json',
    'results/futures_update_status.json',
    'results/lhb_update_status.json',
    'results/scorecard_v1.json',
    'results/strategy_scorecard.json',
    'results/update_status.json',
]
TOKEN = 'results/token_usage.json'
MD_TWINS = {
    'docs/daily_report/REPORT-2026-10-05.md': 'docs/daily_report/REPORT-2026-10-05.json',
    'docs/live_usage/LIVE-2026-10-05.md': 'docs/live_usage/LIVE-2026-10-05.json',
    'docs/live_usage/LIVE-latest.md': 'docs/live_usage/LIVE-latest.json',
}
JS_TWIN = ('results/dashboard_status.js', 'results/dashboard_status.json')
UNION_LEDGERS = {
    'results/compute_audit.json': ['history'],
    'results/regime_state.json': ['history', 'transitions'],
}

receipt = {'round': 'r711 bm-b', 'merge_head': MERGE_TIP, 'faces': {}, 'decisions': {}}

def write(path, data):
    if isinstance(data, bytes):
        open(os.path.join(ROOT, path), 'wb').write(data)
    else:
        open(os.path.join(ROOT, path), 'w', encoding='utf-8', newline='\n').write(data)

decisions = {}

# ---- 1) snapshot faces: embedded-ts newer-wins (parse-verify before write, r185 law)
for p in SNAPSHOTS:
    o_raw, t_raw = side(2, p), side(3, p)
    if t_raw is None and o_raw is None:
        sys.exit('both sides missing for %s (not a UU face?)' % p)
    if t_raw is None:
        decisions[p] = ('ours', 'theirs-missing'); write(p, o_raw); receipt['faces'][p] = {'action': 'ours'}; continue
    if o_raw is None:
        decisions[p] = ('theirs', 'ours-missing'); write(p, t_raw); receipt['faces'][p] = {'action': 'theirs'}; continue
    try:
        o = json.loads(o_raw.decode('utf-8')); t = json.loads(t_raw.decode('utf-8'))
    except Exception as ex:
        decisions[p] = ('theirs', 'parse-fail=%s' % ex); write(p, t_raw)
        receipt['faces'][p] = {'action': 'theirs', 'why': 'parse-fail'}; continue
    to, tt = probe_ts(o), probe_ts(t)
    if to and tt and to > tt:
        decisions[p] = ('ours', 'ts %s>%s' % (to, tt)); write(p, o_raw)
    else:
        decisions[p] = ('theirs', 'ts ours=%s theirs=%s -> newer/origin' % (to, tt)); write(p, t_raw)
    json.loads(open(os.path.join(ROOT, p), 'rb').read().decode('utf-8'))
    receipt['faces'][p] = {'action': decisions[p][0], 'why': decisions[p][1]}

# ---- 2) token_usage: machines per-key max-union (r456 lineage) + newer top-level
p = TOKEN
o_raw, t_raw = side(2, p), side(3, p)
o = json.loads(o_raw.decode('utf-8')); t = json.loads(t_raw.decode('utf-8'))
om, tm = o.get('machines') or {}, t.get('machines') or {}
merged = dict(om)
picked = 0
def tot(v):
    s = 0
    def walk(x):
        nonlocal s
        if isinstance(x, dict):
            for vv in x.values(): walk(vv)
        elif isinstance(x, (int, float)): s += x
    walk(v); return s
for k, tv in tm.items():
    ov = merged.get(k)
    if ov is None:
        merged[k] = tv; picked += 1
    elif tot(tv) > tot(ov):
        merged[k] = tv; picked += 1
if (probe_ts(t) or '') > (probe_ts(o) or ''):
    base = dict(t)
else:
    base = dict(o)
base['machines'] = merged
write(p, json.dumps(base, ensure_ascii=False, indent=1) + '\n')
json.loads(open(os.path.join(ROOT, p), 'rb').read().decode('utf-8'))
decisions[p] = ('per-key-union', 'machines max-union picked_theirs=%d top-side ours=%s theirs=%s' % (
    picked, probe_ts(o), probe_ts(t)))
receipt['faces'][p] = {'action': 'per-key-union', 'ours_keys': sorted(om.keys()), 'theirs_keys': sorted(tm.keys()),
                       'picked_theirs': picked}

# ---- 3) md/js twins follow their json twin (r708/r510 twin same-side law)
for p, twin in MD_TWINS.items():
    s, why = decisions[twin]
    raw = side(2 if s == 'ours' else 3, p)
    write(p, raw)
    decisions[p] = (s, 'md-twin of %s (%s)' % (twin, why))
    receipt['faces'][p] = {'action': s, 'why': decisions[p][1]}
p, twin = JS_TWIN
s, why = decisions[twin]
raw = side(2 if s == 'ours' else 3, p)
write(p, raw)
decisions[p] = (s, 'js-twin of %s (%s)' % (twin, why))
receipt['faces'][p] = {'action': s, 'why': decisions[p][1]}

# ---- 4) rolling-ledger unions (r188/R208: history union + ours latest/state)
for p, keys in UNION_LEDGERS.items():
    o = json.loads(side(2, p).decode('utf-8'))
    t = json.loads(side(3, p).decode('utf-8'))
    for k in keys:
        a, b = o.get(k) or [], t.get(k) or []
        rows = {json.dumps(r, sort_keys=True, ensure_ascii=False): r for r in a}
        for r in b:
            rows.setdefault(json.dumps(r, sort_keys=True, ensure_ascii=False), r)
        merged_rows = sorted(rows.values(), key=lambda r: str(r.get('ts', r.get('updated', ''))))
        o[k] = merged_rows
        assert len(merged_rows) >= max(len(a), len(b)), 'union loss %s %s' % (p, k)
        receipt['faces'][p] = {'action': 'union+' + k, 'ours_len': len(a), 'theirs_len': len(b), 'union_len': len(merged_rows)}
    write(p, json.dumps(o, ensure_ascii=False, indent=1) + '\n')
    decisions[p] = ('union', 'rolling-ledger union, ours latest/state')

# ---- 5) read-back + twin same-side assertion + residual marker scan (r506 law)
for p in SNAPSHOTS + [TOKEN] + list(MD_TWINS) + [JS_TWIN[0]] + list(UNION_LEDGERS):
    raw = open(os.path.join(ROOT, p), 'rb').read()
    assert not re.search(rb'<<<<<<< ', raw), 'marker left in %s' % p
    assert not re.search(rb'>>>>>>> ', raw), 'marker left in %s' % p
dj = json.load(open(os.path.join(ROOT, 'results/dashboard_status.json'), encoding='utf-8'))
js = open(os.path.join(ROOT, 'results/dashboard_status.js'), 'rb').read()
djts = probe_ts(dj) or ''
js_has = djts.encode() in js or djts.replace('T', ' ').encode() in js
receipt['twin_checks'] = {'dashboard_json_ts': djts, 'dashboard_js_contains_same_ts': bool(js_has)}
assert js_has, 'dashboard js/json twin ts mismatch'
receipt['decisions'] = {k: v[0] + ' | ' + v[1] for k, v in decisions.items()}
receipt['resolved_n'] = len(decisions)
open(os.path.join(ROOT, 'results', '_r711bmb_merge_resolve.json'), 'w', encoding='utf-8', newline='\n').write(
    json.dumps(receipt, ensure_ascii=False, indent=1) + '\n')
print('RESOLVED', len(decisions), 'faces')
for k, v in sorted(decisions.items()):
    print('  %-52s -> %s (%s)' % (k, v[0], v[1][:70]))
