# r970 bm-b: map the r965 HANDOVER entry extent + what follows, to locate the
# r970 append point. Binary read. Output to file (GBK console law).
BM = r'C:\Fluxgroup\FluxGroup\quant\bigmoney'
d = open(BM + r'\research\HANDOVER.md', 'rb').read()
i = d.find(b'round 965 bm-b')
n = len(d)
out = []
out.append('size=%d r965_at=%d tail_room=%d' % (n, i, n - i))
# show from r965 entry start to +6000 bytes, then the final 800 bytes of file
seg1 = d[i:i + 6000].decode('utf-8', 'replace')
out.append('--- R965 ENTRY (first 6000B) ---')
out.append(seg1)
out.append('--- FILE TAIL 800B ---')
out.append(d[-800:].decode('utf-8', 'replace'))
open(BM + r'\results\_r970bmb_ho_map.txt', 'w', encoding='utf-8', errors='replace').write('\n'.join(out))
print('WROTE')
