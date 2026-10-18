# -*- coding: utf-8 -*-
# r1086 bm-c: second-pass needle measurement (gaps from preflight pass 1)
import io
t = io.open('results/_w265bmc_freeze_edits_TOL.py', encoding='utf-8', newline='').read()
N = [
 'N1_BANDS[") == 122,', '!= 122', 'N1_BANDS[") == 53', 'N1_BANDS[") == 35',
 'N1_BANDS[") == 18', 'N1_BANDS[") == 69', 'N1_BANDS[") == 19',
 'thirty-five', 'thirty-six', 'fifty-three', 'fifty-four', 'eighteen',
 'block = 123 rows', '123 parity rows', '122 parity rows',
 'engine_owner==bm-c rows 83 + candidate',
 'EIGHTY-FOURTH owned per machine-derive', 'EIGHTY-FOURTH owned claim',
 "bm-a's EIGHTY-FOURTH", 'bma rows 129 + candidate 130th',
 'anchors W261 998,535 / K=572,120 at draft (W264 finalize pending',
 'bm-c r1038 splice window 216b578b0', '_w262bmc_freeze_edits.py template',
 'W265 block = 123 rows', 'W265 block parity = 121 rows',
 '123 rows (W138..W206 +', 'estate 69 rows (W138..W206 full-span',
 'the W265 seat was published AFTER',
 'five-face freeze (bm-c own seat executed at the bm-c r1076 splice window',
 'W265 block parity', 'block parity =', 'singles', 'dual-window parity',
 'W265 FREEZE UNBLOCKED', 'W266 FREEZE UNBLOCKED',
 'W265 = next free number', 'W266 = next free number',
 'post-W265 universe', 'post-W264 universe', 'post-W266 universe',
 'this freeze splice editor derived from the committed',
 'spliced W265', 'candidate bands treated as reserved refusers',
 'MUST re-derive', 'never transcribe', 'W265 walk', 'W266 walk',
 'w244_a holds wave-263 bands', 'w244_a holds wave-262 bands',
 'E63 heal lineage', 'arith define/assert consistent',
 'stale', 'one-behind',
]
for n in N:
    print('%4d  %r' % (t.count(n), n))
