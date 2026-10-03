"""r626 rebase conflict resolver (r467/r634 deep-ts-probe canon).

UU faces from replaying round-626 commit onto origin tip (bm-a r633 S6 mirror + bm-c r422 closeout):
- ts-bearing derived faces -> take newer side (ts probe, fallback theirs=my side)
- compute_audit.json -> history union zero-loss (dedupe by ts)
- x2_watch_log.jsonl -> line-level union (append-only jsonl)
Idempotent: safe to re-run.
"""
import json, subprocess, sys, io, datetime

TS_KEYS = ['ts', 'generated', 'generated_at', 'updated', 'updated_at', 'written_at', 'asof', 'last_run']

def side(path, n):
    r = subprocess.run(['git', 'show', f':{n}:{path}'], capture_output=True)
    if r.returncode != 0:
        return None
    return r.stdout

def ts_of(data):
    try:
        o = json.loads(data.decode('utf-8'))
    except Exception:
        return None
    if not isinstance(o, dict):
        return None
    for k in TS_KEYS:
        v = o.get(k)
        if isinstance(v, (int, float)) and v > 1e9:
            return float(v)
        if isinstance(v, str) and len(v) >= 10:
            try:
                return datetime.datetime.fromisoformat(v.replace('Z', '+00:00')).timestamp()
            except Exception:
                continue
    return None

def resolve(path):
    ours = side(path, 2)    # origin side (bm-a/bm-c)
    theirs = side(path, 3) # my replayed commit side
    if theirs is None and ours is None:
        return 'skip-missing'
    if theirs is None:
        return 'keep-ours(no theirs)'
    if ours is None:
        return 'take-theirs(no ours)'
    if path == 'results/compute_audit.json':
        a = json.loads(ours.decode('utf-8')); b = json.loads(theirs.decode('utf-8'))
        ha = a.get('history', []); hb = b.get('history', [])
        seen = {}; out = []
        for row in ha + hb:
            key = row.get('ts')
            if key in seen:
                continue
            seen[key] = True; out.append(row)
        out.sort(key=lambda r: r.get('ts', ''))
        # base face = theirs (my newer regen), history = union
        face = b
        face['history'] = out
        io.open(path, 'wb').write(json.dumps(face, ensure_ascii=False, indent=1).encode('utf-8'))
        return f'union-history {len(ha)}|{len(hb)}->{len(out)} face=theirs'
    if path.endswith('.jsonl'):
        la = [l for l in ours.decode('utf-8', 'replace').splitlines() if l.strip()]
        lb = [l for l in theirs.decode('utf-8', 'replace').splitlines() if l.strip()]
        seen = set(); out = []
        for l in la + lb:
            if l in seen:
                continue
            seen.add(l); out.append(l)
        io.open(path, 'wb').write(('\n'.join(out) + '\n').encode('utf-8'))
        return f'line-union {len(la)}|{len(lb)}->{len(out)}'
    ta, tb = ts_of(ours), ts_of(theirs)
    if ta is None and tb is None:
        winner = theirs
        return 'take-theirs(no-ts-both, my side later wall-clock)'
    if tb is None or (ta is not None and ta >= tb):
        winner = ours
        w = 'ours'
    else:
        winner = theirs
        w = 'theirs'
    io.open(path, 'wb').write(winner)
    return f'take-{w} (ours_ts={ta} theirs_ts={tb})'

def main():
    r = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True)
    files = [l[3:] for l in r.stdout.splitlines() if l[:2] == 'UU']
    for f in files:
        print(f'{f}: {resolve(f)}')

if __name__ == '__main__':
    main()
