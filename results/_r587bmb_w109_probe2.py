# -*- coding: utf-8 -*-
"""r587 bm-b W109 freeze anchor probe 2: exact anchor texts."""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

t2 = open('scripts/perpetual_faces_n1.py', encoding='utf-8').read()
j = t2.find('"shard_subdir": "n1_w108"')
print('=== W108 config entry tail (300 chars) ===')
print(repr(t2[j:j + 300]))
print()
k = t2.find('    # --- T-141 s2 lane face')
print('=== T-141 region (W108 leg tail before it, 260 chars) ===')
print(repr(t2[k - 260:k + 80]))
print()
m = t2.find('+ W108 materializer face')
seg_end = t2.find('"+ T-141 s2 ', m)
print('=== SUMMARY W108 segment tail (300 chars) ===')
print(repr(t2[seg_end - 260:seg_end + 40]))
