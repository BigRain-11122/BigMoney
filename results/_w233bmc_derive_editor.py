# -*- coding: utf-8 -*-
# r973 bm-c derive: W232 -> W233 five-face freeze editor (count-asserted ordered
# transform; fail-closed pair law; protect-restore sentinels for fixed-estate faces).
# Template = committed _w232bmc_freeze_edits.py (49,833-char text, r968 freeze-window
# generation, splice estate committed+pushed by the dead r968 window itself as
# e58dbcda3, proven live-fire; residual estate absorbed by the r968-continuation
# closeout cf3501cd9). All wave facts shift by token; every machine-derivable fact
# is re-asserted at editor RUNTIME against live template text (fail-closed).
# Sentinel blocks (KEPT/LIVE/LEG230/LEG231/ASM) are extracted from the template at
# RUNTIME by anchored index -- zero hand-transcription of fixed-estate faces (E63 law).
# Census evidence = results/_r973bmc_w233derive_census.py re-run THIS window
# (counts in hand: W232=72 / W231=114 / W230=11 / W229=11 / w232_=11(9 self post
# n1-shift) / w231_=97(94 post-sentinels) / w230_=8(5 post-sentinels) / w229_=3
# / n1_w232=5 / n1w232=2 / aee0bd9fa=7 (6 shift + 1 KEPT) / 0636c1d12=2 /
# 492972ee7=3 = 4e373b743=3 ALL inside compound pair regions / MSG-1345=4 / MSG-1155=2
# / 6638ddf9f=2 / 8d3a1b78a=1 / a3a7aa632=1 / NINETY-SECOND instance=5 / 62nd=6 /
# bmc_ordinal=62=3 / TWO HUNDRED AND THIRTY-SECOND=3 / sixty-second=2 / r968 freeze
# window=4 / r968 freeze-window bundle=2 / r967 prereg derived=1 / r967 window=1 /
# twenty-first consecutive=2 / sixth consecutive=2 / SIXTEEN-level=1 / if w < 232)=5
# / range(16, 232)=2 / range(17, 232)=3 / below 232 composes=2 / below-232=2 /
# arith_a232=3 / arith_b232=3 / n3r1_used232=3 / WAVE_CONFIGS[232]=2 /
# WAVE_CONFIGS[231]=3 / pf.N1_BANDS[231]=5 (4 shift + 1 LEG231-internal) / _c231=5 /
# N1_BANDS.get(231)=1 / 931_989=1 / 506_120=1 / 931,989=2 / 506,120=2 / (525_204,
# 527_203)=1 / (527_204, 527_403)=1 / par_sec==87 x1 / par_full==89 x1 /
# _block_kept=23 / KEPT materializer faces=25 raw, block W209..W231=23).
# Disclosed deltas vs the mechanical clone (correctness pairs, machine-verifiable
# against the committed W233 probe receipt results/_w233bmc_20261013_probe_receipt.json
# and the W233 seat commit dd38a9da8):
#  (a) the ("dead r963 window"->"dead r966 window") shift family DROPPED vs the W232
#      editor: census zero bare "dead r966 window" faces outside KEPT (all four former
#      dead-window cycle-prose regions were rewritten by the W232 editor's pairs into
#      committed+pushed-by-itself phrasing; the W233 pairs carry the cycle-prose aging);
#  (b) upstream W232-cycle prose written honestly: splice e58dbcda3 committed+pushed
#      by the dead r968 window ITSELF (session died post-S6 pre-closeout; residual
#      estate absorbed by the r968-continuation cf3501cd9) + engine self-burn 12/12
#      (5c90051e0+776b15270) + finalize one-pass r968 15:2x 59856ff28 (six-gate
#      PRE-FINALIZE correct phase standing law held, seventh consecutive);
#  (c) prereg_bundle note pair stays DROPPED (all note faces age via bare shifts:
#      r967 window->r972 + a3a7aa632->2a21ef7c + SIXTEEN-level->SEVENTEEN-level +
#      r968 freeze window->r973 + twenty-first->twenty-second + W231->W232).
import os, sys, py_compile, json

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.join(HERE, "_w232bmc_freeze_edits.py")
OUT  = os.path.join(HERE, "_w233bmc_freeze_edits.py")

t = open(BASE, "r", encoding="utf-8", newline="").read()
assert len(t) == 49833, f"template length drift: {len(t)} != 49833"

def rep(old, new, n=1):
    global t
    c = t.count(old)
    assert c == n, f"PAIR FAIL count {c} != {n}: {old[:110]!r}"
    t = t.replace(old, new)

# ---------------- phase 0: sentinels (RUNTIME anchored extraction) ----------------
# KEPT block: W209 estate-source line .. W231 prior-block-kept line (23 assert lines)
k0 = t.index("assert n1_t4.count('    # --- W209 materializer face')")
k1 = t.index("assert n1_t4.count('    # --- W231 materializer face')")
k2 = t.index("\n", k1)
KEPT_ORIG = t[k0:k2]
assert KEPT_ORIG.count("\nassert ") == 22, f"KEPT block shape: {KEPT_ORIG.count(chr(10)+'assert ')}"
assert KEPT_ORIG.count("materializer face") == 23
rep(KEPT_ORIG, "@@KEPT@@", 1)

# LIVE line (liveness_anchors single-line JSON face)
l0 = t.index('"liveness_anchors"')
l0 = t.rindex("\n", 0, l0) + 1
l1 = t.index("\n", l0)
LIVE_ORIG = t[l0:l1]
assert LIVE_ORIG.count("_block_kept") == 23, f"LIVE shape: {LIVE_ORIG.count('_block_kept')}"  # w209..w231
rep(LIVE_ORIG, "@@LIVE@@", 1)

# LEG230 (template w230_leg def, 6 lines) -- protected from w230_->w231_ + W230->W231 aging
g0 = t.index("w230_leg = [")
g2 = t.index("\n]", g0) + 2
LEG230_ORIG = t[g0:g2]
assert LEG230_ORIG.count("N1_BANDS[230]") == 5 and LEG230_ORIG.count("W230 row parity drift") == 1
rep(LEG230_ORIG, "@@LEG230@@", 1)

# LEG231 (template w231_leg def, 6 lines) -- protected from w231_->w232_ + W231->W232 aging
h0 = t.index("w231_leg = [")
h2 = t.index("\n]", h0) + 2
LEG231_ORIG = t[h0:h2]
assert LEG231_ORIG.count("N1_BANDS[231]") == 5 and LEG231_ORIG.count("W231 row parity drift") == 1
rep(LEG231_ORIG, "@@LEG231@@", 1)

# ASM join line (RUNTIME anchored extraction -- E63 law: zero hand-transcription)
a0 = t.index("block = EOL.join(hdr)")
a1 = t.index("\n", a0)
ASM_ORIG = t[a0:a1]
assert ASM_ORIG.count("EOL.join(w229_leg)") == 1 and ASM_ORIG.count("EOL.join(w230_leg)") == 1 \
    and ASM_ORIG.count("EOL.join(w231_leg)") == 1 and ASM_ORIG.count("EOL.join(tail)") == 1, \
    f"ASM shape: {ASM_ORIG!r}"
rep(ASM_ORIG, "@@ASM@@", 1)

# ---------------- phase 1: ordered global shifts (descending, count-logged) ----------------
SHIFTS = [
 # --- self wave faces (W232 -> W233) ---
 ("n1_w232", "n1_w233", 5),            # self shard/out names (BEFORE w232_ var shift, substring law)
 ("w232_", "w233_", 9),               # self vars (census 11 - 2 n1_w232_results rides = 9)
 ("n1w232", "n1w233", 2),              # entry-identity tags
 ("W232", "W233", 72),                # self prose global (incl. PERPETUAL_N1_W232_PREREG x5 + batch x2)
 ("_w232bmc_20261013_probe_receipt.json", "_w233bmc_20261013_probe_receipt.json", 9),
 ("_w232bmc_freeze_receipt.json", "_w233bmc_freeze_receipt.json", 1),
 ("_w231bmc_freeze_edits.py", "_w232bmc_freeze_edits.py", 1),   # lineage template name (upstream->self)
 ("_set_wave(232)", "_set_wave(233)", 1),
 ('"wave": 232,', '"wave": 233,', 1),
 ("f'{CFG_I}232: ", "f'{CFG_I}233: ", 1),
 ("f'{ROW_I}232: ", "f'{ROW_I}233: ", 1),
 ("f'232: {{\"a\":", "f'233: {{\"a\":", 1),
 ("ROW_I + '232: {\"a\"'", "ROW_I + '233: {\"a\"'", 1),
 ("WAVE_CONFIGS[232]", "WAVE_CONFIGS[233]", 2),       # band-facts self asserts (BEFORE the [231]->[232] mirror shift)
 ("seat MSG-1232 tail", "seat MSG-1233 tail", 1),
 ("wave 232 = first free number", "wave 233 = first free number", 1),
 ("wave 232: ", "wave 233: ", 1),
 ("if w < 232)", "if w < 233)", 5),
 ("range(16, 232)", "range(16, 233)", 2),
 ("range(17, 232)", "range(17, 233)", 3),
 ("w<232 count", "w<233 count", 1),
 ("if w < 231", "if w < 232", 1),          # family-6 prior-wave 0-check (no paren tail -- distinct face)
 ("w<231 leaked", "w<232 leaked", 1),     # family-6 prior-wave leak prose
 ("below 232 composes", "below 233 composes", 2),
 ("below-232", "below-233", 2),
 ("arith_a232", "arith_a233", 3),
 ("arith_b232", "arith_b233", 3),
 ("n3r1_used232", "n3r1_used233", 3),
 # --- projection aging (W233 -> W234) ---
 ("W233+ projection", "W234+ projection", 2),
 ("naive W233 A window", "naive W234 A window", 2),
 ("W233 freezer", "W234 freezer", 1),
 ("W233+ freezer", "W234+ freezer", 1),
 ("downstream W233 seat NOT yet published", "downstream W234 seat NOT yet published", 1),
 ("downstream W233 seat publication pending", "downstream W234 seat publication pending", 1),
 ("NINETY-THIRD instance anticipated", "NINETY-FOURTH instance anticipated", 2),
 # --- self ordinal/prose aging ---
 ("NINETY-SECOND instance", "NINETY-THIRD instance", 5),
 ("TWO HUNDRED AND THIRTY-SECOND", "TWO HUNDRED AND THIRTY-THIRD", 3),
 ("sixty-second", "sixty-third", 2),
 ("62nd", "63rd", 6),
 ("bmc_ordinal=62", "bmc_ordinal=63", 3),
 ("rows 61 + candidate", "rows 62 + candidate", 4),
 ("rows 221 + candidate", "rows 222 + candidate", 1),
 ("== 221 and len(bmc_rows_live) == 61", "== 222 and len(bmc_rows_live) == 62", 1),
 ("expect 221/61", "expect 222/62", 1),
 ("precedent 220/60 pre-splice", "precedent 221/61 pre-splice", 1),
 ("splice 221/61", "splice 222/62", 1),
 ("r968 freeze window", "r973 freeze window", 4),
 ("r968 freeze-window bundle", "r973 freeze-window bundle", 2),
 ("r967 prereg derived", "r972 prereg derived", 1),
 ("r967 window", "r972 window", 1),
 ("twenty-first consecutive", "twenty-second consecutive", 2),
 ("sixth consecutive", "seventh consecutive", 2),
 ("SIXTEEN-level", "SEVENTEEN-level", 1),
 # --- seat/provenance aging (self swap FIRST, then upstream) ---
 ("MSG-20261013-1345-bmc", "MSG-20261013-1530-bmc", 4),   # self seat swap FIRST
 ("MSG-20261013-1155-bmc", "MSG-20261013-1345-bmc", 2),   # upstream seat AFTER self swap
 ("8d3a1b78a", "dd38a9da8", 1),                            # SEAT_ORIGIN BEFORE 6638ddf9f aging
 ("6638ddf9f", "8d3a1b78a", 2),                            # upstream seat-origin provenance x2
 ("a3a7aa63230e87cb5a6212f54a07bc1738dde5b3", "2a21ef7cc4eaaa70375c7e4baec99f423488d5e2", 1),  # self prereg sha
 # --- band/ledger fact aging (self W232 facts -> W233 facts) ---
 ("(525_204, 527_203)", "(527_404, 529_403)", 1),
 ("(527_204, 527_403)", "(529_404, 529_603)", 1),
 ("931_989", "934_189", 1),
 ("506_120", "508_320", 1),
 ("931,989", "934,189", 2),
 ("506,120", "508,320", 2),
 # --- upstream cycle shas aging ---
 ("aee0bd9fa", "e58dbcda3", 6),            # KEPT-internal 1 excluded by sentinel
 ("0636c1d12", "59856ff28", 2),
 # engine-append shas (492972ee7/4e373b743) carried ENTIRELY by the P10 prose + receipt
 # upstream pairs (census: 492972ee7=3 / 4e373b743=3, ALL inside "492972ee7+4e373b743"
 # compound pair regions, zero standalone -- delta (a): dead-window shift family dropped)
 ("r966 13:2x", "r968 15:2x", 3),
 ("probe receipt @ r966 window", "probe receipt @ r968 window", 2),
 ("r966 probe leg0", "r968 probe leg0", 1),
 ("r966 seat-time live face", "r968 seat-time live face", 1),
 # --- upstream wave faces (W231 -> W232; descending) ---
 ("W231", "W232", 111),               # upstream prose global (census 114 - KEPT-internal 2 - LEG231-internal 1)
 ("w231_", "w232_", 94),              # upstream vars (census 97 - LEG231 def 1 - ASM join 1 - LIVE w231_block_kept 1)
 ("W230", "W231", 8),                # upstream-upstream prose (census 11 - KEPT-internal 2 - LEG230-internal 1)
 ("w230_", "w231_", 5),              # upstream-upstream vars (census 8 - LEG230 def 1 - ASM join 1 - LIVE 1)
 ("W229", "W230", 9),                # upstream-upstream-upstream prose (census 11 - KEPT-internal 2; w229_leg def face ages then pair-restores)
 ("m229", "m230", 3),
 ("N1_BANDS\\[229\\]", "N1_BANDS\\[230\\]", 1),   # m-cut regex literal (raw-bracket form)
 ("_c231", "_c232", 5),
 ("'231: {\"batch\"'", "'232: {\"batch\"'", 2),   # upstream cfg needles
 ("'231: {\"a\"'", "'232: {\"a\"'", 2),           # upstream row needles
 ("'    231: {\"a\"'", "'    232: {\"a\"'", 1),
 ("N1_BANDS.get(231)", "N1_BANDS.get(232)", 1),
 ("WAVE_CONFIGS[231]", "WAVE_CONFIGS[232]", 3),       # upstream mirror asserts (AFTER self [232]->[233])
 ("pf.N1_BANDS[231]", "pf.N1_BANDS[232]", 4),   # mirror x3 + post-edit gate x1 (LEG231-internal assert face excluded)
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
pair("""# 2026-10-13 14:5x bm-c r968 freeze window (upstream W1..W231 ALL LANDED, clean precondition): W232 five-face freeze splice editor.""",
"""# 2026-10-13 19:2x bm-c r973 freeze window (upstream W1..W232 ALL LANDED, clean precondition): W233 five-face freeze splice editor.""")
# regression guards for the window-label pair (new side must carry the SHIFTED wave faces)
assert t.count("(upstream W1..W232 ALL LANDED, clean precondition): W233 five-face") == 1
assert t.count("W232 five-face freeze splice editor") == 0

pair("""# present (W231 finalize one-pass r966 13:2x landed in-window 0636c1d12; splice
# estate aee0bd9fa committed+pushed by r966 itself in the r966 window (session
# died post-push pre-closeout; residual estate absorbed by r967), net chain head 931,989, merged pool K=506,120,
# n1_w231_results.json machine-read) -- ZERO in-flight upstream seats,""",
"""# present (W232 finalize one-pass r968 15:2x landed in-window 59856ff28; splice
# estate e58dbcda3 committed+pushed by r968 itself in the r968 window (session
# died post-S6 pre-closeout; residual estate absorbed by the r968-continuation cf3501cd9), net chain head 934,189, merged pool K=508,320,
# n1_w232_results.json machine-read) -- ZERO in-flight upstream seats,""")

pair("""# Lineage: _w231bmc_freeze_edits.py pattern (proven live-fire freeze,
# aee0bd9fa committed+pushed by r966 itself, machine-verified by
# r967-absorb receipt) + r787 preflight law + r609""",
"""# Lineage: _w232bmc_freeze_edits.py pattern (proven live-fire freeze,
# e58dbcda3 committed+pushed by r968 itself, machine-verified by
# the r968-continuation closeout receipt) + r787 preflight law + r609""")

pair("""# LHS/RHS/comment ATOMIC TRIPLE absorbed (the new block's w<232>/
# range(16,232)/below-232 triple is count-asserted atomically; the W231
# block's own w<231 face is legitimate prior-wave boundary, not stale).""",
"""# LHS/RHS/comment ATOMIC TRIPLE absorbed (the new block's w<233>/
# range(16,233)/below-233 triple is count-asserted atomically; the W232
# block's own w<232 face is legitimate prior-wave boundary, not stale).""")

pair("""# STRUCTURAL CHOICE (vs the W230 editor): the parity estate (W138..W206
# full-span, 69 rows, r858 absorb generation) is extracted from the OWN W231
# block physical bytes -- structure known exactly (this machine's own splice
# generation) -- the W231 block's own W229 leg (1 row) is excluded from the
# estate path and fresh W229 + W230 + W231 legs are appended for the W232
# block parity (90 rows: estate 69 + W211..W228 legs + W229 leg + W230 leg +
# W231 leg). Extraction self-asserts the 87-row cut (69 estate + W211..W227 +
# W228) regardless.""",
"""# STRUCTURAL CHOICE (vs the W231 editor): the parity estate (W138..W206
# full-span, 69 rows, r858 absorb generation) is extracted from the OWN W232
# block physical bytes -- structure known exactly (this machine's own splice
# generation) -- the W232 block's own W230 leg (1 row) is excluded from the
# estate path and fresh W230 + W231 + W232 legs are appended for the W233
# block parity (91 rows: estate 69 + W211..W229 legs + W230 leg + W231 leg +
# W232 leg). Extraction self-asserts the 88-row cut (69 estate + W211..W228 +
# W229) regardless.""")

pair("""# STRUCTURAL CHOICE: extract the estate from the OWN W231 block (bytes known
# exactly: full-span estate W138..W206 69 rows + own W211 leg + ... + own W228 leg) -- the W231 block is this machine's own splice generation
# (r966 window editor, estate committed+pushed by r966 itself as aee0bd9fa), structure known. The W231 block span ends where the
# T-141 s2 lane face marker begins.""",
"""# STRUCTURAL CHOICE: extract the estate from the OWN W232 block (bytes known
# exactly: full-span estate W138..W206 69 rows + own W211 leg + ... + own W229 leg) -- the W232 block is this machine's own splice generation
# (r968 window editor, estate committed+pushed by r968 itself as e58dbcda3), structure known. The W232 block span ends where the
# T-141 s2 lane face marker begins.""")

# --- transitive window slide (multi-wave faces the global shifts corrupt) ---
pair('f"W231+W230+W229+W228+W227 finalize products present "',
     'f"W232+W231+W230+W229+W228 finalize products present "')

pair("W230/W229/W228/W227 finalize are transitive deps",
     "W231/W230/W229/W228 finalize are transitive deps")

# --- seat/prose fixups (post-shift anchors) ---
pair(" " + "MSG-20261013-1155-bmc, executed bm-c r966 (seat 6638ddf9f); splice aee0bd9fa r966 window committed+pushed by r966 itself (estate machine-verified); engine self-burn 12/12 (492972ee7+4e373b743); finalize one-pass r966 13:2x; six-gate PRE-FINALIZE correct phase standing law held, sixth consecutive), ",
     " " + "MSG-20261013-1345-bmc, executed bm-c r968 (seat 8d3a1b78a); splice e58dbcda3 r968 window committed+pushed by r968 itself (estate machine-verified); engine self-burn 12/12 (5c90051e0+776b15270); finalize one-pass r968 15:2x; six-gate PRE-FINALIZE correct phase standing law held, seventh consecutive), ")

pair(''' "    #     MSG-20261013-1155-bmc, executed bm-c r966 (seat 6638ddf9f); splice",
 "    #     aee0bd9fa r966 window committed+pushed by r966 itself (estate",
 "    #     machine-verified); engine self-burn 12/12 (492972ee7+4e373b743) + finalize one-pass r966 13:2x",
 "    #     splice estate + PRE-FINALIZE six-gate chain (standing law held, sixth",
 "    #     consecutive -- THIS W232 cycle runs PRE-FINALIZE likewise), honest note)",''',
''' "    #     MSG-20261013-1345-bmc, executed bm-c r968 (seat 8d3a1b78a); splice",
 "    #     e58dbcda3 r968 window committed+pushed by r968 itself (estate",
 "    #     machine-verified); engine self-burn 12/12 (5c90051e0+776b15270) + finalize one-pass r968 15:2x",
 "    #     splice estate + PRE-FINALIZE six-gate chain (standing law held, seventh",
 "    #     consecutive -- THIS W233 cycle runs PRE-FINALIZE likewise), honest note)",''')

pair('''"    #     seat MSG + pre-seat probe script + probe receipt @ r966 window; per-wave prereg",
 "    #     r967 + freeze splice script landed in this r968 freeze-window bundle",''',
'''"    #     seat MSG + pre-seat probe script + probe receipt @ r968 window; per-wave prereg",
 "    #     r972 + freeze splice script landed in this r973 freeze-window bundle",''')

pair(''' "seat MSG + pre-seat probe script + probe receipt @ r966 window; per-wave prereg ",
 "r967 + freeze splice script landed in this r968 freeze-window bundle ",''',
''' "seat MSG + pre-seat probe script + probe receipt @ r968 window; per-wave prereg ",
 "r972 + freeze splice script landed in this r973 freeze-window bundle ",''')

# --- correctness delta (a): probe-receipt ordinal aging face fixed (disclosed header) ---
pair("ordinal machine-read NINETY-SECOND per probe receipt",
     "ordinal machine-read NINETY-THIRD per probe receipt")

pair('"machine-checkable = A-hops-prior-B staircase NINETY-SECOND ",',
     '"machine-checkable = A-hops-prior-B staircase NINETY-THIRD ",')

# --- estate/parity count pairs ---
pair('assert par_sec.count("assert pf.N1_BANDS[") == 87 \\',
     'assert par_sec.count("assert pf.N1_BANDS[") == 88 \\')
pair("    and int(_estate_ws[84]) == 226 \\\n    and int(_estate_ws[85]) == 227 \\\n    and int(_estate_ws[86]) == 228, \\",
     "    and int(_estate_ws[84]) == 226 \\\n    and int(_estate_ws[85]) == 227 \\\n    and int(_estate_ws[86]) == 228 \\\n    and int(_estate_ws[87]) == 229, \\")
pair('f"estate segment not W138..W206 full-span 69 rows + W211..W227 legs + W228 leg: n=',
     'f"estate segment not W138..W206 full-span 69 rows + W211..W228 legs + W229 leg: n=')
pair('assert par_full.count("assert pf.N1_BANDS[") == 89, \\',
     'assert par_full.count("assert pf.N1_BANDS[") == 90, \\')
pair("!= 89 (69 estate + W211..W226 legs + W227 leg + W228 leg + W229 leg + W230 leg)\"",
     "!= 90 (69 estate + W211..W227 legs + W228 leg + W229 leg + W230 leg + W231 leg)\"")

# --- cfg/row key literals (self-keyed gate strings, colon-continuation form) ---
pair("assert new_cfg.count('232: {\"batch\": \"PERPETUAL-N1-W232\"') == 1",
     "assert new_cfg.count('233: {\"batch\": \"PERPETUAL-N1-W233\"') == 1")
pair("assert n1_t4.count('232: {\"batch\": \"PERPETUAL-N1-W232\"') == 1",
     "assert n1_t4.count('233: {\"batch\": \"PERPETUAL-N1-W233\"') == 1")

# --- post-edit gate value-source fix (pf_mod faces stay [231] under the bare shift; [232] value source) ---
pair("""assert n1_t4.count(f'assert pf.N1_BANDS[231] == {{"a": ({fmt(pf_mod.N1_BANDS[231]["a"][0])}, {fmt(pf_mod.N1_BANDS[231]["a"][1])}),') == 1""",
     """assert n1_t4.count(f'assert pf.N1_BANDS[232] == {{"a": ({fmt(pf_mod.N1_BANDS[232]["a"][0])}, {fmt(pf_mod.N1_BANDS[232]["a"][1])}),') == 1""")

# --- w229_leg def -> w232_leg def (drop oldest leg, add newest; content [232]) ---
pair("""w229_leg = [
 f'        assert pf.N1_BANDS[229] == {{"a": ({fmt(pf_mod.N1_BANDS[229]["a"][0])}, {fmt(pf_mod.N1_BANDS[229]["a"][1])}),',
 f'                                    "b_exit": ({fmt(pf_mod.N1_BANDS[229]["b_exit"][0])}, {fmt(pf_mod.N1_BANDS[229]["b_exit"][1])}),',
'                                    "engine_owner": "bm-c"}, \\\\',
'            "registered W229 row parity drift (r307; bm-c five-face freeze; own-seat face disclosed)"',
]""",
"""w232_leg = [
 f'        assert pf.N1_BANDS[232] == {{"a": ({fmt(pf_mod.N1_BANDS[232]["a"][0])}, {fmt(pf_mod.N1_BANDS[232]["a"][1])}),',
 f'                                    "b_exit": ({fmt(pf_mod.N1_BANDS[232]["b_exit"][0])}, {fmt(pf_mod.N1_BANDS[232]["b_exit"][1])}),',
'                                    "engine_owner": "bm-c"}, \\\\',
'            "registered W232 row parity drift (r307; bm-c five-face freeze; own-seat face disclosed)"',
]""")

# --- receipt upstream + transitive block ---
pair('''  "w231_upstream": {"freeze_sha": w231_freeze_sha, "prereg_sha": w231_prereg_sha,
                    "ledger_total": w231_total, "merged_n": w231_merged_n,
                    "engine_owner": "bm-c (own seat honored, no takeover face)",
                    "repair_chain_note": "r966 splice (W231 freeze landed aee0bd9fa r966 window, estate committed+pushed by r966 itself; session died post-push pre-closeout, residual absorbed by r967) + engine self-burn 12/12 (492972ee7+4e373b743) + r966 finalize one-pass 13:2x 0636c1d12 (six-gate PRE-FINALIZE correct phase -- standing law held, sixth consecutive)"},''',
'''  "w232_upstream": {"freeze_sha": w232_freeze_sha, "prereg_sha": w232_prereg_sha,
                    "ledger_total": w232_total, "merged_n": w232_merged_n,
                    "engine_owner": "bm-c (own seat honored, no takeover face)",
                    "repair_chain_note": "r968 splice (W232 freeze landed e58dbcda3 r968 window, estate committed+pushed by r968 itself; session died post-S6 pre-closeout, residual absorbed by the r968-continuation) + engine self-burn 12/12 (5c90051e0+776b15270) + r968 finalize one-pass 15:2x 59856ff28 (six-gate PRE-FINALIZE correct phase -- standing law held, seventh consecutive)"},''')

pair('''  "w230_transitive": {"finalize_product": "results/perpetual_faces/n1_w230_results.json present (belt-and-braces gate; ledger 929,789 / K=503,920)"},''',
     '''  "w231_transitive": {"finalize_product": "results/perpetual_faces/n1_w231_results.json present (belt-and-braces gate; ledger 931,989 / K=506,120)"},''')

# --- receipt parity + family6 notes ---
pair("full-span estate W138..W206 (69 rows, r858 absorb generation) + W211..W228 legs + W229 leg + W230 leg + W231 leg -> W232 block = 90 rows ending at W231;",
     "full-span estate W138..W206 (69 rows, r858 absorb generation) + W211..W229 legs + W230 leg + W231 leg + W232 leg -> W233 block = 91 rows ending at W232;")

pair('"note": "W231 editor family-6 gate carried forward: new block LHS w<232 x3 / RHS range(16,232)+range(17,232) / comment below-232 count-asserted ATOMICALLY before splice; W231 block\'s own w<231 face = legitimate prior-wave boundary (not stale)"',
     '"note": "W232 editor family-6 gate carried forward: new block LHS w<233 x3 / RHS range(16,233)+range(17,233) / comment below-233 count-asserted ATOMICALLY before splice; W232 block\'s own w<232 face = legitimate prior-wave boundary (not stale)"')

# --- receipt ordinal faces ---
pair('''                    "probe_receipt_bmc_ordinal_face": 62,''',
     '''                    "probe_receipt_bmc_ordinal_face": 63,''')

# ---------------- phase 3: sentinel restores (with W233 additions) ----------------
rep("@@KEPT@@", KEPT_ORIG + "\nassert n1_t4.count('    # --- W232 materializer face') == 1  # prior block kept (W232 splice landed e58dbcda3 r968 window, estate machine-verified; committed+pushed by r968 itself, session died post-S6 pre-closeout, residual estate absorbed by the r968-continuation)", 1)
rep("@@LIVE@@", LIVE_ORIG.replace('"w231_block_kept": 1},', '"w231_block_kept": 1, "w232_block_kept": 1},'), 1)
rep("@@LEG230@@", LEG230_ORIG, 1)
rep("@@LEG231@@", LEG231_ORIG, 1)
# ASM restore = machine-derived aging of the extracted face (descending-order leg
# aging: w231->w232 first, then w230->w231, then w229->w230; no cascades since each
# target is lower than every remaining source)
ASM_NEW = (ASM_ORIG.replace("w231_leg", "w232_leg")
                  .replace("w230_leg", "w231_leg")
                  .replace("w229_leg", "w230_leg"))
assert ASM_NEW == "block = EOL.join(hdr) + EOL + par_sec + EOL.join(w230_leg) + EOL + EOL.join(w231_leg) + EOL + EOL.join(w232_leg) + EOL + EOL.join(tail) + EOL", f"ASM_NEW drift: {ASM_NEW!r}"
rep("@@ASM@@", ASM_NEW, 1)

# ---------------- phase 4: validation (fail-closed) ----------------
# kept-line legit faces (KEPT-internal splice history carries W229/W230/W231 verbatim)
assert t.count("aee0bd9fa") == 1, f"kept-line aee0bd9fa count {t.count('aee0bd9fa')} != 1"
assert t.count("dead r963 window") == 1, f"kept-line dead r963 window != 1"
assert t.count("r963-continuation") == 1, f"kept-line r963-continuation != 1"
assert t.count("2ae8553e6") == 1, f"kept-line 2ae8553e6 count {t.count('2ae8553e6')} != 1"
assert t.count("dead r961 window") == 1, f"kept-line dead r961 window != 1"
assert t.count("842f817ad") == 1, f"kept-line 842f817ad != 1"
assert t.count("dead r959 window") == 1, f"kept-line dead r959 window != 1"
assert t.count("r959-continuation") == 1, f"kept-line r959-continuation != 1"
# upstream-seat provenance faces (P10 prose carries the W232 seat origin sha)
assert t.count("8d3a1b78a") == 2, f"upstream seat-origin 8d3a1b78a count {t.count('8d3a1b78a')} != 2"

stale = ["(525_204, 527_203)", "(527_204, 527_403)",
 "a3a7aa63230e87cb5a6212f54a07bc1738dde5b3", "FIFTEEN-level", "MSG-20261013-1155-bmc",
 "r968 freeze window", "r968 freeze-window bundle",
 "expect 221/61", "precedent 220/60 pre-splice", "splice 221/61", "== 221 and len", "rows 221 + candidate",
 "rows 61 + candidate", "bmc_ordinal=62", "62nd", "sixty-second",
 "NINETY-SECOND instance", "NINETY-SECOND",
 "TWO HUNDRED AND THIRTY-SECOND", "931_989", "506_120", "(expect 931,989",
 "r966 13:2x", "r966 seat-time", "probe receipt @ r966 window",
 "twenty-first consecutive", "sixth consecutive",
 "_w232bmc_20261013_probe_receipt.json", "_w232bmc_freeze_receipt.json",
 "w229_leg", "n1w232-", "N1_BANDS.get(231)", "if w < 232)", "if w < 231", "w<231 leaked",
 "range(16, 232)", "range(16,232)", "range(17, 232)", "below 232 composes", "below-232",
 "m229", "_c231", "n3r1_used232", "arith_a232", "arith_b232",
 "N1_BANDS\\[229\\]",
 "W233+ projection", "naive W233 A window", "W233 freezer", "W233+ freezer",
 "downstream W233 seat",
 "0636c1d12", "492972ee7", "4e373b743", "2ae8553e6x-guard",
 "e485a0b3f", "4e30ddf69", "c9e9e83b8x-guard",
 "@@KEPT@@", "@@LIVE@@", "@@LEG230@@", "@@LEG231@@", "@@ASM@@", "2a21ef7cc4eaaa70375c7e4baec99f423488d5e2" + "x-guard",
 '233: {"batch": "PERPETUAL-N1-W233"x-guard']
for s in stale:
    c = t.count(s)
    assert c == 0, f"STALE TOKEN {s!r} count {c} != 0"

must_one = ["_set_wave(233)",
 "f'{CFG_I}233: ", "f'{ROW_I}233: ", "ROW_I + '233: {\"a\"'", '"wave": 233',
 "MSG-20261013-1530-bmc.md", "dd38a9da8", "934_189", "508_320",
 "(expect 934,189 / 508,320)", "(527_404, 529_403)", "(529_404, 529_603)",
 "int(_estate_ws[87]) == 229", "2a21ef7cc4eaaa70375c7e4baec99f423488d5e2", "SEVENTEEN-level",
 '"probe_receipt_bmc_ordinal_face": 63,', '"w232_block_kept": 1}',
 "N1_BANDS.get(232)", "r968 probe leg0", "r968 seat-time live face",
 "r972 prereg derived", "88-row cut", '== 88 \\', '== 90, \\',
 "n1w233-0of12", "n1w233-11of12", "seat MSG-1233 tail",
 "ordinal machine-read NINETY-THIRD per probe receipt"]
for s in must_one:
    c = t.count(s)
    assert c == 1, f"MUST-ONE {s!r} count {c} != 1"

# --- calibration dump (dbg5): actual counts for the uncertain final faces ---
_cal = {s: t.count(s) for s in ["W231", "w231_", "n1_w232_results", "n1_w233_results",
 "e58dbcda3", "59856ff28", "r968 15:2x", "seventh consecutive", "91 rows", "w232_a_tail",
 "w232_b_tail", "w232_freeze_sha", "w232_prereg_sha", "w233_prereg_sha", "w233_receipt_sha",
 "W232", "w232_", "w230_leg", "w231_leg", "w232_leg", "r968", "twenty-second consecutive",
 "NINETY-THIRD instance", "NINETY-FOURTH instance anticipated", "dd38a9da8", "2a21ef7cc4eaaa70375c7e4baec99f423488d5e2",
 "n1_w233", "MSG-20261013-1530-bmc", "MSG-20261013-1345-bmc", "63rd", "sixty-third",
 "TWO HUNDRED AND THIRTY-THIRD", "W234+ projection", "naive W234 A window",
 "5c90051e0", "776b15270", "aee0bd9fa", "8d3a1b78a", "r973 freeze window",
 "WAVE_CONFIGS[233]", "WAVE_CONFIGS[232]", "w231_out_path", "w232_out_path", "w232_total",
 "w230_transitive", "w231_transitive", "w232_upstream",
 "assert pf.N1_BANDS[232] ==", "assert pf.N1_BANDS[231] ==", "assert pf.N1_BANDS[230] ==",
 "n1_w231_results.json", "n1_w232_results.json"]}
open(os.path.join(HERE, "_w233bmc_dbg5_counts.json"), "w", encoding="utf-8").write(json.dumps(_cal, indent=1))
print("DBG5 COUNTS:", json.dumps(_cal))

assert t.count("MSG-20261013-1530-bmc") == 4
assert t.count('233: {"batch": "PERPETUAL-N1-W233"') == 2   # new_cfg gate + n1_t4 post-edit gate
assert t.count("MSG-20261013-1345-bmc") == 2          # upstream seat references
assert t.count("W234+ projection") == 2
assert t.count("naive W234 A window") == 2
assert t.count("NINETY-FOURTH instance anticipated") == 2
assert t.count("NINETY-THIRD instance") == 5
assert t.count("TWO HUNDRED AND THIRTY-THIRD") == 3
assert t.count("sixty-third") == 2
assert t.count("63rd") == 6
assert t.count("bmc_ordinal=63") == 3
assert t.count("_w233bmc_20261013_probe_receipt.json") == 9
assert t.count("_w233bmc_freeze_receipt.json") == 1
assert t.count("w230_leg") == 2
assert t.count("w231_leg") == 2
assert t.count("w232_leg") == 2
assert t.count('"w231_transitive"') == 1
assert t.count('"w232_upstream"') == 2
assert t.count("assert pf.N1_BANDS[232] ==") == 2     # w232_leg def + post-edit gate
assert t.count("assert pf.N1_BANDS[231] ==") == 1     # w231_leg def (sentinel-kept)
assert t.count("assert pf.N1_BANDS[230] ==") == 1     # w230_leg def (sentinel-kept)
assert t.count("WAVE_CONFIGS[233]") == 2             # band-facts self asserts
assert t.count("WAVE_CONFIGS[232]") == 3             # upstream mirror asserts
assert t.count("w231_out_path") == 2
assert t.count("n1_w233") == 5
assert t.count("n1_w232_results") == 4               # upstream refs (shift-landed)
assert t.count("n1_w233_results") == 2               # self path refs (shift-landed)
assert t.count("e58dbcda3") >= 6
assert t.count("59856ff28") == 2
assert t.count("r968 15:2x") == 3
assert t.count("r973 freeze window") == 4
assert t.count("r973 freeze-window bundle") == 2
assert t.count("twenty-second consecutive") == 2
assert t.count("91 rows") == 2
assert t.count("if w < 233)") == 5
assert t.count("range(16, 233)") == 2
assert t.count("range(17, 233)") == 3
assert t.count("registered wave below 233 composes") == 2
assert t.count("seventh consecutive") == 2
assert t.count("w232_a_tail") == 14
assert t.count("w232_b_tail") == 9
assert t.count("w232_freeze_sha") == 6
assert t.count("w232_prereg_sha") == 3
assert t.count("w233_prereg_sha") == 5
assert t.count("w233_receipt_sha") == 4
assert t.count("1530") >= 1 and t.count("1345-bmc.md") == 0

open(OUT, "w", encoding="utf-8", newline="").write(t)
py_compile.compile(OUT, doraise=True)
print(f"DERIVE OK: {OUT} ({len(t)} chars, template 49833); py_compile green")
print("NEXT: run the editor (gates fail-closed) -> pf/n1 selftest -> pathspec commit+push -> PRE-FINALIZE six-gate -> engine self-burn verify (2-cycle n1_w233 growth)")
