# -*- coding: utf-8 -*-
# r963 bm-c derive: W229 -> W230 five-face freeze editor (count-asserted ordered
# transform; fail-closed pair law; protect-restore sentinels for fixed-estate faces).
# Template = committed _w229bmc_freeze_edits.py (48,884-char text, r961 dead-window
# generation, estate machine-verified then landed 2ae8553e6 by r962,
# proven live-fire).
# All wave facts shift by token; every machine-derivable fact is re-asserted at
# editor RUNTIME against live git/pf/receipt data (fail-closed).
# Census evidence = _r963bmc_editor_census.py + _r963bmc_gap_probe.py (this window,
# counts in hand: census-gap supplement n1_w228=4 / 4e30ddf69=2 / 6744db794=2 /
# 842f817ad=7 with KEPT-internal 1 / r959-continuation=7 with KEPT 1 / dead r959
# window=5 with KEPT 1 / 03bca8089=1 / 95e210be1=1).
# Disclosed deltas vs the mechanical clone (correctness pairs, machine-verifiable
# against the committed W230 probe receipt _w230bmc_20261013_probe_receipt.json):
#  (a) the MEM/prose "ordinal machine-read EIGHTY-NINTH per probe receipt" aging
#      face (r927 fixB one-wave-behind family) fixed to NINETIETH = the W230 probe
#      receipt leg1 A_semantics machine-read ordinal ("staircase A-hops-prior-B
#      NINETIETH instance, E36 card");
#  (b) upstream W229-cycle prose rewritten honestly: the W229 cycle shape =
#      dead r961 splice estate machine-verified then landed by r962 (2ae8553e6)
#      + engine self-burn 12/12 (e3665b334+b5d62792d) + in-window finalize
#      one-pass f4b24e865 (six-gate PRE-FINALIZE correct phase, fourth
#      consecutive correct-phase wave).
import os, sys, py_compile

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.join(HERE, "_w229bmc_freeze_edits.py")
OUT  = os.path.join(HERE, "_w230bmc_freeze_edits.py")

t = open(BASE, "r", encoding="utf-8", newline="").read()
assert len(t) == 48884, f"template length drift: {len(t)} != 48884"

def rep(old, new, n=1):
    global t
    c = t.count(old)
    assert c == n, f"PAIR FAIL count {c} != {n}: {old[:110]!r}"
    t = t.replace(old, new)

# ---------------- phase 0: sentinels (fixed-estate faces protected) ----------------
KEPT_ORIG = """assert n1_t4.count('    # --- W209 materializer face') == 1  # estate source block kept
assert n1_t4.count('    # --- W210 materializer face') == 1  # prior block kept
assert n1_t4.count('    # --- W211 materializer face') == 1  # prior block kept
assert n1_t4.count('    # --- W212 materializer face') == 1  # prior block kept
assert n1_t4.count('    # --- W213 materializer face') == 1  # prior block kept
assert n1_t4.count('    # --- W214 materializer face') == 1  # prior block kept (W214 splice landed r910 window)
assert n1_t4.count('    # --- W215 materializer face') == 1  # prior block kept (W215 splice landed r912 window)
assert n1_t4.count('    # --- W216 materializer face') == 1  # prior block kept (W216 splice landed r914 window)
assert n1_t4.count('    # --- W217 materializer face') == 1  # prior block kept (W217 splice landed r916 window)
assert n1_t4.count('    # --- W218 materializer face') == 1  # prior block kept (W218 splice landed r918 window)
assert n1_t4.count('    # --- W219 materializer face') == 1  # prior block kept (W219 splice landed r920 window)
assert n1_t4.count('    # --- W220 materializer face') == 1  # prior block kept (W220 splice landed r923 window)
assert n1_t4.count('    # --- W221 materializer face') == 1  # prior block kept (W221 splice landed r927 window)
assert n1_t4.count('    # --- W222 materializer face') == 1  # prior block kept (W222 splice landed r931 window)
assert n1_t4.count('    # --- W223 materializer face') == 1  # prior block kept (W223 splice landed r934 window)
assert n1_t4.count('    # --- W224 materializer face') == 1  # prior block kept (W224 splice landed r937 dead window)
assert n1_t4.count('    # --- W225 materializer face') == 1  # prior block kept (W225 splice landed r939 freeze window)
assert n1_t4.count('    # --- W226 materializer face') == 1  # prior block kept (W226 splice landed r943 dead window, estate absorbed r945)
assert n1_t4.count('    # --- W227 materializer face') == 1  # prior block kept (W227 splice landed r956 dead window, estate absorbed by r956-absorb 1e5ed3326)
assert n1_t4.count('    # --- W228 materializer face') == 1  # prior block kept (W228 splice landed 842f817ad dead r959 window, estate machine-verified then landed by r959-continuation)"""
rep(KEPT_ORIG, "@@KEPT@@", 1)

LIVE_ORIG = '''  "liveness_anchors": {"t141_marker_kept": 1, "w209_block_kept": 1, "w210_block_kept": 1, "w211_block_kept": 1, "w212_block_kept": 1, "w213_block_kept": 1, "w214_block_kept": 1, "w215_block_kept": 1, "w216_block_kept": 1, "w217_block_kept": 1, "w218_block_kept": 1, "w219_block_kept": 1, "w220_block_kept": 1, "w221_block_kept": 1, "w222_block_kept": 1, "w223_block_kept": 1, "w224_block_kept": 1, "w225_block_kept": 1, "w226_block_kept": 1, "w227_block_kept": 1, "w228_block_kept": 1},'''
rep(LIVE_ORIG, "@@LIVE@@", 1)

LEG228_ORIG = '''w228_leg = [
 f\'        assert pf.N1_BANDS[228] == {{"a": ({fmt(pf_mod.N1_BANDS[228]["a"][0])}, {fmt(pf_mod.N1_BANDS[228]["a"][1])}),\',
 f\'                                    "b_exit": ({fmt(pf_mod.N1_BANDS[228]["b_exit"][0])}, {fmt(pf_mod.N1_BANDS[228]["b_exit"][1])}),\',
\'                                    "engine_owner": "bm-c"}, \\\\',
\'            "registered W228 row parity drift (r307; bm-c five-face freeze; own-seat face disclosed)"\',
]'''
rep(LEG228_ORIG, "@@LEG228@@", 1)

ASM_ORIG = "block = EOL.join(hdr) + EOL + par_sec + EOL.join(w226_leg) + EOL + EOL.join(w227_leg) + EOL + EOL.join(w228_leg) + EOL + EOL.join(tail) + EOL"
rep(ASM_ORIG, "@@ASM@@", 1)

# ---------------- phase 1: ordered global shifts (descending, count-logged) ----------------
SHIFTS = [
 ("n1_w229", "n1_w230", 5),            # self shard/out names (BEFORE w229_ var shift, substring law)
 ("w229_", "w230_", 9),               # self vars (post n1_w229: census 11 - 2 n1_w229_results rides = 9)
 ("n1w229", "n1w230", 2),              # entry-identity tags
 ("W229", "W230", 72),                # self prose global (PERPETUAL rides along)
 ("W228", "W229", 111),               # upstream prose global (census 114 - KEPT-internal 2 - LEG228-internal 1)
 ("w228_", "w229_", 94),              # upstream vars (census 97 - LEG228 var 1 - ASM join 1 - LIVE w228_block_kept 1)
 ("m226", "m227", 3),
 ("N1_BANDS\\[226\\]", "N1_BANDS\\[227\\]", 1),   # m-cut regex literal (raw-bracket form)
 ("_c228", "_c229", 5),
 ("arith_a229", "arith_a230", 3),
 ("arith_b229", "arith_b230", 3),
 ("n3r1_used229", "n3r1_used230", 3),
 ("_set_wave(229)", "_set_wave(230)", 1),
 ("'228: {\"batch\"'", "'229: {\"batch\"'", 2),   # upstream cfg needles (CFG_I + _c find)
 ("'228: {\"a\"'", "'229: {\"a\"'", 2),           # upstream row needles (pickaxe -S + ROW_I)
 ("'    228: {\"a\"'", "'    229: {\"a\"'", 1),
 ("f'{CFG_I}229: ", "f'{CFG_I}230: ", 1),
 ("f'{ROW_I}229: ", "f'{ROW_I}230: ", 1),
 ("f'229: {{\"a\":", "f'230: {{\"a\":", 1),
 ("ROW_I + '229: {\"a\"'", "ROW_I + '230: {\"a\"'", 1),
 ("N1_BANDS.get(228)", "N1_BANDS.get(229)", 1),
 ("WAVE_CONFIGS[229]", "WAVE_CONFIGS[230]", 2),       # band-facts self asserts (BEFORE the [228]->[229] mirror shift)
 ("WAVE_CONFIGS[228]", "WAVE_CONFIGS[229]", 3),
 ("pf.N1_BANDS[228]", "pf.N1_BANDS[229]", 4),   # mirror x3 + post-edit gate x1 (LEG228-internal assert face excluded)
 ("wave 229 = first free number", "wave 230 = first free number", 1),
 ("wave 229: ", "wave 230: ", 1),
 ("if w < 229)", "if w < 230)", 5),
 ("if w < 228", "if w < 229", 1),
 ("w<228 leaked", "w<229 leaked", 1),
 ("w<229 count", "w<230 count", 1),
 ("range(16, 229)", "range(16, 230)", 2),
 ("range(17, 229)", "range(17, 230)", 3),
 ("registered wave below 229 composes", "registered wave below 230 composes", 2),
 ("seat MSG-1229 tail", "seat MSG-1230 tail", 1),
 ('"wave": 229,', '"wave": 230,', 1),
 ("NINETIETH instance anticipated", "NINETY-FIRST instance anticipated", 2),   # FIRST (before EIGHTH->NINETH)
 ("EIGHTY-NINDTH instance", "NINETIETH instance", 0),   # no-op guard slot (real form below)
 ("EIGHTY-NINTH instance", "NINETIETH instance", 5),
 ("TWO HUNDRED AND TWENTY-NINTH", "TWO HUNDRED AND THIRTIETH", 3),
 ("fifty-ninth", "sixtieth", 2),
 ("59th", "60th", 6),
 ("bmc_ordinal=59", "bmc_ordinal=60", 3),
 ("rows 58 + candidate", "rows 59 + candidate", 4),
 ("rows 218 + candidate", "rows 219 + candidate", 1),
 ("== 218 and len(bmc_rows_live) == 58", "== 219 and len(bmc_rows_live) == 59", 1),
 ("expect 218/58", "expect 219/59", 1),
 ("precedent 217/57 pre-splice", "precedent 218/58 pre-splice", 1),
 ("splice 218/58", "splice 219/59", 1),
 ("r959 probe leg0", "r962 probe leg0", 1),
 ("r959 seat-time live face", "r962 seat-time live face", 1),
 ("probe receipt @ r959 window", "probe receipt @ r962 window", 2),
 ("r961 freeze window", "r963 freeze window", 4),
 ("r961 freeze-window bundle", "r963 freeze-window bundle", 2),
 ("r960 prereg derived", "r963 prereg derived", 1),
 ("eighteenth consecutive", "nineteenth consecutive", 2),
 ("e485a0b3f", "91de0ae83", 1),
 ("THIRTEEN-level", "FOURTEEN-level", 1),
 ("MSG-20261013-0855-bmc", "MSG-20261013-1000-bmc", 4),   # self seat swap FIRST
 ("MSG-20261013-0720-bmc", "MSG-20261013-0855-bmc", 2),   # upstream seat AFTER self swap
 ("c9e9e83b8", "6cfe285e3", 1),                            # SEAT_ORIGIN BEFORE 4e30ddf69 aging
 ("4e30ddf69", "c9e9e83b8", 2),                            # upstream seat-origin provenance x2
 ("_w229bmc_20261013_probe_receipt.json", "_w230bmc_20261013_probe_receipt.json", 9),
 ("_w229bmc_freeze_receipt.json", "_w230bmc_freeze_receipt.json", 1),
 ("(518_604, 520_603)", "(520_804, 522_803)", 1),
 ("(520_604, 520_803)", "(522_804, 523_003)", 1),
 ("925_389", "927_589", 1),
 ("499_520", "501_720", 1),
 ("(expect 925,389 / 499,520)", "(expect 927,589 / 501,720)", 1),
 ("842f817ad", "2ae8553e6", 6),            # KEPT-internal 1 excluded by sentinel; 6 non-KEPT refs age
 ("r959-continuation", "r962", 6),          # KEPT-internal 1 excluded by sentinel
 ("dead r959 window", "dead r961 window", 4),   # KEPT-internal 1 excluded by sentinel
 ("6744db794", "f4b24e865", 2),            # W228 finalize sha -> W229 finalize sha
 ("03bca8089", "e3665b334", 1),            # W228 engine self-burn appends -> W229 appends
 ("95e210be1", "b5d62792d", 1),
 ("W230+ projection", "W231+ projection", 2),
 ("naive W230 A window", "naive W231 A window", 2),
 ("W230 freezer", "W231 freezer", 1),
 ("W230+ freezer", "W231+ freezer", 1),
 ("downstream W230 seat NOT yet published", "downstream W231 seat NOT yet published", 1),
 ("downstream W230 seat publication pending", "downstream W231 seat publication pending", 1),
 ("W227/W226/W225/W224 finalize are transitive deps", "W228/W227/W226/W225 finalize are transitive deps", 1),
]
def shift_text(s):
    for old, new, _ in SHIFTS:
        s = s.replace(old, new)
    return s
for old, new, mn in SHIFTS:
    if mn == 0:
        continue   # no-op guard slot
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
pair("""# 2026-10-13 09:2x bm-c r961 freeze window (upstream W1..W228 ALL LANDED, clean precondition): W229 five-face freeze splice editor.""",
"""# 2026-10-13 11:1x bm-c r963 freeze window (upstream W1..W229 ALL LANDED, clean precondition): W230 five-face freeze splice editor.""")
# regression guards for the window-label pair (new side must carry the SHIFTED wave faces)
assert t.count("(upstream W1..W229 ALL LANDED, clean precondition): W230 five-face") == 1
assert t.count("W229 five-face freeze splice editor") == 0

pair("""# present (W228 finalize one-pass r959 08:3x landed in-window 6744db794; splice
# estate 842f817ad dead r959 window machine-verified then landed by
# r959-continuation, net chain head 925,389, merged pool K=499,520,
# n1_w228_results.json machine-read) -- ZERO in-flight upstream seats,""",
"""# present (W229 finalize one-pass r962 10:1x landed in-window f4b24e865; splice
# estate 2ae8553e6 dead r961 window machine-verified then landed by
# r962 (absorb continuation), net chain head 927,589, merged pool K=501,720,
# n1_w229_results.json machine-read) -- ZERO in-flight upstream seats,""")

pair("""# Lineage: _w228bmc_freeze_edits.py pattern (proven live-fire freeze,
# r959 dead-window estate, machine-verified then landed 842f817ad by
# r959-continuation) + r787 preflight law + r609""",
"""# Lineage: _w229bmc_freeze_edits.py pattern (proven live-fire freeze,
# r961 dead-window estate, machine-verified then landed 2ae8553e6 by
# r962) + r787 preflight law + r609""")

pair("""# LHS/RHS/comment ATOMIC TRIPLE absorbed (the new block's w<229>/
# range(16,229)/below-229 triple is count-asserted atomically; the W228
# block's own w<228 face is legitimate prior-wave boundary, not stale).""",
"""# LHS/RHS/comment ATOMIC TRIPLE absorbed (the new block's w<230>/
# range(16,230)/below-230 triple is count-asserted atomically; the W229
# block's own w<229 face is legitimate prior-wave boundary, not stale).""")

pair("""# STRUCTURAL CHOICE (vs the W227 editor): the parity estate (W138..W206
# full-span, 69 rows, r858 absorb generation) is extracted from the OWN W228
# block physical bytes -- structure known exactly (this machine's own splice
# generation) -- the W228 block's own W226 leg (1 row) is excluded from the
# estate path and fresh W226 + W227 + W228 legs are appended for the W229
# block parity (87 rows: estate 69 + W211..W225 legs + W226 leg + W227 leg +
# W228 leg). Extraction self-asserts the 84-row cut (69 estate + W211..W224 +
# W225) regardless.""",
"""# STRUCTURAL CHOICE (vs the W228 editor): the parity estate (W138..W206
# full-span, 69 rows, r858 absorb generation) is extracted from the OWN W229
# block physical bytes -- structure known exactly (this machine's own splice
# generation) -- the W229 block's own W227 leg (1 row) is excluded from the
# estate path and fresh W227 + W228 + W229 legs are appended for the W230
# block parity (88 rows: estate 69 + W211..W226 legs + W227 leg + W228 leg +
# W229 leg). Extraction self-asserts the 85-row cut (69 estate + W211..W225 +
# W226) regardless.""")

pair("""# STRUCTURAL CHOICE: extract the estate from the OWN W228 block (bytes known
# exactly: full-span estate W138..W206 69 rows + own W211 leg + ... + own W225 leg) -- the W228 block is this machine's own splice generation
# (r959 freeze-window editor, estate machine-verified then landed 842f817ad by r959-continuation), structure known. The W228 block span ends where the
# T-141 s2 lane face marker begins.""",
"""# STRUCTURAL CHOICE: extract the estate from the OWN W229 block (bytes known
# exactly: full-span estate W138..W206 69 rows + own W211 leg + ... + own W226 leg) -- the W229 block is this machine's own splice generation
# (r961 freeze-window editor, estate machine-verified then landed 2ae8553e6 by r962), structure known. The W229 block span ends where the
# T-141 s2 lane face marker begins.""")

# --- gate 0.5 transitive window slide (W227 out -> W228 transitive) ---
pair("""w227_out_path = os.path.join(REPO, "results", "perpetual_faces", "n1_w227_results.json")
assert os.path.exists(w227_out_path), "W227 finalize product missing (transitive chain dep) -- abort\"""",
"""w228_out_path = os.path.join(REPO, "results", "perpetual_faces", "n1_w228_results.json")
assert os.path.exists(w228_out_path), "W228 finalize product missing (transitive chain dep) -- abort\"""")

pair('f"W228+W227+W226+W225+W224 finalize products present "',
     'f"W229+W228+W227+W226+W225 finalize products present "')

# --- seat/prose fixups (post-shift anchors) ---
pair(" " + "MSG-20261013-0720-bmc, executed bm-c r957 (seat 4e30ddf69); splice 842f817ad dead r959 window estate machine-verified then landed by r959-continuation; engine self-burn 12/12; finalize one-pass r959 08:3x; six-gate PRE-FINALIZE correct phase standing law held, third consecutive), ",
     " " + "MSG-20261013-0855-bmc, executed bm-c r959 (seat c9e9e83b8); splice 2ae8553e6 dead r961 window estate machine-verified then landed by r962; engine self-burn 12/12 (e3665b334+b5d62792d); finalize one-pass r962 10:1x; six-gate PRE-FINALIZE correct phase standing law held, fourth consecutive), ")

pair(''' "    #     MSG-20261013-0720-bmc, executed bm-c r957 (seat 4e30ddf69); splice",
 "    #     842f817ad dead r959 window estate machine-verified then landed by",
 "    #     r959-continuation; engine self-burn 12/12 + finalize one-pass r959 08:3x",
 "    #     splice estate + PRE-FINALIZE six-gate chain (standing law held, third",
 "    #     consecutive -- THIS W229 cycle runs PRE-FINALIZE likewise), honest note)",''',
''' "    #     MSG-20261013-0855-bmc, executed bm-c r959 (seat c9e9e83b8); splice",
 "    #     2ae8553e6 dead r961 window estate machine-verified then landed by",
 "    #     r962; engine self-burn 12/12 (e3665b334+b5d62792d) + finalize one-pass r962 10:1x",
 "    #     splice estate + PRE-FINALIZE six-gate chain (standing law held, fourth",
 "    #     consecutive -- THIS W230 cycle runs PRE-FINALIZE likewise), honest note)",''')

pair('''"    #     seat MSG + pre-seat probe script + probe receipt @ r959 window; per-wave prereg",
 "    #     r960 + freeze splice script landed in this r961 freeze-window bundle",''',
'''"    #     seat MSG + pre-seat probe script + probe receipt @ r962 window; per-wave prereg",
 "    #     r963 + freeze splice script landed in this r963 freeze-window bundle",''')

pair(''' "seat MSG + pre-seat probe script + probe receipt @ r959 window; per-wave prereg ",
 "r960 + freeze splice script landed in this r961 freeze-window bundle ",''',
''' "seat MSG + pre-seat probe script + probe receipt @ r962 window; per-wave prereg ",
 "r963 + freeze splice script landed in this r963 freeze-window bundle ",''')

# --- correctness delta (a): probe-receipt ordinal aging face fixed (disclosed header) ---
pair("ordinal machine-read EIGHTY-NINTH per probe receipt",
     "ordinal machine-read NINETIETH per probe receipt")

pair('"machine-checkable = A-hops-prior-B staircase EIGHTY-NINTH ",',
     '"machine-checkable = A-hops-prior-B staircase NINETIETH ",')

# --- estate/parity count pairs ---
pair('assert par_sec.count("assert pf.N1_BANDS[") == 84 \\',
     'assert par_sec.count("assert pf.N1_BANDS[") == 85 \\')
pair("    and int(_estate_ws[83]) == 225, \\",
     "    and int(_estate_ws[83]) == 225 \\\n    and int(_estate_ws[84]) == 226, \\")
pair('f"estate segment not W138..W206 full-span 69 rows + W211..W224 legs + W225 leg: n=',
     'f"estate segment not W138..W206 full-span 69 rows + W211..W225 legs + W226 leg: n=')
pair('assert par_full.count("assert pf.N1_BANDS[") == 86, \\',
     'assert par_full.count("assert pf.N1_BANDS[") == 87, \\')
pair("!= 86 (69 estate + W211..W223 legs + W224 leg + W225 leg + W226 leg + W227 leg)\"",
     "!= 87 (69 estate + W211..W224 legs + W225 leg + W226 leg + W227 leg + W228 leg)\"")

# --- m-cut assert message (leg index moves down one) ---
pair('assert m226, "upstream W226 row leg not found inside W228 parity span"',
     'assert m227, "upstream W227 row leg not found inside W229 parity span"')

# --- cfg/row key literals (self-keyed gate strings, colon-continuation form) ---
pair("assert new_cfg.count('229: {\"batch\": \"PERPETUAL-N1-W229\"') == 1",
     "assert new_cfg.count('230: {\"batch\": \"PERPETUAL-N1-W230\"') == 1")
pair("assert n1_t4.count('229: {\"batch\": \"PERPETUAL-N1-W229\"') == 1",
     "assert n1_t4.count('230: {\"batch\": \"PERPETUAL-N1-W230\"') == 1")

# --- post-edit gate value-source fix ([228] pf_mod stays via sentinel law; [229] value source) ---
pair("""assert n1_t4.count(f'assert pf.N1_BANDS[228] == {{"a": ({fmt(pf_mod.N1_BANDS[228]["a"][0])}, {fmt(pf_mod.N1_BANDS[228]["a"][1])}),') == 1""",
     """assert n1_t4.count(f'assert pf.N1_BANDS[229] == {{"a": ({fmt(pf_mod.N1_BANDS[229]["a"][0])}, {fmt(pf_mod.N1_BANDS[229]["a"][1])}),') == 1""")

# --- w226_leg def -> w229_leg def (drop oldest leg, add newest; content [229]) ---
pair("""w226_leg = [
 f'        assert pf.N1_BANDS[226] == {{"a": ({fmt(pf_mod.N1_BANDS[226]["a"][0])}, {fmt(pf_mod.N1_BANDS[226]["a"][1])}),',
 f'                                    "b_exit": ({fmt(pf_mod.N1_BANDS[226]["b_exit"][0])}, {fmt(pf_mod.N1_BANDS[226]["b_exit"][1])}),',
'                                    "engine_owner": "bm-c"}, \\\\',
'            "registered W226 row parity drift (r307; bm-c five-face freeze; own-seat face disclosed)"',
]""",
"""w229_leg = [
 f'        assert pf.N1_BANDS[229] == {{"a": ({fmt(pf_mod.N1_BANDS[229]["a"][0])}, {fmt(pf_mod.N1_BANDS[229]["a"][1])}),',
 f'                                    "b_exit": ({fmt(pf_mod.N1_BANDS[229]["b_exit"][0])}, {fmt(pf_mod.N1_BANDS[229]["b_exit"][1])}),',
'                                    "engine_owner": "bm-c"}, \\\\',
'            "registered W229 row parity drift (r307; bm-c five-face freeze; own-seat face disclosed)"',
]""")

# --- receipt upstream + transitive block ---
pair('''  "w228_upstream": {"freeze_sha": w228_freeze_sha, "prereg_sha": w228_prereg_sha,
                    "ledger_total": w228_total, "merged_n": w228_merged_n,
                    "engine_owner": "bm-c (own seat honored, no takeover face)",
                    "repair_chain_note": "r959 splice (W228 freeze landed 842f817ad dead r959 window, estate machine-verified then landed by r959-continuation) + engine self-burn 12/12 (03bca8089+95e210be1) + r959 finalize one-pass 08:3x 6744db794 (six-gate PRE-FINALIZE correct phase -- standing law held, third consecutive)"},''',
'''  "w229_upstream": {"freeze_sha": w229_freeze_sha, "prereg_sha": w229_prereg_sha,
                    "ledger_total": w229_total, "merged_n": w229_merged_n,
                    "engine_owner": "bm-c (own seat honored, no takeover face)",
                    "repair_chain_note": "r961 splice (W229 freeze landed 2ae8553e6 dead r961 window, estate machine-verified then landed by r962) + engine self-burn 12/12 (e3665b334+b5d62792d) + r962 finalize one-pass 10:1x f4b24e865 (six-gate PRE-FINALIZE correct phase -- standing law held, fourth consecutive)"},''')

pair('''  "w227_transitive": {"finalize_product": "results/perpetual_faces/n1_w227_results.json present (belt-and-braces gate; ledger 923,189 / K=497,320)"},''',
'''  "w228_transitive": {"finalize_product": "results/perpetual_faces/n1_w228_results.json present (belt-and-braces gate; ledger 925,389 / K=499,520)"},''')

# --- receipt prereg_bundle note ---
pair('"note": "prereg derived+committed in the r960 window (e485a0b3f, THIRTEEN-level lineage replay chain, preflight 46/46); splice editor derived from the committed W228 editor template by count-asserted ordered transform (protect-restore regions, fail-closed pair law) in this same r961 freeze window; upstream W228 already landed (clean-precondition eighteenth consecutive window); zero transcription"',
     '"note": "prereg derived+committed in the r963 window (91de0ae83, FOURTEEN-level lineage replay chain, preflight 46/46); splice editor derived from the committed W229 editor template by count-asserted ordered transform (protect-restore regions, fail-closed pair law) in this same r963 freeze window; upstream W229 already landed (clean-precondition nineteenth consecutive window); zero transcription"')

# --- receipt parity + family6 notes ---
pair("full-span estate W138..W206 (69 rows, r858 absorb generation) + W211..W225 legs + W226 leg + W227 leg + W228 leg -> W229 block = 87 rows ending at W228;",
     "full-span estate W138..W206 (69 rows, r858 absorb generation) + W211..W226 legs + W227 leg + W228 leg + W229 leg -> W230 block = 88 rows ending at W229;")

pair('"note": "W228 editor family-6 gate carried forward: new block LHS w<229 x3 / RHS range(16,229)+range(17,229) / comment below-229 count-asserted ATOMICALLY before splice; W228 block\'s own w<228 face = legitimate prior-wave boundary (not stale)"',
     '"note": "W229 editor family-6 gate carried forward: new block LHS w<230 x3 / RHS range(16,230)+range(17,230) / comment below-230 count-asserted ATOMICALLY before splice; W229 block\'s own w<229 face = legitimate prior-wave boundary (not stale)"')

# --- receipt ordinal faces ---
pair('''                    "probe_receipt_bmc_ordinal_face": 59,''',
     '''                    "probe_receipt_bmc_ordinal_face": 60,''')

# ---------------- phase 3: sentinel restores (with W230 additions) ----------------
rep("@@KEPT@@", KEPT_ORIG + "\nassert n1_t4.count('    # --- W229 materializer face') == 1  # prior block kept (W229 splice landed 2ae8553e6 dead r961 window, estate machine-verified then landed by r962)", 1)
rep("@@LIVE@@", LIVE_ORIG.replace('"w228_block_kept": 1},', '"w228_block_kept": 1, "w229_block_kept": 1},'), 1)
rep("@@LEG228@@", LEG228_ORIG, 1)
rep("@@ASM@@", "block = EOL.join(hdr) + EOL + par_sec + EOL.join(w227_leg) + EOL + EOL.join(w228_leg) + EOL + EOL.join(w229_leg) + EOL + EOL.join(tail) + EOL", 1)

# ---------------- phase 4: validation (fail-closed) ----------------
# kept-line legit faces (W228 kept-assert comment carries the W228-cycle splice history verbatim)
assert t.count("842f817ad") == 1, f"kept-line 842f817ad count {t.count('842f817ad')} != 1"
assert t.count("dead r959 window") == 1, f"kept-line dead r959 window != 1"
assert t.count("r959-continuation") == 1, f"kept-line r959-continuation != 1"
assert t.count("1e5ed3326") == 1, f"kept-line 1e5ed3326 != 1"
assert t.count("r956 dead window") == 1, f"kept-line r956 dead window != 1"
# upstream-seat provenance faces (P10 prose carries the W229 seat origin sha)
assert t.count("c9e9e83b8") == 2, f"upstream seat-origin c9e9e83b8 count {t.count('c9e9e83b8')} != 2"

stale = ["(518_604, 520_603)", "(520_604, 520_803)",
 "e485a0b3f", "THIRTEEN-level", "MSG-20261013-0720-bmc",
 "r961 freeze window", "r961 freeze-window bundle",
 "expect 218/58", "precedent 217/57 pre-splice", "splice 218/58", "== 218 and len", "rows 218 + candidate",
 "rows 58 + candidate", "bmc_ordinal=59", "58th", "fifty-ninth",
 "EIGHTY-NINTH instance", "EIGHTY-NINTH",
 "TWO HUNDRED AND TWENTY-NINTH", "925_389", "499_520", "(expect 925,389",
 "r959 probe leg0", "r959 seat-time", "probe receipt @ r959 window",
 "eighteenth consecutive", "seventeenth consecutive",
 "_w229bmc_20261013_probe_receipt.json", "_w229bmc_freeze_receipt.json",
 "w225_leg", "n1w229-", "N1_BANDS.get(228)", "if w < 228)", "w<228 leaked", "w<229 count",
 "range(16, 229)", "range(16,229)", "range(17, 229)", "below 229 composes", "below-229",
 "m226", "_c228", "n3r1_used229", "arith_a229", "arith_b229",
 "N1_BANDS\\[226\\]",
 "W230+ projection", "naive W230 A window", "W230 freezer", "W230+ freezer",
 "downstream W230 seat",
 "6744db794", "03bca8089", "95e210be1", "4e30ddf69",
 "@@KEPT@@", "@@LIVE@@", "@@LEG228@@", "@@ASM@@", "91de0ae83" + "x-guard",
 '230: {"batch": "PERPETUAL-N1-W230"x-guard']
for s in stale:
    c = t.count(s)
    assert c == 0, f"STALE TOKEN {s!r} count {c} != 0"

must_one = ["_set_wave(230)",
 "f'{CFG_I}230: ", "f'{ROW_I}230: ", "ROW_I + '230: {\"a\"'", '"wave": 230',
 "MSG-20261013-1000-bmc.md", "6cfe285e3", "927_589", "501_720",
 "(expect 927,589 / 501,720)", "(520_804, 522_803)", "(522_804, 523_003)",
 "int(_estate_ws[84]) == 226", "91de0ae83", "FOURTEEN-level",
 '"probe_receipt_bmc_ordinal_face": 60,', '"w229_block_kept": 1}',
 "N1_BANDS.get(229)", "r962 probe leg0", "r962 seat-time live face",
 "r963 prereg derived", "85-row cut", '== 85 \\', '== 87, \\',
 "n1w230-0of12", "n1w230-11of12", "seat MSG-1230 tail",
 "ordinal machine-read NINETIETH per probe receipt"]
for s in must_one:
    c = t.count(s)
    assert c == 1, f"MUST-ONE {s!r} count {c} != 1"

# --- calibration dump (dbg2): actual counts for the uncertain final faces ---
import json as _json
_cal = {s: t.count(s) for s in ["W228", "w228_", "n1_w229_results", "n1_w230_results",
 "2ae8553e6", "f4b24e865", "r962 10:1x", "fourth consecutive", "88 rows", "w229_a_tail",
 "w229_b_tail", "w229_freeze_sha", "w229_prereg_sha", "w230_prereg_sha", "w230_receipt_sha",
 "W229", "w229_", "w226_leg", "w227_leg", "w228_leg", "w229_leg", "r962", "nineteenth consecutive",
 "NINETIETH instance", "NINETY-FIRST instance anticipated", "6cfe285e3", "91de0ae83",
 "n1_w230", "MSG-20261013-1000-bmc", "MSG-20261013-0855-bmc", "60th", "sixtieth",
 "TWO HUNDRED AND THIRTIETH", "W230+ projection", "naive W231 A window",
 "e3665b334", "b5d62792d", "842f817ad", "c9e9e83b8", "r963 freeze window",
 "WAVE_CONFIGS[230]", "WAVE_CONFIGS[229]", "w229_out_path", "w230_a_tail", "w229_total"]}
open(os.path.join(HERE, "_w230bmc_dbg2_counts.json"), "w", encoding="utf-8").write(_json.dumps(_cal, indent=1))
print("DBG2 COUNTS:", _json.dumps(_cal))

assert t.count("MSG-20261013-1000-bmc") == 4
assert t.count('230: {"batch": "PERPETUAL-N1-W230"') == 2   # new_cfg gate + n1_t4 post-edit gate
assert t.count("MSG-20261013-0855-bmc") == 2          # upstream seat references
assert t.count("W231+ projection") == 2
assert t.count("naive W231 A window") == 2
assert t.count("NINETY-FIRST instance anticipated") == 2
assert t.count("NINETIETH instance") == 5
assert t.count("TWO HUNDRED AND THIRTIETH") == 3
assert t.count("sixtieth") == 2
assert t.count("60th") == 6
assert t.count("60th own wave") == 2
assert t.count("bmc_ordinal=60") == 3
assert t.count("_w230bmc_20261013_probe_receipt.json") == 9
assert t.count("_w230bmc_freeze_receipt.json") == 1
assert t.count("w227_leg") == 2
assert t.count("w228_leg") == 2
assert t.count("w229_leg") == 2
assert t.count('"w228_transitive"') == 1
assert t.count('"w229_upstream"') == 2
assert t.count("assert pf.N1_BANDS[229] ==") == 2     # w229_leg def + post-edit gate
assert t.count("assert pf.N1_BANDS[228] ==") == 1     # w228_leg def (sentinel-kept)
assert t.count("WAVE_CONFIGS[230]") == 2             # band-facts self asserts
assert t.count("WAVE_CONFIGS[229]") == 3             # upstream mirror asserts
assert t.count("w228_out_path") == 2
assert t.count("n1_w230") == 5
assert t.count("n1_w229_results") == 4               # upstream refs (shift-landed)
assert t.count("n1_w230_results") == 2               # self path refs (shift-landed)
assert t.count("2ae8553e6") >= 6
assert t.count("f4b24e865") == 2
assert t.count("r962 10:1x") == 3
assert t.count("r963 freeze window") == 4
assert t.count("r963 freeze-window bundle") == 2
assert t.count("nineteenth consecutive") == 2
assert t.count("88 rows") == 2
assert t.count("if w < 230)") == 5
assert t.count("range(16, 230)") == 2
assert t.count("range(17, 230)") == 3
assert t.count("registered wave below 230 composes") == 2
assert t.count("fourth consecutive") == 2
assert t.count("w229_a_tail") == 14
assert t.count("w229_b_tail") == 9
assert t.count("w229_freeze_sha") == 6
assert t.count("w229_prereg_sha") == 3
assert t.count("w230_prereg_sha") == 5
assert t.count("w230_receipt_sha") == 4
assert t.count("1000") >= 1 and t.count("0855-bmc.md") == 0

open(OUT, "w", encoding="utf-8", newline="").write(t)
py_compile.compile(OUT, doraise=True)
print(f"DERIVE OK: {OUT} ({len(t)} chars, template 48884); py_compile green")
print("NEXT: run the editor (gates fail-closed) -> pf/n1 selftest -> pathspec commit+push -> PRE-FINALIZE six-gate -> engine self-burn verify (2-cycle n1_w230 growth)")
