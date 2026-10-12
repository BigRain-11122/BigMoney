# -*- coding: utf-8 -*-
# W218 freeze editor generator (bm-c r918, 2026-10-12 08:5x).
# Method: machine transform of the committed W217 editor
# (results/_w217bmc_freeze_edits.py, r916 proven live-fire generation)
# into results/_w218bmc_freeze_edits.py via
#   (0) LIV masks (W209..W216 heritage liveness lines) + PRE-FIXES for the
#       two r-window double-shift artifacts disclosed in the W217 editor
#       (upstream-chain prose "executed bm-c r916 freeze window" +
#       receipt repair_chain_note "r916 freeze + ... r915 finalize" -- both
#       described the W216 chain and are healed to their true r914 face
#       BEFORE the cascade, so the cascade then ages them to the correct
#       W217 r916/r917 faces; artifact class root-caused and fixed here,
#       r787 law),
#   (1) ordered BLANKETS with before/after count verification
#       (own 217->218 first, then aging cascade 216->217 / 215->216;
#       r-window order FIXED vs the W217 gen: own r916->r918 BEFORE
#       upstream r914->r916, killing the double-shift class),
#   (2) count==1 EXPLICIT replacements for every context-sensitive literal,
#   (3) unmask + structural addition (W217 liveness line),
#   (4) final sanity + py_compile before this script exits.
import sys, py_compile

sys.stdout.reconfigure(encoding="utf-8")
SRC = r"results\_w217bmc_freeze_edits.py"
DST = r"results\_w218bmc_freeze_edits.py"
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
]
for i, line in enumerate(LIV):
    t = rep1(t, line, f"@LIV{i}@", f"mask{i}")

# ---------------- (0b) pre-fixes: W217-gen double-shift artifacts ----------------
t = rep1(t, "executed bm-c r916 freeze window", "executed bm-c r914 freeze window", "prefix-upstream-prose")
t = rep1(t, '"repair_chain_note": "r916 freeze +', '"repair_chain_note": "r914 freeze +', "prefix-repair-note")

# ---------------- (1) blankets (ordered, count-verified) ----------------
def blanket(s, find, repl, what, min_count=1):
    c = s.count(find)
    assert c >= min_count, f"[{what}] blanket count {c} < {min_count}: {find}"
    print(f"  blanket {what}: {find!r} -> {repl!r} x{c}")
    return s.replace(find, repl)

# own bundle window FIRST (r916->r918), then upstream r914->r916 last --
# kills the W217-gen double-shift class (both artifacts pre-fixed above).
t = blanket(t, "r916 freeze", "r918 freeze", "own-bundle-window")
t = blanket(t, "W217", "W218", "W217->W218")
t = blanket(t, "w217_", "w218_", "w217var->w218var")
t = blanket(t, "_w217bmc", "_w218bmc", "w217bmc")
t = blanket(t, "n1_w217", "n1_w218", "n1_w217")
t = blanket(t, "n1w217", "n1w218", "n1w217")
t = blanket(t, "SEVENTY-SEVENTH", "SEVENTY-EIGHTH", "staircase-ordinal")
t = blanket(t, "TWO HUNDRED AND SEVENTEENTH", "TWO HUNDRED AND EIGHTEENTH", "engine-ordinal-words")
t = blanket(t, "forty-seventh", "forty-eighth", "bmc-ordinal-words")
t = blanket(t, "0700", "0830", "seat-msg-time")          # own seat stamp
t = blanket(t, "0630", "0700", "upstream-seat-time")     # upstream seat stamp
t = blanket(t, "06:5x", "08:1x", "finalize-time")        # upstream finalize stamp
t = blanket(t, "r913 seat", "r915 seat", "upstream-seat-r")
t = blanket(t, "r915 window", "r917 window", "own-payload-window")
t = blanket(t, "r915 finalize", "r917 finalize", "upstream-finalize-r")
t = blanket(t, "r914 freeze", "r916 freeze", "upstream-freeze-r")  # pre-fixed artifacts + none else (count asserted by apply)
t = blanket(t, "1e1454cfb", "8a4c1857a", "seat-origin")
t = blanket(t, "217", "218", "digit-217->218")
t = blanket(t, "W216", "W217", "W216->W217")
t = blanket(t, "w216_", "w217_", "w216var->w217var")
t = blanket(t, "216", "217", "digit-216->217")   # BEFORE W215->W216 (its output must stay W216)
t = blanket(t, "W215", "W216", "W215->W216")
t = blanket(t, "w215_", "w216_", "w215var->w216var")
t = blanket(t, "215", "216", "digit-215->216")
t = blanket(t, "w214_", "w215_", "w214var->w215var")
# NOTE: no digit 214->215 blanket (W217-gen had it for the W214-uppercase
# message; here that message is E1-handled and the estate list [211,212,213,
# 214] + leg lists must keep their 214s verbatim).

# ---------------- (2) explicit replacements (count==1) ----------------
E = []
def E1(find, repl, what):
    E.append((find, repl, what))

E1("2026-10-12 07:5x bm-c r918 freeze: W218 five-face freeze splice editor.",
   "2026-10-12 08:5x bm-c r918 freeze: W218 five-face freeze splice editor.", "hdr-line2")
E1("present (W217 finalize one-pass 08:1x, net chain head 898,989,",
   "present (W217 finalize one-pass 08:1x, net chain head 901,189,", "hdr-chain-head")
E1("merged pool K=473,120, n1_w217_results.json machine-read) -- ZERO\n# in-flight upstream seats, clean precondition (sixth consecutive",
   "merged pool K=475,320, n1_w217_results.json machine-read) -- ZERO\n# in-flight upstream seats, clean precondition (seventh consecutive", "hdr-pool-k")
E1("Lineage: _w217bmc_freeze_edits.py pattern (proven live-fire freeze,\n# r914 window executed)",
   "Lineage: _w217bmc_freeze_edits.py pattern (proven live-fire freeze,\n# r916 window executed)", "lineage")
E1("(r914 window editor)", "(r916 window editor)", "own-editor-window")
E1("(chain-order precondition; W216/W214/W213/W212 finalize are transitive deps of the\n# W218 freeze",
   "(chain-order precondition; W216/W215/W214/W213 finalize are transitive deps of the\n# W218 freeze", "gate05-comment")
E1("assert w217_total == 898_989 and w217_merged_n == 473_120",
   "assert w217_total == 901_189 and w217_merged_n == 475_320", "gate05-anchors")
E1("(expect 898,989 / 473,120)", "(expect 901,189 / 475,320)", "gate05-expect")
E1("assert len(owner_rows_live) == 206 and len(bmc_rows_live) == 46",
   "assert len(owner_rows_live) == 207 and len(bmc_rows_live) == 47", "live-ordinal")
E1("(expect 206/46 PRE-splice post-W217 registration; W217 precedent 205/45 pre-splice + W217 splice 206/46; this candidate = 47th own wave",
   "(expect 207/47 PRE-splice post-W217 registration; W217 precedent 206/46 pre-splice + W217 splice 207/47; this candidate = 48th own wave", "live-ordinal-msg")
E1('f"W217+W216+W214+W213+W212 finalize products present "',
   'f"W217+W216+W215+W214+W213 finalize products present "', "gate05-print-list")
E1("candidate (47th own wave per live derive r587/r359; ",
   "candidate (48th own wave per live derive r587/r359; ", "gate05-print-ordinal")
E1("bmc_ordinal=47 seat",
   "bmc_ordinal=48 seat", "gate05-print-probe")
E1("receipt leg0 face bmc_ordinal=46 = seat-time live face; live derive at freeze\n# time: bmc rows 45 + candidate = 46th EXACT)",
   "receipt leg0 face bmc_ordinal=47 = seat-time live face; live derive at freeze\n# time: bmc rows 46 + candidate = 47th EXACT)", "gate05-comment-heal")
E1("assert (a_lo, a_hi) == (492_204, 494_203) and (b_lo, b_hi) == (494_204, 494_403), \\",
   "assert (a_lo, a_hi) == (494_404, 496_403) and (b_lo, b_hi) == (496_404, 496_603), \\", "band-literals")
E1('def fmt(n):  # 492204 -> "492_204"', 'def fmt(n):  # 494404 -> "494_404"', "fmt-doc")
E1("(75 rows: estate 69 + W211 leg + W212 leg + W213 leg + W214 leg + W216 leg + W217 leg).",
   "(76 rows: estate 69 + W211 leg + W212 leg + W213 leg + W214 leg + W215 leg + W216 leg + W217 leg).", "structural-choice")
E1("Extraction self-asserts the 73-row cut (69 estate + W211 + W212 + W213 + W214)",
   "Extraction self-asserts the 74-row cut (69 estate + W211 + W212 + W213 + W214 + W215)", "extraction-cut")
E1("own W211 leg + own W212 leg +\n# own W213 leg + own W214 leg + own W216 leg)",
   "own W211 leg + own W212 leg +\n# own W213 leg + own W214 leg + own W215 leg + own W216 leg)", "extraction-comment-legs")
E1('and [int(_estate_ws[69]), int(_estate_ws[70]), int(_estate_ws[71]), int(_estate_ws[72])] == [211, 212, 213, 214], \\',
   'and [int(_estate_ws[69]), int(_estate_ws[70]), int(_estate_ws[71]), int(_estate_ws[72]), int(_estate_ws[73])] == [211, 212, 213, 214, 215], \\', "estate-ws")
E1('assert par_sec.count("assert pf.N1_BANDS[") == 73 \\',
   'assert par_sec.count("assert pf.N1_BANDS[") == 74 \\', "parsec-count")
E1('f"estate segment not W138..W206 full-span 69 rows + W211 + W212 + W213 + W214 legs: n={par_sec.count(\'assert pf.N1_BANDS[\')} range={(_estate_ws[:2], _estate_ws[-4:])}"',
   'f"estate segment not W138..W206 full-span 69 rows + W211 + W212 + W213 + W214 + W215 legs: n={par_sec.count(\'assert pf.N1_BANDS[\')} range={(_estate_ws[:2], _estate_ws[-5:])}"', "estate-msg")
E1('assert par_full.count("assert pf.N1_BANDS[") == 74, \\',
   'assert par_full.count("assert pf.N1_BANDS[") == 75, \\', "parfull-count")
E1("f\"full parity span {par_full.count('assert pf.N1_BANDS[')} != 74 (69 estate + W211 leg + W212 leg + W213 leg + W214 leg + W216 leg)\"",
   "f\"full parity span {par_full.count('assert pf.N1_BANDS[')} != 75 (69 estate + W211 leg + W212 leg + W213 leg + W214 leg + W215 leg + W216 leg)\"", "parfull-msg")
E1("W214 finalize product missing (transitive chain dep)",
   "W215 finalize product missing (transitive chain dep)", "transitive-msg-w214")
E1('w213_out_path = os.path.join(REPO, "results", "perpetual_faces", "n1_w213_results.json")\nassert os.path.exists(w213_out_path), "W213 finalize product missing (transitive chain dep) -- abort"\nw212_out_path = os.path.join(REPO, "results", "perpetual_faces", "n1_w212_results.json")\nassert os.path.exists(w212_out_path), "W212 finalize product missing (transitive chain dep) -- abort"',
   'w214_out_path = os.path.join(REPO, "results", "perpetual_faces", "n1_w214_results.json")\nassert os.path.exists(w214_out_path), "W214 finalize product missing (transitive chain dep) -- abort"\nw213_out_path = os.path.join(REPO, "results", "perpetual_faces", "n1_w213_results.json")\nassert os.path.exists(w213_out_path), "W213 finalize product missing (transitive chain dep) -- abort"', "transitive-blocks")
E1("W218+ projection (gate-derived pre-seat probe leg4, pre-W218",
   "W219+ projection (gate-derived pre-seat probe leg4, pre-W218", "pfcomment-proj")
E1('["W218p_A"]', '["W219p_A"]', "leg4-key-a1")
E1("['W218p_A']", "['W219p_A']", "leg4-key-a2")
E1('["W218p_B"]', '["W219p_B"]', "leg4-key-b1")
E1("['W218p_B']", "['W219p_B']", "leg4-key-b2")
E1("will refuse the naive W218 A window; W218 freezer",
   "will refuse the naive W219 A window; W219 freezer", "proj-refuse")
E1('will refuse the naive W218 A window; ",',
   'will refuse the naive W219 A window; ",', "pre-proj-refuse")
E1("W218+ freezer MUST re-derive on the post-W218 universe AND ",
   "W219+ freezer MUST re-derive on the post-W218 universe AND ", "pre-freezer")
E1("downstream W218 seat publication pending per seat-first law",
   "downstream W219 seat publication pending per seat-first law", "pre-downstream")
E1("downstream W218 seat NOT yet published",
   "downstream W219 seat NOT yet published", "finface-downstream")
E1("rows 46 + candidate; seat-time live face 47th = r915 probe leg0",
   "rows 47 + candidate; seat-time live face 48th = r917 probe leg0", "hdr-liveface")
E1("(engine_owner rows 206 + candidate; gate",
   "(engine_owner rows 207 + candidate; gate", "hdr-rows206")
E1('"machine-derive (engine_owner==bm-c rows 46 + candidate; seat-time live face 47th disclosed, "',
   '"machine-derive (engine_owner==bm-c rows 47 + candidate; seat-time live face 48th disclosed, "', "pr-liveface")
E1('"phase": "five-face freeze chain-order splice (r918 freeze window, upstream ALL LANDED clean precondition)"',
   '"phase": "five-face freeze chain-order splice (r918 freeze window, upstream ALL LANDED clean precondition)"', "phase-noop-check")
E1('"w216_transitive": {"finalize_product": "results/perpetual_faces/n1_w216_results.json present (belt-and-braces gate; ledger 896,789 / K=470,920)"}',
   '"w216_transitive": {"finalize_product": "results/perpetual_faces/n1_w216_results.json present (belt-and-braces gate; ledger 898,989 / K=473,120)"}', "receipt-w216")
E1('"w215_transitive": {"finalize_product": "results/perpetual_faces/n1_w215_results.json present (belt-and-braces gate; ledger 894,589 / K=468,720)"}',
   '"w215_transitive": {"finalize_product": "results/perpetual_faces/n1_w215_results.json present (belt-and-braces gate; ledger 896,789 / K=470,920)"}', "receipt-w215")
E1('"w213_transitive": {"finalize_product": "results/perpetual_faces/n1_w213_results.json present (belt-and-braces gate; ledger 892,389 / K=466,520)"}',
   '"w214_transitive": {"finalize_product": "results/perpetual_faces/n1_w214_results.json present (belt-and-braces gate; ledger 894,589 / K=468,720)"}', "receipt-w214")
E1('"w212_transitive": {"finalize_product": "results/perpetual_faces/n1_w212_results.json present (belt-and-braces gate)"}',
   '"w213_transitive": {"finalize_product": "results/perpetual_faces/n1_w213_results.json present (belt-and-braces gate; ledger 892,389 / K=466,520)"}', "receipt-w213")
E1('"probe_receipt_bmc_ordinal_face": 47,', '"probe_receipt_bmc_ordinal_face": 48,', "receipt-ordinal-face")
E1('"note": "post-W217 registration: bm-c rows 46 + candidate = 47th owned (live derive at freeze time governs per r587/r359; probe leg0 bmc_ordinal=47 = r915 seat-time live face -- disclosed honest)"',
   '"note": "post-W217 registration: bm-c rows 47 + candidate = 48th owned (live derive at freeze time governs per r587/r359; probe leg0 bmc_ordinal=48 = r917 seat-time live face -- disclosed honest)"', "receipt-ordinal-note")
E1('+ W211 + W212 + W213 + W214 legs -> W218 block = 75 rows ending at W217; disclosed: inherited W213 leg error-string face (\\"registered W212 row parity drift\\") preserved verbatim per extraction law (r912 generation cosmetic slip, assert target [213] correct, zero functional impact)',
   '+ W211 + W212 + W213 + W214 + W215 legs -> W218 block = 76 rows ending at W217; disclosed: inherited W213 leg error-string face (\\"registered W212 row parity drift\\") preserved verbatim per extraction law (r912 generation cosmetic slip, assert target [213] correct, zero functional impact)', "receipt-parity-note")
E1('"note": "r918 freeze-window bundle: prereg + this splice editor landed same-window, upstream W217 already landed (clean-precondition sixth consecutive window); r916 prereg derive = machine transform of the freeze-time W217 blob (46 count-asserted pairs, old-sides ast-extracted from the committed W217 derive, zero transcription) + @L14@/@L15@/@T16@ placeholder class-guard"',
   '"note": "r918 freeze-window bundle: prereg + this splice editor landed same-window, upstream W217 already landed (clean-precondition seventh consecutive window); r918 prereg derive = machine transform of the freeze-time W217 blob (46 count-asserted pairs, old-sides REPLAYED from the committed W217 derive SUB + the W216 literal PAIRS, every block blob-verified count==1 preflight, zero transcription) + @L14@/@L15@/@L16@/@T17@ placeholder class-guard"', "receipt-prereg-note")
E1('"w213_block_kept": 1, "w215_block_kept": 1, "w216_block_kept": 1, "w217_block_kept": 1}',
   '"w213_block_kept": 1, "w214_block_kept": 1, "w215_block_kept": 1, "w216_block_kept": 1, "w217_block_kept": 1}', "receipt-liveness")

for find, repl, what in E:
    t = rep1(t, find, repl, what)

# 2-count projection-ordinal shift (pf_comment + PRE)
t = repn(t, "SEVENTY-EIGHTH instance anticipated", "SEVENTY-NINTH instance anticipated", 2, "proj-ordinal")

# ---------------- (3) unmask + structural additions ----------------
for i, line in enumerate(LIV):
    t = rep1(t, f"@LIV{i}@", line, f"unmask{i}")
# add the W217 liveness line right after the (unmasked) W216 line
t = rep1(t, LIV[7] + "\n",
         LIV[7] + "\n" +
         "assert n1_t4.count('    # --- W217 materializer face') == 1  # prior block kept (W217 splice landed r916 window)\n",
         "add-w217-liveness")

# ---------------- (4) final sanity ----------------
for s in ("W218", "n1_w218", "_w218bmc", "PERPETUAL-N1-W218", "494_404, 496_403", "496_404, 496_603",
          "SEVENTY-EIGHTH instance, E36 card", "SEVENTY-NINTH instance anticipated",
          "901_189", "475_320", "207 and len(bmc_rows_live) == 47", "MSG-20261012-0830-bmc-w218-seat",
          "8a4c1857a", "== 74 \\", "== 75, \\", "W219+ projection", "w217_block_kept", "w215_block_kept",
          "r916 freeze + engine self-burn 12/12 + r917 finalize one-pass 08:1x",
          "executed bm-c r916 freeze window"):
    assert t.count(s) >= 1, f"final token missing: {s}"
assert t.count("492_204") == 0 and t.count("494_204, 494_403") == 0
# heritage preserved verbatim
assert t.count("# --- W209 materializer face") == 1
assert t.count("# --- W216 materializer face") == 1
assert t.count("# --- W217 materializer face") >= 1
assert t.count('registered W212 row parity drift') == 2  # header disclosure + receipt note
assert t.count("assert target [213] is correct") == 1
# no stale own-wave tokens
for s in ("W217 materializer face (bm-c loop", 'n1_w217"', 'PERPETUAL-N1-W217"', "bmc-w217-seat",
          "1e1454cfb", "SEVENTY-SEVENTH", "TWO HUNDRED AND SEVENTEENTH", "forty-seventh"):
    assert t.count(s) == 0, f"stale own token survives: {s}"

open(DST, "wb").write(t.encode("utf-8"))
py_compile.compile(DST, doraise=True)
print(f"W218 editor generated OK: {DST}")
print(f"bytes: {len(t.encode('utf-8'))} (source {orig_len})")
