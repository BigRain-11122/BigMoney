# -*- coding: utf-8 -*-
# r1086 bm-c: gap measure -- raw [265]-keyed literals in the W265 canon
import io
t = io.open('results/_w265bmc_freeze_edits_TOL.py', encoding='utf-8', newline='').read()
N = [
 'WAVE_CONFIGS[265]', 'N1_BANDS[265]', 'WAVE_CONFIGS[266]', 'N1_BANDS[266]',
 'WAVE_CONFIGS[265]["a_seed_base"]', 'WAVE_CONFIGS[265]["b_exit_seed_base"]',
 'N1_BANDS[264]', 'WAVE_CONFIGS[264]',
 'N1_BANDS[264].get("engine_owner")',
 '265: {"batch"', '265: {"a"', '"PERPETUAL-N1-W265-SHARD-0"',
 '_entry_shard_of(0, 12)', 'PERPETUAL-N1-W265-SHARD-11',
]
for n in N:
    print('%4d  %r' % (t.count(n), n))
