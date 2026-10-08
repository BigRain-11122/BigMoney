# -*- coding: utf-8 -*-
"""r885 bm-a W187 freeze edits: four insertions (pf N1_BANDS[187] row +
n1 WAVE_CONFIGS[187] entry + n1 W187 materializer block + n1 W187
PASS-claim attribution). DRY flag: --dry = zero-write simulation
(r781 verify-separation law + r811/r822/r826/r830/r834/r843/r845/r849/
r852/r863/r867/r869/r874/r878/r882 dry-run precedent: full stale+prose+AST
asserts in memory BEFORE any write).

Bloodline: r819/r822/r826/r830/r834/r843/r845/r849/r852/r863/r867/r869/
r874/r878/r882 freeze-edits machinery (r773 pit law freeze-editor compliance +
r776 fragment-needle law + r781 verify-separation law), W187 facts
live-registry-driven (built by _r885bma_w187_freeze_buildgen.py: old
sides = the PHYSICAL W186 face fragments probed to dumps this window,
new sides = the S86 W187 fact map, counts verified pre-emission):
  - pre-seat probe results/_r885bma_w187_probe_receipt.json rc0 ADMIT
    (naive A 426_004..428_003 refused at its own start by the
    registered W186 B band 426_004..426_203; honest forward walk
    1 hop lands A 426_204..428_203 staircase FORTY-SEVENTH instance
    E36 -- receipt A_semantics machine-cites r880 W186 probe leg4 +
    W186 seat MSG leg4 + W186 prereg sec5.5 succession notes anticipated +
    MANDATED this re-derive (projection and receipt ordinals MATCH,
    no divergence this wave); B 428_204..428_403 own-A mutual
    exclusion hops=1, naive 426_204..426_403);
  - face probe results/_r885bma_w187_probe_stage1.json rc0 (all four
    W186 faces dumped; this TOK is built from the PHYSICAL probe-dumped
    shapes, r776 law);
  - seat MSG-2026-10-08-1626-bma-w187-seat published on origin at
    d176af598 (r885 pre-seat push, path-derived TRUE sha per r812
    precedent); r565 law: on origin BEFORE this freeze commit;
    self-ack archive ALREADY LANDED pre-freeze -- bm-a r885-window
    self-ack move (fff58bba7+f3be51e80, same-machine consume; the W187
    seat MSG sits in fleet/inbox/processed/ at freeze time,
    live-verified);
  - per-wave prereg research/PERPETUAL_N1_W187_PREREG.md built r885
    (buildgen r881-bloodline; banned gate ADMIT 0 verified at
    prereg build; frozen+pushed 8bd37a6b6 r885; on origin, verified
    live below);
  - W186 freeze registered sha machine-derived = 14177b161 (git log
    origin/main --grep "W186 FREEZE"); W186 finalize landed r884
    one-pass same-chain: ledger head 816,528, merged pool K=407,120
    (n1_w186_results.json machine-read); W186 sec7/sec8 settle
    backfill landed the r885 SAME window as this freeze (this
    window, first-leg next-window note);
  - lineage constants disclosed (r795/r845/r849/r852/r863/r867/r869/
    r874/r878/r882 precedent, passed through): (a) the "wave N-1 =
    first free number" mat-header label rolls forward with its
    off-by-one quirk (since W165 r795); (b) "law sec.4 W187 row,
    r795" band-facts template stamp keeps its r795; (c) "single-window
    derive (r812 merged the gate legs INTO the pre-seat probe...)"
    stays (historical merge citation); (d) the bm-a-owned ordinal word
    rolls one-hundred-second -> one-hundred-third (rows 102 +
    candidate = 103rd owned per probe leg0, machine-chosen word form,
    disclosed); (e) mat parity-chain rows W138..W185 keep their
    historical stamps and tuples; the W186 row (the current
    registered tail) is APPENDED with its frozen values
    (424_004, 426_003)/(426_004, 426_203); (f) the "W186 finalize
    landed same-window r827" citation rolls its wave-word with the
    stale r827 session stamp riding (off-by-one wave-word +
    stale-session lineage quirk inherited; head/K values roll
    machine-correct to 816,528/407,120 this window); (g) the sec8
    succession-notes window citation rolls r879 -> r885 回填窗
    (the W186 sec8 notes landed the r885 backfill window, honest
    next-window form replaces "same-window" this generation,
    disclosed).

r773 pit law compliance:
  (1) full string-face inventory empirically probed BEFORE TOK
      (_r885bma_w187_face_probe.py -- four face dumps + stage-1
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
      (r530/r687: fetch + origin carries no W187 registration before
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
probe = json.load(open(r"results\_r885bma_w187_probe_receipt.json",
                       encoding="utf-8"))
check(probe["verdict"] == "ADMIT", "pre-seat probe not ADMIT")
check(probe["bands"] == {"A": "426204_428203", "B": "428204_428403"},
      "probe band shape mismatch")
check(probe["legs"]["leg1"]["A"] == [426204, 428203], "A band mismatch")
check(probe["legs"]["leg1"]["B"] == [428204, 428403], "B band mismatch")
check(probe["legs"]["leg1"]["hops_A"] == 1 and probe["legs"]["leg1"]["hops_B"] == 1,
      "hops mismatch")
check(probe["legs"]["leg0"]["rows"] == 184 and probe["legs"]["leg0"]["tail"] == "W186",
      "leg0 registry tail mismatch")
check(probe["legs"]["leg0"]["ordinal"] == 177 and probe["legs"]["leg0"]["bma_ordinal"] == 103,
      "leg0 ordinal mismatch")
check(probe["legs"]["leg2"]["conflicts"] == 0, "leg2 conflicts nonzero")
check(probe["legs"]["leg3"]["origin_vacancy"] is True, "leg3 origin not vacant")
check(probe["legs"]["leg4"]["W188p_A"] == "428204..430203"
      and probe["legs"]["leg4"]["W188p_B"] == "428404..428603",
      "leg4 W188+ projection mismatch")

# origin anti-collision pre-check (r511 tail-lock / r687 write-time gate)
subprocess.run(["git", "fetch", "origin"], capture_output=True)
pf_o = subprocess.run(["git", "show", "origin/main:" + PF],
                      capture_output=True).stdout.decode("utf-8", "replace")
n1_o = subprocess.run(["git", "show", "origin/main:" + N1],
                      capture_output=True).stdout.decode("utf-8", "replace")
check('187: {"a": (426_204' not in pf_o, "origin pf already carries W187 row")
check("W187 (bm-a r885 freeze" not in pf_o, "origin pf carries W187 block")
check('187: {"batch"' not in n1_o, "origin n1 already carries W187 entry")
check("# --- W187 materializer face" not in n1_o, "origin n1 carries W187 mat")
check('"r885 bm-a] "' not in n1_o, "origin n1 carries W187 claim")

# machine-derived shas (r587 / r812 path-derived precedent)
seat_sha = subprocess.run(
    ["git", "log", "origin/main", "--format=%h", "-n", "1", "--diff-filter=A",
     "--", "fleet/inbox/MSG-2026-10-08-1626-bma-w187-seat.md"],
    capture_output=True).stdout.decode().strip()
check(seat_sha == "d176af598", "seat sha path-derived mismatch: " + seat_sha)
check(os.path.exists(os.path.join(
    "fleet", "inbox", "processed", "MSG-2026-10-08-1626-bma-w187-seat.md")),
    "seat MSG not in processed/ at freeze time (self-ack archive)")
w186_freeze_sha = subprocess.run(
    ["git", "log", "origin/main", "--format=%h", "-n", "1", "--grep=W186 FREEZE"],
    capture_output=True).stdout.decode().strip()
check(w186_freeze_sha == "14177b161", "W186 freeze sha mismatch: " + w186_freeze_sha)

# ---- live-registry parity pre-check (edit-gate: never edit a drifted file)
sys.path.insert(0, "scripts")
import perpetual_faces as pfmod  # noqa: E402
check(len(pfmod.N1_BANDS) == 184, "live N1_BANDS row count drift: %d" % len(pfmod.N1_BANDS))
check(pfmod.N1_BANDS[186] == {"a": (424_004, 426_003),
                              "b_exit": (426_004, 426_203),
                              "engine_owner": "bm-a"}, "live W186 row drift")
check(187 not in pfmod.N1_BANDS, "live N1_BANDS already has 187")
check(os.path.exists(os.path.join("research", "PERPETUAL_N1_W187_PREREG.md")),
      "W187 per-wave prereg missing (materializer gate)")
prereg_o = subprocess.run(["git", "show", "origin/main:research/PERPETUAL_N1_W187_PREREG.md"],
                          capture_output=True)
check(prereg_o.returncode == 0, "W187 prereg absent on origin")

# ---- physical face dumps (r776 law) -----------------------------------
pfblk = io.open(r"results\_r885bma_w187_probe_pf_block.txt", encoding="utf-8",
                newline="").read()
entry = io.open(r"results\_r885bma_w187_probe_n1_entry.txt", encoding="utf-8",
                newline="").read()
mat = io.open(r"results\_r885bma_w187_probe_n1_mat.txt", encoding="utf-8",
              newline="").read()
claim = io.open(r"results\_r885bma_w187_probe_n1_claim.txt", encoding="utf-8",
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
    ('    # W186 (bm-a r882 freeze, seat MSG-2026-10-08-1354-bma-w186-seat', '    # W187 (bm-a r885 freeze, seat MSG-2026-10-08-1626-bma-w187-seat', 1),
    ('pushed to origin dd362c690 pre-freeze r565 law (r880 pre-seat', 'pushed to origin d176af598 pre-freeze r565 law (r885 pre-seat', 1),
    ('(3-item; the W185 finalize product already on origin since r879,', '(3-item; the W186 finalize product already on origin since r884,', 1),
    ('# = direct fast-forward behind-0 at fetch (r880 pre-seat', '# = direct fast-forward behind-0 at fetch (r885 pre-seat', 1),
    ('# push), zero merge, zero --no-verify; self-ack archive ALREADY\r\n    # LANDED pre-freeze -- bm-a r880-window self-ack move (the W186\r\n    # seat MSG sits in fleet/inbox/processed/ at freeze time, honest\r\n    # archived);', '# push), zero merge, zero --no-verify; self-ack archive ALREADY\r\n    # LANDED pre-freeze -- bm-a r885-window self-ack move (the W187\r\n    # seat MSG sits in fleet/inbox/processed/ at freeze time, honest\r\n    # archived);', 1),
    ('band gate ADMIT results/_r880bma_w186_probe_receipt.json: A = FIRST-CLEAN', 'band gate ADMIT results/_r885bma_w187_probe_receipt.json: A = FIRST-CLEAN', 1),
    ('past the registered W185 B band (arithmetic continuation', 'past the registered W186 B band (arithmetic continuation', 1),
    ('423_804..425_803 REFUSED at its own start by the W185 B band', '426_004..428_003 REFUSED at its own start by the W186 B band', 1),
    ('423_804..424_003, exactly as the W185 seat W186+ projection + r875 probe', '426_004..426_203, exactly as the W186 seat W187+ projection + r880 probe', 1),
    ('# leg4 + r879 sec8 same-window succession projection notes all anticipated;', '# leg4 + r885 sec8 回填窗 succession projection notes all anticipated;', 1),
    ('honest forward walk hops=1 -> 424_004..426_003, non-rotational', 'honest forward walk hops=1 -> 426_204..428_203, non-rotational', 1),
    ('(424_003+1) machine-checkable -- A-hops-prior-B staircase', '(426_203+1) machine-checkable -- A-hops-prior-B staircase', 1),
    ('FORTY-SIXTH instance, E36 card);', 'FORTY-SEVENTH instance, E36 card);', 1),
    ('continuation 424_004..424_203 CLEAN on the registered universe', 'continuation 426_204..426_403 CLEAN on the registered universe', 1),
    ('but lands INSIDE the W186 A band window -- same-freeze mutual', 'but lands INSIDE the W187 A band window -- same-freeze mutual', 1),
    ('own-wave A window reserved jumps to 426_004 -> 426_004..426_203,', 'own-wave A window reserved jumps to 428_204 -> 428_204..428_403,', 1),
    ('own-wave A tail+1 (426_003+1) machine-checkable);', 'own-wave A tail+1 (428_203+1) machine-checkable);', 1),
    ('W186+ projection (gate-derived r880): A first-clean', 'W187+ projection (gate-derived r885): A first-clean', 1),
    ('426_004..428_003 CLEAN hops=0 / B first-clean 426_204..426_403', '428_204..430_203 CLEAN hops=0 / B first-clean 428_404..428_603', 1),
    ('registered W186 B band 426_004..426_203 will refuse the naive', 'registered W187 B band 428_204..428_403 will refuse the naive', 1),
    ('W187 A window; W187 freezer MUST re-derive on the post-W186', 'W188 A window; W188 freezer MUST re-derive on the post-W187', 1),
    ('NOT a re-pick (R250: W186 bands were never assigned).', 'NOT a re-pick (R250: W187 bands were never assigned).', 1),
    ('186: {"a": (424_004, 426_003), "b_exit": (426_004, 426_203),', '187: {"a": (426_204, 428_203), "b_exit": (428_204, 428_403),', 1),
]

EN_PAIRS = [
    ('186: {"batch": "PERPETUAL-N1-W186",', '187: {"batch": "PERPETUAL-N1-W187",', 1),
    ('"prereg": ("research/PERPETUAL_N1_W186_PREREG.md (wave-level frozen "', '"prereg": ("research/PERPETUAL_N1_W187_PREREG.md (wave-level frozen "', 1),
    ('new seed bands only; ONE HUNDRED-AND-SEVENTY-SIXTH ENGINE-OWNED WAVE ', 'new seed bands only; ONE HUNDRED-AND-SEVENTY-SEVENTH ENGINE-OWNED WAVE ', 1),
    ('BY MACHINE-DERIVE (engine_owner rows 175 + candidate), ', 'BY MACHINE-DERIVE (engine_owner rows 176 + candidate), ', 1),
    ('number law after the REGISTERED W185 row bm-a r878 freeze ', 'number law after the REGISTERED W186 row bm-a r882 freeze ', 1),
    ('beb4b5abd, SINGLE STATE zero seat gap W2..W185 all ', '14177b161, SINGLE STATE zero seat gap W2..W186 all ', 1),
    ('registered; W186 finalize landed same-window r827, ledger ', 'registered; W187 finalize landed same-window r827, ledger ', 1),
    ('head 814,328, merged pool K=404,920; seat published=reserved ', 'head 816,528, merged pool K=407,120; seat published=reserved ', 1),
    ('MSG-2026-10-08-1354-bma-w186-seat PUSHED to origin dd362c690 ', 'MSG-2026-10-08-1626-bma-w187-seat PUSHED to origin d176af598 ', 1),
    ('probe receipt (3-item; the W185 finalize product already on origin since r879, not re-shipped; W146 precedent); ', 'probe receipt (3-item; the W186 finalize product already on origin since r884, not re-shipped; W146 precedent); ', 1),
    ('at fetch (r880 pre-seat push), zero merge, zero ', 'at fetch (r885 pre-seat push), zero merge, zero ', 1),
    ('engine_owner=bm-a, wave 185: ', 'engine_owner=bm-a, wave 186: ', 1),
    ('A = FIRST-CLEAN past the registered W185 B band (the ', 'A = FIRST-CLEAN past the registered W186 B band (the ', 1),
    ('arithmetic continuation 423_804..425_803 is REFUSED at its ', 'arithmetic continuation 426_004..428_003 is REFUSED at its ', 1),
    ('own start by the W185 B band 423_804..424_003, exactly as ', 'own start by the W186 B band 426_004..426_203, exactly as ', 1),
    ('the W185 seat W186+ projection + r875 probe leg4 + r879 sec8 same-window succession ', 'the W186 seat W187+ projection + r880 probe leg4 + r885 sec8 回填窗 succession ', 1),
    ('projection notes anticipated; honest forward walk hops=1 -> ', 'projection notes anticipated; honest forward walk hops=1 -> ', 1),
    ('424_004..426_003; A base == prior-wave B tail+1 ', '426_204..428_203; A base == prior-wave B tail+1 ', 1),
    ('machine-checkable = A-hops-prior-B staircase FORTY-SIXTH ', 'machine-checkable = A-hops-prior-B staircase FORTY-SEVENTH ', 1),
    ('arithmetic continuation 424_004..424_203 is CLEAN on the ', 'arithmetic continuation 426_204..426_403 is CLEAN on the ', 1),
    ('registered universe but lands INSIDE the W186 A band ', 'registered universe but lands INSIDE the W187 A band ', 1),
    ('jumps to 426_004, first-clean 426_004..426_203 hops=1, ', 'jumps to 428_204, first-clean 428_204..428_403 hops=1, ', 1),
    ('convergence with the W185 seat W186+ projection + r875 probe leg4 + ', 'convergence with the W186 seat W187+ projection + r880 probe leg4 + ', 1),
    ('r879 sec8 same-window succession projection notes re-derived -- all ', 'r885 sec8 回填窗 succession projection notes re-derived -- all ', 1),
    ('MANDATORY notes honored (post-W185 universe re-derive + ', 'MANDATORY notes honored (post-W186 universe re-derive + ', 1),
    ('results/_r880bma_w186_probe_receipt.json; W187+ projection ', 'results/_r885bma_w187_probe_receipt.json; W188+ projection ', 1),
    ('per this window gate: A first-clean 426_004..428_003 ', 'per this window gate: A first-clean 428_204..430_203 ', 1),
    ('CLEAN / B first-clean 426_204..426_403 CLEAN -- naive ', 'CLEAN / B first-clean 428_404..428_603 CLEAN -- naive ', 1),
    ('W186 B band 426_004..426_203 will refuse the naive ', 'W187 B band 428_204..428_403 will refuse the naive ', 1),
    ('W187 A window; W187 freezer MUST re-derive on the ', 'W188 A window; W188 freezer MUST re-derive on the ', 1),
    ('post-W186 universe AND reserve the own-wave A window ', 'post-W187 universe AND reserve the own-wave A window ', 1),
    ('staircase card); W1..W185 finalize ALL LANDED (W185 ', 'staircase card); W1..W186 finalize ALL LANDED (W186 ', 1),
    ('finalize one-pass bm-a r879, net chain head 814,328, ', 'finalize one-pass bm-a r884, net chain head 816,528, ', 1),
    ('merged pool K=404,920) -- ZERO in-flight upstream ', 'merged pool K=407,120) -- ZERO in-flight upstream ', 1),
    ('"a_seed_base": 424_004,        # law sec.4 W186 A: 424_004..426_003 (FIRST-CLEAN past the registered W185 B band; arithmetic 423_804..425_803 REFUSED at own start by the W185 B band; hops=1; A-hops-prior-B staircase FORTY-SIXTH instance, E36 card; ordinal convergence per r587: W185 sec5.5 prose anticipated forty-sixth, r880 receipt machine-read FORTY-SIXTH)', '"a_seed_base": 426_204,        # law sec.4 W187 A: 426_204..428_203 (FIRST-CLEAN past the registered W186 B band; arithmetic 426_004..428_003 REFUSED at own start by the W186 B band; hops=1; A-hops-prior-B staircase FORTY-SEVENTH instance, E36 card; ordinal convergence per r587: W186 sec5.5 prose anticipated forty-seventh, r885 receipt machine-read FORTY-SEVENTH)', 1),
    ('"b_exit_seed_base": 426_004,   # law sec.4 W186 B: 426_004..426_203 (FIRST-CLEAN past the own-wave A window; arithmetic 424_004..424_203 lands inside own-A, same-freeze mutual exclusion W141 precedent; reserved walk hops=1; B base == own-A tail+1)', '"b_exit_seed_base": 428_204,   # law sec.4 W187 B: 428_204..428_403 (FIRST-CLEAN past the own-wave A window; arithmetic 426_204..426_403 lands inside own-A, same-freeze mutual exclusion W141 precedent; reserved walk hops=1; B base == own-A tail+1)', 1),
    ('"shard_subdir": "n1_w186", "out_name": "n1_w186_results.json",', '"shard_subdir": "n1_w187", "out_name": "n1_w187_results.json",', 1),
]

MAT_PAIRS = [
    ('# --- W186 materializer face (r882 bm-a freeze, own-series law', '# --- W187 materializer face (r885 bm-a freeze, own-series law', 1),
    ('#     one-hundred-second owned per machine-derive (engine_owner==bm-a', '#     one-hundred-third owned per machine-derive (engine_owner==bm-a', 1),
    ('#     rows 101 + candidate); wave 185 = first free number after', '#     rows 102 + candidate); wave 186 = first free number after', 1),
    ('#     the REGISTERED W185 row (bm-a r878 freeze beb4b5abd) --', '#     the REGISTERED W186 row (bm-a r882 freeze 14177b161) --', 1),
    ('#     SINGLE STATE zero seat gap (W2..W185 all registered). Seat', '#     SINGLE STATE zero seat gap (W2..W186 all registered). Seat', 1),
    ('#     published=reserved MSG-2026-10-08-1354-bma-w186-seat pushed', '#     published=reserved MSG-2026-10-08-1626-bma-w187-seat pushed', 1),
    ('#     to origin dd362c690 BEFORE this freeze, r565 law (payload', '#     to origin d176af598 BEFORE this freeze, r565 law (payload', 1),
    ('#     the W185 finalize product already on origin since r879, not', '#     the W186 finalize product already on origin since r884, not', 1),
    ('#     at fetch (r880 pre-seat push), zero merge, zero', '#     at fetch (r885 pre-seat push), zero merge, zero', 1),
    ('#     --no-verify; self-ack inbox->processed archive ALREADY LANDED\r\n    #     pre-freeze -- bm-a r880-window self-ack move (the W186 seat\r\n    #     MSG sits in fleet/inbox/processed/ at freeze time, honest\r\n    #     archived).', '#     --no-verify; self-ack inbox->processed archive ALREADY LANDED\r\n    #     pre-freeze -- bm-a r885-window self-ack move (the W187 seat\r\n    #     MSG sits in fleet/inbox/processed/ at freeze time, honest\r\n    #     archived).', 1),
    ('#     ONE HUNDRED-AND-SEVENTY-SIXTH engine wave BY', '#     ONE HUNDRED-AND-SEVENTY-SEVENTH engine wave BY', 1),
    ('#     MACHINE-DERIVE (engine_owner rows 175 + candidate; gate', '#     MACHINE-DERIVE (engine_owner rows 176 + candidate; gate', 1),
    ('#     W1..W185 finalize ALL LANDED (net chain head 814,328,', '#     W1..W186 finalize ALL LANDED (net chain head 816,528,', 1),
    ('#     K=404,920 merged pool; W185 finalize one-pass bm-a r879)', '#     K=407,120 merged pool; W186 finalize one-pass bm-a r884)', 1),
    ('#     always on. ADMIT receipt results/_r880bma_w186_probe_receipt.json;', '#     always on. ADMIT receipt results/_r885bma_w187_probe_receipt.json;', 1),
    ('#     banned gate ADMIT 0; not a re-pick (R250: W186 bands were', '#     banned gate ADMIT 0; not a re-pick (R250: W187 bands were', 1),
    ('    _set_wave(186)', '    _set_wave(187)', 1),
    ('assert WAVE_CONFIGS[185]["a_seed_base"] == pf.N1_BANDS[185]["a"][0], \\', 'assert WAVE_CONFIGS[186]["a_seed_base"] == pf.N1_BANDS[186]["a"][0], \\', 1),
    ('"W186 A band drift vs law mirror"', '"W187 A band drift vs law mirror"', 1),
    ('assert WAVE_CONFIGS[185]["b_exit_seed_base"] == \\', 'assert WAVE_CONFIGS[186]["b_exit_seed_base"] == \\', 1),
    ('pf.N1_BANDS[185]["b_exit"][0], "W186 B band drift vs law mirror"', 'pf.N1_BANDS[186]["b_exit"][0], "W187 B band drift vs law mirror"', 1),
    ('assert WAVE_CONFIGS[185].get("engine_owner") == \\', 'assert WAVE_CONFIGS[186].get("engine_owner") == \\', 1),
    ('pf.N1_BANDS[185].get("engine_owner") == "bm-a", \\', 'pf.N1_BANDS[186].get("engine_owner") == "bm-a", \\', 1),
    ('"W186 engine_owner drift (law mirror parity)"', '"W187 engine_owner drift (law mirror parity)"', 1),
    ('w185_a = {A_SEED_BASE + j for j in range(A_N)}', 'w186_a = {A_SEED_BASE + j for j in range(A_N)}', 1),
    ('w185_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}', 'w186_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}', 1),
    ('assert not (w185_a & w185_b), "W186 A/B band overlap"', 'assert not (w186_a & w186_b), "W187 A/B band overlap"', 1),
    ('assert not (w185_a & reg_ints) and not (w185_b & reg_ints), \\', 'assert not (w186_a & reg_ints) and not (w186_b & reg_ints), \\', 1),
    ('"W186 hits SEED_REGISTRY"', '"W187 hits SEED_REGISTRY"', 1),
    ('for nm, band in (("A", w185_a), ("B", w185_b)):', 'for nm, band in (("A", w186_a), ("B", w186_b)):', 1),
    ('f"W186 {nm} hits v1"', 'f"W187 {nm} hits v1"', 1),
    ('f"W186 {nm} hits W1"', 'f"W187 {nm} hits W1"', 1),
    ('f"W186 {nm} hits probe seeds"', 'f"W187 {nm} hits probe seeds"', 1),
    ('"registered W185 row parity drift (r307; bm-a r878)"', '"registered W185 row parity drift (r307; bm-a r878)"\r\n        assert pf.N1_BANDS[186] == {"a": (424_004, 426_003),\r\n                                    "b_exit": (426_004, 426_203),\r\n                                    "engine_owner": "bm-a"}, \\\r\n            "registered W186 row parity drift (r307; bm-a r882)"', 1),
    ('# prior-wave disjointness W2..W185 (single state: all', '# prior-wave disjointness W2..W186 (single state: all', 1),
    ('for wprev in sorted(w for w in WAVE_CONFIGS if w < 186):', 'for wprev in sorted(w for w in WAVE_CONFIGS if w < 187):', 2),
    ('assert not (w185_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j', 'assert not (w186_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j', 1),
    ('for j in range(A_N)}), f"W186 A hits W{wprev}"', 'for j in range(A_N)}), f"W187 A hits W{wprev}"', 1),
    ('assert not (w185_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j', 'assert not (w186_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j', 1),
    ('for j in range(B_N)}), f"W186 B hits W{wprev}"', 'for j in range(B_N)}), f"W187 B hits W{wprev}"', 1),
    ('n3r1_used185 = set(range(70_000, 70_006))', 'n3r1_used186 = set(range(70_000, 70_006))', 1),
    ('assert not (w185_a & n3r1_used185) and not (w185_b & n3r1_used185), \\', 'assert not (w186_a & n3r1_used186) and not (w186_b & n3r1_used186), \\', 1),
    ('"W186 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"', '"W187 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"', 1),
    ('assert not (w185_a & lfc_actual12) and not (w185_b & lfc_actual12), \\', 'assert not (w186_a & lfc_actual12) and not (w186_b & lfc_actual12), \\', 1),
    ('"W186 bands must clear the lfc actual draw range"', '"W187 bands must clear the lfc actual draw range"', 1),
    ('assert not (w185_a & options_actual12) and \\', 'assert not (w186_a & options_actual12) and \\', 1),
    ('not (w185_b & options_actual12), \\', 'not (w186_b & options_actual12), \\', 1),
    ('"W186 bands must clear the options_wave2 actual draw range"', '"W187 bands must clear the options_wave2 actual draw range"', 1),
    ('# band facts (law sec.4 W186 row, r795): A = FIRST-CLEAN past', '# band facts (law sec.4 W187 row, r795): A = FIRST-CLEAN past', 1),
    ('# the registered W185 B band (the arithmetic continuation', '# the registered W186 B band (the arithmetic continuation', 1),
    ('# 423_804..425_803 is REFUSED at its own start by the W185', '# 426_004..428_003 is REFUSED at its own start by the W186', 1),
    ('# B band 423_804..424_003, exactly as the W185 seat W186+ projection +', '# B band 426_004..426_203, exactly as the W186 seat W187+ projection +', 1),
    ('# r875 probe leg4 + r879 sec8 same-window succession projection notes', '# r880 probe leg4 + r885 sec8 回填窗 succession projection notes', 1),
    ('# 424_004..426_003; A base == prior-wave B tail+1 (424_003+1)', '# 426_204..428_203; A base == prior-wave B tail+1 (426_203+1)', 1),
    ('# machine-checkable -- A-hops-prior-B staircase FORTY-SIXTH', '# machine-checkable -- A-hops-prior-B staircase FORTY-SEVENTH', 1),
    ('# continuation 424_004..424_203 is CLEAN on the registered', '# continuation 426_204..426_403 is CLEAN on the registered', 1),
    ('# universe but lands INSIDE the W186 A band window --', '# universe but lands INSIDE the W187 A band window --', 1),
    ('# 426_004 and lands 426_004..426_203, hops=1, non-rotational', '# 428_204 and lands 428_204..428_403, hops=1, non-rotational', 1),
    ('# (426_003+1) machine-checkable; cross-window convergence', '# (428_203+1) machine-checkable; cross-window convergence', 1),
    ('# with the W185 seat W186+ projection + r875 probe leg4 + r879 sec8', '# with the W186 seat W187+ projection + r880 probe leg4 + r885 sec8', 1),
    ('# honored (post-W185 universe re-derive + own-wave A', '# honored (post-W186 universe re-derive + own-wave A', 1),
    ('# reservation when deriving B); seat MSG-1354 tail,', '# reservation when deriving B); seat MSG-1626 tail,', 1),
    ('assert WAVE_CONFIGS[186]["a_seed_base"] == 424_004 == 424_003 + 1, (', 'assert WAVE_CONFIGS[187]["a_seed_base"] == 426_204 == 426_203 + 1, (', 1),
    ('"W186 A must be the first-clean window past the registered "', '"W187 A must be the first-clean window past the registered "', 1),
    ('"W185 B band tail 424_003+1 (arithmetic continuation "', '"W186 B band tail 426_203+1 (arithmetic continuation "', 1),
    ('"423_804..425_803 REFUSED at its own start by the W185 B "', '"426_004..428_003 REFUSED at its own start by the W186 B "', 1),
    ('"band 423_804..424_003, exactly as the W185 seat W186+ projection + "', '"band 426_004..426_203, exactly as the W186 seat W187+ projection + "', 1),
    ('"r875 probe leg4 + r879 sec8 same-window succession projection notes "', '"r880 probe leg4 + r885 sec8 回填窗 succession projection notes "', 1),
    ('"staircase FORTY-SIXTH instance, E36 card)"', '"staircase FORTY-SEVENTH instance, E36 card)"', 1),
    ('arith_a185 = set(range(424_004, 426_004))', 'arith_a186 = set(range(426_204, 428_204))', 1),
    ('assert not (arith_a185 & reg_ints), \\', 'assert not (arith_a186 & reg_ints), \\', 1),
    ('"W186 A window must be CLEAN (first-clean ADMIT face past prior-wave B)"', '"W187 A window must be CLEAN (first-clean ADMIT face past prior-wave B)"', 1),
    ('assert WAVE_CONFIGS[186]["b_exit_seed_base"] == 426_004 == 426_003 + 1, (', 'assert WAVE_CONFIGS[187]["b_exit_seed_base"] == 428_204 == 428_203 + 1, (', 1),
    ('"W186 B must be the first-clean window past the own-wave A "', '"W187 B must be the first-clean window past the own-wave A "', 1),
    ('"band tail 426_003+1 (arithmetic continuation "', '"band tail 428_203+1 (arithmetic continuation "', 1),
    ('"424_004..424_203 CLEAN on the registered universe but "', '"426_204..426_403 CLEAN on the registered universe but "', 1),
    ('"lands INSIDE the W186 A band window; same-freeze mutual "', '"lands INSIDE the W187 A band window; same-freeze mutual "', 1),
    ('"own-wave A window reserved jumps to 426_004, first-clean "', '"own-wave A window reserved jumps to 428_204, first-clean "', 1),
    ('arith_b185 = set(range(426_004, 426_204))', 'arith_b186 = set(range(428_204, 428_404))', 1),
    ('assert not (arith_b185 & reg_ints), \\', 'assert not (arith_b186 & reg_ints), \\', 1),
    ('"W186 B window must be CLEAN (first-clean ADMIT face past own-wave A)"', '"W187 B window must be CLEAN (first-clean ADMIT face past own-wave A)"', 1),
    ('assert not (arith_b185 & arith_a185), \\', 'assert not (arith_b186 & arith_a186), \\', 1),
    ('"W186 A/B same-freeze mutual exclusion (B hops past own A)"', '"W187 A/B same-freeze mutual exclusion (B hops past own A)"', 1),
    ('assert _entry_shard_of(0, 12) == ("PERPETUAL-N1-W186-SHARD-0",', 'assert _entry_shard_of(0, 12) == ("PERPETUAL-N1-W187-SHARD-0",', 1),
    ('"n1w186-0of12"), "W186 entry identity"', '"n1w187-0of12"), "W187 entry identity"', 1),
    ('assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W186-SHARD-11",', 'assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W187-SHARD-11",', 1),
    ('"n1w186-11of12")', '"n1w187-11of12")', 1),
    ('assert SHARD_DIR.endswith("n1_w186") and OUT.endswith(', 'assert SHARD_DIR.endswith("n1_w187") and OUT.endswith(', 1),
    ('"n1_w186_results.json"), "W186 path drift"', '"n1_w187_results.json"), "W187 path drift"', 1),
    ('f"W186 shard dir collides with W{wprev}"', 'f"W187 shard dir collides with W{wprev}"', 1),
    ('# W186 finalize cumulative deps: W17..W185 outputs ALL PRESENT', '# W187 finalize cumulative deps: W17..W186 outputs ALL PRESENT', 1),
    ('# (landed net chain head 814,328 = W185 bm-a r879 one-pass --', '# (landed net chain head 816,528 = W186 bm-a r884 one-pass --', 1),
    ('for _depw in range(17, 186):', 'for _depw in range(17, 187):', 1),
    ('f"W186 finalize cumulative dep (W{_depw} output) missing"', 'f"W187 finalize cumulative dep (W{_depw} output) missing"', 1),
    ('# registered wave below 186 composes; wave 15 excluded by', '# registered wave below 187 composes; wave 15 excluded by', 1),
    ('# design; SINGLE STATE (W2..W185 all registered -- no', '# design; SINGLE STATE (W2..W186 all registered -- no', 1),
    ('assert sorted(w for w in WAVE_CONFIGS if w < 186) == \\', 'assert sorted(w for w in WAVE_CONFIGS if w < 187) == \\', 1),
    ('[w for w in range(16, 186)], \\', '[w for w in range(16, 187)], \\', 1),
    ('"W186 prior-wave set must derive from registry keys (no 15; "', '"W187 prior-wave set must derive from registry keys (no 15; "', 1),
    ('"W2..W185 registered single state)"', '"W2..W186 registered single state)"', 1),
    ('PATHS.root, "research", "PERPETUAL_N1_W186_PREREG.md")), \\', 'PATHS.root, "research", "PERPETUAL_N1_W187_PREREG.md")), \\', 1),
    ('"W186 per-wave prereg missing (materializer requirement)"', '"W187 per-wave prereg missing (materializer requirement)"', 1),
]

CL_PAIRS = [
    ('"+ W186 materializer face [same guard set, dep=W17..W185 ', '"+ W187 materializer face [same guard set, dep=W17..W186 ', 1),
    ('"outputs ALL PRESENT (landed net chain head 814,328 = "', '"outputs ALL PRESENT (landed net chain head 816,528 = "', 1),
    ('"W185 bm-a r879 one-pass, K=404,920 merged pool; ZERO "', '"W186 bm-a r884 one-pass, K=407,120 merged pool; ZERO "', 1),
    ('"in-flight upstream seats), ONE HUNDRED-AND-SEVENTY-SIXTH "', '"in-flight upstream seats), ONE HUNDRED-AND-SEVENTY-SEVENTH "', 1),
    ('"ENGINE-OWNED WAVE BY MACHINE-DERIVE (engine_owner rows 175 "', '"ENGINE-OWNED WAVE BY MACHINE-DERIVE (engine_owner rows 176 "', 1),
    ("+ candidate) bm-a's one-hundred-second owned claim per ", "+ candidate) bm-a's one-hundred-third owned claim per ", 1),
    ('"machine-derive (engine_owner==bm-a rows 101 + candidate), "', '"machine-derive (engine_owner==bm-a rows 102 + candidate), "', 1),
    ('"A=FIRST-CLEAN past the registered W185 B band (staircase "', '"A=FIRST-CLEAN past the registered W186 B band (staircase "', 1),
    ('"FORTY-SIXTH instance, E36 card, hops=1) + B=FIRST-CLEAN past the "', '"FORTY-SEVENTH instance, E36 card, hops=1) + B=FIRST-CLEAN past the "', 1),
    ('"results/_r880bma_w186_probe_receipt.json, law sec.4 W186 row, "', '"results/_r885bma_w187_probe_receipt.json, law sec.4 W187 row, "', 1),
    ('"r882 bm-a] "', '"r885 bm-a] "', 1),
]

PF_NEG = ['    # W186 (bm-a r882 freeze, seat MSG-2026-10-08-1354-bma-w186-seat', 'pushed to origin dd362c690 pre-freeze r565 law (r880 pre-seat', '(3-item; the W185 finalize product already on origin since r879,', '# = direct fast-forward behind-0 at fetch (r880 pre-seat', '# push), zero merge, zero --no-verify; self-ack archive ALREADY\r\n    # LANDED pre-freeze -- bm-a r880-window self-ack move (the W186\r\n    # seat MSG sits in fleet/inbox/processed/ at freeze time, honest\r\n    # archived);', 'band gate ADMIT results/_r880bma_w186_probe_receipt.json: A = FIRST-CLEAN', 'past the registered W185 B band (arithmetic continuation', '423_804..425_803 REFUSED at its own start by the W185 B band', '423_804..424_003, exactly as the W185 seat W186+ projection + r875 probe', '# leg4 + r879 sec8 same-window succession projection notes all anticipated;', 'honest forward walk hops=1 -> 424_004..426_003, non-rotational', '(424_003+1) machine-checkable -- A-hops-prior-B staircase', 'FORTY-SIXTH instance, E36 card);', 'continuation 424_004..424_203 CLEAN on the registered universe', 'but lands INSIDE the W186 A band window -- same-freeze mutual', 'own-wave A window reserved jumps to 426_004 -> 426_004..426_203,', 'own-wave A tail+1 (426_003+1) machine-checkable);', 'W186+ projection (gate-derived r880): A first-clean', '426_004..428_003 CLEAN hops=0 / B first-clean 426_204..426_403', 'registered W186 B band 426_004..426_203 will refuse the naive', 'W187 A window; W187 freezer MUST re-derive on the post-W186', 'NOT a re-pick (R250: W186 bands were never assigned).', '186: {"a": (424_004, 426_003), "b_exit": (426_004, 426_203),', 'dd362c690', 'r875 probe', 'r879 sec8', 'r880 pre-seat', '_r880bma', 'MSG-2026-10-08-1354', 'beb4b5abd', '814,328', '404,920', 'FORTY-SIXTH', 'ONE HUNDRED-AND-SEVENTY-SIXTH']

EN_NEG = ['186: {"batch": "PERPETUAL-N1-W186",', '"prereg": ("research/PERPETUAL_N1_W186_PREREG.md (wave-level frozen "', 'new seed bands only; ONE HUNDRED-AND-SEVENTY-SIXTH ENGINE-OWNED WAVE ', 'BY MACHINE-DERIVE (engine_owner rows 175 + candidate), ', 'number law after the REGISTERED W185 row bm-a r878 freeze ', 'beb4b5abd, SINGLE STATE zero seat gap W2..W185 all ', 'registered; W186 finalize landed same-window r827, ledger ', 'head 814,328, merged pool K=404,920; seat published=reserved ', 'MSG-2026-10-08-1354-bma-w186-seat PUSHED to origin dd362c690 ', 'probe receipt (3-item; the W185 finalize product already on origin since r879, not re-shipped; W146 precedent); ', 'at fetch (r880 pre-seat push), zero merge, zero ', 'engine_owner=bm-a, wave 185: ', 'A = FIRST-CLEAN past the registered W185 B band (the ', 'arithmetic continuation 423_804..425_803 is REFUSED at its ', 'own start by the W185 B band 423_804..424_003, exactly as ', 'the W185 seat W186+ projection + r875 probe leg4 + r879 sec8 same-window succession ', '424_004..426_003; A base == prior-wave B tail+1 ', 'machine-checkable = A-hops-prior-B staircase FORTY-SIXTH ', 'arithmetic continuation 424_004..424_203 is CLEAN on the ', 'registered universe but lands INSIDE the W186 A band ', 'jumps to 426_004, first-clean 426_004..426_203 hops=1, ', 'convergence with the W185 seat W186+ projection + r875 probe leg4 + ', 'r879 sec8 same-window succession projection notes re-derived -- all ', 'MANDATORY notes honored (post-W185 universe re-derive + ', 'results/_r880bma_w186_probe_receipt.json; W187+ projection ', 'per this window gate: A first-clean 426_004..428_003 ', 'CLEAN / B first-clean 426_204..426_403 CLEAN -- naive ', 'W186 B band 426_004..426_203 will refuse the naive ', 'W187 A window; W187 freezer MUST re-derive on the ', 'post-W186 universe AND reserve the own-wave A window ', 'staircase card); W1..W185 finalize ALL LANDED (W185 ', 'finalize one-pass bm-a r879, net chain head 814,328, ', 'merged pool K=404,920) -- ZERO in-flight upstream ', '"a_seed_base": 424_004,        # law sec.4 W186 A: 424_004..426_003 (FIRST-CLEAN past the registered W185 B band; arithmetic 423_804..425_803 REFUSED at own start by the W185 B band; hops=1; A-hops-prior-B staircase FORTY-SIXTH instance, E36 card; ordinal convergence per r587: W185 sec5.5 prose anticipated forty-sixth, r880 receipt machine-read FORTY-SIXTH)', '"b_exit_seed_base": 426_004,   # law sec.4 W186 B: 426_004..426_203 (FIRST-CLEAN past the own-wave A window; arithmetic 424_004..424_203 lands inside own-A, same-freeze mutual exclusion W141 precedent; reserved walk hops=1; B base == own-A tail+1)', '"shard_subdir": "n1_w186", "out_name": "n1_w186_results.json",', 'beb4b5abd', 'dd362c690', '814,328', '404,920', 'ONE HUNDRED-AND-SEVENTY-SIXTH', 'rows 175', 'r875 probe', '_r880bma', 'MSG-2026-10-08-1354', 'n1w186', 'n1_w186', 'PERPETUAL-N1-W186', 'PERPETUAL_N1_W186', 'FORTY-SIXTH', 'bm-a r878 freeze', '426_004, first-clean']

MAT_NEG = ['# --- W186 materializer face (r882 bm-a freeze, own-series law', '#     one-hundred-second owned per machine-derive (engine_owner==bm-a', '#     rows 101 + candidate); wave 185 = first free number after', '#     the REGISTERED W185 row (bm-a r878 freeze beb4b5abd) --', '#     SINGLE STATE zero seat gap (W2..W185 all registered). Seat', '#     published=reserved MSG-2026-10-08-1354-bma-w186-seat pushed', '#     to origin dd362c690 BEFORE this freeze, r565 law (payload', '#     the W185 finalize product already on origin since r879, not', '#     at fetch (r880 pre-seat push), zero merge, zero', '#     --no-verify; self-ack inbox->processed archive ALREADY LANDED\r\n    #     pre-freeze -- bm-a r880-window self-ack move (the W186 seat\r\n    #     MSG sits in fleet/inbox/processed/ at freeze time, honest\r\n    #     archived).', '#     ONE HUNDRED-AND-SEVENTY-SIXTH engine wave BY', '#     MACHINE-DERIVE (engine_owner rows 175 + candidate; gate', '#     W1..W185 finalize ALL LANDED (net chain head 814,328,', '#     K=404,920 merged pool; W185 finalize one-pass bm-a r879)', '#     always on. ADMIT receipt results/_r880bma_w186_probe_receipt.json;', '#     banned gate ADMIT 0; not a re-pick (R250: W186 bands were', '    _set_wave(186)', 'assert WAVE_CONFIGS[185]["a_seed_base"] == pf.N1_BANDS[185]["a"][0], \\', '"W186 A band drift vs law mirror"', 'assert WAVE_CONFIGS[185]["b_exit_seed_base"] == \\', 'pf.N1_BANDS[185]["b_exit"][0], "W186 B band drift vs law mirror"', 'assert WAVE_CONFIGS[185].get("engine_owner") == \\', 'pf.N1_BANDS[185].get("engine_owner") == "bm-a", \\', '"W186 engine_owner drift (law mirror parity)"', 'w185_a = {A_SEED_BASE + j for j in range(A_N)}', 'w185_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}', 'assert not (w185_a & w185_b), "W186 A/B band overlap"', 'assert not (w185_a & reg_ints) and not (w185_b & reg_ints), \\', '"W186 hits SEED_REGISTRY"', 'for nm, band in (("A", w185_a), ("B", w185_b)):', 'f"W186 {nm} hits v1"', 'f"W186 {nm} hits W1"', 'f"W186 {nm} hits probe seeds"', '# prior-wave disjointness W2..W185 (single state: all', 'for wprev in sorted(w for w in WAVE_CONFIGS if w < 186):', 'assert not (w185_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j', 'for j in range(A_N)}), f"W186 A hits W{wprev}"', 'assert not (w185_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j', 'for j in range(B_N)}), f"W186 B hits W{wprev}"', 'n3r1_used185 = set(range(70_000, 70_006))', 'assert not (w185_a & n3r1_used185) and not (w185_b & n3r1_used185), \\', '"W186 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"', 'assert not (w185_a & lfc_actual12) and not (w185_b & lfc_actual12), \\', '"W186 bands must clear the lfc actual draw range"', 'assert not (w185_a & options_actual12) and \\', 'not (w185_b & options_actual12), \\', '"W186 bands must clear the options_wave2 actual draw range"', '# band facts (law sec.4 W186 row, r795): A = FIRST-CLEAN past', '# the registered W185 B band (the arithmetic continuation', '# 423_804..425_803 is REFUSED at its own start by the W185', '# B band 423_804..424_003, exactly as the W185 seat W186+ projection +', '# r875 probe leg4 + r879 sec8 same-window succession projection notes', '# 424_004..426_003; A base == prior-wave B tail+1 (424_003+1)', '# machine-checkable -- A-hops-prior-B staircase FORTY-SIXTH', '# continuation 424_004..424_203 is CLEAN on the registered', '# universe but lands INSIDE the W186 A band window --', '# 426_004 and lands 426_004..426_203, hops=1, non-rotational', '# (426_003+1) machine-checkable; cross-window convergence', '# with the W185 seat W186+ projection + r875 probe leg4 + r879 sec8', '# honored (post-W185 universe re-derive + own-wave A', '# reservation when deriving B); seat MSG-1354 tail,', 'assert WAVE_CONFIGS[186]["a_seed_base"] == 424_004 == 424_003 + 1, (', '"W186 A must be the first-clean window past the registered "', '"W185 B band tail 424_003+1 (arithmetic continuation "', '"423_804..425_803 REFUSED at its own start by the W185 B "', '"band 423_804..424_003, exactly as the W185 seat W186+ projection + "', '"r875 probe leg4 + r879 sec8 same-window succession projection notes "', '"staircase FORTY-SIXTH instance, E36 card)"', 'arith_a185 = set(range(424_004, 426_004))', 'assert not (arith_a185 & reg_ints), \\', '"W186 A window must be CLEAN (first-clean ADMIT face past prior-wave B)"', 'assert WAVE_CONFIGS[186]["b_exit_seed_base"] == 426_004 == 426_003 + 1, (', '"W186 B must be the first-clean window past the own-wave A "', '"band tail 426_003+1 (arithmetic continuation "', '"424_004..424_203 CLEAN on the registered universe but "', '"lands INSIDE the W186 A band window; same-freeze mutual "', '"own-wave A window reserved jumps to 426_004, first-clean "', 'arith_b185 = set(range(426_004, 426_204))', 'assert not (arith_b185 & reg_ints), \\', '"W186 B window must be CLEAN (first-clean ADMIT face past own-wave A)"', 'assert not (arith_b185 & arith_a185), \\', '"W186 A/B same-freeze mutual exclusion (B hops past own A)"', 'assert _entry_shard_of(0, 12) == ("PERPETUAL-N1-W186-SHARD-0",', '"n1w186-0of12"), "W186 entry identity"', 'assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W186-SHARD-11",', '"n1w186-11of12")', 'assert SHARD_DIR.endswith("n1_w186") and OUT.endswith(', '"n1_w186_results.json"), "W186 path drift"', 'f"W186 shard dir collides with W{wprev}"', '# W186 finalize cumulative deps: W17..W185 outputs ALL PRESENT', '# (landed net chain head 814,328 = W185 bm-a r879 one-pass --', 'for _depw in range(17, 186):', 'f"W186 finalize cumulative dep (W{_depw} output) missing"', '# registered wave below 186 composes; wave 15 excluded by', '# design; SINGLE STATE (W2..W185 all registered -- no', 'assert sorted(w for w in WAVE_CONFIGS if w < 186) == \\', '[w for w in range(16, 186)], \\', '"W186 prior-wave set must derive from registry keys (no 15; "', '"W2..W185 registered single state)"', 'PATHS.root, "research", "PERPETUAL_N1_W186_PREREG.md")), \\', '"W186 per-wave prereg missing (materializer requirement)"', 'w185_', 'arith_a185', 'arith_b185', 'n3r1_used185', 'r875 probe', 'r880 pre-seat', 'beb4b5abd', 'ONE HUNDRED-AND-SEVENTY-SIXTH', 'one-hundred-second', 'rows 175', 'rows 101 ', 'range(17, 186)', 'range(16, 186)', 'PERPETUAL_N1_W186', 'PERPETUAL-N1-W186', 'MSG-1354', '_r880bma', 'bm-a r880-window', 'n1w186', 'n1_w186', '814,328', '404,920']

CL_NEG = ['"+ W186 materializer face [same guard set, dep=W17..W185 ', '"outputs ALL PRESENT (landed net chain head 814,328 = "', '"W185 bm-a r879 one-pass, K=404,920 merged pool; ZERO "', '"in-flight upstream seats), ONE HUNDRED-AND-SEVENTY-SIXTH "', '"ENGINE-OWNED WAVE BY MACHINE-DERIVE (engine_owner rows 175 "', "+ candidate) bm-a's one-hundred-second owned claim per ", '"machine-derive (engine_owner==bm-a rows 101 + candidate), "', '"A=FIRST-CLEAN past the registered W185 B band (staircase "', '"FORTY-SIXTH instance, E36 card, hops=1) + B=FIRST-CLEAN past the "', '"results/_r880bma_w186_probe_receipt.json, law sec.4 W186 row, "', '"r882 bm-a] "', '814,328', '404,920', 'ONE HUNDRED-AND-SEVENTY-SIXTH', 'one-hundred-second', 'rows 175', 'rows 101 ', 'FORTY-SIXTH', '_r880bma', 'r882 bm-a] ']

blk187 = vmap(pfblk, PF_PAIRS, PF_NEG, "pf")
entry187 = IND23 + vmap(entry, EN_PAIRS, EN_NEG, "entry")
mat187 = "    " + vmap(mat, MAT_PAIRS, MAT_NEG, "mat")
claim187 = IND10 + vmap(claim, CL_PAIRS, CL_NEG, "claim")

# ---- apply insertions (in-memory) ---------------------------------------
pfsrc = io.open(PF, encoding="utf-8", newline="").read()
n1src = io.open(N1, encoding="utf-8", newline="").read()

# pf: insert W187 block after the W186 row (last registered), before the
# dict close -- r560 insert-after-last-registered-row + post-anchor gate
seg = EO + NL + "}"
check(pfsrc.count(seg) == 1, "pf row-close segment not unique")
pfnew = pfsrc.replace(seg, EO + NL + blk187 + NL + "}", 1)

# n1 entry: after the W186 entry, before the WAVE_CONFIGS close
seg = EO + NL + IND23 + "}"
check(n1src.count(seg) == 1, "n1 entry-close segment not unique")
n1new = n1src.replace(seg, EO + NL + entry187 + NL + IND23 + "}", 1)

# n1 mat: insert the W187 block before the T-141 s2 lane face header
seg = "    # --- T-141 s2 lane face"
check(n1new.count(seg) == 1, "n1 T-141 mat anchor not unique")
n1new = n1new.replace(seg, mat187 + NL + seg, 1)

# n1 claim: insert the W187 attribution after the W186 claim tail line
# (r581 law: anchor = tail single-line literal + post-anchor guard)
seg = '"r882 bm-a] "' + NL + IND10 + '"+ T-141 s2 "'
check(n1new.count(seg) == 1, "n1 claim anchor not unique")
n1new = n1new.replace(seg, '"r882 bm-a] "' + NL + claim187 + NL + IND10 +
                      '"+ T-141 s2 "', 1)

# ---- gates (r780/r781/r560/r815 lineage) --------------------------------
ast.parse(pfnew)
ast.parse(n1new)
print("AST gate: both files parse OK")

# W187 presence + W186 anti-vanish (r560 law)
checks = [
    (pfnew, '187: {"a": (426_204, 428_203), "b_exit": (428_204, 428_403),', 1),
    (pfnew, '186: {"a": (424_004, 426_003), "b_exit": (426_004, 426_203),', 1),
    (pfnew, "# W187 (bm-a r885 freeze", 1),
    (pfnew, "# W186 (bm-a r882 freeze", 1),
    (n1new, '187: {"batch": "PERPETUAL-N1-W187",', 1),
    (n1new, '186: {"batch": "PERPETUAL-N1-W186",', 1),
    (n1new, "# --- W187 materializer face", 1),
    (n1new, "# --- W186 materializer face", 1),
    (n1new, '"r885 bm-a] "', 1),
    (n1new, '"r882 bm-a] "', 1),
    (n1new, '"a_seed_base": 426_204,', 1),
    (n1new, '"b_exit_seed_base": 428_204,', 1),
    (n1new, "n1_w187", 4),
    (n1new, "PERPETUAL_N1_W187_PREREG.md", 2),
]
for src, needle, cnt in checks:
    got = src.count(needle)
    check(got == cnt, "post-edit needle %r count %d != %d" % (needle[:50], got, cnt))

# W188+ projection prose present in the new W187 blocks (probe leg4
# verbatim; r819 post-edit assert bloodline + r776 fragment-needle law;
# pf header = self-wave W187+ per r845 precedent, n1 fragment =
# next-wave W188+)
check("# W187+ projection (gate-derived r885)" in pfnew,
      "pf W187+ projection head missing")
check('probe_receipt.json; W188+ projection "' in n1new,
      "n1 W188+ projection head fragment missing")
check("# 428_204..430_203 CLEAN hops=0 / B first-clean 428_404..428_603" in pfnew,
      "pf W188p prose missing")
check("W188 A window; W188 freezer MUST re-derive on the post-W187" in pfnew,
      "pf W188 freezer prose missing")
check('"W188 A window; W188 freezer MUST re-derive on the "' in n1new,
      "n1 W188 freezer fragment missing")
check('"W187 B band 428_204..428_403 will refuse the naive "' in n1new,
      "n1 W187-band refuse fragment missing")

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
check('187: {"a": (426_204' not in pf_o2, "write-time: origin pf carries W187")
check('187: {"batch"' not in n1_o2, "write-time: origin n1 carries W187")
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
