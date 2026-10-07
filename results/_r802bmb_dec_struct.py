import re, io, sys

d = open('results/_r802bmb_dec.md', encoding='utf-8', errors='replace').read()
lines = d.split('\n')
out = io.open('results/_r802bmb_dec_struct.txt', 'w', encoding='utf-8')
out.write('n_lines=%d\n' % len(lines))
out.write('--- HEAD 12 ---\n')
for l in lines[:12]:
    out.write(l[:150] + '\n')
out.write('--- ALL ## HEADINGS ---\n')
for l in lines:
    if l.startswith('#'):
        out.write(l[:150] + '\n')
out.write('--- BIGMONEY/quant/bm-b MENTIONS (last 40) ---\n')
hits = [l for l in lines if ('BigMoney' in l or 'bigmoney' in l or 'quant' in l.lower() or 'bm-b' in l)]
for l in hits[-40:]:
    out.write(l[:200] + '\n')
out.write('--- TAIL 30 ---\n')
for l in lines[-30:]:
    out.write(l[:150] + '\n')
out.close()
print('written, mentions=%d' % len(hits))
