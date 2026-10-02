# -*- coding: utf-8 -*-
# r570 bm-a: examine BOTH T-141 lane face comment occurrences (anchor disambiguation)
t = open('scripts/perpetual_faces_n1.py', encoding='utf-8').read()
import re
idxs = [m.start() for m in re.finditer(re.escape('# --- T-141 s2 lane face'), t)]
out = []
for n, i in enumerate(idxs):
    out.append('=== occurrence %d at %d ===' % (n, i))
    out.append(t[i-200:i+120].replace('\r', ''))
    out.append('')
open('results/_r570bma_t141_ctx.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('occurrences:', idxs)
