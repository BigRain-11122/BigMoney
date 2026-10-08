# -*- coding: utf-8 -*-
"""r890 bm-a W189 freeze edits: four insertions (pf N1_BANDS[189] row +
n1 WAVE_CONFIGS[189] entry + n1 W189 materializer block + n1 W189
PASS-claim attribution). DRY flag: --dry = zero-write simulation
(r781 verify-separation law + freeze-edits dry-run precedent: full
stale+prose+AST asserts in memory BEFORE any write).

Bloodline: freeze-edits machinery (r773 pit law freeze-editor compliance +
r776 fragment-needle law + r781 verify-separation law), W189 facts
live-registry-driven (built by _r890bma_w189_freeze_buildgen.py: old
sides = the PHYSICAL W188 face fragments probed to dumps first-leg
r890, new sides = the S88 W189 fact map, counts verified pre-emission):
  - pre-seat probe results/_r888bma_w189_probe_receipt.json rc0 ADMIT
    (naive A 430_404..432_403 refused at its own start by the
    registered W188 B band 430_404..430_603; honest forward walk
    1 hop lands A 430_604..432_603 staircase FORTY-NINTH instance
    E36 -- receipt A_semantics machine-cites r887 W188 probe leg4 +
    W188 materializer W189+ projection anticipated + MANDATED this
    re-derive (projection and receipt ordinals MATCH, no divergence
    this wave); B 432_604..432_803 own-A mutual exclusion hops=1,
    naive 430_604..430_803);
  - face probe results/_r890bma_w189_probe_stage1.json rc0 (all four
    W188 faces dumped first-leg r890; this TOK is built from the
    PHYSICAL probe-dumped shapes, r776 law);
  - seat MSG-2026-10-08-1815-bma-w189-seat published on origin at
    744de26ef (r888 seat push, path-derived TRUE sha per r812
    precedent); r565 law: on origin BEFORE this freeze commit;
    self-ack archive ALREADY LANDED -- bm-a r889-window archive
    move (cross-window consume by the r889 finalize window,
    disclosed; the W189 seat MSG sits in fleet/inbox/processed/ at
    freeze time, live-verified);
  - per-wave prereg research/PERPETUAL_N1_W189_PREREG.md built r890
    (buildgen r888-bloodline; DRY 50/50 green; frozen+pushed
    632761894 r890 post-rebase; on origin, verified live below);
  - W188 freeze registered sha machine-derived = b66117659 (git log
    origin/main --grep "^W188 five-face freeze" -- anchored: the
    r888 round commit a9ab260f6 also carries the unanchored phrase);
    W188 finalize landed r889 one-pass same-chain: ledger head
    820,928, merged pool K=411,520 (n1_w188_results.json
    machine-read); W188 sec7/sec8 settle backfill landed the r890
    window (this window, first-leg, 43322a984 pre-rebase sha);
  - lineage constants disclosed (r795/r845/r849/r852/r863/r867/
    r869/r874/r878/r882/r885/r888 precedent, passed through):
    (a) the "wave N-1 = first free number" mat-header label rolls
    forward with its off-by-one quirk (since W165 r795);
    (b) "law sec.4 W189 row, r795" band-facts template stamp keeps
    its r795; (c) "single-window derive (r812 merged the gate legs
    INTO the pre-seat probe...)" stays (historical merge citation);
    (d) the bm-a-owned ordinal word rolls one-hundred-fourth ->
    one-hundred-fifth (rows 104 + candidate = 105th owned per probe
    leg0, machine-chosen word form, disclosed); (e) mat parity-chain
    rows W138..W187 keep their historical stamps and tuples; the
    W188 row (the current registered tail) is APPENDED with its
    frozen values (428_404, 430_403)/(430_404, 430_603) and its
    freeze-run session stamp (r307; bm-a r888); (f) the "W188
    finalize landed one-pass r889" citation rolls its wave-word with
    the values rolling machine-correct to 820,928/411,520 this
    window; (g) the sec8 succession-notes window citation rolls
    r888 -> r890 回填窗 (the W188 sec8 notes landed the r890
    backfill window, honest next-window form, disclosed).

r773 pit law compliance:
  (1) full string-face inventory empirically probed BEFORE TOK
      (_r890bma_w189_face_probe.py first-leg r890 -- four face
      dumps + stage-1 receipt, rc0);
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
      (r530/r687: fetch + origin carries no W189 registration before
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
probe = json.load(open(r"results\_r888bma_w189_probe_receipt.json",
                       encoding="utf-8"))
check(probe["verdict"] == "ADMIT", "pre-seat probe not ADMIT")
check(probe["bands"] == {"A": "430604_432603", "B": "432604_432803"},
      "probe band shape mismatch")
check(probe["legs"]["leg1"]["A"] == [430604, 432603], "A band mismatch")
check(probe["legs"]["leg1"]["B"] == [432604, 432803], "B band mismatch")
check(probe["legs"]["leg1"]["hops_A"] == 1 and probe["legs"]["leg1"]["hops_B"] == 1,
      "hops mismatch")
check(probe["legs"]["leg0"]["rows"] == 186 and probe["legs"]["leg0"]["tail"] == "W188",
      "leg0 registry tail mismatch")
check(probe["legs"]["leg0"]["ordinal"] == 179 and probe["legs"]["leg0"]["bma_ordinal"] == 105,
      "leg0 ordinal mismatch")
check(probe["legs"]["leg2"]["conflicts"] == 0, "leg2 conflicts nonzero")
check(probe["legs"]["leg3"]["origin_vacancy"] is True, "leg3 origin not vacant")
check(probe["legs"]["leg4"]["W190p_A"] == "432604..434603"
      and probe["legs"]["leg4"]["W190p_B"] == "432804..433003",
      "leg4 W190+ projection mismatch")

# origin anti-collision pre-check (r511 tail-lock / r687 write-time gate)
subprocess.run(["git", "fetch", "origin"], capture_output=True)
pf_o = subprocess.run(["git", "show", "origin/main:" + PF],
                      capture_output=True).stdout.decode("utf-8", "replace")
n1_o = subprocess.run(["git", "show", "origin/main:" + N1],
                      capture_output=True).stdout.decode("utf-8", "replace")
check('189: {"a": (430_604' not in pf_o, "origin pf already carries W189 row")
check("W189 (bm-a r890 freeze" not in pf_o, "origin pf carries W189 block")
check('189: {"batch"' not in n1_o, "origin n1 already carries W189 entry")
check("# --- W189 materializer face" not in n1_o, "origin n1 carries W189 mat")
check('"r890 bm-a] "' not in n1_o, "origin n1 carries W189 claim")

# machine-derived shas (r587 / r812 path-derived precedent)
seat_sha = subprocess.run(
    ["git", "log", "origin/main", "--format=%h", "-n", "1", "--diff-filter=A",
     "--", "fleet/inbox/MSG-2026-10-08-1815-bma-w189-seat.md"],
    capture_output=True).stdout.decode().strip()
check(seat_sha == "744de26ef", "seat sha path-derived mismatch: " + seat_sha)
check(os.path.exists(os.path.join(
    "fleet", "inbox", "processed", "MSG-2026-10-08-1815-bma-w189-seat.md")),
    "seat MSG not in processed/ at freeze time (r889-window archive)")
w188_freeze_sha = subprocess.run(
    ["git", "log", "origin/main", "--format=%h", "-n", "1", "--grep=^W188 five-face freeze"],
    capture_output=True).stdout.decode().strip()
check(w188_freeze_sha == "b66117659", "W188 freeze sha mismatch: " + w188_freeze_sha)

# ---- live-registry parity pre-check (edit-gate: never edit a drifted file)
sys.path.insert(0, "scripts")
import perpetual_faces as pfmod  # noqa: E402
check(len(pfmod.N1_BANDS) == 186, "live N1_BANDS row count drift: %d" % len(pfmod.N1_BANDS))
check(pfmod.N1_BANDS[188] == {"a": (428_404, 430_403),
                              "b_exit": (430_404, 430_603),
                              "engine_owner": "bm-a"}, "live W188 row drift")
check(189 not in pfmod.N1_BANDS, "live N1_BANDS already has 189")
check(os.path.exists(os.path.join("research", "PERPETUAL_N1_W189_PREREG.md")),
      "W189 per-wave prereg missing (materializer gate)")
prereg_o = subprocess.run(["git", "show", "origin/main:research/PERPETUAL_N1_W189_PREREG.md"],
                          capture_output=True)
check(prereg_o.returncode == 0, "W189 prereg absent on origin")

# ---- physical face dumps (r776 law) -----------------------------------
pfblk = io.open(r"results\_r890bma_w189_probe_pf_block.txt", encoding="utf-8",
                newline="").read()
entry = io.open(r"results\_r890bma_w189_probe_n1_entry.txt", encoding="utf-8",
                newline="").read()
mat = io.open(r"results\_r890bma_w189_probe_n1_mat.txt", encoding="utf-8",
              newline="").read()
claim = io.open(r"results\_r890bma_w189_probe_n1_claim.txt", encoding="utf-8",
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
    ('    # W188 (bm-a r888 freeze, seat MSG-2026-10-08-1717-bma-w188-seat', '    # W189 (bm-a r890 freeze, seat MSG-2026-10-08-1815-bma-w189-seat', 1),
    ('pushed to origin 943967370 pre-freeze r565 law (r887 pre-seat', 'pushed to origin 744de26ef pre-freeze r565 law (r888 pre-seat', 1),
    ('(3-item; the W187 finalize product already on origin since r887,', '(3-item; the W188 finalize product already on origin since r888,', 1),
    ('# = direct fast-forward behind-0 at fetch (r887 pre-seat', '# = direct fast-forward behind-0 at fetch (r888 pre-seat', 1),
    ('# push), zero merge, zero --no-verify; self-ack archive ALREADY\r\n    # LANDED pre-freeze -- bm-a r887-window self-ack move (the W188\r\n    # seat MSG sits in fleet/inbox/processed/ at freeze time, honest\r\n    # archived);', '# push), zero merge, zero --no-verify; self-ack archive ALREADY\r\n    # LANDED pre-freeze -- bm-a r889-window archive move (the W189\r\n    # seat MSG sits in fleet/inbox/processed/ at freeze time, honest\r\n    # archived);', 1),
    ('band gate ADMIT results/_r887bma_w188_probe_receipt.json: A = FIRST-CLEAN', 'band gate ADMIT results/_r888bma_w189_probe_receipt.json: A = FIRST-CLEAN', 1),
    ('past the registered W187 B band (arithmetic continuation', 'past the registered W188 B band (arithmetic continuation', 1),
    ('428_204..430_203 REFUSED at its own start by the W187 B band', '430_404..432_403 REFUSED at its own start by the W188 B band', 1),
    ('428_204..428_403, exactly as the W187 seat W188+ projection + r885 probe', '430_404..430_603, exactly as the W188 seat W189+ projection + r888 probe', 1),
    ('# leg4 + r888 sec8 回填窗 succession projection notes all anticipated;', '# leg4 + r890 sec8 回填窗 succession projection notes all anticipated;', 1),
    ('honest forward walk hops=1 -> 428_404..430_403, non-rotational', 'honest forward walk hops=1 -> 430_604..432_603, non-rotational', 1),
    ('(428_403+1) machine-checkable -- A-hops-prior-B staircase', '(430_603+1) machine-checkable -- A-hops-prior-B staircase', 1),
    ('FORTY-EIGHTH instance, E36 card);', 'FORTY-NINTH instance, E36 card);', 1),
    ('continuation 428_404..428_603 CLEAN on the registered universe', 'continuation 430_604..430_803 CLEAN on the registered universe', 1),
    ('but lands INSIDE the W188 A band window -- same-freeze mutual', 'but lands INSIDE the W189 A band window -- same-freeze mutual', 1),
    ('own-wave A window reserved jumps to 430_404 -> 430_404..430_603,', 'own-wave A window reserved jumps to 432_604 -> 432_604..432_803,', 1),
    ('own-wave A tail+1 (430_403+1) machine-checkable);', 'own-wave A tail+1 (432_603+1) machine-checkable);', 1),
    ('W188+ projection (gate-derived r887): A first-clean', 'W189+ projection (gate-derived r888): A first-clean', 1),
    ('430_404..432_403 CLEAN hops=0 / B first-clean 430_604..430_803', '432_604..434_603 CLEAN hops=0 / B first-clean 432_804..433_003', 1),
    ('registered W188 B band 430_404..430_603 will refuse the naive', 'registered W189 B band 432_604..432_803 will refuse the naive', 1),
    ('W189 A window; W189 freezer MUST re-derive on the post-W188', 'W190 A window; W190 freezer MUST re-derive on the post-W189', 1),
    ('NOT a re-pick (R250: W188 bands were never assigned).', 'NOT a re-pick (R250: W189 bands were never assigned).', 1),
    ('188: {"a": (428_404, 430_403), "b_exit": (430_404, 430_603),', '189: {"a": (430_604, 432_603), "b_exit": (432_604, 432_803),', 1),
]

EN_PAIRS = [
    ('188: {"batch": "PERPETUAL-N1-W188",', '189: {"batch": "PERPETUAL-N1-W189",', 1),
    ('"prereg": ("research/PERPETUAL_N1_W188_PREREG.md (wave-level frozen "', '"prereg": ("research/PERPETUAL_N1_W189_PREREG.md (wave-level frozen "', 1),
    ('new seed bands only; ONE HUNDRED-AND-SEVENTY-EIGHTH ENGINE-OWNED WAVE ', 'new seed bands only; ONE HUNDRED-AND-SEVENTY-NINTH ENGINE-OWNED WAVE ', 1),
    ('BY MACHINE-DERIVE (engine_owner rows 177 + candidate), ', 'BY MACHINE-DERIVE (engine_owner rows 178 + candidate), ', 1),
    ('number law after the REGISTERED W187 row bm-a r886 freeze ', 'number law after the REGISTERED W188 row bm-a r888 freeze ', 1),
    ('79c9a567c, SINGLE STATE zero seat gap W2..W187 all ', 'b66117659, SINGLE STATE zero seat gap W2..W188 all ', 1),
    ('registered; W188 finalize landed same-window r827, ledger ', 'registered; W189 finalize landed same-window r827, ledger ', 1),
    ('head 818,728, merged pool K=409,320; seat published=reserved ', 'head 820,928, merged pool K=411,520; seat published=reserved ', 1),
    ('MSG-2026-10-08-1717-bma-w188-seat PUSHED to origin 943967370 ', 'MSG-2026-10-08-1815-bma-w189-seat PUSHED to origin 744de26ef ', 1),
    ('probe receipt (3-item; the W187 finalize product already on origin since r887, not re-shipped; W146 precedent); ', 'probe receipt (3-item; the W188 finalize product already on origin since r888, not re-shipped; W146 precedent); ', 1),
    ('at fetch (r887 pre-seat push), zero merge, zero ', 'at fetch (r888 pre-seat push), zero merge, zero ', 1),
    ('engine_owner=bm-a, wave 187: ', 'engine_owner=bm-a, wave 188: ', 1),
    ('A = FIRST-CLEAN past the registered W187 B band (the ', 'A = FIRST-CLEAN past the registered W188 B band (the ', 1),
    ('arithmetic continuation 428_204..430_203 is REFUSED at its ', 'arithmetic continuation 430_404..432_403 is REFUSED at its ', 1),
    ('own start by the W187 B band 428_204..428_403, exactly as ', 'own start by the W188 B band 430_404..430_603, exactly as ', 1),
    ('the W187 seat W188+ projection + r885 probe leg4 + r888 sec8 回填窗 succession ', 'the W188 seat W189+ projection + r888 probe leg4 + r890 sec8 回填窗 succession ', 1),
    ('projection notes anticipated; honest forward walk hops=1 -> ', 'projection notes anticipated; honest forward walk hops=1 -> ', 1),
    ('428_404..430_403; A base == prior-wave B tail+1 ', '430_604..432_603; A base == prior-wave B tail+1 ', 1),
    ('machine-checkable = A-hops-prior-B staircase FORTY-EIGHTH ', 'machine-checkable = A-hops-prior-B staircase FORTY-NINTH ', 1),
    ('arithmetic continuation 428_404..428_603 is CLEAN on the ', 'arithmetic continuation 430_604..430_803 is CLEAN on the ', 1),
    ('registered universe but lands INSIDE the W188 A band ', 'registered universe but lands INSIDE the W189 A band ', 1),
    ('jumps to 430_404, first-clean 430_404..430_603 hops=1, ', 'jumps to 432_604, first-clean 432_604..432_803 hops=1, ', 1),
    ('convergence with the W187 seat W188+ projection + r885 probe leg4 + ', 'convergence with the W188 seat W189+ projection + r888 probe leg4 + ', 1),
    ('r888 sec8 回填窗 succession projection notes re-derived -- all ', 'r890 sec8 回填窗 succession projection notes re-derived -- all ', 1),
    ('MANDATORY notes honored (post-W187 universe re-derive + ', 'MANDATORY notes honored (post-W188 universe re-derive + ', 1),
    ('results/_r887bma_w188_probe_receipt.json; W189+ projection ', 'results/_r888bma_w189_probe_receipt.json; W190+ projection ', 1),
    ('per this window gate: A first-clean 430_404..432_403 ', 'per this window gate: A first-clean 432_604..434_603 ', 1),
    ('CLEAN / B first-clean 430_604..430_803 CLEAN -- naive ', 'CLEAN / B first-clean 432_804..433_003 CLEAN -- naive ', 1),
    ('W188 B band 430_404..430_603 will refuse the naive ', 'W189 B band 432_604..432_803 will refuse the naive ', 1),
    ('W189 A window; W189 freezer MUST re-derive on the ', 'W190 A window; W190 freezer MUST re-derive on the ', 1),
    ('post-W188 universe AND reserve the own-wave A window ', 'post-W189 universe AND reserve the own-wave A window ', 1),
    ('staircase card); W1..W187 finalize ALL LANDED (W187 ', 'staircase card); W1..W188 finalize ALL LANDED (W188 ', 1),
    ('finalize one-pass bm-a r887, net chain head 818,728, ', 'finalize one-pass bm-a r889, net chain head 820,928, ', 1),
    ('merged pool K=409,320) -- ZERO in-flight upstream ', 'merged pool K=411,520) -- ZERO in-flight upstream ', 1),
    ('"a_seed_base": 428_404,        # law sec.4 W188 A: 428_404..430_403 (FIRST-CLEAN past the registered W187 B band; arithmetic 428_204..430_203 REFUSED at own start by the W187 B band; hops=1; A-hops-prior-B staircase FORTY-EIGHTH instance, E36 card; ordinal convergence per r587: W187 sec5.5 prose anticipated forty-eighth, r887 receipt machine-read FORTY-EIGHTH)', '"a_seed_base": 430_604,        # law sec.4 W189 A: 430_604..432_603 (FIRST-CLEAN past the registered W188 B band; arithmetic 430_404..432_403 REFUSED at own start by the W188 B band; hops=1; A-hops-prior-B staircase FORTY-NINTH instance, E36 card; ordinal convergence per r587: W188 sec5.5 prose anticipated forty-ninth, r888 receipt machine-read FORTY-NINTH)', 1),
    ('"b_exit_seed_base": 430_404,   # law sec.4 W188 B: 430_404..430_603 (FIRST-CLEAN past the own-wave A window; arithmetic 428_404..428_603 lands inside own-A, same-freeze mutual exclusion W141 precedent; reserved walk hops=1; B base == own-A tail+1)', '"b_exit_seed_base": 432_604,   # law sec.4 W189 B: 432_604..432_803 (FIRST-CLEAN past the own-wave A window; arithmetic 430_604..430_803 lands inside own-A, same-freeze mutual exclusion W141 precedent; reserved walk hops=1; B base == own-A tail+1)', 1),
    ('"shard_subdir": "n1_w188", "out_name": "n1_w188_results.json",', '"shard_subdir": "n1_w189", "out_name": "n1_w189_results.json",', 1),
]

MAT_PAIRS = [
    ('# --- W188 materializer face (r888 bm-a freeze, own-series law', '# --- W189 materializer face (r890 bm-a freeze, own-series law', 1),
    ('#     one-hundred-fourth owned per machine-derive (engine_owner==bm-a', '#     one-hundred-fifth owned per machine-derive (engine_owner==bm-a', 1),
    ('#     rows 103 + candidate); wave 187 = first free number after', '#     rows 104 + candidate); wave 188 = first free number after', 1),
    ('#     the REGISTERED W187 row (bm-a r886 freeze 79c9a567c) --', '#     the REGISTERED W188 row (bm-a r888 freeze b66117659) --', 1),
    ('#     SINGLE STATE zero seat gap (W2..W187 all registered). Seat', '#     SINGLE STATE zero seat gap (W2..W188 all registered). Seat', 1),
    ('#     published=reserved MSG-2026-10-08-1717-bma-w188-seat pushed', '#     published=reserved MSG-2026-10-08-1815-bma-w189-seat pushed', 1),
    ('#     to origin 943967370 BEFORE this freeze, r565 law (payload', '#     to origin 744de26ef BEFORE this freeze, r565 law (payload', 1),
    ('#     the W187 finalize product already on origin since r887, not', '#     the W188 finalize product already on origin since r888, not', 1),
    ('#     at fetch (r887 pre-seat push), zero merge, zero', '#     at fetch (r888 pre-seat push), zero merge, zero', 1),
    ('#     --no-verify; self-ack inbox->processed archive ALREADY LANDED\r\n    #     pre-freeze -- bm-a r887-window self-ack move (the W188 seat\r\n    #     MSG sits in fleet/inbox/processed/ at freeze time, honest\r\n    #     archived).', '#     --no-verify; self-ack inbox->processed archive ALREADY LANDED\r\n    #     pre-freeze -- bm-a r889-window archive move (the W189 seat\r\n    #     MSG sits in fleet/inbox/processed/ at freeze time, honest\r\n    #     archived).', 1),
    ('#     ONE HUNDRED-AND-SEVENTY-EIGHTH engine wave BY', '#     ONE HUNDRED-AND-SEVENTY-NINTH engine wave BY', 1),
    ('#     MACHINE-DERIVE (engine_owner rows 177 + candidate; gate', '#     MACHINE-DERIVE (engine_owner rows 178 + candidate; gate', 1),
    ('#     W1..W187 finalize ALL LANDED (net chain head 818,728,', '#     W1..W188 finalize ALL LANDED (net chain head 820,928,', 1),
    ('#     K=409,320 merged pool; W187 finalize one-pass bm-a r887)', '#     K=411,520 merged pool; W188 finalize one-pass bm-a r889)', 1),
    ('#     always on. ADMIT receipt results/_r887bma_w188_probe_receipt.json;', '#     always on. ADMIT receipt results/_r888bma_w189_probe_receipt.json;', 1),
    ('#     banned gate ADMIT 0; not a re-pick (R250: W188 bands were', '#     banned gate ADMIT 0; not a re-pick (R250: W189 bands were', 1),
    ('    _set_wave(188)', '    _set_wave(189)', 1),
    ('assert WAVE_CONFIGS[187]["a_seed_base"] == pf.N1_BANDS[187]["a"][0], \\', 'assert WAVE_CONFIGS[188]["a_seed_base"] == pf.N1_BANDS[188]["a"][0], \\', 1),
    ('"W188 A band drift vs law mirror"', '"W189 A band drift vs law mirror"', 1),
    ('assert WAVE_CONFIGS[187]["b_exit_seed_base"] == \\', 'assert WAVE_CONFIGS[188]["b_exit_seed_base"] == \\', 1),
    ('pf.N1_BANDS[187]["b_exit"][0], "W188 B band drift vs law mirror"', 'pf.N1_BANDS[188]["b_exit"][0], "W189 B band drift vs law mirror"', 1),
    ('assert WAVE_CONFIGS[187].get("engine_owner") == \\', 'assert WAVE_CONFIGS[188].get("engine_owner") == \\', 1),
    ('pf.N1_BANDS[187].get("engine_owner") == "bm-a", \\', 'pf.N1_BANDS[188].get("engine_owner") == "bm-a", \\', 1),
    ('"W188 engine_owner drift (law mirror parity)"', '"W189 engine_owner drift (law mirror parity)"', 1),
    ('w187_a = {A_SEED_BASE + j for j in range(A_N)}', 'w188_a = {A_SEED_BASE + j for j in range(A_N)}', 1),
    ('w187_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}', 'w188_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}', 1),
    ('assert not (w187_a & w187_b), "W188 A/B band overlap"', 'assert not (w188_a & w188_b), "W189 A/B band overlap"', 1),
    ('assert not (w187_a & reg_ints) and not (w187_b & reg_ints), \\', 'assert not (w188_a & reg_ints) and not (w188_b & reg_ints), \\', 1),
    ('"W188 hits SEED_REGISTRY"', '"W189 hits SEED_REGISTRY"', 1),
    ('for nm, band in (("A", w187_a), ("B", w187_b)):', 'for nm, band in (("A", w188_a), ("B", w188_b)):', 1),
    ('f"W188 {nm} hits v1"', 'f"W189 {nm} hits v1"', 1),
    ('f"W188 {nm} hits W1"', 'f"W189 {nm} hits W1"', 1),
    ('f"W188 {nm} hits probe seeds"', 'f"W189 {nm} hits probe seeds"', 1),
    ('"registered W186 row parity drift (r307; bm-a r882)"\r\n        assert pf.N1_BANDS[187] == {"a": (426_204, 428_203),\r\n                                    "b_exit": (428_204, 428_403),\r\n                                    "engine_owner": "bm-a"}, \\\r\n            "registered W187 row parity drift (r307; bm-a r886)"', '"registered W187 row parity drift (r307; bm-a r882)"\r\n        assert pf.N1_BANDS[187] == {"a": (426_204, 428_203),\r\n                                    "b_exit": (428_204, 428_403),\r\n                                    "engine_owner": "bm-a"}, \\\r\n            "registered W188 row parity drift (r307; bm-a r888)"', 1),
    ('# prior-wave disjointness W2..W187 (single state: all', '# prior-wave disjointness W2..W188 (single state: all', 1),
    ('for wprev in sorted(w for w in WAVE_CONFIGS if w < 188):', 'for wprev in sorted(w for w in WAVE_CONFIGS if w < 189):', 2),
    ('assert not (w187_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j', 'assert not (w188_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j', 1),
    ('for j in range(A_N)}), f"W188 A hits W{wprev}"', 'for j in range(A_N)}), f"W189 A hits W{wprev}"', 1),
    ('assert not (w187_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j', 'assert not (w188_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j', 1),
    ('for j in range(B_N)}), f"W188 B hits W{wprev}"', 'for j in range(B_N)}), f"W189 B hits W{wprev}"', 1),
    ('n3r1_used187 = set(range(70_000, 70_006))', 'n3r1_used188 = set(range(70_000, 70_006))', 1),
    ('assert not (w187_a & n3r1_used187) and not (w187_b & n3r1_used187), \\', 'assert not (w188_a & n3r1_used188) and not (w188_b & n3r1_used188), \\', 1),
    ('"W188 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"', '"W189 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"', 1),
    ('assert not (w187_a & lfc_actual12) and not (w187_b & lfc_actual12), \\', 'assert not (w188_a & lfc_actual12) and not (w188_b & lfc_actual12), \\', 1),
    ('"W188 bands must clear the lfc actual draw range"', '"W189 bands must clear the lfc actual draw range"', 1),
    ('assert not (w187_a & options_actual12) and \\', 'assert not (w188_a & options_actual12) and \\', 1),
    ('not (w187_b & options_actual12), \\', 'not (w188_b & options_actual12), \\', 1),
    ('"W188 bands must clear the options_wave2 actual draw range"', '"W189 bands must clear the options_wave2 actual draw range"', 1),
    ('# band facts (law sec.4 W188 row, r795): A = FIRST-CLEAN past', '# band facts (law sec.4 W189 row, r795): A = FIRST-CLEAN past', 1),
    ('# the registered W187 B band (the arithmetic continuation', '# the registered W188 B band (the arithmetic continuation', 1),
    ('# 428_204..430_203 is REFUSED at its own start by the W187', '# 430_404..432_403 is REFUSED at its own start by the W188', 1),
    ('# B band 428_204..428_403, exactly as the W187 seat W188+ projection +', '# B band 430_404..430_603, exactly as the W188 seat W189+ projection +', 1),
    ('# r885 probe leg4 + r888 sec8 回填窗 succession projection notes', '# r888 probe leg4 + r890 sec8 回填窗 succession projection notes', 1),
    ('# 428_404..430_403; A base == prior-wave B tail+1 (428_403+1)', '# 430_604..432_603; A base == prior-wave B tail+1 (430_603+1)', 1),
    ('# machine-checkable -- A-hops-prior-B staircase FORTY-EIGHTH', '# machine-checkable -- A-hops-prior-B staircase FORTY-NINTH', 1),
    ('# continuation 428_404..428_603 is CLEAN on the registered', '# continuation 430_604..430_803 is CLEAN on the registered', 1),
    ('# universe but lands INSIDE the W188 A band window --', '# universe but lands INSIDE the W189 A band window --', 1),
    ('# 430_404 and lands 430_404..430_603, hops=1, non-rotational', '# 432_604 and lands 432_604..432_803, hops=1, non-rotational', 1),
    ('# (430_403+1) machine-checkable; cross-window convergence', '# (432_603+1) machine-checkable; cross-window convergence', 1),
    ('# with the W187 seat W188+ projection + r885 probe leg4 + r888 sec8', '# with the W188 seat W189+ projection + r888 probe leg4 + r890 sec8', 1),
    ('# honored (post-W187 universe re-derive + own-wave A', '# honored (post-W188 universe re-derive + own-wave A', 1),
    ('# reservation when deriving B); seat MSG-1717 tail,', '# reservation when deriving B); seat MSG-1815 tail,', 1),
    ('assert WAVE_CONFIGS[188]["a_seed_base"] == 428_404 == 428_403 + 1, (', 'assert WAVE_CONFIGS[189]["a_seed_base"] == 430_604 == 430_603 + 1, (', 1),
    ('"W188 A must be the first-clean window past the registered "', '"W189 A must be the first-clean window past the registered "', 1),
    ('"W187 B band tail 428_403+1 (arithmetic continuation "', '"W188 B band tail 430_603+1 (arithmetic continuation "', 1),
    ('"428_204..430_203 REFUSED at its own start by the W187 B "', '"430_404..432_403 REFUSED at its own start by the W188 B "', 1),
    ('"band 428_204..428_403, exactly as the W187 seat W188+ projection + "', '"band 430_404..430_603, exactly as the W188 seat W189+ projection + "', 1),
    ('"r885 probe leg4 + r888 sec8 回填窗 succession projection notes "', '"r888 probe leg4 + r890 sec8 回填窗 succession projection notes "', 1),
    ('"staircase FORTY-EIGHTH instance, E36 card)"', '"staircase FORTY-NINTH instance, E36 card)"', 1),
    ('arith_a187 = set(range(428_404, 430_404))', 'arith_a188 = set(range(430_604, 432_604))', 1),
    ('assert not (arith_a187 & reg_ints), \\', 'assert not (arith_a188 & reg_ints), \\', 1),
    ('"W188 A window must be CLEAN (first-clean ADMIT face past prior-wave B)"', '"W189 A window must be CLEAN (first-clean ADMIT face past prior-wave B)"', 1),
    ('assert WAVE_CONFIGS[188]["b_exit_seed_base"] == 430_404 == 430_403 + 1, (', 'assert WAVE_CONFIGS[189]["b_exit_seed_base"] == 432_604 == 432_603 + 1, (', 1),
    ('"W188 B must be the first-clean window past the own-wave A "', '"W189 B must be the first-clean window past the own-wave A "', 1),
    ('"band tail 430_403+1 (arithmetic continuation "', '"band tail 432_603+1 (arithmetic continuation "', 1),
    ('"428_404..428_603 CLEAN on the registered universe but "', '"430_604..430_803 CLEAN on the registered universe but "', 1),
    ('"lands INSIDE the W188 A band window; same-freeze mutual "', '"lands INSIDE the W189 A band window; same-freeze mutual "', 1),
    ('"own-wave A window reserved jumps to 430_404, first-clean "', '"own-wave A window reserved jumps to 432_604, first-clean "', 1),
    ('arith_b187 = set(range(430_404, 430_604))', 'arith_b188 = set(range(432_604, 432_804))', 1),
    ('assert not (arith_b187 & reg_ints), \\', 'assert not (arith_b188 & reg_ints), \\', 1),
    ('"W188 B window must be CLEAN (first-clean ADMIT face past own-wave A)"', '"W189 B window must be CLEAN (first-clean ADMIT face past own-wave A)"', 1),
    ('assert not (arith_b187 & arith_a187), \\', 'assert not (arith_b188 & arith_a188), \\', 1),
    ('"W188 A/B same-freeze mutual exclusion (B hops past own A)"', '"W189 A/B same-freeze mutual exclusion (B hops past own A)"', 1),
    ('assert _entry_shard_of(0, 12) == ("PERPETUAL-N1-W188-SHARD-0",', 'assert _entry_shard_of(0, 12) == ("PERPETUAL-N1-W189-SHARD-0",', 1),
    ('"n1w188-0of12"), "W188 entry identity"', '"n1w189-0of12"), "W189 entry identity"', 1),
    ('assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W188-SHARD-11",', 'assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W189-SHARD-11",', 1),
    ('"n1w188-11of12")', '"n1w189-11of12")', 1),
    ('assert SHARD_DIR.endswith("n1_w188") and OUT.endswith(', 'assert SHARD_DIR.endswith("n1_w189") and OUT.endswith(', 1),
    ('"n1_w188_results.json"), "W188 path drift"', '"n1_w189_results.json"), "W189 path drift"', 1),
    ('f"W188 shard dir collides with W{wprev}"', 'f"W189 shard dir collides with W{wprev}"', 1),
    ('# W188 finalize cumulative deps: W17..W187 outputs ALL PRESENT', '# W189 finalize cumulative deps: W17..W188 outputs ALL PRESENT', 1),
    ('# (landed net chain head 818,728 = W187 bm-a r887 one-pass --', '# (landed net chain head 820,928 = W188 bm-a r889 one-pass --', 1),
    ('for _depw in range(17, 188):', 'for _depw in range(17, 189):', 1),
    ('f"W188 finalize cumulative dep (W{_depw} output) missing"', 'f"W189 finalize cumulative dep (W{_depw} output) missing"', 1),
    ('# registered wave below 188 composes; wave 15 excluded by', '# registered wave below 189 composes; wave 15 excluded by', 1),
    ('# design; SINGLE STATE (W2..W187 all registered -- no', '# design; SINGLE STATE (W2..W188 all registered -- no', 1),
    ('assert sorted(w for w in WAVE_CONFIGS if w < 188) == \\', 'assert sorted(w for w in WAVE_CONFIGS if w < 189) == \\', 1),
    ('[w for w in range(16, 188)], \\', '[w for w in range(16, 189)], \\', 1),
    ('"W188 prior-wave set must derive from registry keys (no 15; "', '"W189 prior-wave set must derive from registry keys (no 15; "', 1),
    ('"W2..W187 registered single state)"', '"W2..W188 registered single state)"', 1),
    ('PATHS.root, "research", "PERPETUAL_N1_W188_PREREG.md")), \\', 'PATHS.root, "research", "PERPETUAL_N1_W189_PREREG.md")), \\', 1),
    ('"W188 per-wave prereg missing (materializer requirement)"', '"W189 per-wave prereg missing (materializer requirement)"', 1),
]

CL_PAIRS = [
    ('"+ W188 materializer face [same guard set, dep=W17..W187 ', '"+ W189 materializer face [same guard set, dep=W17..W188 ', 1),
    ('"outputs ALL PRESENT (landed net chain head 818,728 = "', '"outputs ALL PRESENT (landed net chain head 820,928 = "', 1),
    ('"W187 bm-a r887 one-pass, K=409,320 merged pool; ZERO "', '"W188 bm-a r889 one-pass, K=411,520 merged pool; ZERO "', 1),
    ('"in-flight upstream seats), ONE HUNDRED-AND-SEVENTY-EIGHTH "', '"in-flight upstream seats), ONE HUNDRED-AND-SEVENTY-NINTH "', 1),
    ('"ENGINE-OWNED WAVE BY MACHINE-DERIVE (engine_owner rows 177 "', '"ENGINE-OWNED WAVE BY MACHINE-DERIVE (engine_owner rows 178 "', 1),
    ("+ candidate) bm-a's one-hundred-fourth owned claim per ", "+ candidate) bm-a's one-hundred-fifth owned claim per ", 1),
    ('"machine-derive (engine_owner==bm-a rows 103 + candidate), "', '"machine-derive (engine_owner==bm-a rows 104 + candidate), "', 1),
    ('"A=FIRST-CLEAN past the registered W187 B band (staircase "', '"A=FIRST-CLEAN past the registered W188 B band (staircase "', 1),
    ('"FORTY-EIGHTH instance, E36 card, hops=1) + B=FIRST-CLEAN past the "', '"FORTY-NINTH instance, E36 card, hops=1) + B=FIRST-CLEAN past the "', 1),
    ('"results/_r887bma_w188_probe_receipt.json, law sec.4 W188 row, "', '"results/_r888bma_w189_probe_receipt.json, law sec.4 W189 row, "', 1),
    ('"r888 bm-a] "', '"r890 bm-a] "', 1),
]

PF_NEG = ['    # W188 (bm-a r888 freeze, seat MSG-2026-10-08-1717-bma-w188-seat', 'pushed to origin 943967370 pre-freeze r565 law (r887 pre-seat', '(3-item; the W187 finalize product already on origin since r887,', '# = direct fast-forward behind-0 at fetch (r887 pre-seat', '# push), zero merge, zero --no-verify; self-ack archive ALREADY\r\n    # LANDED pre-freeze -- bm-a r887-window self-ack move (the W188\r\n    # seat MSG sits in fleet/inbox/processed/ at freeze time, honest\r\n    # archived);', 'band gate ADMIT results/_r887bma_w188_probe_receipt.json: A = FIRST-CLEAN', 'past the registered W187 B band (arithmetic continuation', '428_204..430_203 REFUSED at its own start by the W187 B band', '428_204..428_403, exactly as the W187 seat W188+ projection + r885 probe', '# leg4 + r888 sec8 回填窗 succession projection notes all anticipated;', 'honest forward walk hops=1 -> 428_404..430_403, non-rotational', '(428_403+1) machine-checkable -- A-hops-prior-B staircase', 'FORTY-EIGHTH instance, E36 card);', 'continuation 428_404..428_603 CLEAN on the registered universe', 'but lands INSIDE the W188 A band window -- same-freeze mutual', 'own-wave A window reserved jumps to 430_404 -> 430_404..430_603,', 'own-wave A tail+1 (430_403+1) machine-checkable);', 'W188+ projection (gate-derived r887): A first-clean', '430_404..432_403 CLEAN hops=0 / B first-clean 430_604..430_803', 'registered W188 B band 430_404..430_603 will refuse the naive', 'W189 A window; W189 freezer MUST re-derive on the post-W188', 'NOT a re-pick (R250: W188 bands were never assigned).', '188: {"a": (428_404, 430_403), "b_exit": (430_404, 430_603),', '943967370', 'r885 probe', 'r888 sec8', 'r887 pre-seat', '_r887bma', 'MSG-2026-10-08-1717', '79c9a567c', '818,728', '409,320', 'FORTY-EIGHTH', 'ONE HUNDRED-AND-SEVENTY-EIGHTH']

EN_NEG = ['188: {"batch": "PERPETUAL-N1-W188",', '"prereg": ("research/PERPETUAL_N1_W188_PREREG.md (wave-level frozen "', 'new seed bands only; ONE HUNDRED-AND-SEVENTY-EIGHTH ENGINE-OWNED WAVE ', 'BY MACHINE-DERIVE (engine_owner rows 177 + candidate), ', 'number law after the REGISTERED W187 row bm-a r886 freeze ', '79c9a567c, SINGLE STATE zero seat gap W2..W187 all ', 'registered; W188 finalize landed same-window r827, ledger ', 'head 818,728, merged pool K=409,320; seat published=reserved ', 'MSG-2026-10-08-1717-bma-w188-seat PUSHED to origin 943967370 ', 'probe receipt (3-item; the W187 finalize product already on origin since r887, not re-shipped; W146 precedent); ', 'at fetch (r887 pre-seat push), zero merge, zero ', 'engine_owner=bm-a, wave 187: ', 'A = FIRST-CLEAN past the registered W187 B band (the ', 'arithmetic continuation 428_204..430_203 is REFUSED at its ', 'own start by the W187 B band 428_204..428_403, exactly as ', 'the W187 seat W188+ projection + r885 probe leg4 + r888 sec8 回填窗 succession ', '428_404..430_403; A base == prior-wave B tail+1 ', 'machine-checkable = A-hops-prior-B staircase FORTY-EIGHTH ', 'arithmetic continuation 428_404..428_603 is CLEAN on the ', 'registered universe but lands INSIDE the W188 A band ', 'jumps to 430_404, first-clean 430_404..430_603 hops=1, ', 'convergence with the W187 seat W188+ projection + r885 probe leg4 + ', 'r888 sec8 回填窗 succession projection notes re-derived -- all ', 'MANDATORY notes honored (post-W187 universe re-derive + ', 'results/_r887bma_w188_probe_receipt.json; W189+ projection ', 'per this window gate: A first-clean 430_404..432_403 ', 'CLEAN / B first-clean 430_604..430_803 CLEAN -- naive ', 'W188 B band 430_404..430_603 will refuse the naive ', 'W189 A window; W189 freezer MUST re-derive on the ', 'post-W188 universe AND reserve the own-wave A window ', 'staircase card); W1..W187 finalize ALL LANDED (W187 ', 'finalize one-pass bm-a r887, net chain head 818,728, ', 'merged pool K=409,320) -- ZERO in-flight upstream ', '"a_seed_base": 428_404,        # law sec.4 W188 A: 428_404..430_403 (FIRST-CLEAN past the registered W187 B band; arithmetic 428_204..430_203 REFUSED at own start by the W187 B band; hops=1; A-hops-prior-B staircase FORTY-EIGHTH instance, E36 card; ordinal convergence per r587: W187 sec5.5 prose anticipated forty-eighth, r887 receipt machine-read FORTY-EIGHTH)', '"b_exit_seed_base": 430_404,   # law sec.4 W188 B: 430_404..430_603 (FIRST-CLEAN past the own-wave A window; arithmetic 428_404..428_603 lands inside own-A, same-freeze mutual exclusion W141 precedent; reserved walk hops=1; B base == own-A tail+1)', '"shard_subdir": "n1_w188", "out_name": "n1_w188_results.json",', '79c9a567c', '943967370', '818,728', '409,320', 'ONE HUNDRED-AND-SEVENTY-EIGHTH', 'rows 177', 'r885 probe', '_r887bma', 'MSG-2026-10-08-1717', 'n1w188', 'n1_w188', 'PERPETUAL-N1-W188', 'PERPETUAL_N1_W188', 'FORTY-EIGHTH', 'bm-a r886 freeze', '430_404, first-clean']

MAT_NEG = ['# --- W188 materializer face (r888 bm-a freeze, own-series law', '#     one-hundred-fourth owned per machine-derive (engine_owner==bm-a', '#     rows 103 + candidate); wave 187 = first free number after', '#     the REGISTERED W187 row (bm-a r886 freeze 79c9a567c) --', '#     SINGLE STATE zero seat gap (W2..W187 all registered). Seat', '#     published=reserved MSG-2026-10-08-1717-bma-w188-seat pushed', '#     to origin 943967370 BEFORE this freeze, r565 law (payload', '#     the W187 finalize product already on origin since r887, not', '#     at fetch (r887 pre-seat push), zero merge, zero', '#     --no-verify; self-ack inbox->processed archive ALREADY LANDED\r\n    #     pre-freeze -- bm-a r887-window self-ack move (the W188 seat\r\n    #     MSG sits in fleet/inbox/processed/ at freeze time, honest\r\n    #     archived).', '#     ONE HUNDRED-AND-SEVENTY-EIGHTH engine wave BY', '#     MACHINE-DERIVE (engine_owner rows 177 + candidate; gate', '#     W1..W187 finalize ALL LANDED (net chain head 818,728,', '#     K=409,320 merged pool; W187 finalize one-pass bm-a r887)', '#     always on. ADMIT receipt results/_r887bma_w188_probe_receipt.json;', '#     banned gate ADMIT 0; not a re-pick (R250: W188 bands were', '    _set_wave(188)', 'assert WAVE_CONFIGS[187]["a_seed_base"] == pf.N1_BANDS[187]["a"][0], \\', '"W188 A band drift vs law mirror"', 'assert WAVE_CONFIGS[187]["b_exit_seed_base"] == \\', 'pf.N1_BANDS[187]["b_exit"][0], "W188 B band drift vs law mirror"', 'assert WAVE_CONFIGS[187].get("engine_owner") == \\', 'pf.N1_BANDS[187].get("engine_owner") == "bm-a", \\', '"W188 engine_owner drift (law mirror parity)"', 'w187_a = {A_SEED_BASE + j for j in range(A_N)}', 'w187_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}', 'assert not (w187_a & w187_b), "W188 A/B band overlap"', 'assert not (w187_a & reg_ints) and not (w187_b & reg_ints), \\', '"W188 hits SEED_REGISTRY"', 'for nm, band in (("A", w187_a), ("B", w187_b)):', 'f"W188 {nm} hits v1"', 'f"W188 {nm} hits W1"', 'f"W188 {nm} hits probe seeds"', '"registered W186 row parity drift (r307; bm-a r882)"\r\n        assert pf.N1_BANDS[187] == {"a": (426_204, 428_203),\r\n                                    "b_exit": (428_204, 428_403),\r\n                                    "engine_owner": "bm-a"}, \\\r\n            "registered W187 row parity drift (r307; bm-a r886)"', '# prior-wave disjointness W2..W187 (single state: all', 'for wprev in sorted(w for w in WAVE_CONFIGS if w < 188):', 'assert not (w187_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j', 'for j in range(A_N)}), f"W188 A hits W{wprev}"', 'assert not (w187_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j', 'for j in range(B_N)}), f"W188 B hits W{wprev}"', 'n3r1_used187 = set(range(70_000, 70_006))', 'assert not (w187_a & n3r1_used187) and not (w187_b & n3r1_used187), \\', '"W188 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"', 'assert not (w187_a & lfc_actual12) and not (w187_b & lfc_actual12), \\', '"W188 bands must clear the lfc actual draw range"', 'assert not (w187_a & options_actual12) and \\', 'not (w187_b & options_actual12), \\', '"W188 bands must clear the options_wave2 actual draw range"', '# band facts (law sec.4 W188 row, r795): A = FIRST-CLEAN past', '# the registered W187 B band (the arithmetic continuation', '# 428_204..430_203 is REFUSED at its own start by the W187', '# B band 428_204..428_403, exactly as the W187 seat W188+ projection +', '# r885 probe leg4 + r888 sec8 回填窗 succession projection notes', '# 428_404..430_403; A base == prior-wave B tail+1 (428_403+1)', '# machine-checkable -- A-hops-prior-B staircase FORTY-EIGHTH', '# continuation 428_404..428_603 is CLEAN on the registered', '# universe but lands INSIDE the W188 A band window --', '# 430_404 and lands 430_404..430_603, hops=1, non-rotational', '# (430_403+1) machine-checkable; cross-window convergence', '# with the W187 seat W188+ projection + r885 probe leg4 + r888 sec8', '# honored (post-W187 universe re-derive + own-wave A', '# reservation when deriving B); seat MSG-1717 tail,', 'assert WAVE_CONFIGS[188]["a_seed_base"] == 428_404 == 428_403 + 1, (', '"W188 A must be the first-clean window past the registered "', '"W187 B band tail 428_403+1 (arithmetic continuation "', '"428_204..430_203 REFUSED at its own start by the W187 B "', '"band 428_204..428_403, exactly as the W187 seat W188+ projection + "', '"r885 probe leg4 + r888 sec8 回填窗 succession projection notes "', '"staircase FORTY-EIGHTH instance, E36 card)"', 'arith_a187 = set(range(428_404, 430_404))', 'assert not (arith_a187 & reg_ints), \\', '"W188 A window must be CLEAN (first-clean ADMIT face past prior-wave B)"', 'assert WAVE_CONFIGS[188]["b_exit_seed_base"] == 430_404 == 430_403 + 1, (', '"W188 B must be the first-clean window past the own-wave A "', '"band tail 430_403+1 (arithmetic continuation "', '"428_404..428_603 CLEAN on the registered universe but "', '"lands INSIDE the W188 A band window; same-freeze mutual "', '"own-wave A window reserved jumps to 430_404, first-clean "', 'arith_b187 = set(range(430_404, 430_604))', 'assert not (arith_b187 & reg_ints), \\', '"W188 B window must be CLEAN (first-clean ADMIT face past own-wave A)"', 'assert not (arith_b187 & arith_a187), \\', '"W188 A/B same-freeze mutual exclusion (B hops past own A)"', 'assert _entry_shard_of(0, 12) == ("PERPETUAL-N1-W188-SHARD-0",', '"n1w188-0of12"), "W188 entry identity"', 'assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W188-SHARD-11",', '"n1w188-11of12")', 'assert SHARD_DIR.endswith("n1_w188") and OUT.endswith(', '"n1_w188_results.json"), "W188 path drift"', 'f"W188 shard dir collides with W{wprev}"', '# W188 finalize cumulative deps: W17..W187 outputs ALL PRESENT', '# (landed net chain head 818,728 = W187 bm-a r887 one-pass --', 'for _depw in range(17, 188):', 'f"W188 finalize cumulative dep (W{_depw} output) missing"', '# registered wave below 188 composes; wave 15 excluded by', '# design; SINGLE STATE (W2..W187 all registered -- no', 'assert sorted(w for w in WAVE_CONFIGS if w < 188) == \\', '[w for w in range(16, 188)], \\', '"W188 prior-wave set must derive from registry keys (no 15; "', '"W2..W187 registered single state)"', 'PATHS.root, "research", "PERPETUAL_N1_W188_PREREG.md")), \\', '"W188 per-wave prereg missing (materializer requirement)"', 'w187_', 'arith_a187', 'arith_b187', 'n3r1_used187', 'r885 probe', 'r887 pre-seat', '79c9a567c', 'ONE HUNDRED-AND-SEVENTY-EIGHTH', 'one-hundred-fourth', 'rows 177', 'rows 103 ', 'range(17, 188)', 'range(16, 188)', 'PERPETUAL_N1_W188', 'PERPETUAL-N1-W188', 'MSG-1717', '_r887bma', 'bm-a r887-window', 'n1w188', 'n1_w188', '818,728', '409,320']

CL_NEG = ['"+ W188 materializer face [same guard set, dep=W17..W187 ', '"outputs ALL PRESENT (landed net chain head 818,728 = "', '"W187 bm-a r887 one-pass, K=409,320 merged pool; ZERO "', '"in-flight upstream seats), ONE HUNDRED-AND-SEVENTY-EIGHTH "', '"ENGINE-OWNED WAVE BY MACHINE-DERIVE (engine_owner rows 177 "', "+ candidate) bm-a's one-hundred-fourth owned claim per ", '"machine-derive (engine_owner==bm-a rows 103 + candidate), "', '"A=FIRST-CLEAN past the registered W187 B band (staircase "', '"FORTY-EIGHTH instance, E36 card, hops=1) + B=FIRST-CLEAN past the "', '"results/_r887bma_w188_probe_receipt.json, law sec.4 W188 row, "', '"r888 bm-a] "', '818,728', '409,320', 'ONE HUNDRED-AND-SEVENTY-EIGHTH', 'one-hundred-fourth', 'rows 177', 'rows 103 ', 'FORTY-EIGHTH', '_r887bma', 'r888 bm-a] ']

blk189 = vmap(pfblk, PF_PAIRS, PF_NEG, "pf")
entry189 = IND23 + vmap(entry, EN_PAIRS, EN_NEG, "entry")
mat189 = "    " + vmap(mat, MAT_PAIRS, MAT_NEG, "mat")
claim189 = IND10 + vmap(claim, CL_PAIRS, CL_NEG, "claim")

# ---- apply insertions (in-memory) ---------------------------------------
pfsrc = io.open(PF, encoding="utf-8", newline="").read()
n1src = io.open(N1, encoding="utf-8", newline="").read()

# pf: insert W189 block after the W188 row (last registered), before the
# dict close -- r560 insert-after-last-registered-row + post-anchor gate
seg = EO + NL + "}"
check(pfsrc.count(seg) == 1, "pf row-close segment not unique")
pfnew = pfsrc.replace(seg, EO + NL + blk189 + NL + "}", 1)

# n1 entry: after the W188 entry, before the WAVE_CONFIGS close
seg = EO + NL + IND23 + "}"
check(n1src.count(seg) == 1, "n1 entry-close segment not unique")
n1new = n1src.replace(seg, EO + NL + entry189 + NL + IND23 + "}", 1)

# n1 mat: insert the W189 block before the T-141 s2 lane face header
seg = "    # --- T-141 s2 lane face"
check(n1new.count(seg) == 1, "n1 T-141 mat anchor not unique")
n1new = n1new.replace(seg, mat189 + NL + seg, 1)

# n1 claim: insert the W189 attribution after the W188 claim tail line
# (r581 law: anchor = tail single-line literal + post-anchor guard)
seg = '"r888 bm-a] "' + NL + IND10 + '"+ T-141 s2 "'
check(n1new.count(seg) == 1, "n1 claim anchor not unique")
n1new = n1new.replace(seg, '"r888 bm-a] "' + NL + claim189 + NL + IND10 +
                      '"+ T-141 s2 "', 1)

# ---- gates (r780/r781/r560/r815 lineage) --------------------------------
ast.parse(pfnew)
ast.parse(n1new)
print("AST gate: both files parse OK")

# W189 presence + W188 anti-vanish (r560 law)
checks = [
    (pfnew, '189: {"a": (430_604, 432_603), "b_exit": (432_604, 432_803),', 1),
    (pfnew, '188: {"a": (428_404, 430_403), "b_exit": (430_404, 430_603),', 1),
    (pfnew, "# W189 (bm-a r890 freeze", 1),
    (pfnew, "# W188 (bm-a r888 freeze", 1),
    (n1new, '189: {"batch": "PERPETUAL-N1-W189",', 1),
    (n1new, '188: {"batch": "PERPETUAL-N1-W188",', 1),
    (n1new, "# --- W189 materializer face", 1),
    (n1new, "# --- W188 materializer face", 1),
    (n1new, '"r890 bm-a] "', 1),
    (n1new, '"r888 bm-a] "', 1),
    (n1new, '"a_seed_base": 430_604,', 1),
    (n1new, '"b_exit_seed_base": 432_604,', 1),
    (n1new, "n1_w189", 4),
    (n1new, "PERPETUAL_N1_W189_PREREG.md", 2),
]
for src, needle, cnt in checks:
    got = src.count(needle)
    check(got == cnt, "post-edit needle %r count %d != %d" % (needle[:50], got, cnt))

# W190+ projection prose present in the new W189 blocks (probe leg4
# verbatim; r819 post-edit assert bloodline + r776 fragment-needle law;
# pf header = self-wave W189+ per r845 precedent, n1 fragment =
# next-wave W190+)
check("# W189+ projection (gate-derived r888)" in pfnew,
      "pf W189+ projection head missing")
check('probe_receipt.json; W190+ projection "' in n1new,
      "n1 W190+ projection head fragment missing")
check("# 432_604..434_603 CLEAN hops=0 / B first-clean 432_804..433_003" in pfnew,
      "pf W190p prose missing")
check("W190 A window; W190 freezer MUST re-derive on the post-W189" in pfnew,
      "pf W190 freezer prose missing")
check('"W190 A window; W190 freezer MUST re-derive on the "' in n1new,
      "n1 W190 freezer fragment missing")
check('"W189 B band 432_604..432_803 will refuse the naive "' in n1new,
      "n1 W189-band refuse fragment missing")

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
check('189: {"a": (430_604' not in pf_o2, "write-time: origin pf carries W189")
check('189: {"batch"' not in n1_o2, "write-time: origin n1 carries W189")
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
