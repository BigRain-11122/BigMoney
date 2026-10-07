# -*- coding: utf-8 -*-
"""r813 bm-a W170 freeze edits: four insertions (pf N1_BANDS[170] row +
n1 WAVE_CONFIGS[170] entry + n1 W170 materializer block refresh +
n1 PASS snippet claim insertion). DRY flag: --dry = zero-write simulation
(r781 verify-separation law + r811 dry-run precedent: full stale+prose+
AST asserts in memory BEFORE any write).

Bloodline: r811 _r811bma_w169_freeze_edits.py machinery (r773 pit law
freeze-editor compliance + r776 fragment-needle law + r781
verify-separation law), W170 facts live-registry-driven:
  - pre-seat probe results/_r812bma_w170_probe_receipt.json rc0 ADMIT
    (A 388_804..390_803 staircase TWENTY-NINTH instance E36 hops=1 past
    the registered W169 B band 388_604..388_803; naive 388_604..390_603
    refused at its own start by the registered W169 B band; B 390_804..391_003
    own-A mutual exclusion hops=1, naive 388_804..389_003);
  - W170 has ONE receipt (r812 merged the gate legs INTO the pre-seat
    probe: leg0 registry / leg1 bands+hops / leg2 conflicts /
    leg3 origin vacancy / leg4 W171+ projection) -- single-window derive,
    dual-window parity N/A honest;
  - seat MSG-2026-10-07-0738-bma-w170-seat published 0f00fa424
    (r812 pre-seat push, r565 law: on origin BEFORE this freeze commit;
    4-item payload = seat MSG + probe script + probe receipt + the W169
    finalize product n1_w169_results.json, W146 same-push precedent;
    seat MSG still in fleet/inbox/ at freeze time = honest DEFERRED
    state -- self-ack move deferred to the W170 finalize window);
  - per-wave prereg research/PERPETUAL_N1_W170_PREREG.md (r813 build,
    banned gate ADMIT 0);
  - W169 finalize one-pass r812 0f00fa424: ledger head 777,212, merged
    pool K=369,720 (n1_w169_results.json machine-read);
  - W169 freeze registered sha machine-derived = 9c2271baf (git log
    origin/main --grep "W169 FREEZE"; the r812 probe-script header
    carried the stale pre-rebase sha 2ea58d762 -- honest note, the
    r812 rebase estate preserved 9c2271baf as the landed truth);
  - W171+ projection (probe leg4 verbatim): A first-clean 390_804..392_803
    / B first-clean 391_004..391_203, naive-B-inside-naive-A, the
    registered W170 B band will refuse the naive W171 A window.

r773 pit law compliance:
  (1) full string-face inventory empirically probed BEFORE TOK
      (_r813bma_w170_face_probe.py -- four face dumps + needle-count
      receipt, rc0);
  (2) composite band strings tokenized WHOLE (no bare-seed-prefix
      tokens; every dotted band / seed-base row / jump phrase /
      round-sha composite is a single token; bare 169/168 run LAST);
  (3) post-edit full-file start>end malformed-window regex scan on BOTH
      touched files;
  (4) every projection value re-derived FROM the on-disk probe receipt
      (r587 never-transcribe law);
  (5) r776 fragment-needle law: all needles taken from the PHYSICAL
      probe-dumped shapes (python-string fragments / comment lines,
      CRLF-exact);
  (6) same-window HONESTY FIXUPS (deferred direction, THIS window):
      the W169-era source prose claims the seat was already
      consumed-archived pre-freeze (bm-b r798 06:02:52) -- for W170 the
      TRUE state is the seat sits in fleet/inbox/ at freeze time, so
      FIXUPS correct the self-ack direction to DEFERRED (r810 W168-era
      probe-precedent direction), the payload face to the 4-item truth,
      and the dual-window parity face to the single-window truth;
  (7) anti-drift composite @REGROW@ (bm-a r809 freeze 8d8842b61) runs
      BEFORE the freeze-session token so the registered-prior-row sha
      pairing can never be torn by the session map;
  (8) lineage constant disclosed: the mat band-facts comment carries
      the template session stamp "law sec.4 W169 row, r795" -- the r795
      has ridden every vmap since the W165 freeze authored the
      band-facts template (r809/r811 verbatim precedent; passed through).

EOL-adaptive (r370 law: CRLF-dominant blocks written CRLF);
needle count==1 (r745); insert-after-last-registered-row (r560);
anchor = predecessor full lines (r580/r781); AST gate after every
edit batch (r580/r781); origin anti-collision pre-check (r530/r687:
fetch + origin carries no W170 registration before this freeze)."""
import ast
import io
import json
import re
import os
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
DRY = "--dry" in sys.argv
PF = r"scripts/perpetual_faces.py"
N1 = r"scripts/perpetual_faces_n1.py"
CRLF = "\r\n"

# --- machine-derived facts (r587: read from on-disk receipts) ----------------
probe = json.load(open("results/_r812bma_w170_probe_receipt.json", encoding="utf-8"))
assert probe["verdict"] == "ADMIT", probe["verdict"]
assert probe["bands"] == {"A": "388804_390803", "B": "390804_391003"}, probe["bands"]
leg0, leg1 = probe["legs"]["leg0"], probe["legs"]["leg1"]
leg2, leg3, leg4 = probe["legs"]["leg2"], probe["legs"]["leg3"], probe["legs"]["leg4"]
assert leg1["A"] == [388804, 390803] and leg1["B"] == [390804, 391003], leg1
assert leg1["hops_A"] == 1 and leg1["hops_B"] == 1, leg1
assert leg1["ARITH_A"] == [388604, 390603], leg1["ARITH_A"]
assert leg1["ARITH_B"] == [388804, 389003], leg1["ARITH_B"]
assert leg1["B_naive_first_clean"] == [388804, 389003], leg1["B_naive_first_clean"]
assert leg2["conflicts"] == 0, leg2
assert leg3["origin_vacancy"] is True, leg3
assert leg0["rows"] == 167 and leg0["tail"] == "W169" and leg0["ordinal"] == 160 \
    and leg0["bma_ordinal"] == 86 and leg0["owner_rows"] == 159 \
    and leg0["bma_rows"] == 85 and leg0["w169_ledger_head"] == 777212, leg0
w169res = json.load(open("results/perpetual_faces/n1_w169_results.json", encoding="utf-8"))
assert w169res["null_pool_cumulative"]["merged"]["n_values"] == 369720, "W169 merged K drift"
assert w169res["null_pool_cumulative"]["merged"]["n_values"] + 2200 == 371920, \
    "W170 K projection arithmetic"
assert os.path.exists(os.path.join("research", "PERPETUAL_N1_W170_PREREG.md")), \
    "W170 per-wave prereg missing on disk"
# honesty precondition: the W170 seat MSG sits in fleet/inbox/ at freeze
# time (DEFERRED self-ack state; the mover would be THIS machine at the
# W170 finalize closeout window) -- the FIXUPS direction below depends
# on this being true.
assert os.path.exists(os.path.join("fleet", "inbox",
                                   "MSG-2026-10-07-0738-bma-w170-seat.md")), \
    "W170 seat MSG not in fleet/inbox/ (FIXUPS deferred direction would be wrong)"
assert not os.path.exists(os.path.join("fleet", "inbox", "processed",
                                        "MSG-2026-10-07-0738-bma-w170-seat.md")), \
    "W170 seat MSG already processed (landed direction would be TRUE -- FIXUPS wrong)"


def u(s):  # "390804..392803" -> "390_804..392_803"
    def g(part):
        return re.sub(r"(\d)(?=(\d{3})+$)", r"\1_", part)
    a, b = s.split("..")
    return f"{g(a)}..{g(b)}"


W171p_A = u(leg4["W171p_A"])
W171p_B = u(leg4["W171p_B"])
assert W171p_A == "390_804..392_803" and W171p_B == "391_004..391_203", (W171p_A, W171p_B)
assert leg4["W171p_B_lands_inside_W171p_A"] is True, leg4

# --- ordered value-map (tokens first, then back-substitution) ---------------
TOK = [
    # whole-line seed-base rows (entry face; bands + ordinal carried WHOLE)
    ('"a_seed_base": 386_604,        # law sec.4 W169 A: 386_604..388_603 (FIRST-CLEAN past the registered W168 B band; arithmetic 386_404..388_403 REFUSED at own start by the W168 B band; hops=1; A-hops-prior-B staircase twenty-eighth instance, E36 card)', "@ASROW@"),
    ('"b_exit_seed_base": 388_604,   # law sec.4 W169 B: 388_604..388_803 (FIRST-CLEAN past the own-wave A window; arithmetic 386_604..386_803 lands inside own-A, same-freeze mutual exclusion W141 precedent; reserved walk hops=1; B base == own-A tail+1)', "@BSROW@"),
    # row + entry carriers
    ('169: {"a": (386_604, 388_603), "b_exit": (388_604, 388_803),', "@RROW@"),
    ('169: {"batch"', "@RENTRY@"),
    # registered-prior-row citations (machine-verified sha pairing; the
    # anti-drift composite -- MUST precede every session/round token)
    ('W168 row bm-a r809 freeze', "@PROW1@"),
    ('8d8842b61, SINGLE STATE zero seat gap W2..W168 all', "@PROW2@"),
    ('bm-a r809 freeze 8d8842b61', "@REGROW@"),
    # freeze-session composites (this window: bm-a r813 freeze)
    ('bm-a r811 freeze', "@FZH@"),
    ('r811 bm-a freeze', "@MFZH@"),
    # claim-tail session attribution (the W169 claim carries the correct
    # r811 attribution; the NEW W170 claim rolls it to the r813 freeze
    # session via this token)
    ('r811 bm-a] ', "@CLMS@"),
    # prior-finalize citations (W169 finalize one-pass landed r812
    # 0f00fa424; FRAGMENT form per r781/r776 law where physically split)
    ('W168 finalize landed same-window r809', "@FW@"),
    ('W168 finalize one-pass bm-a r809', "@FOPW@"),
    ('finalize one-pass bm-a r809', "@FOPM2@"),
    ('W168 bm-a r809 one-pass', "@FOP@"),
    # gate / probe receipt citations (W170 receipts -- single receipt,
    # the merged-gate probe)
    ('_r810bma_w169_probe_receipt.json', "@PRC@"),
    ('_r810bma_w169_band_gate.json', "@BGR@"),
    # prior gate / sec8 session refs (W168 gate r806 -> cited as r810 for
    # the W170 succession face; W168 sec8 r811 -> cited as r813: the W169
    # sec8 succession face was backfilled THIS window r813)
    ('r806 gate leg3', "@GATE@"),
    ('r806 gate', "@GATEP@"),
    ('r811 sec8 succession', "@SEC8@"),
    ('r811 sec8', "@SEC8M@"),
    # own-wave gate-session prose + pre-seat push session (r810 -> r812)
    ('gate-derived r810', "@GDR@"),
    ('r810 pre-seat push', "@PSP@"),
    # seat tokens (W169 seat 0547/bcd6e4392 -> W170 seat 0738/0f00fa424;
    # 0f00fa424 = the TRUE r812 seat-push commit, machine-verified via
    # git show --stat origin/main)
    ('MSG-2026-10-07-0547', "@SEAT@"),
    ('bma-w169-seat', "@SEATW@"),
    ('MSG-0547', "@MSGS@"),
    ('bcd6e4392', "@SEATSHA@"),
    # W171 projection bands (probe leg4 verbatim, whole; BEFORE all band
    # tokens and seed backstops -- r773 pit law)
    ('388_604..390_603', "@PA@"),
    ('388_804..389_003', "@PB@"),
    # jump phrases (longest first; fragment-safe; BEFORE @BB@ which
    # shares the B-band substring)
    ('jumps to 388_604, first-clean 388_604..388_803 hops=1', "@JN@"),
    ('jumps to 388_604 -> 388_604..388_803,', "@JP@"),
    ('388_604 and lands 388_604..388_803', "@JAND@"),
    # the W170 B-assert jump fragment (rides the @JB@ token; W170 target
    # 390_804 -- the r787/r793/r805/r809/r811 heal lineage, leak class
    # killed)
    ('own-wave A window reserved jumps to 388_604, first-clean ', "@JB@"),
    # assert composites
    ('== 386_604 == 386_603 + 1', "@ASB@"),
    ('== 388_604 == 388_603 + 1', "@BSB@"),
    ('set(range(386_604, 388_604))', "@ARITHA@"),
    ('set(range(388_604, 388_804))', "@ARB@"),
    # dotted band geometry
    ('386_404..388_403', "@NA@"),
    ('386_404..386_603', "@OB@"),
    ('386_604..388_603', "@AB@"),
    ('386_604..386_803', "@NB@"),
    ('388_604..388_803', "@BB@"),
    # base-relation composites
    ('386_603+1', "@ABASE@"),
    ('388_603+1', "@BBASE@"),
    # identity / stats / ordinals
    ('PERPETUAL_N1_W169_PREREG.md', "@PF@"),
    ('PERPETUAL-N1-W169', "@B@"),
    ('n1_w169_results.json', "@OD@"),
    ('n1_w169', "@SD@"),
    ('n1w169', "@SD2@"),
    ('775,012', "@LEDG@"),
    ('367,520', "@K1@"),
    ('ONE HUNDRED-AND-FIFTY-NINTH', "@ORDW@"),
    ('engine_owner rows 158', "@R154@"),
    ('rows 84 + candidate', "@ROWS80@"),
    ('eighty-fourth', "@SVN@"),
    ('twenty-eighth', "@ST24@"),
    # wave numbers (higher first: W170 projection -> W171; then W169->W170,
    # W168->W169)
    ('W170', "@WN2@"),
    ('W169', "@WN@"),
    ('W168', "@W@"),
    # bare round backstop (r776 fragment law: the physical W169 faces
    # break 'r810 pre-seat' + CRLF + '# push' across comment lines in the
    # pf block -- the exact-phrase TOK above cannot match it; every other
    # r810 face is already carried by composite tokens, so the bare roll
    # r810->r812 is safe; runs BEFORE the bare numerals)
    ('r810', "@RB@"),
    # bare numerals LAST (every longer carrier tokenized above; 169 before
    # 168 so the 168->169 output is never re-mapped)
    ('169', "@IDX@"),
    ('168', "@IDX2@"),
]
BACK = [
    ("@ASROW@", '"a_seed_base": 388_804,        # law sec.4 W170 A: 388_804..390_803 (FIRST-CLEAN past the registered W169 B band; arithmetic 388_604..390_603 REFUSED at own start by the W169 B band; hops=1; A-hops-prior-B staircase twenty-ninth instance, E36 card)'),
    ("@BSROW@", '"b_exit_seed_base": 390_804,   # law sec.4 W170 B: 390_804..391_003 (FIRST-CLEAN past the own-wave A window; arithmetic 388_804..389_003 lands inside own-A, same-freeze mutual exclusion W141 precedent; reserved walk hops=1; B base == own-A tail+1)'),
    ("@RROW@", '170: {"a": (388_804, 390_803), "b_exit": (390_804, 391_003),'),
    ("@RENTRY@", '170: {"batch"'),
    ("@PROW1@", "W169 row bm-a r811 freeze"),
    ("@PROW2@", "9c2271baf, SINGLE STATE zero seat gap W2..W169 all"),
    ("@REGROW@", "bm-a r811 freeze 9c2271baf"),
    ("@FZH@", "bm-a r813 freeze"),
    ("@MFZH@", "r813 bm-a freeze"),
    ("@CLMS@", "r813 bm-a] "),
    ("@FW@", "W169 finalize landed same-window r812"),
    ("@FOPW@", "W169 finalize one-pass bm-a r812"),
    ("@FOPM2@", "finalize one-pass bm-a r812"),
    ("@FOP@", "W169 bm-a r812 one-pass"),
    ("@PRC@", "_r812bma_w170_probe_receipt.json"),
    ("@BGR@", "_r812bma_w170_probe_receipt.json"),
    ("@GATE@", "r810 gate leg3"),
    ("@GATEP@", "r810 gate"),
    ("@SEC8@", "r813 sec8 succession"),
    ("@SEC8M@", "r813 sec8"),
    ("@GDR@", "gate-derived r812"),
    ("@PSP@", "r812 pre-seat push"),
    ("@SEAT@", "MSG-2026-10-07-0738"),
    ("@SEATW@", "bma-w170-seat"),
    ("@MSGS@", "MSG-0738"),
    ("@SEATSHA@", "0f00fa424"),
    ("@PA@", W171p_A),
    ("@PB@", W171p_B),
    ("@JN@", "jumps to 390_804, first-clean 390_804..391_003 hops=1"),
    ("@JP@", "jumps to 390_804 -> 390_804..391_003,"),
    ("@JAND@", "390_804 and lands 390_804..391_003"),
    ("@JB@", "own-wave A window reserved jumps to 390_804, first-clean "),
    ("@ASB@", "== 388_804 == 388_803 + 1"),
    ("@BSB@", "== 390_804 == 390_803 + 1"),
    ("@ARITHA@", "set(range(388_804, 390_804))"),
    ("@ARB@", "set(range(390_804, 391_004))"),
    ("@NA@", "388_604..390_603"),
    ("@OB@", "388_604..388_803"),
    ("@AB@", "388_804..390_803"),
    ("@NB@", "388_804..389_003"),
    ("@BB@", "390_804..391_003"),
    ("@ABASE@", "388_803+1"),
    ("@BBASE@", "390_803+1"),
    ("@PF@", "PERPETUAL_N1_W170_PREREG.md"),
    ("@B@", "PERPETUAL-N1-W170"),
    ("@OD@", "n1_w170_results.json"),
    ("@SD@", "n1_w170"),
    ("@SD2@", "n1w170"),
    ("@LEDG@", "777,212"),
    ("@K1@", "369,720"),
    ("@ORDW@", "ONE HUNDRED-AND-SIXTIETH"),
    ("@R154@", "engine_owner rows 159"),
    ("@ROWS80@", "rows 85 + candidate"),
    ("@SVN@", "eighty-fifth"),
    ("@ST24@", "twenty-ninth"),
    ("@WN2@", "W171"),
    ("@WN@", "W170"),
    ("@W@", "W169"),
    ("@RB@", "r812"),
    ("@IDX@", "170"),
    ("@IDX2@", "169"),
]
# r587 belt-and-braces: the projection BACK values must equal the
# machine-derived probe leg4 strings verbatim
assert ("@PA@", W171p_A) in BACK and ("@PB@", W171p_B) in BACK


def vmap(s: str) -> str:
    for a, b in TOK:
        s = s.replace(a, b)
    for a, b in BACK:
        s = s.replace(a, b)
    return s


# --- per-kind fragment-level fixups (r776 law: needles taken from the
# PHYSICAL probe-dumped shapes; applied AFTER vmap) ---------------------------
# Honesty fixups (deferred direction, this window): the W170 seat MSG
# sits in fleet/inbox/ at freeze time -- the rolled "already landed
# pre-freeze (bm-b r798 ...)" prose is FALSE for W170; correct the
# self-ack direction, the payload face (4-item truth, W146 precedent)
# and the single-window derive face (r812 merged gate legs INTO the
# pre-seat probe).
FIXUPS = {
    "pf": [
        ("# move already landed pre-freeze (bm-b r798 consumed-archived the" + CRLF +
         "    # W170 seat to fleet/inbox/processed at 06:02:52 -- honest state);",
         "# move DEFERRED to the W170 finalize window -- the W170 seat" + CRLF +
         "    # MSG sits in fleet/inbox/ at freeze time (honest deferred);"),
        ("payload = seat MSG + pre-seat probe + probe receipt;",
         "payload = seat MSG + pre-seat probe script + probe receipt + the" + CRLF +
         "    # W169 finalize product (4-item, W146 same-push precedent);"),
        ("# dual-window derive parity with pre-seat probe" + CRLF +
         "    # results/_r812bma_w170_probe_receipt.json; scan face =",
         "# single-window derive (r812 merged the gate legs INTO the" + CRLF +
         "    # pre-seat probe; dual-window parity N/A honest); scan face ="),
    ],
    "mat": [
        ("move already landed pre-freeze (bm-b r798 consumed-archived the" + CRLF +
         "    #     W170 seat to fleet/inbox/processed at 06:02:52 -- honest state).",
         "move DEFERRED to the W170 finalize window -- the W170 seat MSG" + CRLF +
         "    #     sits in fleet/inbox/ at freeze time (honest deferred)."),
        ("= seat MSG + pre-seat probe + probe receipt;",
         "= seat MSG + pre-seat probe script + probe receipt + the W169" + CRLF +
         "    #     finalize product (4-item, W146 same-push precedent);"),
    ],
    "entry": [
        ('"seat MSG + pre-seat probe + probe receipt; "',
         '"seat MSG + pre-seat probe script + probe receipt + the W169 finalize product (4-item, W146 precedent); "'),
        ('"--no-verify; pre-seat probe and freeze-window band-gate "',
         '"--no-verify; single-window derive -- r812 merged the gate "'),
        ('"runs derive identical, no fork face), "',
         '"legs INTO the pre-seat probe; parity N/A honest), "'),
    ],
}


def vmap_fix(s: str, kind: str) -> str:
    s = vmap(s)
    if kind not in FIXUPS:
        return s
    for i, (old, new) in enumerate(FIXUPS[kind]):
        n = s.count(old)
        assert n == 1, (kind, "fixup", i, s.count(old), old[:70])
        s = s.replace(old, new)
    return s


def edit(path, pairs):
    src = io.open(path, encoding="utf-8", newline="").read()
    for i, (old, new) in enumerate(pairs):
        n = src.count(old)
        assert n == 1, f"{path}: needle {i} count={n} expect=1: {old[:80]!r}"
        src = src.replace(old, new)
    io.open(path, "w", encoding="utf-8", newline="").write(src)
    ast.parse(io.open(path, encoding="utf-8", newline="").read())
    print(f"{path}: {len(pairs)} edits landed, AST gate PASS")


pfsrc = io.open(PF, encoding="utf-8", newline="").read()
n1src = io.open(N1, encoding="utf-8", newline="").read()

# face-source zero-drift gate vs the r813 probe dumps
EO = '"engine_owner": "bm-a"},'
i1 = pfsrc.find("    # W169 (bm-a r811 freeze")
assert i1 > 0, "pf W169 comment block not found"
r1 = pfsrc.find('169: {"a": (386_604', i1)
assert r1 > i1, "pf W169 row not after comment block"
j1 = pfsrc.find(EO, r1) + len(EO)
block169_pf = pfsrc[i1:j1]
assert block169_pf == io.open(r"results\_r813bma_w170_probe_pf_block.txt",
                             encoding="utf-8", newline="").read(), "pf face drift vs probe"
assert block169_pf.count("engine_owner") == 1 and "8d8842b61" not in block169_pf
assert "386_404..388_403 REFUSED at its own start by the W168 B band" in block169_pf

# pre-edit live registry parity (the W169 registered row must be intact
# before we append the W170 row -- r560 no-replace law)
sys.path.insert(0, ".")
sys.path.insert(0, "scripts")
import perpetual_faces as pfpre
assert pfpre.N1_BANDS[169] == {"a": (386_604, 388_603),
                               "b_exit": (388_604, 388_803),
                               "engine_owner": "bm-a"}, "pre-edit W169 row drift"
assert sorted(pfpre.N1_BANDS)[-1] == 169 and len(pfpre.N1_BANDS) == 167, "pre-edit row count"

# origin anti-collision pre-check (r530 never-dry + r687 dual-scan:
# fetch fresh, origin must carry no W170 registration before this freeze)
subprocess.run(["git", "fetch", "origin"], capture_output=True)
_r = subprocess.run(["git", "show", "origin/main:scripts/perpetual_faces.py"],
                   capture_output=True)
_op = _r.stdout.decode("utf-8", "replace")
assert _r.returncode == 0, "origin pf.py read failed"
assert '170: {"a"' not in _op, "origin already carries a W170 registration (r687 dual-scan)"
assert "# W170 (bm-a" not in _op, "origin already carries a W170 freeze block"
_r2 = subprocess.run(["git", "rev-list", "--count", "origin/main..HEAD"],
                     capture_output=True, text=True)
assert _r2.stdout.strip() == "0", f"local ahead of origin: {_r2.stdout.strip()} (behind-law)"
# seat-on-origin precondition (r565 law: seat published BEFORE this freeze)
_r3 = subprocess.run(["git", "show", "origin/main:fleet/inbox/MSG-2026-10-07-0738-bma-w170-seat.md"],
                     capture_output=True)
assert _r3.returncode == 0, "W170 seat MSG not on origin (r565 pre-freeze law)"

# --- a1: pf.py W169 comment block + row -> append W170 comment block + row ----
a1 = block169_pf + CRLF + "}"
r1n = block169_pf + CRLF + vmap_fix(block169_pf, "pf") + CRLF + "}"

# --- a2: n1.py WAVE_CONFIGS entry ----------------------------------------------
k = n1src.find('169: {"batch"')
assert k > 0, "n1 W169 entry not found"
m = n1src.find(EO, k) + len(EO)
entry169 = n1src[k:m]
assert entry169 == io.open(r"results\_r813bma_w170_probe_n1_entry.txt",
                          encoding="utf-8", newline="").read(), "entry face drift vs probe"
a2 = entry169 + CRLF + "                       }"
r2 = entry169 + CRLF + "                       " + vmap_fix(entry169, "entry") + CRLF + "                       }"

# --- a3: materializer block (chain split-verbatim + one-row extension) --------
w = n1src.find("# --- W169 materializer face")
t2 = n1src.find("# --- T-141 s2 lane face", w)
assert 0 < w < t2, "materializer anchors missing"
block = n1src[w:t2]
assert block == io.open(r"results\_r813bma_w170_probe_n1_mat.txt",
                        encoding="utf-8", newline="").read(), "mat face drift vs probe"
ci = block.find("assert pf.N1_BANDS[138]")
cj = block.find("# prior-wave disjointness")
assert 0 < ci < cj, "chain boundaries missing"
pre, chain, post = block[:ci], block[ci:cj], block[cj:]
chain_rows = re.findall(r"assert pf\.N1_BANDS\[(\d+)\]", chain)
assert chain_rows == [str(x) for x in range(138, 169)], chain_rows
w169row = ('assert pf.N1_BANDS[169] == {"a": (386_604, 388_603),' + CRLF +
           '                                    "b_exit": (388_604, 388_803),' + CRLF +
           '                                    "engine_owner": "bm-a"}, \\' + CRLF +
           '            "registered W169 row parity drift (r307; bm-a r811)"' + CRLF +
           "        ")
# delivery/payload prose lives in the mat pre (header comment face);
# the post (disjointness/band-facts/assert face) passes through plain vmap
block170 = vmap_fix(pre, "mat") + chain + w169row + vmap(post)
a3 = block + "# --- T-141 s2 lane face"
r3 = block170 + "# --- T-141 s2 lane face"

# --- a4: PASS snippet claim insertion ------------------------------------------
cs = n1src.find('"+ W169 materializer face')
assert cs > 0, "W169 claim start not found"
ce = n1src.find('"r811 bm-a] "', cs) + len('"r811 bm-a] "')
assert 0 < cs < ce, "W169 claim end not found"
claim169 = n1src[cs:ce]
assert claim169 == io.open(r"results\_r813bma_w170_probe_n1_claim.txt",
                           encoding="utf-8", newline="").read(), "claim face drift vs probe"
a4 = '"r811 bm-a] "' + CRLF + '          "+ T-141 s2 "'
r4 = '"r811 bm-a] "' + CRLF + "          " + vmap_fix(claim169, "claim") + CRLF + '          "+ T-141 s2 "'

# --- text-level assertions (shared by dry-run and apply) ----------------------
def text_asserts(pf2: str, n2: str, blk2: str):
    # r773 pit law leg 3: full-file start>end malformed-window scans
    for path, txt in ((PF, pf2), (N1, n2)):
        bad = [mm.group() for mm in re.finditer(r"(\d{3})_(\d{3})\.\.(\d{3})_(\d{3})", txt)
               if int(mm.group(3)) < int(mm.group(1))]
        assert not bad, f"malformed windows remain in {path}: {bad[:4]}"
    # W171 projection prose present in the new W170 blocks (probe leg4 verbatim)
    assert f"# {W171p_A} CLEAN hops=0 / B first-clean {W171p_B}" in pf2, "pf W171p prose missing"
    assert "W171 A window; W171 freezer MUST re-derive on the post-W170" in pf2, \
        "pf W171 freezer prose missing"
    # r776 fragment-needle law: the freezer prose in the n1 entry is split
    # across python-string fragments -- a contiguous needle is a false-negative
    # (r775/r781 law); assert the within-fragment shapes instead.
    assert '"W171 A window; W171 freezer MUST re-derive on the "' in n2, "n1 W171 freezer fragment missing"
    assert '"W170 B band 390_804..391_003 will refuse the naive "' in n2, "n1 W170-band refuse fragment missing"
    assert f"A first-clean {W171p_A} " in n2 and f"B first-clean {W171p_B} CLEAN" in n2, \
        "n1 W171p prose missing"
    # honesty faces landed (deferred self-ack truth + 4-item payload +
    # single-window derive)
    assert "move DEFERRED to the W170 finalize window -- the W170 seat" in pf2, "pf self-ack fixup missing"
    assert "MSG sits in fleet/inbox/ at freeze time (honest deferred);" in pf2, "pf self-ack tail fixup missing"
    assert "move DEFERRED to the W170 finalize window -- the W170 seat MSG" in n2, "mat self-ack fixup missing"
    assert "sits in fleet/inbox/ at freeze time (honest deferred)." in n2, "mat self-ack tail missing"
    assert "payload = seat MSG + pre-seat probe script + probe receipt + the" in pf2, "pf 4-item payload fixup missing"
    assert '"seat MSG + pre-seat probe script + probe receipt + the W169 finalize product (4-item, W146 precedent); "' in n2, \
        "entry 4-item payload fixup missing"
    assert "= seat MSG + pre-seat probe script + probe receipt + the W169" in n2, "mat 4-item payload fixup missing"
    assert "# single-window derive (r812 merged the gate legs INTO the" in pf2, "pf single-window fixup missing"
    assert '"--no-verify; single-window derive -- r812 merged the gate "' in n2, "entry single-window frag1 missing"
    assert '"legs INTO the pre-seat probe; parity N/A honest), "' in n2, "entry single-window frag2 missing"
    assert "r812 pre-seat" in pf2 and "r812 pre-seat" in n2, "push session r812 face missing"
    assert "direct fast-forward behind-0" in pf2 and "direct fast-forward behind-0" in n2, \
        "direct-FF delivery face missing"
    assert "0f00fa424" in pf2 and "0f00fa424" in n2, "TRUE seat-push sha face missing"
    # r776 fragment-needle law: the registered-row citation is split across
    # python string fragments -- assert the within-fragment shapes
    assert '"number law after the REGISTERED W169 row bm-a r811 freeze "' in n2, \
        "W169 row citation frag1 missing"
    assert '"9c2271baf, SINGLE STATE zero seat gap W2..W169 all "' in n2, \
        "W169 row citation frag2 missing"
    assert '"finalize one-pass bm-a r812, net chain head 777,212, "' in n2, \
        "W169 finalize one-pass frag missing"
    # r781 fragment law: the contiguous logical string 'W169 finalize one-pass
    # bm-a r812' physically splits across python string fragments -- count the
    # within-fragment shapes instead (mat 1 + entry tail 1 == 2)
    assert n2.count("finalize one-pass bm-a r812") == 2, "W169 finalize one-pass count drift"
    assert "bm-a r811 freeze 9c2271baf" in n2, "mat header registered-row citation missing"
    assert "8d8842b61" not in blk2, "stale W168 sha residue in new W170 block"
    assert "finalize one-pass bm-a r813" not in n2, "stale r813 finalize residue"
    # the NEW W170 claim carries the rolled session attribution (the W169
    # claim's r811 attribution was correct; r307 keeps the W169 frozen claim's
    # own tail untouched)
    assert '"r813 bm-a] "' in n2, "W170 claim r813 attribution missing"
    # no stale round/seat/number leftovers in the NEW W170 blocks only (the
    # frozen W169/W168 faces legitimately retain their historical citations;
    # the mat CHAIN rows are verbatim prior-wave pinned constants (r307) --
    # historical band values there are legitimate, so the mat scan covers
    # only the freshly vmap'd pre (header) + post (band-facts) faces)
    i2 = pf2.find("    # W170 (bm-a r813 freeze")
    j2 = pf2.find(EO, i2) + len(EO)
    newpfblk = pf2[i2:j2]
    k2 = n2.find('170: {"batch"')
    m2 = n2.find(EO, k2) + len(EO)
    newentry = n2[k2:m2]
    cs2 = n2.find('"+ W170 materializer face')
    ce2 = n2.find('"r813 bm-a] "', cs2) + len('"r813 bm-a] "')
    newclaim = n2[cs2:ce2]
    ci2 = blk2.find("assert pf.N1_BANDS[138]")
    cj2 = blk2.find("# prior-wave disjointness")
    mat_new_faces = blk2[:ci2] + blk2[cj2:]
    assert i2 > 0 and k2 > 0 and cs2 > 0, "new W170 block anchors missing"
    for tag, seg in (("pf", newpfblk), ("entry", newentry),
                     ("mat", mat_new_faces), ("claim", newclaim)):
        for stale in ("r793 gate", "r796 sec8", "r797 gate", "r799 sec8",
                      "r797 pre-seat", "r801 pre-seat", "r801 gate",
                      "r806 gate", "r806 sec8", "r806 pre-seat",
                      "W166 (bm-a r799", "W167 (bm-a r805", "W168 (bm-a r809",
                      "W169 (bm-a r811",
                      "bm-a r795 freeze", "r795 bm-a freeze",
                      "bm-a r799 freeze", "r799 bm-a freeze",
                      "bm-a r805 freeze", "r805 bm-a freeze",
                      "bm-a r809 freeze", "r809 bm-a freeze",
                      "r811 bm-a freeze",
                      "gate-derived r797", "gate-derived r801", "gate-derived r806",
                      "gate-derived r810",
                      "r810 pre-seat",
                      "MSG-2026-10-06-223x", "MSG-2026-10-07-0259", "MSG-2026-10-07-0547",
                      "ceaf58908", "bcd6e4392", "d1dc12117", "e51edfcbc",
                      "bma-w167-seat", "bma-w168-seat", "bma-w169-seat",
                      "MSG-223x", "MSG-0259", "MSG-0547", "seat MSG-0259 tail",
                      "merge-absorb",
                      "2ea58d762",
                      "386_404", "386_603", "386_604", "386_803", "388_403", "388_603",
                      "768,412", "360,920", "770,612", "363,120", "772,812", "773,212",
                      "775,012", "365,320", "367,520",
                      "aebb94d2d", "c2d6c5e14", "f61835690", "8d8842b61",
                      "f7d34e5a7", "18231a529", "764cd882a", "678a07d4f",
                      "6957f509e", "6ee1207bb", "ee04482a2",
                      "twenty-sixth", "twenty-seventh", "twenty-eighth",
                      "seventy-ninth", "eightieth", "eighty-first", "eighty-second",
                      "eighty-third", "eighty-fourth",
                      "ONE HUNDRED-AND-FIFTY-FIFTH", "ONE HUNDRED-AND-FIFTY-SIXTH",
                      "ONE HUNDRED-AND-FIFTY-SEVENTH", "ONE HUNDRED-AND-FIFTY-EIGHTH",
                      "ONE HUNDRED-AND-FIFTY-NINTH",
                      "engine_owner rows 154", "engine_owner rows 155",
                      "engine_owner rows 156", "engine_owner rows 157",
                      "engine_owner rows 158",
                      "rows 80 + candidate", "rows 81 + candidate",
                      "rows 82 + candidate", "rows 83 + candidate",
                      "rows 84 + candidate",
                      "n1w165", "n1_w165", "n1w166", "n1_w166", "n1w167", "n1_w167",
                      "n1w168", "n1_w168", "n1w169", "n1_w169",
                      "PERPETUAL-N1-W165", "PERPETUAL_N1_W165",
                      "PERPETUAL-N1-W166", "PERPETUAL_N1_W166",
                      "PERPETUAL-N1-W167", "PERPETUAL_N1_W167",
                      "PERPETUAL-N1-W168", "PERPETUAL_N1_W168",
                      "PERPETUAL-N1-W169", "PERPETUAL_N1_W169",
                      "r789 gate", "r790 sec8", "r785 gate", "r786 sec8",
                      "bm-b r798 consumed-archived the", "06:02:52",
                      "facts helper", "arc generator"):
            assert stale not in seg, f"stale {stale!r} residue in new W170 {tag} block"
            # 388_604/388_803 (W169 B band citation) and
            # 388_804/389_003/390_603/390_803/390_804/391_003/392_803/391_004/391_203
            # are NOT in the stale set: they legitimately appear in the new
            # W170 blocks as the W169 B band citation (prior-B refusal band),
            # the own-wave A/B starts-ends and the naive-A/B starts-ends
            # (r787 371_004-precedent note; r793 379_804-precedent note).
            # 9c2271baf is excluded from the entry/claim scans below via the
            # mat-only legitimate face -- see the mat header citation.
    # NOTE stale-scan carve-out: '9c2271baf' legitimately appears in the new
    # entry (registered-row citation) and the mat pre (header citation); it
    # must NOT appear in the pf block or the claim
    assert "9c2271baf" not in newpfblk, "stale registered-row sha in new pf block"
    assert "9c2271baf" not in newclaim, "stale registered-row sha in new claim"
    # corrupted historical faces must remain eradicated from both files
    for path, txt in ((PF, pf2), (N1, n2)):
        assert "362_204..362_003" not in txt and "362_404..360_403" not in txt, \
            f"r772 malformed-window residue in {path}"
    # the W170 B-assert prose cites the W170 jump target 390_804 via the @JB@
    # token (the r787/r793/r805/r809/r811 heal lineage: SINGLE-LIVE
    # materializer face migrates to the newest wave each freeze; git history
    # carries the record)
    assert "own-wave A window reserved jumps to 390_804, first-clean " in blk2, \
        "W170 healed-fragment face missing"
    assert "own-wave A window reserved jumps to 388_604, first-clean" not in blk2, \
        "vmap-leak residue in new block"
    # materializer chain now 138..W169row (n=32)
    w2 = n2.find("# --- W170 materializer face")
    t3 = n2.find("# --- T-141 s2 lane face", w2)
    blk_check = n2[w2:t3]
    chain_rows2 = re.findall(r"assert pf\.N1_BANDS\[(\d+)\]",
                              blk_check[blk_check.find("assert pf.N1_BANDS[138]"):
                                        blk_check.find("# prior-wave disjointness")])
    assert chain_rows2 == [str(x) for x in range(138, 170)], chain_rows2


if DRY:
    # zero-write simulation (r811 dry-run precedent): build the simulated
    # post-edit file contents, AST-parse them, run every text-level assert
    sim_pf = pfsrc.replace(a1, r1n)
    assert sim_pf != pfsrc, "pf simulation no-op"
    sim_n1 = n1src.replace(a2, r2).replace(a3, r3).replace(a4, r4)
    assert sim_n1 != n1src, "n1 simulation no-op"
    ast.parse(sim_pf)
    ast.parse(sim_n1)
    w2 = sim_n1.find("# --- W170 materializer face")
    t3 = sim_n1.find("# --- T-141 s2 lane face", w2)
    blk2 = sim_n1[w2:t3]
    text_asserts(sim_pf, sim_n1, blk2)
    print("DRY-RUN PASS: zero-write simulation -- all stale+prose+AST+"
          "malformed-window+chain asserts green; no file modified")
else:
    # --- apply the four edits ---------------------------------------------------
    edit(PF, [(a1, r1n)])
    edit(N1, [(a2, r2), (a3, r3), (a4, r4)])

    # --- post-edit structural assertions ----------------------------------------
    import importlib
    import perpetual_faces as pf
    importlib.reload(pf)
    assert sorted(pf.N1_BANDS)[-1] == 170 and len(pf.N1_BANDS) == 168, \
        "pf N1_BANDS row-count drift after W170 insert"
    assert pf.N1_BANDS[170] == {"a": (388_804, 390_803),
                                "b_exit": (390_804, 391_003),
                                "engine_owner": "bm-a"}, "W170 row face drift"
    assert pf.N1_BANDS[169] == {"a": (386_604, 388_603),
                                "b_exit": (388_604, 388_803),
                                "engine_owner": "bm-a"}, "W169 row survived (r560 no-replace law)"
    import perpetual_faces_n1 as n1mod
    importlib.reload(n1mod)
    assert n1mod.WAVE_CONFIGS[170]["a_seed_base"] == 388_804 and \
        n1mod.WAVE_CONFIGS[170]["b_exit_seed_base"] == 390_804, "W170 seed bases drift"
    assert n1mod.WAVE_CONFIGS[170]["shard_subdir"] == "n1_w170" and \
        n1mod.WAVE_CONFIGS[170]["out_name"] == "n1_w170_results.json", "W170 path drift"
    assert n1mod.WAVE_CONFIGS[170]["prereg"].startswith("research/PERPETUAL_N1_W170_PREREG.md"), \
        "W170 per-wave prereg citation drift"
    assert os.path.exists(os.path.join("research", "PERPETUAL_N1_W170_PREREG.md")), \
        "W170 per-wave prereg missing on disk"

    pf2 = io.open(PF, encoding="utf-8", newline="").read()
    n2 = io.open(N1, encoding="utf-8", newline="").read()
    w2 = n2.find("# --- W170 materializer face")
    t3 = n2.find("# --- T-141 s2 lane face", w2)
    blk2 = n2[w2:t3]
    text_asserts(pf2, n2, blk2)

    print("post-edit structural assertions PASS: N1_BANDS 168 rows tail W170, "
          "W169 row intact, WAVE_CONFIGS[170] seeded, chain 138..169 n=32, "
          "W171p prose == r812 probe leg4 verbatim, honesty faces landed "
          "(deferred self-ack truth + 4-item payload + single-window derive), "
          "full-file malformed-window scans CLEAN on both files")
