# r503 bm-c: post-restore decisions face dump + diff vs r502 937A373D face (consumed-set check)
# 75c14df 23:39:25 restored 06e9a1a-deleted faces -> decisions face flipped again. r502 lineage.
import subprocess, hashlib, difflib
HQ = r'K:\Fluxgroup\FluxGroup'
REPO = r'K:\Fluxgroup\FluxGroup\quant\bigmoney'
f = subprocess.run(['git', '-C', HQ, 'fetch', 'origin'], capture_output=True)
r = subprocess.run(['git', '-C', HQ, 'show', 'origin/main:docs/decisions.md'], capture_output=True)
assert r.returncode == 0, r.stderr.decode('utf-8', 'replace')[:300]
b = r.stdout
cur = b.decode('utf-8', 'replace')
sha = hashlib.sha256(b).hexdigest().upper()
open(REPO + r'\results\_r503bmc_dec_latest.txt', 'w', encoding='utf-8').write(cur)
prev = open(REPO + r'\results\_r502bmc_decisions_full.txt', encoding='utf-8').read()
diff = list(difflib.unified_diff(prev.splitlines(), cur.splitlines(), lineterm='', n=0))
print('decisions_sha256=%s' % sha)
print('diff_lines=%d' % len(diff))
for l in diff:
    print(l[:220])
