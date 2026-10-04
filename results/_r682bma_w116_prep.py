# -*- coding: utf-8 -*-
"""r682 bm-a W116 prep probe: read exact W115 WAVE_CONFIGS entry + N1_BANDS tail
rows + selftest SUMMARY anchor faces, to build precise freeze-edit anchors."""
import sys, os
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)
sys.path.insert(0, os.path.join(REPO, 'scripts'))
sys.path.insert(0, os.path.join(REPO, 'research'))

t = open(os.path.join(REPO, 'scripts/perpetual_faces_n1.py'), 'rb').read().decode('utf-8')
i = t.find('115: {"batch": "PERPETUAL-N1-W115"')
print("=== W115 WAVE_CONFIGS entry (verbatim 1000 chars):")
print(t[i:i+1000])
j = t.find('"law sec.4 W115 row, r384 bm-c] "')
print("=== SUMMARY anchor region (500 chars):")
print(t[j-200:j+120])

from perpetual_faces import N1_BANDS
print("=== N1_BANDS tail rows:")
for w in sorted(N1_BANDS)[-3:]:
    print(w, N1_BANDS[w])
owner_rows = [w for w in c for c in [N1_BANDS] if False]  # placeholder
own = sorted(N1_BANDS)
owners = {o: [w for w, c in N1_BANDS.items() if c.get('engine_owner') == o] for o in ('bm-a', 'bm-b', 'bm-c')}
print("total rows:", len(N1_BANDS), "| owner counts:", {k: len(v) for k, v in owners.items()})
print("bm-a owned:", owners['bm-a'])
