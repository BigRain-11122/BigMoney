# -*- coding: utf-8 -*-
# r1066 floor audit: parse VMAP_FLOORS from the derive script (ast, no import/run),
# count every floor key on the frozen W260 face T0, report all mismatches in one shot.
import io, ast
ROOT = r'K:\Fluxgroup\FluxGroup\quant\bigmoney'
SCRIPT = ROOT + r'\results\_w261bmc_prereg_derive.py'
T0P = ROOT + r'\results\_w261bmc_w260_frozen_face.txt'
src = io.open(SCRIPT, encoding='utf-8', newline='').read()
i = src.index('VMAP_FLOORS = {')
istart = i + len('VMAP_FLOORS = ')
j = src.index('\n}\n', i)          # dict closes at column 0; strings inside contain no braces/newlines
dtext = src[istart:j + 2]
floors = ast.literal_eval(dtext)
T0 = io.open(T0P, encoding='utf-8', newline='').read()
bad = []
for k, f in floors.items():
    c = T0.count(k)
    if f == 0:
        if c != 0:
            bad.append(('ZERO-PRESENT', k, c, f))
    elif c < f:
        bad.append(('UNDER', k, c, f))
rep = ROOT + r'\results\_r1066bmc_floor_audit.txt'
lines = ['total floors=%d mismatches=%d' % (len(floors), len(bad))]
for kind, k, c, f in bad:
    lines.append('%s needle=%r count=%d floor=%d' % (kind, k, c, f))
io.open(rep, 'w', encoding='utf-8', newline='').write('\n'.join(lines) + '\n')
print('AUDIT_DONE floors=%d mismatches=%d' % (len(floors), len(bad)))
for kind, k, c, f in bad:
    print('%s|%s|%d|%d' % (kind, k.encode('unicode_escape').decode('ascii'), c, f))
