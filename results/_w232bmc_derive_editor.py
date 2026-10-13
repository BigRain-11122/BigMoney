# -*- coding: utf-8 -*-
# r968 bm-c derive: W231 -> W232 five-face freeze editor (count-asserted ordered
# transform; fail-closed pair law; protect-restore sentinels for fixed-estate faces).
# Template = committed _w231bmc_freeze_edits.py (49,354-char text, r965 freeze-window
# generation, committed+pushed by r966 itself as splice estate aee0bd9fa, proven
# live-fire; session died post-push pre-closeout, residual estate absorbed by r967).
# All wave facts shift by token; every machine-derivable fact is re-asserted at
# editor RUNTIME against live template text (fail-closed). Sentinel blocks
# (KEPT/LIVE/LEG229/LEG230/ASM) are extracted from the template at RUNTIME by
# anchored index -- zero hand-transcription of fixed-estate faces.
# Census evidence = results/_r968bmc_w232derive_census.py (dead r968 window authoring)
# re-run THIS window -> results/_r968bmc_census_out.txt (counts in hand: W231=72 /
# W230=114 / W229=11 / W228=11 / w231_=11(9 self post n1-shift) / w230_=97 /
# w229_=8 / w228_=3 / n1_w231=5 / n1w231=2 / m228=3 / MSG-1155=4 / MSG-1000=2 /
# 6638ddf9f=1 / 6cfe285e3=2 / aebe0a5ac=1 / 24e12fa5e=7 / ce70c5808=2 /
# 0ef11a120=3 / aec41c57c=3 / r965 freeze window=4 / dead r963 window=5 /
# r963 11:5x=3 / NINETY-FIRST=7 / NINETY-SECOND=2 / 61st=6 / bmc_ordinal=61 x3).
# Disclosed deltas vs the mechanical clone (correctness pairs, machine-verifiable
# against the committed W232 probe receipt results/_w232bmc_20261013_probe_receipt.json):
#  (a) ordinal aging face fixed: template NINETY-FIRST (W231 self) -> NINETY-SECOND
#      (W232 self, per probe receipt leg1 A_semantics machine-read) and projection
#      NINETY-SECOND anticipated -> NINETY-THIRD anticipated;
#  (b) upstream W231-cycle prose written honestly: splice aee0bd9fa committed+pushed
#      by r966 ITSELF in the r966 window (NOT a dead-window absorb-continuation case --
#      session died post-push pre-closeout, residual estate absorbed by r967) +
#      engine self-burn 12/12 (492972ee7+4e373b743) + finalize one-pass 0636c1d12
#      (six-gate PRE-FINALIZE correct phase, SIXTH consecutive);
#  (c) m-cut assert pair DROPPED vs the W231 editor: the template's m-cut region
#      (m228 regex + "upstream W228 row leg not found inside W230 parity span")
#      is fully aged by the bare shifts alone (m228->m229 x3 + N1_BANDS\[228\]->\[229\]
#      + W228->W229 + W230->W231) -- no residual face needs a pair, disclosed;
#  (d) prereg_bundle note pair DROPPED vs the W231 editor: new bare shift
#      ("r964 window" -> "r967 window", 1) covers the only unaged face in the note
#      (all other note faces age via FIFTEEN/SIXTEEN + aebe0a5ac + r965/r968 +
#      twentieth/twenty-first + W230->W231 shifts), disclosed.
import os, sys, py_compile, json

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.join(HERE, "_w231bmc_freeze_edits.py")
OUT  = os.path.join(HERE, "_w232bmc_freeze_edits.py")

t = open(BASE, "r", encoding="utf-8", newline="").read()
assert len(t) == 49354, f"template length drift: {len(t)} != 49354"

def rep(old, new, n=1):
    global t
    c = t.count(old)
    assert c == n, f"PAIR FAIL count {c} != {n}: {old[:110]!r}"
    t = t.replace(old, new)

# ---------------- phase 0: sentinels (RUNTIME anchored extraction) ----------------
# KEPT block: W209 estate-source line .. W230 prior-block-kept line (22 assert lines)
k0 = t.index("assert n1_t4.count('    # --- W209 materializer face')")
k1 = t.index("assert n1_t4.count('    # --- W230 materializer face')")
k2 = t.index("\n", k1)
KEPT_ORIG = t[k0:k2]
assert KEPT_ORIG.count("\nassert ") == 21, f"KEPT block shape: {KEPT_ORIG.count(chr(10)+'assert ')}"
assert KEPT_ORIG.count("materializer face") == 22
rep(KEPT_ORIG, "@@KEPT@@", 1)

# LIVE line (liveness_anchors single-line JSON face)
l0 = t.index('"liveness_anchors"')
l0 = t.rindex("\n", 0, l0) + 1
l1 = t.index("\n", l0)
LIVE_ORIG = t[l0:l1]
assert LIVE_ORIG.count("_block_kept") == 22, f"LIVE shape: {LIVE_ORIG.count('_block_kept')}"  # w209..w230 + t141 not counted
rep(LIVE_ORIG, "@@LIVE@@", 1)

# LEG229 (template w229_leg def, 6 lines) -- protected from w229_->w230_ + W229->W230 aging
h0 = t.index("w229_leg = [")
h2 = t.index("\n]", h0) + 2
LEG229_ORIG = t[h0:h2]
assert LEG229_ORIG.count("N1_BANDS[229]") == 5 and LEG229_ORIG.count("W229 row parity drift") == 1
rep(LEG229_ORIG, "@@LEG229@@", 1)

# LEG230 (template w230_leg def, 6 lines) -- protected from w230_->w231_ + W230->W231 aging
g0 = t.index("w230_leg = [")
g2 = t.index("\n]", g0) + 2
LEG230_ORIG = t[g0:g2]
assert LEG230_ORIG.count("N1_BANDS[230]") == 5 and LEG230_ORIG.count("W230 row parity drift") == 1
rep(LEG230_ORIG, "@@LEG230@@", 1)

# ASM join line (RUNTIME anchored extraction -- E63 heal: dead r968 window hand-transcribed
# this face with a spurious "+ EOL" after par_sec; anchored index extraction is
# transcription-drift-immune, same law as KEPT/LIVE/LEG229/LEG230 above)
a0 = t.index("block = EOL.join(hdr)")
a1 = t.index("\n", a0)
ASM_ORIG = t[a0:a1]
assert ASM_ORIG.count("EOL.join(w228_leg)") == 1 and ASM_ORIG.count("EOL.join(w229_leg)") == 1 \
    and ASM_ORIG.count("EOL.join(w230_leg)") == 1 and ASM_ORIG.count("EOL.join(tail)") == 1, \
    f"ASM shape: {ASM_ORIG!r}"
rep(ASM_ORIG, "@@ASM@@", 1)

# ---------------- phase 1: ordered global shifts (descending, count-logged) ----------------
SHIFTS = [
 # --- self wave faces (W231 -> W232) ---
 ("n1_w231", "n1_w232", 5),            # self shard/out names (BEFORE w231_ var shift, substring law)
 ("w231_", "w232_", 9),               # self vars (census 11 - 2 n1_w231_results rides = 9)
 ("n1w231", "n1w232", 2),              # entry-identity tags
 ("W231", "W232", 72),                # self prose global (incl. PERPETUAL_N1_W231_PREREG x5 + batch x2)
 ("_w231bmc_20261013_probe_receipt.json", "_w232bmc_20261013_probe_receipt.json", 9),
 ("_w231bmc_freeze_receipt.json", "_w232bmc_freeze_receipt.json", 1),
 ("_w230bmc_freeze_edits.py", "_w231bmc_freeze_edits.py", 1),   # lineage template name (upstream->self)
 ("_set_wave(231)", "_set_wave(232)", 1),
 ('"wave": 231,', '"wave": 232,', 1),
 ("f'{CFG_I}231: ", "f'{CFG_I}232: ", 1),
 ("f'{ROW_I}231: ", "f'{ROW_I}232: ", 1),
 ("f'231: {{\"a\":", "f'232: {{\"a\":", 1),
 ("ROW_I + '231: {\"a\"'", "ROW_I + '232: {\"a\"'", 1),
 ("WAVE_CONFIGS[231]", "WAVE_CONFIGS[232]", 2),       # band-facts self asserts (BEFORE the [230]->[231] mirror shift)
 ("seat MSG-1231 tail", "seat MSG-1232 tail", 1),
 ("wave 231 = first free number", "wave 232 = first free number", 1),
 ("wave 231: ", "wave 232: ", 1),
 ("if w < 231)", "if w < 232)", 5),
 ("range(16, 231)", "range(16, 232)", 2),
 ("range(17, 231)", "range(17, 232)", 3),
 ("w<231 count", "w<232 count", 1),
 ("if w < 230", "if w < 231", 1),          # family-6 prior-wave 0-check (no paren tail -- distinct face)
 ("w<230 leaked", "w<231 leaked", 1),     # family-6 prior-wave leak prose
 ("below 231 composes", "below 232 composes", 2),
 ("below-231", "below-232", 2),
 ("arith_a231", "arith_a232", 3),
 ("arith_b231", "arith_b232", 3),
 ("n3r1_used231", "n3r1_used232", 3),
 # --- projection aging (W232 -> W233) ---
 ("W232+ projection", "W233+ projection", 2),
 ("naive W232 A window", "naive W233 A window", 2),
 ("W232 freezer", "W233 freezer", 1),
 ("W232+ freezer", "W233+ freezer", 1),
 ("downstream W232 seat NOT yet published", "downstream W233 seat NOT yet published", 1),
 ("downstream W232 seat publication pending", "downstream W233 seat publication pending", 1),
 ("NINETY-SECOND instance anticipated", "NINETY-THIRD instance anticipated", 2),
 # --- self ordinal/prose aging ---
 ("NINETY-FIRST instance", "NINETY-SECOND instance", 5),
 ("TWO HUNDRED AND THIRTY-FIRST", "TWO HUNDRED AND THIRTY-SECOND", 3),
 ("sixty-first", "sixty-second", 2),
 ("61st", "62nd", 6),
 ("bmc_ordinal=61", "bmc_ordinal=62", 3),
 ("rows 60 + candidate", "rows 61 + candidate", 4),
 ("rows 220 + candidate", "rows 221 + candidate", 1),
 ("== 220 and len(bmc_rows_live) == 60", "== 221 and len(bmc_rows_live) == 61", 1),
 ("expect 220/60", "expect 221/61", 1),
 ("precedent 219/59 pre-splice", "precedent 220/60 pre-splice", 1),
 ("splice 220/60", "splice 221/61", 1),
 ("r965 freeze window", "r968 freeze window", 4),
 ("r965 freeze-window bundle", "r968 freeze-window bundle", 2),
 ("r964 prereg derived", "r967 prereg derived", 1),
 ("r964 window", "r967 window", 1),
 ("twentieth consecutive", "twenty-first consecutive", 2),
 ("fifth consecutive", "sixth consecutive", 2),
 ("FIFTEEN-level", "SIXTEEN-level", 1),
 # --- seat/provenance aging (self swap FIRST, then upstream) ---
 ("MSG-20261013-1155-bmc", "MSG-20261013-1345-bmc", 4),   # self seat swap FIRST
 ("MSG-20261013-1000-bmc", "MSG-20261013-1155-bmc", 2),   # upstream seat AFTER self swap
 ("6638ddf9f", "8d3a1b78a", 1),                            # SEAT_ORIGIN BEFORE 6cfe285e3 aging
 ("6cfe285e3", "6638ddf9f", 2),                            # upstream seat-origin provenance x2
 ("aebe0a5ac", "a3a7aa63230e87cb5a6212f54a07bc1738dde5b3", 1),  # self prereg sha
 # --- band/ledger fact aging (self W231 facts -> W232 facts) ---
 ("(523_004, 525_003)", "(525_204, 527_203)", 1),
 ("(525_004, 525_203)", "(527_204, 527_403)", 1),
 ("929_789", "931_989", 1),
 ("503_920", "506_120", 1),
 ("929,789", "931,989", 2),
 ("503,920", "506,120", 2),
 # --- upstream cycle shas aging ---
 ("24e12fa5e", "aee0bd9fa", 6),            # KEPT-internal 1 excluded by sentinel
 ("ce70c5808", "0636c1d12", 2),
 # engine-append shas (0ef11a120/aec41c57c) carried ENTIRELY by the P10 prose + receipt
 # upstream pairs (census: 0ef11a120=3 / aec41c57c=3, ALL inside pair regions, zero standalone)
 ("dead r963 window", "dead r966 window", 4),   # KEPT-internal 1 excluded by sentinel
 ("r963 11:5x", "r966 13:2x", 3),
 ("probe receipt @ r963 window", "probe receipt @ r966 window", 2),
 ("r963 probe leg0", "r966 probe leg0", 1),
 ("r963 seat-time live face", "r966 seat-time live face", 1),
 # --- upstream wave faces (W230 -> W231; descending) ---
 ("W230", "W231", 111),               # upstream prose global (census 114 - KEPT-internal 2 - LEG230-internal 1)
 ("w230_", "w231_", 94),              # upstream vars (census 97 - LEG230 def 1 - ASM join 1 - LIVE w230_block_kept 1)
 ("W229", "W230", 8),                # upstream-upstream prose (census 11 - KEPT-internal 2 - LEG229-internal 1)
 ("w229_", "w230_", 5),              # upstream-upstream vars (census 8 - LEG229 def 1 - ASM join 1 - LIVE 1)
 ("W228", "W229", 9),                # upstream-upstream-upstream prose (census 11 - KEPT-internal 2; w228_leg def face ages then pair-restores)
 ("m228", "m229", 3),
 ("N1_BANDS\\[228\\]", "N1_BANDS\\[229\\]", 1),   # m-cut regex literal (raw-bracket form)
 ("_c230", "_c231", 5),
 ("'230: {\"batch\"'", "'231: {\"batch\"'", 2),   # upstream cfg needles
 ("'230: {\"a\"'", "'231: {\"a\"'", 2),           # upstream row needles
 ("'    230: {\"a\"'", "'    231: {\"a\"'", 1),
 ("N1_BANDS.get(230)", "N1_BANDS.get(231)", 1),
 ("WAVE_CONFIGS[230]", "WAVE_CONFIGS[231]", 3),       # upstream mirror asserts (AFTER self [231]->[232])
 ("pf.N1_BANDS[230]", "pf.N1_BANDS[231]", 4),   # mirror x3 + post-edit gate x1 (LEG230-internal assert face excluded)
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
pair("""# 2026-10-13 12:4x bm-c r965 freeze window (upstream W1..W230 ALL LANDED, clean precondition): W231 five-face freeze splice editor.""",
"""# 2026-10-13 14:5x bm-c r968 freeze window (upstream W1..W231 ALL LANDED, clean precondition): W232 five-face freeze splice editor.""")
# regression guards for the window-label pair (new side must carry the SHIFTED wave faces)
assert t.count("(upstream W1..W231 ALL LANDED, clean precondition): W232 five-face") == 1
assert t.count("W231 five-face freeze splice editor") == 0

pair("""# present (W230 finalize one-pass r963 11:5x landed in-window ce70c5808; splice
# estate 24e12fa5e dead r963 window machine-verified then landed by
# r963 (absorb continuation), net chain head 929,789, merged pool K=503,920,
# n1_w230_results.json machine-read) -- ZERO in-flight upstream seats,""",
"""# present (W231 finalize one-pass r966 13:2x landed in-window 0636c1d12; splice
# estate aee0bd9fa committed+pushed by r966 itself in the r966 window (session
# died post-push pre-closeout; residual estate absorbed by r967), net chain head 931,989, merged pool K=506,120,
# n1_w231_results.json machine-read) -- ZERO in-flight upstream seats,""")

pair("""# Lineage: _w230bmc_freeze_edits.py pattern (proven live-fire freeze,
# r963 dead-window estate, machine-verified then landed 24e12fa5e by
# r963) + r787 preflight law + r609""",
"""# Lineage: _w231bmc_freeze_edits.py pattern (proven live-fire freeze,
# aee0bd9fa committed+pushed by r966 itself, machine-verified by
# r967-absorb receipt) + r787 preflight law + r609""")

pair("""# LHS/RHS/comment ATOMIC TRIPLE absorbed (the new block's w<231>/
# range(16,231)/below-231 triple is count-asserted atomically; the W230
# block's own w<230 face is legitimate prior-wave boundary, not stale).""",
"""# LHS/RHS/comment ATOMIC TRIPLE absorbed (the new block's w<232>/
# range(16,232)/below-232 triple is count-asserted atomically; the W231
# block's own w<231 face is legitimate prior-wave boundary, not stale).""")

pair("""# STRUCTURAL CHOICE (vs the W229 editor): the parity estate (W138..W206
# full-span, 69 rows, r858 absorb generation) is extracted from the OWN W230
# block physical bytes -- structure known exactly (this machine's own splice
# generation) -- the W230 block's own W228 leg (1 row) is excluded from the
# estate path and fresh W228 + W229 + W230 legs are appended for the W231
# block parity (89 rows: estate 69 + W211..W227 legs + W228 leg + W229 leg +
# W230 leg). Extraction self-asserts the 86-row cut (69 estate + W211..W226 +
# W227) regardless.""",
"""# STRUCTURAL CHOICE (vs the W230 editor): the parity estate (W138..W206
# full-span, 69 rows, r858 absorb generation) is extracted from the OWN W231
# block physical bytes -- structure known exactly (this machine's own splice
# generation) -- the W231 block's own W229 leg (1 row) is excluded from the
# estate path and fresh W229 + W230 + W231 legs are appended for the W232
# block parity (90 rows: estate 69 + W211..W228 legs + W229 leg + W230 leg +
# W231 leg). Extraction self-asserts the 87-row cut (69 estate + W211..W227 +
# W228) regardless.""")

pair("""# STRUCTURAL CHOICE: extract the estate from the OWN W230 block (bytes known
# exactly: full-span estate W138..W206 69 rows + own W211 leg + ... + own W227 leg) -- the W230 block is this machine's own splice generation
# (r963 freeze-window editor, estate machine-verified then landed 24e12fa5e by r963), structure known. The W230 block span ends where the
# T-141 s2 lane face marker begins.""",
"""# STRUCTURAL CHOICE: extract the estate from the OWN W231 block (bytes known
# exactly: full-span estate W138..W206 69 rows + own W211 leg + ... + own W228 leg) -- the W231 block is this machine's own splice generation
# (r966 window editor, estate committed+pushed by r966 itself as aee0bd9fa), structure known. The W231 block span ends where the
# T-141 s2 lane face marker begins.""")

# --- transitive window slide (multi-wave faces the global shifts corrupt) ---
pair('f"W230+W229+W228+W227+W226 finalize products present "',
     'f"W231+W230+W229+W228+W227 finalize products present "')

pair("W229/W228/W227/W226 finalize are transitive deps",
     "W230/W229/W228/W227 finalize are transitive deps")

# --- seat/prose fixups (post-shift anchors) ---
pair(" " + "MSG-20261013-1000-bmc, executed bm-c r962 (seat 6cfe285e3); splice 24e12fa5e dead r963 window estate machine-verified then landed by r963; engine self-burn 12/12 (0ef11a120+aec41c57c); finalize one-pass r963 11:5x; six-gate PRE-FINALIZE correct phase standing law held, fifth consecutive), ",
     " " + "MSG-20261013-1155-bmc, executed bm-c r966 (seat 6638ddf9f); splice aee0bd9fa r966 window committed+pushed by r966 itself (estate machine-verified); engine self-burn 12/12 (492972ee7+4e373b743); finalize one-pass r966 13:2x; six-gate PRE-FINALIZE correct phase standing law held, sixth consecutive), ")

pair(''' "    #     MSG-20261013-1000-bmc, executed bm-c r962 (seat 6cfe285e3); splice",
 "    #     24e12fa5e dead r963 window estate machine-verified then landed by",
 "    #     r963; engine self-burn 12/12 (0ef11a120+aec41c57c) + finalize one-pass r963 11:5x",
 "    #     splice estate + PRE-FINALIZE six-gate chain (standing law held, fifth",
 "    #     consecutive -- THIS W231 cycle runs PRE-FINALIZE likewise), honest note)",''',
''' "    #     MSG-20261013-1155-bmc, executed bm-c r966 (seat 6638ddf9f); splice",
 "    #     aee0bd9fa r966 window committed+pushed by r966 itself (estate",
 "    #     machine-verified); engine self-burn 12/12 (492972ee7+4e373b743) + finalize one-pass r966 13:2x",
 "    #     splice estate + PRE-FINALIZE six-gate chain (standing law held, sixth",
 "    #     consecutive -- THIS W232 cycle runs PRE-FINALIZE likewise), honest note)",''')

pair('''"    #     seat MSG + pre-seat probe script + probe receipt @ r963 window; per-wave prereg",
 "    #     r964 + freeze splice script landed in this r965 freeze-window bundle",''',
'''"    #     seat MSG + pre-seat probe script + probe receipt @ r966 window; per-wave prereg",
 "    #     r967 + freeze splice script landed in this r968 freeze-window bundle",''')

pair(''' "seat MSG + pre-seat probe script + probe receipt @ r963 window; per-wave prereg ",
 "r964 + freeze splice script landed in this r965 freeze-window bundle ",''',
''' "seat MSG + pre-seat probe script + probe receipt @ r966 window; per-wave prereg ",
 "r967 + freeze splice script landed in this r968 freeze-window bundle ",''')

# --- correctness delta (a): probe-receipt ordinal aging face fixed (disclosed header) ---
pair("ordinal machine-read NINETY-FIRST per probe receipt",
     "ordinal machine-read NINETY-SECOND per probe receipt")

pair('"machine-checkable = A-hops-prior-B staircase NINETY-FIRST ",',
     '"machine-checkable = A-hops-prior-B staircase NINETY-SECOND ",')

# --- estate/parity count pairs ---
pair('assert par_sec.count("assert pf.N1_BANDS[") == 86 \\',
     'assert par_sec.count("assert pf.N1_BANDS[") == 87 \\')
pair("    and int(_estate_ws[84]) == 226 \\\n    and int(_estate_ws[85]) == 227, \\",
     "    and int(_estate_ws[84]) == 226 \\\n    and int(_estate_ws[85]) == 227 \\\n    and int(_estate_ws[86]) == 228, \\")
pair('f"estate segment not W138..W206 full-span 69 rows + W211..W226 legs + W227 leg: n=',
     'f"estate segment not W138..W206 full-span 69 rows + W211..W227 legs + W228 leg: n=')
pair('assert par_full.count("assert pf.N1_BANDS[") == 88, \\',
     'assert par_full.count("assert pf.N1_BANDS[") == 89, \\')
pair("!= 88 (69 estate + W211..W225 legs + W226 leg + W227 leg + W228 leg + W229 leg)\"",
     "!= 89 (69 estate + W211..W226 legs + W227 leg + W228 leg + W229 leg + W230 leg)\"")

# --- cfg/row key literals (self-keyed gate strings, colon-continuation form) ---
pair("assert new_cfg.count('231: {\"batch\": \"PERPETUAL-N1-W231\"') == 1",
     "assert new_cfg.count('232: {\"batch\": \"PERPETUAL-N1-W232\"') == 1")
pair("assert n1_t4.count('231: {\"batch\": \"PERPETUAL-N1-W231\"') == 1",
     "assert n1_t4.count('232: {\"batch\": \"PERPETUAL-N1-W232\"') == 1")

# --- post-edit gate value-source fix (pf_mod faces stay [230] under the bare shift; [231] value source) ---
pair("""assert n1_t4.count(f'assert pf.N1_BANDS[230] == {{"a": ({fmt(pf_mod.N1_BANDS[230]["a"][0])}, {fmt(pf_mod.N1_BANDS[230]["a"][1])}),') == 1""",
     """assert n1_t4.count(f'assert pf.N1_BANDS[231] == {{"a": ({fmt(pf_mod.N1_BANDS[231]["a"][0])}, {fmt(pf_mod.N1_BANDS[231]["a"][1])}),') == 1""")

# --- w228_leg def -> w231_leg def (drop oldest leg, add newest; content [231]) ---
pair("""w228_leg = [
 f'        assert pf.N1_BANDS[228] == {{"a": ({fmt(pf_mod.N1_BANDS[228]["a"][0])}, {fmt(pf_mod.N1_BANDS[228]["a"][1])}),',
 f'                                    "b_exit": ({fmt(pf_mod.N1_BANDS[228]["b_exit"][0])}, {fmt(pf_mod.N1_BANDS[228]["b_exit"][1])}),',
'                                    "engine_owner": "bm-c"}, \\\\',
'            "registered W228 row parity drift (r307; bm-c five-face freeze; own-seat face disclosed)"',
]""",
"""w231_leg = [
 f'        assert pf.N1_BANDS[231] == {{"a": ({fmt(pf_mod.N1_BANDS[231]["a"][0])}, {fmt(pf_mod.N1_BANDS[231]["a"][1])}),',
 f'                                    "b_exit": ({fmt(pf_mod.N1_BANDS[231]["b_exit"][0])}, {fmt(pf_mod.N1_BANDS[231]["b_exit"][1])}),',
'                                    "engine_owner": "bm-c"}, \\\\',
'            "registered W231 row parity drift (r307; bm-c five-face freeze; own-seat face disclosed)"',
]""")

# --- receipt upstream + transitive block ---
pair('''  "w230_upstream": {"freeze_sha": w230_freeze_sha, "prereg_sha": w230_prereg_sha,
                    "ledger_total": w230_total, "merged_n": w230_merged_n,
                    "engine_owner": "bm-c (own seat honored, no takeover face)",
                    "repair_chain_note": "r963 splice (W230 freeze landed 24e12fa5e dead r963 window, estate machine-verified then landed by r963) + engine self-burn 12/12 (0ef11a120+aec41c57c) + r963 finalize one-pass 11:5x ce70c5808 (six-gate PRE-FINALIZE correct phase -- standing law held, fifth consecutive)"},''',
'''  "w231_upstream": {"freeze_sha": w231_freeze_sha, "prereg_sha": w231_prereg_sha,
                    "ledger_total": w231_total, "merged_n": w231_merged_n,
                    "engine_owner": "bm-c (own seat honored, no takeover face)",
                    "repair_chain_note": "r966 splice (W231 freeze landed aee0bd9fa r966 window, estate committed+pushed by r966 itself; session died post-push pre-closeout, residual absorbed by r967) + engine self-burn 12/12 (492972ee7+4e373b743) + r966 finalize one-pass 13:2x 0636c1d12 (six-gate PRE-FINALIZE correct phase -- standing law held, sixth consecutive)"},''')

pair('''  "w229_transitive": {"finalize_product": "results/perpetual_faces/n1_w229_results.json present (belt-and-braces gate; ledger 927,589 / K=501,720)"},''',
     '''  "w230_transitive": {"finalize_product": "results/perpetual_faces/n1_w230_results.json present (belt-and-braces gate; ledger 929,789 / K=503,920)"},''')

# --- receipt parity + family6 notes ---
pair("full-span estate W138..W206 (69 rows, r858 absorb generation) + W211..W227 legs + W228 leg + W229 leg + W230 leg -> W231 block = 89 rows ending at W230;",
     "full-span estate W138..W206 (69 rows, r858 absorb generation) + W211..W228 legs + W229 leg + W230 leg + W231 leg -> W232 block = 90 rows ending at W231;")

pair('"note": "W230 editor family-6 gate carried forward: new block LHS w<231 x3 / RHS range(16,231)+range(17,231) / comment below-231 count-asserted ATOMICALLY before splice; W230 block\'s own w<230 face = legitimate prior-wave boundary (not stale)"',
     '"note": "W231 editor family-6 gate carried forward: new block LHS w<232 x3 / RHS range(16,232)+range(17,232) / comment below-232 count-asserted ATOMICALLY before splice; W231 block\'s own w<231 face = legitimate prior-wave boundary (not stale)"')

# --- receipt ordinal faces ---
pair('''                    "probe_receipt_bmc_ordinal_face": 61,''',
     '''                    "probe_receipt_bmc_ordinal_face": 62,''')

# ---------------- phase 3: sentinel restores (with W232 additions) ----------------
rep("@@KEPT@@", KEPT_ORIG + "\nassert n1_t4.count('    # --- W231 materializer face') == 1  # prior block kept (W231 splice landed aee0bd9fa r966 window, estate machine-verified; committed+pushed by r966 itself, session died post-push pre-closeout, residual estate absorbed by r967)", 1)
rep("@@LIVE@@", LIVE_ORIG.replace('"w230_block_kept": 1},', '"w230_block_kept": 1, "w231_block_kept": 1},'), 1)
rep("@@LEG229@@", LEG229_ORIG, 1)
rep("@@LEG230@@", LEG230_ORIG, 1)
# ASM restore = machine-derived aging of the extracted face (descending-order leg
# aging: w230->w231 first, then w229->w230, then w228->w229; no cascades since each
# target is lower than every remaining source)
ASM_NEW = (ASM_ORIG.replace("w230_leg", "w231_leg")
                  .replace("w229_leg", "w230_leg")
                  .replace("w228_leg", "w229_leg"))
assert ASM_NEW == "block = EOL.join(hdr) + EOL + par_sec + EOL.join(w229_leg) + EOL + EOL.join(w230_leg) + EOL + EOL.join(w231_leg) + EOL + EOL.join(tail) + EOL", f"ASM_NEW drift: {ASM_NEW!r}"
rep("@@ASM@@", ASM_NEW, 1)

# ---------------- phase 4: validation (fail-closed) ----------------
# kept-line legit faces (KEPT-internal splice history carries W229/W230 verbatim)
assert t.count("24e12fa5e") == 1, f"kept-line 24e12fa5e count {t.count('24e12fa5e')} != 1"
assert t.count("dead r963 window") == 1, f"kept-line dead r963 window != 1"
assert t.count("r963-continuation") == 1, f"kept-line r963-continuation != 1"
assert t.count("2ae8553e6") == 1, f"kept-line 2ae8553e6 count {t.count('2ae8553e6')} != 1"
assert t.count("dead r961 window") == 1, f"kept-line dead r961 window != 1"
assert t.count("842f817ad") == 1, f"kept-line 842f817ad count {t.count('842f817ad')} != 1"
assert t.count("dead r959 window") == 1, f"kept-line dead r959 window != 1"
assert t.count("r959-continuation") == 1, f"kept-line r959-continuation != 1"
# upstream-seat provenance faces (P10 prose carries the W231 seat origin sha)
assert t.count("6638ddf9f") == 2, f"upstream seat-origin 6638ddf9f count {t.count('6638ddf9f')} != 2"

stale = ["(523_004, 525_003)", "(525_004, 525_203)",
 "aebe0a5ac", "FIFTEEN-level", "MSG-20261013-1000-bmc",
 "r965 freeze window", "r965 freeze-window bundle",
 "expect 220/60", "precedent 219/59 pre-splice", "splice 220/60", "== 220 and len", "rows 220 + candidate",
 "rows 60 + candidate", "bmc_ordinal=61", "61st", "sixty-first",
 "NINETY-FIRST instance", "NINETY-FIRST",
 "TWO HUNDRED AND THIRTY-FIRST", "929_789", "503_920", "(expect 929,789",
 "r963 11:5x", "r963 seat-time", "probe receipt @ r963 window",
 "twentieth consecutive", "fifth consecutive",
 "_w231bmc_20261013_probe_receipt.json", "_w231bmc_freeze_receipt.json",
 "w228_leg", "n1w231-", "N1_BANDS.get(230)", "if w < 231)", "if w < 230", "w<230 leaked",
 "range(16, 231)", "range(16,231)", "range(17, 231)", "below 231 composes", "below-231",
 "m228", "_c230", "n3r1_used231", "arith_a231", "arith_b231",
 "N1_BANDS\\[228\\]",
 "W232+ projection", "naive W232 A window", "W232 freezer", "W232+ freezer",
 "downstream W232 seat",
 "ce70c5808", "0ef11a120", "aec41c57c", "2ae8553e6x-guard",
 "e485a0b3f", "4e30ddf69", "c9e9e83b8x-guard",
 "@@KEPT@@", "@@LIVE@@", "@@LEG229@@", "@@LEG230@@", "@@ASM@@", "a3a7aa63230e87cb5a6212f54a07bc1738dde5b3" + "x-guard",
 '232: {"batch": "PERPETUAL-N1-W232"x-guard']
for s in stale:
    c = t.count(s)
    assert c == 0, f"STALE TOKEN {s!r} count {c} != 0"

must_one = ["_set_wave(232)",
 "f'{CFG_I}232: ", "f'{ROW_I}232: ", "ROW_I + '232: {\"a\"'", '"wave": 232',
 "MSG-20261013-1345-bmc.md", "8d3a1b78a", "931_989", "506_120",
 "(expect 931,989 / 506,120)", "(525_204, 527_203)", "(527_204, 527_403)",
 "int(_estate_ws[86]) == 228", "a3a7aa63230e87cb5a6212f54a07bc1738dde5b3", "SIXTEEN-level",
 '"probe_receipt_bmc_ordinal_face": 62,', '"w231_block_kept": 1}',
 "N1_BANDS.get(231)", "r966 probe leg0", "r966 seat-time live face",
 "r967 prereg derived", "87-row cut", '== 87 \\', '== 89, \\',
 "n1w232-0of12", "n1w232-11of12", "seat MSG-1232 tail",
 "ordinal machine-read NINETY-SECOND per probe receipt"]
for s in must_one:
    c = t.count(s)
    assert c == 1, f"MUST-ONE {s!r} count {c} != 1"

# --- calibration dump (dbg4): actual counts for the uncertain final faces ---
_cal = {s: t.count(s) for s in ["W230", "w230_", "n1_w231_results", "n1_w232_results",
 "aee0bd9fa", "0636c1d12", "r966 13:2x", "sixth consecutive", "90 rows", "w231_a_tail",
 "w231_b_tail", "w231_freeze_sha", "w231_prereg_sha", "w232_prereg_sha", "w232_receipt_sha",
 "W231", "w231_", "w229_leg", "w230_leg", "w231_leg", "r966", "twenty-first consecutive",
 "NINETY-SECOND instance", "NINETY-THIRD instance anticipated", "8d3a1b78a", "a3a7aa63230e87cb5a6212f54a07bc1738dde5b3",
 "n1_w232", "MSG-20261013-1345-bmc", "MSG-20261013-1155-bmc", "62nd", "sixty-second",
 "TWO HUNDRED AND THIRTY-SECOND", "W233+ projection", "naive W233 A window",
 "492972ee7", "4e373b743", "24e12fa5e", "6638ddf9f", "r968 freeze window",
 "WAVE_CONFIGS[232]", "WAVE_CONFIGS[231]", "w230_out_path", "w231_out_path", "w231_total",
 "w229_transitive", "w230_transitive", "w231_upstream",
 "assert pf.N1_BANDS[231] ==", "assert pf.N1_BANDS[230] ==", "assert pf.N1_BANDS[229] ==",
 "n1_w230_results.json", "n1_w231_results.json"]}
open(os.path.join(HERE, "_w232bmc_dbg4_counts.json"), "w", encoding="utf-8").write(json.dumps(_cal, indent=1))
print("DBG4 COUNTS:", json.dumps(_cal))

assert t.count("MSG-20261013-1345-bmc") == 4
assert t.count('232: {"batch": "PERPETUAL-N1-W232"') == 2   # new_cfg gate + n1_t4 post-edit gate
assert t.count("MSG-20261013-1155-bmc") == 2          # upstream seat references
assert t.count("W233+ projection") == 2
assert t.count("naive W233 A window") == 2
assert t.count("NINETY-THIRD instance anticipated") == 2
assert t.count("NINETY-SECOND instance") == 5
assert t.count("TWO HUNDRED AND THIRTY-SECOND") == 3
assert t.count("sixty-second") == 2
assert t.count("62nd") == 6
assert t.count("bmc_ordinal=62") == 3
assert t.count("_w232bmc_20261013_probe_receipt.json") == 9
assert t.count("_w232bmc_freeze_receipt.json") == 1
assert t.count("w229_leg") == 2
assert t.count("w230_leg") == 2
assert t.count("w231_leg") == 2
assert t.count('"w230_transitive"') == 1
assert t.count('"w231_upstream"') == 2
assert t.count("assert pf.N1_BANDS[231] ==") == 2     # w231_leg def + post-edit gate
assert t.count("assert pf.N1_BANDS[230] ==") == 1     # w230_leg def (sentinel-kept)
assert t.count("assert pf.N1_BANDS[229] ==") == 1     # w229_leg def (sentinel-kept)
assert t.count("WAVE_CONFIGS[232]") == 2             # band-facts self asserts
assert t.count("WAVE_CONFIGS[231]") == 3             # upstream mirror asserts
assert t.count("w230_out_path") == 2
assert t.count("n1_w232") == 5
assert t.count("n1_w231_results") == 4               # upstream refs (shift-landed)
assert t.count("n1_w232_results") == 2               # self path refs (shift-landed)
assert t.count("aee0bd9fa") >= 6
assert t.count("0636c1d12") == 2
assert t.count("r966 13:2x") == 3
assert t.count("r968 freeze window") == 4
assert t.count("r968 freeze-window bundle") == 2
assert t.count("twenty-first consecutive") == 2
assert t.count("90 rows") == 2
assert t.count("if w < 232)") == 5
assert t.count("range(16, 232)") == 2
assert t.count("range(17, 232)") == 3
assert t.count("registered wave below 232 composes") == 2
assert t.count("sixth consecutive") == 2
assert t.count("w231_a_tail") == 14
assert t.count("w231_b_tail") == 9
assert t.count("w231_freeze_sha") == 6
assert t.count("w231_prereg_sha") == 3
assert t.count("w232_prereg_sha") == 5
assert t.count("w232_receipt_sha") == 4
assert t.count("1345") >= 1 and t.count("1155-bmc.md") == 0

open(OUT, "w", encoding="utf-8", newline="").write(t)
py_compile.compile(OUT, doraise=True)
print(f"DERIVE OK: {OUT} ({len(t)} chars, template 49354); py_compile green")
print("NEXT: run the editor (gates fail-closed) -> pf/n1 selftest -> pathspec commit+push -> PRE-FINALIZE six-gate -> engine self-burn verify (2-cycle n1_w232 growth)")
