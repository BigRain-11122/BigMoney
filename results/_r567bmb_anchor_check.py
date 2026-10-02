src = open('scripts/perpetual_faces.py', encoding='utf-8').read()
n1 = open('scripts/perpetual_faces_n1.py', encoding='utf-8').read()
canon = open('research/PERPETUAL_FACES.md', encoding='utf-8').read()
A1 = '    66: {"a": (175_004, 177_003), "b_exit": (50_001, 50_200),'
A2 = '"shard_subdir": "n1_w66", "out_name": "n1_w66_results.json",'
A3 = '\n    # --- T-141 s2 lane face'
A5 = 'law sec.4 W66 row, r359 bm-c] "'
A4 = '\n- \u6bcf\u6ce2 finalize \u540e\uff1a'
print('pf W66 row anchor:', src.count(A1))
print('n1 W66 cfg tail anchor:', n1.count(A2))
print('T141 anchor count:', n1.count(A3))
print('W66 summary anchor (no leading spaces):', n1.count(A5))
print('canon anchor count:', canon.count(A4))
print('canon W67 absent:', '波67（' not in canon)
print('legs:', [(w, n1.count(f'W{w} materializer face')) for w in (59, 60, 61, 62, 63, 64, 65, 66)])
print('bm-b owned rows in N1_BANDS:')
import sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath('results/_x.py'))) if False else os.getcwd()
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
sys.path.insert(0, ROOT)
from perpetual_faces import N1_BANDS
print(sum(1 for c in N1_BANDS.values() if c.get('engine_owner') == 'bm-b'))
print('rows:', len(N1_BANDS), sorted(N1_BANDS)[-3:])
