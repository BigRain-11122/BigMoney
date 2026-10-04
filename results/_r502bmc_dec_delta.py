# r502: extract delta rows from 06e9a1a (53804aa -> 06e9a1a for docs/decisions.md)
import subprocess
HQ = r'K:\Fluxgroup\FluxGroup'
r = subprocess.run(['git', '-C', HQ, 'diff', '53804aa..06e9a1a', '--', 'docs/decisions.md'], capture_output=True)
txt = r.stdout.decode('utf-8', 'replace')
open(r'K:\Fluxgroup\FluxGroup\quant\bigmoney\results\_r502bmc_dec_delta.txt', 'w', encoding='utf-8').write(txt)
print('delta_bytes=%d' % len(txt))
r2 = subprocess.run(['git', '-C', HQ, 'diff', '53804aa..06e9a1a', '--stat'], capture_output=True)
open(r'K:\Fluxgroup\FluxGroup\quant\bigmoney\results\_r502bmc_dec_stat.txt', 'w', encoding='utf-8').write(r2.stdout.decode('utf-8', 'replace'))
print('stat written')
