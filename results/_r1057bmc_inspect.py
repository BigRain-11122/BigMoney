# -*- coding: utf-8 -*-
# r1057 bm-c scratch: inspect W254 freeze-edits script structure (write targets + header) for the W255 editor derive.
import io, re
t = io.open(r'results\_w254bmc_freeze_edits.py', encoding='utf-8').read()
for m in sorted(set(re.findall(r'"([A-Za-z0-9_/.]+\.[a-z]{2,4})"', t))):
    print(m)
print('----write-face context----')
for m in re.finditer(r'io\.open\(([^\n]{0,120})', t):
    print(m.group(1)[:120])
print('----HEADER-70----')
print(chr(10).join(t.split(chr(10))[:70]))
