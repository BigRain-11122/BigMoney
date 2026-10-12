# -*- coding: utf-8 -*-
# r931 token count probe for the W222 editor transform table (read-only)
import io
t = io.open(r"results\_w221bmc_freeze_edits.py", encoding="utf-8").read()
toks = [
 'W221','W220','W219','W218','W217','W216',
 'w221','w220','w219','w218','w217','w216',
 'EIGHTY-FIRST','EIGHTY-SECOND','fifty-first','51st',
 'TWO HUNDRED AND TWENTY-FIRST','rows 50 + candidate','bmc_ordinal=51',
 '12:0x','907,789','481,920','907_789','481_920',
 '501_004, 503_003','503_004, 503_203',
 'MSG-20261012-1025','MSG-20261012-1225-bmc-w221-seat','063bb5a77',
 'r923 freeze window','r923 window editor','splice landed r923 window',
 'r921 seat window','r924 window','r924 seat-time',
 'r925 prereg derived + r927 freeze-window bundle','r927 freeze-window bundle',
 'r927 absorb window','tenth consecutive','repair-free chain',
 'arith_a221','arith_b221','n3r1_used221',
 '221: {"batch"','220: {"batch"','221: {"a"','220: {"a"',
 'N1_BANDS[221]','N1_BANDS[220]','N1_BANDS[219]','N1_BANDS\\[219\\]',
 'WAVE_CONFIGS[221]','WAVE_CONFIGS[220]',
 'range(17, 221)','range(16, 221)','w < 221','w < 220',
 '_set_wave(221)','"wave": 221','get(220)',
 '== 210 and len(bmc_rows_live) == 50','expect 210/50','precedent 209/49','splice 210/50',
 '"probe_receipt_bmc_ordinal_face": 51','w216_block_kept','907,789 / 481,920',
 'W211 + W212 + W213 + W214 + W215 + W216 + W217 + W218 legs',
 'W211 leg + W212 leg + W213 leg + W214 leg + W215 leg + W216 leg + W217 leg + W218 leg + W219 leg',
 'W211 leg + W212 leg + W213 leg + W214 leg + W215 leg + W216 leg + W217 leg + W218 leg + W219 leg + W220 leg',
 '[211, 212, 213, 214, 215, 216, 217, 218]',
 'int(_estate_ws[69]), int(_estate_ws[70]), int(_estate_ws[71]), int(_estate_ws[72]), int(_estate_ws[73]), int(_estate_ws[74]), int(_estate_ws[75]), int(_estate_ws[76])',
 '== 77','== 78','!= 78','the 77-row cut','79 rows',
 '"engine_owner rows 209 + candidate',
 'W1..W220','W2..W220','W17..W220','below 220',
 'prior-wave disjointness W2..W',
 '909,989','484,120',
]
for tok in toks:
    print(t.count(tok), repr(tok))
