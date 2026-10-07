import subprocess, json, io

ORIGIN = 'origin/main'
MY_DOCS = 'c52a7cf2e'      # my marker-fix commit (w3 chain 16:23 outputs)
MY_PICK3 = '71b40d82c'     # my round-1 pick-3 (16:14-15 chain faces, resolved union compute_audit)

def show(rev, path):
    r = subprocess.run(['git','show','%s:%s' % (rev, path)],capture_output=True)
    if r.returncode != 0 or not r.stdout:
        raise RuntimeError('show %s:%s failed: %s' % (rev, path, r.stderr[:150]))
    return r.stdout

def ts_of(b):
    try:
        j = json.loads(b.decode('utf-8', errors='replace'))
    except Exception:
        import re
        m = re.search(rb'"(?:ts|updated|generated_at|asof)"\s*:\s*"([^"]+)"', b)
        return m.group(1).decode() if m else None
    def find(d, depth=0):
        if depth > 4 or not isinstance(d, dict):
            return None
        for k in ('ts','updated','generated_at','asof','generated','now','time'):
            if isinstance(d.get(k), str):
                return d[k]
        for v in d.values():
            r = find(v, depth+1)
            if r:
                return r
        return None
    return find(j)

docs_faces = ['docs/daily_report/REPORT-2026-10-07.json','docs/daily_report/REPORT-2026-10-07.md',
              'docs/live_usage/LIVE-2026-10-07.json','docs/live_usage/LIVE-2026-10-07.md',
              'docs/live_usage/LIVE-latest.json','docs/live_usage/LIVE-latest.md',
              'results/dashboard_status.js','results/dashboard_status.json',
              'results/fundamental_b_layer_filter.json']
pick3_faces = ['results/futures_update_status.json','results/lhb_update_status.json',
               'results/regime_state.json','results/scorecard_v1.json',
               'results/strategy_scorecard.json','results/update_status.json']
log = []

for f in docs_faces:
    o = show(ORIGIN, f); m = show(MY_DOCS, f)
    to, tm = ts_of(o), ts_of(m)
    data = o if (to or '') >= (tm or '') else m
    with io.open(f,'wb') as fh:
        fh.write(data)
    log.append('%s -> %s (origin=%s mine=%s)' % (f, 'origin' if data is o else 'mine', to, tm))

for f in pick3_faces:
    o = show(ORIGIN, f); m = show(MY_PICK3, f)
    to, tm = ts_of(o), ts_of(m)
    data = o if (to or '') >= (tm or '') else m
    with io.open(f,'wb') as fh:
        fh.write(data)
    log.append('%s -> %s (origin=%s mine=%s)' % (f, 'origin' if data is o else 'mine', to, tm))

# compute_audit.json: latest ts-duel + history union
f = 'results/compute_audit.json'
o = json.loads(show(ORIGIN, f)); m = json.loads(show(MY_PICK3, f))
to, tm = o['latest']['ts'], m['latest']['ts']
base = o if to >= tm else m
seen = set(); rows = []
for r in o['history'] + m['history']:
    k = r.get('ts')
    if k in seen:
        continue
    seen.add(k); rows.append(r)
rows.sort(key=lambda r: r.get('ts',''))
merged = {'latest': base['latest'], 'history': rows[-201:]}
with io.open(f,'w',encoding='utf-8',newline='\n') as fh:
    json.dump(merged, fh, ensure_ascii=False, indent=1)
log.append('compute_audit.json -> latest=%s(%s/%s) history union %d+%d->%d' %
            ('origin' if base is o else 'mine', to, tm, len(o['history']), len(m['history']), len(merged['history'])))

# token_usage.json: keyed adaptive (machines union)
f = 'results/token_usage.json'
o = json.loads(show(ORIGIN, f)); m = json.loads(show(MY_DOCS, f))
merged = {}
for k in set(o) | set(m):
    if k in o and k in m and isinstance(o[k], dict) and isinstance(m[k], dict):
        sub = {}
        for kk in set(o[k]) | set(m[k]):
            if kk in o[k] and kk in m[k]:
                t1 = ts_of(json.dumps(o[k][kk]).encode()); t2 = ts_of(json.dumps(m[k][kk]).encode())
                sub[kk] = o[k][kk] if (t1 or '') >= (t2 or '') else m[k][kk]
            else:
                sub[kk] = o[k].get(kk, m[k].get(kk))
        merged[k] = sub
    elif k in o and k in m and isinstance(o[k], list) and isinstance(m[k], list):
        seen = set(); rr = []
        for r in o[k] + m[k]:
            key = json.dumps(r, sort_keys=True, ensure_ascii=False) if isinstance(r,(dict,list)) else str(r)
            if key in seen: continue
            seen.add(key); rr.append(r)
        merged[k] = rr
    elif k in o and k in m:
        t1 = ts_of(json.dumps(o[k]).encode()) if isinstance(o[k], dict) else None
        t2 = ts_of(json.dumps(m[k]).encode()) if isinstance(m[k], dict) else None
        merged[k] = o[k] if (t1 or '') >= (t2 or '') else m[k]
    else:
        merged[k] = o.get(k, m.get(k))
with io.open(f,'w',encoding='utf-8',newline='\n') as fh:
    json.dump(merged, fh, ensure_ascii=False, indent=1)
log.append('token_usage.json -> keyed merge %d keys (machines=%s)' %
           (len(merged), list(merged.get('machines', {}))[:6] if isinstance(merged.get('machines'), dict) else 'n/a'))

print('\n'.join(log))
print('FINAL-FIX-DONE')
