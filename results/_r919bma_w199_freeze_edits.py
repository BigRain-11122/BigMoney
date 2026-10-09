# -*- coding: utf-8 -*-
"""r919 bm-a W199 five-face freeze edits (five faces: pf N1_BANDS row +
n1 WAVE_CONFIGS row + n1 materializer face + n1 selftest claim + seat
MSG archive-pending verification face). Direct-author per the
r909/r912/r915/r916 physical chunk-roll machinery, rolled ONE generation:
extract current W198 fragments, roll W198->W199 with count-asserted
replacements, insert ADDITIVELY after the last registered row;
originals byte-identical zero-destroy. Old sides DERIVED AT RUNTIME by
the three-gen chain (zero transcription, r587): r912 AST triples
(W195_old, W196_new, cnt) -> r915 AST RULES_* -> W197 text ->
r916 AST RULES_W198_* -> W198 text = this build's old side; W199 fact
substitutions curated here.

Facts machine-read never transcribed (r587): ADMIT receipt
results/_r918bma_w199_probe_receipt.json (bands A 452604..454603 /
B 454604..454803, hops 1/1, FIFTY-NINTH staircase, leg0 rows 196
tail W198 owner_rows 188 bma_rows 113 ordinal 189 bma_ordinal 114
w198_ledger_head 849945, leg2 conflicts 0, leg3 origin vacancy, leg4
W200+ projection A 454604..456603 / B 454804..455003 hops 0/0
B-inside-A). Seat push 3a875bf43 (MSG-2026-10-09-1507-bma-w199-seat +
probe script + receipt, 3-item, r918 seat push, ancestor-verified).
W197=bm-a r915 five-face freeze+finalize one-pass SAME commit
522a0aef5 (dead-session freeze 13:0x + engine self-burn 12/12 landed
pre-death, estate absorbed per r899 law; ledger 847,745 EXACT
zero-deviation 4th consecutive window, K=431,320 EXACT, four pred
keys PASS). W198=bm-a r916 five-face freeze 82b881a4f + engine
self-burn 12/12 14:11.. (r916 session landed prereg+freeze same
window); finalize LANDED r917 session one-pass origin d4ea4b348
(ledger 847,745+2,200=849,945 EXACT five-window consecutive streak,
K=433,520 EXACT, four pred keys 4/4 PASS) -- ZERO in-flight upstream
seats, clean precondition freeze window. Seat MSG archive state =
PENDING (sits in fleet/inbox/ at freeze time, moves to processed/
with THIS freeze window closeout per S7 inbox-processing law -- the
r912 W196-style archive-pending pattern).

Laws honored: r511/r687 write-time fetch + origin-tail vacancy lock;
r560 insert-after-last-registered-row + anti-vanish + before/after
counts; r370 EOL-adaptive anchors; r580/r581 AST + py_compile gate;
r581 multi-line assert messages paren-wrapped; r578 five-segment PASS
prints; r776 fragment-needle law (physical dumps
results/_r919bma_w199_face_*.txt, re-verified against the live files
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
R916 = os.path.join(ROOT, "results", "_r916bma_w198_freeze_edits.py")
RCPT = os.path.join(ROOT, "results", "_r918bma_w199_probe_receipt.json")
OUT_RCPT = os.path.join(ROOT, "results", "_r919bma_w199_freeze_receipt.json")
SEAT_INBOX = "fleet/inbox/MSG-2026-10-09-1507-bma-w199-seat.md"
PREREG = os.path.join(ROOT, "research", "PERPETUAL_N1_W199_PREREG.md")
SEAT_SHA = "3a875bf43"
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


# ---- three-gen extraction: r912 triples + r915 rules + r916 rules ----
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
    t916 = extract_lists(R916, ("RULES_W198_MAT", "RULES_W198_CFG",
                                "RULES_W198_PF", "RULES_W198_CLAIM"))
    assert set(t916) == {"RULES_W198_MAT", "RULES_W198_CFG",
                         "RULES_W198_PF", "RULES_W198_CLAIM"}, \
        "r916 lists missing: %s" % sorted(t916)
    return t912, t915, t916


def apply_rules(text, rules, tag):
    for (a, b) in rules:
        if a in text:
            text = text.replace(a, b)
    return text


# ---- W199 fact substitution rules (curated; applied to W198 sides) ----
RULES_W199_MAT = [
    ("# --- W198 materializer face (r916 bm-a freeze, own-series law",
     "# --- W199 materializer face (r919 bm-a freeze, own-series law"),
    ("one-hundred-thirteenth owned", "one-hundred-fourteenth owned"),
    ("rows 112 + candidate); wave 197 = first free number after",
     "rows 113 + candidate); wave 198 = first free number after"),
    ("the REGISTERED W197 row (bm-a r915 freeze 522a0aef5) --",
     "the REGISTERED W198 row (bm-a r916 freeze 82b881a4f) --"),
    ("(W2..W197 all registered). Seat", "(W2..W198 all registered). Seat"),
    ("MSG-2026-10-09-1355-bma-w198-seat pushed",
     "MSG-2026-10-09-1507-bma-w199-seat pushed"),
    ("to origin 525630e39 BEFORE this freeze",
     "to origin 3a875bf43 BEFORE this freeze"),
    ("the W197 finalize product already on origin since r915, not",
     "the W198 finalize product already on origin since r917, not"),
    ("at fetch (r915 seat push), zero merge, zero",
     "at fetch (r918 seat push), zero merge, zero"),
    ("ONE HUNDRED-AND-NINETY-EIGHTH engine wave BY",
     "ONE HUNDRED-AND-NINETY-NINTH engine wave BY"),
    ("MACHINE-DERIVE (engine_owner rows 187 + candidate; gate",
     "MACHINE-DERIVE (engine_owner rows 188 + candidate; gate"),
    ("W1..W197 finalize ALL LANDED (net chain head 847,745,",
     "W1..W198 finalize ALL LANDED (net chain head 849,945,"),
    ("K=431,320 merged pool; W197 finalize one-pass bm-a r915)",
     "K=433,520 merged pool; W198 finalize one-pass bm-a r917)"),
    ("always on. ADMIT receipt results/_r915bma_w198_probe_receipt.json;",
     "always on. ADMIT receipt results/_r918bma_w199_probe_receipt.json;"),
    ("not a re-pick (R250: W198 bands were",
     "not a re-pick (R250: W199 bands were"),
    ("    _set_wave(198)", "    _set_wave(199)"),
    ('WAVE_CONFIGS[197]["a_seed_base"] == pf.N1_BANDS[197]["a"][0]',
     'WAVE_CONFIGS[198]["a_seed_base"] == pf.N1_BANDS[198]["a"][0]'),
    ('"W198 A band drift vs law mirror"', '"W199 A band drift vs law mirror"'),
    ('WAVE_CONFIGS[197]["b_exit_seed_base"] ==',
     'WAVE_CONFIGS[198]["b_exit_seed_base"] =='),
    ('pf.N1_BANDS[197]["b_exit"][0], "W198 B band drift vs law mirror"',
     'pf.N1_BANDS[198]["b_exit"][0], "W199 B band drift vs law mirror"'),
    ('WAVE_CONFIGS[197].get("engine_owner") ==',
     'WAVE_CONFIGS[198].get("engine_owner") =='),
    ('pf.N1_BANDS[197].get("engine_owner") == "bm-a"',
     'pf.N1_BANDS[198].get("engine_owner") == "bm-a"'),
    ('"W198 engine_owner drift (law mirror parity)"',
     '"W199 engine_owner drift (law mirror parity)"'),
    ("w197_a", "w198_a"),
    ("w197_b", "w198_b"),
    ('"W198 A/B band overlap"', '"W199 A/B band overlap"'),
    ('"W198 hits SEED_REGISTRY"', '"W199 hits SEED_REGISTRY"'),
    ('f"W198 {nm} hits v1"', 'f"W199 {nm} hits v1"'),
    ('f"W198 {nm} hits W1"', 'f"W199 {nm} hits W1"'),
    ('f"W198 {nm} hits probe seeds"', 'f"W199 {nm} hits probe seeds"'),
    ("# prior-wave disjointness W2..W197 (single state: all",
     "# prior-wave disjointness W2..W198 (single state: all"),
    ("WAVE_CONFIGS if w < 198):", "WAVE_CONFIGS if w < 199):"),
    ('f"W198 A hits W{wprev}"', 'f"W199 A hits W{wprev}"'),
    ('f"W198 B hits W{wprev}"', 'f"W199 B hits W{wprev}"'),
    ("n3r1_used197", "n3r1_used198"),
    ('"W198 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"',
     '"W199 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"'),
    ('"W198 bands must clear the lfc actual draw range"',
     '"W199 bands must clear the lfc actual draw range"'),
    ('"W198 bands must clear the options_wave2 actual draw range"',
     '"W199 bands must clear the options_wave2 actual draw range"'),
    ("# band facts (law sec.4 W198 row, r795): A = FIRST-CLEAN past",
     "# band facts (law sec.4 W199 row, r795): A = FIRST-CLEAN past"),
    ("# the registered W197 B band (the arithmetic continuation",
     "# the registered W198 B band (the arithmetic continuation"),
    ("# 450_204..452_203 is REFUSED at its own start by the W197",
     "# 452_404..454_403 is REFUSED at its own start by the W198"),
    ("# B band 450_204..450_403, exactly as the W197 prereg sec5.5 +",
     "# B band 452_404..452_603, exactly as the W198 prereg sec5.5 +"),
    ("# bm-a r914 probe leg4 succession projection notes",
     "# bm-a r915 probe leg4 succession projection notes"),
    ("# 450_404..452_403; A base == prior-wave B tail+1 (450_403+1)",
     "# 452_604..454_603; A base == prior-wave B tail+1 (452_603+1)"),
    ("-- A-hops-prior-B staircase FIFTY-EIGHTH",
     "-- A-hops-prior-B staircase FIFTY-NINTH"),
    ("# continuation 450_404..450_603 is CLEAN on the registered",
     "# continuation 452_604..452_803 is CLEAN on the registered"),
    ("# universe but lands INSIDE the W198 A band window --",
     "# universe but lands INSIDE the W199 A band window --"),
    ("# 452_404 and lands 452_404..452_603, hops=1, non-rotational",
     "# 454_604 and lands 454_604..454_803, hops=1, non-rotational"),
    ("# (452_403+1) machine-checkable; cross-window convergence",
     "# (454_603+1) machine-checkable; cross-window convergence"),
    ("# with the W197 prereg sec5.5 + bm-a r914 probe leg4",
     "# with the W198 prereg sec5.5 + bm-a r915 probe leg4"),
    ("# honored (post-W197 universe re-derive + own-wave A",
     "# honored (post-W198 universe re-derive + own-wave A"),
    ("# reservation when deriving B); seat MSG-1355 tail,",
     "# reservation when deriving B); seat MSG-1507 tail,"),
    ('assert WAVE_CONFIGS[198]["a_seed_base"] == 450_404 == 450_403 + 1, (',
     'assert WAVE_CONFIGS[199]["a_seed_base"] == 452_604 == 452_603 + 1, ('),
    ('"W198 A must be the first-clean window past the registered "',
     '"W199 A must be the first-clean window past the registered "'),
    ('"W197 B band tail 450_403+1 (arithmetic continuation "',
     '"W198 B band tail 452_603+1 (arithmetic continuation "'),
    ('"450_204..452_203 REFUSED at its own start by the W197 B "',
     '"452_404..454_403 REFUSED at its own start by the W198 B "'),
    ('"band 450_204..450_403, exactly as the W197 prereg sec5.5 + "',
     '"band 452_404..452_603, exactly as the W198 prereg sec5.5 + "'),
    ('"bm-a r914 probe leg4 succession projection notes "',
     '"bm-a r915 probe leg4 succession projection notes "'),
    ('"staircase FIFTY-EIGHTH instance, E36 card)")',
     '"staircase FIFTY-NINTH instance, E36 card)")'),
    ("arith_a197 = set(range(450_404, 452_404))",
     "arith_a198 = set(range(452_604, 454_604))"),
    ("assert not (arith_a197 & reg_ints), \\",
     "assert not (arith_a198 & reg_ints), \\"),
    ('"W198 A window must be CLEAN (first-clean ADMIT face past prior-wave B)"',
     '"W199 A window must be CLEAN (first-clean ADMIT face past prior-wave B)"'),
    ('assert WAVE_CONFIGS[198]["b_exit_seed_base"] == 452_404 == 452_403 + 1, (',
     'assert WAVE_CONFIGS[199]["b_exit_seed_base"] == 454_604 == 454_603 + 1, ('),
    ('"W198 B must be the first-clean window past the own-wave A "',
     '"W199 B must be the first-clean window past the own-wave A "'),
    ('"band tail 452_403+1 (arithmetic continuation "',
     '"band tail 454_603+1 (arithmetic continuation "'),
    ('"450_404..450_603 CLEAN on the registered universe but "',
     '"452_604..452_803 CLEAN on the registered universe but "'),
    ('"lands INSIDE the W198 A band window; same-freeze mutual "',
     '"lands INSIDE the W199 A band window; same-freeze mutual "'),
    ('"own-wave A window reserved jumps to 452_404, first-clean "',
     '"own-wave A window reserved jumps to 454_604, first-clean "'),
    ("arith_b197 = set(range(452_404, 452_604))",
     "arith_b198 = set(range(454_604, 454_804))"),
    ("assert not (arith_b197 & reg_ints), \\",
     "assert not (arith_b198 & reg_ints), \\"),
    ('"W198 B window must be CLEAN (first-clean ADMIT face past own-wave A)"',
     '"W199 B window must be CLEAN (first-clean ADMIT face past own-wave A)"'),
    ("assert not (arith_b197 & arith_a197), \\",
     "assert not (arith_b198 & arith_a198), \\"),
    ('"W198 A/B same-freeze mutual exclusion (B hops past own A)"',
     '"W199 A/B same-freeze mutual exclusion (B hops past own A)"'),
    ('assert _entry_shard_of(0, 12) == ("PERPETUAL-N1-W198-SHARD-0",',
     'assert _entry_shard_of(0, 12) == ("PERPETUAL-N1-W199-SHARD-0",'),
    ('"n1w198-0of12"), "W198 entry identity"',
     '"n1w199-0of12"), "W199 entry identity"'),
    ('assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W198-SHARD-11",',
     'assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W199-SHARD-11",'),
    ('"n1w198-11of12")', '"n1w199-11of12")'),
    ('assert SHARD_DIR.endswith("n1_w198") and OUT.endswith(',
     'assert SHARD_DIR.endswith("n1_w199") and OUT.endswith('),
    ('"n1_w198_results.json"), "W198 path drift"',
     '"n1_w199_results.json"), "W199 path drift"'),
    ('f"W198 shard dir collides with W{wprev}"',
     'f"W199 shard dir collides with W{wprev}"'),
    ("# W198 finalize cumulative deps: W17..W197 outputs ALL PRESENT",
     "# W199 finalize cumulative deps: W17..W198 outputs ALL PRESENT"),
    ("# (landed net chain head 847,745 = W197 bm-a r915 one-pass)",
     "# (landed net chain head 849,945 = W198 bm-a r917 one-pass)"),
    ("for _depw in range(17, 198):", "for _depw in range(17, 199):"),
    ('f"W198 finalize cumulative dep (W{_depw} output) missing"',
     'f"W199 finalize cumulative dep (W{_depw} output) missing"'),
    ("# registered wave below 198 composes; wave 15 excluded by",
     "# registered wave below 199 composes; wave 15 excluded by"),
    ("# design; SINGLE STATE (W2..W197 all registered -- no",
     "# design; SINGLE STATE (W2..W198 all registered -- no"),
    ("assert sorted(w for w in WAVE_CONFIGS if w < 198) == \\",
     "assert sorted(w for w in WAVE_CONFIGS if w < 199) == \\"),
    ("[w for w in range(16, 198)], \\", "[w for w in range(16, 199)], \\"),
    ('"W198 prior-wave set must derive from registry keys (no 15; " \\',
     '"W199 prior-wave set must derive from registry keys (no 15; " \\'),
    ('"W2..W197 registered single state)"', '"W2..W198 registered single state)"'),
    ('"research", "PERPETUAL_N1_W198_PREREG.md")), \\',
     '"research", "PERPETUAL_N1_W199_PREREG.md")), \\'),
    ('"W198 per-wave prereg missing (materializer requirement)"',
     '"W199 per-wave prereg missing (materializer requirement)"'),
]

RULES_W199_CFG = [
    ('198: {"batch": "PERPETUAL-N1-W198",', '199: {"batch": "PERPETUAL-N1-W199",'),
    ('PERPETUAL_N1_W198_PREREG.md (wave-level frozen',
     'PERPETUAL_N1_W199_PREREG.md (wave-level frozen'),
    ('ONE HUNDRED-AND-NINETY-EIGHTH ENGINE-OWNED WAVE',
     'ONE HUNDRED-AND-NINETY-NINTH ENGINE-OWNED WAVE'),
    ('engine_owner rows 187 + candidate), ',
     'engine_owner rows 188 + candidate), '),
    ('number law after the REGISTERED W197 row bm-a r915 freeze ',
     'number law after the REGISTERED W198 row bm-a r916 freeze '),
    ('522a0aef5, SINGLE STATE zero seat gap W2..W197 all ',
     '82b881a4f, SINGLE STATE zero seat gap W2..W198 all '),
    ('registered; W1..W197 finalize ALL LANDED (W197 bm-a r915 ',
     'registered; W1..W198 finalize ALL LANDED (W198 bm-a r917 '),
    ('one-pass, ledger head 847,745, merged pool K=431,320) -- ',
     'one-pass, ledger head 849,945, merged pool K=433,520) -- '),
    ('MSG-2026-10-09-1355-bma-w198-seat PUSHED to origin 525630e39 ',
     'MSG-2026-10-09-1507-bma-w199-seat PUSHED to origin 3a875bf43 '),
    ('(3-item; the W197 finalize product already on origin since r915, not re-shipped; W146 precedent); ',
     '(3-item; the W198 finalize product already on origin since r917, not re-shipped; W146 precedent); '),
    ('at fetch (r915 seat push), zero merge, zero ',
     'at fetch (r918 seat push), zero merge, zero '),
    ('engine_owner=bm-a, wave 197: ', 'engine_owner=bm-a, wave 198: '),
    ('"A = FIRST-CLEAN past the registered W197 B band (the "',
     '"A = FIRST-CLEAN past the registered W198 B band (the "'),
    ('"arithmetic continuation 450_204..452_203 is REFUSED at its "',
     '"arithmetic continuation 452_404..454_403 is REFUSED at its "'),
    ('"own start by the W197 B band 450_204..450_403, exactly as "',
     '"own start by the W198 B band 452_404..452_603, exactly as "'),
    ('"the W197 prereg sec5.5 + bm-a r914 probe leg4 succession "',
     '"the W198 prereg sec5.5 + bm-a r915 probe leg4 succession "'),
    ('"450_404..452_403; A base == prior-wave B tail+1 "',
     '"452_604..454_603; A base == prior-wave B tail+1 "'),
    ('"machine-checkable = A-hops-prior-B staircase FIFTY-EIGHTH "',
     '"machine-checkable = A-hops-prior-B staircase FIFTY-NINTH "'),
    ('"arithmetic continuation 450_404..450_603 is CLEAN on the "',
     '"arithmetic continuation 452_604..452_803 is CLEAN on the "'),
    ('"registered universe but lands INSIDE the W198 A band "',
     '"registered universe but lands INSIDE the W199 A band "'),
    ('"jumps to 452_404, first-clean 452_404..452_603 hops=1, "',
     '"jumps to 454_604, first-clean 454_604..454_803 hops=1, "'),
    ('"convergence with the W197 prereg sec5.5 + bm-a r914 probe leg4 + "',
     '"convergence with the W198 prereg sec5.5 + bm-a r915 probe leg4 + "'),
    ('"r915 probe succession projection notes re-derived -- all "',
     '"r918 probe succession projection notes re-derived -- all "'),
    ('"MANDATORY notes honored (post-W197 universe re-derive + "',
     '"MANDATORY notes honored (post-W198 universe re-derive + "'),
    ('"results/_r915bma_w198_probe_receipt.json; W199+ projection "',
     '"results/_r918bma_w199_probe_receipt.json; W200+ projection "'),
    ('"per this window gate: A first-clean 452_404..454_403 "',
     '"per this window gate: A first-clean 454_604..456_603 "'),
    ('"CLEAN / B first-clean 452_604..452_803 CLEAN -- naive "',
     '"CLEAN / B first-clean 454_804..455_003 CLEAN -- naive "'),
    ('"W198 B band 452_404..452_603 will refuse the naive "',
     '"W199 B band 454_604..454_803 will refuse the naive "'),
    ('"W199 A window; W199 freezer MUST re-derive on the "',
     '"W200 A window; W200 freezer MUST re-derive on the "'),
    ('"post-W198 universe AND reserve the own-wave A window "',
     '"post-W199 universe AND reserve the own-wave A window "'),
    ('W1..W197 finalize ALL LANDED (W197 bm-a r915 ',
     'W1..W198 finalize ALL LANDED (W198 bm-a r917 '),
    ('W1..W197 finalize ALL LANDED (W197 "',
     'W1..W198 finalize ALL LANDED (W198 "'),
    ('"finalize one-pass bm-a r915, net chain head 847,745, "',
     '"finalize one-pass bm-a r917, net chain head 849,945, "'),
    ('"merged pool K=431,320) -- ZERO in-flight upstream "',
     '"merged pool K=433,520) -- ZERO in-flight upstream "'),
    ('"a_seed_base": 450_404,        # law sec.4 W198 A: 450_404..452_403 (FIRST-CLEAN past the registered W197 B band; arithmetic 450_204..452_203 REFUSED at own start by the W197 B band 450_204..450_403; hops=1; A-hops-prior-B staircase FIFTY-EIGHTH instance, E36 card; ordinal convergence per r587: W197 prereg sec5.5 prose anticipated fifty-eighth, r915 receipt machine-read FIFTY-EIGHTH)',
     '"a_seed_base": 452_604,        # law sec.4 W199 A: 452_604..454_603 (FIRST-CLEAN past the registered W198 B band; arithmetic 452_404..454_403 REFUSED at own start by the W198 B band 452_404..452_603; hops=1; A-hops-prior-B staircase FIFTY-NINTH instance, E36 card; ordinal convergence per r587: W198 prereg sec5.5 prose anticipated fifty-ninth, r918 receipt machine-read FIFTY-NINTH)'),
    ('"b_exit_seed_base": 452_404,   # law sec.4 W198 B: 452_404..452_603 (FIRST-CLEAN past the own-wave A window; arithmetic 450_404..450_603 lands inside own-A, same-freeze mutual exclusion W141 precedent; reserved walk hops=1; B base == own-A tail+1)',
     '"b_exit_seed_base": 454_604,   # law sec.4 W199 B: 454_604..454_803 (FIRST-CLEAN past the own-wave A window; arithmetic 452_604..452_803 lands inside own-A, same-freeze mutual exclusion W141 precedent; reserved walk hops=1; B base == own-A tail+1)'),
    ('"shard_subdir": "n1_w198", "out_name": "n1_w198_results.json",',
     '"shard_subdir": "n1_w199", "out_name": "n1_w199_results.json",'),
]

RULES_W199_PF = [
    ('# W198 (bm-a r916 freeze, seat MSG-2026-10-09-1355-bma-w198-seat',
     '# W199 (bm-a r919 freeze, seat MSG-2026-10-09-1507-bma-w199-seat'),
    ('# pushed to origin 525630e39 pre-freeze r565 law (r915 seat',
     '# pushed to origin 3a875bf43 pre-freeze r565 law (r918 seat'),
    ('# (3-item; the W197 finalize product already on origin since r915,',
     '# (3-item; the W198 finalize product already on origin since r917,'),
    ('# = direct fast-forward behind-0 at fetch (r915 seat push),',
     '# = direct fast-forward behind-0 at fetch (r918 seat push),'),
    ('# band gate ADMIT results/_r915bma_w198_probe_receipt.json: A = FIRST-CLEAN',
     '# band gate ADMIT results/_r918bma_w199_probe_receipt.json: A = FIRST-CLEAN'),
    ('# past the registered W197 B band (arithmetic continuation',
     '# past the registered W198 B band (arithmetic continuation'),
    ('# 450_204..452_203 REFUSED at its own start by the W197 B band',
     '# 452_404..454_403 REFUSED at its own start by the W198 B band'),
    ('# 450_204..450_403, exactly as the W197 prereg sec5.5 + bm-a r914 probe',
     '# 452_404..452_603, exactly as the W198 prereg sec5.5 + bm-a r915 probe'),
    ('# honest forward walk hops=1 -> 450_404..452_403, non-rotational',
     '# honest forward walk hops=1 -> 452_604..454_603, non-rotational'),
    ('# (450_403+1) machine-checkable -- A-hops-prior-B staircase',
     '# (452_603+1) machine-checkable -- A-hops-prior-B staircase'),
    ('# FIFTY-EIGHTH instance, E36 card);', '# FIFTY-NINTH instance, E36 card);'),
    ('# continuation 450_404..450_603 CLEAN on the registered universe',
     '# continuation 452_604..452_803 CLEAN on the registered universe'),
    ('# but lands INSIDE the W198 A band window -- same-freeze mutual',
     '# but lands INSIDE the W199 A band window -- same-freeze mutual'),
    ('# own-wave A window reserved jumps to 452_404 -> 452_404..452_603,',
     '# own-wave A window reserved jumps to 454_604 -> 454_604..454_803,'),
    ('# own-wave A tail+1 (452_403+1) machine-checkable);',
     '# own-wave A tail+1 (454_603+1) machine-checkable);'),
    ('# W199+ projection (gate-derived r915): A first-clean',
     '# W200+ projection (gate-derived r918): A first-clean'),
    ('# 452_404..454_403 CLEAN hops=0 / B first-clean 452_604..452_803',
     '# 454_604..456_603 CLEAN hops=0 / B first-clean 454_804..455_003'),
    ('# registered W198 B band 452_404..452_603 will refuse the naive',
     '# registered W199 B band 454_604..454_803 will refuse the naive'),
    ('# W199 A window; W199 freezer MUST re-derive on the post-W198',
     '# W200 A window; W200 freezer MUST re-derive on the post-W199'),
    ('# NOT a re-pick (R250: W198 bands were never assigned).',
     '# NOT a re-pick (R250: W199 bands were never assigned).'),
    ('198: {"a": (450_404, 452_403), "b_exit": (452_404, 452_603),',
     '199: {"a": (452_604, 454_603), "b_exit": (454_604, 454_803),'),
]

RULES_W199_CLAIM = [
    ('"+ W198 materializer face [same guard set, dep=W17..W197 "',
     '"+ W199 materializer face [same guard set, dep=W17..W198 "'),
    ('"outputs ALL PRESENT (landed net chain head 847,745 = "',
     '"outputs ALL PRESENT (landed net chain head 849,945 = "'),
    ('"W197 bm-a r915 one-pass, K=431,320 merged pool) -- ZERO "',
     '"W198 bm-a r917 one-pass, K=433,520 merged pool) -- ZERO "'),
    ('"in-flight upstream seats, clean precondition, ONE HUNDRED-AND-NINETY-EIGHTH "',
     '"in-flight upstream seats, clean precondition, ONE HUNDRED-AND-NINETY-NINTH "'),
    ('"ENGINE-OWNED WAVE BY MACHINE-DERIVE (engine_owner rows 187 "',
     '"ENGINE-OWNED WAVE BY MACHINE-DERIVE (engine_owner rows 188 "'),
    ("bm-a's one-hundred-thirteenth owned claim per ",
     "bm-a's one-hundred-fourteenth owned claim per "),
    ('"machine-derive (engine_owner==bm-a rows 112 + candidate), "',
     '"machine-derive (engine_owner==bm-a rows 113 + candidate), "'),
    ('"A=FIRST-CLEAN past the registered W197 B band (staircase "',
     '"A=FIRST-CLEAN past the registered W198 B band (staircase "'),
    ('"FIFTY-EIGHTH instance, E36 card, hops=1) + B=FIRST-CLEAN past the "',
     '"FIFTY-NINTH instance, E36 card, hops=1) + B=FIRST-CLEAN past the "'),
    ('"results/_r915bma_w198_probe_receipt.json, law sec.4 W198 row, "',
     '"results/_r918bma_w199_probe_receipt.json, law sec.4 W199 row, "'),
    ('"r916 bm-a] "', '"r919 bm-a] "'),
]

# Archive face: W199 seat MSG is ARCHIVE-PENDING (sits in fleet/inbox/
# at freeze time; moves to processed/ with this window closeout per
# S7 law -- r912 W196-style pattern). Machine-rolled from the r915
# MAT_ARCHIVE/PF_ARCHIVE triples at runtime: old side = the r912
# archive-pending pattern rolled r912->r916, W196->W198 (the
# already-landed text in the live W198 fragments); new side = the
# r912 archive-pending pattern rolled r912->r919, W196->W199.


def _arch_r916(text):
    return text.replace("r912", "r916").replace("W196", "W198")


def _arch_r919(text):
    return text.replace("r912", "r919").replace("W196", "W199")


STALE = {
    "mat199": ["525630e39", "MSG-2026-10-09-1355", "r915 seat push",
               "_r915bma", "FIFTY-EIGHTH", "450_404",
               "450_404..452_403", "450_404..450_603",
               "450_204..452_203", "450_204..450_403", "450_403+1",
               "452_403+1", '== "bm-c"',
               "one-hundred-thirteenth", "rows 112 + candidate",
               "ONE HUNDRED-AND-NINETY-EIGHTH", "W2..W197 all",
               "arith_a197", "arith_b197", "w197_a", "w197_b",
               "n3r1_used197", "W1..W197 finalize", "847,745",
               "431,320", "r916 freeze-closeout", "one-pass bm-a r915",
               "W197 bm-a r915 one-pass", "bm-a r914 probe",
               "post-W197 universe", "MSG-1355 tail",
               "range(17, 198)", "jumps to 452_404", "n1w198", "n1_w198",
               "W198-SHARD", "W198 entry", "W198 path drift",
               "W198 shard dir", "w < 198):", "W2..W197 registered",
               "PERPETUAL_N1_W198_PREREG", "W198 per-wave prereg",
               "W198 finalize cumulative dep", "W198 prior-wave set",
               "disjointness W2..W197", "W198 A/B band", "W198 hits",
               "W198 bands", "W198 A window must", "W198 B window must",
               "W198 A/B same-freeze", "W199+ projection",
               "W198 A band drift", "W198 B band drift",
               "W198 engine_owner drift", "r909 freeze", "b9b962672",
               "the W195 finalize product", "since r910",
               "02cf6b44d", "522a0aef5",
               "archive ALREADY", "LANDED at the seat round r915",
               "processed/ at freeze time", "archive-pending N/A"],
    "cfg199": ["525630e39", "MSG-2026-10-09-1355", "_r915bma",
               "FIFTY-EIGHTH", "450_404", "450_404..452_403",
               "450_404..450_603", "450_204..452_203",
               "450_403+1", "452_403+1",
               "W197 prereg sec5.5", "bm-a r914",
               "the W197 finalize product", "since r915",
               "ONE HUNDRED-AND-NINETY-EIGHTH", "W2..W197 all",
               "W2..W197 registered", "engine_owner rows 187",
               "r915 seat push", "W199+ projection",
               "A first-clean 452_404..454_403",
               "B first-clean 452_604..452_803", "wave 197: ",
               '"a_seed_base": 450_404,', '"b_exit_seed_base": 452_404,',
               "n1_w198", "W198-SHARD", "r915 freeze", "post-W197 universe",
               "W197 B band 450", "one-pass bm-a r915", "W197 bm-a r915",
               "522a0aef5", "847,745", "431,320", "W1..W197 finalize"],
    "pf199": ["525630e39", "MSG-2026-10-09-1355", "_r915bma",
              "FIFTY-EIGHTH", "450_404", "450_204..452_203",
              "450_404..452_403", "450_404..450_603", "450_403+1",
              "452_403+1", "W199+ projection", "r915 seat",
              "gate-derived r915", "bm-a r914 probe",
              "W197 prereg sec5.5", "r916 freeze",
              "W197 B band", "jumps to 452_404", "W199 freezer",
              "post-W198 universe AND", "the W197 finalize product",
              "since r915", "archive ALREADY",
              "LANDED at the seat round r915", "processed/ (self-acked",
              "archive-pending N/A", "W198 bands were"],
    "claim199": ["_r915bma", "FIFTY-EIGHTH", "one-hundred-thirteenth",
                 "rows 112 + candidate", "rows 187 ",
                 "r916 bm-a] ", "W197 B band",
                 "ONE HUNDRED-AND-NINETY-EIGHTH",
                 "847,745", "431,320", "dep=W17..W197",
                 "W197 bm-a r915 one-pass"],
}


def roll_pairs(r912_list, r915_rules, r916_rules, w199_rules, drop_if, tag):
    """Three-gen chain: old side = r912 new side rolled by the r915 fact
    rules then the r916 fact rules (= the live W198 text, zero
    transcription); new side = W199 rule-rolled."""
    pairs = []
    for (w195_old, w196_new, cnt) in r912_list:
        if any(d in w196_new for d in drop_if):
            continue  # archive-state lines handled by explicit pairs
        w197 = apply_rules(w196_new, r915_rules, tag)
        if w197 == w196_new:
            fails.append("R915-ROLL UNCHANGED [%s]: %r" % (tag, w196_new[:90]))
            continue
        w198 = apply_rules(w197, r916_rules, tag)
        if w198 == w197:
            fails.append("R916-ROLL UNCHANGED [%s]: %r" % (tag, w197[:90]))
            continue
        w199 = apply_rules(w198, w199_rules, tag)
        if w199 == w198:
            fails.append("UNCHANGED PAIR [%s]: %r" % (tag, w198[:90]))
            continue
        pairs.append((w198, w199, cnt))
    return pairs


def main():
    facts = {"round": 919, "machine": "bm-a", "wave": 199,
             "archive_state": "pending (fleet/inbox/ at freeze time; "
                              "moves to processed/ with this window "
                              "closeout per S7 law -- r912 W196-style "
                              "pattern)"}

    # ---- G0 idempotence (already-applied abort) ----
    pf_probe = open(PFP, encoding="utf-8", errors="replace").read()
    if '199: {"a": (452_604, 454_603)' in pf_probe:
        print("ALREADY APPLIED: W199 pf row present -- abort")
        return 3

    # ---- G1 write-time fetch + origin tail lock (r511/r687) ----
    rc, _, err = git_out(["fetch", "origin"])
    assert rc == 0, "fetch failed: %s" % err[:200]
    rc, origin_pf, err = git_out(["show", "origin/main:scripts/perpetual_faces.py"])
    assert rc == 0, "origin pf blob read failed"
    assert "199: {" not in origin_pf, "ORIGIN TAIL MOVED: wave 199 already on origin"
    assert '198: {"a": (450_404, 452_403)' in origin_pf, "origin W198 row drift"
    rc, origin_n1, _ = git_out(["show", "origin/main:scripts/perpetual_faces_n1.py"])
    assert rc == 0
    assert "# --- W199 materializer face" not in origin_n1, "origin n1 W199 face present"
    assert '199: {"batch": "PERPETUAL-N1-W199"' not in origin_n1, \
        "origin n1 W199 cfg row present"
    rc, _, _ = git_out(["merge-base", "--is-ancestor", SEAT_SHA, "origin/main"])
    assert rc == 0, "seat push sha %s not an ancestor of origin/main" % SEAT_SHA
    facts["origin_vacancy"] = True

    # ---- G2 receipt + precheck parity (r587 / r359 machine numbers) ----
    r = json.load(open(RCPT, encoding="utf-8"))
    assert r["verdict"] == "ADMIT", "probe receipt not ADMIT"
    leg1 = r["legs"]["leg1"]
    A, B = leg1["A"], leg1["B"]
    assert A == [452604, 454603] and B == [454604, 454803], \
        "receipt bands drift: %s %s" % (A, B)
    assert leg1["hops_A"] == 1 and leg1["hops_B"] == 1
    assert leg1["ARITH_A"] == [452404, 454403] and \
        leg1["ARITH_B"] == [452604, 452803], "receipt arithmetic drift"
    assert r["bands"] == {"A": "452604_454603", "B": "454604_454803"}
    assert "FIFTY-NINTH" in leg1["A_semantics"], \
        "receipt A_semantics ordinal face missing"
    leg0 = r["legs"]["leg0"]
    assert leg0["rows"] == 196 and leg0["tail"] == "W198"
    assert leg0["ordinal"] == 189 and leg0["bma_ordinal"] == 114
    assert leg0["owner_rows"] == 188 and leg0["bma_rows"] == 113
    assert leg0["w198_ledger_head"] == 849945
    assert r["legs"]["leg2"]["conflicts"] == 0
    assert r["legs"]["leg3"]["origin_vacancy"] is True
    leg4 = r["legs"]["leg4"]
    assert leg4["W200p_A"] == "454604..456603" and \
        leg4["W200p_B"] == "454804..455003"
    assert leg4["hops_A"] == 0 and leg4["hops_B"] == 0
    assert leg4["W200p_B_lands_inside_W200p_A"] is True
    sys.path.insert(0, os.path.join(ROOT, "scripts"))
    from perpetual_faces import N1_BANDS  # noqa: E402
    assert max(N1_BANDS) == 198 and len(N1_BANDS) == 196, "registry tail drift"
    owners = {}
    for w, c in N1_BANDS.items():
        owners[c.get("engine_owner")] = owners.get(c.get("engine_owner"), 0) + 1
    owned = sum(v for k, v in owners.items() if k)
    assert owners.get("bm-a") == 113 and owners.get("bm-c") == 35 \
        and owned == 188, "owner counts drift: %s" % owners
    assert N1_BANDS[198] == {"a": (450404, 452403), "b_exit": (452404, 452603),
                            "engine_owner": "bm-a"}, "W198 row drift"
    assert N1_BANDS[197] == {"a": (448204, 450203), "b_exit": (450204, 450403),
                            "engine_owner": "bm-a"}, "W197 row drift"
    assert N1_BANDS[196] == {"a": (446004, 448003), "b_exit": (448004, 448203),
                            "engine_owner": "bm-a"}, "W196 row drift"
    assert N1_BANDS[195] == {"a": (443804, 445803), "b_exit": (445804, 446003),
                            "engine_owner": "bm-a"}, "W195 row drift"
    assert N1_BANDS[194] == {"a": (441604, 443603), "b_exit": (443604, 443803),
                            "engine_owner": "bm-a"}, "W194 row drift"
    assert os.path.exists(PREREG), "W199 per-wave prereg missing"
    assert os.path.exists(os.path.join(ROOT, SEAT_INBOX)), \
        "seat MSG not in fleet/inbox/ (archive-pending state)"
    assert not os.path.exists(os.path.join(
        ROOT, "fleet", "inbox", "processed",
        "MSG-2026-10-09-1507-bma-w199-seat.md")), \
        "seat MSG double-present (inbox AND processed)"
    assert os.path.exists(os.path.join(
        ROOT, "results", "perpetual_faces", "n1_w198_results.json")), \
        "W198 finalize product missing (dep precondition)"
    for f in ("results/_r918bma_w199_probe.py",
              "results/_r918bma_w199_probe_receipt.json"):
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

    # ---- G4 extract W198 chunks (LF face; r776 physical shapes) ----
    def chunk(text, start, end, stag):
        i = text.find(start)
        assert i >= 0, "start marker not found [%s]" % stag
        j = text.find(end, i)
        assert j > i, "end marker not found [%s]" % stag
        return text[i:j + len(end)]

    mat198 = chunk(n1n, "    # --- W198 materializer face",
                   "    _set_wave(2)", "mat198")
    assert mat198.rstrip("\n").endswith("_set_wave(2)"), "mat198 tail drift"
    cfg198 = chunk(n1n, '    198: {"batch": "PERPETUAL-N1-W198",',
                   '"engine_owner": "bm-a"},', "cfg198")
    pf198 = chunk(pfn, "    # W198 (bm-a r916 freeze, seat MSG-2026-10-09-1355-bma-w198-seat",
                 '"engine_owner": "bm-a"},', "pf198")
    claim198 = chunk(n1n, '          "+ W198 materializer face [same guard set',
                     '"r916 bm-a] "', "claim198")
    assert n1n.count(cfg198) == 1, "cfg198 not unique"
    assert n1n.count(claim198) == 1, "claim198 not unique"
    assert pfn.count(pf198) == 1, "pf198 not unique"
    for nm, frag in (("mat198", mat198), ("cfg198", cfg198),
                     ("pf198", pf198), ("claim198", claim198)):
        with open(os.path.join(ROOT, "results",
                               "_r919bma_w199_face_%s.txt" % nm.replace("198", "")),
                  "w", encoding="utf-8", newline="") as fh:
            fh.write(frag)
    facts["dump_sizes"] = {nm: len(frag) for nm, frag in
                           (("mat", mat198), ("cfg", cfg198),
                            ("pf", pf198), ("claim", claim198))}

    # ---- G5-G7 derive rolled pairs (three-gen bloodline AST chain) ----
    t912, t915, t916 = load_bloodline()
    drop_if = [x[0] if isinstance(x, tuple) else x for x in t915["DROP_IF"]]
    pairs_mat = roll_pairs(t912["R"], t915["RULES_MAT"], t916["RULES_W198_MAT"],
                           RULES_W199_MAT, drop_if, "mat")
    pairs_cfg = roll_pairs(t912["RC"], t915["RULES_CFG"], t916["RULES_W198_CFG"],
                           RULES_W199_CFG, drop_if, "cfg")
    pairs_pf = roll_pairs(t912["RP"], t915["RULES_PF"], t916["RULES_W198_PF"],
                          RULES_W199_PF, drop_if, "pf")
    pairs_claim = roll_pairs(t912["RQ"], t915["RULES_CLAIM"],
                             t916["RULES_W198_CLAIM"], RULES_W199_CLAIM,
                             drop_if, "claim")
    mat_arch = [(_arch_r916(old912), _arch_r919(old912), cnt)
                for (old912, new915, cnt) in t915["MAT_ARCHIVE"]]
    pf_arch = [(_arch_r916(old912), _arch_r919(old912), cnt)
               for (old912, new915, cnt) in t915["PF_ARCHIVE"]]
    facts["pair_counts"] = {"mat": len(pairs_mat), "cfg": len(pairs_cfg),
                            "pf": len(pairs_pf), "claim": len(pairs_claim),
                            "dropped_archive": (len(t912["R"]) - len(pairs_mat))
                            + (len(t912["RP"]) - len(pairs_pf)),
                            "archive_pairs": len(mat_arch) + len(pf_arch)}
    m = mat198
    for k, (old, new, cnt) in enumerate(pairs_mat):
        m = rep(m, old, new, cnt, "mat-%02d" % k)
    for k, (old, new, cnt) in enumerate(mat_arch):
        m = rep(m, old, new, cnt, "mat-arch-%d" % k)
    mat199 = m
    c = cfg198
    for k, (old, new, cnt) in enumerate(pairs_cfg):
        c = rep(c, old, new, cnt, "cfg-%02d" % k)
    cfg199 = c
    p = pf198
    for k, (old, new, cnt) in enumerate(pairs_pf):
        p = rep(p, old, new, cnt, "pf-%02d" % k)
    for k, (old, new, cnt) in enumerate(pf_arch):
        p = rep(p, old, new, cnt, "pf-arch-%d" % k)
    pf199 = p
    q = claim198
    for k, (old, new, cnt) in enumerate(pairs_claim):
        q = rep(q, old, new, cnt, "claim-%02d" % k)
    claim199 = q

    # ---- G7c stale sweeps on the rolled fragments (r780/r781) ----
    # NOTE: W198 band citations (the registered W198 B band
    # 452_404..452_603 and the W199 arithmetic continuations
    # 452_404..454_403 / 452_604..452_803) are LEGITIMATE content of
    # the W199 fragments (prior-wave face) -- they are NOT stale.
    frags = {"mat199": mat199, "cfg199": cfg199, "pf199": pf199,
             "claim199": claim199}
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
    n1_b = n1n.replace(cfg198, cfg198 + "\n" + IND19 + cfg199, 1)
    if n1_b == n1n:
        fails.append("cfg insertion no-op")
        print("RESULT: FAIL -- cfg insertion no-op")
        return 1
    w198_pos = n1_b.find("    # --- W198 materializer face")
    assert w198_pos >= 0
    t141 = n1_b.find("    # --- T-141 s2 lane face", w198_pos)
    assert t141 > w198_pos, "T-141 marker not found after W198 face"
    n1_c = n1_b[:t141] + mat199 + "\n" + n1_b[t141:]
    claim_anchor = claim198 + '\n          "+ T-141 s2 "'
    assert n1_c.count(claim_anchor) == 1, "claim anchor not unique"
    n1_final = n1_c.replace(claim_anchor,
                            claim198 + "\n" + claim199 +
                            '\n          "+ T-141 s2 "', 1)
    pf_final = pfn.replace(pf198, pf198 + "\n" + pf199, 1)
    if pf_final == pfn:
        fails.append("pf insertion no-op")

    # ---- G9 presence + anti-vanish + malformed scans (r560/r819) ----
    checks = [
        (n1_final, '199: {"batch": "PERPETUAL-N1-W199",', 1),
        (n1_final, '198: {"batch": "PERPETUAL-N1-W198",', 1),
        (n1_final, '197: {"batch": "PERPETUAL-N1-W197",', 1),
        (n1_final, '196: {"batch": "PERPETUAL-N1-W196",', 1),
        (n1_final, '195: {"batch": "PERPETUAL-N1-W195",', 1),
        (n1_final, '194: {"batch": "PERPETUAL-N1-W194",', 1),
        (n1_final, '193: {"batch": "PERPETUAL-N1-W193",', 1),
        (n1_final, "# --- W199 materializer face", 1),
        (n1_final, "# --- W198 materializer face", 1),
        (n1_final, "# --- W197 materializer face", 1),
        (n1_final, "# --- W196 materializer face", 1),
        (n1_final, "# --- W195 materializer face", 1),
        (n1_final, "# --- W194 materializer face", 1),
        (n1_final, "# --- W193 materializer face", 1),
        (n1_final, '"r919 bm-a] "', 1),
        (n1_final, '"r916 bm-a] "', 1),
        (n1_final, '"r915 bm-a] "', 1),
        (n1_final, '"r912 bm-a] "', 1),
        (n1_final, '"r909 bm-a] "', 1),
        (n1_final, '"r905 bm-a] "', 1),
        (n1_final, '"r901 bm-a] "', 1),
        (n1_final, '"r787 bm-c] "', 1),
        (n1_final, '"a_seed_base": 452_604,', 1),
        (n1_final, '"b_exit_seed_base": 454_604,', 1),
        (n1_final, "n1_w199", 4),
        (n1_final, "PERPETUAL_N1_W199_PREREG.md", 2),
        (n1_final, "_set_wave(199)", 1),
        (n1_final, 'sorted(w for w in WAVE_CONFIGS if w < 199)', 3),
        (n1_final, "range(17, 199):", 1),
        (n1_final, '"W200 A window; W200 freezer MUST re-derive on the "', 1),
        (n1_final, 'A first-clean 454_604..456_603 ', 1),
        (n1_final, "bm-a r919 freeze-closeout archive move", 1),
        (n1_final, "(the W199 seat MSG sits in fleet/inbox/", 1),
        (pf_final, '199: {"a": (452_604, 454_603), "b_exit": (454_604, 454_803),', 1),
        (pf_final, '198: {"a": (450_404, 452_403), "b_exit": (452_404, 452_603),', 1),
        (pf_final, '197: {"a": (448_204, 450_203), "b_exit": (450_204, 450_403),', 1),
        (pf_final, '196: {"a": (446_004, 448_003), "b_exit": (448_004, 448_203),', 1),
        (pf_final, '195: {"a": (443_804, 445_803), "b_exit": (445_804, 446_003),', 1),
        (pf_final, '194: {"a": (441_604, 443_603), "b_exit": (443_604, 443_803),', 1),
        (pf_final, '193: {"a": (439_404, 441_403), "b_exit": (441_404, 441_603),', 1),
        (pf_final, "# W199 (bm-a r919 freeze", 1),
        (pf_final, "# W198 (bm-a r916 freeze", 1),
        (pf_final, "# W197 (bm-a r915 freeze", 1),
        (pf_final, "# W196 (bm-a r912 freeze", 1),
        (pf_final, "# W195 (bm-a r909 freeze", 1),
        (pf_final, "# W194 (bm-a r905 freeze", 1),
        (pf_final, "# W200+ projection (gate-derived r918)", 1),
        (pf_final, "archive PENDING WITH THIS freeze window -- bm-a r919 freeze", 1),
        (pf_final, "closeout archive move (the W199 seat MSG sits in", 1),
    ]
    for src, needle, cnt in checks:
        got = src.count(needle)
        if got != cnt:
            fails.append("post-edit needle %r count %d != %d"
                         % (needle[:50], got, cnt))
    # W200+ projection prose present (probe leg4 verbatim, r587)
    for needle in ("# 454_604..456_603 CLEAN hops=0 / B first-clean 454_804..455_003",
                   "W200 A window; W200 freezer MUST re-derive on the post-W199"):
        if needle not in pf_final:
            fails.append("pf W200+ prose missing: %r" % needle[:60])
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
         "cfg = n1.WAVE_CONFIGS[199]; "
         "print(json.dumps({'rows': len(B), 'w199': B.get(199), "
         "'w198': B.get(198), 'w197': B.get(197), 'w196': B.get(196), "
         "'w195': B.get(195), 'w194': B.get(194), "
         "'cfg199': [cfg['a_seed_base'], cfg['b_exit_seed_base'], "
         "cfg['shard_subdir'], cfg['out_name'], cfg['engine_owner']]}))"],
        cwd=ROOT, capture_output=True, creationflags=CNW)
    assert chk.returncode == 0, "post-import check failed: %s" % chk.stderr[:300]
    post = json.loads(chk.stdout.decode("utf-8", "replace").strip().splitlines()[-1])
    assert post["rows"] == 197, "row count drift: %s" % post
    assert post["w199"] == {"a": [452604, 454603], "b_exit": [454604, 454803],
                           "engine_owner": "bm-a"}, "W199 row drift: %s" % post
    assert post["w198"] == {"a": [450404, 452403], "b_exit": [452404, 452603],
                           "engine_owner": "bm-a"}, "W198 row damaged: %s" % post
    assert post["w197"] == {"a": [448204, 450203], "b_exit": [450204, 450403],
                           "engine_owner": "bm-a"}, "W197 row damaged: %s" % post
    assert post["w196"] == {"a": [446004, 448003], "b_exit": [448004, 448203],
                           "engine_owner": "bm-a"}, "W196 row damaged: %s" % post
    assert post["w195"] == {"a": [443804, 445803], "b_exit": [445804, 446003],
                           "engine_owner": "bm-a"}, "W195 row damaged: %s" % post
    assert post["w194"] == {"a": [441604, 443603], "b_exit": [443604, 443803],
                           "engine_owner": "bm-a"}, "W194 row damaged: %s" % post
    assert post["cfg199"] == [452604, 454604, "n1_w199",
                              "n1_w199_results.json", "bm-a"], \
        "W199 WAVE_CONFIGS drift: %s" % post
    facts["post_import"] = post

    # ---- G12 receipt + five-segment PASS prints (r578) ----
    with open(OUT_RCPT, "w", encoding="utf-8") as fh:
        json.dump(facts, fh, indent=1, ensure_ascii=False)
    print("PASS 1/5 law-mirror pf N1_BANDS[199] row: a=(452604,454603) "
          "b_exit=(454604,454803) engine_owner=bm-a (comment face rolled, "
          "W198 row byte-intact)")
    print("PASS 2/5 n1 WAVE_CONFIGS[199] row: batch=PERPETUAL-N1-W199 "
          "a_seed_base=452_604 b_exit_seed_base=454_604 shard=n1_w199 "
          "out=n1_w199_results.json owner=bm-a")
    print("PASS 3/5 n1 W199 materializer face: %d+%d+%d+%d derived pairs + "
          "%d+%d archive pairs all count-asserted; staircase FIFTY-NINTH; "
          "prior-wave parity->W198; deps range(17,199) all-landed clean; "
          "prereg presence assert->W199"
          % (len(pairs_mat), len(pairs_cfg), len(pairs_pf),
             len(pairs_claim), len(mat_arch), len(pf_arch)))
    print("PASS 4/5 guards: origin vacancy (fetch+show) + seat sha %s "
          "ancestor + registry 196->197 rows + AST+py_compile + W198/W197/W196 "
          "byte-intact post-import + stale sweeps clean + seat MSG "
          "archive-pending inbox/ verified"
          % SEAT_SHA)
    print("PASS 5/5 summary: W199 = 189th engine wave, bm-a 114th owned "
          "(rows 188+candidate per receipt leg0); A=452_604..454_603 "
          "hops=1 FIFTY-NINTH staircase; B=454_604..454_803 hops=1 "
          "own-A mutual exclusion; ZERO in-flight upstream (W198 "
          "finalize landed r917, head 849,945 K 433,520); ADMIT "
          "receipt machine-read; receipt=results/_r919bma_w199_freeze_receipt.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
