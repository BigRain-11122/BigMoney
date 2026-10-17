# -*- coding: utf-8 -*-
import hashlib, io, subprocess, re, os

n1t = io.open('scripts/perpetual_faces_n1.py', encoding='utf-8').read()
m251 = re.search(r'251: \{"batch": "PERPETUAL-N1-W251"', n1t)
m252 = re.search(r'252: \{"batch": "PERPETUAL-N1-W252"', n1t)
print('W251 row at:', m251.start() if m251 else None)
print('W252 row at:', m252.start() if m252 else None)

if m252:
    seg = n1t[m252.start():m252.start() + 9000]
    if '253: {' in seg:
        seg = seg[:seg.find('253: {')]
    probes = [
        '569701', '571701', 'n1_w252', 'n1_w252_results.json',
        'engine_owner": "bm-c"',
        'seed_admit_gate rc0 base=569701 span=2000 checked=2000 verdict=FREE',
        'seed_admit_gate rc0 base=571701 span=200 checked=200 verdict=FREE',
    ]
    for p in probes:
        print(repr(p[:46]), '->', p in seg)

if m251:
    seg251 = n1t[m251.start():m252.start()] if m252 else n1t[m251.start():m251.start() + 8000]
    print('W251 seg kept faces 567501/569501:', '567501' in seg251, '569501' in seg251)

h_now = hashlib.sha256(io.open('scripts/perpetual_faces_n1.py', 'rb').read()).hexdigest()[:16]
blob = subprocess.run(['git', 'show', 'e63561df3:scripts/perpetual_faces_n1.py'],
                       capture_output=True).stdout
h_land = hashlib.sha256(blob).hexdigest()[:16]
print('n1 worktree sha16:', h_now, '| landed e63561df3 sha16:', h_land, '| equal:', h_now == h_land)
print('W251 finalize product present:', os.path.exists('results/perpetual_faces/n1_w251_results.json'))
