# -*- coding: utf-8 -*-
import subprocess, io, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
b = subprocess.run(['git','show','de4716da2:research/PERPETUAL_N1_W178_PREREG.md'],capture_output=True).stdout.decode('utf-8')
w179 = io.open(r'research/PERPETUAL_N1_W179_PREREG.md',encoding='utf-8',newline='').read()
KEYS = ('mu', 'sigma', 'p95', 'K-lift', 'n_eff', '0.31', '0.24', '1.18', '0.0004', '0.0003')
for tag, t in (('W178freeze', b), ('W179', w179)):
    for ln in t.splitlines():
        s = ln.strip()
        if any(k in s for k in KEYS) and len(s) > 40:
            print(tag, '|', s[:260])
    print('---8<---')
