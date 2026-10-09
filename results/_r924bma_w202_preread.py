# -*- coding: utf-8 -*-
import json, io, sys, re
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
d = json.load(io.open('results/perpetual_faces/n1_w201_results.json', encoding='utf-8'))
led = (d.get('science_gates') or {}).get('ledger') or {}
print('W201 ledger block:', json.dumps(led, ensure_ascii=False))
np = d.get('null_pool_cumulative') or {}
print('merged K:', np.get('merged', {}).get('n_values'), 'mu:', np.get('merged', {}).get('mu'))
sk = d.get('skill_line_v2_k_lift') or {}
print('skill:', sk.get('line_merged_440120'), 'n_eff:', sk.get('n_eff_held_equal'))
src = io.open('scripts/perpetual_faces.py', encoding='utf-8').read()
m = re.search(r'201: \{.*?"a": \((\d+), (\d+)\).*?"b_exit": \((\d+), (\d+)\)', src, re.S)
print('W201 registry row A/B:', m.groups() if m else 'NOT FOUND')
m2 = re.search(r'owner_rows.*?\n', '')
import research.perpetual_faces as pf
rows = [w for w, c in pf.N1_BANDS.items() if c.get('engine_owner')]
bma = [w for w, c in pf.N1_BANDS.items() if c.get('engine_owner') == 'bm-a']
print('owner_rows:', len(rows), 'bma_rows:', len(bma), 'keys tail:', sorted(pf.N1_BANDS)[-3:])
print('W201 A:', tuple(pf.N1_BANDS[201]['a']), 'B:', tuple(pf.N1_BANDS[201]['b_exit']))
print('W200 A:', tuple(pf.N1_BANDS[200]['a']), 'B:', tuple(pf.N1_BANDS[200]['b_exit']))
