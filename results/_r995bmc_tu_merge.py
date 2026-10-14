# -*- coding: utf-8 -*-
"""token_usage.json conflict union-merge: per-machine sub-keys live-wins, shared scalars newer-wins."""
import subprocess, json
G = r'C:\Program Files\Git\cmd\git.exe'
repo = r'K:\Fluxgroup\FluxGroup\quant\bigmoney'
f = 'results/token_usage.json'
a = json.loads(subprocess.run([G, '-C', repo, 'show', ':2:' + f], capture_output=True).stdout.decode('utf-8'))
b = json.loads(subprocess.run([G, '-C', repo, 'show', ':3:' + f], capture_output=True).stdout.decode('utf-8'))
print('origin generated:', a.get('generated'), '| mine generated:', b.get('generated'))
ma, mb = a.get('machines', {}), b.get('machines', {})
print('origin machine keys:', sorted(ma.keys()), '| mine machine keys:', sorted(mb.keys()))
# union merge: machines dict = per-key live-wins by each machine sub-face 'generated'/ts
merged = dict(a)
newer = b
if str(b.get('generated', '')) >= str(a.get('generated', '')):
    for k in ('generated', 'method', 'order', 'delta_vs_prev', 'total_report_tokens_est',
              'total_state_tokens_est', 'per_round_context'):
        if k in b:
            merged[k] = b[k]
# machines: per-machine face, take whichever side has that machine's newer sub-face
mm = dict(ma)
for k, v in mb.items():
    if k not in mm or str(v.get('generated', '')) >= str(mm[k].get('generated', '')):
        mm[k] = v
merged['machines'] = mm
if 'l2_local_llm' in b:
    la, lb = a.get('l2_local_llm', {}), b.get('l2_local_llm', {})
    l2 = dict(la)
    for k, v in lb.items():
        if k not in l2 or str(v.get('generated', '')) >= str(l2[k].get('generated', '')) if isinstance(v, dict) else True:
            l2[k] = v
    merged['l2_local_llm'] = l2
out = json.dumps(merged, ensure_ascii=False, indent=1)
open(repo + '\\' + f, 'w', encoding='utf-8').write(out + '\n')
print('MERGED machines:', sorted(mm.keys()), '| generated ->', merged.get('generated'))
