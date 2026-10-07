# -*- coding: utf-8 -*-
"""r834 bm-a W176 freeze edits: four insertions (pf N1_BANDS[176] row +
n1 WAVE_CONFIGS[176] entry + n1 W176 materializer block + n1 W176
PASS-claim attribution). DRY flag: --dry = zero-write simulation
(r781 verify-separation law + r811/r822/r826/r830 dry-run precedent:
full stale+prose+AST asserts in memory BEFORE any write).

Bloodline: r819/r822/r826/r830 freeze-edits machinery (r773 pit law
freeze-editor compliance + r776 fragment-needle law + r781
verify-separation law), W176 facts live-registry-driven (built by
_r834bma_w176_freeze_buildgen.py: old sides = the PHYSICAL W175 face
fragments probed to dumps this window, new sides = the S75 W176 fact
map, counts verified pre-emission):
  - pre-seat probe results/_r832bma_w176_probe_receipt.json rc0 ADMIT
    (A 402_004..404_003 staircase THIRTY-SIXTH instance E36 hops=1
    past the registered W175 B band 401_804..402_003; naive
    401_804..403_803 refused at its own start by the W175 B band --
    receipt A_semantics machine-cites 'W175 sec5.5 anticipated 36th'
    (projection and receipt ordinals MATCH, no divergence this wave);
    B 404_004..404_203 own-A mutual exclusion hops=1, naive
    402_004..402_203);
  - face probe results/_r834bma_w176_face_probe_receipt.json rc0 (all
    four W175 faces dumped + needle counts; this TOK is built from the
    PHYSICAL probe-dumped shapes, r776 law);
  - seat MSG-2026-10-07-1630-bma-w176-seat published on origin at
    16a8ea982 (r832 pre-seat push, path-derived TRUE sha per r812
    precedent); r565 law: on origin BEFORE this freeze commit;
    self-ack archive ALREADY LANDED pre-freeze -- r833 same-window
    self-ack move (the seat MSG sits in fleet/inbox/processed/ at
    freeze time, honest archived);
  - per-wave prereg research/PERPETUAL_N1_W176_PREREG.md frozen at
    origin 21534ad82 (r833 build, banned gate ADMIT 0 re-verified at
    freeze this window);
  - W175 freeze registered sha machine-derived = f3fca4055 (git log
    origin/main --grep "W175 FREEZE"); W175 finalize one-pass landed
    r831: ledger head 790,412, merged pool K=382,920
    (n1_w175_results.json machine-read);
  - lineage constants disclosed (r795 precedent, passed through):
    (a) the "wave N-1 = first free number" mat-header label rides the
    vmap verbatim (off-by-one lineage quirk since W165 r795);
    (b) "law sec.4 W176 row, r795" band-facts template stamp keeps
    its r795;
    (c) "single-window derive (r812 merged the gate legs INTO the
    pre-seat probe...)" stays (historical merge citation);
    (d) the bm-a-owned ordinal word rolls ninety-first ->
    ninety-second (rows 91 + candidate = 92nd owned per probe leg0);
    (e) mat parity-chain rows W138..W174 keep their historical stamps
    and tuples; the W175 row (the current registered tail) is APPENDED
    with its frozen values (399_804, 401_803)/(401_804, 402_003).

r773 pit law compliance:
  (1) full string-face inventory empirically probed BEFORE TOK
      (_r834bma_w176_face_probe.py -- four face dumps + needle-count
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
      (r530/r687: fetch + origin carries no W176 registration before
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
probe = json.load(open(r"results\_r832bma_w176_probe_receipt.json",
                       encoding="utf-8"))
check(probe["verdict"] == "ADMIT", "pre-seat probe not ADMIT")
check(probe["bands"] == {"A": "402004_404003", "B": "404004_404203"},
      "probe band shape mismatch")
check(probe["legs"]["leg1"]["A"] == [402004, 404003], "A band mismatch")
check(probe["legs"]["leg1"]["B"] == [404004, 404203], "B band mismatch")
check(probe["legs"]["leg1"]["hops_A"] == 1 and probe["legs"]["leg1"]["hops_B"] == 1,
      "hops mismatch")
check(probe["legs"]["leg0"]["rows"] == 173 and probe["legs"]["leg0"]["tail"] == "W175",
      "leg0 registry tail mismatch")
check(probe["legs"]["leg0"]["ordinal"] == 166 and probe["legs"]["leg0"]["bma_ordinal"] == 92,
      "leg0 ordinal mismatch")
check(probe["legs"]["leg2"]["conflicts"] == 0, "leg2 conflicts nonzero")
check(probe["legs"]["leg3"]["origin_vacancy"] is True, "leg3 origin not vacant")
check(probe["legs"]["leg4"]["W177p_A"] == "404004..406003"
      and probe["legs"]["leg4"]["W177p_B"] == "404204..404403",
      "leg4 W177+ projection mismatch")

# origin anti-collision pre-check (r511 tail-lock / r687 write-time gate)
subprocess.run(["git", "fetch", "origin"], capture_output=True)
pf_o = subprocess.run(["git", "show", "origin/main:" + PF],
                      capture_output=True).stdout.decode("utf-8", "replace")
n1_o = subprocess.run(["git", "show", "origin/main:" + N1],
                      capture_output=True).stdout.decode("utf-8", "replace")
check('176: {"a": (402_004' not in pf_o, "origin pf already carries W176 row")
check("W176 (bm-a r834 freeze" not in pf_o, "origin pf carries W176 block")
check('176: {"batch"' not in n1_o, "origin n1 already carries W176 entry")
check("# --- W176 materializer face" not in n1_o, "origin n1 carries W176 mat")
check('"r834 bm-a] "' not in n1_o, "origin n1 carries W176 claim")

# machine-derived shas (r587 / r812 path-derived precedent)
seat_sha = subprocess.run(
    ["git", "log", "origin/main", "--format=%h", "-n", "1", "--diff-filter=A",
     "--", "fleet/inbox/MSG-2026-10-07-1630-bma-w176-seat.md"],
    capture_output=True).stdout.decode().strip()
check(seat_sha == "16a8ea982", "seat sha path-derived mismatch: " + seat_sha)
check(os.path.exists(os.path.join(
    "fleet", "inbox", "processed", "MSG-2026-10-07-1630-bma-w176-seat.md")),
    "seat MSG not in processed/ at freeze time (self-ack archive)")
w175_freeze_sha = subprocess.run(
    ["git", "log", "origin/main", "--format=%h", "-n", "1", "--grep=W175 FREEZE"],
    capture_output=True).stdout.decode().strip()
check(w175_freeze_sha == "f3fca4055", "W175 freeze sha mismatch: " + w175_freeze_sha)

# ---- live-registry parity pre-check (edit-gate: never edit a drifted file)
sys.path.insert(0, "scripts")
import perpetual_faces as pfmod  # noqa: E402
check(len(pfmod.N1_BANDS) == 173, "live N1_BANDS row count drift: %d" % len(pfmod.N1_BANDS))
check(pfmod.N1_BANDS[175] == {"a": (399_804, 401_803),
                              "b_exit": (401_804, 402_003),
                              "engine_owner": "bm-a"}, "live W175 row drift")
check(176 not in pfmod.N1_BANDS, "live N1_BANDS already has 176")
check(os.path.exists(os.path.join("research", "PERPETUAL_N1_W176_PREREG.md")),
      "W176 per-wave prereg missing (materializer gate)")
prereg_o = subprocess.run(["git", "show", "origin/main:research/PERPETUAL_N1_W176_PREREG.md"],
                          capture_output=True)
check(prereg_o.returncode == 0, "W176 prereg absent on origin")

# ---- physical face dumps (r776 law) -----------------------------------
pfblk = io.open(r"results\_r834bma_w176_probe_pf_block.txt", encoding="utf-8",
                newline="").read()
entry = io.open(r"results\_r834bma_w176_probe_n1_entry.txt", encoding="utf-8",
                newline="").read()
mat = io.open(r"results\_r834bma_w176_probe_n1_mat.txt", encoding="utf-8",
              newline="").read()
claim = io.open(r"results\_r834bma_w176_probe_n1_claim.txt", encoding="utf-8",
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
    ('    # W175 (bm-a r830 freeze, seat MSG-2026-10-07-1434-bma-w175-seat', '    # W176 (bm-a r834 freeze, seat MSG-2026-10-07-1630-bma-w176-seat', 1),
    ('pushed to origin 25c414e95 pre-freeze r565 law (r828 pre-seat', 'pushed to origin 16a8ea982 pre-freeze r565 law (r832 pre-seat', 1),
    ('(3-item; the W174 finalize product already on origin since r827,', '(3-item; the W175 finalize product already on origin since r831,', 1),
    ('# = direct fast-forward behind-0 at fetch (r828 pre-seat', '# = direct fast-forward behind-0 at fetch (r832 pre-seat', 1),
    ('# push), zero merge, zero --no-verify; self-ack archive ALREADY\r\n    # LANDED pre-freeze -- r828 same-window self-ack move (the W175\r\n    # seat MSG sits in fleet/inbox/processed/ at freeze time, honest\r\n    # archived);', '# push), zero merge, zero --no-verify; self-ack archive ALREADY\r\n    # LANDED pre-freeze -- r833 same-window self-ack move (the W176\r\n    # seat MSG sits in fleet/inbox/processed/ at freeze time, honest\r\n    # archived);', 1),
    ('band gate ADMIT results/_r828bma_w175_probe_receipt.json: A = FIRST-CLEAN', 'band gate ADMIT results/_r832bma_w176_probe_receipt.json: A = FIRST-CLEAN', 1),
    ('past the registered W174 B band (arithmetic continuation', 'past the registered W175 B band (arithmetic continuation', 1),
    ('399_604..401_603 REFUSED at its own start by the W174 B band', '401_804..403_803 REFUSED at its own start by the W175 B band', 1),
    ('399_604..399_803, exactly as the W174 seat W175+ projection + r823 probe', '401_804..402_003, exactly as the W175 seat W176+ projection + r828 probe', 1),
    ('# leg4 + r826 sec8 succession projection notes all anticipated;', '# leg4 + r831 sec8 succession projection notes all anticipated;', 1),
    ('honest forward walk hops=1 -> 399_804..401_803, non-rotational', 'honest forward walk hops=1 -> 402_004..404_003, non-rotational', 1),
    ('(399_803+1) machine-checkable -- A-hops-prior-B staircase', '(402_003+1) machine-checkable -- A-hops-prior-B staircase', 1),
    ('THIRTY-FIFTH instance, E36 card);', 'THIRTY-SIXTH instance, E36 card);', 1),
    ('continuation 399_804..400_003 CLEAN on the registered universe', 'continuation 402_004..402_203 CLEAN on the registered universe', 1),
    ('but lands INSIDE the W175 A band window -- same-freeze mutual', 'but lands INSIDE the W176 A band window -- same-freeze mutual', 1),
    ('own-wave A window reserved jumps to 401_804 -> 401_804..402_003,', 'own-wave A window reserved jumps to 404_004 -> 404_004..404_203,', 1),
    ('own-wave A tail+1 (401_803+1) machine-checkable);', 'own-wave A tail+1 (404_003+1) machine-checkable);', 1),
    ('W175+ projection (gate-derived r828): A first-clean', 'W176+ projection (gate-derived r832): A first-clean', 1),
    ('401_804..403_803 CLEAN hops=0 / B first-clean 402_004..402_203', '404_004..406_003 CLEAN hops=0 / B first-clean 404_204..404_403', 1),
    ('registered W175 B band 401_804..402_003 will refuse the naive', 'registered W176 B band 404_004..404_203 will refuse the naive', 1),
    ('W176 A window; W176 freezer MUST re-derive on the post-W175', 'W177 A window; W177 freezer MUST re-derive on the post-W176', 1),
    ('NOT a re-pick (R250: W175 bands were never assigned).', 'NOT a re-pick (R250: W176 bands were never assigned).', 1),
    ('175: {"a": (399_804, 401_803), "b_exit": (401_804, 402_003),', '176: {"a": (402_004, 404_003), "b_exit": (404_004, 404_203),', 1),
]

EN_PAIRS = [
    ('175: {"batch": "PERPETUAL-N1-W175",', '176: {"batch": "PERPETUAL-N1-W176",', 1),
    ('"prereg": ("research/PERPETUAL_N1_W175_PREREG.md (wave-level frozen "', '"prereg": ("research/PERPETUAL_N1_W176_PREREG.md (wave-level frozen "', 1),
    ('new seed bands only; ONE HUNDRED-AND-SIXTY-FIFTH ENGINE-OWNED WAVE ', 'new seed bands only; ONE HUNDRED-AND-SIXTY-SIXTH ENGINE-OWNED WAVE ', 1),
    ('BY MACHINE-DERIVE (engine_owner rows 164 + candidate), ', 'BY MACHINE-DERIVE (engine_owner rows 165 + candidate), ', 1),
    ('number law after the REGISTERED W174 row bm-a r826 freeze ', 'number law after the REGISTERED W175 row bm-a r830 freeze ', 1),
    ('db42a0d46, SINGLE STATE zero seat gap W2..W174 all ', 'f3fca4055, SINGLE STATE zero seat gap W2..W175 all ', 1),
    ('registered; W175 finalize landed same-window r827, ledger ', 'registered; W176 finalize landed same-window r827, ledger ', 1),
    ('head 788,212, merged pool K=380,720; seat published=reserved ', 'head 790,412, merged pool K=382,920; seat published=reserved ', 1),
    ('MSG-2026-10-07-1434-bma-w175-seat PUSHED to origin 25c414e95 ', 'MSG-2026-10-07-1630-bma-w176-seat PUSHED to origin 16a8ea982 ', 1),
    ('probe receipt (3-item; the W174 finalize product already on origin since r827, not re-shipped; W146 precedent); ', 'probe receipt (3-item; the W175 finalize product already on origin since r831, not re-shipped; W146 precedent); ', 1),
    ('at fetch (r828 pre-seat push), zero merge, zero ', 'at fetch (r832 pre-seat push), zero merge, zero ', 1),
    ('engine_owner=bm-a, wave 174: ', 'engine_owner=bm-a, wave 175: ', 1),
    ('A = FIRST-CLEAN past the registered W174 B band (the ', 'A = FIRST-CLEAN past the registered W175 B band (the ', 1),
    ('arithmetic continuation 399_604..401_603 is REFUSED at its ', 'arithmetic continuation 401_804..403_803 is REFUSED at its ', 1),
    ('own start by the W174 B band 399_604..399_803, exactly as ', 'own start by the W175 B band 401_804..402_003, exactly as ', 1),
    ('the W174 seat W175+ projection + r823 probe leg4 + r826 sec8 succession ', 'the W175 seat W176+ projection + r828 probe leg4 + r831 sec8 succession ', 1),
    ('projection notes anticipated; honest forward walk hops=1 -> ', 'projection notes anticipated; honest forward walk hops=1 -> ', 1),
    ('399_804..401_803; A base == prior-wave B tail+1 ', '402_004..404_003; A base == prior-wave B tail+1 ', 1),
    ('machine-checkable = A-hops-prior-B staircase THIRTY-FIFTH ', 'machine-checkable = A-hops-prior-B staircase THIRTY-SIXTH ', 1),
    ('arithmetic continuation 399_804..400_003 is CLEAN on the ', 'arithmetic continuation 402_004..402_203 is CLEAN on the ', 1),
    ('registered universe but lands INSIDE the W175 A band ', 'registered universe but lands INSIDE the W176 A band ', 1),
    ('jumps to 401_804, first-clean 401_804..402_003 hops=1, ', 'jumps to 404_004, first-clean 404_004..404_203 hops=1, ', 1),
    ('convergence with the W174 seat W175+ projection + r823 probe leg4 + ', 'convergence with the W175 seat W176+ projection + r828 probe leg4 + ', 1),
    ('r826 sec8 succession projection notes re-derived -- all ', 'r831 sec8 succession projection notes re-derived -- all ', 1),
    ('MANDATORY notes honored (post-W174 universe re-derive + ', 'MANDATORY notes honored (post-W175 universe re-derive + ', 1),
    ('results/_r828bma_w175_probe_receipt.json; W176+ projection ', 'results/_r832bma_w176_probe_receipt.json; W177+ projection ', 1),
    ('per this window gate: A first-clean 401_804..403_803 ', 'per this window gate: A first-clean 404_004..406_003 ', 1),
    ('CLEAN / B first-clean 402_004..402_203 CLEAN -- naive ', 'CLEAN / B first-clean 404_204..404_403 CLEAN -- naive ', 1),
    ('W175 B band 401_804..402_003 will refuse the naive ', 'W176 B band 404_004..404_203 will refuse the naive ', 1),
    ('W176 A window; W176 freezer MUST re-derive on the ', 'W177 A window; W177 freezer MUST re-derive on the ', 1),
    ('post-W175 universe AND reserve the own-wave A window ', 'post-W176 universe AND reserve the own-wave A window ', 1),
    ('staircase card); W1..W174 finalize ALL LANDED (W174 ', 'staircase card); W1..W175 finalize ALL LANDED (W175 ', 1),
    ('finalize one-pass bm-a r827, net chain head 788,212, ', 'finalize one-pass bm-a r831, net chain head 790,412, ', 1),
    ('merged pool K=380,720) -- ZERO in-flight upstream ', 'merged pool K=382,920) -- ZERO in-flight upstream ', 1),
    ('"a_seed_base": 399_804,        # law sec.4 W175 A: 399_804..401_803 (FIRST-CLEAN past the registered W174 B band; arithmetic 399_604..401_603 REFUSED at own start by the W174 B band; hops=1; A-hops-prior-B staircase THIRTY-FIFTH instance, E36 card; ordinal convergence per r587: W174 sec5.5 prose anticipated thirty-fifth, r828 receipt machine-read THIRTY-FIFTH)', '"a_seed_base": 402_004,        # law sec.4 W176 A: 402_004..404_003 (FIRST-CLEAN past the registered W175 B band; arithmetic 401_804..403_803 REFUSED at own start by the W175 B band; hops=1; A-hops-prior-B staircase THIRTY-SIXTH instance, E36 card; ordinal convergence per r587: W175 sec5.5 prose anticipated thirty-sixth, r832 receipt machine-read THIRTY-SIXTH)', 1),
    ('"b_exit_seed_base": 401_804,   # law sec.4 W175 B: 401_804..402_003 (FIRST-CLEAN past the own-wave A window; arithmetic 399_804..400_003 lands inside own-A, same-freeze mutual exclusion W141 precedent; reserved walk hops=1; B base == own-A tail+1)', '"b_exit_seed_base": 404_004,   # law sec.4 W176 B: 404_004..404_203 (FIRST-CLEAN past the own-wave A window; arithmetic 402_004..402_203 lands inside own-A, same-freeze mutual exclusion W141 precedent; reserved walk hops=1; B base == own-A tail+1)', 1),
    ('"shard_subdir": "n1_w175", "out_name": "n1_w175_results.json",', '"shard_subdir": "n1_w176", "out_name": "n1_w176_results.json",', 1),
]

MAT_PAIRS = [
    ('# --- W175 materializer face (r830 bm-a freeze, own-series law', '# --- W176 materializer face (r834 bm-a freeze, own-series law', 1),
    ('#     ninety-first owned per machine-derive (engine_owner==bm-a', '#     ninety-second owned per machine-derive (engine_owner==bm-a', 1),
    ('#     rows 90 + candidate); wave 174 = first free number after', '#     rows 91 + candidate); wave 175 = first free number after', 1),
    ('#     the REGISTERED W174 row (bm-a r826 freeze db42a0d46) --', '#     the REGISTERED W175 row (bm-a r830 freeze f3fca4055) --', 1),
    ('#     SINGLE STATE zero seat gap (W2..W174 all registered). Seat', '#     SINGLE STATE zero seat gap (W2..W175 all registered). Seat', 1),
    ('#     published=reserved MSG-2026-10-07-1434-bma-w175-seat pushed', '#     published=reserved MSG-2026-10-07-1630-bma-w176-seat pushed', 1),
    ('#     to origin 25c414e95 BEFORE this freeze, r565 law (payload', '#     to origin 16a8ea982 BEFORE this freeze, r565 law (payload', 1),
    ('#     the W174 finalize product already on origin since r827, not', '#     the W175 finalize product already on origin since r831, not', 1),
    ('#     at fetch (r828 pre-seat push), zero merge, zero', '#     at fetch (r832 pre-seat push), zero merge, zero', 1),
    ('#     --no-verify; self-ack inbox->processed archive ALREADY LANDED\r\n    #     pre-freeze -- r828 same-window self-ack move (the W175 seat\r\n    #     MSG sits in fleet/inbox/processed/ at freeze time, honest\r\n    #     archived).', '#     --no-verify; self-ack inbox->processed archive ALREADY LANDED\r\n    #     pre-freeze -- r833 same-window self-ack move (the W176 seat\r\n    #     MSG sits in fleet/inbox/processed/ at freeze time, honest\r\n    #     archived).', 1),
    ('#     ONE HUNDRED-AND-SIXTY-FIFTH engine wave BY', '#     ONE HUNDRED-AND-SIXTY-SIXTH engine wave BY', 1),
    ('#     MACHINE-DERIVE (engine_owner rows 164 + candidate; gate', '#     MACHINE-DERIVE (engine_owner rows 165 + candidate; gate', 1),
    ('#     W1..W174 finalize ALL LANDED (net chain head 788,212,', '#     W1..W175 finalize ALL LANDED (net chain head 790,412,', 1),
    ('#     K=380,720 merged pool; W174 finalize one-pass bm-a r827)', '#     K=382,920 merged pool; W175 finalize one-pass bm-a r831)', 1),
    ('#     always on. ADMIT receipt results/_r828bma_w175_probe_receipt.json;', '#     always on. ADMIT receipt results/_r832bma_w176_probe_receipt.json;', 1),
    ('#     banned gate ADMIT 0; not a re-pick (R250: W175 bands were', '#     banned gate ADMIT 0; not a re-pick (R250: W176 bands were', 1),
    ('    _set_wave(175)', '    _set_wave(176)', 1),
    ('assert WAVE_CONFIGS[174]["a_seed_base"] == pf.N1_BANDS[174]["a"][0], \\', 'assert WAVE_CONFIGS[175]["a_seed_base"] == pf.N1_BANDS[175]["a"][0], \\', 1),
    ('"W175 A band drift vs law mirror"', '"W176 A band drift vs law mirror"', 1),
    ('assert WAVE_CONFIGS[174]["b_exit_seed_base"] == \\', 'assert WAVE_CONFIGS[175]["b_exit_seed_base"] == \\', 1),
    ('pf.N1_BANDS[174]["b_exit"][0], "W175 B band drift vs law mirror"', 'pf.N1_BANDS[175]["b_exit"][0], "W176 B band drift vs law mirror"', 1),
    ('assert WAVE_CONFIGS[174].get("engine_owner") == \\', 'assert WAVE_CONFIGS[175].get("engine_owner") == \\', 1),
    ('pf.N1_BANDS[174].get("engine_owner") == "bm-a", \\', 'pf.N1_BANDS[175].get("engine_owner") == "bm-a", \\', 1),
    ('"W175 engine_owner drift (law mirror parity)"', '"W176 engine_owner drift (law mirror parity)"', 1),
    ('w174_a = {A_SEED_BASE + j for j in range(A_N)}', 'w175_a = {A_SEED_BASE + j for j in range(A_N)}', 1),
    ('w174_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}', 'w175_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}', 1),
    ('assert not (w174_a & w174_b), "W175 A/B band overlap"', 'assert not (w175_a & w175_b), "W176 A/B band overlap"', 1),
    ('assert not (w174_a & reg_ints) and not (w174_b & reg_ints), \\', 'assert not (w175_a & reg_ints) and not (w175_b & reg_ints), \\', 1),
    ('"W175 hits SEED_REGISTRY"', '"W176 hits SEED_REGISTRY"', 1),
    ('for nm, band in (("A", w174_a), ("B", w174_b)):', 'for nm, band in (("A", w175_a), ("B", w175_b)):', 1),
    ('f"W175 {nm} hits v1"', 'f"W176 {nm} hits v1"', 1),
    ('f"W175 {nm} hits W1"', 'f"W176 {nm} hits W1"', 1),
    ('f"W175 {nm} hits probe seeds"', 'f"W176 {nm} hits probe seeds"', 1),
    ('"registered W174 row parity drift (r307; bm-a r826)"', '"registered W174 row parity drift (r307; bm-a r826)"\r\n        assert pf.N1_BANDS[175] == {"a": (399_804, 401_803),\r\n                                    "b_exit": (401_804, 402_003),\r\n                                    "engine_owner": "bm-a"}, \\\r\n            "registered W175 row parity drift (r307; bm-a r830)"', 1),
    ('# prior-wave disjointness W2..W174 (single state: all', '# prior-wave disjointness W2..W175 (single state: all', 1),
    ('for wprev in sorted(w for w in WAVE_CONFIGS if w < 175):', 'for wprev in sorted(w for w in WAVE_CONFIGS if w < 176):', 2),
    ('assert not (w174_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j', 'assert not (w175_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j', 1),
    ('for j in range(A_N)}), f"W175 A hits W{wprev}"', 'for j in range(A_N)}), f"W176 A hits W{wprev}"', 1),
    ('assert not (w174_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j', 'assert not (w175_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j', 1),
    ('for j in range(B_N)}), f"W175 B hits W{wprev}"', 'for j in range(B_N)}), f"W176 B hits W{wprev}"', 1),
    ('n3r1_used174 = set(range(70_000, 70_006))', 'n3r1_used175 = set(range(70_000, 70_006))', 1),
    ('assert not (w174_a & n3r1_used174) and not (w174_b & n3r1_used174), \\', 'assert not (w175_a & n3r1_used175) and not (w175_b & n3r1_used175), \\', 1),
    ('"W175 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"', '"W176 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"', 1),
    ('assert not (w174_a & lfc_actual12) and not (w174_b & lfc_actual12), \\', 'assert not (w175_a & lfc_actual12) and not (w175_b & lfc_actual12), \\', 1),
    ('"W175 bands must clear the lfc actual draw range"', '"W176 bands must clear the lfc actual draw range"', 1),
    ('assert not (w174_a & options_actual12) and \\', 'assert not (w175_a & options_actual12) and \\', 1),
    ('not (w174_b & options_actual12), \\', 'not (w175_b & options_actual12), \\', 1),
    ('"W175 bands must clear the options_wave2 actual draw range"', '"W176 bands must clear the options_wave2 actual draw range"', 1),
    ('# band facts (law sec.4 W175 row, r795): A = FIRST-CLEAN past', '# band facts (law sec.4 W176 row, r795): A = FIRST-CLEAN past', 1),
    ('# the registered W174 B band (the arithmetic continuation', '# the registered W175 B band (the arithmetic continuation', 1),
    ('# 399_604..401_603 is REFUSED at its own start by the W174', '# 401_804..403_803 is REFUSED at its own start by the W175', 1),
    ('# B band 399_604..399_803, exactly as the W174 seat W175+ projection +', '# B band 401_804..402_003, exactly as the W175 seat W176+ projection +', 1),
    ('# r823 probe leg4 + r826 sec8 succession projection notes', '# r828 probe leg4 + r831 sec8 succession projection notes', 1),
    ('# 399_804..401_803; A base == prior-wave B tail+1 (399_803+1)', '# 402_004..404_003; A base == prior-wave B tail+1 (402_003+1)', 1),
    ('# machine-checkable -- A-hops-prior-B staircase THIRTY-FIFTH', '# machine-checkable -- A-hops-prior-B staircase THIRTY-SIXTH', 1),
    ('# continuation 399_804..400_003 is CLEAN on the registered', '# continuation 402_004..402_203 is CLEAN on the registered', 1),
    ('# universe but lands INSIDE the W175 A band window --', '# universe but lands INSIDE the W176 A band window --', 1),
    ('# 401_804 and lands 401_804..402_003, hops=1, non-rotational', '# 404_004 and lands 404_004..404_203, hops=1, non-rotational', 1),
    ('# (401_803+1) machine-checkable; cross-window convergence', '# (404_003+1) machine-checkable; cross-window convergence', 1),
    ('# with the W174 seat W175+ projection + r823 probe leg4 + r826 sec8', '# with the W175 seat W176+ projection + r828 probe leg4 + r831 sec8', 1),
    ('# honored (post-W174 universe re-derive + own-wave A', '# honored (post-W175 universe re-derive + own-wave A', 1),
    ('# reservation when deriving B); seat MSG-1434 tail,', '# reservation when deriving B); seat MSG-1630 tail,', 1),
    ('assert WAVE_CONFIGS[175]["a_seed_base"] == 399_804 == 399_803 + 1, (', 'assert WAVE_CONFIGS[176]["a_seed_base"] == 402_004 == 402_003 + 1, (', 1),
    ('"W175 A must be the first-clean window past the registered "', '"W176 A must be the first-clean window past the registered "', 1),
    ('"W174 B band tail 399_803+1 (arithmetic continuation "', '"W175 B band tail 402_003+1 (arithmetic continuation "', 1),
    ('"399_604..401_603 REFUSED at its own start by the W174 B "', '"401_804..403_803 REFUSED at its own start by the W175 B "', 1),
    ('"band 399_604..399_803, exactly as the W174 seat W175+ projection + "', '"band 401_804..402_003, exactly as the W175 seat W176+ projection + "', 1),
    ('"r823 probe leg4 + r826 sec8 succession projection notes "', '"r828 probe leg4 + r831 sec8 succession projection notes "', 1),
    ('"staircase THIRTY-FIFTH instance, E36 card)"', '"staircase THIRTY-SIXTH instance, E36 card)"', 1),
    ('arith_a174 = set(range(399_804, 401_804))', 'arith_a175 = set(range(402_004, 404_004))', 1),
    ('assert not (arith_a174 & reg_ints), \\', 'assert not (arith_a175 & reg_ints), \\', 1),
    ('"W175 A window must be CLEAN (first-clean ADMIT face past prior-wave B)"', '"W176 A window must be CLEAN (first-clean ADMIT face past prior-wave B)"', 1),
    ('assert WAVE_CONFIGS[175]["b_exit_seed_base"] == 401_804 == 401_803 + 1, (', 'assert WAVE_CONFIGS[176]["b_exit_seed_base"] == 404_004 == 404_003 + 1, (', 1),
    ('"W175 B must be the first-clean window past the own-wave A "', '"W176 B must be the first-clean window past the own-wave A "', 1),
    ('"band tail 401_803+1 (arithmetic continuation "', '"band tail 404_003+1 (arithmetic continuation "', 1),
    ('"399_804..400_003 CLEAN on the registered universe but "', '"402_004..402_203 CLEAN on the registered universe but "', 1),
    ('"lands INSIDE the W175 A band window; same-freeze mutual "', '"lands INSIDE the W176 A band window; same-freeze mutual "', 1),
    ('"own-wave A window reserved jumps to 401_804, first-clean "', '"own-wave A window reserved jumps to 404_004, first-clean "', 1),
    ('arith_b174 = set(range(401_804, 402_004))', 'arith_b175 = set(range(404_004, 404_204))', 1),
    ('assert not (arith_b174 & reg_ints), \\', 'assert not (arith_b175 & reg_ints), \\', 1),
    ('"W175 B window must be CLEAN (first-clean ADMIT face past own-wave A)"', '"W176 B window must be CLEAN (first-clean ADMIT face past own-wave A)"', 1),
    ('assert not (arith_b174 & arith_a174), \\', 'assert not (arith_b175 & arith_a175), \\', 1),
    ('"W175 A/B same-freeze mutual exclusion (B hops past own A)"', '"W176 A/B same-freeze mutual exclusion (B hops past own A)"', 1),
    ('assert _entry_shard_of(0, 12) == ("PERPETUAL-N1-W175-SHARD-0",', 'assert _entry_shard_of(0, 12) == ("PERPETUAL-N1-W176-SHARD-0",', 1),
    ('"n1w175-0of12"), "W175 entry identity"', '"n1w176-0of12"), "W176 entry identity"', 1),
    ('assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W175-SHARD-11",', 'assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W176-SHARD-11",', 1),
    ('"n1w175-11of12")', '"n1w176-11of12")', 1),
    ('assert SHARD_DIR.endswith("n1_w175") and OUT.endswith(', 'assert SHARD_DIR.endswith("n1_w176") and OUT.endswith(', 1),
    ('"n1_w175_results.json"), "W175 path drift"', '"n1_w176_results.json"), "W176 path drift"', 1),
    ('f"W175 shard dir collides with W{wprev}"', 'f"W176 shard dir collides with W{wprev}"', 1),
    ('# W175 finalize cumulative deps: W17..W174 outputs ALL PRESENT', '# W176 finalize cumulative deps: W17..W175 outputs ALL PRESENT', 1),
    ('# (landed net chain head 788,212 = W174 bm-a r827 one-pass --', '# (landed net chain head 790,412 = W175 bm-a r831 one-pass --', 1),
    ('for _depw in range(17, 175):', 'for _depw in range(17, 176):', 1),
    ('f"W175 finalize cumulative dep (W{_depw} output) missing"', 'f"W176 finalize cumulative dep (W{_depw} output) missing"', 1),
    ('# registered wave below 175 composes; wave 15 excluded by', '# registered wave below 176 composes; wave 15 excluded by', 1),
    ('# design; SINGLE STATE (W2..W174 all registered -- no', '# design; SINGLE STATE (W2..W175 all registered -- no', 1),
    ('assert sorted(w for w in WAVE_CONFIGS if w < 175) == \\', 'assert sorted(w for w in WAVE_CONFIGS if w < 176) == \\', 1),
    ('[w for w in range(16, 175)], \\', '[w for w in range(16, 176)], \\', 1),
    ('"W175 prior-wave set must derive from registry keys (no 15; "', '"W176 prior-wave set must derive from registry keys (no 15; "', 1),
    ('"W2..W174 registered single state)"', '"W2..W175 registered single state)"', 1),
    ('PATHS.root, "research", "PERPETUAL_N1_W175_PREREG.md")), \\', 'PATHS.root, "research", "PERPETUAL_N1_W176_PREREG.md")), \\', 1),
    ('"W175 per-wave prereg missing (materializer requirement)"', '"W176 per-wave prereg missing (materializer requirement)"', 1),
]

CL_PAIRS = [
    ('"+ W175 materializer face [same guard set, dep=W17..W174 ', '"+ W176 materializer face [same guard set, dep=W17..W175 ', 1),
    ('"outputs ALL PRESENT (landed net chain head 788,212 = "', '"outputs ALL PRESENT (landed net chain head 790,412 = "', 1),
    ('"W174 bm-a r827 one-pass, K=380,720 merged pool; ZERO "', '"W175 bm-a r831 one-pass, K=382,920 merged pool; ZERO "', 1),
    ('"in-flight upstream seats), ONE HUNDRED-AND-SIXTY-FIFTH "', '"in-flight upstream seats), ONE HUNDRED-AND-SIXTY-SIXTH "', 1),
    ('"ENGINE-OWNED WAVE BY MACHINE-DERIVE (engine_owner rows 164 "', '"ENGINE-OWNED WAVE BY MACHINE-DERIVE (engine_owner rows 165 "', 1),
    ("+ candidate) bm-a's ninety-first owned claim per ", "+ candidate) bm-a's ninety-second owned claim per ", 1),
    ('"machine-derive (engine_owner==bm-a rows 90 + candidate), "', '"machine-derive (engine_owner==bm-a rows 91 + candidate), "', 1),
    ('"A=FIRST-CLEAN past the registered W174 B band (staircase "', '"A=FIRST-CLEAN past the registered W175 B band (staircase "', 1),
    ('"THIRTY-FIFTH instance, E36 card, hops=1) + B=FIRST-CLEAN past the "', '"THIRTY-SIXTH instance, E36 card, hops=1) + B=FIRST-CLEAN past the "', 1),
    ('"results/_r828bma_w175_probe_receipt.json, law sec.4 W175 row, "', '"results/_r832bma_w176_probe_receipt.json, law sec.4 W176 row, "', 1),
    ('"r830 bm-a] "', '"r834 bm-a] "', 1),
]

PF_NEG = ['25c414e95', 'r823 probe', 'r826 sec8', 'r828 pre-seat', '_r828bma', 'MSG-2026-10-07-1434', 'r828 same-window', '399_604..401_603', '399_804..400_003', '399_804..401_803', '399_604..399_803', '399_803+1', 'W174', 'W175 (bm-a', 'INSIDE the W175', 'THIRTY-FIFTH', 'W175+ projection (', 'R250: W175', 'W175 bands were', '788,212', '380,720', 'the W175 seat MSG sits in', 'since r827,', 'r830 freeze']

EN_NEG = ['25c414e95', 'db42a0d46', '788,212', '380,720', 'SIXTY-FIFTH', 'rows 164', 'r823 probe', '_r828bma', 'r828 pre-seat', 'r826 sec8', 'MSG-2026-10-07-1434', 'n1_w175', 'n1w175', 'PERPETUAL-N1-W175', 'PERPETUAL_N1_W175', 'W174 finalize', 'thirty-fifth', 'THIRTY-FIFTH', 'bm-a r826 freeze', 'wave 174: ', 'W175 A band', 'INSIDE the W175', 'W174+ projection', '399_604', '401_804, first-clean', 'W1..W174', 'W174 B band', 'R250']

MAT_NEG = ['w174_', 'arith_a174', 'arith_b174', 'n3r1_used174', 'r823 probe', 'r826 sec8', 'r828 pre-seat', '25c414e95', 'db42a0d46', 'SIXTY-FIFTH', 'ninety-first', 'rows 164', 'rows 90 ', 'range(17, 175)', 'range(16, 175)', 'W1..W174', 'wave 174 =', 'PERPETUAL_N1_W175', 'PERPETUAL-N1-W175', 'MSG-1434', '_r828bma', 'the W175 seat MSG sits in', 'r828 same-window', 'W175 materializer', 'INSIDE the W175', 'THIRTY-FIFTH', 'W175 bands', 'W175 A band', 'W175 A window', 'W175 B window', 'W175 A/B', 'W175 hits', 'W175 entry identity', 'W175 path drift', 'W175 shard dir', 'W175 finalize cumulative', 'W175 prior-wave', 'W175 per-wave', 'W175 engine_owner drift', 'W175 A band drift', 'W175 B band drift', 'the W174 seat', 'W174 B band', 'W174 finalize', 'bm-a r826 freeze', 'post-W174', 'seat MSG-1434', 'n1w175', 'n1_w175', '788,212', '380,720']

CL_NEG = ['W175 materializer', '788,212', '380,720', 'SIXTY-FIFTH', 'ninety-first', 'rows 164', 'rows 90 ', 'THIRTY-FIFTH', 'W174 B band', '_r828bma', 'W175 row,', 'r830 bm-a] ']

blk176 = vmap(pfblk, PF_PAIRS, PF_NEG, "pf")
entry176 = IND23 + vmap(entry, EN_PAIRS, EN_NEG, "entry")
mat176 = "    " + vmap(mat, MAT_PAIRS, MAT_NEG, "mat")
claim176 = IND10 + vmap(claim, CL_PAIRS, CL_NEG, "claim")

# ---- apply insertions (in-memory) ---------------------------------------
pfsrc = io.open(PF, encoding="utf-8", newline="").read()
n1src = io.open(N1, encoding="utf-8", newline="").read()

# pf: insert W176 block after the W175 row (last registered), before the
# dict close -- r560 insert-after-last-registered-row + post-anchor gate
seg = EO + NL + "}"
check(pfsrc.count(seg) == 1, "pf row-close segment not unique")
pfnew = pfsrc.replace(seg, EO + NL + blk176 + NL + "}", 1)

# n1 entry: after the W175 entry, before the WAVE_CONFIGS close
seg = EO + NL + IND23 + "}"
check(n1src.count(seg) == 1, "n1 entry-close segment not unique")
n1new = n1src.replace(seg, EO + NL + entry176 + NL + IND23 + "}", 1)

# n1 mat: insert the W176 block before the T-141 s2 lane face header
seg = "    # --- T-141 s2 lane face"
check(n1new.count(seg) == 1, "n1 T-141 mat anchor not unique")
n1new = n1new.replace(seg, mat176 + NL + seg, 1)

# n1 claim: insert the W176 attribution after the W175 claim tail line
# (r581 law: anchor = tail single-line literal + post-anchor guard)
seg = '"r830 bm-a] "' + NL + IND10 + '"+ T-141 s2 "'
check(n1new.count(seg) == 1, "n1 claim anchor not unique")
n1new = n1new.replace(seg, '"r830 bm-a] "' + NL + claim176 + NL + IND10 +
                      '"+ T-141 s2 "', 1)

# ---- gates (r780/r781/r560/r815 lineage) --------------------------------
ast.parse(pfnew)
ast.parse(n1new)
print("AST gate: both files parse OK")

# W176 presence + W175 anti-vanish (r560 law)
checks = [
    (pfnew, '176: {"a": (402_004, 404_003), "b_exit": (404_004, 404_203),', 1),
    (pfnew, '175: {"a": (399_804, 401_803), "b_exit": (401_804, 402_003),', 1),
    (pfnew, "# W176 (bm-a r834 freeze", 1),
    (pfnew, "# W175 (bm-a r830 freeze", 1),
    (n1new, '176: {"batch": "PERPETUAL-N1-W176",', 1),
    (n1new, '175: {"batch": "PERPETUAL-N1-W175",', 1),
    (n1new, "# --- W176 materializer face", 1),
    (n1new, "# --- W175 materializer face", 1),
    (n1new, '"r834 bm-a] "', 1),
    (n1new, '"r830 bm-a] "', 1),
    (n1new, '"a_seed_base": 402_004,', 1),
    (n1new, '"b_exit_seed_base": 404_004,', 1),
    (n1new, "n1_w176", 4),
    (n1new, "PERPETUAL_N1_W176_PREREG.md", 2),
]
for src, needle, cnt in checks:
    got = src.count(needle)
    check(got == cnt, "post-edit needle %r count %d != %d" % (needle[:50], got, cnt))

# W177 projection prose present in the new W176 blocks (probe leg4
# verbatim; r819 post-edit assert bloodline + r776 fragment-needle law)
check("# W176+ projection (gate-derived r832)" in pfnew,
      "pf W176+ projection head missing")
check('probe_receipt.json; W177+ projection "' in n1new,
      "n1 W177+ projection head fragment missing")
check("# 404_004..406_003 CLEAN hops=0 / B first-clean 404_204..404_403" in pfnew,
      "pf W177p prose missing")
check("W177 A window; W177 freezer MUST re-derive on the post-W176" in pfnew,
      "pf W177 freezer prose missing")
check('"W177 A window; W177 freezer MUST re-derive on the "' in n1new,
      "n1 W177 freezer fragment missing")
check('"W176 B band 404_004..404_203 will refuse the naive "' in n1new,
      "n1 W176-band refuse fragment missing")

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
check('176: {"a": (402_004' not in pf_o2, "write-time: origin pf carries W176")
check('176: {"batch"' not in n1_o2, "write-time: origin n1 carries W176")
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
