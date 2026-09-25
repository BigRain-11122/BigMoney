# -*- coding: utf-8 -*-
"""r224 probe: p1e check/finalize part-validation semantics (read-only)."""
import re

src = open('scripts/p1e_ic_batch.py', encoding='utf-8').read()
for fn in ('_thresholds', 'finalize', 'check'):
    i = src.find('def ' + fn)
    if i >= 0:
        print(src[i:i+1800])
        print('=' * 70)
