# -*- coding: utf-8 -*-
"""r849 bm-a W179 freeze edits: four insertions (pf N1_BANDS[179] row +
n1 WAVE_CONFIGS[179] entry + n1 W179 materializer block + n1 W179
PASS-claim attribution). DRY flag: --dry = zero-write simulation
(r781 verify-separation law + r811/r822/r826/r830/r834/r843/r845
dry-run precedent: full stale+prose+AST asserts in memory BEFORE any
write).

Bloodline: r819/r822/r826/r830/r834/r843/r845 freeze-edits machinery (r773 pit
law freeze-editor compliance + r776 fragment-needle law + r781
verify-separation law), W179 facts live-registry-driven (built by
_r849bma_w179_freeze_buildgen.py: old sides = the PHYSICAL W178 face
fragments probed to dumps this window, new sides = the S79f W179 fact
map, counts verified pre-emission):
  - pre-seat probe results/_r848bma_w179_probe_receipt.json rc0 ADMIT
    (A 408_604..410_603 staircase THIRTY-NINTH instance E36 hops=1
    past the registered W178 B band 408_404..408_603; naive
    408_404..410_403 refused at its own start by the W178 B band --
    receipt A_semantics machine-cites the W178 seat MSG leg4 + r844
    probe leg4 anticipated + MANDATED this re-derive (W178 sec5.5
    prose anticipated 39th -- projection and receipt ordinals MATCH,
    no divergence this wave); B 410_604..410_803 own-A mutual
    exclusion hops=1, naive 408_604..408_803);
  - face probe results/_r849bma_w179_face_probe_receipt.json rc0 (all
    four W178 faces dumped + needle counts; this TOK is built from the
    PHYSICAL probe-dumped shapes, r776 law);
  - seat MSG-2026-10-07-2320-bma-w179-seat published on origin at
    4c645c95f (r848 pre-seat push, path-derived TRUE sha per r812
    precedent); r565 law: on origin BEFORE this freeze commit;
    self-ack archive ALREADY LANDED pre-freeze -- r848 same-window
    self-ack move (the W179 seat MSG sits in fleet/inbox/processed/ at
    freeze time, honest archived);
  - per-wave prereg research/PERPETUAL_N1_W179_PREREG.md frozen at
    origin 6f14c35d5 (r849 surgical-path push behind bm-c r706/707
    race; banned gate ADMIT 0 re-verified at prereg freeze);
  - W178 freeze registered sha machine-derived = de4716da2 (git log
    origin/main --grep "W178 FREEZE"); W178 finalize landed r846
    one-pass adoption closeout: ledger head 797,505, merged pool
    K=389,520 (n1_w178_results.json machine-read; sec7/sec8 backfill
    landed the r846 same window -- same-window, honest);
  - lineage constants disclosed (r795/r845 precedent, passed through):
    (a) the "wave N-1 = first free number" mat-header label rides the
    vmap verbatim (off-by-one lineage quirk since W165 r795);
    (b) "law sec.4 W179 row, r795" band-facts template stamp keeps its
    r795;
    (c) "single-window derive (r812 merged the gate legs INTO the
    pre-seat probe...)" stays (historical merge citation);
    (d) the bm-a-owned ordinal word rolls ninety-fourth ->
    ninety-fifth (rows 94 + candidate = 95th owned per probe leg0);
    (e) mat parity-chain rows W138..W177 keep their historical stamps
    and tuples; the W178 row (the current registered tail) is
    APPENDED with its frozen values (406_404, 408_403)/(408_404,
    408_603);
    (f) the "W178 finalize landed same-window r827" citation rides
    the vmap verbatim (off-by-one wave-word + stale-session lineage
    quirk inherited from the r830/r834/r843/r845 generations; head/K
    values roll machine-correct to 797,505/389,520 this window --
    prose session stamp stays per frozen-lineage discipline).

r773 pit law compliance:
  (1) full string-face inventory empirically probed BEFORE TOK
      (_r849bma_w179_face_probe.py -- four face dumps + needle-count
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
      (r530/r687: fetch + origin carries no W179 registration before
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
probe = json.load(open(r"results\_r848bma_w179_probe_receipt.json",
                       encoding="utf-8"))
check(probe["verdict"] == "ADMIT", "pre-seat probe not ADMIT")
check(probe["bands"] == {"A": "408604_410603", "B": "410604_410803"},
      "probe band shape mismatch")
check(probe["legs"]["leg1"]["A"] == [408604, 410603], "A band mismatch")
check(probe["legs"]["leg1"]["B"] == [410604, 410803], "B band mismatch")
check(probe["legs"]["leg1"]["hops_A"] == 1 and probe["legs"]["leg1"]["hops_B"] == 1,
      "hops mismatch")
check(probe["legs"]["leg0"]["rows"] == 176 and probe["legs"]["leg0"]["tail"] == "W178",
      "leg0 registry tail mismatch")
check(probe["legs"]["leg0"]["ordinal"] == 169 and probe["legs"]["leg0"]["bma_ordinal"] == 95,
      "leg0 ordinal mismatch")
check(probe["legs"]["leg2"]["conflicts"] == 0, "leg2 conflicts nonzero")
check(probe["legs"]["leg3"]["origin_vacancy"] is True, "leg3 origin not vacant")
check(probe["legs"]["leg4"]["W180p_A"] == "410604..412603"
      and probe["legs"]["leg4"]["W180p_B"] == "410804..411003",
      "leg4 W180+ projection mismatch")

# origin anti-collision pre-check (r511 tail-lock / r687 write-time gate)
subprocess.run(["git", "fetch", "origin"], capture_output=True)
pf_o = subprocess.run(["git", "show", "origin/main:" + PF],
                      capture_output=True).stdout.decode("utf-8", "replace")
n1_o = subprocess.run(["git", "show", "origin/main:" + N1],
                      capture_output=True).stdout.decode("utf-8", "replace")
check('179: {"a": (408_604' not in pf_o, "origin pf already carries W179 row")
check("W179 (bm-a r849 freeze" not in pf_o, "origin pf carries W179 block")
check('179: {"batch"' not in n1_o, "origin n1 already carries W179 entry")
check("# --- W179 materializer face" not in n1_o, "origin n1 carries W179 mat")
check('"r849 bm-a] "' not in n1_o, "origin n1 carries W179 claim")

# machine-derived shas (r587 / r812 path-derived precedent)
seat_sha = subprocess.run(
    ["git", "log", "origin/main", "--format=%h", "-n", "1", "--diff-filter=A",
     "--", "fleet/inbox/MSG-2026-10-07-2320-bma-w179-seat.md"],
    capture_output=True).stdout.decode().strip()
check(seat_sha == "4c645c95f", "seat sha path-derived mismatch: " + seat_sha)
check(os.path.exists(os.path.join(
    "fleet", "inbox", "processed", "MSG-2026-10-07-2320-bma-w179-seat.md")),
    "seat MSG not in processed/ at freeze time (self-ack archive)")
w178_freeze_sha = subprocess.run(
    ["git", "log", "origin/main", "--format=%h", "-n", "1", "--grep=W178 FREEZE"],
    capture_output=True).stdout.decode().strip()
check(w178_freeze_sha == "de4716da2", "W178 freeze sha mismatch: " + w178_freeze_sha)

# ---- live-registry parity pre-check (edit-gate: never edit a drifted file)
sys.path.insert(0, "scripts")
import perpetual_faces as pfmod  # noqa: E402
check(len(pfmod.N1_BANDS) == 176, "live N1_BANDS row count drift: %d" % len(pfmod.N1_BANDS))
check(pfmod.N1_BANDS[178] == {"a": (406_404, 408_403),
                              "b_exit": (408_404, 408_603),
                              "engine_owner": "bm-a"}, "live W178 row drift")
check(179 not in pfmod.N1_BANDS, "live N1_BANDS already has 179")
check(os.path.exists(os.path.join("research", "PERPETUAL_N1_W179_PREREG.md")),
      "W179 per-wave prereg missing (materializer gate)")
prereg_o = subprocess.run(["git", "show", "origin/main:research/PERPETUAL_N1_W179_PREREG.md"],
                          capture_output=True)
check(prereg_o.returncode == 0, "W179 prereg absent on origin")

# ---- physical face dumps (r776 law) -----------------------------------
pfblk = io.open(r"results\_r849bma_w179_probe_pf_block.txt", encoding="utf-8",
                newline="").read()
entry = io.open(r"results\_r849bma_w179_probe_n1_entry.txt", encoding="utf-8",
                newline="").read()
mat = io.open(r"results\_r849bma_w179_probe_n1_mat.txt", encoding="utf-8",
              newline="").read()
claim = io.open(r"results\_r849bma_w179_probe_n1_claim.txt", encoding="utf-8",
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
    ('    # W178 (bm-a r845 freeze, seat MSG-2026-10-07-2157-bma-w178-seat', '    # W179 (bm-a r849 freeze, seat MSG-2026-10-07-2320-bma-w179-seat', 1),
    ('pushed to origin 5b9284c79 pre-freeze r565 law (r844 pre-seat', 'pushed to origin 4c645c95f pre-freeze r565 law (r848 pre-seat', 1),
    ('(3-item; the W177 finalize product already on origin since r844,', '(3-item; the W178 finalize product already on origin since r846,', 1),
    ('# = direct fast-forward behind-0 at fetch (r844 pre-seat', '# = direct fast-forward behind-0 at fetch (r848 pre-seat', 1),
    ('# push), zero merge, zero --no-verify; self-ack archive ALREADY\r\n    # LANDED pre-freeze -- r845 same-window self-ack move (the W178\r\n    # seat MSG sits in fleet/inbox/processed/ at freeze time, honest\r\n    # archived);', '# push), zero merge, zero --no-verify; self-ack archive ALREADY\r\n    # LANDED pre-freeze -- r848 same-window self-ack move (the W179\r\n    # seat MSG sits in fleet/inbox/processed/ at freeze time, honest\r\n    # archived);', 1),
    ('band gate ADMIT results/_r844bma_w178_probe_receipt.json: A = FIRST-CLEAN', 'band gate ADMIT results/_r848bma_w179_probe_receipt.json: A = FIRST-CLEAN', 1),
    ('past the registered W177 B band (arithmetic continuation', 'past the registered W178 B band (arithmetic continuation', 1),
    ('406_204..408_203 REFUSED at its own start by the W177 B band', '408_404..410_403 REFUSED at its own start by the W178 B band', 1),
    ('406_204..406_403, exactly as the W177 seat W178+ projection + r841 probe', '408_404..408_603, exactly as the W178 seat W179+ projection + r844 probe', 1),
    ('# leg4 + r844 sec8 succession projection notes all anticipated;', '# leg4 + r846 sec8 succession projection notes all anticipated;', 1),
    ('honest forward walk hops=1 -> 406_404..408_403, non-rotational', 'honest forward walk hops=1 -> 408_604..410_603, non-rotational', 1),
    ('(406_403+1) machine-checkable -- A-hops-prior-B staircase', '(408_603+1) machine-checkable -- A-hops-prior-B staircase', 1),
    ('THIRTY-EIGHTH instance, E36 card);', 'THIRTY-NINTH instance, E36 card);', 1),
    ('continuation 406_404..406_603 CLEAN on the registered universe', 'continuation 408_604..408_803 CLEAN on the registered universe', 1),
    ('but lands INSIDE the W178 A band window -- same-freeze mutual', 'but lands INSIDE the W179 A band window -- same-freeze mutual', 1),
    ('own-wave A window reserved jumps to 408_404 -> 408_404..408_603,', 'own-wave A window reserved jumps to 410_604 -> 410_604..410_803,', 1),
    ('own-wave A tail+1 (408_403+1) machine-checkable);', 'own-wave A tail+1 (410_603+1) machine-checkable);', 1),
    ('W178+ projection (gate-derived r844): A first-clean', 'W179+ projection (gate-derived r848): A first-clean', 1),
    ('408_404..410_403 CLEAN hops=0 / B first-clean 408_604..408_803', '410_604..412_603 CLEAN hops=0 / B first-clean 410_804..411_003', 1),
    ('registered W178 B band 408_404..408_603 will refuse the naive', 'registered W179 B band 410_604..410_803 will refuse the naive', 1),
    ('W179 A window; W179 freezer MUST re-derive on the post-W178', 'W180 A window; W180 freezer MUST re-derive on the post-W179', 1),
    ('NOT a re-pick (R250: W178 bands were never assigned).', 'NOT a re-pick (R250: W179 bands were never assigned).', 1),
    ('178: {"a": (406_404, 408_403), "b_exit": (408_404, 408_603),', '179: {"a": (408_604, 410_603), "b_exit": (410_604, 410_803),', 1),
]

EN_PAIRS = [
    ('178: {"batch": "PERPETUAL-N1-W178",', '179: {"batch": "PERPETUAL-N1-W179",', 1),
    ('"prereg": ("research/PERPETUAL_N1_W178_PREREG.md (wave-level frozen "', '"prereg": ("research/PERPETUAL_N1_W179_PREREG.md (wave-level frozen "', 1),
    ('new seed bands only; ONE HUNDRED-AND-SIXTY-EIGHTH ENGINE-OWNED WAVE ', 'new seed bands only; ONE HUNDRED-AND-SIXTY-NINTH ENGINE-OWNED WAVE ', 1),
    ('BY MACHINE-DERIVE (engine_owner rows 167 + candidate), ', 'BY MACHINE-DERIVE (engine_owner rows 168 + candidate), ', 1),
    ('number law after the REGISTERED W177 row bm-a r843 freeze ', 'number law after the REGISTERED W178 row bm-a r845 freeze ', 1),
    ('c06cc230f, SINGLE STATE zero seat gap W2..W177 all ', 'de4716da2, SINGLE STATE zero seat gap W2..W178 all ', 1),
    ('registered; W178 finalize landed same-window r827, ledger ', 'registered; W179 finalize landed same-window r827, ledger ', 1),
    ('head 795,305, merged pool K=387,320; seat published=reserved ', 'head 797,505, merged pool K=389,520; seat published=reserved ', 1),
    ('MSG-2026-10-07-2157-bma-w178-seat PUSHED to origin 5b9284c79 ', 'MSG-2026-10-07-2320-bma-w179-seat PUSHED to origin 4c645c95f ', 1),
    ('probe receipt (3-item; the W177 finalize product already on origin since r844, not re-shipped; W146 precedent); ', 'probe receipt (3-item; the W178 finalize product already on origin since r846, not re-shipped; W146 precedent); ', 1),
    ('at fetch (r844 pre-seat push), zero merge, zero ', 'at fetch (r848 pre-seat push), zero merge, zero ', 1),
    ('engine_owner=bm-a, wave 177: ', 'engine_owner=bm-a, wave 178: ', 1),
    ('A = FIRST-CLEAN past the registered W177 B band (the ', 'A = FIRST-CLEAN past the registered W178 B band (the ', 1),
    ('arithmetic continuation 406_204..408_203 is REFUSED at its ', 'arithmetic continuation 408_404..410_403 is REFUSED at its ', 1),
    ('own start by the W177 B band 406_204..406_403, exactly as ', 'own start by the W178 B band 408_404..408_603, exactly as ', 1),
    ('the W177 seat W178+ projection + r841 probe leg4 + r844 sec8 succession ', 'the W178 seat W179+ projection + r844 probe leg4 + r846 sec8 succession ', 1),
    ('projection notes anticipated; honest forward walk hops=1 -> ', 'projection notes anticipated; honest forward walk hops=1 -> ', 1),
    ('406_404..408_403; A base == prior-wave B tail+1 ', '408_604..410_603; A base == prior-wave B tail+1 ', 1),
    ('machine-checkable = A-hops-prior-B staircase THIRTY-EIGHTH ', 'machine-checkable = A-hops-prior-B staircase THIRTY-NINTH ', 1),
    ('arithmetic continuation 406_404..406_603 is CLEAN on the ', 'arithmetic continuation 408_604..408_803 is CLEAN on the ', 1),
    ('registered universe but lands INSIDE the W178 A band ', 'registered universe but lands INSIDE the W179 A band ', 1),
    ('jumps to 408_404, first-clean 408_404..408_603 hops=1, ', 'jumps to 410_604, first-clean 410_604..410_803 hops=1, ', 1),
    ('convergence with the W177 seat W178+ projection + r841 probe leg4 + ', 'convergence with the W178 seat W179+ projection + r844 probe leg4 + ', 1),
    ('r844 sec8 succession projection notes re-derived -- all ', 'r846 sec8 succession projection notes re-derived -- all ', 1),
    ('MANDATORY notes honored (post-W177 universe re-derive + ', 'MANDATORY notes honored (post-W178 universe re-derive + ', 1),
    ('results/_r844bma_w178_probe_receipt.json; W179+ projection ', 'results/_r848bma_w179_probe_receipt.json; W180+ projection ', 1),
    ('per this window gate: A first-clean 408_404..410_403 ', 'per this window gate: A first-clean 410_604..412_603 ', 1),
    ('CLEAN / B first-clean 408_604..408_803 CLEAN -- naive ', 'CLEAN / B first-clean 410_804..411_003 CLEAN -- naive ', 1),
    ('W178 B band 408_404..408_603 will refuse the naive ', 'W179 B band 410_604..410_803 will refuse the naive ', 1),
    ('W179 A window; W179 freezer MUST re-derive on the ', 'W180 A window; W180 freezer MUST re-derive on the ', 1),
    ('post-W178 universe AND reserve the own-wave A window ', 'post-W179 universe AND reserve the own-wave A window ', 1),
    ('staircase card); W1..W177 finalize ALL LANDED (W177 ', 'staircase card); W1..W178 finalize ALL LANDED (W178 ', 1),
    ('finalize one-pass bm-a r844, net chain head 795,305, ', 'finalize one-pass bm-a r846, net chain head 797,505, ', 1),
    ('merged pool K=387,320) -- ZERO in-flight upstream ', 'merged pool K=389,520) -- ZERO in-flight upstream ', 1),
    ('"a_seed_base": 406_404,        # law sec.4 W178 A: 406_404..408_403 (FIRST-CLEAN past the registered W177 B band; arithmetic 406_204..408_203 REFUSED at own start by the W177 B band; hops=1; A-hops-prior-B staircase THIRTY-EIGHTH instance, E36 card; ordinal convergence per r587: W177 sec5.5 prose anticipated thirty-eighth, r844 receipt machine-read THIRTY-EIGHTH)', '"a_seed_base": 408_604,        # law sec.4 W179 A: 408_604..410_603 (FIRST-CLEAN past the registered W178 B band; arithmetic 408_404..410_403 REFUSED at own start by the W178 B band; hops=1; A-hops-prior-B staircase THIRTY-NINTH instance, E36 card; ordinal convergence per r587: W178 sec5.5 prose anticipated thirty-ninth, r848 receipt machine-read THIRTY-NINTH)', 1),
    ('"b_exit_seed_base": 408_404,   # law sec.4 W178 B: 408_404..408_603 (FIRST-CLEAN past the own-wave A window; arithmetic 406_404..406_603 lands inside own-A, same-freeze mutual exclusion W141 precedent; reserved walk hops=1; B base == own-A tail+1)', '"b_exit_seed_base": 410_604,   # law sec.4 W179 B: 410_604..410_803 (FIRST-CLEAN past the own-wave A window; arithmetic 408_604..408_803 lands inside own-A, same-freeze mutual exclusion W141 precedent; reserved walk hops=1; B base == own-A tail+1)', 1),
    ('"shard_subdir": "n1_w178", "out_name": "n1_w178_results.json",', '"shard_subdir": "n1_w179", "out_name": "n1_w179_results.json",', 1),
]

MAT_PAIRS = [
    ('# --- W178 materializer face (r845 bm-a freeze, own-series law', '# --- W179 materializer face (r849 bm-a freeze, own-series law', 1),
    ('#     ninety-fourth owned per machine-derive (engine_owner==bm-a', '#     ninety-fifth owned per machine-derive (engine_owner==bm-a', 1),
    ('#     rows 93 + candidate); wave 177 = first free number after', '#     rows 94 + candidate); wave 178 = first free number after', 1),
    ('#     the REGISTERED W177 row (bm-a r843 freeze c06cc230f) --', '#     the REGISTERED W178 row (bm-a r845 freeze de4716da2) --', 1),
    ('#     SINGLE STATE zero seat gap (W2..W177 all registered). Seat', '#     SINGLE STATE zero seat gap (W2..W178 all registered). Seat', 1),
    ('#     published=reserved MSG-2026-10-07-2157-bma-w178-seat pushed', '#     published=reserved MSG-2026-10-07-2320-bma-w179-seat pushed', 1),
    ('#     to origin 5b9284c79 BEFORE this freeze, r565 law (payload', '#     to origin 4c645c95f BEFORE this freeze, r565 law (payload', 1),
    ('#     the W177 finalize product already on origin since r844, not', '#     the W178 finalize product already on origin since r846, not', 1),
    ('#     at fetch (r844 pre-seat push), zero merge, zero', '#     at fetch (r848 pre-seat push), zero merge, zero', 1),
    ('#     --no-verify; self-ack inbox->processed archive ALREADY LANDED\r\n    #     pre-freeze -- r845 same-window self-ack move (the W178 seat\r\n    #     MSG sits in fleet/inbox/processed/ at freeze time, honest\r\n    #     archived).', '#     --no-verify; self-ack inbox->processed archive ALREADY LANDED\r\n    #     pre-freeze -- r848 same-window self-ack move (the W179 seat\r\n    #     MSG sits in fleet/inbox/processed/ at freeze time, honest\r\n    #     archived).', 1),
    ('#     ONE HUNDRED-AND-SIXTY-EIGHTH engine wave BY', '#     ONE HUNDRED-AND-SIXTY-NINTH engine wave BY', 1),
    ('#     MACHINE-DERIVE (engine_owner rows 167 + candidate; gate', '#     MACHINE-DERIVE (engine_owner rows 168 + candidate; gate', 1),
    ('#     W1..W177 finalize ALL LANDED (net chain head 795,305,', '#     W1..W178 finalize ALL LANDED (net chain head 797,505,', 1),
    ('#     K=387,320 merged pool; W177 finalize one-pass bm-a r844)', '#     K=389,520 merged pool; W178 finalize one-pass bm-a r846)', 1),
    ('#     always on. ADMIT receipt results/_r844bma_w178_probe_receipt.json;', '#     always on. ADMIT receipt results/_r848bma_w179_probe_receipt.json;', 1),
    ('#     banned gate ADMIT 0; not a re-pick (R250: W178 bands were', '#     banned gate ADMIT 0; not a re-pick (R250: W179 bands were', 1),
    ('    _set_wave(178)', '    _set_wave(179)', 1),
    ('assert WAVE_CONFIGS[177]["a_seed_base"] == pf.N1_BANDS[177]["a"][0], \\', 'assert WAVE_CONFIGS[178]["a_seed_base"] == pf.N1_BANDS[178]["a"][0], \\', 1),
    ('"W178 A band drift vs law mirror"', '"W179 A band drift vs law mirror"', 1),
    ('assert WAVE_CONFIGS[177]["b_exit_seed_base"] == \\', 'assert WAVE_CONFIGS[178]["b_exit_seed_base"] == \\', 1),
    ('pf.N1_BANDS[177]["b_exit"][0], "W178 B band drift vs law mirror"', 'pf.N1_BANDS[178]["b_exit"][0], "W179 B band drift vs law mirror"', 1),
    ('assert WAVE_CONFIGS[177].get("engine_owner") == \\', 'assert WAVE_CONFIGS[178].get("engine_owner") == \\', 1),
    ('pf.N1_BANDS[177].get("engine_owner") == "bm-a", \\', 'pf.N1_BANDS[178].get("engine_owner") == "bm-a", \\', 1),
    ('"W178 engine_owner drift (law mirror parity)"', '"W179 engine_owner drift (law mirror parity)"', 1),
    ('w177_a = {A_SEED_BASE + j for j in range(A_N)}', 'w178_a = {A_SEED_BASE + j for j in range(A_N)}', 1),
    ('w177_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}', 'w178_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}', 1),
    ('assert not (w177_a & w177_b), "W178 A/B band overlap"', 'assert not (w178_a & w178_b), "W179 A/B band overlap"', 1),
    ('assert not (w177_a & reg_ints) and not (w177_b & reg_ints), \\', 'assert not (w178_a & reg_ints) and not (w178_b & reg_ints), \\', 1),
    ('"W178 hits SEED_REGISTRY"', '"W179 hits SEED_REGISTRY"', 1),
    ('for nm, band in (("A", w177_a), ("B", w177_b)):', 'for nm, band in (("A", w178_a), ("B", w178_b)):', 1),
    ('f"W178 {nm} hits v1"', 'f"W179 {nm} hits v1"', 1),
    ('f"W178 {nm} hits W1"', 'f"W179 {nm} hits W1"', 1),
    ('f"W178 {nm} hits probe seeds"', 'f"W179 {nm} hits probe seeds"', 1),
    ('"registered W177 row parity drift (r307; bm-a r843)"', '"registered W177 row parity drift (r307; bm-a r843)"\r\n        assert pf.N1_BANDS[178] == {"a": (406_404, 408_403),\r\n                                    "b_exit": (408_404, 408_603),\r\n                                    "engine_owner": "bm-a"}, \\\r\n            "registered W178 row parity drift (r307; bm-a r845)"', 1),
    ('# prior-wave disjointness W2..W177 (single state: all', '# prior-wave disjointness W2..W178 (single state: all', 1),
    ('for wprev in sorted(w for w in WAVE_CONFIGS if w < 178):', 'for wprev in sorted(w for w in WAVE_CONFIGS if w < 179):', 2),
    ('assert not (w177_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j', 'assert not (w178_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j', 1),
    ('for j in range(A_N)}), f"W178 A hits W{wprev}"', 'for j in range(A_N)}), f"W179 A hits W{wprev}"', 1),
    ('assert not (w177_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j', 'assert not (w178_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j', 1),
    ('for j in range(B_N)}), f"W178 B hits W{wprev}"', 'for j in range(B_N)}), f"W179 B hits W{wprev}"', 1),
    ('n3r1_used177 = set(range(70_000, 70_006))', 'n3r1_used178 = set(range(70_000, 70_006))', 1),
    ('assert not (w177_a & n3r1_used177) and not (w177_b & n3r1_used177), \\', 'assert not (w178_a & n3r1_used178) and not (w178_b & n3r1_used178), \\', 1),
    ('"W178 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"', '"W179 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"', 1),
    ('assert not (w177_a & lfc_actual12) and not (w177_b & lfc_actual12), \\', 'assert not (w178_a & lfc_actual12) and not (w178_b & lfc_actual12), \\', 1),
    ('"W178 bands must clear the lfc actual draw range"', '"W179 bands must clear the lfc actual draw range"', 1),
    ('assert not (w177_a & options_actual12) and \\', 'assert not (w178_a & options_actual12) and \\', 1),
    ('not (w177_b & options_actual12), \\', 'not (w178_b & options_actual12), \\', 1),
    ('"W178 bands must clear the options_wave2 actual draw range"', '"W179 bands must clear the options_wave2 actual draw range"', 1),
    ('# band facts (law sec.4 W178 row, r795): A = FIRST-CLEAN past', '# band facts (law sec.4 W179 row, r795): A = FIRST-CLEAN past', 1),
    ('# the registered W177 B band (the arithmetic continuation', '# the registered W178 B band (the arithmetic continuation', 1),
    ('# 406_204..408_203 is REFUSED at its own start by the W177', '# 408_404..410_403 is REFUSED at its own start by the W178', 1),
    ('# B band 406_204..406_403, exactly as the W177 seat W178+ projection +', '# B band 408_404..408_603, exactly as the W178 seat W179+ projection +', 1),
    ('# r841 probe leg4 + r844 sec8 succession projection notes', '# r844 probe leg4 + r846 sec8 succession projection notes', 1),
    ('# 406_404..408_403; A base == prior-wave B tail+1 (406_403+1)', '# 408_604..410_603; A base == prior-wave B tail+1 (408_603+1)', 1),
    ('# machine-checkable -- A-hops-prior-B staircase THIRTY-EIGHTH', '# machine-checkable -- A-hops-prior-B staircase THIRTY-NINTH', 1),
    ('# continuation 406_404..406_603 is CLEAN on the registered', '# continuation 408_604..408_803 is CLEAN on the registered', 1),
    ('# universe but lands INSIDE the W178 A band window --', '# universe but lands INSIDE the W179 A band window --', 1),
    ('# 408_404 and lands 408_404..408_603, hops=1, non-rotational', '# 410_604 and lands 410_604..410_803, hops=1, non-rotational', 1),
    ('# (408_403+1) machine-checkable; cross-window convergence', '# (410_603+1) machine-checkable; cross-window convergence', 1),
    ('# with the W177 seat W178+ projection + r841 probe leg4 + r844 sec8', '# with the W178 seat W179+ projection + r844 probe leg4 + r846 sec8', 1),
    ('# honored (post-W177 universe re-derive + own-wave A', '# honored (post-W178 universe re-derive + own-wave A', 1),
    ('# reservation when deriving B); seat MSG-2150 tail,', '# reservation when deriving B); seat MSG-2320 tail,', 1),
    ('assert WAVE_CONFIGS[178]["a_seed_base"] == 406_404 == 406_403 + 1, (', 'assert WAVE_CONFIGS[179]["a_seed_base"] == 408_604 == 408_603 + 1, (', 1),
    ('"W178 A must be the first-clean window past the registered "', '"W179 A must be the first-clean window past the registered "', 1),
    ('"W177 B band tail 406_403+1 (arithmetic continuation "', '"W178 B band tail 408_603+1 (arithmetic continuation "', 1),
    ('"406_204..408_203 REFUSED at its own start by the W177 B "', '"408_404..410_403 REFUSED at its own start by the W178 B "', 1),
    ('"band 406_204..406_403, exactly as the W177 seat W178+ projection + "', '"band 408_404..408_603, exactly as the W178 seat W179+ projection + "', 1),
    ('"r841 probe leg4 + r844 sec8 succession projection notes "', '"r844 probe leg4 + r846 sec8 succession projection notes "', 1),
    ('"staircase THIRTY-EIGHTH instance, E36 card)"', '"staircase THIRTY-NINTH instance, E36 card)"', 1),
    ('arith_a177 = set(range(406_404, 408_404))', 'arith_a178 = set(range(408_604, 410_604))', 1),
    ('assert not (arith_a177 & reg_ints), \\', 'assert not (arith_a178 & reg_ints), \\', 1),
    ('"W178 A window must be CLEAN (first-clean ADMIT face past prior-wave B)"', '"W179 A window must be CLEAN (first-clean ADMIT face past prior-wave B)"', 1),
    ('assert WAVE_CONFIGS[178]["b_exit_seed_base"] == 408_404 == 408_403 + 1, (', 'assert WAVE_CONFIGS[179]["b_exit_seed_base"] == 410_604 == 410_603 + 1, (', 1),
    ('"W178 B must be the first-clean window past the own-wave A "', '"W179 B must be the first-clean window past the own-wave A "', 1),
    ('"band tail 408_403+1 (arithmetic continuation "', '"band tail 410_603+1 (arithmetic continuation "', 1),
    ('"406_404..406_603 CLEAN on the registered universe but "', '"408_604..408_803 CLEAN on the registered universe but "', 1),
    ('"lands INSIDE the W178 A band window; same-freeze mutual "', '"lands INSIDE the W179 A band window; same-freeze mutual "', 1),
    ('"own-wave A window reserved jumps to 408_404, first-clean "', '"own-wave A window reserved jumps to 410_604, first-clean "', 1),
    ('arith_b177 = set(range(408_404, 408_604))', 'arith_b178 = set(range(410_604, 410_804))', 1),
    ('assert not (arith_b177 & reg_ints), \\', 'assert not (arith_b178 & reg_ints), \\', 1),
    ('"W178 B window must be CLEAN (first-clean ADMIT face past own-wave A)"', '"W179 B window must be CLEAN (first-clean ADMIT face past own-wave A)"', 1),
    ('assert not (arith_b177 & arith_a177), \\', 'assert not (arith_b178 & arith_a178), \\', 1),
    ('"W178 A/B same-freeze mutual exclusion (B hops past own A)"', '"W179 A/B same-freeze mutual exclusion (B hops past own A)"', 1),
    ('assert _entry_shard_of(0, 12) == ("PERPETUAL-N1-W178-SHARD-0",', 'assert _entry_shard_of(0, 12) == ("PERPETUAL-N1-W179-SHARD-0",', 1),
    ('"n1w178-0of12"), "W178 entry identity"', '"n1w179-0of12"), "W179 entry identity"', 1),
    ('assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W178-SHARD-11",', 'assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W179-SHARD-11",', 1),
    ('"n1w178-11of12")', '"n1w179-11of12")', 1),
    ('assert SHARD_DIR.endswith("n1_w178") and OUT.endswith(', 'assert SHARD_DIR.endswith("n1_w179") and OUT.endswith(', 1),
    ('"n1_w178_results.json"), "W178 path drift"', '"n1_w179_results.json"), "W179 path drift"', 1),
    ('f"W178 shard dir collides with W{wprev}"', 'f"W179 shard dir collides with W{wprev}"', 1),
    ('# W178 finalize cumulative deps: W17..W177 outputs ALL PRESENT', '# W179 finalize cumulative deps: W17..W178 outputs ALL PRESENT', 1),
    ('# (landed net chain head 795,305 = W177 bm-a r844 one-pass --', '# (landed net chain head 797,505 = W178 bm-a r846 one-pass --', 1),
    ('for _depw in range(17, 178):', 'for _depw in range(17, 179):', 1),
    ('f"W178 finalize cumulative dep (W{_depw} output) missing"', 'f"W179 finalize cumulative dep (W{_depw} output) missing"', 1),
    ('# registered wave below 178 composes; wave 15 excluded by', '# registered wave below 179 composes; wave 15 excluded by', 1),
    ('# design; SINGLE STATE (W2..W177 all registered -- no', '# design; SINGLE STATE (W2..W178 all registered -- no', 1),
    ('assert sorted(w for w in WAVE_CONFIGS if w < 178) == \\', 'assert sorted(w for w in WAVE_CONFIGS if w < 179) == \\', 1),
    ('[w for w in range(16, 178)], \\', '[w for w in range(16, 179)], \\', 1),
    ('"W178 prior-wave set must derive from registry keys (no 15; "', '"W179 prior-wave set must derive from registry keys (no 15; "', 1),
    ('"W2..W177 registered single state)"', '"W2..W178 registered single state)"', 1),
    ('PATHS.root, "research", "PERPETUAL_N1_W178_PREREG.md")), \\', 'PATHS.root, "research", "PERPETUAL_N1_W179_PREREG.md")), \\', 1),
    ('"W178 per-wave prereg missing (materializer requirement)"', '"W179 per-wave prereg missing (materializer requirement)"', 1),
]

CL_PAIRS = [
    ('"+ W178 materializer face [same guard set, dep=W17..W177 ', '"+ W179 materializer face [same guard set, dep=W17..W178 ', 1),
    ('"outputs ALL PRESENT (landed net chain head 795,305 = "', '"outputs ALL PRESENT (landed net chain head 797,505 = "', 1),
    ('"W177 bm-a r844 one-pass, K=387,320 merged pool; ZERO "', '"W178 bm-a r846 one-pass, K=389,520 merged pool; ZERO "', 1),
    ('"in-flight upstream seats), ONE HUNDRED-AND-SIXTY-EIGHTH "', '"in-flight upstream seats), ONE HUNDRED-AND-SIXTY-NINTH "', 1),
    ('"ENGINE-OWNED WAVE BY MACHINE-DERIVE (engine_owner rows 167 "', '"ENGINE-OWNED WAVE BY MACHINE-DERIVE (engine_owner rows 168 "', 1),
    ("+ candidate) bm-a's ninety-fourth owned claim per ", "+ candidate) bm-a's ninety-fifth owned claim per ", 1),
    ('"machine-derive (engine_owner==bm-a rows 93 + candidate), "', '"machine-derive (engine_owner==bm-a rows 94 + candidate), "', 1),
    ('"A=FIRST-CLEAN past the registered W177 B band (staircase "', '"A=FIRST-CLEAN past the registered W178 B band (staircase "', 1),
    ('"THIRTY-EIGHTH instance, E36 card, hops=1) + B=FIRST-CLEAN past the "', '"THIRTY-NINTH instance, E36 card, hops=1) + B=FIRST-CLEAN past the "', 1),
    ('"results/_r844bma_w178_probe_receipt.json, law sec.4 W178 row, "', '"results/_r848bma_w179_probe_receipt.json, law sec.4 W179 row, "', 1),
    ('"r845 bm-a] "', '"r849 bm-a] "', 1),
]

PF_NEG = ['    # W178 (bm-a r845 freeze, seat MSG-2026-10-07-2157-bma-w178-seat', 'pushed to origin 5b9284c79 pre-freeze r565 law (r844 pre-seat', '(3-item; the W177 finalize product already on origin since r844,', '# = direct fast-forward behind-0 at fetch (r844 pre-seat', '# push), zero merge, zero --no-verify; self-ack archive ALREADY\r\n    # LANDED pre-freeze -- r845 same-window self-ack move (the W178\r\n    # seat MSG sits in fleet/inbox/processed/ at freeze time, honest\r\n    # archived);', 'band gate ADMIT results/_r844bma_w178_probe_receipt.json: A = FIRST-CLEAN', 'past the registered W177 B band (arithmetic continuation', '406_204..408_203 REFUSED at its own start by the W177 B band', '406_204..406_403, exactly as the W177 seat W178+ projection + r841 probe', '# leg4 + r844 sec8 succession projection notes all anticipated;', 'honest forward walk hops=1 -> 406_404..408_403, non-rotational', '(406_403+1) machine-checkable -- A-hops-prior-B staircase', 'THIRTY-EIGHTH instance, E36 card);', 'continuation 406_404..406_603 CLEAN on the registered universe', 'but lands INSIDE the W178 A band window -- same-freeze mutual', 'own-wave A window reserved jumps to 408_404 -> 408_404..408_603,', 'own-wave A tail+1 (408_403+1) machine-checkable);', 'W178+ projection (gate-derived r844): A first-clean', '408_404..410_403 CLEAN hops=0 / B first-clean 408_604..408_803', 'registered W178 B band 408_404..408_603 will refuse the naive', 'W179 A window; W179 freezer MUST re-derive on the post-W178', 'NOT a re-pick (R250: W178 bands were never assigned).', '178: {"a": (406_404, 408_403), "b_exit": (408_404, 408_603),', '5b9284c79', 'r841 probe', 'r844 sec8', 'r844 pre-seat', '_r844bma', 'MSG-2026-10-07-2157', 'c06cc230f', '795,305', '387,320', 'THIRTY-EIGHTH', 'ONE HUNDRED-AND-SIXTY-EIGHTH']

EN_NEG = ['178: {"batch": "PERPETUAL-N1-W178",', '"prereg": ("research/PERPETUAL_N1_W178_PREREG.md (wave-level frozen "', 'new seed bands only; ONE HUNDRED-AND-SIXTY-EIGHTH ENGINE-OWNED WAVE ', 'BY MACHINE-DERIVE (engine_owner rows 167 + candidate), ', 'number law after the REGISTERED W177 row bm-a r843 freeze ', 'c06cc230f, SINGLE STATE zero seat gap W2..W177 all ', 'registered; W178 finalize landed same-window r827, ledger ', 'head 795,305, merged pool K=387,320; seat published=reserved ', 'MSG-2026-10-07-2157-bma-w178-seat PUSHED to origin 5b9284c79 ', 'probe receipt (3-item; the W177 finalize product already on origin since r844, not re-shipped; W146 precedent); ', 'at fetch (r844 pre-seat push), zero merge, zero ', 'engine_owner=bm-a, wave 177: ', 'A = FIRST-CLEAN past the registered W177 B band (the ', 'arithmetic continuation 406_204..408_203 is REFUSED at its ', 'own start by the W177 B band 406_204..406_403, exactly as ', 'the W177 seat W178+ projection + r841 probe leg4 + r844 sec8 succession ', '406_404..408_403; A base == prior-wave B tail+1 ', 'machine-checkable = A-hops-prior-B staircase THIRTY-EIGHTH ', 'arithmetic continuation 406_404..406_603 is CLEAN on the ', 'registered universe but lands INSIDE the W178 A band ', 'jumps to 408_404, first-clean 408_404..408_603 hops=1, ', 'convergence with the W177 seat W178+ projection + r841 probe leg4 + ', 'r844 sec8 succession projection notes re-derived -- all ', 'MANDATORY notes honored (post-W177 universe re-derive + ', 'results/_r844bma_w178_probe_receipt.json; W179+ projection ', 'per this window gate: A first-clean 408_404..410_403 ', 'CLEAN / B first-clean 408_604..408_803 CLEAN -- naive ', 'W178 B band 408_404..408_603 will refuse the naive ', 'W179 A window; W179 freezer MUST re-derive on the ', 'post-W178 universe AND reserve the own-wave A window ', 'staircase card); W1..W177 finalize ALL LANDED (W177 ', 'finalize one-pass bm-a r844, net chain head 795,305, ', 'merged pool K=387,320) -- ZERO in-flight upstream ', '"a_seed_base": 406_404,        # law sec.4 W178 A: 406_404..408_403 (FIRST-CLEAN past the registered W177 B band; arithmetic 406_204..408_203 REFUSED at own start by the W177 B band; hops=1; A-hops-prior-B staircase THIRTY-EIGHTH instance, E36 card; ordinal convergence per r587: W177 sec5.5 prose anticipated thirty-eighth, r844 receipt machine-read THIRTY-EIGHTH)', '"b_exit_seed_base": 408_404,   # law sec.4 W178 B: 408_404..408_603 (FIRST-CLEAN past the own-wave A window; arithmetic 406_404..406_603 lands inside own-A, same-freeze mutual exclusion W141 precedent; reserved walk hops=1; B base == own-A tail+1)', '"shard_subdir": "n1_w178", "out_name": "n1_w178_results.json",', 'c06cc230f', '5b9284c79', '795,305', '387,320', 'ONE HUNDRED-AND-SIXTY-EIGHTH', 'rows 167', 'r841 probe', '_r844bma', 'MSG-2026-10-07-2157', 'n1w178', 'n1_w178', 'PERPETUAL-N1-W178', 'PERPETUAL_N1_W178', 'THIRTY-EIGHTH', 'bm-a r843 freeze', '408_404, first-clean']

MAT_NEG = ['# --- W178 materializer face (r845 bm-a freeze, own-series law', '#     ninety-fourth owned per machine-derive (engine_owner==bm-a', '#     rows 93 + candidate); wave 177 = first free number after', '#     the REGISTERED W177 row (bm-a r843 freeze c06cc230f) --', '#     SINGLE STATE zero seat gap (W2..W177 all registered). Seat', '#     published=reserved MSG-2026-10-07-2157-bma-w178-seat pushed', '#     to origin 5b9284c79 BEFORE this freeze, r565 law (payload', '#     the W177 finalize product already on origin since r844, not', '#     at fetch (r844 pre-seat push), zero merge, zero', '#     --no-verify; self-ack inbox->processed archive ALREADY LANDED\r\n    #     pre-freeze -- r845 same-window self-ack move (the W178 seat\r\n    #     MSG sits in fleet/inbox/processed/ at freeze time, honest\r\n    #     archived).', '#     ONE HUNDRED-AND-SIXTY-EIGHTH engine wave BY', '#     MACHINE-DERIVE (engine_owner rows 167 + candidate; gate', '#     W1..W177 finalize ALL LANDED (net chain head 795,305,', '#     K=387,320 merged pool; W177 finalize one-pass bm-a r844)', '#     always on. ADMIT receipt results/_r844bma_w178_probe_receipt.json;', '#     banned gate ADMIT 0; not a re-pick (R250: W178 bands were', '    _set_wave(178)', 'assert WAVE_CONFIGS[177]["a_seed_base"] == pf.N1_BANDS[177]["a"][0], \\', '"W178 A band drift vs law mirror"', 'assert WAVE_CONFIGS[177]["b_exit_seed_base"] == \\', 'pf.N1_BANDS[177]["b_exit"][0], "W178 B band drift vs law mirror"', 'assert WAVE_CONFIGS[177].get("engine_owner") == \\', 'pf.N1_BANDS[177].get("engine_owner") == "bm-a", \\', '"W178 engine_owner drift (law mirror parity)"', 'w177_a = {A_SEED_BASE + j for j in range(A_N)}', 'w177_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}', 'assert not (w177_a & w177_b), "W178 A/B band overlap"', 'assert not (w177_a & reg_ints) and not (w177_b & reg_ints), \\', '"W178 hits SEED_REGISTRY"', 'for nm, band in (("A", w177_a), ("B", w177_b)):', 'f"W178 {nm} hits v1"', 'f"W178 {nm} hits W1"', 'f"W178 {nm} hits probe seeds"', '# prior-wave disjointness W2..W177 (single state: all', 'for wprev in sorted(w for w in WAVE_CONFIGS if w < 178):', 'assert not (w177_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j', 'for j in range(A_N)}), f"W178 A hits W{wprev}"', 'assert not (w177_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j', 'for j in range(B_N)}), f"W178 B hits W{wprev}"', 'n3r1_used177 = set(range(70_000, 70_006))', 'assert not (w177_a & n3r1_used177) and not (w177_b & n3r1_used177), \\', '"W178 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"', 'assert not (w177_a & lfc_actual12) and not (w177_b & lfc_actual12), \\', '"W178 bands must clear the lfc actual draw range"', 'assert not (w177_a & options_actual12) and \\', 'not (w177_b & options_actual12), \\', '"W178 bands must clear the options_wave2 actual draw range"', '# band facts (law sec.4 W178 row, r795): A = FIRST-CLEAN past', '# the registered W177 B band (the arithmetic continuation', '# 406_204..408_203 is REFUSED at its own start by the W177', '# B band 406_204..406_403, exactly as the W177 seat W178+ projection +', '# r841 probe leg4 + r844 sec8 succession projection notes', '# 406_404..408_403; A base == prior-wave B tail+1 (406_403+1)', '# machine-checkable -- A-hops-prior-B staircase THIRTY-EIGHTH', '# continuation 406_404..406_603 is CLEAN on the registered', '# universe but lands INSIDE the W178 A band window --', '# 408_404 and lands 408_404..408_603, hops=1, non-rotational', '# (408_403+1) machine-checkable; cross-window convergence', '# with the W177 seat W178+ projection + r841 probe leg4 + r844 sec8', '# honored (post-W177 universe re-derive + own-wave A', '# reservation when deriving B); seat MSG-2150 tail,', 'assert WAVE_CONFIGS[178]["a_seed_base"] == 406_404 == 406_403 + 1, (', '"W178 A must be the first-clean window past the registered "', '"W177 B band tail 406_403+1 (arithmetic continuation "', '"406_204..408_203 REFUSED at its own start by the W177 B "', '"band 406_204..406_403, exactly as the W177 seat W178+ projection + "', '"r841 probe leg4 + r844 sec8 succession projection notes "', '"staircase THIRTY-EIGHTH instance, E36 card)"', 'arith_a177 = set(range(406_404, 408_404))', 'assert not (arith_a177 & reg_ints), \\', '"W178 A window must be CLEAN (first-clean ADMIT face past prior-wave B)"', 'assert WAVE_CONFIGS[178]["b_exit_seed_base"] == 408_404 == 408_403 + 1, (', '"W178 B must be the first-clean window past the own-wave A "', '"band tail 408_403+1 (arithmetic continuation "', '"406_404..406_603 CLEAN on the registered universe but "', '"lands INSIDE the W178 A band window; same-freeze mutual "', '"own-wave A window reserved jumps to 408_404, first-clean "', 'arith_b177 = set(range(408_404, 408_604))', 'assert not (arith_b177 & reg_ints), \\', '"W178 B window must be CLEAN (first-clean ADMIT face past own-wave A)"', 'assert not (arith_b177 & arith_a177), \\', '"W178 A/B same-freeze mutual exclusion (B hops past own A)"', 'assert _entry_shard_of(0, 12) == ("PERPETUAL-N1-W178-SHARD-0",', '"n1w178-0of12"), "W178 entry identity"', 'assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W178-SHARD-11",', '"n1w178-11of12")', 'assert SHARD_DIR.endswith("n1_w178") and OUT.endswith(', '"n1_w178_results.json"), "W178 path drift"', 'f"W178 shard dir collides with W{wprev}"', '# W178 finalize cumulative deps: W17..W177 outputs ALL PRESENT', '# (landed net chain head 795,305 = W177 bm-a r844 one-pass --', 'for _depw in range(17, 178):', 'f"W178 finalize cumulative dep (W{_depw} output) missing"', '# registered wave below 178 composes; wave 15 excluded by', '# design; SINGLE STATE (W2..W177 all registered -- no', 'assert sorted(w for w in WAVE_CONFIGS if w < 178) == \\', '[w for w in range(16, 178)], \\', '"W178 prior-wave set must derive from registry keys (no 15; "', '"W2..W177 registered single state)"', 'PATHS.root, "research", "PERPETUAL_N1_W178_PREREG.md")), \\', '"W178 per-wave prereg missing (materializer requirement)"', 'w177_', 'arith_a177', 'arith_b177', 'n3r1_used177', 'r841 probe', 'r844 pre-seat', 'c06cc230f', 'ONE HUNDRED-AND-SIXTY-EIGHTH', 'ninety-fourth', 'rows 167', 'rows 93 ', 'range(17, 178)', 'range(16, 178)', 'PERPETUAL_N1_W178', 'PERPETUAL-N1-W178', 'MSG-2150', '_r844bma', 'r845 same-window', 'n1w178', 'n1_w178', '795,305', '387,320']

CL_NEG = ['"+ W178 materializer face [same guard set, dep=W17..W177 ', '"outputs ALL PRESENT (landed net chain head 795,305 = "', '"W177 bm-a r844 one-pass, K=387,320 merged pool; ZERO "', '"in-flight upstream seats), ONE HUNDRED-AND-SIXTY-EIGHTH "', '"ENGINE-OWNED WAVE BY MACHINE-DERIVE (engine_owner rows 167 "', "+ candidate) bm-a's ninety-fourth owned claim per ", '"machine-derive (engine_owner==bm-a rows 93 + candidate), "', '"A=FIRST-CLEAN past the registered W177 B band (staircase "', '"THIRTY-EIGHTH instance, E36 card, hops=1) + B=FIRST-CLEAN past the "', '"results/_r844bma_w178_probe_receipt.json, law sec.4 W178 row, "', '"r845 bm-a] "', '795,305', '387,320', 'ONE HUNDRED-AND-SIXTY-EIGHTH', 'ninety-fourth', 'rows 167', 'rows 93 ', 'THIRTY-EIGHTH', '_r844bma', 'r843 bm-a] ']

blk179 = vmap(pfblk, PF_PAIRS, PF_NEG, "pf")
entry179 = IND23 + vmap(entry, EN_PAIRS, EN_NEG, "entry")
mat179 = "    " + vmap(mat, MAT_PAIRS, MAT_NEG, "mat")
claim179 = IND10 + vmap(claim, CL_PAIRS, CL_NEG, "claim")

# ---- apply insertions (in-memory) ---------------------------------------
pfsrc = io.open(PF, encoding="utf-8", newline="").read()
n1src = io.open(N1, encoding="utf-8", newline="").read()

# pf: insert W179 block after the W178 row (last registered), before the
# dict close -- r560 insert-after-last-registered-row + post-anchor gate
seg = EO + NL + "}"
check(pfsrc.count(seg) == 1, "pf row-close segment not unique")
pfnew = pfsrc.replace(seg, EO + NL + blk179 + NL + "}", 1)

# n1 entry: after the W178 entry, before the WAVE_CONFIGS close
seg = EO + NL + IND23 + "}"
check(n1src.count(seg) == 1, "n1 entry-close segment not unique")
n1new = n1src.replace(seg, EO + NL + entry179 + NL + IND23 + "}", 1)

# n1 mat: insert the W179 block before the T-141 s2 lane face header
seg = "    # --- T-141 s2 lane face"
check(n1new.count(seg) == 1, "n1 T-141 mat anchor not unique")
n1new = n1new.replace(seg, mat179 + NL + seg, 1)

# n1 claim: insert the W179 attribution after the W178 claim tail line
# (r581 law: anchor = tail single-line literal + post-anchor guard)
seg = '"r845 bm-a] "' + NL + IND10 + '"+ T-141 s2 "'
check(n1new.count(seg) == 1, "n1 claim anchor not unique")
n1new = n1new.replace(seg, '"r845 bm-a] "' + NL + claim179 + NL + IND10 +
                      '"+ T-141 s2 "', 1)

# ---- gates (r780/r781/r560/r815 lineage) --------------------------------
ast.parse(pfnew)
ast.parse(n1new)
print("AST gate: both files parse OK")

# W179 presence + W178 anti-vanish (r560 law)
checks = [
    (pfnew, '179: {"a": (408_604, 410_603), "b_exit": (410_604, 410_803),', 1),
    (pfnew, '178: {"a": (406_404, 408_403), "b_exit": (408_404, 408_603),', 1),
    (pfnew, "# W179 (bm-a r849 freeze", 1),
    (pfnew, "# W178 (bm-a r845 freeze", 1),
    (n1new, '179: {"batch": "PERPETUAL-N1-W179",', 1),
    (n1new, '178: {"batch": "PERPETUAL-N1-W178",', 1),
    (n1new, "# --- W179 materializer face", 1),
    (n1new, "# --- W178 materializer face", 1),
    (n1new, '"r849 bm-a] "', 1),
    (n1new, '"r845 bm-a] "', 1),
    (n1new, '"a_seed_base": 408_604,', 1),
    (n1new, '"b_exit_seed_base": 410_604,', 1),
    (n1new, "n1_w179", 4),
    (n1new, "PERPETUAL_N1_W179_PREREG.md", 2),
]
for src, needle, cnt in checks:
    got = src.count(needle)
    check(got == cnt, "post-edit needle %r count %d != %d" % (needle[:50], got, cnt))

# W180+ projection prose present in the new W179 blocks (probe leg4
# verbatim; r819 post-edit assert bloodline + r776 fragment-needle law;
# pf header = self-wave W179+ per r845 precedent, n1 fragment = next-wave
# W180+)
check("# W179+ projection (gate-derived r848)" in pfnew,
      "pf W179+ projection head missing")
check('probe_receipt.json; W180+ projection "' in n1new,
      "n1 W180+ projection head fragment missing")
check("# 410_604..412_603 CLEAN hops=0 / B first-clean 410_804..411_003" in pfnew,
      "pf W180p prose missing")
check("W180 A window; W180 freezer MUST re-derive on the post-W179" in pfnew,
      "pf W180 freezer prose missing")
check('"W180 A window; W180 freezer MUST re-derive on the "' in n1new,
      "n1 W180 freezer fragment missing")
check('"W179 B band 410_604..410_803 will refuse the naive "' in n1new,
      "n1 W179-band refuse fragment missing")

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
check('179: {"a": (408_604' not in pf_o2, "write-time: origin pf carries W179")
check('179: {"batch"' not in n1_o2, "write-time: origin n1 carries W179")
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
