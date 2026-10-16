# -*- coding: utf-8 -*-
# r1046 bm-c heal check v6: enumerate ALL candidate heal faces (68/69 rolls)
# in the W250 block + whole file, to map the full disclosed heal delta.
import io

t = io.open('scripts/perpetual_faces_n1.py', encoding='utf-8').read()
hits = []
for idx, l in enumerate(t.splitlines()):
    if any(k in l for k in (' 68 ', ' 69 ', '68 +', '69 +', 'rows 68', 'rows 69',
                            '68th', '69th', 'SEVENTIETH')):
        hits.append(l.strip()[:200])
print('candidate faces:', len(hits))
for h in hits:
    print('  *', h)
