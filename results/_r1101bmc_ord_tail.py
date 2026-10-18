# r1101 bm-c ORD tail extraction: blob matching consumed watermark f99c9c6d vs current origin
import subprocess, hashlib, json

GROUP = 'K:/Fluxgroup/FluxGroup'
WM_OLD = 'f99c9c6d962eef6a023336e90c13242ba5a63feb'

def git(*args):
    return subprocess.check_output(['git', '-C', GROUP] + list(args))

subprocess.run(['git', '-C', GROUP, 'fetch', 'origin'], capture_output=True)
fresh = git('show', 'origin/main:docs/orders.md')
sha_fresh = hashlib.sha1(fresh).hexdigest()
print('fresh sha1:', sha_fresh)

commits = git('log', '--format=%H', '-n', '60', 'origin/main', '--', 'docs/orders.md').decode('utf-8', 'replace').split()
old = None
old_commit = None
for c in commits:
    blob = git('show', c + ':docs/orders.md')
    if hashlib.sha1(blob).hexdigest() == WM_OLD:
        old = blob
        old_commit = c
        break

if old is None:
    print('NOTE: consumed watermark blob not in last 60 orders.md commits (orders-archive spillover); fallback = diff vs previous probe fresh dump')
    old = git('show', 'ff3bb2509:docs/orders.md')

fl = fresh.split(b'\n')
ol = old.split(b'\n')
oset = set(ol)
new_rows = [l for l in fl if l not in oset and l.strip()]
print('=== TAIL NEW ROWS vs watermark %s (count=%d) ===' % (WM_OLD[:8], len(new_rows)))
for l in new_rows:
    print(l.decode('utf-8', 'replace'))
    print('---8<---')
with open('results/_r1101bmc_ord_tail_rows.json', 'w', encoding='utf-8') as f:
    json.dump({'old_commit': old_commit, 'fresh_sha1': sha_fresh,
               'new_rows': [l.decode('utf-8', 'replace') for l in new_rows]}, f, ensure_ascii=False, indent=1)
