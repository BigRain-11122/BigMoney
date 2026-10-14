# -*- coding: utf-8 -*-
import subprocess, json
G = r'C:\Program Files\Git\cmd\git.exe'
repo = r'K:\Fluxgroup\FluxGroup\quant\bigmoney'
f = 'results/token_usage.json'
for stage, label in [('2', 'origin/bm-b'), ('3', 'mine')]:
    r = subprocess.run([G, '-C', repo, 'show', ':%s:%s' % (stage, f)], capture_output=True)
    try:
        d = json.loads(r.stdout.decode('utf-8'))
        print(label, '| top keys:', sorted(d.keys())[:12])
        for k in ('ts', 'updated', 'today', 'total'):
            if k in d:
                print('   ', k, '=', str(d[k])[:100])
    except Exception as e:
        print(label, 'parse err', e, r.stdout[:120])
