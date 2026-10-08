# -*- coding: utf-8 -*-
"""r874 bm-a W184 freeze edits: four insertions (pf N1_BANDS[184] row +
n1 WAVE_CONFIGS[184] entry + n1 W184 materializer block + n1 W184
PASS-claim attribution). DRY flag: --dry = zero-write simulation
(r781 verify-separation law + r811/r822/r826/r830/r834/r843/r845/r849/
r852/r863/r867/r869 dry-run precedent: full stale+prose+AST asserts
in memory BEFORE any write).

Bloodline: r819/r822/r826/r830/r834/r843/r845/r849/r852/r863/r867/r869
freeze-edits machinery (r773 pit law freeze-editor compliance + r776
fragment-needle law + r781 verify-separation law), W184 facts
live-registry-driven (built by _r874bma_w184_freeze_buildgen.py: old
sides = the PHYSICAL W183 face fragments probed to dumps this window,
new sides = the S83 W184 fact map, counts verified pre-emission):
  - pre-seat probe results/_r870bma_w184_probe_receipt.json rc0 ADMIT
    (naive A 419_404..421_403 refused at its own start by the
    registered W183 B band 419_404..419_603; honest forward walk
    1 hop lands A 419_604..421_603 staircase FORTY-FOURTH instance
    E36 -- receipt A_semantics machine-cites the W183 seat MSG leg4 +
    r868 W183 probe leg4 + W183 prereg sec5.5/sec8 anticipated +
    MANDATED this re-derive (projection and receipt ordinals MATCH,
    no divergence this wave); B 421_604..421_803 own-A mutual
    exclusion hops=1, naive 419_604..419_803);
  - face probe results/_r874bma_w184_face_probe_receipt.json rc0 (all
    four W183 faces dumped + needle counts; this TOK is built from the
    PHYSICAL probe-dumped shapes, r776 law);
  - seat MSG-2026-10-08-0826-bma-w184-seat published on origin at
    d1f15ebf9 (r870 pre-seat push, path-derived TRUE sha per r812
    precedent); r565 law: on origin BEFORE this freeze commit;
    self-ack archive ALREADY LANDED pre-freeze -- bm-c r745-window
    self-ack move (cross-machine consume, 1ec9800ae; machine-read git
    history this window -- the W184 prereg's "bm-c r741" citation is a
    stale session number superseded by machine-read, honest); the W184
    seat MSG sits in fleet/inbox/processed/ at freeze time, honest
    archived;
  - per-wave prereg research/PERPETUAL_N1_W184_PREREG.md built r872
    (buildgen r869-bloodline; banned gate ADMIT 0 verified at prereg
    build; frozen+pushed f908433c4 r872; on origin verified live
    below);
  - W183 freeze registered sha machine-derived = 481da4d78 (git log
    origin/main --grep "W183 FREEZE"); W183 finalize landed r870
    one-pass same-window: ledger head 808,918, merged pool K=400,520
    (n1_w183_results.json machine-read); W183 sec7/sec8 settle
    backfill landed the r870 SAME window (r864 lesson 2nd
    consecutive);
  - lineage constants disclosed (r795/r845/r849/r852/r863/r867/r869
    precedent, passed through): (a) the "wave N-1 = first free number"
    mat-header label rolls forward with its off-by-one quirk (since
    W165 r795); (b) "law sec.4 W184 row, r795" band-facts template
    stamp keeps its r795; (c) "single-window derive (r812 merged the
    gate legs INTO the pre-seat probe...)" stays (historical merge
    citation); (d) the bm-a-owned ordinal word rolls ninety-ninth ->
    one-hundredth (rows 99 + candidate = 100th owned per probe leg0 --
    first triple-digit crossing, word form machine-chosen
    "one-hundredth", disclosed); (e) mat parity-chain rows W138..W182
    keep their historical stamps and tuples; the W183 row (the
    current registered tail) is APPENDED with its frozen values
    (417_404, 419_403)/(419_404, 419_603); (f) the "W183 finalize
    landed same-window r827" citation rolls its wave-word with the
    stale r827 session stamp riding (off-by-one wave-word +
    stale-session lineage quirk inherited; head/K values roll
    machine-correct to 808,918/400,520 this window).

r773 pit law compliance:
  (1) full string-face inventory empirically probed BEFORE TOK
      (_r874bma_w184_face_probe.py -- four face dumps + needle-count
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
      (r530/r687: fetch + origin carries no W184 registration before
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
probe = json.load(open(r"results\_r870bma_w184_probe_receipt.json",
                       encoding="utf-8"))
check(probe["verdict"] == "ADMIT", "pre-seat probe not ADMIT")
check(probe["bands"] == {"A": "419604_421603", "B": "421604_421803"},
      "probe band shape mismatch")
check(probe["legs"]["leg1"]["A"] == [419604, 421603], "A band mismatch")
check(probe["legs"]["leg1"]["B"] == [421604, 421803], "B band mismatch")
check(probe["legs"]["leg1"]["hops_A"] == 1 and probe["legs"]["leg1"]["hops_B"] == 1,
      "hops mismatch")
check(probe["legs"]["leg0"]["rows"] == 181 and probe["legs"]["leg0"]["tail"] == "W183",
      "leg0 registry tail mismatch")
check(probe["legs"]["leg0"]["ordinal"] == 174 and probe["legs"]["leg0"]["bma_ordinal"] == 100,
      "leg0 ordinal mismatch")
check(probe["legs"]["leg2"]["conflicts"] == 0, "leg2 conflicts nonzero")
check(probe["legs"]["leg3"]["origin_vacancy"] is True, "leg3 origin not vacant")
check(probe["legs"]["leg4"]["W185p_A"] == "421604..423603"
      and probe["legs"]["leg4"]["W185p_B"] == "421804..422003",
      "leg4 W185+ projection mismatch")

# origin anti-collision pre-check (r511 tail-lock / r687 write-time gate)
subprocess.run(["git", "fetch", "origin"], capture_output=True)
pf_o = subprocess.run(["git", "show", "origin/main:" + PF],
                      capture_output=True).stdout.decode("utf-8", "replace")
n1_o = subprocess.run(["git", "show", "origin/main:" + N1],
                      capture_output=True).stdout.decode("utf-8", "replace")
check('184: {"a": (419_604' not in pf_o, "origin pf already carries W184 row")
check("W184 (bm-a r874 freeze" not in pf_o, "origin pf carries W184 block")
check('184: {"batch"' not in n1_o, "origin n1 already carries W184 entry")
check("# --- W184 materializer face" not in n1_o, "origin n1 carries W184 mat")
check('"r874 bm-a] "' not in n1_o, "origin n1 carries W184 claim")

# machine-derived shas (r587 / r812 path-derived precedent)
seat_sha = subprocess.run(
    ["git", "log", "origin/main", "--format=%h", "-n", "1", "--diff-filter=A",
     "--", "fleet/inbox/MSG-2026-10-08-0826-bma-w184-seat.md"],
    capture_output=True).stdout.decode().strip()
check(seat_sha == "d1f15ebf9", "seat sha path-derived mismatch: " + seat_sha)
check(os.path.exists(os.path.join(
    "fleet", "inbox", "processed", "MSG-2026-10-08-0826-bma-w184-seat.md")),
    "seat MSG not in processed/ at freeze time (self-ack archive)")
w183_freeze_sha = subprocess.run(
    ["git", "log", "origin/main", "--format=%h", "-n", "1", "--grep=W183 FREEZE"],
    capture_output=True).stdout.decode().strip()
check(w183_freeze_sha == "481da4d78", "W183 freeze sha mismatch: " + w183_freeze_sha)

# ---- live-registry parity pre-check (edit-gate: never edit a drifted file)
sys.path.insert(0, "scripts")
import perpetual_faces as pfmod  # noqa: E402
check(len(pfmod.N1_BANDS) == 181, "live N1_BANDS row count drift: %d" % len(pfmod.N1_BANDS))
check(pfmod.N1_BANDS[183] == {"a": (417_404, 419_403),
                              "b_exit": (419_404, 419_603),
                              "engine_owner": "bm-a"}, "live W183 row drift")
check(184 not in pfmod.N1_BANDS, "live N1_BANDS already has 184")
check(os.path.exists(os.path.join("research", "PERPETUAL_N1_W184_PREREG.md")),
      "W184 per-wave prereg missing (materializer gate)")
prereg_o = subprocess.run(["git", "show", "origin/main:research/PERPETUAL_N1_W184_PREREG.md"],
                          capture_output=True)
check(prereg_o.returncode == 0, "W184 prereg absent on origin")

# ---- physical face dumps (r776 law) -----------------------------------
pfblk = io.open(r"results\_r874bma_w184_probe_pf_block.txt", encoding="utf-8",
                newline="").read()
entry = io.open(r"results\_r874bma_w184_probe_n1_entry.txt", encoding="utf-8",
                newline="").read()
mat = io.open(r"results\_r874bma_w184_probe_n1_mat.txt", encoding="utf-8",
              newline="").read()
claim = io.open(r"results\_r874bma_w184_probe_n1_claim.txt", encoding="utf-8",
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
    ('    # W183 (bm-a r869 freeze, seat MSG-2026-10-08-0741-bma-w183-seat', '    # W184 (bm-a r874 freeze, seat MSG-2026-10-08-0826-bma-w184-seat', 1),
    ('pushed to origin ccd18034e pre-freeze r565 law (r868 pre-seat', 'pushed to origin d1f15ebf9 pre-freeze r565 law (r870 pre-seat', 1),
    ('(3-item; the W182 finalize product already on origin since r868,', '(3-item; the W183 finalize product already on origin since r870,', 1),
    ('# = direct fast-forward behind-0 at fetch (r868 pre-seat', '# = direct fast-forward behind-0 at fetch (r870 pre-seat', 1),
    ('# push), zero merge, zero --no-verify; self-ack archive ALREADY\r\n    # LANDED pre-freeze -- bm-c r741-window self-ack move (the W183\r\n    # seat MSG sits in fleet/inbox/processed/ at freeze time, honest\r\n    # archived);', '# push), zero merge, zero --no-verify; self-ack archive ALREADY\r\n    # LANDED pre-freeze -- bm-c r745-window self-ack move (the W184\r\n    # seat MSG sits in fleet/inbox/processed/ at freeze time, honest\r\n    # archived);', 1),
    ('band gate ADMIT results/_r868bma_w183_probe_receipt.json: A = FIRST-CLEAN', 'band gate ADMIT results/_r870bma_w184_probe_receipt.json: A = FIRST-CLEAN', 1),
    ('past the registered W182 B band (arithmetic continuation', 'past the registered W183 B band (arithmetic continuation', 1),
    ('417_204..419_203 REFUSED at its own start by the W182 B band', '419_404..421_403 REFUSED at its own start by the W183 B band', 1),
    ('417_204..417_403, exactly as the W182 seat W183+ projection + r865 probe', '419_404..419_603, exactly as the W183 seat W184+ projection + r868 probe', 1),
    ('# leg4 + r868 sec8 same-window succession projection notes all anticipated;', '# leg4 + r870 sec8 same-window succession projection notes all anticipated;', 1),
    ('honest forward walk hops=1 -> 417_404..419_403, non-rotational', 'honest forward walk hops=1 -> 419_604..421_603, non-rotational', 1),
    ('(417_403+1) machine-checkable -- A-hops-prior-B staircase', '(419_603+1) machine-checkable -- A-hops-prior-B staircase', 1),
    ('FORTY-THIRD instance, E36 card);', 'FORTY-FOURTH instance, E36 card);', 1),
    ('continuation 417_404..417_603 CLEAN on the registered universe', 'continuation 419_604..419_803 CLEAN on the registered universe', 1),
    ('but lands INSIDE the W183 A band window -- same-freeze mutual', 'but lands INSIDE the W184 A band window -- same-freeze mutual', 1),
    ('own-wave A window reserved jumps to 419_404 -> 419_404..419_603,', 'own-wave A window reserved jumps to 421_604 -> 421_604..421_803,', 1),
    ('own-wave A tail+1 (419_403+1) machine-checkable);', 'own-wave A tail+1 (421_603+1) machine-checkable);', 1),
    ('W183+ projection (gate-derived r868): A first-clean', 'W184+ projection (gate-derived r870): A first-clean', 1),
    ('419_404..421_403 CLEAN hops=0 / B first-clean 419_604..419_803', '421_604..423_603 CLEAN hops=0 / B first-clean 421_804..422_003', 1),
    ('registered W183 B band 419_404..419_603 will refuse the naive', 'registered W184 B band 421_604..421_803 will refuse the naive', 1),
    ('W184 A window; W184 freezer MUST re-derive on the post-W183', 'W185 A window; W185 freezer MUST re-derive on the post-W184', 1),
    ('NOT a re-pick (R250: W183 bands were never assigned).', 'NOT a re-pick (R250: W184 bands were never assigned).', 1),
    ('183: {"a": (417_404, 419_403), "b_exit": (419_404, 419_603),', '184: {"a": (419_604, 421_603), "b_exit": (421_604, 421_803),', 1),
]

EN_PAIRS = [
    ('183: {"batch": "PERPETUAL-N1-W183",', '184: {"batch": "PERPETUAL-N1-W184",', 1),
    ('"prereg": ("research/PERPETUAL_N1_W183_PREREG.md (wave-level frozen "', '"prereg": ("research/PERPETUAL_N1_W184_PREREG.md (wave-level frozen "', 1),
    ('new seed bands only; ONE HUNDRED-AND-SEVENTY-THIRD ENGINE-OWNED WAVE ', 'new seed bands only; ONE HUNDRED-AND-SEVENTY-FOURTH ENGINE-OWNED WAVE ', 1),
    ('BY MACHINE-DERIVE (engine_owner rows 172 + candidate), ', 'BY MACHINE-DERIVE (engine_owner rows 173 + candidate), ', 1),
    ('number law after the REGISTERED W182 row bm-a r867 freeze ', 'number law after the REGISTERED W183 row bm-a r869 freeze ', 1),
    ('385dbafd8, SINGLE STATE zero seat gap W2..W182 all ', '481da4d78, SINGLE STATE zero seat gap W2..W183 all ', 1),
    ('registered; W183 finalize landed same-window r827, ledger ', 'registered; W184 finalize landed same-window r827, ledger ', 1),
    ('head 806,718, merged pool K=398,320; seat published=reserved ', 'head 808,918, merged pool K=400,520; seat published=reserved ', 1),
    ('MSG-2026-10-08-0741-bma-w183-seat PUSHED to origin ccd18034e ', 'MSG-2026-10-08-0826-bma-w184-seat PUSHED to origin d1f15ebf9 ', 1),
    ('probe receipt (3-item; the W182 finalize product already on origin since r868, not re-shipped; W146 precedent); ', 'probe receipt (3-item; the W183 finalize product already on origin since r870, not re-shipped; W146 precedent); ', 1),
    ('at fetch (r868 pre-seat push), zero merge, zero ', 'at fetch (r870 pre-seat push), zero merge, zero ', 1),
    ('engine_owner=bm-a, wave 182: ', 'engine_owner=bm-a, wave 183: ', 1),
    ('A = FIRST-CLEAN past the registered W182 B band (the ', 'A = FIRST-CLEAN past the registered W183 B band (the ', 1),
    ('arithmetic continuation 417_204..419_203 is REFUSED at its ', 'arithmetic continuation 419_404..421_403 is REFUSED at its ', 1),
    ('own start by the W182 B band 417_204..417_403, exactly as ', 'own start by the W183 B band 419_404..419_603, exactly as ', 1),
    ('the W182 seat W183+ projection + r865 probe leg4 + r868 sec8 same-window succession ', 'the W183 seat W184+ projection + r868 probe leg4 + r870 sec8 same-window succession ', 1),
    ('projection notes anticipated; honest forward walk hops=1 -> ', 'projection notes anticipated; honest forward walk hops=1 -> ', 1),
    ('417_404..419_403; A base == prior-wave B tail+1 ', '419_604..421_603; A base == prior-wave B tail+1 ', 1),
    ('machine-checkable = A-hops-prior-B staircase FORTY-THIRD ', 'machine-checkable = A-hops-prior-B staircase FORTY-FOURTH ', 1),
    ('arithmetic continuation 417_404..417_603 is CLEAN on the ', 'arithmetic continuation 419_604..419_803 is CLEAN on the ', 1),
    ('registered universe but lands INSIDE the W183 A band ', 'registered universe but lands INSIDE the W184 A band ', 1),
    ('jumps to 419_404, first-clean 419_404..419_603 hops=1, ', 'jumps to 421_604, first-clean 421_604..421_803 hops=1, ', 1),
    ('convergence with the W182 seat W183+ projection + r865 probe leg4 + ', 'convergence with the W183 seat W184+ projection + r868 probe leg4 + ', 1),
    ('r868 sec8 same-window succession projection notes re-derived -- all ', 'r870 sec8 same-window succession projection notes re-derived -- all ', 1),
    ('MANDATORY notes honored (post-W182 universe re-derive + ', 'MANDATORY notes honored (post-W183 universe re-derive + ', 1),
    ('results/_r868bma_w183_probe_receipt.json; W184+ projection ', 'results/_r870bma_w184_probe_receipt.json; W185+ projection ', 1),
    ('per this window gate: A first-clean 419_404..421_403 ', 'per this window gate: A first-clean 421_604..423_603 ', 1),
    ('CLEAN / B first-clean 419_604..419_803 CLEAN -- naive ', 'CLEAN / B first-clean 421_804..422_003 CLEAN -- naive ', 1),
    ('W183 B band 419_404..419_603 will refuse the naive ', 'W184 B band 421_604..421_803 will refuse the naive ', 1),
    ('W184 A window; W184 freezer MUST re-derive on the ', 'W185 A window; W185 freezer MUST re-derive on the ', 1),
    ('post-W183 universe AND reserve the own-wave A window ', 'post-W184 universe AND reserve the own-wave A window ', 1),
    ('staircase card); W1..W182 finalize ALL LANDED (W182 ', 'staircase card); W1..W183 finalize ALL LANDED (W183 ', 1),
    ('finalize one-pass bm-a r868, net chain head 806,718, ', 'finalize one-pass bm-a r870, net chain head 808,918, ', 1),
    ('merged pool K=398,320) -- ZERO in-flight upstream ', 'merged pool K=400,520) -- ZERO in-flight upstream ', 1),
    ('"a_seed_base": 417_404,        # law sec.4 W183 A: 417_404..419_403 (FIRST-CLEAN past the registered W182 B band; arithmetic 417_204..419_203 REFUSED at own start by the W182 B band; hops=1; A-hops-prior-B staircase FORTY-THIRD instance, E36 card; ordinal convergence per r587: W182 sec5.5 prose anticipated forty-third, r868 receipt machine-read FORTY-THIRD)', '"a_seed_base": 419_604,        # law sec.4 W184 A: 419_604..421_603 (FIRST-CLEAN past the registered W183 B band; arithmetic 419_404..421_403 REFUSED at own start by the W183 B band; hops=1; A-hops-prior-B staircase FORTY-FOURTH instance, E36 card; ordinal convergence per r587: W183 sec5.5 prose anticipated forty-fourth, r870 receipt machine-read FORTY-FOURTH)', 1),
    ('"b_exit_seed_base": 419_404,   # law sec.4 W183 B: 419_404..419_603 (FIRST-CLEAN past the own-wave A window; arithmetic 417_404..417_603 lands inside own-A, same-freeze mutual exclusion W141 precedent; reserved walk hops=1; B base == own-A tail+1)', '"b_exit_seed_base": 421_604,   # law sec.4 W184 B: 421_604..421_803 (FIRST-CLEAN past the own-wave A window; arithmetic 419_604..419_803 lands inside own-A, same-freeze mutual exclusion W141 precedent; reserved walk hops=1; B base == own-A tail+1)', 1),
    ('"shard_subdir": "n1_w183", "out_name": "n1_w183_results.json",', '"shard_subdir": "n1_w184", "out_name": "n1_w184_results.json",', 1),
]

MAT_PAIRS = [
    ('# --- W183 materializer face (r869 bm-a freeze, own-series law', '# --- W184 materializer face (r874 bm-a freeze, own-series law', 1),
    ('#     ninety-ninth owned per machine-derive (engine_owner==bm-a', '#     one-hundredth owned per machine-derive (engine_owner==bm-a', 1),
    ('#     rows 98 + candidate); wave 182 = first free number after', '#     rows 99 + candidate); wave 183 = first free number after', 1),
    ('#     the REGISTERED W182 row (bm-a r867 freeze 385dbafd8) --', '#     the REGISTERED W183 row (bm-a r869 freeze 481da4d78) --', 1),
    ('#     SINGLE STATE zero seat gap (W2..W182 all registered). Seat', '#     SINGLE STATE zero seat gap (W2..W183 all registered). Seat', 1),
    ('#     published=reserved MSG-2026-10-08-0741-bma-w183-seat pushed', '#     published=reserved MSG-2026-10-08-0826-bma-w184-seat pushed', 1),
    ('#     to origin ccd18034e BEFORE this freeze, r565 law (payload', '#     to origin d1f15ebf9 BEFORE this freeze, r565 law (payload', 1),
    ('#     the W182 finalize product already on origin since r868, not', '#     the W183 finalize product already on origin since r870, not', 1),
    ('#     at fetch (r868 pre-seat push), zero merge, zero', '#     at fetch (r870 pre-seat push), zero merge, zero', 1),
    ('#     --no-verify; self-ack inbox->processed archive ALREADY LANDED\r\n    #     pre-freeze -- bm-c r741-window self-ack move (the W183 seat\r\n    #     MSG sits in fleet/inbox/processed/ at freeze time, honest\r\n    #     archived).', '#     --no-verify; self-ack inbox->processed archive ALREADY LANDED\r\n    #     pre-freeze -- bm-c r745-window self-ack move (the W184 seat\r\n    #     MSG sits in fleet/inbox/processed/ at freeze time, honest\r\n    #     archived).', 1),
    ('#     ONE HUNDRED-AND-SEVENTY-THIRD engine wave BY', '#     ONE HUNDRED-AND-SEVENTY-FOURTH engine wave BY', 1),
    ('#     MACHINE-DERIVE (engine_owner rows 172 + candidate; gate', '#     MACHINE-DERIVE (engine_owner rows 173 + candidate; gate', 1),
    ('#     W1..W182 finalize ALL LANDED (net chain head 806,718,', '#     W1..W183 finalize ALL LANDED (net chain head 808,918,', 1),
    ('#     K=398,320 merged pool; W182 finalize one-pass bm-a r868)', '#     K=400,520 merged pool; W183 finalize one-pass bm-a r870)', 1),
    ('#     always on. ADMIT receipt results/_r868bma_w183_probe_receipt.json;', '#     always on. ADMIT receipt results/_r870bma_w184_probe_receipt.json;', 1),
    ('#     banned gate ADMIT 0; not a re-pick (R250: W183 bands were', '#     banned gate ADMIT 0; not a re-pick (R250: W184 bands were', 1),
    ('    _set_wave(183)', '    _set_wave(184)', 1),
    ('assert WAVE_CONFIGS[182]["a_seed_base"] == pf.N1_BANDS[182]["a"][0], \\', 'assert WAVE_CONFIGS[183]["a_seed_base"] == pf.N1_BANDS[183]["a"][0], \\', 1),
    ('"W183 A band drift vs law mirror"', '"W184 A band drift vs law mirror"', 1),
    ('assert WAVE_CONFIGS[182]["b_exit_seed_base"] == \\', 'assert WAVE_CONFIGS[183]["b_exit_seed_base"] == \\', 1),
    ('pf.N1_BANDS[182]["b_exit"][0], "W183 B band drift vs law mirror"', 'pf.N1_BANDS[183]["b_exit"][0], "W184 B band drift vs law mirror"', 1),
    ('assert WAVE_CONFIGS[182].get("engine_owner") == \\', 'assert WAVE_CONFIGS[183].get("engine_owner") == \\', 1),
    ('pf.N1_BANDS[182].get("engine_owner") == "bm-a", \\', 'pf.N1_BANDS[183].get("engine_owner") == "bm-a", \\', 1),
    ('"W183 engine_owner drift (law mirror parity)"', '"W184 engine_owner drift (law mirror parity)"', 1),
    ('w182_a = {A_SEED_BASE + j for j in range(A_N)}', 'w183_a = {A_SEED_BASE + j for j in range(A_N)}', 1),
    ('w182_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}', 'w183_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}', 1),
    ('assert not (w182_a & w182_b), "W183 A/B band overlap"', 'assert not (w183_a & w183_b), "W184 A/B band overlap"', 1),
    ('assert not (w182_a & reg_ints) and not (w182_b & reg_ints), \\', 'assert not (w183_a & reg_ints) and not (w183_b & reg_ints), \\', 1),
    ('"W183 hits SEED_REGISTRY"', '"W184 hits SEED_REGISTRY"', 1),
    ('for nm, band in (("A", w182_a), ("B", w182_b)):', 'for nm, band in (("A", w183_a), ("B", w183_b)):', 1),
    ('f"W183 {nm} hits v1"', 'f"W184 {nm} hits v1"', 1),
    ('f"W183 {nm} hits W1"', 'f"W184 {nm} hits W1"', 1),
    ('f"W183 {nm} hits probe seeds"', 'f"W184 {nm} hits probe seeds"', 1),
    ('"registered W182 row parity drift (r307; bm-a r867)"', '"registered W182 row parity drift (r307; bm-a r867)"\r\n        assert pf.N1_BANDS[183] == {"a": (417_404, 419_403),\r\n                                    "b_exit": (419_404, 419_603),\r\n                                    "engine_owner": "bm-a"}, \\\r\n            "registered W183 row parity drift (r307; bm-a r869)"', 1),
    ('# prior-wave disjointness W2..W182 (single state: all', '# prior-wave disjointness W2..W183 (single state: all', 1),
    ('for wprev in sorted(w for w in WAVE_CONFIGS if w < 183):', 'for wprev in sorted(w for w in WAVE_CONFIGS if w < 184):', 2),
    ('assert not (w182_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j', 'assert not (w183_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j', 1),
    ('for j in range(A_N)}), f"W183 A hits W{wprev}"', 'for j in range(A_N)}), f"W184 A hits W{wprev}"', 1),
    ('assert not (w182_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j', 'assert not (w183_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j', 1),
    ('for j in range(B_N)}), f"W183 B hits W{wprev}"', 'for j in range(B_N)}), f"W184 B hits W{wprev}"', 1),
    ('n3r1_used182 = set(range(70_000, 70_006))', 'n3r1_used183 = set(range(70_000, 70_006))', 1),
    ('assert not (w182_a & n3r1_used182) and not (w182_b & n3r1_used182), \\', 'assert not (w183_a & n3r1_used183) and not (w183_b & n3r1_used183), \\', 1),
    ('"W183 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"', '"W184 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"', 1),
    ('assert not (w182_a & lfc_actual12) and not (w182_b & lfc_actual12), \\', 'assert not (w183_a & lfc_actual12) and not (w183_b & lfc_actual12), \\', 1),
    ('"W183 bands must clear the lfc actual draw range"', '"W184 bands must clear the lfc actual draw range"', 1),
    ('assert not (w182_a & options_actual12) and \\', 'assert not (w183_a & options_actual12) and \\', 1),
    ('not (w182_b & options_actual12), \\', 'not (w183_b & options_actual12), \\', 1),
    ('"W183 bands must clear the options_wave2 actual draw range"', '"W184 bands must clear the options_wave2 actual draw range"', 1),
    ('# band facts (law sec.4 W183 row, r795): A = FIRST-CLEAN past', '# band facts (law sec.4 W184 row, r795): A = FIRST-CLEAN past', 1),
    ('# the registered W182 B band (the arithmetic continuation', '# the registered W183 B band (the arithmetic continuation', 1),
    ('# 417_204..419_203 is REFUSED at its own start by the W182', '# 419_404..421_403 is REFUSED at its own start by the W183', 1),
    ('# B band 417_204..417_403, exactly as the W182 seat W183+ projection +', '# B band 419_404..419_603, exactly as the W183 seat W184+ projection +', 1),
    ('# r865 probe leg4 + r868 sec8 same-window succession projection notes', '# r868 probe leg4 + r870 sec8 same-window succession projection notes', 1),
    ('# 417_404..419_403; A base == prior-wave B tail+1 (417_403+1)', '# 419_604..421_603; A base == prior-wave B tail+1 (419_603+1)', 1),
    ('# machine-checkable -- A-hops-prior-B staircase FORTY-THIRD', '# machine-checkable -- A-hops-prior-B staircase FORTY-FOURTH', 1),
    ('# continuation 417_404..417_603 is CLEAN on the registered', '# continuation 419_604..419_803 is CLEAN on the registered', 1),
    ('# universe but lands INSIDE the W183 A band window --', '# universe but lands INSIDE the W184 A band window --', 1),
    ('# 419_404 and lands 419_404..419_603, hops=1, non-rotational', '# 421_604 and lands 421_604..421_803, hops=1, non-rotational', 1),
    ('# (419_403+1) machine-checkable; cross-window convergence', '# (421_603+1) machine-checkable; cross-window convergence', 1),
    ('# with the W182 seat W183+ projection + r865 probe leg4 + r868 sec8', '# with the W183 seat W184+ projection + r868 probe leg4 + r870 sec8', 1),
    ('# honored (post-W182 universe re-derive + own-wave A', '# honored (post-W183 universe re-derive + own-wave A', 1),
    ('# reservation when deriving B); seat MSG-0741 tail,', '# reservation when deriving B); seat MSG-0826 tail,', 1),
    ('assert WAVE_CONFIGS[183]["a_seed_base"] == 417_404 == 417_403 + 1, (', 'assert WAVE_CONFIGS[184]["a_seed_base"] == 419_604 == 419_603 + 1, (', 1),
    ('"W183 A must be the first-clean window past the registered "', '"W184 A must be the first-clean window past the registered "', 1),
    ('"W182 B band tail 417_403+1 (arithmetic continuation "', '"W183 B band tail 419_603+1 (arithmetic continuation "', 1),
    ('"417_204..419_203 REFUSED at its own start by the W182 B "', '"419_404..421_403 REFUSED at its own start by the W183 B "', 1),
    ('"band 417_204..417_403, exactly as the W182 seat W183+ projection + "', '"band 419_404..419_603, exactly as the W183 seat W184+ projection + "', 1),
    ('"r865 probe leg4 + r868 sec8 same-window succession projection notes "', '"r868 probe leg4 + r870 sec8 same-window succession projection notes "', 1),
    ('"staircase FORTY-THIRD instance, E36 card)"', '"staircase FORTY-FOURTH instance, E36 card)"', 1),
    ('arith_a182 = set(range(417_404, 419_404))', 'arith_a183 = set(range(419_604, 421_604))', 1),
    ('assert not (arith_a182 & reg_ints), \\', 'assert not (arith_a183 & reg_ints), \\', 1),
    ('"W183 A window must be CLEAN (first-clean ADMIT face past prior-wave B)"', '"W184 A window must be CLEAN (first-clean ADMIT face past prior-wave B)"', 1),
    ('assert WAVE_CONFIGS[183]["b_exit_seed_base"] == 419_404 == 419_403 + 1, (', 'assert WAVE_CONFIGS[184]["b_exit_seed_base"] == 421_604 == 421_603 + 1, (', 1),
    ('"W183 B must be the first-clean window past the own-wave A "', '"W184 B must be the first-clean window past the own-wave A "', 1),
    ('"band tail 419_403+1 (arithmetic continuation "', '"band tail 421_603+1 (arithmetic continuation "', 1),
    ('"417_404..417_603 CLEAN on the registered universe but "', '"419_604..419_803 CLEAN on the registered universe but "', 1),
    ('"lands INSIDE the W183 A band window; same-freeze mutual "', '"lands INSIDE the W184 A band window; same-freeze mutual "', 1),
    ('"own-wave A window reserved jumps to 419_404, first-clean "', '"own-wave A window reserved jumps to 421_604, first-clean "', 1),
    ('arith_b182 = set(range(419_404, 419_604))', 'arith_b183 = set(range(421_604, 421_804))', 1),
    ('assert not (arith_b182 & reg_ints), \\', 'assert not (arith_b183 & reg_ints), \\', 1),
    ('"W183 B window must be CLEAN (first-clean ADMIT face past own-wave A)"', '"W184 B window must be CLEAN (first-clean ADMIT face past own-wave A)"', 1),
    ('assert not (arith_b182 & arith_a182), \\', 'assert not (arith_b183 & arith_a183), \\', 1),
    ('"W183 A/B same-freeze mutual exclusion (B hops past own A)"', '"W184 A/B same-freeze mutual exclusion (B hops past own A)"', 1),
    ('assert _entry_shard_of(0, 12) == ("PERPETUAL-N1-W183-SHARD-0",', 'assert _entry_shard_of(0, 12) == ("PERPETUAL-N1-W184-SHARD-0",', 1),
    ('"n1w183-0of12"), "W183 entry identity"', '"n1w184-0of12"), "W184 entry identity"', 1),
    ('assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W183-SHARD-11",', 'assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W184-SHARD-11",', 1),
    ('"n1w183-11of12")', '"n1w184-11of12")', 1),
    ('assert SHARD_DIR.endswith("n1_w183") and OUT.endswith(', 'assert SHARD_DIR.endswith("n1_w184") and OUT.endswith(', 1),
    ('"n1_w183_results.json"), "W183 path drift"', '"n1_w184_results.json"), "W184 path drift"', 1),
    ('f"W183 shard dir collides with W{wprev}"', 'f"W184 shard dir collides with W{wprev}"', 1),
    ('# W183 finalize cumulative deps: W17..W182 outputs ALL PRESENT', '# W184 finalize cumulative deps: W17..W183 outputs ALL PRESENT', 1),
    ('# (landed net chain head 806,718 = W182 bm-a r868 one-pass --', '# (landed net chain head 808,918 = W183 bm-a r870 one-pass --', 1),
    ('for _depw in range(17, 183):', 'for _depw in range(17, 184):', 1),
    ('f"W183 finalize cumulative dep (W{_depw} output) missing"', 'f"W184 finalize cumulative dep (W{_depw} output) missing"', 1),
    ('# registered wave below 183 composes; wave 15 excluded by', '# registered wave below 184 composes; wave 15 excluded by', 1),
    ('# design; SINGLE STATE (W2..W182 all registered -- no', '# design; SINGLE STATE (W2..W183 all registered -- no', 1),
    ('assert sorted(w for w in WAVE_CONFIGS if w < 183) == \\', 'assert sorted(w for w in WAVE_CONFIGS if w < 184) == \\', 1),
    ('[w for w in range(16, 183)], \\', '[w for w in range(16, 184)], \\', 1),
    ('"W183 prior-wave set must derive from registry keys (no 15; "', '"W184 prior-wave set must derive from registry keys (no 15; "', 1),
    ('"W2..W182 registered single state)"', '"W2..W183 registered single state)"', 1),
    ('PATHS.root, "research", "PERPETUAL_N1_W183_PREREG.md")), \\', 'PATHS.root, "research", "PERPETUAL_N1_W184_PREREG.md")), \\', 1),
    ('"W183 per-wave prereg missing (materializer requirement)"', '"W184 per-wave prereg missing (materializer requirement)"', 1),
]

CL_PAIRS = [
    ('"+ W183 materializer face [same guard set, dep=W17..W182 ', '"+ W184 materializer face [same guard set, dep=W17..W183 ', 1),
    ('"outputs ALL PRESENT (landed net chain head 806,718 = "', '"outputs ALL PRESENT (landed net chain head 808,918 = "', 1),
    ('"W182 bm-a r868 one-pass, K=398,320 merged pool; ZERO "', '"W183 bm-a r870 one-pass, K=400,520 merged pool; ZERO "', 1),
    ('"in-flight upstream seats), ONE HUNDRED-AND-SEVENTY-THIRD "', '"in-flight upstream seats), ONE HUNDRED-AND-SEVENTY-FOURTH "', 1),
    ('"ENGINE-OWNED WAVE BY MACHINE-DERIVE (engine_owner rows 172 "', '"ENGINE-OWNED WAVE BY MACHINE-DERIVE (engine_owner rows 173 "', 1),
    ("+ candidate) bm-a's ninety-ninth owned claim per ", "+ candidate) bm-a's one-hundredth owned claim per ", 1),
    ('"machine-derive (engine_owner==bm-a rows 98 + candidate), "', '"machine-derive (engine_owner==bm-a rows 99 + candidate), "', 1),
    ('"A=FIRST-CLEAN past the registered W182 B band (staircase "', '"A=FIRST-CLEAN past the registered W183 B band (staircase "', 1),
    ('"FORTY-THIRD instance, E36 card, hops=1) + B=FIRST-CLEAN past the "', '"FORTY-FOURTH instance, E36 card, hops=1) + B=FIRST-CLEAN past the "', 1),
    ('"results/_r868bma_w183_probe_receipt.json, law sec.4 W183 row, "', '"results/_r870bma_w184_probe_receipt.json, law sec.4 W184 row, "', 1),
    ('"r869 bm-a] "', '"r874 bm-a] "', 1),
]

PF_NEG = ['    # W183 (bm-a r869 freeze, seat MSG-2026-10-08-0741-bma-w183-seat', 'pushed to origin ccd18034e pre-freeze r565 law (r868 pre-seat', '(3-item; the W182 finalize product already on origin since r868,', '# = direct fast-forward behind-0 at fetch (r868 pre-seat', '# push), zero merge, zero --no-verify; self-ack archive ALREADY\r\n    # LANDED pre-freeze -- bm-c r741-window self-ack move (the W183\r\n    # seat MSG sits in fleet/inbox/processed/ at freeze time, honest\r\n    # archived);', 'band gate ADMIT results/_r868bma_w183_probe_receipt.json: A = FIRST-CLEAN', 'past the registered W182 B band (arithmetic continuation', '417_204..419_203 REFUSED at its own start by the W182 B band', '417_204..417_403, exactly as the W182 seat W183+ projection + r865 probe', '# leg4 + r868 sec8 same-window succession projection notes all anticipated;', 'honest forward walk hops=1 -> 417_404..419_403, non-rotational', '(417_403+1) machine-checkable -- A-hops-prior-B staircase', 'FORTY-THIRD instance, E36 card);', 'continuation 417_404..417_603 CLEAN on the registered universe', 'but lands INSIDE the W183 A band window -- same-freeze mutual', 'own-wave A window reserved jumps to 419_404 -> 419_404..419_603,', 'own-wave A tail+1 (419_403+1) machine-checkable);', 'W183+ projection (gate-derived r868): A first-clean', '419_404..421_403 CLEAN hops=0 / B first-clean 419_604..419_803', 'registered W183 B band 419_404..419_603 will refuse the naive', 'W184 A window; W184 freezer MUST re-derive on the post-W183', 'NOT a re-pick (R250: W183 bands were never assigned).', '183: {"a": (417_404, 419_403), "b_exit": (419_404, 419_603),', 'ccd18034e', 'r865 probe', 'r868 sec8', 'r868 pre-seat', '_r868bma', 'MSG-2026-10-08-0741', '385dbafd8', '806,718', '398,320', 'FORTY-THIRD', 'ONE HUNDRED-AND-SEVENTY-THIRD']

EN_NEG = ['183: {"batch": "PERPETUAL-N1-W183",', '"prereg": ("research/PERPETUAL_N1_W183_PREREG.md (wave-level frozen "', 'new seed bands only; ONE HUNDRED-AND-SEVENTY-THIRD ENGINE-OWNED WAVE ', 'BY MACHINE-DERIVE (engine_owner rows 172 + candidate), ', 'number law after the REGISTERED W182 row bm-a r867 freeze ', '385dbafd8, SINGLE STATE zero seat gap W2..W182 all ', 'registered; W183 finalize landed same-window r827, ledger ', 'head 806,718, merged pool K=398,320; seat published=reserved ', 'MSG-2026-10-08-0741-bma-w183-seat PUSHED to origin ccd18034e ', 'probe receipt (3-item; the W182 finalize product already on origin since r868, not re-shipped; W146 precedent); ', 'at fetch (r868 pre-seat push), zero merge, zero ', 'engine_owner=bm-a, wave 182: ', 'A = FIRST-CLEAN past the registered W182 B band (the ', 'arithmetic continuation 417_204..419_203 is REFUSED at its ', 'own start by the W182 B band 417_204..417_403, exactly as ', 'the W182 seat W183+ projection + r865 probe leg4 + r868 sec8 same-window succession ', '417_404..419_403; A base == prior-wave B tail+1 ', 'machine-checkable = A-hops-prior-B staircase FORTY-THIRD ', 'arithmetic continuation 417_404..417_603 is CLEAN on the ', 'registered universe but lands INSIDE the W183 A band ', 'jumps to 419_404, first-clean 419_404..419_603 hops=1, ', 'convergence with the W182 seat W183+ projection + r865 probe leg4 + ', 'r868 sec8 same-window succession projection notes re-derived -- all ', 'MANDATORY notes honored (post-W182 universe re-derive + ', 'results/_r868bma_w183_probe_receipt.json; W184+ projection ', 'per this window gate: A first-clean 419_404..421_403 ', 'CLEAN / B first-clean 419_604..419_803 CLEAN -- naive ', 'W183 B band 419_404..419_603 will refuse the naive ', 'W184 A window; W184 freezer MUST re-derive on the ', 'post-W183 universe AND reserve the own-wave A window ', 'staircase card); W1..W182 finalize ALL LANDED (W182 ', 'finalize one-pass bm-a r868, net chain head 806,718, ', 'merged pool K=398,320) -- ZERO in-flight upstream ', '"a_seed_base": 417_404,        # law sec.4 W183 A: 417_404..419_403 (FIRST-CLEAN past the registered W182 B band; arithmetic 417_204..419_203 REFUSED at own start by the W182 B band; hops=1; A-hops-prior-B staircase FORTY-THIRD instance, E36 card; ordinal convergence per r587: W182 sec5.5 prose anticipated forty-third, r868 receipt machine-read FORTY-THIRD)', '"b_exit_seed_base": 419_404,   # law sec.4 W183 B: 419_404..419_603 (FIRST-CLEAN past the own-wave A window; arithmetic 417_404..417_603 lands inside own-A, same-freeze mutual exclusion W141 precedent; reserved walk hops=1; B base == own-A tail+1)', '"shard_subdir": "n1_w183", "out_name": "n1_w183_results.json",', '385dbafd8', 'ccd18034e', '806,718', '398,320', 'ONE HUNDRED-AND-SEVENTY-THIRD', 'rows 172', 'r865 probe', '_r868bma', 'MSG-2026-10-08-0741', 'n1w183', 'n1_w183', 'PERPETUAL-N1-W183', 'PERPETUAL_N1_W183', 'FORTY-THIRD', 'bm-a r867 freeze', '419_404, first-clean']

MAT_NEG = ['# --- W183 materializer face (r869 bm-a freeze, own-series law', '#     ninety-ninth owned per machine-derive (engine_owner==bm-a', '#     rows 98 + candidate); wave 182 = first free number after', '#     the REGISTERED W182 row (bm-a r867 freeze 385dbafd8) --', '#     SINGLE STATE zero seat gap (W2..W182 all registered). Seat', '#     published=reserved MSG-2026-10-08-0741-bma-w183-seat pushed', '#     to origin ccd18034e BEFORE this freeze, r565 law (payload', '#     the W182 finalize product already on origin since r868, not', '#     at fetch (r868 pre-seat push), zero merge, zero', '#     --no-verify; self-ack inbox->processed archive ALREADY LANDED\r\n    #     pre-freeze -- bm-c r741-window self-ack move (the W183 seat\r\n    #     MSG sits in fleet/inbox/processed/ at freeze time, honest\r\n    #     archived).', '#     ONE HUNDRED-AND-SEVENTY-THIRD engine wave BY', '#     MACHINE-DERIVE (engine_owner rows 172 + candidate; gate', '#     W1..W182 finalize ALL LANDED (net chain head 806,718,', '#     K=398,320 merged pool; W182 finalize one-pass bm-a r868)', '#     always on. ADMIT receipt results/_r868bma_w183_probe_receipt.json;', '#     banned gate ADMIT 0; not a re-pick (R250: W183 bands were', '    _set_wave(183)', 'assert WAVE_CONFIGS[182]["a_seed_base"] == pf.N1_BANDS[182]["a"][0], \\', '"W183 A band drift vs law mirror"', 'assert WAVE_CONFIGS[182]["b_exit_seed_base"] == \\', 'pf.N1_BANDS[182]["b_exit"][0], "W183 B band drift vs law mirror"', 'assert WAVE_CONFIGS[182].get("engine_owner") == \\', 'pf.N1_BANDS[182].get("engine_owner") == "bm-a", \\', '"W183 engine_owner drift (law mirror parity)"', 'w182_a = {A_SEED_BASE + j for j in range(A_N)}', 'w182_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}', 'assert not (w182_a & w182_b), "W183 A/B band overlap"', 'assert not (w182_a & reg_ints) and not (w182_b & reg_ints), \\', '"W183 hits SEED_REGISTRY"', 'for nm, band in (("A", w182_a), ("B", w182_b)):', 'f"W183 {nm} hits v1"', 'f"W183 {nm} hits W1"', 'f"W183 {nm} hits probe seeds"', '# prior-wave disjointness W2..W182 (single state: all', 'for wprev in sorted(w for w in WAVE_CONFIGS if w < 183):', 'assert not (w182_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j', 'for j in range(A_N)}), f"W183 A hits W{wprev}"', 'assert not (w182_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j', 'for j in range(B_N)}), f"W183 B hits W{wprev}"', 'n3r1_used182 = set(range(70_000, 70_006))', 'assert not (w182_a & n3r1_used182) and not (w182_b & n3r1_used182), \\', '"W183 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"', 'assert not (w182_a & lfc_actual12) and not (w182_b & lfc_actual12), \\', '"W183 bands must clear the lfc actual draw range"', 'assert not (w182_a & options_actual12) and \\', 'not (w182_b & options_actual12), \\', '"W183 bands must clear the options_wave2 actual draw range"', '# band facts (law sec.4 W183 row, r795): A = FIRST-CLEAN past', '# the registered W182 B band (the arithmetic continuation', '# 417_204..419_203 is REFUSED at its own start by the W182', '# B band 417_204..417_403, exactly as the W182 seat W183+ projection +', '# r865 probe leg4 + r868 sec8 same-window succession projection notes', '# 417_404..419_403; A base == prior-wave B tail+1 (417_403+1)', '# machine-checkable -- A-hops-prior-B staircase FORTY-THIRD', '# continuation 417_404..417_603 is CLEAN on the registered', '# universe but lands INSIDE the W183 A band window --', '# 419_404 and lands 419_404..419_603, hops=1, non-rotational', '# (419_403+1) machine-checkable; cross-window convergence', '# with the W182 seat W183+ projection + r865 probe leg4 + r868 sec8', '# honored (post-W182 universe re-derive + own-wave A', '# reservation when deriving B); seat MSG-0741 tail,', 'assert WAVE_CONFIGS[183]["a_seed_base"] == 417_404 == 417_403 + 1, (', '"W183 A must be the first-clean window past the registered "', '"W182 B band tail 417_403+1 (arithmetic continuation "', '"417_204..419_203 REFUSED at its own start by the W182 B "', '"band 417_204..417_403, exactly as the W182 seat W183+ projection + "', '"r865 probe leg4 + r868 sec8 same-window succession projection notes "', '"staircase FORTY-THIRD instance, E36 card)"', 'arith_a182 = set(range(417_404, 419_404))', 'assert not (arith_a182 & reg_ints), \\', '"W183 A window must be CLEAN (first-clean ADMIT face past prior-wave B)"', 'assert WAVE_CONFIGS[183]["b_exit_seed_base"] == 419_404 == 419_403 + 1, (', '"W183 B must be the first-clean window past the own-wave A "', '"band tail 419_403+1 (arithmetic continuation "', '"417_404..417_603 CLEAN on the registered universe but "', '"lands INSIDE the W183 A band window; same-freeze mutual "', '"own-wave A window reserved jumps to 419_404, first-clean "', 'arith_b182 = set(range(419_404, 419_604))', 'assert not (arith_b182 & reg_ints), \\', '"W183 B window must be CLEAN (first-clean ADMIT face past own-wave A)"', 'assert not (arith_b182 & arith_a182), \\', '"W183 A/B same-freeze mutual exclusion (B hops past own A)"', 'assert _entry_shard_of(0, 12) == ("PERPETUAL-N1-W183-SHARD-0",', '"n1w183-0of12"), "W183 entry identity"', 'assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W183-SHARD-11",', '"n1w183-11of12")', 'assert SHARD_DIR.endswith("n1_w183") and OUT.endswith(', '"n1_w183_results.json"), "W183 path drift"', 'f"W183 shard dir collides with W{wprev}"', '# W183 finalize cumulative deps: W17..W182 outputs ALL PRESENT', '# (landed net chain head 806,718 = W182 bm-a r868 one-pass --', 'for _depw in range(17, 183):', 'f"W183 finalize cumulative dep (W{_depw} output) missing"', '# registered wave below 183 composes; wave 15 excluded by', '# design; SINGLE STATE (W2..W182 all registered -- no', 'assert sorted(w for w in WAVE_CONFIGS if w < 183) == \\', '[w for w in range(16, 183)], \\', '"W183 prior-wave set must derive from registry keys (no 15; "', '"W2..W182 registered single state)"', 'PATHS.root, "research", "PERPETUAL_N1_W183_PREREG.md")), \\', '"W183 per-wave prereg missing (materializer requirement)"', 'w182_', 'arith_a182', 'arith_b182', 'n3r1_used182', 'r865 probe', 'r868 pre-seat', '385dbafd8', 'ONE HUNDRED-AND-SEVENTY-THIRD', 'ninety-ninth', 'rows 172', 'rows 98 ', 'range(17, 183)', 'range(16, 183)', 'PERPETUAL_N1_W183', 'PERPETUAL-N1-W183', 'MSG-0741', '_r868bma', 'bm-c r741-window', 'n1w183', 'n1_w183', '806,718', '398,320']

CL_NEG = ['"+ W183 materializer face [same guard set, dep=W17..W182 ', '"outputs ALL PRESENT (landed net chain head 806,718 = "', '"W182 bm-a r868 one-pass, K=398,320 merged pool; ZERO "', '"in-flight upstream seats), ONE HUNDRED-AND-SEVENTY-THIRD "', '"ENGINE-OWNED WAVE BY MACHINE-DERIVE (engine_owner rows 172 "', "+ candidate) bm-a's ninety-ninth owned claim per ", '"machine-derive (engine_owner==bm-a rows 98 + candidate), "', '"A=FIRST-CLEAN past the registered W182 B band (staircase "', '"FORTY-THIRD instance, E36 card, hops=1) + B=FIRST-CLEAN past the "', '"results/_r868bma_w183_probe_receipt.json, law sec.4 W183 row, "', '"r869 bm-a] "', '806,718', '398,320', 'ONE HUNDRED-AND-SEVENTY-THIRD', 'ninety-ninth', 'rows 172', 'rows 98 ', 'FORTY-THIRD', '_r868bma', 'r869 bm-a] ']

blk184 = vmap(pfblk, PF_PAIRS, PF_NEG, "pf")
entry184 = IND23 + vmap(entry, EN_PAIRS, EN_NEG, "entry")
mat184 = "    " + vmap(mat, MAT_PAIRS, MAT_NEG, "mat")
claim184 = IND10 + vmap(claim, CL_PAIRS, CL_NEG, "claim")

# ---- apply insertions (in-memory) ---------------------------------------
pfsrc = io.open(PF, encoding="utf-8", newline="").read()
n1src = io.open(N1, encoding="utf-8", newline="").read()

# pf: insert W184 block after the W183 row (last registered), before the
# dict close -- r560 insert-after-last-registered-row + post-anchor gate
seg = EO + NL + "}"
check(pfsrc.count(seg) == 1, "pf row-close segment not unique")
pfnew = pfsrc.replace(seg, EO + NL + blk184 + NL + "}", 1)

# n1 entry: after the W183 entry, before the WAVE_CONFIGS close
seg = EO + NL + IND23 + "}"
check(n1src.count(seg) == 1, "n1 entry-close segment not unique")
n1new = n1src.replace(seg, EO + NL + entry184 + NL + IND23 + "}", 1)

# n1 mat: insert the W184 block before the T-141 s2 lane face header
seg = "    # --- T-141 s2 lane face"
check(n1new.count(seg) == 1, "n1 T-141 mat anchor not unique")
n1new = n1new.replace(seg, mat184 + NL + seg, 1)

# n1 claim: insert the W184 attribution after the W183 claim tail line
# (r581 law: anchor = tail single-line literal + post-anchor guard)
seg = '"r869 bm-a] "' + NL + IND10 + '"+ T-141 s2 "'
check(n1new.count(seg) == 1, "n1 claim anchor not unique")
n1new = n1new.replace(seg, '"r869 bm-a] "' + NL + claim184 + NL + IND10 +
                      '"+ T-141 s2 "', 1)

# ---- gates (r780/r781/r560/r815 lineage) --------------------------------
ast.parse(pfnew)
ast.parse(n1new)
print("AST gate: both files parse OK")

# W184 presence + W183 anti-vanish (r560 law)
checks = [
    (pfnew, '184: {"a": (419_604, 421_603), "b_exit": (421_604, 421_803),', 1),
    (pfnew, '183: {"a": (417_404, 419_403), "b_exit": (419_404, 419_603),', 1),
    (pfnew, "# W184 (bm-a r874 freeze", 1),
    (pfnew, "# W183 (bm-a r869 freeze", 1),
    (n1new, '184: {"batch": "PERPETUAL-N1-W184",', 1),
    (n1new, '183: {"batch": "PERPETUAL-N1-W183",', 1),
    (n1new, "# --- W184 materializer face", 1),
    (n1new, "# --- W183 materializer face", 1),
    (n1new, '"r874 bm-a] "', 1),
    (n1new, '"r869 bm-a] "', 1),
    (n1new, '"a_seed_base": 419_604,', 1),
    (n1new, '"b_exit_seed_base": 421_604,', 1),
    (n1new, "n1_w184", 4),
    (n1new, "PERPETUAL_N1_W184_PREREG.md", 2),
]
for src, needle, cnt in checks:
    got = src.count(needle)
    check(got == cnt, "post-edit needle %r count %d != %d" % (needle[:50], got, cnt))

# W185+ projection prose present in the new W184 blocks (probe leg4
# verbatim; r819 post-edit assert bloodline + r776 fragment-needle law;
# pf header = self-wave W184+ per r845 precedent, n1 fragment =
# next-wave W185+)
check("# W184+ projection (gate-derived r870)" in pfnew,
      "pf W184+ projection head missing")
check('probe_receipt.json; W185+ projection "' in n1new,
      "n1 W185+ projection head fragment missing")
check("# 421_604..423_603 CLEAN hops=0 / B first-clean 421_804..422_003" in pfnew,
      "pf W185p prose missing")
check("W185 A window; W185 freezer MUST re-derive on the post-W184" in pfnew,
      "pf W185 freezer prose missing")
check('"W185 A window; W185 freezer MUST re-derive on the "' in n1new,
      "n1 W185 freezer fragment missing")
check('"W184 B band 421_604..421_803 will refuse the naive "' in n1new,
      "n1 W184-band refuse fragment missing")

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
check('184: {"a": (419_604' not in pf_o2, "write-time: origin pf carries W184")
check('184: {"batch"' not in n1_o2, "write-time: origin n1 carries W184")
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
