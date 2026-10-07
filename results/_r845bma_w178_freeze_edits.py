# -*- coding: utf-8 -*-
"""r845 bm-a W178 freeze edits: four insertions (pf N1_BANDS[178] row +
n1 WAVE_CONFIGS[178] entry + n1 W178 materializer block + n1 W178
PASS-claim attribution). DRY flag: --dry = zero-write simulation
(r781 verify-separation law + r811/r822/r826/r830/r834/r843 dry-run
precedent: full stale+prose+AST asserts in memory BEFORE any write).

Bloodline: r819/r822/r826/r830/r834/r843 freeze-edits machinery (r773 pit
law freeze-editor compliance + r776 fragment-needle law + r781
verify-separation law), W178 facts live-registry-driven (built by
_r845bma_w178_freeze_buildgen.py: old sides = the PHYSICAL W177 face
fragments probed to dumps this window, new sides = the S77 W178 fact
map, counts verified pre-emission):
  - pre-seat probe results/_r844bma_w178_probe_receipt.json rc0 ADMIT
    (A 406_404..408_403 staircase THIRTY-EIGHTH instance E36 hops=1
    past the registered W177 B band 406_204..406_403; naive
    406_204..408_203 refused at its own start by the W177 B band --
    receipt A_semantics machine-cites the W177 seat MSG leg4 + r841
    probe leg4 anticipated + MANDATED this re-derive (W177 sec5.5
    prose anticipated 38th -- projection and receipt ordinals MATCH,
    no divergence this wave); B 408_404..408_603 own-A mutual
    exclusion hops=1, naive 406_404..406_603);
  - face probe results/_r845bma_w178_face_probe_receipt.json rc0 (all
    four W177 faces dumped + needle counts; this TOK is built from the
    PHYSICAL probe-dumped shapes, r776 law);
  - seat MSG-2026-10-07-2157-bma-w178-seat published on origin at
    5b9284c79 (r845 pre-seat push, path-derived TRUE sha per r812
    precedent); r565 law: on origin BEFORE this freeze commit;
    self-ack archive ALREADY LANDED pre-freeze -- r845 same-window
    self-ack move (the W178 seat MSG sits in fleet/inbox/processed/ at
    freeze time, honest archived);
  - per-wave prereg research/PERPETUAL_N1_W178_PREREG.md frozen at
    origin a15c62683 (r845 build, banned gate ADMIT 0 re-verified at
    freeze this window);
  - W177 freeze registered sha machine-derived = c06cc230f (git log
    origin/main --grep "W177 FREEZE"); W177 finalize landed r844
    dead-tail adopted: ledger head 795,305, merged pool K=387,320
    (n1_w177_results.json machine-read; sec7/sec8 backfill landed the
    r845 window -- delayed-window precedent, honest);
  - lineage constants disclosed (r795 precedent, passed through):
    (a) the "wave N-1 = first free number" mat-header label rides the
    vmap verbatim (off-by-one lineage quirk since W165 r795);
    (b) "law sec.4 W178 row, r795" band-facts template stamp keeps its
    r795;
    (c) "single-window derive (r812 merged the gate legs INTO the
    pre-seat probe...)" stays (historical merge citation);
    (d) the bm-a-owned ordinal word rolls ninety-third ->
    ninety-fourth (rows 93 + candidate = 94th owned per probe leg0);
    (e) mat parity-chain rows W138..W176 keep their historical stamps
    and tuples; the W177 row (the current registered tail) is
    APPENDED with its frozen values (404_204, 406_203)/(406_204,
    406_403);
    (f) the entry "W176 finalize landed same-window r827" citation
    rides the vmap verbatim (off-by-one wave-word + stale-session
    lineage quirk inherited from the r830/r834/r843 generations; head/K
    values roll machine-correct to 795,305/387,320 this window --
    prose session stamp stays per frozen-lineage discipline).

r773 pit law compliance:
  (1) full string-face inventory empirically probed BEFORE TOK
      (_r845bma_w178_face_probe.py -- four face dumps + needle-count
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
      (r530/r687: fetch + origin carries no W178 registration before
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
probe = json.load(open(r"results\_r844bma_w178_probe_receipt.json",
                       encoding="utf-8"))
check(probe["verdict"] == "ADMIT", "pre-seat probe not ADMIT")
check(probe["bands"] == {"A": "406404_408403", "B": "408404_408603"},
      "probe band shape mismatch")
check(probe["legs"]["leg1"]["A"] == [406404, 408403], "A band mismatch")
check(probe["legs"]["leg1"]["B"] == [408404, 408603], "B band mismatch")
check(probe["legs"]["leg1"]["hops_A"] == 1 and probe["legs"]["leg1"]["hops_B"] == 1,
      "hops mismatch")
check(probe["legs"]["leg0"]["rows"] == 175 and probe["legs"]["leg0"]["tail"] == "W177",
      "leg0 registry tail mismatch")
check(probe["legs"]["leg0"]["ordinal"] == 168 and probe["legs"]["leg0"]["bma_ordinal"] == 94,
      "leg0 ordinal mismatch")
check(probe["legs"]["leg2"]["conflicts"] == 0, "leg2 conflicts nonzero")
check(probe["legs"]["leg3"]["origin_vacancy"] is True, "leg3 origin not vacant")
check(probe["legs"]["leg4"]["W179p_A"] == "408404..410403"
      and probe["legs"]["leg4"]["W179p_B"] == "408604..408803",
      "leg4 W179+ projection mismatch")

# origin anti-collision pre-check (r511 tail-lock / r687 write-time gate)
subprocess.run(["git", "fetch", "origin"], capture_output=True)
pf_o = subprocess.run(["git", "show", "origin/main:" + PF],
                      capture_output=True).stdout.decode("utf-8", "replace")
n1_o = subprocess.run(["git", "show", "origin/main:" + N1],
                      capture_output=True).stdout.decode("utf-8", "replace")
check('178: {"a": (406_404' not in pf_o, "origin pf already carries W178 row")
check("W178 (bm-a r845 freeze" not in pf_o, "origin pf carries W178 block")
check('178: {"batch"' not in n1_o, "origin n1 already carries W178 entry")
check("# --- W178 materializer face" not in n1_o, "origin n1 carries W178 mat")
check('"r845 bm-a] "' not in n1_o, "origin n1 carries W178 claim")

# machine-derived shas (r587 / r812 path-derived precedent)
seat_sha = subprocess.run(
    ["git", "log", "origin/main", "--format=%h", "-n", "1", "--diff-filter=A",
     "--", "fleet/inbox/MSG-2026-10-07-2157-bma-w178-seat.md"],
    capture_output=True).stdout.decode().strip()
check(seat_sha == "5b9284c79", "seat sha path-derived mismatch: " + seat_sha)
check(os.path.exists(os.path.join(
    "fleet", "inbox", "processed", "MSG-2026-10-07-2157-bma-w178-seat.md")),
    "seat MSG not in processed/ at freeze time (self-ack archive)")
w177_freeze_sha = subprocess.run(
    ["git", "log", "origin/main", "--format=%h", "-n", "1", "--grep=W177 FREEZE"],
    capture_output=True).stdout.decode().strip()
check(w177_freeze_sha == "c06cc230f", "W177 freeze sha mismatch: " + w177_freeze_sha)

# ---- live-registry parity pre-check (edit-gate: never edit a drifted file)
sys.path.insert(0, "scripts")
import perpetual_faces as pfmod  # noqa: E402
check(len(pfmod.N1_BANDS) == 175, "live N1_BANDS row count drift: %d" % len(pfmod.N1_BANDS))
check(pfmod.N1_BANDS[177] == {"a": (404_204, 406_203),
                              "b_exit": (406_204, 406_403),
                              "engine_owner": "bm-a"}, "live W177 row drift")
check(178 not in pfmod.N1_BANDS, "live N1_BANDS already has 178")
check(os.path.exists(os.path.join("research", "PERPETUAL_N1_W178_PREREG.md")),
      "W178 per-wave prereg missing (materializer gate)")
prereg_o = subprocess.run(["git", "show", "origin/main:research/PERPETUAL_N1_W178_PREREG.md"],
                          capture_output=True)
check(prereg_o.returncode == 0, "W178 prereg absent on origin")

# ---- physical face dumps (r776 law) -----------------------------------
pfblk = io.open(r"results\_r845bma_w178_probe_pf_block.txt", encoding="utf-8",
                newline="").read()
entry = io.open(r"results\_r845bma_w178_probe_n1_entry.txt", encoding="utf-8",
                newline="").read()
mat = io.open(r"results\_r845bma_w178_probe_n1_mat.txt", encoding="utf-8",
              newline="").read()
claim = io.open(r"results\_r845bma_w178_probe_n1_claim.txt", encoding="utf-8",
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
    ('    # W177 (bm-a r843 freeze, seat MSG-2026-10-07-2031-bma-w177-seat', '    # W178 (bm-a r845 freeze, seat MSG-2026-10-07-2157-bma-w178-seat', 1),
    ('pushed to origin 780a0cd30 pre-freeze r565 law (r841 pre-seat', 'pushed to origin 5b9284c79 pre-freeze r565 law (r844 pre-seat', 1),
    ('(3-item; the W176 finalize product already on origin since r839,', '(3-item; the W177 finalize product already on origin since r844,', 1),
    ('# = direct fast-forward behind-0 at fetch (r841 pre-seat', '# = direct fast-forward behind-0 at fetch (r844 pre-seat', 1),
    ('# push), zero merge, zero --no-verify; self-ack archive ALREADY\r\n    # LANDED pre-freeze -- r841 same-window self-ack move (the W177\r\n    # seat MSG sits in fleet/inbox/processed/ at freeze time, honest\r\n    # archived);', '# push), zero merge, zero --no-verify; self-ack archive ALREADY\r\n    # LANDED pre-freeze -- r845 same-window self-ack move (the W178\r\n    # seat MSG sits in fleet/inbox/processed/ at freeze time, honest\r\n    # archived);', 1),
    ('band gate ADMIT results/_r841bma_w177_probe_receipt.json: A = FIRST-CLEAN', 'band gate ADMIT results/_r844bma_w178_probe_receipt.json: A = FIRST-CLEAN', 1),
    ('past the registered W176 B band (arithmetic continuation', 'past the registered W177 B band (arithmetic continuation', 1),
    ('404_004..406_003 REFUSED at its own start by the W176 B band', '406_204..408_203 REFUSED at its own start by the W177 B band', 1),
    ('404_004..404_203, exactly as the W176 seat W177+ projection + r832 probe', '406_204..406_403, exactly as the W177 seat W178+ projection + r841 probe', 1),
    ('# leg4 + r839 sec8 succession projection notes all anticipated;', '# leg4 + r844 sec8 succession projection notes all anticipated;', 1),
    ('honest forward walk hops=1 -> 404_204..406_203, non-rotational', 'honest forward walk hops=1 -> 406_404..408_403, non-rotational', 1),
    ('(404_203+1) machine-checkable -- A-hops-prior-B staircase', '(406_403+1) machine-checkable -- A-hops-prior-B staircase', 1),
    ('THIRTY-SEVENTH instance, E36 card);', 'THIRTY-EIGHTH instance, E36 card);', 1),
    ('continuation 404_204..404_403 CLEAN on the registered universe', 'continuation 406_404..406_603 CLEAN on the registered universe', 1),
    ('but lands INSIDE the W177 A band window -- same-freeze mutual', 'but lands INSIDE the W178 A band window -- same-freeze mutual', 1),
    ('own-wave A window reserved jumps to 406_204 -> 406_204..406_403,', 'own-wave A window reserved jumps to 408_404 -> 408_404..408_603,', 1),
    ('own-wave A tail+1 (406_203+1) machine-checkable);', 'own-wave A tail+1 (408_403+1) machine-checkable);', 1),
    ('W177+ projection (gate-derived r841): A first-clean', 'W178+ projection (gate-derived r844): A first-clean', 1),
    ('406_204..408_203 CLEAN hops=0 / B first-clean 406_404..406_603', '408_404..410_403 CLEAN hops=0 / B first-clean 408_604..408_803', 1),
    ('registered W177 B band 406_204..406_403 will refuse the naive', 'registered W178 B band 408_404..408_603 will refuse the naive', 1),
    ('W178 A window; W178 freezer MUST re-derive on the post-W177', 'W179 A window; W179 freezer MUST re-derive on the post-W178', 1),
    ('NOT a re-pick (R250: W177 bands were never assigned).', 'NOT a re-pick (R250: W178 bands were never assigned).', 1),
    ('177: {"a": (404_204, 406_203), "b_exit": (406_204, 406_403),', '178: {"a": (406_404, 408_403), "b_exit": (408_404, 408_603),', 1),
]

EN_PAIRS = [
    ('177: {"batch": "PERPETUAL-N1-W177",', '178: {"batch": "PERPETUAL-N1-W178",', 1),
    ('"prereg": ("research/PERPETUAL_N1_W177_PREREG.md (wave-level frozen "', '"prereg": ("research/PERPETUAL_N1_W178_PREREG.md (wave-level frozen "', 1),
    ('new seed bands only; ONE HUNDRED-AND-SIXTY-SEVENTH ENGINE-OWNED WAVE ', 'new seed bands only; ONE HUNDRED-AND-SIXTY-EIGHTH ENGINE-OWNED WAVE ', 1),
    ('BY MACHINE-DERIVE (engine_owner rows 166 + candidate), ', 'BY MACHINE-DERIVE (engine_owner rows 167 + candidate), ', 1),
    ('number law after the REGISTERED W176 row bm-a r834 freeze ', 'number law after the REGISTERED W177 row bm-a r843 freeze ', 1),
    ('15ec44ea6, SINGLE STATE zero seat gap W2..W176 all ', 'c06cc230f, SINGLE STATE zero seat gap W2..W177 all ', 1),
    ('registered; W177 finalize landed same-window r827, ledger ', 'registered; W178 finalize landed same-window r827, ledger ', 1),
    ('head 793,105, merged pool K=385,120; seat published=reserved ', 'head 795,305, merged pool K=387,320; seat published=reserved ', 1),
    ('MSG-2026-10-07-2031-bma-w177-seat PUSHED to origin 780a0cd30 ', 'MSG-2026-10-07-2157-bma-w178-seat PUSHED to origin 5b9284c79 ', 1),
    ('probe receipt (3-item; the W176 finalize product already on origin since r839, not re-shipped; W146 precedent); ', 'probe receipt (3-item; the W177 finalize product already on origin since r844, not re-shipped; W146 precedent); ', 1),
    ('at fetch (r841 pre-seat push), zero merge, zero ', 'at fetch (r844 pre-seat push), zero merge, zero ', 1),
    ('engine_owner=bm-a, wave 176: ', 'engine_owner=bm-a, wave 177: ', 1),
    ('A = FIRST-CLEAN past the registered W176 B band (the ', 'A = FIRST-CLEAN past the registered W177 B band (the ', 1),
    ('arithmetic continuation 404_004..406_003 is REFUSED at its ', 'arithmetic continuation 406_204..408_203 is REFUSED at its ', 1),
    ('own start by the W176 B band 404_004..404_203, exactly as ', 'own start by the W177 B band 406_204..406_403, exactly as ', 1),
    ('the W176 seat W177+ projection + r832 probe leg4 + r839 sec8 succession ', 'the W177 seat W178+ projection + r841 probe leg4 + r844 sec8 succession ', 1),
    ('projection notes anticipated; honest forward walk hops=1 -> ', 'projection notes anticipated; honest forward walk hops=1 -> ', 1),
    ('404_204..406_203; A base == prior-wave B tail+1 ', '406_404..408_403; A base == prior-wave B tail+1 ', 1),
    ('machine-checkable = A-hops-prior-B staircase THIRTY-SEVENTH ', 'machine-checkable = A-hops-prior-B staircase THIRTY-EIGHTH ', 1),
    ('arithmetic continuation 404_204..404_403 is CLEAN on the ', 'arithmetic continuation 406_404..406_603 is CLEAN on the ', 1),
    ('registered universe but lands INSIDE the W177 A band ', 'registered universe but lands INSIDE the W178 A band ', 1),
    ('jumps to 406_204, first-clean 406_204..406_403 hops=1, ', 'jumps to 408_404, first-clean 408_404..408_603 hops=1, ', 1),
    ('convergence with the W176 seat W177+ projection + r832 probe leg4 + ', 'convergence with the W177 seat W178+ projection + r841 probe leg4 + ', 1),
    ('r839 sec8 succession projection notes re-derived -- all ', 'r844 sec8 succession projection notes re-derived -- all ', 1),
    ('MANDATORY notes honored (post-W176 universe re-derive + ', 'MANDATORY notes honored (post-W177 universe re-derive + ', 1),
    ('results/_r841bma_w177_probe_receipt.json; W178+ projection ', 'results/_r844bma_w178_probe_receipt.json; W179+ projection ', 1),
    ('per this window gate: A first-clean 406_204..408_203 ', 'per this window gate: A first-clean 408_404..410_403 ', 1),
    ('CLEAN / B first-clean 406_404..406_603 CLEAN -- naive ', 'CLEAN / B first-clean 408_604..408_803 CLEAN -- naive ', 1),
    ('W177 B band 406_204..406_403 will refuse the naive ', 'W178 B band 408_404..408_603 will refuse the naive ', 1),
    ('W178 A window; W178 freezer MUST re-derive on the ', 'W179 A window; W179 freezer MUST re-derive on the ', 1),
    ('post-W177 universe AND reserve the own-wave A window ', 'post-W178 universe AND reserve the own-wave A window ', 1),
    ('staircase card); W1..W176 finalize ALL LANDED (W176 ', 'staircase card); W1..W177 finalize ALL LANDED (W177 ', 1),
    ('finalize one-pass bm-a r839, net chain head 793,105, ', 'finalize one-pass bm-a r844, net chain head 795,305, ', 1),
    ('merged pool K=385,120) -- ZERO in-flight upstream ', 'merged pool K=387,320) -- ZERO in-flight upstream ', 1),
    ('"a_seed_base": 404_204,        # law sec.4 W177 A: 404_204..406_203 (FIRST-CLEAN past the registered W176 B band; arithmetic 404_004..406_003 REFUSED at own start by the W176 B band; hops=1; A-hops-prior-B staircase THIRTY-SEVENTH instance, E36 card; ordinal convergence per r587: W176 sec5.5 prose anticipated thirty-seventh, r841 receipt machine-read THIRTY-SEVENTH)', '"a_seed_base": 406_404,        # law sec.4 W178 A: 406_404..408_403 (FIRST-CLEAN past the registered W177 B band; arithmetic 406_204..408_203 REFUSED at own start by the W177 B band; hops=1; A-hops-prior-B staircase THIRTY-EIGHTH instance, E36 card; ordinal convergence per r587: W177 sec5.5 prose anticipated thirty-eighth, r844 receipt machine-read THIRTY-EIGHTH)', 1),
    ('"b_exit_seed_base": 406_204,   # law sec.4 W177 B: 406_204..406_403 (FIRST-CLEAN past the own-wave A window; arithmetic 404_204..404_403 lands inside own-A, same-freeze mutual exclusion W141 precedent; reserved walk hops=1; B base == own-A tail+1)', '"b_exit_seed_base": 408_404,   # law sec.4 W178 B: 408_404..408_603 (FIRST-CLEAN past the own-wave A window; arithmetic 406_404..406_603 lands inside own-A, same-freeze mutual exclusion W141 precedent; reserved walk hops=1; B base == own-A tail+1)', 1),
    ('"shard_subdir": "n1_w177", "out_name": "n1_w177_results.json",', '"shard_subdir": "n1_w178", "out_name": "n1_w178_results.json",', 1),
]

MAT_PAIRS = [
    ('# --- W177 materializer face (r843 bm-a freeze, own-series law', '# --- W178 materializer face (r845 bm-a freeze, own-series law', 1),
    ('#     ninety-third owned per machine-derive (engine_owner==bm-a', '#     ninety-fourth owned per machine-derive (engine_owner==bm-a', 1),
    ('#     rows 92 + candidate); wave 176 = first free number after', '#     rows 93 + candidate); wave 177 = first free number after', 1),
    ('#     the REGISTERED W176 row (bm-a r834 freeze 15ec44ea6) --', '#     the REGISTERED W177 row (bm-a r843 freeze c06cc230f) --', 1),
    ('#     SINGLE STATE zero seat gap (W2..W176 all registered). Seat', '#     SINGLE STATE zero seat gap (W2..W177 all registered). Seat', 1),
    ('#     published=reserved MSG-2026-10-07-2031-bma-w177-seat pushed', '#     published=reserved MSG-2026-10-07-2157-bma-w178-seat pushed', 1),
    ('#     to origin 780a0cd30 BEFORE this freeze, r565 law (payload', '#     to origin 5b9284c79 BEFORE this freeze, r565 law (payload', 1),
    ('#     the W176 finalize product already on origin since r839, not', '#     the W177 finalize product already on origin since r844, not', 1),
    ('#     at fetch (r841 pre-seat push), zero merge, zero', '#     at fetch (r844 pre-seat push), zero merge, zero', 1),
    ('#     --no-verify; self-ack inbox->processed archive ALREADY LANDED\r\n    #     pre-freeze -- r841 same-window self-ack move (the W177 seat\r\n    #     MSG sits in fleet/inbox/processed/ at freeze time, honest\r\n    #     archived).', '#     --no-verify; self-ack inbox->processed archive ALREADY LANDED\r\n    #     pre-freeze -- r845 same-window self-ack move (the W178 seat\r\n    #     MSG sits in fleet/inbox/processed/ at freeze time, honest\r\n    #     archived).', 1),
    ('#     ONE HUNDRED-AND-SIXTY-SEVENTH engine wave BY', '#     ONE HUNDRED-AND-SIXTY-EIGHTH engine wave BY', 1),
    ('#     MACHINE-DERIVE (engine_owner rows 166 + candidate; gate', '#     MACHINE-DERIVE (engine_owner rows 167 + candidate; gate', 1),
    ('#     W1..W176 finalize ALL LANDED (net chain head 793,105,', '#     W1..W177 finalize ALL LANDED (net chain head 795,305,', 1),
    ('#     K=385,120 merged pool; W176 finalize one-pass bm-a r839)', '#     K=387,320 merged pool; W177 finalize one-pass bm-a r844)', 1),
    ('#     always on. ADMIT receipt results/_r841bma_w177_probe_receipt.json;', '#     always on. ADMIT receipt results/_r844bma_w178_probe_receipt.json;', 1),
    ('#     banned gate ADMIT 0; not a re-pick (R250: W177 bands were', '#     banned gate ADMIT 0; not a re-pick (R250: W178 bands were', 1),
    ('    _set_wave(177)', '    _set_wave(178)', 1),
    ('assert WAVE_CONFIGS[176]["a_seed_base"] == pf.N1_BANDS[176]["a"][0], \\', 'assert WAVE_CONFIGS[177]["a_seed_base"] == pf.N1_BANDS[177]["a"][0], \\', 1),
    ('"W177 A band drift vs law mirror"', '"W178 A band drift vs law mirror"', 1),
    ('assert WAVE_CONFIGS[176]["b_exit_seed_base"] == \\', 'assert WAVE_CONFIGS[177]["b_exit_seed_base"] == \\', 1),
    ('pf.N1_BANDS[176]["b_exit"][0], "W177 B band drift vs law mirror"', 'pf.N1_BANDS[177]["b_exit"][0], "W178 B band drift vs law mirror"', 1),
    ('assert WAVE_CONFIGS[176].get("engine_owner") == \\', 'assert WAVE_CONFIGS[177].get("engine_owner") == \\', 1),
    ('pf.N1_BANDS[176].get("engine_owner") == "bm-a", \\', 'pf.N1_BANDS[177].get("engine_owner") == "bm-a", \\', 1),
    ('"W177 engine_owner drift (law mirror parity)"', '"W178 engine_owner drift (law mirror parity)"', 1),
    ('w176_a = {A_SEED_BASE + j for j in range(A_N)}', 'w177_a = {A_SEED_BASE + j for j in range(A_N)}', 1),
    ('w176_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}', 'w177_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}', 1),
    ('assert not (w176_a & w176_b), "W177 A/B band overlap"', 'assert not (w177_a & w177_b), "W178 A/B band overlap"', 1),
    ('assert not (w176_a & reg_ints) and not (w176_b & reg_ints), \\', 'assert not (w177_a & reg_ints) and not (w177_b & reg_ints), \\', 1),
    ('"W177 hits SEED_REGISTRY"', '"W178 hits SEED_REGISTRY"', 1),
    ('for nm, band in (("A", w176_a), ("B", w176_b)):', 'for nm, band in (("A", w177_a), ("B", w177_b)):', 1),
    ('f"W177 {nm} hits v1"', 'f"W178 {nm} hits v1"', 1),
    ('f"W177 {nm} hits W1"', 'f"W178 {nm} hits W1"', 1),
    ('f"W177 {nm} hits probe seeds"', 'f"W178 {nm} hits probe seeds"', 1),
    ('"registered W176 row parity drift (r307; bm-a r834)"', '"registered W176 row parity drift (r307; bm-a r834)"\r\n        assert pf.N1_BANDS[177] == {"a": (404_204, 406_203),\r\n                                    "b_exit": (406_204, 406_403),\r\n                                    "engine_owner": "bm-a"}, \\\r\n            "registered W177 row parity drift (r307; bm-a r843)"', 1),
    ('# prior-wave disjointness W2..W176 (single state: all', '# prior-wave disjointness W2..W177 (single state: all', 1),
    ('for wprev in sorted(w for w in WAVE_CONFIGS if w < 177):', 'for wprev in sorted(w for w in WAVE_CONFIGS if w < 178):', 2),
    ('assert not (w176_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j', 'assert not (w177_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j', 1),
    ('for j in range(A_N)}), f"W177 A hits W{wprev}"', 'for j in range(A_N)}), f"W178 A hits W{wprev}"', 1),
    ('assert not (w176_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j', 'assert not (w177_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j', 1),
    ('for j in range(B_N)}), f"W177 B hits W{wprev}"', 'for j in range(B_N)}), f"W178 B hits W{wprev}"', 1),
    ('n3r1_used176 = set(range(70_000, 70_006))', 'n3r1_used177 = set(range(70_000, 70_006))', 1),
    ('assert not (w176_a & n3r1_used176) and not (w176_b & n3r1_used176), \\', 'assert not (w177_a & n3r1_used177) and not (w177_b & n3r1_used177), \\', 1),
    ('"W177 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"', '"W178 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"', 1),
    ('assert not (w176_a & lfc_actual12) and not (w176_b & lfc_actual12), \\', 'assert not (w177_a & lfc_actual12) and not (w177_b & lfc_actual12), \\', 1),
    ('"W177 bands must clear the lfc actual draw range"', '"W178 bands must clear the lfc actual draw range"', 1),
    ('assert not (w176_a & options_actual12) and \\', 'assert not (w177_a & options_actual12) and \\', 1),
    ('not (w176_b & options_actual12), \\', 'not (w177_b & options_actual12), \\', 1),
    ('"W177 bands must clear the options_wave2 actual draw range"', '"W178 bands must clear the options_wave2 actual draw range"', 1),
    ('# band facts (law sec.4 W177 row, r795): A = FIRST-CLEAN past', '# band facts (law sec.4 W178 row, r795): A = FIRST-CLEAN past', 1),
    ('# the registered W176 B band (the arithmetic continuation', '# the registered W177 B band (the arithmetic continuation', 1),
    ('# 404_004..406_003 is REFUSED at its own start by the W176', '# 406_204..408_203 is REFUSED at its own start by the W177', 1),
    ('# B band 404_004..404_203, exactly as the W176 seat W177+ projection +', '# B band 406_204..406_403, exactly as the W177 seat W178+ projection +', 1),
    ('# r832 probe leg4 + r839 sec8 succession projection notes', '# r841 probe leg4 + r844 sec8 succession projection notes', 1),
    ('# 404_204..406_203; A base == prior-wave B tail+1 (404_203+1)', '# 406_404..408_403; A base == prior-wave B tail+1 (406_403+1)', 1),
    ('# machine-checkable -- A-hops-prior-B staircase THIRTY-SEVENTH', '# machine-checkable -- A-hops-prior-B staircase THIRTY-EIGHTH', 1),
    ('# continuation 404_204..404_403 is CLEAN on the registered', '# continuation 406_404..406_603 is CLEAN on the registered', 1),
    ('# universe but lands INSIDE the W177 A band window --', '# universe but lands INSIDE the W178 A band window --', 1),
    ('# 406_204 and lands 406_204..406_403, hops=1, non-rotational', '# 408_404 and lands 408_404..408_603, hops=1, non-rotational', 1),
    ('# (406_203+1) machine-checkable; cross-window convergence', '# (408_403+1) machine-checkable; cross-window convergence', 1),
    ('# with the W176 seat W177+ projection + r832 probe leg4 + r839 sec8', '# with the W177 seat W178+ projection + r841 probe leg4 + r844 sec8', 1),
    ('# honored (post-W176 universe re-derive + own-wave A', '# honored (post-W177 universe re-derive + own-wave A', 1),
    ('# reservation when deriving B); seat MSG-2030 tail,', '# reservation when deriving B); seat MSG-2150 tail,', 1),
    ('assert WAVE_CONFIGS[177]["a_seed_base"] == 404_204 == 404_203 + 1, (', 'assert WAVE_CONFIGS[178]["a_seed_base"] == 406_404 == 406_403 + 1, (', 1),
    ('"W177 A must be the first-clean window past the registered "', '"W178 A must be the first-clean window past the registered "', 1),
    ('"W176 B band tail 404_203+1 (arithmetic continuation "', '"W177 B band tail 406_403+1 (arithmetic continuation "', 1),
    ('"404_004..406_003 REFUSED at its own start by the W176 B "', '"406_204..408_203 REFUSED at its own start by the W177 B "', 1),
    ('"band 404_004..404_203, exactly as the W176 seat W177+ projection + "', '"band 406_204..406_403, exactly as the W177 seat W178+ projection + "', 1),
    ('"r832 probe leg4 + r839 sec8 succession projection notes "', '"r841 probe leg4 + r844 sec8 succession projection notes "', 1),
    ('"staircase THIRTY-SEVENTH instance, E36 card)"', '"staircase THIRTY-EIGHTH instance, E36 card)"', 1),
    ('arith_a176 = set(range(404_204, 406_204))', 'arith_a177 = set(range(406_404, 408_404))', 1),
    ('assert not (arith_a176 & reg_ints), \\', 'assert not (arith_a177 & reg_ints), \\', 1),
    ('"W177 A window must be CLEAN (first-clean ADMIT face past prior-wave B)"', '"W178 A window must be CLEAN (first-clean ADMIT face past prior-wave B)"', 1),
    ('assert WAVE_CONFIGS[177]["b_exit_seed_base"] == 406_204 == 406_203 + 1, (', 'assert WAVE_CONFIGS[178]["b_exit_seed_base"] == 408_404 == 408_403 + 1, (', 1),
    ('"W177 B must be the first-clean window past the own-wave A "', '"W178 B must be the first-clean window past the own-wave A "', 1),
    ('"band tail 406_203+1 (arithmetic continuation "', '"band tail 408_403+1 (arithmetic continuation "', 1),
    ('"404_204..404_403 CLEAN on the registered universe but "', '"406_404..406_603 CLEAN on the registered universe but "', 1),
    ('"lands INSIDE the W177 A band window; same-freeze mutual "', '"lands INSIDE the W178 A band window; same-freeze mutual "', 1),
    ('"own-wave A window reserved jumps to 406_204, first-clean "', '"own-wave A window reserved jumps to 408_404, first-clean "', 1),
    ('arith_b176 = set(range(406_204, 406_404))', 'arith_b177 = set(range(408_404, 408_604))', 1),
    ('assert not (arith_b176 & reg_ints), \\', 'assert not (arith_b177 & reg_ints), \\', 1),
    ('"W177 B window must be CLEAN (first-clean ADMIT face past own-wave A)"', '"W178 B window must be CLEAN (first-clean ADMIT face past own-wave A)"', 1),
    ('assert not (arith_b176 & arith_a176), \\', 'assert not (arith_b177 & arith_a177), \\', 1),
    ('"W177 A/B same-freeze mutual exclusion (B hops past own A)"', '"W178 A/B same-freeze mutual exclusion (B hops past own A)"', 1),
    ('assert _entry_shard_of(0, 12) == ("PERPETUAL-N1-W177-SHARD-0",', 'assert _entry_shard_of(0, 12) == ("PERPETUAL-N1-W178-SHARD-0",', 1),
    ('"n1w177-0of12"), "W177 entry identity"', '"n1w178-0of12"), "W178 entry identity"', 1),
    ('assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W177-SHARD-11",', 'assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W178-SHARD-11",', 1),
    ('"n1w177-11of12")', '"n1w178-11of12")', 1),
    ('assert SHARD_DIR.endswith("n1_w177") and OUT.endswith(', 'assert SHARD_DIR.endswith("n1_w178") and OUT.endswith(', 1),
    ('"n1_w177_results.json"), "W177 path drift"', '"n1_w178_results.json"), "W178 path drift"', 1),
    ('f"W177 shard dir collides with W{wprev}"', 'f"W178 shard dir collides with W{wprev}"', 1),
    ('# W177 finalize cumulative deps: W17..W176 outputs ALL PRESENT', '# W178 finalize cumulative deps: W17..W177 outputs ALL PRESENT', 1),
    ('# (landed net chain head 793,105 = W176 bm-a r839 one-pass --', '# (landed net chain head 795,305 = W177 bm-a r844 one-pass --', 1),
    ('for _depw in range(17, 177):', 'for _depw in range(17, 178):', 1),
    ('f"W177 finalize cumulative dep (W{_depw} output) missing"', 'f"W178 finalize cumulative dep (W{_depw} output) missing"', 1),
    ('# registered wave below 177 composes; wave 15 excluded by', '# registered wave below 178 composes; wave 15 excluded by', 1),
    ('# design; SINGLE STATE (W2..W176 all registered -- no', '# design; SINGLE STATE (W2..W177 all registered -- no', 1),
    ('assert sorted(w for w in WAVE_CONFIGS if w < 177) == \\', 'assert sorted(w for w in WAVE_CONFIGS if w < 178) == \\', 1),
    ('[w for w in range(16, 177)], \\', '[w for w in range(16, 178)], \\', 1),
    ('"W177 prior-wave set must derive from registry keys (no 15; "', '"W178 prior-wave set must derive from registry keys (no 15; "', 1),
    ('"W2..W176 registered single state)"', '"W2..W177 registered single state)"', 1),
    ('PATHS.root, "research", "PERPETUAL_N1_W177_PREREG.md")), \\', 'PATHS.root, "research", "PERPETUAL_N1_W178_PREREG.md")), \\', 1),
    ('"W177 per-wave prereg missing (materializer requirement)"', '"W178 per-wave prereg missing (materializer requirement)"', 1),
]

CL_PAIRS = [
    ('"+ W177 materializer face [same guard set, dep=W17..W176 ', '"+ W178 materializer face [same guard set, dep=W17..W177 ', 1),
    ('"outputs ALL PRESENT (landed net chain head 793,105 = "', '"outputs ALL PRESENT (landed net chain head 795,305 = "', 1),
    ('"W176 bm-a r839 one-pass, K=385,120 merged pool; ZERO "', '"W177 bm-a r844 one-pass, K=387,320 merged pool; ZERO "', 1),
    ('"in-flight upstream seats), ONE HUNDRED-AND-SIXTY-SEVENTH "', '"in-flight upstream seats), ONE HUNDRED-AND-SIXTY-EIGHTH "', 1),
    ('"ENGINE-OWNED WAVE BY MACHINE-DERIVE (engine_owner rows 166 "', '"ENGINE-OWNED WAVE BY MACHINE-DERIVE (engine_owner rows 167 "', 1),
    ("+ candidate) bm-a's ninety-third owned claim per ", "+ candidate) bm-a's ninety-fourth owned claim per ", 1),
    ('"machine-derive (engine_owner==bm-a rows 92 + candidate), "', '"machine-derive (engine_owner==bm-a rows 93 + candidate), "', 1),
    ('"A=FIRST-CLEAN past the registered W176 B band (staircase "', '"A=FIRST-CLEAN past the registered W177 B band (staircase "', 1),
    ('"THIRTY-SEVENTH instance, E36 card, hops=1) + B=FIRST-CLEAN past the "', '"THIRTY-EIGHTH instance, E36 card, hops=1) + B=FIRST-CLEAN past the "', 1),
    ('"results/_r841bma_w177_probe_receipt.json, law sec.4 W177 row, "', '"results/_r844bma_w178_probe_receipt.json, law sec.4 W178 row, "', 1),
    ('"r843 bm-a] "', '"r845 bm-a] "', 1),
]

PF_NEG = ['    # W177 (bm-a r843 freeze, seat MSG-2026-10-07-2031-bma-w177-seat', 'pushed to origin 780a0cd30 pre-freeze r565 law (r841 pre-seat', '(3-item; the W176 finalize product already on origin since r839,', '# = direct fast-forward behind-0 at fetch (r841 pre-seat', '# push), zero merge, zero --no-verify; self-ack archive ALREADY\r\n    # LANDED pre-freeze -- r841 same-window self-ack move (the W177\r\n    # seat MSG sits in fleet/inbox/processed/ at freeze time, honest\r\n    # archived);', 'band gate ADMIT results/_r841bma_w177_probe_receipt.json: A = FIRST-CLEAN', 'past the registered W176 B band (arithmetic continuation', '404_004..406_003 REFUSED at its own start by the W176 B band', '404_004..404_203, exactly as the W176 seat W177+ projection + r832 probe', '# leg4 + r839 sec8 succession projection notes all anticipated;', 'honest forward walk hops=1 -> 404_204..406_203, non-rotational', '(404_203+1) machine-checkable -- A-hops-prior-B staircase', 'THIRTY-SEVENTH instance, E36 card);', 'continuation 404_204..404_403 CLEAN on the registered universe', 'but lands INSIDE the W177 A band window -- same-freeze mutual', 'own-wave A window reserved jumps to 406_204 -> 406_204..406_403,', 'own-wave A tail+1 (406_203+1) machine-checkable);', 'W177+ projection (gate-derived r841): A first-clean', '406_204..408_203 CLEAN hops=0 / B first-clean 406_404..406_603', 'registered W177 B band 406_204..406_403 will refuse the naive', 'W178 A window; W178 freezer MUST re-derive on the post-W177', 'NOT a re-pick (R250: W177 bands were never assigned).', '177: {"a": (404_204, 406_203), "b_exit": (406_204, 406_403),', '780a0cd30', 'r832 probe', 'r839 sec8', 'r841 pre-seat', '_r841bma', 'MSG-2026-10-07-2031', '15ec44ea6', '793,105', '385,120', 'THIRTY-SEVENTH', 'ONE HUNDRED-AND-SIXTY-SEVENTH']

EN_NEG = ['177: {"batch": "PERPETUAL-N1-W177",', '"prereg": ("research/PERPETUAL_N1_W177_PREREG.md (wave-level frozen "', 'new seed bands only; ONE HUNDRED-AND-SIXTY-SEVENTH ENGINE-OWNED WAVE ', 'BY MACHINE-DERIVE (engine_owner rows 166 + candidate), ', 'number law after the REGISTERED W176 row bm-a r834 freeze ', '15ec44ea6, SINGLE STATE zero seat gap W2..W176 all ', 'registered; W177 finalize landed same-window r827, ledger ', 'head 793,105, merged pool K=385,120; seat published=reserved ', 'MSG-2026-10-07-2031-bma-w177-seat PUSHED to origin 780a0cd30 ', 'probe receipt (3-item; the W176 finalize product already on origin since r839, not re-shipped; W146 precedent); ', 'at fetch (r841 pre-seat push), zero merge, zero ', 'engine_owner=bm-a, wave 176: ', 'A = FIRST-CLEAN past the registered W176 B band (the ', 'arithmetic continuation 404_004..406_003 is REFUSED at its ', 'own start by the W176 B band 404_004..404_203, exactly as ', 'the W176 seat W177+ projection + r832 probe leg4 + r839 sec8 succession ', '404_204..406_203; A base == prior-wave B tail+1 ', 'machine-checkable = A-hops-prior-B staircase THIRTY-SEVENTH ', 'arithmetic continuation 404_204..404_403 is CLEAN on the ', 'registered universe but lands INSIDE the W177 A band ', 'jumps to 406_204, first-clean 406_204..406_403 hops=1, ', 'convergence with the W176 seat W177+ projection + r832 probe leg4 + ', 'r839 sec8 succession projection notes re-derived -- all ', 'MANDATORY notes honored (post-W176 universe re-derive + ', 'results/_r841bma_w177_probe_receipt.json; W178+ projection ', 'per this window gate: A first-clean 406_204..408_203 ', 'CLEAN / B first-clean 406_404..406_603 CLEAN -- naive ', 'W177 B band 406_204..406_403 will refuse the naive ', 'W178 A window; W178 freezer MUST re-derive on the ', 'post-W177 universe AND reserve the own-wave A window ', 'staircase card); W1..W176 finalize ALL LANDED (W176 ', 'finalize one-pass bm-a r839, net chain head 793,105, ', 'merged pool K=385,120) -- ZERO in-flight upstream ', '"a_seed_base": 404_204,        # law sec.4 W177 A: 404_204..406_203 (FIRST-CLEAN past the registered W176 B band; arithmetic 404_004..406_003 REFUSED at own start by the W176 B band; hops=1; A-hops-prior-B staircase THIRTY-SEVENTH instance, E36 card; ordinal convergence per r587: W176 sec5.5 prose anticipated thirty-seventh, r841 receipt machine-read THIRTY-SEVENTH)', '"b_exit_seed_base": 406_204,   # law sec.4 W177 B: 406_204..406_403 (FIRST-CLEAN past the own-wave A window; arithmetic 404_204..404_403 lands inside own-A, same-freeze mutual exclusion W141 precedent; reserved walk hops=1; B base == own-A tail+1)', '"shard_subdir": "n1_w177", "out_name": "n1_w177_results.json",', '15ec44ea6', '780a0cd30', '793,105', '385,120', 'ONE HUNDRED-AND-SIXTY-SEVENTH', 'rows 166', 'r832 probe', '_r841bma', 'MSG-2026-10-07-2031', 'n1w177', 'n1_w177', 'PERPETUAL-N1-W177', 'PERPETUAL_N1_W177', 'THIRTY-SEVENTH', 'bm-a r834 freeze', '406_204, first-clean']

MAT_NEG = ['# --- W177 materializer face (r843 bm-a freeze, own-series law', '#     ninety-third owned per machine-derive (engine_owner==bm-a', '#     rows 92 + candidate); wave 176 = first free number after', '#     the REGISTERED W176 row (bm-a r834 freeze 15ec44ea6) --', '#     SINGLE STATE zero seat gap (W2..W176 all registered). Seat', '#     published=reserved MSG-2026-10-07-2031-bma-w177-seat pushed', '#     to origin 780a0cd30 BEFORE this freeze, r565 law (payload', '#     the W176 finalize product already on origin since r839, not', '#     at fetch (r841 pre-seat push), zero merge, zero', '#     --no-verify; self-ack inbox->processed archive ALREADY LANDED\r\n    #     pre-freeze -- r841 same-window self-ack move (the W177 seat\r\n    #     MSG sits in fleet/inbox/processed/ at freeze time, honest\r\n    #     archived).', '#     ONE HUNDRED-AND-SIXTY-SEVENTH engine wave BY', '#     MACHINE-DERIVE (engine_owner rows 166 + candidate; gate', '#     W1..W176 finalize ALL LANDED (net chain head 793,105,', '#     K=385,120 merged pool; W176 finalize one-pass bm-a r839)', '#     always on. ADMIT receipt results/_r841bma_w177_probe_receipt.json;', '#     banned gate ADMIT 0; not a re-pick (R250: W177 bands were', '    _set_wave(177)', 'assert WAVE_CONFIGS[176]["a_seed_base"] == pf.N1_BANDS[176]["a"][0], \\', '"W177 A band drift vs law mirror"', 'assert WAVE_CONFIGS[176]["b_exit_seed_base"] == \\', 'pf.N1_BANDS[176]["b_exit"][0], "W177 B band drift vs law mirror"', 'assert WAVE_CONFIGS[176].get("engine_owner") == \\', 'pf.N1_BANDS[176].get("engine_owner") == "bm-a", \\', '"W177 engine_owner drift (law mirror parity)"', 'w176_a = {A_SEED_BASE + j for j in range(A_N)}', 'w176_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}', 'assert not (w176_a & w176_b), "W177 A/B band overlap"', 'assert not (w176_a & reg_ints) and not (w176_b & reg_ints), \\', '"W177 hits SEED_REGISTRY"', 'for nm, band in (("A", w176_a), ("B", w176_b)):', 'f"W177 {nm} hits v1"', 'f"W177 {nm} hits W1"', 'f"W177 {nm} hits probe seeds"', '# prior-wave disjointness W2..W176 (single state: all', 'for wprev in sorted(w for w in WAVE_CONFIGS if w < 177):', 'assert not (w176_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j', 'for j in range(A_N)}), f"W177 A hits W{wprev}"', 'assert not (w176_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j', 'for j in range(B_N)}), f"W177 B hits W{wprev}"', 'n3r1_used176 = set(range(70_000, 70_006))', 'assert not (w176_a & n3r1_used176) and not (w176_b & n3r1_used176), \\', '"W177 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"', 'assert not (w176_a & lfc_actual12) and not (w176_b & lfc_actual12), \\', '"W177 bands must clear the lfc actual draw range"', 'assert not (w176_a & options_actual12) and \\', 'not (w176_b & options_actual12), \\', '"W177 bands must clear the options_wave2 actual draw range"', '# band facts (law sec.4 W177 row, r795): A = FIRST-CLEAN past', '# the registered W176 B band (the arithmetic continuation', '# 404_004..406_003 is REFUSED at its own start by the W176', '# B band 404_004..404_203, exactly as the W176 seat W177+ projection +', '# r832 probe leg4 + r839 sec8 succession projection notes', '# 404_204..406_203; A base == prior-wave B tail+1 (404_203+1)', '# machine-checkable -- A-hops-prior-B staircase THIRTY-SEVENTH', '# continuation 404_204..404_403 is CLEAN on the registered', '# universe but lands INSIDE the W177 A band window --', '# 406_204 and lands 406_204..406_403, hops=1, non-rotational', '# (406_203+1) machine-checkable; cross-window convergence', '# with the W176 seat W177+ projection + r832 probe leg4 + r839 sec8', '# honored (post-W176 universe re-derive + own-wave A', '# reservation when deriving B); seat MSG-2030 tail,', 'assert WAVE_CONFIGS[177]["a_seed_base"] == 404_204 == 404_203 + 1, (', '"W177 A must be the first-clean window past the registered "', '"W176 B band tail 404_203+1 (arithmetic continuation "', '"404_004..406_003 REFUSED at its own start by the W176 B "', '"band 404_004..404_203, exactly as the W176 seat W177+ projection + "', '"r832 probe leg4 + r839 sec8 succession projection notes "', '"staircase THIRTY-SEVENTH instance, E36 card)"', 'arith_a176 = set(range(404_204, 406_204))', 'assert not (arith_a176 & reg_ints), \\', '"W177 A window must be CLEAN (first-clean ADMIT face past prior-wave B)"', 'assert WAVE_CONFIGS[177]["b_exit_seed_base"] == 406_204 == 406_203 + 1, (', '"W177 B must be the first-clean window past the own-wave A "', '"band tail 406_203+1 (arithmetic continuation "', '"404_204..404_403 CLEAN on the registered universe but "', '"lands INSIDE the W177 A band window; same-freeze mutual "', '"own-wave A window reserved jumps to 406_204, first-clean "', 'arith_b176 = set(range(406_204, 406_404))', 'assert not (arith_b176 & reg_ints), \\', '"W177 B window must be CLEAN (first-clean ADMIT face past own-wave A)"', 'assert not (arith_b176 & arith_a176), \\', '"W177 A/B same-freeze mutual exclusion (B hops past own A)"', 'assert _entry_shard_of(0, 12) == ("PERPETUAL-N1-W177-SHARD-0",', '"n1w177-0of12"), "W177 entry identity"', 'assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W177-SHARD-11",', '"n1w177-11of12")', 'assert SHARD_DIR.endswith("n1_w177") and OUT.endswith(', '"n1_w177_results.json"), "W177 path drift"', 'f"W177 shard dir collides with W{wprev}"', '# W177 finalize cumulative deps: W17..W176 outputs ALL PRESENT', '# (landed net chain head 793,105 = W176 bm-a r839 one-pass --', 'for _depw in range(17, 177):', 'f"W177 finalize cumulative dep (W{_depw} output) missing"', '# registered wave below 177 composes; wave 15 excluded by', '# design; SINGLE STATE (W2..W176 all registered -- no', 'assert sorted(w for w in WAVE_CONFIGS if w < 177) == \\', '[w for w in range(16, 177)], \\', '"W177 prior-wave set must derive from registry keys (no 15; "', '"W2..W176 registered single state)"', 'PATHS.root, "research", "PERPETUAL_N1_W177_PREREG.md")), \\', '"W177 per-wave prereg missing (materializer requirement)"', 'w176_', 'arith_a176', 'arith_b176', 'n3r1_used176', 'r832 probe', 'r841 pre-seat', '15ec44ea6', 'ONE HUNDRED-AND-SIXTY-SEVENTH', 'ninety-third', 'rows 166', 'rows 92 ', 'range(17, 177)', 'range(16, 177)', 'PERPETUAL_N1_W177', 'PERPETUAL-N1-W177', 'MSG-2030', '_r841bma', 'r841 same-window', 'n1w177', 'n1_w177', '793,105', '385,120']

CL_NEG = ['"+ W177 materializer face [same guard set, dep=W17..W176 ', '"outputs ALL PRESENT (landed net chain head 793,105 = "', '"W176 bm-a r839 one-pass, K=385,120 merged pool; ZERO "', '"in-flight upstream seats), ONE HUNDRED-AND-SIXTY-SEVENTH "', '"ENGINE-OWNED WAVE BY MACHINE-DERIVE (engine_owner rows 166 "', "+ candidate) bm-a's ninety-third owned claim per ", '"machine-derive (engine_owner==bm-a rows 92 + candidate), "', '"A=FIRST-CLEAN past the registered W176 B band (staircase "', '"THIRTY-SEVENTH instance, E36 card, hops=1) + B=FIRST-CLEAN past the "', '"results/_r841bma_w177_probe_receipt.json, law sec.4 W177 row, "', '"r843 bm-a] "', '793,105', '385,120', 'ONE HUNDRED-AND-SIXTY-SEVENTH', 'ninety-third', 'rows 166', 'rows 92 ', 'THIRTY-SEVENTH', '_r841bma', 'r834 bm-a] ']

blk178 = vmap(pfblk, PF_PAIRS, PF_NEG, "pf")
entry178 = IND23 + vmap(entry, EN_PAIRS, EN_NEG, "entry")
mat178 = "    " + vmap(mat, MAT_PAIRS, MAT_NEG, "mat")
claim178 = IND10 + vmap(claim, CL_PAIRS, CL_NEG, "claim")

# ---- apply insertions (in-memory) ---------------------------------------
pfsrc = io.open(PF, encoding="utf-8", newline="").read()
n1src = io.open(N1, encoding="utf-8", newline="").read()

# pf: insert W178 block after the W177 row (last registered), before the
# dict close -- r560 insert-after-last-registered-row + post-anchor gate
seg = EO + NL + "}"
check(pfsrc.count(seg) == 1, "pf row-close segment not unique")
pfnew = pfsrc.replace(seg, EO + NL + blk178 + NL + "}", 1)

# n1 entry: after the W177 entry, before the WAVE_CONFIGS close
seg = EO + NL + IND23 + "}"
check(n1src.count(seg) == 1, "n1 entry-close segment not unique")
n1new = n1src.replace(seg, EO + NL + entry178 + NL + IND23 + "}", 1)

# n1 mat: insert the W178 block before the T-141 s2 lane face header
seg = "    # --- T-141 s2 lane face"
check(n1new.count(seg) == 1, "n1 T-141 mat anchor not unique")
n1new = n1new.replace(seg, mat178 + NL + seg, 1)

# n1 claim: insert the W178 attribution after the W177 claim tail line
# (r581 law: anchor = tail single-line literal + post-anchor guard)
seg = '"r843 bm-a] "' + NL + IND10 + '"+ T-141 s2 "'
check(n1new.count(seg) == 1, "n1 claim anchor not unique")
n1new = n1new.replace(seg, '"r843 bm-a] "' + NL + claim178 + NL + IND10 +
                      '"+ T-141 s2 "', 1)

# ---- gates (r780/r781/r560/r815 lineage) --------------------------------
ast.parse(pfnew)
ast.parse(n1new)
print("AST gate: both files parse OK")

# W178 presence + W177 anti-vanish (r560 law)
checks = [
    (pfnew, '178: {"a": (406_404, 408_403), "b_exit": (408_404, 408_603),', 1),
    (pfnew, '177: {"a": (404_204, 406_203), "b_exit": (406_204, 406_403),', 1),
    (pfnew, "# W178 (bm-a r845 freeze", 1),
    (pfnew, "# W177 (bm-a r843 freeze", 1),
    (n1new, '178: {"batch": "PERPETUAL-N1-W178",', 1),
    (n1new, '177: {"batch": "PERPETUAL-N1-W177",', 1),
    (n1new, "# --- W178 materializer face", 1),
    (n1new, "# --- W177 materializer face", 1),
    (n1new, '"r845 bm-a] "', 1),
    (n1new, '"r843 bm-a] "', 1),
    (n1new, '"a_seed_base": 406_404,', 1),
    (n1new, '"b_exit_seed_base": 408_404,', 1),
    (n1new, "n1_w178", 4),
    (n1new, "PERPETUAL_N1_W178_PREREG.md", 2),
]
for src, needle, cnt in checks:
    got = src.count(needle)
    check(got == cnt, "post-edit needle %r count %d != %d" % (needle[:50], got, cnt))

# W179+ projection prose present in the new W178 blocks (probe leg4
# verbatim; r819 post-edit assert bloodline + r776 fragment-needle law)
check("# W178+ projection (gate-derived r844)" in pfnew,
      "pf W178+ projection head missing")
check('probe_receipt.json; W179+ projection "' in n1new,
      "n1 W179+ projection head fragment missing")
check("# 408_404..410_403 CLEAN hops=0 / B first-clean 408_604..408_803" in pfnew,
      "pf W179p prose missing")
check("W179 A window; W179 freezer MUST re-derive on the post-W178" in pfnew,
      "pf W179 freezer prose missing")
check('"W179 A window; W179 freezer MUST re-derive on the "' in n1new,
      "n1 W179 freezer fragment missing")
check('"W178 B band 408_404..408_603 will refuse the naive "' in n1new,
      "n1 W178-band refuse fragment missing")

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
check('178: {"a": (406_404' not in pf_o2, "write-time: origin pf carries W178")
check('178: {"batch"' not in n1_o2, "write-time: origin n1 carries W178")
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
