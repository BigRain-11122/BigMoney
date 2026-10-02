# -*- coding: utf-8 -*-
# r570 bm-a: map the selftest leg region structure after W71 leg start
import re
t = open('scripts/perpetual_faces_n1.py', encoding='utf-8').read()
i71 = t.find('--- W71 materializer face')
# all 'finally:' and '_set_wave(' occurrences after i71, plus next '--- ' comment markers
pats = []
for m in re.finditer(r'finally:|_set_wave\(\d+\)|# --- [A-Z0-9]', t):
    if m.start() > i71:
        pats.append((m.start(), m.group(), t[m.start():m.start()+60].replace('\n', '\\n')))
    if len(pats) > 14:
        break
out = '\n'.join('%d | %s | %s' % p for p in pats)
open('results/_r570bma_after_w71.txt', 'w', encoding='utf-8').write(out)
print(out[:1500])
