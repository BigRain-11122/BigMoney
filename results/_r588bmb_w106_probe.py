import os, glob, json, subprocess, re

print('W106 local shards:', len(glob.glob('results/p2cal_ext/n1_w106/shard-*.json')))
print('W106 finalize exists:', os.path.exists('results/perpetual_faces/n1_w106_results.json'))
print('W107 finalize exists:', os.path.exists('results/perpetual_faces/n1_w107_results.json'))
print('W108 finalize exists:', os.path.exists('results/perpetual_faces/n1_w108_results.json'))
print('W105 finalize exists (local):', os.path.exists('results/perpetual_faces/n1_w105_results.json'))
r = subprocess.run(['git', 'show', 'origin/main:results/perpetual_faces/n1_w105_results.json'], capture_output=True, text=True)
print('W105 on origin:', r.returncode == 0)
if r.returncode == 0:
    d = json.loads(r.stdout)
    print('W105 ledger head:', d['science_gates']['ledger']['total'], 'K:', d['null_pool_cumulative']['merged']['n_values'])

src = open('scripts/perpetual_faces_n1.py', encoding='utf-8').read()
idx = src.find("'n1_w106'")
if idx < 0:
    idx = src.find('n1_w106')
print('---W106 config snippet---')
print(src[idx-300:idx+500] if idx > 0 else 'not found')
