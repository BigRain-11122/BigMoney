# -*- coding: utf-8 -*-
import io, os, re
t = io.open('scripts/perpetual_faces_n1.py', encoding='utf-8').read()
i = t.find('264: {"batch"')
seg = t[i:i+9000]
if '265: {' in seg:
    seg = seg[:seg.find('265: {')]
print('row_faces:', {'a596101': '596101' in seg, 'b598101': '598101' in seg,
                     'shard_n1_w264': 'n1_w264' in seg,
                     'out_n1_w264_results': 'n1_w264_results.json' in seg,
                     'owner_bm_c': 'engine_owner": "bm-c"' in seg})
print('fam:', {f: t.count(f) for f in ['base=596101 span=2000', 'base=598101 span=200']})
m263 = re.search(r'263: \{"batch"', t)
w263seg = t[m263.start():m263.start()+8000]
if '264: {' in w263seg:
    w263seg = w263seg[:w263seg.find('264: {')]
print('w263_boundary_593901_595901:', '593901' in w263seg, '595901' in w263seg)
sd = 'results/p2cal_ext/n1_w264'
sh = sorted(f for f in os.listdir(sd) if f.startswith('shard-'))
print('shards:', len(sh), 'sizes_ok:', all(os.path.getsize(os.path.join(sd, f)) > 100000 for f in sh))
print('w263_results_exists:', os.path.exists('results/perpetual_faces/n1_w263_results.json'))
print('w264_results_exists_pre_finalize:', os.path.exists('results/perpetual_faces/n1_w264_results.json'))
