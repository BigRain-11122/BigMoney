# -*- coding: utf-8 -*-
# W219 freeze editor generator (bm-c r920, 2026-10-12 09:5x).
# Method: machine transform of the committed W218 editor
# (results/_w218bmc_freeze_edits.py, r918 proven live-fire generation)
# into results/_w219bmc_freeze_edits.py via
#   (0) LIV masks (W209..W217 heritage liveness lines);
#       NO pre-fixes needed this generation: every r-window token in the
#       W218 editor was verified true-face before the cascade (the r918
#       gen's double-shift class was healed at its root and the cascade
#       below ages each face exactly one step -- verified by blanket count
#       asserts + dryrun bad=0 + final sanity, r787 law),
#   (1) ordered BLANKETS with before/after count verification
#       (own 218->219 first, then aging cascade 217->218 / 216->217 /
#       215->216; own r-window shifts BEFORE upstream r-window shifts,
#       keeping the r918-gen ordering discipline),
#   (2) count==1 EXPLICIT replacements for every context-sensitive literal,
#   (3) unmask + structural addition (W218 liveness line),
#   (4) final sanity + py_compile before this script exits.
import sys, py_compile

sys.stdout.reconfigure(encoding="utf-8")
SRC = r"results\_w218bmc_freeze_edits.py"
DST = r"results\_w219bmc_freeze_edits.py"
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

# ---------------- (0) masks: heritage liveness gates ----------------
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
]
for i, line in enumerate(LIV):
    t = rep1(t, line, f"@LIV{i}@", f"mask{i}")

# ---------------- (1) blankets (ordered, count-verified) ----------------
def blanket(s, find, repl, what, min_count=1):
    c = s.count(find)
    assert c >= min_count, f"[{what}] blanket count {c} < {min_count}: {find}"
    print(f"  blanket {what}: {find!r} -> {repl!r} x{c}")
    return s.replace(find, repl)

# own bundle window FIRST (r918->r920), then upstream r914/r916->r918 LAST --
# same ordering discipline as the r918 gen (own before upstream).
t = blanket(t, "r918 freeze", "r920 freeze", "own-bundle-window")
t = blanket(t, "W218", "W219", "W218->W219")
t = blanket(t, "w218_", "w219_", "w218var->w219var")
t = blanket(t, "_w218bmc", "_w219bmc", "w218bmc")
t = blanket(t, "n1_w218", "n1_w219", "n1_w218")
t = blanket(t, "n1w218", "n1w219", "n1w218")
t = blanket(t, "SEVENTY-EIGHTH", "SEVENTY-NINTH", "staircase-ordinal")
t = blanket(t, "TWO HUNDRED AND EIGHTEENTH", "TWO HUNDRED AND NINETEENTH", "engine-ordinal-words")
t = blanket(t, "forty-eighth", "forty-ninth", "bmc-ordinal-words")
t = blanket(t, "0830", "0916", "seat-msg-time")          # own seat stamp
t = blanket(t, "0700", "0830", "upstream-seat-time")     # upstream seat stamp
t = blanket(t, "08:1x", "09:1x", "finalize-time")        # upstream finalize stamp
t = blanket(t, "r915 seat", "r917 seat", "upstream-seat-r")
t = blanket(t, "r917 window", "r919 window", "own-payload-window")
t = blanket(t, "r917 finalize", "r919 finalize", "upstream-finalize-r")
t = blanket(t, "r916 freeze", "r918 freeze", "upstream-freeze-r")
t = blanket(t, "8a4c1857a", "7615985e8", "seat-origin")
t = blanket(t, "218", "219", "digit-218->219")
t = blanket(t, "W217", "W218", "W217->W218")
t = blanket(t, "w217_", "w218_", "w217var->w218var")
t = blanket(t, "217", "218", "digit-217->218")
t = blanket(t, "W216", "W217", "W216->W217")
t = blanket(t, "w216_", "w217_", "w216var->w217var")
t = blanket(t, "216", "217", "digit-216->217")   # BEFORE W215->W216 (its output must stay W216)
t = blanket(t, "W215", "W216", "W215->W216")
t = blanket(t, "w215_", "w216_", "w215var->w216var")
t = blanket(t, "215", "216", "digit-215->216")
t = blanket(t, "w214_", "w215_", "w214var->w215var")
# NOTE: no digit 214->215 blanket (same as the r918 gen: the estate list
# [211,212,213,214] + leg lists must keep their 214s verbatim; the w214_
# var blanket handles the code block var+file alignment).

# ---------------- (2) explicit replacements (count==1) ----------------
E = []
def E1(find, repl, what):
    E.append((find, repl, what))

E1("# 2026-10-12 08:5x bm-c r920 freeze: W219 five-face freeze splice editor.",
   "# 2026-10-12 09:5x bm-c r920 freeze: W219 five-face freeze splice editor.", "hdr-line2")
E1("present (W218 finalize one-pass 09:1x, net chain head 901,189,",
   "present (W218 finalize one-pass 09:1x, net chain head 903,389,", "hdr-chain-head")
E1("merged pool K=475,320, n1_w218_results.json machine-read) -- ZERO\n# in-flight upstream seats, clean precondition (seventh consecutive",
   "merged pool K=477,520, n1_w218_results.json machine-read) -- ZERO\n# in-flight upstream seats, clean precondition (eighth consecutive", "hdr-pool-k")
E1("Lineage: _w218bmc_freeze_edits.py pattern (proven live-fire freeze,\n# r916 window executed)",
   "Lineage: _w218bmc_freeze_edits.py pattern (proven live-fire freeze,\n# r918 window executed)", "lineage")
E1("(r916 window editor)", "(r918 window editor)", "own-editor-window")
E1("(chain-order precondition; W217/W216/W214/W213 finalize are transitive deps of the\n# W219 freeze",
   "(chain-order precondition; W217/W216/W215/W214 finalize are transitive deps of the\n# W219 freeze", "gate05-comment")
E1("assert w218_total == 901_189 and w218_merged_n == 475_320",
   "assert w218_total == 903_389 and w218_merged_n == 477_520", "gate05-anchors")
E1("(expect 901,189 / 475,320)", "(expect 903,389 / 477,520)", "gate05-expect")
E1("assert len(owner_rows_live) == 207 and len(bmc_rows_live) == 47",
   "assert len(owner_rows_live) == 208 and len(bmc_rows_live) == 48", "live-ordinal")
E1("(expect 207/47 PRE-splice post-W218 registration; W218 precedent 206/46 pre-splice + W218 splice 207/47; this candidate = 48th own wave",
   "(expect 208/48 PRE-splice post-W219 registration; W219 precedent 207/47 pre-splice + W219 splice 208/48; this candidate = 49th own wave", "live-ordinal-msg")
E1('f"W218+W217+W216+W214+W213 finalize products present "',
   'f"W218+W217+W216+W215+W214 finalize products present "', "gate05-print-list")
E1("candidate (48th own wave per live derive r587/r359; ",
   "candidate (49th own wave per live derive r587/r359; ", "gate05-print-ordinal")
E1("bmc_ordinal=48 seat",
   "bmc_ordinal=49 seat", "gate05-print-probe")
E1("receipt leg0 face bmc_ordinal=47 = seat-time live face; live derive at freeze\n# time: bmc rows 46 + candidate = 47th EXACT)",
   "receipt leg0 face bmc_ordinal=48 = seat-time live face; live derive at freeze\n# time: bmc rows 47 + candidate = 48th EXACT)", "gate05-comment-heal")
E1("assert (a_lo, a_hi) == (494_404, 496_403) and (b_lo, b_hi) == (496_404, 496_603), \\",
   "assert (a_lo, a_hi) == (496_604, 498_603) and (b_lo, b_hi) == (498_604, 498_803), \\", "band-literals")
E1('def fmt(n):  # 494404 -> "494_404"', 'def fmt(n):  # 496604 -> "496_604"', "fmt-doc")
E1("(76 rows: estate 69 + W211 leg + W212 leg + W213 leg + W214 leg + W216 leg + W217 leg + W218 leg).",
   "(77 rows: estate 69 + W211 leg + W212 leg + W213 leg + W214 leg + W215 leg + W216 leg + W217 leg + W218 leg).", "structural-choice")
E1("Extraction self-asserts the 74-row cut (69 estate + W211 + W212 + W213 + W214 + W216)",
   "Extraction self-asserts the 75-row cut (69 estate + W211 + W212 + W213 + W214 + W215 + W216)", "extraction-cut")
E1("own W211 leg + own W212 leg +\n# own W213 leg + own W214 leg + own W216 leg + own W217 leg)",
   "own W211 leg + own W212 leg +\n# own W213 leg + own W214 leg + own W215 leg + own W216 leg + own W217 leg)", "extraction-comment-legs")
E1('and [int(_estate_ws[69]), int(_estate_ws[70]), int(_estate_ws[71]), int(_estate_ws[72]), int(_estate_ws[73])] == [211, 212, 213, 214, 216], \\',
   'and [int(_estate_ws[69]), int(_estate_ws[70]), int(_estate_ws[71]), int(_estate_ws[72]), int(_estate_ws[73]), int(_estate_ws[74])] == [211, 212, 213, 214, 215, 216], \\', "estate-ws")
E1('assert par_sec.count("assert pf.N1_BANDS[") == 74 \\',
   'assert par_sec.count("assert pf.N1_BANDS[") == 75 \\', "parsec-count")
E1('f"estate segment not W138..W206 full-span 69 rows + W211 + W212 + W213 + W214 + W216 legs: n={par_sec.count(\'assert pf.N1_BANDS[\')} range={(_estate_ws[:2], _estate_ws[-5:])}"',
   'f"estate segment not W138..W206 full-span 69 rows + W211 + W212 + W213 + W214 + W215 + W216 legs: n={par_sec.count(\'assert pf.N1_BANDS[\')} range={(_estate_ws[:2], _estate_ws[-6:])}"', "estate-msg")
E1('assert par_full.count("assert pf.N1_BANDS[") == 75, \\',
   'assert par_full.count("assert pf.N1_BANDS[") == 76, \\', "parfull-count")
E1("f\"full parity span {par_full.count('assert pf.N1_BANDS[')} != 75 (69 estate + W211 leg + W212 leg + W213 leg + W214 leg + W216 leg + W217 leg)\"",
   "f\"full parity span {par_full.count('assert pf.N1_BANDS[')} != 76 (69 estate + W211 leg + W212 leg + W213 leg + W214 leg + W215 leg + W216 leg + W217 leg)\"", "parfull-msg")
E1("W214 finalize product missing (transitive chain dep)",
   "W215 finalize product missing (transitive chain dep)", "transitive-msg-w214")
E1("w213_out_path = os.path.join(REPO, \"results\", \"perpetual_faces\", \"n1_w213_results.json\")\nassert os.path.exists(w213_out_path), \"W213 finalize product missing (transitive chain dep) -- abort\"",
   "w214_out_path = os.path.join(REPO, \"results\", \"perpetual_faces\", \"n1_w214_results.json\")\nassert os.path.exists(w214_out_path), \"W214 finalize product missing (transitive chain dep) -- abort\"", "transitive-blocks")
E1("W219+ projection (gate-derived pre-seat probe leg4, pre-W219",
   "W220+ projection (gate-derived pre-seat probe leg4, pre-W219", "pfcomment-proj")
E1('["W219p_A"]', '["W220p_A"]', "leg4-key-a1")
E1("['W219p_A']", "['W220p_A']", "leg4-key-a2")
E1('["W219p_B"]', '["W220p_B"]', "leg4-key-b1")
E1("['W219p_B']", "['W220p_B']", "leg4-key-b2")
E1("will refuse the naive W219 A window; W219 freezer",
   "will refuse the naive W220 A window; W220 freezer", "proj-refuse")
E1('will refuse the naive W219 A window; ",',
   'will refuse the naive W220 A window; ",', "pre-proj-refuse")
E1("W219+ freezer MUST re-derive on the post-W219 universe AND ",
   "W220+ freezer MUST re-derive on the post-W219 universe AND ", "pre-freezer")
E1("downstream W219 seat publication pending per seat-first law",
   "downstream W220 seat publication pending per seat-first law", "pre-downstream")
E1("downstream W219 seat NOT yet published",
   "downstream W220 seat NOT yet published", "finface-downstream")
E1("rows 47 + candidate; seat-time live face 48th = r917 probe leg0",
   "rows 48 + candidate; seat-time live face 49th = r919 probe leg0", "hdr-liveface")
E1("(engine_owner rows 207 + candidate; gate",
   "(engine_owner rows 208 + candidate; gate", "hdr-rows207")
E1('"machine-derive (engine_owner==bm-c rows 47 + candidate; seat-time live face 48th disclosed, "',
   '"machine-derive (engine_owner==bm-c rows 48 + candidate; seat-time live face 49th disclosed, "', "pr-liveface")
E1('"phase": "five-face freeze chain-order splice (r920 freeze window, upstream ALL LANDED clean precondition)"',
   '"phase": "five-face freeze chain-order splice (r920 freeze window, upstream ALL LANDED clean precondition)"', "phase-noop-check")
E1('"w217_transitive": {"finalize_product": "results/perpetual_faces/n1_w217_results.json present (belt-and-braces gate; ledger 898,989 / K=473,120)"}',
   '"w217_transitive": {"finalize_product": "results/perpetual_faces/n1_w217_results.json present (belt-and-braces gate; ledger 901,189 / K=475,320)"}', "receipt-w217")
E1('"w216_transitive": {"finalize_product": "results/perpetual_faces/n1_w216_results.json present (belt-and-braces gate; ledger 896,789 / K=470,920)"}',
   '"w216_transitive": {"finalize_product": "results/perpetual_faces/n1_w216_results.json present (belt-and-braces gate; ledger 898,989 / K=473,120)"}', "receipt-w216")
E1('"w215_transitive": {"finalize_product": "results/perpetual_faces/n1_w215_results.json present (belt-and-braces gate; ledger 894,589 / K=468,720)"}',
   '"w215_transitive": {"finalize_product": "results/perpetual_faces/n1_w215_results.json present (belt-and-braces gate; ledger 896,789 / K=470,920)"}', "receipt-w215")
E1('"w213_transitive": {"finalize_product": "results/perpetual_faces/n1_w213_results.json present (belt-and-braces gate; ledger 892,389 / K=466,520)"}',
   '"w214_transitive": {"finalize_product": "results/perpetual_faces/n1_w214_results.json present (belt-and-braces gate; ledger 894,589 / K=468,720)"}', "receipt-w213")
E1('"probe_receipt_bmc_ordinal_face": 48,', '"probe_receipt_bmc_ordinal_face": 49,', "receipt-ordinal-face")
E1('"note": "post-W218 registration: bm-c rows 47 + candidate = 48th owned (live derive at freeze time governs per r587/r359; probe leg0 bmc_ordinal=48 = r917 seat-time live face -- disclosed honest)"',
   '"note": "post-W219 registration: bm-c rows 48 + candidate = 49th owned (live derive at freeze time governs per r587/r359; probe leg0 bmc_ordinal=49 = r919 seat-time live face -- disclosed honest)"', "receipt-ordinal-note")
E1('+ W211 + W212 + W213 + W214 + W216 legs -> W219 block = 76 rows ending at W218; disclosed: inherited W213 leg error-string face (\\"registered W212 row parity drift\\") preserved verbatim per extraction law (r912 generation cosmetic slip, assert target [213] correct, zero functional impact)',
   '+ W211 + W212 + W213 + W214 + W215 + W216 legs -> W219 block = 77 rows ending at W218; disclosed: inherited W213 leg error-string face (\\"registered W212 row parity drift\\") preserved verbatim per extraction law (r912 generation cosmetic slip, assert target [213] correct, zero functional impact)', "receipt-parity-note")
E1("(clean-precondition seventh consecutive window); r918 prereg derive = machine transform of the freeze-time W218 blob (46 count-asserted pairs, old-sides REPLAYED from the committed W218 derive SUB + the W217 literal PAIRS, every block blob-verified count==1 preflight, zero transcription) + @L14@/@L15@/@L16@/@T17@ placeholder class-guard",
   "(clean-precondition eighth consecutive window); r920 prereg derive = machine transform of the freeze-time W218 blob (46 count-asserted pairs, old-sides REPLAYED from the committed W218 derive SUB + the W217 derive SUB + the W216 literal PAIRS -- three-level replay chain, every block blob-verified count==1 preflight, zero transcription) + @L14@/@L15@/@L16@/@L17@/@T18@ placeholder class-guard", "receipt-prereg-note")
E1('"w213_block_kept": 1, "w215_block_kept": 1, "w216_block_kept": 1, "w217_block_kept": 1, "w218_block_kept": 1}',
   '"w213_block_kept": 1, "w214_block_kept": 1, "w215_block_kept": 1, "w216_block_kept": 1, "w217_block_kept": 1, "w218_block_kept": 1}', "receipt-liveness")

for find, repl, what in E:
    t = rep1(t, find, repl, what)

# 2-count projection-ordinal shift (pf_comment + PRE)
t = repn(t, "SEVENTY-NINTH instance anticipated", "EIGHTIETH instance anticipated", 2, "proj-ordinal")

# ---------------- (3) unmask + structural additions ----------------
for i, line in enumerate(LIV):
    t = rep1(t, f"@LIV{i}@", line, f"unmask{i}")
# add the W218 liveness line right after the (unmasked) W217 line
t = rep1(t, LIV[8] + "\n",
         LIV[8] + "\n" +
         "assert n1_t4.count('    # --- W218 materializer face') == 1  # prior block kept (W218 splice landed r918 window)\n",
         "add-w218-liveness")

# ---------------- (4) final sanity ----------------
for s in ("W219", "n1_w219", "_w219bmc", "PERPETUAL-N1-W219", "496_604, 498_603", "498_604, 498_803",
          "SEVENTY-NINTH instance, E36 card", "EIGHTIETH instance anticipated",
          "903_389", "477_520", "208 and len(bmc_rows_live) == 48", "MSG-20261012-0916-bmc-w219-seat",
          "7615985e8", "== 75 \\", "== 76, \\", "W220+ projection", "w218_block_kept", "w216_block_kept",
          "r918 freeze + engine self-burn 12/12 + r919 finalize one-pass 09:1x",
          "executed bm-c r918 freeze window"):
    assert t.count(s) >= 1, f"final token missing: {s}"
assert t.count("494_404") == 0 and t.count("496_404, 496_603") == 0
# heritage preserved verbatim
assert t.count("# --- W209 materializer face") == 1
assert t.count("# --- W217 materializer face") == 1
assert t.count("# --- W218 materializer face") >= 1
assert t.count('registered W212 row parity drift') == 2  # header disclosure + receipt note
assert t.count("assert target [213] is correct") == 1
# no stale own-wave tokens
for s in ("W218 materializer face (bm-c loop", 'n1_w218"', 'PERPETUAL-N1-W218"', "bmc-w218-seat",
          "8a4c1857a", "SEVENTY-EIGHTH", "TWO HUNDRED AND EIGHTEENTH", "forty-eighth"):
    assert t.count(s) == 0, f"stale own token survives: {s}"
# no stale upstream r-window tokens (aged exactly one step this generation;
# the LIV heritage comment "(W217 splice landed r916 window)" stays verbatim)
for s in ("r916 freeze", "r916 window executed", "r916 window editor", "r915 seat", "r917 window", "r917 finalize"):
    assert t.count(s) == 0, f"stale upstream r-window token survives: {s}"

open(DST, "wb").write(t.encode("utf-8"))
py_compile.compile(DST, doraise=True)
print(f"W219 editor generated OK: {DST}")
print(f"bytes: {len(t.encode('utf-8'))} (source {orig_len})")
