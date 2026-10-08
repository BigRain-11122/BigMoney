# -*- coding: utf-8 -*-
"""r892 bm-a W190 freeze edits: four insertions (pf N1_BANDS[190] row +
n1 WAVE_CONFIGS[190] entry + n1 W190 materializer block + n1 W190
PASS-claim attribution). DRY flag: --dry = zero-write simulation
(r781 verify-separation law + freeze-edits dry-run precedent: full
stale+prose+AST asserts in memory BEFORE any write).

Bloodline: freeze-edits machinery (r773 pit law freeze-editor compliance +
r776 fragment-needle law + r781 verify-separation law), W190 facts
live-registry-driven (built by _r892bma_w190_freeze_buildgen.py: old
sides = the PHYSICAL W189 face fragments probed to dumps first-leg
r892, new sides = the S89 W190 fact map, counts verified pre-emission;
extraction-from-EMISSION law: pairs AST-carried from the r890 emitted
tool -- the ground truth that produced the live faces, the r890
buildgen source having diverged in the MAT append-pair shape):
  - pre-seat probe results/_r891bma_w190_probe_receipt.json rc0 ADMIT
    (naive A 432_604..434_603 refused at its own start by the
    registered W189 B band 432_604..432_803; honest forward walk
    1 hop lands A 432_804..434_803 staircase FIFTIETH instance
    E36 -- receipt A_semantics machine-cites r891 W189 probe leg4 +
    W189 materializer W190+ projection anticipated + MANDATED this
    re-derive (projection and receipt ordinals MATCH, no divergence
    this wave); B 434_804..435_003 own-A mutual exclusion hops=1,
    naive 432_804..433_003);
  - face probe results/_r892bma_w190_probe_stage1.json rc0 (all four
    W189 faces dumped first-leg r892; this TOK is built from the
    PHYSICAL probe-dumped shapes, r776 law);
  - seat MSG-2026-10-08-2035-bma-w190-seat published on origin at
    c177bf73b (r891 seat push; r565 law: on origin BEFORE this freeze
    commit); self-ack archive ALREADY LANDED -- bm-a r892-window
    archive move (this window, on-disk processed/ live-verified at
    freeze time; origin face = the r891 inbox path, dual-path union
    per r374 law);
  - per-wave prereg research/PERPETUAL_N1_W190_PREREG.md built r892
    (buildgen r890-bloodline; DRY 50/50 green; frozen+pushed 8394b75ea
    r892; on origin, verified live below);
  - W190 freeze registered sha machine-derived = 8addea3eb
    (GENERATION FACT CHANGE disclosed: no standalone anchored 'W189
    five-face freeze' subject -- the W189 insertions rode the r890
    round closeout commit; content-anchored git log -S '189: {"a":
    (430_604' -- scripts/perpetual_faces.py, r812 path-derived
    precedent); W189 finalize landed r891 one-pass same-chain: ledger
    head 823,128, merged pool K=413,720 (n1_w189_results.json
    machine-read); W189 sec7/sec8 settle backfill landed the r892
    window (this window, first-leg);
  - lineage constants disclosed (r795/r845/r849/r852/r863/r867/
    r869/r874/r878/r882/r885/r888/r890 precedent, passed through):
    (a) the "wave N-1 = first free number" mat-header label rolls
    forward with its off-by-one quirk (since W165 r795);
    (b) "law sec.4 W190 row, r795" band-facts template stamp keeps
    its r795; (c) "single-window derive (r812 merged the gate legs
    INTO the pre-seat probe...)" stays (historical merge citation);
    (d) the bm-a-owned ordinal word rolls one-hundred-fifth ->
    one-hundred-sixth (rows 105 + candidate = 106th owned per probe
    leg0, machine-chosen word form, disclosed); (e) mat parity-chain
    rows W138..W187 keep their historical stamps and tuples; the tail
    stamps re-label +1 per the r890-emitted shape (the [186]-row stamp
    session r882 rides STALE per quirk (f); the last stamp session
    rolls r888 -> r890); (f) the "W189 finalize landed one-pass r891"
    citation rolls its wave-word with the values rolling
    machine-correct to 823,128/413,720 this window; (g) the sec8
    succession-notes window citation rolls r890 -> r892 回填窗 (the
    W189 sec8 notes landed the r892 backfill window, honest
    next-window form, disclosed).

r773 pit law compliance:
  (1) full string-face inventory empirically probed BEFORE TOK
      (_r892bma_w190_face_probe.py first-leg r892 -- four face
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
      (r530/r687: fetch + origin carries no W190 registration before
      this freeze);
  (7) AST gate after every edit batch (r580/r781)."""
import ast
import io
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, "scripts")
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
probe = json.load(open(r"results\_r891bma_w190_probe_receipt.json",
                       encoding="utf-8"))
check(probe["verdict"] == "ADMIT", "pre-seat probe not ADMIT")
check(probe["bands"] == {"A": "432804_434803", "B": "434804_435003"},
      "probe band shape mismatch")
check(probe["legs"]["leg1"]["A"] == [432804, 434803], "A band mismatch")
check(probe["legs"]["leg1"]["B"] == [434804, 435003], "B band mismatch")
check(probe["legs"]["leg1"]["hops_A"] == 1 and probe["legs"]["leg1"]["hops_B"] == 1,
      "hops mismatch")
check(probe["legs"]["leg0"]["rows"] == 187 and probe["legs"]["leg0"]["tail"] == "W189",
      "leg0 registry tail mismatch")
check(probe["legs"]["leg0"]["ordinal"] == 180 and probe["legs"]["leg0"]["bma_ordinal"] == 106,
      "leg0 ordinal mismatch")
check(probe["legs"]["leg2"]["conflicts"] == 0, "leg2 conflicts nonzero")
check(probe["legs"]["leg3"]["origin_vacancy"] is True, "leg3 origin not vacant")
check(probe["legs"]["leg4"]["W191p_A"] == "434804..436803"
      and probe["legs"]["leg4"]["W191p_B"] == "435004..435203",
      "leg4 W191+ projection mismatch")

# origin anti-collision pre-check (r511 tail-lock / r687 write-time gate)
subprocess.run(["git", "fetch", "origin"], capture_output=True)
pf_o = subprocess.run(["git", "show", "origin/main:" + PF],
                      capture_output=True).stdout.decode("utf-8", "replace")
n1_o = subprocess.run(["git", "show", "origin/main:" + N1],
                      capture_output=True).stdout.decode("utf-8", "replace")
check('190: {"a": (432_804' not in pf_o, "origin pf already carries W190 row")
check("W190 (bm-a r892 freeze" not in pf_o, "origin pf carries W190 block")
check('190: {"batch"' not in n1_o, "origin n1 already carries W190 entry")
check("# --- W190 materializer face" not in n1_o, "origin n1 carries W190 mat")
check('"r892 bm-a] "' not in n1_o, "origin n1 carries W190 claim")

# machine-derived shas (r587 / r812 path-derived precedent)
seat_sha = subprocess.run(
    ["git", "log", "origin/main", "--format=%h", "-n", "1", "--diff-filter=A",
     "--", "fleet/inbox/MSG-2026-10-08-2035-bma-w190-seat.md"],
    capture_output=True).stdout.decode().strip()
check(seat_sha == "c177bf73b", "seat sha path-derived mismatch: " + seat_sha)
check(os.path.exists(os.path.join(
    "fleet", "inbox", "processed", "MSG-2026-10-08-2035-bma-w190-seat.md")),
    "seat MSG not in on-disk processed/ at freeze time (r892-window archive)")
w189_freeze_sha = subprocess.run(
    ["git", "log", "origin/main", "--format=%h", "-n", "1",
     "-S", '189: {"a": (430_604', "--", "scripts/perpetual_faces.py"],
    capture_output=True).stdout.decode().strip()
check(w189_freeze_sha == "8addea3eb",
      "W190 five-face registration sha mismatch (content-anchored): "
      + w189_freeze_sha)

# ---- live-registry parity pre-check (edit-gate: never edit a drifted file)
sys.path.insert(0, ".")
import perpetual_faces as pfmod  # noqa: E402
check(len(pfmod.N1_BANDS) == 187, "live N1_BANDS row count drift: %d" % len(pfmod.N1_BANDS))
check(pfmod.N1_BANDS[189] == {"a": (430_604, 432_603),
                              "b_exit": (432_604, 432_803),
                              "engine_owner": "bm-a"}, "live W189 row drift")
check(190 not in pfmod.N1_BANDS, "live N1_BANDS already has 190")
check(os.path.exists(os.path.join("research", "PERPETUAL_N1_W190_PREREG.md")),
      "W190 per-wave prereg missing (materializer gate)")
prereg_o = subprocess.run(["git", "show", "origin/main:research/PERPETUAL_N1_W190_PREREG.md"],
                          capture_output=True)
check(prereg_o.returncode == 0, "W190 prereg absent on origin")

# ---- physical face dumps (r776 law) -----------------------------------
pfblk = io.open(r"results\_r892bma_w190_probe_pf_block.txt", encoding="utf-8",
                newline="").read()
entry = io.open(r"results\_r892bma_w190_probe_n1_entry.txt", encoding="utf-8",
                newline="").read()
mat = io.open(r"results\_r892bma_w190_probe_n1_mat.txt", encoding="utf-8",
              newline="").read()
claim = io.open(r"results\_r892bma_w190_probe_n1_claim.txt", encoding="utf-8",
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
    ('    # W189 (bm-a r890 freeze, seat MSG-2026-10-08-1815-bma-w189-seat', '    # W190 (bm-a r892 freeze, seat MSG-2026-10-08-2035-bma-w190-seat', 1),
    ('pushed to origin 744de26ef pre-freeze r565 law (r888 pre-seat', 'pushed to origin c177bf73b pre-freeze r565 law (r891 pre-seat', 1),
    ('(3-item; the W188 finalize product already on origin since r888,', '(3-item; the W189 finalize product already on origin since r890,', 1),
    ('# = direct fast-forward behind-0 at fetch (r888 pre-seat', '# = direct fast-forward behind-0 at fetch (r891 pre-seat', 1),
    ('# push), zero merge, zero --no-verify; self-ack archive ALREADY\r\n    # LANDED pre-freeze -- bm-a r889-window archive move (the W189\r\n    # seat MSG sits in fleet/inbox/processed/ at freeze time, honest\r\n    # archived);', '# push), zero merge, zero --no-verify; self-ack archive ALREADY\r\n    # LANDED pre-freeze -- bm-a r892-window archive move (the W190\r\n    # seat MSG sits in fleet/inbox/processed/ at freeze time, honest\r\n    # archived);', 1),
    ('band gate ADMIT results/_r888bma_w189_probe_receipt.json: A = FIRST-CLEAN', 'band gate ADMIT results/_r891bma_w190_probe_receipt.json: A = FIRST-CLEAN', 1),
    ('past the registered W188 B band (arithmetic continuation', 'past the registered W189 B band (arithmetic continuation', 1),
    ('430_404..432_403 REFUSED at its own start by the W188 B band', '432_604..434_603 REFUSED at its own start by the W189 B band', 1),
    ('430_404..430_603, exactly as the W188 seat W189+ projection + r888 probe', '432_604..432_803, exactly as the W189 seat W190+ projection + r891 probe', 1),
    ('# leg4 + r890 sec8 回填窗 succession projection notes all anticipated;', '# leg4 + r892 sec8 回填窗 succession projection notes all anticipated;', 1),
    ('honest forward walk hops=1 -> 430_604..432_603, non-rotational', 'honest forward walk hops=1 -> 432_804..434_803, non-rotational', 1),
    ('(430_603+1) machine-checkable -- A-hops-prior-B staircase', '(432_803+1) machine-checkable -- A-hops-prior-B staircase', 1),
    ('FORTY-NINTH instance, E36 card);', 'FIFTIETH instance, E36 card);', 1),
    ('continuation 430_604..430_803 CLEAN on the registered universe', 'continuation 432_804..433_003 CLEAN on the registered universe', 1),
    ('but lands INSIDE the W189 A band window -- same-freeze mutual', 'but lands INSIDE the W190 A band window -- same-freeze mutual', 1),
    ('own-wave A window reserved jumps to 432_604 -> 432_604..432_803,', 'own-wave A window reserved jumps to 434_804 -> 434_804..435_003,', 1),
    ('own-wave A tail+1 (432_603+1) machine-checkable);', 'own-wave A tail+1 (434_803+1) machine-checkable);', 1),
    ('W189+ projection (gate-derived r888): A first-clean', 'W190+ projection (gate-derived r891): A first-clean', 1),
    ('432_604..434_603 CLEAN hops=0 / B first-clean 432_804..433_003', '434_804..436_803 CLEAN hops=0 / B first-clean 435_004..435_203', 1),
    ('registered W189 B band 432_604..432_803 will refuse the naive', 'registered W190 B band 434_804..435_003 will refuse the naive', 1),
    ('W190 A window; W190 freezer MUST re-derive on the post-W189', 'W191 A window; W191 freezer MUST re-derive on the post-W190', 1),
    ('NOT a re-pick (R250: W189 bands were never assigned).', 'NOT a re-pick (R250: W190 bands were never assigned).', 1),
    ('189: {"a": (430_604, 432_603), "b_exit": (432_604, 432_803),', '190: {"a": (432_804, 434_803), "b_exit": (434_804, 435_003),', 1),
]

EN_PAIRS = [
    ('189: {"batch": "PERPETUAL-N1-W189",', '190: {"batch": "PERPETUAL-N1-W190",', 1),
    ('"prereg": ("research/PERPETUAL_N1_W189_PREREG.md (wave-level frozen "', '"prereg": ("research/PERPETUAL_N1_W190_PREREG.md (wave-level frozen "', 1),
    ('new seed bands only; ONE HUNDRED-AND-SEVENTY-NINTH ENGINE-OWNED WAVE ', 'new seed bands only; ONE HUNDRED-AND-NINETIETH ENGINE-OWNED WAVE ', 1),
    ('BY MACHINE-DERIVE (engine_owner rows 178 + candidate), ', 'BY MACHINE-DERIVE (engine_owner rows 179 + candidate), ', 1),
    ('number law after the REGISTERED W188 row bm-a r888 freeze ', 'number law after the REGISTERED W189 row bm-a r890 freeze ', 1),
    ('b66117659, SINGLE STATE zero seat gap W2..W188 all ', '8addea3eb, SINGLE STATE zero seat gap W2..W189 all ', 1),
    ('registered; W189 finalize landed same-window r827, ledger ', 'registered; W190 finalize landed same-window r827, ledger ', 1),
    ('head 820,928, merged pool K=411,520; seat published=reserved ', 'head 823,128, merged pool K=413,720; seat published=reserved ', 1),
    ('MSG-2026-10-08-1815-bma-w189-seat PUSHED to origin 744de26ef ', 'MSG-2026-10-08-2035-bma-w190-seat PUSHED to origin c177bf73b ', 1),
    ('probe receipt (3-item; the W188 finalize product already on origin since r888, not re-shipped; W146 precedent); ', 'probe receipt (3-item; the W189 finalize product already on origin since r890, not re-shipped; W146 precedent); ', 1),
    ('at fetch (r888 pre-seat push), zero merge, zero ', 'at fetch (r891 pre-seat push), zero merge, zero ', 1),
    ('engine_owner=bm-a, wave 188: ', 'engine_owner=bm-a, wave 189: ', 1),
    ('A = FIRST-CLEAN past the registered W188 B band (the ', 'A = FIRST-CLEAN past the registered W189 B band (the ', 1),
    ('arithmetic continuation 430_404..432_403 is REFUSED at its ', 'arithmetic continuation 432_604..434_603 is REFUSED at its ', 1),
    ('own start by the W188 B band 430_404..430_603, exactly as ', 'own start by the W189 B band 432_604..432_803, exactly as ', 1),
    ('the W188 seat W189+ projection + r888 probe leg4 + r890 sec8 回填窗 succession ', 'the W189 seat W190+ projection + r891 probe leg4 + r892 sec8 回填窗 succession ', 1),
    ('projection notes anticipated; honest forward walk hops=1 -> ', 'projection notes anticipated; honest forward walk hops=1 -> ', 1),
    ('430_604..432_603; A base == prior-wave B tail+1 ', '432_804..434_803; A base == prior-wave B tail+1 ', 1),
    ('machine-checkable = A-hops-prior-B staircase FORTY-NINTH ', 'machine-checkable = A-hops-prior-B staircase FIFTIETH ', 1),
    ('arithmetic continuation 430_604..430_803 is CLEAN on the ', 'arithmetic continuation 432_804..433_003 is CLEAN on the ', 1),
    ('registered universe but lands INSIDE the W189 A band ', 'registered universe but lands INSIDE the W190 A band ', 1),
    ('jumps to 432_604, first-clean 432_604..432_803 hops=1, ', 'jumps to 434_804, first-clean 434_804..435_003 hops=1, ', 1),
    ('convergence with the W188 seat W189+ projection + r888 probe leg4 + ', 'convergence with the W189 seat W190+ projection + r891 probe leg4 + ', 1),
    ('r890 sec8 回填窗 succession projection notes re-derived -- all ', 'r892 sec8 回填窗 succession projection notes re-derived -- all ', 1),
    ('MANDATORY notes honored (post-W188 universe re-derive + ', 'MANDATORY notes honored (post-W189 universe re-derive + ', 1),
    ('results/_r888bma_w189_probe_receipt.json; W190+ projection ', 'results/_r891bma_w190_probe_receipt.json; W191+ projection ', 1),
    ('per this window gate: A first-clean 432_604..434_603 ', 'per this window gate: A first-clean 434_804..436_803 ', 1),
    ('CLEAN / B first-clean 432_804..433_003 CLEAN -- naive ', 'CLEAN / B first-clean 435_004..435_203 CLEAN -- naive ', 1),
    ('W189 B band 432_604..432_803 will refuse the naive ', 'W190 B band 434_804..435_003 will refuse the naive ', 1),
    ('W190 A window; W190 freezer MUST re-derive on the ', 'W191 A window; W191 freezer MUST re-derive on the ', 1),
    ('post-W189 universe AND reserve the own-wave A window ', 'post-W190 universe AND reserve the own-wave A window ', 1),
    ('staircase card); W1..W188 finalize ALL LANDED (W188 ', 'staircase card); W1..W189 finalize ALL LANDED (W189 ', 1),
    ('finalize one-pass bm-a r889, net chain head 820,928, ', 'finalize one-pass bm-a r891, net chain head 823,128, ', 1),
    ('merged pool K=411,520) -- ZERO in-flight upstream ', 'merged pool K=413,720) -- ZERO in-flight upstream ', 1),
    ('"a_seed_base": 430_604,        # law sec.4 W189 A: 430_604..432_603 (FIRST-CLEAN past the registered W188 B band; arithmetic 430_404..432_403 REFUSED at own start by the W188 B band; hops=1; A-hops-prior-B staircase FORTY-NINTH instance, E36 card; ordinal convergence per r587: W188 sec5.5 prose anticipated forty-ninth, r888 receipt machine-read FORTY-NINTH)', '"a_seed_base": 432_804,        # law sec.4 W190 A: 432_804..434_803 (FIRST-CLEAN past the registered W189 B band; arithmetic 432_604..434_603 REFUSED at own start by the W189 B band; hops=1; A-hops-prior-B staircase FIFTIETH instance, E36 card; ordinal convergence per r587: W189 sec5.5 prose anticipated fiftieth, r891 receipt machine-read FIFTIETH)', 1),
    ('"b_exit_seed_base": 432_604,   # law sec.4 W189 B: 432_604..432_803 (FIRST-CLEAN past the own-wave A window; arithmetic 430_604..430_803 lands inside own-A, same-freeze mutual exclusion W141 precedent; reserved walk hops=1; B base == own-A tail+1)', '"b_exit_seed_base": 434_804,   # law sec.4 W190 B: 434_804..435_003 (FIRST-CLEAN past the own-wave A window; arithmetic 432_804..433_003 lands inside own-A, same-freeze mutual exclusion W141 precedent; reserved walk hops=1; B base == own-A tail+1)', 1),
    ('"shard_subdir": "n1_w189", "out_name": "n1_w189_results.json",', '"shard_subdir": "n1_w190", "out_name": "n1_w190_results.json",', 1),
]

MAT_PAIRS = [
    ('# --- W189 materializer face (r890 bm-a freeze, own-series law', '# --- W190 materializer face (r892 bm-a freeze, own-series law', 1),
    ('#     one-hundred-fifth owned per machine-derive (engine_owner==bm-a', '#     one-hundred-sixth owned per machine-derive (engine_owner==bm-a', 1),
    ('#     rows 104 + candidate); wave 188 = first free number after', '#     rows 105 + candidate); wave 189 = first free number after', 1),
    ('#     the REGISTERED W188 row (bm-a r888 freeze b66117659) --', '#     the REGISTERED W189 row (bm-a r890 freeze 8addea3eb) --', 1),
    ('#     SINGLE STATE zero seat gap (W2..W188 all registered). Seat', '#     SINGLE STATE zero seat gap (W2..W189 all registered). Seat', 1),
    ('#     published=reserved MSG-2026-10-08-1815-bma-w189-seat pushed', '#     published=reserved MSG-2026-10-08-2035-bma-w190-seat pushed', 1),
    ('#     to origin 744de26ef BEFORE this freeze, r565 law (payload', '#     to origin c177bf73b BEFORE this freeze, r565 law (payload', 1),
    ('#     the W188 finalize product already on origin since r888, not', '#     the W189 finalize product already on origin since r890, not', 1),
    ('#     at fetch (r888 pre-seat push), zero merge, zero', '#     at fetch (r891 pre-seat push), zero merge, zero', 1),
    ('#     --no-verify; self-ack inbox->processed archive ALREADY LANDED\r\n    #     pre-freeze -- bm-a r889-window archive move (the W189 seat\r\n    #     MSG sits in fleet/inbox/processed/ at freeze time, honest\r\n    #     archived).', '#     --no-verify; self-ack inbox->processed archive ALREADY LANDED\r\n    #     pre-freeze -- bm-a r892-window archive move (the W190 seat\r\n    #     MSG sits in fleet/inbox/processed/ at freeze time, honest\r\n    #     archived).', 1),
    ('#     ONE HUNDRED-AND-SEVENTY-NINTH engine wave BY', '#     ONE HUNDRED-AND-NINETIETH engine wave BY', 1),
    ('#     MACHINE-DERIVE (engine_owner rows 178 + candidate; gate', '#     MACHINE-DERIVE (engine_owner rows 179 + candidate; gate', 1),
    ('#     W1..W188 finalize ALL LANDED (net chain head 820,928,', '#     W1..W189 finalize ALL LANDED (net chain head 823,128,', 1),
    ('#     K=411,520 merged pool; W188 finalize one-pass bm-a r889)', '#     K=413,720 merged pool; W189 finalize one-pass bm-a r891)', 1),
    ('#     always on. ADMIT receipt results/_r888bma_w189_probe_receipt.json;', '#     always on. ADMIT receipt results/_r891bma_w190_probe_receipt.json;', 1),
    ('#     banned gate ADMIT 0; not a re-pick (R250: W189 bands were', '#     banned gate ADMIT 0; not a re-pick (R250: W190 bands were', 1),
    ('    _set_wave(189)', '    _set_wave(190)', 1),
    ('assert WAVE_CONFIGS[188]["a_seed_base"] == pf.N1_BANDS[188]["a"][0], \\', 'assert WAVE_CONFIGS[189]["a_seed_base"] == pf.N1_BANDS[189]["a"][0], \\', 1),
    ('"W189 A band drift vs law mirror"', '"W190 A band drift vs law mirror"', 1),
    ('assert WAVE_CONFIGS[188]["b_exit_seed_base"] == \\', 'assert WAVE_CONFIGS[189]["b_exit_seed_base"] == \\', 1),
    ('pf.N1_BANDS[188]["b_exit"][0], "W189 B band drift vs law mirror"', 'pf.N1_BANDS[189]["b_exit"][0], "W190 B band drift vs law mirror"', 1),
    ('assert WAVE_CONFIGS[188].get("engine_owner") == \\', 'assert WAVE_CONFIGS[189].get("engine_owner") == \\', 1),
    ('pf.N1_BANDS[188].get("engine_owner") == "bm-a", \\', 'pf.N1_BANDS[189].get("engine_owner") == "bm-a", \\', 1),
    ('"W189 engine_owner drift (law mirror parity)"', '"W190 engine_owner drift (law mirror parity)"', 1),
    ('w188_a = {A_SEED_BASE + j for j in range(A_N)}', 'w189_a = {A_SEED_BASE + j for j in range(A_N)}', 1),
    ('w188_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}', 'w189_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}', 1),
    ('assert not (w188_a & w188_b), "W189 A/B band overlap"', 'assert not (w189_a & w189_b), "W190 A/B band overlap"', 1),
    ('assert not (w188_a & reg_ints) and not (w188_b & reg_ints), \\', 'assert not (w189_a & reg_ints) and not (w189_b & reg_ints), \\', 1),
    ('"W189 hits SEED_REGISTRY"', '"W190 hits SEED_REGISTRY"', 1),
    ('for nm, band in (("A", w188_a), ("B", w188_b)):', 'for nm, band in (("A", w189_a), ("B", w189_b)):', 1),
    ('f"W189 {nm} hits v1"', 'f"W190 {nm} hits v1"', 1),
    ('f"W189 {nm} hits W1"', 'f"W190 {nm} hits W1"', 1),
    ('f"W189 {nm} hits probe seeds"', 'f"W190 {nm} hits probe seeds"', 1),
    ('"registered W187 row parity drift (r307; bm-a r882)"\r\n        assert pf.N1_BANDS[187] == {"a": (426_204, 428_203),\r\n                                    "b_exit": (428_204, 428_403),\r\n                                    "engine_owner": "bm-a"}, \\\r\n            "registered W188 row parity drift (r307; bm-a r888)"', '"registered W188 row parity drift (r307; bm-a r882)"\r\n        assert pf.N1_BANDS[187] == {"a": (426_204, 428_203),\r\n                                    "b_exit": (428_204, 428_403),\r\n                                    "engine_owner": "bm-a"}, \\\r\n            "registered W189 row parity drift (r307; bm-a r890)"', 1),
    ('# prior-wave disjointness W2..W188 (single state: all', '# prior-wave disjointness W2..W189 (single state: all', 1),
    ('for wprev in sorted(w for w in WAVE_CONFIGS if w < 189):', 'for wprev in sorted(w for w in WAVE_CONFIGS if w < 190):', 2),
    ('assert not (w188_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j', 'assert not (w189_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j', 1),
    ('for j in range(A_N)}), f"W189 A hits W{wprev}"', 'for j in range(A_N)}), f"W190 A hits W{wprev}"', 1),
    ('assert not (w188_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j', 'assert not (w189_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j', 1),
    ('for j in range(B_N)}), f"W189 B hits W{wprev}"', 'for j in range(B_N)}), f"W190 B hits W{wprev}"', 1),
    ('n3r1_used188 = set(range(70_000, 70_006))', 'n3r1_used189 = set(range(70_000, 70_006))', 1),
    ('assert not (w188_a & n3r1_used188) and not (w188_b & n3r1_used188), \\', 'assert not (w189_a & n3r1_used189) and not (w189_b & n3r1_used189), \\', 1),
    ('"W189 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"', '"W190 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"', 1),
    ('assert not (w188_a & lfc_actual12) and not (w188_b & lfc_actual12), \\', 'assert not (w189_a & lfc_actual12) and not (w189_b & lfc_actual12), \\', 1),
    ('"W189 bands must clear the lfc actual draw range"', '"W190 bands must clear the lfc actual draw range"', 1),
    ('assert not (w188_a & options_actual12) and \\', 'assert not (w189_a & options_actual12) and \\', 1),
    ('not (w188_b & options_actual12), \\', 'not (w189_b & options_actual12), \\', 1),
    ('"W189 bands must clear the options_wave2 actual draw range"', '"W190 bands must clear the options_wave2 actual draw range"', 1),
    ('# band facts (law sec.4 W189 row, r795): A = FIRST-CLEAN past', '# band facts (law sec.4 W190 row, r795): A = FIRST-CLEAN past', 1),
    ('# the registered W188 B band (the arithmetic continuation', '# the registered W189 B band (the arithmetic continuation', 1),
    ('# 430_404..432_403 is REFUSED at its own start by the W188', '# 432_604..434_603 is REFUSED at its own start by the W189', 1),
    ('# B band 430_404..430_603, exactly as the W188 seat W189+ projection +', '# B band 432_604..432_803, exactly as the W189 seat W190+ projection +', 1),
    ('# r888 probe leg4 + r890 sec8 回填窗 succession projection notes', '# r891 probe leg4 + r892 sec8 回填窗 succession projection notes', 1),
    ('# 430_604..432_603; A base == prior-wave B tail+1 (430_603+1)', '# 432_804..434_803; A base == prior-wave B tail+1 (432_803+1)', 1),
    ('# machine-checkable -- A-hops-prior-B staircase FORTY-NINTH', '# machine-checkable -- A-hops-prior-B staircase FIFTIETH', 1),
    ('# continuation 430_604..430_803 is CLEAN on the registered', '# continuation 432_804..433_003 is CLEAN on the registered', 1),
    ('# universe but lands INSIDE the W189 A band window --', '# universe but lands INSIDE the W190 A band window --', 1),
    ('# 432_604 and lands 432_604..432_803, hops=1, non-rotational', '# 434_804 and lands 434_804..435_003, hops=1, non-rotational', 1),
    ('# (432_603+1) machine-checkable; cross-window convergence', '# (434_803+1) machine-checkable; cross-window convergence', 1),
    ('# with the W188 seat W189+ projection + r888 probe leg4 + r890 sec8', '# with the W189 seat W190+ projection + r891 probe leg4 + r892 sec8', 1),
    ('# honored (post-W188 universe re-derive + own-wave A', '# honored (post-W189 universe re-derive + own-wave A', 1),
    ('# reservation when deriving B); seat MSG-1815 tail,', '# reservation when deriving B); seat MSG-2035 tail,', 1),
    ('assert WAVE_CONFIGS[189]["a_seed_base"] == 430_604 == 430_603 + 1, (', 'assert WAVE_CONFIGS[190]["a_seed_base"] == 432_804 == 432_803 + 1, (', 1),
    ('"W189 A must be the first-clean window past the registered "', '"W190 A must be the first-clean window past the registered "', 1),
    ('"W188 B band tail 430_603+1 (arithmetic continuation "', '"W189 B band tail 432_803+1 (arithmetic continuation "', 1),
    ('"430_404..432_403 REFUSED at its own start by the W188 B "', '"432_604..434_603 REFUSED at its own start by the W189 B "', 1),
    ('"band 430_404..430_603, exactly as the W188 seat W189+ projection + "', '"band 432_604..432_803, exactly as the W189 seat W190+ projection + "', 1),
    ('"r888 probe leg4 + r890 sec8 回填窗 succession projection notes "', '"r891 probe leg4 + r892 sec8 回填窗 succession projection notes "', 1),
    ('"staircase FORTY-NINTH instance, E36 card)"', '"staircase FIFTIETH instance, E36 card)"', 1),
    ('arith_a188 = set(range(430_604, 432_604))', 'arith_a189 = set(range(432_804, 434_804))', 1),
    ('assert not (arith_a188 & reg_ints), \\', 'assert not (arith_a189 & reg_ints), \\', 1),
    ('"W189 A window must be CLEAN (first-clean ADMIT face past prior-wave B)"', '"W190 A window must be CLEAN (first-clean ADMIT face past prior-wave B)"', 1),
    ('assert WAVE_CONFIGS[189]["b_exit_seed_base"] == 432_604 == 432_603 + 1, (', 'assert WAVE_CONFIGS[190]["b_exit_seed_base"] == 434_804 == 434_803 + 1, (', 1),
    ('"W189 B must be the first-clean window past the own-wave A "', '"W190 B must be the first-clean window past the own-wave A "', 1),
    ('"band tail 432_603+1 (arithmetic continuation "', '"band tail 434_803+1 (arithmetic continuation "', 1),
    ('"430_604..430_803 CLEAN on the registered universe but "', '"432_804..433_003 CLEAN on the registered universe but "', 1),
    ('"lands INSIDE the W189 A band window; same-freeze mutual "', '"lands INSIDE the W190 A band window; same-freeze mutual "', 1),
    ('"own-wave A window reserved jumps to 432_604, first-clean "', '"own-wave A window reserved jumps to 434_804, first-clean "', 1),
    ('arith_b188 = set(range(432_604, 432_804))', 'arith_b189 = set(range(434_804, 435_004))', 1),
    ('assert not (arith_b188 & reg_ints), \\', 'assert not (arith_b189 & reg_ints), \\', 1),
    ('"W189 B window must be CLEAN (first-clean ADMIT face past own-wave A)"', '"W190 B window must be CLEAN (first-clean ADMIT face past own-wave A)"', 1),
    ('assert not (arith_b188 & arith_a188), \\', 'assert not (arith_b189 & arith_a189), \\', 1),
    ('"W189 A/B same-freeze mutual exclusion (B hops past own A)"', '"W190 A/B same-freeze mutual exclusion (B hops past own A)"', 1),
    ('assert _entry_shard_of(0, 12) == ("PERPETUAL-N1-W189-SHARD-0",', 'assert _entry_shard_of(0, 12) == ("PERPETUAL-N1-W190-SHARD-0",', 1),
    ('"n1w189-0of12"), "W189 entry identity"', '"n1w190-0of12"), "W190 entry identity"', 1),
    ('assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W189-SHARD-11",', 'assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W190-SHARD-11",', 1),
    ('"n1w189-11of12")', '"n1w190-11of12")', 1),
    ('assert SHARD_DIR.endswith("n1_w189") and OUT.endswith(', 'assert SHARD_DIR.endswith("n1_w190") and OUT.endswith(', 1),
    ('"n1_w189_results.json"), "W189 path drift"', '"n1_w190_results.json"), "W190 path drift"', 1),
    ('f"W189 shard dir collides with W{wprev}"', 'f"W190 shard dir collides with W{wprev}"', 1),
    ('# W189 finalize cumulative deps: W17..W188 outputs ALL PRESENT', '# W190 finalize cumulative deps: W17..W189 outputs ALL PRESENT', 1),
    ('# (landed net chain head 820,928 = W188 bm-a r889 one-pass --', '# (landed net chain head 823,128 = W189 bm-a r891 one-pass --', 1),
    ('for _depw in range(17, 189):', 'for _depw in range(17, 190):', 1),
    ('f"W189 finalize cumulative dep (W{_depw} output) missing"', 'f"W190 finalize cumulative dep (W{_depw} output) missing"', 1),
    ('# registered wave below 189 composes; wave 15 excluded by', '# registered wave below 190 composes; wave 15 excluded by', 1),
    ('# design; SINGLE STATE (W2..W188 all registered -- no', '# design; SINGLE STATE (W2..W189 all registered -- no', 1),
    ('assert sorted(w for w in WAVE_CONFIGS if w < 189) == \\', 'assert sorted(w for w in WAVE_CONFIGS if w < 190) == \\', 1),
    ('[w for w in range(16, 189)], \\', '[w for w in range(16, 190)], \\', 1),
    ('"W189 prior-wave set must derive from registry keys (no 15; "', '"W190 prior-wave set must derive from registry keys (no 15; "', 1),
    ('"W2..W188 registered single state)"', '"W2..W189 registered single state)"', 1),
    ('PATHS.root, "research", "PERPETUAL_N1_W189_PREREG.md")), \\', 'PATHS.root, "research", "PERPETUAL_N1_W190_PREREG.md")), \\', 1),
    ('"W189 per-wave prereg missing (materializer requirement)"', '"W190 per-wave prereg missing (materializer requirement)"', 1),
]

CL_PAIRS = [
    ('"+ W189 materializer face [same guard set, dep=W17..W188 ', '"+ W190 materializer face [same guard set, dep=W17..W189 ', 1),
    ('"outputs ALL PRESENT (landed net chain head 820,928 = "', '"outputs ALL PRESENT (landed net chain head 823,128 = "', 1),
    ('"W188 bm-a r889 one-pass, K=411,520 merged pool; ZERO "', '"W189 bm-a r891 one-pass, K=413,720 merged pool; ZERO "', 1),
    ('"in-flight upstream seats), ONE HUNDRED-AND-SEVENTY-NINTH "', '"in-flight upstream seats), ONE HUNDRED-AND-NINETIETH "', 1),
    ('"ENGINE-OWNED WAVE BY MACHINE-DERIVE (engine_owner rows 178 "', '"ENGINE-OWNED WAVE BY MACHINE-DERIVE (engine_owner rows 179 "', 1),
    ("+ candidate) bm-a's one-hundred-fifth owned claim per ", "+ candidate) bm-a's one-hundred-sixth owned claim per ", 1),
    ('"machine-derive (engine_owner==bm-a rows 104 + candidate), "', '"machine-derive (engine_owner==bm-a rows 105 + candidate), "', 1),
    ('"A=FIRST-CLEAN past the registered W188 B band (staircase "', '"A=FIRST-CLEAN past the registered W189 B band (staircase "', 1),
    ('"FORTY-NINTH instance, E36 card, hops=1) + B=FIRST-CLEAN past the "', '"FIFTIETH instance, E36 card, hops=1) + B=FIRST-CLEAN past the "', 1),
    ('"results/_r888bma_w189_probe_receipt.json, law sec.4 W189 row, "', '"results/_r891bma_w190_probe_receipt.json, law sec.4 W190 row, "', 1),
    ('"r890 bm-a] "', '"r892 bm-a] "', 1),
]

PF_NEG = ['    # W189 (bm-a r890 freeze, seat MSG-2026-10-08-1815-bma-w189-seat', 'pushed to origin 744de26ef pre-freeze r565 law (r888 pre-seat', '(3-item; the W188 finalize product already on origin since r888,', '# = direct fast-forward behind-0 at fetch (r888 pre-seat', '# push), zero merge, zero --no-verify; self-ack archive ALREADY\r\n    # LANDED pre-freeze -- bm-a r889-window archive move (the W189\r\n    # seat MSG sits in fleet/inbox/processed/ at freeze time, honest\r\n    # archived);', 'band gate ADMIT results/_r888bma_w189_probe_receipt.json: A = FIRST-CLEAN', 'past the registered W188 B band (arithmetic continuation', '430_404..432_403 REFUSED at its own start by the W188 B band', '430_404..430_603, exactly as the W188 seat W189+ projection + r888 probe', '# leg4 + r890 sec8 回填窗 succession projection notes all anticipated;', 'honest forward walk hops=1 -> 430_604..432_603, non-rotational', '(430_603+1) machine-checkable -- A-hops-prior-B staircase', 'FORTY-NINTH instance, E36 card);', 'continuation 430_604..430_803 CLEAN on the registered universe', 'but lands INSIDE the W189 A band window -- same-freeze mutual', 'own-wave A window reserved jumps to 432_604 -> 432_604..432_803,', 'own-wave A tail+1 (432_603+1) machine-checkable);', 'W189+ projection (gate-derived r888): A first-clean', '432_604..434_603 CLEAN hops=0 / B first-clean 432_804..433_003', 'registered W189 B band 432_604..432_803 will refuse the naive', 'W190 A window; W190 freezer MUST re-derive on the post-W189', 'NOT a re-pick (R250: W189 bands were never assigned).', '189: {"a": (430_604, 432_603), "b_exit": (432_604, 432_803),', '744de26ef', 'r888 probe', 'r890 sec8', 'r888 pre-seat', '_r888bma', 'MSG-2026-10-08-1815', 'b66117659', '820,928', '411,520', 'FORTY-NINTH', 'ONE HUNDRED-AND-SEVENTY-NINTH']

EN_NEG = ['189: {"batch": "PERPETUAL-N1-W189",', '"prereg": ("research/PERPETUAL_N1_W189_PREREG.md (wave-level frozen "', 'new seed bands only; ONE HUNDRED-AND-SEVENTY-NINTH ENGINE-OWNED WAVE ', 'BY MACHINE-DERIVE (engine_owner rows 178 + candidate), ', 'number law after the REGISTERED W188 row bm-a r888 freeze ', 'b66117659, SINGLE STATE zero seat gap W2..W188 all ', 'registered; W189 finalize landed same-window r827, ledger ', 'head 820,928, merged pool K=411,520; seat published=reserved ', 'MSG-2026-10-08-1815-bma-w189-seat PUSHED to origin 744de26ef ', 'probe receipt (3-item; the W188 finalize product already on origin since r888, not re-shipped; W146 precedent); ', 'at fetch (r888 pre-seat push), zero merge, zero ', 'engine_owner=bm-a, wave 188: ', 'A = FIRST-CLEAN past the registered W188 B band (the ', 'arithmetic continuation 430_404..432_403 is REFUSED at its ', 'own start by the W188 B band 430_404..430_603, exactly as ', 'the W188 seat W189+ projection + r888 probe leg4 + r890 sec8 回填窗 succession ', '430_604..432_603; A base == prior-wave B tail+1 ', 'machine-checkable = A-hops-prior-B staircase FORTY-NINTH ', 'arithmetic continuation 430_604..430_803 is CLEAN on the ', 'registered universe but lands INSIDE the W189 A band ', 'jumps to 432_604, first-clean 432_604..432_803 hops=1, ', 'convergence with the W188 seat W189+ projection + r888 probe leg4 + ', 'r890 sec8 回填窗 succession projection notes re-derived -- all ', 'MANDATORY notes honored (post-W188 universe re-derive + ', 'results/_r888bma_w189_probe_receipt.json; W190+ projection ', 'per this window gate: A first-clean 432_604..434_603 ', 'CLEAN / B first-clean 432_804..433_003 CLEAN -- naive ', 'W189 B band 432_604..432_803 will refuse the naive ', 'W190 A window; W190 freezer MUST re-derive on the ', 'post-W189 universe AND reserve the own-wave A window ', 'staircase card); W1..W188 finalize ALL LANDED (W188 ', 'finalize one-pass bm-a r889, net chain head 820,928, ', 'merged pool K=411,520) -- ZERO in-flight upstream ', '"a_seed_base": 430_604,        # law sec.4 W189 A: 430_604..432_603 (FIRST-CLEAN past the registered W188 B band; arithmetic 430_404..432_403 REFUSED at own start by the W188 B band; hops=1; A-hops-prior-B staircase FORTY-NINTH instance, E36 card; ordinal convergence per r587: W188 sec5.5 prose anticipated forty-ninth, r888 receipt machine-read FORTY-NINTH)', '"b_exit_seed_base": 432_604,   # law sec.4 W189 B: 432_604..432_803 (FIRST-CLEAN past the own-wave A window; arithmetic 430_604..430_803 lands inside own-A, same-freeze mutual exclusion W141 precedent; reserved walk hops=1; B base == own-A tail+1)', '"shard_subdir": "n1_w189", "out_name": "n1_w189_results.json",', 'b66117659', '744de26ef', '820,928', '411,520', 'ONE HUNDRED-AND-SEVENTY-NINTH', 'rows 178', 'r888 probe', '_r888bma', 'MSG-2026-10-08-1815', 'n1w189', 'n1_w189', 'PERPETUAL-N1-W189', 'PERPETUAL_N1_W189', 'FORTY-NINTH', 'bm-a r888 freeze', '432_604, first-clean']

MAT_NEG = ['# --- W189 materializer face (r890 bm-a freeze, own-series law', '#     one-hundred-fifth owned per machine-derive (engine_owner==bm-a', '#     rows 104 + candidate); wave 188 = first free number after', '#     the REGISTERED W188 row (bm-a r888 freeze b66117659) --', '#     SINGLE STATE zero seat gap (W2..W188 all registered). Seat', '#     published=reserved MSG-2026-10-08-1815-bma-w189-seat pushed', '#     to origin 744de26ef BEFORE this freeze, r565 law (payload', '#     the W188 finalize product already on origin since r888, not', '#     at fetch (r888 pre-seat push), zero merge, zero', '#     --no-verify; self-ack inbox->processed archive ALREADY LANDED\r\n    #     pre-freeze -- bm-a r889-window archive move (the W189 seat\r\n    #     MSG sits in fleet/inbox/processed/ at freeze time, honest\r\n    #     archived).', '#     ONE HUNDRED-AND-SEVENTY-NINTH engine wave BY', '#     MACHINE-DERIVE (engine_owner rows 178 + candidate; gate', '#     W1..W188 finalize ALL LANDED (net chain head 820,928,', '#     K=411,520 merged pool; W188 finalize one-pass bm-a r889)', '#     always on. ADMIT receipt results/_r888bma_w189_probe_receipt.json;', '#     banned gate ADMIT 0; not a re-pick (R250: W189 bands were', '    _set_wave(189)', 'assert WAVE_CONFIGS[188]["a_seed_base"] == pf.N1_BANDS[188]["a"][0], \\', '"W189 A band drift vs law mirror"', 'assert WAVE_CONFIGS[188]["b_exit_seed_base"] == \\', 'pf.N1_BANDS[188]["b_exit"][0], "W189 B band drift vs law mirror"', 'assert WAVE_CONFIGS[188].get("engine_owner") == \\', 'pf.N1_BANDS[188].get("engine_owner") == "bm-a", \\', '"W189 engine_owner drift (law mirror parity)"', 'w188_a = {A_SEED_BASE + j for j in range(A_N)}', 'w188_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}', 'assert not (w188_a & w188_b), "W189 A/B band overlap"', 'assert not (w188_a & reg_ints) and not (w188_b & reg_ints), \\', '"W189 hits SEED_REGISTRY"', 'for nm, band in (("A", w188_a), ("B", w188_b)):', 'f"W189 {nm} hits v1"', 'f"W189 {nm} hits W1"', 'f"W189 {nm} hits probe seeds"', '"registered W187 row parity drift (r307; bm-a r882)"\r\n        assert pf.N1_BANDS[187] == {"a": (426_204, 428_203),\r\n                                    "b_exit": (428_204, 428_403),\r\n                                    "engine_owner": "bm-a"}, \\\r\n            "registered W188 row parity drift (r307; bm-a r888)"', '# prior-wave disjointness W2..W188 (single state: all', 'for wprev in sorted(w for w in WAVE_CONFIGS if w < 189):', 'assert not (w188_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j', 'for j in range(A_N)}), f"W189 A hits W{wprev}"', 'assert not (w188_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j', 'for j in range(B_N)}), f"W189 B hits W{wprev}"', 'n3r1_used188 = set(range(70_000, 70_006))', 'assert not (w188_a & n3r1_used188) and not (w188_b & n3r1_used188), \\', '"W189 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"', 'assert not (w188_a & lfc_actual12) and not (w188_b & lfc_actual12), \\', '"W189 bands must clear the lfc actual draw range"', 'assert not (w188_a & options_actual12) and \\', 'not (w188_b & options_actual12), \\', '"W189 bands must clear the options_wave2 actual draw range"', '# band facts (law sec.4 W189 row, r795): A = FIRST-CLEAN past', '# the registered W188 B band (the arithmetic continuation', '# 430_404..432_403 is REFUSED at its own start by the W188', '# B band 430_404..430_603, exactly as the W188 seat W189+ projection +', '# r888 probe leg4 + r890 sec8 回填窗 succession projection notes', '# 430_604..432_603; A base == prior-wave B tail+1 (430_603+1)', '# machine-checkable -- A-hops-prior-B staircase FORTY-NINTH', '# continuation 430_604..430_803 is CLEAN on the registered', '# universe but lands INSIDE the W189 A band window --', '# 432_604 and lands 432_604..432_803, hops=1, non-rotational', '# (432_603+1) machine-checkable; cross-window convergence', '# with the W188 seat W189+ projection + r888 probe leg4 + r890 sec8', '# honored (post-W188 universe re-derive + own-wave A', '# reservation when deriving B); seat MSG-1815 tail,', 'assert WAVE_CONFIGS[189]["a_seed_base"] == 430_604 == 430_603 + 1, (', '"W189 A must be the first-clean window past the registered "', '"W188 B band tail 430_603+1 (arithmetic continuation "', '"430_404..432_403 REFUSED at its own start by the W188 B "', '"band 430_404..430_603, exactly as the W188 seat W189+ projection + "', '"r888 probe leg4 + r890 sec8 回填窗 succession projection notes "', '"staircase FORTY-NINTH instance, E36 card)"', 'arith_a188 = set(range(430_604, 432_604))', 'assert not (arith_a188 & reg_ints), \\', '"W189 A window must be CLEAN (first-clean ADMIT face past prior-wave B)"', 'assert WAVE_CONFIGS[189]["b_exit_seed_base"] == 432_604 == 432_603 + 1, (', '"W189 B must be the first-clean window past the own-wave A "', '"band tail 432_603+1 (arithmetic continuation "', '"430_604..430_803 CLEAN on the registered universe but "', '"lands INSIDE the W189 A band window; same-freeze mutual "', '"own-wave A window reserved jumps to 432_604, first-clean "', 'arith_b188 = set(range(432_604, 432_804))', 'assert not (arith_b188 & reg_ints), \\', '"W189 B window must be CLEAN (first-clean ADMIT face past own-wave A)"', 'assert not (arith_b188 & arith_a188), \\', '"W189 A/B same-freeze mutual exclusion (B hops past own A)"', 'assert _entry_shard_of(0, 12) == ("PERPETUAL-N1-W189-SHARD-0",', '"n1w189-0of12"), "W189 entry identity"', 'assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W189-SHARD-11",', '"n1w189-11of12")', 'assert SHARD_DIR.endswith("n1_w189") and OUT.endswith(', '"n1_w189_results.json"), "W189 path drift"', 'f"W189 shard dir collides with W{wprev}"', '# W189 finalize cumulative deps: W17..W188 outputs ALL PRESENT', '# (landed net chain head 820,928 = W188 bm-a r889 one-pass --', 'for _depw in range(17, 189):', 'f"W189 finalize cumulative dep (W{_depw} output) missing"', '# registered wave below 189 composes; wave 15 excluded by', '# design; SINGLE STATE (W2..W188 all registered -- no', 'assert sorted(w for w in WAVE_CONFIGS if w < 189) == \\', '[w for w in range(16, 189)], \\', '"W189 prior-wave set must derive from registry keys (no 15; "', '"W2..W188 registered single state)"', 'PATHS.root, "research", "PERPETUAL_N1_W189_PREREG.md")), \\', '"W189 per-wave prereg missing (materializer requirement)"', 'w188_', 'arith_a188', 'arith_b188', 'n3r1_used188', 'r888 probe', 'r888 pre-seat', 'b66117659', 'ONE HUNDRED-AND-SEVENTY-NINTH', 'one-hundred-fifth', 'rows 178', 'rows 104 ', 'range(17, 189)', 'range(16, 189)', 'PERPETUAL_N1_W189', 'PERPETUAL-N1-W189', 'MSG-1815', '_r888bma', 'bm-a r889-window', 'n1w189', 'n1_w189', '820,928', '411,520']

CL_NEG = ['"+ W189 materializer face [same guard set, dep=W17..W188 ', '"outputs ALL PRESENT (landed net chain head 820,928 = "', '"W188 bm-a r889 one-pass, K=411,520 merged pool; ZERO "', '"in-flight upstream seats), ONE HUNDRED-AND-SEVENTY-NINTH "', '"ENGINE-OWNED WAVE BY MACHINE-DERIVE (engine_owner rows 178 "', "+ candidate) bm-a's one-hundred-fifth owned claim per ", '"machine-derive (engine_owner==bm-a rows 104 + candidate), "', '"A=FIRST-CLEAN past the registered W188 B band (staircase "', '"FORTY-NINTH instance, E36 card, hops=1) + B=FIRST-CLEAN past the "', '"results/_r888bma_w189_probe_receipt.json, law sec.4 W189 row, "', '"r890 bm-a] "', '820,928', '411,520', 'ONE HUNDRED-AND-SEVENTY-NINTH', 'one-hundred-fifth', 'rows 178', 'rows 104 ', 'FORTY-NINTH', '_r888bma', 'r890 bm-a] ']

blk190 = vmap(pfblk, PF_PAIRS, PF_NEG, "pf")
entry190 = IND23 + vmap(entry, EN_PAIRS, EN_NEG, "entry")
mat190 = "    " + vmap(mat, MAT_PAIRS, MAT_NEG, "mat")
claim190 = IND10 + vmap(claim, CL_PAIRS, CL_NEG, "claim")

# ---- apply insertions (in-memory) ---------------------------------------
pfsrc = io.open(PF, encoding="utf-8", newline="").read()
n1src = io.open(N1, encoding="utf-8", newline="").read()

# pf: insert W190 block after the W189 row (last registered), before the
# dict close -- r560 insert-after-last-registered-row + post-anchor gate
seg = EO + NL + "}"
check(pfsrc.count(seg) == 1, "pf row-close segment not unique")
pfnew = pfsrc.replace(seg, EO + NL + blk190 + NL + "}", 1)

# n1 entry: after the W189 entry, before the WAVE_CONFIGS close
seg = EO + NL + IND23 + "}"
check(n1src.count(seg) == 1, "n1 entry-close segment not unique")
n1new = n1src.replace(seg, EO + NL + entry190 + NL + IND23 + "}", 1)

# n1 mat: insert the W190 block before the T-141 s2 lane face header
seg = "    # --- T-141 s2 lane face"
check(n1new.count(seg) == 1, "n1 T-141 mat anchor not unique")
n1new = n1new.replace(seg, mat190 + NL + seg, 1)

# n1 claim: insert the W190 attribution after the W189 claim tail line
# (r581 law: anchor = tail single-line literal + post-anchor guard)
seg = '"r890 bm-a] "' + NL + IND10 + '"+ T-141 s2 "'
check(n1new.count(seg) == 1, "n1 claim anchor not unique")
n1new = n1new.replace(seg, '"r890 bm-a] "' + NL + claim190 + NL + IND10 +
                      '"+ T-141 s2 "', 1)

# ---- gates (r780/r781/r560/r815 lineage) --------------------------------
ast.parse(pfnew)
ast.parse(n1new)
print("AST gate: both files parse OK")

# W190 presence + W189 anti-vanish (r560 law)
checks = [
    (pfnew, '190: {"a": (432_804, 434_803), "b_exit": (434_804, 435_003),', 1),
    (pfnew, '189: {"a": (430_604, 432_603), "b_exit": (432_604, 432_803),', 1),
    (pfnew, "# W190 (bm-a r892 freeze", 1),
    (pfnew, "# W189 (bm-a r890 freeze", 1),
    (n1new, '190: {"batch": "PERPETUAL-N1-W190",', 1),
    (n1new, '189: {"batch": "PERPETUAL-N1-W189",', 1),
    (n1new, "# --- W190 materializer face", 1),
    (n1new, "# --- W189 materializer face", 1),
    (n1new, '"r892 bm-a] "', 1),
    (n1new, '"r890 bm-a] "', 1),
    (n1new, '"a_seed_base": 432_804,', 1),
    (n1new, '"b_exit_seed_base": 434_804,', 1),
    (n1new, "n1_w190", 4),
    (n1new, "PERPETUAL_N1_W190_PREREG.md", 2),
]
for src, needle, cnt in checks:
    got = src.count(needle)
    check(got == cnt, "post-edit needle %r count %d != %d" % (needle[:50], got, cnt))

# W191+ projection prose present in the new W190 blocks (probe leg4
# verbatim; r819 post-edit assert bloodline + r776 fragment-needle law;
# pf header = self-wave W190+ per r845 precedent, n1 fragment =
# next-wave W191+)
check("# W190+ projection (gate-derived r891)" in pfnew,
      "pf W190+ projection head missing")
check('probe_receipt.json; W191+ projection "' in n1new,
      "n1 W191+ projection head fragment missing")
check("# 434_804..436_803 CLEAN hops=0 / B first-clean 435_004..435_203" in pfnew,
      "pf W191p prose missing")
check("W191 A window; W191 freezer MUST re-derive on the post-W190" in pfnew,
      "pf W191 freezer prose missing")
check('"W191 A window; W191 freezer MUST re-derive on the "' in n1new,
      "n1 W191 freezer fragment missing")
check('"W190 B band 434_804..435_003 will refuse the naive "' in n1new,
      "n1 W190-band refuse fragment missing")

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
check('190: {"a": (432_804' not in pf_o2, "write-time: origin pf carries W190")
check('190: {"batch"' not in n1_o2, "write-time: origin n1 carries W190")
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
