# -*- coding: utf-8 -*-
# r1108 bm-c splice window: W275 editor needle preflight (r1077 MEASURED-counts law).
# Measures every needle count on the committed W274 freeze-edits canon
# (results/_w274bmc_freeze_edits.py, proven live-fire: W274 five-face splice
# ec907d164 + engine self-burn 12/12 + finalize one-pass acf37937ec ledger
# 1,027,135 / K=600,720, bm-c r1105 window) and simulates the phase-1
# (pre-D-swap) + phase-2 (W-blanket) transforms to measure the post-blanket
# phase-3 needle forms. Zero hand-assumed counts: the editor is authored
# FROM this receipt.
# W275 FACTS (probe receipt results/_w275bmc_20261019_probe_receipt.json,
# committed with the seat @ bf4bbbde1 r1106, ADMIT): bands A 620_301..622_300
# (TWENTY-FOURTH consecutive A-hop, staircase-affects-A, hops=1; naive A
# 620_101..622_100 refused at the registered W274 B band 620_101..620_300) /
# B 622_301..622_500 (TWENTY-FIFTH consecutive above-own-A, own-A reservation
# cascade, hops=1; naive B 620_301..620_500 inside the own-A window
# 620_301..622_300); seed_admit FREE x2 (base=620301 span=2000 /
# base=622301 span=200); ordinals owner 264 + candidate = 265th / bm-c rows
# 93 + candidate = 94th; W274 finalize anchors 1,027,135 / K=600,720.
# W275 PREREG: research/PERPETUAL_N1_W275_PREREG.md 23,551B sha256_16
# e4e1ce44f5afd03b (authored 04:4x bm-c r1107 window via E63 canon-clone
# builder _r1107bmc_build_w275_derive.py; pushed FIRST-TRY to origin
# 1fcc0bc30f, no CAS graft needed).
# DATE-ROLL FACE this generation: count 0 -- canon receipts already dated
# 20261019 and the W275 seat/probe receipts are same-date; NO p1_date_roll rep.
import io, json, subprocess, sys

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
CANON = "results/_w274bmc_freeze_edits.py"
OUT = "results/_r1108bmc_needle_preflight.json"
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
m("W275p"); m("W275"); m("W276p")
# ---- bands (underscore faces: own registered + naive + prior) ----
for k in ("620_101", "620_300", "620_100", "619_900", "618_101", "618_300",
          "617_901", "618_100", "622_301", "622_500", "622_300", "622_100",
          "620_301", "620_500"):
    m(k)
# ---- int-form projections ----
for k in ("620101", "622100", "620301", "620500", "622301", "624300",
          "622501", "622700"):
    m(k)
# ---- ledger/K ----
for k in ("1,024,935", "598,520", "1_024_935", "598_520", "1,027,135", "600,720"):
    m(k)
# ---- lc machine tokens ----
for k in ("n1_w274", "n1_w274_results.json", "n1w274-", "w274_",
          "n1_w273", "n1_w273_results.json", "w273_", "w275_",
          "_r1104bmc_build_w274_derive.py", "_r1107bmc_build_w275_derive.py"):
    m(k)
# ---- receipt paths / lineage / seat ----
for k in ("_w274bmc_", "_w273bmc_", "_w273bmc_freeze_edits.py template",
          "_w274bmc_freeze_edits.py template",
          "MSG-20261019-012x-bmc-w274-seat", "MSG-20261019-034x-bmc-w275-seat",
          'SEAT_ORIGIN = "70b21a0264"', 'SEAT_ORIGIN = "bf4bbbde1"',
          "70b21a0264", "70b21a0264 r1102", "bf4bbbde1", "04f2127db", "ec907d164",
          "acf37937ec", "c4e752d682"):
    m(k)
# ---- prereg delivery prose faces ----
m("(authored 02:2x, banned_direction_gate ADMIT rc0, frozen sha16 ddc158b5047596ea + CAS-" + CRLF +
  "# graft-delivered to origin 6f31f6e073, r1104 window).")
m("(E63 canon-clone builder _r1104bmc_build_w274_derive.py)")
m("(E63 canon-clone builder derive landed pre-freeze")
m("(authored 02:2x, banned gate ADMIT rc0, frozen ddc158b5047596ea -> CAS-graft-delivered r1104 origin ")
for k in ("bm-c r1104 window", "# r1104 window", "bm-c r1107 window",
          "ddc158b5047596ea", "6f31f6e073", "e4e1ce44f5afd03b", "1fcc0bc30f",
          "authored 04:4x", "authored 02:2x"):
    m(k)
# ---- window stamps ----
for k in ("2026-10-19 02:5x bm-c r1105 splice window",
          "bm-c r1102 splice window", "the bm-c r1102 splice window",
          "# r1102 splice window", "verified r1102",
          "cycle COMPLETE bm-c r1102 closeout 01:0x",
          "bm-c own seat executed at the bm-c r1102 splice window",
          "finalize one-pass bm-c r1102 closeout, ledger",
          "finalize one-pass bm-c r1102 closeout ledger",
          "own-wave full cycle r1102", "bm-c splice generation r1102 window",
          "(bm-c r1102", "r1102 BEFORE this freeze",
          "seat itself r1102; queue-head", "(r1102, queue-head seat-first supply",
          "(r1102 MSG-", "(R273: ", "r1102", "r1104", "r1106", "r1108"):
    m(k)
# ---- dates / receipt wave ----
for k in ("20261018", "2026-10-18", '"wave": 272', '"wave": 273', '"wave": 274',
          "20261019"):
    m(k)
# ---- phase-2 blanket counts ----
m("W274"); m("W273"); m("W272"); m("W276")
# ---- ordinal faces ----
for k in ("len(owner_rows_live) == 263 and len(bma_rows_live) == 130 and len(bmc_rows_live) == 92",
          "263/130/92", "owner_rows=263 / bma_rows=130 / bmc_rows=92",
          "rows 263 + candidate = 264th", "; bm-c rows 92 +",
          "bm-c rows 92 + candidate = 93rd owned", "# candidate = 93rd EXACT",
          "engine_owner==bm-c rows 92 + candidate",
          "bm-c rows {len(bmc_rows_live)} + candidate (93rd own wave",
          "bm-c's 93rd own wave", "NINETY-THIRD owned", "NINETY-FOURTH owned",
          "TWO HUNDRED AND SEVENTY-FOURTH", "TWO HUNDRED AND SEVENTY-FIFTH",
          "bmc_rows=92", '"probe_receipt_bmc_ordinal_face": 92',
          "bmc rows 92 + candidate 93rd", "TWENTY-THIRD", "TWENTY-FOURTH",
          "TWENTY-FIFTH", "twenty-third", "twenty-fourth", "twenty-fifth",
          "sixty-second", "sixty-two legs", "sixty-third",
          "wave 274 engine_owner=bm-c", '"wave 274: "',
          "wave 274 = first free number"):
    m(k)
# ---- parity / count / range / cfg faces ----
for k in ("block = 132 rows", "132 parity rows", "block parity = 132 rows",
          'N1_BANDS[") == 131,', '!= 131', 'N1_BANDS[") == 62',
          '"fresh_legs_row_asserts": 26', '+ 26,',
          "range(248, 274)", "range(248, 273)", "range(16, 274)", "range(17, 274)",
          "range(209, 275)", "range(211, 273)", "range(211, 248)", "range(138, 207)",
          "if w < 274)", "if w < 273)", "274 - _lw", "_w == 273", "_w == 272",
          "WAVE_CONFIGS[274]", "WAVE_CONFIGS[273]", "N1_BANDS[273]", "get(273)",
          "_c273", '274: {"batch"', '274: {{"batch"', '274: {"a"', '274: {{"a"',
          '273: {"batch"', '273: {{"batch"', '273: {"a"', '273: {{"a"',
          '272: {"batch"', '272: {"a"',
          "arith_a274", "arith_b274", "arith_a273", "arith_b273",
          "(270, 269, 268, 267, 266, 265, 264, 263, 262, 261)",
          "(271, 270, 269, 268, 267, 266, 265, 264, 263, 262)",
          "W260..W269", "W261..W270", "_set_wave(274)", "_set_wave(275)", "_set_wave(2)",
          "W211..W247 legs (37)", "W211..W247 verbatim (37 legs)",
          "W211..W247 thirty-seven legs", 'N1_BANDS[") == 37',
          "W211..W272 legs (62)", "W211..W272 sixty-two legs",
          "W211..W273 legs 62", "own W248..W272", "own W248..W272 legs (25)",
          "own W248..W272" + CRLF + "# legs (25 rows) do NOT enter the estate path",
          "W248..W272 twenty-five legs", 'N1_BANDS[") == 25',
          "W248..W274 legs (26", "W271_W272_W273_bands_respected",
          "post-W273-REGISTERED", "post-W273 registration", "W274 FREEZE UNBLOCKED",
          "PRE-W274-splice",
          "fourteen-wave", "dual-window parity", '"machine": "bm-c"',
          "derived by the bm-c", "was published AFTER", "physical bytes",
          "m248", "m211", "593901", "registered wave below 263 composes",
          "bm-c own-seat continuity", 'N1_BANDS[248] ==', 'N1_BANDS\\[248\\]',
          "zero skip-claim", "banned gate ADMIT 0 (re-run at freeze window)",
          "bm-a", "w244_a", "w244_b", "n3r1_used245",
          "w244_a holds wave-263 bands",
          "PERPETUAL_N1_W274_PREREG", "PERPETUAL_N1_W273_PREREG",
          "PERPETUAL-N1-W274", "PERPETUAL-N1-W273",
          "W274 materializer face", "W273 materializer face",
          "W273 finalize product", "W272 finalize product",
          "W275 walk", "sixty-second consecutive",
          "anchors W273 1,024,935 / K=598,520 at draft",
          "bm-c five-face freeze upstream seat", "bm-c (upstream seat honored)",
          "owner=bm-c seat honored", "expect 263/130/92"):
    m(k)

# ================= simulation: apply phase-1 + phase-2 =================
sim = t
def s_rep(old, new, expect, tag):
    global sim
    n = sim.count(old)
    assert n == expect, f"SIM [{tag}] count {n} != {expect}: {old[:100]!r}"
    sim = sim.replace(old, new)

# phase 1 -- projections first
s_rep("W275p", "W276p", raw["W275p"], "p1_proj_prefix")
s_rep("W275", "W276", raw["W275"] - raw["W275p"], "p1_proj_plain")
# bands: CONSUMERS first, producers last
s_rep("620_101", "622_301", raw["620_101"], "p1_band_Blo")
s_rep("620_300", "622_500", raw["620_300"], "p1_band_Bhi")
s_rep("620_100", "622_300", raw["620_100"], "p1_band_Ahi")
s_rep("619_900", "622_100", raw["619_900"], "p1_band_naiveAhi")
s_rep("618_101", "620_301", raw["618_101"], "p1_band_Alo_Bnaivelo")
s_rep("618_300", "620_500", raw["618_300"], "p1_band_Bnaivehi")
s_rep("617_901", "620_101", raw["617_901"], "p1_band_naiveAlo_priorBlo")
s_rep("618_100", "620_300", raw["618_100"], "p1_band_priorBhi")
# int-form projections
s_rep("620101", "622301", raw["620101"], "p1_int_projAlo")
s_rep("622100", "624300", raw["622100"], "p1_int_projAhi")
s_rep("620301", "622501", raw["620301"], "p1_int_projBlo")
s_rep("620500", "622700", raw["620500"], "p1_int_projBhi")
# ledger/K
s_rep("1,024,935", "1,027,135", raw["1,024,935"], "p1_ledger_prose")
s_rep("598,520", "600,720", raw["598,520"], "p1_k_prose")
s_rep("1_024_935", "1_027_135", raw["1_024_935"], "p1_ledger_code")
s_rep("598_520", "600_720", raw["598_520"], "p1_k_code")
# builder filename FIRST (consumes its embedded w274_)
s_rep("(E63 canon-clone builder _r1104bmc_build_w274_derive.py)",
      "(E63 canon-clone builder _r1107bmc_build_w275_derive.py)",
      raw["(E63 canon-clone builder _r1104bmc_build_w274_derive.py)"], "p1_builder")
# lc: own first, then upstream
s_rep("n1_w274", "n1_w275", raw["n1_w274"], "p1_n1w274_own")
s_rep("n1w274-", "n1w275-", raw["n1w274-"], "p1_n1w274dash")
s_rep("w274_", "w275_",
      raw["w274_"] - raw["n1_w274_results.json"] - raw["_r1104bmc_build_w274_derive.py"],
      "p1_lc_w274_")
s_rep("n1_w273", "n1_w274", raw["n1_w273"], "p1_n1w273_upstream")
s_rep("w273_", "w274_", raw["w273_"] - raw["n1_w273_results.json"], "p1_lc_w273_")
# receipt paths / lineage / seat
s_rep("_w274bmc_", "_w275bmc_", raw["_w274bmc_"], "p1_receiptpath")
s_rep("_w273bmc_freeze_edits.py template", "_w274bmc_freeze_edits.py template",
      raw["_w273bmc_freeze_edits.py template"], "p1_lineage_template")
s_rep("MSG-20261019-012x-bmc-w274-seat", "MSG-20261019-034x-bmc-w275-seat",
      raw["MSG-20261019-012x-bmc-w274-seat"], "p1_seat_msg")
s_rep('SEAT_ORIGIN = "70b21a0264"', 'SEAT_ORIGIN = "bf4bbbde1"',
      raw['SEAT_ORIGIN = "70b21a0264"'], "p1_seat_origin_const")
s_rep("70b21a0264 r1102", "bf4bbbde1 r1106", raw["70b21a0264 r1102"], "p1_seat_origin_hdr")
s_rep("04f2127db", "ec907d164", raw["04f2127db"], "p1_lineage_sha")
# prereg delivery prose
s_rep("(authored 02:2x, banned_direction_gate ADMIT rc0, frozen sha16 ddc158b5047596ea + CAS-" + CRLF +
      "# graft-delivered to origin 6f31f6e073, r1104 window).",
      "(authored 04:4x, banned_direction_gate ADMIT rc0, frozen sha16 e4e1ce44f5afd03b + pushed-" + CRLF +
      "# first-try to origin 1fcc0bc30f, r1107 window).",
      raw["(authored 02:2x, banned_direction_gate ADMIT rc0, frozen sha16 ddc158b5047596ea + CAS-" + CRLF +
      "# graft-delivered to origin 6f31f6e073, r1104 window)."],
      "p1_prereg_delivery_hdr")
s_rep("(authored 02:2x, banned gate ADMIT rc0, frozen ddc158b5047596ea -> CAS-graft-delivered r1104 origin ",
      "(authored 04:4x, banned gate ADMIT rc0, frozen e4e1ce44f5afd03b -> pushed first-try r1107 origin ",
      raw["(authored 02:2x, banned gate ADMIT rc0, frozen ddc158b5047596ea -> CAS-graft-delivered r1104 origin "],
      "p1_prereg_delivery_note")
# header window stamp
s_rep("2026-10-19 02:5x bm-c r1105 splice window", "2026-10-19 05:0x bm-c r1108 splice window",
      raw["2026-10-19 02:5x bm-c r1105 splice window"], "p1_hdr_stamp")
# receipt wave field (mechanical +1)
s_rep('"wave": 273', '"wave": 274', raw['"wave": 273'], "p1_receipt_wave")
# DATE ROLL: ZERO this generation (20261019 == 20261019) -- no rep, disclosed

# phase 2 -- D-swaps: own wave FIRST, then upstream
s_rep("W274", "W275", raw["W274"], "p2_own_wave")
s_rep("W273", "W274", raw["W273"], "p2_upstream_wave")

# ---- post-blanket phase-3 needle measurements ----
post = {}
def pm(key):
    post[key] = sim.count(key)
    return post[key]

for k in ("W271_W272_W274_bands_respected", "W272_W273_W274_bands_respected",
          "W211..W274 legs 62", "W211..W273 legs 63",
          "W248..W275 legs (26", "own W248..W273 legs (26)",
          "W211..W272 legs (62)", "W211..W272 sixty-two legs",
          "own W248..W273" + CRLF + "# legs (26 rows) do NOT enter the estate path",
          "W248..W273 twenty-six legs", 'N1_BANDS[") == 26',
          "block = 133 rows", "133 parity rows", "block parity = 133 rows",
          'N1_BANDS[") == 132,', '!= 132', 'N1_BANDS[") == 63',
          '"fresh_legs_row_asserts": 27', '+ 27,',
          "range(248, 275)", "range(248, 274)", "range(16, 275)", "range(17, 275)",
          "range(209, 276)", "range(211, 274)",
          "if w < 275)", "if w < 274)", "275 - _lw", "_w == 274",
          "WAVE_CONFIGS[275]", "WAVE_CONFIGS[274]", "N1_BANDS[274]", "get(274)",
          "_c274", '275: {"batch"', '275: {{"batch"', '275: {"a"', '275: {{"a"',
          '274: {"batch"', '274: {"a"', "arith_a275", "arith_b275",
          "(271, 270, 269, 268, 267, 266, 265, 264, 263, 262)", "W262..W271",
          "_set_wave(275)",
          "bm-c r1107 window", "# r1107 window", "bm-c r1105 splice window",
          "the bm-c r1105 splice window", "# r1105 splice window", "verified r1105",
          "cycle COMPLETE bm-c r1105 closeout 03:2x",
          "bm-c own seat executed at the bm-c r1105 splice window",
          "finalize one-pass bm-c r1105 closeout, ledger",
          "finalize one-pass bm-c r1105 closeout ledger",
          "own-wave full cycle r1105", "bm-c splice generation r1105 window",
          "(bm-c r1105", "r1106 BEFORE this freeze",
          "seat itself r1106; queue-head", "(r1106, queue-head seat-first supply",
          "(r1106 MSG-", "(R274: ",
          "len(owner_rows_live) == 264 and len(bma_rows_live) == 130 and len(bmc_rows_live) == 93",
          "264/130/93", "owner_rows=264 / bma_rows=130 / bmc_rows=93",
          "rows 264 + candidate = 265th", "; bm-c rows 93 +",
          "bm-c rows 93 + candidate = 94th owned", "# candidate = 94th EXACT",
          "engine_owner==bm-c rows 93 + candidate",
          "bm-c rows {len(bmc_rows_live)} + candidate (94th own wave",
          "bm-c's 94th own wave", "NINETY-FOURTH owned",
          "TWO HUNDRED AND SEVENTY-FIFTH", "bmc_rows=93",
          '"probe_receipt_bmc_ordinal_face": 93', "bmc rows 93 + candidate 94th",
          "TWENTY-FOURTH", "TWENTY-FIFTH", "twenty-fourth", "twenty-fifth",
          "sixty-third", "sixty-three legs",
          "wave 275 engine_owner=bm-c", '"wave 275: "',
          "wave 275 = first free number",
          "620_100", "619_900", "618_101", "618_300", "617_901", "618_100",
          "620_101", "620_300", "622_301", "622_500", "622_300", "622_100",
          "620_301", "620_500",
          "620101", "622100", "620301", "620500",
          "622301", "624300", "622501", "622700",
          "1,024,935", "598,520", "1_024_935", "598_520",
          "1,027,135", "600,720",
          "w273_", "w274_", "w275_", "n1_w273", "n1_w274", "n1_w275",
          "n1w273-", "n1w274-", "n1w275-",
          "_w273bmc_", "_w274bmc_", "_w275bmc_",
          "W272", "W273", "W274", "W275", "W275p", "W276", "W276p",
          "70b21a0264", "bf4bbbde1", "04f2127db", "ec907d164",
          "ddc158b5047596ea", "6f31f6e073", "e4e1ce44f5afd03b", "1fcc0bc30f",
          "MSG-20261019-012x", "MSG-20261019-034x",
          "20261018", "20261019", "2026-10-18",
          "r1102", "r1104", "r1106", "r1107", "r1108",
          "01:0x", "02:2x", "04:4x",
          "PERPETUAL-N1-W274", "PERPETUAL-N1-W275",
          "PERPETUAL_N1_W274_PREREG", "PERPETUAL_N1_W275_PREREG",
          "post-W274-REGISTERED", "W275 FREEZE UNBLOCKED", "PRE-W275-splice",
          "post-W274 registration", "W276 walk",
          "anchors W274 1,027,135 / K=600,720 at draft",
          "expect 264/130/93",
          "W275 materializer face", "W274 materializer face",
          "W274 finalize product", "W273 finalize product",
          "sixty-third consecutive", '"wave": 274',
          "w244_a", "w244_b", "n3r1_used245", "m248", "m211",
          "fourteen-wave", "bm-a"):
    pm(k)

receipt = {
  "canon": CANON, "canon_blob": blob_wt, "bytes": len(t.encode("utf-8")),
  "eol": {"crlf": crlf, "lf": lf},
  "raw": raw, "post_blanket": post,
  "note": "phase-1+phase-2 simulated; phase-3 needles measured on the simulated text; editor authors FROM these counts; DATE-ROLL count 0 this generation (20261019==20261019)",
}
io.open(REPO + "\\" + OUT.replace("/", "\\"), "w", encoding="utf-8", newline="").write(
    json.dumps(receipt, indent=1, ensure_ascii=False))
print("PREFLIGHT OK canon", blob_wt[:16], "bytes", len(t.encode("utf-8")))
print("proj W275p=%d plain=%d | bands Blo=%d Bhi=%d Ahi=%d nAh=%d Alo=%d nBh=%d pB=%d pBhi=%d"
      % (raw["W275p"], raw["W275"] - raw["W275p"], raw["620_101"], raw["620_300"],
         raw["620_100"], raw["619_900"], raw["618_101"], raw["618_300"],
         raw["617_901"], raw["618_100"]))
print("lc w274_=%d (own=%d) w273_=%d (upstream=%d) | W274=%d W273=%d"
      % (raw["w274_"], raw["w274_"] - raw["n1_w274_results.json"] - raw["_r1104bmc_build_w274_derive.py"],
         raw["w273_"], raw["w273_"] - raw["n1_w273_results.json"], raw["W274"], raw["W273"]))
print("post relkey=%d fullspan62=%d fresh26=%d splice_win=%d gone618_101=%d"
      % (post["W271_W272_W274_bands_respected"], post["W211..W274 legs 62"],
         post["W248..W275 legs (26"], post["bm-c r1105 splice window"], post["618_101"]))
