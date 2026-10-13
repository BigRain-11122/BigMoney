# -*- coding: utf-8 -*-
# r976 bm-c derive: W233 -> W234 five-face freeze editor (count-asserted ordered
# transform; fail-closed pair law; protect-restore sentinels for fixed-estate faces).
# Template = committed _w233bmc_freeze_edits.py (50,218-char text, dead-r973 freeze-window
# generation, splice estate committed+pushed by the dead r973 window itself as
# 0ca920362, proven live-fire; residual estate absorbed by r974 260217d39). All wave
# facts shift by token; every machine-derivable fact is re-asserted at editor
# RUNTIME against live template text (fail-closed).
# Sentinel blocks (KEPT/LIVE/LEG231/LEG232/ASM) are extracted from the template at
# RUNTIME by anchored index -- zero hand-transcription of fixed-estate faces (E63 law).
# Census evidence = results/_r977bmc_w234derive_census.py + _r977bmc_w234derive_postsent.py
# re-run THIS window (post-sentinel counts: W233=72 / W232=111 / W231=8 / W230=9 /
# W229=8 / w233_=11(9 self post n1-shift) / w232_=94 / w231_=5(3 standalone + 2
# n1_w231_results rides) / w230_=1(def name; rides sentinel-protected) / w229_=0 /
# n1_w233=5 / n1w233=2 / e58dbcda3=6 (KEPT-internal 1) / 59856ff28=2 /
# 5c90051e0=776b15270=3 ALL inside compound pair regions / MSG-1530=4 / MSG-1345=2
# / dd38a9da8=1 / 8d3a1b78a=2 / executed bm-c r968=2 / r968 window=7(1 KEPT) /
# r968 itself=6(1 KEPT) / r968-continuation=3(1 KEPT) / cf3501cd9=1 /
# probe receipt @ r968 window=2 / r968 15:2x=3 / r968 probe leg0=1 /
# r968 seat-time live face=1 / NINETY-THIRD instance=5 / NINETY-THIRD per probe=1 /
# staircase NINETY-THIRD "=1 / 63rd=6 / bmc_ordinal=63=3 / TWO HUNDRED AND
# THIRTY-THIRD=3 / sixty-third=2 / r973 freeze window=4 / r973 freeze-window
# bundle=2 / r972 prereg derived=1 / r972 window=1 / r972 + freeze splice script
# landed=2 / twenty-second consecutive=2 / seventh consecutive=2 / SEVENTEEN-level=1
# / if w < 233)=5 / range(16, 233)=2 / range(17, 233)=3 / below 233 composes=2 /
# below-233=2 / arith_a233=arith_b233=n3r1_used233=3 / WAVE_CONFIGS[232]=3 /
# WAVE_CONFIGS[233]=2 / pf.N1_BANDS[232]=4 / N1_BANDS.get(232)=1 / _c232=5 /
# '232: {"batch"'=2 / '232: {"a"'=2+1sp / m230=3 / N1_BANDS\[230\]=1 /
# 934_189=508_320=1 / 934,189=508,320=2 / par_sec==88 / par_full==90, /
# != 90 (69 estate=1 / 88-row cut=1 / 91 rows=2 / int(_estate_ws[87])==229 /
# W211..W229 legs=2 / W211..W228 legs=1 / downstream W234 seat NOT yet published=1 /
# publication pending=1 / W234+ projection=naive W234 A window=NINETY-FOURTH instance
# anticipated=2 / probe_receipt_bmc_ordinal_face": 63=1 / KEPT materializer=24
# faces 23 asserts / LIVE _block_kept=24 / LEG231 N1_BANDS[231]=5 / LEG232
# N1_BANDS[232]=5).
# Disclosed deltas vs the mechanical clone (correctness pairs, machine-verifiable
# against the committed W234 probe receipt results/_w234bmc_20261013_probe_receipt.json
# and the W234 seat commit 260217d39):
#  (a) upstream W233-cycle prose written honestly: splice 0ca920362 committed+pushed
#      by the dead r973 window ITSELF (session died pre-closeout; residual estate
#      absorbed by r974 260217d39) + engine self-burn 12/12 (6c1587483+d4cce3ffe)
#      + finalize one-pass r974 19:4x landed in-window 260217d39 (six-gate
#      PRE-FINALIZE correct phase standing law held, eighth consecutive);
#  (b) prereg_bundle note faces age via bare shifts: r972 window->r976 +
#      2a21ef7cc->1193b255 + SEVENTEEN-level->EIGHTEEN-level + r973 freeze
#      window->r976 + twenty-second->twenty-third + W231->W232 (auto);
#  (c) W234 prereg derive full pass landed by the dead r976 window itself (252d5cc95
#      on origin, R34 authored r975 PREP + 18-level replay 46/46) -- THIS window
#      executes as the r976 continuation (r951/r956 absorb precedent: counter at
#      dead-label value -> same-label continuation, advance 976->977).
import os, sys, py_compile, json

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.join(HERE, "_w233bmc_freeze_edits.py")
OUT  = os.path.join(HERE, "_w234bmc_freeze_edits.py")

t = open(BASE, "r", encoding="utf-8", newline="").read()
assert len(t) == 50218, f"template length drift: {len(t)} != 50218"

def rep(old, new, n=1):
    global t
    c = t.count(old)
    assert c == n, f"PAIR FAIL count {c} != {n}: {old[:110]!r}"
    t = t.replace(old, new)

# ---------------- phase 0: sentinels (RUNTIME anchored extraction) ----------------
# KEPT block: W209 estate-source line .. W232 prior-block-kept line (24 assert lines)
k0 = t.index("assert n1_t4.count('    # --- W209 materializer face')")
k1 = t.index("assert n1_t4.count('    # --- W232 materializer face')")
k2 = t.index("\n", k1)
KEPT_ORIG = t[k0:k2]
assert KEPT_ORIG.count("\nassert ") == 23, f"KEPT block shape: {KEPT_ORIG.count(chr(10)+'assert ')}"
assert KEPT_ORIG.count("materializer face") == 24
rep(KEPT_ORIG, "@@KEPT@@", 1)

# LIVE line (liveness_anchors single-line JSON face)
l0 = t.index('"liveness_anchors"')
l0 = t.rindex("\n", 0, l0) + 1
l1 = t.index("\n", l0)
LIVE_ORIG = t[l0:l1]
assert LIVE_ORIG.count("_block_kept") == 24, f"LIVE shape: {LIVE_ORIG.count('_block_kept')}"  # w209..w232
rep(LIVE_ORIG, "@@LIVE@@", 1)

# LEG231 (template w231_leg def, 6 lines) -- protected from w231_->w232_ + W231->W232 aging
g0 = t.index("w231_leg = [")
g2 = t.index("\n]", g0) + 2
LEG231_ORIG = t[g0:g2]
assert LEG231_ORIG.count("N1_BANDS[231]") == 5 and LEG231_ORIG.count("W231 row parity drift") == 1
rep(LEG231_ORIG, "@@LEG231@@", 1)

# LEG232 (template w232_leg def, 6 lines) -- protected from w232_->w233_ + W232->W233 aging
h0 = t.index("w232_leg = [")
h2 = t.index("\n]", h0) + 2
LEG232_ORIG = t[h0:h2]
assert LEG232_ORIG.count("N1_BANDS[232]") == 5 and LEG232_ORIG.count("W232 row parity drift") == 1
rep(LEG232_ORIG, "@@LEG232@@", 1)

# ASM join line (RUNTIME anchored extraction -- E63 law: zero hand-transcription)
a0 = t.index("block = EOL.join(hdr)")
a1 = t.index("\n", a0)
ASM_ORIG = t[a0:a1]
assert ASM_ORIG.count("EOL.join(w230_leg)") == 1 and ASM_ORIG.count("EOL.join(w231_leg)") == 1 \
    and ASM_ORIG.count("EOL.join(w232_leg)") == 1 and ASM_ORIG.count("EOL.join(tail)") == 1, \
    f"ASM shape: {ASM_ORIG!r}"
rep(ASM_ORIG, "@@ASM@@", 1)

# ---------------- phase 1: ordered global shifts (descending, count-logged) ----------------
SHIFTS = [
 # --- self wave faces (W233 -> W234) ---
 ("n1_w233", "n1_w234", 5),            # self shard/out names (BEFORE w233_ var shift, substring law)
 ("w233_", "w234_", 9),               # self vars (census 11 - 2 n1_w233_results rides = 9)
 ("n1w233", "n1w234", 2),              # entry-identity tags
 ("W233", "W234", 72),                # self prose global (incl. PERPETUAL_N1_W233_PREREG x5 + batch x2)
 ("_w233bmc_20261013_probe_receipt.json", "_w234bmc_20261013_probe_receipt.json", 9),
 ("_w233bmc_freeze_receipt.json", "_w234bmc_freeze_receipt.json", 1),
 ("_w232bmc_freeze_edits.py", "_w233bmc_freeze_edits.py", 1),   # lineage template name (upstream->self)
 ("_set_wave(233)", "_set_wave(234)", 1),
 ('"wave": 233,', '"wave": 234,', 1),
 ("f'{CFG_I}233: ", "f'{CFG_I}234: ", 1),
 ("f'{ROW_I}233: ", "f'{ROW_I}234: ", 1),
 ("f'233: {{\"a\":", "f'234: {{\"a\":", 1),
 ("ROW_I + '233: {\"a\"'", "ROW_I + '234: {\"a\"'", 1),
 ("WAVE_CONFIGS[233]", "WAVE_CONFIGS[234]", 2),       # band-facts self asserts (BEFORE the [232]->[233] mirror shift)
 ("seat MSG-1233 tail", "seat MSG-1234 tail", 1),
 ("wave 233 = first free number", "wave 234 = first free number", 1),
 ("wave 233: ", "wave 234: ", 1),
 ("if w < 233)", "if w < 234)", 5),
 ("range(16, 233)", "range(16, 234)", 2),
 ("range(17, 233)", "range(17, 234)", 3),
 ("w<233 count", "w<234 count", 1),
 ("if w < 232", "if w < 233", 1),          # family-6 prior-wave 0-check (no paren tail -- distinct face)
 ("w<232 leaked", "w<233 leaked", 1),     # family-6 prior-wave leak prose
 ("below 233 composes", "below 234 composes", 2),
 ("below-233", "below-234", 2),
 ("arith_a233", "arith_a234", 3),
 ("arith_b233", "arith_b234", 3),
 ("n3r1_used233", "n3r1_used234", 3),
 # --- projection aging (W234 -> W235) ---
 ("W234+ projection", "W235+ projection", 2),
 ("naive W234 A window", "naive W235 A window", 2),
 ("W234 freezer", "W235 freezer", 1),
 ("W234+ freezer", "W235+ freezer", 1),
 ("downstream W234 seat NOT yet published", "downstream W235 seat NOT yet published", 1),
 ("downstream W234 seat publication pending", "downstream W235 seat publication pending", 1),
 ("NINETY-FOURTH instance anticipated", "NINETY-FIFTH instance anticipated", 2),
 # --- self ordinal/prose aging ---
 ("NINETY-THIRD instance", "NINETY-FOURTH instance", 5),
 ("TWO HUNDRED AND THIRTY-THIRD", "TWO HUNDRED AND THIRTY-FOURTH", 3),
 ("sixty-third", "sixty-fourth", 2),
 ("63rd", "64th", 6),
 ("bmc_ordinal=63", "bmc_ordinal=64", 3),
 ("rows 62 + candidate", "rows 63 + candidate", 4),
 ("rows 222 + candidate", "rows 223 + candidate", 1),
 ("== 222 and len(bmc_rows_live) == 62", "== 223 and len(bmc_rows_live) == 63", 1),
 ("expect 222/62", "expect 223/63", 1),
 ("precedent 221/61 pre-splice", "precedent 222/62 pre-splice", 1),
 ("splice 222/62", "splice 223/63", 1),
 ("r973 freeze window", "r976 freeze window", 4),
 ("r973 freeze-window bundle", "r976 freeze-window bundle", 2),
 ("r972 prereg derived", "r976 prereg derived", 1),
 ("r972 window", "r976 window", 1),
 ("r972 + freeze splice script landed", "r976 + freeze splice script landed", 2),
 ("twenty-second consecutive", "twenty-third consecutive", 2),
 ("seventh consecutive", "eighth consecutive", 2),
 ("SEVENTEEN-level", "EIGHTEEN-level", 1),
 # --- seat/provenance aging (self swap FIRST, then upstream) ---
 ("MSG-20261013-1530-bmc", "MSG-20261013-1955-bmc", 4),   # self seat swap FIRST
 ("MSG-20261013-1345-bmc", "MSG-20261013-1530-bmc", 2),   # upstream seat AFTER self swap
 ("dd38a9da8", "260217d39", 1),                            # SEAT_ORIGIN BEFORE 8d3a1b78a aging
 ("8d3a1b78a", "dd38a9da8", 2),                            # upstream seat-origin provenance x2
 ("2a21ef7cc4eaaa70375c7e4baec99f423488d5e2", "1193b255531f7aadcdff050069371c5e5169b11f", 1),  # self prereg sha
 # --- band/ledger fact aging (self W233 facts -> W234 facts) ---
 ("(527_404, 529_403)", "(529_604, 531_603)", 1),
 ("(529_404, 529_603)", "(531_604, 531_803)", 1),
 ("934_189", "936_389", 1),
 ("508_320", "510_520", 1),
 ("934,189", "936,389", 2),
 ("508,320", "510,520", 2),
 # --- upstream cycle shas aging ---
 ("e58dbcda3", "0ca920362", 6),            # KEPT-internal 1 excluded by sentinel
 ("59856ff28", "260217d39", 2),
 # engine-append shas (5c90051e0/776b15270) carried ENTIRELY by the P9/P10/receipt
 # upstream pairs (census: 3/3, ALL inside "5c90051e0+776b15270" compound pair
 # regions, zero standalone -- carried to 6c1587483+d4cce3ffe by authored pairs)
 ("r968 15:2x", "r974 19:4x", 3),
 ("probe receipt @ r968 window", "probe receipt @ r974 window", 2),
 ("r968 probe leg0", "r974 probe leg0", 1),
 ("r968 seat-time live face", "r974 seat-time live face", 1),
 # --- upstream wave faces (W232 -> W233; descending) ---
 ("W232", "W233", 111),               # upstream prose global (census 114 - KEPT-internal 2 - LEG232-internal 1)
 ("w232_", "w233_", 94),              # upstream vars (incl. 4 n1_w232_results rides; LEG232/ASM/LIVE sentinel-excluded)
 ("W231", "W232", 8),                 # upstream-upstream prose (census 8 post-sentinels)
 ("w231_", "w232_", 5),              # upstream-upstream vars (3 standalone + 2 n1_w231_results rides; LEG231 sentinel-excluded)
 ("W230", "W231", 9),                # upstream-upstream-upstream prose (incl. w230_leg def interior; LEG230-free generation)
 ("w230_", "w231_", 1),              # w230_leg def name ONLY (ASM/LIVE rides sentinel-excluded; pair renames to w233_leg def)
 ("W229", "W230", 8),                # estate prose (KEPT-internal 2 excluded by sentinel)
 ("m230", "m231", 3),
 ("N1_BANDS\\[230\\]", "N1_BANDS\\[231\\]", 1),   # m-cut regex literal (raw-bracket form)
 ("_c232", "_c233", 5),
 ("'232: {\"batch\"'", "'233: {\"batch\"'", 2),   # upstream cfg needles
 ("'232: {\"a\"'", "'233: {\"a\"'", 2),           # upstream row needles
 ("'    232: {\"a\"'", "'    233: {\"a\"'", 1),
 ("N1_BANDS.get(232)", "N1_BANDS.get(233)", 1),
 ("WAVE_CONFIGS[232]", "WAVE_CONFIGS[233]", 3),       # upstream mirror asserts (AFTER self [233]->[234])
 ("pf.N1_BANDS[232]", "pf.N1_BANDS[233]", 4),   # mirror x3 + post-edit gate x1 (LEG232-internal assert face excluded)
]
def shift_text(s):
    for old, new, _ in SHIFTS:
        s = s.replace(old, new)
    return s
for old, new, mn in SHIFTS:
    c = t.count(old)
    assert c == mn, f"SHIFT FAIL count {c} != {mn}: {old!r}"
    t = t.replace(old, new)
    print(f"  shift {mn:3d}x {old[:58]!r}")
