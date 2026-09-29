# r441 bm-a probe: extract 13 SURVIVE+D6-ACCEPT cells with key metrics from gate_timing_prescreen_a158.json
import json

d = json.load(open('results/gate_timing_prescreen_a158.json', encoding='utf-8'))
print('=== 13 SURVIVE+D6-ACCEPT cells ===')
for k, c in d['cells'].items():
    d6 = str(c.get('d6', ''))
    if c.get('verdict') == 'SURVIVE' and 'ACCEPT' in d6:
        oos = c.get('OOS', {})
        full = c.get('full', {})
        null = c.get('null', {})
        print(k)
        print('  oos_excess_vs_bh=%s oos_n=%s is_n=%s' % (c.get('oos_excess_vs_bh'), c.get('oos_n'), c.get('is_n')))
        print('  OOS:', {kk: (round(vv, 4) if isinstance(vv, float) else vv) for kk, vv in oos.items()})
        print('  full:', {kk: (round(vv, 4) if isinstance(vv, float) else vv) for kk, vv in full.items()})
        print('  null:', {kk: (round(vv, 4) if isinstance(vv, float) else vv) for kk, vv in null.items()})
        print('  d6:', d6, '| segments_oos:', c.get('segments_oos'))
print()
print('final_status values:', {})
from collections import Counter
print(Counter(str(c.get('final_status')) for c in d['cells'].values()))
