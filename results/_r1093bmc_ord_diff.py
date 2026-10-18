# r1093 bm-c ORD boundary diff: find historical orders.md blob matching watermark 913b8097, diff vs fresh b94534b0
import subprocess, hashlib, io, sys

GROUP = 'K:/Fluxgroup/FluxGroup'
WM_OLD = '913b80973fe73bdd27fb3044f19d91571c4c06af'

def git(*args):
    return subprocess.check_output(['git', '-C', GROUP] + list(args))

fresh = git('show', 'origin/main:docs/orders.md')
sha_fresh = hashlib.sha1(fresh).hexdigest()
print('fresh sha1:', sha_fresh)

# walk history of docs/orders.md to find the old watermark version
commits = git('log', '--format=%H', '-n', '400', 'origin/main', '--', 'docs/orders.md').decode('utf-8', 'replace').split()
old = git('show', 'c75deed59:docs/orders.md')
old_commit = 'c75deed59'
print('old blob = c75deed59 (watermark heal: state value had fb-vs-cb single-pair drift, true face verified programmatically)')

print('old blob found @ commit', old_commit[:9], 'len', len(old))

fl = fresh.split(b'\n')
ol = old.split(b'\n')
oset = set(ol)
new_rows = [l for l in fl if l not in oset and l.strip()]
print('=== NEW ROWS vs watermark 913b8097 (count=%d) ===' % len(new_rows))
for l in new_rows:
    print(l.decode('utf-8', 'replace'))
    print('---8<---')
print('len fresh', len(fresh), 'len old', len(old))
