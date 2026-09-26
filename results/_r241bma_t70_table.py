# -*- coding: utf-8 -*-
"""R241 T-70: A/B/C per-task gate comparison from ledger.jsonl."""
import io
import json

rows = [json.loads(l) for l in
        io.open('results/local_coding_pilot/ledger.jsonl', encoding='utf-8')
        if l.strip()]
ab = [r for r in rows if 'arm_A_cloud' in r]
cc = {r['task']: r for r in rows if r.get('arm') == 'C_selffix'}

apass, bpass, cpass = [], [], []
print('task | A(cloud) | B(single-shot) | C(self-fix loop)')
for r in ab:
    t = r['task']
    a = r['arm_A_cloud'].get('pass')
    b = r['arm_B_local'].get('pass')
    c = cc.get(t, {}).get('arm_C_selffix', {})
    cv = c.get('verdict')
    fr = c.get('fix_rounds')
    apass.append(a)
    bpass.append(b)
    if cv == 'PASS':
        cpass.append(t)
    print(f"{t} | {a} | {b} | {cv} @{fr}r")

print()
print('A gate pass:', sum(1 for x in apass if x), '/10')
print('B gate pass:', sum(1 for x in bpass if x), '/10')
print('C gate pass:', len(cpass), '/10 ->', sorted(cpass))
