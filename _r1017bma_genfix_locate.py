# -*- coding: utf-8 -*-
# r1017 bm-a scratch: locate edit points in the W246 generator (fix floors after dead-window mismatch)
import io, re

t = io.open('results/_r1017bma_w246_gen.py', encoding='utf-8', newline='').read()
pats = [
    'r1010, queue-depth',
    'derived by the absorbed r1010 window and landed',
    '"gap face seventh consecutive": 6',
    'W232..W244 legs 12',
    'AND the W232..W244 fresh legs',
]
for pat in pats:
    for m in re.finditer(re.escape(pat), t):
        ls = t.rfind('\n', 0, m.start()) + 1
        line = t[ls:t.find('\n', ls)]
        print('LINE@%d: %r' % (m.start(), line[:170]))
    print('---')
