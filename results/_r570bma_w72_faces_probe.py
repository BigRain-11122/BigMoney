# -*- coding: utf-8 -*-
# r570 bm-a: probe bm-b's W72 registration faces for W73 freeze anchors
import io, re

canon = open('research/PERPETUAL_FACES.md', encoding='utf-8').read()
lines = canon.splitlines()
out = io.StringIO()
for i, l in enumerate(lines):
    if '- N1 波72（' in l:
        out.write('CANON W72 row line %d (len %d)\n' % (i, len(l)))
        out.write('HEAD: ' + l[:400] + '\n')
        out.write('TAIL: ' + l[-700:] + '\n')
pf = open('scripts/perpetual_faces.py', encoding='utf-8').read()
i = pf.find('72: {"a"')
out.write('\nPF W72 ROW:\n' + pf[i-80:i+200] + '\n')
n1 = open('scripts/perpetual_faces_n1.py', encoding='utf-8').read()
i = n1.find('72: {"batch": "PERPETUAL-N1-W72"')
j = n1.find('}', n1.find('engine_owner', i))
out.write('\nN1 WAVE_CONFIGS[72]:\n' + n1[i-30:j+2] + '\n')
# summary segment anchor: second occurrence of 'W72 materializer face'
idxs = [m.start() for m in re.finditer(re.escape('W72 materializer face'), n1)]
out.write('\nW72 face occurrences: %r\n' % idxs)
seg = n1[idxs[1]-100:idxs[1]+1600]
out.write('\nSUMMARY SEG:\n' + seg + '\n')
# count anchor for leg insert
out.write('\nT-141 lane-face indented anchor count: %d\n' % n1.count('\n    # --- T-141 s2 lane face'))
open('results/_r570bma_w72_faces.txt', 'w', encoding='utf-8').write(out.getvalue())
print('written')
