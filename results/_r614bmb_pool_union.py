# r614 bm-b generic shared-pool-face 3-way union (newer-wins, monotonic):
# runnable_pool.json / crash_fuse.json / pool lane mirrors -- MSG-0612 law.
# Lists of dicts matched by id/shard/key; ts fields drive newer-wins; ties take origin.
import subprocess, json, sys

PATH = sys.argv[1] if len(sys.argv) > 1 else 'results/runnable_pool.json'
TS_FIELDS = ('last_crash_ts', 'cleared_ts', 'owner_since', 'ts', 'updated',
             'updated_at', 'last_refusal_ts', 'claimed_at', 'cleared_at')
ID_KEYS = ('id', 'shard', 'key', 'name')

def show(ref):
    r = subprocess.run(['git', 'show', ref], capture_output=True)
    assert r.returncode == 0, (ref, r.stderr[:200])
    return json.loads(r.stdout.decode('utf-8'))

def ts_of(v):
    best = None
    if isinstance(v, dict):
        for f in TS_FIELDS:
            t = v.get(f)
            if isinstance(t, str) and (best is None or t > best):
                best = t
        for vv in v.values():
            t = ts_of(vv)
            if t and (best is None or t > best):
                best = t
    elif isinstance(v, list):
        for vv in v:
            t = ts_of(vv)
            if t and (best is None or t > best):
                best = t
    return best

def list_key(items):
    for k in ID_KEYS:
        if items and all(isinstance(x, dict) and k in x for x in items):
            return k
    return None

def merge3(b, m, t):
    if m == t:
        return m
    if b == m:
        return t
    if b == t:
        return m
    if isinstance(m, dict) and isinstance(t, dict):
        out = {}
        for k in sorted(set(m) | set(t) | (set(b) if isinstance(b, dict) else set())):
            out[k] = merge3(b.get(k) if isinstance(b, dict) else None,
                            m.get(k), t.get(k))
        return out
    if isinstance(m, list) and isinstance(t, list):
        k = list_key(m + t)
        if k:
            idx_b = {x[k]: x for x in b} if isinstance(b, list) else {}
            idx_m = {x[k]: x for x in m}
            idx_t = {x[k]: x for x in t}
            out = []
            for kk in sorted(set(idx_m) | set(idx_t)):
                out.append(merge3(idx_b.get(kk), idx_m.get(kk), idx_t.get(kk)))
            return out
        # non-id lists: newer side wins
        tm, tt = ts_of(m), ts_of(t)
        if tm and tt:
            return m if tm > tt else t
        return t if len(t) >= len(m) else m
    tm, tt = ts_of(m), ts_of(t)
    if tm and tt:
        return m if tm > tt else t
    if tm:
        return m
    if tt:
        return t
    return t

mb = subprocess.run(['git', 'merge-base', 'HEAD', 'origin/main'],
                    capture_output=True, text=True).stdout.strip()
base = show(mb + ':' + PATH)
mine = show('HEAD:' + PATH)
theirs = show('origin/main:' + PATH)
merged = merge3(base, mine, theirs)
with open(PATH, 'w', encoding='utf-8', newline='\n') as f:
    json.dump(merged, f, ensure_ascii=False, indent=1)
    f.write('\n')
if isinstance(merged, list):
    print('%s union OK: %d entries (mine %d / theirs %d)'
          % (PATH, len(merged), len(mine), len(theirs)))
else:
    print('%s union OK: top keys %s' % (PATH, sorted(merged)[:6]))
