# r970 bm-b HANDOVER 5x duty: extract r921-r970 report line heads (binary read,
# r962 law: no rewrite of round_reports.md). ASCII only. NO_WINDOW per U060.
import re

BM = r'C:\Fluxgroup\FluxGroup\quant\bigmoney'
data = open(BM + r'\logs\iteration-loop\round_reports.md', 'rb').read()
lines = data.split(b'\n')
pat = re.compile(rb'2026-10-1[45] \d{2}:\d{2} \| r9(2[1-9]|3\d|4\d|5\d|6\d|70) \|')
hits = [l for l in lines if pat.match(l)]
out = ['COUNT=%d' % len(hits)]
for l in hits:
    out.append(l[:180].decode('utf-8', 'replace'))
open(BM + r'\results\_r970bmb_ho_extract.txt', 'w', encoding='utf-8', errors='replace').write('\n'.join(out))
print('WROTE', len(hits))
