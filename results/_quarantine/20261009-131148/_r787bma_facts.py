# -*- coding: utf-8 -*-
import json, subprocess, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
r = json.load(open('results/perpetual_faces/n1_w161_results.json', encoding='utf-8'))
m = r['null_pool_cumulative']['merged']
print('W161 merged n_values:', m['n_values'])
out = subprocess.run(['python', '-c',
    'import sys; sys.path.insert(0, "research"); sys.path.insert(0, "."); '
    'from science_gates import ledger_head; print(ledger_head())'],
    capture_output=True)
print('ledger_head:', out.stdout.decode('utf-8', 'replace').strip())
sh = subprocess.run(['git', 'log', '--oneline', '-S', '161: {"a": (369_004',
                     '--', 'scripts/perpetual_faces.py'], capture_output=True)
print('W161 freeze commits:', sh.stdout.decode('utf-8', 'replace').strip())
