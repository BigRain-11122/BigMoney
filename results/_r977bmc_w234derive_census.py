# -*- coding: utf-8 -*-
"""r977 census: _w233bmc_freeze_edits.py token faces for the W234 derive pairs."""
import io, re
t = io.open(r"results\_w233bmc_freeze_edits.py", encoding="utf-8", newline="").read()
print("total chars", len(t))
needles = [
 # self wave faces (W233 -> W234)
 "n1_w233", "w233_", "n1w233", "W233", "_w233bmc_20261013_probe_receipt.json",
 "_w233bmc_freeze_receipt.json", "_w232bmc_freeze_edits.py", "_set_wave(233)",
 '"wave": 233,', '233: {"batch"', '233: {"a"', "WAVE_CONFIGS[233]",
 "seat MSG-1233 tail", "wave 233 = first free number", "wave 233: ",
 "if w < 233)", "range(16, 233)", "range(17, 233)", "w<233 count", "if w < 232",
 "w<232 leaked", "below 233 composes", "below-233", "arith_a233", "arith_b233",
 "n3r1_used233", "PERPETUAL_N1_W233_PREREG.md", "PERPETUAL_N1-W233",
 "f'{CFG_I}233: ", "f'{ROW_I}233: ", "ROW_I + '233: {\"a\"'", "f'233: {{\"a\":",
 # upstream faces (W232 -> W233)
 "W232", "w232_", "W231", "w231_", "W230", "w230_", "W229", "w229_", "m230", "m229",
 "N1_BANDS\\[230\\]", "N1_BANDS\\[231\\]", "_c232", '232: {"batch"', '232: {"a"',
 "'    232: {\"a\"'", "N1_BANDS.get(232)", "WAVE_CONFIGS[232]",
 "pf.N1_BANDS[232]", "pf.N1_BANDS[231]", "pf.N1_BANDS[230]", "pf.N1_BANDS[229]",
 "n1_w232", "n1_w231", "n1_w230", "n1_w232_results", "n1_w231_results", "n1_w230_results",
 "PERPETUAL_N1_W232_PREREG.md", "PERPETUAL_N1-W232",
 # projection aging
 "W234+ projection", "naive W234 A window", "W234 freezer", "W234+ freezer",
 "downstream W234 seat", "W235", "NINETY-FOURTH instance anticipated",
 "NINETY-FIFTH", "NINETY-FOURTH",
 # ordinals
 "NINETY-THIRD instance", "NINETY-SECOND", "TWO HUNDRED AND THIRTY-THIRD",
 "TWO HUNDRED AND THIRTY-FOURTH", "sixty-third", "sixty-fourth", "63rd", "64th",
 "bmc_ordinal=63", "bmc_ordinal=64", "62nd",
 "rows 62 + candidate", "rows 222 + candidate", "rows 63 + candidate", "rows 223 + candidate",
 "expect 222/62", "expect 223/63", "precedent 221/61 pre-splice", "precedent 222/62 pre-splice",
 "splice 222/62", "splice 223/63", "== 222 and len(bmc_rows_live) == 62",
 "== 223 and len(bmc_rows_live) == 63", "224th", '"ordinal": 223', '"ordinal": 224',
 # seat/provenance
 "MSG-20261013-1530-bmc", "MSG-20261013-1345-bmc", "MSG-20261013-1955-bmc",
 "MSG-20261013-1155-bmc", "dd38a9da8", "8d3a1b78a", "260217d39", "6638ddf9f",
 "2a21ef7cc4eaaa70375c7e4baec99f423488d5e2",
 "1193b255531f7aadcdff050069371c5e5169b11f",
 "a3a7aa63230e87cb5a6212f54a07bc1738dde5b3",
 # band/ledger facts
 "(527_404, 529_403)", "(529_404, 529_603)", "(529_604, 531_603)", "(531_604, 531_803)",
 "934_189", "508_320", "936_389", "510_520",
 "934,189", "508,320", "936,389", "510,520", "(expect 934,189", "(expect 936,389",
 # upstream cycle shas
 "e58dbcda3", "59856ff28", "5c90051e0", "776b15270", "0ca920362", "6c1587483",
 "d4cce3ffe", "aee0bd9fa", "0636c1d12", "2ae8553e6", "842f817ad", "933e3ceea",
 "51f663b64", "252d5cc95",
 # window labels
 "r973 freeze window", "r973 freeze-window bundle", "r972 prereg derived", "r972 window",
 "r976", "r977", "r974", "twenty-second consecutive", "twenty-third consecutive",
 "seventh consecutive", "eighth consecutive", "SEVENTEEN-level", "EIGHTEEN-level",
 "r966 13:2x", "r968 15:2x", "probe receipt @ r968 window", "r968 probe leg0",
 "r968 seat-time live face", "executed bm-c r968", "executed bm-c r973",
 "r972 (seat", "dead r972 window", "dead r973 window", "r968 (seat",
 "twenty-first consecutive", "sixth consecutive",
 # structure
 "assert pf.N1_BANDS[", "== 88 \\", "== 89, \\", "== 90, \\", "== 91, \\",
 "int(_estate_ws[85]) == 227", "int(_estate_ws[86]) == 228", "int(_estate_ws[87]) == 229",
 "int(_estate_ws[88]) == 230",
 "88-row cut", "89 rows", "90 rows", "91 rows", "92 rows", "w230_leg", "w231_leg",
 "w232_leg", "w233_leg", "materializer face'", "liveness_anchors", "w232_block_kept",
 "w231_block_kept", "w230_block_kept", "w229_block_kept", "_block_kept",
 "upstream W230 row leg not found inside W232 parity span",
 "upstream W229 row leg not found inside W231 parity span",
 "par_sec", "par_full", "block = EOL.join(hdr)", "EOL.join(w230_leg)",
 "EOL.join(w231_leg)", "EOL.join(w232_leg)",
 # receipt keys
 "w232_freeze_sha", "w232_prereg_sha", "w232_total", "w232_merged_n", "w232_a_tail",
 "w232_b_tail", "w233_prereg_sha", "w233_receipt_sha", "w232_upstream", "w232_transitive",
 "w231_transitive", "w231_upstream", "w230_transitive", "w233_transitive",
 "w230_out_path", "w231_out_path", "w232_out_path", "w233_out_path",
 "probe_receipt_bmc_ordinal_face",
 # misc
 "engine_owner rows", "0ef11a120+aec41c57c", "492972ee7+4e373b743",
 "5c90051e0+776b15270", "6c1587483+d4cce3ffe",
 "W231+W230+W229+W228+W227 finalize products present",
 "W232+W231+W230+W229+W228 finalize products present",
 "W231/W230/W229/W228 finalize are transitive deps",
 "W232/W231/W230/W229 finalize are transitive deps",
 "rows 221 + candidate", "rows 61 + candidate",
 "n1w233-0of12", "n1w233-11of12", "n1w234-0of12",
 "twentieth consecutive", "twenty-first consecutive",
 "r958 absorb generation", "r857",
 # dbg5 faces carried
 "w233_prereg_sha", "w233_receipt_sha", "w234_prereg_sha", "w234_receipt_sha",
]
for nd in needles:
    print("%-56r %d" % (nd, t.count(nd)))
print("---- contexts")
for pat in ("SEVENTEEN-level", "NINETY-THIRD", "NINETY-FOURTH", "TWO HUNDRED AND THIRTY-THIRD",
            "63rd", "w230_leg", "934,189", "if w < 232", "w<232", "below-233", "below-232",
            "r973 freeze window", "twenty-second consecutive", "seventh consecutive",
            "0ca920362", "6c1587483", "d4cce3ffe", "933e3ceea", "e58dbcda3", "w232_transitive",
            "w231_transitive", "w232_upstream", "w232_freeze_sha", "MSG-20261013-1530-bmc"):
    print("-- ctx:", pat)
    for m in list(re.finditer(re.escape(pat), t))[:6]:
        print("   ", repr(t[max(0, m.start()-70):m.start()+80].replace("\n", "\\n")))
