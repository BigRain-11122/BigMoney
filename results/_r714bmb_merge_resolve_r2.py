# r714 bm-b merge resolver ROUND-2 (r714 lineage; push-race window vs bm-c r518 S6 wave)
# Faces: 14 UU vs origin/main tip (bm-c r518). Same canon as r714 round-1:
# per-face embedded-ts newer-wins (deep-ts audit fallback), stage sides :2:/:3:,
# stage-blob readback, md twins same-side, rolling-ledger union, token per-key max.
import json, subprocess, sys, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

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
    'results/_attrition_guard_scan.json',
    'results/fundamental_b_layer_filter.json',
    'results/futures_update_status.json',
    'results/lhb_update_status.json',
    'results/update_status.json',
]
TOKEN = 'results/token_usage.json'
MD_TWINS = {
    'docs/daily_report/REPORT-2026-10-05.md': 'docs/daily_report/REPORT-2026-10-05.json',
    'docs/live_usage/LIVE-2026-10-05.md': 'docs/live_usage/LIVE-2026-10-05.json',
    'docs/live_usage/LIVE-latest.md': 'docs/live_usage/LIVE-latest.json',
}
UNION_LEDGERS = {
    'results/compute_audit.json': ['history'],
    'results/regime_state.json': ['history', 'transitions'],
}

receipt = {'round': 'r714 bm-b r2', 'faces': {}, 'decisions': {}}

def write_bytes(path, data):
    open(os.path.join(ROOT, path), 'wb').write(data)

def readback_assert(path, raw):
    rb = open(os.path.join(ROOT, path), 'rb').read()
    assert rb.replace(b'\r\n', b'\n') == raw.replace(b'\r\n', b'\n'), 'readback != stage blob: %s' % path

decisions = {}

for p in SNAPSHOTS:
    o_raw, t_raw = side(2, p), side(3, p)
    if t_raw is None and o_raw is None:
        sys.exit('both sides missing for %s' % p)
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
    if to is None: to = deep_ts(o); mode = 'deep_ts'
    if tt is None: tt = deep_ts(t)
    if to and tt and to > tt:
        decisions[p] = ('ours', '%s %s>%s' % (mode, to, tt)); write_bytes(p, o_raw); readback_assert(p, o_raw)
    else:
        decisions[p] = ('theirs', '%s ours=%s theirs=%s -> newer/origin' % (mode, to, tt))
        write_bytes(p, t_raw); readback_assert(p, t_raw)
    json.loads(open(os.path.join(ROOT, p), 'rb').read().decode('utf-8'))
    receipt['faces'][p] = {'action': decisions[p][0], 'why': decisions[p][1]}

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
base = dict(t) if (probe_ts(t) or '') > (probe_ts(o) or '') else dict(o)
base['machines'] = merged
write_bytes(p, (json.dumps(base, ensure_ascii=False, indent=1) + '\n').encode('utf-8'))
json.loads(open(os.path.join(ROOT, p), 'rb').read().decode('utf-8'))
decisions[p] = ('per-key-union', 'machines max-union picked_theirs=%d' % picked)
receipt['faces'][p] = {'action': 'per-key-union', 'picked_theirs': picked}

for p, twin in MD_TWINS.items():
    s, why = decisions[twin]
    raw = side(2 if s == 'ours' else 3, p)
    write_bytes(p, raw); readback_assert(p, raw)
    decisions[p] = (s, 'md-twin of %s (%s)' % (twin, why))
    receipt['faces'][p] = {'action': s, 'why': decisions[p][1]}

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
    write_bytes(p, (json.dumps(o, ensure_ascii=False, indent=1) + '\n').encode('utf-8'))
    json.loads(open(os.path.join(ROOT, p), 'rb').read().decode('utf-8'))
    decisions[p] = ('union', 'rolling-ledger union, ours latest/state')

ALL = SNAPSHOTS + [TOKEN] + list(MD_TWINS) + list(UNION_LEDGERS)
for p in ALL:
    raw = open(os.path.join(ROOT, p), 'rb').read()
    assert not re.search(rb'(^|\n)<{7} ', raw), 'marker left in %s' % p
    assert not re.search(rb'(^|\n)>{7}( |$)', raw), 'marker left in %s' % p
receipt['decisions'] = {k: v[0] + ' | ' + v[1] for k, v in decisions.items()}
receipt['resolved_n'] = len(decisions)
open(os.path.join(ROOT, 'results', '_r714bmb_merge_resolve_r2.json'), 'w', encoding='utf-8', newline='\n').write(
    json.dumps(receipt, ensure_ascii=False, indent=1) + '\n')
print('RESOLVED', len(decisions), 'faces')
for k, v in sorted(decisions.items()):
    print('  %-48s -> %s (%s)' % (k, v[0], v[1][:76]))
