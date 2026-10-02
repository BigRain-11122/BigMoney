# -*- coding: utf-8 -*-
# r570 bm-a: read W69 finalize anchors + verify selftest leg anchor positions for W72 adaptation
import json, io

r = json.load(open('results/perpetual_faces/n1_w69_results.json', encoding='utf-8'))
out = io.StringIO()
keys = ['n_values', 'K', 'k_eff', 'n_eff', 'mu', 'sigma', 'mu_se', 'se_mu',
        'skill_line_v2', 'prev_skill_line_v2', 'k_lift', 'K_lift',
        'ledger_head', 'prev_total', 'batch_trials', 'evidence_cutoff']
for k in sorted(r.keys()):
    v = r[k]
    if isinstance(v, (int, float, str)):
        out.write('%s = %s\n' % (k, v))
# nested faces
for k in ('a_p95', 'p95', 'a_face', 'faces', 'a_family', 'A', 'a'):
    if k in r:
        out.write('NESTED %s = %s\n' % (k, json.dumps(r[k])[:400]))
open('results/_r570bma_w69_anchor.txt', 'w', encoding='utf-8').write(out.getvalue())

t = open('scripts/perpetual_faces_n1.py', encoding='utf-8').read()
pos = {}
for needle in ('W70 materializer face', 'W71 materializer face', 'T-141 s2 lane face',
               'W69 materializer face'):
    pos[needle] = t.count(needle)
# find order of legs: indexes
idx = []
for needle in ('--- W69 materializer face', '--- W70 materializer face', '--- W71 materializer face',
               '--- T-141 s2 lane face'):
    i = t.find(needle)
    idx.append((needle, i))
open('results/_r570bma_legpos.txt', 'w', encoding='utf-8').write(
    json.dumps({'counts': pos, 'first_idx': idx}, ensure_ascii=False, indent=1))
print('done')
