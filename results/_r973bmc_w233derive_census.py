# -*- coding: utf-8 -*-
"""r973 census: _w232bmc_freeze_edits.py token faces for the W233 derive pairs."""
import io, re
t = io.open(r"results\_w232bmc_freeze_edits.py", encoding="utf-8", newline="").read()
print("total chars", len(t))
needles = [
 # self wave faces (W232 -> W233)
 "n1_w232", "w232_", "n1w232", "W232", "_w232bmc_20261013_probe_receipt.json",
 "_w232bmc_freeze_receipt.json", "_w231bmc_freeze_edits.py", "_set_wave(232)",
 '"wave": 232,', '232: {"batch"', '232: {"a"', "WAVE_CONFIGS[232]",
 "seat MSG-1232 tail", "wave 232 = first free number", "wave 232: ",
 "if w < 232)", "range(16, 232)", "range(17, 232)", "w<232 count", "if w < 231",
 "w<231 leaked", "below 232 composes", "below-232", "arith_a232", "arith_b232",
 "n3r1_used232", "PERPETUAL_N1-W232", "PERPETUAL_N1_W232_PREREG.md",
 "f'{CFG_I}232: ", "f'{ROW_I}232: ", "ROW_I + '232: {\"a\"'", "f'232: {{\"a\":",
 # upstream faces (W231 -> W232)
 "W231", "w231_", "W230", "w230_", "W229", "w229_", "W228", "w228_", "m229", "m228",
 "N1_BANDS\\[229\\]", "N1_BANDS\\[228\\]", "_c231", "_c230", '231: {"batch"', '231: {"a"',
 "'    231: {\"a\"'", "N1_BANDS.get(231)", "N1_BANDS.get(230)", "WAVE_CONFIGS[231]",
 "WAVE_CONFIGS[230]", "pf.N1_BANDS[231]", "pf.N1_BANDS[230]", "pf.N1_BANDS[229]",
 "n1_w231", "n1_w230", "n1_w229", "n1_w231_results", "n1_w230_results", "n1_w232_results",
 "PERPETUAL_N1_W231_PREREG.md", "PERPETUAL_N1-W231",
 # projection aging
 "W233+ projection", "naive W233 A window", "W233 freezer", "W233+ freezer",
 "downstream W233 seat", "W234", "NINETY-THIRD instance anticipated",
 "NINETY-FOURTH",
 # ordinals
 "NINETY-SECOND instance", "NINETY-FIRST", "NINETY-SECOND", "NINETY-THIRD",
 "TWO HUNDRED AND THIRTY-SECOND", "TWO HUNDRED AND THIRTY-THIRD", "sixty-second",
 "sixty-third", "62nd", "63rd", "bmc_ordinal=62", "bmc_ordinal=63",
 "rows 61 + candidate", "rows 221 + candidate", "rows 222 + candidate",
 "expect 221/61", "expect 222/62", "precedent 220/60 pre-splice",
 "precedent 221/61 pre-splice", "splice 221/61", "splice 222/62",
 "== 221 and len(bmc_rows_live) == 61", "== 222 and len(bmc_rows_live) == 62",
 "223rd", '"ordinal": 222', '"ordinal": 223', "candidate = 63rd", "62nd owned",
 "61st", "TWO HUNDRED AND TWENTY-THIRD",
 # seat/provenance
 "MSG-20261013-1345-bmc", "MSG-20261013-1155-bmc", "MSG-20261013-1530-bmc",
 "MSG-20261013-1000-bmc", "8d3a1b78a", "dd38a9da8", "6638ddf9f", "6cfe285e3",
 "a3a7aa63230e87cb5a6212f54a07bc1738dde5b3", "2a21ef7cc4eaaa70375c7e4baec99f423488d5e2",
 "91de0ae83", "e485a0b3f", "4e30ddf69",
 # band/ledger facts
 "(525_204, 527_203)", "(527_204, 527_403)", "(527_404, 529_403)", "(529_404, 529_603)",
 "931_989", "506_120", "934_189", "508_320",
 "931,989", "506,120", "934,189", "508,320", "(expect 931,989", "(expect 934,189",
 # upstream cycle shas
 "aee0bd9fa", "0636c1d12", "492972ee7", "4e373b743", "e58dbcda3", "59856ff28",
 "5c90051e0", "776b15270", "24e12fa5e", "ce70c5808", "0ef11a120", "aec41c57c",
 "2ae8553e6", "842f817ad",
 # window labels
 "r968 freeze window", "r968 freeze-window bundle", "r967 prereg derived",
 "r967 window", "r972 window", "dead r966 window", "dead r968 window",
 "r966 13:2x", "r968 15:2x", "probe receipt @ r966 window", "r966 probe leg0",
 "r966 seat-time live face", "executed bm-c r966", "executed bm-c r968",
 "r962 (seat", "r966 (seat", "twentieth consecutive", "twenty-first consecutive",
 "twenty-second consecutive", "fifth consecutive", "sixth consecutive",
 "seventh consecutive", "FIFTEEN-level", "SIXTEEN-level", "SEVENTEEN-level",
 "r965 freeze window", "r963 11:5x", "r965-continuation", "r963-continuation",
 "r959-continuation", "dead r963 window", "dead r961 window", "dead r959 window",
 # structure
 "assert pf.N1_BANDS[", "== 87 \\", "== 88, \\", "== 89, \\",
 "int(_estate_ws[85]) == 227", "int(_estate_ws[86]) == 228", "int(_estate_ws[87]) == 229",
 "88-row cut", "87-row cut", "89 rows", "90 rows", "91 rows", "w229_leg", "w230_leg",
 "w231_leg", "w232_leg", "materializer face'", "liveness_anchors", "w231_block_kept",
 "w230_block_kept", "w229_block_kept", "_block_kept",
 "upstream W229 row leg not found inside W231 parity span",
 "upstream W228 row leg not found inside W230 parity span",
 "par_sec", "par_full", "block = EOL.join(hdr)", "EOL.join(w229_leg)",
 "EOL.join(w230_leg)", "EOL.join(w231_leg)",
 # receipt keys
 "w231_freeze_sha", "w231_prereg_sha", "w231_total", "w231_merged_n", "w231_a_tail",
 "w231_b_tail", "w232_prereg_sha", "w232_receipt_sha", "w231_upstream", "w231_transitive",
 "w230_transitive", "w230_upstream", "w229_transitive", "w232_transitive",
 "w230_out_path", "w231_out_path", "w232_out_path", "w231_receipt_sha",
 "probe_receipt_bmc_ordinal_face",
 # misc
 "engine_owner rows", "0ef11a120+aec41c57c", "492972ee7+4e373b743",
 "5c90051e0+776b15270", "r963 freeze-window editor", "r958 absorb generation",
 "W230+W229+W228+W227+W226 finalize products present",
 "W231+W230+W229+W228+W227 finalize products present",
 "W229/W228/W227/W226 finalize are transitive deps",
 "W230/W229/W228/W227 finalize are transitive deps",
 "rows 220 + candidate", "rows 60 + candidate",
]
for nd in needles:
    print("%-56r %d" % (nd, t.count(nd)))
print("---- contexts: twentieth/twenty-first consecutive")
for pat in ("twentieth consecutive", "twenty-first consecutive", "FIFTEEN", "SIXTEEN",
            "NINETY-SECOND", "TWO HUNDRED AND THIRTY-SECOND", "62nd", "w229_leg", "w232_",
            "931,989", "if w < 231", "w<231", "below-232"):
    print("-- ctx:", pat)
    for m in list(re.finditer(re.escape(pat), t))[:6]:
        print("   ", repr(t[max(0, m.start()-60):m.start()+70].replace("\n", "\\n")))
