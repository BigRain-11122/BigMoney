# -*- coding: utf-8 -*-
"""r565 bm-a W62 derive probe: candidate bands + owned-count + anchor faces (machine-derived, no hand-copy)."""
import io, sys, json, os
sys.path.insert(0, r'scripts')
import perpetual_faces as pf

# candidate = arithmetic continuation from the W61 tail (W61 = bm-b, registered)
w61 = pf.N1_BANDS[61]
cand_a = (w61['a'][1] + 1, w61['a'][1] + 2000)
cand_b = (w61['b_exit'][1] + 1, w61['b_exit'][1] + 200)
print('W61 tail row:', w61)
print('W62 candidate A:', cand_a, '| B:', cand_b)
own = [w for w, c in pf.N1_BANDS.items() if c.get('engine_owner') == 'bm-a']
print('bm-a owned registered rows:', len(own), sorted(own))
print('W62 = bm-a owned #', len(own) + 1)
print('total engine waves after W62 lands:', len(pf.N1_BANDS) + 1)
# W62+ projection (for the canon warning row)
w62_a = (cand_a[1] + 1, cand_a[1] + 2000)
w62_b = (cand_b[1] + 1, cand_b[1] + 200)
print('W63+ projection A:', w62_a, '| B:', w62_b)
# landed anchor: W60 results ledger + pool projection
d = json.loads(io.open(r'results/perpetual_faces/n1_w60_results.json', encoding='utf-8').read())
print('W60 skill_line_v2_k_lift:', json.dumps(d['skill_line_v2_k_lift']))
nc = d['null_pool_cumulative']
print('merged n/mu/sigma:', nc['merged'])
print('W60-only mu/sigma:', nc['w60_only']['mu'], nc['w60_only']['sigma'])
fams = d['families']
for k in fams:
    print('family', k, 'p95:', fams[k].get('full_sharpe_p95'))
# W61 in-flight status on origin
import subprocess
out = subprocess.check_output(['git', 'ls-tree', 'origin/main', '--name-only',
                                'results/p2cal_ext/n1_w61/'], encoding='utf-8')
print('W61 shards on origin:', len([l for l in out.splitlines() if l.strip()]))
