# -*- coding: utf-8 -*-
"""r811 bm-a W169 freeze edits: four insertions (pf N1_BANDS[169] row +
n1 WAVE_CONFIGS[169] entry + n1 W169 materializer block refresh +
n1 PASS snippet claim insertion).

Bloodline: r809 _r809bma_w168_freeze_edits.py machinery (r773 pit law
freeze-editor compliance + r776 fragment-needle law + r781
verify-separation law), W169 facts live-registry-driven:
  - band gate results/_r810bma_w169_band_gate.json rc0 ADMIT
    (A 386_604..388_603 staircase TWENTY-EIGHTH instance E36 hops=1 past
    the registered W168 B band; naive 386_404..388_403 refused at its own
    start by the registered W168 B band 386_404..386_603; B 388_604..388_803
    own-A mutual exclusion hops=1, naive 386_604..386_803);
  - pre-seat probe results/_r810bma_w169_probe_receipt.json ADMIT,
    dual-window parity True (gate leg1 parity_with_probe);
  - seat MSG-2026-10-07-0547-bma-w169-seat published bcd6e4392
    (r810 pre-seat push, r565 law: on origin BEFORE this freeze commit;
    3-item payload seat MSG + probe + probe receipt, deletion-set EMPTY;
    gate leg0b recorded the fetch-time origin tip e51edfcbc = bm-b autofill
    commit, NOT the seat push -- sha corrected this window, honest note);
  - per-wave prereg research/PERPETUAL_N1_W169_PREREG.md (r811 build,
    banned gate ADMIT 0);
  - W168 finalize one-pass r809 abb7c0517: ledger head 775,012, merged
    pool K=367,520 (n1_w168_results.json machine-read);
  - W168 freeze r809 sha 8d8842b61 (the REGISTERED W168 row citation);
  - W170+ projection (gate leg3 verbatim): A first-clean 388_604..390_603
    / B first-clean 388_804..389_003, naive-B-inside-naive-A, the
    registered W169 B band will refuse the naive W170 A window.

r773 pit law compliance:
  (1) full string-face inventory empirically probed BEFORE TOK
      (_r811bma_w169_face_probe.py -- four face dumps + needle-count
      receipt, rc0);
  (2) composite band strings tokenized WHOLE (no bare-seed-prefix
      tokens; every dotted band / seed-base row / jump phrase /
      round-sha composite is a single token; bare 168/167 run LAST);
  (3) post-edit full-file start>end malformed-window regex scan on BOTH
      touched files;
  (4) every projection value re-derived FROM the on-disk gate receipts
      (r587 never-transcribe law);
  (5) r776 fragment-needle law: all needles taken from the PHYSICAL
      probe-dumped shapes (python-string fragments / comment lines,
      CRLF-exact);
  (6) same-window HONESTY FIXUPS (landed direction, corrected THIS
      adoption window): the dead r811 session authored the fixups for a
      DEFERRED state (seat still in fleet/inbox/), but by freeze time
      (this r811 estate-adoption session, 06:4x) bm-b r798 had already
      consumed-archived the W169 seat MSG to fleet/inbox/processed/ at
      06:02:52 (commit 4c397fae1, verified on disk) -- so the mechanical
      vmap roll of the W168-era "move already landed pre-freeze" prose is
      now directionally TRUE; FIXUPS['pf']/['mat'] correct only the false
      attribution/timestamp the roll would carry (bm-c r650 -> bm-b r798,
      03:27:53 -> 06:02:52); the frozen W168 face keeps its historical
      attribution (r307);
  (7) anti-drift composite @REGROW@ (bm-a r809 freeze 8d8842b61) runs
      BEFORE the freeze-session token so the registered-prior-row sha
      pairing can never be torn by the session map;
  (8) lineage constant disclosed: the mat band-facts comment carries
      the template session stamp "law sec.4 W168 row, r795" -- the r795
      has ridden every vmap since the W165 freeze authored the
      band-facts template (r809 verbatim precedent; passed through).

EOL-adaptive (r370 law: CRLF-dominant blocks written CRLF);
needle count==1 (r745); insert-after-last-registered-row (r560);
anchor = predecessor full lines (r580/r781); AST gate after every
edit batch (r580/r781); origin anti-collision pre-check (r530/r687:
fetch + origin carries no W169 registration before this freeze)."""
import ast
import io
import json
import re
import os
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
PF = r"scripts/perpetual_faces.py"
N1 = r"scripts/perpetual_faces_n1.py"
CRLF = "\r\n"

# --- machine-derived facts (r587: read from on-disk receipts) ----------------
gate = json.load(open("results/_r810bma_w169_band_gate.json", encoding="utf-8"))
leg1, leg3 = gate["legs"]["leg1"], gate["legs"]["leg3"]
assert gate["verdict"] == "ADMIT", gate["verdict"]
assert leg1["A"] == [386604, 388603] and leg1["B"] == [388604, 388803], leg1
assert leg1["hops_A"] == 1 and leg1["hops_B"] == 1
assert leg1["ARITH_A"] == [386404, 388403], leg1["ARITH_A"]
assert leg1["B_naive_first_clean"] == [386604, 386803], leg1["B_naive_first_clean"]
assert leg1["parity_with_probe"] is True
probe = json.load(open("results/_r810bma_w169_probe_receipt.json", encoding="utf-8"))
assert probe["verdict"] == "ADMIT" and probe["bands"] == {"A": "386604_388603", "B": "388604_388803"}, probe
w168res = json.load(open("results/perpetual_faces/n1_w168_results.json", encoding="utf-8"))
assert w168res["null_pool_cumulative"]["merged"]["n_values"] == 367520, "W168 merged K drift"
assert w168res["null_pool_cumulative"]["merged"]["n_values"] + 2200 == 369720, "W169 K projection arithmetic"
leg0 = gate["legs"]["leg0"]
assert leg0["rows"] == 166 and leg0["tail"] == "W168" and leg0["ordinal"] == 159 \
    and leg0["bma_ordinal"] == 85, leg0
assert gate["legs"]["leg0b"]["own_seat_on_origin"] is True, "seat leg0b"
assert os.path.exists(os.path.join("research", "PERPETUAL_N1_W169_PREREG.md")), \
    "W169 per-wave prereg missing on disk"
# honesty precondition: the W169 seat MSG has LANDED pre-freeze (bm-b
# r798 consumed-archived it to fleet/inbox/processed at 06:02:52,
# commit 4c397fae1 -> landed state -> FIXUPS correct attribution only)
assert os.path.exists(os.path.join("fleet", "inbox", "processed",
                                   "MSG-2026-10-07-0547-bma-w169-seat.md")), \
    "W169 seat MSG not in fleet/inbox/processed (FIXUPS direction would be wrong)"


def u(s):  # "388604..390603" -> "388_604..390_603"
    def g(part):
        return re.sub(r"(\d)(?=(\d{3})+$)", r"\1_", part)
    a, b = s.split("..")
    return f"{g(a)}..{g(b)}"


W170p_A = u(leg3["W170p_A"])
W170p_B = u(leg3["W170p_B"])
assert W170p_A == "388_604..390_603" and W170p_B == "388_804..389_003", (W170p_A, W170p_B)
assert leg3["W170p_B_lands_inside_W170p_A"] is True

# --- ordered value-map (tokens first, then back-substitution) ---------------
TOK = [
    # whole-line seed-base rows (entry face; bands + ordinal carried WHOLE)
    ('"a_seed_base": 384_404,        # law sec.4 W168 A: 384_404..386_403 (FIRST-CLEAN past the registered W167 B band; arithmetic 384_204..386_203 REFUSED at own start by the W167 B band; hops=1; A-hops-prior-B staircase twenty-seventh instance, E36 card)', "@ASROW@"),
    ('"b_exit_seed_base": 386_404,   # law sec.4 W168 B: 386_404..386_603 (FIRST-CLEAN past the own-wave A window; arithmetic 384_404..384_603 lands inside own-A, same-freeze mutual exclusion W141 precedent; reserved walk hops=1; B base == own-A tail+1)', "@BSROW@"),
    # row + entry carriers
    ('168: {"a": (384_404, 386_403), "b_exit": (386_404, 386_603),', "@RROW@"),
    ('168: {"batch"', "@RENTRY@"),
    # registered-prior-row citations (machine-verified sha pairing; the
    # anti-drift composite -- MUST precede every session/round token)
    ('W167 row bm-a r805 freeze', "@PROW1@"),
    ('f61835690, SINGLE STATE zero seat gap W2..W167 all', "@PROW2@"),
    ('bm-a r805 freeze f61835690', "@REGROW@"),
    # freeze-session composites (this window: bm-a r811 freeze)
    ('bm-a r809 freeze', "@FZH@"),
    ('r809 bm-a freeze', "@MFZH@"),
    # claim-tail session attribution (the W168 claim carries the correct
    # r809 attribution; the NEW W169 claim rolls it to the r811 freeze
    # session via this token)
    ('r809 bm-a] ', "@CLMS@"),
    # prior-finalize citations (W168 finalize one-pass landed r809
    # abb7c0517; FRAGMENT form per r781/r776 law where physically split)
    ('W167 finalize landed same-window r806', "@FW@"),
    ('finalize one-pass bm-a r806', "@FOPM2@"),
    ('W167 bm-a r806 one-pass', "@FOP@"),
    # gate / probe receipt citations (W169 receipts)
    ('_r806bma_w168_probe_receipt.json', "@PRC@"),
    ('_r806bma_w168_band_gate.json', "@BGR@"),
    # prior gate / sec8 session refs (W167 gate r801 -> cited as r806;
    # W167 sec8 r806 -> cited as r811: the W168 sec8 succession face
    # was backfilled THIS window r811 (W159 overdue-settle precedent))
    ('r801 gate leg3', "@GATE@"),
    ('r801 gate', "@GATEP@"),
    ('r806 sec8 succession', "@SEC8@"),
    ('r806 sec8', "@SEC8M@"),
    # own-wave gate-session prose + pre-seat push session (r806 -> r810)
    ('gate-derived r806', "@GDR@"),
    ('r806 pre-seat push', "@PSP@"),
    # seat tokens (W168 seat 0259/ceaf58908 -> W169 seat 0547/bcd6e4392;
    # bcd6e4392 = the TRUE r810 seat-push commit -- gate leg0b recorded
    # fetch-time origin tip e51edfcbc which is a bm-b autofill commit,
    # sha corrected this window with honest note)
    ('MSG-2026-10-07-0259', "@SEAT@"),
    ('bma-w168-seat', "@SEATW@"),
    ('MSG-0259', "@MSGS@"),
    ('ceaf58908', "@SEATSHA@"),
    # W170 projection bands (gate leg3 verbatim, whole; BEFORE all band
    # tokens and seed backstops -- r773 pit law)
    ('386_404..388_403', "@PA@"),
    ('386_604..386_803', "@PB@"),
    # jump phrases (longest first; fragment-safe; BEFORE @BB@ which
    # shares the B-band substring)
    ('jumps to 386_404, first-clean 386_404..386_603 hops=1', "@JN@"),
    ('jumps to 386_404 -> 386_404..386_603,', "@JP@"),
    ('386_404 and lands 386_404..386_603', "@JAND@"),
    # the W169 B-assert jump fragment (rides the @JB@ token; W169 target
    # 388_604 -- the r787/r793/r805/r809 heal lineage, leak class killed)
    ('own-wave A window reserved jumps to 386_404, first-clean ', "@JB@"),
    # assert composites
    ('== 384_404 == 384_403 + 1', "@ASB@"),
    ('== 386_404 == 386_403 + 1', "@BSB@"),
    ('set(range(384_404, 386_404))', "@ARITHA@"),
    ('set(range(386_404, 386_604))', "@ARB@"),
    # dotted band geometry
    ('384_204..386_203', "@NA@"),
    ('384_204..384_403', "@OB@"),
    ('384_404..386_403', "@AB@"),
    ('384_404..384_603', "@NB@"),
    ('386_404..386_603', "@BB@"),
    # base-relation composites
    ('384_403+1', "@ABASE@"),
    ('386_403+1', "@BBASE@"),
    # identity / stats / ordinals
    ('PERPETUAL_N1_W168_PREREG.md', "@PF@"),
    ('PERPETUAL-N1-W168', "@B@"),
    ('n1_w168_results.json', "@OD@"),
    ('n1_w168', "@SD@"),
    ('n1w168', "@SD2@"),
    ('772,812', "@LEDG@"),
    ('365,320', "@K1@"),
    ('ONE HUNDRED-AND-FIFTY-EIGHTH', "@ORDW@"),
    ('engine_owner rows 157', "@R154@"),
    ('rows 83 + candidate', "@ROWS80@"),
    ('eighty-third', "@SVN@"),
    ('twenty-seventh', "@ST24@"),
    # wave numbers (higher first: W169 projection -> W170; then W168->W169,
    # W167->W168)
    ('W169', "@WN2@"),
    ('W168', "@WN@"),
    ('W167', "@W@"),
    # bare round backstop (r776 fragment law: the physical W168 faces
    # break 'r806 pre-seat' + CRLF + '# push' across comment lines in the
    # pf block -- the exact-phrase TOK above cannot match it; every other
    # r806 face is already carried by composite tokens, so the bare roll
    # r806->r810 is safe; runs BEFORE the bare numerals)
    ('r806', "@RB@"),
    # bare numerals LAST (every longer carrier tokenized above; 168 before
    # 167 so the 167->168 output is never re-mapped)
    ('168', "@IDX@"),
    ('167', "@IDX2@"),
]
BACK = [
    ("@ASROW@", '"a_seed_base": 386_604,        # law sec.4 W169 A: 386_604..388_603 (FIRST-CLEAN past the registered W168 B band; arithmetic 386_404..388_403 REFUSED at own start by the W168 B band; hops=1; A-hops-prior-B staircase twenty-eighth instance, E36 card)'),
    ("@BSROW@", '"b_exit_seed_base": 388_604,   # law sec.4 W169 B: 388_604..388_803 (FIRST-CLEAN past the own-wave A window; arithmetic 386_604..386_803 lands inside own-A, same-freeze mutual exclusion W141 precedent; reserved walk hops=1; B base == own-A tail+1)'),
    ("@RROW@", '169: {"a": (386_604, 388_603), "b_exit": (388_604, 388_803),'),
    ("@RENTRY@", '169: {"batch"'),
    ("@PROW1@", "W168 row bm-a r809 freeze"),
    ("@PROW2@", "8d8842b61, SINGLE STATE zero seat gap W2..W168 all"),
    ("@REGROW@", "bm-a r809 freeze 8d8842b61"),
    ("@FZH@", "bm-a r811 freeze"),
    ("@MFZH@", "r811 bm-a freeze"),
    ("@CLMS@", "r811 bm-a] "),
    ("@FW@", "W168 finalize landed same-window r809"),
    ("@FOPM2@", "finalize one-pass bm-a r809"),
    ("@FOP@", "W168 bm-a r809 one-pass"),
    ("@PRC@", "_r810bma_w169_probe_receipt.json"),
    ("@BGR@", "_r810bma_w169_band_gate.json"),
    ("@GATE@", "r806 gate leg3"),
    ("@GATEP@", "r806 gate"),
    ("@SEC8@", "r811 sec8 succession"),
    ("@SEC8M@", "r811 sec8"),
    ("@GDR@", "gate-derived r810"),
    ("@PSP@", "r810 pre-seat push"),
    ("@SEAT@", "MSG-2026-10-07-0547"),
    ("@SEATW@", "bma-w169-seat"),
    ("@MSGS@", "MSG-0547"),
    ("@SEATSHA@", "bcd6e4392"),
    ("@PA@", "388_604..390_603"),
    ("@PB@", "388_804..389_003"),
    ("@JN@", "jumps to 388_604, first-clean 388_604..388_803 hops=1"),
    ("@JP@", "jumps to 388_604 -> 388_604..388_803,"),
    ("@JAND@", "388_604 and lands 388_604..388_803"),
    ("@JB@", "own-wave A window reserved jumps to 388_604, first-clean "),
    ("@ASB@", "== 386_604 == 386_603 + 1"),
    ("@BSB@", "== 388_604 == 388_603 + 1"),
    ("@ARITHA@", "set(range(386_604, 388_604))"),
    ("@ARB@", "set(range(388_604, 388_804))"),
    ("@NA@", "386_404..388_403"),
    ("@OB@", "386_404..386_603"),
    ("@AB@", "386_604..388_603"),
    ("@NB@", "386_604..386_803"),
    ("@BB@", "388_604..388_803"),
    ("@ABASE@", "386_603+1"),
    ("@BBASE@", "388_603+1"),
    ("@PF@", "PERPETUAL_N1_W169_PREREG.md"),
    ("@B@", "PERPETUAL-N1-W169"),
    ("@OD@", "n1_w169_results.json"),
    ("@SD@", "n1_w169"),
    ("@SD2@", "n1w169"),
    ("@LEDG@", "775,012"),
    ("@K1@", "367,520"),
    ("@ORDW@", "ONE HUNDRED-AND-FIFTY-NINTH"),
    ("@R154@", "engine_owner rows 158"),
    ("@ROWS80@", "rows 84 + candidate"),
    ("@SVN@", "eighty-fourth"),
    ("@ST24@", "twenty-eighth"),
    ("@WN2@", "W170"),
    ("@WN@", "W169"),
    ("@W@", "W168"),
    ("@RB@", "r810"),
    ("@IDX@", "169"),
    ("@IDX2@", "168"),
]
# r587 belt-and-braces: the projection BACK values must equal the
# machine-derived gate leg3 strings verbatim
assert ("@PA@", W170p_A) in BACK and ("@PB@", W170p_B) in BACK


def vmap(s: str) -> str:
    for a, b in TOK:
        s = s.replace(a, b)
    for a, b in BACK:
        s = s.replace(a, b)
    return s


# --- per-kind fragment-level fixups (r776 law: needles taken from the
# PHYSICAL probe-dumped shapes; applied AFTER vmap) ---------------------------
# Honesty fixups (landed direction, corrected this adoption window):
# the seat HAS landed pre-freeze (bm-b r798 archive 06:02:52, commit
# 4c397fae1), so the rolled landed prose is TRUE -- only its attribution
# is stale (the vmap carries the W168-era "bm-c r650 ... 03:27:53"
# wording); correct both faces to the true mover + timestamp.
FIXUPS = {
    "pf": [
        ("bm-c r650 consumed-archived the",
         "bm-b r798 consumed-archived the"),
        ("03:27:53 -- honest state);",
         "06:02:52 -- honest state);"),
    ],
    "mat": [
        ("bm-c r650 consumed-archived the",
         "bm-b r798 consumed-archived the"),
        ("03:27:53 -- honest state).",
         "06:02:52 -- honest state)."),
    ],
}


def vmap_fix(s: str, kind: str) -> str:
    s = vmap(s)
    if kind == "claim" or kind not in FIXUPS:
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

# face-source zero-drift gate vs the r811 probe dumps
EO = '"engine_owner": "bm-a"},'
i1 = pfsrc.find("    # W168 (bm-a r809 freeze")
assert i1 > 0, "pf W168 comment block not found"
r1 = pfsrc.find('168: {"a": (384_404', i1)
assert r1 > i1, "pf W168 row not after comment block"
j1 = pfsrc.find(EO, r1) + len(EO)
block168_pf = pfsrc[i1:j1]
assert block168_pf == io.open(r"results\_r811bma_w169_probe_pf_block.txt",
                             encoding="utf-8", newline="").read(), "pf face drift vs probe"
assert block168_pf.count("engine_owner") == 1 and "f61835690" not in block168_pf
assert "384_204..386_203 REFUSED at its own start by the W167 B band" in block168_pf

# pre-edit live registry parity (the W168 registered row must be intact
# before we append the W169 row -- r560 no-replace law)
sys.path.insert(0, ".")
sys.path.insert(0, "scripts")
import perpetual_faces as pfpre
assert pfpre.N1_BANDS[168] == {"a": (384_404, 386_403),
                               "b_exit": (386_404, 386_603),
                               "engine_owner": "bm-a"}, "pre-edit W168 row drift"
assert sorted(pfpre.N1_BANDS)[-1] == 168 and len(pfpre.N1_BANDS) == 166, "pre-edit row count"

# origin anti-collision pre-check (r530 never-dry + r687 dual-scan:
# fetch fresh, origin must carry no W169 registration before this freeze)
subprocess.run(["git", "fetch", "origin"], capture_output=True)
_r = subprocess.run(["git", "show", "origin/main:scripts/perpetual_faces.py"],
                    capture_output=True)
_op = _r.stdout.decode("utf-8", "replace")
assert _r.returncode == 0, "origin pf.py read failed"
assert '169: {"a"' not in _op, "origin already carries a W169 registration (r687 dual-scan)"
assert "# W169 (bm-a" not in _op, "origin already carries a W169 freeze block"
_r2 = subprocess.run(["git", "rev-list", "--count", "origin/main..HEAD"],
                     capture_output=True, text=True)
assert _r2.stdout.strip() == "0", f"local ahead of origin: {_r2.stdout.strip()} (behind-law)"

# --- a1: pf.py W168 comment block + row -> append W169 comment block + row ----
a1 = block168_pf + CRLF + "}"
r1n = block168_pf + CRLF + vmap_fix(block168_pf, "pf") + CRLF + "}"

# --- a2: n1.py WAVE_CONFIGS entry ----------------------------------------------
k = n1src.find('168: {"batch"')
assert k > 0, "n1 W168 entry not found"
m = n1src.find(EO, k) + len(EO)
entry168 = n1src[k:m]
assert entry168 == io.open(r"results\_r811bma_w169_probe_n1_entry.txt",
                          encoding="utf-8", newline="").read(), "entry face drift vs probe"
a2 = entry168 + CRLF + "                       }"
r2 = entry168 + CRLF + "                       " + vmap_fix(entry168, "n1entry") + CRLF + "                       }"

# --- a3: materializer block (chain split-verbatim + one-row extension) --------
w = n1src.find("# --- W168 materializer face")
t2 = n1src.find("# --- T-141 s2 lane face", w)
assert 0 < w < t2, "materializer anchors missing"
block = n1src[w:t2]
assert block == io.open(r"results\_r811bma_w169_probe_n1_mat.txt",
                        encoding="utf-8", newline="").read(), "mat face drift vs probe"
ci = block.find("assert pf.N1_BANDS[138]")
cj = block.find("# prior-wave disjointness")
assert 0 < ci < cj, "chain boundaries missing"
pre, chain, post = block[:ci], block[ci:cj], block[cj:]
chain_rows = re.findall(r"assert pf\.N1_BANDS\[(\d+)\]", chain)
assert chain_rows == [str(x) for x in range(138, 168)], chain_rows
w168row = ('assert pf.N1_BANDS[168] == {"a": (384_404, 386_403),' + CRLF +
           '                                    "b_exit": (386_404, 386_603),' + CRLF +
           '                                    "engine_owner": "bm-a"}, \\' + CRLF +
           '            "registered W168 row parity drift (r307; bm-a r809)"' + CRLF +
           "        ")
# delivery/payload prose lives ONLY in the mat pre (header comment face);
# the post (disjointness/band-facts/assert face) passes through plain vmap
block169 = vmap_fix(pre, "mat") + chain + w168row + vmap(post)
a3 = block + "# --- T-141 s2 lane face"
r3 = block169 + "# --- T-141 s2 lane face"

# --- a4: PASS snippet claim insertion ------------------------------------------
cs = n1src.find('"+ W168 materializer face')
assert cs > 0, "W168 claim start not found"
ce = n1src.find('"r809 bm-a] "', cs) + len('"r809 bm-a] "')
assert 0 < cs < ce, "W168 claim end not found"
claim168 = n1src[cs:ce]
assert claim168 == io.open(r"results\_r811bma_w169_probe_n1_claim.txt",
                           encoding="utf-8", newline="").read(), "claim face drift vs probe"
a4 = '"r809 bm-a] "' + CRLF + '          "+ T-141 s2 "'
r4 = '"r809 bm-a] "' + CRLF + "          " + vmap_fix(claim168, "claim") + CRLF + '          "+ T-141 s2 "'

# --- apply the four edits -------------------------------------------------------
edit(PF, [(a1, r1n)])
edit(N1, [(a2, r2), (a3, r3), (a4, r4)])

# --- post-edit structural assertions --------------------------------------------
import importlib
import perpetual_faces as pf
importlib.reload(pf)
assert sorted(pf.N1_BANDS)[-1] == 169 and len(pf.N1_BANDS) == 167, \
    "pf N1_BANDS row-count drift after W169 insert"
assert pf.N1_BANDS[169] == {"a": (386_604, 388_603),
                            "b_exit": (388_604, 388_803),
                            "engine_owner": "bm-a"}, "W169 row face drift"
assert pf.N1_BANDS[168] == {"a": (384_404, 386_403),
                            "b_exit": (386_404, 386_603),
                            "engine_owner": "bm-a"}, "W168 row survived (r560 no-replace law)"
import perpetual_faces_n1 as n1mod
importlib.reload(n1mod)
assert n1mod.WAVE_CONFIGS[169]["a_seed_base"] == 386_604 and \
    n1mod.WAVE_CONFIGS[169]["b_exit_seed_base"] == 388_604, "W169 seed bases drift"
assert n1mod.WAVE_CONFIGS[169]["shard_subdir"] == "n1_w169" and \
    n1mod.WAVE_CONFIGS[169]["out_name"] == "n1_w169_results.json", "W169 path drift"
assert n1mod.WAVE_CONFIGS[169]["prereg"].startswith("research/PERPETUAL_N1_W169_PREREG.md"), \
    "W169 per-wave prereg citation drift"
assert os.path.exists(os.path.join("research", "PERPETUAL_N1_W169_PREREG.md")), \
    "W169 per-wave prereg missing on disk"

# materializer chain now 138..W168row (n=31)
n2 = io.open(N1, encoding="utf-8", newline="").read()
w2 = n2.find("# --- W169 materializer face")
t3 = n2.find("# --- T-141 s2 lane face", w2)
blk2 = n2[w2:t3]
chain_rows2 = re.findall(r"assert pf\.N1_BANDS\[(\d+)\]",
                         blk2[blk2.find("assert pf.N1_BANDS[138]"):
                              blk2.find("# prior-wave disjointness")])
assert chain_rows2 == [str(x) for x in range(138, 169)], chain_rows2

# r773 pit law leg 3: full-file start>end malformed-window scans on BOTH files
for path in (PF, N1):
    txt = io.open(path, encoding="utf-8", newline="").read()
    bad = [m.group() for m in re.finditer(r"(\d{3})_(\d{3})\.\.(\d{3})_(\d{3})", txt)
           if int(m.group(3)) < int(m.group(1))]
    assert not bad, f"malformed windows remain in {path}: {bad[:4]}"

# W170 projection prose present in the new W169 blocks (gate leg3 verbatim)
pf2 = io.open(PF, encoding="utf-8", newline="").read()
assert f"# {W170p_A} CLEAN hops=0 / B first-clean {W170p_B}" in pf2, "pf W170p prose missing"
assert "W170 A window; W170 freezer MUST re-derive on the post-W169" in pf2, \
    "pf W170 freezer prose missing"
# r776 fragment-needle law: the freezer prose in the n1 entry is split
# across python-string fragments -- a contiguous needle is a false-negative
# (r775/r781 law); assert the within-fragment shapes instead.
assert '"W170 A window; W170 freezer MUST re-derive on the "' in n2, "n1 W170 freezer fragment missing"
assert '"W169 B band 388_604..388_803 will refuse the naive "' in n2, "n1 W169-band refuse fragment missing"
assert f"A first-clean {W170p_A} " in n2 and f"B first-clean {W170p_B} CLEAN" in n2, \
    "n1 W170p prose missing"
# honesty faces landed (self-ack LANDED truth with TRUE mover bm-b r798
# + timestamp 06:02:52 + 3-item payload +
# direct-FF delivery + anti-drift registered-row citation + TRUE seat sha)
assert "bm-b r798 consumed-archived the" in pf2, "pf self-ack fixup missing"
assert "06:02:52 -- honest state);" in pf2, "pf self-ack tail fixup missing"
assert "bm-b r798 consumed-archived the" in n2, "mat self-ack fixup missing"
assert "06:02:52 -- honest state)." in n2, "mat self-ack tail missing"
assert "payload = seat MSG + pre-seat probe + probe receipt;" in pf2, "pf 3-item payload fixup missing"
assert '"seat MSG + pre-seat probe + probe receipt; "' in n2, "entry 3-item payload fixup missing"
assert "= seat MSG + pre-seat probe + probe receipt;" in n2, "mat 3-item payload fixup missing"
assert "r810 pre-seat" in pf2 and "r810 pre-seat" in n2, "push session r810 face missing"
assert "direct fast-forward behind-0" in pf2 and "direct fast-forward behind-0" in n2, \
    "direct-FF delivery face missing"
assert "bcd6e4392" in pf2 and "bcd6e4392" in n2, "TRUE seat-push sha face missing"
# r776 fragment-needle law: the registered-row citation is split across
# python string fragments -- assert the within-fragment shapes
assert '"number law after the REGISTERED W168 row bm-a r809 freeze "' in n2, \
    "W168 row citation frag1 missing"
assert '"8d8842b61, SINGLE STATE zero seat gap W2..W168 all "' in n2, \
    "W168 row citation frag2 missing"
assert '"finalize one-pass bm-a r809, net chain head 775,012, "' in n2, \
    "W168 finalize one-pass frag missing"
# r781 fragment law: the contiguous logical string 'W168 finalize one-pass
# bm-a r809' physically splits across python string fragments -- count the
# within-fragment shapes instead (mat 1 + entry tail 1 == 2)
assert n2.count("finalize one-pass bm-a r809") == 2, "W168 finalize one-pass count drift"
assert "bm-a r809 freeze 8d8842b61" in n2, "mat header registered-row citation missing"
assert "f61835690" not in blk2, "stale W167 sha residue in new W169 block"
assert "finalize one-pass bm-a r811" not in n2, "stale r811 finalize residue"
# the NEW W169 claim carries the rolled session attribution (the W168
# claim's r809 attribution was correct; r307 keeps the W168 frozen claim's
# own tail untouched)
assert '"r811 bm-a] "' in n2, "W169 claim r811 attribution missing"
# no stale round/seat/number leftovers in the NEW W169 blocks only (the
# frozen W168/W167 faces legitimately retain their historical citations;
# the mat CHAIN rows are verbatim prior-wave pinned constants (r307) --
# historical band values there are legitimate, so the mat scan covers
# only the freshly vmap'd pre (header) + post (band-facts) faces)
i2 = pf2.find("    # W169 (bm-a r811 freeze")
j2 = pf2.find(EO, i2) + len(EO)
newpfblk = pf2[i2:j2]
k2 = n2.find('169: {"batch"')
m2 = n2.find(EO, k2) + len(EO)
newentry = n2[k2:m2]
cs2 = n2.find('"+ W169 materializer face')
ce2 = n2.find('"r811 bm-a] "', cs2) + len('"r811 bm-a] "')
newclaim = n2[cs2:ce2]
ci2 = blk2.find("assert pf.N1_BANDS[138]")
cj2 = blk2.find("# prior-wave disjointness")
mat_new_faces = blk2[:ci2] + blk2[cj2:]
assert i2 > 0 and k2 > 0 and cs2 > 0, "new W169 block anchors missing"
for tag, seg in (("pf", newpfblk), ("entry", newentry),
                 ("mat", mat_new_faces), ("claim", newclaim)):
    for stale in ("r793 gate", "r796 sec8", "r797 gate", "r799 sec8",
                  "r797 pre-seat", "r801 pre-seat", "r801 gate",
                  "W166 (bm-a r799", "W167 (bm-a r805", "W168 (bm-a r809",
                  "bm-a r795 freeze", "r795 bm-a freeze",
                  "bm-a r799 freeze", "r799 bm-a freeze",
                  "bm-a r805 freeze", "r805 bm-a freeze",
                  "MSG-2026-10-06-223x", "MSG-2026-10-07-0259", "ceaf58908",
                  "d1dc12117", "bma-w167-seat", "bma-w168-seat", "MSG-223x",
                  "MSG-0259", "seat MSG-0259 tail", "merge-absorb",
                  "gate-derived r797", "gate-derived r801", "gate-derived r806",
                  "r806 pre-seat", "r806 sec8",
                  # NOTE "r806 gate" deliberately NOT stale: the @GATE@
                  # back-substitution legitimately produces "r806 gate
                  # leg3" (the PRIOR-wave W168 gate citation in the new
                  # W169 succession prose -- W168's gate DID run r806);
                  # sources carry zero un-rolled own-wave "r806 gate"
                  # faces (dry-run _r812bma_w169_freeze_dryrun.py proof),
                  # so this entry was a post-edit false positive in the
                  # dead r811 draft; "r806 pre-seat"/"r806 sec8" keep
                  # their stale status (own-wave refs must roll to r810)
                  "e51edfcbc",
                  "382_004", "382_203", "382_204", "382_403",
                  "384_003", "384_203", "384_204", "384_403",
                  "384_404", "384_603", "386_203",
                  "768,412", "360,920", "770,612", "363,120", "772,812",
                  "365,320", "aebb94d2d", "c2d6c5e14", "f61835690",
                  "f7d34e5a7", "18231a529", "764cd882a", "678a07d4f",
                  "6957f509e", "6ee1207bb", "ee04482a2",
                  "twenty-sixth", "twenty-seventh",
                  "seventy-ninth", "eightieth", "eighty-first", "eighty-second",
                  "eighty-third",
                  "ONE HUNDRED-AND-FIFTY-FIFTH", "ONE HUNDRED-AND-FIFTY-SIXTH",
                  "ONE HUNDRED-AND-FIFTY-SEVENTH", "ONE HUNDRED-AND-FIFTY-EIGHTH",
                  "engine_owner rows 154", "engine_owner rows 155",
                  "engine_owner rows 156", "engine_owner rows 157",
                  "rows 80 + candidate", "rows 81 + candidate",
                  "rows 82 + candidate", "rows 83 + candidate",
                  "n1w165", "n1_w165", "n1w166", "n1_w166", "n1w167", "n1_w167",
                  "n1w168", "n1_w168",
                  "PERPETUAL-N1-W165", "PERPETUAL_N1_W165",
                  "PERPETUAL-N1-W166", "PERPETUAL_N1_W166",
                  "PERPETUAL-N1-W167", "PERPETUAL_N1_W167",
                  "PERPETUAL-N1-W168", "PERPETUAL_N1_W168",
                  "r789 gate", "r790 sec8", "r785 gate", "r786 sec8",
                  "facts helper", "arc generator"):
        assert stale not in seg, f"stale {stale!r} residue in new W169 {tag} block"
        # 386_404/386_603/386_604/386_803/388_403/388_603/388_604/388_803 are
        # NOT in the stale set: they legitimately appear in the new W169
        # blocks as the W168 B band citation (prior-B refusal band), the
        # own-wave A/B starts-ends and the naive-A/B starts-ends (r787
        # 371_004-precedent note; r793 379_804-precedent note)
# corrupted historical faces must remain eradicated from both files
for path in (PF, N1):
    txt = io.open(path, encoding="utf-8", newline="").read()
    assert "362_204..362_003" not in txt and "362_404..360_403" not in txt, \
        f"r772 malformed-window residue in {path}"
# the W169 B-assert prose cites the W169 jump target 388_604 via the @JB@
# token (the r787/r793/r805/r809 heal lineage: SINGLE-LIVE materializer
# face migrates to the newest wave each freeze; git history carries the record)
assert "own-wave A window reserved jumps to 388_604, first-clean " in blk2, \
    "W169 healed-fragment face missing"
assert "own-wave A window reserved jumps to 386_404, first-clean" not in blk2, \
    "vmap-leak residue in new block"

print("post-edit structural assertions PASS: N1_BANDS 167 rows tail W169, "
      "W168 row intact, WAVE_CONFIGS[169] seeded, chain 138..168 n=31, "
      "W170p prose == r810 gate leg3 verbatim, honesty faces landed "
      "(self-ack LANDED truth, mover=bm-b r798, ts=06:02:52 / 3-item "
      "payload / direct-FF delivery / anti-drift registered-row cite / "
      "TRUE seat sha bcd6e4392 / @CLMS@ claim r811 attribution), "
      "full-file malformed-window scans CLEAN on both files, "
      "same-window FIXUPS applied (W169 seat in fleet/inbox/processed "
      "at freeze time = honest landed state)")
