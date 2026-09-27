# r335 bm-a rebase push-collision resolver (28-UU batch vs bm-b r332 window {564e5594,6ff89ddd,538cf74e} same-window S6 double-run, R322 family)
# Canon: bigmoney-conflict-resolve SKILL.md 形态表 + 解后纪律 §三. Lineage: _r334bma_resolve.py 27-face set + NEW CODELY.md memory-union face.
# r331 intersection audit (done pre-resolver, ground truth): inter(29) == UU(28) + MSG-1552-processed (both sides made IDENTICAL move, bm-b consumed+archived per their r332 msg -- zero action).
# Stage semantics DURING REBASE (r85 law): stage2 = origin side (bm-b), stage3 = replayed commit (bm-a r335). VERIFIED by probes below (fail-closed).
# Recipes: CODELY.md=memory-union (merge-base byte-prefix assertion both sides -> base+A-suffix+B-suffix direct concat, r208/r212; fallback=entry-level dual-coverage, raise for manual if prefix fails, r327/r329);
#           compute_audit=rolling-ledger (ts,machine) union (r85 window law, collision content-identity assert);
#           regime_state=rolling-ledger asof-union + state take-new by 'updated';
#           x2_watch=append-log line-union; 24x snapshot/measurement faces=take-side WHOLE BYTES by producer-path ts probe,
#           FUTURE-SENTINEL blanket fallback (ts>now excluded -- r334 probe-poisoning law: blanket max-ts was poisoned by next-fire 2026-09-28 09:15);
#           daily_report md twin = same-side blob byte-copy (twin-side coupling r329, md is NOT JSON); dashboard js+json pair-law same side.
# EOL/indent: take-side whole-blob bytes preserve producer format exactly; union faces mirror base blob :1: (r223/r234/r329-p3).
# autofill_state.json (auto-merged by git, NOT in UU): canon verification vs both parents (launches composite-key union zero-dup + last_tick take-later-ts dict + asc re-sort r245) -- zero-fix if already canon.
# Fail-closed: any assertion failure raises BEFORE any write (zero wrong-side writes).
import subprocess, json, re

NOW = '2026-09-27 23:59'  # future sentinel: any ts beyond this is a PLAN-face field, excluded from take-side comparison (r334 law)

def _norm_ts(t):
    # ISO-T form sorts after space-form ('T' 0x54 > ' ' 0x20) -- normalize pos-10 separator to space BEFORE comparing (r335 live catch)
    return t[:10] + ' ' + t[11:] if len(t) > 10 and t[10] == 'T' else t

def blob(stage, path):
    r = subprocess.run(['git', 'show', f':{stage}:{path}'], capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(f'git show :{stage}:{path} failed')
    return r.stdout

def parse(b, path):
    return json.loads(b.decode('utf-8'))

def base_eol_indent(path):
    b = blob(1, path)
    eol = '\r\n' if b'\r\n' in b else '\n'
    indent = 1
    for line in b.decode('utf-8', errors='replace').split(eol):
        if line.startswith(' '):
            indent = len(line) - len(line.lstrip(' '))
            break
    return eol, indent

def dump(obj, eol, indent):
    return (json.dumps(obj, ensure_ascii=False, indent=indent) + '\n').replace('\n', eol).encode('utf-8')

TSRE = re.compile(r'2026-09-2[0-9][ T][0-9:.]+')
def maxts(b):
    m = [t for t in TSRE.findall(b.decode('utf-8', errors='replace')) if _norm_ts(t) <= NOW]  # future sentinel (r334 law), T-form normalized (r335)
    return max(m) if m else None

def deep_ts(obj, *paths):
    # producer-known probe paths first (r319 existence-first); returns first found
    for pth in paths:
        cur = obj
        ok = True
        for k in pth:
            if isinstance(cur, dict) and k in cur:
                cur = cur[k]
            else:
                ok = False
                break
        if ok and isinstance(cur, str) and TSRE.search(cur):
            m = [t for t in TSRE.findall(cur) if _norm_ts(t) <= NOW]
            if m:
                return max(m)
    return None

RES = {}
REPORT = []

def resolve_codely():
    p = 'CODELY.md'
    base, orig, mine = blob(1, p), blob(2, p), blob(3, p)
    if not (orig.startswith(base) and mine.startswith(base)):
        raise RuntimeError('CODELY.md memory-union: merge-base prefix assertion FAILED on at least one side '
                           '(in-place edit suspected) -- r327/r329 entry-level dual-coverage required, MANUAL face, aborting writes')
    sa, sb = orig[len(base):], mine[len(base):]
    result = base + sa + sb
    assert len(result) == len(base) + len(sa) + len(sb), 'byte account mismatch'
    # both suffixes must be non-empty pure appends (this window: bm-b pitlaw entry + bm-a pitlaw entry)
    assert sa.strip() and sb.strip(), 'empty suffix on a memory-union face -- unexpected, escalate'
    RES[p] = result
    REPORT.append(f'CODELY.md: memory-union direct-concat base={len(base)}B + bm-b suffix={len(sa)}B + bm-a suffix={len(sb)}B -> {len(result)}B (zero-loss byte account)')

def resolve_compute_audit():
    p = 'results/compute_audit.json'
    eol, ind = base_eol_indent(p)
    a, b = parse(blob(2, p), p), parse(blob(3, p), p)
    # stage-semantics probe (r85 law): bm-a r335 chain ran 16:10:28 -- stage3 must contain it
    s3_ts = {e.get('ts') for e in b['history']}
    assert '2026-09-27 16:10:28' in s3_ts or any(e.get('machine') == 'bm-a' and e.get('ts', '') >= '2026-09-27 16:10' for e in b['history']), \
        'stage3 does not look like bm-a r335 side (no 16:10 bm-a audit row) -- stage semantics suspect, escalate'
    ha, hb = a['history'], b['history']
    def key(e): return (e.get('ts'), e.get('machine'))
    seen, merged = {}, []
    for e in ha + hb:
        k = key(e)
        if k in seen:
            if seen[k] != e:
                raise RuntimeError(f'compute_audit history key {k} content-divergent -- escalate')
            continue
        seen[k] = e
        merged.append(e)
    merged.sort(key=lambda e: (e.get('ts', ''), e.get('machine', '')))
    n_union = len({key(e) for e in ha} | {key(e) for e in hb})
    assert len(merged) == n_union, 'history union count != key-union count'
    la, lb = a['latest'], b['latest']
    ta, tb = la.get('ts'), lb.get('ts')
    latest = la if (ta is not None and (tb is None or ta >= tb)) else lb
    if ta == tb:
        latest = la  # tie -> HEAD (r140)
    out = {'latest': latest, 'history': merged}
    RES[p] = dump(out, eol, ind)
    REPORT.append(f'compute_audit: history {len(ha)}|{len(hb)} -> {len(merged)} (ts,machine)-union collisions-content-checked, latest ts={latest.get("ts")} (origin={ta} mine={tb})')

def resolve_regime():
    p = 'results/regime_state.json'
    eol, ind = base_eol_indent(p)
    a, b = parse(blob(2, p), p), parse(blob(3, p), p)
    def union_list(la, lb, kfields, tag):
        seen, merged = {}, []
        for e in la + lb:
            k = tuple(e.get(f) for f in kfields) if kfields else json.dumps(e, sort_keys=True, ensure_ascii=False)
            if k in seen:
                if seen[k] != e:
                    raise RuntimeError(f'regime {tag} key {k} divergent -- escalate')
                continue
            seen[k] = e
            merged.append(e)
        return merged
    hist = union_list(a.get('history', []), b.get('history', []), ('asof',), 'history')
    tr = union_list(a.get('transitions', []), b.get('transitions', []), ('asof',), 'transitions')
    out = dict(a)
    out['history'] = hist
    out['transitions'] = tr
    ta, tb = a.get('updated'), b.get('updated')
    src = a if (ta is not None and (tb is None or ta >= tb)) else b
    if ta == tb:
        src = a
    for f in ('asof', 'updated', 'mode', 'state', 'state_cn', 'raw_level', 'green_streak', 'days_in_state', 'dims', 'rule', 'triggers', 'thresholds_fp'):
        if f in src:
            out[f] = src[f]
    RES[p] = dump(out, eol, ind)
    REPORT.append(f'regime_state: history {len(a.get("history",[]))}|{len(b.get("history",[]))} -> {len(hist)} asof-union, transitions -> {len(tr)}, state from updated={src.get("updated")}')

def resolve_x2():
    p = 'results/x2_watch_log.jsonl'
    ba, bb = blob(2, p), blob(3, p)
    eol = '\r\n' if b'\r\n' in blob(1, p) else '\n'
    la = [l for l in ba.decode('utf-8', errors='replace').splitlines() if l.strip()]
    lb = [l for l in bb.decode('utf-8', errors='replace').splitlines() if l.strip()]
    seen, merged = set(), []
    for l in la + lb:
        if l in seen:
            continue
        seen.add(l)
        merged.append(l)
    union_n = len(set(la) | set(lb))
    assert len(merged) == union_n, 'x2 line union count mismatch'
    RES[p] = (eol.join(merged) + eol).encode('utf-8')
    REPORT.append(f'x2_watch_log: {len(la)}|{len(lb)} -> {len(merged)} line-union')

# take-side whole-bytes faces: (path, producer-probe-paths or None for future-filtered blanket) -- md/js are NOT json.loads'd (r329/R209 laws)
TAKE_SIDES = [
    ('docs/daily_report/REPORT-2026-09-27.json', (('generated_at',), ('meta', 'generated_at'), ('ts',))),  # TRUE index path is DASHED (ls-files byte-exact repr; resolver v1 used compact form -> git show :2: refused)
    ('docs/daily_report/REPORT-2026-09-27.md', None),          # twin md face: same-side blob byte-copy (coupled)
    ('results/daily_scorecard.json', (('generated',), ('generated_at',), ('ts',))),
    ('results/dashboard_status.js', None),                     # js-wrapper whole bytes, pair-law same side as .json
    ('results/dashboard_status.json', (('meta', 'generated_at'), ('generated_at',), ('ts',))),  # r334: meta.generated_at authoritative
    ('results/fundamental_b_layer_filter.json', (('generated_at',), ('ts',), ('asof',))),
    ('results/futures_update_status.json', (('ts',), ('cutoff',), ('updated',))),
    ('results/heat_update_status.json', (('ts',), ('cutoff',), ('updated',))),
    ('results/lhb_update_status.json', (('ts',), ('cutoff',), ('updated',))),
    ('results/paper/COMPOSITE-CE-01_paper.json', (('asof',), ('updated',), ('ts',))),
    ('results/paper/COMPOSITE-CE-02_paper.json', (('asof',), ('updated',), ('ts',))),
    ('results/paper/DROUGHT-CE-01_paper.json', (('asof',), ('updated',), ('ts',))),
    ('results/paper/ENGULF-CE-01_paper.json', (('asof',), ('updated',), ('ts',))),
    ('results/paper/NEEDLE-DE-01_paper.json', (('asof',), ('updated',), ('ts',))),
    ('results/paper/VOLATILITY-CE-01_paper.json', (('asof',), ('updated',), ('ts',))),
    ('results/paper_export/export-2026-09-24.json', (('export_date',), ('ts',), ('asof',))),
    ('results/paper_export/latest.json', (('export_date',), ('ts',), ('asof',))),
    ('results/prospect_paper/_summary.json', (('asof',), ('updated',), ('ts',))),
    ('results/prospect_promotion/_summary.json', (('asof',), ('evaluated_at',), ('ts',))),
    ('results/scorecard_v1.json', (('generated',), ('generated_at',), ('ts',))),
    ('results/strategy_scorecard.json', (('generated',), ('generated_at',), ('ts',))),
    ('results/t35_open_fill_verify.json', (('day',), ('ts',), ('generated',))),
    ('results/token_usage.json', (('ts',), ('updated',), ('generated',))),
    ('results/update_status.json', (('ts',), ('updated',), ('cutoff',))),
]

def side_ts(path, bobj, braw, probes):
    if probes:
        t = deep_ts(bobj, *probes)
        if t is not None:
            return t, 'producer-path'
    t = maxts(braw)
    return t, 'blanket+future-sentinel'

def resolve_take_sides():
    for p, probes in TAKE_SIDES:
        bo, bm = blob(2, p), blob(3, p)
        if p.endswith('.json'):
            ao, am = parse(bo, p), parse(bm, p)  # both sides valid JSON (r185 pre-write verify)
        else:
            ao = am = None
        to, mo = side_ts(p, ao, bo, probes)
        tm, mm = side_ts(p, am, bm, probes)
        assert to is not None or tm is not None, f'{p}: no admissible ts either side (r319 existence-first fail)'
        if tm is not None and (to is None or tm > to):
            side, ts = 'stage3(mine)', tm
            RES[p] = bm
        elif to is not None and (tm is None or to > tm):
            side, ts = 'stage2(origin)', to
            RES[p] = bo
        else:
            side, ts = 'stage2(origin) tie', to  # r140 tie -> HEAD/origin
            RES[p] = bo
        REPORT.append(f'{p}: take-side {side} ts={ts} probe={mo if mo != "producer-path" else mm}')

def verify_autofill_automerge():
    # autofill_state.json auto-merged by git (M staged, not UU). Canon per r322/r245: launches composite-key union
    # zero-dup + collision content-identity; last_tick = later-ts whole dict; asc sort. Zero-fix if staged blob == canon.
    p = 'results/autofill_state.json'
    staged = parse(subprocess.run(['git', 'show', ':0:results/autofill_state.json'], capture_output=True).stdout, p)
    a = parse(subprocess.run(['git', 'show', '538cf74e:results/autofill_state.json'], capture_output=True).stdout, p)
    b = parse(subprocess.run(['git', 'show', '2aa06fe9:results/autofill_state.json'], capture_output=True).stdout, p)
    KF = ('ts', 'machine', 'pid', 'runner_sha256', 'entry', 'shard')
    def canon(av, bv):
        la, lb = av.get('launches', []), bv.get('launches', [])
        seen, merged = {}, []
        for e in la + lb:
            k = tuple(e.get(f) for f in KF)
            if k in seen:
                if seen[k] != e:
                    raise RuntimeError(f'autofill launches key {k} content-divergent -- escalate')
                continue
            seen[k] = e
            merged.append(e)
        merged.sort(key=lambda e: e.get('ts', ''))
        out = dict(av)
        out['launches'] = merged
        lta, ltb = av.get('last_tick', {}), bv.get('last_tick', {})
        out['last_tick'] = lta if str(lta.get('ts', '')) >= str(ltb.get('ts', '')) else ltb
        return out
    c = canon(a, b)
    def norm(o):
        return json.dumps(o, sort_keys=True, ensure_ascii=False)
    if norm(staged) == norm(c):
        REPORT.append(f'autofill_state: git automerge == canon (launches key-union {len(c.get("launches", []))}, last_tick ts={c.get("last_tick", {}).get("ts")}) -- ZERO-FIX (r334 precedent)')
        return
    # automerge deviates from canon: rewrite canon (mirror base EOL/indent)
    eol, ind = base_eol_indent(p)
    RES[p] = dump(c, eol, ind)
    REPORT.append(f'autofill_state: automerge DEVIATED from canon -- canon rewritten (launches {len(c.get("launches", []))} key-union, last_tick ts={c.get("last_tick", {}).get("ts")})')

def main():
    resolve_codely()
    resolve_compute_audit()
    resolve_regime()
    resolve_x2()
    resolve_take_sides()
    verify_autofill_automerge()
    # twin-side coupling assert (r329): json and md must come from the SAME side
    twin_js = 'docs/daily_report/REPORT-2026-09-27.json'
    twin_md = 'docs/daily_report/REPORT-2026-09-27.md'
    jside = 'mine' if RES[twin_js] == blob(3, twin_js) else 'origin'
    mside = 'mine' if RES[twin_md] == blob(3, twin_md) else 'origin'
    assert jside == mside, f'daily_report twins picked different sides: json={jside} md={mside} -- HYBRID TWIN FORBIDDEN'
    # dashboard pair-law assert: js and json same side
    djs, djson = 'results/dashboard_status.js', 'results/dashboard_status.json'
    js_side = 'mine' if RES[djs] == blob(3, djs) else 'origin'
    json_side = 'mine' if RES[djson] == blob(3, djson) else 'origin'
    assert js_side == json_side, f'dashboard pair picked different sides: js={js_side} json={json_side}'
    # parse-verify all resolved payloads BEFORE any write (r185 law)
    for p, data in RES.items():
        if p.endswith('.jsonl'):
            for l in data.decode('utf-8').splitlines():
                if l.strip().startswith('{'):
                    json.loads(l)
        elif p.endswith('.json'):
            json.loads(data.decode('utf-8'))
    for p, data in RES.items():
        with open(p, 'wb') as f:
            f.write(data)
    print('== r335 resolver: resolved faces ==')
    for r in REPORT:
        print(r)
    print('twin-coupling: json/md same side =', jside, '| dashboard pair same side =', js_side)
    assert len(RES) == 28, f'expected 28 resolved files, got {len(RES)}'

if __name__ == '__main__':
    main()
