# -*- coding: utf-8 -*-
"""r869 bm-a W183 freeze edits: four insertions (pf N1_BANDS[183] row +
n1 WAVE_CONFIGS[183] entry + n1 W183 materializer block + n1 W183
PASS-claim attribution). DRY flag: --dry = zero-write simulation
(r781 verify-separation law + r811/r822/r826/r830/r834/r843/r845/r849/
r852/r863/r867 dry-run precedent: full stale+prose+AST asserts in memory
BEFORE any write).

Bloodline: r819/r822/r826/r830/r834/r843/r845/r849/r852/r863/r867
freeze-edits machinery (r773 pit law freeze-editor compliance + r776
fragment-needle law + r781 verify-separation law), W183 facts
live-registry-driven (built by _r869bma_w183_freeze_buildgen.py: old
sides = the PHYSICAL W182 face fragments probed to dumps this window,
new sides = the S82f W183 fact map, counts verified pre-emission):
  - pre-seat probe results/_r868bma_w183_probe_receipt.json rc0 ADMIT
    (naive A 417_204..419_203 refused at its own start by the
    registered W182 B band 417_204..417_403; honest forward walk
    1 hop lands A 417_404..419_403 staircase FORTY-THIRD instance E36
    -- receipt A_semantics machine-cites the W182 seat MSG leg4 + r865
    probe leg4 anticipated + MANDATED this re-derive (W182 sec5.5
    prose anticipated 43rd -- projection and receipt ordinals MATCH,
    no divergence this wave); B 419_404..419_603 own-A mutual exclusion
    hops=1, naive 417_404..417_603);
  - face probe results/_r869bma_w183_face_probe_receipt.json rc0 (all
    four W182 faces dumped + needle counts; this TOK is built from the
    PHYSICAL probe-dumped shapes, r776 law);
  - seat MSG-2026-10-08-0741-bma-w183-seat published on origin at
    ccd18034e (r868 pre-seat push, path-derived TRUE sha per r812
    precedent); r565 law: on origin BEFORE this freeze commit;
    self-ack archive ALREADY LANDED pre-freeze -- bm-c r741-window
    self-ack move (cross-machine consume, a79ceeb9b); the W183 seat
    MSG sits in fleet/inbox/processed/ at freeze time, honest archived;
  - per-wave prereg research/PERPETUAL_N1_W183_PREREG.md built this
    window (r869 buildgen r867-bloodline; banned gate ADMIT 0
    verified at prereg build; prereg-freeze push this window);
  - W182 freeze registered sha machine-derived = 385dbafd8 (git log
    origin/main --grep "W182 FREEZE"); W182 finalize landed r868
    one-pass same-window: ledger head 806,718, merged pool K=398,320
    (n1_w182_results.json machine-read); W182 sec7/sec8 settle
    backfill landed the r868 SAME window (r864 lesson welded into
    process -- no heal window needed, honest);
  - lineage constants disclosed (r795/r845/r849/r852/r863/r867
    precedent, passed through): (a) the "wave N-1 = first free number"
    mat-header label rolls forward with its off-by-one quirk (since
    W165 r795); (b) "law sec.4 W183 row, r795" band-facts template
    stamp keeps its r795; (c) "single-window derive (r812 merged the
    gate legs INTO the pre-seat probe...)" stays (historical merge
    citation); (d) the bm-a-owned ordinal word rolls ninety-eighth ->
    ninety-ninth (rows 98 + candidate = 99th owned per probe leg0);
    (e) mat parity-chain rows W138..W181 keep their historical stamps
    and tuples; the W182 row (the current registered tail) is APPENDED
    with its frozen values (415_204, 417_203)/(417_204, 417_403);
    (f) the "W182 finalize landed same-window r827" citation rolls its
    wave-word with the stale r827 session stamp riding (off-by-one
    wave-word + stale-session lineage quirk inherited; head/K values
    roll machine-correct to 806,718/398,320 this window).

r773 pit law compliance:
  (1) full string-face inventory empirically probed BEFORE TOK
      (_r869bma_w183_face_probe.py -- four face dumps + needle-count
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
      (r530/r687: fetch + origin carries no W183 registration before
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
probe = json.load(open(r"results\_r868bma_w183_probe_receipt.json",
                       encoding="utf-8"))
check(probe["verdict"] == "ADMIT", "pre-seat probe not ADMIT")
check(probe["bands"] == {"A": "417404_419403", "B": "419404_419603"},
      "probe band shape mismatch")
check(probe["legs"]["leg1"]["A"] == [417404, 419403], "A band mismatch")
check(probe["legs"]["leg1"]["B"] == [419404, 419603], "B band mismatch")
check(probe["legs"]["leg1"]["hops_A"] == 1 and probe["legs"]["leg1"]["hops_B"] == 1,
      "hops mismatch")
check(probe["legs"]["leg0"]["rows"] == 180 and probe["legs"]["leg0"]["tail"] == "W182",
      "leg0 registry tail mismatch")
check(probe["legs"]["leg0"]["ordinal"] == 173 and probe["legs"]["leg0"]["bma_ordinal"] == 99,
      "leg0 ordinal mismatch")
check(probe["legs"]["leg2"]["conflicts"] == 0, "leg2 conflicts nonzero")
check(probe["legs"]["leg3"]["origin_vacancy"] is True, "leg3 origin not vacant")
check(probe["legs"]["leg4"]["W184p_A"] == "419404..421403"
      and probe["legs"]["leg4"]["W184p_B"] == "419604..419803",
      "leg4 W184+ projection mismatch")

# origin anti-collision pre-check (r511 tail-lock / r687 write-time gate)
subprocess.run(["git", "fetch", "origin"], capture_output=True)
pf_o = subprocess.run(["git", "show", "origin/main:" + PF],
                      capture_output=True).stdout.decode("utf-8", "replace")
n1_o = subprocess.run(["git", "show", "origin/main:" + N1],
                      capture_output=True).stdout.decode("utf-8", "replace")
check('183: {"a": (417_404' not in pf_o, "origin pf already carries W183 row")
check("W183 (bm-a r869 freeze" not in pf_o, "origin pf carries W183 block")
check('183: {"batch"' not in n1_o, "origin n1 already carries W183 entry")
check("# --- W183 materializer face" not in n1_o, "origin n1 carries W183 mat")
check('"r869 bm-a] "' not in n1_o, "origin n1 carries W183 claim")

# machine-derived shas (r587 / r812 path-derived precedent)
seat_sha = subprocess.run(
    ["git", "log", "origin/main", "--format=%h", "-n", "1", "--diff-filter=A",
     "--", "fleet/inbox/MSG-2026-10-08-0741-bma-w183-seat.md"],
    capture_output=True).stdout.decode().strip()
check(seat_sha == "ccd18034e", "seat sha path-derived mismatch: " + seat_sha)
check(os.path.exists(os.path.join(
    "fleet", "inbox", "processed", "MSG-2026-10-08-0741-bma-w183-seat.md")),
    "seat MSG not in processed/ at freeze time (self-ack archive)")
w182_freeze_sha = subprocess.run(
    ["git", "log", "origin/main", "--format=%h", "-n", "1", "--grep=W182 FREEZE"],
    capture_output=True).stdout.decode().strip()
check(w182_freeze_sha == "385dbafd8", "W182 freeze sha mismatch: " + w182_freeze_sha)

# ---- live-registry parity pre-check (edit-gate: never edit a drifted file)
sys.path.insert(0, "scripts")
import perpetual_faces as pfmod  # noqa: E402
check(len(pfmod.N1_BANDS) == 180, "live N1_BANDS row count drift: %d" % len(pfmod.N1_BANDS))
check(pfmod.N1_BANDS[182] == {"a": (415_204, 417_203),
                              "b_exit": (417_204, 417_403),
                              "engine_owner": "bm-a"}, "live W182 row drift")
check(183 not in pfmod.N1_BANDS, "live N1_BANDS already has 183")
check(os.path.exists(os.path.join("research", "PERPETUAL_N1_W183_PREREG.md")),
      "W183 per-wave prereg missing (materializer gate)")
prereg_o = subprocess.run(["git", "show", "origin/main:research/PERPETUAL_N1_W183_PREREG.md"],
                          capture_output=True)
check(prereg_o.returncode == 0, "W183 prereg absent on origin")

# ---- physical face dumps (r776 law) -----------------------------------
pfblk = io.open(r"results\_r869bma_w183_probe_pf_block.txt", encoding="utf-8",
                newline="").read()
entry = io.open(r"results\_r869bma_w183_probe_n1_entry.txt", encoding="utf-8",
                newline="").read()
mat = io.open(r"results\_r869bma_w183_probe_n1_mat.txt", encoding="utf-8",
              newline="").read()
claim = io.open(r"results\_r869bma_w183_probe_n1_claim.txt", encoding="utf-8",
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
    ('    # W182 (bm-a r867 freeze, seat MSG-2026-10-08-0603-bma-w182-seat', '    # W183 (bm-a r869 freeze, seat MSG-2026-10-08-0741-bma-w183-seat', 1),
    ('pushed to origin df062c5c1 pre-freeze r565 law (r865 pre-seat', 'pushed to origin ccd18034e pre-freeze r565 law (r868 pre-seat', 1),
    ('(3-item; the W181 finalize product already on origin since r864,', '(3-item; the W182 finalize product already on origin since r868,', 1),
    ('# = direct fast-forward behind-0 at fetch (r865 pre-seat', '# = direct fast-forward behind-0 at fetch (r868 pre-seat', 1),
    ('# push), zero merge, zero --no-verify; self-ack archive ALREADY\r\n    # LANDED pre-freeze -- bm-c r737-window self-ack move (the W182\r\n    # seat MSG sits in fleet/inbox/processed/ at freeze time, honest\r\n    # archived);', '# push), zero merge, zero --no-verify; self-ack archive ALREADY\r\n    # LANDED pre-freeze -- bm-c r741-window self-ack move (the W183\r\n    # seat MSG sits in fleet/inbox/processed/ at freeze time, honest\r\n    # archived);', 1),
    ('band gate ADMIT results/_r865bma_w182_probe_receipt.json: A = FIRST-CLEAN', 'band gate ADMIT results/_r868bma_w183_probe_receipt.json: A = FIRST-CLEAN', 1),
    ('past the registered W181 B band (arithmetic continuation', 'past the registered W182 B band (arithmetic continuation', 1),
    ('415_004..417_003 REFUSED at its own start by the W181 B band', '417_204..419_203 REFUSED at its own start by the W182 B band', 1),
    ('415_004..415_203, exactly as the W181 seat W182+ projection + r862 probe', '417_204..417_403, exactly as the W182 seat W183+ projection + r865 probe', 1),
    ('# leg4 + r867 sec8 heal succession projection notes all anticipated;', '# leg4 + r868 sec8 same-window succession projection notes all anticipated;', 1),
    ('honest forward walk hops=1 -> 415_204..417_203, non-rotational', 'honest forward walk hops=1 -> 417_404..419_403, non-rotational', 1),
    ('(415_203+1) machine-checkable -- A-hops-prior-B staircase', '(417_403+1) machine-checkable -- A-hops-prior-B staircase', 1),
    ('FORTY-SECOND instance, E36 card);', 'FORTY-THIRD instance, E36 card);', 1),
    ('continuation 415_204..415_403 CLEAN on the registered universe', 'continuation 417_404..417_603 CLEAN on the registered universe', 1),
    ('but lands INSIDE the W182 A band window -- same-freeze mutual', 'but lands INSIDE the W183 A band window -- same-freeze mutual', 1),
    ('own-wave A window reserved jumps to 417_204 -> 417_204..417_403,', 'own-wave A window reserved jumps to 419_404 -> 419_404..419_603,', 1),
    ('own-wave A tail+1 (417_203+1) machine-checkable);', 'own-wave A tail+1 (419_403+1) machine-checkable);', 1),
    ('W182+ projection (gate-derived r865): A first-clean', 'W183+ projection (gate-derived r868): A first-clean', 1),
    ('417_204..419_203 CLEAN hops=0 / B first-clean 417_404..417_603', '419_404..421_403 CLEAN hops=0 / B first-clean 419_604..419_803', 1),
    ('registered W182 B band 417_204..417_403 will refuse the naive', 'registered W183 B band 419_404..419_603 will refuse the naive', 1),
    ('W183 A window; W183 freezer MUST re-derive on the post-W182', 'W184 A window; W184 freezer MUST re-derive on the post-W183', 1),
    ('NOT a re-pick (R250: W182 bands were never assigned).', 'NOT a re-pick (R250: W183 bands were never assigned).', 1),
    ('182: {"a": (415_204, 417_203), "b_exit": (417_204, 417_403),', '183: {"a": (417_404, 419_403), "b_exit": (419_404, 419_603),', 1),
]

EN_PAIRS = [
    ('182: {"batch": "PERPETUAL-N1-W182",', '183: {"batch": "PERPETUAL-N1-W183",', 1),
    ('"prereg": ("research/PERPETUAL_N1_W182_PREREG.md (wave-level frozen "', '"prereg": ("research/PERPETUAL_N1_W183_PREREG.md (wave-level frozen "', 1),
    ('new seed bands only; ONE HUNDRED-AND-SEVENTY-SECOND ENGINE-OWNED WAVE ', 'new seed bands only; ONE HUNDRED-AND-SEVENTY-THIRD ENGINE-OWNED WAVE ', 1),
    ('BY MACHINE-DERIVE (engine_owner rows 171 + candidate), ', 'BY MACHINE-DERIVE (engine_owner rows 172 + candidate), ', 1),
    ('number law after the REGISTERED W181 row bm-a r863 freeze ', 'number law after the REGISTERED W182 row bm-a r867 freeze ', 1),
    ('de699e8cd, SINGLE STATE zero seat gap W2..W181 all ', '385dbafd8, SINGLE STATE zero seat gap W2..W182 all ', 1),
    ('registered; W182 finalize landed same-window r827, ledger ', 'registered; W183 finalize landed same-window r827, ledger ', 1),
    ('head 804,518, merged pool K=396,120; seat published=reserved ', 'head 806,718, merged pool K=398,320; seat published=reserved ', 1),
    ('MSG-2026-10-08-0603-bma-w182-seat PUSHED to origin df062c5c1 ', 'MSG-2026-10-08-0741-bma-w183-seat PUSHED to origin ccd18034e ', 1),
    ('probe receipt (3-item; the W181 finalize product already on origin since r864, not re-shipped; W146 precedent); ', 'probe receipt (3-item; the W182 finalize product already on origin since r868, not re-shipped; W146 precedent); ', 1),
    ('at fetch (r865 pre-seat push), zero merge, zero ', 'at fetch (r868 pre-seat push), zero merge, zero ', 1),
    ('engine_owner=bm-a, wave 181: ', 'engine_owner=bm-a, wave 182: ', 1),
    ('A = FIRST-CLEAN past the registered W181 B band (the ', 'A = FIRST-CLEAN past the registered W182 B band (the ', 1),
    ('arithmetic continuation 415_004..417_003 is REFUSED at its ', 'arithmetic continuation 417_204..419_203 is REFUSED at its ', 1),
    ('own start by the W181 B band 415_004..415_203, exactly as ', 'own start by the W182 B band 417_204..417_403, exactly as ', 1),
    ('the W181 seat W182+ projection + r862 probe leg4 + r867 sec8 heal succession ', 'the W182 seat W183+ projection + r865 probe leg4 + r868 sec8 same-window succession ', 1),
    ('projection notes anticipated; honest forward walk hops=1 -> ', 'projection notes anticipated; honest forward walk hops=1 -> ', 1),
    ('415_204..417_203; A base == prior-wave B tail+1 ', '417_404..419_403; A base == prior-wave B tail+1 ', 1),
    ('machine-checkable = A-hops-prior-B staircase FORTY-SECOND ', 'machine-checkable = A-hops-prior-B staircase FORTY-THIRD ', 1),
    ('arithmetic continuation 415_204..415_403 is CLEAN on the ', 'arithmetic continuation 417_404..417_603 is CLEAN on the ', 1),
    ('registered universe but lands INSIDE the W182 A band ', 'registered universe but lands INSIDE the W183 A band ', 1),
    ('jumps to 417_204, first-clean 417_204..417_403 hops=1, ', 'jumps to 419_404, first-clean 419_404..419_603 hops=1, ', 1),
    ('convergence with the W181 seat W182+ projection + r862 probe leg4 + ', 'convergence with the W182 seat W183+ projection + r865 probe leg4 + ', 1),
    ('r867 sec8 heal succession projection notes re-derived -- all ', 'r868 sec8 same-window succession projection notes re-derived -- all ', 1),
    ('MANDATORY notes honored (post-W181 universe re-derive + ', 'MANDATORY notes honored (post-W182 universe re-derive + ', 1),
    ('results/_r865bma_w182_probe_receipt.json; W183+ projection ', 'results/_r868bma_w183_probe_receipt.json; W184+ projection ', 1),
    ('per this window gate: A first-clean 417_204..419_203 ', 'per this window gate: A first-clean 419_404..421_403 ', 1),
    ('CLEAN / B first-clean 417_404..417_603 CLEAN -- naive ', 'CLEAN / B first-clean 419_604..419_803 CLEAN -- naive ', 1),
    ('W182 B band 417_204..417_403 will refuse the naive ', 'W183 B band 419_404..419_603 will refuse the naive ', 1),
    ('W183 A window; W183 freezer MUST re-derive on the ', 'W184 A window; W184 freezer MUST re-derive on the ', 1),
    ('post-W182 universe AND reserve the own-wave A window ', 'post-W183 universe AND reserve the own-wave A window ', 1),
    ('staircase card); W1..W181 finalize ALL LANDED (W181 ', 'staircase card); W1..W182 finalize ALL LANDED (W182 ', 1),
    ('finalize one-pass bm-a r864, net chain head 804,518, ', 'finalize one-pass bm-a r868, net chain head 806,718, ', 1),
    ('merged pool K=396,120) -- ZERO in-flight upstream ', 'merged pool K=398,320) -- ZERO in-flight upstream ', 1),
    ('"a_seed_base": 415_204,        # law sec.4 W182 A: 415_204..417_203 (FIRST-CLEAN past the registered W181 B band; arithmetic 415_004..417_003 REFUSED at own start by the W181 B band; hops=1; A-hops-prior-B staircase FORTY-SECOND instance, E36 card; ordinal convergence per r587: W181 sec5.5 prose anticipated forty-second, r865 receipt machine-read FORTY-SECOND)', '"a_seed_base": 417_404,        # law sec.4 W183 A: 417_404..419_403 (FIRST-CLEAN past the registered W182 B band; arithmetic 417_204..419_203 REFUSED at own start by the W182 B band; hops=1; A-hops-prior-B staircase FORTY-THIRD instance, E36 card; ordinal convergence per r587: W182 sec5.5 prose anticipated forty-third, r868 receipt machine-read FORTY-THIRD)', 1),
    ('"b_exit_seed_base": 417_204,   # law sec.4 W182 B: 417_204..417_403 (FIRST-CLEAN past the own-wave A window; arithmetic 415_204..415_403 lands inside own-A, same-freeze mutual exclusion W141 precedent; reserved walk hops=1; B base == own-A tail+1)', '"b_exit_seed_base": 419_404,   # law sec.4 W183 B: 419_404..419_603 (FIRST-CLEAN past the own-wave A window; arithmetic 417_404..417_603 lands inside own-A, same-freeze mutual exclusion W141 precedent; reserved walk hops=1; B base == own-A tail+1)', 1),
    ('"shard_subdir": "n1_w182", "out_name": "n1_w182_results.json",', '"shard_subdir": "n1_w183", "out_name": "n1_w183_results.json",', 1),
]

MAT_PAIRS = [
    ('# --- W182 materializer face (r867 bm-a freeze, own-series law', '# --- W183 materializer face (r869 bm-a freeze, own-series law', 1),
    ('#     ninety-eighth owned per machine-derive (engine_owner==bm-a', '#     ninety-ninth owned per machine-derive (engine_owner==bm-a', 1),
    ('#     rows 97 + candidate); wave 181 = first free number after', '#     rows 98 + candidate); wave 182 = first free number after', 1),
    ('#     the REGISTERED W181 row (bm-a r863 freeze de699e8cd) --', '#     the REGISTERED W182 row (bm-a r867 freeze 385dbafd8) --', 1),
    ('#     SINGLE STATE zero seat gap (W2..W181 all registered). Seat', '#     SINGLE STATE zero seat gap (W2..W182 all registered). Seat', 1),
    ('#     published=reserved MSG-2026-10-08-0603-bma-w182-seat pushed', '#     published=reserved MSG-2026-10-08-0741-bma-w183-seat pushed', 1),
    ('#     to origin df062c5c1 BEFORE this freeze, r565 law (payload', '#     to origin ccd18034e BEFORE this freeze, r565 law (payload', 1),
    ('#     the W181 finalize product already on origin since r864, not', '#     the W182 finalize product already on origin since r868, not', 1),
    ('#     at fetch (r865 pre-seat push), zero merge, zero', '#     at fetch (r868 pre-seat push), zero merge, zero', 1),
    ('#     --no-verify; self-ack inbox->processed archive ALREADY LANDED\r\n    #     pre-freeze -- bm-c r737-window self-ack move (the W182 seat\r\n    #     MSG sits in fleet/inbox/processed/ at freeze time, honest\r\n    #     archived).', '#     --no-verify; self-ack inbox->processed archive ALREADY LANDED\r\n    #     pre-freeze -- bm-c r741-window self-ack move (the W183 seat\r\n    #     MSG sits in fleet/inbox/processed/ at freeze time, honest\r\n    #     archived).', 1),
    ('#     ONE HUNDRED-AND-SEVENTY-SECOND engine wave BY', '#     ONE HUNDRED-AND-SEVENTY-THIRD engine wave BY', 1),
    ('#     MACHINE-DERIVE (engine_owner rows 171 + candidate; gate', '#     MACHINE-DERIVE (engine_owner rows 172 + candidate; gate', 1),
    ('#     W1..W181 finalize ALL LANDED (net chain head 804,518,', '#     W1..W182 finalize ALL LANDED (net chain head 806,718,', 1),
    ('#     K=396,120 merged pool; W181 finalize one-pass bm-a r864)', '#     K=398,320 merged pool; W182 finalize one-pass bm-a r868)', 1),
    ('#     always on. ADMIT receipt results/_r865bma_w182_probe_receipt.json;', '#     always on. ADMIT receipt results/_r868bma_w183_probe_receipt.json;', 1),
    ('#     banned gate ADMIT 0; not a re-pick (R250: W182 bands were', '#     banned gate ADMIT 0; not a re-pick (R250: W183 bands were', 1),
    ('    _set_wave(182)', '    _set_wave(183)', 1),
    ('assert WAVE_CONFIGS[181]["a_seed_base"] == pf.N1_BANDS[181]["a"][0], \\', 'assert WAVE_CONFIGS[182]["a_seed_base"] == pf.N1_BANDS[182]["a"][0], \\', 1),
    ('"W182 A band drift vs law mirror"', '"W183 A band drift vs law mirror"', 1),
    ('assert WAVE_CONFIGS[181]["b_exit_seed_base"] == \\', 'assert WAVE_CONFIGS[182]["b_exit_seed_base"] == \\', 1),
    ('pf.N1_BANDS[181]["b_exit"][0], "W182 B band drift vs law mirror"', 'pf.N1_BANDS[182]["b_exit"][0], "W183 B band drift vs law mirror"', 1),
    ('assert WAVE_CONFIGS[181].get("engine_owner") == \\', 'assert WAVE_CONFIGS[182].get("engine_owner") == \\', 1),
    ('pf.N1_BANDS[181].get("engine_owner") == "bm-a", \\', 'pf.N1_BANDS[182].get("engine_owner") == "bm-a", \\', 1),
    ('"W182 engine_owner drift (law mirror parity)"', '"W183 engine_owner drift (law mirror parity)"', 1),
    ('w181_a = {A_SEED_BASE + j for j in range(A_N)}', 'w182_a = {A_SEED_BASE + j for j in range(A_N)}', 1),
    ('w181_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}', 'w182_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}', 1),
    ('assert not (w181_a & w181_b), "W182 A/B band overlap"', 'assert not (w182_a & w182_b), "W183 A/B band overlap"', 1),
    ('assert not (w181_a & reg_ints) and not (w181_b & reg_ints), \\', 'assert not (w182_a & reg_ints) and not (w182_b & reg_ints), \\', 1),
    ('"W182 hits SEED_REGISTRY"', '"W183 hits SEED_REGISTRY"', 1),
    ('for nm, band in (("A", w181_a), ("B", w181_b)):', 'for nm, band in (("A", w182_a), ("B", w182_b)):', 1),
    ('f"W182 {nm} hits v1"', 'f"W183 {nm} hits v1"', 1),
    ('f"W182 {nm} hits W1"', 'f"W183 {nm} hits W1"', 1),
    ('f"W182 {nm} hits probe seeds"', 'f"W183 {nm} hits probe seeds"', 1),
    ('"registered W181 row parity drift (r307; bm-a r863)"', '"registered W181 row parity drift (r307; bm-a r863)"\r\n        assert pf.N1_BANDS[182] == {"a": (415_204, 417_203),\r\n                                    "b_exit": (417_204, 417_403),\r\n                                    "engine_owner": "bm-a"}, \\\r\n            "registered W182 row parity drift (r307; bm-a r867)"', 1),
    ('# prior-wave disjointness W2..W181 (single state: all', '# prior-wave disjointness W2..W182 (single state: all', 1),
    ('for wprev in sorted(w for w in WAVE_CONFIGS if w < 182):', 'for wprev in sorted(w for w in WAVE_CONFIGS if w < 183):', 2),
    ('assert not (w181_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j', 'assert not (w182_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j', 1),
    ('for j in range(A_N)}), f"W182 A hits W{wprev}"', 'for j in range(A_N)}), f"W183 A hits W{wprev}"', 1),
    ('assert not (w181_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j', 'assert not (w182_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j', 1),
    ('for j in range(B_N)}), f"W182 B hits W{wprev}"', 'for j in range(B_N)}), f"W183 B hits W{wprev}"', 1),
    ('n3r1_used181 = set(range(70_000, 70_006))', 'n3r1_used182 = set(range(70_000, 70_006))', 1),
    ('assert not (w181_a & n3r1_used181) and not (w181_b & n3r1_used181), \\', 'assert not (w182_a & n3r1_used182) and not (w182_b & n3r1_used182), \\', 1),
    ('"W182 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"', '"W183 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"', 1),
    ('assert not (w181_a & lfc_actual12) and not (w181_b & lfc_actual12), \\', 'assert not (w182_a & lfc_actual12) and not (w182_b & lfc_actual12), \\', 1),
    ('"W182 bands must clear the lfc actual draw range"', '"W183 bands must clear the lfc actual draw range"', 1),
    ('assert not (w181_a & options_actual12) and \\', 'assert not (w182_a & options_actual12) and \\', 1),
    ('not (w181_b & options_actual12), \\', 'not (w182_b & options_actual12), \\', 1),
    ('"W182 bands must clear the options_wave2 actual draw range"', '"W183 bands must clear the options_wave2 actual draw range"', 1),
    ('# band facts (law sec.4 W182 row, r795): A = FIRST-CLEAN past', '# band facts (law sec.4 W183 row, r795): A = FIRST-CLEAN past', 1),
    ('# the registered W181 B band (the arithmetic continuation', '# the registered W182 B band (the arithmetic continuation', 1),
    ('# 415_004..417_003 is REFUSED at its own start by the W181', '# 417_204..419_203 is REFUSED at its own start by the W182', 1),
    ('# B band 415_004..415_203, exactly as the W181 seat W182+ projection +', '# B band 417_204..417_403, exactly as the W182 seat W183+ projection +', 1),
    ('# r862 probe leg4 + r867 sec8 heal succession projection notes', '# r865 probe leg4 + r868 sec8 same-window succession projection notes', 1),
    ('# 415_204..417_203; A base == prior-wave B tail+1 (415_203+1)', '# 417_404..419_403; A base == prior-wave B tail+1 (417_403+1)', 1),
    ('# machine-checkable -- A-hops-prior-B staircase FORTY-SECOND', '# machine-checkable -- A-hops-prior-B staircase FORTY-THIRD', 1),
    ('# continuation 415_204..415_403 is CLEAN on the registered', '# continuation 417_404..417_603 is CLEAN on the registered', 1),
    ('# universe but lands INSIDE the W182 A band window --', '# universe but lands INSIDE the W183 A band window --', 1),
    ('# 417_204 and lands 417_204..417_403, hops=1, non-rotational', '# 419_404 and lands 419_404..419_603, hops=1, non-rotational', 1),
    ('# (417_203+1) machine-checkable; cross-window convergence', '# (419_403+1) machine-checkable; cross-window convergence', 1),
    ('# with the W181 seat W182+ projection + r862 probe leg4 + r867 sec8', '# with the W182 seat W183+ projection + r865 probe leg4 + r868 sec8', 1),
    ('# honored (post-W181 universe re-derive + own-wave A', '# honored (post-W182 universe re-derive + own-wave A', 1),
    ('# reservation when deriving B); seat MSG-0603 tail,', '# reservation when deriving B); seat MSG-0741 tail,', 1),
    ('assert WAVE_CONFIGS[182]["a_seed_base"] == 415_204 == 415_203 + 1, (', 'assert WAVE_CONFIGS[183]["a_seed_base"] == 417_404 == 417_403 + 1, (', 1),
    ('"W182 A must be the first-clean window past the registered "', '"W183 A must be the first-clean window past the registered "', 1),
    ('"W181 B band tail 415_203+1 (arithmetic continuation "', '"W182 B band tail 417_403+1 (arithmetic continuation "', 1),
    ('"415_004..417_003 REFUSED at its own start by the W181 B "', '"417_204..419_203 REFUSED at its own start by the W182 B "', 1),
    ('"band 415_004..415_203, exactly as the W181 seat W182+ projection + "', '"band 417_204..417_403, exactly as the W182 seat W183+ projection + "', 1),
    ('"r862 probe leg4 + r867 sec8 heal succession projection notes "', '"r865 probe leg4 + r868 sec8 same-window succession projection notes "', 1),
    ('"staircase FORTY-SECOND instance, E36 card)"', '"staircase FORTY-THIRD instance, E36 card)"', 1),
    ('arith_a181 = set(range(415_204, 417_204))', 'arith_a182 = set(range(417_404, 419_404))', 1),
    ('assert not (arith_a181 & reg_ints), \\', 'assert not (arith_a182 & reg_ints), \\', 1),
    ('"W182 A window must be CLEAN (first-clean ADMIT face past prior-wave B)"', '"W183 A window must be CLEAN (first-clean ADMIT face past prior-wave B)"', 1),
    ('assert WAVE_CONFIGS[182]["b_exit_seed_base"] == 417_204 == 417_203 + 1, (', 'assert WAVE_CONFIGS[183]["b_exit_seed_base"] == 419_404 == 419_403 + 1, (', 1),
    ('"W182 B must be the first-clean window past the own-wave A "', '"W183 B must be the first-clean window past the own-wave A "', 1),
    ('"band tail 417_203+1 (arithmetic continuation "', '"band tail 419_403+1 (arithmetic continuation "', 1),
    ('"415_204..415_403 CLEAN on the registered universe but "', '"417_404..417_603 CLEAN on the registered universe but "', 1),
    ('"lands INSIDE the W182 A band window; same-freeze mutual "', '"lands INSIDE the W183 A band window; same-freeze mutual "', 1),
    ('"own-wave A window reserved jumps to 417_204, first-clean "', '"own-wave A window reserved jumps to 419_404, first-clean "', 1),
    ('arith_b181 = set(range(417_204, 417_404))', 'arith_b182 = set(range(419_404, 419_604))', 1),
    ('assert not (arith_b181 & reg_ints), \\', 'assert not (arith_b182 & reg_ints), \\', 1),
    ('"W182 B window must be CLEAN (first-clean ADMIT face past own-wave A)"', '"W183 B window must be CLEAN (first-clean ADMIT face past own-wave A)"', 1),
    ('assert not (arith_b181 & arith_a181), \\', 'assert not (arith_b182 & arith_a182), \\', 1),
    ('"W182 A/B same-freeze mutual exclusion (B hops past own A)"', '"W183 A/B same-freeze mutual exclusion (B hops past own A)"', 1),
    ('assert _entry_shard_of(0, 12) == ("PERPETUAL-N1-W182-SHARD-0",', 'assert _entry_shard_of(0, 12) == ("PERPETUAL-N1-W183-SHARD-0",', 1),
    ('"n1w182-0of12"), "W182 entry identity"', '"n1w183-0of12"), "W183 entry identity"', 1),
    ('assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W182-SHARD-11",', 'assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W183-SHARD-11",', 1),
    ('"n1w182-11of12")', '"n1w183-11of12")', 1),
    ('assert SHARD_DIR.endswith("n1_w182") and OUT.endswith(', 'assert SHARD_DIR.endswith("n1_w183") and OUT.endswith(', 1),
    ('"n1_w182_results.json"), "W182 path drift"', '"n1_w183_results.json"), "W183 path drift"', 1),
    ('f"W182 shard dir collides with W{wprev}"', 'f"W183 shard dir collides with W{wprev}"', 1),
    ('# W182 finalize cumulative deps: W17..W181 outputs ALL PRESENT', '# W183 finalize cumulative deps: W17..W182 outputs ALL PRESENT', 1),
    ('# (landed net chain head 804,518 = W181 bm-a r864 one-pass --', '# (landed net chain head 806,718 = W182 bm-a r868 one-pass --', 1),
    ('for _depw in range(17, 182):', 'for _depw in range(17, 183):', 1),
    ('f"W182 finalize cumulative dep (W{_depw} output) missing"', 'f"W183 finalize cumulative dep (W{_depw} output) missing"', 1),
    ('# registered wave below 182 composes; wave 15 excluded by', '# registered wave below 183 composes; wave 15 excluded by', 1),
    ('# design; SINGLE STATE (W2..W181 all registered -- no', '# design; SINGLE STATE (W2..W182 all registered -- no', 1),
    ('assert sorted(w for w in WAVE_CONFIGS if w < 182) == \\', 'assert sorted(w for w in WAVE_CONFIGS if w < 183) == \\', 1),
    ('[w for w in range(16, 182)], \\', '[w for w in range(16, 183)], \\', 1),
    ('"W182 prior-wave set must derive from registry keys (no 15; "', '"W183 prior-wave set must derive from registry keys (no 15; "', 1),
    ('"W2..W181 registered single state)"', '"W2..W182 registered single state)"', 1),
    ('PATHS.root, "research", "PERPETUAL_N1_W182_PREREG.md")), \\', 'PATHS.root, "research", "PERPETUAL_N1_W183_PREREG.md")), \\', 1),
    ('"W182 per-wave prereg missing (materializer requirement)"', '"W183 per-wave prereg missing (materializer requirement)"', 1),
]

CL_PAIRS = [
    ('"+ W182 materializer face [same guard set, dep=W17..W181 ', '"+ W183 materializer face [same guard set, dep=W17..W182 ', 1),
    ('"outputs ALL PRESENT (landed net chain head 804,518 = "', '"outputs ALL PRESENT (landed net chain head 806,718 = "', 1),
    ('"W181 bm-a r864 one-pass, K=396,120 merged pool; ZERO "', '"W182 bm-a r868 one-pass, K=398,320 merged pool; ZERO "', 1),
    ('"in-flight upstream seats), ONE HUNDRED-AND-SEVENTY-SECOND "', '"in-flight upstream seats), ONE HUNDRED-AND-SEVENTY-THIRD "', 1),
    ('"ENGINE-OWNED WAVE BY MACHINE-DERIVE (engine_owner rows 171 "', '"ENGINE-OWNED WAVE BY MACHINE-DERIVE (engine_owner rows 172 "', 1),
    ("+ candidate) bm-a's ninety-eighth owned claim per ", "+ candidate) bm-a's ninety-ninth owned claim per ", 1),
    ('"machine-derive (engine_owner==bm-a rows 97 + candidate), "', '"machine-derive (engine_owner==bm-a rows 98 + candidate), "', 1),
    ('"A=FIRST-CLEAN past the registered W181 B band (staircase "', '"A=FIRST-CLEAN past the registered W182 B band (staircase "', 1),
    ('"FORTY-SECOND instance, E36 card, hops=1) + B=FIRST-CLEAN past the "', '"FORTY-THIRD instance, E36 card, hops=1) + B=FIRST-CLEAN past the "', 1),
    ('"results/_r865bma_w182_probe_receipt.json, law sec.4 W182 row, "', '"results/_r868bma_w183_probe_receipt.json, law sec.4 W183 row, "', 1),
    ('"r867 bm-a] "', '"r869 bm-a] "', 1),
]

PF_NEG = ['    # W182 (bm-a r867 freeze, seat MSG-2026-10-08-0603-bma-w182-seat', 'pushed to origin df062c5c1 pre-freeze r565 law (r865 pre-seat', '(3-item; the W181 finalize product already on origin since r864,', '# = direct fast-forward behind-0 at fetch (r865 pre-seat', '# push), zero merge, zero --no-verify; self-ack archive ALREADY\r\n    # LANDED pre-freeze -- bm-c r737-window self-ack move (the W182\r\n    # seat MSG sits in fleet/inbox/processed/ at freeze time, honest\r\n    # archived);', 'band gate ADMIT results/_r865bma_w182_probe_receipt.json: A = FIRST-CLEAN', 'past the registered W181 B band (arithmetic continuation', '415_004..417_003 REFUSED at its own start by the W181 B band', '415_004..415_203, exactly as the W181 seat W182+ projection + r862 probe', '# leg4 + r867 sec8 heal succession projection notes all anticipated;', 'honest forward walk hops=1 -> 415_204..417_203, non-rotational', '(415_203+1) machine-checkable -- A-hops-prior-B staircase', 'FORTY-SECOND instance, E36 card);', 'continuation 415_204..415_403 CLEAN on the registered universe', 'but lands INSIDE the W182 A band window -- same-freeze mutual', 'own-wave A window reserved jumps to 417_204 -> 417_204..417_403,', 'own-wave A tail+1 (417_203+1) machine-checkable);', 'W182+ projection (gate-derived r865): A first-clean', '417_204..419_203 CLEAN hops=0 / B first-clean 417_404..417_603', 'registered W182 B band 417_204..417_403 will refuse the naive', 'W183 A window; W183 freezer MUST re-derive on the post-W182', 'NOT a re-pick (R250: W182 bands were never assigned).', '182: {"a": (415_204, 417_203), "b_exit": (417_204, 417_403),', 'df062c5c1', 'r862 probe', 'r867 sec8', 'r865 pre-seat', '_r865bma', 'MSG-2026-10-08-0603', 'de699e8cd', '804,518', '396,120', 'FORTY-SECOND', 'ONE HUNDRED-AND-SEVENTY-SECOND']

EN_NEG = ['182: {"batch": "PERPETUAL-N1-W182",', '"prereg": ("research/PERPETUAL_N1_W182_PREREG.md (wave-level frozen "', 'new seed bands only; ONE HUNDRED-AND-SEVENTY-SECOND ENGINE-OWNED WAVE ', 'BY MACHINE-DERIVE (engine_owner rows 171 + candidate), ', 'number law after the REGISTERED W181 row bm-a r863 freeze ', 'de699e8cd, SINGLE STATE zero seat gap W2..W181 all ', 'registered; W182 finalize landed same-window r827, ledger ', 'head 804,518, merged pool K=396,120; seat published=reserved ', 'MSG-2026-10-08-0603-bma-w182-seat PUSHED to origin df062c5c1 ', 'probe receipt (3-item; the W181 finalize product already on origin since r864, not re-shipped; W146 precedent); ', 'at fetch (r865 pre-seat push), zero merge, zero ', 'engine_owner=bm-a, wave 181: ', 'A = FIRST-CLEAN past the registered W181 B band (the ', 'arithmetic continuation 415_004..417_003 is REFUSED at its ', 'own start by the W181 B band 415_004..415_203, exactly as ', 'the W181 seat W182+ projection + r862 probe leg4 + r867 sec8 heal succession ', '415_204..417_203; A base == prior-wave B tail+1 ', 'machine-checkable = A-hops-prior-B staircase FORTY-SECOND ', 'arithmetic continuation 415_204..415_403 is CLEAN on the ', 'registered universe but lands INSIDE the W182 A band ', 'jumps to 417_204, first-clean 417_204..417_403 hops=1, ', 'convergence with the W181 seat W182+ projection + r862 probe leg4 + ', 'r867 sec8 heal succession projection notes re-derived -- all ', 'MANDATORY notes honored (post-W181 universe re-derive + ', 'results/_r865bma_w182_probe_receipt.json; W183+ projection ', 'per this window gate: A first-clean 417_204..419_203 ', 'CLEAN / B first-clean 417_404..417_603 CLEAN -- naive ', 'W182 B band 417_204..417_403 will refuse the naive ', 'W183 A window; W183 freezer MUST re-derive on the ', 'post-W182 universe AND reserve the own-wave A window ', 'staircase card); W1..W181 finalize ALL LANDED (W181 ', 'finalize one-pass bm-a r864, net chain head 804,518, ', 'merged pool K=396,120) -- ZERO in-flight upstream ', '"a_seed_base": 415_204,        # law sec.4 W182 A: 415_204..417_203 (FIRST-CLEAN past the registered W181 B band; arithmetic 415_004..417_003 REFUSED at own start by the W181 B band; hops=1; A-hops-prior-B staircase FORTY-SECOND instance, E36 card; ordinal convergence per r587: W181 sec5.5 prose anticipated forty-second, r865 receipt machine-read FORTY-SECOND)', '"b_exit_seed_base": 417_204,   # law sec.4 W182 B: 417_204..417_403 (FIRST-CLEAN past the own-wave A window; arithmetic 415_204..415_403 lands inside own-A, same-freeze mutual exclusion W141 precedent; reserved walk hops=1; B base == own-A tail+1)', '"shard_subdir": "n1_w182", "out_name": "n1_w182_results.json",', 'de699e8cd', 'df062c5c1', '804,518', '396,120', 'ONE HUNDRED-AND-SEVENTY-SECOND', 'rows 171', 'r862 probe', '_r865bma', 'MSG-2026-10-08-0603', 'n1w182', 'n1_w182', 'PERPETUAL-N1-W182', 'PERPETUAL_N1_W182', 'FORTY-SECOND', 'bm-a r863 freeze', '417_204, first-clean']

MAT_NEG = ['# --- W182 materializer face (r867 bm-a freeze, own-series law', '#     ninety-eighth owned per machine-derive (engine_owner==bm-a', '#     rows 97 + candidate); wave 181 = first free number after', '#     the REGISTERED W181 row (bm-a r863 freeze de699e8cd) --', '#     SINGLE STATE zero seat gap (W2..W181 all registered). Seat', '#     published=reserved MSG-2026-10-08-0603-bma-w182-seat pushed', '#     to origin df062c5c1 BEFORE this freeze, r565 law (payload', '#     the W181 finalize product already on origin since r864, not', '#     at fetch (r865 pre-seat push), zero merge, zero', '#     --no-verify; self-ack inbox->processed archive ALREADY LANDED\r\n    #     pre-freeze -- bm-c r737-window self-ack move (the W182 seat\r\n    #     MSG sits in fleet/inbox/processed/ at freeze time, honest\r\n    #     archived).', '#     ONE HUNDRED-AND-SEVENTY-SECOND engine wave BY', '#     MACHINE-DERIVE (engine_owner rows 171 + candidate; gate', '#     W1..W181 finalize ALL LANDED (net chain head 804,518,', '#     K=396,120 merged pool; W181 finalize one-pass bm-a r864)', '#     always on. ADMIT receipt results/_r865bma_w182_probe_receipt.json;', '#     banned gate ADMIT 0; not a re-pick (R250: W182 bands were', '    _set_wave(182)', 'assert WAVE_CONFIGS[181]["a_seed_base"] == pf.N1_BANDS[181]["a"][0], \\', '"W182 A band drift vs law mirror"', 'assert WAVE_CONFIGS[181]["b_exit_seed_base"] == \\', 'pf.N1_BANDS[181]["b_exit"][0], "W182 B band drift vs law mirror"', 'assert WAVE_CONFIGS[181].get("engine_owner") == \\', 'pf.N1_BANDS[181].get("engine_owner") == "bm-a", \\', '"W182 engine_owner drift (law mirror parity)"', 'w181_a = {A_SEED_BASE + j for j in range(A_N)}', 'w181_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}', 'assert not (w181_a & w181_b), "W182 A/B band overlap"', 'assert not (w181_a & reg_ints) and not (w181_b & reg_ints), \\', '"W182 hits SEED_REGISTRY"', 'for nm, band in (("A", w181_a), ("B", w181_b)):', 'f"W182 {nm} hits v1"', 'f"W182 {nm} hits W1"', 'f"W182 {nm} hits probe seeds"', '# prior-wave disjointness W2..W181 (single state: all', 'for wprev in sorted(w for w in WAVE_CONFIGS if w < 182):', 'assert not (w181_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j', 'for j in range(A_N)}), f"W182 A hits W{wprev}"', 'assert not (w181_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j', 'for j in range(B_N)}), f"W182 B hits W{wprev}"', 'n3r1_used181 = set(range(70_000, 70_006))', 'assert not (w181_a & n3r1_used181) and not (w181_b & n3r1_used181), \\', '"W182 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"', 'assert not (w181_a & lfc_actual12) and not (w181_b & lfc_actual12), \\', '"W182 bands must clear the lfc actual draw range"', 'assert not (w181_a & options_actual12) and \\', 'not (w181_b & options_actual12), \\', '"W182 bands must clear the options_wave2 actual draw range"', '# band facts (law sec.4 W182 row, r795): A = FIRST-CLEAN past', '# the registered W181 B band (the arithmetic continuation', '# 415_004..417_003 is REFUSED at its own start by the W181', '# B band 415_004..415_203, exactly as the W181 seat W182+ projection +', '# r862 probe leg4 + r867 sec8 heal succession projection notes', '# 415_204..417_203; A base == prior-wave B tail+1 (415_203+1)', '# machine-checkable -- A-hops-prior-B staircase FORTY-SECOND', '# continuation 415_204..415_403 is CLEAN on the registered', '# universe but lands INSIDE the W182 A band window --', '# 417_204 and lands 417_204..417_403, hops=1, non-rotational', '# (417_203+1) machine-checkable; cross-window convergence', '# with the W181 seat W182+ projection + r862 probe leg4 + r867 sec8', '# honored (post-W181 universe re-derive + own-wave A', '# reservation when deriving B); seat MSG-0603 tail,', 'assert WAVE_CONFIGS[182]["a_seed_base"] == 415_204 == 415_203 + 1, (', '"W182 A must be the first-clean window past the registered "', '"W181 B band tail 415_203+1 (arithmetic continuation "', '"415_004..417_003 REFUSED at its own start by the W181 B "', '"band 415_004..415_203, exactly as the W181 seat W182+ projection + "', '"r862 probe leg4 + r867 sec8 heal succession projection notes "', '"staircase FORTY-SECOND instance, E36 card)"', 'arith_a181 = set(range(415_204, 417_204))', 'assert not (arith_a181 & reg_ints), \\', '"W182 A window must be CLEAN (first-clean ADMIT face past prior-wave B)"', 'assert WAVE_CONFIGS[182]["b_exit_seed_base"] == 417_204 == 417_203 + 1, (', '"W182 B must be the first-clean window past the own-wave A "', '"band tail 417_203+1 (arithmetic continuation "', '"415_204..415_403 CLEAN on the registered universe but "', '"lands INSIDE the W182 A band window; same-freeze mutual "', '"own-wave A window reserved jumps to 417_204, first-clean "', 'arith_b181 = set(range(417_204, 417_404))', 'assert not (arith_b181 & reg_ints), \\', '"W182 B window must be CLEAN (first-clean ADMIT face past own-wave A)"', 'assert not (arith_b181 & arith_a181), \\', '"W182 A/B same-freeze mutual exclusion (B hops past own A)"', 'assert _entry_shard_of(0, 12) == ("PERPETUAL-N1-W182-SHARD-0",', '"n1w182-0of12"), "W182 entry identity"', 'assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W182-SHARD-11",', '"n1w182-11of12")', 'assert SHARD_DIR.endswith("n1_w182") and OUT.endswith(', '"n1_w182_results.json"), "W182 path drift"', 'f"W182 shard dir collides with W{wprev}"', '# W182 finalize cumulative deps: W17..W181 outputs ALL PRESENT', '# (landed net chain head 804,518 = W181 bm-a r864 one-pass --', 'for _depw in range(17, 182):', 'f"W182 finalize cumulative dep (W{_depw} output) missing"', '# registered wave below 182 composes; wave 15 excluded by', '# design; SINGLE STATE (W2..W181 all registered -- no', 'assert sorted(w for w in WAVE_CONFIGS if w < 182) == \\', '[w for w in range(16, 182)], \\', '"W182 prior-wave set must derive from registry keys (no 15; "', '"W2..W181 registered single state)"', 'PATHS.root, "research", "PERPETUAL_N1_W182_PREREG.md")), \\', '"W182 per-wave prereg missing (materializer requirement)"', 'w181_', 'arith_a181', 'arith_b181', 'n3r1_used181', 'r862 probe', 'r865 pre-seat', 'de699e8cd', 'ONE HUNDRED-AND-SEVENTY-SECOND', 'ninety-eighth', 'rows 171', 'rows 97 ', 'range(17, 182)', 'range(16, 182)', 'PERPETUAL_N1_W182', 'PERPETUAL-N1-W182', 'MSG-0603', '_r865bma', 'bm-c r737-window', 'n1w182', 'n1_w182', '804,518', '396,120']

CL_NEG = ['"+ W182 materializer face [same guard set, dep=W17..W181 ', '"outputs ALL PRESENT (landed net chain head 804,518 = "', '"W181 bm-a r864 one-pass, K=396,120 merged pool; ZERO "', '"in-flight upstream seats), ONE HUNDRED-AND-SEVENTY-SECOND "', '"ENGINE-OWNED WAVE BY MACHINE-DERIVE (engine_owner rows 171 "', "+ candidate) bm-a's ninety-eighth owned claim per ", '"machine-derive (engine_owner==bm-a rows 97 + candidate), "', '"A=FIRST-CLEAN past the registered W181 B band (staircase "', '"FORTY-SECOND instance, E36 card, hops=1) + B=FIRST-CLEAN past the "', '"results/_r865bma_w182_probe_receipt.json, law sec.4 W182 row, "', '"r867 bm-a] "', '804,518', '396,120', 'ONE HUNDRED-AND-SEVENTY-SECOND', 'ninety-eighth', 'rows 171', 'rows 97 ', 'FORTY-SECOND', '_r865bma', 'r867 bm-a] ']

blk183 = vmap(pfblk, PF_PAIRS, PF_NEG, "pf")
entry183 = IND23 + vmap(entry, EN_PAIRS, EN_NEG, "entry")
mat183 = "    " + vmap(mat, MAT_PAIRS, MAT_NEG, "mat")
claim183 = IND10 + vmap(claim, CL_PAIRS, CL_NEG, "claim")

# ---- apply insertions (in-memory) ---------------------------------------
pfsrc = io.open(PF, encoding="utf-8", newline="").read()
n1src = io.open(N1, encoding="utf-8", newline="").read()

# pf: insert W183 block after the W182 row (last registered), before the
# dict close -- r560 insert-after-last-registered-row + post-anchor gate
seg = EO + NL + "}"
check(pfsrc.count(seg) == 1, "pf row-close segment not unique")
pfnew = pfsrc.replace(seg, EO + NL + blk183 + NL + "}", 1)

# n1 entry: after the W182 entry, before the WAVE_CONFIGS close
seg = EO + NL + IND23 + "}"
check(n1src.count(seg) == 1, "n1 entry-close segment not unique")
n1new = n1src.replace(seg, EO + NL + entry183 + NL + IND23 + "}", 1)

# n1 mat: insert the W183 block before the T-141 s2 lane face header
seg = "    # --- T-141 s2 lane face"
check(n1new.count(seg) == 1, "n1 T-141 mat anchor not unique")
n1new = n1new.replace(seg, mat183 + NL + seg, 1)

# n1 claim: insert the W183 attribution after the W182 claim tail line
# (r581 law: anchor = tail single-line literal + post-anchor guard)
seg = '"r867 bm-a] "' + NL + IND10 + '"+ T-141 s2 "'
check(n1new.count(seg) == 1, "n1 claim anchor not unique")
n1new = n1new.replace(seg, '"r867 bm-a] "' + NL + claim183 + NL + IND10 +
                      '"+ T-141 s2 "', 1)

# ---- gates (r780/r781/r560/r815 lineage) --------------------------------
ast.parse(pfnew)
ast.parse(n1new)
print("AST gate: both files parse OK")

# W183 presence + W182 anti-vanish (r560 law)
checks = [
    (pfnew, '183: {"a": (417_404, 419_403), "b_exit": (419_404, 419_603),', 1),
    (pfnew, '182: {"a": (415_204, 417_203), "b_exit": (417_204, 417_403),', 1),
    (pfnew, "# W183 (bm-a r869 freeze", 1),
    (pfnew, "# W182 (bm-a r867 freeze", 1),
    (n1new, '183: {"batch": "PERPETUAL-N1-W183",', 1),
    (n1new, '182: {"batch": "PERPETUAL-N1-W182",', 1),
    (n1new, "# --- W183 materializer face", 1),
    (n1new, "# --- W182 materializer face", 1),
    (n1new, '"r869 bm-a] "', 1),
    (n1new, '"r867 bm-a] "', 1),
    (n1new, '"a_seed_base": 417_404,', 1),
    (n1new, '"b_exit_seed_base": 419_404,', 1),
    (n1new, "n1_w183", 4),
    (n1new, "PERPETUAL_N1_W183_PREREG.md", 2),
]
for src, needle, cnt in checks:
    got = src.count(needle)
    check(got == cnt, "post-edit needle %r count %d != %d" % (needle[:50], got, cnt))

# W184+ projection prose present in the new W183 blocks (probe leg4
# verbatim; r819 post-edit assert bloodline + r776 fragment-needle law;
# pf header = self-wave W183+ per r845 precedent, n1 fragment =
# next-wave W184+)
check("# W183+ projection (gate-derived r868)" in pfnew,
      "pf W183+ projection head missing")
check('probe_receipt.json; W184+ projection "' in n1new,
      "n1 W184+ projection head fragment missing")
check("# 419_404..421_403 CLEAN hops=0 / B first-clean 419_604..419_803" in pfnew,
      "pf W184p prose missing")
check("W184 A window; W184 freezer MUST re-derive on the post-W183" in pfnew,
      "pf W184 freezer prose missing")
check('"W184 A window; W184 freezer MUST re-derive on the "' in n1new,
      "n1 W184 freezer fragment missing")
check('"W183 B band 419_404..419_603 will refuse the naive "' in n1new,
      "n1 W183-band refuse fragment missing")

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
check('183: {"a": (417_404' not in pf_o2, "write-time: origin pf carries W183")
check('183: {"batch"' not in n1_o2, "write-time: origin n1 carries W183")
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
