# r502: check docs/ tree in origin/main for decisions archive volume; verify BigMoney rows D-20261002-02/03 receipts state
import subprocess
HQ = r'K:\Fluxgroup\FluxGroup'
out = []
r = subprocess.run(['git', '-C', HQ, 'ls-tree', '--name-only', 'origin/main:docs'], capture_output=True)
out.append('--- docs/ tree ---')
out.append(r.stdout.decode('utf-8', 'replace'))
# does any file still mention D-20261002-02 principal / D-20261004-05?
r2 = subprocess.run(['git', '-C', HQ, 'grep', '-l', 'D-20261002-02', 'origin/main', '--', 'docs'], capture_output=True)
out.append('--- grep D-20261002-02 in docs ---')
out.append(r2.stdout.decode('utf-8', 'replace'))
r3 = subprocess.run(['git', '-C', HQ, 'grep', '-l', 'D-20261004-05', 'origin/main', '--', 'docs'], capture_output=True)
out.append('--- grep D-20261004-05 in docs ---')
out.append(r3.stdout.decode('utf-8', 'replace'))
open(r'K:\Fluxgroup\FluxGroup\quant\bigmoney\results\_r502bmc_docs_tree.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('ok')
