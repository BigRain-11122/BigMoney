# -*- coding: utf-8 -*-
import io
t = io.open('results/_w264bmc_freeze_edits.py', encoding='utf-8', newline='').read()
lines = t.split('\n')
for i, ln in enumerate(lines):
    if any(x in ln for x in ['assert (a_lo, a_hi)', 'assert w263_total', 'len(owner_rows_live) == 253',
                             'range(245, 264)', 'range(211, 245)', 'm245 = re.search',
                             'w244_a = {A_SEED_BASE', 'RECEIPT_IN = ', 'SEAT_MSG = ', 'SEAT_ORIGIN = ']):
        print(f'L{i+1}| {ln.strip()[:170]}')
print('---')
print('seat_msg:', 'MSG-20261017-1950-bmc-w264-seat' in t)
print('seat_origin dd5fd438e:', t.count('dd5fd438e'))
print('own owner bm-c count:', t.count('"engine_owner": "bm-c"}'))
print('upstream owner bm-a count:', t.count('"bm-a"}'))
