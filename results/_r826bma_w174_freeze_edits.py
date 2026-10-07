# -*- coding: utf-8 -*-
"""r826 bm-a W174 freeze edits: four insertions (pf N1_BANDS[174] row +
n1 WAVE_CONFIGS[174] entry + n1 W174 materializer block + n1 W174
PASS-claim attribution). DRY flag: --dry = zero-write simulation
(r781 verify-separation law + r811/r822 dry-run precedent: full
stale+prose+AST asserts in memory BEFORE any write).

Bloodline: r819/r822 freeze-edits machinery (r773 pit law freeze-editor
compliance + r776 fragment-needle law + r781 verify-separation law),
W174 facts live-registry-driven:
  - pre-seat probe results/_r823bma_w174_probe_receipt.json rc0 ADMIT
    (A 397_604..399_603 staircase THIRTY-FOURTH instance E36 hops=1
    past the registered W173 B band 397_404..397_603; naive
    397_404..399_403 refused at its own start by the W173 B band --
    receipt A_semantics machine-cites 'W173 prereg sec5 item5 +
    W173 seat MSG leg4 + r820 probe leg4' anticipation + MANDATE; B
    399_604..399_803 own-A mutual exclusion hops=1, naive
    397_604..397_803);
  - ordinal convergence: W173 sec5.5 prose anticipated 34th, r823
    receipt machine-read THIRTY-FOURTH -- no divergence this wave
    (contrast W173's 32nd/THIRTY-THIRD divergence disclosed r822);
  - prereg citation slip disclosed: the frozen W174 prereg (cf9a8e1fe)
    prose says 'r823 probe leg4' in the anticipation quad while the
    machine receipt A_semantics says 'r820 probe leg4' (the W173
    pre-seat probe whose leg4 carried the W174+ projection); the NEW
    faces carry the machine-receipt citation per r587, prereg face not
    edited per freeze discipline (r821/r822 same-slip precedent);
  - face probe results/_r826bma_w174_face_probe_receipt.json rc0 (all
    four W173 faces dumped + needle counts; this TOK is built from the
    PHYSICAL probe-dumped shapes, r776 law);
  - seat MSG-2026-10-07-1247-bma-w174-seat published on origin at
    9b0e1cb29 (r823 pre-seat push, path-derived TRUE sha per r812
    precedent); r565 law: on origin BEFORE this freeze commit;
    self-ack archive ALREADY LANDED pre-freeze -- r823 same-window
    self-ack move (the seat MSG sits in fleet/inbox/processed/ at
    freeze time, honest archived);
  - per-wave prereg research/PERPETUAL_N1_W174_PREREG.md frozen at
    origin cf9a8e1fe (r825 build, banned gate ADMIT 0 re-verified at
    freeze this window);
  - W173 freeze registered sha machine-derived = 04e95748a (git log
    origin/main --grep "W173 FREEZE"); W173 finalize one-pass landed
    r823: ledger head 786,012, merged pool K=378,520
    (n1_w173_results.json machine-read);
  - lineage constants disclosed (r795 precedent, passed through):
    (a) the "wave N-1:" entry label + "wave N-1 = first free number"
    mat-header label ride the vmap verbatim (off-by-one lineage quirk
    since the W165 r795 band-facts template);
    (b) "law sec.4 W174 row, r795" band-facts template stamp keeps
    its r795;
    (c) "single-window derive (r812 merged the gate legs INTO the
    pre-seat probe...)" stays (historical merge citation);
    (d) the bm-a-owned ordinal word rolls eighty-ninth -> ninetieth
    (rows 89 + candidate = 90th owned per probe leg0);
    (e) mat B-face convergence universe-token stale carry healed
    post-W171 -> post-W173 (the live W173 block carried the
    W172-era 'post-W171' token untransformed -- r822 sec8-heal
    one-token precedent; the live W173 block face itself NOT edited
    per freeze discipline; heal applies to the NEW W174 block only).

r773 pit law compliance:
  (1) full string-face inventory empirically probed BEFORE TOK
      (_r826bma_w174_face_probe.py -- four face dumps + needle-count
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
      (r530/r687: fetch + origin carries no W174 registration before
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
probe = json.load(open(r"results\_r823bma_w174_probe_receipt.json",
                       encoding="utf-8"))
check(probe["verdict"] == "ADMIT", "pre-seat probe not ADMIT")
check(probe["bands"] == {"A": "397604_399603", "B": "399604_399803"},
      "probe band shape mismatch")
check(probe["legs"]["leg1"]["A"] == [397604, 399603], "A band mismatch")
check(probe["legs"]["leg1"]["B"] == [399604, 399803], "B band mismatch")
check(probe["legs"]["leg1"]["hops_A"] == 1 and probe["legs"]["leg1"]["hops_B"] == 1,
      "hops mismatch")
check(probe["legs"]["leg0"]["rows"] == 171 and probe["legs"]["leg0"]["tail"] == "W173",
      "leg0 registry tail mismatch")
check(probe["legs"]["leg0"]["ordinal"] == 164 and probe["legs"]["leg0"]["bma_ordinal"] == 90,
      "leg0 ordinal mismatch")
check(probe["legs"]["leg2"]["conflicts"] == 0, "leg2 conflicts nonzero")
check(probe["legs"]["leg3"]["origin_vacancy"] is True, "leg3 origin not vacant")
check(probe["legs"]["leg4"]["W175p_A"] == "399604..401603"
      and probe["legs"]["leg4"]["W175p_B"] == "399804..400003",
      "leg4 W175+ projection mismatch")

# origin anti-collision pre-check (r511 tail-lock / r687 write-time gate)
subprocess.run(["git", "fetch", "origin"], capture_output=True)
pf_o = subprocess.run(["git", "show", "origin/main:" + PF],
                      capture_output=True).stdout.decode("utf-8", "replace")
n1_o = subprocess.run(["git", "show", "origin/main:" + N1],
                      capture_output=True).stdout.decode("utf-8", "replace")
check('174: {"a": (397_604' not in pf_o, "origin pf already carries W174 row")
check("W174 (bm-a r826 freeze" not in pf_o, "origin pf carries W174 block")
check('174: {"batch"' not in n1_o, "origin n1 already carries W174 entry")
check("# --- W174 materializer face" not in n1_o, "origin n1 carries W174 mat")
check('"r826 bm-a] "' not in n1_o, "origin n1 carries W174 claim")

# machine-derived shas (r587 / r812 path-derived precedent)
seat_sha = subprocess.run(
    ["git", "log", "origin/main", "--format=%h", "-n", "1", "--diff-filter=A",
     "--", "fleet/inbox/MSG-2026-10-07-1247-bma-w174-seat.md"],
    capture_output=True).stdout.decode().strip()
check(seat_sha == "9b0e1cb29", "seat sha path-derived mismatch: " + seat_sha)
w173_freeze_sha = subprocess.run(
    ["git", "log", "origin/main", "--format=%h", "-n", "1", "--grep=W173 FREEZE"],
    capture_output=True).stdout.decode().strip()
check(w173_freeze_sha == "04e95748a", "W173 freeze sha mismatch: " + w173_freeze_sha)

# ---- live-registry parity pre-check (edit-gate: never edit a drifted file)
sys.path.insert(0, "scripts")
import perpetual_faces as pfmod  # noqa: E402
check(len(pfmod.N1_BANDS) == 171, "live N1_BANDS row count drift: %d" % len(pfmod.N1_BANDS))
check(pfmod.N1_BANDS[173] == {"a": (395_404, 397_403),
                              "b_exit": (397_404, 397_603),
                              "engine_owner": "bm-a"}, "live W173 row drift")
check(174 not in pfmod.N1_BANDS, "live N1_BANDS already has 174")
check(os.path.exists(os.path.join("research", "PERPETUAL_N1_W174_PREREG.md")),
      "W174 per-wave prereg missing (materializer gate)")
prereg_o = subprocess.run(["git", "show", "origin/main:research/PERPETUAL_N1_W174_PREREG.md"],
                          capture_output=True)
check(prereg_o.returncode == 0, "W174 prereg absent on origin")

# ---- physical face dumps (r776 law) -----------------------------------
pfblk = io.open(r"results\_r826bma_w174_probe_pf_block.txt", encoding="utf-8",
                newline="").read()
entry = io.open(r"results\_r826bma_w174_probe_n1_entry.txt", encoding="utf-8",
                newline="").read()
mat = io.open(r"results\_r826bma_w174_probe_n1_mat.txt", encoding="utf-8",
              newline="").read()
claim = io.open(r"results\_r826bma_w174_probe_n1_claim.txt", encoding="utf-8",
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


# ---- face 1: pf N1_BANDS[174] comment block + row -----------------------
PF_PAIRS = [
    ("    # W173 (bm-a r822 freeze, seat MSG-2026-10-07-1122-bma-w173-seat",
     "    # W174 (bm-a r826 freeze, seat MSG-2026-10-07-1247-bma-w174-seat", 1),
    ("pushed to origin 9cd8af3af pre-freeze r565 law (r820 pre-seat",
     "pushed to origin 9b0e1cb29 pre-freeze r565 law (r823 pre-seat", 1),
    ("(3-item; the W172 finalize product already on origin since r819,",
     "(3-item; the W173 finalize product already on origin since r823,", 1),
    ("# = direct fast-forward behind-0 at fetch (r820 pre-seat",
     "# = direct fast-forward behind-0 at fetch (r823 pre-seat", 1),
    ("# push), zero merge, zero --no-verify; self-ack archive ALREADY" + NL +
     "    # LANDED pre-freeze -- bm-c r672 inbox sweep observed-archived" + NL +
     "    # the bm-a-lane seat MSG at 11:41:55 (the W173 seat MSG sits in" + NL +
     "    # fleet/inbox/processed/ at freeze time, honest archived);",
     "# push), zero merge, zero --no-verify; self-ack archive ALREADY" + NL +
     "    # LANDED pre-freeze -- r823 same-window self-ack move (the W174" + NL +
     "    # seat MSG sits in fleet/inbox/processed/ at freeze time, honest" + NL +
     "    # archived);", 1),
    ("band gate ADMIT results/_r820bma_w173_probe_receipt.json: A = FIRST-CLEAN",
     "band gate ADMIT results/_r823bma_w174_probe_receipt.json: A = FIRST-CLEAN", 1),
    ("past the registered W172 B band (arithmetic continuation",
     "past the registered W173 B band (arithmetic continuation", 1),
    ("395_204..397_203 REFUSED at its own start by the W172 B band",
     "397_404..399_403 REFUSED at its own start by the W173 B band", 1),
    ("395_204..395_403, exactly as the W172 seat W173+ projection + r818 probe",
     "397_404..397_603, exactly as the W173 seat W174+ projection + r820 probe", 1),
    ("# leg4 + r819 sec8 succession projection notes all anticipated;",
     "# leg4 + r823 sec8 succession projection notes all anticipated;", 1),
    ("honest forward walk hops=1 -> 395_404..397_403, non-rotational",
     "honest forward walk hops=1 -> 397_604..399_603, non-rotational", 1),
    ("(395_403+1) machine-checkable -- A-hops-prior-B staircase",
     "(397_603+1) machine-checkable -- A-hops-prior-B staircase", 1),
    ("THIRTY-THIRD instance, E36 card);",
     "THIRTY-FOURTH instance, E36 card);", 1),
    ("continuation 395_404..395_603 CLEAN on the registered universe",
     "continuation 397_604..397_803 CLEAN on the registered universe", 1),
    ("but lands INSIDE the W173 A band window -- same-freeze mutual",
     "but lands INSIDE the W174 A band window -- same-freeze mutual", 1),
    ("own-wave A window reserved jumps to 397_404 -> 397_404..397_603,",
     "own-wave A window reserved jumps to 399_604 -> 399_604..399_803,", 1),
    ("own-wave A tail+1 (397_403+1) machine-checkable);",
     "own-wave A tail+1 (399_603+1) machine-checkable);", 1),
    ("W173+ projection (gate-derived r820): A first-clean",
     "W174+ projection (gate-derived r823): A first-clean", 1),
    ("397_404..399_403 CLEAN hops=0 / B first-clean 397_604..397_803",
     "399_604..401_603 CLEAN hops=0 / B first-clean 399_804..400_003", 1),
    ("registered W173 B band 397_404..397_603 will refuse the naive",
     "registered W174 B band 399_604..399_803 will refuse the naive", 1),
    ("W174 A window; W174 freezer MUST re-derive on the post-W173",
     "W175 A window; W175 freezer MUST re-derive on the post-W174", 1),
    ("NOT a re-pick (R250: W173 bands were never assigned).",
     "NOT a re-pick (R250: W174 bands were never assigned).", 1),
    ('173: {"a": (395_404, 397_403), "b_exit": (397_404, 397_603),',
     '174: {"a": (397_604, 399_603), "b_exit": (399_604, 399_803),', 1),
]
PF_NEG = ["9cd8af3af", "r818 probe", "r819 sec8", "r820 pre-seat", "_r820bma",
          "MSG-2026-10-07-1122", "bm-c r672", "395_204", "395_404", "395_603",
          "395_403+1", "397_403+1", "W172", "W173 (bm-a", "INSIDE the W173",
          "THIRTY-THIRD", "W173+ projection (", "R250: W173", "W173 bands were",
          "783,812", "376,320", "the W173 seat MSG sits in", "since r819,",
          "r822 freeze"]
blk174 = vmap(pfblk, PF_PAIRS, PF_NEG, "pf")

# ---- face 2: n1 WAVE_CONFIGS[174] entry ---------------------------------
EN_PAIRS = [
    ('173: {"batch": "PERPETUAL-N1-W173",', '174: {"batch": "PERPETUAL-N1-W174",', 1),
    ('"prereg": ("research/PERPETUAL_N1_W173_PREREG.md (wave-level frozen "',
     '"prereg": ("research/PERPETUAL_N1_W174_PREREG.md (wave-level frozen "', 1),
    ('new seed bands only; ONE HUNDRED-AND-SIXTY-THIRD ENGINE-OWNED WAVE ',
     'new seed bands only; ONE HUNDRED-AND-SIXTY-FOURTH ENGINE-OWNED WAVE ', 1),
    ('BY MACHINE-DERIVE (engine_owner rows 162 + candidate), ',
     'BY MACHINE-DERIVE (engine_owner rows 163 + candidate), ', 1),
    ('number law after the REGISTERED W172 row bm-a r819 freeze ',
     'number law after the REGISTERED W173 row bm-a r822 freeze ', 1),
    ('59fde9319, SINGLE STATE zero seat gap W2..W172 all ',
     '04e95748a, SINGLE STATE zero seat gap W2..W173 all ', 1),
    ('registered; W172 finalize landed same-window r819, ledger ',
     'registered; W173 finalize landed same-window r823, ledger ', 1),
    ('head 783,812, merged pool K=376,320; seat published=reserved ',
     'head 786,012, merged pool K=378,520; seat published=reserved ', 1),
    ('MSG-2026-10-07-1122-bma-w173-seat PUSHED to origin 9cd8af3af ',
     'MSG-2026-10-07-1247-bma-w174-seat PUSHED to origin 9b0e1cb29 ', 1),
    ('probe receipt (3-item; the W172 finalize product already on origin since r819, not re-shipped; W146 precedent); ',
     'probe receipt (3-item; the W173 finalize product already on origin since r823, not re-shipped; W146 precedent); ', 1),
    ('at fetch (r820 pre-seat push), zero merge, zero ',
     'at fetch (r823 pre-seat push), zero merge, zero ', 1),
    ('engine_owner=bm-a, wave 172: ',
     'engine_owner=bm-a, wave 173: ', 1),
    ('A = FIRST-CLEAN past the registered W172 B band (the ',
     'A = FIRST-CLEAN past the registered W173 B band (the ', 1),
    ('arithmetic continuation 395_204..397_203 is REFUSED at its ',
     'arithmetic continuation 397_404..399_403 is REFUSED at its ', 1),
    ('own start by the W172 B band 395_204..395_403, exactly as ',
     'own start by the W173 B band 397_404..397_603, exactly as ', 1),
    ('the W172 seat W173+ projection + r818 probe leg4 + r819 sec8 succession ',
     'the W173 seat W174+ projection + r820 probe leg4 + r823 sec8 succession ', 1),
    ('projection notes anticipated; honest forward walk hops=1 -> ',
     'projection notes anticipated; honest forward walk hops=1 -> ', 1),
    ('395_404..397_403; A base == prior-wave B tail+1 ',
     '397_604..399_603; A base == prior-wave B tail+1 ', 1),
    ('machine-checkable = A-hops-prior-B staircase THIRTY-THIRD ',
     'machine-checkable = A-hops-prior-B staircase THIRTY-FOURTH ', 1),
    ('arithmetic continuation 395_404..395_603 is CLEAN on the ',
     'arithmetic continuation 397_604..397_803 is CLEAN on the ', 1),
    ('registered universe but lands INSIDE the W173 A band ',
     'registered universe but lands INSIDE the W174 A band ', 1),
    ('jumps to 397_404, first-clean 397_404..397_603 hops=1, ',
     'jumps to 399_604, first-clean 399_604..399_803 hops=1, ', 1),
    ('convergence with the W172 seat W173+ projection + r818 probe leg4 + ',
     'convergence with the W173 seat W174+ projection + r820 probe leg4 + ', 1),
    ('r819 sec8 succession projection notes re-derived -- all ',
     'r823 sec8 succession projection notes re-derived -- all ', 1),
    ('MANDATORY notes honored (post-W172 universe re-derive + ',
     'MANDATORY notes honored (post-W173 universe re-derive + ', 1),
    ('results/_r820bma_w173_probe_receipt.json; W174+ projection ',
     'results/_r823bma_w174_probe_receipt.json; W175+ projection ', 1),
    ('per this window gate: A first-clean 397_404..399_403 ',
     'per this window gate: A first-clean 399_604..401_603 ', 1),
    ('CLEAN / B first-clean 397_604..397_803 CLEAN -- naive ',
     'CLEAN / B first-clean 399_804..400_003 CLEAN -- naive ', 1),
    ('W173 B band 397_404..397_603 will refuse the naive ',
     'W174 B band 399_604..399_803 will refuse the naive ', 1),
    ('W174 A window; W174 freezer MUST re-derive on the ',
     'W175 A window; W175 freezer MUST re-derive on the ', 1),
    ('post-W173 universe AND reserve the own-wave A window ',
     'post-W174 universe AND reserve the own-wave A window ', 1),
    ('staircase card); W1..W172 finalize ALL LANDED (W172 ',
     'staircase card); W1..W173 finalize ALL LANDED (W173 ', 1),
    ('finalize one-pass bm-a r819, net chain head 783,812, ',
     'finalize one-pass bm-a r823, net chain head 786,012, ', 1),
    ('merged pool K=376,320) -- ZERO in-flight upstream ',
     'merged pool K=378,520) -- ZERO in-flight upstream ', 1),
    ('"a_seed_base": 395_404,        # law sec.4 W173 A: 395_404..397_403 (FIRST-CLEAN past the registered W172 B band; arithmetic 395_204..397_203 REFUSED at own start by the W172 B band; hops=1; A-hops-prior-B staircase THIRTY-THIRD instance, E36 card; ordinal divergence disclosed per r587: W172 sec5.5 prose anticipated thirty-second, r820 receipt machine-read THIRTY-THIRD)',
     '"a_seed_base": 397_604,        # law sec.4 W174 A: 397_604..399_603 (FIRST-CLEAN past the registered W173 B band; arithmetic 397_404..399_403 REFUSED at own start by the W173 B band; hops=1; A-hops-prior-B staircase THIRTY-FOURTH instance, E36 card; ordinal convergence per r587: W173 sec5.5 prose anticipated thirty-fourth, r823 receipt machine-read THIRTY-FOURTH)', 1),
    ('"b_exit_seed_base": 397_404,   # law sec.4 W173 B: 397_404..397_603 (FIRST-CLEAN past the own-wave A window; arithmetic 395_404..395_603 lands inside own-A, same-freeze mutual exclusion W141 precedent; reserved walk hops=1; B base == own-A tail+1)',
     '"b_exit_seed_base": 399_604,   # law sec.4 W174 B: 399_604..399_803 (FIRST-CLEAN past the own-wave A window; arithmetic 397_604..397_803 lands inside own-A, same-freeze mutual exclusion W141 precedent; reserved walk hops=1; B base == own-A tail+1)', 1),
    ('"shard_subdir": "n1_w173", "out_name": "n1_w173_results.json",',
     '"shard_subdir": "n1_w174", "out_name": "n1_w174_results.json",', 1),
]
EN_NEG = ["9cd8af3af", "59fde9319", "783,812", "376,320", "SIXTY-THIRD",
          "rows 162", "r818 probe", "_r820bma", "r820 pre-seat", "r819 sec8",
          "MSG-2026-10-07-1122", "n1_w173", "n1w173", "PERPETUAL-N1-W173",
          "PERPETUAL_N1_W173", "W172 finalize", "thirty-second", "THIRTY-THIRD",
          "bm-a r819 freeze", "wave 172: ", "W173 A band", "INSIDE the W173",
          "W173+ projection", "395_204", "395_404", "397_404, first-clean",
          "W1..W172", "W172 B band", "R250"]
entry174 = IND23 + vmap(entry, EN_PAIRS, EN_NEG, "entry")

# ---- face 3: n1 W174 materializer block ---------------------------------
MAT_PAIRS = [
    ("# --- W173 materializer face (r822 bm-a freeze, own-series law",
     "# --- W174 materializer face (r826 bm-a freeze, own-series law", 1),
    ("#     eighty-ninth owned per machine-derive (engine_owner==bm-a",
     "#     ninetieth owned per machine-derive (engine_owner==bm-a", 1),
    ("#     rows 88 + candidate); wave 172 = first free number after",
     "#     rows 89 + candidate); wave 173 = first free number after", 1),
    ("#     the REGISTERED W172 row (bm-a r819 freeze 59fde9319) --",
     "#     the REGISTERED W173 row (bm-a r822 freeze 04e95748a) --", 1),
    ("#     SINGLE STATE zero seat gap (W2..W172 all registered). Seat",
     "#     SINGLE STATE zero seat gap (W2..W173 all registered). Seat", 1),
    ("#     published=reserved MSG-2026-10-07-1122-bma-w173-seat pushed",
     "#     published=reserved MSG-2026-10-07-1247-bma-w174-seat pushed", 1),
    ("#     to origin 9cd8af3af BEFORE this freeze, r565 law (payload",
     "#     to origin 9b0e1cb29 BEFORE this freeze, r565 law (payload", 1),
    ("#     the W172 finalize product already on origin since r819, not",
     "#     the W173 finalize product already on origin since r823, not", 1),
    ("#     at fetch (r820 pre-seat push), zero merge, zero",
     "#     at fetch (r823 pre-seat push), zero merge, zero", 1),
    ("#     --no-verify; self-ack inbox->processed archive ALREADY LANDED" + NL +
     "    #     pre-freeze -- bm-c r672 inbox sweep observed-archived the" + NL +
     "    #     bm-a-lane seat MSG at 11:41:55 (the W173 seat MSG sits in" + NL +
     "    #     fleet/inbox/processed/ at freeze time, honest archived).",
     "#     --no-verify; self-ack inbox->processed archive ALREADY LANDED" + NL +
     "    #     pre-freeze -- r823 same-window self-ack move (the W174 seat" + NL +
     "    #     MSG sits in fleet/inbox/processed/ at freeze time, honest" + NL +
     "    #     archived).", 1),
    ("#     ONE HUNDRED-AND-SIXTY-THIRD engine wave BY",
     "#     ONE HUNDRED-AND-SIXTY-FOURTH engine wave BY", 1),
    ("#     MACHINE-DERIVE (engine_owner rows 162 + candidate; gate",
     "#     MACHINE-DERIVE (engine_owner rows 163 + candidate; gate", 1),
    ("#     W1..W172 finalize ALL LANDED (net chain head 783,812,",
     "#     W1..W173 finalize ALL LANDED (net chain head 786,012,", 1),
    ("#     K=376,320 merged pool; W172 finalize one-pass bm-a r819)",
     "#     K=378,520 merged pool; W173 finalize one-pass bm-a r823)", 1),
    ("#     always on. ADMIT receipt results/_r820bma_w173_probe_receipt.json;",
     "#     always on. ADMIT receipt results/_r823bma_w174_probe_receipt.json;", 1),
    ("#     banned gate ADMIT 0; not a re-pick (R250: W173 bands were",
     "#     banned gate ADMIT 0; not a re-pick (R250: W174 bands were", 1),
    ("    _set_wave(173)", "    _set_wave(174)", 1),
    ('assert WAVE_CONFIGS[172]["a_seed_base"] == pf.N1_BANDS[172]["a"][0], \\',
     'assert WAVE_CONFIGS[173]["a_seed_base"] == pf.N1_BANDS[173]["a"][0], \\', 1),
    ('"W173 A band drift vs law mirror"', '"W174 A band drift vs law mirror"', 1),
    ('assert WAVE_CONFIGS[172]["b_exit_seed_base"] == \\',
     'assert WAVE_CONFIGS[173]["b_exit_seed_base"] == \\', 1),
    ('pf.N1_BANDS[172]["b_exit"][0], "W173 B band drift vs law mirror"',
     'pf.N1_BANDS[173]["b_exit"][0], "W174 B band drift vs law mirror"', 1),
    ('assert WAVE_CONFIGS[172].get("engine_owner") == \\',
     'assert WAVE_CONFIGS[173].get("engine_owner") == \\', 1),
    ('pf.N1_BANDS[172].get("engine_owner") == "bm-a", \\',
     'pf.N1_BANDS[173].get("engine_owner") == "bm-a", \\', 1),
    ('"W173 engine_owner drift (law mirror parity)"',
     '"W174 engine_owner drift (law mirror parity)"', 1),
    ("w172_a = {A_SEED_BASE + j for j in range(A_N)}",
     "w173_a = {A_SEED_BASE + j for j in range(A_N)}", 1),
    ("w172_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}",
     "w173_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}", 1),
    ('assert not (w172_a & w172_b), "W173 A/B band overlap"',
     'assert not (w173_a & w173_b), "W174 A/B band overlap"', 1),
    ("assert not (w172_a & reg_ints) and not (w172_b & reg_ints), \\",
     "assert not (w173_a & reg_ints) and not (w173_b & reg_ints), \\", 1),
    ('"W173 hits SEED_REGISTRY"', '"W174 hits SEED_REGISTRY"', 1),
    ('for nm, band in (("A", w172_a), ("B", w172_b)):',
     'for nm, band in (("A", w173_a), ("B", w173_b)):', 1),
    ('f"W173 {nm} hits v1"', 'f"W174 {nm} hits v1"', 1),
    ('f"W173 {nm} hits W1"', 'f"W174 {nm} hits W1"', 1),
    ('f"W173 {nm} hits probe seeds"', 'f"W174 {nm} hits probe seeds"', 1),
    ('"registered W172 row parity drift (r307; bm-a r819)"',
     '"registered W172 row parity drift (r307; bm-a r819)"' + NL +
     '        assert pf.N1_BANDS[173] == {"a": (395_404, 397_403),' + NL +
     '                                    "b_exit": (397_404, 397_603),' + NL +
     '                                    "engine_owner": "bm-a"}, \\' + NL +
     '            "registered W173 row parity drift (r307; bm-a r822)"', 1),
    ("# prior-wave disjointness W2..W172 (single state: all",
     "# prior-wave disjointness W2..W173 (single state: all", 1),
    ("for wprev in sorted(w for w in WAVE_CONFIGS if w < 173):",
     "for wprev in sorted(w for w in WAVE_CONFIGS if w < 174):", 2),
    ('assert not (w172_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j',
     'assert not (w173_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j', 1),
    ('for j in range(A_N)}), f"W173 A hits W{wprev}"',
     'for j in range(A_N)}), f"W174 A hits W{wprev}"', 1),
    ('assert not (w172_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j',
     'assert not (w173_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j', 1),
    ('for j in range(B_N)}), f"W173 B hits W{wprev}"',
     'for j in range(B_N)}), f"W174 B hits W{wprev}"', 1),
    ("n3r1_used172 = set(range(70_000, 70_006))",
     "n3r1_used173 = set(range(70_000, 70_006))", 1),
    ("assert not (w172_a & n3r1_used172) and not (w172_b & n3r1_used172), \\",
     "assert not (w173_a & n3r1_used173) and not (w173_b & n3r1_used173), \\", 1),
    ('"W173 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"',
     '"W174 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"', 1),
    ("assert not (w172_a & lfc_actual12) and not (w172_b & lfc_actual12), \\",
     "assert not (w173_a & lfc_actual12) and not (w173_b & lfc_actual12), \\", 1),
    ('"W173 bands must clear the lfc actual draw range"',
     '"W174 bands must clear the lfc actual draw range"', 1),
    ("assert not (w172_a & options_actual12) and \\",
     "assert not (w173_a & options_actual12) and \\", 1),
    ("not (w172_b & options_actual12), \\",
     "not (w173_b & options_actual12), \\", 1),
    ('"W173 bands must clear the options_wave2 actual draw range"',
     '"W174 bands must clear the options_wave2 actual draw range"', 1),
    ("# band facts (law sec.4 W173 row, r795): A = FIRST-CLEAN past",
     "# band facts (law sec.4 W174 row, r795): A = FIRST-CLEAN past", 1),
    ("# the registered W172 B band (the arithmetic continuation",
     "# the registered W173 B band (the arithmetic continuation", 1),
    ("# 395_204..397_203 is REFUSED at its own start by the W172",
     "# 397_404..399_403 is REFUSED at its own start by the W173", 1),
    ("# B band 395_204..395_403, exactly as the W172 seat W173+ projection +",
     "# B band 397_404..397_603, exactly as the W173 seat W174+ projection +", 1),
    ("# r818 probe leg4 + r819 sec8 succession projection notes",
     "# r820 probe leg4 + r823 sec8 succession projection notes", 1),
    ("# 395_404..397_403; A base == prior-wave B tail+1 (395_403+1)",
     "# 397_604..399_603; A base == prior-wave B tail+1 (397_603+1)", 1),
    ("# machine-checkable -- A-hops-prior-B staircase THIRTY-THIRD",
     "# machine-checkable -- A-hops-prior-B staircase THIRTY-FOURTH", 1),
    ("# continuation 395_404..395_603 is CLEAN on the registered",
     "# continuation 397_604..397_803 is CLEAN on the registered", 1),
    ("# universe but lands INSIDE the W173 A band window --",
     "# universe but lands INSIDE the W174 A band window --", 1),
    ("# 397_404 and lands 397_404..397_603, hops=1, non-rotational",
     "# 399_604 and lands 399_604..399_803, hops=1, non-rotational", 1),
    ("# (397_403+1) machine-checkable; cross-window convergence",
     "# (399_603+1) machine-checkable; cross-window convergence", 1),
    ("# with the W172 seat W173+ projection + r818 probe leg4 + r819 sec8",
     "# with the W173 seat W174+ projection + r820 probe leg4 + r823 sec8", 1),
    ("# honored (post-W171 universe re-derive + own-wave A",
     "# honored (post-W173 universe re-derive + own-wave A", 1),
    ("# reservation when deriving B); seat MSG-1122 tail,",
     "# reservation when deriving B); seat MSG-1247 tail,", 1),
    ('assert WAVE_CONFIGS[173]["a_seed_base"] == 395_404 == 395_403 + 1, (',
     'assert WAVE_CONFIGS[174]["a_seed_base"] == 397_604 == 397_603 + 1, (', 1),
    ('"W173 A must be the first-clean window past the registered "',
     '"W174 A must be the first-clean window past the registered "', 1),
    ('"W172 B band tail 395_403+1 (arithmetic continuation "',
     '"W173 B band tail 397_603+1 (arithmetic continuation "', 1),
    ('"395_204..397_203 REFUSED at its own start by the W172 B "',
     '"397_404..399_403 REFUSED at its own start by the W173 B "', 1),
    ('"band 395_204..395_403, exactly as the W172 seat W173+ projection + "',
     '"band 397_404..397_603, exactly as the W173 seat W174+ projection + "', 1),
    ('"r818 probe leg4 + r819 sec8 succession projection notes "',
     '"r820 probe leg4 + r823 sec8 succession projection notes "', 1),
    ('"staircase THIRTY-THIRD instance, E36 card)"',
     '"staircase THIRTY-FOURTH instance, E36 card)"', 1),
    ("arith_a172 = set(range(395_404, 397_404))",
     "arith_a173 = set(range(397_604, 399_604))", 1),
    ("assert not (arith_a172 & reg_ints), \\",
     "assert not (arith_a173 & reg_ints), \\", 1),
    ('"W173 A window must be CLEAN (first-clean ADMIT face past prior-wave B)"',
     '"W174 A window must be CLEAN (first-clean ADMIT face past prior-wave B)"', 1),
    ('assert WAVE_CONFIGS[173]["b_exit_seed_base"] == 397_404 == 397_403 + 1, (',
     'assert WAVE_CONFIGS[174]["b_exit_seed_base"] == 399_604 == 399_603 + 1, (', 1),
    ('"W173 B must be the first-clean window past the own-wave A "',
     '"W174 B must be the first-clean window past the own-wave A "', 1),
    ('"band tail 397_403+1 (arithmetic continuation "',
     '"band tail 399_603+1 (arithmetic continuation "', 1),
    ('"395_404..395_603 CLEAN on the registered universe but "',
     '"397_604..397_803 CLEAN on the registered universe but "', 1),
    ('"lands INSIDE the W173 A band window; same-freeze mutual "',
     '"lands INSIDE the W174 A band window; same-freeze mutual "', 1),
    ('"own-wave A window reserved jumps to 397_404, first-clean "',
     '"own-wave A window reserved jumps to 399_604, first-clean "', 1),
    ("arith_b172 = set(range(397_404, 397_604))",
     "arith_b173 = set(range(399_604, 399_804))", 1),
    ("assert not (arith_b172 & reg_ints), \\",
     "assert not (arith_b173 & reg_ints), \\", 1),
    ('"W173 B window must be CLEAN (first-clean ADMIT face past own-wave A)"',
     '"W174 B window must be CLEAN (first-clean ADMIT face past own-wave A)"', 1),
    ("assert not (arith_b172 & arith_a172), \\",
     "assert not (arith_b173 & arith_a173), \\", 1),
    ('"W173 A/B same-freeze mutual exclusion (B hops past own A)"',
     '"W174 A/B same-freeze mutual exclusion (B hops past own A)"', 1),
    ('assert _entry_shard_of(0, 12) == ("PERPETUAL-N1-W173-SHARD-0",',
     'assert _entry_shard_of(0, 12) == ("PERPETUAL-N1-W174-SHARD-0",', 1),
    ('"n1w173-0of12"), "W173 entry identity"',
     '"n1w174-0of12"), "W174 entry identity"', 1),
    ('assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W173-SHARD-11",',
     'assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W174-SHARD-11",', 1),
    ('"n1w173-11of12")', '"n1w174-11of12")', 1),
    ('assert SHARD_DIR.endswith("n1_w173") and OUT.endswith(',
     'assert SHARD_DIR.endswith("n1_w174") and OUT.endswith(', 1),
    ('"n1_w173_results.json"), "W173 path drift"',
     '"n1_w174_results.json"), "W174 path drift"', 1),
    ('f"W173 shard dir collides with W{wprev}"',
     'f"W174 shard dir collides with W{wprev}"', 1),
    ("# W173 finalize cumulative deps: W17..W172 outputs ALL PRESENT",
     "# W174 finalize cumulative deps: W17..W173 outputs ALL PRESENT", 1),
    ("# (landed net chain head 783,812 = W172 bm-a r819 one-pass --",
     "# (landed net chain head 786,012 = W173 bm-a r823 one-pass --", 1),
    ("for _depw in range(17, 173):", "for _depw in range(17, 174):", 1),
    ('f"W173 finalize cumulative dep (W{_depw} output) missing"',
     'f"W174 finalize cumulative dep (W{_depw} output) missing"', 1),
    ("# registered wave below 173 composes; wave 15 excluded by",
     "# registered wave below 174 composes; wave 15 excluded by", 1),
    ("# design; SINGLE STATE (W2..W172 all registered -- no",
     "# design; SINGLE STATE (W2..W173 all registered -- no", 1),
    ("assert sorted(w for w in WAVE_CONFIGS if w < 173) == \\",
     "assert sorted(w for w in WAVE_CONFIGS if w < 174) == \\", 1),
    ("[w for w in range(16, 173)], \\", "[w for w in range(16, 174)], \\", 1),
    ('"W173 prior-wave set must derive from registry keys (no 15; "',
     '"W174 prior-wave set must derive from registry keys (no 15; "', 1),
    ('"W2..W172 registered single state)"', '"W2..W173 registered single state)"', 1),
    ('PATHS.root, "research", "PERPETUAL_N1_W173_PREREG.md")), \\',
     'PATHS.root, "research", "PERPETUAL_N1_W174_PREREG.md")), \\', 1),
    ('"W173 per-wave prereg missing (materializer requirement)"',
     '"W174 per-wave prereg missing (materializer requirement)"', 1),
]
# negative tokens are surgical: the CARRIED parity chain keeps its
# historical stamps (W138..W172 rows cite r743..r819; the APPENDED W173
# parity row keeps its (395_404, 397_403) tuple), and the prior-wave
# band references keep W173-era dotted forms (397_404..397_603 etc.)
# -- bare numerals are therefore forbidden as negatives; only
# W173-era assert/comment forms qualify.
MAT_NEG = ["w172_", "arith_a172", "arith_b172", "n3r1_used172", "r818 probe",
           "r819 sec8", "r820 pre-seat", "9cd8af3af", "59fde9319",
           "SIXTY-THIRD", "eighty-ninth", "rows 162", "rows 88 ",
           "range(17, 173)", "range(16, 173)", "W1..W172", "wave 172 =",
           "PERPETUAL_N1_W173", "PERPETUAL-N1-W173", "MSG-1122", "_r820bma",
           "the W173 seat MSG sits in", "bm-c r672", "W173 materializer",
           "INSIDE the W173", "THIRTY-THIRD", "W173 bands", "W173 A band",
           "W173 A window", "W173 B window", "W173 A/B", "W173 hits",
           "W173 entry identity", "W173 path drift", "W173 shard dir",
           "W173 finalize cumulative", "W173 prior-wave", "W173 per-wave",
           "W173 engine_owner drift", "W173 A band drift",
           "W173 B band drift", "the W172 seat", "W172 B band",
           "W172 finalize", "bm-a r819 freeze", "post-W171", "seat MSG-1122"]
mat174 = "    " + vmap(mat, MAT_PAIRS, MAT_NEG, "mat")

# ---- face 4: n1 W174 PASS-claim attribution -----------------------------
CL_PAIRS = [
    ('"+ W173 materializer face [same guard set, dep=W17..W172 ',
     '"+ W174 materializer face [same guard set, dep=W17..W173 ', 1),
    ('"outputs ALL PRESENT (landed net chain head 783,812 = "',
     '"outputs ALL PRESENT (landed net chain head 786,012 = "', 1),
    ('"W172 bm-a r819 one-pass, K=376,320 merged pool; ZERO "',
     '"W173 bm-a r823 one-pass, K=378,520 merged pool; ZERO "', 1),
    ('"in-flight upstream seats), ONE HUNDRED-AND-SIXTY-THIRD "',
     '"in-flight upstream seats), ONE HUNDRED-AND-SIXTY-FOURTH "', 1),
    ('"ENGINE-OWNED WAVE BY MACHINE-DERIVE (engine_owner rows 162 "',
     '"ENGINE-OWNED WAVE BY MACHINE-DERIVE (engine_owner rows 163 "', 1),
    ("+ candidate) bm-a's eighty-ninth owned claim per ",
     "+ candidate) bm-a's ninetieth owned claim per ", 1),
    ('"machine-derive (engine_owner==bm-a rows 88 + candidate), "',
     '"machine-derive (engine_owner==bm-a rows 89 + candidate), "', 1),
    ('"A=FIRST-CLEAN past the registered W172 B band (staircase "',
     '"A=FIRST-CLEAN past the registered W173 B band (staircase "', 1),
    ('"THIRTY-THIRD instance, E36 card, hops=1) + B=FIRST-CLEAN past the "',
     '"THIRTY-FOURTH instance, E36 card, hops=1) + B=FIRST-CLEAN past the "', 1),
    ('"results/_r820bma_w173_probe_receipt.json, law sec.4 W173 row, "',
     '"results/_r823bma_w174_probe_receipt.json, law sec.4 W174 row, "', 1),
    ('"r822 bm-a] "', '"r826 bm-a] "', 1),
]
CL_NEG = ["W173 materializer", "783,812", "376,320", "SIXTY-THIRD",
          "eighty-ninth", "rows 162", "rows 88 ", "THIRTY-THIRD",
          "W172 B band", "_r820bma", "W173 row,", "r822 bm-a]"]
claim174 = IND10 + vmap(claim, CL_PAIRS, CL_NEG, "claim")

# ---- apply insertions (in-memory) ---------------------------------------
pfsrc = io.open(PF, encoding="utf-8", newline="").read()
n1src = io.open(N1, encoding="utf-8", newline="").read()

# pf: insert W174 block after the W173 row (last registered), before the
# dict close -- r560 insert-after-last-registered-row + post-anchor gate
seg = EO + NL + "}"
check(pfsrc.count(seg) == 1, "pf row-close segment not unique")
pfnew = pfsrc.replace(seg, EO + NL + blk174 + NL + "}", 1)

# n1 entry: after the W173 entry, before the WAVE_CONFIGS close
seg = EO + NL + IND23 + "}"
check(n1src.count(seg) == 1, "n1 entry-close segment not unique")
n1new = n1src.replace(seg, EO + NL + entry174 + NL + IND23 + "}", 1)

# n1 mat: insert the W174 block before the T-141 s2 lane face header
seg = "    # --- T-141 s2 lane face"
check(n1new.count(seg) == 1, "n1 T-141 mat anchor not unique")
n1new = n1new.replace(seg, mat174 + NL + seg, 1)

# n1 claim: insert the W174 attribution after the W173 claim tail line
# (r581 law: anchor = tail single-line literal + post-anchor guard)
seg = '"r822 bm-a] "' + NL + IND10 + '"+ T-141 s2 "'
check(n1new.count(seg) == 1, "n1 claim anchor not unique")
n1new = n1new.replace(seg, '"r822 bm-a] "' + NL + claim174 + NL + IND10 +
                      '"+ T-141 s2 "', 1)

# ---- gates (r780/r781/r560/r815 lineage) --------------------------------
ast.parse(pfnew)
ast.parse(n1new)
print("AST gate: both files parse OK")

# W174 presence + W173 anti-vanish (r560 law)
checks = [
    (pfnew, '174: {"a": (397_604, 399_603), "b_exit": (399_604, 399_803),', 1),
    (pfnew, '173: {"a": (395_404, 397_403), "b_exit": (397_404, 397_603),', 1),
    (pfnew, "# W174 (bm-a r826 freeze", 1),
    (pfnew, "# W173 (bm-a r822 freeze", 1),
    (n1new, '174: {"batch": "PERPETUAL-N1-W174",', 1),
    (n1new, '173: {"batch": "PERPETUAL-N1-W173",', 1),
    (n1new, "# --- W174 materializer face", 1),
    (n1new, "# --- W173 materializer face", 1),
    (n1new, '"r826 bm-a] "', 1),
    (n1new, '"r822 bm-a] "', 1),
    (n1new, '"a_seed_base": 397_604,', 1),
    (n1new, '"b_exit_seed_base": 399_604,', 1),
    (n1new, "n1_w174", 4),
    (n1new, "PERPETUAL_N1_W174_PREREG.md", 2),
]
for src, needle, cnt in checks:
    got = src.count(needle)
    check(got == cnt, "post-edit needle %r count %d != %d" % (needle[:50], got, cnt))

# W175 projection prose present in the new W174 blocks (probe leg4
# verbatim; r819 post-edit assert bloodline + r776 fragment-needle law)
check("# W174+ projection (gate-derived r823)" in pfnew,
      "pf W174+ projection head missing")
check('probe_receipt.json; W175+ projection "' in n1new,
      "n1 W175+ projection head fragment missing")
check("# 399_604..401_603 CLEAN hops=0 / B first-clean 399_804..400_003" in pfnew,
      "pf W175p prose missing")
check("W175 A window; W175 freezer MUST re-derive on the post-W174" in pfnew,
      "pf W175 freezer prose missing")
check('"W175 A window; W175 freezer MUST re-derive on the "' in n1new,
      "n1 W175 freezer fragment missing")
check('"W174 B band 399_604..399_803 will refuse the naive "' in n1new,
      "n1 W174-band refuse fragment missing")

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
check('174: {"a": (397_604' not in pf_o2, "write-time: origin pf carries W174")
check('174: {"batch"' not in n1_o2, "write-time: origin n1 carries W174")
if fail:
    print("RESULT: FAIL at write-time re-check (%d) -- zero writes" % len(fail))
    for f in fail:
        print("  -", f)
    sys.exit(1)

# ---- live writes: n1 FIRST then pf (engine queue derive keyses off the
# pf N1_BANDS row -- a row without a WAVE_CONFIGS entry would be a dead
# face for one tick; an entry without a row never ignites (safe order) --
# r666 law window face) ----------------------------------------------------
io.open(N1, "w", encoding="utf-8", newline="").write(n1new)
io.open(PF, "w", encoding="utf-8", newline="").write(pfnew)
print("LIVE WRITES DONE: pf %d->%d B, n1 %d->%d B" %
      (len(pfsrc), len(pfnew), len(n1src), len(n1new)))
print("freeze edits rc0: 4 insertions landed (pf row + n1 entry + mat + claim)")
