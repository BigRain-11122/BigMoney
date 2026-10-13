# -*- coding: utf-8 -*-
# r959 bm-c derive: W227 -> W228 five-face freeze editor (count-asserted ordered
# transform; fail-closed pair law; protect-restore sentinels for fixed-estate faces).
# Template = committed _w227bmc_freeze_edits.py (48,037-char text, r956 dead-window
# generation, estate absorbed by r956-absorb 1e5ed3326, proven live-fire).
# All wave facts shift by token; every machine-derivable fact is re-asserted at
# editor RUNTIME against live git/pf/receipt data (fail-closed).
# Census evidence = _r959bmc_editor_census.py run this window (counts in hand).
# Clone map = results/_w228bmc_freeze_clone_map.md (r958 handover).
import os, sys, py_compile

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.join(HERE, "_w227bmc_freeze_edits.py")
OUT  = os.path.join(HERE, "_w228bmc_freeze_edits.py")

t = open(BASE, "r", encoding="utf-8", newline="").read()
assert len(t) == 48037, f"template length drift: {len(t)} != 48037"

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
assert n1_t4.count('    # --- W226 materializer face') == 1  # prior block kept (W226 splice landed r943 dead window, estate absorbed r945)"""
rep(KEPT_ORIG, "@@KEPT@@", 1)

LIVE_ORIG = '''  "liveness_anchors": {"t141_marker_kept": 1, "w209_block_kept": 1, "w210_block_kept": 1, "w211_block_kept": 1, "w212_block_kept": 1, "w213_block_kept": 1, "w214_block_kept": 1, "w215_block_kept": 1, "w216_block_kept": 1, "w217_block_kept": 1, "w218_block_kept": 1, "w219_block_kept": 1, "w220_block_kept": 1, "w221_block_kept": 1, "w222_block_kept": 1, "w223_block_kept": 1, "w224_block_kept": 1, "w225_block_kept": 1, "w226_block_kept": 1},'''
rep(LIVE_ORIG, "@@LIVE@@", 1)

LEG226_ORIG = '''w226_leg = [
 f\'        assert pf.N1_BANDS[226] == {{"a": ({fmt(pf_mod.N1_BANDS[226]["a"][0])}, {fmt(pf_mod.N1_BANDS[226]["a"][1])}),\',
 f\'                                    "b_exit": ({fmt(pf_mod.N1_BANDS[226]["b_exit"][0])}, {fmt(pf_mod.N1_BANDS[226]["b_exit"][1])}),\',
\'                                    "engine_owner": "bm-c"}, \\\\',
\'            "registered W226 row parity drift (r307; bm-c five-face freeze; own-seat face disclosed)"\',
]'''
rep(LEG226_ORIG, "@@LEG226@@", 1)

ASM_ORIG = "block = EOL.join(hdr) + EOL + par_sec + EOL.join(w224_leg) + EOL + EOL.join(w225_leg) + EOL + EOL.join(w226_leg) + EOL + EOL.join(tail) + EOL"
rep(ASM_ORIG, "@@ASM@@", 1)

# ---------------- phase 1: ordered global shifts (descending, count-logged) ----------------
SHIFTS = [
 ("n1_w227", "n1_w228", 5),            # self shard/out names (BEFORE w227_ var shift, substring law)
 ("w227_", "w228_", 9),                # self vars: prereg_sha 5 + receipt_sha 4 (post n1_w227)
 ("n1w227", "n1w228", 2),              # entry-identity tags
 ("W227", "W228", 73),                 # self prose global (PERPETUAL rides along)
 ("W226", "W227", 111),                # upstream prose global (census 114 minus 2 KEPT minus 1 LEG226)
 ("w226_", "w227_", 94),               # upstream vars (census 97 minus 1 LIVE minus 1 LEG226 minus 1 ASM)
 ("m224", "m225", 3),
 ("N1_BANDS\\[224\\]", "N1_BANDS\\[225\\]", 1),   # m-cut regex literal (raw-bracket form)
 ("_c226", "_c227", 5),
 ("arith_a227", "arith_a228", 3),
 ("arith_b227", "arith_b228", 3),
 ("n3r1_used227", "n3r1_used228", 3),
 ("_set_wave(227)", "_set_wave(228)", 1),
 ("'226: {\"batch\"'", "'227: {\"batch\"'", 2),
 ("'226: {\"a\"'", "'227: {\"a\"'", 2),
 ("'    226: {\"a\"'", "'    227: {\"a\"'", 1),
 ("f'{CFG_I}227: ", "f'{CFG_I}228: ", 1),
 ("f'{ROW_I}227: ", "f'{ROW_I}228: ", 1),
 ("f'227: {{\"a\":", "f'228: {{\"a\":", 1),
 ("ROW_I + '227: {\"a\"'", "ROW_I + '228: {\"a\"'", 1),
 ("N1_BANDS.get(226)", "N1_BANDS.get(227)", 1),
 ("WAVE_CONFIGS[227]", "WAVE_CONFIGS[228]", 2),       # band-facts self asserts (key form; BEFORE the [226]->[227] mirror shift)
 ("WAVE_CONFIGS[226]", "WAVE_CONFIGS[227]", 3),
 ("pf.N1_BANDS[226]", "pf.N1_BANDS[227]", 4),   # mirror x3 + post-gate ==" x1 (LEG226 sentinel-excluded)
 ("wave 227 = first free number", "wave 228 = first free number", 1),
 ("wave 227: ", "wave 228: ", 1),
 ("if w < 227)", "if w < 228)", 5),
 ("if w < 226", "if w < 227", 1),
 ("w<226 leaked", "w<227 leaked", 1),
 ("w<227 count", "w<228 count", 1),
 ("range(16, 227)", "range(16, 228)", 2),
 ("range(17, 227)", "range(17, 228)", 3),
 ("registered wave below 227 composes", "registered wave below 228 composes", 2),
 ("seat MSG-1227 tail", "seat MSG-1228 tail", 1),
 ('"wave": 227,', '"wave": 228,', 1),
 ("EIGHTY-EIGHTH instance anticipated", "EIGHTY-NINTH instance anticipated", 2),   # FIRST (before SEVENTH->EIGHTH)
 ("EIGHTY-SEVENTH instance", "EIGHTY-EIGHTH instance", 5),
 ("TWO HUNDRED AND TWENTY-SEVENTH", "TWO HUNDRED AND TWENTY-EIGHTH", 3),
 ("fifty-seventh", "fifty-eighth", 2),
 ("57th", "58th", 6),
 ("bmc_ordinal=57", "bmc_ordinal=58", 3),
 ("rows 56 + candidate", "rows 57 + candidate", 4),
 ("rows 216 + candidate", "rows 217 + candidate", 1),
 ("== 216 and len(bmc_rows_live) == 56", "== 217 and len(bmc_rows_live) == 57", 1),
 ("expect 216/56", "expect 217/57", 1),
 ("precedent 215/55 pre-splice", "precedent 216/56 pre-splice", 1),
 ("splice 216/56", "splice 217/57", 1),
 ("r955 probe leg0", "r957 probe leg0", 1),
 ("r955 seat-time live face", "r957 seat-time live face", 1),
 ("probe receipt @ r955 window", "probe receipt @ r957 window", 2),
 ("r956 freeze window", "r959 freeze window", 4),
 ("r956 prereg derived", "r958 prereg derived", 1),
 ("sixteenth consecutive", "seventeenth consecutive", 2),
 ("0d0c63c6e", "e6c8441aa", 1),
 ("ELEVEN-level", "TWELVE-level", 1),
 ("MSG-20261013-0645-bmc", "MSG-20261013-0720-bmc", 4),   # self seat swap FIRST
 ("MSG-20261012-2040", "MSG-20261013-0645-bmc", 2),       # upstream seat AFTER self swap
 ("10781c2f8", "4e30ddf69", 1),
 ("_w227bmc_20261012_probe_receipt.json", "_w228bmc_20261013_probe_receipt.json", 9),
 ("_w227bmc_freeze_receipt.json", "_w228bmc_freeze_receipt.json", 1),
 ("(514_204, 516_203)", "(516_404, 518_403)", 1),
 ("(516_204, 516_403)", "(518_404, 518_603)", 1),
 ("920_989", "923_189", 1),
 ("495_120", "497_320", 1),
 ("(expect 920,989 / 495,120)", "(expect 923,189 / 497,320)", 1),
 ("9b44d37d1", "48c321706", 1),
 ("bd50be730", "1e5ed3326", 2),
 ("r943 22:4x", "r956 06:5x", 3),
 ("W228+ projection", "W229+ projection", 2),
 ("naive W228 A window", "naive W229 A window", 2),
 ("W228 freezer", "W229 freezer", 1),
 ("W228+ freezer", "W229+ freezer", 1),
 ("downstream W228 seat NOT yet published", "downstream W229 seat NOT yet published", 1),
 ("downstream W228 seat publication pending", "downstream W229 seat publication pending", 1),
 ("W225/W224/W223/W222 finalize are transitive deps", "W226/W225/W224/W223 finalize are transitive deps", 1),
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
pair("""# 2026-10-13 06:4x bm-c r956 freeze window (upstream W1..W226 ALL LANDED, clean precondition): W227 five-face freeze splice editor.""",
"""# 2026-10-13 08:1x bm-c r959 freeze window (upstream W1..W227 ALL LANDED, clean precondition): W228 five-face freeze splice editor.""")

pair("""# present (W226 finalize one-pass r943 22:4x dead-window body absorbed by
# r945 bd50be730, net chain head 920,989, merged pool K=495,120,
# n1_w226_results.json machine-read) -- ZERO in-flight upstream seats,""",
"""# present (W227 finalize one-pass r956 06:5x dead-window body absorbed by
# r956-absorb 1e5ed3326, net chain head 923,189, merged pool K=497,320,
# n1_w227_results.json machine-read) -- ZERO in-flight upstream seats,""")

pair("""# Upstream six-gate disclosure: the W226 cycle ran its six-gate POST-FINALIZE
# (W212-pattern phase-miss #3, healed r944 receipts); THIS W227 cycle runs
# PRE-FINALIZE per the standing law (W217 debt lesson).""",
"""# Upstream six-gate disclosure: the W227 cycle ran its six-gate PRE-FINALIZE
# correctly (W217-debt standing law held, W212-pattern zero recurrence); THIS
# W228 cycle runs PRE-FINALIZE likewise (standing law).""")

pair("""# Lineage: _w226bmc_freeze_edits.py pattern (proven live-fire freeze,
# r943 dead-window body, estate absorbed r945) + r787 preflight law + r609""",
"""# Lineage: _w227bmc_freeze_edits.py pattern (proven live-fire freeze,
# r956 dead-window body, estate absorbed by r956-absorb 1e5ed3326) + r787 preflight law + r609""")

pair("""# LHS/RHS/comment ATOMIC TRIPLE absorbed (the new block's w<227>/
# range(16,227)/below-227 triple is count-asserted atomically; the W226
# block's own w<226 face is legitimate prior-wave boundary, not stale).""",
"""# LHS/RHS/comment ATOMIC TRIPLE absorbed (the new block's w<228>/
# range(16,228)/below-228 triple is count-asserted atomically; the W227
# block's own w<227 face is legitimate prior-wave boundary, not stale).""")

pair("""# STRUCTURAL CHOICE (vs the W225 editor): the parity estate (W138..W206
# full-span, 69 rows, r858 absorb generation) is extracted from the OWN W226
# block physical bytes -- structure known exactly (this machine's own splice
# generation) -- the W226 block's own W224 leg (1 row) is excluded from the
# estate path and fresh W224 + W225 + W226 legs are appended for the W227
# block parity (85 rows: estate 69 + W211..W223 legs + W224 leg + W225 leg +
# W226 leg). Extraction self-asserts the 82-row cut (69 estate + W211..W222 +
# W223) regardless.""",
"""# STRUCTURAL CHOICE (vs the W226 editor): the parity estate (W138..W206
# full-span, 69 rows, r858 absorb generation) is extracted from the OWN W227
# block physical bytes -- structure known exactly (this machine's own splice
# generation) -- the W227 block's own W225 leg (1 row) is excluded from the
# estate path and fresh W225 + W226 + W227 legs are appended for the W228
# block parity (86 rows: estate 69 + W211..W224 legs + W225 leg + W226 leg +
# W227 leg). Extraction self-asserts the 83-row cut (69 estate + W211..W223 +
# W224) regardless.""")

pair("""# STRUCTURAL CHOICE: extract the estate from the OWN W226 block (bytes known
# exactly: full-span estate W138..W206 69 rows + own W211 leg + ... + own W223 leg) -- the W226 block is this machine's own splice generation
# (r943 freeze-window editor, estate absorbed r945), structure known. The W226 block span ends where the
# T-141 s2 lane face marker begins.""",
"""# STRUCTURAL CHOICE: extract the estate from the OWN W227 block (bytes known
# exactly: full-span estate W138..W206 69 rows + own W211 leg + ... + own W223 leg) -- the W227 block is this machine's own splice generation
# (r956 freeze-window editor, estate absorbed by r956-absorb 1e5ed3326), structure known. The W227 block span ends where the
# T-141 s2 lane face marker begins.""")

# --- gate 0.5 transitive window slide (W222 out -> W226 transitive) ---
pair("""w222_out_path = os.path.join(REPO, "results", "perpetual_faces", "n1_w222_results.json")
assert os.path.exists(w222_out_path), "W222 finalize product missing (transitive chain dep) -- abort\"""",
"""w226_out_path = os.path.join(REPO, "results", "perpetual_faces", "n1_w226_results.json")
assert os.path.exists(w226_out_path), "W226 finalize product missing (transitive chain dep) -- abort\"""")

pair('f"W226+W225+W224+W223+W222 finalize products present "',
     'f"W227+W226+W225+W224+W223 finalize products present "')

# --- seat/prose fixups (post-shift anchors) ---
pair(" " + "MSG-20261012-2040, executed bm-c r943 dead window, estate absorbed r945; engine self-burn 12/12; finalize one-pass r943 22:4x; six-gate POST-FINALIZE heal disclosed W212-pattern #3), ",
     " " + "MSG-20261013-0645-bmc, executed bm-c r956 dead window, estate absorbed by r956-absorb 1e5ed3326; engine self-burn 12/12; finalize one-pass r956 06:5x; six-gate PRE-FINALIZE correct phase standing law held), ")

pair(''' "    #     MSG-20261012-2040, executed bm-c r943 dead window, estate absorbed",
 "    #     r945; engine self-burn 12/12 + finalize one-pass r943 22:4x splice",
 "    #     estate + POST-FINALIZE six-gate heal chain (W212-pattern #3",
 "    #     disclosed; THIS W227 cycle runs PRE-FINALIZE per standing law), honest note)",''',
''' "    #     MSG-20261013-0645-bmc, executed bm-c r956 dead window, estate absorbed",
 "    #     by r956-absorb 1e5ed3326; engine self-burn 12/12 + finalize one-pass r956 06:5x splice",
 "    #     estate + PRE-FINALIZE six-gate chain (standing law held, W212-pattern",
 "    #     zero recurrence -- THIS W228 cycle runs PRE-FINALIZE likewise), honest note)",''')

pair('"    # r956 prereg derived + freeze-window bundle, probe",',
     '"    # r958 prereg derived + landed pre-freeze, probe",')

pair('''"    #     seat MSG + pre-seat probe script + probe receipt @ r955 window; per-wave prereg +",
 "    #     freeze splice script landed in the r956 freeze-window bundle",''',
'''"    #     seat MSG + pre-seat probe script + probe receipt @ r957 window; per-wave prereg",
 "    #     r958 + freeze splice script landed in this r959 freeze-window bundle",''')

pair(''' "seat MSG + pre-seat probe script + probe receipt @ r955 window; per-wave prereg + ",
 "freeze splice script landed in the r956 freeze-window bundle ",''',
''' "seat MSG + pre-seat probe script + probe receipt @ r957 window; per-wave prereg ",
 "r958 + freeze splice script landed in this r959 freeze-window bundle ",''')

# --- estate/parity count pairs ---
pair('assert par_sec.count("assert pf.N1_BANDS[") == 82 \\',
     'assert par_sec.count("assert pf.N1_BANDS[") == 83 \\')
pair("    and int(_estate_ws[81]) == 223, \\",
     "    and int(_estate_ws[81]) == 223 \\\n    and int(_estate_ws[82]) == 224, \\")
pair('f"estate segment not W138..W206 full-span 69 rows + W211..W222 legs + W223 leg: n=',
     'f"estate segment not W138..W206 full-span 69 rows + W211..W223 legs + W224 leg: n=')
pair('assert par_full.count("assert pf.N1_BANDS[") == 84, \\',
     'assert par_full.count("assert pf.N1_BANDS[") == 85, \\')
pair("!= 84 (69 estate + W211..W223 legs + W224 leg + W225 leg)\"",
     "!= 85 (69 estate + W211..W223 legs + W224 leg + W225 leg + W226 leg)\"")

# --- m-cut assert message (leg index moves down one) ---
pair('assert m224, "upstream W224 row leg not found inside W226 parity span"',
     'assert m225, "upstream W225 row leg not found inside W227 parity span"')

# --- cfg/row key literals ---
pair("assert new_cfg.count('227: {\"batch\": \"PERPETUAL-N1-W227\"') == 1",
     "assert new_cfg.count('228: {\"batch\": \"PERPETUAL-N1-W228\"') == 1")
pair("assert n1_t4.count('227: {\"batch\": \"PERPETUAL-N1-W227\"') == 1",
     "assert n1_t4.count('228: {\"batch\": \"PERPETUAL-N1-W228\"') == 1")

# --- post-edit gate [226] -> [227] (leg def keeps [226] via sentinel) ---
pair("""assert n1_t4.count(f'assert pf.N1_BANDS[227] == {{"a": ({fmt(pf_mod.N1_BANDS[226]["a"][0])}, {fmt(pf_mod.N1_BANDS[226]["a"][1])}),') == 1""",
     """assert n1_t4.count(f'assert pf.N1_BANDS[227] == {{"a": ({fmt(pf_mod.N1_BANDS[227]["a"][0])}, {fmt(pf_mod.N1_BANDS[227]["a"][1])}),') == 1""")

# --- w224_leg def -> w227_leg def (drop oldest leg, add newest; content [227]) ---
pair("""w224_leg = [
 f'        assert pf.N1_BANDS[224] == {{"a": ({fmt(pf_mod.N1_BANDS[224]["a"][0])}, {fmt(pf_mod.N1_BANDS[224]["a"][1])}),',
 f'                                    "b_exit": ({fmt(pf_mod.N1_BANDS[224]["b_exit"][0])}, {fmt(pf_mod.N1_BANDS[224]["b_exit"][1])}),',
'                                    "engine_owner": "bm-c"}, \\\\',
'            "registered W224 row parity drift (r307; bm-c five-face freeze; own-seat face disclosed)"',
]""",
"""w227_leg = [
 f'        assert pf.N1_BANDS[227] == {{"a": ({fmt(pf_mod.N1_BANDS[227]["a"][0])}, {fmt(pf_mod.N1_BANDS[227]["a"][1])}),',
 f'                                    "b_exit": ({fmt(pf_mod.N1_BANDS[227]["b_exit"][0])}, {fmt(pf_mod.N1_BANDS[227]["b_exit"][1])}),',
'                                    "engine_owner": "bm-c"}, \\\\',
'            "registered W227 row parity drift (r307; bm-c five-face freeze; own-seat face disclosed)"',
]""")

# --- receipt upstream + transitive block ---
pair('''  "w226_upstream": {"freeze_sha": w226_freeze_sha, "prereg_sha": w226_prereg_sha,
                    "ledger_total": w226_total, "merged_n": w226_merged_n,
                    "engine_owner": "bm-c (own seat honored, no takeover face)",
                    "repair_chain_note": "r943 splice (W226 freeze landed 9b44d37d1 dead window, estate absorbed r945 bd50be730) + engine self-burn 12/12 + r943 finalize one-pass 22:4x (six-gate POST-FINALIZE heal W212-pattern #3 disclosed -- THIS W227 cycle runs PRE-FINALIZE standing law, honest note)"},''',
'''  "w227_upstream": {"freeze_sha": w227_freeze_sha, "prereg_sha": w227_prereg_sha,
                    "ledger_total": w227_total, "merged_n": w227_merged_n,
                    "engine_owner": "bm-c (own seat honored, no takeover face)",
                    "repair_chain_note": "r956 splice (W227 freeze landed 48c321706 dead window, estate absorbed by r956-absorb 1e5ed3326) + engine self-burn 12/12 + r956 finalize one-pass 06:5x (six-gate PRE-FINALIZE correct phase -- standing law held)"},''')

pair('''  "w222_transitive": {"finalize_product": "results/perpetual_faces/n1_w222_results.json present (belt-and-braces gate; ledger 912,189 / K=486,320)"},''',
'''  "w226_transitive": {"finalize_product": "results/perpetual_faces/n1_w226_results.json present (belt-and-braces gate; ledger 920,989 / K=495,120)"},''')

# --- receipt prereg_bundle note ---
pair('"note": "prereg derived+committed in the r956 window (0d0c63c6e, ELEVEN-level lineage replay chain, preflight 46/46); splice editor derived from the committed W226 editor template by count-asserted ordered transform (protect-restore regions, fail-closed pair law) in this same r956 freeze window; upstream W226 already landed (clean-precondition sixteenth consecutive window); zero transcription"',
     '"note": "prereg derived+committed in the r958 window (e6c8441aa, TWELVE-level lineage replay chain, preflight 46/46); splice editor derived from the committed W227 editor template by count-asserted ordered transform (protect-restore regions, fail-closed pair law) in this same r959 freeze window; upstream W227 already landed (clean-precondition seventeenth consecutive window); zero transcription"')

# --- receipt parity + family6 notes ---
pair("full-span estate W138..W206 (69 rows, r858 absorb generation) + W211..W223 legs + W224 leg + W225 leg + W226 leg -> W227 block = 85 rows ending at W226;",
     "full-span estate W138..W206 (69 rows, r858 absorb generation) + W211..W224 legs + W225 leg + W226 leg + W227 leg -> W228 block = 86 rows ending at W227;")

pair('"note": "W226 editor family-6 gate carried forward: new block LHS w<227 x3 / RHS range(16,227)+range(17,227) / comment below-227 count-asserted ATOMICALLY before splice; W226 block\'s own w<226 face = legitimate prior-wave boundary (not stale)"',
     '"note": "W227 editor family-6 gate carried forward: new block LHS w<228 x3 / RHS range(16,228)+range(17,228) / comment below-228 count-asserted ATOMICALLY before splice; W227 block\'s own w<227 face = legitimate prior-wave boundary (not stale)"')

# --- receipt ordinal faces ---
pair('''                    "probe_receipt_bmc_ordinal_face": 57,
                    "note": "post-W227 registration: bm-c rows 56 + candidate = 57th owned (live derive at freeze time governs per r587/r359; probe leg0 bmc_ordinal=57 = r955 seat-time live face -- disclosed honest)"},''',
'''                    "probe_receipt_bmc_ordinal_face": 58,
                    "note": "post-W228 registration: bm-c rows 57 + candidate = 58th owned (live derive at freeze time governs per r587/r359; probe leg0 bmc_ordinal=58 = r957 seat-time live face -- disclosed honest)"},''')

# ---------------- phase 3: sentinel restores (with W228 additions) ----------------
rep("@@KEPT@@", KEPT_ORIG + "\nassert n1_t4.count('    # --- W227 materializer face') == 1  # prior block kept (W227 splice landed r956 dead window, estate absorbed by r956-absorb 1e5ed3326)", 1)
rep("@@LIVE@@", LIVE_ORIG.replace('"w226_block_kept": 1},', '"w226_block_kept": 1, "w227_block_kept": 1},'), 1)
rep("@@LEG226@@", LEG226_ORIG, 1)
rep("@@ASM@@", "block = EOL.join(hdr) + EOL + par_sec + EOL.join(w225_leg) + EOL + EOL.join(w226_leg) + EOL + EOL.join(w227_leg) + EOL + EOL.join(tail) + EOL", 1)

# ---------------- phase 4: validation (fail-closed) ----------------
stale = ["(514_204, 516_203)", "(516_204, 516_403)", "9b44d37d1", "bd50be730", "0d0c63c6e",
 "MSG-20261012-2040", "MSG-20261013-0645-bmc.md", "10781c2f8", "ELEVEN-level",
 "r943 22:4x", "r943 splice", "r943 freeze-window editor", "r943 finalize one-pass",
 "expect 216/56", "precedent 215/55", "splice 216/56", "== 216 and len", "rows 216 + candidate",
 "rows 56 + candidate", "bmc_ordinal=57", "57th", "fifty-seventh",
 "EIGHTY-SEVENTH instance", "EIGHTY-NINTH instance, E36 card",
 "TWO HUNDRED AND TWENTY-SEVENTH", "920_989", "495_120", "(expect 920,989",
 "r955 window", "r955 probe leg0", "r955 seat-time", "r956 freeze window", "r956 freeze-window bundle",
 "r956 window", "r956 prereg derived", "sixteenth consecutive",
 "_w227bmc_20261012_probe_receipt.json", "_w227bmc_freeze_receipt.json",
 "w224_leg", "n1w227-", "N1_BANDS.get(226)", "if w < 226", "w<226 leaked", "w<227 count",
 "range(16, 227)", "range(17, 227)", "below 227 composes", "m224", "_c226", "n3r1_used227",
 "arith_a227", "arith_b227", "WAVE_CONFIGS[226]", "N1_BANDS\\[224\\]",
 "W228+ projection", "naive W228 A window", "W228 freezer", "W228+ freezer",
 "downstream W228 seat", "(85 rows", "the 82-row cut", '== 82 \\', '== 84, \\',
 "!= 84 (69 estate", "own W224 leg (1 row)", "upstream W224 row leg",
 "rows 57 + candidate = 58th owned (live derive at freeze time governs per r587/r359; probe leg0 bmc_ordinal=58 = r955",
 "@@KEPT@@", "@@LIVE@@", "@@LEG226@@", "@@ASM@@", "e6c8441aa" + "x-guard", "227: {\"batch\": \"PERPETUAL-N1-W227\""]
for s in stale:
    c = t.count(s)
    assert c == 0, f"STALE TOKEN {s!r} count {c} != 0"

must_one = ["_set_wave(228)",
 "f'{CFG_I}228: ", "f'{ROW_I}228: ", "ROW_I + '228: {\"a\"'", '"wave": 228',
 'MSG-20261013-0720-bmc.md', "4e30ddf69", "923_189", "497_320",
 "(expect 923,189 / 497,320)", "(516_404, 518_403)", "(518_404, 518_603)",
 "int(_estate_ws[82]) == 224", "e6c8441aa", "TWELVE-level",
 '"probe_receipt_bmc_ordinal_face": 58,', '"w227_block_kept": 1}',
 "N1_BANDS.get(227)", "r957 probe leg0", "r957 seat-time live face",
 "r958 prereg derived", "83-row cut", '== 83 \\', '== 85, \\',
 "n1w228-0of12", "n1w228-11of12", "seat MSG-1228 tail"]
for s in must_one:
    c = t.count(s)
    assert c == 1, f"MUST-ONE {s!r} count {c} != 1"

assert t.count("MSG-20261013-0720-bmc") == 4
assert t.count('228: {"batch": "PERPETUAL-N1-W228"') == 2   # new_cfg gate + n1_t4 post-edit gate
assert t.count("MSG-20261013-0645-bmc") == 2          # upstream seat references
assert t.count("W229+ projection") == 2
assert t.count("naive W229 A window") == 2
assert t.count("EIGHTY-NINTH instance anticipated") == 2
assert t.count("EIGHTY-EIGHTH instance") == 5
assert t.count("TWO HUNDRED AND TWENTY-EIGHTH") == 3
assert t.count("fifty-eighth") == 2
assert t.count("58th") == 6
assert t.count("58th own wave") == 2
assert t.count("bmc_ordinal=58") == 3
assert t.count("_w228bmc_20261013_probe_receipt.json") == 9
assert t.count("_w228bmc_freeze_receipt.json") == 1
assert t.count("w225_leg") == 2
assert t.count("w226_leg") == 2
assert t.count("w227_leg") == 2
assert t.count('"w226_transitive"') == 1
assert t.count('"w225_transitive"') == 1
assert t.count('"w227_upstream"') == 2
assert t.count("assert pf.N1_BANDS[227] ==") == 2     # w227_leg def + post-edit gate
assert t.count("assert pf.N1_BANDS[226] ==") == 1     # w226_leg def (sentinel-kept)
assert t.count("W226") == 11                          # legit upstream/kept faces (P7 x3, s72, P10, P11, P24e, LEG226, KEPT x2, P19)
assert t.count("w226_") == 8                          # leg def+asm x2, out_path x2, live, transitive, n1_w226_results x2
assert t.count("WAVE_CONFIGS[228]") == 2             # band-facts self asserts
assert t.count("WAVE_CONFIGS[227]") == 3             # upstream mirror asserts
assert t.count("w226_out_path") == 2
assert t.count("r943") == 1                           # KEPT kept-comment only
assert t.count("r945") == 1                           # KEPT kept-comment only
assert t.count("w227_a_tail") == 14
assert t.count("w227_b_tail") == 9
assert t.count("w227_freeze_sha") == 6
assert t.count("w227_prereg_sha") == 3
assert t.count("w228_prereg_sha") == 5
assert t.count("w228_receipt_sha") == 4
assert t.count("n1_w228") == 5
assert t.count("48c321706") == 1                     # receipt repair note (P17; shift-63 occurrence consumed by the same pair)
assert t.count("1e5ed3326") >= 6
assert t.count("r956 06:5x") == 3
assert t.count("r959 freeze window") == 4
assert t.count("r959 freeze-window bundle") == 2
assert t.count("seventeenth consecutive") == 2
assert t.count("n1_w226_results.json") == 2
assert t.count("n1_w227_results") == 4                # upstream refs
assert t.count("86 rows") == 2
assert t.count("if w < 228)") == 5
assert t.count("range(16, 228)") == 2
assert t.count("range(17, 228)") == 3
assert t.count("registered wave below 228 composes") == 2
assert t.count("07:20") == 0 and t.count("0645-bmc.md") == 0

open(OUT, "w", encoding="utf-8", newline="").write(t)
py_compile.compile(OUT, doraise=True)
print(f"DERIVE OK: {OUT} ({len(t)} chars, template 48037); py_compile green")
print("NEXT: run the editor (gates fail-closed) -> pf/n1 selftest -> pathspec commit+push -> PRE-FINALIZE six-gate -> engine self-burn verify")
