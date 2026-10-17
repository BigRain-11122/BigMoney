# -*- coding: utf-8 -*-
import io, re
t = io.open('results/_w259bmc_freeze_edits.py', encoding='utf-8', newline='').read()
print('file size:', len(t))
# all w<N>_x style identifiers
ids = re.findall(r'\bw(2[0-9][0-9])_([a-z0-9_]+)\b', t)
from collections import Counter
c = Counter('%s_%s' % (a,b) for a,b in ids)
for k, v in sorted(c.items()):
    print(' ', k, 'x', v)
