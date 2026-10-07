# -*- coding: utf-8 -*-
"""r822 bm-a W173 freeze edits: four insertions (pf N1_BANDS[173] row +
n1 WAVE_CONFIGS[173] entry + n1 W173 materializer block + n1 W173
PASS-claim attribution). DRY flag: --dry = zero-write simulation
(r781 verify-separation law + r811 dry-run precedent: full stale+prose+
AST asserts in memory BEFORE any write).

Bloodline: r819 _r819bma_w172_freeze_edits.py machinery (r773 pit law
freeze-editor compliance + r776 fragment-needle law + r781
verify-separation law), W173 facts live-registry-driven:
  - pre-seat probe results/_r820bma_w173_probe_receipt.json rc0 ADMIT
    (A 395_404..397_403 staircase THIRTY-THIRD instance E36 hops=1 past
    the registered W172 B band 395_204..395_403; naive 395_204..397_203
    refused at its own start by the W172 B band -- receipt A_semantics
    machine-cites 'r818 probe leg4' anticipation + MANDATE; B
    397_404..397_603 own-A mutual exclusion hops=1, naive
    395_404..395_603);
  - ordinal divergence disclosed per r587: W172 sec5.5 prose
    anticipated 32nd, r820 receipt machine-read THIRTY-THIRD -- the
    NEW faces carry the receipt ordinal THIRTY-THIRD;
  - prereg citation slip disclosed: the frozen W173 prereg (d76ce93d5)
    prose says 'r820 probe leg4' in the anticipation triple while the
    machine receipt A_semantics says 'r818 probe leg4'; the NEW faces
    carry the machine-receipt citation (r818 probe = the W172 pre-seat
    probe whose leg4 carried the W173+ projection), prereg face not
    edited per freeze discipline;
  - face probe results/_r822bma_w173_face_probe_receipt.json rc0 (all
    four W172 faces dumped + needle counts; this TOK is built from the
    PHYSICAL probe-dumped shapes, r776 law);
  - seat MSG-2026-10-07-1122-bma-w173-seat published on origin at
    9cd8af3af (r820 pre-seat push, path-derived TRUE sha per r812
    precedent; r820 closeout prose 014b4ede5 = stale pre-rebase
    artifact, honesty-noted r821); r565 law: on origin BEFORE this
    freeze commit; self-ack archive ALREADY LANDED pre-freeze -- bm-c
    r672 inbox sweep observed-archived the bm-a-lane seat MSG at
    11:41:55 (the seat MSG sits in fleet/inbox/processed/ at freeze
    time, honest archived state -- NOT the r819-era deferred state);
  - per-wave prereg research/PERPETUAL_N1_W173_PREREG.md frozen at
    origin d76ce93d5 (r821 build, banned gate ADMIT 0);
  - W172 freeze registered sha machine-derived = 59fde9319 (git log
    origin/main --grep "W172 FREEZE"); W172 finalize one-pass landed
    r819: ledger head 783,812, merged pool K=376,320
    (n1_w172_results.json machine-read);
  - lineage constants disclosed (r795 precedent, passed through):
    (a) the "wave N-1:" entry label + "wave N-1 = first free number"
    mat-header label ride the vmap verbatim (off-by-one lineage quirk
    since the W165 r795 band-facts template); (b) "law sec.4 W173 row,
    r795" band-facts template stamp keeps its r795; (c) "single-window
    derive (r812 merged the gate legs INTO the pre-seat probe...)"
    stays (historical merge citation, the structure persists); (d) the
    bm-a-owned ordinal word rolls eighty-seventh -> eighty-ninth (the
    lineage pattern: ordinal word = prior-row count, rows 88 +
    candidate = 89th owned per probe leg0); (e) the mat B-face
    cross-window sec8 succession citation heals the stale r813 carry
    -> r819 (the W172 sec8 succession notes landed r819; one-token
    heal, disclosed).

r773 pit law compliance:
  (1) full string-face inventory empirically probed BEFORE TOK
      (_r822bma_w173_face_probe.py -- four face dumps + needle-count
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
      parity + origin anti-collision pre-check (r530/r687: fetch +
      origin carries no W173 registration before this freeze);
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
probe = json.load(open(r"results\_r820bma_w173_probe_receipt.json",
                       encoding="utf-8"))
check(probe["verdict"] == "ADMIT", "pre-seat probe not ADMIT")
check(probe["bands"] == {"A": "395404_397403", "B": "397404_397603"},
      "probe band shape mismatch")
check(probe["legs"]["leg1"]["A"] == [395404, 397403], "A band mismatch")
check(probe["legs"]["leg1"]["B"] == [397404, 397603], "B band mismatch")
check(probe["legs"]["leg1"]["hops_A"] == 1 and probe["legs"]["leg1"]["hops_B"] == 1,
      "hops mismatch")
check(probe["legs"]["leg0"]["rows"] == 170 and probe["legs"]["leg0"]["tail"] == "W172",
      "leg0 registry tail mismatch")
check(probe["legs"]["leg0"]["ordinal"] == 163 and probe["legs"]["leg0"]["bma_ordinal"] == 89,
      "leg0 ordinal mismatch")
check(probe["legs"]["leg2"]["conflicts"] == 0, "leg2 conflicts nonzero")
check(probe["legs"]["leg3"]["origin_vacancy"] is True, "leg3 origin not vacant")
check(probe["legs"]["leg4"]["W174p_A"] == "397404..399403"
      and probe["legs"]["leg4"]["W174p_B"] == "397604..397803",
      "leg4 W174+ projection mismatch")

# origin anti-collision pre-check (r511 tail-lock / r687 write-time gate)
subprocess.run(["git", "fetch", "origin"], capture_output=True)
pf_o = subprocess.run(["git", "show", "origin/main:" + PF],
                      capture_output=True).stdout.decode("utf-8", "replace")
n1_o = subprocess.run(["git", "show", "origin/main:" + N1],
                      capture_output=True).stdout.decode("utf-8", "replace")
check('173: {"a": (395_404' not in pf_o, "origin pf already carries W173 row")
check("W173 (bm-a r822 freeze" not in pf_o, "origin pf carries W173 block")
check('173: {"batch"' not in n1_o, "origin n1 already carries W173 entry")
check("# --- W173 materializer face" not in n1_o, "origin n1 carries W173 mat")
check('"r822 bm-a] "' not in n1_o, "origin n1 carries W173 claim")

# machine-derived shas (r587 / r812 path-derived precedent)
seat_sha = subprocess.run(
    ["git", "log", "origin/main", "--format=%h", "-n", "1", "--diff-filter=A",
     "--", "fleet/inbox/MSG-2026-10-07-1122-bma-w173-seat.md"],
    capture_output=True).stdout.decode().strip()
check(seat_sha == "9cd8af3af", "seat sha path-derived mismatch: " + seat_sha)
w172_freeze_sha = subprocess.run(
    ["git", "log", "origin/main", "--format=%h", "-n", "1", "--grep=W172 FREEZE"],
    capture_output=True).stdout.decode().strip()
check(w172_freeze_sha == "59fde9319", "W172 freeze sha mismatch: " + w172_freeze_sha)

# ---- live-registry parity pre-check (edit-gate: never edit a drifted file)
sys.path.insert(0, "scripts")
import perpetual_faces as pfmod  # noqa: E402
check(len(pfmod.N1_BANDS) == 170, "live N1_BANDS row count drift: %d" % len(pfmod.N1_BANDS))
check(pfmod.N1_BANDS[172] == {"a": (393_204, 395_203),
                              "b_exit": (395_204, 395_403),
                              "engine_owner": "bm-a"}, "live W172 row drift")
check(173 not in pfmod.N1_BANDS, "live N1_BANDS already has 173")
check(os.path.exists(os.path.join("research", "PERPETUAL_N1_W173_PREREG.md")),
      "W173 per-wave prereg missing (materializer gate)")
prereg_o = subprocess.run(["git", "show", "origin/main:research/PERPETUAL_N1_W173_PREREG.md"],
                          capture_output=True)
check(prereg_o.returncode == 0, "W173 prereg absent on origin")

# ---- physical face dumps (r776 law) -----------------------------------
pfblk = io.open(r"results\_r822bma_w173_probe_pf_block.txt", encoding="utf-8",
                newline="").read()
entry = io.open(r"results\_r822bma_w173_probe_n1_entry.txt", encoding="utf-8",
                newline="").read()
mat = io.open(r"results\_r822bma_w173_probe_n1_mat.txt", encoding="utf-8",
              newline="").read()
claim = io.open(r"results\_r822bma_w173_probe_n1_claim.txt", encoding="utf-8",
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


# ---- face 1: pf N1_BANDS[173] comment block + row -----------------------
PF_PAIRS = [
    ("    # W172 (bm-a r819 freeze, seat MSG-2026-10-07-1012-bma-w172-seat",
     "    # W173 (bm-a r822 freeze, seat MSG-2026-10-07-1122-bma-w173-seat", 1),
    ("pushed to origin 01a7480e1 pre-freeze r565 law (r818 pre-seat",
     "pushed to origin 9cd8af3af pre-freeze r565 law (r820 pre-seat", 1),
    ("(3-item; the W171 finalize product already on origin since r816,",
     "(3-item; the W172 finalize product already on origin since r819,", 1),
    ("# = direct fast-forward behind-0 at fetch (r818 pre-seat",
     "# = direct fast-forward behind-0 at fetch (r820 pre-seat", 1),
    ("# push), zero merge, zero --no-verify; self-ack inbox->processed" + NL +
     "    # move DEFERRED to the W172 finalize window -- the W172 seat" + NL +
     "    # MSG sits in fleet/inbox/ at freeze time (honest deferred);",
     "# push), zero merge, zero --no-verify; self-ack archive ALREADY" + NL +
     "    # LANDED pre-freeze -- bm-c r672 inbox sweep observed-archived" + NL +
     "    # the bm-a-lane seat MSG at 11:41:55 (the W173 seat MSG sits in" + NL +
     "    # fleet/inbox/processed/ at freeze time, honest archived);", 1),
    ("band gate ADMIT results/_r818bma_w172_probe_receipt.json: A = FIRST-CLEAN",
     "band gate ADMIT results/_r820bma_w173_probe_receipt.json: A = FIRST-CLEAN", 1),
    ("past the registered W171 B band (arithmetic continuation",
     "past the registered W172 B band (arithmetic continuation", 1),
    ("393_004..395_003 REFUSED at its own start by the W171 B band",
     "395_204..397_203 REFUSED at its own start by the W172 B band", 1),
    ("393_004..393_203, exactly as the W171 seat W172+ projection + r814 probe",
     "395_204..395_403, exactly as the W172 seat W173+ projection + r818 probe", 1),
    ("honest forward walk hops=1 -> 393_204..395_203, non-rotational",
     "honest forward walk hops=1 -> 395_404..397_403, non-rotational", 1),
    ("(393_203+1) machine-checkable -- A-hops-prior-B staircase",
     "(395_403+1) machine-checkable -- A-hops-prior-B staircase", 1),
    ("thirty-first instance, E36 card);",
     "THIRTY-THIRD instance, E36 card);", 1),
    ("continuation 393_204..393_403 CLEAN on the registered universe",
     "continuation 395_404..395_603 CLEAN on the registered universe", 1),
    ("but lands INSIDE the W172 A band window -- same-freeze mutual",
     "but lands INSIDE the W173 A band window -- same-freeze mutual", 1),
    ("own-wave A window reserved jumps to 395_204 -> 395_204..395_403,",
     "own-wave A window reserved jumps to 397_404 -> 397_404..397_603,", 1),
    ("own-wave A tail+1 (395_203+1) machine-checkable);",
     "own-wave A tail+1 (397_403+1) machine-checkable);", 1),
    ("W172+ projection (gate-derived r818): A first-clean",
     "W173+ projection (gate-derived r820): A first-clean", 1),
    ("395_204..397_203 CLEAN hops=0 / B first-clean 395_404..395_603",
     "397_404..399_403 CLEAN hops=0 / B first-clean 397_604..397_803", 1),
    ("registered W172 B band 395_204..395_403 will refuse the naive",
     "registered W173 B band 397_404..397_603 will refuse the naive", 1),
    ("W173 A window; W173 freezer MUST re-derive on the post-W172",
     "W174 A window; W174 freezer MUST re-derive on the post-W173", 1),
    ("NOT a re-pick (R250: W172 bands were never assigned).",
     "NOT a re-pick (R250: W173 bands were never assigned).", 1),
    ('172: {"a": (393_204, 395_203), "b_exit": (395_204, 395_403),',
     '173: {"a": (395_404, 397_403), "b_exit": (397_404, 397_603),', 1),
]
PF_NEG = ["01a7480e1", "r814", "r816", "r818 pre-seat", "gate-derived r818",
          "_r818bma", "456f3affc", "393_204", "393_004",
          "395_203,", "W171", "W172 (bm-a", "INSIDE the W172", "thirty-first",
          "W172+ projection (", "R250: W172", "MSG-2026-10-07-1012", "_r818bma",
          "W172 bands were", "the W172 finalize window", "DEFERRED",
          "W172 A band window", "W172 seat" + NL]
blk173 = vmap(pfblk, PF_PAIRS, PF_NEG, "pf")

# ---- face 2: n1 WAVE_CONFIGS[173] entry ---------------------------------
EN_PAIRS = [
    ('172: {"batch": "PERPETUAL-N1-W172",', '173: {"batch": "PERPETUAL-N1-W173",', 1),
    ('"prereg": ("research/PERPETUAL_N1_W172_PREREG.md (wave-level frozen "',
     '"prereg": ("research/PERPETUAL_N1_W173_PREREG.md (wave-level frozen "', 1),
    ('new seed bands only; ONE HUNDRED-AND-SIXTY-SECOND ENGINE-OWNED WAVE ',
     'new seed bands only; ONE HUNDRED-AND-SIXTY-THIRD ENGINE-OWNED WAVE ', 1),
    ('BY MACHINE-DERIVE (engine_owner rows 161 + candidate), ',
     'BY MACHINE-DERIVE (engine_owner rows 162 + candidate), ', 1),
    ('number law after the REGISTERED W171 row bm-a r815 freeze ',
     'number law after the REGISTERED W172 row bm-a r819 freeze ', 1),
    ('456f3affc, SINGLE STATE zero seat gap W2..W171 all ',
     '59fde9319, SINGLE STATE zero seat gap W2..W172 all ', 1),
    ('registered; W171 finalize landed same-window r816, ledger ',
     'registered; W172 finalize landed same-window r819, ledger ', 1),
    ('head 781,612, merged pool K=374,120; seat published=reserved ',
     'head 783,812, merged pool K=376,320; seat published=reserved ', 1),
    ('MSG-2026-10-07-1012-bma-w172-seat PUSHED to origin 01a7480e1 ',
     'MSG-2026-10-07-1122-bma-w173-seat PUSHED to origin 9cd8af3af ', 1),
    ('probe receipt (3-item; the W171 finalize product already on origin since r816, not re-shipped; W146 precedent); ',
     'probe receipt (3-item; the W172 finalize product already on origin since r819, not re-shipped; W146 precedent); ', 1),
    ('at fetch (r818 pre-seat push), zero merge, zero ',
     'at fetch (r820 pre-seat push), zero merge, zero ', 1),
    ('engine_owner=bm-a, wave 171: ', 'engine_owner=bm-a, wave 172: ', 1),
    ('A = FIRST-CLEAN past the registered W171 B band (the ',
     'A = FIRST-CLEAN past the registered W172 B band (the ', 1),
    ('arithmetic continuation 393_004..395_003 is REFUSED at its ',
     'arithmetic continuation 395_204..397_203 is REFUSED at its ', 1),
    ('own start by the W171 B band 393_004..393_203, exactly as ',
     'own start by the W172 B band 395_204..395_403, exactly as ', 1),
    ('the W171 seat W172+ projection + r814 probe leg4 + r819 sec8 succession ',
     'the W172 seat W173+ projection + r818 probe leg4 + r819 sec8 succession ', 1),
    # B-face split-line variant (the citation rides two python string
    # fragments in the physical entry -- r776 fragment-needle law)
    ('the W171 seat W172+ projection + r814 probe leg4 + "',
     'the W172 seat W173+ projection + r818 probe leg4 + "', 1),
    ('MANDATORY notes honored (post-W171 universe re-derive + "',
     'MANDATORY notes honored (post-W172 universe re-derive + "', 1),
    ('projection notes anticipated; honest forward walk hops=1 -> ',
     'projection notes anticipated; honest forward walk hops=1 -> ', 1),
    ('393_204..395_203; A base == prior-wave B tail+1 ',
     '395_404..397_403; A base == prior-wave B tail+1 ', 1),
    ('machine-checkable = A-hops-prior-B staircase thirty-first ',
     'machine-checkable = A-hops-prior-B staircase THIRTY-THIRD ', 1),
    ('walk) + B = FIRST-CLEAN past the own-wave A window (the ',
     'walk) + B = FIRST-CLEAN past the own-wave A window (the ', 1),
    ('arithmetic continuation 393_204..393_403 is CLEAN on the ',
     'arithmetic continuation 395_404..395_603 is CLEAN on the ', 1),
    ('registered universe but lands INSIDE the W172 A band ',
     'registered universe but lands INSIDE the W173 A band ', 1),
    ('jumps to 395_204, first-clean 395_204..395_403 hops=1, ',
     'jumps to 397_404, first-clean 397_404..397_603 hops=1, ', 1),
    ('results/_r818bma_w172_probe_receipt.json; W172+ projection ',
     'results/_r820bma_w173_probe_receipt.json; W174+ projection ', 1),
    ('per this window gate: A first-clean 395_204..397_203 ',
     'per this window gate: A first-clean 397_404..399_403 ', 1),
    ('CLEAN / B first-clean 395_404..395_603 CLEAN -- naive ',
     'CLEAN / B first-clean 397_604..397_803 CLEAN -- naive ', 1),
    ('W172 B band 395_204..395_403 will refuse the naive ',
     'W173 B band 397_404..397_603 will refuse the naive ', 1),
    ('W173 A window; W173 freezer MUST re-derive on the ',
     'W174 A window; W174 freezer MUST re-derive on the ', 1),
    ('post-W172 universe AND reserve the own-wave A window ',
     'post-W173 universe AND reserve the own-wave A window ', 1),
    ('staircase card); W1..W171 finalize ALL LANDED (W171 ',
     'staircase card); W1..W172 finalize ALL LANDED (W172 ', 1),
    ('finalize one-pass bm-a r816, net chain head 781,612, ',
     'finalize one-pass bm-a r819, net chain head 783,812, ', 1),
    ('merged pool K=374,120) -- ZERO in-flight upstream ',
     'merged pool K=376,320) -- ZERO in-flight upstream ', 1),
    ('"a_seed_base": 393_204,        # law sec.4 W172 A: 393_204..395_203 (FIRST-CLEAN past the registered W171 B band; arithmetic 393_004..395_003 REFUSED at own start by the W171 B band; hops=1; A-hops-prior-B staircase thirty-first instance, E36 card)',
     '"a_seed_base": 395_404,        # law sec.4 W173 A: 395_404..397_403 (FIRST-CLEAN past the registered W172 B band; arithmetic 395_204..397_203 REFUSED at own start by the W172 B band; hops=1; A-hops-prior-B staircase THIRTY-THIRD instance, E36 card; ordinal divergence disclosed per r587: W172 sec5.5 prose anticipated thirty-second, r820 receipt machine-read THIRTY-THIRD)', 1),
    ('"b_exit_seed_base": 395_204,   # law sec.4 W172 B: 395_204..395_403 (FIRST-CLEAN past the own-wave A window; arithmetic 393_204..393_403 lands inside own-A, same-freeze mutual exclusion W141 precedent; reserved walk hops=1; B base == own-A tail+1)',
     '"b_exit_seed_base": 397_404,   # law sec.4 W173 B: 397_404..397_603 (FIRST-CLEAN past the own-wave A window; arithmetic 395_404..395_603 lands inside own-A, same-freeze mutual exclusion W141 precedent; reserved walk hops=1; B base == own-A tail+1)', 1),
    ('"shard_subdir": "n1_w172", "out_name": "n1_w172_results.json",',
     '"shard_subdir": "n1_w173", "out_name": "n1_w173_results.json",', 1),
]
EN_NEG = ["01a7480e1", "r814", "r816", "r818 pre-seat", "_r818bma", "456f3affc",
          "393_204", "393_004",
          "393_203", "W171", "W172 (bm-a", "INSIDE the W172", "thirty-first ",
          "W172+ projection", "MSG-1012", "_r818bma", "n1_w172", "n1w172",
          "781,612", "374,120", "SIXTY-SECOND", "eighty-seventh", "rows 161",
          "rows 87 ", "W1..W171", "wave 171", "PERPETUAL-N1-W172",
          "PERPETUAL_N1_W172", "R250"]
entry173 = IND23 + vmap(entry, EN_PAIRS, EN_NEG, "entry")

# ---- face 3: n1 W173 materializer block ---------------------------------
MAT_PAIRS = [
    ("# --- W172 materializer face (r819 bm-a freeze, own-series law",
     "# --- W173 materializer face (r822 bm-a freeze, own-series law", 1),
    ("#     eighty-seventh owned per machine-derive (engine_owner==bm-a",
     "#     eighty-ninth owned per machine-derive (engine_owner==bm-a", 1),
    ("#     rows 87 + candidate); wave 171 = first free number after",
     "#     rows 88 + candidate); wave 172 = first free number after", 1),
    ("#     the REGISTERED W171 row (bm-a r815 freeze 456f3affc) --",
     "#     the REGISTERED W172 row (bm-a r819 freeze 59fde9319) --", 1),
    ("#     SINGLE STATE zero seat gap (W2..W171 all registered). Seat",
     "#     SINGLE STATE zero seat gap (W2..W172 all registered). Seat", 1),
    ("#     published=reserved MSG-2026-10-07-1012-bma-w172-seat pushed",
     "#     published=reserved MSG-2026-10-07-1122-bma-w173-seat pushed", 1),
    ("#     to origin 01a7480e1 BEFORE this freeze, r565 law (payload",
     "#     to origin 9cd8af3af BEFORE this freeze, r565 law (payload", 1),
    ("#     the W171 finalize product already on origin since r816, not",
     "#     the W172 finalize product already on origin since r819, not", 1),
    ("#     at fetch (r818 pre-seat push), zero merge, zero",
     "#     at fetch (r820 pre-seat push), zero merge, zero", 1),
    ("#     --no-verify; self-ack inbox->processed move DEFERRED to the W172 finalize window -- the W172 seat MSG" + NL +
     "    #     sits in fleet/inbox/ at freeze time (honest deferred). ONE HUNDRED-AND-SIXTY-SECOND engine wave BY",
     "#     --no-verify; self-ack inbox->processed archive ALREADY LANDED" + NL +
     "    #     pre-freeze -- bm-c r672 inbox sweep observed-archived the" + NL +
     "    #     bm-a-lane seat MSG at 11:41:55 (the W173 seat MSG sits in" + NL +
     "    #     fleet/inbox/processed/ at freeze time, honest archived)." + NL +
     "    #     ONE HUNDRED-AND-SIXTY-THIRD engine wave BY", 1),
    ("#     MACHINE-DERIVE (engine_owner rows 161 + candidate; gate",
     "#     MACHINE-DERIVE (engine_owner rows 162 + candidate; gate", 1),
    ("#     W1..W171 finalize ALL LANDED (net chain head 781,612,",
     "#     W1..W172 finalize ALL LANDED (net chain head 783,812,", 1),
    ("#     K=374,120 merged pool; W171 finalize one-pass bm-a r816)",
     "#     K=376,320 merged pool; W172 finalize one-pass bm-a r819)", 1),
    ("#     always on. ADMIT receipt results/_r818bma_w172_probe_receipt.json;",
     "#     always on. ADMIT receipt results/_r820bma_w173_probe_receipt.json;", 1),
    ("#     banned gate ADMIT 0; not a re-pick (R250: W172 bands were",
     "#     banned gate ADMIT 0; not a re-pick (R250: W173 bands were", 1),
    ("    _set_wave(172)", "    _set_wave(173)", 1),
    ('assert WAVE_CONFIGS[171]["a_seed_base"] == pf.N1_BANDS[171]["a"][0], \\',
     'assert WAVE_CONFIGS[172]["a_seed_base"] == pf.N1_BANDS[172]["a"][0], \\', 1),
    ('"W172 A band drift vs law mirror"', '"W173 A band drift vs law mirror"', 1),
    ('assert WAVE_CONFIGS[171]["b_exit_seed_base"] == \\',
     'assert WAVE_CONFIGS[172]["b_exit_seed_base"] == \\', 1),
    ('pf.N1_BANDS[171]["b_exit"][0], "W172 B band drift vs law mirror"',
     'pf.N1_BANDS[172]["b_exit"][0], "W173 B band drift vs law mirror"', 1),
    ('assert WAVE_CONFIGS[171].get("engine_owner") == \\',
     'assert WAVE_CONFIGS[172].get("engine_owner") == \\', 1),
    ('pf.N1_BANDS[171].get("engine_owner") == "bm-a", \\',
     'pf.N1_BANDS[172].get("engine_owner") == "bm-a", \\', 1),
    ('"W172 engine_owner drift (law mirror parity)"',
     '"W173 engine_owner drift (law mirror parity)"', 1),
    ("w171_a = {A_SEED_BASE + j for j in range(A_N)}",
     "w172_a = {A_SEED_BASE + j for j in range(A_N)}", 1),
    ("w171_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}",
     "w172_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}", 1),
    ('assert not (w171_a & w171_b), "W172 A/B band overlap"',
     'assert not (w172_a & w172_b), "W173 A/B band overlap"', 1),
    ("assert not (w171_a & reg_ints) and not (w171_b & reg_ints), \\",
     "assert not (w172_a & reg_ints) and not (w172_b & reg_ints), \\", 1),
    ('"W172 hits SEED_REGISTRY"', '"W173 hits SEED_REGISTRY"', 1),
    ("for nm, band in ((\"A\", w171_a), (\"B\", w171_b)):",
     "for nm, band in ((\"A\", w172_a), (\"B\", w172_b)):", 1),
    ('f"W172 {nm} hits v1"', 'f"W173 {nm} hits v1"', 1),
    ('f"W172 {nm} hits W1"', 'f"W173 {nm} hits W1"', 1),
    ('f"W172 {nm} hits probe seeds"', 'f"W173 {nm} hits probe seeds"', 1),
    ('"registered W171 row parity drift (r307; bm-a r815)"',
     '"registered W171 row parity drift (r307; bm-a r815)"' + NL +
     '        assert pf.N1_BANDS[172] == {"a": (393_204, 395_203),' + NL +
     '                                    "b_exit": (395_204, 395_403),' + NL +
     '                                    "engine_owner": "bm-a"}, \\' + NL +
     '            "registered W172 row parity drift (r307; bm-a r819)"', 1),
    ("# prior-wave disjointness W2..W171 (single state: all",
     "# prior-wave disjointness W2..W172 (single state: all", 1),
    ("for wprev in sorted(w for w in WAVE_CONFIGS if w < 172):",
     "for wprev in sorted(w for w in WAVE_CONFIGS if w < 173):", 2),
    ("assert not (w171_a & {WAVE_CONFIGS[wprev][\"a_seed_base\"] + j",
     "assert not (w172_a & {WAVE_CONFIGS[wprev][\"a_seed_base\"] + j", 1),
    ("for j in range(A_N)}), f\"W172 A hits W{wprev}\"",
     "for j in range(A_N)}), f\"W173 A hits W{wprev}\"", 1),
    ("assert not (w171_b & {WAVE_CONFIGS[wprev][\"b_exit_seed_base\"] + j",
     "assert not (w172_b & {WAVE_CONFIGS[wprev][\"b_exit_seed_base\"] + j", 1),
    ("for j in range(B_N)}), f\"W172 B hits W{wprev}\"",
     "for j in range(B_N)}), f\"W173 B hits W{wprev}\"", 1),
    ("n3r1_used171 = set(range(70_000, 70_006))",
     "n3r1_used172 = set(range(70_000, 70_006))", 1),
    ("assert not (w171_a & n3r1_used171) and not (w171_b & n3r1_used171), \\",
     "assert not (w172_a & n3r1_used172) and not (w172_b & n3r1_used172), \\", 1),
    ('"W172 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"',
     '"W173 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"', 1),
    ("assert not (w171_a & lfc_actual12) and not (w171_b & lfc_actual12), \\",
     "assert not (w172_a & lfc_actual12) and not (w172_b & lfc_actual12), \\", 1),
    ('"W172 bands must clear the lfc actual draw range"',
     '"W173 bands must clear the lfc actual draw range"', 1),
    ("assert not (w171_a & options_actual12) and \\",
     "assert not (w172_a & options_actual12) and \\", 1),
    ("not (w171_b & options_actual12), \\",
     "not (w172_b & options_actual12), \\", 1),
    ('"W172 bands must clear the options_wave2 actual draw range"',
     '"W173 bands must clear the options_wave2 actual draw range"', 1),
    ("# band facts (law sec.4 W172 row, r795): A = FIRST-CLEAN past",
     "# band facts (law sec.4 W173 row, r795): A = FIRST-CLEAN past", 1),
    ("# the registered W171 B band (the arithmetic continuation",
     "# the registered W172 B band (the arithmetic continuation", 1),
    ("# 393_004..395_003 is REFUSED at its own start by the W171",
     "# 395_204..397_203 is REFUSED at its own start by the W172", 1),
    ("# B band 393_004..393_203, exactly as the W171 seat W172+ projection +",
     "# B band 395_204..395_403, exactly as the W172 seat W173+ projection +", 1),
    ("# r814 probe leg4 + r819 sec8 succession projection notes",
     "# r818 probe leg4 + r819 sec8 succession projection notes", 1),
    ("# 393_204..395_203; A base == prior-wave B tail+1 (393_203+1)",
     "# 395_404..397_403; A base == prior-wave B tail+1 (395_403+1)", 1),
    ("# machine-checkable -- A-hops-prior-B staircase thirty-first",
     "# machine-checkable -- A-hops-prior-B staircase THIRTY-THIRD", 1),
    ("# continuation 393_204..393_403 is CLEAN on the registered",
     "# continuation 395_404..395_603 is CLEAN on the registered", 1),
    ("# universe but lands INSIDE the W172 A band window --",
     "# universe but lands INSIDE the W173 A band window --", 1),
    ("# 395_204 and lands 395_204..395_403, hops=1, non-rotational",
     "# 397_404 and lands 397_404..397_603, hops=1, non-rotational", 1),
    ("# (395_203+1) machine-checkable; cross-window convergence",
     "# (397_403+1) machine-checkable; cross-window convergence", 1),
    ("# with the W171 seat W172+ projection + r814 probe leg4 + r813 sec8",
     "# with the W172 seat W173+ projection + r818 probe leg4 + r819 sec8", 1),
    ("# reservation when deriving B); seat MSG-1012 tail,",
     "# reservation when deriving B); seat MSG-1122 tail,", 1),
    ("assert WAVE_CONFIGS[172][\"a_seed_base\"] == 393_204 == 393_203 + 1, (",
     "assert WAVE_CONFIGS[173][\"a_seed_base\"] == 395_404 == 395_403 + 1, (", 1),
    ('"W172 A must be the first-clean window past the registered "',
     '"W173 A must be the first-clean window past the registered "', 1),
    ('"W171 B band tail 393_203+1 (arithmetic continuation "',
     '"W172 B band tail 395_403+1 (arithmetic continuation "', 1),
    ('"393_004..395_003 REFUSED at its own start by the W171 B "',
     '"395_204..397_203 REFUSED at its own start by the W172 B "', 1),
    ('"band 393_004..393_203, exactly as the W171 seat W172+ projection + "',
     '"band 395_204..395_403, exactly as the W172 seat W173+ projection + "', 1),
    ('"r814 probe leg4 + r819 sec8 succession projection notes "',
     '"r818 probe leg4 + r819 sec8 succession projection notes "', 1),
    ('"staircase thirty-first instance, E36 card)"',
     '"staircase THIRTY-THIRD instance, E36 card)"', 1),
    ("arith_a171 = set(range(393_204, 395_204))",
     "arith_a172 = set(range(395_404, 397_404))", 1),
    ("assert not (arith_a171 & reg_ints), \\",
     "assert not (arith_a172 & reg_ints), \\", 1),
    ('"W172 A window must be CLEAN (first-clean ADMIT face past prior-wave B)"',
     '"W173 A window must be CLEAN (first-clean ADMIT face past prior-wave B)"', 1),
    ("assert WAVE_CONFIGS[172][\"b_exit_seed_base\"] == 395_204 == 395_203 + 1, (",
     "assert WAVE_CONFIGS[173][\"b_exit_seed_base\"] == 397_404 == 397_403 + 1, (", 1),
    ('"W172 B must be the first-clean window past the own-wave A "',
     '"W173 B must be the first-clean window past the own-wave A "', 1),
    ('"band tail 395_203+1 (arithmetic continuation "',
     '"band tail 397_403+1 (arithmetic continuation "', 1),
    ('"393_204..393_403 CLEAN on the registered universe but "',
     '"395_404..395_603 CLEAN on the registered universe but "', 1),
    ('"lands INSIDE the W172 A band window; same-freeze mutual "',
     '"lands INSIDE the W173 A band window; same-freeze mutual "', 1),
    ('"own-wave A window reserved jumps to 395_204, first-clean "',
     '"own-wave A window reserved jumps to 397_404, first-clean "', 1),
    ("arith_b171 = set(range(395_204, 395_404))",
     "arith_b172 = set(range(397_404, 397_604))", 1),
    ("assert not (arith_b171 & reg_ints), \\",
     "assert not (arith_b172 & reg_ints), \\", 1),
    ('"W172 B window must be CLEAN (first-clean ADMIT face past own-wave A)"',
     '"W173 B window must be CLEAN (first-clean ADMIT face past own-wave A)"', 1),
    ("assert not (arith_b171 & arith_a171), \\",
     "assert not (arith_b172 & arith_a172), \\", 1),
    ('"W172 A/B same-freeze mutual exclusion (B hops past own A)"',
     '"W173 A/B same-freeze mutual exclusion (B hops past own A)"', 1),
    ("assert _entry_shard_of(0, 12) == (\"PERPETUAL-N1-W172-SHARD-0\",",
     "assert _entry_shard_of(0, 12) == (\"PERPETUAL-N1-W173-SHARD-0\",", 1),
    ('"n1w172-0of12"), "W172 entry identity"',
     '"n1w173-0of12"), "W173 entry identity"', 1),
    ("assert _entry_shard_of(11, 12) == (\"PERPETUAL-N1-W172-SHARD-11\",",
     "assert _entry_shard_of(11, 12) == (\"PERPETUAL-N1-W173-SHARD-11\",", 1),
    ('"n1w172-11of12")', '"n1w173-11of12")', 1),
    ('assert SHARD_DIR.endswith("n1_w172") and OUT.endswith(',
     'assert SHARD_DIR.endswith("n1_w173") and OUT.endswith(', 1),
    ('"n1_w172_results.json"), "W172 path drift"',
     '"n1_w173_results.json"), "W173 path drift"', 1),
    ('f"W172 shard dir collides with W{wprev}"',
     'f"W173 shard dir collides with W{wprev}"', 1),
    ("# W172 finalize cumulative deps: W17..W171 outputs ALL PRESENT",
     "# W173 finalize cumulative deps: W17..W172 outputs ALL PRESENT", 1),
    ("# (landed net chain head 781,612 = W171 bm-a r816 one-pass --",
     "# (landed net chain head 783,812 = W172 bm-a r819 one-pass --", 1),
    ("for _depw in range(17, 172):", "for _depw in range(17, 173):", 1),
    ('f"W172 finalize cumulative dep (W{_depw} output) missing"',
     'f"W173 finalize cumulative dep (W{_depw} output) missing"', 1),
    ("# registered wave below 172 composes; wave 15 excluded by",
     "# registered wave below 173 composes; wave 15 excluded by", 1),
    ("# design; SINGLE STATE (W2..W171 all registered -- no",
     "# design; SINGLE STATE (W2..W172 all registered -- no", 1),
    ("assert sorted(w for w in WAVE_CONFIGS if w < 172) == \\",
     "assert sorted(w for w in WAVE_CONFIGS if w < 173) == \\", 1),
    ("[w for w in range(16, 172)], \\", "[w for w in range(16, 173)], \\", 1),
    ('"W172 prior-wave set must derive from registry keys (no 15; "',
     '"W173 prior-wave set must derive from registry keys (no 15; "', 1),
    ('"W2..W171 registered single state)"', '"W2..W172 registered single state)"', 1),
    ('PATHS.root, "research", "PERPETUAL_N1_W172_PREREG.md")), \\',
     'PATHS.root, "research", "PERPETUAL_N1_W173_PREREG.md")), \\', 1),
    ('"W172 per-wave prereg missing (materializer requirement)"',
     '"W173 per-wave prereg missing (materializer requirement)"', 1),
]
# negative tokens are surgical: the CARRIED parity chain keeps its
# historical stamps (W138..W171 rows cite r743..r815; the W171 row's
# b_exit tuple contains 393_004/393_203), and the APPENDED W172 parity
# row keeps its (393_204, 395_203) tuple -- bare numerals are therefore
# forbidden as negatives; only W172-era assert/comment forms qualify.
MAT_NEG = ["w171_", "arith_a171", "arith_b171", "n3r1_used171", "r814 probe",
           "r813 sec8", "r818 pre-seat", "01a7480e1", "456f3affc, SINGLE",
           "== 393_204 ==", "set(range(393_204", "393_004..",
           "and lands 395_204..395_403", "INSIDE the W172",
           "thirty-first", "W172-SHARD", '"n1_w172', "n1w172", "781,612",
           "374,120", "SIXTY-SECOND", "eighty-seventh", "rows 161",
           "rows 87 ", "range(17, 172)", "range(16, 172)", "W1..W171",
           "wave 171 =", "PERPETUAL_N1_W172", "PERPETUAL-N1-W172",
           "MSG-1012", "_r818bma", "DEFERRED", "the W171 seat",
           "W171 B band", "W171 finalize", "bm-a r815 freeze",
           "the W172 seat MSG sits in", "W172 (bm-a", "W172 materializer",
           "W172 A band window", "W172 A window", "W172 B window",
           "W172 A/B", "W172 hits", "W172 bands", "W172 entry identity",
           "W172 path drift", "W172 shard dir", "W172 finalize cumulative",
           "W172 prior-wave", "W172 per-wave", "W172 engine_owner drift",
           "W172 A band drift", "W172 B band drift", "W172 A/B band"]
mat173 = "    " + vmap(mat, MAT_PAIRS, MAT_NEG, "mat")

# ---- face 4: n1 W173 PASS-claim attribution -----------------------------
CL_PAIRS = [
    ('"+ W172 materializer face [same guard set, dep=W17..W171 ',
     '"+ W173 materializer face [same guard set, dep=W17..W172 ', 1),
    ('"outputs ALL PRESENT (landed net chain head 781,612 = "',
     '"outputs ALL PRESENT (landed net chain head 783,812 = "', 1),
    ('"W171 bm-a r816 one-pass, K=374,120 merged pool; ZERO "',
     '"W172 bm-a r819 one-pass, K=376,320 merged pool; ZERO "', 1),
    ('"in-flight upstream seats), ONE HUNDRED-AND-SIXTY-SECOND "',
     '"in-flight upstream seats), ONE HUNDRED-AND-SIXTY-THIRD "', 1),
    ('"ENGINE-OWNED WAVE BY MACHINE-DERIVE (engine_owner rows 161 "',
     '"ENGINE-OWNED WAVE BY MACHINE-DERIVE (engine_owner rows 162 "', 1),
    ("+ candidate) bm-a's eighty-seventh owned claim per ",
     "+ candidate) bm-a's eighty-ninth owned claim per ", 1),
    ('"machine-derive (engine_owner==bm-a rows 87 + candidate), "',
     '"machine-derive (engine_owner==bm-a rows 88 + candidate), "', 1),
    ('"A=FIRST-CLEAN past the registered W171 B band (staircase "',
     '"A=FIRST-CLEAN past the registered W172 B band (staircase "', 1),
    ('"thirty-first instance, E36 card, hops=1) + B=FIRST-CLEAN past the "',
     '"THIRTY-THIRD instance, E36 card, hops=1) + B=FIRST-CLEAN past the "', 1),
    ('"results/_r818bma_w172_probe_receipt.json, law sec.4 W172 row, "',
     '"results/_r820bma_w173_probe_receipt.json, law sec.4 W173 row, "', 1),
    ('"r819 bm-a] "', '"r822 bm-a] "', 1),
]
CL_NEG = ["W172 materializer", "781,612", "374,120", "SIXTY-SECOND",
          "eighty-seventh", "rows 161", "rows 87 ", "thirty-first",
          "W171 B band", "_r818bma", "W172 row,", "r819 bm-a]"]
claim173 = IND10 + vmap(claim, CL_PAIRS, CL_NEG, "claim")

# ---- apply insertions (in-memory) ---------------------------------------
pfsrc = io.open(PF, encoding="utf-8", newline="").read()
n1src = io.open(N1, encoding="utf-8", newline="").read()

# pf: insert W173 block after the W172 row (last registered), before the
# dict close -- r560 insert-after-last-registered-row + post-anchor gate
seg = EO + NL + "}"
check(pfsrc.count(seg) == 1, "pf row-close segment not unique")
pfnew = pfsrc.replace(seg, EO + NL + blk173 + NL + "}", 1)

# n1 entry: after the W172 entry, before the WAVE_CONFIGS close
seg = EO + NL + IND23 + "}"
check(n1src.count(seg) == 1, "n1 entry-close segment not unique")
n1new = n1src.replace(seg, EO + NL + entry173 + NL + IND23 + "}", 1)

# n1 mat: insert the W173 block before the T-141 s2 lane face header
seg = "    # --- T-141 s2 lane face"
check(n1new.count(seg) == 1, "n1 T-141 mat anchor not unique")
n1new = n1new.replace(seg, mat173 + NL + seg, 1)

# n1 claim: insert the W173 attribution after the W172 claim tail line
# (r581 law: anchor = tail single-line literal + post-anchor guard)
seg = '"r819 bm-a] "' + NL + IND10 + '"+ T-141 s2 "'
check(n1new.count(seg) == 1, "n1 claim anchor not unique")
n1new = n1new.replace(seg, '"r819 bm-a] "' + NL + claim173 + NL + IND10 +
                      '"+ T-141 s2 "', 1)

# ---- gates (r780/r781/r560/r815 lineage) --------------------------------
ast.parse(pfnew)
ast.parse(n1new)
print("AST gate: both files parse OK")

# W173 presence + W172 anti-vanish (r560 law)
checks = [
    (pfnew, '173: {"a": (395_404, 397_403), "b_exit": (397_404, 397_603),', 1),
    (pfnew, '172: {"a": (393_204, 395_203), "b_exit": (395_204, 395_403),', 1),
    (pfnew, "# W173 (bm-a r822 freeze", 1),
    (pfnew, "# W172 (bm-a r819 freeze", 1),
    (n1new, '173: {"batch": "PERPETUAL-N1-W173",', 1),
    (n1new, '172: {"batch": "PERPETUAL-N1-W172",', 1),
    (n1new, "# --- W173 materializer face", 1),
    (n1new, "# --- W172 materializer face", 1),
    (n1new, '"r822 bm-a] "', 1),
    (n1new, '"r819 bm-a] "', 1),
    (n1new, '"a_seed_base": 395_404,', 1),
    (n1new, '"b_exit_seed_base": 397_404,', 1),
    (n1new, "n1_w173", 4),
    (n1new, "PERPETUAL_N1_W173_PREREG.md", 2),
]
for src, needle, cnt in checks:
    got = src.count(needle)
    check(got == cnt, "post-edit needle %r count %d != %d" % (needle[:50], got, cnt))

# W174 projection prose present in the new W173 blocks (probe leg4
# verbatim; r819 post-edit assert bloodline + r776 fragment-needle law)
check("# W173+ projection (gate-derived r820)" in pfnew,
      "pf W173+ projection head missing")
check('probe_receipt.json; W174+ projection "' in n1new,
      "n1 W174+ projection head fragment missing")
check("# 397_404..399_403 CLEAN hops=0 / B first-clean 397_604..397_803" in pfnew,
      "pf W174p prose missing")
check("W174 A window; W174 freezer MUST re-derive on the post-W173" in pfnew,
      "pf W174 freezer prose missing")
check('"W174 A window; W174 freezer MUST re-derive on the "' in n1new,
      "n1 W174 freezer fragment missing")
check('"W173 B band 397_404..397_603 will refuse the naive "' in n1new,
      "n1 W173-band refuse fragment missing")

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

# ---- live writes: n1 FIRST then pf (engine queue derive keyses off the
# pf N1_BANDS row -- a row without a WAVE_CONFIGS entry would be a dead
# face for one tick; an entry without a row never ignites (safe order) --
# r666 law window face) ----------------------------------------------------
io.open(N1, "w", encoding="utf-8", newline="").write(n1new)
io.open(PF, "w", encoding="utf-8", newline="").write(pfnew)
print("LIVE WRITES DONE: pf %d->%d B, n1 %d->%d B" %
      (len(pfsrc), len(pfnew), len(n1src), len(n1new)))
print("freeze edits rc0: 4 insertions landed (pf row + n1 entry + mat + claim)")
