# -*- coding: utf-8 -*-
"""r565 bm-a W62 precheck: exact anchors in post-rebase tree + W61 leg/config/summary/canon verbatim."""
import io
t = io.open(r'scripts/perpetual_faces_n1.py', encoding='utf-8').read()
p = io.open(r'scripts/perpetual_faces.py', encoding='utf-8').read()
canon = io.open(r'research/PERPETUAL_FACES.md', encoding='utf-8').read()
a_pf = '    61: {"a": (165_004, 167_003), "b_exit": (48_401, 48_600),\n         "engine_owner": "bm-b"},\n}'
print('pf anchor count =', p.count(a_pf))
a_cfg = '"shard_subdir": "n1_w61", "out_name": "n1_w61_results.json",\n                            "engine_owner": "bm-b"},\n                       }'
print('cfg anchor count =', t.count(a_cfg))
a_sum = 'law sec.4 W61 row, r564 bm-b] "\n          "+ T-141 s2 '
print('summary anchor count =', t.count(a_sum))
a_leg = '\n    # --- T-141 s2 lane face (SATURATION_ENGINE_LAW sec.2 pre-claim'
print('leg anchor count =', t.count(a_leg))
a_canon = '\n- \u6bcf\u6ce2 finalize \u540e\uff1a`science_gates.append_ledger` \u843d\u884c'
print('canon anchor count =', canon.count(a_canon))
print('W61 legs count =', t.count('W61 materializer face'), '| W61 configs =', t.count('"batch": "PERPETUAL-N1-W61"'))
print('canon W61 row count =', canon.count('- N1 \u6ce261\uff08'))
i = t.find('61: {"batch": "PERPETUAL-N1-W61"')
print('--- W61 WAVE_CONFIGS entry verbatim ---')
print(t[i:i + 1500])
