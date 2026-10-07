# -*- coding: utf-8 -*-
"""r830 bm-a W175 freeze edits: four insertions (pf N1_BANDS[175] row +
n1 WAVE_CONFIGS[175] entry + n1 W175 materializer block + n1 W175
PASS-claim attribution). DRY flag: --dry = zero-write simulation
(r781 verify-separation law + r811/r822/r826 dry-run precedent: full
stale+prose+AST asserts in memory BEFORE any write).

Bloodline: r819/r822/r826 freeze-edits machinery (r773 pit law freeze-editor
compliance + r776 fragment-needle law + r781 verify-separation law),
W175 facts live-registry-driven (built by _r830bma_w175_freeze_buildgen.py:
old sides = the PHYSICAL W174 face fragments probed to dumps this window,
new sides = the S74 W175 fact map, counts verified pre-emission):
  - pre-seat probe results/_r828bma_w175_probe_receipt.json rc0 ADMIT
    (A 399_804..401_803 staircase THIRTY-FIFTH instance E36 hops=1
    past the registered W174 B band 399_604..399_803; naive
    399_604..401_603 refused at its own start by the W174 B band --
    receipt A_semantics machine-cites 'W174 prereg sec5 item5 + W174
    seat MSG leg4 + r823 probe leg4' anticipation + MANDATE; B
    401_804..402_003 own-A mutual exclusion hops=1, naive
    399_804..400_003);
  - ordinal convergence: W174 sec5.5 prose anticipated 35th, r828
    receipt machine-read THIRTY-FIFTH -- no divergence this wave;
  - face probe results/_r830bma_w175_face_probe_receipt.json rc0 (all
    four W174 faces dumped + needle counts; this TOK is built from the
    PHYSICAL probe-dumped shapes, r776 law);
  - seat MSG-2026-10-07-1434-bma-w175-seat published on origin at
    25c414e95 (r828 pre-seat push, path-derived TRUE sha per r812
    precedent); r565 law: on origin BEFORE this freeze commit;
    self-ack archive ALREADY LANDED pre-freeze -- r828 same-window
    self-ack move (the seat MSG sits in fleet/inbox/processed/ at
    freeze time, honest archived);
  - per-wave prereg research/PERPETUAL_N1_W175_PREREG.md frozen at
    origin 7510a8acf (r829 build, banned gate ADMIT 0 re-verified at
    freeze this window);
  - W174 freeze registered sha machine-derived = db42a0d46 (git log
    origin/main --grep "W174 FREEZE"); W174 finalize one-pass landed
    r827: ledger head 788,212, merged pool K=380,720
    (n1_w174_results.json machine-read);
  - lineage constants disclosed (r795 precedent, passed through):
    (a) the "wave N-1 = first free number" mat-header label rides the
    vmap verbatim (off-by-one lineage quirk since W165 r795);
    (b) "law sec.4 W175 row, r795" band-facts template stamp keeps
    its r795;
    (c) "single-window derive (r812 merged the gate legs INTO the
    pre-seat probe...)" stays (historical merge citation);
    (d) the bm-a-owned ordinal word rolls ninetieth -> ninety-first
    (rows 90 + candidate = 91st owned per probe leg0);
    (e) mat parity-chain rows W138..W173 keep their historical stamps
    and tuples; the W174 row (the current registered tail) is APPENDED
    with its frozen values (397_604, 399_603)/(399_604, 399_803).

r773 pit law compliance:
  (1) full string-face inventory empirically probed BEFORE TOK
      (_r830bma_w175_face_probe.py -- four face dumps + needle-count
      receipt, rc0);
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
      (r530/r687: fetch + origin carries no W175 registration before
      this freeze);
  (7) AST gate after every edit batch (r580/r781)."""
import ast
import io
import json
import os
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
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
probe = json.load(open(r"results\_r828bma_w175_probe_receipt.json",
                       encoding="utf-8"))
check(probe["verdict"] == "ADMIT", "pre-seat probe not ADMIT")
check(probe["bands"] == {"A": "399804_401803", "B": "401804_402003"},
      "probe band shape mismatch")
check(probe["legs"]["leg1"]["A"] == [399804, 401803], "A band mismatch")
check(probe["legs"]["leg1"]["B"] == [401804, 402003], "B band mismatch")
check(probe["legs"]["leg1"]["hops_A"] == 1 and probe["legs"]["leg1"]["hops_B"] == 1,
      "hops mismatch")
check(probe["legs"]["leg0"]["rows"] == 172 and probe["legs"]["leg0"]["tail"] == "W174",
      "leg0 registry tail mismatch")
check(probe["legs"]["leg0"]["ordinal"] == 165 and probe["legs"]["leg0"]["bma_ordinal"] == 91,
      "leg0 ordinal mismatch")
check(probe["legs"]["leg2"]["conflicts"] == 0, "leg2 conflicts nonzero")
check(probe["legs"]["leg3"]["origin_vacancy"] is True, "leg3 origin not vacant")
check(probe["legs"]["leg4"]["W176p_A"] == "401804..403803"
      and probe["legs"]["leg4"]["W176p_B"] == "402004..402203",
      "leg4 W176+ projection mismatch")

# origin anti-collision pre-check (r511 tail-lock / r687 write-time gate)
subprocess.run(["git", "fetch", "origin"], capture_output=True)
pf_o = subprocess.run(["git", "show", "origin/main:" + PF],
                      capture_output=True).stdout.decode("utf-8", "replace")
n1_o = subprocess.run(["git", "show", "origin/main:" + N1],
                      capture_output=True).stdout.decode("utf-8", "replace")
check('175: {"a": (399_804' not in pf_o, "origin pf already carries W175 row")
check("W175 (bm-a r830 freeze" not in pf_o, "origin pf carries W175 block")
check('175: {"batch"' not in n1_o, "origin n1 already carries W175 entry")
check("# --- W175 materializer face" not in n1_o, "origin n1 carries W175 mat")
check('"r830 bm-a] "' not in n1_o, "origin n1 carries W175 claim")

# machine-derived shas (r587 / r812 path-derived precedent)
seat_sha = subprocess.run(
    ["git", "log", "origin/main", "--format=%h", "-n", "1", "--diff-filter=A",
     "--", "fleet/inbox/MSG-2026-10-07-1434-bma-w175-seat.md"],
    capture_output=True).stdout.decode().strip()
check(seat_sha == "25c414e95", "seat sha path-derived mismatch: " + seat_sha)
check(os.path.exists(os.path.join(
    "fleet", "inbox", "processed", "MSG-2026-10-07-1434-bma-w175-seat.md")),
    "seat MSG not in processed/ at freeze time (self-ack archive)")
w174_freeze_sha = subprocess.run(
    ["git", "log", "origin/main", "--format=%h", "-n", "1", "--grep=W174 FREEZE"],
    capture_output=True).stdout.decode().strip()
check(w174_freeze_sha == "db42a0d46", "W174 freeze sha mismatch: " + w174_freeze_sha)

# ---- live-registry parity pre-check (edit-gate: never edit a drifted file)
sys.path.insert(0, "scripts")
import perpetual_faces as pfmod  # noqa: E402
check(len(pfmod.N1_BANDS) == 172, "live N1_BANDS row count drift: %d" % len(pfmod.N1_BANDS))
check(pfmod.N1_BANDS[174] == {"a": (397_604, 399_603),
                              "b_exit": (399_604, 399_803),
                              "engine_owner": "bm-a"}, "live W174 row drift")
check(175 not in pfmod.N1_BANDS, "live N1_BANDS already has 175")
check(os.path.exists(os.path.join("research", "PERPETUAL_N1_W175_PREREG.md")),
      "W175 per-wave prereg missing (materializer gate)")
prereg_o = subprocess.run(["git", "show", "origin/main:research/PERPETUAL_N1_W175_PREREG.md"],
                          capture_output=True)
check(prereg_o.returncode == 0, "W175 prereg absent on origin")

# ---- physical face dumps (r776 law) -----------------------------------
pfblk = io.open(r"results\_r830bma_w175_probe_pf_block.txt", encoding="utf-8",
                newline="").read()
entry = io.open(r"results\_r830bma_w175_probe_n1_entry.txt", encoding="utf-8",
                newline="").read()
mat = io.open(r"results\_r830bma_w175_probe_n1_mat.txt", encoding="utf-8",
              newline="").read()
claim = io.open(r"results\_r830bma_w175_probe_n1_claim.txt", encoding="utf-8",
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


PF_PAIRS = [
    ('    # W174 (bm-a r826 freeze, seat MSG-2026-10-07-1247-bma-w174-seat', '    # W175 (bm-a r830 freeze, seat MSG-2026-10-07-1434-bma-w175-seat', 1),
    ('pushed to origin 9b0e1cb29 pre-freeze r565 law (r823 pre-seat', 'pushed to origin 25c414e95 pre-freeze r565 law (r828 pre-seat', 1),
    ('(3-item; the W173 finalize product already on origin since r823,', '(3-item; the W174 finalize product already on origin since r827,', 1),
    ('# = direct fast-forward behind-0 at fetch (r823 pre-seat', '# = direct fast-forward behind-0 at fetch (r828 pre-seat', 1),
    ('# push), zero merge, zero --no-verify; self-ack archive ALREADY\r\n    # LANDED pre-freeze -- r823 same-window self-ack move (the W174\r\n    # seat MSG sits in fleet/inbox/processed/ at freeze time, honest\r\n    # archived);', '# push), zero merge, zero --no-verify; self-ack archive ALREADY\r\n    # LANDED pre-freeze -- r828 same-window self-ack move (the W175\r\n    # seat MSG sits in fleet/inbox/processed/ at freeze time, honest\r\n    # archived);', 1),
    ('band gate ADMIT results/_r823bma_w174_probe_receipt.json: A = FIRST-CLEAN', 'band gate ADMIT results/_r828bma_w175_probe_receipt.json: A = FIRST-CLEAN', 1),
    ('past the registered W173 B band (arithmetic continuation', 'past the registered W174 B band (arithmetic continuation', 1),
    ('397_404..399_403 REFUSED at its own start by the W173 B band', '399_604..401_603 REFUSED at its own start by the W174 B band', 1),
    ('397_404..397_603, exactly as the W173 seat W174+ projection + r820 probe', '399_604..399_803, exactly as the W174 seat W175+ projection + r823 probe', 1),
    ('# leg4 + r823 sec8 succession projection notes all anticipated;', '# leg4 + r826 sec8 succession projection notes all anticipated;', 1),
    ('honest forward walk hops=1 -> 397_604..399_603, non-rotational', 'honest forward walk hops=1 -> 399_804..401_803, non-rotational', 1),
    ('(397_603+1) machine-checkable -- A-hops-prior-B staircase', '(399_803+1) machine-checkable -- A-hops-prior-B staircase', 1),
    ('THIRTY-FOURTH instance, E36 card);', 'THIRTY-FIFTH instance, E36 card);', 1),
    ('continuation 397_604..397_803 CLEAN on the registered universe', 'continuation 399_804..400_003 CLEAN on the registered universe', 1),
    ('but lands INSIDE the W174 A band window -- same-freeze mutual', 'but lands INSIDE the W175 A band window -- same-freeze mutual', 1),
    ('own-wave A window reserved jumps to 399_604 -> 399_604..399_803,', 'own-wave A window reserved jumps to 401_804 -> 401_804..402_003,', 1),
    ('own-wave A tail+1 (399_603+1) machine-checkable);', 'own-wave A tail+1 (401_803+1) machine-checkable);', 1),
    ('W174+ projection (gate-derived r823): A first-clean', 'W175+ projection (gate-derived r828): A first-clean', 1),
    ('399_604..401_603 CLEAN hops=0 / B first-clean 399_804..400_003', '401_804..403_803 CLEAN hops=0 / B first-clean 402_004..402_203', 1),
    ('registered W174 B band 399_604..399_803 will refuse the naive', 'registered W175 B band 401_804..402_003 will refuse the naive', 1),
    ('W175 A window; W175 freezer MUST re-derive on the post-W174', 'W176 A window; W176 freezer MUST re-derive on the post-W175', 1),
    ('NOT a re-pick (R250: W174 bands were never assigned).', 'NOT a re-pick (R250: W175 bands were never assigned).', 1),
    ('174: {"a": (397_604, 399_603), "b_exit": (399_604, 399_803),', '175: {"a": (399_804, 401_803), "b_exit": (401_804, 402_003),', 1),
]

EN_PAIRS = [
    ('174: {"batch": "PERPETUAL-N1-W174",', '175: {"batch": "PERPETUAL-N1-W175",', 1),
    ('"prereg": ("research/PERPETUAL_N1_W174_PREREG.md (wave-level frozen "', '"prereg": ("research/PERPETUAL_N1_W175_PREREG.md (wave-level frozen "', 1),
    ('new seed bands only; ONE HUNDRED-AND-SIXTY-FOURTH ENGINE-OWNED WAVE ', 'new seed bands only; ONE HUNDRED-AND-SIXTY-FIFTH ENGINE-OWNED WAVE ', 1),
    ('BY MACHINE-DERIVE (engine_owner rows 163 + candidate), ', 'BY MACHINE-DERIVE (engine_owner rows 164 + candidate), ', 1),
    ('number law after the REGISTERED W173 row bm-a r822 freeze ', 'number law after the REGISTERED W174 row bm-a r826 freeze ', 1),
    ('04e95748a, SINGLE STATE zero seat gap W2..W173 all ', 'db42a0d46, SINGLE STATE zero seat gap W2..W174 all ', 1),
    ('registered; W173 finalize landed same-window r823, ledger ', 'registered; W175 finalize landed same-window r827, ledger ', 1),
    ('head 786,012, merged pool K=378,520; seat published=reserved ', 'head 788,212, merged pool K=380,720; seat published=reserved ', 1),
    ('MSG-2026-10-07-1247-bma-w174-seat PUSHED to origin 9b0e1cb29 ', 'MSG-2026-10-07-1434-bma-w175-seat PUSHED to origin 25c414e95 ', 1),
    ('probe receipt (3-item; the W173 finalize product already on origin since r823, not re-shipped; W146 precedent); ', 'probe receipt (3-item; the W174 finalize product already on origin since r827, not re-shipped; W146 precedent); ', 1),
    ('at fetch (r823 pre-seat push), zero merge, zero ', 'at fetch (r828 pre-seat push), zero merge, zero ', 1),
    ('engine_owner=bm-a, wave 173: ', 'engine_owner=bm-a, wave 174: ', 1),
    ('A = FIRST-CLEAN past the registered W173 B band (the ', 'A = FIRST-CLEAN past the registered W174 B band (the ', 1),
    ('arithmetic continuation 397_404..399_403 is REFUSED at its ', 'arithmetic continuation 399_604..401_603 is REFUSED at its ', 1),
    ('own start by the W173 B band 397_404..397_603, exactly as ', 'own start by the W174 B band 399_604..399_803, exactly as ', 1),
    ('the W173 seat W174+ projection + r820 probe leg4 + r823 sec8 succession ', 'the W174 seat W175+ projection + r823 probe leg4 + r826 sec8 succession ', 1),
    ('projection notes anticipated; honest forward walk hops=1 -> ', 'projection notes anticipated; honest forward walk hops=1 -> ', 1),
    ('397_604..399_603; A base == prior-wave B tail+1 ', '399_804..401_803; A base == prior-wave B tail+1 ', 1),
    ('machine-checkable = A-hops-prior-B staircase THIRTY-FOURTH ', 'machine-checkable = A-hops-prior-B staircase THIRTY-FIFTH ', 1),
    ('arithmetic continuation 397_604..397_803 is CLEAN on the ', 'arithmetic continuation 399_804..400_003 is CLEAN on the ', 1),
    ('registered universe but lands INSIDE the W174 A band ', 'registered universe but lands INSIDE the W175 A band ', 1),
    ('jumps to 399_604, first-clean 399_604..399_803 hops=1, ', 'jumps to 401_804, first-clean 401_804..402_003 hops=1, ', 1),
    ('convergence with the W173 seat W174+ projection + r820 probe leg4 + ', 'convergence with the W174 seat W175+ projection + r823 probe leg4 + ', 1),
    ('r823 sec8 succession projection notes re-derived -- all ', 'r826 sec8 succession projection notes re-derived -- all ', 1),
    ('MANDATORY notes honored (post-W173 universe re-derive + ', 'MANDATORY notes honored (post-W174 universe re-derive + ', 1),
    ('results/_r823bma_w174_probe_receipt.json; W175+ projection ', 'results/_r828bma_w175_probe_receipt.json; W176+ projection ', 1),
    ('per this window gate: A first-clean 399_604..401_603 ', 'per this window gate: A first-clean 401_804..403_803 ', 1),
    ('CLEAN / B first-clean 399_804..400_003 CLEAN -- naive ', 'CLEAN / B first-clean 402_004..402_203 CLEAN -- naive ', 1),
    ('W174 B band 399_604..399_803 will refuse the naive ', 'W175 B band 401_804..402_003 will refuse the naive ', 1),
    ('W175 A window; W175 freezer MUST re-derive on the ', 'W176 A window; W176 freezer MUST re-derive on the ', 1),
    ('post-W174 universe AND reserve the own-wave A window ', 'post-W175 universe AND reserve the own-wave A window ', 1),
    ('staircase card); W1..W173 finalize ALL LANDED (W173 ', 'staircase card); W1..W174 finalize ALL LANDED (W174 ', 1),
    ('finalize one-pass bm-a r823, net chain head 786,012, ', 'finalize one-pass bm-a r827, net chain head 788,212, ', 1),
    ('merged pool K=378,520) -- ZERO in-flight upstream ', 'merged pool K=380,720) -- ZERO in-flight upstream ', 1),
    ('"a_seed_base": 397_604,        # law sec.4 W174 A: 397_604..399_603 (FIRST-CLEAN past the registered W173 B band; arithmetic 397_404..399_403 REFUSED at own start by the W173 B band; hops=1; A-hops-prior-B staircase THIRTY-FOURTH instance, E36 card; ordinal convergence per r587: W173 sec5.5 prose anticipated thirty-fourth, r823 receipt machine-read THIRTY-FOURTH)', '"a_seed_base": 399_804,        # law sec.4 W175 A: 399_804..401_803 (FIRST-CLEAN past the registered W174 B band; arithmetic 399_604..401_603 REFUSED at own start by the W174 B band; hops=1; A-hops-prior-B staircase THIRTY-FIFTH instance, E36 card; ordinal convergence per r587: W174 sec5.5 prose anticipated thirty-fifth, r828 receipt machine-read THIRTY-FIFTH)', 1),
    ('"b_exit_seed_base": 399_604,   # law sec.4 W174 B: 399_604..399_803 (FIRST-CLEAN past the own-wave A window; arithmetic 397_604..397_803 lands inside own-A, same-freeze mutual exclusion W141 precedent; reserved walk hops=1; B base == own-A tail+1)', '"b_exit_seed_base": 401_804,   # law sec.4 W175 B: 401_804..402_003 (FIRST-CLEAN past the own-wave A window; arithmetic 399_804..400_003 lands inside own-A, same-freeze mutual exclusion W141 precedent; reserved walk hops=1; B base == own-A tail+1)', 1),
    ('"shard_subdir": "n1_w174", "out_name": "n1_w174_results.json",', '"shard_subdir": "n1_w175", "out_name": "n1_w175_results.json",', 1),
]

MAT_PAIRS = [
    ('# --- W174 materializer face (r826 bm-a freeze, own-series law', '# --- W175 materializer face (r830 bm-a freeze, own-series law', 1),
    ('#     ninetieth owned per machine-derive (engine_owner==bm-a', '#     ninety-first owned per machine-derive (engine_owner==bm-a', 1),
    ('#     rows 89 + candidate); wave 173 = first free number after', '#     rows 90 + candidate); wave 174 = first free number after', 1),
    ('#     the REGISTERED W173 row (bm-a r822 freeze 04e95748a) --', '#     the REGISTERED W174 row (bm-a r826 freeze db42a0d46) --', 1),
    ('#     SINGLE STATE zero seat gap (W2..W173 all registered). Seat', '#     SINGLE STATE zero seat gap (W2..W174 all registered). Seat', 1),
    ('#     published=reserved MSG-2026-10-07-1247-bma-w174-seat pushed', '#     published=reserved MSG-2026-10-07-1434-bma-w175-seat pushed', 1),
    ('#     to origin 9b0e1cb29 BEFORE this freeze, r565 law (payload', '#     to origin 25c414e95 BEFORE this freeze, r565 law (payload', 1),
    ('#     the W173 finalize product already on origin since r823, not', '#     the W174 finalize product already on origin since r827, not', 1),
    ('#     at fetch (r823 pre-seat push), zero merge, zero', '#     at fetch (r828 pre-seat push), zero merge, zero', 1),
    ('#     --no-verify; self-ack inbox->processed archive ALREADY LANDED\r\n    #     pre-freeze -- r823 same-window self-ack move (the W174 seat\r\n    #     MSG sits in fleet/inbox/processed/ at freeze time, honest\r\n    #     archived).', '#     --no-verify; self-ack inbox->processed archive ALREADY LANDED\r\n    #     pre-freeze -- r828 same-window self-ack move (the W175 seat\r\n    #     MSG sits in fleet/inbox/processed/ at freeze time, honest\r\n    #     archived).', 1),
    ('#     ONE HUNDRED-AND-SIXTY-FOURTH engine wave BY', '#     ONE HUNDRED-AND-SIXTY-FIFTH engine wave BY', 1),
    ('#     MACHINE-DERIVE (engine_owner rows 163 + candidate; gate', '#     MACHINE-DERIVE (engine_owner rows 164 + candidate; gate', 1),
    ('#     W1..W173 finalize ALL LANDED (net chain head 786,012,', '#     W1..W174 finalize ALL LANDED (net chain head 788,212,', 1),
    ('#     K=378,520 merged pool; W173 finalize one-pass bm-a r823)', '#     K=380,720 merged pool; W174 finalize one-pass bm-a r827)', 1),
    ('#     always on. ADMIT receipt results/_r823bma_w174_probe_receipt.json;', '#     always on. ADMIT receipt results/_r828bma_w175_probe_receipt.json;', 1),
    ('#     banned gate ADMIT 0; not a re-pick (R250: W174 bands were', '#     banned gate ADMIT 0; not a re-pick (R250: W175 bands were', 1),
    ('    _set_wave(174)', '    _set_wave(175)', 1),
    ('assert WAVE_CONFIGS[173]["a_seed_base"] == pf.N1_BANDS[173]["a"][0], \\', 'assert WAVE_CONFIGS[174]["a_seed_base"] == pf.N1_BANDS[174]["a"][0], \\', 1),
    ('"W174 A band drift vs law mirror"', '"W175 A band drift vs law mirror"', 1),
    ('assert WAVE_CONFIGS[173]["b_exit_seed_base"] == \\', 'assert WAVE_CONFIGS[174]["b_exit_seed_base"] == \\', 1),
    ('pf.N1_BANDS[173]["b_exit"][0], "W174 B band drift vs law mirror"', 'pf.N1_BANDS[174]["b_exit"][0], "W175 B band drift vs law mirror"', 1),
    ('assert WAVE_CONFIGS[173].get("engine_owner") == \\', 'assert WAVE_CONFIGS[174].get("engine_owner") == \\', 1),
    ('pf.N1_BANDS[173].get("engine_owner") == "bm-a", \\', 'pf.N1_BANDS[174].get("engine_owner") == "bm-a", \\', 1),
    ('"W174 engine_owner drift (law mirror parity)"', '"W175 engine_owner drift (law mirror parity)"', 1),
    ('w173_a = {A_SEED_BASE + j for j in range(A_N)}', 'w174_a = {A_SEED_BASE + j for j in range(A_N)}', 1),
    ('w173_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}', 'w174_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}', 1),
    ('assert not (w173_a & w173_b), "W174 A/B band overlap"', 'assert not (w174_a & w174_b), "W175 A/B band overlap"', 1),
    ('assert not (w173_a & reg_ints) and not (w173_b & reg_ints), \\', 'assert not (w174_a & reg_ints) and not (w174_b & reg_ints), \\', 1),
    ('"W174 hits SEED_REGISTRY"', '"W175 hits SEED_REGISTRY"', 1),
    ('for nm, band in (("A", w173_a), ("B", w173_b)):', 'for nm, band in (("A", w174_a), ("B", w174_b)):', 1),
    ('f"W174 {nm} hits v1"', 'f"W175 {nm} hits v1"', 1),
    ('f"W174 {nm} hits W1"', 'f"W175 {nm} hits W1"', 1),
    ('f"W174 {nm} hits probe seeds"', 'f"W175 {nm} hits probe seeds"', 1),
    ('"registered W173 row parity drift (r307; bm-a r822)"', '"registered W173 row parity drift (r307; bm-a r822)"\r\n        assert pf.N1_BANDS[174] == {"a": (397_604, 399_603),\r\n                                    "b_exit": (399_604, 399_803),\r\n                                    "engine_owner": "bm-a"}, \\\r\n            "registered W174 row parity drift (r307; bm-a r826)"', 1),
    ('# prior-wave disjointness W2..W173 (single state: all', '# prior-wave disjointness W2..W174 (single state: all', 1),
    ('for wprev in sorted(w for w in WAVE_CONFIGS if w < 174):', 'for wprev in sorted(w for w in WAVE_CONFIGS if w < 175):', 2),
    ('assert not (w173_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j', 'assert not (w174_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j', 1),
    ('for j in range(A_N)}), f"W174 A hits W{wprev}"', 'for j in range(A_N)}), f"W175 A hits W{wprev}"', 1),
    ('assert not (w173_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j', 'assert not (w174_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j', 1),
    ('for j in range(B_N)}), f"W174 B hits W{wprev}"', 'for j in range(B_N)}), f"W175 B hits W{wprev}"', 1),
    ('n3r1_used173 = set(range(70_000, 70_006))', 'n3r1_used174 = set(range(70_000, 70_006))', 1),
    ('assert not (w173_a & n3r1_used173) and not (w173_b & n3r1_used173), \\', 'assert not (w174_a & n3r1_used174) and not (w174_b & n3r1_used174), \\', 1),
    ('"W174 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"', '"W175 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"', 1),
    ('assert not (w173_a & lfc_actual12) and not (w173_b & lfc_actual12), \\', 'assert not (w174_a & lfc_actual12) and not (w174_b & lfc_actual12), \\', 1),
    ('"W174 bands must clear the lfc actual draw range"', '"W175 bands must clear the lfc actual draw range"', 1),
    ('assert not (w173_a & options_actual12) and \\', 'assert not (w174_a & options_actual12) and \\', 1),
    ('not (w173_b & options_actual12), \\', 'not (w174_b & options_actual12), \\', 1),
    ('"W174 bands must clear the options_wave2 actual draw range"', '"W175 bands must clear the options_wave2 actual draw range"', 1),
    ('# band facts (law sec.4 W174 row, r795): A = FIRST-CLEAN past', '# band facts (law sec.4 W175 row, r795): A = FIRST-CLEAN past', 1),
    ('# the registered W173 B band (the arithmetic continuation', '# the registered W174 B band (the arithmetic continuation', 1),
    ('# 397_404..399_403 is REFUSED at its own start by the W173', '# 399_604..401_603 is REFUSED at its own start by the W174', 1),
    ('# B band 397_404..397_603, exactly as the W173 seat W174+ projection +', '# B band 399_604..399_803, exactly as the W174 seat W175+ projection +', 1),
    ('# r820 probe leg4 + r823 sec8 succession projection notes', '# r823 probe leg4 + r826 sec8 succession projection notes', 1),
    ('# 397_604..399_603; A base == prior-wave B tail+1 (397_603+1)', '# 399_804..401_803; A base == prior-wave B tail+1 (399_803+1)', 1),
    ('# machine-checkable -- A-hops-prior-B staircase THIRTY-FOURTH', '# machine-checkable -- A-hops-prior-B staircase THIRTY-FIFTH', 1),
    ('# continuation 397_604..397_803 is CLEAN on the registered', '# continuation 399_804..400_003 is CLEAN on the registered', 1),
    ('# universe but lands INSIDE the W174 A band window --', '# universe but lands INSIDE the W175 A band window --', 1),
    ('# 399_604 and lands 399_604..399_803, hops=1, non-rotational', '# 401_804 and lands 401_804..402_003, hops=1, non-rotational', 1),
    ('# (399_603+1) machine-checkable; cross-window convergence', '# (401_803+1) machine-checkable; cross-window convergence', 1),
    ('# with the W173 seat W174+ projection + r820 probe leg4 + r823 sec8', '# with the W174 seat W175+ projection + r823 probe leg4 + r826 sec8', 1),
    ('# honored (post-W173 universe re-derive + own-wave A', '# honored (post-W174 universe re-derive + own-wave A', 1),
    ('# reservation when deriving B); seat MSG-1247 tail,', '# reservation when deriving B); seat MSG-1434 tail,', 1),
    ('assert WAVE_CONFIGS[174]["a_seed_base"] == 397_604 == 397_603 + 1, (', 'assert WAVE_CONFIGS[175]["a_seed_base"] == 399_804 == 399_803 + 1, (', 1),
    ('"W174 A must be the first-clean window past the registered "', '"W175 A must be the first-clean window past the registered "', 1),
    ('"W173 B band tail 397_603+1 (arithmetic continuation "', '"W174 B band tail 399_803+1 (arithmetic continuation "', 1),
    ('"397_404..399_403 REFUSED at its own start by the W173 B "', '"399_604..401_603 REFUSED at its own start by the W174 B "', 1),
    ('"band 397_404..397_603, exactly as the W173 seat W174+ projection + "', '"band 399_604..399_803, exactly as the W174 seat W175+ projection + "', 1),
    ('"r820 probe leg4 + r823 sec8 succession projection notes "', '"r823 probe leg4 + r826 sec8 succession projection notes "', 1),
    ('"staircase THIRTY-FOURTH instance, E36 card)"', '"staircase THIRTY-FIFTH instance, E36 card)"', 1),
    ('arith_a173 = set(range(397_604, 399_604))', 'arith_a174 = set(range(399_804, 401_804))', 1),
    ('assert not (arith_a173 & reg_ints), \\', 'assert not (arith_a174 & reg_ints), \\', 1),
    ('"W174 A window must be CLEAN (first-clean ADMIT face past prior-wave B)"', '"W175 A window must be CLEAN (first-clean ADMIT face past prior-wave B)"', 1),
    ('assert WAVE_CONFIGS[174]["b_exit_seed_base"] == 399_604 == 399_603 + 1, (', 'assert WAVE_CONFIGS[175]["b_exit_seed_base"] == 401_804 == 401_803 + 1, (', 1),
    ('"W174 B must be the first-clean window past the own-wave A "', '"W175 B must be the first-clean window past the own-wave A "', 1),
    ('"band tail 399_603+1 (arithmetic continuation "', '"band tail 401_803+1 (arithmetic continuation "', 1),
    ('"397_604..397_803 CLEAN on the registered universe but "', '"399_804..400_003 CLEAN on the registered universe but "', 1),
    ('"lands INSIDE the W174 A band window; same-freeze mutual "', '"lands INSIDE the W175 A band window; same-freeze mutual "', 1),
    ('"own-wave A window reserved jumps to 399_604, first-clean "', '"own-wave A window reserved jumps to 401_804, first-clean "', 1),
    ('arith_b173 = set(range(399_604, 399_804))', 'arith_b174 = set(range(401_804, 402_004))', 1),
    ('assert not (arith_b173 & reg_ints), \\', 'assert not (arith_b174 & reg_ints), \\', 1),
    ('"W174 B window must be CLEAN (first-clean ADMIT face past own-wave A)"', '"W175 B window must be CLEAN (first-clean ADMIT face past own-wave A)"', 1),
    ('assert not (arith_b173 & arith_a173), \\', 'assert not (arith_b174 & arith_a174), \\', 1),
    ('"W174 A/B same-freeze mutual exclusion (B hops past own A)"', '"W175 A/B same-freeze mutual exclusion (B hops past own A)"', 1),
    ('assert _entry_shard_of(0, 12) == ("PERPETUAL-N1-W174-SHARD-0",', 'assert _entry_shard_of(0, 12) == ("PERPETUAL-N1-W175-SHARD-0",', 1),
    ('"n1w174-0of12"), "W174 entry identity"', '"n1w175-0of12"), "W175 entry identity"', 1),
    ('assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W174-SHARD-11",', 'assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W175-SHARD-11",', 1),
    ('"n1w174-11of12")', '"n1w175-11of12")', 1),
    ('assert SHARD_DIR.endswith("n1_w174") and OUT.endswith(', 'assert SHARD_DIR.endswith("n1_w175") and OUT.endswith(', 1),
    ('"n1_w174_results.json"), "W174 path drift"', '"n1_w175_results.json"), "W175 path drift"', 1),
    ('f"W174 shard dir collides with W{wprev}"', 'f"W175 shard dir collides with W{wprev}"', 1),
    ('# W174 finalize cumulative deps: W17..W173 outputs ALL PRESENT', '# W175 finalize cumulative deps: W17..W174 outputs ALL PRESENT', 1),
    ('# (landed net chain head 786,012 = W173 bm-a r823 one-pass --', '# (landed net chain head 788,212 = W174 bm-a r827 one-pass --', 1),
    ('for _depw in range(17, 174):', 'for _depw in range(17, 175):', 1),
    ('f"W174 finalize cumulative dep (W{_depw} output) missing"', 'f"W175 finalize cumulative dep (W{_depw} output) missing"', 1),
    ('# registered wave below 174 composes; wave 15 excluded by', '# registered wave below 175 composes; wave 15 excluded by', 1),
    ('# design; SINGLE STATE (W2..W173 all registered -- no', '# design; SINGLE STATE (W2..W174 all registered -- no', 1),
    ('assert sorted(w for w in WAVE_CONFIGS if w < 174) == \\', 'assert sorted(w for w in WAVE_CONFIGS if w < 175) == \\', 1),
    ('[w for w in range(16, 174)], \\', '[w for w in range(16, 175)], \\', 1),
    ('"W174 prior-wave set must derive from registry keys (no 15; "', '"W175 prior-wave set must derive from registry keys (no 15; "', 1),
    ('"W2..W173 registered single state)"', '"W2..W174 registered single state)"', 1),
    ('PATHS.root, "research", "PERPETUAL_N1_W174_PREREG.md")), \\', 'PATHS.root, "research", "PERPETUAL_N1_W175_PREREG.md")), \\', 1),
    ('"W174 per-wave prereg missing (materializer requirement)"', '"W175 per-wave prereg missing (materializer requirement)"', 1),
]

CL_PAIRS = [
    ('"+ W174 materializer face [same guard set, dep=W17..W173 ', '"+ W175 materializer face [same guard set, dep=W17..W174 ', 1),
    ('"outputs ALL PRESENT (landed net chain head 786,012 = "', '"outputs ALL PRESENT (landed net chain head 788,212 = "', 1),
    ('"W173 bm-a r823 one-pass, K=378,520 merged pool; ZERO "', '"W174 bm-a r827 one-pass, K=380,720 merged pool; ZERO "', 1),
    ('"in-flight upstream seats), ONE HUNDRED-AND-SIXTY-FOURTH "', '"in-flight upstream seats), ONE HUNDRED-AND-SIXTY-FIFTH "', 1),
    ('"ENGINE-OWNED WAVE BY MACHINE-DERIVE (engine_owner rows 163 "', '"ENGINE-OWNED WAVE BY MACHINE-DERIVE (engine_owner rows 164 "', 1),
    ("+ candidate) bm-a's ninetieth owned claim per ", "+ candidate) bm-a's ninety-first owned claim per ", 1),
    ('"machine-derive (engine_owner==bm-a rows 89 + candidate), "', '"machine-derive (engine_owner==bm-a rows 90 + candidate), "', 1),
    ('"A=FIRST-CLEAN past the registered W173 B band (staircase "', '"A=FIRST-CLEAN past the registered W174 B band (staircase "', 1),
    ('"THIRTY-FOURTH instance, E36 card, hops=1) + B=FIRST-CLEAN past the "', '"THIRTY-FIFTH instance, E36 card, hops=1) + B=FIRST-CLEAN past the "', 1),
    ('"results/_r823bma_w174_probe_receipt.json, law sec.4 W174 row, "', '"results/_r828bma_w175_probe_receipt.json, law sec.4 W175 row, "', 1),
    ('"r826 bm-a] "', '"r830 bm-a] "', 1),
]

PF_NEG = ['9b0e1cb29', 'r820 probe', 'r823 sec8', 'r823 pre-seat', '_r823bma', 'MSG-2026-10-07-1247', 'r823 same-window', '397_404', '397_604', '397_803', '397_603+1', '399_603+1', 'W173', 'W174 (bm-a', 'INSIDE the W174', 'THIRTY-FOURTH', 'W174+ projection (', 'R250: W174', 'W174 bands were', '786,012', '378,520', 'the W174 seat MSG sits in', 'since r823,', 'r826 freeze']

EN_NEG = ['9b0e1cb29', '04e95748a', '786,012', '378,520', 'SIXTY-FOURTH', 'rows 163', 'r820 probe', '_r823bma', 'r823 pre-seat', 'r823 sec8', 'MSG-2026-10-07-1247', 'n1_w174', 'n1w174', 'PERPETUAL-N1-W174', 'PERPETUAL_N1_W174', 'W173 finalize', 'thirty-fourth', 'THIRTY-FOURTH', 'bm-a r822 freeze', 'wave 173: ', 'W174 A band', 'INSIDE the W174', 'W174+ projection', '397_404', '397_604', '399_604, first-clean', 'W1..W173', 'W173 B band', 'R250']

MAT_NEG = ['w173_', 'arith_a173', 'arith_b173', 'n3r1_used173', 'r820 probe', 'r823 sec8', 'r823 pre-seat', '9b0e1cb29', '04e95748a', 'SIXTY-FOURTH', 'ninetieth', 'rows 163', 'rows 89 ', 'range(17, 174)', 'range(16, 174)', 'W1..W173', 'wave 173 =', 'PERPETUAL_N1_W174', 'PERPETUAL-N1-W174', 'MSG-1247', '_r823bma', 'the W174 seat MSG sits in', 'r823 same-window', 'W174 materializer', 'INSIDE the W174', 'THIRTY-FOURTH', 'W174 bands', 'W174 A band', 'W174 A window', 'W174 B window', 'W174 A/B', 'W174 hits', 'W174 entry identity', 'W174 path drift', 'W174 shard dir', 'W174 finalize cumulative', 'W174 prior-wave', 'W174 per-wave', 'W174 engine_owner drift', 'W174 A band drift', 'W174 B band drift', 'the W173 seat', 'W173 B band', 'W173 finalize', 'bm-a r822 freeze', 'post-W173', 'seat MSG-1247', 'n1w174', 'n1_w174']

CL_NEG = ['W174 materializer', '786,012', '378,520', 'SIXTY-FOURTH', 'ninetieth', 'rows 163', 'rows 89 ', 'THIRTY-FOURTH', 'W173 B band', '_r823bma', 'W174 row,', 'r826 bm-a] ']

blk175 = vmap(pfblk, PF_PAIRS, PF_NEG, "pf")
entry175 = IND23 + vmap(entry, EN_PAIRS, EN_NEG, "entry")
mat175 = "    " + vmap(mat, MAT_PAIRS, MAT_NEG, "mat")
claim175 = IND10 + vmap(claim, CL_PAIRS, CL_NEG, "claim")

# ---- apply insertions (in-memory) ---------------------------------------
pfsrc = io.open(PF, encoding="utf-8", newline="").read()
n1src = io.open(N1, encoding="utf-8", newline="").read()

# pf: insert W175 block after the W174 row (last registered), before the
# dict close -- r560 insert-after-last-registered-row + post-anchor gate
seg = EO + NL + "}"
check(pfsrc.count(seg) == 1, "pf row-close segment not unique")
pfnew = pfsrc.replace(seg, EO + NL + blk175 + NL + "}", 1)

# n1 entry: after the W174 entry, before the WAVE_CONFIGS close
seg = EO + NL + IND23 + "}"
check(n1src.count(seg) == 1, "n1 entry-close segment not unique")
n1new = n1src.replace(seg, EO + NL + entry175 + NL + IND23 + "}", 1)

# n1 mat: insert the W175 block before the T-141 s2 lane face header
seg = "    # --- T-141 s2 lane face"
check(n1new.count(seg) == 1, "n1 T-141 mat anchor not unique")
n1new = n1new.replace(seg, mat175 + NL + seg, 1)

# n1 claim: insert the W175 attribution after the W174 claim tail line
# (r581 law: anchor = tail single-line literal + post-anchor guard)
seg = '"r826 bm-a] "' + NL + IND10 + '"+ T-141 s2 "'
check(n1new.count(seg) == 1, "n1 claim anchor not unique")
n1new = n1new.replace(seg, '"r826 bm-a] "' + NL + claim175 + NL + IND10 +
                      '"+ T-141 s2 "', 1)

# ---- gates (r780/r781/r560/r815 lineage) --------------------------------
ast.parse(pfnew)
ast.parse(n1new)
print("AST gate: both files parse OK")

# W175 presence + W174 anti-vanish (r560 law)
checks = [
    (pfnew, '175: {"a": (399_804, 401_803), "b_exit": (401_804, 402_003),', 1),
    (pfnew, '174: {"a": (397_604, 399_603), "b_exit": (399_604, 399_803),', 1),
    (pfnew, "# W175 (bm-a r830 freeze", 1),
    (pfnew, "# W174 (bm-a r826 freeze", 1),
    (n1new, '175: {"batch": "PERPETUAL-N1-W175",', 1),
    (n1new, '174: {"batch": "PERPETUAL-N1-W174",', 1),
    (n1new, "# --- W175 materializer face", 1),
    (n1new, "# --- W174 materializer face", 1),
    (n1new, '"r830 bm-a] "', 1),
    (n1new, '"r826 bm-a] "', 1),
    (n1new, '"a_seed_base": 399_804,', 1),
    (n1new, '"b_exit_seed_base": 401_804,', 1),
    (n1new, "n1_w175", 4),
    (n1new, "PERPETUAL_N1_W175_PREREG.md", 2),
]
for src, needle, cnt in checks:
    got = src.count(needle)
    check(got == cnt, "post-edit needle %r count %d != %d" % (needle[:50], got, cnt))

# W176 projection prose present in the new W175 blocks (probe leg4
# verbatim; r819 post-edit assert bloodline + r776 fragment-needle law)
check("# W175+ projection (gate-derived r828)" in pfnew,
      "pf W175+ projection head missing")
check('probe_receipt.json; W176+ projection "' in n1new,
      "n1 W176+ projection head fragment missing")
check("# 401_804..403_803 CLEAN hops=0 / B first-clean 402_004..402_203" in pfnew,
      "pf W176p prose missing")
check("W176 A window; W176 freezer MUST re-derive on the post-W175" in pfnew,
      "pf W176 freezer prose missing")
check('"W176 A window; W176 freezer MUST re-derive on the "' in n1new,
      "n1 W176 freezer fragment missing")
check('"W175 B band 401_804..402_003 will refuse the naive "' in n1new,
      "n1 W175-band refuse fragment missing")

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
check('175: {"a": (399_804' not in pf_o2, "write-time: origin pf carries W175")
check('175: {"batch"' not in n1_o2, "write-time: origin n1 carries W175")
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
