# r502: locate decisions.md change between watermark 4E5BE321 (r501 22:59 MATCH) and current 937A373D
import subprocess
HQ = r'K:\Fluxgroup\FluxGroup'
out = []
r = subprocess.run(['git', '-C', HQ, 'log', '--oneline', '-8', 'origin/main', '--', 'docs/decisions.md'], capture_output=True)
out.append('--- log origin/main docs/decisions.md (last 8) ---')
out.append(r.stdout.decode('utf-8', 'replace'))
# show last commit that touched it
r2 = subprocess.run(['git', '-C', HQ, 'log', '--format=%H %ci %s', '-3', 'origin/main', '--', 'docs/decisions.md'], capture_output=True)
out.append(r2.stdout.decode('utf-8', 'replace'))
open(r'K:\Fluxgroup\FluxGroup\quant\bigmoney\results\_r502bmc_dec_hist.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('written')
