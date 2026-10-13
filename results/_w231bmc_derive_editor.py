# -*- coding: utf-8 -*-
# r965 bm-c derive: W230 -> W231 five-face freeze editor (count-asserted ordered
# transform; fail-closed pair law; protect-restore sentinels for fixed-estate faces).
# Template = committed _w230bmc_freeze_edits.py (49,077-char text, r963 dead-window
# generation, estate machine-verified then landed 24e12fa5e by r963 continuation,
# proven live-fire).
# All wave facts shift by token; every machine-derivable fact is re-asserted at
# editor RUNTIME against live template text (fail-closed). Sentinel blocks
# (KEPT/LIVE/LEG228/LEG229/ASM) are extracted from the template at RUNTIME by
# anchored index -- zero hand-transcription of fixed-estate faces.
# Census evidence = results/_r965bmc_census.py + _r965bmc_census2.py (this window,
# counts in hand: W230=72 / W229=114 / W228=11 / w230_=11(9 self post n1-shift) /
# w229_=97 / w228_=8 / n1_w230=5 / n1w230=2 / m227=3 / MSG-1000=4 / MSG-0855=2 /
# 6cfe285e3=1 / c9e9e83b8=2 / 91de0ae83=1 / 2ae8553e6=7 / f4b24e865=2 /
# e3665b334=3 / b5d62792d=3 / r962=15 / dead r961 window=5 / r963 freeze window=4).
# Disclosed deltas vs the mechanical clone (correctness pairs, machine-verifiable
# against the committed W231 probe receipt results/_w231bmc_20261013_probe_receipt.json):
#  (a) ordinal aging face fixed: template NINETIETH (W230 self) -> NINETY-FIRST
#      (W231 self, per probe receipt leg1 A_semantics machine-read) and projection
#      NINETY-FIRST anticipated -> NINETY-SECOND anticipated;
#  (b) upstream W230-cycle prose written honestly: dead r963 window splice estate
#      machine-verified then landed by r963 (absorb continuation) + engine
#      self-burn 12/12 (0ef11a120+aec41c57c) + in-window finalize one-pass
#      ce70c5808 (six-gate PRE-FINALIZE correct phase, FIFTH consecutive).
import os, sys, py_compile, json

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.join(HERE, "_w230bmc_freeze_edits.py")
OUT  = os.path.join(HERE, "_w231bmc_freeze_edits.py")

t = open(BASE, "r", encoding="utf-8", newline="").read()
assert len(t) == 49077, f"template length drift: {len(t)} != 49077"

def rep(old, new, n=1):
    global t
    c = t.count(old)
    assert c == n, f"PAIR FAIL count {c} != {n}: {old[:110]!r}"
    t = t.replace(old, new)

# ---------------- phase 0: sentinels (RUNTIME anchored extraction) ----------------
# KEPT block: W209 estate-source line .. W229 prior-block-kept line (20 assert lines)
k0 = t.index("assert n1_t4.count('    # --- W209 materializer face')")
k1 = t.index("assert n1_t4.count('    # --- W229 materializer face')")
k2 = t.index("\n", k1)
KEPT_ORIG = t[k0:k2]
assert KEPT_ORIG.count("\nassert ") == 20, f"KEPT block shape: {KEPT_ORIG.count(chr(10)+'assert ')}"
assert KEPT_ORIG.count("materializer face") == 21
rep(KEPT_ORIG, "@@KEPT@@", 1)

# LIVE line (liveness_anchors single-line JSON face)
l0 = t.index('"liveness_anchors"')
l0 = t.rindex("\n", 0, l0) + 1
l1 = t.index("\n", l0)
LIVE_ORIG = t[l0:l1]
assert LIVE_ORIG.count("_block_kept") == 21, f"LIVE shape: {LIVE_ORIG.count('_block_kept')}"  # w209..w229 + t141 not counted
rep(LIVE_ORIG, "@@LIVE@@", 1)

# LEG228 (template w228_leg def, 6 lines) -- protected from w228_->w229_ + W228->W229 aging
g0 = t.index("w228_leg = [")
g2 = t.index("\n]", g0) + 2
LEG228_ORIG = t[g0:g2]
assert LEG228_ORIG.count("N1_BANDS[228]") == 5 and LEG228_ORIG.count("W228 row parity drift") == 1
rep(LEG228_ORIG, "@@LEG228@@", 1)

# LEG229 (template w229_leg def, 6 lines) -- protected from w229_->w230_ + W229->W230 aging
h0 = t.index("w229_leg = [")
h2 = t.index("\n]", h0) + 2
LEG229_ORIG = t[h0:h2]
assert LEG229_ORIG.count("N1_BANDS[229]") == 5 and LEG229_ORIG.count("W229 row parity drift") == 1
rep(LEG229_ORIG, "@@LEG229@@", 1)

# ASM join line
ASM_ORIG = "block = EOL.join(hdr) + EOL + par_sec + EOL.join(w227_leg) + EOL + EOL.join(w228_leg) + EOL + EOL.join(w229_leg) + EOL + EOL.join(tail) + EOL"
rep(ASM_ORIG, "@@ASM@@", 1)

# ---------------- phase 1: ordered global shifts (descending, count-logged) ----------------
SHIFTS = [
 # --- self wave faces (W230 -> W231) ---
 ("n1_w230", "n1_w231", 5),            # self shard/out names (BEFORE w230_ var shift, substring law)
 ("w230_", "w231_", 9),               # self vars (census 11 - 2 n1_w230_results rides = 9)
 ("n1w230", "n1w231", 2),              # entry-identity tags
 ("W230", "W231", 72),                # self prose global (incl. PERPETUAL_N1_W230_PREREG x5 + batch x2)
 ("_w230bmc_20261013_probe_receipt.json", "_w231bmc_20261013_probe_receipt.json", 9),
 ("_w230bmc_freeze_receipt.json", "_w231bmc_freeze_receipt.json", 1),
 ("_w229bmc_freeze_edits.py", "_w230bmc_freeze_edits.py", 1),   # lineage template name (upstream->self)
 ("_set_wave(230)", "_set_wave(231)", 1),
 ('"wave": 230,', '"wave": 231,', 1),
 ("f'{CFG_I}230: ", "f'{CFG_I}231: ", 1),
 ("f'{ROW_I}230: ", "f'{ROW_I}231: ", 1),
 ("f'230: {{\"a\":", "f'231: {{\"a\":", 1),
 ("ROW_I + '230: {\"a\"'", "ROW_I + '231: {\"a\"'", 1),
 ("WAVE_CONFIGS[230]", "WAVE_CONFIGS[231]", 2),       # band-facts self asserts (BEFORE the [229]->[230] mirror shift)
 ("seat MSG-1230 tail", "seat MSG-1231 tail", 1),
 ("wave 230 = first free number", "wave 231 = first free number", 1),
 ("wave 230: ", "wave 231: ", 1),
 ("if w < 230)", "if w < 231)", 5),
 ("range(16, 230)", "range(16, 231)", 2),
 ("range(17, 230)", "range(17, 231)", 3),
 ("w<230 count", "w<231 count", 1),
 ("if w < 229", "if w < 230", 1),          # family-6 prior-wave 0-check (no paren tail -- distinct face)
 ("w<229 leaked", "w<230 leaked", 1),     # family-6 prior-wave leak prose
 ("below 230 composes", "below 231 composes", 2),
 ("below-230", "below-231", 2),
 ("arith_a230", "arith_a231", 3),
 ("arith_b230", "arith_b231", 3),
 ("n3r1_used230", "n3r1_used231", 3),
 # --- projection aging (W231 -> W232) ---
 ("W231+ projection", "W232+ projection", 2),
 ("naive W231 A window", "naive W232 A window", 2),
 ("W231 freezer", "W232 freezer", 1),
 ("W231+ freezer", "W232+ freezer", 1),
 ("downstream W231 seat NOT yet published", "downstream W232 seat NOT yet published", 1),
 ("downstream W231 seat publication pending", "downstream W232 seat publication pending", 1),
 ("NINETY-FIRST instance anticipated", "NINETY-SECOND instance anticipated", 2),
 # --- self ordinal/prose aging ---
 ("NINETIETH instance", "NINETY-FIRST instance", 5),
 ("TWO HUNDRED AND THIRTIETH", "TWO HUNDRED AND THIRTY-FIRST", 3),
 ("sixtieth", "sixty-first", 2),
 ("60th", "61st", 6),
 ("bmc_ordinal=60", "bmc_ordinal=61", 3),
 ("rows 59 + candidate", "rows 60 + candidate", 4),
 ("rows 219 + candidate", "rows 220 + candidate", 1),
 ("== 219 and len(bmc_rows_live) == 59", "== 220 and len(bmc_rows_live) == 60", 1),
 ("expect 219/59", "expect 220/60", 1),
 ("precedent 218/58 pre-splice", "precedent 219/59 pre-splice", 1),
 ("splice 219/59", "splice 220/60", 1),
 ("r963 freeze window", "r965 freeze window", 4),
 ("r963 freeze-window bundle", "r965 freeze-window bundle", 2),
 ("r963 prereg derived", "r964 prereg derived", 1),
 ("nineteenth consecutive", "twentieth consecutive", 2),
 ("fourth consecutive", "fifth consecutive", 2),
 ("FOURTEEN-level", "FIFTEEN-level", 1),
 # --- seat/provenance aging (self swap FIRST, then upstream) ---
 ("MSG-20261013-1000-bmc", "MSG-20261013-1155-bmc", 4),   # self seat swap FIRST
 ("MSG-20261013-0855-bmc", "MSG-20261013-1000-bmc", 2),   # upstream seat AFTER self swap
 ("6cfe285e3", "6638ddf9f", 1),                            # SEAT_ORIGIN BEFORE c9e9e83b8 aging
 ("c9e9e83b8", "6cfe285e3", 2),                            # upstream seat-origin provenance x2
 ("91de0ae83", "aebe0a5ac", 1),                            # self prereg sha
 # --- band/ledger fact aging (self W230 facts -> W231 facts) ---
 ("(520_804, 522_803)", "(523_004, 525_003)", 1),
 ("(522_804, 523_003)", "(525_004, 525_203)", 1),
 ("927_589", "929_789", 1),
 ("501_720", "503_920", 1),
 ("927,589", "929,789", 2),
 ("501,720", "503,920", 2),
 # --- upstream cycle shas aging ---
 ("2ae8553e6", "24e12fa5e", 6),            # KEPT-internal 1 excluded by sentinel
 ("f4b24e865", "ce70c5808", 2),
 # engine-append shas (0ef11a120/aec41c57c) carried ENTIRELY by the P10 prose + receipt
 # upstream pairs (census: e3665b334=3 / b5d62792d=3, ALL inside pair regions, zero standalone)
 ("dead r961 window", "dead r963 window", 4),   # KEPT-internal 1 excluded by sentinel
 ("r961 dead-window estate", "r963 dead-window estate", 1),
 ("r962 10:1x", "r963 11:5x", 3),
 ("probe receipt @ r962 window", "probe receipt @ r963 window", 2),
 ("r962 probe leg0", "r963 probe leg0", 1),
 ("r962 seat-time live face", "r963 seat-time live face", 1),
 # --- upstream wave faces (W229 -> W230) ---
 ("W229", "W230", 111),               # upstream prose global (census 114 - KEPT-internal 2 - LEG229-internal 1)
 ("w229_", "w230_", 94),              # upstream vars (census 97 - LEG229 var 1 - ASM join 1 - LIVE w229_block_kept 1)
 ("W228", "W229", 8),                # upstream-upstream prose (census 11 - KEPT-internal 2 - LEG228-internal 1)
 ("w228_", "w229_", 5),              # upstream-upstream vars (census 8 - LEG228 def 1 - ASM join 1 - LIVE 1)
 ("m227", "m228", 3),
 ("N1_BANDS\\[227\\]", "N1_BANDS\\[228\\]", 1),   # m-cut regex literal (raw-bracket form)
 ("_c229", "_c230", 5),
 ("'229: {\"batch\"'", "'230: {\"batch\"'", 2),   # upstream cfg needles
 ("'229: {\"a\"'", "'230: {\"a\"'", 2),           # upstream row needles
 ("'    229: {\"a\"'", "'    230: {\"a\"'", 1),
 ("N1_BANDS.get(229)", "N1_BANDS.get(230)", 1),
 ("WAVE_CONFIGS[229]", "WAVE_CONFIGS[230]", 3),       # upstream mirror asserts (AFTER self [230]->[231])
 ("pf.N1_BANDS[229]", "pf.N1_BANDS[230]", 4),   # mirror x3 + post-edit gate x1 (LEG229-internal assert face excluded)
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
pair("""# 2026-10-13 11:1x bm-c r963 freeze window (upstream W1..W229 ALL LANDED, clean precondition): W230 five-face freeze splice editor.""",
"""# 2026-10-13 12:4x bm-c r965 freeze window (upstream W1..W230 ALL LANDED, clean precondition): W231 five-face freeze splice editor.""")
# regression guards for the window-label pair (new side must carry the SHIFTED wave faces)
assert t.count("(upstream W1..W230 ALL LANDED, clean precondition): W231 five-face") == 1
assert t.count("W230 five-face freeze splice editor") == 0

pair("""# present (W229 finalize one-pass r962 10:1x landed in-window f4b24e865; splice
# estate 2ae8553e6 dead r961 window machine-verified then landed by
# r962 (absorb continuation), net chain head 927,589, merged pool K=501,720,
# n1_w229_results.json machine-read) -- ZERO in-flight upstream seats,""",
"""# present (W230 finalize one-pass r963 11:5x landed in-window ce70c5808; splice
# estate 24e12fa5e dead r963 window machine-verified then landed by
# r963 (absorb continuation), net chain head 929,789, merged pool K=503,920,
# n1_w230_results.json machine-read) -- ZERO in-flight upstream seats,""")

pair("""# Lineage: _w229bmc_freeze_edits.py pattern (proven live-fire freeze,
# r961 dead-window estate, machine-verified then landed 2ae8553e6 by
# r962) + r787 preflight law + r609""",
"""# Lineage: _w230bmc_freeze_edits.py pattern (proven live-fire freeze,
# r963 dead-window estate, machine-verified then landed 24e12fa5e by
# r963) + r787 preflight law + r609""")

pair("""# LHS/RHS/comment ATOMIC TRIPLE absorbed (the new block's w<230>/
# range(16,230)/below-230 triple is count-asserted atomically; the W229
# block's own w<229 face is legitimate prior-wave boundary, not stale).""",
"""# LHS/RHS/comment ATOMIC TRIPLE absorbed (the new block's w<231>/
# range(16,231)/below-231 triple is count-asserted atomically; the W230
# block's own w<230 face is legitimate prior-wave boundary, not stale).""")

pair("""# STRUCTURAL CHOICE (vs the W228 editor): the parity estate (W138..W206
# full-span, 69 rows, r858 absorb generation) is extracted from the OWN W229
# block physical bytes -- structure known exactly (this machine's own splice
# generation) -- the W229 block's own W227 leg (1 row) is excluded from the
# estate path and fresh W227 + W228 + W229 legs are appended for the W230
# block parity (88 rows: estate 69 + W211..W226 legs + W227 leg + W228 leg +
# W229 leg). Extraction self-asserts the 85-row cut (69 estate + W211..W225 +
# W226) regardless.""",
"""# STRUCTURAL CHOICE (vs the W229 editor): the parity estate (W138..W206
# full-span, 69 rows, r858 absorb generation) is extracted from the OWN W230
# block physical bytes -- structure known exactly (this machine's own splice
# generation) -- the W230 block's own W228 leg (1 row) is excluded from the
# estate path and fresh W228 + W229 + W230 legs are appended for the W231
# block parity (89 rows: estate 69 + W211..W227 legs + W228 leg + W229 leg +
# W230 leg). Extraction self-asserts the 86-row cut (69 estate + W211..W226 +
# W227) regardless.""")

pair("""# STRUCTURAL CHOICE: extract the estate from the OWN W229 block (bytes known
# exactly: full-span estate W138..W206 69 rows + own W211 leg + ... + own W226 leg) -- the W229 block is this machine's own splice generation
# (r961 freeze-window editor, estate machine-verified then landed 2ae8553e6 by r962), structure known. The W229 block span ends where the
# T-141 s2 lane face marker begins.""",
"""# STRUCTURAL CHOICE: extract the estate from the OWN W230 block (bytes known
# exactly: full-span estate W138..W206 69 rows + own W211 leg + ... + own W227 leg) -- the W230 block is this machine's own splice generation
# (r963 freeze-window editor, estate machine-verified then landed 24e12fa5e by r963), structure known. The W230 block span ends where the
# T-141 s2 lane face marker begins.""")

# --- transitive window slide (multi-wave faces the global shifts corrupt) ---
pair('f"W229+W228+W227+W226+W225 finalize products present "',
     'f"W230+W229+W228+W227+W226 finalize products present "')

pair("W228/W227/W226/W225 finalize are transitive deps",
     "W229/W228/W227/W226 finalize are transitive deps")

# --- seat/prose fixups (post-shift anchors) ---
pair(" " + "MSG-20261013-0855-bmc, executed bm-c r959 (seat c9e9e83b8); splice 2ae8553e6 dead r961 window estate machine-verified then landed by r962; engine self-burn 12/12 (e3665b334+b5d62792d); finalize one-pass r962 10:1x; six-gate PRE-FINALIZE correct phase standing law held, fourth consecutive), ",
     " " + "MSG-20261013-1000-bmc, executed bm-c r962 (seat 6cfe285e3); splice 24e12fa5e dead r963 window estate machine-verified then landed by r963; engine self-burn 12/12 (0ef11a120+aec41c57c); finalize one-pass r963 11:5x; six-gate PRE-FINALIZE correct phase standing law held, fifth consecutive), ")

pair(''' "    #     MSG-20261013-0855-bmc, executed bm-c r959 (seat c9e9e83b8); splice",
 "    #     2ae8553e6 dead r961 window estate machine-verified then landed by",
 "    #     r962; engine self-burn 12/12 (e3665b334+b5d62792d) + finalize one-pass r962 10:1x",
 "    #     splice estate + PRE-FINALIZE six-gate chain (standing law held, fourth",
 "    #     consecutive -- THIS W230 cycle runs PRE-FINALIZE likewise), honest note)",''',
''' "    #     MSG-20261013-1000-bmc, executed bm-c r962 (seat 6cfe285e3); splice",
 "    #     24e12fa5e dead r963 window estate machine-verified then landed by",
 "    #     r963; engine self-burn 12/12 (0ef11a120+aec41c57c) + finalize one-pass r963 11:5x",
 "    #     splice estate + PRE-FINALIZE six-gate chain (standing law held, fifth",
 "    #     consecutive -- THIS W231 cycle runs PRE-FINALIZE likewise), honest note)",''')

pair('''"    #     seat MSG + pre-seat probe script + probe receipt @ r962 window; per-wave prereg",
 "    #     r963 + freeze splice script landed in this r963 freeze-window bundle",''',
'''"    #     seat MSG + pre-seat probe script + probe receipt @ r963 window; per-wave prereg",
 "    #     r964 + freeze splice script landed in this r965 freeze-window bundle",''')

pair(''' "seat MSG + pre-seat probe script + probe receipt @ r962 window; per-wave prereg ",
 "r963 + freeze splice script landed in this r963 freeze-window bundle ",''',
''' "seat MSG + pre-seat probe script + probe receipt @ r963 window; per-wave prereg ",
 "r964 + freeze splice script landed in this r965 freeze-window bundle ",''')

# --- correctness delta (a): probe-receipt ordinal aging face fixed (disclosed header) ---
pair("ordinal machine-read NINETIETH per probe receipt",
     "ordinal machine-read NINETY-FIRST per probe receipt")

pair('"machine-checkable = A-hops-prior-B staircase NINETIETH ",',
     '"machine-checkable = A-hops-prior-B staircase NINETY-FIRST ",')

# --- estate/parity count pairs ---
pair('assert par_sec.count("assert pf.N1_BANDS[") == 85 \\',
     'assert par_sec.count("assert pf.N1_BANDS[") == 86 \\')
pair("    and int(_estate_ws[83]) == 225 \\\n    and int(_estate_ws[84]) == 226, \\",
     "    and int(_estate_ws[83]) == 225 \\\n    and int(_estate_ws[84]) == 226 \\\n    and int(_estate_ws[85]) == 227, \\")
pair('f"estate segment not W138..W206 full-span 69 rows + W211..W225 legs + W226 leg: n=',
     'f"estate segment not W138..W206 full-span 69 rows + W211..W226 legs + W227 leg: n=')
pair('assert par_full.count("assert pf.N1_BANDS[") == 87, \\',
     'assert par_full.count("assert pf.N1_BANDS[") == 88, \\')
pair("!= 87 (69 estate + W211..W224 legs + W225 leg + W226 leg + W227 leg + W228 leg)\"",
     "!= 88 (69 estate + W211..W225 legs + W226 leg + W227 leg + W228 leg + W229 leg)\"")

# --- m-cut assert message (leg index moves down one) ---
pair('assert m227, "upstream W227 row leg not found inside W229 parity span"',
     'assert m228, "upstream W228 row leg not found inside W230 parity span"')

# --- cfg/row key literals (self-keyed gate strings, colon-continuation form) ---
pair("assert new_cfg.count('230: {\"batch\": \"PERPETUAL-N1-W230\"') == 1",
     "assert new_cfg.count('231: {\"batch\": \"PERPETUAL-N1-W231\"') == 1")
pair("assert n1_t4.count('230: {\"batch\": \"PERPETUAL-N1-W230\"') == 1",
     "assert n1_t4.count('231: {\"batch\": \"PERPETUAL-N1-W231\"') == 1")

# --- post-edit gate value-source fix ([229] pf_mod stays via sentinel law; [230] value source) ---
pair("""assert n1_t4.count(f'assert pf.N1_BANDS[229] == {{"a": ({fmt(pf_mod.N1_BANDS[229]["a"][0])}, {fmt(pf_mod.N1_BANDS[229]["a"][1])}),') == 1""",
     """assert n1_t4.count(f'assert pf.N1_BANDS[230] == {{"a": ({fmt(pf_mod.N1_BANDS[230]["a"][0])}, {fmt(pf_mod.N1_BANDS[230]["a"][1])}),') == 1""")

# --- w227_leg def -> w230_leg def (drop oldest leg, add newest; content [230]) ---
pair("""w227_leg = [
 f'        assert pf.N1_BANDS[227] == {{"a": ({fmt(pf_mod.N1_BANDS[227]["a"][0])}, {fmt(pf_mod.N1_BANDS[227]["a"][1])}),',
 f'                                    "b_exit": ({fmt(pf_mod.N1_BANDS[227]["b_exit"][0])}, {fmt(pf_mod.N1_BANDS[227]["b_exit"][1])}),',
'                                    "engine_owner": "bm-c"}, \\\\',
'            "registered W227 row parity drift (r307; bm-c five-face freeze; own-seat face disclosed)"',
]""",
"""w230_leg = [
 f'        assert pf.N1_BANDS[230] == {{"a": ({fmt(pf_mod.N1_BANDS[230]["a"][0])}, {fmt(pf_mod.N1_BANDS[230]["a"][1])}),',
 f'                                    "b_exit": ({fmt(pf_mod.N1_BANDS[230]["b_exit"][0])}, {fmt(pf_mod.N1_BANDS[230]["b_exit"][1])}),',
'                                    "engine_owner": "bm-c"}, \\\\',
'            "registered W230 row parity drift (r307; bm-c five-face freeze; own-seat face disclosed)"',
]""")

# --- receipt upstream + transitive block ---
pair('''  "w229_upstream": {"freeze_sha": w229_freeze_sha, "prereg_sha": w229_prereg_sha,
                    "ledger_total": w229_total, "merged_n": w229_merged_n,
                    "engine_owner": "bm-c (own seat honored, no takeover face)",
                    "repair_chain_note": "r961 splice (W229 freeze landed 2ae8553e6 dead r961 window, estate machine-verified then landed by r962) + engine self-burn 12/12 (e3665b334+b5d62792d) + r962 finalize one-pass 10:1x f4b24e865 (six-gate PRE-FINALIZE correct phase -- standing law held, fourth consecutive)"},''',
'''  "w230_upstream": {"freeze_sha": w230_freeze_sha, "prereg_sha": w230_prereg_sha,
                    "ledger_total": w230_total, "merged_n": w230_merged_n,
                    "engine_owner": "bm-c (own seat honored, no takeover face)",
                    "repair_chain_note": "r963 splice (W230 freeze landed 24e12fa5e dead r963 window, estate machine-verified then landed by r963) + engine self-burn 12/12 (0ef11a120+aec41c57c) + r963 finalize one-pass 11:5x ce70c5808 (six-gate PRE-FINALIZE correct phase -- standing law held, fifth consecutive)"},''')

pair('''  "w228_transitive": {"finalize_product": "results/perpetual_faces/n1_w228_results.json present (belt-and-braces gate; ledger 925,389 / K=499,520)"},''',
     '''  "w229_transitive": {"finalize_product": "results/perpetual_faces/n1_w229_results.json present (belt-and-braces gate; ledger 927,589 / K=501,720)"},''')

# --- receipt prereg_bundle note ---
pair('"note": "prereg derived+committed in the r963 window (91de0ae83, FOURTEEN-level lineage replay chain, preflight 46/46); splice editor derived from the committed W229 editor template by count-asserted ordered transform (protect-restore regions, fail-closed pair law) in this same r963 freeze window; upstream W229 already landed (clean-precondition nineteenth consecutive window); zero transcription"',
     '"note": "prereg derived+committed in the r964 window (aebe0a5ac, FIFTEEN-level lineage replay chain, preflight 46/46); splice editor derived from the committed W230 editor template by count-asserted ordered transform (protect-restore regions, fail-closed pair law) in this same r965 freeze window; upstream W230 already landed (clean-precondition twentieth consecutive window); zero transcription"')

# --- receipt parity + family6 notes ---
pair("full-span estate W138..W206 (69 rows, r858 absorb generation) + W211..W226 legs + W227 leg + W228 leg + W229 leg -> W230 block = 88 rows ending at W229;",
     "full-span estate W138..W206 (69 rows, r858 absorb generation) + W211..W227 legs + W228 leg + W229 leg + W230 leg -> W231 block = 89 rows ending at W230;")

pair('"note": "W229 editor family-6 gate carried forward: new block LHS w<230 x3 / RHS range(16,230)+range(17,230) / comment below-230 count-asserted ATOMICALLY before splice; W229 block\'s own w<229 face = legitimate prior-wave boundary (not stale)"',
     '"note": "W230 editor family-6 gate carried forward: new block LHS w<231 x3 / RHS range(16,231)+range(17,231) / comment below-231 count-asserted ATOMICALLY before splice; W230 block\'s own w<230 face = legitimate prior-wave boundary (not stale)"')

# --- receipt ordinal faces ---
pair('''                    "probe_receipt_bmc_ordinal_face": 60,''',
     '''                    "probe_receipt_bmc_ordinal_face": 61,''')

# ---------------- phase 3: sentinel restores (with W231 additions) ----------------
rep("@@KEPT@@", KEPT_ORIG + "\nassert n1_t4.count('    # --- W230 materializer face') == 1  # prior block kept (W230 splice landed 24e12fa5e dead r963 window, estate machine-verified then landed by r963-continuation)", 1)
rep("@@LIVE@@", LIVE_ORIG.replace('"w229_block_kept": 1},', '"w229_block_kept": 1, "w230_block_kept": 1},'), 1)
rep("@@LEG228@@", LEG228_ORIG, 1)
rep("@@LEG229@@", LEG229_ORIG, 1)
rep("@@ASM@@", "block = EOL.join(hdr) + EOL + par_sec + EOL.join(w228_leg) + EOL + EOL.join(w229_leg) + EOL + EOL.join(w230_leg) + EOL + EOL.join(tail) + EOL", 1)

# ---------------- phase 4: validation (fail-closed) ----------------
# kept-line legit faces (W229 kept-assert comment carries the W229-cycle splice history verbatim)
assert t.count("2ae8553e6") == 1, f"kept-line 2ae8553e6 count {t.count('2ae8553e6')} != 1"
assert t.count("dead r961 window") == 1, f"kept-line dead r961 window != 1"
assert t.count("landed by r962)") == 1 or t.count("by r962)") == 1, "kept-line landed-by r962 face missing"
assert t.count("842f817ad") == 1, f"kept-line 842f817ad count {t.count('842f817ad')} != 1"
assert t.count("dead r959 window") == 1, f"kept-line dead r959 window != 1"
assert t.count("r959-continuation") == 1, f"kept-line r959-continuation != 1"
# upstream-seat provenance faces (P10 prose carries the W230 seat origin sha)
assert t.count("6cfe285e3") == 2, f"upstream seat-origin 6cfe285e3 count {t.count('6cfe285e3')} != 2"

stale = ["(520_804, 522_803)", "(522_804, 523_003)",
 "91de0ae83", "FOURTEEN-level", "MSG-20261013-0855-bmc",
 "r963 freeze window", "r963 freeze-window bundle",
 "expect 219/59", "precedent 218/58 pre-splice", "splice 219/59", "== 219 and len", "rows 219 + candidate",
 "rows 59 + candidate", "bmc_ordinal=60", "60th", "sixtieth",
 "NINETIETH instance", "NINETIETH",
 "TWO HUNDRED AND THIRTIETH", "927_589", "501_720", "(expect 927,589",
 "r962 10:1x", "r962 seat-time", "probe receipt @ r962 window",
 "nineteenth consecutive", "fourth consecutive",
 "_w230bmc_20261013_probe_receipt.json", "_w230bmc_freeze_receipt.json",
 "w227_leg", "n1w230-", "N1_BANDS.get(229)", "if w < 230)", "if w < 229", "w<229 leaked",
 "range(16, 230)", "range(16,230)", "range(17, 230)", "below 230 composes", "below-230",
 "m227", "_c229", "n3r1_used230", "arith_a230", "arith_b230",
 "N1_BANDS\\[227\\]",
 "W231+ projection", "naive W231 A window", "W231 freezer", "W231+ freezer",
 "downstream W231 seat",
 "f4b24e865", "e3665b334", "b5d62792d", "2ae8553e6x-guard",
 "e485a0b3f", "4e30ddf69", "c9e9e83b8x-guard",
 "@@KEPT@@", "@@LIVE@@", "@@LEG228@@", "@@LEG229@@", "@@ASM@@", "aebe0a5ac" + "x-guard",
 '231: {"batch": "PERPETUAL-N1-W231"x-guard']
for s in stale:
    c = t.count(s)
    assert c == 0, f"STALE TOKEN {s!r} count {c} != 0"

must_one = ["_set_wave(231)",
 "f'{CFG_I}231: ", "f'{ROW_I}231: ", "ROW_I + '231: {\"a\"'", '"wave": 231',
 "MSG-20261013-1155-bmc.md", "6638ddf9f", "929_789", "503_920",
 "(expect 929,789 / 503,920)", "(523_004, 525_003)", "(525_004, 525_203)",
 "int(_estate_ws[85]) == 227", "aebe0a5ac", "FIFTEEN-level",
 '"probe_receipt_bmc_ordinal_face": 61,', '"w230_block_kept": 1}',
 "N1_BANDS.get(230)", "r963 probe leg0", "r963 seat-time live face",
 "r964 prereg derived", "86-row cut", '== 86 \\', '== 88, \\',
 "n1w231-0of12", "n1w231-11of12", "seat MSG-1231 tail",
 "ordinal machine-read NINETY-FIRST per probe receipt"]
for s in must_one:
    c = t.count(s)
    assert c == 1, f"MUST-ONE {s!r} count {c} != 1"

# --- calibration dump (dbg3): actual counts for the uncertain final faces ---
_cal = {s: t.count(s) for s in ["W229", "w229_", "n1_w230_results", "n1_w231_results",
 "24e12fa5e", "ce70c5808", "r963 11:5x", "fifth consecutive", "89 rows", "w230_a_tail",
 "w230_b_tail", "w230_freeze_sha", "w230_prereg_sha", "w231_prereg_sha", "w231_receipt_sha",
 "W230", "w230_", "w228_leg", "w229_leg", "w230_leg", "r963", "twentieth consecutive",
 "NINETY-FIRST instance", "NINETY-SECOND instance anticipated", "6638ddf9f", "aebe0a5ac",
 "n1_w231", "MSG-20261013-1155-bmc", "MSG-20261013-1000-bmc", "61st", "sixty-first",
 "TWO HUNDRED AND THIRTY-FIRST", "W232+ projection", "naive W232 A window",
 "0ef11a120", "aec41c57c", "2ae8553e6", "6cfe285e3", "r965 freeze window",
 "WAVE_CONFIGS[231]", "WAVE_CONFIGS[230]", "w229_out_path", "w230_a_tail", "w230_total",
 "w226_transitive", "w225_transitive", "w229_transitive",
 "assert pf.N1_BANDS[230] ==", "assert pf.N1_BANDS[229] ==", "assert pf.N1_BANDS[228] ==",
 "n1_w229_results.json", "n1_w230_results.json"]}
open(os.path.join(HERE, "_w231bmc_dbg3_counts.json"), "w", encoding="utf-8").write(json.dumps(_cal, indent=1))
print("DBG3 COUNTS:", json.dumps(_cal))

assert t.count("MSG-20261013-1155-bmc") == 4
assert t.count('231: {"batch": "PERPETUAL-N1-W231"') == 2   # new_cfg gate + n1_t4 post-edit gate
assert t.count("MSG-20261013-1000-bmc") == 2          # upstream seat references
assert t.count("W232+ projection") == 2
assert t.count("naive W232 A window") == 2
assert t.count("NINETY-SECOND instance anticipated") == 2
assert t.count("NINETY-FIRST instance") == 5
assert t.count("TWO HUNDRED AND THIRTY-FIRST") == 3
assert t.count("sixty-first") == 2
assert t.count("61st") == 6
assert t.count("bmc_ordinal=61") == 3
assert t.count("_w231bmc_20261013_probe_receipt.json") == 9
assert t.count("_w231bmc_freeze_receipt.json") == 1
assert t.count("w228_leg") == 2
assert t.count("w229_leg") == 2
assert t.count("w230_leg") == 2
assert t.count('"w229_transitive"') == 1
assert t.count('"w230_upstream"') == 2
assert t.count("assert pf.N1_BANDS[230] ==") == 2     # w230_leg def + post-edit gate
assert t.count("assert pf.N1_BANDS[229] ==") == 1     # w229_leg def (sentinel-kept)
assert t.count("assert pf.N1_BANDS[228] ==") == 1     # w228_leg def (sentinel-kept)
assert t.count("WAVE_CONFIGS[231]") == 2             # band-facts self asserts
assert t.count("WAVE_CONFIGS[230]") == 3             # upstream mirror asserts
assert t.count("w229_out_path") == 2
assert t.count("n1_w231") == 5
assert t.count("n1_w230_results") == 4               # upstream refs (shift-landed)
assert t.count("n1_w231_results") == 2               # self path refs (shift-landed)
assert t.count("24e12fa5e") >= 6
assert t.count("ce70c5808") == 2
assert t.count("r963 11:5x") == 3
assert t.count("r965 freeze window") == 4
assert t.count("r965 freeze-window bundle") == 2
assert t.count("twentieth consecutive") == 2
assert t.count("89 rows") == 2
assert t.count("if w < 231)") == 5
assert t.count("range(16, 231)") == 2
assert t.count("range(17, 231)") == 3
assert t.count("registered wave below 231 composes") == 2
assert t.count("fifth consecutive") == 2
assert t.count("w230_a_tail") == 14
assert t.count("w230_b_tail") == 9
assert t.count("w230_freeze_sha") == 6
assert t.count("w230_prereg_sha") == 3
assert t.count("w231_prereg_sha") == 5
assert t.count("w231_receipt_sha") == 4
assert t.count("1155") >= 1 and t.count("0855-bmc.md") == 0

open(OUT, "w", encoding="utf-8", newline="").write(t)
py_compile.compile(OUT, doraise=True)
print(f"DERIVE OK: {OUT} ({len(t)} chars, template 49077); py_compile green")
print("NEXT: run the editor (gates fail-closed) -> pf/n1 selftest -> pathspec commit+push -> PRE-FINALIZE six-gate -> engine self-burn verify (2-cycle n1_w231 growth)")
