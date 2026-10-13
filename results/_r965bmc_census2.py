# -*- coding: utf-8 -*-
import io, json
t = io.open(r"results\_w230bmc_freeze_edits.py", encoding="utf-8", newline="").read()
faces = [
 '229: {"batch', '230: {"batch', '229: {"a', '    229: {"a', '    230: {"a',
 "f'{CFG_I}230: ", "f'{ROW_I}230: ", "f'230: {{\"a\":", "ROW_I + '230: {\"a\"",
 "N1_BANDS.get(229)", "N1_BANDS.get(230)", "pf.N1_BANDS[230]", "WAVE_CONFIGS[231]",
 "seat MSG-1230 tail", "seat MSG-1231 tail", "wave 231", "if w < 231",
 "range(16, 231", "range(17, 231", "below 231", "below-231", "w<231",
 "NINETY-SECOND instance", "NINETY-FIRST instance", "staircase NINETY-FIRST",
 "bmc_ordinal=61", "(expect 929,789 / 503,920)", "925_389", "499_520",
 "842f817ad", "e1401e62", "51ac5362", "WAVE row census", "229/230", "230/231",
 "221st wave", "owner_total", "MSG-1231", "_w230bmc_20261013_probe_receipt.json",
 "_w230bmc_freeze_receipt.json", "_w231bmc", "PERPETUAL_N1_W231_PREREG",
 "PERPETUAL_N1_W230_PREREG", "r963 (absorb continuation)", "r963-continuation",
 "w230_prereg_sha[:10]", "w230_receipt_sha[:10]", "w231_prereg_sha", "w231_receipt_sha",
 "'229: {\"a\"'", "'230: {\"a\"'", "W229/W228", "W228/W227",
 "results/perpetual_faces/n1_w228_results.json", "n1_w229_results.json",
 "ledger 925,389 / K=499,520", "ledger 927,589 / K=501,720", "w226_transitive",
 "w225_transitive", "w228_transitive", "w229_transitive", "w230_transitive",
]
print(json.dumps({f: t.count(f) for f in faces}, indent=1, sort_keys=True))
