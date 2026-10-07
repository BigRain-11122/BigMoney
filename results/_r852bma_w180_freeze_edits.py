# -*- coding: utf-8 -*-
"""r852 bm-a W180 freeze edits: four insertions (pf N1_BANDS[180] row +
n1 WAVE_CONFIGS[180] entry + n1 W180 materializer block + n1 W180
PASS-claim attribution). DRY flag: --dry = zero-write simulation
(r781 verify-separation law + r811/r822/r826/r830/r834/r843/r845/r849
dry-run precedent: full stale+prose+AST asserts in memory BEFORE any
write).

Bloodline: r819/r822/r826/r830/r834/r843/r845/r849 freeze-edits machinery
(r773 pit law freeze-editor compliance + r776 fragment-needle law + r781
verify-separation law), W180 facts live-registry-driven (built by
_r852bma_w180_freeze_buildgen.py: old sides = the PHYSICAL W179 face
fragments probed to dumps this window, new sides = the S80f W180 fact
map, counts verified pre-emission):
  - pre-seat probe results/_r851bma_w180_probe_receipt.json rc0 ADMIT
    (A 410_804..412_803 staircase FORTIETH instance E36 hops=1
    past the registered W179 B band 410_604..410_803; naive
    410_604..412_603 refused at its own start by the W179 B band --
    receipt A_semantics machine-cites the W179 seat MSG leg4 + r848
    probe leg4 anticipated + MANDATED this re-derive (W179 sec5.5
    prose anticipated 40th -- projection and receipt ordinals MATCH,
    no divergence this wave); B 412_804..413_003 own-A mutual
    exclusion hops=1, naive 410_804..411_003);
  - face probe results/_r852bma_w180_face_probe_receipt.json rc0 (all
    four W179 faces dumped + needle counts; this TOK is built from the
    PHYSICAL probe-dumped shapes, r776 law);
  - seat MSG-2026-10-08-0030-bma-w180-seat published on origin at
    d3b0737fe (r851 pre-seat push, path-derived TRUE sha per r812
    precedent); r565 law: on origin BEFORE this freeze commit;
    self-ack archive ALREADY LANDED pre-freeze -- r851 same-window
    self-ack move (the W180 seat MSG sits in fleet/inbox/processed/ at
    freeze time, honest archived; e069782f7);
  - per-wave prereg research/PERPETUAL_N1_W180_PREREG.md frozen at
    origin (r852 prereg-freeze push; banned gate ADMIT 0 re-verified
    at prereg freeze);
  - W179 freeze registered sha machine-derived = ef540bf8f (git log
    origin/main --grep "W179 FREEZE"); W179 finalize landed r850
    one-pass adoption closeout: ledger head 799,705, merged pool
    K=391,720 (n1_w179_results.json machine-read; sec7/sec8 backfill
    landed the r850 same window -- same-window, honest);
  - lineage constants disclosed (r795/r845/r849 precedent, passed
    through): (a) the "wave N-1 = first free number" mat-header label
    rides the vmap verbatim (off-by-one lineage quirk since W165
    r795); (b) "law sec.4 W180 row, r795" band-facts template stamp
    keeps its r795; (c) "single-window derive (r812 merged the gate
    legs INTO the pre-seat probe...)" stays (historical merge
    citation); (d) the bm-a-owned ordinal word rolls ninety-fifth ->
    ninety-sixth (rows 95 + candidate = 96th owned per probe leg0);
    (e) mat parity-chain rows W138..W178 keep their historical stamps
    and tuples; the W179 row (the current registered tail) is
    APPENDED with its frozen values (408_604, 410_603)/(410_604,
    410_803); (f) the "W179 finalize landed same-window r827"
    citation rides the vmap verbatim (off-by-one wave-word +
    stale-session lineage quirk inherited; head/K values roll
    machine-correct to 799,705/391,720 this window).

r773 pit law compliance:
  (1) full string-face inventory empirically probed BEFORE TOK
      (_r852bma_w180_face_probe.py -- four face dumps + needle-count
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
      (r530/r687: fetch + origin carries no W180 registration before
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
probe = json.load(open(r"results\_r851bma_w180_probe_receipt.json",
                       encoding="utf-8"))
check(probe["verdict"] == "ADMIT", "pre-seat probe not ADMIT")
check(probe["bands"] == {"A": "410804_412803", "B": "412804_413003"},
      "probe band shape mismatch")
check(probe["legs"]["leg1"]["A"] == [410804, 412803], "A band mismatch")
check(probe["legs"]["leg1"]["B"] == [412804, 413003], "B band mismatch")
check(probe["legs"]["leg1"]["hops_A"] == 1 and probe["legs"]["leg1"]["hops_B"] == 1,
      "hops mismatch")
check(probe["legs"]["leg0"]["rows"] == 177 and probe["legs"]["leg0"]["tail"] == "W179",
      "leg0 registry tail mismatch")
check(probe["legs"]["leg0"]["ordinal"] == 170 and probe["legs"]["leg0"]["bma_ordinal"] == 96,
      "leg0 ordinal mismatch")
check(probe["legs"]["leg2"]["conflicts"] == 0, "leg2 conflicts nonzero")
check(probe["legs"]["leg3"]["origin_vacancy"] is True, "leg3 origin not vacant")
check(probe["legs"]["leg4"]["W181p_A"] == "412804..414803"
      and probe["legs"]["leg4"]["W181p_B"] == "413004..413203",
      "leg4 W181+ projection mismatch")

# origin anti-collision pre-check (r511 tail-lock / r687 write-time gate)
subprocess.run(["git", "fetch", "origin"], capture_output=True)
pf_o = subprocess.run(["git", "show", "origin/main:" + PF],
                      capture_output=True).stdout.decode("utf-8", "replace")
n1_o = subprocess.run(["git", "show", "origin/main:" + N1],
                      capture_output=True).stdout.decode("utf-8", "replace")
check('180: {"a": (410_804' not in pf_o, "origin pf already carries W180 row")
check("W180 (bm-a r852 freeze" not in pf_o, "origin pf carries W180 block")
check('180: {"batch"' not in n1_o, "origin n1 already carries W180 entry")
check("# --- W180 materializer face" not in n1_o, "origin n1 carries W180 mat")
check('"r852 bm-a] "' not in n1_o, "origin n1 carries W180 claim")

# machine-derived shas (r587 / r812 path-derived precedent)
seat_sha = subprocess.run(
    ["git", "log", "origin/main", "--format=%h", "-n", "1", "--diff-filter=A",
     "--", "fleet/inbox/MSG-2026-10-08-0030-bma-w180-seat.md"],
    capture_output=True).stdout.decode().strip()
check(seat_sha == "d3b0737fe", "seat sha path-derived mismatch: " + seat_sha)
check(os.path.exists(os.path.join(
    "fleet", "inbox", "processed", "MSG-2026-10-08-0030-bma-w180-seat.md")),
    "seat MSG not in processed/ at freeze time (self-ack archive)")
w179_freeze_sha = subprocess.run(
    ["git", "log", "origin/main", "--format=%h", "-n", "1", "--grep=W179 FREEZE"],
    capture_output=True).stdout.decode().strip()
check(w179_freeze_sha == "ef540bf8f", "W179 freeze sha mismatch: " + w179_freeze_sha)

# ---- live-registry parity pre-check (edit-gate: never edit a drifted file)
sys.path.insert(0, "scripts")
import perpetual_faces as pfmod  # noqa: E402
check(len(pfmod.N1_BANDS) == 177, "live N1_BANDS row count drift: %d" % len(pfmod.N1_BANDS))
check(pfmod.N1_BANDS[179] == {"a": (408_604, 410_603),
                              "b_exit": (410_604, 410_803),
                              "engine_owner": "bm-a"}, "live W179 row drift")
check(180 not in pfmod.N1_BANDS, "live N1_BANDS already has 180")
check(os.path.exists(os.path.join("research", "PERPETUAL_N1_W180_PREREG.md")),
      "W180 per-wave prereg missing (materializer gate)")
prereg_o = subprocess.run(["git", "show", "origin/main:research/PERPETUAL_N1_W180_PREREG.md"],
                          capture_output=True)
check(prereg_o.returncode == 0, "W180 prereg absent on origin")

# ---- physical face dumps (r776 law) -----------------------------------
pfblk = io.open(r"results\_r852bma_w180_probe_pf_block.txt", encoding="utf-8",
                newline="").read()
entry = io.open(r"results\_r852bma_w180_probe_n1_entry.txt", encoding="utf-8",
                newline="").read()
mat = io.open(r"results\_r852bma_w180_probe_n1_mat.txt", encoding="utf-8",
              newline="").read()
claim = io.open(r"results\_r852bma_w180_probe_n1_claim.txt", encoding="utf-8",
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
    ('    # W179 (bm-a r849 freeze, seat MSG-2026-10-07-2320-bma-w179-seat', '    # W180 (bm-a r852 freeze, seat MSG-2026-10-08-0030-bma-w180-seat', 1),
    ('pushed to origin 4c645c95f pre-freeze r565 law (r848 pre-seat', 'pushed to origin d3b0737fe pre-freeze r565 law (r851 pre-seat', 1),
    ('(3-item; the W178 finalize product already on origin since r846,', '(3-item; the W179 finalize product already on origin since r850,', 1),
    ('# = direct fast-forward behind-0 at fetch (r848 pre-seat', '# = direct fast-forward behind-0 at fetch (r851 pre-seat', 1),
    ('# push), zero merge, zero --no-verify; self-ack archive ALREADY\r\n    # LANDED pre-freeze -- r848 same-window self-ack move (the W179\r\n    # seat MSG sits in fleet/inbox/processed/ at freeze time, honest\r\n    # archived);', '# push), zero merge, zero --no-verify; self-ack archive ALREADY\r\n    # LANDED pre-freeze -- r851 same-window self-ack move (the W180\r\n    # seat MSG sits in fleet/inbox/processed/ at freeze time, honest\r\n    # archived);', 1),
    ('band gate ADMIT results/_r848bma_w179_probe_receipt.json: A = FIRST-CLEAN', 'band gate ADMIT results/_r851bma_w180_probe_receipt.json: A = FIRST-CLEAN', 1),
    ('past the registered W178 B band (arithmetic continuation', 'past the registered W179 B band (arithmetic continuation', 1),
    ('408_404..410_403 REFUSED at its own start by the W178 B band', '410_604..412_603 REFUSED at its own start by the W179 B band', 1),
    ('408_404..408_603, exactly as the W178 seat W179+ projection + r844 probe', '410_604..410_803, exactly as the W179 seat W180+ projection + r848 probe', 1),
    ('# leg4 + r846 sec8 succession projection notes all anticipated;', '# leg4 + r850 sec8 succession projection notes all anticipated;', 1),
    ('honest forward walk hops=1 -> 408_604..410_603, non-rotational', 'honest forward walk hops=1 -> 410_804..412_803, non-rotational', 1),
    ('(408_603+1) machine-checkable -- A-hops-prior-B staircase', '(410_803+1) machine-checkable -- A-hops-prior-B staircase', 1),
    ('THIRTY-NINTH instance, E36 card);', 'FORTIETH instance, E36 card);', 1),
    ('continuation 408_604..408_803 CLEAN on the registered universe', 'continuation 410_804..411_003 CLEAN on the registered universe', 1),
    ('but lands INSIDE the W179 A band window -- same-freeze mutual', 'but lands INSIDE the W180 A band window -- same-freeze mutual', 1),
    ('own-wave A window reserved jumps to 410_604 -> 410_604..410_803,', 'own-wave A window reserved jumps to 412_804 -> 412_804..413_003,', 1),
    ('own-wave A tail+1 (410_603+1) machine-checkable);', 'own-wave A tail+1 (412_803+1) machine-checkable);', 1),
    ('W179+ projection (gate-derived r848): A first-clean', 'W180+ projection (gate-derived r851): A first-clean', 1),
    ('410_604..412_603 CLEAN hops=0 / B first-clean 410_804..411_003', '412_804..414_803 CLEAN hops=0 / B first-clean 413_004..413_203', 1),
    ('registered W179 B band 410_604..410_803 will refuse the naive', 'registered W180 B band 412_804..413_003 will refuse the naive', 1),
    ('W180 A window; W180 freezer MUST re-derive on the post-W179', 'W181 A window; W181 freezer MUST re-derive on the post-W180', 1),
    ('NOT a re-pick (R250: W179 bands were never assigned).', 'NOT a re-pick (R250: W180 bands were never assigned).', 1),
    ('179: {"a": (408_604, 410_603), "b_exit": (410_604, 410_803),', '180: {"a": (410_804, 412_803), "b_exit": (412_804, 413_003),', 1),
]

EN_PAIRS = [
    ('179: {"batch": "PERPETUAL-N1-W179",', '180: {"batch": "PERPETUAL-N1-W180",', 1),
    ('"prereg": ("research/PERPETUAL_N1_W179_PREREG.md (wave-level frozen "', '"prereg": ("research/PERPETUAL_N1_W180_PREREG.md (wave-level frozen "', 1),
    ('new seed bands only; ONE HUNDRED-AND-SIXTY-NINTH ENGINE-OWNED WAVE ', 'new seed bands only; ONE HUNDRED-AND-SEVENTIETH ENGINE-OWNED WAVE ', 1),
    ('BY MACHINE-DERIVE (engine_owner rows 168 + candidate), ', 'BY MACHINE-DERIVE (engine_owner rows 169 + candidate), ', 1),
    ('number law after the REGISTERED W178 row bm-a r845 freeze ', 'number law after the REGISTERED W179 row bm-a r849 freeze ', 1),
    ('de4716da2, SINGLE STATE zero seat gap W2..W178 all ', 'ef540bf8f, SINGLE STATE zero seat gap W2..W179 all ', 1),
    ('registered; W179 finalize landed same-window r827, ledger ', 'registered; W180 finalize landed same-window r827, ledger ', 1),
    ('head 797,505, merged pool K=389,520; seat published=reserved ', 'head 799,705, merged pool K=391,720; seat published=reserved ', 1),
    ('MSG-2026-10-07-2320-bma-w179-seat PUSHED to origin 4c645c95f ', 'MSG-2026-10-08-0030-bma-w180-seat PUSHED to origin d3b0737fe ', 1),
    ('probe receipt (3-item; the W178 finalize product already on origin since r846, not re-shipped; W146 precedent); ', 'probe receipt (3-item; the W179 finalize product already on origin since r850, not re-shipped; W146 precedent); ', 1),
    ('at fetch (r848 pre-seat push), zero merge, zero ', 'at fetch (r851 pre-seat push), zero merge, zero ', 1),
    ('engine_owner=bm-a, wave 178: ', 'engine_owner=bm-a, wave 179: ', 1),
    ('A = FIRST-CLEAN past the registered W178 B band (the ', 'A = FIRST-CLEAN past the registered W179 B band (the ', 1),
    ('arithmetic continuation 408_404..410_403 is REFUSED at its ', 'arithmetic continuation 410_604..412_603 is REFUSED at its ', 1),
    ('own start by the W178 B band 408_404..408_603, exactly as ', 'own start by the W179 B band 410_604..410_803, exactly as ', 1),
    ('the W178 seat W179+ projection + r844 probe leg4 + r846 sec8 succession ', 'the W179 seat W180+ projection + r848 probe leg4 + r850 sec8 succession ', 1),
    ('projection notes anticipated; honest forward walk hops=1 -> ', 'projection notes anticipated; honest forward walk hops=1 -> ', 1),
    ('408_604..410_603; A base == prior-wave B tail+1 ', '410_804..412_803; A base == prior-wave B tail+1 ', 1),
    ('machine-checkable = A-hops-prior-B staircase THIRTY-NINTH ', 'machine-checkable = A-hops-prior-B staircase FORTIETH ', 1),
    ('arithmetic continuation 408_604..408_803 is CLEAN on the ', 'arithmetic continuation 410_804..411_003 is CLEAN on the ', 1),
    ('registered universe but lands INSIDE the W179 A band ', 'registered universe but lands INSIDE the W180 A band ', 1),
    ('jumps to 410_604, first-clean 410_604..410_803 hops=1, ', 'jumps to 412_804, first-clean 412_804..413_003 hops=1, ', 1),
    ('convergence with the W178 seat W179+ projection + r844 probe leg4 + ', 'convergence with the W179 seat W180+ projection + r848 probe leg4 + ', 1),
    ('r846 sec8 succession projection notes re-derived -- all ', 'r850 sec8 succession projection notes re-derived -- all ', 1),
    ('MANDATORY notes honored (post-W178 universe re-derive + ', 'MANDATORY notes honored (post-W179 universe re-derive + ', 1),
    ('results/_r848bma_w179_probe_receipt.json; W180+ projection ', 'results/_r851bma_w180_probe_receipt.json; W181+ projection ', 1),
    ('per this window gate: A first-clean 410_604..412_603 ', 'per this window gate: A first-clean 412_804..414_803 ', 1),
    ('CLEAN / B first-clean 410_804..411_003 CLEAN -- naive ', 'CLEAN / B first-clean 413_004..413_203 CLEAN -- naive ', 1),
    ('W179 B band 410_604..410_803 will refuse the naive ', 'W180 B band 412_804..413_003 will refuse the naive ', 1),
    ('W180 A window; W180 freezer MUST re-derive on the ', 'W181 A window; W181 freezer MUST re-derive on the ', 1),
    ('post-W179 universe AND reserve the own-wave A window ', 'post-W180 universe AND reserve the own-wave A window ', 1),
    ('staircase card); W1..W178 finalize ALL LANDED (W178 ', 'staircase card); W1..W179 finalize ALL LANDED (W179 ', 1),
    ('finalize one-pass bm-a r846, net chain head 797,505, ', 'finalize one-pass bm-a r850, net chain head 799,705, ', 1),
    ('merged pool K=389,520) -- ZERO in-flight upstream ', 'merged pool K=391,720) -- ZERO in-flight upstream ', 1),
    ('"a_seed_base": 408_604,        # law sec.4 W179 A: 408_604..410_603 (FIRST-CLEAN past the registered W178 B band; arithmetic 408_404..410_403 REFUSED at own start by the W178 B band; hops=1; A-hops-prior-B staircase THIRTY-NINTH instance, E36 card; ordinal convergence per r587: W178 sec5.5 prose anticipated thirty-ninth, r848 receipt machine-read THIRTY-NINTH)', '"a_seed_base": 410_804,        # law sec.4 W180 A: 410_804..412_803 (FIRST-CLEAN past the registered W179 B band; arithmetic 410_604..412_603 REFUSED at own start by the W179 B band; hops=1; A-hops-prior-B staircase FORTIETH instance, E36 card; ordinal convergence per r587: W179 sec5.5 prose anticipated fortieth, r851 receipt machine-read FORTIETH)', 1),
    ('"b_exit_seed_base": 410_604,   # law sec.4 W179 B: 410_604..410_803 (FIRST-CLEAN past the own-wave A window; arithmetic 408_604..408_803 lands inside own-A, same-freeze mutual exclusion W141 precedent; reserved walk hops=1; B base == own-A tail+1)', '"b_exit_seed_base": 412_804,   # law sec.4 W180 B: 412_804..413_003 (FIRST-CLEAN past the own-wave A window; arithmetic 410_804..411_003 lands inside own-A, same-freeze mutual exclusion W141 precedent; reserved walk hops=1; B base == own-A tail+1)', 1),
    ('"shard_subdir": "n1_w179", "out_name": "n1_w179_results.json",', '"shard_subdir": "n1_w180", "out_name": "n1_w180_results.json",', 1),
]

MAT_PAIRS = [
    ('# --- W179 materializer face (r849 bm-a freeze, own-series law', '# --- W180 materializer face (r852 bm-a freeze, own-series law', 1),
    ('#     ninety-fifth owned per machine-derive (engine_owner==bm-a', '#     ninety-sixth owned per machine-derive (engine_owner==bm-a', 1),
    ('#     rows 94 + candidate); wave 178 = first free number after', '#     rows 95 + candidate); wave 179 = first free number after', 1),
    ('#     the REGISTERED W178 row (bm-a r845 freeze de4716da2) --', '#     the REGISTERED W179 row (bm-a r849 freeze ef540bf8f) --', 1),
    ('#     SINGLE STATE zero seat gap (W2..W178 all registered). Seat', '#     SINGLE STATE zero seat gap (W2..W179 all registered). Seat', 1),
    ('#     published=reserved MSG-2026-10-07-2320-bma-w179-seat pushed', '#     published=reserved MSG-2026-10-08-0030-bma-w180-seat pushed', 1),
    ('#     to origin 4c645c95f BEFORE this freeze, r565 law (payload', '#     to origin d3b0737fe BEFORE this freeze, r565 law (payload', 1),
    ('#     the W178 finalize product already on origin since r846, not', '#     the W179 finalize product already on origin since r850, not', 1),
    ('#     at fetch (r848 pre-seat push), zero merge, zero', '#     at fetch (r851 pre-seat push), zero merge, zero', 1),
    ('#     --no-verify; self-ack inbox->processed archive ALREADY LANDED\r\n    #     pre-freeze -- r848 same-window self-ack move (the W179 seat\r\n    #     MSG sits in fleet/inbox/processed/ at freeze time, honest\r\n    #     archived).', '#     --no-verify; self-ack inbox->processed archive ALREADY LANDED\r\n    #     pre-freeze -- r851 same-window self-ack move (the W180 seat\r\n    #     MSG sits in fleet/inbox/processed/ at freeze time, honest\r\n    #     archived).', 1),
    ('#     ONE HUNDRED-AND-SIXTY-NINTH engine wave BY', '#     ONE HUNDRED-AND-SEVENTIETH engine wave BY', 1),
    ('#     MACHINE-DERIVE (engine_owner rows 168 + candidate; gate', '#     MACHINE-DERIVE (engine_owner rows 169 + candidate; gate', 1),
    ('#     W1..W178 finalize ALL LANDED (net chain head 797,505,', '#     W1..W179 finalize ALL LANDED (net chain head 799,705,', 1),
    ('#     K=389,520 merged pool; W178 finalize one-pass bm-a r846)', '#     K=391,720 merged pool; W179 finalize one-pass bm-a r850)', 1),
    ('#     always on. ADMIT receipt results/_r848bma_w179_probe_receipt.json;', '#     always on. ADMIT receipt results/_r851bma_w180_probe_receipt.json;', 1),
    ('#     banned gate ADMIT 0; not a re-pick (R250: W179 bands were', '#     banned gate ADMIT 0; not a re-pick (R250: W180 bands were', 1),
    ('    _set_wave(179)', '    _set_wave(180)', 1),
    ('assert WAVE_CONFIGS[178]["a_seed_base"] == pf.N1_BANDS[178]["a"][0], \\', 'assert WAVE_CONFIGS[179]["a_seed_base"] == pf.N1_BANDS[179]["a"][0], \\', 1),
    ('"W179 A band drift vs law mirror"', '"W180 A band drift vs law mirror"', 1),
    ('assert WAVE_CONFIGS[178]["b_exit_seed_base"] == \\', 'assert WAVE_CONFIGS[179]["b_exit_seed_base"] == \\', 1),
    ('pf.N1_BANDS[178]["b_exit"][0], "W179 B band drift vs law mirror"', 'pf.N1_BANDS[179]["b_exit"][0], "W180 B band drift vs law mirror"', 1),
    ('assert WAVE_CONFIGS[178].get("engine_owner") == \\', 'assert WAVE_CONFIGS[179].get("engine_owner") == \\', 1),
    ('pf.N1_BANDS[178].get("engine_owner") == "bm-a", \\', 'pf.N1_BANDS[179].get("engine_owner") == "bm-a", \\', 1),
    ('"W179 engine_owner drift (law mirror parity)"', '"W180 engine_owner drift (law mirror parity)"', 1),
    ('w178_a = {A_SEED_BASE + j for j in range(A_N)}', 'w179_a = {A_SEED_BASE + j for j in range(A_N)}', 1),
    ('w178_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}', 'w179_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}', 1),
    ('assert not (w178_a & w178_b), "W179 A/B band overlap"', 'assert not (w179_a & w179_b), "W180 A/B band overlap"', 1),
    ('assert not (w178_a & reg_ints) and not (w178_b & reg_ints), \\', 'assert not (w179_a & reg_ints) and not (w179_b & reg_ints), \\', 1),
    ('"W179 hits SEED_REGISTRY"', '"W180 hits SEED_REGISTRY"', 1),
    ('for nm, band in (("A", w178_a), ("B", w178_b)):', 'for nm, band in (("A", w179_a), ("B", w179_b)):', 1),
    ('f"W179 {nm} hits v1"', 'f"W180 {nm} hits v1"', 1),
    ('f"W179 {nm} hits W1"', 'f"W180 {nm} hits W1"', 1),
    ('f"W179 {nm} hits probe seeds"', 'f"W180 {nm} hits probe seeds"', 1),
    ('"registered W178 row parity drift (r307; bm-a r845)"', '"registered W178 row parity drift (r307; bm-a r845)"\r\n        assert pf.N1_BANDS[179] == {"a": (408_604, 410_603),\r\n                                    "b_exit": (410_604, 410_803),\r\n                                    "engine_owner": "bm-a"}, \\\r\n            "registered W179 row parity drift (r307; bm-a r849)"', 1),
    ('# prior-wave disjointness W2..W178 (single state: all', '# prior-wave disjointness W2..W179 (single state: all', 1),
    ('for wprev in sorted(w for w in WAVE_CONFIGS if w < 179):', 'for wprev in sorted(w for w in WAVE_CONFIGS if w < 180):', 2),
    ('assert not (w178_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j', 'assert not (w179_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j', 1),
    ('for j in range(A_N)}), f"W179 A hits W{wprev}"', 'for j in range(A_N)}), f"W180 A hits W{wprev}"', 1),
    ('assert not (w178_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j', 'assert not (w179_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j', 1),
    ('for j in range(B_N)}), f"W179 B hits W{wprev}"', 'for j in range(B_N)}), f"W180 B hits W{wprev}"', 1),
    ('n3r1_used178 = set(range(70_000, 70_006))', 'n3r1_used179 = set(range(70_000, 70_006))', 1),
    ('assert not (w178_a & n3r1_used178) and not (w178_b & n3r1_used178), \\', 'assert not (w179_a & n3r1_used179) and not (w179_b & n3r1_used179), \\', 1),
    ('"W179 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"', '"W180 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"', 1),
    ('assert not (w178_a & lfc_actual12) and not (w178_b & lfc_actual12), \\', 'assert not (w179_a & lfc_actual12) and not (w179_b & lfc_actual12), \\', 1),
    ('"W179 bands must clear the lfc actual draw range"', '"W180 bands must clear the lfc actual draw range"', 1),
    ('assert not (w178_a & options_actual12) and \\', 'assert not (w179_a & options_actual12) and \\', 1),
    ('not (w178_b & options_actual12), \\', 'not (w179_b & options_actual12), \\', 1),
    ('"W179 bands must clear the options_wave2 actual draw range"', '"W180 bands must clear the options_wave2 actual draw range"', 1),
    ('# band facts (law sec.4 W179 row, r795): A = FIRST-CLEAN past', '# band facts (law sec.4 W180 row, r795): A = FIRST-CLEAN past', 1),
    ('# the registered W178 B band (the arithmetic continuation', '# the registered W179 B band (the arithmetic continuation', 1),
    ('# 408_404..410_403 is REFUSED at its own start by the W178', '# 410_604..412_603 is REFUSED at its own start by the W179', 1),
    ('# B band 408_404..408_603, exactly as the W178 seat W179+ projection +', '# B band 410_604..410_803, exactly as the W179 seat W180+ projection +', 1),
    ('# r844 probe leg4 + r846 sec8 succession projection notes', '# r848 probe leg4 + r850 sec8 succession projection notes', 1),
    ('# 408_604..410_603; A base == prior-wave B tail+1 (408_603+1)', '# 410_804..412_803; A base == prior-wave B tail+1 (410_803+1)', 1),
    ('# machine-checkable -- A-hops-prior-B staircase THIRTY-NINTH', '# machine-checkable -- A-hops-prior-B staircase FORTIETH', 1),
    ('# continuation 408_604..408_803 is CLEAN on the registered', '# continuation 410_804..411_003 is CLEAN on the registered', 1),
    ('# universe but lands INSIDE the W179 A band window --', '# universe but lands INSIDE the W180 A band window --', 1),
    ('# 410_604 and lands 410_604..410_803, hops=1, non-rotational', '# 412_804 and lands 412_804..413_003, hops=1, non-rotational', 1),
    ('# (410_603+1) machine-checkable; cross-window convergence', '# (412_803+1) machine-checkable; cross-window convergence', 1),
    ('# with the W178 seat W179+ projection + r844 probe leg4 + r846 sec8', '# with the W179 seat W180+ projection + r848 probe leg4 + r850 sec8', 1),
    ('# honored (post-W178 universe re-derive + own-wave A', '# honored (post-W179 universe re-derive + own-wave A', 1),
    ('# reservation when deriving B); seat MSG-2320 tail,', '# reservation when deriving B); seat MSG-0030 tail,', 1),
    ('assert WAVE_CONFIGS[179]["a_seed_base"] == 408_604 == 408_603 + 1, (', 'assert WAVE_CONFIGS[180]["a_seed_base"] == 410_804 == 410_803 + 1, (', 1),
    ('"W179 A must be the first-clean window past the registered "', '"W180 A must be the first-clean window past the registered "', 1),
    ('"W178 B band tail 408_603+1 (arithmetic continuation "', '"W179 B band tail 410_803+1 (arithmetic continuation "', 1),
    ('"408_404..410_403 REFUSED at its own start by the W178 B "', '"410_604..412_603 REFUSED at its own start by the W179 B "', 1),
    ('"band 408_404..408_603, exactly as the W178 seat W179+ projection + "', '"band 410_604..410_803, exactly as the W179 seat W180+ projection + "', 1),
    ('"r844 probe leg4 + r846 sec8 succession projection notes "', '"r848 probe leg4 + r850 sec8 succession projection notes "', 1),
    ('"staircase THIRTY-NINTH instance, E36 card)"', '"staircase FORTIETH instance, E36 card)"', 1),
    ('arith_a178 = set(range(408_604, 410_604))', 'arith_a179 = set(range(410_804, 412_804))', 1),
    ('assert not (arith_a178 & reg_ints), \\', 'assert not (arith_a179 & reg_ints), \\', 1),
    ('"W179 A window must be CLEAN (first-clean ADMIT face past prior-wave B)"', '"W180 A window must be CLEAN (first-clean ADMIT face past prior-wave B)"', 1),
    ('assert WAVE_CONFIGS[179]["b_exit_seed_base"] == 410_604 == 410_603 + 1, (', 'assert WAVE_CONFIGS[180]["b_exit_seed_base"] == 412_804 == 412_803 + 1, (', 1),
    ('"W179 B must be the first-clean window past the own-wave A "', '"W180 B must be the first-clean window past the own-wave A "', 1),
    ('"band tail 410_603+1 (arithmetic continuation "', '"band tail 412_803+1 (arithmetic continuation "', 1),
    ('"408_604..408_803 CLEAN on the registered universe but "', '"410_804..411_003 CLEAN on the registered universe but "', 1),
    ('"lands INSIDE the W179 A band window; same-freeze mutual "', '"lands INSIDE the W180 A band window; same-freeze mutual "', 1),
    ('"own-wave A window reserved jumps to 410_604, first-clean "', '"own-wave A window reserved jumps to 412_804, first-clean "', 1),
    ('arith_b178 = set(range(410_604, 410_804))', 'arith_b179 = set(range(412_804, 413_004))', 1),
    ('assert not (arith_b178 & reg_ints), \\', 'assert not (arith_b179 & reg_ints), \\', 1),
    ('"W179 B window must be CLEAN (first-clean ADMIT face past own-wave A)"', '"W180 B window must be CLEAN (first-clean ADMIT face past own-wave A)"', 1),
    ('assert not (arith_b178 & arith_a178), \\', 'assert not (arith_b179 & arith_a179), \\', 1),
    ('"W179 A/B same-freeze mutual exclusion (B hops past own A)"', '"W180 A/B same-freeze mutual exclusion (B hops past own A)"', 1),
    ('assert _entry_shard_of(0, 12) == ("PERPETUAL-N1-W179-SHARD-0",', 'assert _entry_shard_of(0, 12) == ("PERPETUAL-N1-W180-SHARD-0",', 1),
    ('"n1w179-0of12"), "W179 entry identity"', '"n1w180-0of12"), "W180 entry identity"', 1),
    ('assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W179-SHARD-11",', 'assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W180-SHARD-11",', 1),
    ('"n1w179-11of12")', '"n1w180-11of12")', 1),
    ('assert SHARD_DIR.endswith("n1_w179") and OUT.endswith(', 'assert SHARD_DIR.endswith("n1_w180") and OUT.endswith(', 1),
    ('"n1_w179_results.json"), "W179 path drift"', '"n1_w180_results.json"), "W180 path drift"', 1),
    ('f"W179 shard dir collides with W{wprev}"', 'f"W180 shard dir collides with W{wprev}"', 1),
    ('# W179 finalize cumulative deps: W17..W178 outputs ALL PRESENT', '# W180 finalize cumulative deps: W17..W179 outputs ALL PRESENT', 1),
    ('# (landed net chain head 797,505 = W178 bm-a r846 one-pass --', '# (landed net chain head 799,705 = W179 bm-a r850 one-pass --', 1),
    ('for _depw in range(17, 179):', 'for _depw in range(17, 180):', 1),
    ('f"W179 finalize cumulative dep (W{_depw} output) missing"', 'f"W180 finalize cumulative dep (W{_depw} output) missing"', 1),
    ('# registered wave below 179 composes; wave 15 excluded by', '# registered wave below 180 composes; wave 15 excluded by', 1),
    ('# design; SINGLE STATE (W2..W178 all registered -- no', '# design; SINGLE STATE (W2..W179 all registered -- no', 1),
    ('assert sorted(w for w in WAVE_CONFIGS if w < 179) == \\', 'assert sorted(w for w in WAVE_CONFIGS if w < 180) == \\', 1),
    ('[w for w in range(16, 179)], \\', '[w for w in range(16, 180)], \\', 1),
    ('"W179 prior-wave set must derive from registry keys (no 15; "', '"W180 prior-wave set must derive from registry keys (no 15; "', 1),
    ('"W2..W178 registered single state)"', '"W2..W179 registered single state)"', 1),
    ('PATHS.root, "research", "PERPETUAL_N1_W179_PREREG.md")), \\', 'PATHS.root, "research", "PERPETUAL_N1_W180_PREREG.md")), \\', 1),
    ('"W179 per-wave prereg missing (materializer requirement)"', '"W180 per-wave prereg missing (materializer requirement)"', 1),
]

CL_PAIRS = [
    ('"+ W179 materializer face [same guard set, dep=W17..W178 ', '"+ W180 materializer face [same guard set, dep=W17..W179 ', 1),
    ('"outputs ALL PRESENT (landed net chain head 797,505 = "', '"outputs ALL PRESENT (landed net chain head 799,705 = "', 1),
    ('"W178 bm-a r846 one-pass, K=389,520 merged pool; ZERO "', '"W179 bm-a r850 one-pass, K=391,720 merged pool; ZERO "', 1),
    ('"in-flight upstream seats), ONE HUNDRED-AND-SIXTY-NINTH "', '"in-flight upstream seats), ONE HUNDRED-AND-SEVENTIETH "', 1),
    ('"ENGINE-OWNED WAVE BY MACHINE-DERIVE (engine_owner rows 168 "', '"ENGINE-OWNED WAVE BY MACHINE-DERIVE (engine_owner rows 169 "', 1),
    ("+ candidate) bm-a's ninety-fifth owned claim per ", "+ candidate) bm-a's ninety-sixth owned claim per ", 1),
    ('"machine-derive (engine_owner==bm-a rows 94 + candidate), "', '"machine-derive (engine_owner==bm-a rows 95 + candidate), "', 1),
    ('"A=FIRST-CLEAN past the registered W178 B band (staircase "', '"A=FIRST-CLEAN past the registered W179 B band (staircase "', 1),
    ('"THIRTY-NINTH instance, E36 card, hops=1) + B=FIRST-CLEAN past the "', '"FORTIETH instance, E36 card, hops=1) + B=FIRST-CLEAN past the "', 1),
    ('"results/_r848bma_w179_probe_receipt.json, law sec.4 W179 row, "', '"results/_r851bma_w180_probe_receipt.json, law sec.4 W180 row, "', 1),
    ('"r849 bm-a] "', '"r852 bm-a] "', 1),
]

PF_NEG = ['    # W179 (bm-a r849 freeze, seat MSG-2026-10-07-2320-bma-w179-seat', 'pushed to origin 4c645c95f pre-freeze r565 law (r848 pre-seat', '(3-item; the W178 finalize product already on origin since r846,', '# = direct fast-forward behind-0 at fetch (r848 pre-seat', '# push), zero merge, zero --no-verify; self-ack archive ALREADY\r\n    # LANDED pre-freeze -- r848 same-window self-ack move (the W179\r\n    # seat MSG sits in fleet/inbox/processed/ at freeze time, honest\r\n    # archived);', 'band gate ADMIT results/_r848bma_w179_probe_receipt.json: A = FIRST-CLEAN', 'past the registered W178 B band (arithmetic continuation', '408_404..410_403 REFUSED at its own start by the W178 B band', '408_404..408_603, exactly as the W178 seat W179+ projection + r844 probe', '# leg4 + r846 sec8 succession projection notes all anticipated;', 'honest forward walk hops=1 -> 408_604..410_603, non-rotational', '(408_603+1) machine-checkable -- A-hops-prior-B staircase', 'THIRTY-NINTH instance, E36 card);', 'continuation 408_604..408_803 CLEAN on the registered universe', 'but lands INSIDE the W179 A band window -- same-freeze mutual', 'own-wave A window reserved jumps to 410_604 -> 410_604..410_803,', 'own-wave A tail+1 (410_603+1) machine-checkable);', 'W179+ projection (gate-derived r848): A first-clean', '410_604..412_603 CLEAN hops=0 / B first-clean 410_804..411_003', 'registered W179 B band 410_604..410_803 will refuse the naive', 'W180 A window; W180 freezer MUST re-derive on the post-W179', 'NOT a re-pick (R250: W179 bands were never assigned).', '179: {"a": (408_604, 410_603), "b_exit": (410_604, 410_803),', '4c645c95f', 'r844 probe', 'r846 sec8', 'r848 pre-seat', '_r848bma', 'MSG-2026-10-07-2320', 'de4716da2', '797,505', '389,520', 'THIRTY-NINTH', 'ONE HUNDRED-AND-SIXTY-NINTH']

EN_NEG = ['179: {"batch": "PERPETUAL-N1-W179",', '"prereg": ("research/PERPETUAL_N1_W179_PREREG.md (wave-level frozen "', 'new seed bands only; ONE HUNDRED-AND-SIXTY-NINTH ENGINE-OWNED WAVE ', 'BY MACHINE-DERIVE (engine_owner rows 168 + candidate), ', 'number law after the REGISTERED W178 row bm-a r845 freeze ', 'de4716da2, SINGLE STATE zero seat gap W2..W178 all ', 'registered; W179 finalize landed same-window r827, ledger ', 'head 797,505, merged pool K=389,520; seat published=reserved ', 'MSG-2026-10-07-2320-bma-w179-seat PUSHED to origin 4c645c95f ', 'probe receipt (3-item; the W178 finalize product already on origin since r846, not re-shipped; W146 precedent); ', 'at fetch (r848 pre-seat push), zero merge, zero ', 'engine_owner=bm-a, wave 178: ', 'A = FIRST-CLEAN past the registered W178 B band (the ', 'arithmetic continuation 408_404..410_403 is REFUSED at its ', 'own start by the W178 B band 408_404..408_603, exactly as ', 'the W178 seat W179+ projection + r844 probe leg4 + r846 sec8 succession ', '408_604..410_603; A base == prior-wave B tail+1 ', 'machine-checkable = A-hops-prior-B staircase THIRTY-NINTH ', 'arithmetic continuation 408_604..408_803 is CLEAN on the ', 'registered universe but lands INSIDE the W179 A band ', 'jumps to 410_604, first-clean 410_604..410_803 hops=1, ', 'convergence with the W178 seat W179+ projection + r844 probe leg4 + ', 'r846 sec8 succession projection notes re-derived -- all ', 'MANDATORY notes honored (post-W178 universe re-derive + ', 'results/_r848bma_w179_probe_receipt.json; W180+ projection ', 'per this window gate: A first-clean 410_604..412_603 ', 'CLEAN / B first-clean 410_804..411_003 CLEAN -- naive ', 'W179 B band 410_604..410_803 will refuse the naive ', 'W180 A window; W180 freezer MUST re-derive on the ', 'post-W179 universe AND reserve the own-wave A window ', 'staircase card); W1..W178 finalize ALL LANDED (W178 ', 'finalize one-pass bm-a r846, net chain head 797,505, ', 'merged pool K=389,520) -- ZERO in-flight upstream ', '"a_seed_base": 408_604,        # law sec.4 W179 A: 408_604..410_603 (FIRST-CLEAN past the registered W178 B band; arithmetic 408_404..410_403 REFUSED at own start by the W178 B band; hops=1; A-hops-prior-B staircase THIRTY-NINTH instance, E36 card; ordinal convergence per r587: W178 sec5.5 prose anticipated thirty-ninth, r848 receipt machine-read THIRTY-NINTH)', '"b_exit_seed_base": 410_604,   # law sec.4 W179 B: 410_604..410_803 (FIRST-CLEAN past the own-wave A window; arithmetic 408_604..408_803 lands inside own-A, same-freeze mutual exclusion W141 precedent; reserved walk hops=1; B base == own-A tail+1)', '"shard_subdir": "n1_w179", "out_name": "n1_w179_results.json",', 'de4716da2', '4c645c95f', '797,505', '389,520', 'ONE HUNDRED-AND-SIXTY-NINTH', 'rows 168', 'r844 probe', '_r848bma', 'MSG-2026-10-07-2320', 'n1w179', 'n1_w179', 'PERPETUAL-N1-W179', 'PERPETUAL_N1_W179', 'THIRTY-NINTH', 'bm-a r845 freeze', '410_604, first-clean']

MAT_NEG = ['# --- W179 materializer face (r849 bm-a freeze, own-series law', '#     ninety-fifth owned per machine-derive (engine_owner==bm-a', '#     rows 94 + candidate); wave 178 = first free number after', '#     the REGISTERED W178 row (bm-a r845 freeze de4716da2) --', '#     SINGLE STATE zero seat gap (W2..W178 all registered). Seat', '#     published=reserved MSG-2026-10-07-2320-bma-w179-seat pushed', '#     to origin 4c645c95f BEFORE this freeze, r565 law (payload', '#     the W178 finalize product already on origin since r846, not', '#     at fetch (r848 pre-seat push), zero merge, zero', '#     --no-verify; self-ack inbox->processed archive ALREADY LANDED\r\n    #     pre-freeze -- r848 same-window self-ack move (the W179 seat\r\n    #     MSG sits in fleet/inbox/processed/ at freeze time, honest\r\n    #     archived).', '#     ONE HUNDRED-AND-SIXTY-NINTH engine wave BY', '#     MACHINE-DERIVE (engine_owner rows 168 + candidate; gate', '#     W1..W178 finalize ALL LANDED (net chain head 797,505,', '#     K=389,520 merged pool; W178 finalize one-pass bm-a r846)', '#     always on. ADMIT receipt results/_r848bma_w179_probe_receipt.json;', '#     banned gate ADMIT 0; not a re-pick (R250: W179 bands were', '    _set_wave(179)', 'assert WAVE_CONFIGS[178]["a_seed_base"] == pf.N1_BANDS[178]["a"][0], \\', '"W179 A band drift vs law mirror"', 'assert WAVE_CONFIGS[178]["b_exit_seed_base"] == \\', 'pf.N1_BANDS[178]["b_exit"][0], "W179 B band drift vs law mirror"', 'assert WAVE_CONFIGS[178].get("engine_owner") == \\', 'pf.N1_BANDS[178].get("engine_owner") == "bm-a", \\', '"W179 engine_owner drift (law mirror parity)"', 'w178_a = {A_SEED_BASE + j for j in range(A_N)}', 'w178_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}', 'assert not (w178_a & w178_b), "W179 A/B band overlap"', 'assert not (w178_a & reg_ints) and not (w178_b & reg_ints), \\', '"W179 hits SEED_REGISTRY"', 'for nm, band in (("A", w178_a), ("B", w178_b)):', 'f"W179 {nm} hits v1"', 'f"W179 {nm} hits W1"', 'f"W179 {nm} hits probe seeds"', '# prior-wave disjointness W2..W178 (single state: all', 'for wprev in sorted(w for w in WAVE_CONFIGS if w < 179):', 'assert not (w178_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j', 'for j in range(A_N)}), f"W179 A hits W{wprev}"', 'assert not (w178_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j', 'for j in range(B_N)}), f"W179 B hits W{wprev}"', 'n3r1_used178 = set(range(70_000, 70_006))', 'assert not (w178_a & n3r1_used178) and not (w178_b & n3r1_used178), \\', '"W179 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"', 'assert not (w178_a & lfc_actual12) and not (w178_b & lfc_actual12), \\', '"W179 bands must clear the lfc actual draw range"', 'assert not (w178_a & options_actual12) and \\', 'not (w178_b & options_actual12), \\', '"W179 bands must clear the options_wave2 actual draw range"', '# band facts (law sec.4 W179 row, r795): A = FIRST-CLEAN past', '# the registered W178 B band (the arithmetic continuation', '# 408_404..410_403 is REFUSED at its own start by the W178', '# B band 408_404..408_603, exactly as the W178 seat W179+ projection +', '# r844 probe leg4 + r846 sec8 succession projection notes', '# 408_604..410_603; A base == prior-wave B tail+1 (408_603+1)', '# machine-checkable -- A-hops-prior-B staircase THIRTY-NINTH', '# continuation 408_604..408_803 is CLEAN on the registered', '# universe but lands INSIDE the W179 A band window --', '# 410_604 and lands 410_604..410_803, hops=1, non-rotational', '# (410_603+1) machine-checkable; cross-window convergence', '# with the W178 seat W179+ projection + r844 probe leg4 + r846 sec8', '# honored (post-W178 universe re-derive + own-wave A', '# reservation when deriving B); seat MSG-2320 tail,', 'assert WAVE_CONFIGS[179]["a_seed_base"] == 408_604 == 408_603 + 1, (', '"W179 A must be the first-clean window past the registered "', '"W178 B band tail 408_603+1 (arithmetic continuation "', '"408_404..410_403 REFUSED at its own start by the W178 B "', '"band 408_404..408_603, exactly as the W178 seat W179+ projection + "', '"r844 probe leg4 + r846 sec8 succession projection notes "', '"staircase THIRTY-NINTH instance, E36 card)"', 'arith_a178 = set(range(408_604, 410_604))', 'assert not (arith_a178 & reg_ints), \\', '"W179 A window must be CLEAN (first-clean ADMIT face past prior-wave B)"', 'assert WAVE_CONFIGS[179]["b_exit_seed_base"] == 410_604 == 410_603 + 1, (', '"W179 B must be the first-clean window past the own-wave A "', '"band tail 410_603+1 (arithmetic continuation "', '"408_604..408_803 CLEAN on the registered universe but "', '"lands INSIDE the W179 A band window; same-freeze mutual "', '"own-wave A window reserved jumps to 410_604, first-clean "', 'arith_b178 = set(range(410_604, 410_804))', 'assert not (arith_b178 & reg_ints), \\', '"W179 B window must be CLEAN (first-clean ADMIT face past own-wave A)"', 'assert not (arith_b178 & arith_a178), \\', '"W179 A/B same-freeze mutual exclusion (B hops past own A)"', 'assert _entry_shard_of(0, 12) == ("PERPETUAL-N1-W179-SHARD-0",', '"n1w179-0of12"), "W179 entry identity"', 'assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W179-SHARD-11",', '"n1w179-11of12")', 'assert SHARD_DIR.endswith("n1_w179") and OUT.endswith(', '"n1_w179_results.json"), "W179 path drift"', 'f"W179 shard dir collides with W{wprev}"', '# W179 finalize cumulative deps: W17..W178 outputs ALL PRESENT', '# (landed net chain head 797,505 = W178 bm-a r846 one-pass --', 'for _depw in range(17, 179):', 'f"W179 finalize cumulative dep (W{_depw} output) missing"', '# registered wave below 179 composes; wave 15 excluded by', '# design; SINGLE STATE (W2..W178 all registered -- no', 'assert sorted(w for w in WAVE_CONFIGS if w < 179) == \\', '[w for w in range(16, 179)], \\', '"W179 prior-wave set must derive from registry keys (no 15; "', '"W2..W178 registered single state)"', 'PATHS.root, "research", "PERPETUAL_N1_W179_PREREG.md")), \\', '"W179 per-wave prereg missing (materializer requirement)"', 'w178_', 'arith_a178', 'arith_b178', 'n3r1_used178', 'r844 probe', 'r848 pre-seat', 'de4716da2', 'ONE HUNDRED-AND-SIXTY-NINTH', 'ninety-fifth', 'rows 168', 'rows 94 ', 'range(17, 179)', 'range(16, 179)', 'PERPETUAL_N1_W179', 'PERPETUAL-N1-W179', 'MSG-2320', '_r848bma', 'r848 same-window', 'n1w179', 'n1_w179', '797,505', '389,520']

CL_NEG = ['"+ W179 materializer face [same guard set, dep=W17..W178 ', '"outputs ALL PRESENT (landed net chain head 797,505 = "', '"W178 bm-a r846 one-pass, K=389,520 merged pool; ZERO "', '"in-flight upstream seats), ONE HUNDRED-AND-SIXTY-NINTH "', '"ENGINE-OWNED WAVE BY MACHINE-DERIVE (engine_owner rows 168 "', "+ candidate) bm-a's ninety-fifth owned claim per ", '"machine-derive (engine_owner==bm-a rows 94 + candidate), "', '"A=FIRST-CLEAN past the registered W178 B band (staircase "', '"THIRTY-NINTH instance, E36 card, hops=1) + B=FIRST-CLEAN past the "', '"results/_r848bma_w179_probe_receipt.json, law sec.4 W179 row, "', '"r849 bm-a] "', '797,505', '389,520', 'ONE HUNDRED-AND-SIXTY-NINTH', 'ninety-fifth', 'rows 168', 'rows 94 ', 'THIRTY-NINTH', '_r848bma', 'r845 bm-a] ']

blk180 = vmap(pfblk, PF_PAIRS, PF_NEG, "pf")
entry180 = IND23 + vmap(entry, EN_PAIRS, EN_NEG, "entry")
mat180 = "    " + vmap(mat, MAT_PAIRS, MAT_NEG, "mat")
claim180 = IND10 + vmap(claim, CL_PAIRS, CL_NEG, "claim")

# ---- apply insertions (in-memory) ---------------------------------------
pfsrc = io.open(PF, encoding="utf-8", newline="").read()
n1src = io.open(N1, encoding="utf-8", newline="").read()

# pf: insert W180 block after the W179 row (last registered), before the
# dict close -- r560 insert-after-last-registered-row + post-anchor gate
seg = EO + NL + "}"
check(pfsrc.count(seg) == 1, "pf row-close segment not unique")
pfnew = pfsrc.replace(seg, EO + NL + blk180 + NL + "}", 1)

# n1 entry: after the W179 entry, before the WAVE_CONFIGS close
seg = EO + NL + IND23 + "}"
check(n1src.count(seg) == 1, "n1 entry-close segment not unique")
n1new = n1src.replace(seg, EO + NL + entry180 + NL + IND23 + "}", 1)

# n1 mat: insert the W180 block before the T-141 s2 lane face header
seg = "    # --- T-141 s2 lane face"
check(n1new.count(seg) == 1, "n1 T-141 mat anchor not unique")
n1new = n1new.replace(seg, mat180 + NL + seg, 1)

# n1 claim: insert the W180 attribution after the W179 claim tail line
# (r581 law: anchor = tail single-line literal + post-anchor guard)
seg = '"r849 bm-a] "' + NL + IND10 + '"+ T-141 s2 "'
check(n1new.count(seg) == 1, "n1 claim anchor not unique")
n1new = n1new.replace(seg, '"r849 bm-a] "' + NL + claim180 + NL + IND10 +
                      '"+ T-141 s2 "', 1)

# ---- gates (r780/r781/r560/r815 lineage) --------------------------------
ast.parse(pfnew)
ast.parse(n1new)
print("AST gate: both files parse OK")

# W180 presence + W179 anti-vanish (r560 law)
checks = [
    (pfnew, '180: {"a": (410_804, 412_803), "b_exit": (412_804, 413_003),', 1),
    (pfnew, '179: {"a": (408_604, 410_603), "b_exit": (410_604, 410_803),', 1),
    (pfnew, "# W180 (bm-a r852 freeze", 1),
    (pfnew, "# W179 (bm-a r849 freeze", 1),
    (n1new, '180: {"batch": "PERPETUAL-N1-W180",', 1),
    (n1new, '179: {"batch": "PERPETUAL-N1-W179",', 1),
    (n1new, "# --- W180 materializer face", 1),
    (n1new, "# --- W179 materializer face", 1),
    (n1new, '"r852 bm-a] "', 1),
    (n1new, '"r849 bm-a] "', 1),
    (n1new, '"a_seed_base": 410_804,', 1),
    (n1new, '"b_exit_seed_base": 412_804,', 1),
    (n1new, "n1_w180", 4),
    (n1new, "PERPETUAL_N1_W180_PREREG.md", 2),
]
for src, needle, cnt in checks:
    got = src.count(needle)
    check(got == cnt, "post-edit needle %r count %d != %d" % (needle[:50], got, cnt))

# W181+ projection prose present in the new W180 blocks (probe leg4
# verbatim; r819 post-edit assert bloodline + r776 fragment-needle law;
# pf header = self-wave W180+ per r845 precedent, n1 fragment = next-wave
# W181+)
check("# W180+ projection (gate-derived r851)" in pfnew,
      "pf W180+ projection head missing")
check('probe_receipt.json; W181+ projection "' in n1new,
      "n1 W181+ projection head fragment missing")
check("# 412_804..414_803 CLEAN hops=0 / B first-clean 413_004..413_203" in pfnew,
      "pf W181p prose missing")
check("W181 A window; W181 freezer MUST re-derive on the post-W180" in pfnew,
      "pf W181 freezer prose missing")
check('"W181 A window; W181 freezer MUST re-derive on the "' in n1new,
      "n1 W181 freezer fragment missing")
check('"W180 B band 412_804..413_003 will refuse the naive "' in n1new,
      "n1 W180-band refuse fragment missing")

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
check('180: {"a": (410_804' not in pf_o2, "write-time: origin pf carries W180")
check('180: {"batch"' not in n1_o2, "write-time: origin n1 carries W180")
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
