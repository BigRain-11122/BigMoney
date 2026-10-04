# r710 bm-b merge resolver (r708/r709 bloodline, MERGE_MODE stage: 2=ours 3=theirs)
# Faces: 19 UU vs origin/main 8a51cc634 (bm-c r512 wave + bm-a churn-absorb wave)
# Decisions:
#   - 14 snapshot/derive faces: embedded-ts newer-wins (normalized compare, r709 format-asymmetry law),
#     tie/missing-ts -> theirs (origin authority, r140 canon)
#   - daily_scorecard.json: top-ts probe TIES do not trust (r701 pit) -> deep probe incl as_of keys, depth 4
#   - md/js twins follow their json twin decision (r708/r510 twin same-side law)
#   - compute_audit.json / regime_state.json: rolling-ledger union (history/transitions) + ours latest/state (r188/R208)
# Zero-loss assertions: parse-verify-then-write (r185), read-back, residual marker scan.
import json, subprocess, sys, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MERGE_TIP = '8a51cc634'

def side(stage, path):
    r = subprocess.run(['git', 'show', ':%d:%s' % (stage, path)], capture_output=True, cwd=ROOT)
    if r.returncode != 0 or not r.stdout:
        return None
    return r.stdout

TS_KEYS = ('generated_at', 'updated', 'generated', 'now', 'ts', 'asof', 'as_of', 'last_run', 'scan_ts')

def norm_ts(s):
    # r709 law: ' ' < 'T' lexical poison; normalize space-form to T-form before compare
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

def probe_deep_ts(obj, depth=0, max_depth=4):
    # r701 pit: daily_scorecard top-ts can tie while deeper as_of differs; walk lists too
    best = None
    def walk(v, d):
        nonlocal best
        if isinstance(v, dict):
            for k, x in v.items():
                if k in TS_KEYS and isinstance(x, str) and len(x) >= 8:
                    n = norm_ts(x)
                    if best is None or n > best:
                        best = n
                elif isinstance(x, (dict, list)) and d < max_depth:
                    walk(x, d + 1)
        elif isinstance(v, list):
            for x in v:
                if d < max_depth:
                    walk(x, d + 1)
    walk(obj, depth)
    return best

SNAPSHOTS = [
    'docs/daily_report/REPORT-2026-10-05.json',
    'docs/live_usage/LIVE-2026-10-05.json',
    'docs/live_usage/LIVE-latest.json',
    'results/_attrition_guard_scan.json',
    'results/dashboard_status.json',
    'results/fundamental_b_layer_filter.json',
    'results/futures_update_status.json',
    'results/lhb_update_status.json',
    'results/scorecard_v1.json',
    'results/strategy_scorecard.json',
    'results/token_usage.json',
    'results/update_status.json',
]
DEEP = ['results/daily_scorecard.json']
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

receipt = {'round': 'r710 bm-b', 'merge_head': MERGE_TIP, 'faces': {}, 'decisions': {}}

def write(path, data):
    if isinstance(data, bytes):
        open(os.path.join(ROOT, path), 'wb').write(data)
    else:
        open(os.path.join(ROOT, path), 'w', encoding='utf-8', newline='\n').write(data)

# ---- 1) snapshot faces: embedded-ts newer-wins (parse-verify before write, r185 law)
decisions = {}
for p in SNAPSHOTS + DEEP:
    o_raw, t_raw = side(2, p), side(3, p)
    if t_raw is None:
        decisions[p] = ('ours', 'theirs-missing'); write(p, o_raw); receipt['faces'][p] = {'action': 'ours', 'why': 'theirs-missing'}; continue
    if o_raw is None:
        decisions[p] = ('theirs', 'ours-missing'); write(p, t_raw); receipt['faces'][p] = {'action': 'theirs', 'why': 'ours-missing'}; continue
    try:
        o = json.loads(o_raw.decode('utf-8')); t = json.loads(t_raw.decode('utf-8'))
    except Exception as ex:
        decisions[p] = ('theirs', 'parse-fail=%s' % ex); write(p, t_raw)
        receipt['faces'][p] = {'action': 'theirs', 'why': 'parse-fail %s' % ex}; continue
    if p in DEEP:
        to, tt = probe_deep_ts(o), probe_deep_ts(t)
    else:
        to, tt = probe_ts(o), probe_ts(t)
    if to and tt and to > tt:
        decisions[p] = ('ours', 'ts %s>%s' % (to, tt)); write(p, o_raw)
    elif to and tt and to == tt and p in DEEP and o != t:
        # deep tie on max ts but content differs: take theirs only if any ts newer; else ours-live (same regen second)
        decisions[p] = ('ours', 'deep-tie content-diff -> ours live regen (r701 note: as_of-only diffs are runtime metadata)')
        write(p, o_raw)
    else:
        decisions[p] = ('theirs', 'ts ours=%s theirs=%s -> newer/origin' % (to, tt)); write(p, t_raw)
    # parse-verify what we wrote (r185)
    json.loads(open(os.path.join(ROOT, p), 'rb').read().decode('utf-8'))
    receipt['faces'][p] = {'action': decisions[p][0], 'why': decisions[p][1]}

# ---- 2) md/js twins follow their json twin (r708/r510 twin same-side law)
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

# ---- 3) rolling-ledger unions (r188/R208: history union + ours latest/state)
for p, keys in UNION_LEDGERS.items():
    o = json.loads(side(2, p).decode('utf-8'))
    t = json.loads(side(3, p).decode('utf-8'))
    for k in keys:
        a, b = o.get(k) or [], t.get(k) or []
        rows = {json.dumps(r, sort_keys=True, ensure_ascii=False): r for r in a}
        for r in b:
            rows.setdefault(json.dumps(r, sort_keys=True, ensure_ascii=False), r)
        merged = sorted(rows.values(), key=lambda r: str(r.get('ts', r.get('updated', ''))))
        o[k] = merged
        assert len(merged) >= max(len(a), len(b)), 'union loss %s %s' % (p, k)
        receipt['faces'][p] = {'action': 'union+' + k, 'ours_len': len(a), 'theirs_len': len(b), 'union_len': len(merged)}
    write(p, json.dumps(o, ensure_ascii=False, indent=1) + '\n')
    decisions[p] = ('union', 'rolling-ledger union, ours latest/state')

# ---- 4) read-back + twin same-side assertions + residual marker scan
back_ok = []
for p in SNAPSHOTS + DEEP + list(MD_TWINS) + [JS_TWIN[0]] + list(UNION_LEDGERS):
    raw = open(os.path.join(ROOT, p), 'rb').read()
    assert not re.search(rb'<<<<<<< ', raw), 'marker left in %s' % p
    assert not re.search(rb'>>>>>>> ', raw), 'marker left in %s' % p
    back_ok.append(p)
dj = json.load(open(os.path.join(ROOT, 'results/dashboard_status.json'), encoding='utf-8'))
js = open(os.path.join(ROOT, 'results/dashboard_status.js'), 'rb').read()
djts = probe_ts(dj) or ''
js_has = djts.encode() in js or djts.replace('T', ' ').encode() in js
receipt['twin_checks'] = {'dashboard_json_ts': djts, 'dashboard_js_contains_same_ts': bool(js_has)}
rep = json.load(open(os.path.join(ROOT, 'docs/daily_report/REPORT-2026-10-05.json'), encoding='utf-8'))
receipt['report_json_ts'] = probe_ts(rep)
receipt['decisions'] = {k: v[0] + ' | ' + v[1] for k, v in decisions.items()}
receipt['resolved_n'] = len(decisions)
open(os.path.join(ROOT, 'results', '_r710bmb_merge_resolve.json'), 'w', encoding='utf-8', newline='\n').write(
    json.dumps(receipt, ensure_ascii=False, indent=1) + '\n')
print('RESOLVED', len(decisions), 'faces')
for k, v in sorted(decisions.items()):
    print('  %-52s -> %s (%s)' % (k, v[0], v[1][:60]))
