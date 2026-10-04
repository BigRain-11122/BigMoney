# r502: orders.md latest delta check (fast-moving HQ face) - ensure no new BigMoney rows
import subprocess
HQ = r'K:\Fluxgroup\FluxGroup'
out = []
r = subprocess.run(['git', '-C', HQ, 'log', '--format=%h %ci %s', '-3', 'origin/main', '--', 'docs/orders.md'], capture_output=True)
out.append(r.stdout.decode('utf-8', 'replace'))
# newest two versions delta
r2 = subprocess.run(['git', '-C', HQ, 'log', '--format=%H', '-2', 'origin/main', '--', 'docs/orders.md'], capture_output=True)
shas = r2.stdout.decode().split()
if len(shas) >= 2:
    r3 = subprocess.run(['git', '-C', HQ, 'diff', shas[1] + '..' + shas[0], '--', 'docs/orders.md'], capture_output=True)
    d = r3.stdout.decode('utf-8', 'replace')
    out.append('--- delta %s..%s ---' % (shas[1][:9], shas[0][:9]))
    added = [l for l in d.splitlines() if l.startswith('+') and not l.startswith('+++')]
    out.extend(added[-10:])
open(r'K:\Fluxgroup\FluxGroup\quant\bigmoney\results\_r502bmc_ord_latest.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('written; added_lines=%d' % len([l for l in out if l.startswith('+')]))
