# -*- coding: utf-8 -*-
import io

n1n = io.open('scripts/perpetual_faces_n1.py', encoding='utf-8',
              newline='').read().replace('\r\n', '\n')
for tag, needle in (('cfg194', '194: {"batch"'),
                    ('cfg193', '193: {"batch"'),
                    ('cfg192', '192: {"batch"')):
    i = n1n.find(needle)
    print(tag, 'line repr:', repr(n1n[n1n.rfind('\n', 0, i) + 1:i + 40]))
c = n1n.find('"+ W194 materializer face')
print('claim194 line repr:', repr(n1n[n1n.rfind('\n', 0, c) + 1:c + 50]))
a = n1n.find('"+ T-141 s2 "')
print('t141 claim line repr:', repr(n1n[n1n.rfind('\n', 0, a) + 1:a + 40]))
# bytes between claim194 end and t141 claim start (should be 1 newline)
ce = n1n.find('"r905 bm-a] "', c) + len('"r905 bm-a] "')
print('between claim194-end and T141-claim:', repr(n1n[ce:a]))
