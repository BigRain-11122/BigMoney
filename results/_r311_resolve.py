# -*- coding: utf-8 -*-
"""r311 bm-b S7 push-collision resolver (bigmoney-conflict-resolve canon).

Collision: bm-a same-window round 304 (3e9d455c 08:24:57 + b4f036ac 08:25:43) vs
bm-b r311 push 08:26 -> rejected -> pull --rebase single retry (discipline).
24 UU, ALL regenerable S6 mirror faces; zero core-deliverable touch.

Recipes (classifier 12 + 16 UNKNOWN hand-classified per SKILL.md):
- rolling-ledger (compute_audit.json / regime_state.json): list-key union zero-loss, scalars take-new.
- mixed-dict+ledger (autofill_state.json): launches union -> ts desc cap50 -> re-sort ASC write-back (r245);
  last_tick inner-ts compare whole-dict assign, tie->HEAD/stage2 (r140); CRLF+indent mirrored from base (r223).
- append-log (x2_watch_log.jsonl): line-level union (r188).
- js-wrapper-snapshot (dashboard_status.js): take-side WHOLE bytes paired with .json twin (R209).
- snapshot (all status/scorecard/paper/report/export/verify/token files): take-new whole bytes by named ts key,
  tie or ts-absent -> HEAD/stage2 (r140). 16 UNKNOWN hand-classified as overwrite-style snapshots (each
  S6 producer re-writes the doc fresh each round; losing side = superseded state, not unique records).
"""
import subprocess, json, re, sys

REPO = r'C:\Users\Administrator\Desktop\Bigmoney'
CAPS = {'launches': 50}
TS_KEYS = ['ts', 'generated', 'generated_at', 'updated', 'updated_at', 'asof', 'as_of',
           'report_date', 'date', 'last_fetched_at']
ABSENT = '__ABSENT__'

def sh(args):
    r = subprocess.run(args, capture_output=True, cwd=REPO)
    return r.returncode, r.stdout, r.stderr

def stage(n, path):
    rc, out, _ = sh(['git', 'show', ':%d:%s' % (n, path)])
    return out if rc == 0 else None

def ufe(b):
    return b.decode('utf-8-sig')

def find_ts(obj):
    if not isinstance(obj, dict):
        return None
    for k in TS_KEYS:
        v = obj.get(k)
        if v is not None and not isinstance(v, (dict, list)):
            return str(v)
    return None

def newer(a_ts, b_ts):
    """Return 'a' | 'b' | 'tie' | None(both unknown)."""
    if a_ts is None and b_ts is None:
        return None
    if a_ts is None:
        return 'b'
    if b_ts is None:
        return 'a'
    try:
        fa, fb = float(a_ts), float(b_ts)
        return 'a' if fa > fb else ('b' if fb > fa else 'tie')
    except ValueError:
        return 'a' if a_ts > b_ts else ('b' if b_ts > a_ts else 'tie')

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
        t = find_ts(e) if isinstance(e, dict) else None
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
    ta, tb = find_ts(oj), find_ts(tj)
    r = newer(ta, tb)
    side = 'theirs' if r == 'b' else 'ours'  # tie/None -> HEAD/stage2 (r140)
    diff_keys = [k for k in set(list(oj) + list(tj))
                 if json.dumps(oj.get(k, ABSENT), sort_keys=True) != json.dumps(tj.get(k, ABSENT), sort_keys=True)]
    return {'recipe': 'snapshot-take-new', 'side': side, 'ts_ours': ta, 'ts_theirs': tb,
            'diff_keys': diff_keys[:8], 'n_diff_keys': len(diff_keys),
            'bytes': theirs_b if side == 'theirs' else ours_b}

def resolve_ledger(path, ours_b, theirs_b, base_b):
    oj = json.loads(ufe(ours_b))
    tj = json.loads(ufe(theirs_b))
    ta, tb = find_ts(oj), find_ts(tj)
    r = newer(ta, tb)
    if r == 'b':
        newj, oldj, new_side = tj, oj, 'theirs'
    else:
        newj, oldj, new_side = oj, tj, 'ours'  # tie/None -> ours(stage2=HEAD)
    out = {}
    report_lists = {}
    for k in list(newj) + list(oldj):
        if k in out:
            continue
        nv, ov = newj.get(k, ABSENT), oldj.get(k, ABSENT)
        if isinstance(nv, list) and isinstance(ov, list):
            merged = union_id(ov + nv)
            if k in CAPS:
                newest = sorted(merged, key=lambda e: (find_ts(e) if isinstance(e, dict) else None) or '', reverse=True)
                merged = sort_ts(newest[:CAPS[k]])
            else:
                merged = sort_ts(merged)
            out[k] = merged
            report_lists[k] = {'|ours|': len(ov), '|theirs|': len(nv), '|union|': len(merged)}
        elif isinstance(nv, dict) and isinstance(ov, dict):
            rr = newer(find_ts(ov), find_ts(nv))
            if rr == 'a':
                out[k] = ov
            elif rr == 'b':
                out[k] = nv
            else:
                out[k] = nv if new_side == 'ours' else ov  # tie -> stage2(HEAD)
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

def main():
    rc, out, _ = sh(['git', 'diff', '--name-only', '--diff-filter=U'])
    uu = [p for p in ufe(out).splitlines() if p.strip()]
    summary = {}
    for path in uu:
        base_b, ours_b, theirs_b = stage(1, path), stage(2, path), stage(3, path)
        if ours_b is None or theirs_b is None:
            summary[path] = {'error': 'missing stage blob'}
            continue
        if path == 'results/autofill_state.json':
            res = resolve_ledger(path, ours_b, theirs_b, base_b)
            res['recipe'] = 'mixed-dict+ledger (launches union cap50 asc write-back + last_tick inner-ts whole-dict, tie->HEAD)'
            body = res.pop('text').encode('utf-8')
            lt = json.loads(ufe(body))['last_tick']
            assert isinstance(lt, dict), 'last_tick not dict (r220)'
            res['last_tick'] = lt.get('ts'), lt.get('machine')
        elif path in ('results/compute_audit.json', 'results/regime_state.json'):
            res = resolve_ledger(path, ours_b, theirs_b, base_b)
            body = res.pop('text').encode('utf-8')
        elif path.endswith('.jsonl'):
            res = resolve_jsonl(path, ours_b, theirs_b, base_b)
            body = res.pop('text').encode('utf-8')
        else:
            # dashboard pair: choose side via json twin; js/md follow twin's side
            twin = None
            if path == 'results/dashboard_status.js':
                twin = 'results/dashboard_status.json'
            elif path.endswith('REPORT-2026-09-27.md'):
                twin = path[:-3] + '.json'
            if twin and twin in [p for p in uu] and twin in summary and 'side' in summary[twin]:
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
        with open(path, 'wb') as f:
            f.write(body)
        sh(['git', 'add', '--', path])
        summary[path] = res
    print(json.dumps(summary, ensure_ascii=False, indent=1))
    rc, out, err = sh(['git', 'status', '--porcelain'])
    print('--- post-resolve status ---')
    print(ufe(out))

def phase2():
    """Late-adjudicated take-side by DEEP ts evidence (first-pass TS_KEYS missed nested keys).

    Evidence (git show b4f036ac vs 3b738722):
    - dashboard_status.json meta.generated_at: bm-a 08:23:20 < bm-b 08:24:50 -> bm-b side (.js twin follows)
    - paper_export generated_from_state_updated: bm-a 08:23:08 < bm-b 08:24:42 -> bm-b side (both files)
    - daily_scorecard traders[*].forward_guard.as_of: bm-a 08:23:05 < bm-b 08:24:37 (ONLY diff) -> bm-b side
    """
    FIX = {
        'results/dashboard_status.json': 'theirs',
        'results/dashboard_status.js': 'theirs',
        'results/paper_export/export-2026-09-24.json': 'theirs',
        'results/paper_export/latest.json': 'theirs',
        'results/daily_scorecard.json': 'theirs',
    }
    for path, side in FIX.items():
        ref = '3b738722' if side == 'theirs' else 'b4f036ac'  # theirs = bm-b r311 original commit
        rc, out, _ = sh(['git', 'show', '%s:%s' % (ref, path)])
        assert rc == 0, 'blob missing: %s' % path
        if path.endswith('.js'):
            assert ufe(out).lstrip().startswith('window.DASH_DATA'), 'js wrapper stripped (R209)'
        else:
            json.loads(ufe(out))  # parse-validate (r185)
        with open(path, 'wb') as f:
            f.write(out)
        sh(['git', 'add', '--', path])
        print('phase2 fixed:', path, '->', side)


if __name__ == '__main__':
    if '--phase2' in sys.argv:
        phase2()
    else:
        main()
