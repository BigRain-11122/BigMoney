# -*- coding: utf-8 -*-
# r1105 bm-c splice window: W274 editor needle preflight (r1077 MEASURED-counts law).
# Measures every needle count on the committed W273 freeze-edits canon
# (results/_w273bmc_freeze_edits.py, proven live-fire: W273 five-face splice
# 04f2127db + engine self-burn 12/12 + finalize one-pass 6659a0e36 ledger
# 1,024,935 / K=598,520, bm-c r1102 window) and simulates the phase-1
# (pre-D-swap) + phase-2 (W-blanket) transforms to measure the post-blanket
# phase-3 needle forms. Zero hand-assumed counts: the editor is authored
# FROM this receipt.
import io, json, subprocess, sys

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
CANON = "results/_w273bmc_freeze_edits.py"
OUT = "results/_r1105bmc_needle_preflight.json"
CRLF = "\r\n"

blob_wt = subprocess.run(["git", "-C", REPO, "hash-object", CANON],
                         capture_output=True, text=True).stdout.strip()
blob_head = subprocess.run(["git", "-C", REPO, "rev-parse", "HEAD:" + CANON],
                           capture_output=True, text=True).stdout.strip()
blob_origin = subprocess.run(["git", "-C", REPO, "rev-parse", "origin/main:" + CANON],
                             capture_output=True, text=True).stdout.strip()
assert blob_wt == blob_head == blob_origin and len(blob_wt) == 40, \
    f"canon blob drift wt={blob_wt} head={blob_head} origin={blob_origin}"

t = io.open(REPO + "\\" + CANON.replace("/", "\\"), encoding="utf-8", newline="").read()
crlf = t.count(CRLF); lf = t.count("\n") - crlf
assert crlf > lf, "canon EOL face drift (CRLF expected)"

raw = {}
def m(key):
    raw[key] = t.count(key)
    return raw[key]

# ---- projections ----
m("W274p"); m("W274"); m("W275p")
# ---- bands (underscore faces) ----
for k in ("617_901", "618_100", "617_900", "617_700", "615_901", "616_100",
          "615_701", "615_900", "620_101", "620_300", "620_100", "619_900",
          "618_101", "618_300"):
    m(k)
# ---- int-form projections ----
for k in ("617901", "619900", "618101", "618300", "620101", "622100",
          "620301", "620500"):
    m(k)
# ---- ledger/K ----
for k in ("1,022,735", "596,320", "1_022_735", "596_320", "1,024,935", "598,520"):
    m(k)
# ---- lc machine tokens ----
for k in ("n1_w273", "n1_w273_results.json", "n1w273-", "w273_",
          "n1_w272", "n1_w272_results.json", "w272_", "w274_",
          "_r1102bmc_build_w273_derive.py", "_r1104bmc_build_w274_derive.py"):
    m(k)
# ---- receipt paths / lineage / seat ----
for k in ("_w273bmc_", "_w272bmc_", "_w272bmc_freeze_edits.py template",
          "MSG-20261018-211x-bmc-w273-seat", "MSG-20261019-012x-bmc-w274-seat",
          'SEAT_ORIGIN = "39e1bb32f1"', "39e1bb32f1", "39e1bb32f1 r1101",
          "70b21a0264", "c99ee20a4", "04f2127db"):
    m(k)
# ---- prereg delivery prose faces ----
m("(authored 22:4x, banned_direction_gate ADMIT rc0, frozen b6bbb69e92 + surgery-" + CRLF +
  "# delivered to origin 839441a547 + receipts eeb3bf07ad, r1102 window).")
m("(E63 canon-clone builder _r1102bmc_build_w273_derive.py)")
m("(E63 canon-clone builder derive landed pre-freeze")
m("(authored 22:4x, banned gate ADMIT rc0, frozen b6bbb69e92 -> surgery-delivered r1102 origin ")
for k in ("bm-c r1102 window", "# r1102 window", "b6bbb69e92", "839441a547",
          "eeb3bf07ad", "ddc158b5047596ea", "6f31f6e073"):
    m(k)
# ---- window stamps ----
for k in ("2026-10-18 23:5x bm-c r1102 splice window",
          "bm-c r1100 splice window", "the bm-c r1100 splice window",
          "# r1100 splice window", "verified r1100",
          "cycle COMPLETE bm-c r1100 closeout 20:4x",
          "bm-c own seat executed at the bm-c r1100 splice window",
          "finalize one-pass bm-c r1100 closeout, ledger",
          "finalize one-pass bm-c r1100 closeout ledger",
          "own-wave full cycle r1100", "bm-c splice generation r1100 window",
          "(bm-c r1100", "r1101 BEFORE this freeze",
          "seat itself r1101; queue-head", "(r1101, queue-head seat-first supply",
          "(r1101 MSG-", "(R272: ", "r1104", "r1105"):
    m(k)
# ---- dates / receipt wave ----
for k in ("20261018", "2026-10-18", '"wave": 272', '"wave": 273', "20261019"):
    m(k)
# ---- phase-2 blanket counts ----
m("W273"); m("W272"); m("W271"); m("W275")
# ---- ordinal faces ----
for k in ("len(owner_rows_live) == 262 and len(bma_rows_live) == 130 and len(bmc_rows_live) == 91",
          "262/130/91", "owner_rows=262 / bma_rows=130 / bmc_rows=91",
          "rows 262 + candidate = 263rd", "; bm-c rows 91 +",
          "bm-c rows 91 + candidate = 92nd owned", "# candidate = 92nd EXACT",
          "engine_owner==bm-c rows 91 + candidate",
          "bm-c rows {len(bmc_rows_live)} + candidate (92nd own wave",
          "bm-c's 92nd own wave", "NINETY-SECOND owned", "NINETY-THIRD owned",
          "TWO HUNDRED AND SEVENTY-THIRD", "TWO HUNDRED AND SEVENTY-FOURTH",
          "bmc_rows=91", '"probe_receipt_bmc_ordinal_face": 91',
          "bmc rows 91 + candidate 92nd", "TWENTY-SECOND", "TWENTY-THIRD",
          "TWENTY-FOURTH", "twenty-second", "twenty-third", "twenty-fourth",
          "sixty-first", "sixty-one legs", "sixty-second",
          "wave 273 engine_owner=bm-c", '"wave 273: "', "wave 273 = first free number"):
    m(k)
# ---- parity / count / range / cfg faces ----
for k in ("block = 131 rows", "131 parity rows", "block parity = 131 rows",
          'N1_BANDS[") == 130,', '!= 130', 'N1_BANDS[") == 61',
          '"fresh_legs_row_asserts": 25', '+ 25,',
          "range(248, 273)", "range(248, 272)", "range(16, 273)", "range(17, 273)",
          "range(209, 274)", "range(211, 272)", "range(211, 248)", "range(138, 207)",
          "if w < 273)", "if w < 272)", "273 - _lw", "_w == 272",
          "WAVE_CONFIGS[273]", "WAVE_CONFIGS[272]", "N1_BANDS[272]", "get(272)",
          "_c272", '273: {"batch"', '273: {{"batch"', '273: {"a"', '273: {{"a"',
          '272: {"batch"', '272: {"a"', "arith_a273", "arith_b273",
          "(269, 268, 267, 266, 265, 264, 263, 262, 261, 260)",
          "(270, 269, 268, 267, 266, 265, 264, 263, 262, 261)",
          "W260..W269", "W261..W270", "_set_wave(273)", "_set_wave(274)", "_set_wave(2)",
          "W211..W247 legs (37)", "W211..W247 verbatim (37 legs)",
          "W211..W247 thirty-seven legs", 'N1_BANDS[") == 37',
          "W211..W271 legs (61)", "W211..W271 sixty-one legs",
          "W211..W272 legs 61", "own W248..W271", "own W248..W271 legs (24)",
          "own W248..W271" + CRLF + "# legs (24 rows) do NOT enter the estate path",
          "W248..W271 twenty-four legs", 'N1_BANDS[") == 24',
          "W248..W273 legs (25", "W270_W271_W272_bands_respected",
          "post-W272-REGISTERED", "W273 FREEZE UNBLOCKED", "PRE-W273-splice",
          "fourteen-wave", "dual-window parity", '"machine": "bm-c"',
          "derived by the bm-c", "was published AFTER", "physical bytes",
          "m248", "m211", "593901", "registered wave below 263 composes",
          "bm-c own-seat continuity", 'N1_BANDS[248] ==', 'N1_BANDS\\[248\\]',
          "zero skip-claim", "banned gate ADMIT 0 (re-run at freeze window)",
          "bm-a", "w244_a", "w244_b", "n3r1_used245",
          "w244_a holds wave-263 bands"):
    m(k)

# ================= simulation: apply phase-1 + phase-2 =================
sim = t
def s_rep(old, new, expect, tag):
    global sim
    n = sim.count(old)
    assert n == expect, f"SIM [{tag}] count {n} != {expect}: {old[:100]!r}"
    sim = sim.replace(old, new)

# phase 1 -- projections first
s_rep("W274p", "W275p", raw["W274p"], "p1_proj_prefix")
s_rep("W274", "W275", raw["W274"] - raw["W274p"], "p1_proj_plain")
# bands: CONSUMERS first, producers last
s_rep("617_901", "620_101", raw["617_901"], "p1_band_Blo")
s_rep("618_100", "620_300", raw["618_100"], "p1_band_Bhi")
s_rep("617_900", "620_100", raw["617_900"], "p1_band_Ahi")
s_rep("617_700", "619_900", raw["617_700"], "p1_band_naiveAhi")
s_rep("615_901", "618_101", raw["615_901"], "p1_band_Alo_Bnaivelo")
s_rep("616_100", "618_300", raw["616_100"], "p1_band_Bnaivehi")
s_rep("615_701", "617_901", raw["615_701"], "p1_band_naiveAlo_priorBlo")
s_rep("615_900", "618_100", raw["615_900"], "p1_band_priorBhi")
# int-form projections
s_rep("617901", "620101", raw["617901"], "p1_int_projAlo")
s_rep("619900", "622100", raw["619900"], "p1_int_projAhi")
s_rep("618101", "620301", raw["618101"], "p1_int_projBlo")
s_rep("618300", "620500", raw["618300"], "p1_int_projBhi")
# ledger/K
s_rep("1,022,735", "1,024,935", raw["1,022,735"], "p1_ledger_prose")
s_rep("596,320", "598,520", raw["596,320"], "p1_k_prose")
s_rep("1_022_735", "1_024_935", raw["1_022_735"], "p1_ledger_code")
s_rep("596_320", "598_520", raw["596_320"], "p1_k_code")
# builder filename FIRST (consumes its embedded w273_)
s_rep("(E63 canon-clone builder _r1102bmc_build_w273_derive.py)",
      "(E63 canon-clone builder _r1104bmc_build_w274_derive.py)",
      raw["(E63 canon-clone builder _r1102bmc_build_w273_derive.py)"], "p1_builder")
# lc: own first, then upstream
s_rep("n1_w273", "n1_w274", raw["n1_w273"], "p1_n1w273_own")
s_rep("n1w273-", "n1w274-", raw["n1w273-"], "p1_n1w273dash")
s_rep("w273_", "w274_",
      raw["w273_"] - raw["n1_w273_results.json"] - raw["_r1102bmc_build_w273_derive.py"],
      "p1_lc_w273_")
s_rep("n1_w272", "n1_w273", raw["n1_w272"], "p1_n1w272_upstream")
s_rep("w272_", "w273_", raw["w272_"] - raw["n1_w272_results.json"], "p1_lc_w272_")
# receipt paths / lineage / seat
s_rep("_w273bmc_", "_w274bmc_", raw["_w273bmc_"], "p1_receiptpath")
s_rep("_w272bmc_freeze_edits.py template", "_w273bmc_freeze_edits.py template",
      raw["_w272bmc_freeze_edits.py template"], "p1_lineage_template")
s_rep("MSG-20261018-211x-bmc-w273-seat", "MSG-20261019-012x-bmc-w274-seat",
      raw["MSG-20261018-211x-bmc-w273-seat"], "p1_seat_msg")
s_rep('SEAT_ORIGIN = "39e1bb32f1"', 'SEAT_ORIGIN = "70b21a0264"',
      raw['SEAT_ORIGIN = "39e1bb32f1"'], "p1_seat_origin_const")
s_rep("39e1bb32f1 r1101", "70b21a0264 r1102", raw["39e1bb32f1 r1101"], "p1_seat_origin_hdr")
s_rep("c99ee20a4", "04f2127db", raw["c99ee20a4"], "p1_lineage_sha")
# prereg delivery prose
s_rep("(authored 22:4x, banned_direction_gate ADMIT rc0, frozen b6bbb69e92 + surgery-" + CRLF +
      "# delivered to origin 839441a547 + receipts eeb3bf07ad, r1102 window).",
      "(authored 02:2x, banned_direction_gate ADMIT rc0, frozen sha16 ddc158b5047596ea + CAS-" + CRLF +
      "# graft-delivered to origin 6f31f6e073, r1104 window).",
      raw["(authored 22:4x, banned_direction_gate ADMIT rc0, frozen b6bbb69e92 + surgery-" + CRLF +
      "# delivered to origin 839441a547 + receipts eeb3bf07ad, r1102 window)."],
      "p1_prereg_delivery_hdr")
s_rep("(authored 22:4x, banned gate ADMIT rc0, frozen b6bbb69e92 -> surgery-delivered r1102 origin ",
      "(authored 02:2x, banned gate ADMIT rc0, frozen ddc158b5047596ea -> CAS-graft-delivered r1104 origin ",
      raw["(authored 22:4x, banned gate ADMIT rc0, frozen b6bbb69e92 -> surgery-delivered r1102 origin "],
      "p1_prereg_delivery_note")
# header window stamp
s_rep("2026-10-18 23:5x bm-c r1102 splice window", "2026-10-19 02:5x bm-c r1105 splice window",
      raw["2026-10-18 23:5x bm-c r1102 splice window"], "p1_hdr_stamp")
# receipt wave field (mechanical +1)
s_rep('"wave": 272', '"wave": 273', raw['"wave": 272'], "p1_receipt_wave")
# date roll (remaining after the seat-msg rep consumed its 7 embedded dates)
s_rep("20261018", "20261019",
      raw["20261018"] - raw["MSG-20261018-211x-bmc-w273-seat"], "p1_date_roll")

# phase 2 -- D-swaps: own wave FIRST, then upstream
s_rep("W273", "W274", raw["W273"], "p2_own_wave")
s_rep("W272", "W273", raw["W272"], "p2_upstream_wave")

# ---- post-blanket phase-3 needle measurements ----
post = {}
def pm(key):
    post[key] = sim.count(key)
    return post[key]

for k in ("W270_W271_W273_bands_respected", "W271_W272_W273_bands_respected",
          "W211..W273 legs 61", "W211..W272 legs 62",
          "W248..W274 legs (25", "own W248..W271 legs (24)",
          "W211..W271 legs (61)", "W211..W271 sixty-one legs",
          "own W248..W271" + CRLF + "# legs (24 rows) do NOT enter the estate path",
          "W248..W271 twenty-four legs", 'N1_BANDS[") == 24',
          "block = 131 rows", "131 parity rows", "block parity = 131 rows",
          'N1_BANDS[") == 130,', '!= 130', 'N1_BANDS[") == 61',
          '"fresh_legs_row_asserts": 25', '+ 25,',
          "range(248, 273)", "range(248, 272)", "range(16, 273)", "range(17, 273)",
          "range(209, 274)", "range(211, 272)",
          "if w < 273)", "if w < 272)", "273 - _lw", "_w == 272",
          "WAVE_CONFIGS[273]", "WAVE_CONFIGS[272]", "N1_BANDS[272]", "get(272)",
          "_c272", '273: {"batch"', '273: {{"batch"', '273: {"a"', '273: {{"a"',
          '272: {"batch"', '272: {"a"', "arith_a273", "arith_b273",
          "(269, 268, 267, 266, 265, 264, 263, 262, 261, 260)", "W260..W269",
          "_set_wave(273)",
          "bm-c r1102 window", "# r1102 window", "bm-c r1100 splice window",
          "the bm-c r1100 splice window", "# r1100 splice window", "verified r1100",
          "cycle COMPLETE bm-c r1100 closeout 20:4x",
          "bm-c own seat executed at the bm-c r1100 splice window",
          "finalize one-pass bm-c r1100 closeout, ledger",
          "finalize one-pass bm-c r1100 closeout ledger",
          "own-wave full cycle r1100", "bm-c splice generation r1100 window",
          "(bm-c r1100", "r1101 BEFORE this freeze",
          "seat itself r1101; queue-head", "(r1101, queue-head seat-first supply",
          "(r1101 MSG-", "(R272: ",
          "len(owner_rows_live) == 262 and len(bma_rows_live) == 130 and len(bmc_rows_live) == 91",
          "262/130/91", "owner_rows=262 / bma_rows=130 / bmc_rows=91",
          "rows 262 + candidate = 263rd", "; bm-c rows 91 +",
          "bm-c rows 91 + candidate = 92nd owned", "# candidate = 92nd EXACT",
          "engine_owner==bm-c rows 91 + candidate",
          "bm-c rows {len(bmc_rows_live)} + candidate (92nd own wave",
          "bm-c's 92nd own wave", "NINETY-SECOND owned",
          "TWO HUNDRED AND SEVENTY-THIRD", "bmc_rows=91",
          '"probe_receipt_bmc_ordinal_face": 91', "bmc rows 91 + candidate 92nd",
          "TWENTY-SECOND", "TWENTY-THIRD", "twenty-second", "twenty-third",
          "sixty-first", "sixty-one legs",
          "wave 273 engine_owner=bm-c", '"wave 273: "',
          "wave 273 = first free number",
          "615_901", "616_100", "617_700", "617_900", "615_701", "615_900",
          "617_901", "618_100", "620_101", "620_300", "620_100", "619_900",
          "618_101", "618_300",
          "617901", "619900", "618101", "618300",
          "1,022,735", "596,320", "1_022_735", "596_320",
          "w272_", "w273_", "w274_", "n1_w272", "n1_w273", "n1_w274",
          "n1w272-", "n1w273-", "n1w274-",
          "_w272bmc_", "_w273bmc_", "_w274bmc_",
          "W272", "W273", "W274", "W275", "W275p", "W274p",
          "39e1bb32f1", "70b21a0264", "c99ee20a4", "04f2127db",
          "b6bbb69e92", "839441a547", "eeb3bf07ad", "ddc158b5047596ea", "6f31f6e073",
          "MSG-20261018-211x", "MSG-20261019-012x",
          "20261018", "20261019", "2026-10-18",
          "r1100", "r1101", "r1102", "r1104",
          "20:4x", "23:5x", "22:4x",
          "PERPETUAL-N1-W273", "PERPETUAL-N1-W274",
          "PERPETUAL_N1_W273_PREREG", "PERPETUAL_N1_W274_PREREG",
          "post-W273-REGISTERED", "W274 FREEZE UNBLOCKED", "PRE-W274-splice"):
    pm(k)

receipt = {
  "canon": CANON, "canon_blob": blob_wt, "bytes": len(t.encode("utf-8")),
  "eol": {"crlf": crlf, "lf": lf},
  "raw": raw, "post_blanket": post,
  "note": "phase-1+phase-2 simulated; phase-3 needles measured on the simulated text; editor authors FROM these counts",
}
io.open(REPO + "\\" + OUT.replace("/", "\\"), "w", encoding="utf-8", newline="").write(
    json.dumps(receipt, indent=1, ensure_ascii=False))
print("PREFLIGHT OK canon", blob_wt[:16], "bytes", len(t.encode("utf-8")))
print("proj W274p=%d plain=%d | bands Blo=%d Bhi=%d Ahi=%d nAh=%d Alo=%d nBh=%d pB=%d pBhi=%d"
      % (raw["W274p"], raw["W274"] - raw["W274p"], raw["617_901"], raw["618_100"],
         raw["617_900"], raw["617_700"], raw["615_901"], raw["616_100"],
         raw["615_701"], raw["615_900"]))
print("lc w273_=%d (own=%d) w272_=%d (upstream=%d) | W273=%d W272=%d"
      % (raw["w273_"], raw["w273_"] - raw["n1_w273_results.json"] - raw["_r1102bmc_build_w273_derive.py"],
         raw["w272_"], raw["w272_"] - raw["n1_w272_results.json"], raw["W273"], raw["W272"]))
print("post relkey=%d fullspan61=%d fresh25=%d splice_win=%d gone615_901=%d"
      % (post["W270_W271_W273_bands_respected"], post["W211..W273 legs 61"],
         post["W248..W274 legs (25"], post["bm-c r1100 splice window"], post["615_901"]))
