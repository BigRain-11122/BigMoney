# -*- coding: utf-8 -*-
"""r587 bm-b W109 freeze anchor probe: extract the W108 freeze-face regions
written by bm-c r378 (pf row / n1 config / selftest leg / summary / canon row)
to derive exact pure-insertion anchors for the W109 freeze edits."""
import io, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

t = open('scripts/perpetual_faces.py', encoding='utf-8').read()
i = t.find('108: {"a"')
print('=== pf.py W108 row region (tail anchor candidates) ===')
print(t[i - 60:i + 520])
print()

t2 = open('scripts/perpetual_faces_n1.py', encoding='utf-8').read()
j = t2.find('108: {"batch"')
print('=== n1.py W108 config entry region ===')
print(t2[j - 40:j + 700])
print()

k = t2.find('W108 materializer face')
print('=== n1.py W108 selftest leg head ===')
print(t2[k - 120:k + 260])
print()
m = t2.find('+ W108 materializer face')
print('=== n1.py SUMMARY W108 segment ===')
print(t2[m - 120:m + 400])
print()
leg_anchor = t2.find('_set_wave(2)\n    # --- T-141 s2 lane face')
print('=== T-141 lane-face anchor present:', leg_anchor > 0, '@', leg_anchor)

t3 = open('research/PERPETUAL_FACES.md', encoding='utf-8').read()
n = t3.find('- N1 \u6ce2108\uff08')
print('=== canon W108 row (first 400 chars) ===')
print(t3[n:n + 400])
print()
p = t3.find('\n- \u6bcf\u6ce2 finalize \u540e\uff1a')
print('=== canon sec.5 anchor present:', p > 0, '@', p)
