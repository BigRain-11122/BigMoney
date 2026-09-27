# r338 bm-a rebase push-collision resolver (28-UU batch vs bm-c r90 S0-FOLD + bm-b r333/tick same-window S6 double-run; r334 lineage)
# Canon: bigmoney-conflict-resolve SKILL.md forms + post-discipline; r335 amendments applied:
#   (1) future-sentinel in blanket max-ts (dashboard next-fire 2026-09-28 poison guard), (2) known-producer probe path first.
# Stage semantics DURING REBASE (r85 law): stage2 = origin side (bm-c r90 / bm-b), stage3 = replayed commit (bm-a r338).
# Archive 202609.md = append-journal suffix-concat union: base :1: + origin-suffix + mine-suffix
#   (double 20th-batch same-window = r85 double-十五批 precedent: both sections coexist zero-overwrite, receipt in round report).
# Fail-closed: any assertion failure raises BEFORE any write.
import subprocess
import json
import re
import time

TODAY = time.strftime('%Y-%m-%d')


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


TSRE = re.compile(r'2026-[0-9]{2}-[0-9]{2}[ T][0-9:.]+')


def maxts(b):
    # r335 law: future-sentinel -- plan-face fields (next-fire etc.) are NOT generation ts; exclude > today
    m = [t for t in TSRE.findall(b.decode('utf-8', errors='replace')) if t[:10] <= TODAY]
    return max(m) if m else None


def probe_generated(b):
    # r335 law: known-producer probe path FIRST (existence-checked, r319)
    try:
        o = json.loads(b.decode('utf-8'))
    except Exception:
        return None
    for path in (('meta', 'generated_at'), ('generated_at',), ('latest', 'ts'), ('ts',)):
        cur = o
        ok = True
        for k in path:
            if isinstance(cur, dict) and k in cur:
                cur = cur[k]
            else:
                ok = False
                break
        if ok and isinstance(cur, str) and cur[:10] <= TODAY:
            return cur
    return None


RES = {}
REPORT = []


def resolve_compute_audit():
    p = 'results/compute_audit.json'
    eol, ind = base_eol_indent(p)
    a, b = parse(blob(2, p), p), parse(blob(3, p), p)
    ha, hb = a['history'], b['history']

    def key(e):
        return (e.get('ts'), e.get('machine'))

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
    # r85 window law: producer roll-window write-back may shrink union face; window-first-ts survival check, not line-count
    assert len(merged) == n_union, 'history union count != key-union count'
    la, lb = a['latest'], b['latest']
    ta, tb = la.get('ts'), lb.get('ts')
    latest = la if (ta is not None and (tb is None or ta >= tb)) else lb
    if ta == tb:
        latest = la  # tie -> HEAD side (stage2 origin, r140)
    out = {'latest': latest, 'history': merged}
    RES[p] = dump(out, eol, ind)
    REPORT.append(f'compute_audit: history {len(ha)}|{len(hb)} -> {len(merged)} (ts,machine)-union, latest ts={latest.get("ts")}')


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
    REPORT.append(f'regime_state: history {len(a.get("history", []))}|{len(b.get("history", []))} -> {len(hist)} asof-union, transitions -> {len(tr)}, state from updated={src.get("updated")}')


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


def resolve_archive_suffix():
    # append-journal md: base :1: + origin-suffix + mine-suffix (D-09 suffix-concat, entry lines preserved both sides)
    p = 'research/memory-archive/202609.md'
    base = blob(1, p)
    o = blob(2, p)
    m = blob(3, p)
    if not o.startswith(base) and not m.startswith(base):
        # in-place edits on both sides vs base: fall back to line-level union of fulls
        raise RuntimeError('archive: neither side extends base blob -- manual entry-level union required')
    if o.startswith(base) and m.startswith(base):
        so, sm = o[len(base):], m[len(base):]
    elif o.startswith(base):
        so, sm = o[len(base):], b''
    else:
        so, sm = b'', m[len(base):]
    RES[p] = base + so + sm
    REPORT.append(f'archive: suffix-concat base={len(base)}B + origin-suffix={len(so)}B + mine-suffix={len(sm)}B (double 20th-batch coexist, r85 precedent)')


# take-side whole-bytes faces; md/js never json.loads'd (r329/R209); known-producer probe FIRST for dashboard pair (r335)
PROBE_FIRST = {'results/dashboard_status.json', 'results/dashboard_status.js'}
TAKE_SIDES = [
    ('docs/daily_report/REPORT-2026-09-27.json', True),
    ('docs/daily_report/REPORT-2026-09-27.md', False),
    ('results/daily_scorecard.json', True),
    ('results/dashboard_status.js', False),
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
        if is_json:
            parse(bo, p)
            parse(bm, p)  # both sides valid JSON (r185)
        po, pm = (probe_generated(bo) if p in PROBE_FIRST else None), (probe_generated(bm) if p in PROBE_FIRST else None)
        to, tm = po or maxts(bo), pm or maxts(bm)
        assert to is not None or tm is not None, f'{p}: no ts either side (r319 fail)'
        if tm is not None and (to is None or tm > to):
            side, ts = 'stage3(mine)', tm
            RES[p] = bm
        elif to is not None and (tm is None or to > tm):
            side, ts = 'stage2(origin)', to
            RES[p] = bo
        else:
            side, ts = 'stage2(origin) tie', to  # r140 tie -> HEAD
            RES[p] = bo
        REPORT.append(f'{p}: take-side {side} ts={ts}')


def main():
    resolve_compute_audit()
    resolve_regime()
    resolve_x2()
    resolve_archive_suffix()
    resolve_take_sides()
    # twin-side coupling (r329): json and md same side
    twin_js = 'docs/daily_report/REPORT-2026-09-27.json'
    twin_md = 'docs/daily_report/REPORT-2026-09-27.md'
    jside = 'mine' if RES[twin_js] == blob(3, twin_js) else 'origin'
    mside = 'mine' if RES[twin_md] == blob(3, twin_md) else 'origin'
    assert jside == mside, f'daily_report twins different sides: json={jside} md={mside} -- HYBRID TWIN FORBIDDEN'
    # dashboard pair-law: js+json same side
    djs, djson = 'results/dashboard_status.js', 'results/dashboard_status.json'
    js_side = 'mine' if RES[djs] == blob(3, djs) else 'origin'
    json_side = 'mine' if RES[djson] == blob(3, djson) else 'origin'
    assert js_side == json_side, f'dashboard pair different sides: js={js_side} json={json_side}'
    # parse-verify all before write (r185)
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
    print('== r338 resolver: %d UU files resolved, parse-verified, written ==' % len(RES))
    for r in REPORT:
        print(r)
    print('twin-coupling: json/md same side =', jside, '| dashboard pair same side =', js_side)


if __name__ == '__main__':
    main()
