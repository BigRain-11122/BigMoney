import subprocess, json, io, os, time

def side(stage, f, retries=8):
    for i in range(retries):
        r = subprocess.run(['git','show',stage+':'+f],capture_output=True)
        if r.returncode == 0 and r.stdout:
            return r.stdout
        time.sleep(0.4)
    raise RuntimeError('stage read failed %s%s: %s' % (stage, f, r.stderr[:150]))

uu = subprocess.run(['git','diff','--name-only','--diff-filter=U'],capture_output=True,text=True).stdout.split()
print('UU count:', len(uu))

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

def union_rows(txt):
    return [s for s in (ln.strip() for ln in txt.splitlines())
            if s and not s.startswith(('<<<<<<<','=======','>>>>>>>'))]

def write_jsonl_union(f):
    o = union_rows(side(':2:', f).decode('utf-8',errors='replace'))
    m = union_rows(side(':3:', f).decode('utf-8',errors='replace'))
    seen = set(); u = []
    for r in o + m:
        if r not in seen:
            seen.add(r); u.append(r)
    tail = 0
    if os.path.exists(f):
        for r in union_rows(io.open(f,encoding='utf-8',errors='replace').read()):
            if r not in seen:
                seen.add(r); u.append(r); tail += 1
    with io.open(f,'w',encoding='utf-8',newline='\n') as fh:
        fh.write('\n'.join(u) + ('\n' if u else ''))
    print('%s -> UNION o=%d m=%d -> %d (tail+%d)' % (f, len(o), len(m), len(u), tail))

def write_ts_duel(f, prefer_origin_tie=False):
    o = side(':2:', f); m = side(':3:', f)
    to, tm = ts_of(o), ts_of(m)
    if to and tm and to >= tm:
        data, w = o, 'origin'
    elif to and tm and to < tm:
        data, w = m, 'mine'
    else:
        data, w = (o if prefer_origin_tie else m), 'tie'
    with io.open(f,'wb') as fh:
        fh.write(data)
    print('%s -> %s (origin=%s mine=%s)' % (f, w, to, tm))

def worktree_live_ok(f):
    if not os.path.exists(f):
        return False
    raw = io.open(f, encoding='utf-8', errors='replace').read()
    if '<<<<<<<' in raw or '>>>>>>>' in raw:
        return False
    try:
        json.loads(raw)
        return True
    except Exception:
        return False

log = []
for f in uu:
    if f.endswith('.jsonl'):
        write_jsonl_union(f)
    elif f in ('results/saturation_engine/face_bm-b.json','results/saturation_engine/state_bm-b.json'):
        if worktree_live_ok(f):
            print('%s -> WORKTREE-LIVE (sat daemon rewrote clean)' % f)
        else:
            write_ts_duel(f, prefer_origin_tie=False)
    elif f == 'results/p1d_gates.json' or f == 'results/token_usage.json':
        # keyed adaptive
        try:
            h = json.loads(side(':2:', f).decode('utf-8',errors='replace'))
            p = json.loads(side(':3:', f).decode('utf-8',errors='replace'))
        except Exception as e:
            print('%s -> json-decode issue %s, fallback ts-duel' % (f, str(e)[:50]))
            write_ts_duel(f)
            continue
        merged = {}
        for k in set(h) | set(p):
            if k in h and k in p and isinstance(h[k], dict) and isinstance(p[k], dict):
                sub = {}
                for kk in set(h[k]) | set(p[k]):
                    if kk in h[k] and kk in p[k]:
                        t1, t2 = ts_of(json.dumps(h[k][kk]).encode()), ts_of(json.dumps(p[k][kk]).encode())
                        sub[kk] = h[k][kk] if (t1 or '') >= (t2 or '') else p[k][kk]
                    else:
                        sub[kk] = h[k].get(kk, p[k].get(kk))
                merged[k] = sub
            elif k in h and k in p and isinstance(h[k], list) and isinstance(p[k], list):
                seen = set(); rows = []
                for r in h[k] + p[k]:
                    key = json.dumps(r, sort_keys=True, ensure_ascii=False) if isinstance(r,(dict,list)) else str(r)
                    if key in seen: continue
                    seen.add(key); rows.append(r)
                merged[k] = rows
            elif k in h and k in p:
                t1, t2 = ts_of(json.dumps(h[k]).encode()) if isinstance(h[k],(dict,)) else None, ts_of(json.dumps(p[k]).encode()) if isinstance(p[k],(dict,)) else None
                merged[k] = h[k] if (t1 or '') >= (t2 or '') else p[k]
            else:
                merged[k] = h.get(k, p.get(k))
        with io.open(f,'w',encoding='utf-8',newline='\n') as fh:
            json.dump(merged, fh, ensure_ascii=False, indent=1)
        print('%s -> keyed adaptive merge (%d keys)' % (f, len(merged)))
    else:
        write_ts_duel(f)
print('RESOLVED-OK')
