# -*- coding: utf-8 -*-
"""r979 census: _w234bmc_freeze_edits.py token faces for the W235 derive pairs."""
import io, re
t = io.open(r"results\_w234bmc_freeze_edits.py", encoding="utf-8", newline="").read()
print("total chars", len(t))
needles = [
 # self wave faces (W234 -> W235)
 "n1_w234", "w234_", "n1w234", "W234", "_w234bmc_20261013_probe_receipt.json",
 "_w234bmc_freeze_receipt.json", "_w233bmc_freeze_edits.py", "_set_wave(234)",
 '"wave": 234,', '234: {"batch"', '234: {"a"', "WAVE_CONFIGS[234]",
 "seat MSG-1234 tail", "wave 234 = first free number", "wave 234: ",
 "if w < 234)", "range(16, 234)", "range(17, 234)", "w<234 count", "if w < 233",
 "w<233 leaked", "below 234 composes", "below-234", "arith_a234", "arith_b234",
 "n3r1_used234", "PERPETUAL_N1_W234_PREREG.md", "PERPETUAL_N1-W234",
 "f'{CFG_I}234: ", "f'{ROW_I}234: ", "ROW_I + '234: {\"a\"'", "f'234: {{\"a\":",
 # upstream faces (W233 -> W234)
 "W233", "w233_", "W232", "w232_", "W231", "w231_", "W230", "w230_", "W229", "w229_",
 "m231", "m230", "N1_BANDS\\[231\\]", "N1_BANDS\\[232\\]", "_c233", "_c232",
 '233: {"batch"', '233: {"a"', "'    233: {\"a\"'", "N1_BANDS.get(233)",
 "WAVE_CONFIGS[233]", "pf.N1_BANDS[233]", "pf.N1_BANDS[232]", "pf.N1_BANDS[231]",
 "pf.N1_BANDS[230]", "n1_w233", "n1_w232", "n1_w231", "n1_w233_results",
 "n1_w232_results", "n1_w231_results", "PERPETUAL_N1_W233_PREREG.md", "PERPETUAL_N1-W233",
 # projection aging
 "W235+ projection", "naive W235 A window", "W235 freezer", "W235+ freezer",
 "downstream W235 seat", "W236", "NINETY-FIFTH instance anticipated", "NINETY-SIXTH",
 "NINETY-FIFTH", "NINETY-FOURTH",
 # ordinals
 "NINETY-FOURTH instance", "NINETY-THIRD", "TWO HUNDRED AND THIRTY-FOURTH",
 "TWO HUNDRED AND THIRTY-FIFTH", "sixty-fourth", "sixty-fifth", "64th", "65th",
 "bmc_ordinal=64", "bmc_ordinal=65", "63rd",
 "rows 63 + candidate", "rows 223 + candidate", "rows 64 + candidate", "rows 224 + candidate",
 "expect 223/63", "expect 224/64", "precedent 222/62 pre-splice", "precedent 223/63 pre-splice",
 "splice 223/63", "splice 224/64", "== 223 and len(bmc_rows_live) == 63",
 "== 224 and len(bmc_rows_live) == 64", "225th", '"ordinal": 224', '"ordinal": 225',
 "engine_owner rows 223", "engine_owner rows 224",
 # seat/provenance
 "MSG-20261013-1955-bmc", "MSG-20261013-1530-bmc", "MSG-20261013-2149-bmc",
 "dd38a9da8", "260217d39", "e830a26324a4473e503e0e0cab6a035cfb601949",
 "2a21ef7cc4eaaa70375c7e4baec99f423488d5e2",
 "1193b255531f7aadcdff050069371c5e5169b11f",
 "89bd6962cd9e367586e1fdb520e37b8b47e5ee86",
 "a3a7aa63230e87cb5a6212f54a07bc1738dde5b3",
 # band/ledger facts
 "(529_604, 531_603)", "(531_604, 531_803)", "(531_804, 533_803)", "(533_804, 534_003)",
 "936_389", "510_520", "938_589", "512_720",
 "936,389", "510,520", "938,589", "512,720", "(expect 936,389", "(expect 938,589",
 # upstream cycle shas
 "e58dbcda3", "59856ff28", "5c90051e0", "776b15270", "0ca920362", "6c1587483",
 "d4cce3ffe", "aee0bd9fa", "0636c1d12", "2ae8553e6", "842f817ad", "933e3ceea",
 "51f663b64", "252d5cc95", "de342250c", "39f7b8b0c", "5022491bc", "cbe25f1a4",
 # window labels
 "r976 freeze window", "r976 freeze-window bundle", "r976 prereg derived",
 "r976 window", "r978", "r979", "r974", "twenty-third consecutive",
 "twenty-fourth consecutive", "eighth consecutive", "ninth consecutive",
 "EIGHTEEN-level", "NINETEEN-level", "r974 19:4x", "r976 21:5x",
 "probe receipt @ r974 window", "r974 probe leg0", "r974 seat-time live face",
 "executed bm-c r974", "executed bm-c r976", "r974 (seat", "dead r973 window",
 "dead r976-continuation window", "dead r976 window", "r976 (seat",
 "twenty-second consecutive", "seventh consecutive", "r968 15:2x",
 # structure
 "assert pf.N1_BANDS[", "== 89 \\", "== 90, \\", "== 91, \\", "== 92, \\",
 "int(_estate_ws[85]) == 227", "int(_estate_ws[86]) == 228", "int(_estate_ws[87]) == 229",
 "int(_estate_ws[88]) == 230", "int(_estate_ws[89]) == 231",
 "89-row cut", "90 rows", "91 rows", "92 rows", "93 rows", "w231_leg", "w232_leg",
 "w233_leg", "w234_leg", "materializer face'", "liveness_anchors", "w233_block_kept",
 "w232_block_kept", "w231_block_kept", "w230_block_kept", "_block_kept",
 "upstream W231 row leg not found inside W233 parity span",
 "upstream W230 row leg not found inside W232 parity span",
 "par_sec", "par_full", "block = EOL.join(hdr)", "EOL.join(w231_leg)",
 "EOL.join(w232_leg)", "EOL.join(w233_leg)",
 # receipt keys
 "w233_freeze_sha", "w233_prereg_sha", "w233_total", "w233_merged_n", "w233_a_tail",
 "w233_b_tail", "w234_prereg_sha", "w234_receipt_sha", "w233_upstream",
 "w233_transitive", "w232_transitive", "w232_upstream", "w231_transitive",
 "w234_transitive", "w231_out_path", "w232_out_path", "w233_out_path", "w234_out_path",
 "probe_receipt_bmc_ordinal_face",
 # misc
 "6c1587483+d4cce3ffe", "39f7b8b0c+5022491bc", "0ef11a120+aec41c57c",
 "492972ee7+4e373b743", "5c90051e0+776b15270",
 "W231+W230+W229+W228+W227 finalize products present",
 "W232+W231+W230+W229+W228 finalize products present",
 "W233+W232+W231+W230+W229 finalize products present",
 "W231/W230/W229/W228 finalize are transitive deps",
 "W232/W231/W230/W229 finalize are transitive deps",
 "W233/W232/W231/W230 finalize are transitive deps",
 "rows 222 + candidate", "rows 62 + candidate", "rows 61 + candidate",
 "n1w234-0of12", "n1w234-11of12", "n1w235-0of12",
 "twenty-second consecutive", "twenty-first consecutive", "r958 absorb generation",
 "r857", "w234_prereg_sha", "w235_prereg_sha", "w235_receipt_sha",
]
for nd in needles:
    print("%-58r %d" % (nd, t.count(nd)))
print("---- contexts")
for pat in ("EIGHTEEN-level", "NINETY-FOURTH", "NINETY-FIFTH", "TWO HUNDRED AND THIRTY-FOURTH",
            "64th", "w231_leg", "936,389", "if w < 233", "w<233", "below-234",
            "r976 freeze window", "twenty-third consecutive", "eighth consecutive",
            "260217d39", "6c1587483", "d4cce3ffe", "252d5cc95", "de342250c",
            "w233_transitive", "w232_transitive", "w233_upstream", "w233_freeze_sha",
            "MSG-20261013-1955-bmc", "MSG-20261013-2149-bmc", "e830a2632", "1193b255",
            "a3a7aa632", "engine_owner rows", "92 rows", "ninth consecutive"):
    print("-- ctx:", pat)
    for m in list(re.finditer(re.escape(pat), t))[:6]:
        print("   ", repr(t[max(0, m.start()-70):m.start()+90].replace("\n", "\\n")))
