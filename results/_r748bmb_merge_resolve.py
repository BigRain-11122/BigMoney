# r748 bm-b merge resolver (r746 bloodline verbatim, MERGE_MODE stage: 2=ours 3=theirs)
# r746 round-commit push -> behind-10 merge window, 16 UU product/daemon faces (diff-filter=U authoritative r713 law):
#   8 snapshot json + token + 3 md twins; union ledgers + CODELY block-union legs guarded, skip if not UU.
# Canon: r709/r711 ts-newer-wins (format-normalized, face-level top-key anchor, deep-ts audit fallback),
#        r708 twin same-side (md/js follow json), r729 rolling union ts-newer base, r715/r522 token
#        per-key max-union, r706 lstrip-bullet CODELY block-union + fusion probe, r515 stage-source,
#        r704 readback, r506/r511 residual marker scan (line-anchored).
import json, subprocess, sys, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def git_out(*args):
    return subprocess.run(['git'] + list(args), capture_output=True, cwd=ROOT,
                          creationflags=0x08000000)

MERGE_TIP = git_out('rev-parse', 'MERGE_HEAD').stdout.decode('utf-8').strip()
# r713 law: face list per live diff-filter=U authoritative; non-UU faces skipped (round-2 window reuse)
UU = set(git_out('diff', '--name-only', '--diff-filter=U').stdout.decode('utf-8').split())
if not UU:
    sys.exit('no UU faces (merge already clean?)')

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
            for v in x.values() if isinstance(x, dict) else x: walk(v)
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
CODELY = 'CODELY.md'

receipt = {'round': 'r748 bm-b merge window (r747 dead-tail absorb + behind-10 same-window product race)', 'merge_head': MERGE_TIP,
           'faces': {}, 'decisions': {}}
decisions = {}

def write_bytes(path, data):
    open(os.path.join(ROOT, path), 'wb').write(data)

def readback_assert(path, raw):
    rb = open(os.path.join(ROOT, path), 'rb').read()
    assert rb.replace(b'\r\n', b'\n') == raw.replace(b'\r\n', b'\n'), 'readback != stage blob: %s' % path

# ---- 1) snapshot faces: embedded-ts newer-wins; deep-ts audit fallback (r516-1)
for p in [x for x in SNAPSHOTS if x in UU]:
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
assert p in UU, 'token face expected in UU set'
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

# ---- 3) md/js twins follow their json twin (r708/r510 twin same-side law)
for p, twin in [(k, v) for k, v in MD_TWINS.items() if k in UU]:
    s, why = decisions[twin]
    raw = side(2 if s == 'ours' else 3, p)
    write_bytes(p, raw); readback_assert(p, raw)
    decisions[p] = (s, 'md-twin of %s (%s)' % (twin, why))
    receipt['faces'][p] = {'action': s, 'why': decisions[p][1]}
for p, twin in [t for t in (JS_TWIN,) if t[0] in UU]:
    s, why = decisions[twin]
    raw = side(2 if s == 'ours' else 3, p)
    write_bytes(p, raw); readback_assert(p, raw)
    decisions[p] = (s, 'twin of %s (%s)' % (twin, why))
    receipt['faces'][p] = {'action': s, 'why': decisions[p][1]}

# ---- 4) rolling-ledger unions (r188/R208: history union + ts-newer base, r709/r729 law)
for p, keys in [(k, v) for k, v in UNION_LEDGERS.items() if k in UU]:
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

# ---- 5) CODELY.md per-section block-union (r706 lstrip-bullet law + fusion probe)
p = CODELY
if p in UU:
    o_txt = side(2, p).decode('utf-8')
    t_txt = side(3, p).decode('utf-8')
    def split_sections(txt):
        lines = txt.splitlines()
        pre, secs, cur_title, cur = [], [], None, []
        for l in lines:
            if l.startswith('### '):
                if cur_title is not None:
                    secs.append((cur_title, cur))
                cur_title = l; cur = []
            elif cur_title is None:
                pre.append(l)
            else:
                cur.append(l)
        if cur_title is not None:
            secs.append((cur_title, cur))
        return pre, secs
    def split_entries(lines):
        ents, cur = [], []
        for l in lines:
            if l.lstrip().startswith('- ['):
                if cur:
                    ents.append(cur)
                cur = [l]
            elif cur:
                cur.append(l)
            else:
                cur = ['<PRE>%s' % l]
        if cur:
            ents.append(cur)
        return ents
    def ekey(ent):
        return ent[0].lstrip()
    pre_o, secs_o = split_sections(o_txt)
    pre_t, secs_t = split_sections(t_txt)
    result_secs = []
    codely_receipt = {'ours_sections': [t for t, _ in secs_o], 'theirs_sections': [t for t, _ in secs_t], 'appended': [], 'shared_diff': []}
    for title, tbody in secs_t:
        o_body = None
        for t2, b2 in secs_o:
            if t2 == title:
                o_body = b2; break
        if o_body is None:
            result_secs.append((title, tbody))
            codely_receipt['appended'].append(('theirs-only-section', title))
            continue
        t_ents = split_entries(tbody)
        o_ents = split_entries(o_body)
        t_keys = {}
        for e in t_ents:
            k = ekey(e)
            assert k not in t_keys, 'dup key theirs %s' % k[:60]
            t_keys[k] = e
        out_ents = list(t_ents)
        for e in o_ents:
            k = ekey(e)
            if k.startswith('<PRE>'):
                continue
            if k in t_keys:
                if e != t_keys[k]:
                    keep, drop = (e, t_keys[k]) if len('\n'.join(e)) >= len('\n'.join(t_keys[k])) else (t_keys[k], e)
                    codely_receipt['shared_diff'].append({'key': k[:80], 'kept': 'ours' if keep is e else 'theirs',
                                                          'ours_len': len('\n'.join(e)), 'theirs_len': len('\n'.join(t_keys[k]))})
                    if keep is e:
                        idx = out_ents.index(t_keys[k])
                        out_ents[idx] = e
                continue
            out_ents.append(e)
            codely_receipt['appended'].append(('ours-entry', k[:80]))
        body_lines = []
        for e in out_ents:
            for l in e:
                if l.startswith('<PRE>'):
                    body_lines.append(l[5:])
                else:
                    body_lines.append(l)
        result_secs.append((title, body_lines))
    o_titles = {t for t, _ in secs_o}
    for title, body in secs_o:
        if title not in {t for t, _ in secs_t}:
            result_secs.append((title, body))
            codely_receipt['appended'].append(('ours-only-section', title))
    out_txt = '\n'.join(pre_t if pre_t else pre_o) + '\n'
    for title, body in result_secs:
        out_txt += '\n' + title + '\n'
        if body:
            out_txt += '\n'.join(body) + '\n'
    res_keys = set()
    _, res_secs_final = split_sections(out_txt)
    for title, body in res_secs_final:
        for e in split_entries(body):
            k = ekey(e)
            if not k.startswith('<PRE>'):
                res_keys.add(k)
    for title, body in secs_o:
        for e in split_entries(body):
            k = ekey(e)
            if not k.startswith('<PRE>'):
                assert k in res_keys, 'CODELY zero-loss violated: %s' % k[:60]
    for title, body in secs_t:
        for e in split_entries(body):
            k = ekey(e)
            if not k.startswith('<PRE>'):
                assert k in res_keys, 'CODELY zero-loss violated (theirs): %s' % k[:60]
    write_bytes(p, out_txt.encode('utf-8'))
    decisions[p] = ('block-union', 'per-section union; appended=%d shared_diff=%d' % (
        len(codely_receipt['appended']), len(codely_receipt['shared_diff'])))
    receipt['faces'][p] = {'action': 'block-union', 'codely': codely_receipt}

# ---- 6) read-back marker scan (r506 residual law) + twin coherence
ALL = SNAPSHOTS + [TOKEN] + list(MD_TWINS) + [JS_TWIN[0]] + list(UNION_LEDGERS) + [CODELY]
for p in ALL:
    raw = open(os.path.join(ROOT, p), 'rb').read()
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
open(os.path.join(ROOT, 'results', '_r748bmb_merge_resolve.json'), 'w', encoding='utf-8', newline='\n').write(
    json.dumps(receipt, ensure_ascii=False, indent=1) + '\n')
print('RESOLVED %d faces (MERGE_HEAD=%s)' % (len(decisions), MERGE_TIP[:9]))
for k, v in sorted(decisions.items()):
    print('%-55s %-14s %s' % (k, v[0], v[1][:90]))
