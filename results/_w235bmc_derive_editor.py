# -*- coding: utf-8 -*-
# r979 bm-c derive: W234 -> W235 five-face freeze editor (count-asserted ordered
# transform; fail-closed pair law; protect-restore sentinels for fixed-estate faces).
# Template = committed _w234bmc_freeze_edits.py (50,608-char text, dead-r976-continuation
# freeze-window generation, splice estate committed+pushed by the dead r976-continuation
# window itself as de342250c, proven live-fire; residual estate absorbed by the r976
# closeout e830a2632). All wave facts shift by token; every machine-derivable fact is
# re-asserted at editor RUNTIME against live template text (fail-closed).
# Sentinel blocks (KEPT/LIVE/LEG232/LEG233/ASM) are extracted from the template at
# RUNTIME by anchored index -- zero hand-transcription of fixed-estate faces (E63 law).
# Census evidence = results/_r979bmc_w235derive_census.py + _r979bmc_w235derive_postsent.py
# re-run THIS window (post-sentinel stripped counts: W234=72 / w234_=11(9 self post
# n1_w234 rides) / n1_w234=5 / n1w234=2 / W233=111 / w233_=94 / W232=8 / w232_=5 /
# W231=9 / w231_=1 / W230=8 / W229=3 / m231=3 / _c233=5 / 0ca920362=6(KEPT-internal 1
# excluded) / 260217d39=3(SEAT_ORIGIN+header finalize+receipt finalize; KEPT-restore 1
# sentinel-carried) / 1193b255=1 / dd38a9da8=2 / NINETY-FOURTH=7(5 instance + 2 pair
# faces) / sixty-fourth=2 / 64th=6 / bmc_ordinal=64=3 / rows 63+cand=4 / engine_owner
# rows 223=1 / r976 freeze window=4 / r976 bundle=2 / r976 prereg derived=1 / r976
# window=1 / r976+splice script landed=2 / r974 19:4x=3 / probe receipt@r974=2 /
# r974 probe leg0=1 / r974 seat-time=1 / dead r973 window=6 (ALL in pair regions) /
# executed bm-c r973=2 / r973 (seat=2 / eighth consecutive=2 / twenty-third
# consecutive=2 / EIGHTEEN-level=1 / 936_389=1 / 510_520=1 / 936,389=2 / 510,520=2 /
# == 89 \=1 / == 91, \=1 / 89-row cut=1 / 92 rows=2 / w232_transitive(934,189/508,320)=1 /
# (92 rows: estate 69=1 / int(_estate_ws[88])==230=1 / pf.N1_BANDS[233]=4(LEG233-internal
# 5 excluded) / N1_BANDS[231\]=1 / N1_BANDS.get(233)=1 / WAVE_CONFIGS[233]=3 /
# WAVE_CONFIGS[234]=2 / 233: {"batch"=2 / 233: {"a"=3 / '    233: {"a"'=1 / w231_leg=1 /
# materializer face=25 / _block_kept=25 / EOL.join trio w231/w232/w233).
# Disclosed deltas vs the mechanical clone (correctness pairs, machine-verifiable
# against the committed W235 prereg sha 89bd6962cd9e367586e1fdb520e37b8b47e5ee86 and
# the W234 cycle closeout commit e830a2632):
#  (a) upstream W234-cycle prose written honestly: prereg 252d5cc95 by dead r976 +
#      splice de342250c by dead r976-continuation + engine self-burn 12/12
#      (39f7b8b0c+5022491bc) + six-gate PRE-FINALIZE 21:4x ninth consecutive +
#      finalize one-pass 21:5x landed in-window e830a2632 (r976 absorb closeout);
#  (b) THIS wave's prereg derived+landed by bm-a TAKEOVER (bm-c hb-stall; r968 window
#      89bd6962c, R35 takeover faces machine-asserted, 46 groups 79 pairs preflight
#      count==1 ALL, STALE all-zero x38 / NEW all-present x38) -- prereg NOT redone
#      per anti-duplication law; THIS window (bm-c r979) executes the splice on its
#      OWN seat (takeover returned, disclosed honestly in receipt engine_owner face);
#  (c) seat/prose aging: MSG-1955->MSG-2149 self swap + upstream MSG-1530->MSG-1955;
#      SEAT_ORIGIN 260217d39->e830a2632 (all 3 stripped occurrences converge: W234 seat
#      origin + W234-cycle finalize refs in header/receipt).
import os, sys, py_compile, json

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.join(HERE, "_w234bmc_freeze_edits.py")
OUT  = os.path.join(HERE, "_w235bmc_freeze_edits.py")

t = open(BASE, "r", encoding="utf-8", newline="").read()
assert len(t) == 50608, f"template length drift: {len(t)} != 50608"

def rep(old, new, n=1):
    global t
    c = t.count(old)
    assert c == n, f"PAIR FAIL count {c} != {n}: {old[:110]!r}"
    t = t.replace(old, new)

# ---------------- phase 0: sentinels (RUNTIME anchored extraction) ----------------
# KEPT block: W209 estate-source line .. W233 prior-block-kept line (25 assert lines)
k0 = t.index("assert n1_t4.count('    # --- W209 materializer face')")
k1 = t.index("assert n1_t4.count('    # --- W233 materializer face')")
k2 = t.index("\n", k1)
KEPT_ORIG = t[k0:k2]
assert KEPT_ORIG.count("\nassert ") == 24, f"KEPT block shape: {KEPT_ORIG.count(chr(10)+'assert ')}"
assert KEPT_ORIG.count("materializer face") == 25
rep(KEPT_ORIG, "@@KEPT@@", 1)

# LIVE line (liveness_anchors single-line JSON face)
l0 = t.index('"liveness_anchors"')
l0 = t.rindex("\n", 0, l0) + 1
l1 = t.index("\n", l0)
LIVE_ORIG = t[l0:l1]
assert LIVE_ORIG.count("_block_kept") == 25, f"LIVE shape: {LIVE_ORIG.count('_block_kept')}"  # w209..w233
rep(LIVE_ORIG, "@@LIVE@@", 1)

# LEG232 (template w232_leg def, 6 lines) -- protected from w232_->w233_ + W232->W233 aging
g0 = t.index("w232_leg = [")
g2 = t.index("\n]", g0) + 2
LEG232_ORIG = t[g0:g2]
assert LEG232_ORIG.count("N1_BANDS[232]") == 5 and LEG232_ORIG.count("W232 row parity drift") == 1
rep(LEG232_ORIG, "@@LEG232@@", 1)

# LEG233 (template w233_leg def, 6 lines) -- protected from w233_->w234_ + W233->W234 aging
h0 = t.index("w233_leg = [")
h2 = t.index("\n]", h0) + 2
LEG233_ORIG = t[h0:h2]
assert LEG233_ORIG.count("N1_BANDS[233]") == 5 and LEG233_ORIG.count("W233 row parity drift") == 1
rep(LEG233_ORIG, "@@LEG233@@", 1)

# ASM join line (RUNTIME anchored extraction -- E63 law: zero hand-transcription)
a0 = t.index("block = EOL.join(hdr)")
a1 = t.index("\n", a0)
ASM_ORIG = t[a0:a1]
assert ASM_ORIG.count("EOL.join(w231_leg)") == 1 and ASM_ORIG.count("EOL.join(w232_leg)") == 1 \
    and ASM_ORIG.count("EOL.join(w233_leg)") == 1 and ASM_ORIG.count("EOL.join(tail)") == 1, \
    f"ASM shape: {ASM_ORIG!r}"
rep(ASM_ORIG, "@@ASM@@", 1)

# ---------------- phase 1: ordered global shifts (descending, count-logged) ----------------
SHIFTS = [
 # --- self wave faces (W234 -> W235) ---
 ("n1_w234", "n1_w235", 5),            # self shard/out names (BEFORE w234_ var shift, substring law)
 ("w234_", "w235_", 9),               # self vars (census 11 - 2 n1_w234_results rides = 9)
 ("n1w234", "n1w235", 2),              # entry-identity tags
 ("W234", "W235", 72),                # self prose global (incl. PERPETUAL_N1_W234_PREREG x5 + batch x2)
 ("_w234bmc_20261013_probe_receipt.json", "_w235bmc_20261013_probe_receipt.json", 9),
 ("_w234bmc_freeze_receipt.json", "_w235bmc_freeze_receipt.json", 1),
 ("_w233bmc_freeze_edits.py", "_w234bmc_freeze_edits.py", 1),   # lineage template name (upstream->self)
 ("_set_wave(234)", "_set_wave(235)", 1),
 ('"wave": 234,', '"wave": 235,', 1),
 ("f'{CFG_I}234: ", "f'{CFG_I}235: ", 1),
 ("f'{ROW_I}234: ", "f'{ROW_I}235: ", 1),
 ("f'234: {{\"a\":", "f'235: {{\"a\":", 1),
 ("ROW_I + '234: {\"a\"'", "ROW_I + '235: {\"a\"'", 1),
 ("WAVE_CONFIGS[234]", "WAVE_CONFIGS[235]", 2),       # band-facts self asserts (BEFORE the [233]->[234] mirror shift)
 ("seat MSG-1234 tail", "seat MSG-1235 tail", 1),
 ("wave 234 = first free number", "wave 235 = first free number", 1),
 ("wave 234: ", "wave 235: ", 1),
 ("if w < 234)", "if w < 235)", 5),
 ("range(16, 234)", "range(16, 235)", 2),
 ("range(17, 234)", "range(17, 235)", 3),
 ("w<234 count", "w<235 count", 1),
 ("if w < 233", "if w < 234", 1),          # family-6 prior-wave 0-check (no paren tail -- distinct face)
 ("w<233 leaked", "w<234 leaked", 1),     # family-6 prior-wave leak prose
 ("below 234 composes", "below 235 composes", 2),
 ("below-234", "below-235", 2),
 ("arith_a234", "arith_a235", 3),
 ("arith_b234", "arith_b235", 3),
 ("n3r1_used234", "n3r1_used235", 3),
 # --- projection aging (W235 -> W236) ---
 ("W235+ projection", "W236+ projection", 2),
 ("naive W235 A window", "naive W236 A window", 2),
 ("W235 freezer", "W236 freezer", 1),
 ("W235+ freezer", "W236+ freezer", 1),
 ("downstream W235 seat NOT yet published", "downstream W236 seat NOT yet published", 1),
 ("downstream W235 seat publication pending", "downstream W236 seat publication pending", 1),
 ("NINETY-FIFTH instance anticipated", "NINETY-SIXTH instance anticipated", 2),
 # --- self ordinal/prose aging ---
 ("NINETY-FOURTH instance", "NINETY-FIFTH instance", 5),
 ("TWO HUNDRED AND THIRTY-FOURTH", "TWO HUNDRED AND THIRTY-FIFTH", 3),
 ("sixty-fourth", "sixty-fifth", 2),
 ("64th", "65th", 6),
 ("bmc_ordinal=64", "bmc_ordinal=65", 3),
 ("rows 63 + candidate", "rows 64 + candidate", 4),
 ("rows 223 + candidate", "rows 224 + candidate", 1),
 ("== 223 and len(bmc_rows_live) == 63", "== 224 and len(bmc_rows_live) == 64", 1),
 ("expect 223/63", "expect 224/64", 1),
 ("precedent 222/62 pre-splice", "precedent 223/63 pre-splice", 1),
 ("splice 223/63", "splice 224/64", 1),
 # --- window labels (this freeze = bm-c r979; upstream W234-cycle prose r976 21:5x) ---
 ("r976 freeze window", "r979 freeze window", 4),
 ("r976 freeze-window bundle", "r979 freeze-window bundle", 2),
 ("r976 prereg derived", "bm-a r968-takeover prereg derived", 1),
 ("r976 + freeze splice script landed", "bm-a r968-takeover prereg + r979 freeze splice script landed", 2),
 ("r974 19:4x", "r976 21:5x", 3),
 ("probe receipt @ r974 window", "probe receipt @ r976 window", 2),
 ("r974 probe leg0", "r976 probe leg0", 1),
 ("r974 seat-time live face", "r976 seat-time live face", 1),
 ("twenty-third consecutive", "twenty-fourth consecutive", 2),
 ("eighth consecutive", "ninth consecutive", 2),
 # --- seat/provenance aging (self swap FIRST, then upstream) ---
 ("MSG-20261013-1955-bmc", "MSG-20261013-2149-bmc", 4),   # self seat swap FIRST
 ("MSG-20261013-1530-bmc", "MSG-20261013-1955-bmc", 2),   # upstream seat AFTER self swap
 ("260217d39", "e830a2632", 3),  # SEAT_ORIGIN + header finalize + receipt finalize (all converge on the W234-cycle closeout/seat commit)
 ("dd38a9da8", "260217d39", 2),                            # upstream seat-origin provenance x2
 ("1193b255531f7aadcdff050069371c5e5169b11f", "89bd6962cd9e367586e1fdb520e37b8b47e5ee86", 1),  # self prereg sha
 # --- band/ledger fact aging (self W234 facts -> W235 facts; probe ADMIT bands) ---
 ("(529_604, 531_603)", "(531_804, 533_803)", 1),
 ("(531_604, 531_803)", "(533_804, 534_003)", 1),
 ("936_389", "938_589", 1),
 ("510_520", "512_720", 1),
 ("936,389", "938,589", 2),
 ("510,520", "512,720", 2),
 # --- upstream cycle shas aging ---
 ("0ca920362", "de342250c", 6),            # KEPT-internal 1 excluded by sentinel
 # engine burn shas (6c1587483+d4cce3ffe) carried ENTIRELY by the P9/P10/receipt
 # upstream pairs (census: 3/3, ALL inside compound pair regions, zero standalone
 # -- carried to 39f7b8b0c+5022491bc by authored pairs)
 # --- upstream wave faces (W233 -> W234; descending) ---
 ("W233", "W234", 111),               # upstream prose global (census 114 - KEPT-internal 2 - LEG233-internal 1)
 ("w233_", "w234_", 94),              # upstream vars (incl. 4 n1_w233_results rides; LEG233/ASM/LIVE sentinel-excluded)
 ("W232", "W233", 8),                 # upstream-upstream prose (census 8 post-sentinels)
 ("w232_", "w233_", 5),              # upstream-upstream vars (LEG232/ASM sentinel-excluded)
 ("W231", "W232", 9),                 # upstream-upstream-upstream prose (census 9 post-sentinels)
 ("w231_", "w232_", 1),              # w231_leg def name ONLY (ASM/LIVE rides sentinel-excluded; pair renames to w234_leg def)
 ("W230", "W231", 8),                # estate prose (KEPT-internal 2 excluded by sentinel)
 ("W229", "W230", 3),                # estate prose (KEPT-internal 2 excluded by sentinel)
 ("m231", "m232", 3),
 ("N1_BANDS\\[231\\]", "N1_BANDS\\[232\\]", 1),   # m-cut regex literal (raw-bracket form)
 ("_c233", "_c234", 5),
 ("'233: {\"batch\"'", "'234: {\"batch\"'", 2),   # upstream cfg needles
 ("'233: {\"a\"'", "'234: {\"a\"'", 2),           # upstream row needles
 ("'    233: {\"a\"'", "'    234: {\"a\"'", 1),
 ("N1_BANDS.get(233)", "N1_BANDS.get(234)", 1),
 ("WAVE_CONFIGS[233]", "WAVE_CONFIGS[234]", 3),       # upstream mirror asserts (AFTER self [234]->[235])
 ("pf.N1_BANDS[233]", "pf.N1_BANDS[234]", 4),   # mirror x3 + post-edit gate x1 (LEG233-internal assert face excluded)
 ("89-row cut", "90-row cut", 1),
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
pair("""# 2026-10-13 21:2x bm-c r976 freeze window (upstream W1..W233 ALL LANDED, clean precondition): W234 five-face freeze splice editor.""",
"""# 2026-10-14 04:5x bm-c r979 freeze window (upstream W1..W234 ALL LANDED, clean precondition): W235 five-face freeze splice editor.""")
# regression guards for the window-label pair (new side must carry the SHIFTED wave faces)
assert t.count("(upstream W1..W234 ALL LANDED, clean precondition): W235 five-face") == 1
assert t.count("W234 five-face freeze splice editor") == 0

pair("""Upstream chain ALL LANDED at this window: W1..W233 finalize products
# present (W233 finalize one-pass r974 19:4x landed in-window 260217d39 (r974 absorb closeout); splice
# estate 0ca920362 committed+pushed by the dead r973 window itself (session
# died pre-closeout; residual estate absorbed by r974), net chain head 936,389, merged pool K=510,520,
# n1_w233_results.json machine-read) -- ZERO in-flight upstream seats,""",
"""Upstream chain ALL LANDED at this window: W1..W234 finalize products
# present (W234 finalize one-pass r976 21:5x landed in-window e830a2632 (r976 absorb closeout); splice
# estate de342250c committed+pushed by the dead r976-continuation window itself (session
# died pre-closeout; residual estate absorbed by r976), net chain head 938,589, merged pool K=512,720,
# n1_w234_results.json machine-read) -- ZERO in-flight upstream seats,""")

pair("""# Lineage: _w233bmc_freeze_edits.py pattern (proven live-fire freeze,
# 0ca920362 committed+pushed by the dead r973 window itself, machine-verified by
# the r974-absorb closeout receipt) + r787 preflight law + r609""",
"""# Lineage: _w234bmc_freeze_edits.py pattern (proven live-fire freeze,
# de342250c committed+pushed by the dead r976-continuation window itself, machine-verified by
# the r976-absorb closeout receipt) + r787 preflight law + r609""")

pair("""# LHS/RHS/comment ATOMIC TRIPLE absorbed (the new block's w<234>/
# range(16,234)/below-234 triple is count-asserted atomically; the W233
# block's own w<233 face is legitimate prior-wave boundary, not stale).""",
"""# LHS/RHS/comment ATOMIC TRIPLE absorbed (the new block's w<235>/
# range(16,235)/below-235 triple is count-asserted atomically; the W234
# block's own w<234 face is legitimate prior-wave boundary, not stale).""")

# --- structural-choice provenance fixup (post-shift anchors) ---
pair("""# (dead-r973 window editor, estate committed+pushed by the dead r973 window itself as 0ca920362), structure known. The W233 block span ends where the""",
"""# (dead-r976-continuation window editor, estate committed+pushed by the dead r976-continuation window itself as de342250c), structure known. The W234 block span ends where the""")

# --- seat/prose fixups (post-shift anchors) ---
pair(" " + "MSG-20261013-1530-bmc, executed bm-c r973 (seat dd38a9da8); splice 0ca920362 dead-r973 window committed+pushed by the dead r973 window itself (estate machine-verified); engine self-burn 12/12 (6c1587483+d4cce3ffe); finalize one-pass r974 19:4x; six-gate PRE-FINALIZE correct phase standing law held, eighth consecutive), ",
     " " + "MSG-20261013-1955-bmc, executed bm-c r974 (seat 260217d39); splice de342250c dead-r976-continuation window committed+pushed by the dead r976-continuation window itself (estate machine-verified); engine self-burn 12/12 (39f7b8b0c+5022491bc); finalize one-pass r976 21:5x; six-gate PRE-FINALIZE correct phase standing law held, ninth consecutive), ")

pair(''' "    #     MSG-20261013-1530-bmc, executed bm-c r973 (seat dd38a9da8); splice",
 "    #     0ca920362 dead-r973 window committed+pushed by the dead r973 window itself (estate",
 "    #     machine-verified); engine self-burn 12/12 (6c1587483+d4cce3ffe) + finalize one-pass r974 19:4x",
 "    #     splice estate + PRE-FINALIZE six-gate chain (standing law held, eighth",
 "    #     consecutive -- THIS W234 cycle runs PRE-FINALIZE likewise), honest note)",''',
''' "    #     MSG-20261013-1955-bmc, executed bm-c r974 (seat 260217d39); splice",
 "    #     de342250c dead-r976-continuation window committed+pushed by the dead r976-continuation window itself (estate",
 "    #     machine-verified); engine self-burn 12/12 (39f7b8b0c+5022491bc) + finalize one-pass r976 21:5x",
 "    #     splice estate + PRE-FINALIZE six-gate chain (standing law held, ninth",
 "    #     consecutive -- THIS W235 cycle runs PRE-FINALIZE likewise), honest note)",''')

# --- correctness delta (a): probe-receipt ordinal aging face fixed (disclosed header) ---
pair("ordinal machine-read NINETY-FOURTH per probe receipt",
     "ordinal machine-read NINETY-FIFTH per probe receipt")

pair('"machine-checkable = A-hops-prior-B staircase NINETY-FOURTH ",',
     '"machine-checkable = A-hops-prior-B staircase NINETY-FIFTH ",')

# --- estate/parity count pairs ---
pair('assert par_sec.count("assert pf.N1_BANDS[") == 89 \\',
     'assert par_sec.count("assert pf.N1_BANDS[") == 90 \\')
pair("    and int(_estate_ws[84]) == 226 \\\n    and int(_estate_ws[85]) == 227 \\\n    and int(_estate_ws[86]) == 228 \\\n    and int(_estate_ws[87]) == 229 \\\n    and int(_estate_ws[88]) == 230, \\",
     "    and int(_estate_ws[84]) == 226 \\\n    and int(_estate_ws[85]) == 227 \\\n    and int(_estate_ws[86]) == 228 \\\n    and int(_estate_ws[87]) == 229 \\\n    and int(_estate_ws[88]) == 230 \\\n    and int(_estate_ws[89]) == 231, \\")
pair('assert par_full.count("assert pf.N1_BANDS[") == 91, \\',
     'assert par_full.count("assert pf.N1_BANDS[") == 92, \\')
pair('    f"full parity span {par_full.count(\'assert pf.N1_BANDS[\')} != 91 (69 estate + W211..W228 legs + W229 leg + W230 leg + W231 leg + W232 leg)"',
     '    f"full parity span {par_full.count(\'assert pf.N1_BANDS[\')} != 92 (69 estate + W211..W229 legs + W230 leg + W231 leg + W232 leg + W233 leg)"')
pair("(92 rows: estate 69", "(93 rows: estate 69", 1)   # STRUCTURAL CHOICE face (receipt note fixed by its own block pair)

# --- cfg/row key literals (self-keyed gate strings, colon-continuation form) ---
pair("assert new_cfg.count('234: {\"batch\": \"PERPETUAL-N1-W234\"') == 1",
     "assert new_cfg.count('235: {\"batch\": \"PERPETUAL-N1-W235\"') == 1")
pair("assert n1_t4.count('234: {\"batch\": \"PERPETUAL-N1-W234\"') == 1",
     "assert n1_t4.count('235: {\"batch\": \"PERPETUAL-N1-W235\"') == 1")

# --- post-edit gate value-source fix (pf_mod faces stay [233] under the bare shift; [234] value source) ---
pair("""assert n1_t4.count(f'assert pf.N1_BANDS[233] == {{"a": ({fmt(pf_mod.N1_BANDS[233]["a"][0])}, {fmt(pf_mod.N1_BANDS[233]["a"][1])}),') == 1""",
     """assert n1_t4.count(f'assert pf.N1_BANDS[234] == {{"a": ({fmt(pf_mod.N1_BANDS[234]["a"][0])}, {fmt(pf_mod.N1_BANDS[234]["a"][1])}),') == 1""")

# --- w231_leg def -> w234_leg def (drop oldest leg, add newest; content [234]) ---
pair("""w231_leg = [
 f'        assert pf.N1_BANDS[231] == {{"a": ({fmt(pf_mod.N1_BANDS[231]["a"][0])}, {fmt(pf_mod.N1_BANDS[231]["a"][1])}),',
 f'                                    "b_exit": ({fmt(pf_mod.N1_BANDS[231]["b_exit"][0])}, {fmt(pf_mod.N1_BANDS[231]["b_exit"][1])}),',
'                                    "engine_owner": "bm-c"}, \\\\',
'            "registered W231 row parity drift (r307; bm-c five-face freeze; own-seat face disclosed)"',
]""",
"""w234_leg = [
 f'        assert pf.N1_BANDS[234] == {{"a": ({fmt(pf_mod.N1_BANDS[234]["a"][0])}, {fmt(pf_mod.N1_BANDS[234]["a"][1])}),',
 f'                                    "b_exit": ({fmt(pf_mod.N1_BANDS[234]["b_exit"][0])}, {fmt(pf_mod.N1_BANDS[234]["b_exit"][1])}),',
'                                    "engine_owner": "bm-c"}, \\\\',
'            "registered W234 row parity drift (r307; bm-c five-face freeze; own-seat face disclosed)"',
]""")

# --- receipt upstream + transitive block ---
pair('''  "w233_upstream": {"freeze_sha": w233_freeze_sha, "prereg_sha": w233_prereg_sha,
                    "ledger_total": w233_total, "merged_n": w233_merged_n,
                    "engine_owner": "bm-c (own seat honored, no takeover face)",
                    "repair_chain_note": "r973 splice (W233 freeze landed 0ca920362 dead-r973 window, estate committed+pushed by the dead r973 window itself; session died pre-closeout, residual absorbed by r974) + engine self-burn 12/12 (6c1587483+d4cce3ffe) + r974 finalize one-pass 19:4x 260217d39 (six-gate PRE-FINALIZE correct phase -- standing law held, eighth consecutive)"},''',
'''  "w234_upstream": {"freeze_sha": w234_freeze_sha, "prereg_sha": w234_prereg_sha,
                    "ledger_total": w234_total, "merged_n": w234_merged_n,
                    "engine_owner": "bm-c (own seat honored; prereg derive taken over by bm-a per hb-stall law -- disclosed; splice+freeze back on bm-c own seat)",
                    "repair_chain_note": "r976-continuation splice (W234 freeze landed de342250c dead-r976-continuation window, estate committed+pushed by the dead r976-continuation window itself; session died pre-closeout, residual absorbed by r976) + engine self-burn 12/12 (39f7b8b0c+5022491bc) + r976 finalize one-pass 21:5x e830a2632 (six-gate PRE-FINALIZE correct phase -- standing law held, ninth consecutive)"},''')

pair('''  "w232_transitive": {"finalize_product": "results/perpetual_faces/n1_w232_results.json present (belt-and-braces gate; ledger 934,189 / K=508,320)"},''',
     '''  "w233_transitive": {"finalize_product": "results/perpetual_faces/n1_w233_results.json present (belt-and-braces gate; ledger 936,389 / K=510,520)"},''')

# --- receipt prereg_bundle note (bm-a takeover provenance, honest new face) ---
pair('"note": "prereg derived+committed in the r976 window (1193b255531f7aadcdff050069371c5e5169b11f, EIGHTEEN-level lineage replay chain, preflight 46/46); splice editor derived from the committed W233 editor template by count-asserted ordered transform (protect-restore regions, fail-closed pair law) in this same r976 freeze window; upstream W233 already landed (clean-precondition twenty-third consecutive window); zero transcription"',
     '"note": "prereg derived+committed by the bm-a takeover (bm-c hb-stall) in the r968 window (89bd6962cd9e367586e1fdb520e37b8b47e5ee86, R35 takeover faces machine-asserted vs live JSON, 46 groups 79 pairs preflight count==1 ALL, STALE all-zero x38 / NEW all-present x38); splice editor derived from the committed W234 editor template by count-asserted ordered transform (protect-restore regions, fail-closed pair law) in this same r979 freeze window; upstream W234 already landed (clean-precondition twenty-fourth consecutive window); zero transcription"')

# --- receipt parity + family6 notes ---
pair("full-span estate W138..W206 (69 rows, r858 absorb generation) + W211..W230 legs + W231 leg + W232 leg + W233 leg -> W234 block = 92 rows ending at W233;",
     "full-span estate W138..W206 (69 rows, r858 absorb generation) + W211..W231 legs + W232 leg + W233 leg + W234 leg -> W235 block = 93 rows ending at W234;")

pair('"note": "W233 editor family-6 gate carried forward: new block LHS w<234 x3 / RHS range(16,234)+range(17,234) / comment below-234 count-asserted ATOMICALLY before splice; W233 block\'s own w<233 face = legitimate prior-wave boundary (not stale)"',
     '"note": "W234 editor family-6 gate carried forward: new block LHS w<235 x3 / RHS range(16,235)+range(17,235) / comment below-235 count-asserted ATOMICALLY before splice; W234 block\'s own w<234 face = legitimate prior-wave boundary (not stale)"')

# --- receipt ordinal faces ---
pair('''                    "probe_receipt_bmc_ordinal_face": 64,''',
     '''                    "probe_receipt_bmc_ordinal_face": 65,''')

# ---------------- phase 3: sentinel restores (with W235 additions) ----------------
rep("@@KEPT@@", KEPT_ORIG + "\nassert n1_t4.count('    # --- W234 materializer face') == 1  # prior block kept (W234 splice landed de342250c dead-r976-continuation window, estate machine-verified; committed+pushed by the dead r976-continuation window itself, session died pre-closeout, residual estate absorbed by r976 e830a2632)", 1)
rep("@@LIVE@@", LIVE_ORIG.replace('"w233_block_kept": 1},', '"w233_block_kept": 1, "w234_block_kept": 1},'), 1)
rep("@@LEG232@@", LEG232_ORIG, 1)
rep("@@LEG233@@", LEG233_ORIG, 1)
# ASM restore = machine-derived aging of the extracted face (descending-order leg
# aging: w233->w234 first, then w232->w233, then w231->w232; no cascades since each
# target is lower than every remaining source)
ASM_NEW = (ASM_ORIG.replace("w233_leg", "w234_leg")
                  .replace("w232_leg", "w233_leg")
                  .replace("w231_leg", "w232_leg"))
assert ASM_NEW == "block = EOL.join(hdr) + EOL + par_sec + EOL.join(w232_leg) + EOL + EOL.join(w233_leg) + EOL + EOL.join(w234_leg) + EOL + EOL.join(tail) + EOL", f"ASM_NEW drift: {ASM_NEW!r}"
rep("@@ASM@@", ASM_NEW, 1)

# ---------------- phase 4: validation (fail-closed) ----------------
# kept-line legit faces (KEPT-internal splice history carries W229..W233 verbatim)
assert t.count("0ca920362") == 1, f"kept-line 0ca920362 count {t.count('0ca920362')} != 1"
assert t.count("dead r973 window") == 1, f"kept-line dead r973 window != 1"
assert t.count("0ca920362 dead-r973 window") == 1, f"kept-line hyphenated splice window face"
assert t.count("W233") == 11, f"upstream W233 count {t.count('W233')} != 11 (2 KEPT + 8 shift-landed + 1 transitive-prose)"
# upstream-seat provenance faces (P9/P10 prose carries the W234 seat origin sha)
assert t.count("260217d39") == 3, f"upstream seat-origin 260217d39 count {t.count('260217d39')} != 3 (2 aging-landed + 1 KEPT-internal verbatim)"

stale = ["(529_604, 531_603)", "(531_604, 531_803)",
 "1193b255531f7aadcdff050069371c5e5169b11f", "EIGHTEEN-level", "MSG-20261013-1530-bmc",
 "r976 freeze window", "r976 freeze-window bundle",
 "expect 223/63", "precedent 222/62 pre-splice", "splice 223/63", "== 223 and len", "rows 223 + candidate",
 "rows 63 + candidate", "bmc_ordinal=64", "64th", "sixty-fourth",
 "NINETY-FOURTH instance", "NINETY-FOURTH",
 "TWO HUNDRED AND THIRTY-FOURTH", "936_389", "510_520", "(expect 936,389",
 "r974 19:4x", "r974 seat-time", "probe receipt @ r974 window",
 "twenty-third consecutive", "eighth consecutive",
 "_w234bmc_20261013_probe_receipt.json", "_w234bmc_freeze_receipt.json",
 "w231_leg", "n1w234-", "N1_BANDS.get(233)", "if w < 234)", "if w < 233", "w<233 leaked",
 "range(16, 234)", "range(16,234)", "range(17, 234)", "below 234 composes", "below-234",
 "m231", "_c233", "n3r1_used234", "arith_a234", "arith_b234",
 "N1_BANDS\\[231\\]",
 "W235+ projection", "naive W235 A window", "W235 freezer", "W235+ freezer",
 "downstream W235 seat",
 "6c1587483", "d4cce3ffe", "dd38a9da8", "e58dbcda3x-guard",
 "executed bm-c r973",
 "dead r973 windowx-guard", "260217d39x-guard",
 "@@KEPT@@", "@@LIVE@@", "@@LEG232@@", "@@LEG233@@", "@@ASM@@", "89bd6962cd9e367586e1fdb520e37b8b47e5ee86" + "x-guard",
 '235: {"batch": "PERPETUAL-N1-W235"x-guard']
for s in stale:
    c = t.count(s)
    assert c == 0, f"STALE TOKEN {s!r} count {c} != 0"

must_one = ["_set_wave(235)",
 "if w < 234",
 "f'{CFG_I}235: ", "f'{ROW_I}235: ", "ROW_I + '235: {\"a\"'", '"wave": 235',
 "MSG-20261013-2149-bmc.md", "938_589", "512_720",
 "(expect 938,589 / 512,720)", "(531_804, 533_803)", "(533_804, 534_003)",
 "int(_estate_ws[89]) == 231", "89bd6962cd9e367586e1fdb520e37b8b47e5ee86",
 '"probe_receipt_bmc_ordinal_face": 65,', '"w234_block_kept": 1}',
 "N1_BANDS.get(234)", "r976 probe leg0", "r976 seat-time live face",
 "bm-a r968-takeover prereg derived", "90-row cut", '== 90 \\', '== 92, \\',
 "n1w235-0of12", "n1w235-11of12", "seat MSG-1235 tail",
 "ordinal machine-read NINETY-FIFTH per probe receipt"]
for s in must_one:
    c = t.count(s)
    assert c == 1, f"MUST-ONE {s!r} count {c} != 1"

# --- calibration dump (dbg6): actual counts for the uncertain final faces ---
_cal = {s: t.count(s) for s in ["W234", "w234_", "n1_w235", "n1_w235_results", "n1_w234_results",
 "de342250c", "e830a2632", "r976 21:5x", "ninth consecutive", "93 rows", "w234_a_tail",
 "w234_b_tail", "w234_freeze_sha", "w234_prereg_sha", "w235_prereg_sha", "w235_receipt_sha",
 "W235", "w235_", "w232_leg", "w233_leg", "w234_leg", "r979", "twenty-fourth consecutive",
 "NINETY-FIFTH instance", "NINETY-SIXTH instance anticipated", "260217d39",
 "MSG-20261013-2149-bmc", "MSG-20261013-1955-bmc", "65th", "sixty-fifth",
 "TWO HUNDRED AND THIRTY-FIFTH", "W236+ projection", "naive W236 A window",
 "39f7b8b0c", "5022491bc", "de342250c", "r979 freeze window",
 "WAVE_CONFIGS[235]", "WAVE_CONFIGS[234]", "w233_out_path",
 "w233_transitive", "w234_upstream",
 "assert pf.N1_BANDS[234] ==", "assert pf.N1_BANDS[233] ==", "assert pf.N1_BANDS[232] ==",
 "n1_w235_results.json", "n1_w234_results.json", "engine_owner rows 224",
 "rows 224 + candidate", '235: {"batch"',
 "bm-a r968-takeover prereg + r979 freeze splice script landed"]}
open(os.path.join(HERE, "_w235bmc_dbg6_counts.json"), "w", encoding="utf-8").write(json.dumps(_cal, indent=1))
print("DBG6 COUNTS:", json.dumps(_cal))

assert t.count("MSG-20261013-2149-bmc") == 4
assert t.count('235: {"batch": "PERPETUAL-N1-W235"') == 2   # new_cfg gate + n1_t4 post-edit gate
assert t.count("MSG-20261013-1955-bmc") == 2          # upstream seat references
assert t.count("W236+ projection") == 2
assert t.count("naive W236 A window") == 2
assert t.count("NINETY-SIXTH instance anticipated") == 2
assert t.count("NINETY-FIFTH instance") == 5
assert t.count("TWO HUNDRED AND THIRTY-FIFTH") == 3
assert t.count("sixty-fifth") == 2
assert t.count("65th") == 6
assert t.count("bmc_ordinal=65") == 3
assert t.count("_w235bmc_20261013_probe_receipt.json") == 9
assert t.count("_w235bmc_freeze_receipt.json") == 1
assert t.count("w231_leg") == 0
assert t.count("w232_leg") == 2
assert t.count("w233_leg") == 2
assert t.count("w234_leg") == 2
assert t.count('"w233_transitive"') == 1
assert t.count('"w234_upstream"') == 2
assert t.count("assert pf.N1_BANDS[234] ==") == 2     # w234_leg def + post-edit gate
assert t.count("assert pf.N1_BANDS[233] ==") == 1     # w233_leg def (sentinel-kept)
assert t.count("assert pf.N1_BANDS[232] ==") == 1     # w232_leg def (sentinel-kept)
assert t.count("WAVE_CONFIGS[235]") == 2             # band-facts self asserts
assert t.count("WAVE_CONFIGS[234]") == 3             # upstream mirror asserts
assert t.count("n1_w235") == 5
assert t.count("n1_w234_results") == 4               # upstream refs (shift-landed)
assert t.count("n1_w235_results") == 2               # self path refs (shift-landed)
assert t.count("de342250c") >= 6
assert t.count("e830a2632") == 4   # SEAT_ORIGIN 1 + header finalize 1 + receipt finalize 1 + KEPT-restore 1
assert t.count("r976 21:5x") == 3
assert t.count("r979 freeze window") == 4
assert t.count("r979 freeze-window bundle") == 2
assert t.count("twenty-fourth consecutive") == 2
assert t.count("93 rows") == 2
assert t.count("if w < 235)") == 5
assert t.count("range(16, 235)") == 2
assert t.count("range(17, 235)") == 3
assert t.count("registered wave below 235 composes") == 2
assert t.count("ninth consecutive") == 2
assert t.count("w234_a_tail") == 14
assert t.count("w234_b_tail") == 9
assert t.count("w234_freeze_sha") == 6
assert t.count("w235_prereg_sha") == 5
assert t.count("w235_receipt_sha") == 4
assert t.count("39f7b8b0c+5022491bc") == 3
assert t.count("2149") >= 1 and t.count("1955-bmc.md") == 0

open(OUT, "w", encoding="utf-8", newline="").write(t)
py_compile.compile(OUT, doraise=True)
print(f"DERIVE OK: {OUT} ({len(t)} chars, template 50608); py_compile green")
print("NEXT: run the editor (gates fail-closed) -> pf/n1 selftest -> pathspec commit+push -> PRE-FINALIZE six-gate -> engine self-burn verify (2-cycle n1_w235 growth)")
