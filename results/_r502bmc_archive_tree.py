# r502: check docs/_archive tree for decisions volume files (分卷 Step2 destination)
import subprocess
HQ = r'K:\Fluxgroup\FluxGroup'
out = []
r = subprocess.run(['git', '-C', HQ, 'ls-tree', '--name-only', '-r', 'origin/main:docs/_archive'], capture_output=True)
out.append('--- docs/_archive tree ---')
out.append(r.stdout.decode('utf-8', 'replace'))
# grep the archive for the BigMoney rows
for pat in ['D-20261004-02', 'D-20261004-05', 'D-20261003-04']:
    r2 = subprocess.run(['git', '-C', HQ, 'grep', '-l', pat, 'origin/main', '--', 'docs/_archive'], capture_output=True)
    out.append('--- grep %s in docs/_archive ---' % pat)
    out.append(r2.stdout.decode('utf-8', 'replace') or '(no hits)')
open(r'K:\Fluxgroup\FluxGroup\quant\bigmoney\results\_r502bmc_archive_tree.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('ok')
