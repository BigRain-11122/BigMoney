# -*- coding: utf-8 -*-
import subprocess, re
G = r'C:\Program Files\Git\cmd\git.exe'
repo = r'K:\Fluxgroup\FluxGroup\quant\bigmoney'
files = ['results/_attrition_guard_scan.json', 'results/compute_audit.json', 'results/fundamental_b_layer_filter.json']
for f in files:
    for stage, label in [('2', 'origin/bm-b'), ('3', 'mine')]:
        r = subprocess.run([G, '-C', repo, 'show', ':%s:%s' % (stage, f)], capture_output=True)
        txt = r.stdout.decode('utf-8', errors='replace')
        m = re.search(r'"ts":\s*"([^"]+)"', txt)
        m2 = re.search(r'"machine":\s*"([^"]+)"', txt)
        print(f.split('/')[-1], '|', label, '| ts=', m.group(1) if m else '?', '| machine=', m2.group(1) if m2 else '-')
