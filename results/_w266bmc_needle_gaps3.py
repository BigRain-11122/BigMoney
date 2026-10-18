# -*- coding: utf-8 -*-
# r1086 bm-c: third-pass overlap adjudication (own-prefix vs legs-suffix)
import io
t = io.open('results/_w265bmc_freeze_edits_TOL.py', encoding='utf-8', newline='').read()
N = [
 'own W246..W263 legs (18)', 'own W246..W263', 'W246..W263 legs (18)',
 'W246..W263 eighteen legs', 'W246..W263',
 'W211..W245 legs (35)', 'keep W211..W245 verbatim (35 legs)',
 'W211..W245 thirty-five legs', 'W211..W245',
 'W211..W263 legs (53)', 'W211..W263 fifty-three legs', 'W211..W263',
 'W246..W264 legs (19', 'fresh W246..W264 legs (19',
 'W265 block parity = 121 rows', 'block parity = 121',
 'legs (18) are EXCLUDED', 'legs (18) are excluded',
 'own W246..W264', 'own W247..W264',
 'W264 block', 'W265 block', 'W265 block parity', 'OWN W264 block',
 'W263 legs', 'W264 legs', 'W265 legs',
 'post-W265-REGISTERED', 'post-W264-REGISTERED',
 'staircase-affects-A FIFTEENTH', 'SIXTEENTH consecutive above-own-A',
 'above-own-A', 'A-hop',
]
for n in N:
    print('%4d  %r' % (t.count(n), n))
