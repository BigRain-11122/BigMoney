# r334 bm-a rebase push-collision resolver (27-UU batch vs bm-b r331 window {b5957767,c3a46b8a,88e6dc96} same-window S6 double-run, R322 family)
# Canon: bigmoney-conflict-resolve SKILL.md 形态表 + 解后纪律 §三.
# Stage semantics DURING REBASE (r85 law): stage2 = origin side (bm-b), stage3 = replayed commit (bm-a r334). Verified by ts probes.
# Intersection audit (r331 pitlaw): intersection(28) == 27 UU + autofill_state.json(auto-merged, VERIFIED canon-perfect separately:
#   launches 46=46|45 key-union zero-dup asc-sorted, last_tick take-mine 15:50:02 later-than-origin 15:40:02 dict-ok -- zero fix needed).
# Recipes: compute_audit=rolling-ledger (ts,machine) union (r85 window law, collisions content-identical assert);
#          regime_state=rolling-ledger asof-union + state take-new by 'updated';
#          x2_watch=append-log line-union; 22x snapshot/measurement faces=take-side WHOLE BYTES by deep max-ts probe
#          (all probes: mine 15:51-15:53 > origin 15:47-15:48, recon pre-verified); daily_report md twin = same-side blob
#          byte-copy (twin-side coupling r329, md is NOT JSON -- never json.loads it); dashboard js+json pair-law same side.
# EOL/indent: take-side whole-blob bytes preserve producer format exactly (no re-emit); union faces mirror base blob :1: (r223/r234/r329-p3).
# Fail-closed: any assertion failure raises BEFORE any write (zero wrong-side writes).
import subprocess, json, re

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
    m = TSRE.findall(b.decode('utf-8', errors='replace'))
    return max(m) if m else None

RES = {}
REPORT = []

def resolve_compute_audit():
    p = 'results/compute_audit.json'
    eol, ind = base_eol_indent(p)
    a, b = parse(blob(2, p), p), parse(blob(3, p), p)
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
        latest = la  # tie -> HEAD
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

# take-side whole-bytes faces: (path, is_json) -- md and js are NOT json.loads'd (r329 md law; R209 js law)
TAKE_SIDES = [
    ('docs/daily_report/REPORT-2026-09-27.json', True),   # twin json face: generated_at deep-probe
    ('docs/daily_report/REPORT-2026-09-27.md', False),    # twin md face: same-side blob byte-copy (coupled to json side)
    ('results/daily_scorecard.json', True),
    ('results/dashboard_status.js', False),               # js-wrapper: whole bytes, pair-law same side as .json
    ('results/dashboard_status.json', True),
    ('results/fundamental_b_layer_filter.json', True),
    ('results/futures_update_status.json', True),
    ('results/heat_update_status.json', True),
    ('results/lhb_update_status.json', True),
    ('results/paper/COMPOSITE-CE-01_paper.json', True),
    ('results/paper/COMPOSITE-CE-02_paper.json', True),
    ('results/paper/DROUGHT-CE-01_paper.json', True),
    ('results/paper/ENGULF-CE-01_paper.json', True),
    ('results/paper/NEEDLE-DE-01_paper.json', True),
    ('results/paper/VOLATILITY-CE-01_paper.json', True),
    ('results/paper_export/export-2026-09-24.json', True),
    ('results/paper_export/latest.json', True),
    ('results/prospect_paper/_summary.json', True),
    ('results/prospect_promotion/_summary.json', True),
    ('results/scorecard_v1.json', True),
    ('results/strategy_scorecard.json', True),
    ('results/t35_open_fill_verify.json', True),
    ('results/token_usage.json', True),
    ('results/update_status.json', True),
]

def resolve_take_sides():
    for p, is_json in TAKE_SIDES:
        bo, bm = blob(2, p), blob(3, p)
        to, tm = maxts(bo), maxts(bm)
        if is_json:
            parse(bo, p); parse(bm, p)  # both sides must be valid JSON (r185 pre-write verify)
        assert to is not None or tm is not None, f'{p}: no ts found either side (r319 existence-first fail)'
        if tm is not None and (to is None or tm > to):
            side, ts = 'stage3(mine)', tm
            RES[p] = bm
        elif to is not None and (tm is None or to > tm):
            side, ts = 'stage2(origin)', to
            RES[p] = bo
        else:
            side, ts = 'stage2(origin) tie', to  # r140 tie -> HEAD/origin
            RES[p] = bo
        REPORT.append(f'{p}: take-side {side} ts={ts}')

def main():
    resolve_compute_audit()
    resolve_regime()
    resolve_x2()
    resolve_take_sides()
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
    print('== r334 resolver: 27 UU files resolved, parse-verified, written ==')
    for r in REPORT:
        print(r)
    assert len(RES) == 27, f'expected 27 resolved files, got {len(RES)}'
    print('twin-coupling: json/md same side =', jside, '| dashboard pair same side =', js_side)

if __name__ == '__main__':
    main()
