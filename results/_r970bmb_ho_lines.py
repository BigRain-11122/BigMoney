# r970 bm-b: dump full r965 + r956/r957 (product rounds) report lines for HANDOVER
# duty verification (binary read, r962 law). ASCII script, output to file.
import re
BM = r'C:\Fluxgroup\FluxGroup\quant\bigmoney'
data = open(BM + r'\logs\iteration-loop\round_reports.md', 'rb').read()
lines = data.split(b'\n')
out = []
for l in lines:
    m = re.match(rb'2026-10-1[45] \d{2}:\d{2} \| (r9(?:6[0-5]|4[7-9]|5[0-6]|2\d|3\d|4[0-6])) \| ', l)
    if m:
        out.append(l.decode('utf-8', 'replace'))
open(BM + r'\results\_r970bmb_ho_lines.txt', 'w', encoding='utf-8', errors='replace').write('\n\n'.join(out))
print('WROTE', len(out))
