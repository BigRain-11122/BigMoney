# -*- coding: utf-8 -*-
"""r498 bm-b S0 rebase resolver: replay 51fb149be (r497 rider0 carry) onto bb3ebb3b2.

17 UU canon-resolved per bigmoney-conflict-resolve SKILL.md:
- memory-union      CODELY.md (3-way line union via git merge-file --union, dedupe non-empty exact lines)
- rolling-ledger    results/compute_audit.json, results/regime_state.json (ledger list union zero-loss, state take-new by doc ts)
- snapshot take-new by ts (raw bytes of winner side; same-second tie -> stage2=HEAD per r140):
    results/fundamental_b_layer_filter.json, futures_update_status.json, lhb_update_status.json,
    update_status.json, token_usage.json, scorecard_v1.json, strategy_scorecard.json,
    docs/daily_report/REPORT-2026-10-01.json, docs/live_usage/LIVE-2026-10-01.json, LIVE-latest.json,
    results/dashboard_status.json
- js/md twins follow their .json twin winner side (raw bytes, pair consistency):
    dashboard_status.js, REPORT-2026-10-01.md, LIVE-2026-10-01.md, LIVE-latest.md

Fail-closed per file: any error -> file left UU, reported, exit 2.
Rebase stage convention (cherry-pick replay): stage2 = HEAD = onto side (origin), stage3 = replayed commit (ours).
All side decisions are content/ts based, not stage-identity based.
"""
import subprocess, json, os, re, sys, tempfile

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def git(*args, binary=False):
    r = subprocess.run(['git', '-C', REPO] + list(args), capture_output=True)
    if r.returncode != 0:
        raise RuntimeError('git %s rc=%s: %s' % (args[:3], r.returncode, r.stderr[:300]))
    return r.stdout if binary else r.stdout.decode('utf-8', 'replace')

def stage_entries():
    out = git('ls-files', '-u')
    per = {}
    for line in out.strip().splitlines():
        meta, path = line.split('\t', 1)
        mode, sha, stage = meta.split()
        per.setdefault(path, {})[int(stage)] = sha
    return per

def blob(sha):
    return git('cat-file', 'blob', sha, binary=True)

def writeb(path, data):
    with open(os.path.join(REPO, path), 'wb') as f:
        f.write(data)

TS_KEYS = ['generated', 'generated_at', 'generated_utc', 'updated', 'updated_at', 'ts', 'as_of', 'cutoff', 'time', 'last_run', 'run_at']

def _tsval(v):
    if isinstance(v, bool):
        return None
    if isinstance(v, (int, float)):
        return ('num', float(v))
    if isinstance(v, str) and v.strip():
        return ('str', v.strip())
    return None

def doc_winner_ts(o, t):
    """Common ts-ish key (top-level, then inside 'meta') present in both docs; newer wins.
    Returns ('O'|'T', key, oval, tval) or None."""
    for scope in (None, 'meta'):
        for k in TS_KEYS:
            ov_src = o if scope is None else (o.get(scope) if isinstance(o, dict) else None)
            tv_src = t if scope is None else (t.get(scope) if isinstance(t, dict) else None)
            if not isinstance(ov_src, dict) or not isinstance(tv_src, dict):
                continue
            if k in ov_src and k in tv_src:
                ov, tv = _tsval(ov_src[k]), _tsval(tv_src[k])
                if ov is None or tv is None or ov[0] != tv[0]:
                    continue
                label = k if scope is None else scope + '.' + k
                if ov[1] != tv[1]:
                    win = 'O' if ov[1] > tv[1] else 'T'
                    return (win, label, ov_src[k], tv_src[k])
                return ('O', label + '(tie)', ov_src[k], tv_src[k])  # same-second tie -> stage2 = HEAD-side
    return None

def take_side_by_ts(path, stages):
    b = json.loads(blob(stages[2]).decode('utf-8-sig'))
    t = json.loads(blob(stages[3]).decode('utf-8-sig'))
    w = doc_winner_ts(b, t)
    if w is None:
        # no comparable ts key -> fail closed for manual定性 (never blind take)
        raise RuntimeError('no common ts key to compare')
    side = w[0]
    sha = stages[2] if side == 'O' else stages[3]
    writeb(path, blob(sha))
    return {'class': 'snapshot', 'winner': side, 'ts_key': w[1], 'O': w[2], 'T': w[3]}

def detect_fmt(raw):
    m = re.search(rb'\n( +)["\{\[\d]', raw)
    indent = len(m.group(1)) if m else 2
    crlf = b'\r\n' in raw
    trail = raw.endswith(b'\n')
    bom = raw.startswith(b'\xef\xbb\xbf')
    return indent, crlf, trail, bom

def union_list(o, t):
    seen, out = set(), []
    for item in (o if isinstance(o, list) else []) + (t if isinstance(t, list) else []):
        key = json.dumps(item, sort_keys=True, ensure_ascii=False)
        if key not in seen:
            seen.add(key)
            out.append(item)
    if out and all(isinstance(i, dict) and _tsval(i.get('ts')) for i in out):
        try:
            out.sort(key=lambda i: i['ts'])
        except Exception:
            pass
    n_in = len(set(json.dumps(i, sort_keys=True, ensure_ascii=False) for i in (o or []) + (t or [])))
    assert len(out) == n_in, 'union loss: %d -> %d' % (n_in, len(out))
    return out

def merge3(b, o, t, winner, path=''):
    if o == t:
        return o
    if o == b:
        return t
    if t == b:
        return o
    if isinstance(o, dict) and isinstance(t, dict):
        res = {}
        keys = set(o) | set(t)
        if isinstance(b, dict):
            keys |= set(b)
        for k in sorted(keys):
            res[k] = merge3(b.get(k) if isinstance(b, dict) else None,
                            o.get(k), t.get(k), winner, path + '.' + k)
        return res
    if isinstance(o, list) and isinstance(t, list):
        return union_list(o, t)
    # scalar both-changed: state field -> take from doc winner (newest state semantics)
    return o if winner == 'O' else t

def resolve_ledger(path, stages):
    B = json.loads(blob(stages[1]).decode('utf-8-sig'))
    O = json.loads(blob(stages[2]).decode('utf-8-sig'))
    T = json.loads(blob(stages[3]).decode('utf-8-sig'))
    w = doc_winner_ts(O, T)
    winner = w[0] if w else 'O'
    res = merge3(B, O, T, winner)
    raw_ref = blob(stages[2])
    indent, crlf, trail, bom = detect_fmt(raw_ref)
    text = json.dumps(res, ensure_ascii=False, indent=indent)
    if trail:
        text += '\n'
    if crlf:
        text = text.replace('\n', '\r\n')
    writeb(path, (b'\xef\xbb\xbf' if bom else b'') + text.encode('utf-8'))
    # parse-validate round trip
    json.loads(open(os.path.join(REPO, path), 'rb').read().decode('utf-8-sig'))
    return {'class': 'rolling-ledger', 'winner_state': winner, 'ts_key': (w[1] if w else 'fallback-stage2')}

def resolve_memory(path, stages):
    fd, tmp_o = tempfile.mkstemp(text=True); os.close(fd)
    fd, tmp_b = tempfile.mkstemp(text=True); os.close(fd)
    fd, tmp_t = tempfile.mkstemp(text=True); os.close(fd)
    for p, sha in ((tmp_o, stages[2]), (tmp_b, stages[1]), (tmp_t, stages[3])):
        with open(p, 'wb') as f:
            f.write(blob(sha))
    r = subprocess.run(['git', '-C', REPO, 'merge-file', '-p', '--union', tmp_o, tmp_b, tmp_t], capture_output=True)
    if r.returncode not in (0,):
        # merge-file returns >0 on conflicts, but --union should always succeed; accept 0..255 w/o markers
        if b'<<<<<<<' in r.stdout or r.returncode > 127:
            raise RuntimeError('merge-file rc=%d' % r.returncode)
    data = r.stdout
    lines = data.splitlines(keepends=True)
    seen, out = set(), []
    for ln in lines:
        s = ln.strip()
        if s and s in seen:
            continue
        if s:
            seen.add(s)
        out.append(ln)
    merged = b''.join(out)
    for marker in (b'<<<<<<<', b'>>>>>>>', b'======='):
        if any(l.strip() == marker or l.strip().startswith(marker) for l in merged.splitlines()):
            raise RuntimeError('marker survived union: %r' % marker)
    n_o = len(blob(stages[2]).splitlines()); n_t = len(blob(stages[3]).splitlines())
    assert len(merged.splitlines()) >= max(n_o, n_t), 'memory union line loss'
    writeb(path, merged)
    return {'class': 'memory-union', 'lines': len(merged.splitlines()), 'O_lines': n_o, 'T_lines': n_t}

def resolve_js_twin(path, stages, json_winner):
    side = json_winner
    # extract inner ts from both sides for diagnostics; winner side forced to json twin for pair consistency
    diag = {}
    for tag, sha in (('O', stages[2]), ('T', stages[3])):
        raw = blob(sha)
        m = re.search(rb'window\.DASH_DATA\s*=\s*(\{.*\})\s*;?\s*$', raw, re.S)
        if m:
            try:
                inner = json.loads(m.group(1).decode('utf-8-sig'))
                diag[tag] = inner.get('generated') or inner.get('ts') or inner.get('updated')
            except Exception:
                diag[tag] = 'unparsed'
        else:
            diag[tag] = 'no-wrapper'
    writeb(path, blob(stages[2] if side == 'O' else stages[3]))
    return {'class': 'js-twin', 'winner': side, 'inner_ts': diag}

def main():
    per = stage_entries()
    report = {}
    failed = []
    TWINS = {
        'results/dashboard_status.json': 'results/dashboard_status.js',
        'docs/live_usage/LIVE-2026-10-01.json': 'docs/live_usage/LIVE-2026-10-01.md',
        'docs/live_usage/LIVE-latest.json': 'docs/live_usage/LIVE-latest.md',
        'docs/daily_report/REPORT-2026-10-01.json': 'docs/daily_report/REPORT-2026-10-01.md',
    }
    LEDGERS = ['results/compute_audit.json', 'results/regime_state.json']
    resolved = []
    # pass 1: non-twin faces
    for path, stages in sorted(per.items()):
        if path in TWINS or path in TWINS.values() or path == 'CODELY.md' or path in LEDGERS:
            continue
        try:
            if len(stages) < 3:
                raise RuntimeError('missing stage entries: %s' % sorted(stages))
            report[path] = take_side_by_ts(path, stages)
            resolved.append(path)
        except Exception as e:
            failed.append((path, repr(e)))
            report[path] = {'error': repr(e)}
    # pass 2: ledgers
    for path in LEDGERS:
        try:
            stages = per[path]
            report[path] = resolve_ledger(path, stages)
            resolved.append(path)
        except Exception as e:
            failed.append((path, repr(e)))
            report[path] = {'error': repr(e)}
    # pass 3: memory
    try:
        report['CODELY.md'] = resolve_memory('CODELY.md', per['CODELY.md'])
        resolved.append('CODELY.md')
    except Exception as e:
        failed.append(('CODELY.md', repr(e)))
        report['CODELY.md'] = {'error': repr(e)}
    # pass 4: twins (.json already resolved in pass 1; carry winner to .js/.md twin)
    for jpath, twin in TWINS.items():
        try:
            if jpath not in resolved:
                stages = per[jpath]
                if len(stages) < 3:
                    raise RuntimeError('missing stage entries: %s' % sorted(stages))
                report[jpath] = take_side_by_ts(jpath, stages)
                resolved.append(jpath)
                git('add', '--', jpath)
            winner = report[jpath]['winner']
            if twin.endswith('.js'):
                report[twin] = resolve_js_twin(twin, per[twin], winner)
            else:
                writeb(twin, blob(per[twin][2] if winner == 'O' else per[twin][3]))
                report[twin] = {'class': 'md-twin', 'winner': winner}
            resolved.append(twin)
        except Exception as e:
            failed.append((twin, repr(e)))
            report[twin] = {'error': repr(e)}
    # git add each resolved file (targeted; never add -A during shared-tree surgery)
    for path in resolved:
        git('add', '--', path)
    # final validation: no unmerged entries left among resolved set
    still = set(stage_entries().keys())
    leftover = still - set(p for p, _ in failed)
    print(json.dumps({'resolved': sorted(resolved), 'failed': [(p, e) for p, e in failed],
                      'leftover_unmerged_after_add': sorted(leftover),
                      'detail': report}, ensure_ascii=False, indent=1, default=str))
    if failed or leftover:
        sys.exit(2)
    sys.exit(0)

if __name__ == '__main__':
    main()
