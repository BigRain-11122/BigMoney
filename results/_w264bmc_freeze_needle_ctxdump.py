# -*- coding: utf-8 -*-
import io
t = io.open('results/_w263bma_freeze_edits.py', encoding='utf-8', newline='').read()
for tag, needle in [
 ('relkey_preD', 'W260_W261_W262_bands_respected'),
 ('gate05_owner_preD', 'W262.get("engine_owner")'),
 ('mirror_owner_preD', 'N1_BANDS[262].get("engine_owner")'),
 ('row263_fbrace', '263: {{"a"'),
 ('row262_fbrace', '262: {{"a"'),
 ('bm_a_q', '"bm-a"'), ('bm_c_q', '"bm-c"'),
 ('registered_selfburn', 'registered + self-burn 12/12 at publish'),
 ('registered_burned', 'registered + 12/12 burned at publish'),
 ('arith_define', 'arith_a263 = set(range'),
]:
    print(tag, t.count(needle))
print('---context lines---')
lines = t.split('\n')
seen = set()
for i, ln in enumerate(lines):
    for ph in ('PENDING at seat', 'waits-upstream face disclosed honest', '129 + candidate',
               'ONE HUNDRED AND THIRTIETH', '130th own', 'fifty-first', 'rows 252 + candidate',
               '252/129/82', 'owner_rows=252', 'bm-a rows 129', '262: {"a"'):
        if ph in ln:
            key = (ph, i)
            if key in seen:
                break
            seen.add(key)
            print(f'L{i+1}|{ph[:18]}|{ln.strip()[:170]}')
            break
