import subprocess, json, io, os, time

ENV = {**os.environ, 'MSYS2_ARG_CONV_EXCL': '*'}

def side(stage, f, retries=6):
    for i in range(retries):
        r = subprocess.run(['git','show',stage+':'+f],capture_output=True, env=ENV)
        if r.returncode == 0 and r.stdout:
            return r.stdout
        time.sleep(0.4)
    raise RuntimeError('stage read failed %s%s: %s' % (stage, f, r.stderr[:150]))

uu = subprocess.run(['git','diff','--name-only','--diff-filter=U'],capture_output=True,text=True,env=ENV).stdout.split()
print('UU:', uu)

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

for f in uu:
    if f.endswith('.jsonl'):
        def rows(txt):
            return [s for s in (ln.strip() for ln in txt.splitlines())
                    if s and not s.startswith(('<<<<<<<','=======','>>>>>>>'))]
        o = rows(side(':2:', f).decode('utf-8',errors='replace'))
        m = rows(side(':3:', f).decode('utf-8',errors='replace'))
        seen = set(); u = []
        for r in o + m:
            if r not in seen:
                seen.add(r); u.append(r)
        with io.open(f,'w',encoding='utf-8',newline='\n') as fh:
            fh.write('\n'.join(u) + ('\n' if u else ''))
        print(f, '-> UNION', len(o), '+', len(m), '->', len(u))
    elif f in ('results/p1d_gates.json','results/token_usage.json','results/autofill_state.bm-b.json'):
        h = json.loads(side(':2:', f).decode('utf-8',errors='replace'))
        p = json.loads(side(':3:', f).decode('utf-8',errors='replace'))
        merged = {}
        for k in set(h) | set(p):
            if k in h and k in p and isinstance(h[k], dict) and isinstance(p[k], dict):
                sub = {}
                for kk in set(h[k]) | set(p[k]):
                    if kk in h[k] and kk in p[k]:
                        t1 = ts_of(json.dumps(h[k][kk]).encode()); t2 = ts_of(json.dumps(p[k][kk]).encode())
                        sub[kk] = h[k][kk] if (t1 or '') >= (t2 or '') else p[k][kk]
                    else:
                        sub[kk] = h[k].get(kk, p[k].get(kk))
                merged[k] = sub
            elif k in h and k in p and isinstance(h[k], list) and isinstance(p[k], list):
                seen = set(); rr = []
                for r in h[k] + p[k]:
                    key = json.dumps(r, sort_keys=True, ensure_ascii=False) if isinstance(r,(dict,list)) else str(r)
                    if key in seen: continue
                    seen.add(key); rr.append(r)
                merged[k] = rr
            elif k in h and k in p:
                t1 = ts_of(json.dumps(h[k]).encode()) if isinstance(h[k], dict) else None
                t2 = ts_of(json.dumps(p[k]).encode()) if isinstance(p[k], dict) else None
                merged[k] = h[k] if (t1 or '') >= (t2 or '') else p[k]
            else:
                merged[k] = h.get(k, p.get(k))
        with io.open(f,'w',encoding='utf-8',newline='\n') as fh:
            json.dump(merged, fh, ensure_ascii=False, indent=1)
        print(f, '-> keyed merge', len(merged), 'keys')
    else:
        o = side(':2:', f); m = side(':3:', f)
        to, tm = ts_of(o), ts_of(m)
        data = o if (to or '') >= (tm or '') else m
        with io.open(f,'wb') as fh:
            fh.write(data)
        print(f, '-> ts-duel', 'origin' if data is o else 'mine', '(o=%s m=%s)' % (to, tm))
print('RESOLVED-OK')
