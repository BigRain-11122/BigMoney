# -*- coding: utf-8 -*-
# r1093 bm-c: canon context grep for W269 editor phase-3 needle design
import io
t = io.open(r'results\_w268bmc_freeze_edits.py', encoding='utf-8', newline='').read()
lines = t.split('\n')
pats = ['legs', 'bands_respected', 'block parity', 'fresh_legs', '_BANDS[_', 'fullspan',
        'nineteen', 'twenty', 'range(2', 'if w <', ' - _lw', 'authored', '13:1x', '13:5x',
        '14:0x', '12:3x', 'cycle COMPLETE', 'R267', '_w ==', 'verified', 'BEFORE this freeze',
        'MSG-', 'first free number', 'engine_owner=bm-c', 'fifty', 'wave 268', 'wave": 267']
seen = set()
for i, ln in enumerate(lines, 1):
    for p in pats:
        if p in ln:
            key = (i)
            if key in seen:
                continue
            seen.add(key)
            print(f'L{i}: {ln.strip()[:210]}')
            break
