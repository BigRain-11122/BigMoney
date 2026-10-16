# -*- coding: utf-8 -*-
# r1046 bm-c: pre-author check -- N1_BANDS[250] live values + owner counts.
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from perpetual_faces import N1_BANDS

c250 = N1_BANDS[250]
print('W250 row:', {k: c250[k] for k in ('a', 'b_exit', 'engine_owner') if k in c250})
owner = [w for w, c in N1_BANDS.items() if c.get('engine_owner')]
print('owner rows:', len(owner))
for m in ('bm-a', 'bm-b', 'bm-c'):
    print(m, len([w for w, c in N1_BANDS.items() if c.get('engine_owner') == m]))
print('keys tail:', sorted(N1_BANDS)[-6:])
print('251 in N1_BANDS:', 251 in N1_BANDS)
w249 = N1_BANDS[249]
print('W249 row:', {k: w249[k] for k in ('a', 'b_exit', 'engine_owner') if k in w249})
