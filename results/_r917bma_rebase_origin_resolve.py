# -*- coding: utf-8 -*-
# r917 bm-a rebase onto origin/main: shared S6 face resolve (25 files, bm-c
# r806 same-day refresh vs r916 14:1x chain).
# Laws: jsonl = S2|S3 line-union zero-loss (r910); union-set json = dict-union
# (r914/r916); flat faces = newest content-ts wins (r915); parse-wins guard
# against PS UTF-16 artifact sides (r814/r828 pit family).
import json, subprocess

GIT = r'C:\Program Files\Git\cmd\git.exe'
MARKERS = ('<<<<<<<', '=======', '>>>>>>>')

DICT_UNION = {
    'results/runnable_pool.json',
    'results/compute_audit.json',
    'results/regime_state.json',
    'results/token_usage.json',
}
JSONL = {
    'results/x2_watch_log.jsonl',
}

FILES = [
    'docs/daily_report/REPORT-2026-10-09.json',
    'docs/daily_report/REPORT-2026-10-09.md',
    'docs/live_usage/LIVE-2026-10-09.json',
    'docs/live_usage/LIVE-2026-10-09.md',
    'docs/live_usage/LIVE-latest.json',
    'docs/live_usage/LIVE-latest.md',
    'results/_attrition_guard_scan.json',
    'results/compute_audit.json',
    'results/daily_scorecard.json',
    'results/dashboard_status.js',
    'results/dashboard_status.json',
    'results/fundamental_b_layer_filter.json',
    'results/futures_update_status.json',
    'results/lhb_update_status.json',
    'results/paper_export/export-2026-10-08.json',
    'results/paper_export/latest.json',
    'results/prospect_paper/_summary.json',
    'results/prospect_promotion/_summary.json',
    'results/regime_state.json',
    'results/runnable_pool.json',
    'results/scorecard_v1.json',
    'results/strategy_scorecard.json',
    'results/t35_open_fill_verify.json',
    'results/update_status.json',
    'results/x2_watch_log.jsonl',
]

def raw(stage, path):
    r = subprocess.run([GIT, 'show', ':%s:%s' % (stage, path)], capture_output=True)
    return r.stdout if r.returncode == 0 else b''

def parse(rawb):
    if not rawb:
        return None, None
    for enc in ('utf-8', 'utf-16'):
        try:
            return json.loads(rawb.decode(enc)), enc
        except Exception:
            pass
    try:
        return json.loads(rawb.decode('utf-8', 'replace')), 'replace'
    except Exception:
        return None, None

def ts_of(d):
    for k in ('ts', 'time', 'generated', 'generated_at', 'updated', 'asof', 'date', 'last_run'):
        v = (d or {}).get(k) if isinstance(d, dict) else None
        if isinstance(v, str) and v:
            return v
    return ''

def write_raw(path, rawb):
    open(path, 'wb').write(rawb)

def resolve_jsonl(path):
    seen, union = set(), []
    for stage in (2, 3):
        txt = raw(stage, path).decode('utf-8', 'replace')
        for ln in txt.splitlines():
            s = ln.strip()
            if s and s not in seen and not s.startswith(MARKERS):
                seen.add(s)
                union.append(s)
    def ts_key(s):
        d = None
        try:
            d = json.loads(s)
        except Exception:
            pass
        return ts_of(d)
    union.sort(key=ts_key)
    body = '\n'.join(union) + ('\n' if union else '')
    write_raw(path, body.encode('utf-8'))
    print('%s: line-union %d' % (path, len(union)))

def resolve_dict_union(path):
    a, ea = parse(raw(2, path))
    b, eb = parse(raw(3, path))
    if not isinstance(a, dict) or not isinstance(b, dict):
        resolve_flat(path)
        return
    merged = dict(b)
    merged.update(a)
    for k in set(a) & set(b):
        if isinstance(a[k], list) and isinstance(b[k], list):
            seen, u = set(), []
            for e in b[k] + a[k]:
                s = json.dumps(e, sort_keys=True, ensure_ascii=False)
                if s not in seen:
                    seen.add(s)
                    u.append(e)
            merged[k] = u
        elif isinstance(a[k], dict) and isinstance(b[k], dict):
            nm = dict(b[k])
            nm.update(a[k])
            merged[k] = nm
    body = json.dumps(merged, ensure_ascii=False, indent=1) + '\n'
    write_raw(path, body.encode('utf-8'))
    print('%s: dict-union %d top keys' % (path, len(merged)))

def resolve_flat(path):
    # stage 2 = ours = origin/main side; stage 3 = theirs = my r916 side
    ra, rb = raw(2, path), raw(3, path)
    da, ea = parse(ra)
    db, eb = parse(rb)
    if da is None and db is None:
        write_raw(path, rb if rb else ra)
        print('%s: neither parses, take theirs-bytes' % path)
        return
    if da is None:
        write_raw(path, rb); print('%s: theirs parses (ours artifact), theirs' % path); return
    if db is None:
        write_raw(path, ra); print('%s: ours parses (theirs artifact), ours' % path); return
    ta, tb = ts_of(da), ts_of(db)
    if ta >= tb:
        write_raw(path, ra); print('%s: ours newer ts=%s' % (path, ta[:19]))
    else:
        write_raw(path, rb); print('%s: theirs newer ts=%s' % (path, tb[:19]))

for p in FILES:
    if p in JSONL or p.endswith('.jsonl'):
        resolve_jsonl(p)
    elif p in DICT_UNION:
        resolve_dict_union(p)
    else:
        resolve_flat(p)

r = subprocess.run([GIT, 'add'] + FILES, capture_output=True)
assert r.returncode == 0, r.stderr.decode('utf-8', 'replace')[:300]
print('ALL %d shared faces resolved + staged' % len(FILES))
