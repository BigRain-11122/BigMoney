# r503 bm-c: group orders face dump + delta vs r502 consumed state (C6F5CC90)
# r446 law: probe lands as file, zero python -c inline. Raw bytes via subprocess (r660).
import subprocess, hashlib
HQ = r'K:\Fluxgroup\FluxGroup\out'
HQ = r'K:\Fluxgroup\FluxGroup'
r = subprocess.run(['git', '-C', HQ, 'show', 'origin/main:docs/orders.md'], capture_output=True)
assert r.returncode == 0, r.stderr.decode('utf-8', 'replace')[:300]
b = r.stdout
txt = b.decode('utf-8', 'replace')
sha = hashlib.sha1(b).hexdigest().upper()
open(r'K:\Fluxgroup\FluxGroup\quant\bigmoney\results\_r503bmc_ord_latest.txt', 'w', encoding='utf-8').write(txt)
lines = txt.splitlines()
print('group_orders_sha1=%s lines=%d' % (sha, len(lines)))
# print rows mentioning BigMoney/quant/CEO todo physical-items section markers
for i, l in enumerate(lines):
    if ('BigMoney' in l or 'quant' in l or '量化' in l) and l.strip():
        print('%04d| %s' % (i, l[:200]))
