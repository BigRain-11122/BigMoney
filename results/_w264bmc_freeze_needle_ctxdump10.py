# -*- coding: utf-8 -*-
import io
t = io.open('results/_w263bma_freeze_edits.py', encoding='utf-8', newline='').read()
for i, ln in enumerate(t.split('\n')):
    if 'wave 263' in ln or 'wave 262' in ln:
        print(f'L{i+1} | {ln.strip()[:240]}')
