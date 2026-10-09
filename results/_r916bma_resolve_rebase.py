# -*- coding: utf-8 -*-
# r916 bm-a rebase resolve: 12 shared live faces UU vs bm-c r805/806 S6 same-day
# refresh. Laws: jsonl = line-union zero-loss (r910 family); compute_audit
# history = entry-union zero-loss (r914 precedent); regime = dict union
# (r914); flat status/report faces = whole-file newest-ts wins (r915 daemon
# live-face law); fundamental mask = deterministic newest-wins.
import json, subprocess, sys

GIT = r'C:\Program Files\Git\cmd\git.exe'

UU = [
    "docs/daily_report/REPORT-2026-10-09.json",
    "docs/live_usage/LIVE-2026-10-09.json",
    "results/_attrition_guard_scan.json",
    "results/compute_audit.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/pool_core_samples.jsonl",
    "results/regime_state.json",
    "results/runnable_pool.json",
    "results/token_usage.json",
    "results/update_status.json",
]

def show(stage, path):
    r = subprocess.run([GIT, 'show', ':%s:%s' % (stage, path)],
                       capture_output=True)
    return r.stdout.decode('utf-8', 'replace') if r.returncode == 0 else None

def ts_of(obj):
    if isinstance(obj, dict):
        for k in ('ts', 'time', 'generated', 'updated', 'asof', 'date'):
            v = obj.get(k)
            if isinstance(v, str) and v:
                return v
    return ''

def try_json(text):
    try:
        return json.loads(text)
    except Exception:
        return None

def resolve_jsonl(path):
    ours = show(2, path) or ''
    theirs = show(3, path) or ''
    try:
        wt = open(path, encoding='utf-8').read()
    except Exception:
        wt = ''
    seen, union = set(), []
    for ln in (ours + '\n' + theirs + '\n' + wt).splitlines():
        s = ln.strip()
        if s and s not in seen:
            seen.add(s)
            union.append(s)
    def ts_key(s):
        d = try_json(s)
        return (d or {}).get('ts', '') or (d or {}).get('time', '') or ''
    union.sort(key=ts_key)
    open(path, 'w', encoding='utf-8', newline='').write(
        '\n'.join(union) + ('\n' if union else ''))
    print('%s: line-union %d (dedup zero-loss)' % (path, len(union)))

def resolve_flat(path):
    cands = []
    for txt in (show(2, path), show(3, path)):
        d = try_json(txt) if txt else None
        if d is not None:
            cands.append((ts_of(d), txt))
    if not cands:
        print('%s: no parsable candidate, take ours' % path)
        subprocess.run([GIT, 'checkout', '--ours', '--', path],
                       capture_output=True)
        return
    best_ts, best_txt = max(cands, key=lambda c: c[0])
    open(path, 'w', encoding='utf-8', newline='').write(best_txt)
    print('%s: newest-ts=%s wins' % (path, best_ts[:19] or 'n/a'))

def resolve_union_dict(path):
    a = try_json(show(2, path) or '') or {}
    b = try_json(show(3, path) or '') or {}
    if not isinstance(a, dict) or not isinstance(b, dict):
        resolve_flat(path)
        return
    merged = dict(b)
    merged.update(a)
    # nested history lists: entry-union by json identity
    for k in set(a) & set(b):
        if isinstance(a[k], list) and isinstance(b[k], list):
            seen, union = set(), []
            for e in b[k] + a[k]:
                s = json.dumps(e, sort_keys=True, ensure_ascii=False)
                if s not in seen:
                    seen.add(s)
                    union.append(e)
            merged[k] = union
        elif isinstance(a[k], dict) and isinstance(b[k], dict):
            nm = dict(b[k])
            nm.update(a[k])
            merged[k] = nm
    open(path, 'w', encoding='utf-8', newline='').write(
        json.dumps(merged, ensure_ascii=False, indent=1) + '\n')
    print('%s: dict-union (%d top keys, history lists entry-unioned)'
          % (path, len(merged)))

for p in UU:
    if p.endswith('.jsonl'):
        resolve_jsonl(p)
    elif p in ('results/compute_audit.json', 'results/regime_state.json',
               'results/runnable_pool.json', 'results/token_usage.json'):
        resolve_union_dict(p)
    else:
        resolve_flat(p)

r = subprocess.run([GIT, 'add'] + UU, capture_output=True)
assert r.returncode == 0, r.stderr.decode('utf-8', 'replace')[:200]
print('12 UU resolved + staged')
