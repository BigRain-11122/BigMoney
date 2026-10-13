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

# ---------------- phase 2: pairs (shift-derived anchors, final new text) ----------------
def pair(orig_old, new, n=1):
    global t
    old = shift_text(orig_old)
    c = t.count(old)
    assert c == n, f"PAIR FAIL count {c} != {n}: {old[:110]!r}"
    t = t.replace(old, new)

# --- header blocks ---
pair("""# 2026-10-13 19:2x bm-c r973 freeze window (upstream W1..W232 ALL LANDED, clean precondition): W233 five-face freeze splice editor.""",
"""# 2026-10-13 21:2x bm-c r976 freeze window (upstream W1..W233 ALL LANDED, clean precondition): W234 five-face freeze splice editor.""")
# regression guards for the window-label pair (new side must carry the SHIFTED wave faces)
assert t.count("(upstream W1..W233 ALL LANDED, clean precondition): W234 five-face") == 1
assert t.count("W233 five-face freeze splice editor") == 0

pair("""# present (W232 finalize one-pass r968 15:2x landed in-window 59856ff28; splice
# estate e58dbcda3 committed+pushed by r968 itself in the r968 window (session
# died post-S6 pre-closeout; residual estate absorbed by the r968-continuation cf3501cd9), net chain head 934,189, merged pool K=508,320,
# n1_w232_results.json machine-read) -- ZERO in-flight upstream seats,""",
"""# present (W233 finalize one-pass r974 19:4x landed in-window 260217d39 (r974 absorb closeout); splice
# estate 0ca920362 committed+pushed by the dead r973 window itself (session
# died pre-closeout; residual estate absorbed by r974), net chain head 936,389, merged pool K=510,520,
# n1_w233_results.json machine-read) -- ZERO in-flight upstream seats,""")

pair("""# Lineage: _w232bmc_freeze_edits.py pattern (proven live-fire freeze,
# e58dbcda3 committed+pushed by r968 itself, machine-verified by
# the r968-continuation closeout receipt) + r787 preflight law + r609""",
"""# Lineage: _w233bmc_freeze_edits.py pattern (proven live-fire freeze,
# 0ca920362 committed+pushed by the dead r973 window itself, machine-verified by
# the r974-absorb closeout receipt) + r787 preflight law + r609""")

pair("""# LHS/RHS/comment ATOMIC TRIPLE absorbed (the new block's w<233>/
# range(16,233)/below-233 triple is count-asserted atomically; the W232
# block's own w<232 face is legitimate prior-wave boundary, not stale).""",
"""# LHS/RHS/comment ATOMIC TRIPLE absorbed (the new block's w<234>/
# range(16,234)/below-234 triple is count-asserted atomically; the W233
# block's own w<233 face is legitimate prior-wave boundary, not stale).""")

# --- transitive window slide (multi-wave faces the global shifts corrupt) ---
pair('f"W232+W231+W230+W229+W228 finalize products present "',
     'f"W233+W232+W231+W230+W229 finalize products present "')

pair("""# (chain-order precondition; W231/W230/W229/W228 finalize are transitive deps of the
# W233 freeze and are belt-and-braces checked here + enforced by the block's
# cumulative-deps assert range(17, 233) at selftest time)""",
"""# (chain-order precondition; W232/W231/W230/W229 finalize are transitive deps of the
# W234 freeze and are belt-and-braces checked here + enforced by the block's
# cumulative-deps assert range(17, 234) at selftest time)""")

# --- structural-choice provenance fixup (post-shift anchors) ---
pair("""# (r968 window editor, estate committed+pushed by r968 itself as e58dbcda3), structure known. The W232 block span ends where the""",
"""# (dead-r973 window editor, estate committed+pushed by the dead r973 window itself as 0ca920362), structure known. The W233 block span ends where the""")

# --- seat/prose fixups (post-shift anchors) ---
pair(" " + "MSG-20261013-1345-bmc, executed bm-c r968 (seat 8d3a1b78a); splice e58dbcda3 r968 window committed+pushed by r968 itself (estate machine-verified); engine self-burn 12/12 (5c90051e0+776b15270); finalize one-pass r968 15:2x; six-gate PRE-FINALIZE correct phase standing law held, seventh consecutive), ",
     " " + "MSG-20261013-1530-bmc, executed bm-c r973 (seat dd38a9da8); splice 0ca920362 dead-r973 window committed+pushed by the dead r973 window itself (estate machine-verified); engine self-burn 12/12 (6c1587483+d4cce3ffe); finalize one-pass r974 19:4x; six-gate PRE-FINALIZE correct phase standing law held, eighth consecutive), ")

pair(''' "    #     MSG-20261013-1345-bmc, executed bm-c r968 (seat 8d3a1b78a); splice",
 "    #     e58dbcda3 r968 window committed+pushed by r968 itself (estate",
 "    #     machine-verified); engine self-burn 12/12 (5c90051e0+776b15270) + finalize one-pass r968 15:2x",
 "    #     splice estate + PRE-FINALIZE six-gate chain (standing law held, seventh",
 "    #     consecutive -- THIS W233 cycle runs PRE-FINALIZE likewise), honest note)",''',
''' "    #     MSG-20261013-1530-bmc, executed bm-c r973 (seat dd38a9da8); splice",
 "    #     0ca920362 dead-r973 window committed+pushed by the dead r973 window itself (estate",
 "    #     machine-verified); engine self-burn 12/12 (6c1587483+d4cce3ffe) + finalize one-pass r974 19:4x",
 "    #     splice estate + PRE-FINALIZE six-gate chain (standing law held, eighth",
 "    #     consecutive -- THIS W234 cycle runs PRE-FINALIZE likewise), honest note)",''')

# --- correctness delta (a): probe-receipt ordinal aging face fixed (disclosed header) ---
pair("ordinal machine-read NINETY-THIRD per probe receipt",
     "ordinal machine-read NINETY-FOURTH per probe receipt")

pair('"machine-checkable = A-hops-prior-B staircase NINETY-THIRD ",',
     '"machine-checkable = A-hops-prior-B staircase NINETY-FOURTH ",')

# --- estate/parity count pairs ---
pair('assert par_sec.count("assert pf.N1_BANDS[") == 88 \\',
     'assert par_sec.count("assert pf.N1_BANDS[") == 89 \\')
pair("    and int(_estate_ws[84]) == 226 \\\n    and int(_estate_ws[85]) == 227 \\\n    and int(_estate_ws[86]) == 228 \\\n    and int(_estate_ws[87]) == 229, \\",
     "    and int(_estate_ws[84]) == 226 \\\n    and int(_estate_ws[85]) == 227 \\\n    and int(_estate_ws[86]) == 228 \\\n    and int(_estate_ws[87]) == 229 \\\n    and int(_estate_ws[88]) == 230, \\")
pair('assert par_full.count("assert pf.N1_BANDS[") == 90, \\',
     'assert par_full.count("assert pf.N1_BANDS[") == 91, \\')
pair('    f"full parity span {par_full.count(\'assert pf.N1_BANDS[\')} != 90 (69 estate + W211..W227 legs + W228 leg + W229 leg + W230 leg + W231 leg)"',
     '    f"full parity span {par_full.count(\'assert pf.N1_BANDS[\')} != 91 (69 estate + W211..W228 legs + W229 leg + W230 leg + W231 leg + W232 leg)"')
pair("88-row cut", "89-row cut", 1)
pair("(91 rows: estate 69", "(92 rows: estate 69", 1)   # STRUCTURAL CHOICE face (receipt note fixed by its own block pair)

# --- cfg/row key literals (self-keyed gate strings, colon-continuation form) ---
pair("assert new_cfg.count('233: {\"batch\": \"PERPETUAL-N1-W233\"') == 1",
     "assert new_cfg.count('234: {\"batch\": \"PERPETUAL-N1-W234\"') == 1")
pair("assert n1_t4.count('233: {\"batch\": \"PERPETUAL-N1-W233\"') == 1",
     "assert n1_t4.count('234: {\"batch\": \"PERPETUAL-N1-W234\"') == 1")

# --- post-edit gate value-source fix (pf_mod faces stay [232] under the bare shift; [233] value source) ---
pair("""assert n1_t4.count(f'assert pf.N1_BANDS[232] == {{"a": ({fmt(pf_mod.N1_BANDS[232]["a"][0])}, {fmt(pf_mod.N1_BANDS[232]["a"][1])}),') == 1""",
     """assert n1_t4.count(f'assert pf.N1_BANDS[233] == {{"a": ({fmt(pf_mod.N1_BANDS[233]["a"][0])}, {fmt(pf_mod.N1_BANDS[233]["a"][1])}),') == 1""")

# --- w230_leg def -> w233_leg def (drop oldest leg, add newest; content [233]) ---
pair("""w230_leg = [
 f'        assert pf.N1_BANDS[230] == {{"a": ({fmt(pf_mod.N1_BANDS[230]["a"][0])}, {fmt(pf_mod.N1_BANDS[230]["a"][1])}),',
 f'                                    "b_exit": ({fmt(pf_mod.N1_BANDS[230]["b_exit"][0])}, {fmt(pf_mod.N1_BANDS[230]["b_exit"][1])}),',
'                                    "engine_owner": "bm-c"}, \\\\',
'            "registered W230 row parity drift (r307; bm-c five-face freeze; own-seat face disclosed)"',
]""",
"""w233_leg = [
 f'        assert pf.N1_BANDS[233] == {{"a": ({fmt(pf_mod.N1_BANDS[233]["a"][0])}, {fmt(pf_mod.N1_BANDS[233]["a"][1])}),',
 f'                                    "b_exit": ({fmt(pf_mod.N1_BANDS[233]["b_exit"][0])}, {fmt(pf_mod.N1_BANDS[233]["b_exit"][1])}),',
'                                    "engine_owner": "bm-c"}, \\\\',
'            "registered W233 row parity drift (r307; bm-c five-face freeze; own-seat face disclosed)"',
]""")

# --- receipt upstream + transitive block ---
pair('''  "w232_upstream": {"freeze_sha": w232_freeze_sha, "prereg_sha": w232_prereg_sha,
                    "ledger_total": w232_total, "merged_n": w232_merged_n,
                    "engine_owner": "bm-c (own seat honored, no takeover face)",
                    "repair_chain_note": "r968 splice (W232 freeze landed e58dbcda3 r968 window, estate committed+pushed by r968 itself; session died post-S6 pre-closeout, residual absorbed by the r968-continuation) + engine self-burn 12/12 (5c90051e0+776b15270) + r968 finalize one-pass 15:2x 59856ff28 (six-gate PRE-FINALIZE correct phase -- standing law held, seventh consecutive)"},''',
'''  "w233_upstream": {"freeze_sha": w233_freeze_sha, "prereg_sha": w233_prereg_sha,
                    "ledger_total": w233_total, "merged_n": w233_merged_n,
                    "engine_owner": "bm-c (own seat honored, no takeover face)",
                    "repair_chain_note": "r973 splice (W233 freeze landed 0ca920362 dead-r973 window, estate committed+pushed by the dead r973 window itself; session died pre-closeout, residual absorbed by r974) + engine self-burn 12/12 (6c1587483+d4cce3ffe) + r974 finalize one-pass 19:4x 260217d39 (six-gate PRE-FINALIZE correct phase -- standing law held, eighth consecutive)"},''')

pair('''  "w231_transitive": {"finalize_product": "results/perpetual_faces/n1_w231_results.json present (belt-and-braces gate; ledger 931,989 / K=506,120)"},''',
     '''  "w232_transitive": {"finalize_product": "results/perpetual_faces/n1_w232_results.json present (belt-and-braces gate; ledger 934,189 / K=508,320)"},''')

# --- receipt parity + family6 notes ---
pair("full-span estate W138..W206 (69 rows, r858 absorb generation) + W211..W229 legs + W230 leg + W231 leg + W232 leg -> W233 block = 91 rows ending at W232;",
     "full-span estate W138..W206 (69 rows, r858 absorb generation) + W211..W230 legs + W231 leg + W232 leg + W233 leg -> W234 block = 92 rows ending at W233;")

pair('"note": "W232 editor family-6 gate carried forward: new block LHS w<233 x3 / RHS range(16,233)+range(17,233) / comment below-233 count-asserted ATOMICALLY before splice; W232 block\'s own w<232 face = legitimate prior-wave boundary (not stale)"',
     '"note": "W233 editor family-6 gate carried forward: new block LHS w<234 x3 / RHS range(16,234)+range(17,234) / comment below-234 count-asserted ATOMICALLY before splice; W233 block\'s own w<233 face = legitimate prior-wave boundary (not stale)"')

# --- receipt ordinal faces ---
pair('''                    "probe_receipt_bmc_ordinal_face": 63,''',
     '''                    "probe_receipt_bmc_ordinal_face": 64,''')

# ---------------- phase 3: sentinel restores (with W234 additions) ----------------
rep("@@KEPT@@", KEPT_ORIG + "\nassert n1_t4.count('    # --- W233 materializer face') == 1  # prior block kept (W233 splice landed 0ca920362 dead-r973 window, estate machine-verified; committed+pushed by the dead r973 window itself, session died pre-closeout, residual estate absorbed by r974 260217d39)", 1)
rep("@@LIVE@@", LIVE_ORIG.replace('"w232_block_kept": 1},', '"w232_block_kept": 1, "w233_block_kept": 1},'), 1)
rep("@@LEG231@@", LEG231_ORIG, 1)
rep("@@LEG232@@", LEG232_ORIG, 1)
# ASM restore = machine-derived aging of the extracted face (descending-order leg
# aging: w232->w233 first, then w231->w232, then w230->w231; no cascades since each
# target is lower than every remaining source)
ASM_NEW = (ASM_ORIG.replace("w232_leg", "w233_leg")
                  .replace("w231_leg", "w232_leg")
                  .replace("w230_leg", "w231_leg"))
assert ASM_NEW == "block = EOL.join(hdr) + EOL + par_sec + EOL.join(w231_leg) + EOL + EOL.join(w232_leg) + EOL + EOL.join(w233_leg) + EOL + EOL.join(tail) + EOL", f"ASM_NEW drift: {ASM_NEW!r}"
rep("@@ASM@@", ASM_NEW, 1)

# ---------------- phase 4: validation (fail-closed) ----------------
# kept-line legit faces (KEPT-internal splice history carries W229..W232 verbatim)
assert t.count("e58dbcda3") == 1, f"kept-line e58dbcda3 count {t.count('e58dbcda3')} != 1"
assert t.count("r968 window") == 1, f"kept-line r968 window != 1"
assert t.count("r968 itself") == 1, f"kept-line r968 itself != 1"
assert t.count("r968-continuation") == 1, f"kept-line r968-continuation != 1"
assert t.count("W232") == 11, f"upstream W232 count {t.count('W232')} != 11 (2 KEPT + 8 shift-landed + 1 transitive-prose)"
# upstream-seat provenance faces (P9/P10 prose carries the W233 seat origin sha)
assert t.count("dd38a9da8") == 2, f"upstream seat-origin dd38a9da8 count {t.count('dd38a9da8')} != 2"

stale = ["(527_404, 529_403)", "(529_404, 529_603)",
 "2a21ef7cc4eaaa70375c7e4baec99f423488d5e2", "SEVENTEEN-level", "MSG-20261013-1345-bmc",
 "r973 freeze window", "r973 freeze-window bundle",
 "expect 222/62", "precedent 221/61 pre-splice", "splice 222/62", "== 222 and len", "rows 222 + candidate",
 "rows 62 + candidate", "bmc_ordinal=63", "63rd", "sixty-third",
 "NINETY-THIRD instance", "NINETY-THIRD",
 "TWO HUNDRED AND THIRTY-THIRD", "934_189", "508_320", "(expect 934,189",
 "r968 15:2x", "r968 seat-time", "probe receipt @ r968 window",
 "twenty-second consecutive", "seventh consecutive",
 "_w233bmc_20261013_probe_receipt.json", "_w233bmc_freeze_receipt.json",
 "w230_leg", "n1w233-", "N1_BANDS.get(232)", "if w < 233)", "if w < 232", "w<232 leaked",
 "range(16, 233)", "range(16,233)", "range(17, 233)", "below 233 composes", "below-233",
 "m230", "_c232", "n3r1_used233", "arith_a233", "arith_b233",
 "N1_BANDS\\[230\\]",
 "W234+ projection", "naive W234 A window", "W234 freezer", "W234+ freezer",
 "downstream W234 seat",
 "59856ff28", "5c90051e0", "776b15270", "cf3501cd9",
 "executed bm-c r968",
 "8d3a1b78a", "e58dbcda3x-guard", "r968-continuationx-guard",
 "@@KEPT@@", "@@LIVE@@", "@@LEG231@@", "@@LEG232@@", "@@ASM@@", "1193b255531f7aadcdff050069371c5e5169b11f" + "x-guard",
 '234: {"batch": "PERPETUAL-N1-W234"x-guard']
for s in stale:
    c = t.count(s)
    assert c == 0, f"STALE TOKEN {s!r} count {c} != 0"

must_one = ["_set_wave(234)",
 "f'{CFG_I}234: ", "f'{ROW_I}234: ", "ROW_I + '234: {\"a\"'", '"wave": 234',
 "MSG-20261013-1955-bmc.md", "936_389", "510_520",
 "(expect 936,389 / 510,520)", "(529_604, 531_603)", "(531_604, 531_803)",
 "int(_estate_ws[88]) == 230", "1193b255531f7aadcdff050069371c5e5169b11f", "EIGHTEEN-level",
 '"probe_receipt_bmc_ordinal_face": 64,', '"w233_block_kept": 1}',
 "N1_BANDS.get(233)", "r974 probe leg0", "r974 seat-time live face",
 "r976 prereg derived", "89-row cut", '== 89 \\', '== 91, \\',
 "n1w234-0of12", "n1w234-11of12", "seat MSG-1234 tail",
 "ordinal machine-read NINETY-FOURTH per probe receipt"]
for s in must_one:
    c = t.count(s)
    assert c == 1, f"MUST-ONE {s!r} count {c} != 1"

# --- calibration dump (dbg6): actual counts for the uncertain final faces ---
_cal = {s: t.count(s) for s in ["W233", "w233_", "n1_w234", "n1_w234_results", "n1_w233_results",
 "0ca920362", "260217d39", "r974 19:4x", "eighth consecutive", "92 rows", "w233_a_tail",
 "w233_b_tail", "w233_freeze_sha", "w233_prereg_sha", "w234_prereg_sha", "w234_receipt_sha",
 "W234", "w234_", "w231_leg", "w232_leg", "w233_leg", "r976", "twenty-third consecutive",
 "NINETY-FOURTH instance", "NINETY-FIFTH instance anticipated", "dd38a9da8",
 "n1_w234", "MSG-20261013-1955-bmc", "MSG-20261013-1530-bmc", "64th", "sixty-fourth",
 "TWO HUNDRED AND THIRTY-FOURTH", "W235+ projection", "naive W235 A window",
 "6c1587483", "d4cce3ffe", "e58dbcda3", "r976 freeze window",
 "WAVE_CONFIGS[234]", "WAVE_CONFIGS[233]", "w232_out_path", "w233_total",
 "w232_transitive", "w233_upstream",
 "assert pf.N1_BANDS[233] ==", "assert pf.N1_BANDS[232] ==", "assert pf.N1_BANDS[231] ==",
 "n1_w233_results.json", "n1_w234_results.json", "engine_owner rows 223 + candidate",
 "rows 223 + candidate", "234: {\"batch\""]}
open(os.path.join(HERE, "_w234bmc_dbg6_counts.json"), "w", encoding="utf-8").write(json.dumps(_cal, indent=1))
print("DBG6 COUNTS:", json.dumps(_cal))

assert t.count("MSG-20261013-1955-bmc") == 4
assert t.count('234: {"batch": "PERPETUAL-N1-W234"') == 2   # new_cfg gate + n1_t4 post-edit gate
assert t.count("MSG-20261013-1530-bmc") == 2          # upstream seat references
assert t.count("W235+ projection") == 2
assert t.count("naive W235 A window") == 2
assert t.count("NINETY-FIFTH instance anticipated") == 2
assert t.count("NINETY-FOURTH instance") == 5
assert t.count("TWO HUNDRED AND THIRTY-FOURTH") == 3
assert t.count("sixty-fourth") == 2
assert t.count("64th") == 6
assert t.count("bmc_ordinal=64") == 3
assert t.count("_w234bmc_20261013_probe_receipt.json") == 9
assert t.count("_w234bmc_freeze_receipt.json") == 1
assert t.count("w230_leg") == 0
assert t.count("w231_leg") == 2
assert t.count("w232_leg") == 2
assert t.count("w233_leg") == 2
assert t.count('"w232_transitive"') == 1
assert t.count('"w233_upstream"') == 2
assert t.count("assert pf.N1_BANDS[233] ==") == 2     # w233_leg def + post-edit gate
assert t.count("assert pf.N1_BANDS[232] ==") == 1     # w232_leg def (sentinel-kept)
assert t.count("assert pf.N1_BANDS[231] ==") == 1     # w231_leg def (sentinel-kept)
assert t.count("WAVE_CONFIGS[234]") == 2             # band-facts self asserts
assert t.count("WAVE_CONFIGS[233]") == 3             # upstream mirror asserts
assert t.count("n1_w234") == 5
assert t.count("n1_w233_results") == 4               # upstream refs (shift-landed)
assert t.count("n1_w234_results") == 2               # self path refs (shift-landed)
assert t.count("0ca920362") >= 6
assert t.count("260217d39") == 4   # SEAT_ORIGIN 1 + header finalize 1 + receipt finalize 1 + KEPT-restore 1
assert t.count("r974 19:4x") == 3
assert t.count("r976 freeze window") == 4
assert t.count("r976 freeze-window bundle") == 2
assert t.count("twenty-third consecutive") == 2
assert t.count("92 rows") == 2
assert t.count("if w < 234)") == 5
assert t.count("range(16, 234)") == 2
assert t.count("range(17, 234)") == 3
assert t.count("registered wave below 234 composes") == 2
assert t.count("eighth consecutive") == 2
assert t.count("w233_a_tail") == 14
assert t.count("w233_b_tail") == 9
assert t.count("w233_freeze_sha") == 6
assert t.count("w234_prereg_sha") == 5
assert t.count("w234_receipt_sha") == 4
assert t.count("6c1587483+d4cce3ffe") == 3
assert t.count("1955") >= 1 and t.count("1530-bmc.md") == 0

open(OUT, "w", encoding="utf-8", newline="").write(t)
py_compile.compile(OUT, doraise=True)
print(f"DERIVE OK: {OUT} ({len(t)} chars, template 50218); py_compile green")
print("NEXT: run the editor (gates fail-closed) -> pf/n1 selftest -> pathspec commit+push -> PRE-FINALIZE six-gate -> engine self-burn verify (2-cycle n1_w234 growth)")
