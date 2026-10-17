# -*- coding: utf-8 -*-
import io
t = io.open('results/_w263bma_freeze_edits.py', encoding='utf-8', newline='').read()
total = 0
for i, ln in enumerate(t.split('\n')):
    c = ln.count('r1037')
    if c:
        total += c
        print(f'L{i+1} x{c} | {ln.strip()[:220]}')
print('TOTAL', total)
