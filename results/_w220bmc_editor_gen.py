# -*- coding: utf-8 -*-
# W220 freeze editor generator (bm-c r923, 2026-10-12 11:3x).
# ABSORB note: this window lands the W220 freeze splice for the r922 dead
# session's estate (prereg derive 10:39-11:03, zero commits). Own r-window
# tokens age +3 (r920 freeze -> r923 freeze) because slot r922 died
# pre-splice; every other face ages one wave exactly as the r920 gen did.
# Method: machine transform of the committed W219 editor
# (results/_w219bmc_freeze_edits.py, r920 proven live-fire generation)
# into results/_w220bmc_freeze_edits.py via
#   (0) LIV masks (W209..W218 heritage liveness lines, 10 lines);
#   (1) ordered BLANKETS with before/after count verification
#       (own 219->220 first, then aging cascade 218->219 / 217->218 /
#       216->217 / 215->216; own r-window shifts BEFORE upstream r-window
#       shifts, keeping the r920-gen ordering discipline),
#   (2) count==1 EXPLICIT replacements for every context-sensitive literal,
#   (3) unmask + structural addition (W219 liveness line),
#   (4) final sanity + py_compile before this script exits.
import sys, py_compile

sys.stdout.reconfigure(encoding="utf-8")
SRC = r"results\_w219bmc_freeze_edits.py"
DST = r"results\_w220bmc_freeze_edits.py"
t = open(SRC, encoding="utf-8").read()
orig_len = len(t)

def rep1(s, find, repl, what):
    c = s.count(find)
    assert c == 1, f"[{what}] count {c} != 1: {find[:70]}..."
    return s.replace(find, repl, 1)

def repn(s, find, repl, expect, what):
    c = s.count(find)
    assert c == expect, f"[{what}] count {c} != {expect}: {find[:70]}..."
    return s.replace(find, repl)

# ---------------- (0) masks: heritage liveness gates (10 lines) ----------------
LIV = [
 "assert n1_t4.count('    # --- W209 materializer face') == 1  # estate source block kept",
 "assert n1_t4.count('    # --- W210 materializer face') == 1  # prior block kept",
 "assert n1_t4.count('    # --- W211 materializer face') == 1  # prior block kept",
 "assert n1_t4.count('    # --- W212 materializer face') == 1  # prior block kept",
 "assert n1_t4.count('    # --- W213 materializer face') == 1  # prior block kept",
 "assert n1_t4.count('    # --- W214 materializer face') == 1  # prior block kept (W214 splice landed r910 window)",
 "assert n1_t4.count('    # --- W215 materializer face') == 1  # prior block kept (W215 splice landed r912 window)",
 "assert n1_t4.count('    # --- W216 materializer face') == 1  # prior block kept (W216 splice landed r914 window)",
 "assert n1_t4.count('    # --- W217 materializer face') == 1  # prior block kept (W217 splice landed r916 window)",
 "assert n1_t4.count('    # --- W218 materializer face') == 1  # prior block kept (W218 splice landed r918 window)",
]
for i, line in enumerate(LIV):
    t = rep1(t, line, f"@LIV{i}@", f"mask{i}")

# ---------------- (1) blankets (ordered, count-verified) ----------------
def blanket(s, find, repl, what, min_count=1):
    c = s.count(find)
    assert c >= min_count, f"[{what}] blanket count {c} < {min_count}: {find}"
    print(f"  blanket {what}: {find!r} -> {repl!r} x{c}")
    return s.replace(find, repl)

# own bundle window FIRST (r920->r923: +3 absorb case, r922 died pre-splice),
# then own wave tokens, then upstream cascade LAST -- r920-gen discipline.
t = blanket(t, "r920 freeze", "r923 freeze", "own-bundle-window")
t = blanket(t, "W219", "W220", "W219->W220")
t = blanket(t, "w219_", "w220_", "w219var->w220var")
t = blanket(t, "_w219bmc", "_w220bmc", "w219bmc")
t = blanket(t, "n1_w219", "n1_w220", "n1_w219")
t = blanket(t, "n1w219", "n1w220", "n1w219")
t = blanket(t, "SEVENTY-NINTH", "EIGHTIETH", "staircase-ordinal")
t = blanket(t, "TWO HUNDRED AND NINETEENTH", "TWO HUNDRED AND TWENTIETH", "engine-ordinal-words")
t = blanket(t, "forty-ninth", "fiftieth", "bmc-ordinal-words")
t = blanket(t, "0916", "1025", "seat-msg-time")          # own seat stamp (W220 seat MSG-20261012-1025)
t = blanket(t, "0830", "0916", "upstream-seat-time")     # upstream seat stamp (W219 seat 0916)
t = blanket(t, "09:1x", "10:1x", "finalize-time")        # upstream finalize stamp (W219 finalize 10:1x)
t = blanket(t, "r917 seat", "r919 seat", "upstream-seat-r")
t = blanket(t, "r919 window", "r921 window", "own-payload-window")
t = blanket(t, "r919 finalize", "r921 finalize", "upstream-finalize-r")
t = blanket(t, "r918 freeze", "r920 freeze", "upstream-freeze-r")
t = blanket(t, "7615985e8", "13a81d182", "seat-origin")
t = blanket(t, "219", "220", "digit-219->220")
t = blanket(t, "W218", "W219", "W218->W219")
t = blanket(t, "w218_", "w219_", "w218var->w219var")
t = blanket(t, "218", "219", "digit-218->219")
t = blanket(t, "W217", "W218", "W217->W218")
t = blanket(t, "w217_", "w218_", "w217var->w218var")
t = blanket(t, "217", "218", "digit-217->218")   # BEFORE W215->W216 (its output must stay W216)
t = blanket(t, "W216", "W217", "W216->W217")
t = blanket(t, "w216_", "w217_", "w216var->w217var")
t = blanket(t, "216", "217", "digit-216->217")
t = blanket(t, "W215", "W216", "W215->W216")
t = blanket(t, "w215_", "w216_", "w215var->w216var")
t = blanket(t, "215", "216", "digit-215->216")
t = blanket(t, "w214_", "w215_", "w214var->w215var")
# NOTE: no digit 214->215 blanket (same as the r918/r920 gens: the estate list
# [211,212,213,214] + leg lists must keep their 214s verbatim; the w214_
# var blanket handles the code block var+file alignment).

# ---------------- (2) explicit replacements (count==1) ----------------
E = []
def E1(find, repl, what):
    E.append((find, repl, what))

E1("# 2026-10-12 09:5x bm-c r923 freeze: W220 five-face freeze splice editor.",
   "# 2026-10-12 11:4x bm-c r923 freeze (absorb r922 freeze-prep estate): W220 five-face freeze splice editor.", "hdr-line2")
E1("present (W219 finalize one-pass 10:1x, net chain head 903,389,",
   "present (W219 finalize one-pass 10:1x, net chain head 905,589,", "hdr-chain-head")
E1("merged pool K=477,520, n1_w219_results.json machine-read) -- ZERO\n# in-flight upstream seats, clean precondition (eighth consecutive",
   "merged pool K=479,720, n1_w219_results.json machine-read) -- ZERO\n# in-flight upstream seats, clean precondition (ninth consecutive", "hdr-pool-k")
E1("Lineage: _w219bmc_freeze_edits.py pattern (proven live-fire freeze,\n# r918 window executed)",
   "Lineage: _w219bmc_freeze_edits.py pattern (proven live-fire freeze,\n# r920 window executed)", "lineage")
E1("(r918 window editor)", "(r920 window editor)", "own-editor-window")
E1("(chain-order precondition; W218/W217/W216/W214 finalize are transitive deps of the\n# W220 freeze",
   "(chain-order precondition; W218/W217/W216/W215 finalize are transitive deps of the\n# W220 freeze", "gate05-comment")
E1("assert w219_total == 903_389 and w219_merged_n == 477_520",
   "assert w219_total == 905_589 and w219_merged_n == 479_720", "gate05-anchors")
E1("(expect 903,389 / 477,520)", "(expect 905,589 / 479,720)", "gate05-expect")
E1("assert len(owner_rows_live) == 208 and len(bmc_rows_live) == 48",
   "assert len(owner_rows_live) == 209 and len(bmc_rows_live) == 49", "live-ordinal")
E1("(expect 208/48 PRE-splice post-W220 registration; W220 precedent 207/47 pre-splice + W220 splice 208/48; this candidate = 49th own wave per the same live-derive law, r587/r359)",
   "(expect 209/49 PRE-splice post-W220 registration; W220 precedent 208/48 pre-splice + W220 splice 209/49; this candidate = 50th own wave per the same live-derive law, r587/r359)", "live-ordinal-msg")
E1('f"W219+W218+W217+W216+W214 finalize products present "',
   'f"W219+W218+W217+W216+W215 finalize products present "', "gate05-print-list")
E1("candidate (49th own wave per live derive r587/r359; ",
   "candidate (50th own wave per live derive r587/r359; ", "gate05-print-ordinal")
E1("probe receipt leg0 bmc_ordinal=49 seat",
   "probe receipt leg0 bmc_ordinal=50 seat", "gate05-print-probe")
E1("receipt leg0 face bmc_ordinal=48 = seat-time live face; live derive at freeze\n# time: bmc rows 47 + candidate = 48th EXACT)",
   "receipt leg0 face bmc_ordinal=49 = seat-time live face; live derive at freeze\n# time: bmc rows 48 + candidate = 49th EXACT)", "gate05-comment-heal")
E1("assert (a_lo, a_hi) == (496_604, 498_603) and (b_lo, b_hi) == (498_604, 498_803), \\",
   "assert (a_lo, a_hi) == (498_804, 500_803) and (b_lo, b_hi) == (500_804, 501_003), \\", "band-literals")
E1('def fmt(n):  # 496604 -> "496_604"', 'def fmt(n):  # 498804 -> "498_804"', "fmt-doc")
E1("(77 rows: estate 69 + W211 leg + W212 leg + W213 leg + W214 leg + W216 leg + W217 leg + W218 leg + W219 leg).",
   "(78 rows: estate 69 + W211 leg + W212 leg + W213 leg + W214 leg + W215 leg + W216 leg + W217 leg + W218 leg + W219 leg).", "structural-choice")
E1("Extraction self-asserts the 75-row cut (69 estate + W211 + W212 + W213 + W214 + W216 + W217)",
   "Extraction self-asserts the 76-row cut (69 estate + W211 + W212 + W213 + W214 + W215 + W216 + W217)", "extraction-cut")
E1("own W211 leg + own W212 leg +\n# own W213 leg + own W214 leg + own W216 leg + own W217 leg + own W218 leg)",
   "own W211 leg + own W212 leg +\n# own W213 leg + own W214 leg + own W215 leg + own W216 leg + own W217 leg + own W218 leg)", "extraction-comment-legs")
E1('and [int(_estate_ws[69]), int(_estate_ws[70]), int(_estate_ws[71]), int(_estate_ws[72]), int(_estate_ws[73]), int(_estate_ws[74])] == [211, 212, 213, 214, 216, 217], \\',
   'and [int(_estate_ws[69]), int(_estate_ws[70]), int(_estate_ws[71]), int(_estate_ws[72]), int(_estate_ws[73]), int(_estate_ws[74]), int(_estate_ws[75])] == [211, 212, 213, 214, 215, 216, 217], \\', "estate-ws")
E1('assert par_sec.count("assert pf.N1_BANDS[") == 75 \\',
   'assert par_sec.count("assert pf.N1_BANDS[") == 76 \\', "parsec-count")
E1('f"estate segment not W138..W206 full-span 69 rows + W211 + W212 + W213 + W214 + W216 + W217 legs: n={par_sec.count(\'assert pf.N1_BANDS[\')} range={(_estate_ws[:2], _estate_ws[-6:])}"',
   'f"estate segment not W138..W206 full-span 69 rows + W211 + W212 + W213 + W214 + W215 + W216 + W217 legs: n={par_sec.count(\'assert pf.N1_BANDS[\')} range={(_estate_ws[:2], _estate_ws[-7:])}"', "estate-msg")
E1('assert par_full.count("assert pf.N1_BANDS[") == 76, \\',
   'assert par_full.count("assert pf.N1_BANDS[") == 77, \\', "parfull-count")
E1("f\"full parity span {par_full.count('assert pf.N1_BANDS[')} != 76 (69 estate + W211 leg + W212 leg + W213 leg + W214 leg + W216 leg + W217 leg + W218 leg)\"",
   "f\"full parity span {par_full.count('assert pf.N1_BANDS[')} != 77 (69 estate + W211 leg + W212 leg + W213 leg + W214 leg + W215 leg + W216 leg + W217 leg + W218 leg)\"", "parfull-msg")
E1("W214 finalize product missing (transitive chain dep)",
   "W215 finalize product missing (transitive chain dep)", "transitive-msg-w214")
E1('"w218_transitive": {"finalize_product": "results/perpetual_faces/n1_w218_results.json present (belt-and-braces gate; ledger 901,189 / K=475,320)"}',
   '"w218_transitive": {"finalize_product": "results/perpetual_faces/n1_w218_results.json present (belt-and-braces gate; ledger 903,389 / K=477,520)"}', "receipt-w218")
E1('"w217_transitive": {"finalize_product": "results/perpetual_faces/n1_w217_results.json present (belt-and-braces gate; ledger 898,989 / K=473,120)"}',
   '"w217_transitive": {"finalize_product": "results/perpetual_faces/n1_w217_results.json present (belt-and-braces gate; ledger 901,189 / K=475,320)"}', "receipt-w217")
E1('"w216_transitive": {"finalize_product": "results/perpetual_faces/n1_w216_results.json present (belt-and-braces gate; ledger 896,789 / K=470,920)"}',
   '"w216_transitive": {"finalize_product": "results/perpetual_faces/n1_w216_results.json present (belt-and-braces gate; ledger 898,989 / K=473,120)"}', "receipt-w216")
E1('"w215_transitive": {"finalize_product": "results/perpetual_faces/n1_w215_results.json present (belt-and-braces gate; ledger 894,589 / K=468,720)"}',
   '"w215_transitive": {"finalize_product": "results/perpetual_faces/n1_w215_results.json present (belt-and-braces gate; ledger 896,789 / K=470,920)"}', "receipt-w215")
E1("W220+ projection (gate-derived pre-seat probe leg4, pre-W220",
   "W221+ projection (gate-derived pre-seat probe leg4, pre-W220", "pfcomment-proj")
E1('["W220p_A"]', '["W221p_A"]', "leg4-key-a1")
E1("['W220p_A']", "['W221p_A']", "leg4-key-a2")
E1('["W220p_B"]', '["W221p_B"]', "leg4-key-b1")
E1("['W220p_B']", "['W221p_B']", "leg4-key-b2")
E1("will refuse the naive W220 A window; W220 freezer",
   "will refuse the naive W221 A window; W221 freezer", "proj-refuse")
E1('will refuse the naive W220 A window; ",',
   'will refuse the naive W221 A window; ",', "pre-proj-refuse")
E1("W220+ freezer MUST re-derive on the post-W220 universe AND ",
   "W221+ freezer MUST re-derive on the post-W220 universe AND ", "pre-freezer")
E1("downstream W220 seat publication pending per seat-first law",
   "downstream W221 seat publication pending per seat-first law", "pre-downstream")
E1("downstream W220 seat NOT yet published",
   "downstream W221 seat NOT yet published", "finface-downstream")
E1("rows 48 + candidate; seat-time live face 49th = r919 probe leg0",
   "rows 49 + candidate; seat-time live face 50th = r921 probe leg0", "hdr-liveface")
E1("(engine_owner rows 208 + candidate; gate",
   "(engine_owner rows 209 + candidate; gate", "hdr-rows207")
E1('"machine-derive (engine_owner==bm-c rows 48 + candidate; seat-time live face 49th disclosed, "',
   '"machine-derive (engine_owner==bm-c rows 49 + candidate; seat-time live face 50th disclosed, "', "pr-liveface")
E1('"phase": "five-face freeze chain-order splice (r923 freeze window, upstream ALL LANDED clean precondition)"',
   '"phase": "five-face freeze chain-order splice (r923 freeze window, upstream ALL LANDED clean precondition)"', "phase-noop-check")
E1('"probe_receipt_bmc_ordinal_face": 49,', '"probe_receipt_bmc_ordinal_face": 50,', "receipt-ordinal-face")
E1('"note": "post-W220 registration: bm-c rows 48 + candidate = 49th owned (live derive at freeze time governs per r587/r359; probe leg0 bmc_ordinal=49 = r919 seat-time live face -- disclosed honest)"',
   '"note": "post-W220 registration: bm-c rows 49 + candidate = 50th owned (live derive at freeze time governs per r587/r359; probe leg0 bmc_ordinal=50 = r921 seat-time live face -- disclosed honest)"', "receipt-ordinal-note")
E1('+ W211 + W212 + W213 + W214 + W216 + W217 legs -> W220 block = 77 rows ending at W219; disclosed: inherited W213 leg error-string face (\\"registered W212 row parity drift\\") preserved verbatim per extraction law (r912 generation cosmetic slip, assert target [213] correct, zero functional impact)',
   '+ W211 + W212 + W213 + W214 + W215 + W216 + W217 legs -> W220 block = 78 rows ending at W219; disclosed: inherited W213 leg error-string face (\\"registered W212 row parity drift\\") preserved verbatim per extraction law (r912 generation cosmetic slip, assert target [213] correct, zero functional impact)', "receipt-parity-note")
E1("r923 freeze-window bundle: prereg + this splice editor landed same-window, upstream W219 already landed (clean-precondition eighth consecutive window); r920 prereg derive = machine transform of the freeze-time W219 blob (46 count-asserted pairs, old-sides REPLAYED from the committed W219 derive SUB + the W218 derive SUB + the W217 literal PAIRS -- three-level replay chain, every block blob-verified count==1 preflight, zero transcription) + @L14@/@L15@/@L16@/@L17@/@T18@ placeholder class-guard",
   "r923 freeze-window bundle (absorb: prereg derived in the r922 dead window + 46/46 subverified in this r923 absorb window; splice editor landed r923), upstream W219 already landed (clean-precondition ninth consecutive window); r922 prereg derive = machine transform of the freeze-time W219 blob (46 count-asserted pairs, old-sides REPLAYED from the committed W219 derive SUB + the W218 derive SUB + the W217 derive SUB + the W216 literal PAIRS -- four-level replay chain, every block blob-verified count==1 preflight, zero transcription) + @L14@/@L15@/@L16@/@L17@/@L18@/@T19@ placeholder class-guard", "receipt-prereg-note")
E1('"w213_block_kept": 1, "w215_block_kept": 1, "w216_block_kept": 1, "w217_block_kept": 1, "w218_block_kept": 1, "w219_block_kept": 1}',
   '"w213_block_kept": 1, "w214_block_kept": 1, "w215_block_kept": 1, "w216_block_kept": 1, "w217_block_kept": 1, "w218_block_kept": 1, "w219_block_kept": 1}', "receipt-liveness")

for find, repl, what in E:
    t = rep1(t, find, repl, what)

# 2-count projection-ordinal shift (pf_comment + PRE)
t = repn(t, "EIGHTIETH instance anticipated", "EIGHTY-FIRST instance anticipated", 2, "proj-ordinal")

# ---------------- (3) unmask + structural additions ----------------
for i, line in enumerate(LIV):
    t = rep1(t, f"@LIV{i}@", line, f"unmask{i}")
# add the W219 liveness line right after the (unmasked) W218 line
t = rep1(t, LIV[9] + "\n",
         LIV[9] + "\n" +
         "assert n1_t4.count('    # --- W219 materializer face') == 1  # prior block kept (W219 splice landed r920 window)\n",
         "add-w219-liveness")

# ---------------- (4) final sanity ----------------
for s in ("W220", "n1_w220", "_w220bmc", "PERPETUAL-N1-W220", "498_804, 500_803", "500_804, 501_003",
          "EIGHTIETH instance, E36 card", "EIGHTY-FIRST instance anticipated",
          "905_589", "479_720", "209 and len(bmc_rows_live) == 49", "MSG-20261012-1025-bmc-w220-seat",
          "13a81d182", "== 76 \\", "== 77, \\", "W221+ projection", "w219_block_kept", "w217_block_kept",
          "r920 freeze + engine self-burn 12/12 + r921 finalize one-pass 10:1x",
          "executed bm-c r920 freeze window"):
    assert t.count(s) >= 1, f"final token missing: {s}"
assert t.count("496_604") == 0 and t.count("498_604, 498_803") == 0 and t.count("496604") == 0
# heritage preserved verbatim
assert t.count("# --- W209 materializer face") == 1
assert t.count("# --- W218 materializer face") == 1
assert t.count("# --- W219 materializer face") >= 1
assert t.count('registered W212 row parity drift') == 2  # header disclosure + receipt note
assert t.count("assert target [213] is correct") == 1
# no stale own-wave tokens
for s in ("W219 materializer face (bm-c loop", 'n1_w219"', 'PERPETUAL-N1-W219"', "bmc-w219-seat",
          "7615985e8", "SEVENTY-NINTH", "TWO HUNDRED AND NINETEENTH", "forty-ninth"):
    assert t.count(s) == 0, f"stale own token survives: {s}"
# no stale upstream r-window tokens (aged exactly one step this generation;
# the LIV heritage comment "(W218 splice landed r918 window)" stays verbatim)
for s in ("r918 freeze", "r918 window executed", "r918 window editor", "r917 seat", "r919 window", "r919 finalize"):
    assert t.count(s) == 0, f"stale upstream r-window token survives: {s}"

open(DST, "wb").write(t.encode("utf-8"))
py_compile.compile(DST, doraise=True)
print(f"W220 editor generated OK: {DST}")
print(f"bytes: {len(t.encode('utf-8'))} (source {orig_len})")
