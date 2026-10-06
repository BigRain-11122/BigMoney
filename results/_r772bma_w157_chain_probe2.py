# -*- coding: utf-8 -*-
# r772 bm-a: full block structure map - first chain row, all assert rows, section boundaries
import io
import re

t = io.open(r'results/_r772bma_w157_src_block.txt', encoding='utf-8', newline='').read()
rows = [(m.start(), m.group(1)) for m in re.finditer(r'assert pf\.N1_BANDS\[(\d+)\]', t)]
print('all pf.N1_BANDS row asserts:', [(p, r) for p, r in rows])
first = rows[0][0]
print('--- first chain row head ---')
print(repr(t[first - 120:first + 120]))
wcfg = [(m.start(), m.group(1)) for m in re.finditer(r'assert WAVE_CONFIGS\[(\d+)\]', t)]
print('WAVE_CONFIGS self asserts:', wcfg)
# dep ranges
for m in re.finditer(r'range\((\d+), (\d+)\)', t):
    print('range:', m.group(0), 'at', m.start())
for m in re.finditer(r'if w < (\d+)', t):
    print('w <', m.group(1), 'at', m.start())
# the r768 cite in pre-chain narrative
for m in re.finditer(r'r768', t):
    print('r768 at', m.start(), repr(t[m.start() - 60:m.start() + 20]))
