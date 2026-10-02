# -*- coding: utf-8 -*-
"""r565 bm-a W62 derive probe 2: owner census (validate machine-derive convention)."""
import sys
sys.path.insert(0, r'scripts')
import perpetual_faces as pf
from collections import Counter
c = Counter(cfg.get('engine_owner') for cfg in pf.N1_BANDS.values())
print('owner census:', dict(c))
print('total rows:', len(pf.N1_BANDS))
