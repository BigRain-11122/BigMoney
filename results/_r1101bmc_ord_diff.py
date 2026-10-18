# r1101 bm-c ORD boundary diff: find historical orders.md blob matching watermark d923d08918, diff vs fresh f99c9c6d
import subprocess, hashlib, json

GROUP = 'K:/Fluxgroup/FluxGroup'
WM_OLD = 'd923d08918d026de8db7d251f6b3a5aed93238df'
WM_NEW_EXPECT = 'f99c9c6d962eef6a023336e90c13242ba5a63feb'

def git(*args):
    return subprocess.check_output(['git', '-C', GROUP] + list(args))

fresh = git('show', 'origin/main:docs/orders.md')
sha_fresh = hashlib.sha1(fresh).hexdigest()
print('fresh sha1:', sha_fresh)
assert sha_fresh == WM_NEW_EXPECT, 'fresh drift: ' + sha_fresh

# walk history of docs/orders.md to find the old watermark version (content-bytes sha1 pin, r977)
commits = git('log', '--format=%H', '-n', '300', 'origin/main', '--', 'docs/orders.md').decode('utf-8', 'replace').split()
old = None
old_commit = None
for c in commits:
    blob = git('show', c + ':docs/orders.md')
    if hashlib.sha1(blob).hexdigest() == WM_OLD:
        old = blob
        old_commit = c
        break

assert old is not None, 'watermark blob not found in 300-commit history'
print('old blob found @ commit', old_commit[:9], 'len', len(old))

fl = fresh.split(b'\n')
ol = old.split(b'\n')
oset = set(ol)
new_rows = [l for l in fl if l not in oset and l.strip()]
print('=== NEW ROWS vs watermark %s (count=%d) ===' % (WM_OLD[:8], len(new_rows)))
for l in new_rows:
    print(l.decode('utf-8', 'replace'))
    print('---8<---')
print('len fresh', len(fresh), 'len old', len(old))

with open('results/_r1101bmc_ord_rows.json', 'w', encoding='utf-8') as f:
    json.dump({'old_commit': old_commit, 'fresh_sha1': sha_fresh,
               'new_rows': [l.decode('utf-8', 'replace') for l in new_rows]}, f, ensure_ascii=False, indent=1)
