import subprocess, json, io, os

out = subprocess.run(['git','ls-files','-u'],capture_output=True,text=True).stdout
stages = {}
for ln in out.splitlines():
    parts = ln.split('\t')
    if len(parts) != 2:
        continue
    meta, path = parts
    mode, sha, stage = meta.split()
    stages.setdefault(path, {})[int(stage)] = sha

print('unmerged paths:', list(stages))

def blob(sha):
    r = subprocess.run(['git','cat-file','blob',sha],capture_output=True)
    if r.returncode != 0:
        raise RuntimeError('cat-file %s failed: %s' % (sha, r.stderr[:150]))
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
        for k in ('ts','updated','generated_at','asof','generated','now','time','heartbeat_epoch_utc'):
            if isinstance(d.get(k), str):
                return d[k]
        for v in d.values():
            r = find(v, depth+1)
            if r:
                return r
        return None
    return find(j)

def rows_clean(txt):
    return [s for s in (ln.strip() for ln in txt.splitlines())
            if s and not s.startswith(('<<<<<<<','=======','>>>>>>>'))]

for path, st in stages.items():
    if path.endswith('.jsonl'):
        o = rows_clean(blob(st[2]).decode('utf-8',errors='replace'))
        m = rows_clean(blob(st[3]).decode('utf-8',errors='replace'))
        seen = set(); u = []
        for r in o + m:
            if r not in seen:
                seen.add(r); u.append(r)
        tail = 0
        if os.path.exists(path):
            for r in rows_clean(io.open(path,encoding='utf-8',errors='replace').read()):
                if r not in seen:
                    seen.add(r); u.append(r); tail += 1
        with io.open(path,'w',encoding='utf-8',newline='\n') as fh:
            fh.write('\n'.join(u) + ('\n' if u else ''))
        print(path, '-> UNION o=%d m=%d -> %d (tail+%d)' % (len(o), len(m), len(u), tail))
        continue
    # json faces: bm-b-owned live faces prefer clean worktree (daemon live-wins)
    if os.path.exists(path):
        raw = io.open(path,encoding='utf-8',errors='replace').read()
        if '<<<<<<<' not in raw and '>>>>>>>' not in raw:
            try:
                json.loads(raw)
                print(path, '-> WORKTREE-LIVE (daemon rewrote clean, live-wins)')
                continue
            except Exception:
                pass
    o = blob(st[2]); m = blob(st[3])
    to, tm = ts_of(o), ts_of(m)
    data = o if (to or '') >= (tm or '') else m
    with io.open(path,'wb') as fh:
        fh.write(data)
    print(path, '-> ts-duel', 'origin' if data is o else 'mine', '(o=%s m=%s)' % (to, tm))
print('RESOLVED-OK')
