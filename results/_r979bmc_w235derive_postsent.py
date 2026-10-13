# -*- coding: utf-8 -*-
"""r979 probe: sentinel-stripped counts + key contexts of _w234bmc_freeze_edits.py
for authoring _w235bmc_derive_editor.py. Replicates the W234 editor's phase-0 anchors
one wave forward (KEPT tail=W233 line, LEG232=w232_leg, LEG233=w233_leg, ASM w231/232/233)."""
import io, re

t = io.open(r"results\_w234bmc_freeze_edits.py", encoding="utf-8", newline="").read()
print("total chars", len(t))

# --- phase-0 replica: KEPT (W209..W233), LIVE, LEG232, LEG233, ASM ---
k0 = t.index("assert n1_t4.count('    # --- W209 materializer face')")
k1 = t.index("assert n1_t4.count('    # --- W233 materializer face')")
k2 = t.index("\n", k1)
KEPT = t[k0:k2]
print("KEPT: assert-lines", KEPT.count("\nassert "), "materializer faces", KEPT.count("materializer face"))
print("KEPT tail line:", repr(KEPT.splitlines()[-1][:150]))
t2 = t.replace(KEPT, "@@KEPT@@")

l0 = t2.index('"liveness_anchors"')
l0 = t2.rindex("\n", 0, l0) + 1
l1 = t2.index("\n", l0)
LIVE = t2[l0:l1]
print("LIVE _block_kept:", LIVE.count("_block_kept"))
t2 = t2.replace(LIVE, "@@LIVE@@")

g0 = t2.index("w232_leg = [")
g2 = t2.index("\n]", g0) + 2
LEG232 = t2[g0:g2]
print("LEG232 N1_BANDS[232]:", LEG232.count("N1_BANDS[232]"), "w232_ inside:", LEG232.count("w232_"))
t2 = t2.replace(LEG232, "@@LEG232@@")

h0 = t2.index("w233_leg = [")
h2 = t2.index("\n]", h0) + 2
LEG233 = t2[h0:h2]
print("LEG233 N1_BANDS[233]:", LEG233.count("N1_BANDS[233]"), "w233_ inside:", LEG233.count("w233_"))
t2 = t2.replace(LEG233, "@@LEG233@@")

a0 = t2.index("block = EOL.join(hdr)")
a1 = t2.index("\n", a0)
ASM = t2[a0:a1]
print("ASM:", repr(ASM))
t2 = t2.replace(ASM, "@@ASM@@")

print()
print("=== STRIPPED COUNTS (shift-order relevant) ===")
needles = [
 ("n1_w234",), ("w234_",), ("n1w234",), ("W234",),
 ("_w234bmc_20261013_probe_receipt.json",), ("_w234bmc_freeze_receipt.json",),
 ("_w233bmc_freeze_edits.py",), ("_set_wave(234)",), ('"wave": 234,',),
 ("WAVE_CONFIGS[234]",), ("seat MSG-1234 tail",), ("wave 234 = first free number",),
 ("wave 234: ",), ("if w < 234)",), ("range(16, 234)",), ("range(17, 234)",),
 ("w<234 count",), ("if w < 233",), ("w<233 leaked",), ("below 234 composes",),
 ("below-234",), ("arith_a234",), ("arith_b234",), ("n3r1_used234",),
 ("PERPETUAL_N1_W234_PREREG.md",), ("f'{CFG_I}234: ",), ("f'{ROW_I}234: ",),
 ("ROW_I + '234: {\"a\"'",), ("f'234: {{\"a\":",), ('234: {"batch"',), ('234: {"a"',),
 # upstream
 ("W233",), ("w233_",), ("W232",), ("w232_",), ("W231",), ("w231_",),
 ("W230",), ("w230_",), ("W229",), ("m231",), ("N1_BANDS\\[231\\]",), ("_c233",),
 ('233: {"batch"',), ('233: {"a"',), ("'    233: {\"a\"'",), ("N1_BANDS.get(233)",),
 ("WAVE_CONFIGS[233]",), ("pf.N1_BANDS[233]",), ("pf.N1_BANDS[232]",),
 ("n1_w233",), ("n1_w232",), ("n1_w233_results",), ("n1_w232_results",),
 ("PERPETUAL_N1_W233_PREREG.md",),
 # projections
 ("W235+ projection",), ("naive W235 A window",), ("W235 freezer",), ("W235+ freezer",),
 ("downstream W235 seat",), ("NINETY-FIFTH instance anticipated",),
 # ordinals
 ("NINETY-FOURTH instance",), ("TWO HUNDRED AND THIRTY-FOURTH",), ("sixty-fourth",),
 ("64th",), ("bmc_ordinal=64",), ("rows 63 + candidate",), ("rows 223 + candidate",),
 ("expect 223/63",), ("precedent 222/62 pre-splice",), ("splice 223/63",),
 ("== 223 and len(bmc_rows_live) == 63",), ("== 223 and len",),
 # seats/shas
 ("MSG-20261013-1955-bmc",), ("MSG-20261013-1530-bmc",), ("dd38a9da8",),
 ("260217d39",), ("1193b255531f7aadcdff050069371c5e5169b11f",),
 # band/ledger
 ("(529_604, 531_603)",), ("(531_604, 531_803)",), ("936_389",), ("510_520",),
 ("936,389",), ("510,520",), ("(expect 936,389",),
 # upstream cycle shas
 ("0ca920362",), ("6c1587483",), ("d4cce3ffe",), ("6c1587483+d4cce3ffe",),
 ("e58dbcda3",), ("aee0bd9fa",), ("2ae8553e6",), ("842f817ad",),
 # window labels
 ("r976 freeze window",), ("r976 freeze-window bundle",), ("r976 prereg derived",),
 ("r976 window",), ("r976 + freeze splice script landed",), ("r974 19:4x",),
 ("probe receipt @ r974 window",), ("r974 probe leg0",), ("r974 seat-time live face",),
 ("twenty-third consecutive",), ("eighth consecutive",), ("EIGHTEEN-level",),
 ("dead r973 window",), ("r976 21:5x",), ("r976 continuation",),
 # structure
 ('== 89 \\',), ('== 91, \\',), ("int(_estate_ws[88]) == 230",), ("89-row cut",),
 ("92 rows",), ("w231_leg",), ("w232_leg",), ("w233_leg",),
 ("w233_block_kept",), ("w232_block_kept",),
 ("w233_freeze_sha",), ("w233_prereg_sha",), ("w234_prereg_sha",),
 ("w234_receipt_sha",), ("w233_upstream",), ("w232_transitive",),
 ("W233+W232+W231+W230+W229 finalize products present",),
 ("W232/W231/W230/W229 finalize are transitive deps",),
 ("n1w234-0of12",), ("n1w234-11of12",), ("probe_receipt_bmc_ordinal_face",),
 ("engine_owner rows 223",), ("engine_owner rows 222",),
 ("executed bm-c r976",), ("executed bm-c r973",), ("dead r976 window",),
 ("r976 (seat",), ("r973 (seat",), ("r976 itself",),
]
for (nd,) in needles:
    print("%-58r %d" % (nd, t2.count(nd)))

print()
print("=== CONTEXTS (stripped) ===")
for pat in ("r976 prereg derived", "r976 window", "r976 + freeze splice script landed",
            "EIGHTEEN-level", "260217d39", "dd38a9da8", "eighth consecutive",
            "twenty-third consecutive", "92 rows", "engine_owner rows 223",
            "r974 19:4x", "6c1587483+d4cce3ffe", "dead r973 window",
            "MSG-20261013-1955-bmc", "NINETY-FOURTH instance", "rows 63 + candidate",
            "w231_leg = [", "(529_604, 531_603)", "936_389", "expect 223/63",
            "probe_receipt_bmc_ordinal_face", "89-row cut", "== 89 \\", "== 91, \\",
            "W233+W232", "n1w234-0of12", "w233_upstream", "w232_transitive",
            "MSG-20261013-1530-bmc", "0ca920362"):
    print("-- ctx:", pat)
    for m in list(re.finditer(re.escape(pat), t2))[:5]:
        print("   ", repr(t2[max(0, m.start()-90):m.start()+110].replace("\n", "\\n")))
