# r970 bm-b HANDOVER duty check: find bm-b r9xx rows in HANDOVER.md (binary read).
import re
BM = r'C:\Fluxgroup\FluxGroup\quant\bigmoney'
d = open(BM + r'\research\HANDOVER.md', 'rb').read()
hits = [m.start() for m in re.finditer(b'bm-b round 9', d)]
out = ['HITS=%d' % len(hits)]
for m in hits:
    seg = d[m:m+130].decode('utf-8', 'replace')
    out.append(seg.split('\n')[0][:115])
open(BM + r'\results\_r970bmb_ho_check.txt', 'w', encoding='utf-8', errors='replace').write('\n'.join(out))
print('WROTE', len(hits))
