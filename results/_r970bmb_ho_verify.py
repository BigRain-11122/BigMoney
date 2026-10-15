# r970 bm-b: verify r965 HANDOVER entry claim - local disk vs origin blob dual face.
# Binary reads only. Zero tree touch (origin consumption law). ASCII needles only.
import subprocess
BM = r'C:\Fluxgroup\FluxGroup\quant\bigmoney'
NO_WINDOW = 0x08000000

out = []
# face 1: local disk
d = open(BM + r'\research\HANDOVER.md', 'rb').read()
for needle in (b'round 965', b'r911-r965', b'bm-b round 9'):
    out.append('LOCAL %r -> %s' % (needle, str(d.count(needle))))
out.append('LOCAL size=%d' % len(d))

# face 2: origin blob (zero tree touch)
p = subprocess.run(['git', '-C', BM, 'show', 'origin/main:research/HANDOVER.md'],
                   capture_output=True, creationflags=NO_WINDOW, timeout=90)
od = p.stdout
for needle in (b'round 965', b'r911-r965', b'bm-b round 9'):
    out.append('ORIGIN %r -> %s' % (needle, str(od.count(needle))))
out.append('ORIGIN size=%d rc=%d' % (len(od), p.returncode))

open(BM + r'\results\_r970bmb_ho_verify.txt', 'w', encoding='utf-8', errors='replace').write('\n'.join(out))
print('WROTE')
