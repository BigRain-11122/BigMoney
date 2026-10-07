import subprocess, json, io, os, time

def side(stage, f, retries=8):
    for i in range(retries):
        r = subprocess.run(['git','show',stage+':'+f],capture_output=True)
        if r.returncode == 0 and r.stdout:
            return r.stdout
        time.sleep(0.4)
    raise RuntimeError('stage read failed %s%s: %s' % (stage, f, r.stderr[:150]))

files = subprocess.run(['git','diff','--name-only','--diff-filter=U'],capture_output=True,text=True).stdout.split()
print('UU:', len(files), files)

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
        for k in ('ts','updated','generated_at','asof','generated','now'):
            if isinstance(d.get(k), str):
                return d[k]
        for v in d.values():
            r = find(v, depth+1)
            if r:
                return r
        return None
    return find(j)

log = []
for f in files:
    o = side(':2:', f)  # upstream = origin (rebase orientation)
    m = side(':3:', f)  # my replayed commit
    if f == 'results/compute_audit.json':
        oj = json.loads(o.decode('utf-8')); mj = json.loads(m.decode('utf-8'))
        to, tm = oj['latest']['ts'], mj['latest']['ts']
        base_latest = oj if to >= tm else mj
        seen = set(); rows = []
        for r in oj['history'] + mj['history']:
            k = r.get('ts')
            if k in seen:
                continue
            seen.add(k); rows.append(r)
        rows.sort(key=lambda r: r.get('ts',''))
        merged = {'latest': base_latest, 'history': rows[-201:]}
        with io.open(f,'w',encoding='utf-8',newline='\n') as fh:
            json.dump(merged, fh, ensure_ascii=False, indent=1)
        log.append('%s -> latest=%s(%s) history union %d+%d->%d' % (f, 'origin' if base_latest is oj else 'mine', max(to,tm), len(oj['history']), len(mj['history']), len(merged['history'])))
        continue
    to, tm = ts_of(o), ts_of(m)
    if to and tm and to >= tm:
        data, w = o, 'origin-newer'
    else:
        data, w = m, 'mine-newer-or-nots'
    with io.open(f,'wb') as fh:
        fh.write(data)
    log.append('%s -> %s (origin=%s mine=%s)' % (f, w, to, tm))

print('\n'.join(log))
print('RESOLVED-OK')
