# -*- coding: utf-8 -*-
# r1012 bm-a: extract W243-editor language template blocks (B assert face)
# for W245 gen NEW construction. Physical extraction, never transcribed.
import io
t = io.open('results/_w243bma_freeze_edits.py', encoding='utf-8').read()

i = t.find('assert WAVE_CONFIGS[243]["b_exit_seed_base"] == {b_lo}, (')
assert i >= 0, 'A9B anchor not found'
ls = t.rfind('\n', 0, i) + 1
seg = t[ls:].split('\n')[:22]
print('=== W243 B-assert block (22 lines) ===')
for j, l in enumerate(seg):
    print(j, l.encode('unicode_escape').decode('ascii')[:160])
