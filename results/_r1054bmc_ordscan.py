# r1054 bm-c ORD tail scan (GROUP repo face): rows since watermark e40ba851 (content-bytes sha1)
import subprocess, hashlib, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

GIT = r'C:\Program Files\Git\cmd\git.exe'
TREE = r'K:\Fluxgroup\FluxGroup'
CUR_WM = 'e40ba85142a2b4dc6bdadf541c9bca20be48add4'

def get_bytes(ref, path):
    r = subprocess.run([GIT, '-C', TREE, 'show', ref + ':' + path], capture_output=True)
    if r.returncode != 0:
        print('SHOW-FAIL', ref, path, r.stderr.decode('utf-8', 'replace')[:200]); sys.exit(2)
    return r.stdout

cur = get_bytes('origin/main', 'docs/orders.md')
cur_sha = hashlib.sha1(cur).hexdigest()
print('cur_orders_sha1:', cur_sha)

log = subprocess.run([GIT, '-C', TREE, 'log', '--format=%H', '-n', '60', 'origin/main', '--', 'docs/orders.md'],
                     capture_output=True).stdout.decode('utf-8', 'replace').split()
found = False
commits = []
for sha in log:
    b = get_bytes(sha, 'docs/orders.md')
    if hashlib.sha1(b).hexdigest() == CUR_WM:
        found = True
        break
    commits.append(sha)

print('watermark_commit_found:', found)
print('commits_with_new_rows:', len(commits))
if found and commits:
    wm = get_bytes(commits[-1], 'docs/orders.md')
    wm_lines = set(l.rstrip('\r') for l in wm.decode('utf-8', 'replace').splitlines())
    cur_lines = [l.rstrip('\r') for l in cur.decode('utf-8', 'replace').splitlines()]
    new_rows = [l for l in cur_lines if l not in wm_lines and l.strip()]
    print('--- NEW ROWS (%d) ---' % len(new_rows))
    for ln in new_rows:
        print(ln[:500])
else:
    text = cur.decode('utf-8', 'replace')
    tail = text.strip().splitlines()[-10:]
    print('--- TAIL 10 ROWS (fallback manual read) ---')
    for ln in tail:
        print(ln[:400])
