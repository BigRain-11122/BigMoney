# r970 bm-b: extract the r965 HANDOVER entry (context around r911-r965 needle).
# Binary read. Output to file (GBK console law).
BM = r'C:\Fluxgroup\FluxGroup\quant\bigmoney'
d = open(BM + r'\research\HANDOVER.md', 'rb').read()
i = d.find(b'r911-r965')
seg = d[max(0, i - 400):i + 1400].decode('utf-8', 'replace')
open(BM + r'\results\_r970bmb_ho_r965_entry.txt', 'w', encoding='utf-8', errors='replace').write(seg)
print('WROTE', i)
