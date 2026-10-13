# -*- coding: utf-8 -*-
"""r968 census-3: mirror/cfg needle contexts."""
import io, re
t = io.open(r"results\_w231bmc_freeze_edits.py", encoding="utf-8", newline="").read()
toks = [
 "pf.N1_BANDS[230]", "WAVE_CONFIGS[230]", '230: {"a"', '    230: {"a"',
 '231: {"a"', "f'231: {{", "f'{ROW_I}231: ", "{CFG_I}231: ",
 "pf_mod.N1_BANDS[230]", "N1_BANDS.get(230)", "PERPETUAL-N1-W231",
 "_entry_shard_of", 'n1w231', "n1w230",
 "PERPETUAL_N1-W231-SHARD", "assert pf.N1_BANDS[228] ==",
 "assert pf.N1_BANDS[229] ==", "assert pf.N1_BANDS[230] ==",
 "w228_a", "w228_b", "w229_a", "w229_b", "w230_a", "w230_b", "w231_a", "w231_b",
 "reg_ints", "lfc_actual12", "options_actual12",
]
for tok in toks:
    n = t.count(tok)
    print("== %r %d" % (tok, n))
    if n <= 10:
        for m in re.finditer(re.escape(tok), t):
            s = max(0, m.start() - 40)
            print("   ", repr(t[s:m.end() + 48]))
