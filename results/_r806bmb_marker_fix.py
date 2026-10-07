import subprocess, json, io, os

H = 'd66d51ac6^'   # pick-3 result tree (HEAD side of the failed merge)
P = '2ffde7bde'    # original pick-4 commit (literal w3 chain outputs)

def blob(rev, f, retries=5):
    import time
    for i in range(retries):
        r = subprocess.run(['git','show','%s:%s' % (rev, f)],capture_output=True)
        if r.returncode == 0:
            return r.stdout
        time.sleep(0.5)
    raise RuntimeError('show %s:%s failed %s' % (rev, f, r.stderr[:150]))

def find_ts(obj, depth=0):
    if depth > 4 or not isinstance(obj, dict):
        return None
    for k in ('ts','updated','generated_at','asof','generated','now','report_ts','time'):
        v = obj.get(k)
        if isinstance(v, str):
            return v
    for v in obj.values():
        r = find_ts(v, depth+1)
        if r:
            return r
    return None

log = []

def fix_regen(f):
    h = blob(H, f); p = blob(P, f)
    try:
        th, tp = find_ts(json.loads(h.decode('utf-8',errors='replace'))), find_ts(json.loads(p.decode('utf-8',errors='replace')))
    except Exception:
        th = tp = None
    if th and tp and th > tp:
        data, w = h, 'H'
    else:
        data, w = p, 'P'
    with io.open(f,'wb') as fh:
        fh.write(data)
    log.append('%s -> %s (H=%s P=%s)' % (f, w, th, tp))

def fix_jsonl_union(f):
    def rows(txt):
        return [s for s in (ln.strip() for ln in txt.splitlines()) if s and not s.startswith(('<<<<<<<','=======','>>>>>>>'))]
    hr = rows(blob(H, f).decode('utf-8',errors='replace'))
    pr = rows(blob(P, f).decode('utf-8',errors='replace'))
    seen = set(); union = []
    for r in hr + pr:
        if r not in seen:
            seen.add(r); union.append(r)
    tail = 0
    if os.path.exists(f):
        for r in rows(io.open(f,encoding='utf-8',errors='replace').read()):
            if r not in seen:
                seen.add(r); union.append(r); tail += 1
    with io.open(f,'w',encoding='utf-8',newline='\n') as fh:
        fh.write('\n'.join(union) + ('\n' if union else ''))
    log.append('%s -> UNION H=%d P=%d -> %d (tail +%d)' % (f, len(hr), len(pr), len(union), tail))

def fix_token(f):
    h = json.loads(blob(H, f).decode('utf-8',errors='replace'))
    p = json.loads(blob(P, f).decode('utf-8',errors='replace'))
    merged = {}
    for k in set(h) | set(p):
        if k in h and k in p:
            if isinstance(h[k], dict) and isinstance(p[k], dict):
                sub = {}
                for kk in set(h[k]) | set(p[k]):
                    if kk in h[k] and kk in p[k]:
                        t1, t2 = find_ts(h[k][kk]), find_ts(p[k][kk])
                        sub[kk] = h[k][kk] if (t1 or '') >= (t2 or '') else p[k][kk]
                    else:
                        sub[kk] = h[k].get(kk, p[k].get(kk))
                merged[k] = sub
            elif isinstance(h[k], list) and isinstance(p[k], list):
                seen = set(); rows = []
                for r in h[k] + p[k]:
                    key = json.dumps(r, sort_keys=True, ensure_ascii=False) if isinstance(r,(dict,list)) else str(r)
                    if key in seen:
                        continue
                    seen.add(key); rows.append(r)
                merged[k] = rows
            else:
                t1, t2 = find_ts(h[k]) if isinstance(h[k],dict) else None, find_ts(p[k]) if isinstance(p[k],dict) else None
                merged[k] = h[k] if (t1 or '') >= (t2 or '') else p[k]
        else:
            merged[k] = h.get(k, p.get(k))
    with io.open(f,'w',encoding='utf-8',newline='\n') as fh:
        json.dump(merged, fh, ensure_ascii=False, indent=1)
    log.append('%s -> adaptive keyed/list merge (%d keys)' % (f, len(merged)))

for f in ['docs/daily_report/REPORT-2026-10-07.json','docs/daily_report/REPORT-2026-10-07.md',
          'docs/live_usage/LIVE-2026-10-07.json','docs/live_usage/LIVE-2026-10-07.md',
          'docs/live_usage/LIVE-latest.json','docs/live_usage/LIVE-latest.md',
          'results/dashboard_status.js','results/dashboard_status.json',
          'results/fundamental_b_layer_filter.json']:
    fix_regen(f)
fix_jsonl_union('results/fund_divlowvol_p1/nulls.jsonl')
fix_jsonl_union('results/saturation_engine/history_bm-b.jsonl')
fix_token('results/token_usage.json')

print('\n'.join(log))
print('FIX-DONE')
