# -*- coding: utf-8 -*-
"""R265 bm-a S7 push-collision resolver (rebase face: :2=origin/bm-b new base, :3=bm-a replayed commit).

Recipes per bigmoney-conflict-resolve skill + r257/r258/r264 addendum precedents:
  rolling-ledger  compute_audit.json / regime_state.json  -> history/transitions union (ts-asc, content-dedupe, zero loss) + fields take-new by ts
  append-log      post_review.jsonl                        -> line-level union zero loss
  snapshot        *_status.json / scorecards / dashboard pair / daily_report pair / token_usage
                                                          -> take-new by ts probe (RECURSIVE two-level per r267 bm-b law), tie -> :2 (HEAD/origin side)
  js-wrapper      dashboard_status.js                      -> take-side whole bytes (R209)
  fail-closed     any file with no ts face on either side -> report UNKNOWN, do not write.

Parse-verify before write+add (r185). Bytes via subprocess capture only (r255 channel law).
"""
import json, subprocess, sys, io

FILES_UNION_LEDGER = {
    'results/compute_audit.json': 'history',
    'results/regime_state.json': None,   # transitions key probed dynamically
}
FILE_APPEND_LOG = ['results/post_review.jsonl']
FILE_SNAPSHOT = [
    'results/dashboard_status.json',
    'results/dashboard_status.js',
    'results/update_status.json',
    'results/futures_update_status.json',
    'results/heat_update_status.json',
    'results/lhb_update_status.json',
    'results/fundamental_b_layer_filter.json',
    'results/daily_scorecard.html',
    'results/daily_scorecard.json',
    'results/scorecard_v1.json',
    'results/strategy_scorecard.json',
    'results/token_usage.json',
    'docs/daily_report/REPORT-2026-09-26.json',
    'docs/daily_report/REPORT-2026-09-26.md',
    'results/post_review/REPORT-20260926.md',
]

def stage_bytes(path, stage):
    r = subprocess.run(['git', 'show', ':%d:%s' % (stage, path)], capture_output=True)
    if r.returncode != 0:
        raise RuntimeError('stage %d missing for %s: %s' % (stage, path, r.stderr[:200]))
    return r.stdout

def write_bytes(path, data):
    open(path, 'wb').write(data)

def probe_ts(obj, depth=0):
    """Recursive two-level ts probe (r267 bm-b law): flatten keys, take max over ts-like candidates."""
    cands = []
    def walk(x, d):
        if d > 2:
            return
        if isinstance(x, dict):
            for k, v in x.items():
                kl = str(k).lower()
                if isinstance(v, str) and any(t in kl for t in ('ts', 'time', 'date', 'generated', 'updated', 'as_of', 'written')) and len(v) >= 10:
                    cands.append(v)
                elif isinstance(v, (int, float)) and ('epoch' in kl or 'generated' in kl or 'updated' in kl):
                    cands.append(str(v))
                else:
                    walk(v, d + 1)
        elif isinstance(x, list):
            for e in x[:5]:
                walk(e, d + 1)
    walk(obj, 0)
    return max(cands) if cands else None

def json_load(b):
    return json.loads(b.decode('utf-8-sig'))

def resolve_ledger_union(path, ledger_key):
    a = json_load(stage_bytes(path, 2))   # origin/bm-b base side
    b = json_load(stage_bytes(path, 3))   # bm-a replay side
    if ledger_key is None:
        ledger_key = 'transitions' if 'transitions' in a or 'transitions' in b else 'history'
    la, lb = a.get(ledger_key, []), b.get(ledger_key, [])
    seen, union = set(), []
    for e in la + lb:
        key = json.dumps(e, ensure_ascii=False, sort_keys=True)
        if key not in seen:
            seen.add(key)
            union.append(e)
    def ts_of(e):
        if isinstance(e, dict):
            v = probe_ts(e, 1)
            if v:
                return v
        return ''
    union.sort(key=ts_of)
    out = dict(b)  # start from bm-a face
    out[ledger_key] = union
    ta, tb = probe_ts(a) or '', probe_ts(b) or ''
    src = 'bm-b(:2)' if (ta or '') >= (tb or '') and ta else 'bm-a(:3)'
    fields = {k: v for k, v in (a if src.startswith('bm-b') else b).items() if k != ledger_key}
    out.update(fields)
    out[ledger_key] = union
    txt = json.dumps(out, ensure_ascii=False, indent=1)
    if b'\r\n' in stage_bytes(path, 2)[:4000]:
        txt = txt.replace('\n', '\r\n')
    write_bytes(path, txt.encode('utf-8'))
    print('%s: union %d|%d -> %d rows zero-loss; fields take %s' % (path, len(la), len(lb), len(union), src))
    json.loads(open(path, 'rb').read().decode('utf-8-sig'))  # parse-verify

def resolve_append_log(path):
    a = stage_bytes(path, 2).decode('utf-8-sig').splitlines()
    b = stage_bytes(path, 3).decode('utf-8-sig').splitlines()
    seen, union = set(), []
    for ln in a + b:
        if ln.strip() and ln not in seen:
            seen.add(ln)
            union.append(ln)
    raw2 = stage_bytes(path, 2)
    eol = '\r\n' if b'\r\n' in raw2 else '\n'
    txt = eol.join(union) + (eol if raw2.endswith((b'\r\n', b'\n')) else '')
    write_bytes(path, txt.encode('utf-8'))
    for ln in union:
        if ln.strip():
            json.loads(ln)  # parse-verify each line
    print('%s: union %d|%d -> %d lines zero-loss' % (path, len(a), len(b), len(union)))

def resolve_snapshot(path):
    a_raw, b_raw = stage_bytes(path, 2), stage_bytes(path, 3)
    ta = tb = None
    if path.endswith('.js'):
        # js-wrapper: extract DASH_DATA json for ts probe only; take-side whole bytes
        def ts_js(raw):
            s = raw.decode('utf-8-sig', errors='replace')
            i = s.find('{')
            j = s.rfind('}')
            try:
                return probe_ts(json.loads(s[i:j + 1]))
            except Exception:
                return None
        ta, tb = ts_js(a_raw), ts_js(b_raw)
    elif path.endswith('.json'):
        try:
            ta = probe_ts(json_load(a_raw))
            tb = probe_ts(json_load(b_raw))
        except Exception:
            ta = tb = None
    if ta is None and tb is None and (path.endswith('.md') or path.endswith('.html')):
        # text-level fallback: max ISO-ish timestamp string in document = generation time face
        import re
        pat = re.compile(r'20\d\d-\d\d-\d\d[T ]\d\d:\d\d(?::\d\d)?')
        ma = pat.findall(a_raw.decode('utf-8-sig', errors='replace'))
        mb = pat.findall(b_raw.decode('utf-8-sig', errors='replace'))
        ta = max(ma) if ma else None
        tb = max(mb) if mb else None
    if ta is None and tb is None:
        print('%s: UNKNOWN (no ts face) -> skip, manual adjudication' % path)
        return False
    if (tb or '') > (ta or ''):
        take, side = b_raw, 'bm-a(:3)'
    else:
        take, side = a_raw, 'bm-b(:2) tie-or-newer' if (ta or '') >= (tb or '') else 'bm-b(:2)'
    write_bytes(path, take)
    if path.endswith('.json') and not path.endswith('REPORT-2026-09-26.json'):
        json.loads(take.decode('utf-8-sig'))  # parse-verify
    print('%s: take %s (ts %s vs %s)' % (path, side, ta, tb))
    return True

def main():
    ok = True
    for path, key in FILES_UNION_LEDGER.items():
        resolve_ledger_union(path, key)
    for path in FILE_APPEND_LOG:
        resolve_append_log(path)
    # daily_report pair: json twin governs, md same-side whole bytes (r242/r257 precedent)
    j = 'docs/daily_report/REPORT-2026-09-26.json'
    m = 'docs/daily_report/REPORT-2026-09-26.md'
    a_j, b_j = json_load(stage_bytes(j, 2)), json_load(stage_bytes(j, 3))
    ta, tb = probe_ts(a_j), probe_ts(b_j)
    side = 3 if (tb or '') > (ta or '') else 2
    write_bytes(j, stage_bytes(j, side))
    write_bytes(m, stage_bytes(m, side))
    json.loads(open(j, 'rb').read().decode('utf-8-sig'))
    print('%s + %s: pair take %s (generated %s vs %s)' % (j, m, ':2 bm-b' if side == 2 else ':3 bm-a', ta, tb))
    FILE_SNAPSHOT.remove(j); FILE_SNAPSHOT.remove(m)
    for path in FILE_SNAPSHOT:
        if not resolve_snapshot(path):
            ok = False
    print('RESOLVE %s' % ('OK' if ok else 'HAS-UNKNOWN'))
    return 0 if ok else 2

if __name__ == '__main__':
    sys.exit(main())
