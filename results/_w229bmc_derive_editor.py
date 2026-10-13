# -*- coding: utf-8 -*-
# r961 bm-c derive: W228 -> W229 five-face freeze editor (count-asserted ordered
# transform; fail-closed pair law; protect-restore sentinels for fixed-estate faces).
# Template = committed _w228bmc_freeze_edits.py (48,325-char text, r959 dead-window
# generation, estate machine-verified then landed 842f817ad by r959-continuation,
# proven live-fire).
# All wave facts shift by token; every machine-derivable fact is re-asserted at
# editor RUNTIME against live git/pf/receipt data (fail-closed).
# Census evidence = _r961bmc_editor_census.py run this window (counts in hand).
# Disclosed deltas vs the mechanical clone (correctness pairs, both machine-verifiable
# against the committed W229 probe receipt):
#  (a) the MEM/PRE "ordinal machine-read EIGHTY-SEVENTH per probe receipt" aging face
#      (r927 fixB one-wave-behind family, inherited un-shifted since the W227 editor
#      because the token lacks the " instance" suffix the ordinals shift matches)
#      fixed to EIGHTY-NINTH = the W229 probe receipt leg1 A_semantics machine-read
#      ordinal ("staircase A-hops-prior-B EIGHTY-NINTH instance, E36 card");
#  (b) upstream W228-cycle prose rewritten honestly: the W228 cycle shape differs
#      from the W227 absorb shape (in-window finalize one-pass 6744db794 08:3x +
#      dead-r959-window splice estate machine-verified then landed 842f817ad by
#      r959-continuation + engine self-burn 12/12 self-committed 03bca8089+95e210be1;
#      six-gate PRE-FINALIZE correct phase, third consecutive correct-phase wave).
import os, sys, py_compile

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.join(HERE, "_w228bmc_freeze_edits.py")
OUT  = os.path.join(HERE, "_w229bmc_freeze_edits.py")

t = open(BASE, "r", encoding="utf-8", newline="").read()
assert len(t) == 48325, f"template length drift: {len(t)} != 48325"

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
assert n1_t4.count('    # --- W227 materializer face') == 1  # prior block kept (W227 splice landed r956 dead window, estate absorbed by r956-absorb 1e5ed3326)"""
rep(KEPT_ORIG, "@@KEPT@@", 1)

LIVE_ORIG = '''  "liveness_anchors": {"t141_marker_kept": 1, "w209_block_kept": 1, "w210_block_kept": 1, "w211_block_kept": 1, "w212_block_kept": 1, "w213_block_kept": 1, "w214_block_kept": 1, "w215_block_kept": 1, "w216_block_kept": 1, "w217_block_kept": 1, "w218_block_kept": 1, "w219_block_kept": 1, "w220_block_kept": 1, "w221_block_kept": 1, "w222_block_kept": 1, "w223_block_kept": 1, "w224_block_kept": 1, "w225_block_kept": 1, "w226_block_kept": 1, "w227_block_kept": 1},'''
rep(LIVE_ORIG, "@@LIVE@@", 1)

LEG227_ORIG = '''w227_leg = [
 f\'        assert pf.N1_BANDS[227] == {{"a": ({fmt(pf_mod.N1_BANDS[227]["a"][0])}, {fmt(pf_mod.N1_BANDS[227]["a"][1])}),\',
 f\'                                    "b_exit": ({fmt(pf_mod.N1_BANDS[227]["b_exit"][0])}, {fmt(pf_mod.N1_BANDS[227]["b_exit"][1])}),\',
\'                                    "engine_owner": "bm-c"}, \\\\',
\'            "registered W227 row parity drift (r307; bm-c five-face freeze; own-seat face disclosed)"\',
]'''
rep(LEG227_ORIG, "@@LEG227@@", 1)

ASM_ORIG = "block = EOL.join(hdr) + EOL + par_sec + EOL.join(w225_leg) + EOL + EOL.join(w226_leg) + EOL + EOL.join(w227_leg) + EOL + EOL.join(tail) + EOL"
rep(ASM_ORIG, "@@ASM@@", 1)

# ---------------- phase 1: ordered global shifts (descending, count-logged) ----------------
SHIFTS = [
 ("n1_w228", "n1_w229", 5),            # self shard/out names (BEFORE w228_ var shift, substring law)
 ("w228_", "w229_", 9),               # self vars: prereg_sha 5 + receipt_sha 4 (post n1_w228)
 ("n1w228", "n1w229", 2),              # entry-identity tags
 ("W228", "W229", 72),                # self prose global (PERPETUAL rides along)
 ("W227", "W228", 111),               # upstream prose global
 ("w227_", "w228_", 94),              # upstream vars (n1_w227_results rides along; LEG227 sentinel-excluded)
 ("m225", "m226", 3),
 ("N1_BANDS\\[225\\]", "N1_BANDS\\[226\\]", 1),   # m-cut regex literal (raw-bracket form)
 ("_c227", "_c228", 5),
 ("arith_a228", "arith_a229", 3),
 ("arith_b228", "arith_b229", 3),
 ("n3r1_used228", "n3r1_used229", 3),
 ("_set_wave(228)", "_set_wave(229)", 1),
 ("'227: {\"batch\"'", "'228: {\"batch\"'", 2),   # upstream cfg needles (CFG_I + _c find; quoted complete tokens only)
 ("'227: {\"a\"'", "'228: {\"a\"'", 2),           # upstream row needles (pickaxe -S + ROW_I; quoted complete tokens)
 ("'    227: {\"a\"'", "'    228: {\"a\"'", 1),
 ("f'{CFG_I}228: ", "f'{CFG_I}229: ", 1),
 ("f'{ROW_I}228: ", "f'{ROW_I}229: ", 1),
 ("f'228: {{\"a\":", "f'229: {{\"a\":", 1),
 ("ROW_I + '228: {\"a\"'", "ROW_I + '229: {\"a\"'", 1),
 ("N1_BANDS.get(227)", "N1_BANDS.get(228)", 1),
 ("WAVE_CONFIGS[228]", "WAVE_CONFIGS[229]", 2),       # band-facts self asserts (key form; BEFORE the [227]->[228] mirror shift)
 ("WAVE_CONFIGS[227]", "WAVE_CONFIGS[228]", 3),
 ("pf.N1_BANDS[227]", "pf.N1_BANDS[228]", 4),   # mirror x3 + post-edit gate ==" x1 (LEG227 sentinel-excluded)
 ("wave 228 = first free number", "wave 229 = first free number", 1),
 ("wave 228: ", "wave 229: ", 1),
 ("if w < 228)", "if w < 229)", 5),
 ("if w < 227", "if w < 228", 1),
 ("w<227 leaked", "w<228 leaked", 1),
 ("w<228 count", "w<229 count", 1),
 ("range(16, 228)", "range(16, 229)", 2),
 ("range(17, 228)", "range(17, 229)", 3),
 ("registered wave below 228 composes", "registered wave below 229 composes", 2),
 ("seat MSG-1228 tail", "seat MSG-1229 tail", 1),
 ('"wave": 228,', '"wave": 229,', 1),
 ("EIGHTY-NINTH instance anticipated", "NINETIETH instance anticipated", 2),   # FIRST (before EIGHTH->NINTH)
 ("EIGHTY-EIGHTH instance", "EIGHTY-NINTH instance", 5),
 ("TWO HUNDRED AND TWENTY-EIGHTH", "TWO HUNDRED AND TWENTY-NINTH", 3),
 ("fifty-eighth", "fifty-ninth", 2),
 ("58th", "59th", 6),
 ("bmc_ordinal=58", "bmc_ordinal=59", 3),
 ("rows 57 + candidate", "rows 58 + candidate", 4),
 ("rows 217 + candidate", "rows 218 + candidate", 1),
 ("== 217 and len(bmc_rows_live) == 57", "== 218 and len(bmc_rows_live) == 58", 1),
 ("expect 217/57", "expect 218/58", 1),
 ("precedent 216/56 pre-splice", "precedent 217/57 pre-splice", 1),
 ("splice 217/57", "splice 218/58", 1),
 ("r957 probe leg0", "r959 probe leg0", 1),
 ("r957 seat-time live face", "r959 seat-time live face", 1),
 ("probe receipt @ r957 window", "probe receipt @ r959 window", 2),
 ("r959 freeze window", "r961 freeze window", 4),
 ("r959 freeze-window bundle", "r961 freeze-window bundle", 2),
 ("r958 prereg derived", "r960 prereg derived", 1),
 ("seventeenth consecutive", "eighteenth consecutive", 2),
 ("e6c8441aa", "e485a0b3f", 1),
 ("TWELVE-level", "THIRTEEN-level", 1),
 ("MSG-20261013-0720-bmc", "MSG-20261013-0855-bmc", 4),   # self seat swap FIRST
 ("MSG-20261013-0645-bmc", "MSG-20261013-0720-bmc", 2),   # upstream seat AFTER self swap
 ("4e30ddf69", "c9e9e83b8", 1),
 ("_w228bmc_20261013_probe_receipt.json", "_w229bmc_20261013_probe_receipt.json", 9),
 ("_w228bmc_freeze_receipt.json", "_w229bmc_freeze_receipt.json", 1),
 ("(516_404, 518_403)", "(518_604, 520_603)", 1),
 ("(518_404, 518_603)", "(520_604, 520_803)", 1),
 ("923_189", "925_389", 1),
 ("497_320", "499_520", 1),
 ("(expect 923,189 / 497,320)", "(expect 925,389 / 499,520)", 1),
 ("48c321706", "842f817ad", 1),
 ("r956 06:5x", "r959 08:3x", 3),
 ("W229+ projection", "W230+ projection", 2),
 ("naive W229 A window", "naive W230 A window", 2),
 ("W229 freezer", "W230 freezer", 1),
 ("W229+ freezer", "W230+ freezer", 1),
 ("downstream W229 seat NOT yet published", "downstream W230 seat NOT yet published", 1),
 ("downstream W229 seat publication pending", "downstream W230 seat publication pending", 1),
 ("W226/W225/W224/W223 finalize are transitive deps", "W227/W226/W225/W224 finalize are transitive deps", 1),
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
pair("""# 2026-10-13 08:1x bm-c r959 freeze window (upstream W1..W227 ALL LANDED, clean precondition): W228 five-face freeze splice editor.""",
"""# 2026-10-13 09:2x bm-c r961 freeze window (upstream W1..W228 ALL LANDED, clean precondition): W229 five-face freeze splice editor.""")
# regression guards for the window-label pair (new side must carry the SHIFTED wave faces)
assert t.count("(upstream W1..W228 ALL LANDED, clean precondition): W229 five-face") == 1
assert t.count("W228 five-face freeze splice editor") == 0

pair("""# present (W227 finalize one-pass r956 06:5x dead-window body absorbed by
# r956-absorb 1e5ed3326, net chain head 923,189, merged pool K=497,320,
# n1_w227_results.json machine-read) -- ZERO in-flight upstream seats,""",
"""# present (W228 finalize one-pass r959 08:3x landed in-window 6744db794; splice
# estate 842f817ad dead r959 window machine-verified then landed by
# r959-continuation, net chain head 925,389, merged pool K=499,520,
# n1_w228_results.json machine-read) -- ZERO in-flight upstream seats,""")

pair("""# Lineage: _w227bmc_freeze_edits.py pattern (proven live-fire freeze,
# r956 dead-window body, estate absorbed by r956-absorb 1e5ed3326) + r787 preflight law + r609""",
"""# Lineage: _w228bmc_freeze_edits.py pattern (proven live-fire freeze,
# r959 dead-window estate, machine-verified then landed 842f817ad by
# r959-continuation) + r787 preflight law + r609""")

pair("""# LHS/RHS/comment ATOMIC TRIPLE absorbed (the new block's w<228>/
# range(16,228)/below-228 triple is count-asserted atomically; the W227
# block's own w<227 face is legitimate prior-wave boundary, not stale).""",
"""# LHS/RHS/comment ATOMIC TRIPLE absorbed (the new block's w<229>/
# range(16,229)/below-229 triple is count-asserted atomically; the W228
# block's own w<228 face is legitimate prior-wave boundary, not stale).""")

pair("""# STRUCTURAL CHOICE (vs the W226 editor): the parity estate (W138..W206
# full-span, 69 rows, r858 absorb generation) is extracted from the OWN W227
# block physical bytes -- structure known exactly (this machine's own splice
# generation) -- the W227 block's own W225 leg (1 row) is excluded from the
# estate path and fresh W225 + W226 + W227 legs are appended for the W228
# block parity (86 rows: estate 69 + W211..W224 legs + W225 leg + W226 leg +
# W227 leg). Extraction self-asserts the 83-row cut (69 estate + W211..W223 +
# W224) regardless.""",
"""# STRUCTURAL CHOICE (vs the W227 editor): the parity estate (W138..W206
# full-span, 69 rows, r858 absorb generation) is extracted from the OWN W228
# block physical bytes -- structure known exactly (this machine's own splice
# generation) -- the W228 block's own W226 leg (1 row) is excluded from the
# estate path and fresh W226 + W227 + W228 legs are appended for the W229
# block parity (87 rows: estate 69 + W211..W225 legs + W226 leg + W227 leg +
# W228 leg). Extraction self-asserts the 84-row cut (69 estate + W211..W224 +
# W225) regardless.""")

pair("""# STRUCTURAL CHOICE: extract the estate from the OWN W227 block (bytes known
# exactly: full-span estate W138..W206 69 rows + own W211 leg + ... + own W223 leg) -- the W227 block is this machine's own splice generation
# (r956 freeze-window editor, estate absorbed by r956-absorb 1e5ed3326), structure known. The W227 block span ends where the
# T-141 s2 lane face marker begins.""",
"""# STRUCTURAL CHOICE: extract the estate from the OWN W228 block (bytes known
# exactly: full-span estate W138..W206 69 rows + own W211 leg + ... + own W225 leg) -- the W228 block is this machine's own splice generation
# (r959 freeze-window editor, estate machine-verified then landed 842f817ad by r959-continuation), structure known. The W228 block span ends where the
# T-141 s2 lane face marker begins.""")

# --- gate 0.5 transitive window slide (W226 out -> W227 transitive) ---
pair("""w226_out_path = os.path.join(REPO, "results", "perpetual_faces", "n1_w226_results.json")
assert os.path.exists(w226_out_path), "W226 finalize product missing (transitive chain dep) -- abort\"""",
"""w227_out_path = os.path.join(REPO, "results", "perpetual_faces", "n1_w227_results.json")
assert os.path.exists(w227_out_path), "W227 finalize product missing (transitive chain dep) -- abort\"""")

pair('f"W227+W226+W225+W224+W223 finalize products present "',
     'f"W228+W227+W226+W225+W224 finalize products present "')

# --- seat/prose fixups (post-shift anchors) ---
pair(" " + "MSG-20261013-0645-bmc, executed bm-c r956 dead window, estate absorbed by r956-absorb 1e5ed3326; engine self-burn 12/12; finalize one-pass r959 08:3x; six-gate PRE-FINALIZE correct phase standing law held), ",
     " " + "MSG-20261013-0720-bmc, executed bm-c r957 (seat 4e30ddf69); splice 842f817ad dead r959 window estate machine-verified then landed by r959-continuation; engine self-burn 12/12; finalize one-pass r959 08:3x; six-gate PRE-FINALIZE correct phase standing law held, third consecutive), ")

pair(''' "    #     MSG-20261013-0645-bmc, executed bm-c r956 dead window, estate absorbed",
 "    #     by r956-absorb 1e5ed3326; engine self-burn 12/12 + finalize one-pass r959 08:3x splice",
 "    #     estate + PRE-FINALIZE six-gate chain (standing law held, W212-pattern",
 "    #     zero recurrence -- THIS W229 cycle runs PRE-FINALIZE likewise), honest note)",''',
''' "    #     MSG-20261013-0720-bmc, executed bm-c r957 (seat 4e30ddf69); splice",
 "    #     842f817ad dead r959 window estate machine-verified then landed by",
 "    #     r959-continuation; engine self-burn 12/12 + finalize one-pass r959 08:3x",
 "    #     splice estate + PRE-FINALIZE six-gate chain (standing law held, third",
 "    #     consecutive -- THIS W229 cycle runs PRE-FINALIZE likewise), honest note)",''')

pair('''"    #     seat MSG + pre-seat probe script + probe receipt @ r957 window; per-wave prereg",
 "    #     r958 + freeze splice script landed in this r959 freeze-window bundle",''',
'''"    #     seat MSG + pre-seat probe script + probe receipt @ r959 window; per-wave prereg",
 "    #     r960 + freeze splice script landed in this r961 freeze-window bundle",''')

pair(''' "seat MSG + pre-seat probe script + probe receipt @ r957 window; per-wave prereg ",
 "r958 + freeze splice script landed in this r959 freeze-window bundle ",''',
''' "seat MSG + pre-seat probe script + probe receipt @ r959 window; per-wave prereg ",
 "r960 + freeze splice script landed in this r961 freeze-window bundle ",''')

# --- correctness delta (a): probe-receipt ordinal aging face fixed (disclosed header) ---
pair("ordinal machine-read EIGHTY-SEVENTH per probe receipt",
     "ordinal machine-read EIGHTY-NINTH per probe receipt")

pair('"machine-checkable = A-hops-prior-B staircase EIGHTY-SEVENTH ",',
     '"machine-checkable = A-hops-prior-B staircase EIGHTY-NINTH ",')

# --- estate/parity count pairs ---
pair('assert par_sec.count("assert pf.N1_BANDS[") == 83 \\',
     'assert par_sec.count("assert pf.N1_BANDS[") == 84 \\')
pair("    and int(_estate_ws[82]) == 224, \\",
     "    and int(_estate_ws[82]) == 224 \\\n    and int(_estate_ws[83]) == 225, \\")
pair('f"estate segment not W138..W206 full-span 69 rows + W211..W223 legs + W224 leg: n=',
     'f"estate segment not W138..W206 full-span 69 rows + W211..W224 legs + W225 leg: n=')
pair('assert par_full.count("assert pf.N1_BANDS[") == 85, \\',
     'assert par_full.count("assert pf.N1_BANDS[") == 86, \\')
pair("!= 85 (69 estate + W211..W223 legs + W224 leg + W225 leg + W226 leg)\"",
     "!= 86 (69 estate + W211..W223 legs + W224 leg + W225 leg + W226 leg + W227 leg)\"")

# --- m-cut assert message (leg index moves down one) ---
pair('assert m225, "upstream W225 row leg not found inside W227 parity span"',
     'assert m226, "upstream W226 row leg not found inside W228 parity span"')

# --- cfg/row key literals (self-keyed gate strings, colon-continuation form) ---
pair("assert new_cfg.count('228: {\"batch\": \"PERPETUAL-N1-W228\"') == 1",
     "assert new_cfg.count('229: {\"batch\": \"PERPETUAL-N1-W229\"') == 1")
pair("assert n1_t4.count('228: {\"batch\": \"PERPETUAL-N1-W228\"') == 1",
     "assert n1_t4.count('229: {\"batch\": \"PERPETUAL-N1-W229\"') == 1")

# --- post-edit gate [227] -> [228] (leg def keeps [227] via sentinel) ---
pair("""assert n1_t4.count(f'assert pf.N1_BANDS[228] == {{"a": ({fmt(pf_mod.N1_BANDS[227]["a"][0])}, {fmt(pf_mod.N1_BANDS[227]["a"][1])}),') == 1""",
     """assert n1_t4.count(f'assert pf.N1_BANDS[228] == {{"a": ({fmt(pf_mod.N1_BANDS[228]["a"][0])}, {fmt(pf_mod.N1_BANDS[228]["a"][1])}),') == 1""")

# --- w225_leg def -> w228_leg def (drop oldest leg, add newest; content [228]) ---
pair("""w225_leg = [
 f'        assert pf.N1_BANDS[225] == {{"a": ({fmt(pf_mod.N1_BANDS[225]["a"][0])}, {fmt(pf_mod.N1_BANDS[225]["a"][1])}),',
 f'                                    "b_exit": ({fmt(pf_mod.N1_BANDS[225]["b_exit"][0])}, {fmt(pf_mod.N1_BANDS[225]["b_exit"][1])}),',
'                                    "engine_owner": "bm-c"}, \\\\',
'            "registered W225 row parity drift (r307; bm-c five-face freeze; own-seat face disclosed)"',
]""",
"""w228_leg = [
 f'        assert pf.N1_BANDS[228] == {{"a": ({fmt(pf_mod.N1_BANDS[228]["a"][0])}, {fmt(pf_mod.N1_BANDS[228]["a"][1])}),',
 f'                                    "b_exit": ({fmt(pf_mod.N1_BANDS[228]["b_exit"][0])}, {fmt(pf_mod.N1_BANDS[228]["b_exit"][1])}),',
'                                    "engine_owner": "bm-c"}, \\\\',
'            "registered W228 row parity drift (r307; bm-c five-face freeze; own-seat face disclosed)"',
]""")

# --- receipt upstream + transitive block ---
pair('''  "w227_upstream": {"freeze_sha": w227_freeze_sha, "prereg_sha": w227_prereg_sha,
                    "ledger_total": w227_total, "merged_n": w227_merged_n,
                    "engine_owner": "bm-c (own seat honored, no takeover face)",
                    "repair_chain_note": "r956 splice (W227 freeze landed 48c321706 dead window, estate absorbed by r956-absorb 1e5ed3326) + engine self-burn 12/12 + r956 finalize one-pass 06:5x (six-gate PRE-FINALIZE correct phase -- standing law held)"},''',
'''  "w228_upstream": {"freeze_sha": w228_freeze_sha, "prereg_sha": w228_prereg_sha,
                    "ledger_total": w228_total, "merged_n": w228_merged_n,
                    "engine_owner": "bm-c (own seat honored, no takeover face)",
                    "repair_chain_note": "r959 splice (W228 freeze landed 842f817ad dead r959 window, estate machine-verified then landed by r959-continuation) + engine self-burn 12/12 (03bca8089+95e210be1) + r959 finalize one-pass 08:3x 6744db794 (six-gate PRE-FINALIZE correct phase -- standing law held, third consecutive)"},''')

pair('''  "w226_transitive": {"finalize_product": "results/perpetual_faces/n1_w226_results.json present (belt-and-braces gate; ledger 920,989 / K=495,120)"},''',
'''  "w227_transitive": {"finalize_product": "results/perpetual_faces/n1_w227_results.json present (belt-and-braces gate; ledger 923,189 / K=497,320)"},''')

# --- receipt prereg_bundle note ---
pair('"note": "prereg derived+committed in the r958 window (e6c8441aa, TWELVE-level lineage replay chain, preflight 46/46); splice editor derived from the committed W227 editor template by count-asserted ordered transform (protect-restore regions, fail-closed pair law) in this same r959 freeze window; upstream W227 already landed (clean-precondition seventeenth consecutive window); zero transcription"',
     '"note": "prereg derived+committed in the r960 window (e485a0b3f, THIRTEEN-level lineage replay chain, preflight 46/46); splice editor derived from the committed W228 editor template by count-asserted ordered transform (protect-restore regions, fail-closed pair law) in this same r961 freeze window; upstream W228 already landed (clean-precondition eighteenth consecutive window); zero transcription"')

# --- receipt parity + family6 notes ---
pair("full-span estate W138..W206 (69 rows, r858 absorb generation) + W211..W224 legs + W225 leg + W226 leg + W227 leg -> W228 block = 86 rows ending at W227;",
     "full-span estate W138..W206 (69 rows, r858 absorb generation) + W211..W225 legs + W226 leg + W227 leg + W228 leg -> W229 block = 87 rows ending at W228;")

pair('"note": "W227 editor family-6 gate carried forward: new block LHS w<228 x3 / RHS range(16,228)+range(17,228) / comment below-228 count-asserted ATOMICALLY before splice; W227 block\'s own w<227 face = legitimate prior-wave boundary (not stale)"',
     '"note": "W228 editor family-6 gate carried forward: new block LHS w<229 x3 / RHS range(16,229)+range(17,229) / comment below-229 count-asserted ATOMICALLY before splice; W228 block\'s own w<228 face = legitimate prior-wave boundary (not stale)"')

# --- receipt ordinal faces ---
pair('''                    "probe_receipt_bmc_ordinal_face": 58,''',
'''                    "probe_receipt_bmc_ordinal_face": 59,''')

# ---------------- phase 3: sentinel restores (with W229 additions) ----------------
rep("@@KEPT@@", KEPT_ORIG + "\nassert n1_t4.count('    # --- W228 materializer face') == 1  # prior block kept (W228 splice landed 842f817ad dead r959 window, estate machine-verified then landed by r959-continuation)", 1)
rep("@@LIVE@@", LIVE_ORIG.replace('"w227_block_kept": 1},', '"w227_block_kept": 1, "w228_block_kept": 1},'), 1)
rep("@@LEG227@@", LEG227_ORIG, 1)
rep("@@ASM@@", "block = EOL.join(hdr) + EOL + par_sec + EOL.join(w226_leg) + EOL + EOL.join(w227_leg) + EOL + EOL.join(w228_leg) + EOL + EOL.join(tail) + EOL", 1)

# ---------------- phase 4: validation (fail-closed) ----------------
stale = ["(516_404, 518_403)", "(518_404, 518_603)", "48c321706",
 "e6c8441aa", "TWELVE-level", "MSG-20261013-0645-bmc",
 "r956 06:5x", "r956 splice", "r956 freeze-window editor",
 "r959 freeze window", "r959 freeze-window bundle",
 "expect 217/57", "precedent 216/56 pre-splice", "splice 217/57", "== 217 and len", "rows 217 + candidate",
 "rows 57 + candidate", "bmc_ordinal=58", "58th", "fifty-eighth",
 "EIGHTY-EIGHTH instance", "EIGHTY-SEVENTH",
 "TWO HUNDRED AND TWENTY-EIGHTH", "923_189", "497_320", "(expect 923,189",
 "r957 probe leg0", "r957 seat-time", "r957 window",
 "seventeenth consecutive",
 "_w228bmc_20261013_probe_receipt.json", "_w228bmc_freeze_receipt.json",
 "w225_leg", "n1w228-", "N1_BANDS.get(227)", "if w < 227", "w<227 leaked", "w<228 count",
 "range(16, 228)", "range(16,228)", "range(17, 228)", "below 228 composes", "below-228",
 "m225", "_c227", "n3r1_used228", "arith_a228", "arith_b228",
 "N1_BANDS\\[225\\]",
 "W229+ projection", "naive W229 A window", "W229 freezer", "W229+ freezer",
 "downstream W229 seat", "(86 rows", "83-row cut", "the 82-row cut", '== 83 \\', '== 85, \\',
 "!= 85 (69 estate", "own W225 leg (1 row)", "own W223 leg", "upstream W225 row leg",
 "rows 57 + candidate = 58th owned (live derive at freeze time governs per r587/r359; probe leg0 bmc_ordinal=58 = r957",
 "@@KEPT@@", "@@LIVE@@", "@@LEG227@@", "@@ASM@@", "e485a0b3f" + "x-guard",
 '229: {"batch": "PERPETUAL-N1-W229"x-guard']
# kept-line legit faces (W227 kept-assert comment carries the W227-cycle splice history verbatim)
assert t.count("1e5ed3326") == 1, f"kept-line 1e5ed3326 count {t.count('1e5ed3326')} != 1"
assert t.count("r956 dead window") == 1, f"kept-line r956 dead window != 1"
assert t.count("r956-absorb") == 1, f"kept-line r956-absorb != 1"
# upstream-seat provenance faces (P10 prose carries the W228 seat origin sha)
assert t.count("4e30ddf69") == 2, f"upstream seat-origin 4e30ddf69 count != 2"
for s in stale:
    c = t.count(s)
    assert c == 0, f"STALE TOKEN {s!r} count {c} != 0"

must_one = ["_set_wave(229)",
 "f'{CFG_I}229: ", "f'{ROW_I}229: ", "ROW_I + '229: {\"a\"'", '"wave": 229',
 "MSG-20261013-0855-bmc.md", "c9e9e83b8", "925_389", "499_520",
 "(expect 925,389 / 499,520)", "(518_604, 520_603)", "(520_604, 520_803)",
 "int(_estate_ws[83]) == 225", "e485a0b3f", "THIRTEEN-level",
 '"probe_receipt_bmc_ordinal_face": 59,', '"w228_block_kept": 1}',
 "N1_BANDS.get(228)", "r959 probe leg0", "r959 seat-time live face",
 "r960 prereg derived", "84-row cut", '== 84 \\', '== 86, \\',
 "n1w229-0of12", "n1w229-11of12", "seat MSG-1229 tail",
 "ordinal machine-read EIGHTY-NINTH per probe receipt"]
for s in must_one:
    c = t.count(s)
    assert c == 1, f"MUST-ONE {s!r} count {c} != 1"

# --- calibration dump (dbg2): actual counts for the uncertain final faces ---
import json as _json
_cal = {s: t.count(s) for s in ["W227", "w227_", "n1_w228_results", "n1_w227_results",
 "842f817ad", "6744db794", "r959 08:3x", "third consecutive", "87 rows", "w228_a_tail",
 "w228_b_tail", "w228_freeze_sha", "w228_prereg_sha", "w229_prereg_sha", "w229_receipt_sha",
 "W226", "w226_", "MSG-20261013-0855-bmc", "MSG-20261013-0720-bmc", "59th", "fifty-ninth",
 "EIGHTY-NINTH instance", "NINETIETH instance anticipated", "c9e9e83b8", "e485a0b3f",
 "n1_w229", "w226_leg", "w227_leg", "w228_leg", "r959-continuation", "eighteenth consecutive"]}
open(os.path.join(HERE, "_w229bmc_dbg2_counts.json"), "w", encoding="utf-8").write(_json.dumps(_cal, indent=1))
print("DBG2 COUNTS:", _json.dumps(_cal))

assert t.count("MSG-20261013-0855-bmc") == 4
assert t.count('229: {"batch": "PERPETUAL-N1-W229"') == 2   # new_cfg gate + n1_t4 post-edit gate
assert t.count("MSG-20261013-0720-bmc") == 2          # upstream seat references
assert t.count("W230+ projection") == 2
assert t.count("naive W230 A window") == 2
assert t.count("NINETIETH instance anticipated") == 2
assert t.count("EIGHTY-NINTH instance") == 5
assert t.count("TWO HUNDRED AND TWENTY-NINTH") == 3
assert t.count("fifty-ninth") == 2
assert t.count("59th") == 6
assert t.count("59th own wave") == 2
assert t.count("bmc_ordinal=59") == 3
assert t.count("_w229bmc_20261013_probe_receipt.json") == 9
assert t.count("_w229bmc_freeze_receipt.json") == 1
assert t.count("w226_leg") == 2
assert t.count("w227_leg") == 2
assert t.count("w228_leg") == 2
assert t.count('"w227_transitive"') == 1
assert t.count('"w228_upstream"') == 2
assert t.count("assert pf.N1_BANDS[228] ==") == 2     # w228_leg def + post-edit gate
assert t.count("assert pf.N1_BANDS[227] ==") == 1     # w227_leg def (sentinel-kept)
assert t.count("W227") == 11                          # legit upstream/kept faces (grep-verified in OUT)
assert t.count("w227_") == 8                          # leg def+asm, out_path x2, transitive key, +grep-verified kept faces
assert t.count("WAVE_CONFIGS[229]") == 2             # band-facts self asserts
assert t.count("WAVE_CONFIGS[228]") == 3             # upstream mirror asserts
assert t.count("w227_out_path") == 2
assert t.count("n1_w229") == 5
assert t.count("n1_w228_results") == 4               # upstream refs
assert t.count("n1_w227_results") == 2               # transitive refs (out_path block + receipt)
assert t.count("842f817ad") >= 5
assert t.count("6744db794") == 2
assert t.count("r959 08:3x") == 3
assert t.count("r961 freeze window") == 4
assert t.count("r961 freeze-window bundle") == 2
assert t.count("eighteenth consecutive") == 2
assert t.count("87 rows") == 2
assert t.count("if w < 229)") == 5
assert t.count("range(16, 229)") == 2
assert t.count("range(17, 229)") == 3
assert t.count("registered wave below 229 composes") == 2
assert t.count("third consecutive") == 2
assert t.count("w228_a_tail") == 14
assert t.count("w228_b_tail") == 9
assert t.count("w228_freeze_sha") == 6
assert t.count("w228_prereg_sha") == 3
assert t.count("w229_prereg_sha") == 5
assert t.count("w229_receipt_sha") == 4
assert t.count("0855") >= 1 and t.count("0720-bmc.md") == 0

open(OUT, "w", encoding="utf-8", newline="").write(t)
py_compile.compile(OUT, doraise=True)
print(f"DERIVE OK: {OUT} ({len(t)} chars, template 48325); py_compile green")
print("NEXT: run the editor (gates fail-closed) -> pf/n1 selftest -> pathspec commit+push -> PRE-FINALIZE six-gate -> engine self-burn verify (2-cycle n1_w229 growth)")
