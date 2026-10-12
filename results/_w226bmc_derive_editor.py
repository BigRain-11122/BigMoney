# -*- coding: utf-8 -*-
# r942 bm-c derive: W225 -> W226 five-face freeze editor (count-asserted ordered
# transform; fail-closed pair law; protect-restore sentinels for fixed-estate faces).
# Template = committed _w225bmc_freeze_edits.py (84ecb3a3a generation, proven
# live-fire). All wave facts shift by token; every machine-derivable fact is
# re-asserted at editor RUNTIME against live git/pf/receipt data (fail-closed).
# Census evidence = _r942bmc_editor_census.py run this window (counts in hand).
import os, sys, py_compile

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.join(HERE, "_w225bmc_freeze_edits.py")
OUT  = os.path.join(HERE, "_w226bmc_freeze_edits.py")

t = open(BASE, "r", encoding="utf-8", newline="").read()
assert len(t) == 46422, f"template length drift: {len(t)} != 46422"

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
assert n1_t4.count('    # --- W224 materializer face') == 1  # prior block kept (W224 splice landed r937 dead window)"""
rep(KEPT_ORIG, "@@KEPT@@", 1)

LIVE_ORIG = '''  "liveness_anchors": {"t141_marker_kept": 1, "w209_block_kept": 1, "w210_block_kept": 1, "w211_block_kept": 1, "w212_block_kept": 1, "w213_block_kept": 1, "w214_block_kept": 1, "w215_block_kept": 1, "w216_block_kept": 1, "w217_block_kept": 1, "w218_block_kept": 1, "w219_block_kept": 1, "w220_block_kept": 1, "w221_block_kept": 1, "w222_block_kept": 1, "w223_block_kept": 1, "w224_block_kept": 1},'''
rep(LIVE_ORIG, "@@LIVE@@", 1)

# ---------------- phase 1: ordered global shifts (descending, count-logged) ----------------
SHIFTS = [
 ("W226", "W227", 7),
 ("W225", "W226", 74),
 ("W224", "W225", 107),   # census 109 minus 2 inside @@KEPT@@ sentinel
 ("W223", "W224", 11),    # census 13 minus 2 inside @@KEPT@@ sentinel
 ("n1_w225", "n1_w226", 5),           # runs BEFORE w225_/w224_ var shifts (substring overlap law)
 ("n1w225", "n1w226", 2),
 ("n1_w224_results", "n1_w225_results", 4),
 ("n1_w223_results", "n1_w224_results", 2),
 ("n1_w222_results", "n1_w223_results", 2),
 ("n1_w221_results", "n1_w222_results", 2),
 ("n1_w220_results", "n1_w221_results", 2),
 ("w225_", "w226_", 13),  # census 11 minus 2 (inside n1_w225_results, consumed above) plus 4 recreated by the n1_w224_results shift
 ("w224_", "w225_", 94),  # census 97 minus 4 (n1_w224_results) minus 1 (@@LIVE@@ sentinel) plus 2 recreated by the n1_w223_results shift (r942 fix: dead-window slip, w225_ row had the analogous +4)
 ("w223_leg", "w224_leg", 2),
 ("w223_out_path", "w224_out_path", 2),
 ("w222_out_path", "w223_out_path", 2),
 ("w221_out_path", "w222_out_path", 2),
 ("w220_out_path", "w221_out_path", 2),
 ("WAVE_CONFIGS[225]", "WAVE_CONFIGS[226]", 2),
 ("WAVE_CONFIGS[224]", "WAVE_CONFIGS[225]", 3),
 ("N1_BANDS[224]", "N1_BANDS[225]", 11),
 ("N1_BANDS[223]", "N1_BANDS[224]", 5),
 ("N1_BANDS\\[223\\]", "N1_BANDS\\[224\\]", 1),
 ("m223", "m224", 3),
 ("_c224", "_c225", 5),
 ("arith_a225", "arith_a226", 3),
 ("arith_b225", "arith_b226", 3),
 ("n3r1_used225", "n3r1_used226", 3),
 ("'224: {\"batch\"'", "'225: {\"batch\"'", 2),
 ("'224: {\"a\"'", "'225: {\"a\"'", 2),
 ("'    224: {\"a\"'", "'    225: {\"a\"'", 1),
 ("PERPETUAL-N1-W225", "PERPETUAL-N1-W226", 7),
 ("PERPETUAL_N1_W225_PREREG", "PERPETUAL_N1_W226_PREREG", 5),
 ("PERPETUAL_N1_W224_PREREG", "PERPETUAL_N1_W225_PREREG", 3),
 ("EIGHTY-SIXTH instance anticipated", "EIGHTY-SEVENTH instance anticipated", 2),
 ("EIGHTY-FIFTH", "EIGHTY-SIXTH", 7),
 ("TWO HUNDRED AND TWENTY-FIFTH", "TWO HUNDRED AND TWENTY-SIXTH", 3),
 ("fifty-fifth", "fifty-sixth", 2),
 ("MSG-20261012-1943-bmc-w225-seat", "MSG-20261012-2040-bmc-w226-seat", 4),
 ("MSG-20261012-175x", "MSG-20261012-1943-bmc-w225-seat", 2),
 ("r938 window", "r940 window", 2),
 ("_w225bmc_20261012_probe_receipt.json", "_w226bmc_20261012_probe_receipt.json", 9),
 ("_w225bmc_freeze_receipt.json", "_w226bmc_freeze_receipt.json", 1),
 ("916_589", "918_789", 1),
 ("490_720", "492_920", 1),
 ("(expect 916,589 / 490,720)", "(expect 918,789 / 492,920)", 1),
 ("(509_804, 511_803)", "(512_004, 514_003)", 1),
 ("(511_804, 512_003)", "(514_004, 514_203)", 1),
 ("c78dd1a44", "d7d270752", 1),
 ("N1_BANDS.get(224)", "N1_BANDS.get(225)", 1),
 ("_set_wave(225)", "_set_wave(226)", 1),
 ("if w < 225)", "if w < 226)", 5),
 ("if w < 224", "if w < 225", 1),
 ("range(16, 225)", "range(16, 226)", 2),
 ("range(17, 225)", "range(17, 226)", 3),
 ("registered wave below 225 composes", "registered wave below 226 composes", 2),
 ("seat MSG-1225 tail", "seat MSG-1226 tail", 1),
 ('"wave": 225,', '"wave": 226,', 1),
 ("55th own wave", "56th own wave", 2),
 ("55th owned", "56th owned", 1),
 ("= 55th EXACT)", "= 56th EXACT)", 1),
 ("bmc_ordinal=55", "bmc_ordinal=56", 3),
 ("== 214 and len(bmc_rows_live) == 54", "== 215 and len(bmc_rows_live) == 55", 1),
 ("expect 214/54", "expect 215/55", 1),
 ("precedent 213/53 pre-splice", "precedent 214/54 pre-splice", 1),
 ("splice 214/54", "splice 215/55", 1),
 ("rows 54 + candidate", "rows 55 + candidate", 4),
 ("rows 214 + candidate", "rows 215 + candidate", 1),
 ("r939 freeze window", "r942 freeze window", 3),
 ("fourteenth consecutive", "fifteenth consecutive", 2),
 ("== 81 \\", "== 82 \\", 1),
 ("!= 82 (69 estate + W211..W221 legs + W222 leg + W224 leg)",
  "!= 83 (69 estate + W211..W221 legs + W222 leg + W223 leg + W224 leg)", 1),
 ("and int(_estate_ws[80]) == 222, \\",
  "and int(_estate_ws[80]) == 222 and int(_estate_ws[81]) == 223, \\", 1),
 ("legs + W222 leg: n=", "legs + W222 leg + W223 leg: n=", 1),
 ("== 82,", "== 83,", 1),
 ("(83 rows: estate 69", "(84 rows: estate 69", 1),
 ("+ W222 leg + W224 leg + W225 leg).", "+ W222 leg + W223 leg + W224 leg + W225 leg).", 1),
 ("own W222 leg)", "own W223 leg)", 1),
 ("(r937 dead-window editor landed by r937 absorb), structure known",
  "(r939 window editor), structure known", 1),
]
def shift_text(s):
    for old, new, _ in SHIFTS:
        s = s.replace(old, new)
    return s
for old, new, mn in SHIFTS:
    c = t.count(old)
    assert c == mn, f"SHIFT FAIL count {c} != {mn}: {old!r}"
    t = t.replace(old, new)
    print(f"  shift {mn:3d}x {old[:60]!r}")

# ---------------- phase 2: pairs (shift-derived anchors, final new text) ----------------
def pair(orig_old, new, n=1):
    global t
    old = shift_text(orig_old)
    c = t.count(old)
    assert c == n, f"PAIR FAIL count {c} != {n}: {old[:110]!r}"
    t = t.replace(old, new)

# --- header blocks ---
pair("""# 2026-10-12 20:2x bm-c r939 freeze window (upstream W1..W224 ALL LANDED, clean precondition): W225 five-face freeze splice editor.
# Upstream chain ALL LANDED at this window: W1..W224 finalize products
# present (W224 finalize one-pass 19:1x, net chain head 916,589,
# merged pool K=490,720, n1_w224_results.json machine-read) -- ZERO
# in-flight upstream seats, clean precondition (fourteenth consecutive
# fully-clean freeze window).""",
"""# 2026-10-12 21:2x bm-c r942 freeze window (upstream W1..W225 ALL LANDED, clean precondition): W226 five-face freeze splice editor.
# Upstream chain ALL LANDED at this window: W1..W225 finalize products
# present (W225 finalize one-pass 20:3x, net chain head 918,789,
# merged pool K=492,920, n1_w225_results.json machine-read) -- ZERO
# in-flight upstream seats, clean precondition (fifteenth consecutive
# fully-clean freeze window).""")

pair("""# Lineage: _w224bmc_freeze_edits.py pattern (proven live-fire freeze,
# r937 dead-window splice landed by r937 absorb) + r787 preflight law +""",
"""# Lineage: _w225bmc_freeze_edits.py pattern (proven live-fire freeze,
# r939 window executed) + r787 preflight law +""")

pair("""# LHS/RHS/comment ATOMIC TRIPLE absorbed (W225 editor derive review leg
# per the W224 sec.8 upgrade proposal -- the new block's w<N+1>/range(16,N+1)
# /below-N+1 triple is count-asserted atomically; W223 block's own w<223
# face is legitimate prior-wave boundary, not stale).""",
"""# LHS/RHS/comment ATOMIC TRIPLE absorbed (W226 editor derive review leg
# carried from the W224 sec.8 upgrade proposal -- the new block's w<N+1>/range(16,N+1)
# /below-N+1 triple is count-asserted atomically; W225 block's own w<225
# face is legitimate prior-wave boundary, not stale).""")

# gate 0.5 comment block (transitive window slides W224/W223/W222/W221)
pair("""# ---------- gate 0.5: W224 five-face landed + W224 finalize product present ----------
# (chain-order precondition; W223/W222/W221/W220 finalize are transitive deps of the
# W225 freeze and are belt-and-braces checked here + enforced by the block's
# cumulative-deps assert range(17, 225) at selftest time)""",
"""# ---------- gate 0.5: W225 five-face landed + W225 finalize product present ----------
# (chain-order precondition; W224/W223/W222/W221 finalize are transitive deps of the
# W226 freeze and are belt-and-braces checked here + enforced by the block's
# cumulative-deps assert range(17, 226) at selftest time)""")

# --- seat/prose fixups (post-shift anchors = shift_text of originals) ---
pair("MSG-20261012-1943-bmc-w225-seat, executed bm-c r935 seat window; engine self-burn 12/12",
     "MSG-20261012-1943-bmc-w225-seat, executed bm-c r939 window; engine self-burn 12/12", 1)
pair("MSG-20261012-1943-bmc-w225-seat, executed bm-c r937 dead-window splice landed by r937 absorb; engine self-burn 12/12; finalize one-pass 19:1x",
     "MSG-20261012-1943-bmc-w225-seat, executed bm-c r939 window splice; engine self-burn 12/12; finalize one-pass 20:3x r940 window (estate absorbed by r941)", 1)
pair('"    #     + finalize one-pass 19:1x dead-window splice estate + PRE-FINALIZE six-gate all-green chain, honest note)",',
     '"    #     + finalize one-pass 20:3x r940 window (estate absorbed by r941) + PRE-FINALIZE six-gate all-green chain, honest note)",', 1)
pair(' "freeze splice script landed in the r939 freeze-window bundle ",',
     ' "per-wave prereg landed in the r941 window; freeze splice script in this ",', 1)
pair('"    #     freeze splice script landed in the r939 freeze-window bundle",',
     '"    #     freeze splice script landed in the r942 freeze-window bundle",', 1)
pair('"    # r939 prereg derived + freeze-window bundle, probe",',
     '"    # r941 prereg derived + landed pre-freeze, probe",', 1)
pair("prereg derived+committed in the r939 window",
     "prereg derived+committed in the r941 window", 1)
pair("4b22941a7, NINE-level lineage replay chain",
     "f65d886cb, TEN-level lineage replay chain", 1)
pair("r938 seat-time live face", "r940 seat-time live face", 1)
pair('"probe_receipt_bmc_ordinal_face": 55,', '"probe_receipt_bmc_ordinal_face": 56,', 1)

# --- receipt upstream + transitive block (wholesale) ---
pair('''  "w224_upstream": {"freeze_sha": w224_freeze_sha, "prereg_sha": w224_prereg_sha,
                    "ledger_total": w224_total, "merged_n": w224_merged_n,
                    "engine_owner": "bm-c (own seat honored, no takeover face)",
                    "repair_chain_note": "r937 splice (dead-window estate, landed by r937 absorb commit) + engine self-burn 12/12 + r937 finalize one-pass 19:1x (six-gate PRE-FINALIZE all-green 19:1x, correct-phase post-miss run 2)"},
  "w223_transitive": {"finalize_product": "results/perpetual_faces/n1_w223_results.json present (belt-and-braces gate; ledger 914,389 / K=488,520)"},
  "w222_transitive": {"finalize_product": "results/perpetual_faces/n1_w222_results.json present (belt-and-braces gate; ledger 912,189 / K=486,320)"},
  "w221_transitive": {"finalize_product": "results/perpetual_faces/n1_w221_results.json present (belt-and-braces gate; ledger 909,989 / K=484,120)"},
  "w220_transitive": {"finalize_product": "results/perpetual_faces/n1_w220_results.json present (belt-and-braces gate; ledger 907,789 / K=481,920)"},''',
'''  "w225_upstream": {"freeze_sha": w225_freeze_sha, "prereg_sha": w225_prereg_sha,
                    "ledger_total": w225_total, "merged_n": w225_merged_n,
                    "engine_owner": "bm-c (own seat honored, no takeover face)",
                    "repair_chain_note": "r939 splice + engine self-burn 12/12 + r940 finalize one-pass 20:3x (six-gate PRE-FINALIZE all-green, correct-phase run 3 consecutive; r940 estate absorbed by r941)"},
  "w224_transitive": {"finalize_product": "results/perpetual_faces/n1_w224_results.json present (belt-and-braces gate; ledger 916,589 / K=490,720)"},
  "w223_transitive": {"finalize_product": "results/perpetual_faces/n1_w223_results.json present (belt-and-braces gate; ledger 914,389 / K=488,520)"},
  "w222_transitive": {"finalize_product": "results/perpetual_faces/n1_w222_results.json present (belt-and-braces gate; ledger 912,189 / K=486,320)"},
  "w221_transitive": {"finalize_product": "results/perpetual_faces/n1_w221_results.json present (belt-and-braces gate; ledger 909,989 / K=484,120)"},''')

# --- receipt parity + family6 note fixups ---
pair("full-span estate W138..W206 (69 rows, r858 absorb generation) + W211..W221 legs + W222 leg -> W225 block = 83 rows ending at W224;",
     "full-span estate W138..W206 (69 rows, r858 absorb generation) + W211..W221 legs + W222 leg + W223 leg -> W226 block = 84 rows ending at W225;", 1)
pair('"note": "W225 sec.8 upgrade proposal absorbed into the W226 editor derive: new block LHS w<225 x3 / RHS range(16,225)+range(17,225) / comment below-225 count-asserted ATOMICALLY before splice; W224 block\'s own w<224 face = legitimate prior-wave boundary (not stale)"',
     '"note": "W224 sec.8 upgrade proposal carried through the W225/W226 editor derives: new block LHS w<226 x3 / RHS range(16,226)+range(17,226) / comment below-226 count-asserted ATOMICALLY before splice; W225 block\'s own w<225 face = legitimate prior-wave boundary (not stale)"', 1)

# --- small config-row pairs (count-asserted, post-shift unique) ---
pair("f'{CFG_I}225: ", "f'{CFG_I}226: ", 1)
pair("count('225: {\"batch\": \"PERPETUAL-N1-W225\"')", "count('226: {\"batch\": \"PERPETUAL-N1-W226\"')", 1)
pair("f'{ROW_I}225: ", "f'{ROW_I}226: ", 1)
pair("f'225: {{\"a\": ({fmt(a_lo)}, {fmt(a_hi)}), \"b_exit\": ({fmt(b_lo)}, {fmt(b_hi)}),'",
     "f'226: {{\"a\": ({fmt(a_lo)}, {fmt(a_hi)}), \"b_exit\": ({fmt(b_lo)}, {fmt(b_hi)}),'", 1)
pair("ROW_I + '225: {\"a\"'", "ROW_I + '226: {\"a\"'", 1)
pair("wave 225 = first free number after the", "wave 226 = first free number after the", 1)
pair("wave 225: ", "wave 226: ", 1)

# ---------------- phase 3: sentinel restores (with W225 additions) ----------------
rep("@@KEPT@@", KEPT_ORIG + "\nassert n1_t4.count('    # --- W225 materializer face') == 1  # prior block kept (W225 splice landed r939 window)", 1)
rep("@@LIVE@@", LIVE_ORIG.replace('"w224_block_kept": 1},', '"w224_block_kept": 1, "w225_block_kept": 1},'), 1)

# ---------------- phase 4: validation (fail-closed) ----------------
stale = ["509_804", "511_803", "511_804, 512_003", "c78dd1a44", "MSG-20261012-1943-bmc-w225-seat",
 "MSG-20261012-175x", "19:1x", "r935 ", "213/53", "bmc_ordinal=55", "EIGHTY-FIFTH",
 "EIGHTY-SIXTH instance anticipated", "TWO HUNDRED AND TWENTY-FIFTH", "fifty-fifth",
 "916_589", "490_720", "(expect 916,589", "== 81 \\", "== 214 and len", "expect 214/54",
 "55th own wave", "55th owned", "55th EXACT", "r937", "r938 ", "r939 freeze-window bundle",
 "r939 freeze window", "fourteenth", "w223_leg", "w223_out_path", "m223", "_c224",
 "n3r1_used225", "arith_a225", "arith_b225", "WAVE_CONFIGS[224]", "PERPETUAL-N1-W225",
 "n1w225", "W225 (bm-c loop", "wave 225 ", "wave 225=", '"wave": 225', "if w < 224",
 "range(16, 225)", "range(17, 225)", "below 225 composes", "MSG-1225", "N1_BANDS.get(224)",
 "N1_BANDS\\[223\\]", "W225p_", "rows 214 + candidate", "rows 54 + candidate",
 "precedent 213", "own W222 leg)", "(83 rows", "== 82 (69 estate", '== 82,',
 "@@KEPT@@", "@@LIVE@@", "W225 seat MSG", "w225_prereg_sha", "w225_receipt_sha"]
for s in stale:
    c = t.count(s)
    assert c == 0, f"STALE TOKEN {s!r} count {c} != 0"

must_one = ["_set_wave(226)", '226: {"batch": "PERPETUAL-N1-W226"',
 "f'{CFG_I}226: ", "f'{ROW_I}226: ", "ROW_I + '226: {\"a\"'", '"wave": 226',
 'MSG-20261012-2040-bmc-w226-seat.md', "d7d270752", "918_789", "492_920",
 "(512_004, 514_003)", "(514_004, 514_203)", "int(_estate_ws[81]) == 223",
 "f65d886cb", "TEN-level lineage replay chain", "r941 window",
 '"probe_receipt_bmc_ordinal_face": 56,', "w225_block_kept\": 1}",
 "assert pf.N1_BANDS[225] ==", "assert pf.N1_BANDS[224] ==",
 "N1_BANDS.get(225)", "r940 seat-time live face"]
for s in must_one:
    c = t.count(s)
    assert c == 1, f" MUST-ONE {s!r} count {c} != 1"
assert t.count("MSG-20261012-2040-bmc-w226-seat") == 4
assert t.count("EIGHTY-SEVENTH instance anticipated") == 2
assert t.count("EIGHTY-SIXTH instance, E36 card") >= 3
assert t.count("TWO HUNDRED AND TWENTY-SIXTH") == 3
assert t.count("fifty-sixth") == 2
assert t.count("if w < 226)") == 5
assert t.count('if w < 225"') == 1
assert t.count("range(16, 226)") == 2
assert t.count("range(17, 226)") == 3
assert t.count("84 rows") == 2
assert t.count("r942 freeze window") == 3
assert t.count("r942 freeze-window bundle") == 1
assert t.count("_w226bmc_20261012_probe_receipt.json") == 9
assert t.count("_w226bmc_freeze_receipt.json") == 1
assert t.count("n1_w226") >= 4
assert t.count("w224_leg") == 2
assert t.count("w225_leg") == 2
assert t.count("w225_freeze_sha") >= 5
assert t.count("w226_prereg_sha") >= 4
assert t.count('"w225_upstream"') == 2
assert t.count('"w224_transitive"') == 1
assert t.count("20:3x") == 2

open(OUT, "w", encoding="utf-8", newline="").write(t)
py_compile.compile(OUT, doraise=True)
print(f"DERIVE OK: {OUT} ({len(t)} bytes, template {46422}); py_compile green")
print("NEXT: run the editor (gates fail-closed) -> pf/n1 selftest -> pathspec commit+push -> engine self-burn verify")
