# -*- coding: utf-8 -*-
"""r977 post-sentinel calibration probe: counts after the W234 sentinel extraction."""
import io
t = io.open(r"results\_w233bmc_freeze_edits.py", encoding="utf-8", newline="").read()
assert len(t) == 50218, f"len {len(t)}"

# KEPT block
k0 = t.index("assert n1_t4.count('    # --- W209 materializer face')")
k1 = t.index("assert n1_t4.count('    # --- W232 materializer face')")
k2 = t.index("\n", k1)
KEPT = t[k0:k2]
print("KEPT materializer faces:", KEPT.count("materializer face"), "| assert lines:", KEPT.count("\nassert "))
print("KEPT W229:", KEPT.count("W229"), "| KEPT W230:", KEPT.count("W230"), "| KEPT W231:", KEPT.count("W231"),
      "| KEPT W232:", KEPT.count("W232"), "| KEPT e58dbcda3:", KEPT.count("e58dbcda3"),
      "| KEPT aee0bd9fa:", KEPT.count("aee0bd9fa"), "| KEPT W233:", KEPT.count("W233"),
      "| KEPT r968:", KEPT.count("r968"))
t2 = t.replace(KEPT, "@@KEPT@@")

# LIVE line
l0 = t2.index('"liveness_anchors"')
l0 = t2.rindex("\n", 0, l0) + 1
l1 = t2.index("\n", l0)
LIVE = t2[l0:l1]
print("LIVE _block_kept:", LIVE.count("_block_kept"), "| LIVE tail:", LIVE[-60:])
print("LIVE w232_block_kept:", LIVE.count("w232_block_kept"), "| LIVE w233:", LIVE.count("w233"))
t2 = t2.replace(LIVE, "@@LIVE@@")

# LEG231
g0 = t2.index("w231_leg = [")
g2 = t2.index("\n]", g0) + 2
LEG231 = t2[g0:g2]
print("LEG231 N1_BANDS[231]:", LEG231.count("N1_BANDS[231]"), "| W231 parity:", LEG231.count("W231 row parity drift"),
      "| w231_:", LEG231.count("w231_"), "| W231:", LEG231.count("W231"))
t2 = t2.replace(LEG231, "@@LEG231@@")

# LEG232
h0 = t2.index("w232_leg = [")
h2 = t2.index("\n]", h0) + 2
LEG232 = t2[h0:h2]
print("LEG232 N1_BANDS[232]:", LEG232.count("N1_BANDS[232]"), "| W232 parity:", LEG232.count("W232 row parity drift"),
      "| w232_:", LEG232.count("w232_"), "| W232:", LEG232.count("W232"), "| pf.N1_BANDS[232]:", LEG232.count("pf.N1_BANDS[232]"))
t2 = t2.replace(LEG232, "@@LEG232@@")

# ASM
a0 = t2.index("block = EOL.join(hdr)")
a1 = t2.index("\n", a0)
ASM = t2[a0:a1]
print("ASM:", ASM)
t2 = t2.replace(ASM, "@@ASM@@")

print("--- POST-SENTINEL COUNTS ---")
faces = ["W233", "w233_", "n1_w233", "n1w233", "W232", "w232_", "W231", "w231_", "W230", "w230_",
 "W229", "w229_", "m230", "N1_BANDS\\[230\\]", "_c232", "N1_BANDS.get(232)", "WAVE_CONFIGS[232]",
 "WAVE_CONFIGS[233]", "pf.N1_BANDS[232]", "pf.N1_BANDS[231]", "pf.N1_BANDS[230]",
 "n1_w232_results", "n1_w232", "e58dbcda3", "59856ff28", "5c90051e0+776b15270",
 "5c90051e0", "776b15270", "MSG-20261013-1530-bmc", "MSG-20261013-1345-bmc",
 "dd38a9da8", "8d3a1b78a", "executed bm-c r968", "r968 (seat", "r968 window",
 "r968 itself", "r968-continuation", "cf3501cd9", "probe receipt @ r968 window",
 "r968 15:2x", "r968 probe leg0", "r968 seat-time live face",
 "rows 62 + candidate", "63rd", "bmc_ordinal=63", "NINETY-THIRD instance",
 "TWO HUNDRED AND THIRTY-THIRD", "sixty-third", "rows 222 + candidate",
 "expect 222/62", "precedent 221/61 pre-splice", "splice 222/62",
 "== 222 and len(bmc_rows_live) == 62",
 "934_189", "508_320", "934,189", "508,320", "(527_404, 529_403)", "(529_404, 529_603)",
 "r973 freeze window", "r973 freeze-window bundle", "r972 prereg derived", "r972 window",
 "r972 + freeze splice script landed", "twenty-second consecutive", "seventh consecutive",
 "SEVENTEEN-level", "2a21ef7cc4eaaa70375c7e4baec99f423488d5e2",
 "_w232bmc_freeze_edits.py", "w231_out_path", "w232_out_path", "w231_transitive",
 "w232_a_tail", "w232_b_tail", "w232_freeze_sha", "w232_prereg_sha",
 "w233_prereg_sha", "w233_receipt_sha", "w232_upstream", "w232_total", "w232_merged_n",
 "w230_leg", "w231_leg", "w232_leg", "assert pf.N1_BANDS[",
 "if w < 233)", "range(16, 233)", "range(17, 233)", "below 233 composes", "below-233",
 "if w < 232", "w<232 leaked", "arith_a233", "arith_b233", "n3r1_used233",
 "== 88 \\", "== 90, \\", "!= 90 (69 estate", "89 rows", "91 rows", "88-row cut",
 "int(_estate_ws[87]) == 229", "W211..W229 legs", "W211..W228 legs",
 "downstream W234 seat NOT yet published", "downstream W234 seat publication pending",
 "W234+ projection", "naive W234 A window", "NINETY-FOURTH instance anticipated",
 "233: {\"batch\"", "'233: {\"a\"'", "'    233: {\"a\"'", "w<233 count",
 "W231+W230+W229+W228+W227 finalize", "W232+W231+W230+W229+W228 finalize",
 "W231/W230/W229/W228 finalize are transitive",
 "probe_receipt_bmc_ordinal_face\": 63", "n1w233-0of12", "n1w233-11of12",
 "PARITY span", "upstream W230 row leg not found inside W232 parity span",
 "w232_out_path", "w233_out_path", "w233_prereg_sha[:10]", "w232_freeze_sha[:10]",
 "_w233bmc_20261013_probe_receipt.json", "_w233bmc_freeze_receipt.json",
 "MSG-1233 tail", "wave 233 = first free number", '"wave": 233,', "_set_wave(233)",
 "f'{CFG_I}233: ", "f'{ROW_I}233: ", "ROW_I + '233: {\"a\"'", "f'233: {{\"a\":",
 "PERPETUAL_N1_W233_PREREG.md", "PERPETUAL_N1_W234_PREREG.md", "1193b255",
 "SEVENTEEN-level lineage replay", "rows 223 + candidate", "224th",
 "engine_owner rows 222 + candidate", "engine_owner rows 223 + candidate",
 "twentieth", "twenty-first", "sixth consecutive", "FIFTEEN-level",
 "dead r966", "dead r963", "r963-continuation", "r959-continuation", "dead r961",
 "842f817ad", "2ae8553e6", "0636c1d12", "492972ee7", "4e373b743", "aee0bd9fa",
 "f'234: {{\"a\":", "234: {\"batch\"", "w234_", "n1_w234", "n1w234"]
for f_ in faces:
    print("%-58r %d" % (f_, t2.count(f_)))
print("--- W233 contexts (non-KEPT) ---")
import re
for m in list(re.finditer(re.escape("W233"), t2)):
    seg = t2[max(0, m.start()-40):m.start()+45].replace("\n", "\\n")
    print("   ", repr(seg))
