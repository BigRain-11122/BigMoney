# -*- coding: utf-8 -*-
# r1017 bm-a scratch: dump gen VMAP/CHAIN sha-variable roll entries
import io, re

src = io.open('results/_r1017bma_w246_gen.py', encoding='utf-8', newline='').read()
for m in re.finditer(r'\("[^"]*(?:prereg_sha|receipt_sha|freeze_sha)[^"]*",\s*"[^"]*"\)', src):
    print('SHA-ENTRY:', m.group(0)[:190])
print('--- w24x var rolls ---')
for m in re.finditer(r'\("w24\d_[a-z_]+",\s*"w24\d_[a-z_]+"\)', src):
    print('VAR:', m.group(0))
