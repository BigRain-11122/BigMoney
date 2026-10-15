# -*- coding: utf-8 -*-
# r1017 bm-a scratch: compare W245 registered block assert-closer structure
import io

t = io.open('scripts/perpetual_faces_n1.py', encoding='utf-8', newline='').read()
lines = t.split('\n')
for needle, tag in (('WAVE_CONFIGS[245]', 'W245 a_seed'),
                    ('WAVE_CONFIGS[246]', 'W246 a_seed')):
    idx = [n for n, ln in enumerate(lines) if needle in ln and 'a_seed_base' in ln]
    print('=== %s hits: %s ===' % (tag, [n + 1 for n in idx]))
    if not idx:
        continue
    n = idx[0]
    for k in range(n - 2, n + 14):
        print('L%d: %r' % (k + 1, lines[k]))
