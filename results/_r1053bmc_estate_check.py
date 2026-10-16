# -*- coding: utf-8 -*-
# r1053 bm-c absorb-window estate check: W253 splice triple-identity + burn shards
import hashlib
import io
import json
import os
import subprocess

n1t = io.open('scripts/perpetual_faces_n1.py', encoding='utf-8').read()
i = n1t.find('253: {"batch": "PERPETUAL-N1-W253"')
print('w253_row_found', i >= 0)
seg = n1t[i:i + 9000] if i >= 0 else ''
if '254: {' in seg:
    seg = seg[:seg.find('254: {')]
for face in ['571901', '573901', 'n1_w253', 'n1_w253_results.json', 'engine_owner": "bm-c"']:
    print('face', face, face in seg)

r = subprocess.run(['git', 'show', 'c9b4fd855:scripts/perpetual_faces_n1.py'], capture_output=True)
landed = hashlib.sha256(r.stdout).hexdigest()[:16]
worktree = hashlib.sha256(io.open('scripts/perpetual_faces_n1.py', 'rb').read()).hexdigest()[:16]
r2 = subprocess.run(['git', 'show', 'HEAD:scripts/perpetual_faces_n1.py'], capture_output=True)
head_blob = hashlib.sha256(r2.stdout).hexdigest()[:16]
print('n1 landed_c9b4fd855', landed, 'worktree', worktree, 'HEAD', head_blob)
rpf = subprocess.run(['git', 'show', 'c9b4fd855:scripts/perpetual_faces.py'], capture_output=True)
pf_landed = hashlib.sha256(rpf.stdout).hexdigest()[:16]
pf_worktree = hashlib.sha256(io.open('scripts/perpetual_faces.py', 'rb').read()).hexdigest()[:16]
print('pf landed_c9b4fd855', pf_landed, 'worktree', pf_worktree)

fr = json.load(io.open('results/_w253bmc_freeze_receipt.json', encoding='utf-8'))
print('receipt_post n1', fr['n1_sha16_post'], 'pf', fr['pf_sha16_post'])

sd = 'results/p2cal_ext/n1_w253'
if os.path.isdir(sd):
    shards = sorted(f for f in os.listdir(sd) if f.startswith('shard-') and f.endswith('.json'))
    sizes = {f: os.path.getsize(os.path.join(sd, f)) for f in shards}
    print('shards', len(shards), 'all_above_100k', all(v > 100000 for v in sizes.values()))
    print('shard_sizes_tail', sorted(sizes.items())[-3:])
else:
    print('MISSING', sd)

m252 = n1t.find('252: {"batch": "PERPETUAL-N1-W252"')
w252_seg = n1t[m252:m252 + 8000] if m252 >= 0 else ''
if '253: {' in w252_seg:
    w252_seg = w252_seg[:w252_seg.find('253: {')]
print('w252_boundary_kept', m252 >= 0 and '569701' in w252_seg and '571701' in w252_seg)
print('w252_finalize_present', os.path.exists('results/perpetual_faces/n1_w252_results.json'))
print('w253_finalize_absent', not os.path.exists('results/perpetual_faces/n1_w253_results.json'))
