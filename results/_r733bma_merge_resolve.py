# r733 bm-a merge resolver HOP-2 (vs bm-c r554 wave, MERGE_MODE stage: 2=ours 3=theirs)
# 18 UU faces = 11 snapshot json + 3 md twins + 1 js twin + 2 rolling ledgers + token.
# Bloodline: r734 bm-b _r734bmb_merge_resolve_w2.py verbatim + face-list extension
#            (dashboard_status twins + gate status faces + scorecard twins); face list = diff-filter=U authoritative (r713 law).
# Canon: r709/r711 ts-newer-wins, r708 twin same-side (md+js), r729 rolling union,
#        r715/r522 token per-key max-union, r515 stage-source, r704 readback, r706 marker scan.
import json, subprocess, sys, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def git_out(*args):
    return subprocess.run(['git'] + list(args), capture_output=True, cwd=ROOT,
                          creationflags=0x08000000)

MERGE_TIP = git_out('rev-parse', 'MERGE_HEAD').stdout.decode('utf-8').strip()

def side(stage, path):
    r = git_out('show', ':%d:%s' % (stage, path))
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
    'results/dashboard_status.json',
    'results/futures_update_status.json',
    'results/lhb_update_status.json',
    'results/update_status.json',
    'results/fundamental_b_layer_filter.json',
    'results/scorecard_v1.json',
    'results/strategy_scorecard.json',
]
TOKEN = 'results/token_usage.json'
MD_TWINS = {
    'docs/daily_report/REPORT-2026-10-05.md': 'docs/daily_report/REPORT-2026-10-05.json',
    'docs/live_usage/LIVE-2026-10-05.md': 'docs/live_usage/LIVE-2026-10-05.json',
    'docs/live_usage/LIVE-latest.md': 'docs/live_usage/LIVE-latest.json',
}
JS_TWINS = {
    'results/dashboard_status.js': 'results/dashboard_status.json',
}
UNION_LEDGERS = {
    'results/compute_audit.json': ['history'],
    'results/regime_state.json': ['history', 'transitions'],
}

receipt = {'round': 'r733 bm-a S0 merge hop-2', 'merge_head': MERGE_TIP,
           'faces': {}, 'decisions': {}}
decisions = {}

def write_bytes(path, data):
    open(os.path.join(ROOT, path), 'wb').write(data)

def readback_assert(path, raw):
    rb = open(os.path.join(ROOT, path), 'rb').read()
    assert rb.replace(b'\r\n', b'\n') == raw.replace(b'\r\n', b'\n'), 'readback != stage blob: %s' % path

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

# ---- 3) md+js twins follow their json twin (r708/r510 twin same-side law)
for p, twin in dict(MD_TWINS, **JS_TWINS).items():
    s, why = decisions[twin]
    raw = side(2 if s == 'ours' else 3, p)
    write_bytes(p, raw); readback_assert(p, raw)
    decisions[p] = (s, 'twin of %s (%s)' % (twin, why))
    receipt['faces'][p] = {'action': s, 'why': decisions[p][1]}

# ---- 4) rolling-ledger unions (r188/R208: history union + ts-newer base, r709/r729 law)
for p, keys in UNION_LEDGERS.items():
    o = json.loads(side(2, p).decode('utf-8'))
    t = json.loads(side(3, p).decode('utf-8'))
    oo, tt = probe_ts(o), probe_ts(t)
    if oo is None: oo = deep_ts(o)
    if tt is None: tt = deep_ts(t)
    base, base_side = (o, 'ours') if (oo and tt and oo > tt) else (t, 'theirs')
    for k in keys:
        a, b = o.get(k) or [], t.get(k) or []
        rows = {json.dumps(r, sort_keys=True, ensure_ascii=False): r for r in a}
        for r in b:
            rows.setdefault(json.dumps(r, sort_keys=True, ensure_ascii=False), r)
        merged_rows = sorted(rows.values(), key=lambda r: str(r.get('ts', r.get('updated', ''))))
        base[k] = merged_rows
        assert len(merged_rows) >= max(len(a), len(b)), 'union loss %s %s' % (p, k)
        assert all(isinstance(r, dict) for r in merged_rows), 'union row not dict %s %s (r522 law)' % (p, k)
        receipt['faces'][p] = {'action': 'union+' + k, 'base': base_side, 'ours_len': len(a), 'theirs_len': len(b), 'union_len': len(merged_rows)}
    write_bytes(p, (json.dumps(base, ensure_ascii=False, indent=1) + '\n').encode('utf-8'))
    json.loads(open(os.path.join(ROOT, p), 'rb').read().decode('utf-8'))
    decisions[p] = ('union', 'rolling-ledger union, base=%s (ours=%s theirs=%s)' % (base_side, oo, tt))

# ---- 5) read-back marker scan (r506 residual law, line-anchored)
ALL = SNAPSHOTS + [TOKEN] + list(MD_TWINS) + list(JS_TWINS) + list(UNION_LEDGERS)
for p in ALL:
    raw = open(os.path.join(ROOT, p), 'rb').read()
    assert not re.search(rb'(^|\n)<{7} ', raw), 'marker left in %s' % p
    assert not re.search(rb'(^|\n)>{7}( |$)', raw), 'marker left in %s' % p
receipt['decisions'] = {k: v[0] + ' | ' + v[1] for k, v in decisions.items()}
receipt['resolved_n'] = len(decisions)
open(os.path.join(ROOT, 'results', '_r733bma_merge_resolve_hop2.json'), 'w', encoding='utf-8', newline='\n').write(
    json.dumps(receipt, ensure_ascii=False, indent=1) + '\n')
print('RESOLVED %d faces (MERGE_HEAD=%s)' % (len(decisions), MERGE_TIP[:9]))
for k, v in sorted(decisions.items()):
    print('%-55s %-14s %s' % (k, v[0], v[1][:90]))
