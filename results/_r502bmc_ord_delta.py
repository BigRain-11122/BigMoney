# r502: orders.md delta in 06e9a1a + current text of D-20261002-02/03 rows (canonical obligation source)
import subprocess
HQ = r'K:\Fluxgroup\FluxGroup'
out = []
r = subprocess.run(['git', '-C', HQ, 'diff', '53804aa..06e9a1a', '--', 'docs/orders.md'], capture_output=True)
out.append('--- orders.md delta 53804aa..06e9a1a ---')
out.append(r.stdout.decode('utf-8', 'replace'))
r2 = subprocess.run(['git', '-C', HQ, 'show', 'origin/main:docs/decisions.md'], capture_output=True)
txt = r2.stdout.decode('utf-8', 'replace')
lines = txt.splitlines()
for i, l in enumerate(lines):
    if 'D-20261002-02' in l or 'D-20261002-03' in l:
        out.append('--- line %d ---' % i)
        out.append(l)
open(r'K:\Fluxgroup\FluxGroup\quant\bigmoney\results\_r502bmc_ord_delta.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('ok')
