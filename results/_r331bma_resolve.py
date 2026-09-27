# r331 bm-a rebase push-collision resolver (16-UU batch vs bm-c r86 eb2bb3db same-window S6 double-run, R322 family)
# Canon: bigmoney-conflict-resolve SKILL.md 形态表 + 解后纪律 §三.
# Stage semantics DURING REBASE (r85 law): stage2 = origin side (bm-c), stage3 = replayed commit (bm-a r331). Verified by ts probes below.
# Recipes: autofill=mixed-dict+ledger composite-key union (r322/r83); compute_audit=rolling-ledger (ts,machine) union (r85 window law);
#          regime_state=rolling-ledger asof-union; x2_watch=append-log line-union; 12x snapshot faces=take-new by deep ts probe (r319 existence-first, r140 tie->HEAD).
# EOL/indent mirror = base blob (:1:) probe per r223/r234/r329-pitlaw-3 (never the conflicted worktree file).
# Fail-closed: any assertion failure raises BEFORE any write (zero wrong-side writes).
import subprocess, json, sys

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

RES = {}

def resolve_autofill():
    p = 'results/autofill_state.json'
    eol, ind = base_eol_indent(p)
    a, b = parse(blob(2, p), p), parse(blob(3, p), p)
    KEY = ('ts', 'machine', 'pid', 'runner_sha256', 'entry', 'shard')
    def key(e): return tuple(e.get(k) for k in KEY)
    merged, seen = [], {}
    for e in a['launches'] + b['launches']:
        k = key(e)
        if k in seen:
            prev = seen[k]
            if prev == e:
                continue
            fa, fb = set(prev.keys()), set(e.keys())
            if fa <= fb or fb <= fa:
                u = dict(prev); u.update(e)
                seen[k] = u
                merged[merged.index(prev)] = u
            else:
                raise RuntimeError(f'autofill composite-key collision TRUE-DIVERGENCE at {k} -- escalate, no write')
        else:
            seen[k] = e
            merged.append(e)
    merged.sort(key=lambda e: e.get('ts', ''), reverse=True)
    merged = merged[:50]
    merged.sort(key=lambda e: e.get('ts', ''))
    lt_a, lt_b = a.get('last_tick', {}), b.get('last_tick', {})
    ta, tb = lt_a.get('ts'), lt_b.get('ts')
    lt = lt_a if (ta is None and tb is None) or (tb is None or (ta is not None and ta >= tb)) else lt_b
    if ta == tb:
        lt = lt_a  # tie -> HEAD (stage2/origin)
    out = {'launches': merged, 'last_tick': lt}
    assert isinstance(out['last_tick'], dict), 'last_tick must be dict'
    assert len(out['launches']) <= 50
    n_union = len({key(e) for e in a['launches']} | {key(e) for e in b['launches']})
    assert len(merged) <= n_union
    RES[p] = dump(out, eol, ind)
    return f'autofill: launches {len(a["launches"])}|{len(b["launches"])} -> {len(merged)} (key-union {n_union}, collisions content-checked), last_tick ts={lt.get("ts")} (a={ta} b={tb})'

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
    return f'compute_audit: history {len(ha)}|{len(hb)} -> {len(merged)} union (dedup identical only), latest ts={latest.get("ts")} machine={latest.get("machine")} (a={ta} b={tb})'

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
                    if tag == 'transitions':
                        raise RuntimeError(f'regime transitions key {k} divergent')
                    raise RuntimeError(f'regime {tag} key {k} divergent')
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
    return f'regime_state: history {len(a.get("history",[]))}|{len(b.get("history",[]))} -> {len(hist)} asof-union, transitions -> {len(tr)}, state from updated={src.get("updated")}'

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
    return f'x2_watch_log: {len(la)}|{len(lb)} -> {len(merged)} line-union'

SNAPSHOTS = {
    'results/dashboard_status.json': ('meta', 'generated_at'),
    'results/fundamental_b_layer_filter.json': ('updated',),
    'results/futures_update_status.json': ('ts',),
    'results/heat_update_status.json': ('updated',),
    'results/lhb_update_status.json': ('updated',),
    'results/prospect_paper/_summary.json': ('generated',),
    'results/prospect_promotion/_summary.json': ('generated',),
    'results/scorecard_v1.json': ('generated',),
    'results/strategy_scorecard.json': ('generated',),
    'results/t35_open_fill_verify.json': ('ts',),
    'results/token_usage.json': ('generated',),
    'results/update_status.json': ('updated',),
}

def probe(d, path):
    cur = d
    for f in path:
        if not isinstance(cur, dict) or f not in cur:
            return None
        cur = cur[f]
    return cur

def resolve_snapshots():
    lines = []
    for p, tspath in SNAPSHOTS.items():
        eol, ind = base_eol_indent(p)
        a, b = parse(blob(2, p), p), parse(blob(3, p), p)
        ta, tb = probe(a, tspath), probe(b, tspath)
        if ta is None and tb is None:
            raise RuntimeError(f'{p}: ts probe {tspath} missing BOTH sides (r319 existence-first fail)')
        if ta is None or (tb is not None and tb > ta):
            pick, side, ts = b, 'stage3(mine)', tb
        elif tb is None or ta > tb:
            pick, side, ts = a, 'stage2(origin)', ta
        else:
            pick, side, ts = a, 'stage2(origin) tie', ta
        RES[p] = dump(pick, eol, ind)
        lines.append(f'{p}: take-new {side} ts={ts}')
    return '\n'.join(lines)

def main():
    report = [resolve_autofill(), resolve_compute_audit(), resolve_regime(), resolve_x2(), resolve_snapshots()]
    # parse-verify all resolved payloads BEFORE any write (r185 law)
    for p, data in RES.items():
        if p.endswith('.jsonl'):
            for i, l in enumerate(data.decode('utf-8').splitlines()):
                if not l.strip():
                    continue
                json.loads(l) if l.startswith('{') else None
        else:
            json.loads(data.decode('utf-8'))
    for p, data in RES.items():
        with open(p, 'wb') as f:
            f.write(data)
    print('== r331 resolver: 16 files resolved, parse-verified, written ==')
    for r in report:
        print(r)
    print('files:', len(RES))
    assert len(RES) == 16, f'expected 16 resolved files, got {len(RES)}'

if __name__ == '__main__':
    main()
