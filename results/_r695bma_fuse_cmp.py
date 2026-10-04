# r695 bm-a: compare local crash_fuse.json vs origin blob for merge strategy (r437 treadmill pre-align)
import json, subprocess, sys

def load_local():
    with open(r'results\crash_fuse.json', 'rb') as f:
        return json.loads(f.read().decode('utf-8'))

def load_origin():
    out = subprocess.run(['git', 'show', 'origin/main:results/crash_fuse.json'],
                         capture_output=True)
    if out.returncode != 0:
        print('ORIGIN_READ_FAIL', out.stderr.decode('utf-8', 'replace')[:200]); sys.exit(2)
    return json.loads(out.stdout.decode('utf-8'))

loc = load_local(); org = load_origin()
lk = set(loc.keys()); ok = set(org.keys())
print('keys_local_only:', sorted(lk - ok))
print('keys_origin_only:', sorted(ok - lk))
common_diff = []
for k in sorted(lk & ok):
    if loc[k] != org[k]:
        # summarize diff fields
        if isinstance(loc[k], dict) and isinstance(org[k], dict):
            fl = [f for f in set(loc[k]) | set(org[k]) if loc[k].get(f) != org[k].get(f)]
            common_diff.append((k, fl[:8]))
        else:
            common_diff.append((k, 'scalar-diff'))
print('common_keys_diff:')
for k, d in common_diff:
    print(' ', k, d)
print('PROBE_OK')
