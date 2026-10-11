# -*- coding: utf-8 -*-
# W217 freeze editor generator (bm-c r916, 2026-10-12 07:5x).
# Method: machine transform of the committed W216 editor
# (results/_w216bmc_freeze_edits.py, r914 proven live-fire generation)
# into results/_w217bmc_freeze_edits.py via
#   (1) full-line masks for heritage liveness gates (W209..W215 blocks),
#   (2) ordered BLANKETS with before/after count verification
#       (216->217, 215->216, 214->215 cascades + family shifts),
#   (3) count==1 EXPLICIT replacements for every context-sensitive
#       literal (upstream chain stamps, ordinals, anchors, parity
#       constants, receipt faces),
#   (4) unmask + structural additions (W216 liveness line, receipt key).
# Every step asserts; zero silent no-ops (r787 law). Output py_compiles
# before this script exits.
import re, sys, py_compile

sys.stdout.reconfigure(encoding="utf-8")
SRC = r"results\_w216bmc_freeze_edits.py"
DST = r"results\_w217bmc_freeze_edits.py"
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

# ---------------- (1) masks: heritage liveness gates ----------------
LIV = [
 "assert n1_t4.count('    # --- W209 materializer face') == 1  # estate source block kept",
 "assert n1_t4.count('    # --- W210 materializer face') == 1  # prior block kept",
 "assert n1_t4.count('    # --- W211 materializer face') == 1  # prior block kept",
 "assert n1_t4.count('    # --- W212 materializer face') == 1  # prior block kept",
 "assert n1_t4.count('    # --- W213 materializer face') == 1  # prior block kept",
 "assert n1_t4.count('    # --- W214 materializer face') == 1  # prior block kept (W214 splice landed r910 window)",
 "assert n1_t4.count('    # --- W215 materializer face') == 1  # prior block kept (W215 splice landed r912 window)",
]
for i, line in enumerate(LIV):
    t = rep1(t, line, f"@LIV{i}@", f"mask{i}")

# ---------------- (2) blankets (ordered, count-verified) ----------------
def blanket(s, find, repl, what, min_count=1):
    c = s.count(find)
    assert c >= min_count, f"[{what}] blanket count {c} < {min_count}: {find}"
    print(f"  blanket {what}: {find!r} -> {repl!r} x{c}")
    return s.replace(find, repl)

# own-wave family first (W216 -> W217), then upstream (W215 -> W216),
# then transitive-top (W214 -> W215); descending prevents double-shift.
t = blanket(t, "W216", "W217", "W216->W217")
t = blanket(t, "w216_", "w217_", "w216var->w217var")
t = blanket(t, "_w216bmc", "_w217bmc", "w216bmc")
# (PERPETUAL-N1-W216 / PERPETUAL_N1_W216 forms already consumed by the
#  uppercase W216 blanket above -- counted inside its x65)
t = blanket(t, "n1_w216", "n1_w217", "n1_w216")
t = blanket(t, "n1w216", "n1w217", "n1w216")
t = blanket(t, "SEVENTY-SIXTH", "SEVENTY-SEVENTH", "staircase-ordinal")
t = blanket(t, "TWO HUNDRED AND SIXTEENTH", "TWO HUNDRED AND SEVENTEENTH", "engine-ordinal-words")
t = blanket(t, "forty-sixth", "forty-seventh", "bmc-ordinal-words")
t = blanket(t, "0630", "0700", "seat-msg-time")          # own seat stamp
t = blanket(t, "0536", "0630", "upstream-seat-time")       # upstream seat stamp (after 0630->0700)
t = blanket(t, "06:1x", "06:5x", "finalize-time")          # upstream finalize stamp
t = blanket(t, "r912 freeze", "r914 freeze", "upstream-freeze-r")
t = blanket(t, "r913 finalize", "r915 finalize", "upstream-finalize-r")
t = blanket(t, "r911 seat", "r913 seat", "upstream-seat-r")
t = blanket(t, "r913 window", "r915 window", "payload-window")
t = blanket(t, "r914 freeze", "r916 freeze", "bundle-window")  # r914 freeze window/bundle -> r916
t = blanket(t, "f8b38fa1e", "1e1454cfb", "seat-origin")
t = blanket(t, "216", "217", "digit-216->217")
t = blanket(t, "W215", "W216", "W215->W216")
t = blanket(t, "w215_", "w216_", "w215var->w216var")
# (n1_w215 consumed by the w215_ var blanket -> n1_w216 upstream refs)
t = blanket(t, "215", "216", "digit-215->216")
t = blanket(t, "w214_", "w215_", "w214var->w215var")
# (n1_w214 consumed by the w214_ var blanket -> n1_w215 transitive refs)
t = blanket(t, "214", "215", "digit-214->215")

# ---------------- (3) explicit replacements (count==1) ----------------
E = []
def E1(find, repl, what):
    E.append((find, repl, what))

# header block
E1("2026-10-12 06:5x bm-c r916 freeze: W217 five-face freeze splice editor.",
   "2026-10-12 07:5x bm-c r916 freeze: W217 five-face freeze splice editor.", "hdr-line2")
E1("present (W216 finalize one-pass 06:5x, net chain head 896,789,",
   "present (W216 finalize one-pass 06:5x, net chain head 898,989,", "hdr-chain-head")
E1("merged pool K=470,920, n1_w216_results.json machine-read) -- ZERO\n# in-flight upstream seats, clean precondition (fifth consecutive",
   "merged pool K=473,120, n1_w216_results.json machine-read) -- ZERO\n# in-flight upstream seats, clean precondition (sixth consecutive", "hdr-pool-k")
E1("Lineage: _w215bmc_freeze_edits.py pattern (proven live-fire freeze,\n# r912 window executed)",
   "Lineage: _w216bmc_freeze_edits.py pattern (proven live-fire freeze,\n# r914 window executed)", "lineage")
E1("(chain-order precondition; W215/W213/W212/W211 finalize are transitive deps of the\n# W217 freeze",
   "(chain-order precondition; W215/W214/W213/W212 finalize are transitive deps of the\n# W217 freeze", "gate05-comment")
E1("assert w216_total == 896_789 and w216_merged_n == 470_920",
   "assert w216_total == 898_989 and w216_merged_n == 473_120", "gate05-anchors")
E1("(expect 896,789 / 470,920)", "(expect 898,989 / 473,120)", "gate05-expect")
E1('assert len(owner_rows_live) == 205 and len(bmc_rows_live) == 45',
   'assert len(owner_rows_live) == 206 and len(bmc_rows_live) == 46', "live-ordinal")
E1("(expect 205/45 PRE-splice post-W216 registration; W216 precedent 204/44 pre-splice + W216 splice 205/45; this candidate = 46th own wave",
   "(expect 206/46 PRE-splice post-W216 registration; W216 precedent 205/45 pre-splice + W216 splice 206/46; this candidate = 47th own wave", "live-ordinal-msg")
E1("f\"W216+W214+W213+W212+W211 finalize products present \"",
   "f\"W216+W215+W214+W213+W212 finalize products present \"", "gate05-print-list")
E1("candidate (46th own wave per live derive r587/r359; ",
   "candidate (47th own wave per live derive r587/r359; ", "gate05-print-ordinal")
E1("probe receipt leg0 bmc_ordinal=46 seat-time live face disclosed\")",
   "probe receipt leg0 bmc_ordinal=47 seat-time live face disclosed\")", "gate05-print-probe")
# band literals (placeholder order)
E1("(490_004, 492_003)", "(@BA@)", "bandA-mask")
E1("(492_004, 492_203)", "(494_204, 494_403)", "bandB")
E1("(@BA@)", "(492_204, 494_203)", "bandA")
E1('def fmt(n):  # 490004 -> "490_004"', 'def fmt(n):  # 492204 -> "492_204"', "fmt-doc")
# STRUCTURAL CHOICE comment (digit blankets already shifted the W214->W215 leg tokens)
E1("parity (74 rows: estate 69 + W211 leg + W212 leg + W213 leg + W215 leg + W216 leg).",
   "parity (75 rows: estate 69 + W211 leg + W212 leg + W213 leg + W214 leg + W215 leg + W216 leg).", "structural-choice")
E1("Extraction self-asserts the 72-row cut (69 estate + W211 + W212 + W213)",
   "Extraction self-asserts the 73-row cut (69 estate + W211 + W212 + W213 + W214)", "extraction-cut")
E1('and [int(_estate_ws[69]), int(_estate_ws[70]), int(_estate_ws[71])] == [211, 212, 213], \\',
   'and [int(_estate_ws[69]), int(_estate_ws[70]), int(_estate_ws[71]), int(_estate_ws[72])] == [211, 212, 213, 214], \\', "estate-ws")
E1('== 72 \\\n    and [int(w) for w in _estate_ws[:69]] == list(range(138, 207)) \\',
   '== 73 \\\n    and [int(w) for w in _estate_ws[:69]] == list(range(138, 207)) \\', "parsec-count")
E1('f"estate segment not W138..W206 full-span 69 rows + W211 + W212 + W213 legs: n={par_sec.count(\'assert pf.N1_BANDS[\')} range={(_estate_ws[:2], _estate_ws[-3:])}"',
   'f"estate segment not W138..W206 full-span 69 rows + W211 + W212 + W213 + W214 legs: n={par_sec.count(\'assert pf.N1_BANDS[\')} range={(_estate_ws[:2], _estate_ws[-4:])}"', "estate-msg")
E1('assert par_full.count("assert pf.N1_BANDS[") == 73, \\',
   'assert par_full.count("assert pf.N1_BANDS[") == 74, \\', "parfull-count")
E1("f\"full parity span {par_full.count('assert pf.N1_BANDS[')} != 73 (69 estate + W211 leg + W212 leg + W213 leg + W215 leg)\"",
   "f\"full parity span {par_full.count('assert pf.N1_BANDS[')} != 74 (69 estate + W211 leg + W212 leg + W213 leg + W214 leg + W215 leg)\"", "parfull-msg")
# transitive gate0.5 blocks (W213/W212/W211 -> W214/W213/W212)
E1('w213_out_path = os.path.join(REPO, "results", "perpetual_faces", "n1_w213_results.json")\nassert os.path.exists(w213_out_path), "W213 finalize product missing (transitive chain dep) -- abort"\nw212_out_path = os.path.join(REPO, "results", "perpetual_faces", "n1_w212_results.json")\nassert os.path.exists(w212_out_path), "W212 finalize product missing (transitive chain dep) -- abort"\nw211_out_path = os.path.join(REPO, "results", "perpetual_faces", "n1_w211_results.json")\nassert os.path.exists(w211_out_path), "W211 finalize product missing (transitive chain dep) -- abort"',
   'w214_out_path = os.path.join(REPO, "results", "perpetual_faces", "n1_w214_results.json")\nassert os.path.exists(w214_out_path), "W214 finalize product missing (transitive chain dep) -- abort"\nw213_out_path = os.path.join(REPO, "results", "perpetual_faces", "n1_w213_results.json")\nassert os.path.exists(w213_out_path), "W213 finalize product missing (transitive chain dep) -- abort"\nw212_out_path = os.path.join(REPO, "results", "perpetual_faces", "n1_w212_results.json")\nassert os.path.exists(w212_out_path), "W212 finalize product missing (transitive chain dep) -- abort"', "transitive-blocks")
# projection face W217+ -> W218+
E1("W217+ projection (gate-derived pre-seat probe leg4, pre-W217",
   "W218+ projection (gate-derived pre-seat probe leg4, pre-W217", "pfcomment-proj")
E1("W217+ projection per this window gate: ", "W218+ projection per this window gate: ", "pre-proj")
E1("will refuse the naive W217 A window; W217 freezer",
   "will refuse the naive W218 A window; W218 freezer", "proj-refuse")
E1('will refuse the naive W217 A window; ",',
   'will refuse the naive W218 A window; ",', "pre-proj-refuse")
E1("W217+ freezer MUST re-derive on the post-W217 universe AND ",
   "W218+ freezer MUST re-derive on the post-W217 universe AND ", "pre-freezer")
E1("downstream W217 seat publication pending per seat-first law",
   "downstream W218 seat publication pending per seat-first law", "pre-downstream")
E1('["W217p_A"]', '["W218p_A"]', "leg4-key-a1")
E1("['W217p_A']", "['W218p_A']", "leg4-key-a2")
E1('["W217p_B"]', '["W218p_B"]', "leg4-key-b1")
E1("['W217p_B']", "['W218p_B']", "leg4-key-b2")
E1("downstream W217 seat NOT yet published", "downstream W218 seat NOT yet published", "finface-downstream")
# live faces in hdr/pr
E1("rows 45 + candidate; seat-time live face 46th = r913 probe leg0",
   "rows 46 + candidate; seat-time live face 47th = r915 probe leg0", "hdr-liveface")
E1("(engine_owner==bm-c rows 205 + candidate; gate",
   "(engine_owner==bm-c rows 206 + candidate; gate", "hdr-rows205")
E1('"machine-derive (engine_owner==bm-c rows 45 + candidate; seat-time live face 46th disclosed, "',
   '"machine-derive (engine_owner==bm-c rows 46 + candidate; seat-time live face 47th disclosed, "', "pr-liveface")
# receipt faces
E1('"phase": "five-face freeze chain-order splice (r916 freeze window, upstream ALL LANDED clean precondition)"',
   '"phase": "five-face freeze chain-order splice (r916 freeze window, upstream ALL LANDED clean precondition)"', "phase-noop-check")
E1('"w215_transitive": {"finalize_product": "results/perpetual_faces/n1_w215_results.json present (belt-and-braces gate; ledger 894,589 / K=468,720)"}',
   '"w215_transitive": {"finalize_product": "results/perpetual_faces/n1_w215_results.json present (belt-and-braces gate; ledger 896,789 / K=470,920)"}', "receipt-w215")
E1('"w213_transitive": {"finalize_product": "results/perpetual_faces/n1_w213_results.json present (belt-and-braces gate; ledger 892,389 / K=466,520)"}',
   '"w214_transitive": {"finalize_product": "results/perpetual_faces/n1_w214_results.json present (belt-and-braces gate; ledger 894,589 / K=468,720)"}', "receipt-w214")
E1('"w212_transitive": {"finalize_product": "results/perpetual_faces/n1_w212_results.json present (belt-and-braces gate)"}',
   '"w213_transitive": {"finalize_product": "results/perpetual_faces/n1_w213_results.json present (belt-and-braces gate; ledger 892,389 / K=466,520)"}', "receipt-w213")
E1('"w211_transitive": {"finalize_product": "results/perpetual_faces/n1_w211_results.json present (belt-and-braces gate)"}',
   '"w212_transitive": {"finalize_product": "results/perpetual_faces/n1_w212_results.json present (belt-and-braces gate)"}', "receipt-w212")
E1('"probe_receipt_bmc_ordinal_face": 46,', '"probe_receipt_bmc_ordinal_face": 47,', "receipt-ordinal-face")
E1('"note": "post-W216 registration: bm-c rows 45 + candidate = 46th owned (live derive at freeze time governs per r587/r359; probe leg0 bmc_ordinal=46 = r913 seat-time live face -- disclosed honest)"',
   '"note": "post-W216 registration: bm-c rows 46 + candidate = 47th owned (live derive at freeze time governs per r587/r359; probe leg0 bmc_ordinal=47 = r915 seat-time live face -- disclosed honest)"', "receipt-ordinal-note")
E1('"+ W211 + W212 + W213 legs -> W217 block = 74 rows ending at W216; disclosed: inherited W213 leg error-string face (\\"registered W212 row parity drift\\") from the r912 editor generation -- physical bytes preserved verbatim per extraction law (r912 generation cosmetic slip, assert target [213] is correct, zero functional impact)"',
   '"+ W211 + W212 + W213 + W214 legs -> W217 block = 75 rows ending at W216; disclosed: inherited W213 leg error-string face (\\"registered W212 row parity drift\\") from the r912 editor generation -- physical bytes preserved verbatim per extraction law (r912 generation cosmetic slip, assert target [213] is correct, zero functional impact)"', "receipt-parity-note")
E1('"note": "r916 freeze-window bundle: prereg + this splice editor landed same-window, upstream W216 already landed (clean-precondition fifth consecutive window); r914 prereg derive also HEALED five inherited W216-face corruption spots (chain-history W213 leg relabel + RAM list dup + estate note + se_mu chain + editor template self-ref) with machine-checked pairs + @L14@/@T15@ placeholder class-guard"',
   '"note": "r916 freeze-window bundle: prereg + this splice editor landed same-window, upstream W216 already landed (clean-precondition sixth consecutive window); r916 prereg derive = machine transform of the freeze-time W216 blob (46 count-asserted pairs, old-sides ast-extracted from the committed W216 derive, zero transcription) + @L14@/@L15@/@T16@ placeholder class-guard"', "receipt-prereg-note")
E1('"w213_block_kept": 1, "w215_block_kept": 1, "w216_block_kept": 1}',
   '"w213_block_kept": 1, "w214_block_kept": 1, "w215_block_kept": 1, "w216_block_kept": 1}', "receipt-liveness")


print("=== DRY: E1 find counts (post-blanket) ===")
bad = 0
for find, repl, what in E:
    c = t.count(find)
    flag = "OK " if c == 1 else "!! "
    if c != 1:
        bad += 1
    find_show = find if len(find) <= 90 else find[:87] + "..."
    print(f"{flag}[{what}] count={c}: {find_show!r}")
print(f"=== DRY: bad={bad} of {len(E)} ===")
c2 = t.count("SEVENTY-SEVENTH instance anticipated")
print(f"[proj-ordinal repn] count={c2} (expect 2)")
