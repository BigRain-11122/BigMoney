# r503 bm-c: orders delta #2 consumption (F06E044F -> 3BF0F16E)
import subprocess, hashlib, difflib
HQ = r'K:\Fluxgroup\FluxGroup'
REPO = r'K:\Fluxgroup\FluxGroup\quant\bigmoney'
f = subprocess.run(['git', '-C', HQ, 'fetch', 'origin'], capture_output=True)
r = subprocess.run(['git', '-C', HQ, 'show', 'origin/main:docs/orders.md'], capture_output=True)
assert r.returncode == 0, r.stderr.decode('utf-8', 'replace')[:300]
b = r.stdout
cur = b.decode('utf-8', 'replace')
sha = hashlib.sha1(b).hexdigest().upper()
prev = open(REPO + r'\results\_r503bmc_ord_latest.txt', encoding='utf-8').read()
open(REPO + r'\results\_r503bmc_ord_latest2.txt', 'w', encoding='utf-8').write(cur)
diff = list(difflib.unified_diff(prev.splitlines(), cur.splitlines(), lineterm='', n=0))
print('group_orders_sha1=%s diff_lines=%d' % (sha, len(diff)))
for l in diff:
    print(l[:260])
