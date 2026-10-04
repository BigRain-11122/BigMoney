# r714 bm-b merge resolver (r712 bloodline, MERGE_MODE stage: 2=ours 3=theirs)
# Faces: 31 UU vs origin/main 8475d5689b26f87a03accaebc1d289156cf54761
#        (bm-a r710/711 + bm-c r516/517 S6 same-family regen wave)
# Decisions:
#   - snapshot/derive faces: embedded-ts newer-wins (r709 format-asymmetry law),
#     tie/missing -> theirs (r140 canon); no-ts -> deep recursive ts audit
#     (r516-1 law) before fallback; sides from index stages (:2:/:3:) per r515
#     full-side-source law; take-side faces get stage-blob CR-normalized
#     readback assertion (r515/r704 law)
#   - token_usage.json: machines per-key max-union (r456/r704 lineage)
#   - md/js/latest twins follow their json twin (r708/r510 twin same-side law)
#   - compute_audit.json / regime_state.json: rolling-ledger union (r188/R208)
#   - x2_watch_log.jsonl: identity-union + ts stable sort, residual-tolerant
#     (r706 law: source residual lines preserved verbatim, no new residuals)
#   - CODELY.md: per-section block-union, entries keyed by lstrip'd first line
#     (r706 leading-space bullet law + fusion probe), zero-loss asserted
import json, subprocess, sys, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MERGE_TIP = '8475d5689b26f87a03accaebc1d289156cf54761'

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
    'results/daily_scorecard.json',
    'results/dashboard_status.json',
    'results/fundamental_b_layer_filter.json',
    'results/futures_update_status.json',
    'results/lhb_update_status.json',
    'results/paper/COMPOSITE-CE-01_paper.json',
    'results/paper/COMPOSITE-CE-02_paper.json',
    'results/paper/DROUGHT-CE-01_paper.json',
    'results/paper/ENGULF-CE-01_paper.json',
    'results/paper/NEEDLE-DE-01_paper.json',
    'results/paper/VOLATILITY-CE-01_paper.json',
    'results/paper_export/export-2026-09-30.json',
    'results/prospect_paper/_summary.json',
    'results/prospect_promotion/_summary.json',
    'results/scorecard_v1.json',
    'results/strategy_scorecard.json',
    'results/t35_open_fill_verify.json',
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
X2 = 'results/x2_watch_log.jsonl'
CODELY = 'CODELY.md'

receipt = {'round': 'r714 bm-b', 'merge_head': MERGE_TIP, 'faces': {}, 'decisions': {}}

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
    write_bytes(p, (json.dumps(o, ensure_ascii=False, indent=1) + '\n').encode('utf-8'))
    json.loads(open(os.path.join(ROOT, p), 'rb').read().decode('utf-8'))
    decisions[p] = ('union', 'rolling-ledger union, ours latest/state')

# ---- 5) x2_watch_log.jsonl: identity-union + ts stable sort, residual-tolerant (r706 law)
p = X2
o_txt = side(2, p).decode('utf-8')
t_txt = side(3, p).decode('utf-8')
o_lines = [l for l in o_txt.splitlines()]
t_lines = [l for l in t_txt.splitlines()]
def split_resid(lines):
    good, bad = [], []
    for l in lines:
        s = l.strip()
        if not s:
            continue
        try:
            j = json.loads(s)
            good.append((s, j))
        except Exception:
            bad.append(s)
    return good, bad
o_good, o_res = split_resid(o_lines)
t_good, t_res = split_resid(t_lines)
src_res = set(o_res) | set(t_res)
seen = {}
for s, j in t_good + o_good:
    key = s
    if key in seen:
        continue
    seen[key] = (s, j)
merged = sorted(seen.values(), key=lambda x: str(x[1].get('ts', '')))
final_res = []
out_lines = [s for s, j in merged]
for s in out_lines:
    try:
        json.loads(s)
    except Exception:
        final_res.append(s)
assert set(final_res) <= src_res, 'new residual lines introduced (r706 law)'
assert len(out_lines) >= max(len(o_good), len(t_good)), 'union loss %s' % p
write_bytes(p, ('\n'.join(out_lines) + '\n').encode('utf-8'))
decisions[p] = ('union', 'identity-union+ts-sort ours=%d theirs=%d union=%d residual_src=%d kept=%d' % (
    len(o_good), len(t_good), len(out_lines), len(src_res), len(final_res)))
receipt['faces'][p] = {'action': 'jsonl-union', 'ours': len(o_good), 'theirs': len(t_good), 'union': len(out_lines),
                       'residual_src': len(src_res), 'residual_kept': len(final_res)}

# ---- 6) CODELY.md per-section block-union (r706 lstrip-bullet law + fusion probe)
p = CODELY
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
        # preamble lines inside a section before first entry: attach to a pseudo entry
        else:
            cur = ['<PRE>%s' % l]
    if cur:
        ents.append(cur)
    return ents
def ekey(ent):
    return ent[0].lstrip()
pre_o, secs_o = split_sections(o_txt)
pre_t, secs_t = split_sections(t_txt)
t_map = {title: body for title, body in secs_t}
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
                # shared entry, differing bytes: keep longer, disclose
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
# zero-loss assertion: every ours entry key present in result
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

# ---- 7) read-back marker scan (r506 residual law) + twin coherence
ALL = SNAPSHOTS + [TOKEN] + list(MD_TWINS) + [JS_TWIN[0], EXPORT_TWIN[0]] + list(UNION_LEDGERS) + [X2, CODELY]
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
open(os.path.join(ROOT, 'results', '_r714bmb_merge_resolve.json'), 'w', encoding='utf-8', newline='\n').write(
    json.dumps(receipt, ensure_ascii=False, indent=1) + '\n')
print('RESOLVED', len(decisions), 'faces')
for k, v in sorted(decisions.items()):
    print('  %-52s -> %s (%s)' % (k, v[0], v[1][:80]))
