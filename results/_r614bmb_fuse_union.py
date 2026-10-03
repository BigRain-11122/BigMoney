# r614 bm-b crash_fuse.json merge resolution: recursive 3-way dict union with
# ts-based newer-wins tie-break (pit-pool per-face law; take-origin tie pref).
import subprocess, json

def show(ref):
    r = subprocess.run(['git', 'show', ref], capture_output=True)
    assert r.returncode == 0, (ref, r.stderr[:200])
    return json.loads(r.stdout.decode('utf-8'))

mb = subprocess.run(['git', 'merge-base', 'HEAD', 'origin/main'],
                    capture_output=True, text=True).stdout.strip()
base = show(mb + ':results/crash_fuse.json')
mine = show('HEAD:results/crash_fuse.json')
theirs = show('origin/main:results/crash_fuse.json')

TS_FIELDS = ('last_crash_ts', 'cleared_ts', 'ts', 'updated', 'updated_at', 'last_refusal_ts')

def ts_of(v):
    best = None
    if isinstance(v, dict):
        for f in TS_FIELDS:
            t = v.get(f)
            if isinstance(t, str):
                if best is None or t > best:
                    best = t
        for vv in v.values():
            t = ts_of(vv)
            if t and (best is None or t > best):
                best = t
    return best

def merge3(b, m, t):
    if m == t:
        return m
    if b == m:
        return t
    if b == t:
        return m
    if isinstance(m, dict) and isinstance(t, dict):
        out = {}
        keys = sorted(set(m) | set(t) | (set(b) if isinstance(b, dict) else set()))
        for k in keys:
            out[k] = merge3(b.get(k) if isinstance(b, dict) else None,
                            m.get(k), t.get(k))
        return out
    # both sides changed differently -> newer-wins on ts, tie -> origin (shared-face authority)
    tm, tt = ts_of(m), ts_of(t)
    if tm and tt:
        return m if tm > tt else t
    if tm:
        return m
    if tt:
        return t
    return t  # no ts evidence: take-origin per r513 shared-face law

merged = merge3(base, mine, theirs)
with open('results/crash_fuse.json', 'w', encoding='utf-8', newline='\n') as f:
    json.dump(merged, f, ensure_ascii=False, indent=1)
    f.write('\n')
print('crash_fuse union OK: sigs=%d cleared=%d (mine sigs=%d theirs sigs=%d)'
      % (len(merged.get('sigs', {})), len(merged.get('cleared', {})),
         len(mine.get('sigs', {})), len(theirs.get('sigs', {}))))
