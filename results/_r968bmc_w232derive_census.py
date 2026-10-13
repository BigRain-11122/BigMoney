# -*- coding: utf-8 -*-
"""r968 census: _w231bmc_freeze_edits.py token faces for the W232 derive pairs."""
import io
t = io.open(r"results\_w231bmc_freeze_edits.py", encoding="utf-8", newline="").read()
print("total chars", len(t))
needles = [
 # self wave faces (W231 -> W232)
 "n1_w231", "w231_", "n1w231", "W231", "_w231bmc_20261013_probe_receipt.json",
 "_w231bmc_freeze_receipt.json", "_w230bmc_freeze_edits.py", "_set_wave(231)",
 '"wave": 231,', "231: {\"batch\"", "231: {\"a\"", "WAVE_CONFIGS[231]",
 "seat MSG-1231 tail", "wave 231 = first free number", "wave 231: ",
 "if w < 231)", "range(16, 231)", "range(17, 231)", "w<231 count", "if w < 230",
 "w<230 leaked", "below 231 composes", "below-231", "arith_a231", "arith_b231",
 "n3r1_used231", "PERPETUAL_N1-W231", "PERPETUAL_N1_W231_PREREG.md",
 # upstream faces (W230 -> W231)
 "W230", "w230_", "W229", "w229_", "W228", "w228_", "m227",
 "N1_BANDS\\[227\\]", "_c229", "229: {\"batch\"", "229: {\"a\"",
 "N1_BANDS.get(229)", "WAVE_CONFIGS[229]", "pf.N1_BANDS[229]",
 "N1_BANDS.get(230)", "WAVE_CONFIGS[230]", "pf.N1_BANDS[230]",
 "n1_w230", "n1_w229", "n1_w228", "n1_w227", "n1_w226", "n1_w225",
 "n1_w224", "n1_w223",
 # projection aging
 "W232+ projection", "naive W232 A window", "W232 freezer", "W232+ freezer",
 "downstream W232 seat", "NINETY-SECOND instance anticipated",
 # ordinals
 "NINETY-FIRST instance", "NINETIETH", "NINETY-FIRST", "NINETY-SECOND",
 "TWO HUNDRED AND THIRTY-FIRST", "sixty-first", "61st", "bmc_ordinal=61",
 "rows 60 + candidate", "rows 220 + candidate", "expect 220/60",
 "precedent 219/59 pre-splice", "splice 220/60", "== 220 and len(bmc_rows_live) == 60",
 "engine_owner rows 220 + candidate", "rows 61 + candidate", "61st own wave",
 # seat/provenance
 "MSG-20261013-1155-bmc", "MSG-20261013-1000-bmc", "6638ddf9f", "6cfe285e3",
 "aebe0a5ac", "91de0ae83", "8d3a1b78a",
 # band/ledger facts
 "(523_004, 525_003)", "(525_004, 525_203)", "929_789", "503_920",
 "929,789", "503,920", "931,989", "506,120", "(expect 929,789",
 # upstream cycle shas
 "24e12fa5e", "ce70c5808", "0ef11a120", "aec41c57c", "2ae8553e6",
 "f4b24e865", "492972ee7", "4e373b743", "aee0bd9fa", "0636c1d12",
 # window labels
 "r965 freeze window", "r965 freeze-window bundle", "r964 prereg derived",
 "r964 window", "dead r963 window", "r963 dead-window estate",
 "r963 11:5x", "probe receipt @ r963 window", "r963 probe leg0",
 "r963 seat-time live face", "executed bm-c r962", "twentieth consecutive",
 "fifth consecutive", "FIFTEEN-level", "SIXTEEN-level",
 # structure
 "assert pf.N1_BANDS[", "== 86 \\", "== 88, \\", "int(_estate_ws[85]) == 227",
 "89 rows", "87-row cut", "86-row cut", "w228_leg", "w229_leg", "w230_leg",
 "materializer face'", "liveness_anchors", "w230_block_kept",
 "upstream W228 row leg not found inside W230 parity span",
 "par_sec", "par_full",
 # misc upstream prose
 "r963 freeze-window editor", "r958 absorb generation",
 "r962 (seat 6cfe285e3)", "r962 (seat", "r963-continuation",
 "0ef11a120+aec41c57c", "492972ee7+4e373b743",
]
for nd in needles:
    print("%-52r %d" % (nd, t.count(nd)))
