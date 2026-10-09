# -*- coding: utf-8 -*-
"""r915 bm-a W197 five-face freeze edits (five faces: pf N1_BANDS row +
n1 WAVE_CONFIGS row + n1 materializer face + n1 selftest claim + seat
MSG already-archived verification face). Direct-author per the
r909/r912 physical chunk-roll machinery, rolled ONE generation:
extract current W196 fragments, roll W196->W197 with count-asserted
replacements, insert ADDITIVELY after the last registered row;
originals byte-identical zero-destroy. The replacement pair old-sides
are DERIVED AT RUNTIME from the r912 script's own AST lists (zero
transcription, r587); only the W197 fact substitutions are curated
here.

Facts machine-read never transcribed (r587): ADMIT receipt
results/_r914bma_w197_probe_receipt.json (bands A 448204..450203 /
B 450204..450403, hops 1/1, FIFTY-SEVENTH staircase, leg0 rows 194
tail W196 owner_rows 186 bma_rows 111 ordinal 187 bma_ordinal 112
w196_ledger_head 845545, leg2 conflicts 0, leg3 origin vacancy, leg4
W198+ projection A 450204..452203 / B 450404..450603 hops 0/0
B-inside-A). Seat push c59843acb (MSG-2026-10-09-1159-bma-w197-seat +
probe script + receipt, 3-item, r914 seat push, ancestor-verified).
W196=bm-a r912 five-face freeze landed origin 02cf6b44d, burn
COMPLETE 12/12, finalize LANDED r913 one-pass (ledger 845,545 EXACT
zero-deviation, K=429,120 EXACT, four pred keys PASS) -- ZERO
in-flight upstream seats, clean precondition freeze window. Seat MSG
archive state = ALREADY LANDED at the seat round r914 closeout
(fleet/inbox/processed/, self-acked per the S7 inbox-processing
law; honest per frozen prereg sec.0 -- the W196-style
archive-pending pattern does not apply; archive faces adapted).

Laws honored: r511/r687 write-time fetch + origin-tail vacancy lock;
r560 insert-after-last-registered-row + anti-vanish + before/after
counts; r370 EOL-adaptive anchors; r580/r581 AST + py_compile gate;
r581 multi-line assert messages paren-wrapped; r578 five-segment PASS
prints; r776 fragment-needle law (physical dumps
results/_r915bma_w197_face_*.txt, re-verified against the live files
at run time); r780/r781 verify-separation (all stale+presence asserts
in memory BEFORE any write); r666 safe write order (n1 first, then
pf). Dry-run by default; --write performs the live writes."""
import ast
import json
import os
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
N1P = os.path.join(ROOT, "scripts", "perpetual_faces_n1.py")
PFP = os.path.join(ROOT, "scripts", "perpetual_faces.py")
R912 = os.path.join(ROOT, "results", "_r912bma_w196_freeze_edits.py")
RCPT = os.path.join(ROOT, "results", "_r914bma_w197_probe_receipt.json")
OUT_RCPT = os.path.join(ROOT, "results", "_r915bma_w197_freeze_receipt.json")
SEAT_ARCHIVED = "fleet/inbox/processed/MSG-2026-10-09-1159-bma-w197-seat.md"
PREREG = os.path.join(ROOT, "research", "PERPETUAL_N1_W197_PREREG.md")
SEAT_SHA = "c59843acb"
CNW = getattr(subprocess, "CREATE_NO_WINDOW", 0)
WRITE = "--write" in sys.argv
fails = []


def git_out(args):
    p = subprocess.run([r"C:\Program Files\Git\cmd\git.exe", "-C", ROOT]
                       + args, capture_output=True, creationflags=CNW)
    return (p.returncode, p.stdout.decode("utf-8", "replace"),
            p.stderr.decode("utf-8", "replace"))


def rep(text, old, new, expect, tag):
    n = text.count(old)
    if n != expect:
        fails.append("REPLACEMENT COUNT MISMATCH [%s]: got %d expect %d"
                     " literal=%r" % (tag, n, expect, old[:100]))
        return text
    return text.replace(old, new)


def extract_r912_lists():
    src = open(R912, encoding="utf-8").read()
    tree = ast.parse(src)
    out = {}
    for node in ast.walk(tree):
        if (isinstance(node, ast.Assign) and len(node.targets) == 1
                and isinstance(node.targets[0], ast.Name)
                and node.targets[0].id in ("R", "RC", "RP", "RQ")
                and isinstance(node.value, ast.List)):
            out[node.targets[0].id] = [ast.literal_eval(e)
                                       for e in node.value.elts]
    assert set(out) == {"R", "RC", "RP", "RQ"}, "r912 lists missing: %s" % sorted(out)
    return out


# ---- W197 fact substitution rules (applied to the r912 new-sides) ----
RULES_MAT = [
    ("# --- W196 materializer face (r912 bm-a freeze, own-series law",
     "# --- W197 materializer face (r915 bm-a freeze, own-series law"),
    ("one-hundred-eleventh owned", "one-hundred-twelfth owned"),
    ("rows 110 + candidate); wave 195 = first free number after",
     "rows 111 + candidate); wave 196 = first free number after"),
    ("the REGISTERED W195 row (bm-a r909 freeze b9b962672) --",
     "the REGISTERED W196 row (bm-a r912 freeze 02cf6b44d) --"),
    ("(W2..W195 all registered). Seat", "(W2..W196 all registered). Seat"),
    ("MSG-2026-10-09-1007-bma-w196-seat pushed",
     "MSG-2026-10-09-1159-bma-w197-seat pushed"),
    ("to origin 01992cd42 BEFORE this freeze",
     "to origin c59843acb BEFORE this freeze"),
    ("the W195 finalize product already on origin since r910, not",
     "the W196 finalize product already on origin since r913, not"),
    ("at fetch (r910 seat push), zero merge, zero",
     "at fetch (r914 seat push), zero merge, zero"),
    ("ONE HUNDRED-AND-NINETY-SIXTH engine wave BY",
     "ONE HUNDRED-AND-NINETY-SEVENTH engine wave BY"),
    ("MACHINE-DERIVE (engine_owner rows 185 + candidate; gate",
     "MACHINE-DERIVE (engine_owner rows 186 + candidate; gate"),
    ("W1..W195 finalize ALL LANDED (net chain head 843,345,",
     "W1..W196 finalize ALL LANDED (net chain head 845,545,"),
    ("K=426,920 merged pool; W195 finalize one-pass bm-a r910)",
     "K=429,120 merged pool; W196 finalize one-pass bm-a r913)"),
    ("always on. ADMIT receipt results/_r910bma_w196_probe_receipt.json;",
     "always on. ADMIT receipt results/_r914bma_w197_probe_receipt.json;"),
    ("not a re-pick (R250: W196 bands were",
     "not a re-pick (R250: W197 bands were"),
    ("    _set_wave(196)", "    _set_wave(197)"),
    ('WAVE_CONFIGS[195]["a_seed_base"] == pf.N1_BANDS[195]["a"][0]',
     'WAVE_CONFIGS[196]["a_seed_base"] == pf.N1_BANDS[196]["a"][0]'),
    ('"W196 A band drift vs law mirror"', '"W197 A band drift vs law mirror"'),
    ('WAVE_CONFIGS[195]["b_exit_seed_base"] ==',
     'WAVE_CONFIGS[196]["b_exit_seed_base"] =='),
    ('pf.N1_BANDS[195]["b_exit"][0], "W196 B band drift vs law mirror"',
     'pf.N1_BANDS[196]["b_exit"][0], "W197 B band drift vs law mirror"'),
    ('WAVE_CONFIGS[195].get("engine_owner") ==',
     'WAVE_CONFIGS[196].get("engine_owner") =='),
    ('pf.N1_BANDS[195].get("engine_owner") == "bm-a"',
     'pf.N1_BANDS[196].get("engine_owner") == "bm-a"'),
    ('"W196 engine_owner drift (law mirror parity)"',
     '"W197 engine_owner drift (law mirror parity)"'),
    ("w195_a", "w196_a"),
    ("w195_b", "w196_b"),
    ('"W196 A/B band overlap"', '"W197 A/B band overlap"'),
    ('"W196 hits SEED_REGISTRY"', '"W197 hits SEED_REGISTRY"'),
    ('f"W196 {nm} hits v1"', 'f"W197 {nm} hits v1"'),
    ('f"W196 {nm} hits W1"', 'f"W197 {nm} hits W1"'),
    ('f"W196 {nm} hits probe seeds"', 'f"W197 {nm} hits probe seeds"'),
    ("# prior-wave disjointness W2..W195 (single state: all",
     "# prior-wave disjointness W2..W196 (single state: all"),
    ("WAVE_CONFIGS if w < 196):", "WAVE_CONFIGS if w < 197):"),
    ('f"W196 A hits W{wprev}"', 'f"W197 A hits W{wprev}"'),
    ('f"W196 B hits W{wprev}"', 'f"W197 B hits W{wprev}"'),
    ("n3r1_used195", "n3r1_used196"),
    ('"W196 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"',
     '"W197 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"'),
    ('"W196 bands must clear the lfc actual draw range"',
     '"W197 bands must clear the lfc actual draw range"'),
    ('"W196 bands must clear the options_wave2 actual draw range"',
     '"W197 bands must clear the options_wave2 actual draw range"'),
    ("# band facts (law sec.4 W196 row, r795): A = FIRST-CLEAN past",
     "# band facts (law sec.4 W197 row, r795): A = FIRST-CLEAN past"),
    ("# the registered W195 B band (the arithmetic continuation",
     "# the registered W196 B band (the arithmetic continuation"),
    ("# 445_804..447_803 is REFUSED at its own start by the W195",
     "# 448_004..450_003 is REFUSED at its own start by the W196"),
    ("# B band 445_804..446_003, exactly as the W195 prereg sec5.5 +",
     "# B band 448_004..448_203, exactly as the W196 prereg sec5.5 +"),
    ("# bm-a r907 probe leg4 succession projection notes",
     "# bm-a r910 probe leg4 succession projection notes"),
    ("# 446_004..448_003; A base == prior-wave B tail+1 (446_003+1)",
     "# 448_204..450_203; A base == prior-wave B tail+1 (448_203+1)"),
    ("-- A-hops-prior-B staircase FIFTY-SIXTH",
     "-- A-hops-prior-B staircase FIFTY-SEVENTH"),
    ("# continuation 446_004..446_203 is CLEAN on the registered",
     "# continuation 448_204..448_403 is CLEAN on the registered"),
    ("# universe but lands INSIDE the W196 A band window --",
     "# universe but lands INSIDE the W197 A band window --"),
    ("# 448_004 and lands 448_004..448_203, hops=1, non-rotational",
     "# 450_204 and lands 450_204..450_403, hops=1, non-rotational"),
    ("# (448_003+1) machine-checkable; cross-window convergence",
     "# (450_203+1) machine-checkable; cross-window convergence"),
    ("# with the W195 prereg sec5.5 + bm-a r907 probe leg4",
     "# with the W196 prereg sec5.5 + bm-a r910 probe leg4"),
    ("# honored (post-W195 universe re-derive + own-wave A",
     "# honored (post-W196 universe re-derive + own-wave A"),
    ("# reservation when deriving B); seat MSG-1007 tail,",
     "# reservation when deriving B); seat MSG-1159 tail,"),
    ('assert WAVE_CONFIGS[196]["a_seed_base"] == 446_004 == 446_003 + 1, (',
     'assert WAVE_CONFIGS[197]["a_seed_base"] == 448_204 == 448_203 + 1, ('),
    ('"W196 A must be the first-clean window past the registered "',
     '"W197 A must be the first-clean window past the registered "'),
    ('"W195 B band tail 446_003+1 (arithmetic continuation "',
     '"W196 B band tail 448_203+1 (arithmetic continuation "'),
    ('"445_804..447_803 REFUSED at its own start by the W195 B "',
     '"448_004..450_003 REFUSED at its own start by the W196 B "'),
    ('"band 445_804..446_003, exactly as the W195 prereg sec5.5 + "',
     '"band 448_004..448_203, exactly as the W196 prereg sec5.5 + "'),
    ('"bm-a r907 probe leg4 succession projection notes "',
     '"bm-a r910 probe leg4 succession projection notes "'),
    ('"staircase FIFTY-SIXTH instance, E36 card)")',
     '"staircase FIFTY-SEVENTH instance, E36 card)")'),
    ("arith_a195 = set(range(446_004, 448_004))",
     "arith_a196 = set(range(448_204, 450_204))"),
    ("assert not (arith_a195 & reg_ints), \\",
     "assert not (arith_a196 & reg_ints), \\"),
    ('"W196 A window must be CLEAN (first-clean ADMIT face past prior-wave B)"',
     '"W197 A window must be CLEAN (first-clean ADMIT face past prior-wave B)"'),
    ('assert WAVE_CONFIGS[196]["b_exit_seed_base"] == 448_004 == 448_003 + 1, (',
     'assert WAVE_CONFIGS[197]["b_exit_seed_base"] == 450_204 == 450_203 + 1, ('),
    ('"W196 B must be the first-clean window past the own-wave A "',
     '"W197 B must be the first-clean window past the own-wave A "'),
    ('"band tail 448_003+1 (arithmetic continuation "',
     '"band tail 450_203+1 (arithmetic continuation "'),
    ('"446_004..446_203 CLEAN on the registered universe but "',
     '"448_204..448_403 CLEAN on the registered universe but "'),
    ('"lands INSIDE the W196 A band window; same-freeze mutual "',
     '"lands INSIDE the W197 A band window; same-freeze mutual "'),
    ('"own-wave A window reserved jumps to 448_004, first-clean "',
     '"own-wave A window reserved jumps to 450_204, first-clean "'),
    ("arith_b195 = set(range(448_004, 448_204))",
     "arith_b196 = set(range(450_204, 450_404))"),
    ("assert not (arith_b195 & reg_ints), \\",
     "assert not (arith_b196 & reg_ints), \\"),
    ('"W196 B window must be CLEAN (first-clean ADMIT face past own-wave A)"',
     '"W197 B window must be CLEAN (first-clean ADMIT face past own-wave A)"'),
    ("assert not (arith_b195 & arith_a195), \\",
     "assert not (arith_b196 & arith_a196), \\"),
    ('"W196 A/B same-freeze mutual exclusion (B hops past own A)"',
     '"W197 A/B same-freeze mutual exclusion (B hops past own A)"'),
    ('assert _entry_shard_of(0, 12) == ("PERPETUAL-N1-W196-SHARD-0",',
     'assert _entry_shard_of(0, 12) == ("PERPETUAL-N1-W197-SHARD-0",'),
    ('"n1w196-0of12"), "W196 entry identity"',
     '"n1w197-0of12"), "W197 entry identity"'),
    ('assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W196-SHARD-11",',
     'assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W197-SHARD-11",'),
    ('"n1w196-11of12")', '"n1w197-11of12")'),
    ('assert SHARD_DIR.endswith("n1_w196") and OUT.endswith(',
     'assert SHARD_DIR.endswith("n1_w197") and OUT.endswith('),
    ('"n1_w196_results.json"), "W196 path drift"',
     '"n1_w197_results.json"), "W197 path drift"'),
    ('f"W196 shard dir collides with W{wprev}"',
     'f"W197 shard dir collides with W{wprev}"'),
    ("# W196 finalize cumulative deps: W17..W195 outputs ALL PRESENT",
     "# W197 finalize cumulative deps: W17..W196 outputs ALL PRESENT"),
    ("# (landed net chain head 843,345 = W195 bm-a r910 one-pass)",
     "# (landed net chain head 845,545 = W196 bm-a r913 one-pass)"),
    ("for _depw in range(17, 196):", "for _depw in range(17, 197):"),
    ('f"W196 finalize cumulative dep (W{_depw} output) missing"',
     'f"W197 finalize cumulative dep (W{_depw} output) missing"'),
    ("# registered wave below 196 composes; wave 15 excluded by",
     "# registered wave below 197 composes; wave 15 excluded by"),
    ("# design; SINGLE STATE (W2..W195 all registered -- no",
     "# design; SINGLE STATE (W2..W196 all registered -- no"),
    ("assert sorted(w for w in WAVE_CONFIGS if w < 196) == \\",
     "assert sorted(w for w in WAVE_CONFIGS if w < 197) == \\"),
    ("[w for w in range(16, 196)], \\", "[w for w in range(16, 197)], \\"),
    ('"W196 prior-wave set must derive from registry keys (no 15; " \\',
     '"W197 prior-wave set must derive from registry keys (no 15; " \\'),
    ('"W2..W195 registered single state)"', '"W2..W196 registered single state)"'),
    ('"research", "PERPETUAL_N1_W196_PREREG.md")), \\',
     '"research", "PERPETUAL_N1_W197_PREREG.md")), \\'),
    ('"W196 per-wave prereg missing (materializer requirement)"',
     '"W197 per-wave prereg missing (materializer requirement)"'),
]

RULES_CFG = [
    ('196: {"batch": "PERPETUAL-N1-W196",', '197: {"batch": "PERPETUAL-N1-W197",'),
    ('PERPETUAL_N1_W196_PREREG.md (wave-level frozen',
     'PERPETUAL_N1_W197_PREREG.md (wave-level frozen'),
    ('ONE HUNDRED-AND-NINETY-SIXTH ENGINE-OWNED WAVE',
     'ONE HUNDRED-AND-NINETY-SEVENTH ENGINE-OWNED WAVE'),
    ('engine_owner rows 185 + candidate), ',
     'engine_owner rows 186 + candidate), '),
    ('number law after the REGISTERED W195 row bm-a r909 freeze ',
     'number law after the REGISTERED W196 row bm-a r912 freeze '),
    ('b9b962672, SINGLE STATE zero seat gap W2..W195 all ',
     '02cf6b44d, SINGLE STATE zero seat gap W2..W196 all '),
    ('registered; W1..W195 finalize ALL LANDED (W195 bm-a r910 ',
     'registered; W1..W196 finalize ALL LANDED (W196 bm-a r913 '),
    ('one-pass, ledger head 843,345, merged pool K=426,920) -- ',
     'one-pass, ledger head 845,545, merged pool K=429,120) -- '),
    ('MSG-2026-10-09-1007-bma-w196-seat PUSHED to origin 01992cd42 ',
     'MSG-2026-10-09-1159-bma-w197-seat PUSHED to origin c59843acb '),
    ('(3-item; the W195 finalize product already on origin since r910, not re-shipped; W146 precedent); ',
     '(3-item; the W196 finalize product already on origin since r913, not re-shipped; W146 precedent); '),
    ('at fetch (r910 seat push), zero merge, zero ',
     'at fetch (r914 seat push), zero merge, zero '),
    ('engine_owner=bm-a, wave 195: ', 'engine_owner=bm-a, wave 196: '),
    ('"A = FIRST-CLEAN past the registered W195 B band (the "',
     '"A = FIRST-CLEAN past the registered W196 B band (the "'),
    ('"arithmetic continuation 445_804..447_803 is REFUSED at its "',
     '"arithmetic continuation 448_004..450_003 is REFUSED at its "'),
    ('"own start by the W195 B band 445_804..446_003, exactly as "',
     '"own start by the W196 B band 448_004..448_203, exactly as "'),
    ('"the W195 prereg sec5.5 + bm-a r907 probe leg4 succession "',
     '"the W196 prereg sec5.5 + bm-a r910 probe leg4 succession "'),
    ('"446_004..448_003; A base == prior-wave B tail+1 "',
     '"448_204..450_203; A base == prior-wave B tail+1 "'),
    ('"machine-checkable = A-hops-prior-B staircase FIFTY-SIXTH "',
     '"machine-checkable = A-hops-prior-B staircase FIFTY-SEVENTH "'),
    ('"arithmetic continuation 446_004..446_203 is CLEAN on the "',
     '"arithmetic continuation 448_204..448_403 is CLEAN on the "'),
    ('"registered universe but lands INSIDE the W196 A band "',
     '"registered universe but lands INSIDE the W197 A band "'),
    ('"jumps to 448_004, first-clean 448_004..448_203 hops=1, "',
     '"jumps to 450_204, first-clean 450_204..450_403 hops=1, "'),
    ('"convergence with the W195 prereg sec5.5 + bm-a r907 probe leg4 + "',
     '"convergence with the W196 prereg sec5.5 + bm-a r910 probe leg4 + "'),
    ('"r910 probe succession projection notes re-derived -- all "',
     '"r914 probe succession projection notes re-derived -- all "'),
    ('"MANDATORY notes honored (post-W195 universe re-derive + "',
     '"MANDATORY notes honored (post-W196 universe re-derive + "'),
    ('"results/_r910bma_w196_probe_receipt.json; W197+ projection "',
     '"results/_r914bma_w197_probe_receipt.json; W198+ projection "'),
    ('"per this window gate: A first-clean 448_004..450_003 "',
     '"per this window gate: A first-clean 450_204..452_203 "'),
    ('"CLEAN / B first-clean 448_204..448_403 CLEAN -- naive "',
     '"CLEAN / B first-clean 450_404..450_603 CLEAN -- naive "'),
    ('"W196 B band 448_004..448_203 will refuse the naive "',
     '"W197 B band 450_204..450_403 will refuse the naive "'),
    ('"W197 A window; W197 freezer MUST re-derive on the "',
     '"W198 A window; W198 freezer MUST re-derive on the "'),
    ('"post-W196 universe AND reserve the own-wave A window "',
     '"post-W197 universe AND reserve the own-wave A window "'),
    ('W1..W195 finalize ALL LANDED (W195 "', 'W1..W196 finalize ALL LANDED (W196 "'),
    ('"finalize one-pass bm-a r910, net chain head 843,345, "',
     '"finalize one-pass bm-a r913, net chain head 845,545, "'),
    ('"merged pool K=426,920) -- ZERO in-flight upstream "',
     '"merged pool K=429,120) -- ZERO in-flight upstream "'),
    ('"a_seed_base": 446_004,        # law sec.4 W196 A: 446_004..448_003 (FIRST-CLEAN past the registered W195 B band; arithmetic 445_804..447_803 REFUSED at own start by the W195 B band 445_804..446_003; hops=1; A-hops-prior-B staircase FIFTY-SIXTH instance, E36 card; ordinal convergence per r587: W195 prereg sec5.5 prose anticipated fifty-sixth, r910 receipt machine-read FIFTY-SIXTH)',
     '"a_seed_base": 448_204,        # law sec.4 W197 A: 448_204..450_203 (FIRST-CLEAN past the registered W196 B band; arithmetic 448_004..450_003 REFUSED at own start by the W196 B band 448_004..448_203; hops=1; A-hops-prior-B staircase FIFTY-SEVENTH instance, E36 card; ordinal convergence per r587: W196 prereg sec5.5 prose anticipated fifty-seventh, r914 receipt machine-read FIFTY-SEVENTH)'),
    ('"b_exit_seed_base": 448_004,   # law sec.4 W196 B: 448_004..448_203 (FIRST-CLEAN past the own-wave A window; arithmetic 446_004..446_203 lands inside own-A, same-freeze mutual exclusion W141 precedent; reserved walk hops=1; B base == own-A tail+1)',
     '"b_exit_seed_base": 450_204,   # law sec.4 W197 B: 450_204..450_403 (FIRST-CLEAN past the own-wave A window; arithmetic 448_204..448_403 lands inside own-A, same-freeze mutual exclusion W141 precedent; reserved walk hops=1; B base == own-A tail+1)'),
    ('"shard_subdir": "n1_w196", "out_name": "n1_w196_results.json",',
     '"shard_subdir": "n1_w197", "out_name": "n1_w197_results.json",'),
]

RULES_PF = [
    ('# W196 (bm-a r912 freeze, seat MSG-2026-10-09-1007-bma-w196-seat',
     '# W197 (bm-a r915 freeze, seat MSG-2026-10-09-1159-bma-w197-seat'),
    ('# pushed to origin 01992cd42 pre-freeze r565 law (r910 seat',
     '# pushed to origin c59843acb pre-freeze r565 law (r914 seat'),
    ('# (3-item; the W195 finalize product already on origin since r910,',
     '# (3-item; the W196 finalize product already on origin since r913,'),
    ('# = direct fast-forward behind-0 at fetch (r910 seat push),',
     '# = direct fast-forward behind-0 at fetch (r914 seat push),'),
    ('# band gate ADMIT results/_r910bma_w196_probe_receipt.json: A = FIRST-CLEAN',
     '# band gate ADMIT results/_r914bma_w197_probe_receipt.json: A = FIRST-CLEAN'),
    ('# past the registered W195 B band (arithmetic continuation',
     '# past the registered W196 B band (arithmetic continuation'),
    ('# 445_804..447_803 REFUSED at its own start by the W195 B band',
     '# 448_004..450_003 REFUSED at its own start by the W196 B band'),
    ('# 445_804..446_003, exactly as the W195 prereg sec5.5 + bm-a r907 probe',
     '# 448_004..448_203, exactly as the W196 prereg sec5.5 + bm-a r910 probe'),
    ('# honest forward walk hops=1 -> 446_004..448_003, non-rotational',
     '# honest forward walk hops=1 -> 448_204..450_203, non-rotational'),
    ('# (446_003+1) machine-checkable -- A-hops-prior-B staircase',
     '# (448_203+1) machine-checkable -- A-hops-prior-B staircase'),
    ('# FIFTY-SIXTH instance, E36 card);', '# FIFTY-SEVENTH instance, E36 card);'),
    ('# continuation 446_004..446_203 CLEAN on the registered universe',
     '# continuation 448_204..448_403 CLEAN on the registered universe'),
    ('# but lands INSIDE the W196 A band window -- same-freeze mutual',
     '# but lands INSIDE the W197 A band window -- same-freeze mutual'),
    ('# own-wave A window reserved jumps to 448_004 -> 448_004..448_203,',
     '# own-wave A window reserved jumps to 450_204 -> 450_204..450_403,'),
    ('# own-wave A tail+1 (448_003+1) machine-checkable);',
     '# own-wave A tail+1 (450_203+1) machine-checkable);'),
    ('# W197+ projection (gate-derived r910): A first-clean',
     '# W198+ projection (gate-derived r914): A first-clean'),
    ('# 448_004..450_003 CLEAN hops=0 / B first-clean 448_204..448_403',
     '# 450_204..452_203 CLEAN hops=0 / B first-clean 450_404..450_603'),
    ('# registered W196 B band 448_004..448_203 will refuse the naive',
     '# registered W197 B band 450_204..450_403 will refuse the naive'),
    ('# W197 A window; W197 freezer MUST re-derive on the post-W196',
     '# W198 A window; W198 freezer MUST re-derive on the post-W197'),
    ('# NOT a re-pick (R250: W196 bands were never assigned).',
     '# NOT a re-pick (R250: W197 bands were never assigned).'),
    ('196: {"a": (446_004, 448_003), "b_exit": (448_004, 448_203),',
     '197: {"a": (448_204, 450_203), "b_exit": (450_204, 450_403),'),
]

RULES_CLAIM = [
    ('"+ W196 materializer face [same guard set, dep=W17..W195 "',
     '"+ W197 materializer face [same guard set, dep=W17..W196 "'),
    ('"outputs ALL PRESENT (landed net chain head 843,345 = "',
     '"outputs ALL PRESENT (landed net chain head 845,545 = "'),
    ('"W195 bm-a r910 one-pass, K=426,920 merged pool) -- ZERO "',
     '"W196 bm-a r913 one-pass, K=429,120 merged pool) -- ZERO "'),
    ('"in-flight upstream seats, clean precondition, ONE HUNDRED-AND-NINETY-SIXTH "',
     '"in-flight upstream seats, clean precondition, ONE HUNDRED-AND-NINETY-SEVENTH "'),
    ('"ENGINE-OWNED WAVE BY MACHINE-DERIVE (engine_owner rows 185 "',
     '"ENGINE-OWNED WAVE BY MACHINE-DERIVE (engine_owner rows 186 "'),
    ("bm-a's one-hundred-eleventh owned claim per ",
     "bm-a's one-hundred-twelfth owned claim per "),
    ('"machine-derive (engine_owner==bm-a rows 110 + candidate), "',
     '"machine-derive (engine_owner==bm-a rows 111 + candidate), "'),
    ('"A=FIRST-CLEAN past the registered W195 B band (staircase "',
     '"A=FIRST-CLEAN past the registered W196 B band (staircase "'),
    ('"FIFTY-SIXTH instance, E36 card, hops=1) + B=FIRST-CLEAN past the "',
     '"FIFTY-SEVENTH instance, E36 card, hops=1) + B=FIRST-CLEAN past the "'),
    ('"results/_r910bma_w196_probe_receipt.json, law sec.4 W196 row, "',
     '"results/_r914bma_w197_probe_receipt.json, law sec.4 W197 row, "'),
    ('"r912 bm-a] "', '"r915 bm-a] "'),
]

# Archive-state honest adaptation (W197 seat MSG already archived at
# the r914 seat round per the S7 inbox-processing law; frozen prereg
# sec.0 anticipated the move WITH the freeze window -- it landed
# early, honest note per r587). These lines are NOT in the r912 pair
# lists (wave-agnostic there); supplied explicitly here.
DROP_IF = [
    "freeze-closeout archive move",
    "seat MSG sits in fleet/inbox/ at freeze time,",
    "archive PENDING WITH THIS freeze window -- bm-a r912 freeze",
    "closeout archive move (the W196 seat MSG sits in",
]
MAT_ARCHIVE = [
    ("    #     --no-verify; self-ack inbox->processed archive PENDING WITH",
     "    #     --no-verify; self-ack inbox->processed archive ALREADY", 1),
    ("    #     THIS freeze window -- bm-a r912 freeze-closeout archive move",
     "    #     LANDED at the seat round r914 closeout (the W197 seat MSG", 1),
    ("    #     (the W196 seat MSG sits in fleet/inbox/ at freeze time,",
     "    #     sits in fleet/inbox/processed/ at freeze time, self-acked", 1),
    ("    #     moves to processed/ with this window closeout, honest per",
     "    #     at the seat round S7 per the inbox-processing law, honest", 1),
    ("    #     frozen prereg sec.0).",
     "    #     per frozen prereg sec.0 -- W196 archive-pending N/A).", 1),
]
PF_ARCHIVE = [
    ("    # archive PENDING WITH THIS freeze window -- bm-a r912 freeze",
     "    # archive ALREADY LANDED at the seat round r914 closeout --", 1),
    ("    # closeout archive move (the W196 seat MSG sits in",
     "    # the W197 seat MSG sits in fleet/inbox/processed/ (self-acked", 1),
    ("    # fleet/inbox/ at freeze time, moves to processed/ with this",
     "    # per the S7 inbox-processing law at the seat round, honest", 1),
    ("    # window closeout, honest per frozen prereg sec.0);",
     "    # per frozen prereg sec.0 -- W196 archive-pending N/A);", 1),
]

STALE = {
    "mat197": ["01992cd42", "MSG-2026-10-09-1007", "r910 seat push",
               "_r910bma", "FIFTY-SIXTH", "445_804",
               "446_004..448_003", "446_004..446_203",
               "446_003+1", "448_003+1", '== "bm-c"',
               "one-hundred-eleventh", "rows 110 + candidate",
               "ONE HUNDRED-AND-NINETY-SIXTH", "W2..W195 all",
               "arith_a195", "arith_b195", "w195_a", "w195_b",
               "n3r1_used195", "W1..W195 finalize", "843,345",
               "426,920", "r912 freeze-closeout", "one-pass bm-a r910",
               "W195 bm-a r910 one-pass", "bm-a r907 probe",
               "post-W195 universe", "MSG-1007 tail",
               "range(17, 196)", "jumps to 448_004", "n1w196", "n1_w196",
               "W196-SHARD", "W196 entry", "W196 path drift",
               "W196 shard dir", "w < 196):", "W2..W195 registered",
               "PERPETUAL_N1_W196_PREREG", "W196 per-wave prereg",
               "W196 finalize cumulative dep", "W196 prior-wave set",
               "disjointness W2..W195", "W196 A/B band", "W196 hits",
               "W196 bands", "W196 A window must", "W196 B window must",
               "W196 A/B same-freeze", "W197+ projection",
               "W196 A band drift", "W196 B band drift",
               "W196 engine_owner drift", "r909 freeze", "b9b962672",
               "the W195 finalize product", "since r910",
               "PENDING WITH THIS freeze window",
               "moves to processed/ with this"],
    "cfg197": ["01992cd42", "MSG-2026-10-09-1007", "_r910bma",
               "FIFTY-SIXTH", "445_804", "446_004..448_003",
               "446_004..446_203", "446_003+1", "448_003+1",
               "W195 prereg sec5.5", "bm-a r907",
               "the W195 finalize product", "since r910",
               "ONE HUNDRED-AND-NINETY-SIXTH", "W2..W195 all",
               "W2..W195 registered", "engine_owner rows 185",
               "r910 seat push", "W197+ projection",
               "A first-clean 448_004..450_003",
               "B first-clean 448_204..448_403", "wave 195: ",
               "446_004,", "448_004,   #", "n1_w196", "W196-SHARD",
               "r909 freeze", "post-W195 universe",
               "W195 B band 445", "one-pass bm-a r910", "W195 bm-a r910",
               "b9b962672", "843,345", "426,920", "W1..W195 finalize"],
    "pf197": ["01992cd42", "MSG-2026-10-09-1007", "_r910bma",
              "FIFTY-SIXTH", "445_804", "445_804..447_803",
              "446_004..448_003", "446_004..446_203", "446_003+1",
              "448_003+1", "W197+ projection", "r910 seat",
              "gate-derived r910", "bm-a r907 probe",
              "W195 prereg sec5.5", "r912 freeze",
              "the W196 seat MSG sits", "W195 B band",
              "jumps to 448_004", "W197 freezer",
              "post-W196 universe AND", "the W195 finalize product",
              "since r910", "archive PENDING WITH THIS freeze window",
              "moves to processed/ with this"],
    "claim197": ["_r910bma", "FIFTY-SIXTH", "one-hundred-eleventh",
                 "rows 110 + candidate", "rows 185 ",
                 "r912 bm-a] ", "W195 B band",
                 "ONE HUNDRED-AND-NINETY-SIXTH",
                 "843,345", "426,920", "dep=W17..W195",
                 "W195 bm-a r910 one-pass"],
}


def apply_rules(text, rules, tag):
    for (a, b) in rules:
        if a in text:
            text = text.replace(a, b)
    return text


def roll_pairs(r912_list, rules, tag):
    """Derive W197 pairs from the r912 list: old side = r912's new side
    (AST-extracted, zero transcription), new side = rule-rolled."""
    pairs = []
    for (old, new, cnt) in r912_list:
        if any(d in new for d in DROP_IF):
            continue  # archive-state lines handled by explicit pairs
        w197 = apply_rules(new, rules, tag)
        if w197 == new:
            fails.append("UNCHANGED PAIR [%s]: %r" % (tag, new[:90]))
            continue
        pairs.append((new, w197, cnt))
    return pairs


def main():
    facts = {"round": 915, "machine": "bm-a", "wave": 197,
             "archive_state": "already-landed-r914 (processed/, S7 "
                              "inbox-processing law; prereg sec.0 move "
                              "landed early, honest note)"}

    # ---- G0 idempotence (already-applied abort) ----
    pf_probe = open(PFP, encoding="utf-8", errors="replace").read()
    if '197: {"a": (448_204, 450_203)' in pf_probe:
        print("ALREADY APPLIED: W197 pf row present -- abort")
        return 3

    # ---- G1 write-time fetch + origin tail lock (r511/r687) ----
    rc, _, err = git_out(["fetch", "origin"])
    assert rc == 0, "fetch failed: %s" % err[:200]
    rc, origin_pf, err = git_out(["show", "origin/main:scripts/perpetual_faces.py"])
    assert rc == 0, "origin pf blob read failed"
    assert "197: {" not in origin_pf, "ORIGIN TAIL MOVED: wave 197 already on origin"
    assert '196: {"a": (446_004, 448_003)' in origin_pf, "origin W196 row drift"
    rc, origin_n1, _ = git_out(["show", "origin/main:scripts/perpetual_faces_n1.py"])
    assert rc == 0
    assert "# --- W197 materializer face" not in origin_n1, "origin n1 W197 face present"
    assert '197: {"batch": "PERPETUAL-N1-W197"' not in origin_n1, \
        "origin n1 W197 cfg row present"
    rc, _, _ = git_out(["merge-base", "--is-ancestor", SEAT_SHA, "origin/main"])
    assert rc == 0, "seat push sha %s not an ancestor of origin/main" % SEAT_SHA
    facts["origin_vacancy"] = True

    # ---- G2 receipt + precheck parity (r587 / r359 machine numbers) ----
    r = json.load(open(RCPT, encoding="utf-8"))
    assert r["verdict"] == "ADMIT", "probe receipt not ADMIT"
    leg1 = r["legs"]["leg1"]
    A, B = leg1["A"], leg1["B"]
    assert A == [448204, 450203] and B == [450204, 450403], \
        "receipt bands drift: %s %s" % (A, B)
    assert leg1["hops_A"] == 1 and leg1["hops_B"] == 1
    assert leg1["ARITH_A"] == [448004, 450003] and \
        leg1["ARITH_B"] == [448204, 448403], "receipt arithmetic drift"
    assert r["bands"] == {"A": "448204_450203", "B": "450204_450403"}
    assert "FIFTY-SEVENTH" in leg1["A_semantics"], \
        "receipt A_semantics ordinal face missing"
    leg0 = r["legs"]["leg0"]
    assert leg0["rows"] == 194 and leg0["tail"] == "W196"
    assert leg0["ordinal"] == 187 and leg0["bma_ordinal"] == 112
    assert leg0["owner_rows"] == 186 and leg0["bma_rows"] == 111
    assert leg0["w196_ledger_head"] == 845545
    assert r["legs"]["leg2"]["conflicts"] == 0
    assert r["legs"]["leg3"]["origin_vacancy"] is True
    leg4 = r["legs"]["leg4"]
    assert leg4["W198p_A"] == "450204..452203" and \
        leg4["W198p_B"] == "450404..450603"
    assert leg4["hops_A"] == 0 and leg4["hops_B"] == 0
    assert leg4["W198p_B_lands_inside_W198p_A"] is True
    sys.path.insert(0, os.path.join(ROOT, "scripts"))
    from perpetual_faces import N1_BANDS  # noqa: E402
    assert max(N1_BANDS) == 196 and len(N1_BANDS) == 194, "registry tail drift"
    owners = {}
    for w, c in N1_BANDS.items():
        owners[c.get("engine_owner")] = owners.get(c.get("engine_owner"), 0) + 1
    owned = sum(v for k, v in owners.items() if k)
    assert owners.get("bm-a") == 111 and owners.get("bm-c") == 35 \
        and owned == 186, "owner counts drift: %s" % owners
    assert N1_BANDS[196] == {"a": (446004, 448003), "b_exit": (448004, 448203),
                            "engine_owner": "bm-a"}, "W196 row drift"
    assert N1_BANDS[195] == {"a": (443804, 445803), "b_exit": (445804, 446003),
                            "engine_owner": "bm-a"}, "W195 row drift"
    assert N1_BANDS[194] == {"a": (441604, 443603), "b_exit": (443604, 443803),
                            "engine_owner": "bm-a"}, "W194 row drift"
    assert os.path.exists(PREREG), "W197 per-wave prereg missing"
    assert os.path.exists(os.path.join(ROOT, SEAT_ARCHIVED)), \
        "seat MSG not in fleet/inbox/processed/ (already-archived state)"
    assert not os.path.exists(os.path.join(
        ROOT, "fleet", "inbox", "MSG-2026-10-09-1159-bma-w197-seat.md")), \
        "seat MSG double-present (inbox AND processed)"
    assert os.path.exists(os.path.join(
        ROOT, "results", "perpetual_faces", "n1_w196_results.json")), \
        "W196 finalize product missing (dep precondition)"
    for f in ("results/_r914bma_w197_probe.py",
              "results/_r914bma_w197_probe_receipt.json"):
        assert os.path.exists(os.path.join(ROOT, f)), \
            "seat-cited artifact missing: %s" % f
    facts["precheck"] = {"rows": len(N1_BANDS), "bma_rows": owners.get("bm-a"),
                         "bmc_rows": owners.get("bm-c"),
                         "bmb_rows": owners.get("bm-b"),
                         "owner_rows": owned}

    # ---- G3 read live files, EOL detect (r370) ----
    n1_raw = open(N1P, encoding="utf-8", errors="replace", newline="").read()
    pf_raw = open(PFP, encoding="utf-8", errors="replace", newline="").read()
    n1_crlf = n1_raw.count("\r\n") > n1_raw.count("\n") / 2
    pf_crlf = pf_raw.count("\r\n") > pf_raw.count("\n") / 2
    n1n = n1_raw.replace("\r\n", "\n")
    pfn = pf_raw.replace("\r\n", "\n")
    facts["eol"] = {"n1_crlf": n1_crlf, "pf_crlf": pf_crlf}

    # ---- G4 extract W196 chunks (LF face; r776 physical shapes) ----
    def chunk(text, start, end, stag):
        i = text.find(start)
        assert i >= 0, "start marker not found [%s]" % stag
        j = text.find(end, i)
        assert j > i, "end marker not found [%s]" % stag
        return text[i:j + len(end)]

    mat196 = chunk(n1n, "    # --- W196 materializer face",
                   "    _set_wave(2)", "mat196")
    assert mat196.rstrip("\n").endswith("_set_wave(2)"), "mat196 tail drift"
    cfg196 = chunk(n1n, '    196: {"batch": "PERPETUAL-N1-W196",',
                   '"engine_owner": "bm-a"},', "cfg196")
    pf196 = chunk(pfn, "    # W196 (bm-a r912 freeze, seat MSG-2026-10-09-1007-bma-w196-seat",
                  '"engine_owner": "bm-a"},', "pf196")
    claim196 = chunk(n1n, '          "+ W196 materializer face [same guard set',
                     '"r912 bm-a] "', "claim196")
    assert n1n.count(cfg196) == 1, "cfg196 not unique"
    assert n1n.count(claim196) == 1, "claim196 not unique"
    assert pfn.count(pf196) == 1, "pf196 not unique"
    for nm, frag in (("mat196", mat196), ("cfg196", cfg196),
                     ("pf196", pf196), ("claim196", claim196)):
        with open(os.path.join(ROOT, "results",
                               "_r915bma_w197_face_%s.txt" % nm),
                  "w", encoding="utf-8", newline="") as fh:
            fh.write(frag)
    facts["dump_sizes"] = {nm: len(frag) for nm, frag in
                           (("mat", mat196), ("cfg", cfg196),
                            ("pf", pf196), ("claim", claim196))}

    # ---- G5-G7 derive rolled pairs from the r912 bloodline AST ----
    L = extract_r912_lists()
    pairs_mat = roll_pairs(L["R"], RULES_MAT, "mat")
    pairs_cfg = roll_pairs(L["RC"], RULES_CFG, "cfg")
    pairs_pf = roll_pairs(L["RP"], RULES_PF, "pf")
    pairs_claim = roll_pairs(L["RQ"], RULES_CLAIM, "claim")
    facts["pair_counts"] = {"mat": len(pairs_mat), "cfg": len(pairs_cfg),
                            "pf": len(pairs_pf), "claim": len(pairs_claim),
                            "dropped_archive": (len(L["R"]) - len(pairs_mat))
                            + (len(L["RP"]) - len(pairs_pf))}
    m = mat196
    for k, (old, new, cnt) in enumerate(pairs_mat):
        m = rep(m, old, new, cnt, "mat-%02d" % k)
    for k, (old, new, cnt) in enumerate(MAT_ARCHIVE):
        m = rep(m, old, new, cnt, "mat-arch-%d" % k)
    mat197 = m
    c = cfg196
    for k, (old, new, cnt) in enumerate(pairs_cfg):
        c = rep(c, old, new, cnt, "cfg-%02d" % k)
    cfg197 = c
    p = pf196
    for k, (old, new, cnt) in enumerate(pairs_pf):
        p = rep(p, old, new, cnt, "pf-%02d" % k)
    for k, (old, new, cnt) in enumerate(PF_ARCHIVE):
        p = rep(p, old, new, cnt, "pf-arch-%d" % k)
    pf197 = p
    q = claim196
    for k, (old, new, cnt) in enumerate(pairs_claim):
        q = rep(q, old, new, cnt, "claim-%02d" % k)
    claim197 = q

    # ---- G7c stale sweeps on the rolled fragments (r780/r781) ----
    # NOTE: W196 band citations (the registered W196 B band
    # 448_004..448_203 and the W197 arithmetic continuations
    # 448_004..450_003 / 448_204..448_403) are LEGITIMATE content of
    # the W197 fragments (prior-wave face) -- they are NOT stale.
    frags = {"mat197": mat197, "cfg197": cfg197, "pf197": pf197,
             "claim197": claim197}
    for frag, stale_list in STALE.items():
        txt = frags[frag]
        for s in stale_list:
            if s in txt:
                fails.append("%s stale token remains: %r" % (frag, s[:60]))

    if fails:
        print("RESULT: FAIL (%d) -- zero writes" % len(fails))
        for f in fails:
            print("  -", f)
        return 1

    # ---- G8 insertions (r560 additive, after last registered row) ----
    IND19 = " " * 19
    n1_b = n1n.replace(cfg196, cfg196 + "\n" + IND19 + cfg197, 1)
    if n1_b == n1n:
        fails.append("cfg insertion no-op")
        print("RESULT: FAIL -- cfg insertion no-op")
        return 1
    w196_pos = n1_b.find("    # --- W196 materializer face")
    assert w196_pos >= 0
    t141 = n1_b.find("    # --- T-141 s2 lane face", w196_pos)
    assert t141 > w196_pos, "T-141 marker not found after W196 face"
    n1_c = n1_b[:t141] + mat197 + "\n" + n1_b[t141:]
    claim_anchor = claim196 + '\n          "+ T-141 s2 "'
    assert n1_c.count(claim_anchor) == 1, "claim anchor not unique"
    n1_final = n1_c.replace(claim_anchor,
                            claim196 + "\n" + claim197 +
                            '\n          "+ T-141 s2 "', 1)
    pf_final = pfn.replace(pf196, pf196 + "\n" + pf197, 1)
    if pf_final == pfn:
        fails.append("pf insertion no-op")

    # ---- G9 presence + anti-vanish + malformed scans (r560/r819) ----
    checks = [
        (n1_final, '197: {"batch": "PERPETUAL-N1-W197",', 1),
        (n1_final, '196: {"batch": "PERPETUAL-N1-W196",', 1),
        (n1_final, '195: {"batch": "PERPETUAL-N1-W195",', 1),
        (n1_final, '194: {"batch": "PERPETUAL-N1-W194",', 1),
        (n1_final, '193: {"batch": "PERPETUAL-N1-W193",', 1),
        (n1_final, "# --- W197 materializer face", 1),
        (n1_final, "# --- W196 materializer face", 1),
        (n1_final, "# --- W195 materializer face", 1),
        (n1_final, "# --- W194 materializer face", 1),
        (n1_final, "# --- W193 materializer face", 1),
        (n1_final, '"r915 bm-a] "', 1),
        (n1_final, '"r912 bm-a] "', 1),
        (n1_final, '"r909 bm-a] "', 1),
        (n1_final, '"r905 bm-a] "', 1),
        (n1_final, '"r901 bm-a] "', 1),
        (n1_final, '"r787 bm-c] "', 1),
        (n1_final, '"a_seed_base": 448_204,', 1),
        (n1_final, '"b_exit_seed_base": 450_204,', 1),
        (n1_final, "n1_w197", 4),
        (n1_final, "PERPETUAL_N1_W197_PREREG.md", 2),
        (n1_final, "_set_wave(197)", 1),
        (n1_final, 'sorted(w for w in WAVE_CONFIGS if w < 197)', 3),
        (n1_final, "range(17, 197):", 1),
        (n1_final, '"W198 A window; W198 freezer MUST re-derive on the "', 1),
        (n1_final, 'A first-clean 450_204..452_203 ', 1),
        (n1_final, "LANDED at the seat round r914 closeout (the W197 seat MSG", 1),
        (pf_final, '197: {"a": (448_204, 450_203), "b_exit": (450_204, 450_403),', 1),
        (pf_final, '196: {"a": (446_004, 448_003), "b_exit": (448_004, 448_203),', 1),
        (pf_final, '195: {"a": (443_804, 445_803), "b_exit": (445_804, 446_003),', 1),
        (pf_final, '194: {"a": (441_604, 443_603), "b_exit": (443_604, 443_803),', 1),
        (pf_final, '193: {"a": (439_404, 441_403), "b_exit": (441_404, 441_603),', 1),
        (pf_final, "# W197 (bm-a r915 freeze", 1),
        (pf_final, "# W196 (bm-a r912 freeze", 1),
        (pf_final, "# W195 (bm-a r909 freeze", 1),
        (pf_final, "# W194 (bm-a r905 freeze", 1),
        (pf_final, "# W198+ projection (gate-derived r914)", 1),
        (pf_final, "archive ALREADY LANDED at the seat round r914 closeout", 1),
    ]
    for src, needle, cnt in checks:
        got = src.count(needle)
        if got != cnt:
            fails.append("post-edit needle %r count %d != %d"
                         % (needle[:50], got, cnt))
    # W198+ projection prose present (probe leg4 verbatim, r587)
    for needle in ("# 450_204..452_203 CLEAN hops=0 / B first-clean 450_404..450_603",
                   "W198 A window; W198 freezer MUST re-derive on the post-W197"):
        if needle not in pf_final:
            fails.append("pf W198+ prose missing: %r" % needle[:60])
    pat = re.compile(r"(\d{3})_(\d{3})\.\.(\d{3})_(\d{3})")
    for name, txt in (("pf", pf_final), ("n1", n1_final)):
        bad = [mm.group() for mm in pat.finditer(txt)
               if int(mm.group(3)) < int(mm.group(1))]
        if bad:
            fails.append("%s malformed windows: %s" % (name, bad[:5]))
    # CR/LF hygiene: rolled fragments carry no CR and no triple-LF;
    # final outputs introduce ZERO NEW anomalies vs the originals.
    for frag, txt in frags.items():
        if "\r" in txt:
            fails.append("%s fragment carries a bare CR" % frag)
        if "\n\n\n" in txt:
            fails.append("%s fragment carries triple-LF" % frag)
    n1_out_probe = n1_final.replace("\n", "\r\n") if n1_crlf else n1_final
    pf_out_probe = pf_final.replace("\n", "\r\n") if pf_crlf else pf_final
    for name, out_txt, raw in (("n1", n1_out_probe, n1_raw),
                               ("pf", pf_out_probe, pf_raw)):
        for tok in ("\r\r", "\n\n\n"):
            if out_txt.count(tok) != raw.count(tok):
                fails.append("%s anomaly count DRIFT for %r: %d -> %d"
                             % (name, tok, raw.count(tok), out_txt.count(tok)))

    # ---- G9b AST gate (r580/r581) ----
    ast.parse(n1_final)
    ast.parse(pf_final)
    print("AST gate: both files parse OK")

    if fails:
        print("RESULT: FAIL at gates (%d) -- zero writes" % len(fails))
        for f in fails:
            print("  -", f)
        return 1

    if not WRITE:
        print("DRY-RUN PASS: all gates green, zero writes "
              "(rerun with --write to land)")
        with open(OUT_RCPT.replace(".json", "_dryrun.json"), "w",
                  encoding="utf-8") as fh:
            json.dump(facts, fh, indent=1, ensure_ascii=False)
        return 0

    # ---- G10 live writes (r666 safe order: n1 FIRST then pf) ----
    n1_out = n1_final.replace("\n", "\r\n") if n1_crlf else n1_final
    pf_out = pf_final.replace("\n", "\r\n") if pf_crlf else pf_final
    with open(N1P, "w", encoding="utf-8", newline="") as fh:
        fh.write(n1_out)
    with open(PFP, "w", encoding="utf-8", newline="") as fh:
        fh.write(pf_out)
    print("LIVE WRITES DONE: pf %d->%d B, n1 %d->%d B"
          % (len(pfn), len(pf_final), len(n1n), len(n1_final)))

    # ---- G11 py_compile + post-import guard ----
    for f in (N1P, PFP):
        prc = subprocess.run([sys.executable, "-m", "py_compile", f],
                             capture_output=True, creationflags=CNW)
        assert prc.returncode == 0, "py_compile failed: %s" % f
    chk = subprocess.run(
        [sys.executable, "-c",
         "import sys, json; sys.path.insert(0, 'scripts'); "
         "sys.path.insert(0, '.'); "
         "from perpetual_faces import N1_BANDS as B; "
         "import perpetual_faces_n1 as n1; "
         "cfg = n1.WAVE_CONFIGS[197]; "
         "print(json.dumps({'rows': len(B), 'w197': B.get(197), "
         "'w196': B.get(196), 'w195': B.get(195), 'w194': B.get(194), "
         "'cfg197': [cfg['a_seed_base'], cfg['b_exit_seed_base'], "
         "cfg['shard_subdir'], cfg['out_name'], cfg['engine_owner']]}))"],
        cwd=ROOT, capture_output=True, creationflags=CNW)
    assert chk.returncode == 0, "post-import check failed: %s" % chk.stderr[:300]
    post = json.loads(chk.stdout.decode("utf-8", "replace").strip().splitlines()[-1])
    assert post["rows"] == 195, "row count drift: %s" % post
    assert post["w197"] == {"a": [448204, 450203], "b_exit": [450204, 450403],
                           "engine_owner": "bm-a"}, "W197 row drift: %s" % post
    assert post["w196"] == {"a": [446004, 448003], "b_exit": [448004, 448203],
                           "engine_owner": "bm-a"}, "W196 row damaged: %s" % post
    assert post["w195"] == {"a": [443804, 445803], "b_exit": [445804, 446003],
                           "engine_owner": "bm-a"}, "W195 row damaged: %s" % post
    assert post["w194"] == {"a": [441604, 443603], "b_exit": [443604, 443803],
                           "engine_owner": "bm-a"}, "W194 row damaged: %s" % post
    assert post["cfg197"] == [448204, 450204, "n1_w197",
                              "n1_w197_results.json", "bm-a"], \
        "W197 WAVE_CONFIGS drift: %s" % post
    facts["post_import"] = post

    # ---- G12 receipt + five-segment PASS prints (r578) ----
    with open(OUT_RCPT, "w", encoding="utf-8") as fh:
        json.dump(facts, fh, indent=1, ensure_ascii=False)
    print("PASS 1/5 law-mirror pf N1_BANDS[197] row: a=(448204,450203) "
          "b_exit=(450204,450403) engine_owner=bm-a (comment face rolled, "
          "W196 row byte-intact)")
    print("PASS 2/5 n1 WAVE_CONFIGS[197] row: batch=PERPETUAL-N1-W197 "
          "a_seed_base=448_204 b_exit_seed_base=450_204 shard=n1_w197 "
          "out=n1_w197_results.json owner=bm-a")
    print("PASS 3/5 n1 W197 materializer face: %d+%d+%d+%d derived pairs + "
          "%d+%d archive pairs all count-asserted; staircase FIFTY-SEVENTH; "
          "prior-wave parity->W196; deps range(17,197) all-landed clean; "
          "prereg presence assert->W197"
          % (len(pairs_mat), len(pairs_cfg), len(pairs_pf),
             len(pairs_claim), len(MAT_ARCHIVE), len(PF_ARCHIVE)))
    print("PASS 4/5 guards: origin vacancy (fetch+show) + seat sha %s "
          "ancestor + registry 194->195 rows + AST+py_compile + W196/W195/W194 "
          "byte-intact post-import + stale sweeps clean + seat MSG "
          "already-archived processed/ verified"
          % SEAT_SHA)
    print("PASS 5/5 summary: W197 = 187th engine wave, bm-a 112th owned "
          "(rows 186+candidate per receipt leg0); A=448_204..450_203 "
          "hops=1 FIFTY-SEVENTH staircase; B=450_204..450_403 hops=1 "
          "own-A mutual exclusion; ZERO in-flight upstream (W196 "
          "finalize landed r913, head 845,545 K 429,120); ADMIT "
          "receipt machine-read; receipt=results/_r915bma_w197_freeze_receipt.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
