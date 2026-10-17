# -*- coding: utf-8 -*-
import io
t = io.open('results/_w263bma_freeze_edits.py', encoding='utf-8', newline='').read()
lines = t.split('\n')
for i, ln in enumerate(lines):
    if 'r1037' in ln:
        print(f'L{i+1}|{ln.strip()[:180]}')
print('--- w244_a lines ---')
for i, ln in enumerate(lines):
    if 'w244_a' in ln or 'w244_b' in ln:
        print(f'L{i+1}|{ln.strip()[:150]}')
