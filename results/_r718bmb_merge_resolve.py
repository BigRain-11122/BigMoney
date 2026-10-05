# r718 bm-b merge resolver (r714 bloodline + r709 pool leg + r717 str-normalize law)
# Faces: 20 UU vs origin/main (bm-a r714 wave: readiness probe + satengine churn + addendum closeout)
# MERGE_MODE stage: 2=ours 3=theirs (r701-3 law)
# Decisions:
#   - snapshot/derive faces: embedded-ts newer-wins (r709 directed format-normalized probe),
#     tie/missing -> theirs (r140 canon); no-ts -> deep recursive ts audit (r516-1 law);
#     sides from index stages (:2:/:3:) per r515 full-side-source law;
#     take-side faces get stage-blob CR-normalized readback assertion (r515/r704 law)
#   - token_usage.json: machines per-key max-union (r456 lineage)
#   - md/js/latest twins follow their json twin (r708/r510 twin same-side law)
#   - compute_audit.json / regime_state.json: rolling-ledger union (r188/R208)
#     with r717 heal: str (double-encoded) entries json.loads-normalized before dedup
#   - runnable_pool.json: per-entry newer-wins on directed owner_since/claimed_at/cleared_ts
#     (r709 directed-comparison law; r704 in-place replace + readback assert)
#   - end-of-run: full marker scan on every resolved face (r717-1 law) + twin coherence
import json, subprocess, sys, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MERGE_TIP = subprocess.run(['git', 'rev-parse', 'MERGE_HEAD'], capture_output=True, text=True, cwd=ROOT).stdout.strip()

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

ISO_RE = re.compile(r'20\d{2}-\d{2}-\d{2}[T ][0-9:.]+[0-9]')

def deep_ts(obj):
    best = None
    def walk(x):
        nonlocal best
        if isinstance(x, dict):
            for v in x.values(): walk(v)
        elif isinstance(x, list):
            for v in x: walk(v)
        elif isinstance(x, str):
            m = ISO_RE.search(x)
            if m:
                t = norm_ts(m.group(0))
                if best is None or t > best:
                    best = t
    walk(obj)
    return best

SNAPSHOTS = [
    'docs/daily_report/REPORT-2026-10-05.json',
    'docs/live_usage/LIVE-2026-10-05.json',
    'docs/live_usage/LIVE-latest.json',
    'results/daily_scorecard.json',
    'results/dashboard_status.json',
    'results/fundamental_b_layer_filter.json',
    'results/futures_update_status.json',
    'results/paper_export/export-2026-09-30.json',
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
EXPORT_TWIN = ('results/paper_export/latest.json', 'results/paper_export/export-2026-09-30.json')
UNION_LEDGERS = {
    'results/compute_audit.json': ['history'],
    'results/regime_state.json': ['history', 'transitions'],
}
POOL = 'results/runnable_pool.json'

receipt = {'round': 'r718 bm-b', 'merge_head': MERGE_TIP, 'faces': {}, 'decisions': {}}

def write_bytes(path, data):
    open(os.path.join(ROOT, path), 'wb').write(data)

def readback_assert(path, raw):
    rb = open(os.path.join(ROOT, path), 'rb').read()
    assert rb.replace(b'\r\n', b'\n') == raw.replace(b'\r\n', b'\n'), 'readback != stage blob: %s' % path

decisions = {}

# ---- 1) snapshot faces: embedded-ts newer-wins; deep-ts audit fallback (r516-1)
for p in SNAPSHOTS:
    o_raw, t_raw = side(2, p), side(3, p)
    if t_raw is None and o_raw is None:
        sys.exit('both sides missing for %s (not a UU face?)' % p)
    if t_raw is None:
        decisions[p] = ('ours', 'theirs-missing'); write_bytes(p, o_raw); readback_assert(p, o_raw)
        receipt['faces'][p] = {'action': 'ours', 'why': 'theirs-missing'}; continue
    if o_raw is None:
        decisions[p] = ('theirs', 'ours-missing'); write_bytes(p, t_raw); readback_assert(p, t_raw)
        receipt['faces'][p] = {'action': 'theirs', 'why': 'ours-missing'}; continue
    try:
        o = json.loads(o_raw.decode('utf-8')); t = json.loads(t_raw.decode('utf-8'))
    except Exception as ex:
        decisions[p] = ('theirs', 'parse-fail=%s' % ex); write_bytes(p, t_raw); readback_assert(p, t_raw)
        receipt['faces'][p] = {'action': 'theirs', 'why': 'parse-fail'}; continue
    to, tt = probe_ts(o), probe_ts(t)
    mode = 'probe_ts'
    if to is None:
        to = deep_ts(o); mode = 'deep_ts'
    if tt is None:
        tt = deep_ts(t)
    if to and tt and to > tt:
        decisions[p] = ('ours', '%s %s>%s' % (mode, to, tt)); write_bytes(p, o_raw); readback_assert(p, o_raw)
    else:
        decisions[p] = ('theirs', '%s ours=%s theirs=%s -> newer/origin' % (mode, to, tt))
        write_bytes(p, t_raw); readback_assert(p, t_raw)
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
write_bytes(p, (json.dumps(base, ensure_ascii=False, indent=1) + '\n').encode('utf-8'))
json.loads(open(os.path.join(ROOT, p), 'rb').read().decode('utf-8'))
decisions[p] = ('per-key-union', 'machines max-union picked_theirs=%d top ours=%s theirs=%s' % (
    picked, probe_ts(o), probe_ts(t)))
receipt['faces'][p] = {'action': 'per-key-union', 'picked_theirs': picked}

# ---- 3) twins follow their json twin (r708/r510 twin same-side law)
for p, twin in MD_TWINS.items():
    s, why = decisions[twin]
    raw = side(2 if s == 'ours' else 3, p)
    write_bytes(p, raw); readback_assert(p, raw)
    decisions[p] = (s, 'md-twin of %s (%s)' % (twin, why))
    receipt['faces'][p] = {'action': s, 'why': decisions[p][1]}
for p, twin in (JS_TWIN, EXPORT_TWIN):
    s, why = decisions[twin]
    raw = side(2 if s == 'ours' else 3, p)
    write_bytes(p, raw); readback_assert(p, raw)
    decisions[p] = (s, 'twin of %s (%s)' % (twin, why))
    receipt['faces'][p] = {'action': s, 'why': decisions[p][1]}

# ---- 4) rolling-ledger unions (r188/R208 + r717 str-normalize heal law)
def norm_entry(e):
    """r717 heal: cross-machine drift once delivered double-encoded (str) entries."""
    if isinstance(e, str):
        try:
            return json.loads(e)
        except Exception:
            return None
    return e

for p, keys in UNION_LEDGERS.items():
    o = json.loads(side(2, p).decode('utf-8'))
    t = json.loads(side(3, p).decode('utf-8'))
    # base = side with newer top-level ts (latest/state keep-position, r711 lineage + take-new)
    if (probe_ts(t) or deep_ts(t) or '') > (probe_ts(o) or deep_ts(o) or ''):
        o, t = t, o
        base_side = 'theirs'
    else:
        base_side = 'ours'
    for k in keys:
        a = [x for x in (norm_entry(e) for e in (o.get(k) or [])) if isinstance(x, dict)]
        b = [x for x in (norm_entry(e) for e in (t.get(k) or [])) if isinstance(x, dict)]
        dropped_o = len(o.get(k) or []) - len(a)
        dropped_t = len(t.get(k) or []) - len(b)
        rows = {json.dumps(r, sort_keys=True, ensure_ascii=False): r for r in a}
        for r in b:
            rows.setdefault(json.dumps(r, sort_keys=True, ensure_ascii=False), r)
        merged_rows = sorted(rows.values(), key=lambda r: str(r.get('ts', r.get('updated', ''))))
        o[k] = merged_rows
        assert len(merged_rows) >= max(len(a), len(b)), 'union loss %s %s' % (p, k)
        assert all(isinstance(x, dict) for x in merged_rows), 'non-dict entry survived union %s' % p
        receipt['faces'][p] = {'action': 'union+' + k, 'ours_len': len(a), 'theirs_len': len(b),
                               'union_len': len(merged_rows), 'base_side': base_side,
                               'norm_dropped': {'ours': dropped_o, 'theirs': dropped_t}}
    write_bytes(p, (json.dumps(o, ensure_ascii=False, indent=1) + '\n').encode('utf-8'))
    json.loads(open(os.path.join(ROOT, p), 'rb').read().decode('utf-8'))
    decisions[p] = ('union', 'rolling-ledger union base=%s, all-dicts (r717 heal)' % base_side)

# ---- 5) runnable_pool per-entry newer-wins (r709 directed owner_since law + r704 readback)
p = POOL
o = json.loads(side(2, p).decode('utf-8'))
t = json.loads(side(3, p).decode('utf-8'))
oe = {e['id']: e for e in o['entries']}
te = {e['id']: e for e in t['entries']}
assert set(oe) == set(te), 'entry id sets diverge: only-ours=%s only-theirs=%s' % (
    sorted(set(oe) - set(te)), sorted(set(te) - set(oe)))
diff_ids = [i for i in oe if oe[i] != te[i]]

def shards_owner_max(e):
    """r709 law: compare ONLY owner_since/claimed_at/cleared_ts fields (space format)."""
    best = ''
    def walk(v):
        nonlocal best
        if isinstance(v, dict):
            for k, x in v.items():
                if k in ('owner_since', 'claimed_at', 'cleared_ts') and isinstance(x, str) and x > best:
                    best = x
                elif isinstance(x, (dict, list)):
                    walk(x)
        elif isinstance(v, list):
            for x in v:
                walk(x)
    walk(e)
    return best

decided = {}
for i in diff_ids:
    ots, tts = shards_owner_max(oe[i]), shards_owner_max(te[i])
    if ots > tts:
        o['entries'][[k for k, e in enumerate(o['entries']) if e['id'] == i][0]] = oe[i]
        decided[i] = 'ours(owner_since %s>%s)' % (ots, tts)
    elif tts > ots:
        o['entries'][[k for k, e in enumerate(o['entries']) if e['id'] == i][0]] = te[i]
        decided[i] = 'theirs(owner_since %s>%s)' % (tts, ots)
    else:
        decided[i] = 'tie-keep-ours(%s)' % ots
write_bytes(p, (json.dumps(o, ensure_ascii=False, indent=1) + '\n').encode('utf-8'))
back = json.load(open(os.path.join(ROOT, p), encoding='utf-8'))
be = {e['id']: e for e in back['entries']}
assert len(be) == len(oe), 'entry count changed'
for i, d in decided.items():
    if d.startswith('theirs'):
        assert be[i] == te[i], 'read-back mismatch %s' % i
    elif d.startswith('ours'):
        assert be[i] == oe[i], 'read-back mismatch (ours) %s' % i
receipt['faces'][p] = {'action': 'per-entry newer-wins', 'diff_ids': {k: v for k, v in decided.items()},
                       'entry_count': len(be)}
decisions[p] = ('per-entry-newer-wins', 'diff=%d decided; directed owner_since compare' % len(decided))

# ---- 6) read-back marker scan on ALL resolved faces (r717-1 law) + twin coherence
ALL = SNAPSHOTS + [TOKEN] + list(MD_TWINS) + [JS_TWIN[0], EXPORT_TWIN[0]] + list(UNION_LEDGERS) + [POOL]
for p in ALL:
    raw = open(os.path.join(ROOT, p), 'rb').read()
    # r506 law: line-start anchored markers only (entries legally quote markers mid-line)
    assert not re.search(rb'(^|\n)<{7} ', raw), 'marker left in %s' % p
    assert not re.search(rb'(^|\n)>{7}( |$)', raw), 'marker left in %s' % p
dj = json.load(open(os.path.join(ROOT, 'results/dashboard_status.json'), encoding='utf-8'))
js = open(os.path.join(ROOT, 'results/dashboard_status.js'), 'rb').read()
djts = probe_ts(dj) or ''
js_has = djts.encode() in js or djts.replace('T', ' ').encode() in js
receipt['twin_checks'] = {'dashboard_json_ts': djts, 'dashboard_js_contains_same_ts': bool(js_has)}
assert js_has, 'dashboard js/json twin ts mismatch'
receipt['decisions'] = {k: v[0] + ' | ' + v[1] for k, v in decisions.items()}
receipt['resolved_n'] = len(decisions)
open(os.path.join(ROOT, 'results', '_r718bmb_merge_resolve.json'), 'w', encoding='utf-8', newline='\n').write(
    json.dumps(receipt, ensure_ascii=False, indent=1) + '\n')
print('RESOLVED', len(decisions), 'faces; pool decided:', json.dumps(decided, ensure_ascii=False))
for k, v in sorted(decisions.items()):
    print('  %-52s -> %s (%s)' % (k, v[0], v[1][:90]))
