# -*- coding: utf-8 -*-
import io
pf = io.open('scripts/perpetual_faces.py', encoding='utf-8', newline='').read()
n1 = io.open('scripts/perpetual_faces_n1.py', encoding='utf-8', newline='').read()
for a in ['    # W160 (bm-a r783 freeze', '160: {"a": (366_804', '160: {"batch"',
          '# --- W160 materializer face', '# --- T-141 s2 lane face']:
    print(repr(a), 'pf:', pf.count(a), 'n1:', n1.count(a))
for a in ['"+ W160 materializer face', '"r783 bm-a] "', '"r779 bm-a] "']:
    print(repr(a), 'n1:', n1.count(a))
