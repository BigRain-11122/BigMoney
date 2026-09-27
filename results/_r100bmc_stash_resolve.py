# r100 bm-c stash-pop autofill UU resolver: HEAD vs stash@{0} composite-key union, per-key fresher wins (r84/r91 law)
import subprocess, json, io

def blob(rev, path):
    r = subprocess.run(['git', 'show', rev + path], capture_output=True)
    assert r.returncode == 0, (rev, path, r.stderr[:200])
    return r.stdout

def ts_of(obj, keys=('ts', 'generated', 'updated', 'epoch', 'asof', 'last_tick', 'state')):
    best = None
    def walk(o):
        nonlocal best
        if isinstance(o, dict):
            for k, v in o.items():
                if isinstance(v, str):
                    for kk in keys:
                        if k.lower().startswith(kk):
                            if best is None or v > best[1]:
                                best = (k, v)
                walk(v)
        elif isinstance(o, list):
            for x in o:
                walk(x)
    walk(obj)
    return best[1] if best else None

p = 'results/autofill_state.json'
jo = json.loads(blob('HEAD:', p).decode('utf-8'))
jt = json.loads(blob("stash@{0}:", p).decode('utf-8'))  # inside python file, stash ref safe

mo = dict(jo)
detail = []
for k, v in jt.items():
    if k not in mo:
        mo[k] = v; detail.append((k, 'stash-only key added')); continue
    so, st = ts_of(mo[k]), ts_of(v)
    if st is not None and so is not None:
        if st > so:
            mo[k] = v; detail.append((k, 'stash fresher (%s > %s)' % (st, so)))
        else:
            detail.append((k, 'HEAD kept (%s >= %s)' % (so, st)))
    elif st is not None:
        mo[k] = v; detail.append((k, 'HEAD no-ts, stash has ts'))
    else:
        detail.append((k, 'stash no-ts, HEAD kept'))

io.open(p, 'wb').write(json.dumps(mo, ensure_ascii=False, indent=1).encode('utf-8') + b'\n')
for k, note in detail:
    print('%-24s %s' % (k, note))
print('keys merged=%d (HEAD %d / stash %d)' % (len(mo), len(jo), len(jt)))
print('STASH-POP RESOLVE DONE; next: git add results/autofill_state.json + git stash drop')
