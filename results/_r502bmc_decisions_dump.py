# r502 bm-c: dump new decisions.md rows not seen at old watermark 4E5BE321 (D-19 consume step)
import subprocess, sys
HQ = r'K:\Fluxgroup\FluxGroup'
r = subprocess.run(['git', '-C', HQ, 'show', 'origin/main:docs/decisions.md'], capture_output=True)
txt = r.stdout.decode('utf-8', 'replace')
open(r'K:\Fluxgroup\FluxGroup\quant\bigmoney\results\_r502bmc_decisions_full.txt', 'w', encoding='utf-8').write(txt)
lines = txt.splitlines()
# find all decision ids
import re
ids = [(i, l) for i, l in enumerate(lines) if re.match(r'.*D-2026100[34]-\d+', l)]
# print last 60 lines around the newest decisions and the dispatch board block
out = []
# show the last decision block: find last occurrence of a D- row then +5 lines
if ids:
    li = ids[-1][0]
    out.extend(lines[max(0, li - 3):min(len(lines), li + 8)])
out.append('=====TAIL=====')
out.extend(lines[-40:])
print('\n'.join(out))
