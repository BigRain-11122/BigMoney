# -*- coding: utf-8 -*-
# r772 bm-a: map all _set_wave(15x) + T-141 marker positions in n1.py
import io

n1 = io.open(r'scripts/perpetual_faces_n1.py', encoding='utf-8', newline='').read()
print('file chars =', len(n1))
import re
for m in re.finditer(re.escape('# --- T-141 s2 lane face'), n1):
    print('T-141 marker at', m.start())
for m in re.finditer(r'_set_wave\((15[0-9])\)', n1):
    print('_set_wave(' + m.group(1) + ') at', m.start())
for m in re.finditer(r'# --- W15[0-9] materializer face', n1):
    print('materializer marker at', m.start(), repr(n1[m.start():m.start() + 40]))
