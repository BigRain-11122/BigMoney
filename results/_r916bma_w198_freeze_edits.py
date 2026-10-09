# -*- coding: utf-8 -*-
"""r916 bm-a W198 five-face freeze edits (five faces: pf N1_BANDS row +
n1 WAVE_CONFIGS row + n1 materializer face + n1 selftest claim + seat
MSG archive-pending verification face). Direct-author per the
r909/r912/r915 physical chunk-roll machinery, rolled ONE generation:
extract current W197 fragments, roll W197->W198 with count-asserted
replacements, insert ADDITIVELY after the last registered row;
originals byte-identical zero-destroy. Old sides DERIVED AT RUNTIME by
the two-gen chain (zero transcription, r587): r912 AST triples
(W195_old, W196_new, cnt) -> r915 AST RULES_* -> W197 text = this
build's old side; W198 fact substitutions curated here.

Facts machine-read never transcribed (r587): ADMIT receipt
results/_r915bma_w198_probe_receipt.json (bands A 450404..452403 /
B 452404..452603, hops 1/1, FIFTY-EIGHTH staircase, leg0 rows 195
tail W197 owner_rows 187 bma_rows 112 ordinal 188 bma_ordinal 113
w197_ledger_head 847745, leg2 conflicts 0, leg3 origin vacancy, leg4
W199+ projection A 452404..454403 / B 452604..452803 hops 0/0
B-inside-A). Seat push 525630e39 (MSG-2026-10-09-1355-bma-w198-seat +
probe script + receipt, 3-item, r915 seat push, ancestor-verified).
W197=bm-a r915 five-face freeze+finalize one-pass SAME commit
522a0aef5 (dead-session freeze 13:0x + engine self-burn 12/12 landed
pre-death, estate absorbed per r899 law; ledger 847,745 EXACT
zero-deviation 4th consecutive window, K=431,320 EXACT, four pred
keys PASS) -- ZERO in-flight upstream seats, clean precondition
freeze window. Seat MSG archive state = PENDING (sits in
fleet/inbox/ at freeze time, moves to processed/ with THIS freeze
window closeout per S7 inbox-processing law -- the r912 W196-style
archive-pending pattern; r915 already-landed adaptation N/A).

Laws honored: r511/r687 write-time fetch + origin-tail vacancy lock;
r560 insert-after-last-registered-row + anti-vanish + before/after
counts; r370 EOL-adaptive anchors; r580/r581 AST + py_compile gate;
r581 multi-line assert messages paren-wrapped; r578 five-segment PASS
prints; r776 fragment-needle law (physical dumps
results/_r916bma_w198_face_*.txt, re-verified against the live files
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
R915 = os.path.join(ROOT, "results", "_r915bma_w197_freeze_edits.py")
RCPT = os.path.join(ROOT, "results", "_r915bma_w198_probe_receipt.json")
OUT_RCPT = os.path.join(ROOT, "results", "_r916bma_w198_freeze_receipt.json")
SEAT_INBOX = "fleet/inbox/MSG-2026-10-09-1355-bma-w198-seat.md"
PREREG = os.path.join(ROOT, "research", "PERPETUAL_N1_W198_PREREG.md")
SEAT_SHA = "525630e39"
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


def extract_lists(path, names):
    src = open(path, encoding="utf-8").read()
    tree = ast.parse(src)
    out = {}
    for node in ast.walk(tree):
        if (isinstance(node, ast.Assign) and len(node.targets) == 1
                and isinstance(node.targets[0], ast.Name)
                and node.targets[0].id in names
                and isinstance(node.value, ast.List)):
            out[node.targets[0].id] = [ast.literal_eval(e)
                                       for e in node.value.elts]
    return out


def extract_dict(path, name):
    src = open(path, encoding="utf-8").read()
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if (isinstance(node, ast.Assign) and len(node.targets) == 1
                and isinstance(node.targets[0], ast.Name)
                and node.targets[0].id == name
                and isinstance(node.value, ast.Dict)):
            return {ast.literal_eval(k): [ast.literal_eval(v)
                    for v in [e]] for k, e in
                    zip(node.value.keys, node.value.values)}
    return None


# ---- two-gen extraction: r912 triples + r915 fact rules ----
def load_bloodline():
    t912 = extract_lists(R912, ("R", "RC", "RP", "RQ"))
    assert set(t912) == {"R", "RC", "RP", "RQ"}, \
        "r912 lists missing: %s" % sorted(t912)
    t915 = extract_lists(R915, ("RULES_MAT", "RULES_CFG", "RULES_PF",
                                "RULES_CLAIM", "MAT_ARCHIVE", "PF_ARCHIVE",
                                "DROP_IF"))
    assert set(t915) == {"RULES_MAT", "RULES_CFG", "RULES_PF",
                         "RULES_CLAIM", "MAT_ARCHIVE", "PF_ARCHIVE",
                         "DROP_IF"}, "r915 lists missing: %s" % sorted(t915)
    return t912, t915


def apply_rules(text, rules, tag):
    for (a, b) in rules:
        if a in text:
            text = text.replace(a, b)
    return text


# ---- W198 fact substitution rules (curated; applied to W197 sides) ----
RULES_W198_MAT = [
    ("# --- W197 materializer face (r915 bm-a freeze, own-series law",
     "# --- W198 materializer face (r916 bm-a freeze, own-series law"),
    ("one-hundred-twelfth owned", "one-hundred-thirteenth owned"),
    ("rows 111 + candidate); wave 196 = first free number after",
     "rows 112 + candidate); wave 197 = first free number after"),
    ("the REGISTERED W196 row (bm-a r912 freeze 02cf6b44d) --",
     "the REGISTERED W197 row (bm-a r915 freeze 522a0aef5) --"),
    ("(W2..W196 all registered). Seat", "(W2..W197 all registered). Seat"),
    ("MSG-2026-10-09-1159-bma-w197-seat pushed",
     "MSG-2026-10-09-1355-bma-w198-seat pushed"),
    ("to origin c59843acb BEFORE this freeze",
     "to origin 525630e39 BEFORE this freeze"),
    ("the W196 finalize product already on origin since r913, not",
     "the W197 finalize product already on origin since r915, not"),
    ("at fetch (r914 seat push), zero merge, zero",
     "at fetch (r915 seat push), zero merge, zero"),
    ("ONE HUNDRED-AND-NINETY-SEVENTH engine wave BY",
     "ONE HUNDRED-AND-NINETY-EIGHTH engine wave BY"),
    ("MACHINE-DERIVE (engine_owner rows 186 + candidate; gate",
     "MACHINE-DERIVE (engine_owner rows 187 + candidate; gate"),
    ("W1..W196 finalize ALL LANDED (net chain head 845,545,",
     "W1..W197 finalize ALL LANDED (net chain head 847,745,"),
    ("K=429,120 merged pool; W196 finalize one-pass bm-a r913)",
     "K=431,320 merged pool; W197 finalize one-pass bm-a r915)"),
    ("always on. ADMIT receipt results/_r914bma_w197_probe_receipt.json;",
     "always on. ADMIT receipt results/_r915bma_w198_probe_receipt.json;"),
    ("not a re-pick (R250: W197 bands were",
     "not a re-pick (R250: W198 bands were"),
    ("    _set_wave(197)", "    _set_wave(198)"),
    ('WAVE_CONFIGS[196]["a_seed_base"] == pf.N1_BANDS[196]["a"][0]',
     'WAVE_CONFIGS[197]["a_seed_base"] == pf.N1_BANDS[197]["a"][0]'),
    ('"W197 A band drift vs law mirror"', '"W198 A band drift vs law mirror"'),
    ('WAVE_CONFIGS[196]["b_exit_seed_base"] ==',
     'WAVE_CONFIGS[197]["b_exit_seed_base"] =='),
    ('pf.N1_BANDS[196]["b_exit"][0], "W197 B band drift vs law mirror"',
     'pf.N1_BANDS[197]["b_exit"][0], "W198 B band drift vs law mirror"'),
    ('WAVE_CONFIGS[196].get("engine_owner") ==',
     'WAVE_CONFIGS[197].get("engine_owner") =='),
    ('pf.N1_BANDS[196].get("engine_owner") == "bm-a"',
     'pf.N1_BANDS[197].get("engine_owner") == "bm-a"'),
    ('"W197 engine_owner drift (law mirror parity)"',
     '"W198 engine_owner drift (law mirror parity)"'),
    ("w196_a", "w197_a"),
    ("w196_b", "w197_b"),
    ('"W197 A/B band overlap"', '"W198 A/B band overlap"'),
    ('"W197 hits SEED_REGISTRY"', '"W198 hits SEED_REGISTRY"'),
    ('f"W197 {nm} hits v1"', 'f"W198 {nm} hits v1"'),
    ('f"W197 {nm} hits W1"', 'f"W198 {nm} hits W1"'),
    ('f"W197 {nm} hits probe seeds"', 'f"W198 {nm} hits probe seeds"'),
    ("# prior-wave disjointness W2..W196 (single state: all",
     "# prior-wave disjointness W2..W197 (single state: all"),
    ("WAVE_CONFIGS if w < 197):", "WAVE_CONFIGS if w < 198):"),
    ('f"W197 A hits W{wprev}"', 'f"W198 A hits W{wprev}"'),
    ('f"W197 B hits W{wprev}"', 'f"W198 B hits W{wprev}"'),
    ("n3r1_used196", "n3r1_used197"),
    ('"W197 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"',
     '"W198 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"'),
    ('"W197 bands must clear the lfc actual draw range"',
     '"W198 bands must clear the lfc actual draw range"'),
    ('"W197 bands must clear the options_wave2 actual draw range"',
     '"W198 bands must clear the options_wave2 actual draw range"'),
    ("# band facts (law sec.4 W197 row, r795): A = FIRST-CLEAN past",
     "# band facts (law sec.4 W198 row, r795): A = FIRST-CLEAN past"),
    ("# the registered W196 B band (the arithmetic continuation",
     "# the registered W197 B band (the arithmetic continuation"),
    ("# 448_004..450_003 is REFUSED at its own start by the W196",
     "# 450_204..452_203 is REFUSED at its own start by the W197"),
    ("# B band 448_004..448_203, exactly as the W196 prereg sec5.5 +",
     "# B band 450_204..450_403, exactly as the W197 prereg sec5.5 +"),
    ("# bm-a r910 probe leg4 succession projection notes",
     "# bm-a r914 probe leg4 succession projection notes"),
    ("# 448_204..450_203; A base == prior-wave B tail+1 (448_203+1)",
     "# 450_404..452_403; A base == prior-wave B tail+1 (450_403+1)"),
    ("-- A-hops-prior-B staircase FIFTY-SEVENTH",
     "-- A-hops-prior-B staircase FIFTY-EIGHTH"),
    ("# continuation 448_204..448_403 is CLEAN on the registered",
     "# continuation 450_404..450_603 is CLEAN on the registered"),
    ("# universe but lands INSIDE the W197 A band window --",
     "# universe but lands INSIDE the W198 A band window --"),
    ("# 450_204 and lands 450_204..450_403, hops=1, non-rotational",
     "# 452_404 and lands 452_404..452_603, hops=1, non-rotational"),
    ("# (450_203+1) machine-checkable; cross-window convergence",
     "# (452_403+1) machine-checkable; cross-window convergence"),
    ("# with the W196 prereg sec5.5 + bm-a r910 probe leg4",
     "# with the W197 prereg sec5.5 + bm-a r914 probe leg4"),
    ("# honored (post-W196 universe re-derive + own-wave A",
     "# honored (post-W197 universe re-derive + own-wave A"),
    ("# reservation when deriving B); seat MSG-1159 tail,",
     "# reservation when deriving B); seat MSG-1355 tail,"),
    ('assert WAVE_CONFIGS[197]["a_seed_base"] == 448_204 == 448_203 + 1, (',
     'assert WAVE_CONFIGS[198]["a_seed_base"] == 450_404 == 450_403 + 1, ('),
    ('"W197 A must be the first-clean window past the registered "',
     '"W198 A must be the first-clean window past the registered "'),
    ('"W196 B band tail 448_203+1 (arithmetic continuation "',
     '"W197 B band tail 450_403+1 (arithmetic continuation "'),
    ('"448_004..450_003 REFUSED at its own start by the W196 B "',
     '"450_204..452_203 REFUSED at its own start by the W197 B "'),
    ('"band 448_004..448_203, exactly as the W196 prereg sec5.5 + "',
     '"band 450_204..450_403, exactly as the W197 prereg sec5.5 + "'),
    ('"bm-a r910 probe leg4 succession projection notes "',
     '"bm-a r914 probe leg4 succession projection notes "'),
    ('"staircase FIFTY-SEVENTH instance, E36 card)")',
     '"staircase FIFTY-EIGHTH instance, E36 card)")'),
    ("arith_a196 = set(range(448_204, 450_204))",
     "arith_a197 = set(range(450_404, 452_404))"),
    ("assert not (arith_a196 & reg_ints), \\",
     "assert not (arith_a197 & reg_ints), \\"),
    ('"W197 A window must be CLEAN (first-clean ADMIT face past prior-wave B)"',
     '"W198 A window must be CLEAN (first-clean ADMIT face past prior-wave B)"'),
    ('assert WAVE_CONFIGS[197]["b_exit_seed_base"] == 450_204 == 450_203 + 1, (',
     'assert WAVE_CONFIGS[198]["b_exit_seed_base"] == 452_404 == 452_403 + 1, ('),
    ('"W197 B must be the first-clean window past the own-wave A "',
     '"W198 B must be the first-clean window past the own-wave A "'),
    ('"band tail 450_203+1 (arithmetic continuation "',
     '"band tail 452_403+1 (arithmetic continuation "'),
    ('"448_204..448_403 CLEAN on the registered universe but "',
     '"450_404..450_603 CLEAN on the registered universe but "'),
    ('"lands INSIDE the W197 A band window; same-freeze mutual "',
     '"lands INSIDE the W198 A band window; same-freeze mutual "'),
    ('"own-wave A window reserved jumps to 450_204, first-clean "',
     '"own-wave A window reserved jumps to 452_404, first-clean "'),
    ("arith_b196 = set(range(450_204, 450_404))",
     "arith_b197 = set(range(452_404, 452_604))"),
    ("assert not (arith_b196 & reg_ints), \\",
     "assert not (arith_b197 & reg_ints), \\"),
    ('"W197 B window must be CLEAN (first-clean ADMIT face past own-wave A)"',
     '"W198 B window must be CLEAN (first-clean ADMIT face past own-wave A)"'),
    ("assert not (arith_b196 & arith_a196), \\",
     "assert not (arith_b197 & arith_a197), \\"),
    ('"W197 A/B same-freeze mutual exclusion (B hops past own A)"',
     '"W198 A/B same-freeze mutual exclusion (B hops past own A)"'),
    ('assert _entry_shard_of(0, 12) == ("PERPETUAL-N1-W197-SHARD-0",',
     'assert _entry_shard_of(0, 12) == ("PERPETUAL-N1-W198-SHARD-0",'),
    ('"n1w197-0of12"), "W197 entry identity"',
     '"n1w198-0of12"), "W198 entry identity"'),
    ('assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W197-SHARD-11",',
     'assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W198-SHARD-11",'),
    ('"n1w197-11of12")', '"n1w198-11of12")'),
    ('assert SHARD_DIR.endswith("n1_w197") and OUT.endswith(',
     'assert SHARD_DIR.endswith("n1_w198") and OUT.endswith('),
    ('"n1_w197_results.json"), "W197 path drift"',
     '"n1_w198_results.json"), "W198 path drift"'),
    ('f"W197 shard dir collides with W{wprev}"',
     'f"W198 shard dir collides with W{wprev}"'),
    ("# W197 finalize cumulative deps: W17..W196 outputs ALL PRESENT",
     "# W198 finalize cumulative deps: W17..W197 outputs ALL PRESENT"),
    ("# (landed net chain head 845,545 = W196 bm-a r913 one-pass)",
     "# (landed net chain head 847,745 = W197 bm-a r915 one-pass)"),
    ("for _depw in range(17, 197):", "for _depw in range(17, 198):"),
    ('f"W197 finalize cumulative dep (W{_depw} output) missing"',
     'f"W198 finalize cumulative dep (W{_depw} output) missing"'),
    ("# registered wave below 197 composes; wave 15 excluded by",
     "# registered wave below 198 composes; wave 15 excluded by"),
    ("# design; SINGLE STATE (W2..W196 all registered -- no",
     "# design; SINGLE STATE (W2..W197 all registered -- no"),
    ("assert sorted(w for w in WAVE_CONFIGS if w < 197) == \\",
     "assert sorted(w for w in WAVE_CONFIGS if w < 198) == \\"),
    ("[w for w in range(16, 197)], \\", "[w for w in range(16, 198)], \\"),
    ('"W197 prior-wave set must derive from registry keys (no 15; " \\',
     '"W198 prior-wave set must derive from registry keys (no 15; " \\'),
    ('"W2..W196 registered single state)"', '"W2..W197 registered single state)"'),
    ('"research", "PERPETUAL_N1_W197_PREREG.md")), \\',
     '"research", "PERPETUAL_N1_W198_PREREG.md")), \\'),
    ('"W197 per-wave prereg missing (materializer requirement)"',
     '"W198 per-wave prereg missing (materializer requirement)"'),
]

RULES_W198_CFG = [
    ('197: {"batch": "PERPETUAL-N1-W197",', '198: {"batch": "PERPETUAL-N1-W198",'),
    ('PERPETUAL_N1_W197_PREREG.md (wave-level frozen',
     'PERPETUAL_N1_W198_PREREG.md (wave-level frozen'),
    ('ONE HUNDRED-AND-NINETY-SEVENTH ENGINE-OWNED WAVE',
     'ONE HUNDRED-AND-NINETY-EIGHTH ENGINE-OWNED WAVE'),
    ('engine_owner rows 186 + candidate), ',
     'engine_owner rows 187 + candidate), '),
    ('number law after the REGISTERED W196 row bm-a r912 freeze ',
     'number law after the REGISTERED W197 row bm-a r915 freeze '),
    ('02cf6b44d, SINGLE STATE zero seat gap W2..W196 all ',
     '522a0aef5, SINGLE STATE zero seat gap W2..W197 all '),
    ('registered; W1..W196 finalize ALL LANDED (W196 bm-a r913 ',
     'registered; W1..W197 finalize ALL LANDED (W197 bm-a r915 '),
    ('one-pass, ledger head 845,545, merged pool K=429,120) -- ',
     'one-pass, ledger head 847,745, merged pool K=431,320) -- '),
    ('MSG-2026-10-09-1159-bma-w197-seat PUSHED to origin c59843acb ',
     'MSG-2026-10-09-1355-bma-w198-seat PUSHED to origin 525630e39 '),
    ('(3-item; the W196 finalize product already on origin since r913, not re-shipped; W146 precedent); ',
     '(3-item; the W197 finalize product already on origin since r915, not re-shipped; W146 precedent); '),
    ('at fetch (r914 seat push), zero merge, zero ',
     'at fetch (r915 seat push), zero merge, zero '),
    ('engine_owner=bm-a, wave 196: ', 'engine_owner=bm-a, wave 197: '),
    ('"A = FIRST-CLEAN past the registered W196 B band (the "',
     '"A = FIRST-CLEAN past the registered W197 B band (the "'),
    ('"arithmetic continuation 448_004..450_003 is REFUSED at its "',
     '"arithmetic continuation 450_204..452_203 is REFUSED at its "'),
    ('"own start by the W196 B band 448_004..448_203, exactly as "',
     '"own start by the W197 B band 450_204..450_403, exactly as "'),
    ('"the W196 prereg sec5.5 + bm-a r910 probe leg4 succession "',
     '"the W197 prereg sec5.5 + bm-a r914 probe leg4 succession "'),
    ('"448_204..450_203; A base == prior-wave B tail+1 "',
     '"450_404..452_403; A base == prior-wave B tail+1 "'),
    ('"machine-checkable = A-hops-prior-B staircase FIFTY-SEVENTH "',
     '"machine-checkable = A-hops-prior-B staircase FIFTY-EIGHTH "'),
    ('"arithmetic continuation 448_204..448_403 is CLEAN on the "',
     '"arithmetic continuation 450_404..450_603 is CLEAN on the "'),
    ('"registered universe but lands INSIDE the W197 A band "',
     '"registered universe but lands INSIDE the W198 A band "'),
    ('"jumps to 450_204, first-clean 450_204..450_403 hops=1, "',
     '"jumps to 452_404, first-clean 452_404..452_603 hops=1, "'),
    ('"convergence with the W196 prereg sec5.5 + bm-a r910 probe leg4 + "',
     '"convergence with the W197 prereg sec5.5 + bm-a r914 probe leg4 + "'),
    ('"r914 probe succession projection notes re-derived -- all "',
     '"r915 probe succession projection notes re-derived -- all "'),
    ('"MANDATORY notes honored (post-W196 universe re-derive + "',
     '"MANDATORY notes honored (post-W197 universe re-derive + "'),
    ('"results/_r914bma_w197_probe_receipt.json; W198+ projection "',
     '"results/_r915bma_w198_probe_receipt.json; W199+ projection "'),
    ('"per this window gate: A first-clean 450_204..452_203 "',
     '"per this window gate: A first-clean 452_404..454_403 "'),
    ('"CLEAN / B first-clean 450_404..450_603 CLEAN -- naive "',
     '"CLEAN / B first-clean 452_604..452_803 CLEAN -- naive "'),
    ('"W197 B band 450_204..450_403 will refuse the naive "',
     '"W198 B band 452_404..452_603 will refuse the naive "'),
    ('"W198 A window; W198 freezer MUST re-derive on the "',
     '"W199 A window; W199 freezer MUST re-derive on the "'),
    ('"post-W197 universe AND reserve the own-wave A window "',
     '"post-W198 universe AND reserve the own-wave A window "'),
    ('W1..W196 finalize ALL LANDED (W196 bm-a r913 ',
     'W1..W197 finalize ALL LANDED (W197 bm-a r915 '),
    ('W1..W196 finalize ALL LANDED (W196 "',
     'W1..W197 finalize ALL LANDED (W197 "'),
    ('"finalize one-pass bm-a r913, net chain head 845,545, "',
     '"finalize one-pass bm-a r915, net chain head 847,745, "'),
    ('"merged pool K=429,120) -- ZERO in-flight upstream "',
     '"merged pool K=431,320) -- ZERO in-flight upstream "'),
    ('"a_seed_base": 448_204,        # law sec.4 W197 A: 448_204..450_203 (FIRST-CLEAN past the registered W196 B band; arithmetic 448_004..450_003 REFUSED at own start by the W196 B band 448_004..448_203; hops=1; A-hops-prior-B staircase FIFTY-SEVENTH instance, E36 card; ordinal convergence per r587: W196 prereg sec5.5 prose anticipated fifty-seventh, r914 receipt machine-read FIFTY-SEVENTH)',
     '"a_seed_base": 450_404,        # law sec.4 W198 A: 450_404..452_403 (FIRST-CLEAN past the registered W197 B band; arithmetic 450_204..452_203 REFUSED at own start by the W197 B band 450_204..450_403; hops=1; A-hops-prior-B staircase FIFTY-EIGHTH instance, E36 card; ordinal convergence per r587: W197 prereg sec5.5 prose anticipated fifty-eighth, r915 receipt machine-read FIFTY-EIGHTH)'),
    ('"b_exit_seed_base": 450_204,   # law sec.4 W197 B: 450_204..450_403 (FIRST-CLEAN past the own-wave A window; arithmetic 448_204..448_403 lands inside own-A, same-freeze mutual exclusion W141 precedent; reserved walk hops=1; B base == own-A tail+1)',
     '"b_exit_seed_base": 452_404,   # law sec.4 W198 B: 452_404..452_603 (FIRST-CLEAN past the own-wave A window; arithmetic 450_404..450_603 lands inside own-A, same-freeze mutual exclusion W141 precedent; reserved walk hops=1; B base == own-A tail+1)'),
    ('"shard_subdir": "n1_w197", "out_name": "n1_w197_results.json",',
     '"shard_subdir": "n1_w198", "out_name": "n1_w198_results.json",'),
]

RULES_W198_PF = [
    ('# W197 (bm-a r915 freeze, seat MSG-2026-10-09-1159-bma-w197-seat',
     '# W198 (bm-a r916 freeze, seat MSG-2026-10-09-1355-bma-w198-seat'),
    ('# pushed to origin c59843acb pre-freeze r565 law (r914 seat',
     '# pushed to origin 525630e39 pre-freeze r565 law (r915 seat'),
    ('# (3-item; the W196 finalize product already on origin since r913,',
     '# (3-item; the W197 finalize product already on origin since r915,'),
    ('# = direct fast-forward behind-0 at fetch (r914 seat push),',
     '# = direct fast-forward behind-0 at fetch (r915 seat push),'),
    ('# band gate ADMIT results/_r914bma_w197_probe_receipt.json: A = FIRST-CLEAN',
     '# band gate ADMIT results/_r915bma_w198_probe_receipt.json: A = FIRST-CLEAN'),
    ('# past the registered W196 B band (arithmetic continuation',
     '# past the registered W197 B band (arithmetic continuation'),
    ('# 448_004..450_003 REFUSED at its own start by the W196 B band',
     '# 450_204..452_203 REFUSED at its own start by the W197 B band'),
    ('# 448_004..448_203, exactly as the W196 prereg sec5.5 + bm-a r910 probe',
     '# 450_204..450_403, exactly as the W197 prereg sec5.5 + bm-a r914 probe'),
    ('# honest forward walk hops=1 -> 448_204..450_203, non-rotational',
     '# honest forward walk hops=1 -> 450_404..452_403, non-rotational'),
    ('# (448_203+1) machine-checkable -- A-hops-prior-B staircase',
     '# (450_403+1) machine-checkable -- A-hops-prior-B staircase'),
    ('# FIFTY-SEVENTH instance, E36 card);', '# FIFTY-EIGHTH instance, E36 card);'),
    ('# continuation 448_204..448_403 CLEAN on the registered universe',
     '# continuation 450_404..450_603 CLEAN on the registered universe'),
    ('# but lands INSIDE the W197 A band window -- same-freeze mutual',
     '# but lands INSIDE the W198 A band window -- same-freeze mutual'),
    ('# own-wave A window reserved jumps to 450_204 -> 450_204..450_403,',
     '# own-wave A window reserved jumps to 452_404 -> 452_404..452_603,'),
    ('# own-wave A tail+1 (450_203+1) machine-checkable);',
     '# own-wave A tail+1 (452_403+1) machine-checkable);'),
    ('# W198+ projection (gate-derived r914): A first-clean',
     '# W199+ projection (gate-derived r915): A first-clean'),
    ('# 450_204..452_203 CLEAN hops=0 / B first-clean 450_404..450_603',
     '# 452_404..454_403 CLEAN hops=0 / B first-clean 452_604..452_803'),
    ('# registered W197 B band 450_204..450_403 will refuse the naive',
     '# registered W198 B band 452_404..452_603 will refuse the naive'),
    ('# W198 A window; W198 freezer MUST re-derive on the post-W197',
     '# W199 A window; W199 freezer MUST re-derive on the post-W198'),
    ('# NOT a re-pick (R250: W197 bands were never assigned).',
     '# NOT a re-pick (R250: W198 bands were never assigned).'),
    ('197: {"a": (448_204, 450_203), "b_exit": (450_204, 450_403),',
     '198: {"a": (450_404, 452_403), "b_exit": (452_404, 452_603),'),
]

RULES_W198_CLAIM = [
    ('"+ W197 materializer face [same guard set, dep=W17..W196 "',
     '"+ W198 materializer face [same guard set, dep=W17..W197 "'),
    ('"outputs ALL PRESENT (landed net chain head 845,545 = "',
     '"outputs ALL PRESENT (landed net chain head 847,745 = "'),
    ('"W196 bm-a r913 one-pass, K=429,120 merged pool) -- ZERO "',
     '"W197 bm-a r915 one-pass, K=431,320 merged pool) -- ZERO "'),
    ('"in-flight upstream seats, clean precondition, ONE HUNDRED-AND-NINETY-SEVENTH "',
     '"in-flight upstream seats, clean precondition, ONE HUNDRED-AND-NINETY-EIGHTH "'),
    ('"ENGINE-OWNED WAVE BY MACHINE-DERIVE (engine_owner rows 186 "',
     '"ENGINE-OWNED WAVE BY MACHINE-DERIVE (engine_owner rows 187 "'),
    ("bm-a's one-hundred-twelfth owned claim per ",
     "bm-a's one-hundred-thirteenth owned claim per "),
    ('"machine-derive (engine_owner==bm-a rows 111 + candidate), "',
     '"machine-derive (engine_owner==bm-a rows 112 + candidate), "'),
    ('"A=FIRST-CLEAN past the registered W196 B band (staircase "',
     '"A=FIRST-CLEAN past the registered W197 B band (staircase "'),
    ('"FIFTY-SEVENTH instance, E36 card, hops=1) + B=FIRST-CLEAN past the "',
     '"FIFTY-EIGHTH instance, E36 card, hops=1) + B=FIRST-CLEAN past the "'),
    ('"results/_r914bma_w197_probe_receipt.json, law sec.4 W197 row, "',
     '"results/_r915bma_w198_probe_receipt.json, law sec.4 W198 row, "'),
    ('"r915 bm-a] "', '"r916 bm-a] "'),
]

# Archive face: W198 seat MSG is ARCHIVE-PENDING (sits in fleet/inbox/
# at freeze time; moves to processed/ with this window closeout per
# S7 law -- r912 W196-style pattern, r915 already-landed N/A).
# Machine-rolled from the r915 MAT_ARCHIVE/PF_ARCHIVE pairs at runtime:
# old side = r915 NEW side (the already-landed text in the live W197
# fragments); new side = r915 OLD side (the r912 archive-pending
# pattern) rolled r912->r916, W196->W198.


def roll_r912_archive(text):
    return text.replace("r912", "r916").replace("W196", "W198")


STALE = {
    "mat198": ["c59843acb", "MSG-2026-10-09-1159", "r914 seat push",
               "_r914bma", "FIFTY-SEVENTH", "448_204",
               "448_204..450_203", "448_204..448_403",
               "448_203+1", "450_203+1", '== "bm-c"',
               "one-hundred-twelfth", "rows 111 + candidate",
               "ONE HUNDRED-AND-NINETY-SEVENTH", "W2..W196 all",
               "arith_a196", "arith_b196", "w196_a", "w196_b",
               "n3r1_used196", "W1..W196 finalize", "845,545",
               "429,120", "r915 freeze-closeout", "one-pass bm-a r913",
               "W196 bm-a r913 one-pass", "bm-a r910 probe",
               "post-W196 universe", "MSG-1159 tail",
               "range(17, 197)", "jumps to 450_204", "n1w197", "n1_w197",
               "W197-SHARD", "W197 entry", "W197 path drift",
               "W197 shard dir", "w < 197):", "W2..W196 registered",
               "PERPETUAL_N1_W197_PREREG", "W197 per-wave prereg",
               "W197 finalize cumulative dep", "W197 prior-wave set",
               "disjointness W2..W196", "W197 A/B band", "W197 hits",
               "W197 bands", "W197 A window must", "W197 B window must",
               "W197 A/B same-freeze", "W198+ projection",
               "W197 A band drift", "W197 B band drift",
               "W197 engine_owner drift", "r909 freeze", "b9b962672",
               "the W195 finalize product", "since r910",
               "02cf6b44d",
               "archive ALREADY", "LANDED at the seat round r914",
               "processed/ at freeze time", "archive-pending N/A"],
    "cfg198": ["c59843acb", "MSG-2026-10-09-1159", "_r914bma",
               "FIFTY-SEVENTH", "448_204", "448_204..450_203",
               "448_204..448_403", "448_203+1", "450_203+1",
               "W196 prereg sec5.5", "bm-a r910",
               "the W196 finalize product", "since r913",
               "ONE HUNDRED-AND-NINETY-SEVENTH", "W2..W196 all",
               "W2..W196 registered", "engine_owner rows 186",
               "r914 seat push", "W198+ projection",
               "A first-clean 450_204..452_203",
               "B first-clean 450_404..450_603", "wave 196: ",
               "448_204,", "450_204,   #", "n1_w197", "W197-SHARD",
               "r912 freeze", "post-W196 universe",
               "W196 B band 448", "one-pass bm-a r913", "W196 bm-a r913",
               "02cf6b44d", "845,545", "429,120", "W1..W196 finalize"],
    "pf198": ["c59843acb", "MSG-2026-10-09-1159", "_r914bma",
              "FIFTY-SEVENTH", "448_204", "448_004..450_003",
              "448_204..450_203", "448_204..448_403", "448_203+1",
              "450_203+1", "W198+ projection", "r914 seat",
              "gate-derived r914", "bm-a r910 probe",
              "W196 prereg sec5.5", "r915 freeze",
              "W196 B band", "jumps to 450_204", "W198 freezer",
              "post-W197 universe AND", "the W196 finalize product",
              "since r913", "archive ALREADY",
              "LANDED at the seat round r914", "processed/ (self-acked",
              "archive-pending N/A", "W197 bands were"],
    "claim198": ["_r914bma", "FIFTY-SEVENTH", "one-hundred-twelfth",
                 "rows 111 + candidate", "rows 186 ",
                 "r915 bm-a] ", "W196 B band",
                 "ONE HUNDRED-AND-NINETY-SEVENTH",
                 "845,545", "429,120", "dep=W17..W196",
                 "W196 bm-a r913 one-pass"],
}


def roll_pairs(r912_list, r915_rules, w198_rules, drop_if, tag):
    """Two-gen chain: old side = r912 new side rolled by the r915 fact
    rules (= the live W197 text, zero transcription); new side = W198
    rule-rolled."""
    pairs = []
    for (w195_old, w196_new, cnt) in r912_list:
        if any(d in w196_new for d in drop_if):
            continue  # archive-state lines handled by explicit pairs
        w197 = apply_rules(w196_new, r915_rules, tag)
        if w197 == w196_new:
            fails.append("R915-ROLL UNCHANGED [%s]: %r" % (tag, w196_new[:90]))
            continue
        w198 = apply_rules(w197, w198_rules, tag)
        if w198 == w197:
            fails.append("UNCHANGED PAIR [%s]: %r" % (tag, w197[:90]))
            continue
        pairs.append((w197, w198, cnt))
    return pairs


def main():
    facts = {"round": 916, "machine": "bm-a", "wave": 198,
             "archive_state": "pending (fleet/inbox/ at freeze time; "
                              "moves to processed/ with this window "
                              "closeout per S7 law -- r912 W196-style "
                              "pattern)"}

    # ---- G0 idempotence (already-applied abort) ----
    pf_probe = open(PFP, encoding="utf-8", errors="replace").read()
    if '198: {"a": (450_404, 452_403)' in pf_probe:
        print("ALREADY APPLIED: W198 pf row present -- abort")
        return 3

    # ---- G1 write-time fetch + origin tail lock (r511/r687) ----
    rc, _, err = git_out(["fetch", "origin"])
    assert rc == 0, "fetch failed: %s" % err[:200]
    rc, origin_pf, err = git_out(["show", "origin/main:scripts/perpetual_faces.py"])
    assert rc == 0, "origin pf blob read failed"
    assert "198: {" not in origin_pf, "ORIGIN TAIL MOVED: wave 198 already on origin"
    assert '197: {"a": (448_204, 450_203)' in origin_pf, "origin W197 row drift"
    rc, origin_n1, _ = git_out(["show", "origin/main:scripts/perpetual_faces_n1.py"])
    assert rc == 0
    assert "# --- W198 materializer face" not in origin_n1, "origin n1 W198 face present"
    assert '198: {"batch": "PERPETUAL-N1-W198"' not in origin_n1, \
        "origin n1 W198 cfg row present"
    rc, _, _ = git_out(["merge-base", "--is-ancestor", SEAT_SHA, "origin/main"])
    assert rc == 0, "seat push sha %s not an ancestor of origin/main" % SEAT_SHA
    facts["origin_vacancy"] = True

    # ---- G2 receipt + precheck parity (r587 / r359 machine numbers) ----
    r = json.load(open(RCPT, encoding="utf-8"))
    assert r["verdict"] == "ADMIT", "probe receipt not ADMIT"
    leg1 = r["legs"]["leg1"]
    A, B = leg1["A"], leg1["B"]
    assert A == [450404, 452403] and B == [452404, 452603], \
        "receipt bands drift: %s %s" % (A, B)
    assert leg1["hops_A"] == 1 and leg1["hops_B"] == 1
    assert leg1["ARITH_A"] == [450204, 452203] and \
        leg1["ARITH_B"] == [450404, 450603], "receipt arithmetic drift"
    assert r["bands"] == {"A": "450404_452403", "B": "452404_452603"}
    assert "FIFTY-EIGHTH" in leg1["A_semantics"], \
        "receipt A_semantics ordinal face missing"
    leg0 = r["legs"]["leg0"]
    assert leg0["rows"] == 195 and leg0["tail"] == "W197"
    assert leg0["ordinal"] == 188 and leg0["bma_ordinal"] == 113
    assert leg0["owner_rows"] == 187 and leg0["bma_rows"] == 112
    assert leg0["w197_ledger_head"] == 847745
    assert r["legs"]["leg2"]["conflicts"] == 0
    assert r["legs"]["leg3"]["origin_vacancy"] is True
    leg4 = r["legs"]["leg4"]
    assert leg4["W199p_A"] == "452404..454403" and \
        leg4["W199p_B"] == "452604..452803"
    assert leg4["hops_A"] == 0 and leg4["hops_B"] == 0
    assert leg4["W199p_B_lands_inside_W199p_A"] is True
    sys.path.insert(0, os.path.join(ROOT, "scripts"))
    from perpetual_faces import N1_BANDS  # noqa: E402
    assert max(N1_BANDS) == 197 and len(N1_BANDS) == 195, "registry tail drift"
    owners = {}
    for w, c in N1_BANDS.items():
        owners[c.get("engine_owner")] = owners.get(c.get("engine_owner"), 0) + 1
    owned = sum(v for k, v in owners.items() if k)
    assert owners.get("bm-a") == 112 and owners.get("bm-c") == 35 \
        and owned == 187, "owner counts drift: %s" % owners
    assert N1_BANDS[197] == {"a": (448204, 450203), "b_exit": (450204, 450403),
                            "engine_owner": "bm-a"}, "W197 row drift"
    assert N1_BANDS[196] == {"a": (446004, 448003), "b_exit": (448004, 448203),
                            "engine_owner": "bm-a"}, "W196 row drift"
    assert N1_BANDS[195] == {"a": (443804, 445803), "b_exit": (445804, 446003),
                            "engine_owner": "bm-a"}, "W195 row drift"
    assert N1_BANDS[194] == {"a": (441604, 443603), "b_exit": (443604, 443803),
                            "engine_owner": "bm-a"}, "W194 row drift"
    assert os.path.exists(PREREG), "W198 per-wave prereg missing"
    assert os.path.exists(os.path.join(ROOT, SEAT_INBOX)), \
        "seat MSG not in fleet/inbox/ (archive-pending state)"
    assert not os.path.exists(os.path.join(
        ROOT, "fleet", "inbox", "processed",
        "MSG-2026-10-09-1355-bma-w198-seat.md")), \
        "seat MSG double-present (inbox AND processed)"
    assert os.path.exists(os.path.join(
        ROOT, "results", "perpetual_faces", "n1_w197_results.json")), \
        "W197 finalize product missing (dep precondition)"
    for f in ("results/_r915bma_w198_probe.py",
              "results/_r915bma_w198_probe_receipt.json"):
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

    # ---- G4 extract W197 chunks (LF face; r776 physical shapes) ----
    def chunk(text, start, end, stag):
        i = text.find(start)
        assert i >= 0, "start marker not found [%s]" % stag
        j = text.find(end, i)
        assert j > i, "end marker not found [%s]" % stag
        return text[i:j + len(end)]

    mat197 = chunk(n1n, "    # --- W197 materializer face",
                   "    _set_wave(2)", "mat197")
    assert mat197.rstrip("\n").endswith("_set_wave(2)"), "mat197 tail drift"
    cfg197 = chunk(n1n, '    197: {"batch": "PERPETUAL-N1-W197",',
                   '"engine_owner": "bm-a"},', "cfg197")
    pf197 = chunk(pfn, "    # W197 (bm-a r915 freeze, seat MSG-2026-10-09-1159-bma-w197-seat",
                  '"engine_owner": "bm-a"},', "pf197")
    claim197 = chunk(n1n, '          "+ W197 materializer face [same guard set',
                     '"r915 bm-a] "', "claim197")
    assert n1n.count(cfg197) == 1, "cfg197 not unique"
    assert n1n.count(claim197) == 1, "claim197 not unique"
    assert pfn.count(pf197) == 1, "pf197 not unique"
    for nm, frag in (("mat197", mat197), ("cfg197", cfg197),
                     ("pf197", pf197), ("claim197", claim197)):
        with open(os.path.join(ROOT, "results",
                               "_r916bma_w198_face_%s.txt" % nm),
                  "w", encoding="utf-8", newline="") as fh:
            fh.write(frag)
    facts["dump_sizes"] = {nm: len(frag) for nm, frag in
                           (("mat", mat197), ("cfg", cfg197),
                            ("pf", pf197), ("claim", claim197))}

    # ---- G5-G7 derive rolled pairs (two-gen bloodline AST chain) ----
    t912, t915 = load_bloodline()
    drop_if = [x[0] if isinstance(x, tuple) else x for x in t915["DROP_IF"]]
    pairs_mat = roll_pairs(t912["R"], t915["RULES_MAT"], RULES_W198_MAT,
                           drop_if, "mat")
    pairs_cfg = roll_pairs(t912["RC"], t915["RULES_CFG"], RULES_W198_CFG,
                           drop_if, "cfg")
    pairs_pf = roll_pairs(t912["RP"], t915["RULES_PF"], RULES_W198_PF,
                           drop_if, "pf")
    pairs_claim = roll_pairs(t912["RQ"], t915["RULES_CLAIM"], RULES_W198_CLAIM,
                             drop_if, "claim")
    mat_arch = [(new915, roll_r912_archive(old912), cnt)
                for (old912, new915, cnt) in t915["MAT_ARCHIVE"]]
    pf_arch = [(new915, roll_r912_archive(old912), cnt)
               for (old912, new915, cnt) in t915["PF_ARCHIVE"]]
    facts["pair_counts"] = {"mat": len(pairs_mat), "cfg": len(pairs_cfg),
                            "pf": len(pairs_pf), "claim": len(pairs_claim),
                            "dropped_archive": (len(t912["R"]) - len(pairs_mat))
                            + (len(t912["RP"]) - len(pairs_pf)),
                            "archive_pairs": len(mat_arch) + len(pf_arch)}
    m = mat197
    for k, (old, new, cnt) in enumerate(pairs_mat):
        m = rep(m, old, new, cnt, "mat-%02d" % k)
    for k, (old, new, cnt) in enumerate(mat_arch):
        m = rep(m, old, new, cnt, "mat-arch-%d" % k)
    mat198 = m
    c = cfg197
    for k, (old, new, cnt) in enumerate(pairs_cfg):
        c = rep(c, old, new, cnt, "cfg-%02d" % k)
    cfg198 = c
    p = pf197
    for k, (old, new, cnt) in enumerate(pairs_pf):
        p = rep(p, old, new, cnt, "pf-%02d" % k)
    for k, (old, new, cnt) in enumerate(pf_arch):
        p = rep(p, old, new, cnt, "pf-arch-%d" % k)
    pf198 = p
    q = claim197
    for k, (old, new, cnt) in enumerate(pairs_claim):
        q = rep(q, old, new, cnt, "claim-%02d" % k)
    claim198 = q

    # ---- G7c stale sweeps on the rolled fragments (r780/r781) ----
    # NOTE: W197 band citations (the registered W197 B band
    # 450_204..450_403 and the W198 arithmetic continuations
    # 450_204..452_203 / 450_404..450_603) are LEGITIMATE content of
    # the W198 fragments (prior-wave face) -- they are NOT stale.
    frags = {"mat198": mat198, "cfg198": cfg198, "pf198": pf198,
             "claim198": claim198}
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
    n1_b = n1n.replace(cfg197, cfg197 + "\n" + IND19 + cfg198, 1)
    if n1_b == n1n:
        fails.append("cfg insertion no-op")
        print("RESULT: FAIL -- cfg insertion no-op")
        return 1
    w197_pos = n1_b.find("    # --- W197 materializer face")
    assert w197_pos >= 0
    t141 = n1_b.find("    # --- T-141 s2 lane face", w197_pos)
    assert t141 > w197_pos, "T-141 marker not found after W197 face"
    n1_c = n1_b[:t141] + mat198 + "\n" + n1_b[t141:]
    claim_anchor = claim197 + '\n          "+ T-141 s2 "'
    assert n1_c.count(claim_anchor) == 1, "claim anchor not unique"
    n1_final = n1_c.replace(claim_anchor,
                            claim197 + "\n" + claim198 +
                            '\n          "+ T-141 s2 "', 1)
    pf_final = pfn.replace(pf197, pf197 + "\n" + pf198, 1)
    if pf_final == pfn:
        fails.append("pf insertion no-op")

    # ---- G9 presence + anti-vanish + malformed scans (r560/r819) ----
    checks = [
        (n1_final, '198: {"batch": "PERPETUAL-N1-W198",', 1),
        (n1_final, '197: {"batch": "PERPETUAL-N1-W197",', 1),
        (n1_final, '196: {"batch": "PERPETUAL-N1-W196",', 1),
        (n1_final, '195: {"batch": "PERPETUAL-N1-W195",', 1),
        (n1_final, '194: {"batch": "PERPETUAL-N1-W194",', 1),
        (n1_final, '193: {"batch": "PERPETUAL-N1-W193",', 1),
        (n1_final, "# --- W198 materializer face", 1),
        (n1_final, "# --- W197 materializer face", 1),
        (n1_final, "# --- W196 materializer face", 1),
        (n1_final, "# --- W195 materializer face", 1),
        (n1_final, "# --- W194 materializer face", 1),
        (n1_final, "# --- W193 materializer face", 1),
        (n1_final, '"r916 bm-a] "', 1),
        (n1_final, '"r915 bm-a] "', 1),
        (n1_final, '"r912 bm-a] "', 1),
        (n1_final, '"r909 bm-a] "', 1),
        (n1_final, '"r905 bm-a] "', 1),
        (n1_final, '"r901 bm-a] "', 1),
        (n1_final, '"r787 bm-c] "', 1),
        (n1_final, '"a_seed_base": 450_404,', 1),
        (n1_final, '"b_exit_seed_base": 452_404,', 1),
        (n1_final, "n1_w198", 4),
        (n1_final, "PERPETUAL_N1_W198_PREREG.md", 2),
        (n1_final, "_set_wave(198)", 1),
        (n1_final, 'sorted(w for w in WAVE_CONFIGS if w < 198)', 3),
        (n1_final, "range(17, 198):", 1),
        (n1_final, '"W199 A window; W199 freezer MUST re-derive on the "', 1),
        (n1_final, 'A first-clean 452_404..454_403 ', 1),
        (n1_final, "bm-a r916 freeze-closeout archive move", 1),
        (n1_final, "(the W198 seat MSG sits in fleet/inbox/", 1),
        (pf_final, '198: {"a": (450_404, 452_403), "b_exit": (452_404, 452_603),', 1),
        (pf_final, '197: {"a": (448_204, 450_203), "b_exit": (450_204, 450_403),', 1),
        (pf_final, '196: {"a": (446_004, 448_003), "b_exit": (448_004, 448_203),', 1),
        (pf_final, '195: {"a": (443_804, 445_803), "b_exit": (445_804, 446_003),', 1),
        (pf_final, '194: {"a": (441_604, 443_603), "b_exit": (443_604, 443_803),', 1),
        (pf_final, '193: {"a": (439_404, 441_403), "b_exit": (441_404, 441_603),', 1),
        (pf_final, "# W198 (bm-a r916 freeze", 1),
        (pf_final, "# W197 (bm-a r915 freeze", 1),
        (pf_final, "# W196 (bm-a r912 freeze", 1),
        (pf_final, "# W195 (bm-a r909 freeze", 1),
        (pf_final, "# W194 (bm-a r905 freeze", 1),
        (pf_final, "# W199+ projection (gate-derived r915)", 1),
        (pf_final, "archive PENDING WITH THIS freeze window -- bm-a r916 freeze", 1),
        (pf_final, "closeout archive move (the W198 seat MSG sits in", 1),
    ]
    for src, needle, cnt in checks:
        got = src.count(needle)
        if got != cnt:
            fails.append("post-edit needle %r count %d != %d"
                         % (needle[:50], got, cnt))
    # W199+ projection prose present (probe leg4 verbatim, r587)
    for needle in ("# 452_404..454_403 CLEAN hops=0 / B first-clean 452_604..452_803",
                   "W199 A window; W199 freezer MUST re-derive on the post-W198"):
        if needle not in pf_final:
            fails.append("pf W199+ prose missing: %r" % needle[:60])
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
         "cfg = n1.WAVE_CONFIGS[198]; "
         "print(json.dumps({'rows': len(B), 'w198': B.get(198), "
         "'w197': B.get(197), 'w196': B.get(196), 'w195': B.get(195), "
         "'w194': B.get(194), "
         "'cfg198': [cfg['a_seed_base'], cfg['b_exit_seed_base'], "
         "cfg['shard_subdir'], cfg['out_name'], cfg['engine_owner']]}))"],
        cwd=ROOT, capture_output=True, creationflags=CNW)
    assert chk.returncode == 0, "post-import check failed: %s" % chk.stderr[:300]
    post = json.loads(chk.stdout.decode("utf-8", "replace").strip().splitlines()[-1])
    assert post["rows"] == 196, "row count drift: %s" % post
    assert post["w198"] == {"a": [450404, 452403], "b_exit": [452404, 452603],
                           "engine_owner": "bm-a"}, "W198 row drift: %s" % post
    assert post["w197"] == {"a": [448204, 450203], "b_exit": [450204, 450403],
                           "engine_owner": "bm-a"}, "W197 row damaged: %s" % post
    assert post["w196"] == {"a": [446004, 448003], "b_exit": [448004, 448203],
                           "engine_owner": "bm-a"}, "W196 row damaged: %s" % post
    assert post["w195"] == {"a": [443804, 445803], "b_exit": [445804, 446003],
                           "engine_owner": "bm-a"}, "W195 row damaged: %s" % post
    assert post["w194"] == {"a": [441604, 443603], "b_exit": [443604, 443803],
                           "engine_owner": "bm-a"}, "W194 row damaged: %s" % post
    assert post["cfg198"] == [450404, 452404, "n1_w198",
                              "n1_w198_results.json", "bm-a"], \
        "W198 WAVE_CONFIGS drift: %s" % post
    facts["post_import"] = post

    # ---- G12 receipt + five-segment PASS prints (r578) ----
    with open(OUT_RCPT, "w", encoding="utf-8") as fh:
        json.dump(facts, fh, indent=1, ensure_ascii=False)
    print("PASS 1/5 law-mirror pf N1_BANDS[198] row: a=(450404,452403) "
          "b_exit=(452404,452603) engine_owner=bm-a (comment face rolled, "
          "W197 row byte-intact)")
    print("PASS 2/5 n1 WAVE_CONFIGS[198] row: batch=PERPETUAL-N1-W198 "
          "a_seed_base=450_404 b_exit_seed_base=452_404 shard=n1_w198 "
          "out=n1_w198_results.json owner=bm-a")
    print("PASS 3/5 n1 W198 materializer face: %d+%d+%d+%d derived pairs + "
          "%d+%d archive pairs all count-asserted; staircase FIFTY-EIGHTH; "
          "prior-wave parity->W197; deps range(17,198) all-landed clean; "
          "prereg presence assert->W198"
          % (len(pairs_mat), len(pairs_cfg), len(pairs_pf),
             len(pairs_claim), len(mat_arch), len(pf_arch)))
    print("PASS 4/5 guards: origin vacancy (fetch+show) + seat sha %s "
          "ancestor + registry 195->196 rows + AST+py_compile + W197/W196/W195 "
          "byte-intact post-import + stale sweeps clean + seat MSG "
          "archive-pending inbox/ verified"
          % SEAT_SHA)
    print("PASS 5/5 summary: W198 = 188th engine wave, bm-a 113th owned "
          "(rows 187+candidate per receipt leg0); A=450_404..452_403 "
          "hops=1 FIFTY-EIGHTH staircase; B=452_404..452_603 hops=1 "
          "own-A mutual exclusion; ZERO in-flight upstream (W197 "
          "finalize landed r915, head 847,745 K 431,320); ADMIT "
          "receipt machine-read; receipt=results/_r916bma_w198_freeze_receipt.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
