# -*- coding: utf-8 -*-
"""r894 bm-a W191 freeze edits: four insertions (pf N1_BANDS[191] row +
n1 WAVE_CONFIGS[191] entry + n1 W191 materializer block + n1 W191
PASS-claim attribution). DRY flag: --dry = zero-write simulation
(r781 verify-separation law + freeze-edits dry-run precedent: full
stale+prose+AST asserts in memory BEFORE any write).

Bloodline: freeze-edits machinery (r773 pit law freeze-editor compliance +
r776 fragment-needle law + r781 verify-separation law), W191 facts
live-registry-driven (built by _r894bma_w191_freeze_buildgen.py: old
sides = the PHYSICAL W190 face fragments probed by the r893 window
(results/_r893bma_w191_probe_*.txt, re-verified against the live files
this window), new sides = the S90 W191 fact map, counts verified
pre-emission; extraction-from-EMISSION law: pairs AST-carried from the
r892 emitted tool -- the ground truth that produced the live faces).
Factual rolls disclosed in the buildgen docstring: sec8 succession
citation r892 -> r893 (the W190 sec7/sec8 backfill landed the r893
window, NOT a +2 session shift); archive-move prose r892-window ->
r892-closeout-window (the W191 seat MSG archive landed the r892 ROUND-
CLOSEOUT window adeaab565, same-round cross-window); ordinal words
continue the r892-established wave-number convention (NINETIETH ->
NINETY-FIRST, rows 180 + candidate per probe leg0 = 181st wave / 107th
bm-a-owned, matches the frozen prereg sec.0 exactly); deep-history
430_*/428_* dotted bands verified ZERO in the pair space -> S90 drops
them (mat parity tuples + the [186]-row r882 stale stamp ride verbatim
per quirks (e)/(f), cascade high-first keeps them intact).

r773 pit law compliance:
  (1) full string-face inventory empirically probed BEFORE TOK
      (r893 window four face dumps + stage-1 receipt, rc0; re-verified
      against the live files this window, count==1 each);
  (2) composite band strings tokenized WHOLE (every dotted band /
      seed-base row / jump phrase / projection pair is a single token;
      bare numerals run LAST);
  (3) post-edit full-file start>end malformed-window regex scan on BOTH
      touched files + double-CR scan;
  (4) every projection value re-derived FROM the on-disk probe receipt
      (r587 never-transcribe law);
  (5) r776 fragment-needle law: all needles taken from the PHYSICAL
      probe-dumped shapes;
  (6) r560 insert-after-last-registered-row + pre-edit live registry
      parity + origin anti-collision pre-check + write-time re-check
      (r530/r687: fetch + origin carries no W191 registration before
      this freeze);
  (7) AST gate after every edit batch (r580/r781)."""
import ast
import io
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, "scripts")
DRY = "--dry" in sys.argv
PF = r"scripts/perpetual_faces.py"
N1 = r"scripts/perpetual_faces_n1.py"
EO = '"engine_owner": "bm-a"},'
NL = "\r\n"
IND23 = " " * 23
IND10 = " " * 10

fail = []


def check(cond, msg):
    if not cond:
        fail.append(msg)
        print("FAIL:", msg)


# ---- receipts / machine-derived facts --------------------------------
probe = json.load(open(r"results\_r892bma_w191_probe_receipt.json",
                       encoding="utf-8"))
check(probe["verdict"] == "ADMIT", "pre-seat probe not ADMIT")
check(probe["bands"] == {"A": "435004_437003", "B": "437004_437203"},
      "probe band shape mismatch")
check(probe["legs"]["leg1"]["A"] == [435004, 437003], "A band mismatch")
check(probe["legs"]["leg1"]["B"] == [437004, 437203], "B band mismatch")
check(probe["legs"]["leg1"]["hops_A"] == 1 and probe["legs"]["leg1"]["hops_B"] == 1,
      "hops mismatch")
check(probe["legs"]["leg0"]["rows"] == 188 and probe["legs"]["leg0"]["tail"] == "W190",
      "leg0 registry tail mismatch")
check(probe["legs"]["leg0"]["ordinal"] == 181 and probe["legs"]["leg0"]["bma_ordinal"] == 107,
      "leg0 ordinal mismatch")
check(probe["legs"]["leg2"]["conflicts"] == 0, "leg2 conflicts nonzero")
check(probe["legs"]["leg3"]["origin_vacancy"] is True, "leg3 origin not vacant")
check(probe["legs"]["leg4"]["W192p_A"] == "437004..439003"
      and probe["legs"]["leg4"]["W192p_B"] == "437204..437403",
      "leg4 W192+ projection mismatch")

# origin anti-collision pre-check (r511 tail-lock / r687 write-time gate)
subprocess.run(["git", "fetch", "origin"], capture_output=True)
pf_o = subprocess.run(["git", "show", "origin/main:" + PF],
                      capture_output=True).stdout.decode("utf-8", "replace")
n1_o = subprocess.run(["git", "show", "origin/main:" + N1],
                      capture_output=True).stdout.decode("utf-8", "replace")
check('191: {"a": (435_004' not in pf_o, "origin pf already carries W191 row")
check("# W191 (bm-a r894 freeze" not in pf_o, "origin pf carries W191 block")
check('191: {"batch"' not in n1_o, "origin n1 already carries W191 entry")
check("# --- W191 materializer face" not in n1_o, "origin n1 carries W191 mat")
check('"r894 bm-a] "' not in n1_o, "origin n1 carries W191 claim")

# machine-derived shas (r587 / r812 path-derived precedent)
seat_sha = subprocess.run(
    ["git", "log", "origin/main", "--format=%h", "-n", "1", "--diff-filter=A",
     "--", "fleet/inbox/MSG-2026-10-08-2130-bma-w191-seat.md"],
    capture_output=True).stdout.decode().strip()
check(seat_sha == "1c28dd21d", "seat sha path-derived mismatch: " + seat_sha)
check(os.path.exists(os.path.join(
    "fleet", "inbox", "processed", "MSG-2026-10-08-2130-bma-w191-seat.md")),
    "seat MSG not in on-disk processed/ at freeze time (r892-closeout archive)")
w190_freeze_sha = subprocess.run(
    ["git", "log", "origin/main", "--format=%h", "-n", "1",
     "-S", '190: {"a": (432_804', "--", "scripts/perpetual_faces.py"],
    capture_output=True).stdout.decode().strip()
check(w190_freeze_sha == "0cce3c47e",
      "W190 five-face registration sha mismatch (content-anchored): "
      + w190_freeze_sha)

# ---- live-registry parity pre-check (edit-gate: never edit a drifted file)
sys.path.insert(0, ".")
import perpetual_faces as pfmod  # noqa: E402
check(len(pfmod.N1_BANDS) == 188, "live N1_BANDS row count drift: %d" % len(pfmod.N1_BANDS))
check(pfmod.N1_BANDS[190] == {"a": (432_804, 434_803),
                              "b_exit": (434_804, 435_003),
                              "engine_owner": "bm-a"}, "live W190 row drift")
check(191 not in pfmod.N1_BANDS, "live N1_BANDS already has 191")
check(os.path.exists(os.path.join("research", "PERPETUAL_N1_W191_PREREG.md")),
      "W191 per-wave prereg missing (materializer gate)")
prereg_o = subprocess.run(["git", "show", "origin/main:research/PERPETUAL_N1_W191_PREREG.md"],
                          capture_output=True)
check(prereg_o.returncode == 0, "W191 prereg absent on origin")

# ---- physical face dumps (r776 law; r893 window probes) ------------------
pfblk = io.open(r"results\_r893bma_w191_probe_pf_block.txt", encoding="utf-8",
                newline="").read()
entry = io.open(r"results\_r893bma_w191_probe_n1_entry.txt", encoding="utf-8",
                newline="").read()
mat = io.open(r"results\_r893bma_w191_probe_n1_mat.txt", encoding="utf-8",
              newline="").read()
claim = io.open(r"results\_r893bma_w191_probe_n1_claim.txt", encoding="utf-8",
                newline="").read()
check(mat.endswith("_set_wave(2)" + NL + "    "), "mat dump tail unexpected")
mat = mat[: -len(NL + "    ")]  # strip the T-141 line indent ride-along
check(mat.endswith("_set_wave(2)"), "mat core tail unexpected")


def vmap(src, pairs, negatives, name):
    for old, new, cnt in pairs:
        got = src.count(old)
        if got != cnt:
            check(False, "%s pair count %d != %d: %r" % (name, got, cnt, old[:60]))
            continue
        src = src.replace(old, new)
    for neg in negatives:
        check(neg not in src, "%s stale token remains: %r" % (name, neg[:60]))
    return src


PF_PAIRS = [('    # W190 (bm-a r892 freeze, seat MSG-2026-10-08-2035-bma-w190-seat', '    # W191 (bm-a r894 freeze, seat MSG-2026-10-08-2130-bma-w191-seat', 1), ('pushed to origin c177bf73b pre-freeze r565 law (r891 pre-seat', 'pushed to origin 1c28dd21d pre-freeze r565 law (r892 pre-seat', 1), ('(3-item; the W189 finalize product already on origin since r890,', '(3-item; the W190 finalize product already on origin since r892,', 1), ('# = direct fast-forward behind-0 at fetch (r891 pre-seat', '# = direct fast-forward behind-0 at fetch (r892 pre-seat', 1), ('# push), zero merge, zero --no-verify; self-ack archive ALREADY\r\n    # LANDED pre-freeze -- bm-a r892-window archive move (the W190\r\n    # seat MSG sits in fleet/inbox/processed/ at freeze time, honest\r\n    # archived);', '# push), zero merge, zero --no-verify; self-ack archive ALREADY\r\n    # LANDED pre-freeze -- bm-a r892-closeout-window archive move (the W191\r\n    # seat MSG sits in fleet/inbox/processed/ at freeze time, honest\r\n    # archived);', 1), ('band gate ADMIT results/_r891bma_w190_probe_receipt.json: A = FIRST-CLEAN', 'band gate ADMIT results/_r892bma_w191_probe_receipt.json: A = FIRST-CLEAN', 1), ('past the registered W189 B band (arithmetic continuation', 'past the registered W190 B band (arithmetic continuation', 1), ('432_604..434_603 REFUSED at its own start by the W189 B band', '434_804..436_803 REFUSED at its own start by the W190 B band', 1), ('432_604..432_803, exactly as the W189 seat W190+ projection + r891 probe', '434_804..435_003, exactly as the W190 seat W191+ projection + r892 probe', 1), ('# leg4 + r892 sec8 回填窗 succession projection notes all anticipated;', '# leg4 + r893 sec8 回填窗 succession projection notes all anticipated;', 1), ('honest forward walk hops=1 -> 432_804..434_803, non-rotational', 'honest forward walk hops=1 -> 435_004..437_003, non-rotational', 1), ('(432_803+1) machine-checkable -- A-hops-prior-B staircase', '(435_003+1) machine-checkable -- A-hops-prior-B staircase', 1), ('FIFTIETH instance, E36 card);', 'FIFTY-FIRST instance, E36 card);', 1), ('continuation 432_804..433_003 CLEAN on the registered universe', 'continuation 435_004..435_203 CLEAN on the registered universe', 1), ('but lands INSIDE the W190 A band window -- same-freeze mutual', 'but lands INSIDE the W191 A band window -- same-freeze mutual', 1), ('own-wave A window reserved jumps to 434_804 -> 434_804..435_003,', 'own-wave A window reserved jumps to 437_004 -> 437_004..437_203,', 1), ('own-wave A tail+1 (434_803+1) machine-checkable);', 'own-wave A tail+1 (437_003+1) machine-checkable);', 1), ('W190+ projection (gate-derived r891): A first-clean', 'W191+ projection (gate-derived r892): A first-clean', 1), ('434_804..436_803 CLEAN hops=0 / B first-clean 435_004..435_203', '437_004..439_003 CLEAN hops=0 / B first-clean 437_204..437_403', 1), ('registered W190 B band 434_804..435_003 will refuse the naive', 'registered W191 B band 437_004..437_203 will refuse the naive', 1), ('W191 A window; W191 freezer MUST re-derive on the post-W190', 'W192 A window; W192 freezer MUST re-derive on the post-W191', 1), ('NOT a re-pick (R250: W190 bands were never assigned).', 'NOT a re-pick (R250: W191 bands were never assigned).', 1), ('190: {"a": (432_804, 434_803), "b_exit": (434_804, 435_003),', '191: {"a": (435_004, 437_003), "b_exit": (437_004, 437_203),', 1)]

EN_PAIRS = [('190: {"batch": "PERPETUAL-N1-W190",', '191: {"batch": "PERPETUAL-N1-W191",', 1), ('"prereg": ("research/PERPETUAL_N1_W190_PREREG.md (wave-level frozen "', '"prereg": ("research/PERPETUAL_N1_W191_PREREG.md (wave-level frozen "', 1), ('new seed bands only; ONE HUNDRED-AND-NINETIETH ENGINE-OWNED WAVE ', 'new seed bands only; ONE HUNDRED-AND-NINETY-FIRST ENGINE-OWNED WAVE ', 1), ('BY MACHINE-DERIVE (engine_owner rows 179 + candidate), ', 'BY MACHINE-DERIVE (engine_owner rows 180 + candidate), ', 1), ('number law after the REGISTERED W189 row bm-a r890 freeze ', 'number law after the REGISTERED W190 row bm-a r892 freeze ', 1), ('8addea3eb, SINGLE STATE zero seat gap W2..W189 all ', '0cce3c47e, SINGLE STATE zero seat gap W2..W190 all ', 1), ('registered; W190 finalize landed same-window r827, ledger ', 'registered; W191 finalize landed same-window r827, ledger ', 1), ('head 823,128, merged pool K=413,720; seat published=reserved ', 'head 825,328, merged pool K=415,920; seat published=reserved ', 1), ('MSG-2026-10-08-2035-bma-w190-seat PUSHED to origin c177bf73b ', 'MSG-2026-10-08-2130-bma-w191-seat PUSHED to origin 1c28dd21d ', 1), ('probe receipt (3-item; the W189 finalize product already on origin since r890, not re-shipped; W146 precedent); ', 'probe receipt (3-item; the W190 finalize product already on origin since r892, not re-shipped; W146 precedent); ', 1), ('at fetch (r891 pre-seat push), zero merge, zero ', 'at fetch (r892 pre-seat push), zero merge, zero ', 1), ('engine_owner=bm-a, wave 189: ', 'engine_owner=bm-a, wave 190: ', 1), ('A = FIRST-CLEAN past the registered W189 B band (the ', 'A = FIRST-CLEAN past the registered W190 B band (the ', 1), ('arithmetic continuation 432_604..434_603 is REFUSED at its ', 'arithmetic continuation 434_804..436_803 is REFUSED at its ', 1), ('own start by the W189 B band 432_604..432_803, exactly as ', 'own start by the W190 B band 434_804..435_003, exactly as ', 1), ('the W189 seat W190+ projection + r891 probe leg4 + r892 sec8 回填窗 succession ', 'the W190 seat W191+ projection + r892 probe leg4 + r893 sec8 回填窗 succession ', 1), ('projection notes anticipated; honest forward walk hops=1 -> ', 'projection notes anticipated; honest forward walk hops=1 -> ', 1), ('432_804..434_803; A base == prior-wave B tail+1 ', '435_004..437_003; A base == prior-wave B tail+1 ', 1), ('machine-checkable = A-hops-prior-B staircase FIFTIETH ', 'machine-checkable = A-hops-prior-B staircase FIFTY-FIRST ', 1), ('arithmetic continuation 432_804..433_003 is CLEAN on the ', 'arithmetic continuation 435_004..435_203 is CLEAN on the ', 1), ('registered universe but lands INSIDE the W190 A band ', 'registered universe but lands INSIDE the W191 A band ', 1), ('jumps to 434_804, first-clean 434_804..435_003 hops=1, ', 'jumps to 437_004, first-clean 437_004..437_203 hops=1, ', 1), ('convergence with the W189 seat W190+ projection + r891 probe leg4 + ', 'convergence with the W190 seat W191+ projection + r892 probe leg4 + ', 1), ('r892 sec8 回填窗 succession projection notes re-derived -- all ', 'r893 sec8 回填窗 succession projection notes re-derived -- all ', 1), ('MANDATORY notes honored (post-W189 universe re-derive + ', 'MANDATORY notes honored (post-W190 universe re-derive + ', 1), ('results/_r891bma_w190_probe_receipt.json; W191+ projection ', 'results/_r892bma_w191_probe_receipt.json; W192+ projection ', 1), ('per this window gate: A first-clean 434_804..436_803 ', 'per this window gate: A first-clean 437_004..439_003 ', 1), ('CLEAN / B first-clean 435_004..435_203 CLEAN -- naive ', 'CLEAN / B first-clean 437_204..437_403 CLEAN -- naive ', 1), ('W190 B band 434_804..435_003 will refuse the naive ', 'W191 B band 437_004..437_203 will refuse the naive ', 1), ('W191 A window; W191 freezer MUST re-derive on the ', 'W192 A window; W192 freezer MUST re-derive on the ', 1), ('post-W190 universe AND reserve the own-wave A window ', 'post-W191 universe AND reserve the own-wave A window ', 1), ('staircase card); W1..W189 finalize ALL LANDED (W189 ', 'staircase card); W1..W190 finalize ALL LANDED (W190 ', 1), ('finalize one-pass bm-a r891, net chain head 823,128, ', 'finalize one-pass bm-a r892, net chain head 825,328, ', 1), ('merged pool K=413,720) -- ZERO in-flight upstream ', 'merged pool K=415,920) -- ZERO in-flight upstream ', 1), ('"a_seed_base": 432_804,        # law sec.4 W190 A: 432_804..434_803 (FIRST-CLEAN past the registered W189 B band; arithmetic 432_604..434_603 REFUSED at own start by the W189 B band; hops=1; A-hops-prior-B staircase FIFTIETH instance, E36 card; ordinal convergence per r587: W189 sec5.5 prose anticipated fiftieth, r891 receipt machine-read FIFTIETH)', '"a_seed_base": 435_004,        # law sec.4 W191 A: 435_004..437_003 (FIRST-CLEAN past the registered W190 B band; arithmetic 434_804..436_803 REFUSED at own start by the W190 B band; hops=1; A-hops-prior-B staircase FIFTY-FIRST instance, E36 card; ordinal convergence per r587: W190 sec5.5 prose anticipated fifty-first, r892 receipt machine-read FIFTY-FIRST)', 1), ('"b_exit_seed_base": 434_804,   # law sec.4 W190 B: 434_804..435_003 (FIRST-CLEAN past the own-wave A window; arithmetic 432_804..433_003 lands inside own-A, same-freeze mutual exclusion W141 precedent; reserved walk hops=1; B base == own-A tail+1)', '"b_exit_seed_base": 437_004,   # law sec.4 W191 B: 437_004..437_203 (FIRST-CLEAN past the own-wave A window; arithmetic 435_004..435_203 lands inside own-A, same-freeze mutual exclusion W141 precedent; reserved walk hops=1; B base == own-A tail+1)', 1), ('"shard_subdir": "n1_w190", "out_name": "n1_w190_results.json",', '"shard_subdir": "n1_w191", "out_name": "n1_w191_results.json",', 1)]

MAT_PAIRS = [('# --- W190 materializer face (r892 bm-a freeze, own-series law', '# --- W191 materializer face (r894 bm-a freeze, own-series law', 1), ('#     one-hundred-sixth owned per machine-derive (engine_owner==bm-a', '#     one-hundred-seventh owned per machine-derive (engine_owner==bm-a', 1), ('#     rows 105 + candidate); wave 189 = first free number after', '#     rows 106 + candidate); wave 190 = first free number after', 1), ('#     the REGISTERED W189 row (bm-a r890 freeze 8addea3eb) --', '#     the REGISTERED W190 row (bm-a r892 freeze 0cce3c47e) --', 1), ('#     SINGLE STATE zero seat gap (W2..W189 all registered). Seat', '#     SINGLE STATE zero seat gap (W2..W190 all registered). Seat', 1), ('#     published=reserved MSG-2026-10-08-2035-bma-w190-seat pushed', '#     published=reserved MSG-2026-10-08-2130-bma-w191-seat pushed', 1), ('#     to origin c177bf73b BEFORE this freeze, r565 law (payload', '#     to origin 1c28dd21d BEFORE this freeze, r565 law (payload', 1), ('#     the W189 finalize product already on origin since r890, not', '#     the W190 finalize product already on origin since r892, not', 1), ('#     at fetch (r891 pre-seat push), zero merge, zero', '#     at fetch (r892 pre-seat push), zero merge, zero', 1), ('#     --no-verify; self-ack inbox->processed archive ALREADY LANDED\r\n    #     pre-freeze -- bm-a r892-window archive move (the W190 seat\r\n    #     MSG sits in fleet/inbox/processed/ at freeze time, honest\r\n    #     archived).', '#     --no-verify; self-ack inbox->processed archive ALREADY LANDED\r\n    #     pre-freeze -- bm-a r892-closeout-window archive move (the W191 seat\r\n    #     MSG sits in fleet/inbox/processed/ at freeze time, honest\r\n    #     archived).', 1), ('#     ONE HUNDRED-AND-NINETIETH engine wave BY', '#     ONE HUNDRED-AND-NINETY-FIRST engine wave BY', 1), ('#     MACHINE-DERIVE (engine_owner rows 179 + candidate; gate', '#     MACHINE-DERIVE (engine_owner rows 180 + candidate; gate', 1), ('#     W1..W189 finalize ALL LANDED (net chain head 823,128,', '#     W1..W190 finalize ALL LANDED (net chain head 825,328,', 1), ('#     K=413,720 merged pool; W189 finalize one-pass bm-a r891)', '#     K=415,920 merged pool; W190 finalize one-pass bm-a r892)', 1), ('#     always on. ADMIT receipt results/_r891bma_w190_probe_receipt.json;', '#     always on. ADMIT receipt results/_r892bma_w191_probe_receipt.json;', 1), ('#     banned gate ADMIT 0; not a re-pick (R250: W190 bands were', '#     banned gate ADMIT 0; not a re-pick (R250: W191 bands were', 1), ('    _set_wave(190)', '    _set_wave(191)', 1), ('assert WAVE_CONFIGS[189]["a_seed_base"] == pf.N1_BANDS[189]["a"][0], \\', 'assert WAVE_CONFIGS[190]["a_seed_base"] == pf.N1_BANDS[190]["a"][0], \\', 1), ('"W190 A band drift vs law mirror"', '"W191 A band drift vs law mirror"', 1), ('assert WAVE_CONFIGS[189]["b_exit_seed_base"] == \\', 'assert WAVE_CONFIGS[190]["b_exit_seed_base"] == \\', 1), ('pf.N1_BANDS[189]["b_exit"][0], "W190 B band drift vs law mirror"', 'pf.N1_BANDS[190]["b_exit"][0], "W191 B band drift vs law mirror"', 1), ('assert WAVE_CONFIGS[189].get("engine_owner") == \\', 'assert WAVE_CONFIGS[190].get("engine_owner") == \\', 1), ('pf.N1_BANDS[189].get("engine_owner") == "bm-a", \\', 'pf.N1_BANDS[190].get("engine_owner") == "bm-a", \\', 1), ('"W190 engine_owner drift (law mirror parity)"', '"W191 engine_owner drift (law mirror parity)"', 1), ('w189_a = {A_SEED_BASE + j for j in range(A_N)}', 'w190_a = {A_SEED_BASE + j for j in range(A_N)}', 1), ('w189_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}', 'w190_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}', 1), ('assert not (w189_a & w189_b), "W190 A/B band overlap"', 'assert not (w190_a & w190_b), "W191 A/B band overlap"', 1), ('assert not (w189_a & reg_ints) and not (w189_b & reg_ints), \\', 'assert not (w190_a & reg_ints) and not (w190_b & reg_ints), \\', 1), ('"W190 hits SEED_REGISTRY"', '"W191 hits SEED_REGISTRY"', 1), ('for nm, band in (("A", w189_a), ("B", w189_b)):', 'for nm, band in (("A", w190_a), ("B", w190_b)):', 1), ('f"W190 {nm} hits v1"', 'f"W191 {nm} hits v1"', 1), ('f"W190 {nm} hits W1"', 'f"W191 {nm} hits W1"', 1), ('f"W190 {nm} hits probe seeds"', 'f"W191 {nm} hits probe seeds"', 1), ('"registered W188 row parity drift (r307; bm-a r882)"\r\n        assert pf.N1_BANDS[187] == {"a": (426_204, 428_203),\r\n                                    "b_exit": (428_204, 428_403),\r\n                                    "engine_owner": "bm-a"}, \\\r\n            "registered W189 row parity drift (r307; bm-a r890)"', '"registered W189 row parity drift (r307; bm-a r882)"\r\n        assert pf.N1_BANDS[187] == {"a": (426_204, 428_203),\r\n                                    "b_exit": (428_204, 428_403),\r\n                                    "engine_owner": "bm-a"}, \\\r\n            "registered W190 row parity drift (r307; bm-a r892)"', 1), ('# prior-wave disjointness W2..W189 (single state: all', '# prior-wave disjointness W2..W190 (single state: all', 1), ('for wprev in sorted(w for w in WAVE_CONFIGS if w < 190):', 'for wprev in sorted(w for w in WAVE_CONFIGS if w < 191):', 2), ('assert not (w189_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j', 'assert not (w190_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j', 1), ('for j in range(A_N)}), f"W190 A hits W{wprev}"', 'for j in range(A_N)}), f"W191 A hits W{wprev}"', 1), ('assert not (w189_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j', 'assert not (w190_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j', 1), ('for j in range(B_N)}), f"W190 B hits W{wprev}"', 'for j in range(B_N)}), f"W191 B hits W{wprev}"', 1), ('n3r1_used189 = set(range(70_000, 70_006))', 'n3r1_used190 = set(range(70_000, 70_006))', 1), ('assert not (w189_a & n3r1_used189) and not (w189_b & n3r1_used189), \\', 'assert not (w190_a & n3r1_used190) and not (w190_b & n3r1_used190), \\', 1), ('"W190 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"', '"W191 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"', 1), ('assert not (w189_a & lfc_actual12) and not (w189_b & lfc_actual12), \\', 'assert not (w190_a & lfc_actual12) and not (w190_b & lfc_actual12), \\', 1), ('"W190 bands must clear the lfc actual draw range"', '"W191 bands must clear the lfc actual draw range"', 1), ('assert not (w189_a & options_actual12) and \\', 'assert not (w190_a & options_actual12) and \\', 1), ('not (w189_b & options_actual12), \\', 'not (w190_b & options_actual12), \\', 1), ('"W190 bands must clear the options_wave2 actual draw range"', '"W191 bands must clear the options_wave2 actual draw range"', 1), ('# band facts (law sec.4 W190 row, r795): A = FIRST-CLEAN past', '# band facts (law sec.4 W191 row, r795): A = FIRST-CLEAN past', 1), ('# the registered W189 B band (the arithmetic continuation', '# the registered W190 B band (the arithmetic continuation', 1), ('# 432_604..434_603 is REFUSED at its own start by the W189', '# 434_804..436_803 is REFUSED at its own start by the W190', 1), ('# B band 432_604..432_803, exactly as the W189 seat W190+ projection +', '# B band 434_804..435_003, exactly as the W190 seat W191+ projection +', 1), ('# r891 probe leg4 + r892 sec8 回填窗 succession projection notes', '# r892 probe leg4 + r893 sec8 回填窗 succession projection notes', 1), ('# 432_804..434_803; A base == prior-wave B tail+1 (432_803+1)', '# 435_004..437_003; A base == prior-wave B tail+1 (435_003+1)', 1), ('# machine-checkable -- A-hops-prior-B staircase FIFTIETH', '# machine-checkable -- A-hops-prior-B staircase FIFTY-FIRST', 1), ('# continuation 432_804..433_003 is CLEAN on the registered', '# continuation 435_004..435_203 is CLEAN on the registered', 1), ('# universe but lands INSIDE the W190 A band window --', '# universe but lands INSIDE the W191 A band window --', 1), ('# 434_804 and lands 434_804..435_003, hops=1, non-rotational', '# 437_004 and lands 437_004..437_203, hops=1, non-rotational', 1), ('# (434_803+1) machine-checkable; cross-window convergence', '# (437_003+1) machine-checkable; cross-window convergence', 1), ('# with the W189 seat W190+ projection + r891 probe leg4 + r892 sec8', '# with the W190 seat W191+ projection + r892 probe leg4 + r893 sec8', 1), ('# honored (post-W189 universe re-derive + own-wave A', '# honored (post-W190 universe re-derive + own-wave A', 1), ('# reservation when deriving B); seat MSG-2035 tail,', '# reservation when deriving B); seat MSG-2130 tail,', 1), ('assert WAVE_CONFIGS[190]["a_seed_base"] == 432_804 == 432_803 + 1, (', 'assert WAVE_CONFIGS[191]["a_seed_base"] == 435_004 == 435_003 + 1, (', 1), ('"W190 A must be the first-clean window past the registered "', '"W191 A must be the first-clean window past the registered "', 1), ('"W189 B band tail 432_803+1 (arithmetic continuation "', '"W190 B band tail 435_003+1 (arithmetic continuation "', 1), ('"432_604..434_603 REFUSED at its own start by the W189 B "', '"434_804..436_803 REFUSED at its own start by the W190 B "', 1), ('"band 432_604..432_803, exactly as the W189 seat W190+ projection + "', '"band 434_804..435_003, exactly as the W190 seat W191+ projection + "', 1), ('"r891 probe leg4 + r892 sec8 回填窗 succession projection notes "', '"r892 probe leg4 + r893 sec8 回填窗 succession projection notes "', 1), ('"staircase FIFTIETH instance, E36 card)"', '"staircase FIFTY-FIRST instance, E36 card)"', 1), ('arith_a189 = set(range(432_804, 434_804))', 'arith_a190 = set(range(435_004, 437_004))', 1), ('assert not (arith_a189 & reg_ints), \\', 'assert not (arith_a190 & reg_ints), \\', 1), ('"W190 A window must be CLEAN (first-clean ADMIT face past prior-wave B)"', '"W191 A window must be CLEAN (first-clean ADMIT face past prior-wave B)"', 1), ('assert WAVE_CONFIGS[190]["b_exit_seed_base"] == 434_804 == 434_803 + 1, (', 'assert WAVE_CONFIGS[191]["b_exit_seed_base"] == 437_004 == 437_003 + 1, (', 1), ('"W190 B must be the first-clean window past the own-wave A "', '"W191 B must be the first-clean window past the own-wave A "', 1), ('"band tail 434_803+1 (arithmetic continuation "', '"band tail 437_003+1 (arithmetic continuation "', 1), ('"432_804..433_003 CLEAN on the registered universe but "', '"435_004..435_203 CLEAN on the registered universe but "', 1), ('"lands INSIDE the W190 A band window; same-freeze mutual "', '"lands INSIDE the W191 A band window; same-freeze mutual "', 1), ('"own-wave A window reserved jumps to 434_804, first-clean "', '"own-wave A window reserved jumps to 437_004, first-clean "', 1), ('arith_b189 = set(range(434_804, 435_004))', 'arith_b190 = set(range(437_004, 437_204))', 1), ('assert not (arith_b189 & reg_ints), \\', 'assert not (arith_b190 & reg_ints), \\', 1), ('"W190 B window must be CLEAN (first-clean ADMIT face past own-wave A)"', '"W191 B window must be CLEAN (first-clean ADMIT face past own-wave A)"', 1), ('assert not (arith_b189 & arith_a189), \\', 'assert not (arith_b190 & arith_a190), \\', 1), ('"W190 A/B same-freeze mutual exclusion (B hops past own A)"', '"W191 A/B same-freeze mutual exclusion (B hops past own A)"', 1), ('assert _entry_shard_of(0, 12) == ("PERPETUAL-N1-W190-SHARD-0",', 'assert _entry_shard_of(0, 12) == ("PERPETUAL-N1-W191-SHARD-0",', 1), ('"n1w190-0of12"), "W190 entry identity"', '"n1w191-0of12"), "W191 entry identity"', 1), ('assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W190-SHARD-11",', 'assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W191-SHARD-11",', 1), ('"n1w190-11of12")', '"n1w191-11of12")', 1), ('assert SHARD_DIR.endswith("n1_w190") and OUT.endswith(', 'assert SHARD_DIR.endswith("n1_w191") and OUT.endswith(', 1), ('"n1_w190_results.json"), "W190 path drift"', '"n1_w191_results.json"), "W191 path drift"', 1), ('f"W190 shard dir collides with W{wprev}"', 'f"W191 shard dir collides with W{wprev}"', 1), ('# W190 finalize cumulative deps: W17..W189 outputs ALL PRESENT', '# W191 finalize cumulative deps: W17..W190 outputs ALL PRESENT', 1), ('# (landed net chain head 823,128 = W189 bm-a r891 one-pass --', '# (landed net chain head 825,328 = W190 bm-a r892 one-pass --', 1), ('for _depw in range(17, 190):', 'for _depw in range(17, 191):', 1), ('f"W190 finalize cumulative dep (W{_depw} output) missing"', 'f"W191 finalize cumulative dep (W{_depw} output) missing"', 1), ('# registered wave below 190 composes; wave 15 excluded by', '# registered wave below 191 composes; wave 15 excluded by', 1), ('# design; SINGLE STATE (W2..W189 all registered -- no', '# design; SINGLE STATE (W2..W190 all registered -- no', 1), ('assert sorted(w for w in WAVE_CONFIGS if w < 190) == \\', 'assert sorted(w for w in WAVE_CONFIGS if w < 191) == \\', 1), ('[w for w in range(16, 190)], \\', '[w for w in range(16, 191)], \\', 1), ('"W190 prior-wave set must derive from registry keys (no 15; "', '"W191 prior-wave set must derive from registry keys (no 15; "', 1), ('"W2..W189 registered single state)"', '"W2..W190 registered single state)"', 1), ('PATHS.root, "research", "PERPETUAL_N1_W190_PREREG.md")), \\', 'PATHS.root, "research", "PERPETUAL_N1_W191_PREREG.md")), \\', 1), ('"W190 per-wave prereg missing (materializer requirement)"', '"W191 per-wave prereg missing (materializer requirement)"', 1)]

CL_PAIRS = [('"+ W190 materializer face [same guard set, dep=W17..W189 ', '"+ W191 materializer face [same guard set, dep=W17..W190 ', 1), ('"outputs ALL PRESENT (landed net chain head 823,128 = "', '"outputs ALL PRESENT (landed net chain head 825,328 = "', 1), ('"W189 bm-a r891 one-pass, K=413,720 merged pool; ZERO "', '"W190 bm-a r892 one-pass, K=415,920 merged pool; ZERO "', 1), ('"in-flight upstream seats), ONE HUNDRED-AND-NINETIETH "', '"in-flight upstream seats), ONE HUNDRED-AND-NINETY-FIRST "', 1), ('"ENGINE-OWNED WAVE BY MACHINE-DERIVE (engine_owner rows 179 "', '"ENGINE-OWNED WAVE BY MACHINE-DERIVE (engine_owner rows 180 "', 1), ("+ candidate) bm-a's one-hundred-sixth owned claim per ", "+ candidate) bm-a's one-hundred-seventh owned claim per ", 1), ('"machine-derive (engine_owner==bm-a rows 105 + candidate), "', '"machine-derive (engine_owner==bm-a rows 106 + candidate), "', 1), ('"A=FIRST-CLEAN past the registered W189 B band (staircase "', '"A=FIRST-CLEAN past the registered W190 B band (staircase "', 1), ('"FIFTIETH instance, E36 card, hops=1) + B=FIRST-CLEAN past the "', '"FIFTY-FIRST instance, E36 card, hops=1) + B=FIRST-CLEAN past the "', 1), ('"results/_r891bma_w190_probe_receipt.json, law sec.4 W190 row, "', '"results/_r892bma_w191_probe_receipt.json, law sec.4 W191 row, "', 1), ('"r892 bm-a] "', '"r894 bm-a] "', 1)]

PF_NEG = ['    # W190 (bm-a r892 freeze, seat MSG-2026-10-08-2035-bma-w190-seat', 'pushed to origin c177bf73b pre-freeze r565 law (r891 pre-seat', '(3-item; the W189 finalize product already on origin since r890,', '# = direct fast-forward behind-0 at fetch (r891 pre-seat', '# push), zero merge, zero --no-verify; self-ack archive ALREADY\r\n    # LANDED pre-freeze -- bm-a r892-window archive move (the W190\r\n    # seat MSG sits in fleet/inbox/processed/ at freeze time, honest\r\n    # archived);', 'band gate ADMIT results/_r891bma_w190_probe_receipt.json: A = FIRST-CLEAN', 'past the registered W189 B band (arithmetic continuation', '432_604..434_603 REFUSED at its own start by the W189 B band', '432_604..432_803, exactly as the W189 seat W190+ projection + r891 probe', '# leg4 + r892 sec8 回填窗 succession projection notes all anticipated;', 'honest forward walk hops=1 -> 432_804..434_803, non-rotational', '(432_803+1) machine-checkable -- A-hops-prior-B staircase', 'FIFTIETH instance, E36 card);', 'continuation 432_804..433_003 CLEAN on the registered universe', 'but lands INSIDE the W190 A band window -- same-freeze mutual', 'own-wave A window reserved jumps to 434_804 -> 434_804..435_003,', 'own-wave A tail+1 (434_803+1) machine-checkable);', 'W190+ projection (gate-derived r891): A first-clean', '434_804..436_803 CLEAN hops=0 / B first-clean 435_004..435_203', 'registered W190 B band 434_804..435_003 will refuse the naive', 'W191 A window; W191 freezer MUST re-derive on the post-W190', 'NOT a re-pick (R250: W190 bands were never assigned).', '190: {"a": (432_804, 434_803), "b_exit": (434_804, 435_003),', 'c177bf73b', 'r891 probe', 'r892 sec8', 'r891 pre-seat', '_r891bma', 'MSG-2026-10-08-2035', '8addea3eb', '823,128', '413,720', 'FIFTIETH', 'ONE HUNDRED-AND-NINETIETH']

EN_NEG = ['190: {"batch": "PERPETUAL-N1-W190",', '"prereg": ("research/PERPETUAL_N1_W190_PREREG.md (wave-level frozen "', 'new seed bands only; ONE HUNDRED-AND-NINETIETH ENGINE-OWNED WAVE ', 'BY MACHINE-DERIVE (engine_owner rows 179 + candidate), ', 'number law after the REGISTERED W189 row bm-a r890 freeze ', '8addea3eb, SINGLE STATE zero seat gap W2..W189 all ', 'registered; W190 finalize landed same-window r827, ledger ', 'head 823,128, merged pool K=413,720; seat published=reserved ', 'MSG-2026-10-08-2035-bma-w190-seat PUSHED to origin c177bf73b ', 'probe receipt (3-item; the W189 finalize product already on origin since r890, not re-shipped; W146 precedent); ', 'at fetch (r891 pre-seat push), zero merge, zero ', 'engine_owner=bm-a, wave 189: ', 'A = FIRST-CLEAN past the registered W189 B band (the ', 'arithmetic continuation 432_604..434_603 is REFUSED at its ', 'own start by the W189 B band 432_604..432_803, exactly as ', 'the W189 seat W190+ projection + r891 probe leg4 + r892 sec8 回填窗 succession ', '432_804..434_803; A base == prior-wave B tail+1 ', 'machine-checkable = A-hops-prior-B staircase FIFTIETH ', 'arithmetic continuation 432_804..433_003 is CLEAN on the ', 'registered universe but lands INSIDE the W190 A band ', 'jumps to 434_804, first-clean 434_804..435_003 hops=1, ', 'convergence with the W189 seat W190+ projection + r891 probe leg4 + ', 'r892 sec8 回填窗 succession projection notes re-derived -- all ', 'MANDATORY notes honored (post-W189 universe re-derive + ', 'results/_r891bma_w190_probe_receipt.json; W191+ projection ', 'per this window gate: A first-clean 434_804..436_803 ', 'CLEAN / B first-clean 435_004..435_203 CLEAN -- naive ', 'W190 B band 434_804..435_003 will refuse the naive ', 'W191 A window; W191 freezer MUST re-derive on the ', 'post-W190 universe AND reserve the own-wave A window ', 'staircase card); W1..W189 finalize ALL LANDED (W189 ', 'finalize one-pass bm-a r891, net chain head 823,128, ', 'merged pool K=413,720) -- ZERO in-flight upstream ', '"a_seed_base": 432_804,        # law sec.4 W190 A: 432_804..434_803 (FIRST-CLEAN past the registered W189 B band; arithmetic 432_604..434_603 REFUSED at own start by the W189 B band; hops=1; A-hops-prior-B staircase FIFTIETH instance, E36 card; ordinal convergence per r587: W189 sec5.5 prose anticipated fiftieth, r891 receipt machine-read FIFTIETH)', '"b_exit_seed_base": 434_804,   # law sec.4 W190 B: 434_804..435_003 (FIRST-CLEAN past the own-wave A window; arithmetic 432_804..433_003 lands inside own-A, same-freeze mutual exclusion W141 precedent; reserved walk hops=1; B base == own-A tail+1)', '"shard_subdir": "n1_w190", "out_name": "n1_w190_results.json",', '8addea3eb', 'c177bf73b', '823,128', '413,720', 'ONE HUNDRED-AND-NINETIETH', 'rows 179', 'r891 probe', '_r891bma', 'MSG-2026-10-08-2035', 'n1w190', 'n1_w190', 'PERPETUAL-N1-W190', 'PERPETUAL_N1_W190', 'FIFTIETH', 'bm-a r890 freeze', '434_804, first-clean']

MAT_NEG = ['# --- W190 materializer face (r892 bm-a freeze, own-series law', '#     one-hundred-sixth owned per machine-derive (engine_owner==bm-a', '#     rows 105 + candidate); wave 189 = first free number after', '#     the REGISTERED W189 row (bm-a r890 freeze 8addea3eb) --', '#     SINGLE STATE zero seat gap (W2..W189 all registered). Seat', '#     published=reserved MSG-2026-10-08-2035-bma-w190-seat pushed', '#     to origin c177bf73b BEFORE this freeze, r565 law (payload', '#     the W189 finalize product already on origin since r890, not', '#     at fetch (r891 pre-seat push), zero merge, zero', '#     --no-verify; self-ack inbox->processed archive ALREADY LANDED\r\n    #     pre-freeze -- bm-a r892-window archive move (the W190 seat\r\n    #     MSG sits in fleet/inbox/processed/ at freeze time, honest\r\n    #     archived).', '#     ONE HUNDRED-AND-NINETIETH engine wave BY', '#     MACHINE-DERIVE (engine_owner rows 179 + candidate; gate', '#     W1..W189 finalize ALL LANDED (net chain head 823,128,', '#     K=413,720 merged pool; W189 finalize one-pass bm-a r891)', '#     always on. ADMIT receipt results/_r891bma_w190_probe_receipt.json;', '#     banned gate ADMIT 0; not a re-pick (R250: W190 bands were', '    _set_wave(190)', 'assert WAVE_CONFIGS[189]["a_seed_base"] == pf.N1_BANDS[189]["a"][0], \\', '"W190 A band drift vs law mirror"', 'assert WAVE_CONFIGS[189]["b_exit_seed_base"] == \\', 'pf.N1_BANDS[189]["b_exit"][0], "W190 B band drift vs law mirror"', 'assert WAVE_CONFIGS[189].get("engine_owner") == \\', 'pf.N1_BANDS[189].get("engine_owner") == "bm-a", \\', '"W190 engine_owner drift (law mirror parity)"', 'w189_a = {A_SEED_BASE + j for j in range(A_N)}', 'w189_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}', 'assert not (w189_a & w189_b), "W190 A/B band overlap"', 'assert not (w189_a & reg_ints) and not (w189_b & reg_ints), \\', '"W190 hits SEED_REGISTRY"', 'for nm, band in (("A", w189_a), ("B", w189_b)):', 'f"W190 {nm} hits v1"', 'f"W190 {nm} hits W1"', 'f"W190 {nm} hits probe seeds"', '"registered W188 row parity drift (r307; bm-a r882)"\r\n        assert pf.N1_BANDS[187] == {"a": (426_204, 428_203),\r\n                                    "b_exit": (428_204, 428_403),\r\n                                    "engine_owner": "bm-a"}, \\\r\n            "registered W189 row parity drift (r307; bm-a r890)"', '# prior-wave disjointness W2..W189 (single state: all', 'for wprev in sorted(w for w in WAVE_CONFIGS if w < 190):', 'assert not (w189_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j', 'for j in range(A_N)}), f"W190 A hits W{wprev}"', 'assert not (w189_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j', 'for j in range(B_N)}), f"W190 B hits W{wprev}"', 'n3r1_used189 = set(range(70_000, 70_006))', 'assert not (w189_a & n3r1_used189) and not (w189_b & n3r1_used189), \\', '"W190 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"', 'assert not (w189_a & lfc_actual12) and not (w189_b & lfc_actual12), \\', '"W190 bands must clear the lfc actual draw range"', 'assert not (w189_a & options_actual12) and \\', 'not (w189_b & options_actual12), \\', '"W190 bands must clear the options_wave2 actual draw range"', '# band facts (law sec.4 W190 row, r795): A = FIRST-CLEAN past', '# the registered W189 B band (the arithmetic continuation', '# 432_604..434_603 is REFUSED at its own start by the W189', '# B band 432_604..432_803, exactly as the W189 seat W190+ projection +', '# r891 probe leg4 + r892 sec8 回填窗 succession projection notes', '# 432_804..434_803; A base == prior-wave B tail+1 (432_803+1)', '# machine-checkable -- A-hops-prior-B staircase FIFTIETH', '# continuation 432_804..433_003 is CLEAN on the registered', '# universe but lands INSIDE the W190 A band window --', '# 434_804 and lands 434_804..435_003, hops=1, non-rotational', '# (434_803+1) machine-checkable; cross-window convergence', '# with the W189 seat W190+ projection + r891 probe leg4 + r892 sec8', '# honored (post-W189 universe re-derive + own-wave A', '# reservation when deriving B); seat MSG-2035 tail,', 'assert WAVE_CONFIGS[190]["a_seed_base"] == 432_804 == 432_803 + 1, (', '"W190 A must be the first-clean window past the registered "', '"W189 B band tail 432_803+1 (arithmetic continuation "', '"432_604..434_603 REFUSED at its own start by the W189 B "', '"band 432_604..432_803, exactly as the W189 seat W190+ projection + "', '"r891 probe leg4 + r892 sec8 回填窗 succession projection notes "', '"staircase FIFTIETH instance, E36 card)"', 'arith_a189 = set(range(432_804, 434_804))', 'assert not (arith_a189 & reg_ints), \\', '"W190 A window must be CLEAN (first-clean ADMIT face past prior-wave B)"', 'assert WAVE_CONFIGS[190]["b_exit_seed_base"] == 434_804 == 434_803 + 1, (', '"W190 B must be the first-clean window past the own-wave A "', '"band tail 434_803+1 (arithmetic continuation "', '"432_804..433_003 CLEAN on the registered universe but "', '"lands INSIDE the W190 A band window; same-freeze mutual "', '"own-wave A window reserved jumps to 434_804, first-clean "', 'arith_b189 = set(range(434_804, 435_004))', 'assert not (arith_b189 & reg_ints), \\', '"W190 B window must be CLEAN (first-clean ADMIT face past own-wave A)"', 'assert not (arith_b189 & arith_a189), \\', '"W190 A/B same-freeze mutual exclusion (B hops past own A)"', 'assert _entry_shard_of(0, 12) == ("PERPETUAL-N1-W190-SHARD-0",', '"n1w190-0of12"), "W190 entry identity"', 'assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W190-SHARD-11",', '"n1w190-11of12")', 'assert SHARD_DIR.endswith("n1_w190") and OUT.endswith(', '"n1_w190_results.json"), "W190 path drift"', 'f"W190 shard dir collides with W{wprev}"', '# W190 finalize cumulative deps: W17..W189 outputs ALL PRESENT', '# (landed net chain head 823,128 = W189 bm-a r891 one-pass --', 'for _depw in range(17, 190):', 'f"W190 finalize cumulative dep (W{_depw} output) missing"', '# registered wave below 190 composes; wave 15 excluded by', '# design; SINGLE STATE (W2..W189 all registered -- no', 'assert sorted(w for w in WAVE_CONFIGS if w < 190) == \\', '[w for w in range(16, 190)], \\', '"W190 prior-wave set must derive from registry keys (no 15; "', '"W2..W189 registered single state)"', 'PATHS.root, "research", "PERPETUAL_N1_W190_PREREG.md")), \\', '"W190 per-wave prereg missing (materializer requirement)"', 'w189_', 'arith_a189', 'arith_b189', 'n3r1_used189', 'r891 probe', 'r891 pre-seat', '8addea3eb', 'ONE HUNDRED-AND-NINETIETH', 'one-hundred-sixth', 'rows 179', 'rows 105 ', 'range(17, 190)', 'range(16, 190)', 'PERPETUAL_N1_W190', 'PERPETUAL-N1-W190', 'MSG-2035', '_r891bma', 'bm-a r892-window', 'n1w190', 'n1_w190', '823,128', '413,720']

CL_NEG = ['"+ W190 materializer face [same guard set, dep=W17..W189 ', '"outputs ALL PRESENT (landed net chain head 823,128 = "', '"W189 bm-a r891 one-pass, K=413,720 merged pool; ZERO "', '"in-flight upstream seats), ONE HUNDRED-AND-NINETIETH "', '"ENGINE-OWNED WAVE BY MACHINE-DERIVE (engine_owner rows 179 "', "+ candidate) bm-a's one-hundred-sixth owned claim per ", '"machine-derive (engine_owner==bm-a rows 105 + candidate), "', '"A=FIRST-CLEAN past the registered W189 B band (staircase "', '"FIFTIETH instance, E36 card, hops=1) + B=FIRST-CLEAN past the "', '"results/_r891bma_w190_probe_receipt.json, law sec.4 W190 row, "', '"r892 bm-a] "', '823,128', '413,720', 'ONE HUNDRED-AND-NINETIETH', 'one-hundred-sixth', 'rows 179', 'rows 105 ', 'FIFTIETH', '_r891bma', 'r892 bm-a] ']
blk191 = vmap(pfblk, PF_PAIRS, PF_NEG, "pf")
entry191 = IND23 + vmap(entry, EN_PAIRS, EN_NEG, "entry")
mat191 = "    " + vmap(mat, MAT_PAIRS, MAT_NEG, "mat")
claim191 = IND10 + vmap(claim, CL_PAIRS, CL_NEG, "claim")

# ---- apply insertions (in-memory) ---------------------------------------
pfsrc = io.open(PF, encoding="utf-8", newline="").read()
n1src = io.open(N1, encoding="utf-8", newline="").read()

# pf: insert W191 block after the W190 row (last registered), before the
# dict close -- r560 insert-after-last-registered-row + post-anchor gate
seg = EO + NL + "}"
check(pfsrc.count(seg) == 1, "pf row-close segment not unique")
pfnew = pfsrc.replace(seg, EO + NL + blk191 + NL + "}", 1)

# n1 entry: after the W190 entry, before the WAVE_CONFIGS close
seg = EO + NL + IND23 + "}"
check(n1src.count(seg) == 1, "n1 entry-close segment not unique")
n1new = n1src.replace(seg, EO + NL + entry191 + NL + IND23 + "}", 1)

# n1 mat: insert the W191 block before the T-141 s2 lane face header
seg = "    # --- T-141 s2 lane face"
check(n1new.count(seg) == 1, "n1 T-141 mat anchor not unique")
n1new = n1new.replace(seg, mat191 + NL + seg, 1)

# n1 claim: insert the W191 attribution after the W190 claim tail line
# (r581 law: anchor = tail single-line literal + post-anchor guard)
seg = '"r892 bm-a] "' + NL + IND10 + '"+ T-141 s2 "'
check(n1new.count(seg) == 1, "n1 claim anchor not unique")
n1new = n1new.replace(seg, '"r892 bm-a] "' + NL + claim191 + NL + IND10 +
                      '"+ T-141 s2 "', 1)

# ---- gates (r780/r781/r560/r815 lineage) --------------------------------
ast.parse(pfnew)
ast.parse(n1new)
print("AST gate: both files parse OK")

# W191 presence + W190 anti-vanish (r560 law)
checks = [
    (pfnew, '191: {"a": (435_004, 437_003), "b_exit": (437_004, 437_203),', 1),
    (pfnew, '190: {"a": (432_804, 434_803), "b_exit": (434_804, 435_003),', 1),
    (pfnew, "# W191 (bm-a r894 freeze", 1),
    (pfnew, "# W190 (bm-a r892 freeze", 1),
    (n1new, '191: {"batch": "PERPETUAL-N1-W191",', 1),
    (n1new, '190: {"batch": "PERPETUAL-N1-W190",', 1),
    (n1new, "# --- W191 materializer face", 1),
    (n1new, "# --- W190 materializer face", 1),
    (n1new, '"r894 bm-a] "', 1),
    (n1new, '"r892 bm-a] "', 1),
    (n1new, '"a_seed_base": 435_004,', 1),
    (n1new, '"b_exit_seed_base": 437_004,', 1),
    (n1new, "n1_w191", 4),
    (n1new, "PERPETUAL_N1_W191_PREREG.md", 2),
]
for src, needle, cnt in checks:
    got = src.count(needle)
    check(got == cnt, "post-edit needle %r count %d != %d" % (needle[:50], got, cnt))

# W192+ projection prose present in the new W191 blocks (probe leg4
# verbatim; r819 post-edit assert bloodline + r776 fragment-needle law;
# pf header = self-wave W191+ per r845 precedent, n1 fragment =
# next-wave W192+)
check("# W191+ projection (gate-derived r892)" in pfnew,
      "pf W191+ projection head missing")
check('probe_receipt.json; W192+ projection "' in n1new,
      "n1 W192+ projection head fragment missing")
check("# 437_004..439_003 CLEAN hops=0 / B first-clean 437_204..437_403" in pfnew,
      "pf W192p prose missing")
check("W192 A window; W192 freezer MUST re-derive on the post-W191" in pfnew,
      "pf W192 freezer prose missing")
check('"W192 A window; W192 freezer MUST re-derive on the "' in n1new,
      "n1 W192 freezer fragment missing")
check('"W191 B band 437_004..437_203 will refuse the naive "' in n1new,
      "n1 W191-band refuse fragment missing")

# malformed-window scans (r819 bloodline regex: the XXX_YYY..XXX_YYY
# 3-digit-triplet window shape, first-triplet comparison -- the proven
# scan; broader shapes hit pre-existing prose false positives) +
# double-CR / triple-LF scans
pat = re.compile(r"(\d{3})_(\d{3})\.\.(\d{3})_(\d{3})")
for name, txt in (("pf", pfnew), ("n1", n1new)):
    bad = [mm.group() for mm in pat.finditer(txt)
           if int(mm.group(3)) < int(mm.group(1))]
    check(not bad, "%s malformed windows: %s" % (name, bad[:5]))
    check("\r\r" not in txt, "%s double-CR present" % name)
    check("\n\n\n" not in txt, "%s triple-LF present" % name)
print("malformed-window scans: CLEAN both files")

if fail:
    print("RESULT: FAIL (%d) -- zero writes" % len(fail))
    for f in fail:
        print("  -", f)
    sys.exit(1)

if DRY:
    print("DRY-RUN PASS: all gates green, zero writes "
          "(pf %d->%d B, n1 %d->%d B)" % (len(pfsrc), len(pfnew),
                                          len(n1src), len(n1new)))
    sys.exit(0)

# ---- write-time re-check (r687 law): re-fetch + origin vacancy re-verify
subprocess.run(["git", "fetch", "origin"], capture_output=True)
pf_o2 = subprocess.run(["git", "show", "origin/main:" + PF],
                       capture_output=True).stdout.decode("utf-8", "replace")
n1_o2 = subprocess.run(["git", "show", "origin/main:" + N1],
                       capture_output=True).stdout.decode("utf-8", "replace")
check('191: {"a": (435_004' not in pf_o2, "write-time: origin pf carries W191")
check('191: {"batch"' not in n1_o2, "write-time: origin n1 carries W191")
if fail:
    print("RESULT: FAIL at write-time re-check (%d) -- zero writes" % len(fail))
    for f in fail:
        print("  -", f)
    sys.exit(1)

# ---- live writes: n1 FIRST then pf (engine queue derive keys off the
# pf N1_BANDS row -- a row without a WAVE_CONFIGS entry would be a dead
# face for one tick; an entry without a row never ignites (safe order) --
# r666 law window face) ----------------------------------------------------
io.open(N1, "w", encoding="utf-8", newline="").write(n1new)
io.open(PF, "w", encoding="utf-8", newline="").write(pfnew)
print("LIVE WRITES DONE: pf %d->%d B, n1 %d->%d B" %
      (len(pfsrc), len(pfnew), len(n1src), len(n1new)))
print("freeze edits rc0: 4 insertions landed (pf row + n1 entry + mat + claim)")
