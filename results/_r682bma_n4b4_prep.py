# -*- coding: utf-8 -*-
"""r682 bm-a N4-B4 prep probe: read n4 runner WAVE_CONFIGS (B1/B2/B3 rows),
probe seed logic, band-scan script anchors -- build the B4 adaptation faces."""
import sys, os
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

t = open(os.path.join(REPO, 'scripts/perpetual_faces_n4.py'), 'rb').read().decode('utf-8')
i = t.find('WAVE_CONFIGS')
print("=== WAVE_CONFIGS region (1800 chars):")
print(t[i:i+1800])
j = t.find('95_006')
print("=== probe seed region (600 chars around first 95_006):")
print(t[max(0,j-400):j+200])
k = t.find('def cmd_probe')
print("=== cmd_probe head (800 chars):")
print(t[k:k+800])
