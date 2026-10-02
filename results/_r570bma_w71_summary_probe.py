# -*- coding: utf-8 -*-
# r570 bm-a: find W71 SUMMARY segment tail (second occurrence of 'W71 materializer face')
import re
t = open('scripts/perpetual_faces_n1.py', encoding='utf-8').read()
idxs = [m.start() for m in re.finditer(re.escape('W71 materializer face'), t)]
print('occurrences:', idxs)
seg = t[idxs[1]-100:idxs[1]+2600]
open('results/_r570bma_w71_summary.txt', 'w', encoding='utf-8').write(seg)
