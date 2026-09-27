# -*- coding: utf-8 -*-
"""r312 bm-b S0 main-reconcile resolver (bigmoney-conflict-resolve canon).

Collision: bm-a round-305 trio (db53a270 + eb99d7c7 pushed to origin/main) vs
bm-b r311 trio (5c43e1a2/d3dbbef0/6f939528 on local main) = 3v3 divergence.
S0 rebase local main onto eb99d7c7; commit 1 replay hit 27 UU, ALL regenerable
S6 mirror faces; zero core-deliverable touch.

REBASE STAGE SEMANTICS (r311 phase2 mapping kept): stage2=ours=new base
(origin/main, bm-a r305 face); stage3=theirs=replayed bm-b r311 face.

Recipes (classifier output + 16 UNKNOWN hand-classified, same family as _r311_resolve.py):
- rolling-ledger (compute_audit.json / regime_state.json): list-key union zero-loss, scalars take-new.
- append-log (x2_watch_log.jsonl): line-level union (r188).
- js-wrapper-snapshot (dashboard_status.js): take-side whole bytes paired with .json twin (R209), wrapper assert.
- snapshot (all status/scorecard/paper/report/export/verify/token files): take-new whole bytes by
  DEEP ts probe (F-20260927-01 nested-key gap applied locally: probe ts at any depth, time-of-day
  format only so bar/cutoff dates never masquerade as recency); tie/absent -> HEAD/stage2 (r140).
- REPORT-*.md follows its .json twin side.
"""
import subprocess, json, re, sys

REPO = r'C:\Users\Administrator\Desktop\Bigmoney'
CAPS = {'launches': 50}
TS_KEYS = ['ts', 'generated', 'generated_at', 'updated', 'updated_at', 'asof', 'as_of',
           'report_date', 'last_fetched_at', 'generated_from_state_updated', 'time']
ABSENT = '__ABSENT__'
TS_RE = re.compile(r'^\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}')

def sh(args):
    r = subprocess.run(args, capture_output=True, cwd=REPO)
    return r.returncode, r.stdout, r.stderr

def stage(n, path):
    rc, out, _ = sh(['git', 'show', ':%d:%s' % (n, path)])
    return out if rc == 0 else None

def ufe(b):
    return b.decode('utf-8-sig')

def looks_like_ts(v):
    return isinstance(v, str) and bool(TS_RE.match(v))

def deep_ts(obj, _depth=0):
    """Collect recency-looking ts values at any dict/list depth (time-of-day format only)."""
    cands = []
    if _depth > 8:
        return cands
    if isinstance(obj, dict):
        for k, v in obj.items():
            if looks_like_ts(v) and (k in TS_KEYS or k.endswith('_at') or k.endswith('_ts')):
                cands.append(v)
            elif isinstance(v, (dict, list)):
                cands += deep_ts(v, _depth + 1)
    elif isinstance(obj, list):
        for e in (obj[:50] + (obj[-5:] if len(obj) > 50 else [])):
            cands += deep_ts(e, _depth + 1)
    return cands

def pick_newest(cands):
    return max(cands) if cands else None  # ISO same-format lexicographic max

def newer(a_ts, b_ts):
    if a_ts is None and b_ts is None:
        return None
    if a_ts is None:
        return 'b'
    if b_ts is None:
        return 'a'
    if a_ts == b_ts:
        return 'tie'
    return 'a' if a_ts > b_ts else 'b'

def union_id(lst):
    seen, out = set(), []
    for e in lst:
        i = json.dumps(e, sort_keys=True, ensure_ascii=False)
        if i not in seen:
            seen.add(i)
            out.append(e)
    return out

def sort_ts(lst):
    def key(e):
        t = pick_newest(deep_ts(e)) if isinstance(e, dict) else None
        return t or ''
    try:
        return sorted(lst, key=key)
    except Exception:
        return list(lst)

def emit(obj, base_b):
    txt_b = ufe(base_b)
    m = re.search(r'\r?\n([ \t]+)"', txt_b)
    indent = len(m.group(1)) if m else 1
    crlf = '\r\n' in txt_b
    text = json.dumps(obj, ensure_ascii=False, indent=indent)
    if crlf:
        text = text.replace('\n', '\r\n')
    if txt_b.endswith('\n') or txt_b.endswith('\r'):
        text += '\r\n' if crlf else '\n'
    return text

def resolve_snapshot(path, ours_b, theirs_b):
    try:
        oj = json.loads(ufe(ours_b))
        tj = json.loads(ufe(theirs_b))
    except Exception as e:
        return {'error': 'parse: %s' % e}
    ca, cb = deep_ts(oj), deep_ts(tj)
    ta, tb = pick_newest(ca), pick_newest(cb)
    r = newer(ta, tb)
    side = 'theirs' if r == 'b' else 'ours'  # tie/None -> HEAD/stage2 (r140)
    diff_keys = [k for k in set(list(oj) + list(tj))
                 if json.dumps(oj.get(k, ABSENT), sort_keys=True) != json.dumps(tj.get(k, ABSENT), sort_keys=True)]
    return {'recipe': 'snapshot-take-new(deep-ts)', 'side': side,
            'side_ours': 'origin/main bm-a r305', 'side_theirs': 'bm-b r311 5c43e1a2',
            'ts_ours': ta, 'ts_theirs': tb,
            'n_ts_cands_ours': len(ca), 'n_ts_cands_theirs': len(cb),
            'diff_keys': diff_keys[:8], 'n_diff_keys': len(diff_keys),
            'bytes': theirs_b if side == 'theirs' else ours_b}

def resolve_ledger(path, ours_b, theirs_b, base_b):
    oj = json.loads(ufe(ours_b))
    tj = json.loads(ufe(theirs_b))
    ta, tb = pick_newest(deep_ts(oj)), pick_newest(deep_ts(tj))
    r = newer(ta, tb)
    if r == 'b':
        newj, oldj, new_side = tj, oj, 'theirs'
    else:
        newj, oldj, new_side = oj, tj, 'ours'
    out, report_lists = {}, {}
    for k in list(newj) + list(oldj):
        if k in out:
            continue
        nv, ov = newj.get(k, ABSENT), oldj.get(k, ABSENT)
        if isinstance(nv, list) and isinstance(ov, list):
            merged = union_id(ov + nv)
            if k in CAPS:
                newest = sorted(merged, key=lambda e: (pick_newest(deep_ts(e)) if isinstance(e, dict) else None) or '', reverse=True)
                merged = sort_ts(newest[:CAPS[k]])
            else:
                merged = sort_ts(merged)
            out[k] = merged
            report_lists[k] = {'|ours|': len(ov), '|theirs|': len(nv), '|union|': len(merged)}
        elif isinstance(nv, dict) and isinstance(ov, dict):
            rr = newer(pick_newest(deep_ts(ov)), pick_newest(deep_ts(nv)))
            out[k] = ov if rr == 'a' else (nv if rr == 'b' else (nv if new_side == 'ours' else ov))
        else:
            out[k] = nv if nv is not ABSENT else ov
    text = emit(out, base_b)
    json.loads(text)  # parse-validate before write (r185)
    return {'recipe': 'ledger-union', 'side_new': new_side, 'ts_ours': ta, 'ts_theirs': tb,
            'lists': report_lists, 'text': text}

def resolve_jsonl(path, ours_b, theirs_b, base_b):
    la = [l for l in ufe(ours_b).splitlines() if l.strip()]
    lb = [l for l in ufe(theirs_b).splitlines() if l.strip()]
    seen, out = set(), []
    for l in la + lb:
        if l not in seen:
            seen.add(l)
            out.append(l)
    for l in out:
        json.loads(l)
    crlf = '\r\n' in ufe(base_b)
    nl = '\r\n' if crlf else '\n'
    text = nl.join(out)
    if ufe(base_b).endswith('\n'):
        text += nl
    return {'recipe': 'jsonl-line-union', 'n_ours': len(la), 'n_theirs': len(lb),
            'n_union': len(out), 'text': text}

def main(probe_only):
    rc, out, _ = sh(['git', 'diff', '--name-only', '--diff-filter=U'])
    uu = [p for p in ufe(out).splitlines() if p.strip()]
    def twin_of(path):
        if path == 'results/dashboard_status.js':
            return 'results/dashboard_status.json'
        if path.endswith('.md'):
            return path[:-3] + '.json'
        return None
    followers = [p for p in uu if twin_of(p) and twin_of(p) in uu]
    order = [p for p in uu if p not in followers] + followers
    summary = {}
    for path in order:
        base_b, ours_b, theirs_b = stage(1, path), stage(2, path), stage(3, path)
        if ours_b is None or theirs_b is None:
            summary[path] = {'error': 'missing stage blob'}
            continue
        if path in ('results/compute_audit.json', 'results/regime_state.json', 'results/autofill_state.json'):
            res = resolve_ledger(path, ours_b, theirs_b, base_b)
            if path == 'results/autofill_state.json':
                res['recipe'] = 'mixed-dict+ledger (launches union cap50 asc write-back + last_tick inner-ts whole-dict, tie->HEAD)'
            body = res.pop('text').encode('utf-8')
        elif path.endswith('.jsonl'):
            res = resolve_jsonl(path, ours_b, theirs_b, base_b)
            body = res.pop('text').encode('utf-8')
        else:
            twin = twin_of(path)
            if twin and twin in uu and 'side' in summary.get(twin, {}):
                side = summary[twin]['side']
                res = {'recipe': 'take-side-whole-bytes (twin %s side=%s)' % (twin, side), 'side': side}
                body = theirs_b if side == 'theirs' else ours_b
            else:
                res = resolve_snapshot(path, ours_b, theirs_b)
                if 'error' in res:
                    summary[path] = res
                    continue
                body = res.pop('bytes')
            if path.endswith('.js'):
                assert ufe(body).lstrip().startswith('window.DASH_DATA'), 'js wrapper stripped (R209)'
        if probe_only:
            res = dict(res)
            res.pop('bytes', None)
            summary[path] = res
            continue
        with open(path, 'wb') as f:
            f.write(body)
        sh(['git', 'add', '--', path])
        summary[path] = res
    print(json.dumps(summary, ensure_ascii=False, indent=1))
    if not probe_only:
        rc, out, err = sh(['git', 'status', '--porcelain'])
        print('--- post-resolve status ---')
        print(ufe(out))

if __name__ == '__main__':
    main('--probe' in sys.argv)
