# -*- coding: utf-8 -*-
"""r809 bm-a W168 freeze edits: four insertions (pf N1_BANDS[168] row +
n1 WAVE_CONFIGS[168] entry + n1 W168 materializer block refresh +
n1 PASS snippet claim insertion).

Bloodline: r805 _r805bma_w167_freeze_edits.py machinery (r773 pit law
freeze-editor compliance + r776 fragment-needle law + r781
verify-separation law), W168 facts live-registry-driven:
  - band gate results/_r806bma_w168_band_gate.json rc0 ADMIT
    (A 384_404..386_403 staircase TWENTY-SEVENTH instance E36 hops=1 past
    the registered W167 B band; naive 384_204..386_203 refused at its own
    start by the registered W167 B band 384_204..384_403; B 386_404..386_603
    own-A mutual exclusion hops=1, naive 384_404..384_603);
  - pre-seat probe results/_r806bma_w168_probe_receipt.json ADMIT,
    dual-window parity True (gate leg1 parity_with_probe);
  - seat MSG-2026-10-07-0259-bma-w168-seat published ceaf58908
    (r806 pre-seat push, r565 law: on origin BEFORE this freeze commit;
    3-item payload seat MSG + probe + probe receipt, deletion-set EMPTY);
  - per-wave prereg research/PERPETUAL_N1_W168_PREREG.md (r807 xform build,
    landed origin via r808, banned gate ADMIT 0);
  - W167 finalize one-pass r806: ledger head 772,812, merged pool
    K=365,320 (n1_w167_results.json machine-read);
  - W167 freeze r805 sha f61835690 (the REGISTERED W167 row citation);
  - W169+ projection (gate leg3 verbatim): A first-clean 386_404..388_403
    / B first-clean 386_604..386_803, naive-B-inside-naive-A, the
    registered W168 B band will refuse the naive W169 A window.

r773 pit law compliance:
  (1) full string-face inventory empirically probed BEFORE TOK
      (_r809bma_w168_face_probe.py -- four face dumps + needle-count
      receipt, rc0);
  (2) composite band strings tokenized WHOLE (no bare-seed-prefix
      tokens; every dotted band / seed-base row / jump phrase /
      round-sha composite is a single token; bare 167/166 run LAST);
  (3) post-edit full-file start>end malformed-window regex scan on BOTH
      touched files;
  (4) every projection value re-derived FROM the on-disk gate receipts
      (r587 never-transcribe law);
  (5) r776 fragment-needle law: all needles taken from the PHYSICAL
      probe-dumped shapes (python-string fragments / comment lines,
      CRLF-exact);
  (6) same-window FIXUPS (honesty face): the W168 seat MSG was
      consumed-archived to fleet/inbox/processed by bm-c r650 at
      03:27:53 BEFORE this freeze window -- the mechanical vmap roll of
      the W167-era "move deferred ... still in fleet/inbox" prose would
      produce a FALSE statement, so FIXUPS['pf']/['mat'] rewrite the
      self-ack face to the true already-landed state (r307 does not
      apply: this is the NEW block being authored, not a frozen face);
      the W167 frozen face keeps its historical deferred prose (the
      deferral was honored -- MSG-0056 is in processed/ on disk);
  (7) anti-drift composite @REGROW@ (bm-a r805 freeze f61835690) runs
      BEFORE the freeze-session token so the registered-prior-row sha
      pairing can never be torn by the session map;
  (8) lineage constant disclosed: the mat band-facts comment carries
      the template session stamp "law sec.4 W168 row, r795" -- the r795
      has ridden every vmap since the W165 freeze authored the
      band-facts template (git -S verbatim: W166 face already said
      "law sec.4 W166 row, r795"); passed through per r805 precedent.

EOL-adaptive (r370 law: CRLF-dominant blocks written CRLF);
needle count==1 (r745); insert-after-last-registered-row (r560);
anchor = predecessor full lines (r580/r781); AST gate after every
edit batch (r580/r781); origin anti-collision pre-check (r530/r687:
fetch + origin carries no W168 registration before this freeze)."""
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
gate = json.load(open("results/_r806bma_w168_band_gate.json", encoding="utf-8"))
leg1, leg3 = gate["legs"]["leg1"], gate["legs"]["leg3"]
assert gate["verdict"] == "ADMIT", gate["verdict"]
assert leg1["A"] == [384404, 386403] and leg1["B"] == [386404, 386603], leg1
assert leg1["hops_A"] == 1 and leg1["hops_B"] == 1
assert leg1["ARITH_A"] == [384204, 386203], leg1["ARITH_A"]
assert leg1["B_naive_first_clean"] == [384404, 384603], leg1["B_naive_first_clean"]
assert leg1["parity_with_probe"] is True
probe = json.load(open("results/_r806bma_w168_probe_receipt.json", encoding="utf-8"))
assert probe["verdict"] == "ADMIT" and probe["bands"] == {"A": "384404_386403", "B": "386404_386603"}, probe
w167res = json.load(open("results/perpetual_faces/n1_w167_results.json", encoding="utf-8"))
assert w167res["null_pool_cumulative"]["merged"]["n_values"] == 365320, "W167 merged K drift"
assert w167res["null_pool_cumulative"]["merged"]["n_values"] + 2200 == 367520, "W168 K projection arithmetic"
leg0 = gate["legs"]["leg0"]
assert leg0["rows"] == 165 and leg0["tail"] == "W167" and leg0["ordinal"] == 158 \
    and leg0["bma_ordinal"] == 84, leg0
assert gate["legs"]["leg0b"]["own_seat_on_origin"] is True, "seat leg0b"
assert os.path.exists(os.path.join("research", "PERPETUAL_N1_W168_PREREG.md")), \
    "W168 per-wave prereg missing on disk"


def u(s):  # "386404..388403" -> "386_404..388_403"
    def g(part):
        return re.sub(r"(\d)(?=(\d{3})+$)", r"\1_", part)
    a, b = s.split("..")
    return f"{g(a)}..{g(b)}"


W169p_A = u(leg3["W169p_A"])
W169p_B = u(leg3["W169p_B"])
assert W169p_A == "386_404..388_403" and W169p_B == "386_604..386_803", (W169p_A, W169p_B)
assert leg3["W169p_B_lands_inside_W169p_A"] is True

# --- ordered value-map (tokens first, then back-substitution) ---------------
TOK = [
    # whole-line seed-base rows (entry face; bands + ordinal carried WHOLE)
    ('"a_seed_base": 382_204,        # law sec.4 W167 A: 382_204..384_203 (FIRST-CLEAN past the registered W166 B band; arithmetic 382_004..384_003 REFUSED at own start by the W166 B band; hops=1; A-hops-prior-B staircase twenty-sixth instance, E36 card)', "@ASROW@"),
    ('"b_exit_seed_base": 384_204,   # law sec.4 W167 B: 384_204..384_403 (FIRST-CLEAN past the own-wave A window; arithmetic 382_204..382_403 lands inside own-A, same-freeze mutual exclusion W141 precedent; reserved walk hops=1; B base == own-A tail+1)', "@BSROW@"),
    # row + entry carriers
    ('167: {"a": (382_204, 384_203), "b_exit": (384_204, 384_403),', "@RROW@"),
    ('167: {"batch"', "@RENTRY@"),
    # registered-prior-row citations (machine-verified sha pairing; the
    # anti-drift composite -- MUST precede every session/round token)
    ('W166 row bm-a r799 freeze', "@PROW1@"),
    ('c2d6c5e14, SINGLE STATE zero seat gap W2..W166 all', "@PROW2@"),
    ('bm-a r799 freeze c2d6c5e14', "@REGROW@"),
    # freeze-session composites (this window: bm-a r809 freeze)
    ('bm-a r805 freeze', "@FZH@"),
    ('r805 bm-a freeze', "@MFZH@"),
    # claim-tail session attribution (the W167 claim carries the correct
    # r805 attribution -- healed lineage; the NEW W168 claim rolls it to
    # the r809 freeze session via this token)
    ('r805 bm-a] ', "@CLMS@"),
    # prior-finalize citations (W167 finalize one-pass landed r806;
    # FRAGMENT form per r781/r776 law: the entry tail physically splits
    # 'W167 ' (prior fragment) + CRLF + 'finalize one-pass bm-a r806, ...'
    # (within-fragment) -- the contiguous logical needle would count=0)
    ('W166 finalize landed same-window r799', "@FW@"),
    ('finalize one-pass bm-a r799', "@FOPM2@"),
    ('W166 bm-a r799 one-pass', "@FOP@"),
    # gate / probe receipt citations (W168 receipts)
    ('_r801bma_w167_probe_receipt.json', "@PRC@"),
    ('_r801bma_w167_band_gate.json', "@BGR@"),
    # prior gate / sec8 session refs (W166 gate r797 -> cited as r801;
    # W166 sec8 r799 -> cited as r806)
    ('r797 gate leg3', "@GATE@"),
    ('r797 gate', "@GATEP@"),
    ('r799 sec8 succession', "@SEC8@"),
    ('r799 sec8', "@SEC8M@"),
    # own-wave gate-session prose + pre-seat push session (r801 -> r806)
    ('gate-derived r801', "@GDR@"),
    ('r801 pre-seat push', "@PSP@"),
    # seat tokens (W167 seat 0056/982424c5f -> W168 seat 0259/ceaf58908)
    ('MSG-2026-10-07-0056', "@SEAT@"),
    ('bma-w167-seat', "@SEATW@"),
    ('MSG-0056', "@MSGS@"),
    ('982424c5f', "@SEATSHA@"),
    # W169 projection bands (gate leg3 verbatim, whole; BEFORE all band
    # tokens and seed backstops -- r773 pit law)
    ('384_204..386_203', "@PA@"),
    ('384_404..384_603', "@PB@"),
    # jump phrases (longest first; fragment-safe; BEFORE @BB@ which
    # shares the B-band substring)
    ('jumps to 384_204, first-clean 384_204..384_403 hops=1', "@JN@"),
    ('jumps to 384_204 -> 384_204..384_403,', "@JP@"),
    ('384_204 and lands 384_204..384_403', "@JAND@"),
    # the W168 B-assert jump fragment (rides the @JB@ token; W168 target
    # 386_404 -- the r787/r793/r805 heal lineage, leak class killed at source)
    ('own-wave A window reserved jumps to 384_204, first-clean ', "@JB@"),
    # assert composites
    ('== 382_204 == 382_203 + 1', "@ASB@"),
    ('== 384_204 == 384_203 + 1', "@BSB@"),
    ('set(range(382_204, 384_204))', "@ARITHA@"),
    ('set(range(384_204, 384_404))', "@ARB@"),
    # dotted band geometry
    ('382_004..384_003', "@NA@"),
    ('382_004..382_203', "@OB@"),
    ('382_204..384_203', "@AB@"),
    ('382_204..382_403', "@NB@"),
    ('384_204..384_403', "@BB@"),
    # base-relation composites
    ('382_203+1', "@ABASE@"),
    ('384_203+1', "@BBASE@"),
    # identity / stats / ordinals
    ('PERPETUAL_N1_W167_PREREG.md', "@PF@"),
    ('PERPETUAL-N1-W167', "@B@"),
    ('n1_w167_results.json', "@OD@"),
    ('n1_w167', "@SD@"),
    ('n1w167', "@SD2@"),
    ('770,612', "@LEDG@"),
    ('363,120', "@K1@"),
    ('ONE HUNDRED-AND-FIFTY-SEVENTH', "@ORDW@"),
    ('engine_owner rows 156', "@R154@"),
    ('rows 82 + candidate', "@ROWS80@"),
    ('eighty-second', "@SVN@"),
    ('twenty-sixth', "@ST24@"),
    # wave numbers (higher first: W168 projection -> W169; then W167->W168,
    # W166->W167)
    ('W168', "@WN2@"),
    ('W167', "@WN@"),
    ('W166', "@W@"),
    # bare round backstop (r776 fragment law: the physical W167 faces
    # break 'r801 pre-seat' + CRLF + '# push' across comment lines in the
    # pf block -- the exact-phrase TOK above cannot match it; every other
    # r801 face is already carried by composite tokens, so the bare roll
    # r801->r806 is safe; runs BEFORE the bare numerals)
    ('r801', "@RB@"),
    # bare numerals LAST (every longer carrier tokenized above; 167 before
    # 166 so the 166->167 output is never re-mapped)
    ('167', "@IDX@"),
    ('166', "@IDX2@"),
]
BACK = [
    ("@ASROW@", '"a_seed_base": 384_404,        # law sec.4 W168 A: 384_404..386_403 (FIRST-CLEAN past the registered W167 B band; arithmetic 384_204..386_203 REFUSED at own start by the W167 B band; hops=1; A-hops-prior-B staircase twenty-seventh instance, E36 card)'),
    ("@BSROW@", '"b_exit_seed_base": 386_404,   # law sec.4 W168 B: 386_404..386_603 (FIRST-CLEAN past the own-wave A window; arithmetic 384_404..384_603 lands inside own-A, same-freeze mutual exclusion W141 precedent; reserved walk hops=1; B base == own-A tail+1)'),
    ("@RROW@", '168: {"a": (384_404, 386_403), "b_exit": (386_404, 386_603),'),
    ("@RENTRY@", '168: {"batch"'),
    ("@PROW1@", "W167 row bm-a r805 freeze"),
    ("@PROW2@", "f61835690, SINGLE STATE zero seat gap W2..W167 all"),
    ("@REGROW@", "bm-a r805 freeze f61835690"),
    ("@FZH@", "bm-a r809 freeze"),
    ("@MFZH@", "r809 bm-a freeze"),
    ("@CLMS@", "r809 bm-a] "),
    ("@FW@", "W167 finalize landed same-window r806"),
    ("@FOPM2@", "finalize one-pass bm-a r806"),
    ("@FOP@", "W167 bm-a r806 one-pass"),
    ("@PRC@", "_r806bma_w168_probe_receipt.json"),
    ("@BGR@", "_r806bma_w168_band_gate.json"),
    ("@GATE@", "r801 gate leg3"),
    ("@GATEP@", "r801 gate"),
    ("@SEC8@", "r806 sec8 succession"),
    ("@SEC8M@", "r806 sec8"),
    ("@GDR@", "gate-derived r806"),
    ("@PSP@", "r806 pre-seat push"),
    ("@SEAT@", "MSG-2026-10-07-0259"),
    ("@SEATW@", "bma-w168-seat"),
    ("@MSGS@", "MSG-0259"),
    ("@SEATSHA@", "ceaf58908"),
    ("@PA@", "386_404..388_403"),
    ("@PB@", "386_604..386_803"),
    ("@JN@", "jumps to 386_404, first-clean 386_404..386_603 hops=1"),
    ("@JP@", "jumps to 386_404 -> 386_404..386_603,"),
    ("@JAND@", "386_404 and lands 386_404..386_603"),
    ("@JB@", "own-wave A window reserved jumps to 386_404, first-clean "),
    ("@ASB@", "== 384_404 == 384_403 + 1"),
    ("@BSB@", "== 386_404 == 386_403 + 1"),
    ("@ARITHA@", "set(range(384_404, 386_404))"),
    ("@ARB@", "set(range(386_404, 386_604))"),
    ("@NA@", "384_204..386_203"),
    ("@OB@", "384_204..384_403"),
    ("@AB@", "384_404..386_403"),
    ("@NB@", "384_404..384_603"),
    ("@BB@", "386_404..386_603"),
    ("@ABASE@", "384_403+1"),
    ("@BBASE@", "386_403+1"),
    ("@PF@", "PERPETUAL_N1_W168_PREREG.md"),
    ("@B@", "PERPETUAL-N1-W168"),
    ("@OD@", "n1_w168_results.json"),
    ("@SD@", "n1_w168"),
    ("@SD2@", "n1w168"),
    ("@LEDG@", "772,812"),
    ("@K1@", "365,320"),
    ("@ORDW@", "ONE HUNDRED-AND-FIFTY-EIGHTH"),
    ("@R154@", "engine_owner rows 157"),
    ("@ROWS80@", "rows 83 + candidate"),
    ("@SVN@", "eighty-third"),
    ("@ST24@", "twenty-seventh"),
    ("@WN2@", "W169"),
    ("@WN@", "W168"),
    ("@W@", "W167"),
    ("@IDX@", "168"),
    ("@IDX2@", "167"),
    ("@RB@", "r806"),
]
# r587 belt-and-braces: the projection BACK values must equal the
# machine-derived gate leg3 strings verbatim
assert ("@PA@", W169p_A) in BACK and ("@PB@", W169p_B) in BACK


def vmap(s: str) -> str:
    for a, b in TOK:
        s = s.replace(a, b)
    for a, b in BACK:
        s = s.replace(a, b)
    return s


# --- per-kind fragment-level fixups (r776 law: needles taken from the
# PHYSICAL probe-dumped shapes; applied AFTER vmap) ---------------------------
# Honesty fixup (this window's TRUE state): the W168 seat MSG was
# consumed-archived to fleet/inbox/processed/ by bm-c r650 at 03:27:53
# (git R100 rename, commit 0335e4a7d) BEFORE this freeze window -- the
# mechanical vmap roll of the W167-era deferred prose would state a
# falsehood ("W168 seat still in fleet/inbox"), so both carrying faces
# (pf block + mat header) are rewritten to the already-landed truth.
FIXUPS = {
    "pf": [
        ("move deferred to the W169 finalize window (W168 seat still in" + CRLF +
         "    # fleet/inbox at freeze time -- honest state);",
         "move already landed pre-freeze (bm-c r650 consumed-archived the" + CRLF +
         "    # W168 seat to fleet/inbox/processed at 03:27:53 -- honest state);"),
    ],
    "mat": [
        ("move deferred to the W169 finalize window (W168 seat still in" + CRLF +
         "    #     fleet/inbox at freeze time -- honest state).",
         "move already landed pre-freeze (bm-c r650 consumed-archived the" + CRLF +
         "    #     W168 seat to fleet/inbox/processed at 03:27:53 -- honest state)."),
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

# face-source zero-drift gate vs the r809 probe dumps
EO = '"engine_owner": "bm-a"},'
i1 = pfsrc.find("    # W167 (bm-a r805 freeze")
assert i1 > 0, "pf W167 comment block not found"
r1 = pfsrc.find('167: {"a": (382_204', i1)
assert r1 > i1, "pf W167 row not after comment block"
j1 = pfsrc.find(EO, r1) + len(EO)
block167_pf = pfsrc[i1:j1]
assert block167_pf == io.open(r"results\_r809bma_w168_probe_pf_block.txt",
                             encoding="utf-8", newline="").read(), "pf face drift vs probe"
assert block167_pf.count("engine_owner") == 1 and "c2d6c5e14" not in block167_pf
assert "382_004..384_003 REFUSED at its own start by the W166 B band" in block167_pf

# pre-edit live registry parity (the W167 registered row must be intact
# before we append the W168 row -- r560 no-replace law)
sys.path.insert(0, ".")
sys.path.insert(0, "scripts")
import perpetual_faces as pfpre
assert pfpre.N1_BANDS[167] == {"a": (382_204, 384_203),
                               "b_exit": (384_204, 384_403),
                               "engine_owner": "bm-a"}, "pre-edit W167 row drift"
assert sorted(pfpre.N1_BANDS)[-1] == 167 and len(pfpre.N1_BANDS) == 165, "pre-edit row count"

# origin anti-collision pre-check (r530 never-dry + r687 dual-scan:
# fetch fresh, origin must carry no W168 registration before this freeze)
subprocess.run(["git", "fetch", "origin"], capture_output=True)
_r = subprocess.run(["git", "show", "origin/main:scripts/perpetual_faces.py"],
                    capture_output=True)
_op = _r.stdout.decode("utf-8", "replace")
assert _r.returncode == 0, "origin pf.py read failed"
assert '168: {"a"' not in _op, "origin already carries a W168 registration (r687 dual-scan)"
assert "# W168 (bm-a" not in _op, "origin already carries a W168 freeze block"
_r2 = subprocess.run(["git", "rev-list", "--count", "origin/main..HEAD"],
                     capture_output=True, text=True)
assert _r2.stdout.strip() == "0", f"local ahead of origin: {_r2.stdout.strip()} (behind-law)"

# --- a1: pf.py W167 comment block + row -> append W168 comment block + row ----
a1 = block167_pf + CRLF + "}"
r1n = block167_pf + CRLF + vmap_fix(block167_pf, "pf") + CRLF + "}"

# --- a2: n1.py WAVE_CONFIGS entry ----------------------------------------------
k = n1src.find('167: {"batch"')
assert k > 0, "n1 W167 entry not found"
m = n1src.find(EO, k) + len(EO)
entry167 = n1src[k:m]
assert entry167 == io.open(r"results\_r809bma_w168_probe_n1_entry.txt",
                          encoding="utf-8", newline="").read(), "entry face drift vs probe"
a2 = entry167 + CRLF + "                       }"
r2 = entry167 + CRLF + "                       " + vmap_fix(entry167, "n1entry") + CRLF + "                       }"

# --- a3: materializer block (chain split-verbatim + one-row extension) --------
w = n1src.find("# --- W167 materializer face")
t2 = n1src.find("# --- T-141 s2 lane face", w)
assert 0 < w < t2, "materializer anchors missing"
block = n1src[w:t2]
assert block == io.open(r"results\_r809bma_w168_probe_n1_mat.txt",
                        encoding="utf-8", newline="").read(), "mat face drift vs probe"
ci = block.find("assert pf.N1_BANDS[138]")
cj = block.find("# prior-wave disjointness")
assert 0 < ci < cj, "chain boundaries missing"
pre, chain, post = block[:ci], block[ci:cj], block[cj:]
chain_rows = re.findall(r"assert pf\.N1_BANDS\[(\d+)\]", chain)
assert chain_rows == [str(x) for x in range(138, 167)], chain_rows
w167row = ('assert pf.N1_BANDS[167] == {"a": (382_204, 384_203),' + CRLF +
           '                                    "b_exit": (384_204, 384_403),' + CRLF +
           '                                    "engine_owner": "bm-a"}, \\' + CRLF +
           '            "registered W167 row parity drift (r307; bm-a r805)"' + CRLF +
           "        ")
# delivery/payload prose lives ONLY in the mat pre (header comment face);
# the post (disjointness/band-facts/assert face) passes through plain vmap
block168 = vmap_fix(pre, "mat") + chain + w167row + vmap(post)
a3 = block + "# --- T-141 s2 lane face"
r3 = block168 + "# --- T-141 s2 lane face"

# --- a4: PASS snippet claim insertion ------------------------------------------
cs = n1src.find('"+ W167 materializer face')
assert cs > 0, "W167 claim start not found"
ce = n1src.find('"r805 bm-a] "', cs) + len('"r805 bm-a] "')
assert 0 < cs < ce, "W167 claim end not found"
claim167 = n1src[cs:ce]
assert claim167 == io.open(r"results\_r809bma_w168_probe_n1_claim.txt",
                           encoding="utf-8", newline="").read(), "claim face drift vs probe"
a4 = '"r805 bm-a] "' + CRLF + '          "+ T-141 s2 "'
r4 = '"r805 bm-a] "' + CRLF + "          " + vmap_fix(claim167, "claim") + CRLF + '          "+ T-141 s2 "'

# --- apply the four edits -------------------------------------------------------
edit(PF, [(a1, r1n)])
edit(N1, [(a2, r2), (a3, r3), (a4, r4)])

# --- post-edit structural assertions --------------------------------------------
import importlib
import perpetual_faces as pf
importlib.reload(pf)
assert sorted(pf.N1_BANDS)[-1] == 168 and len(pf.N1_BANDS) == 166, \
    "pf N1_BANDS row-count drift after W168 insert"
assert pf.N1_BANDS[168] == {"a": (384_404, 386_403),
                            "b_exit": (386_404, 386_603),
                            "engine_owner": "bm-a"}, "W168 row face drift"
assert pf.N1_BANDS[167] == {"a": (382_204, 384_203),
                            "b_exit": (384_204, 384_403),
                            "engine_owner": "bm-a"}, "W167 row survived (r560 no-replace law)"
import perpetual_faces_n1 as n1mod
importlib.reload(n1mod)
assert n1mod.WAVE_CONFIGS[168]["a_seed_base"] == 384_404 and \
    n1mod.WAVE_CONFIGS[168]["b_exit_seed_base"] == 386_404, "W168 seed bases drift"
assert n1mod.WAVE_CONFIGS[168]["shard_subdir"] == "n1_w168" and \
    n1mod.WAVE_CONFIGS[168]["out_name"] == "n1_w168_results.json", "W168 path drift"
assert n1mod.WAVE_CONFIGS[168]["prereg"].startswith("research/PERPETUAL_N1_W168_PREREG.md"), \
    "W168 per-wave prereg citation drift"
assert os.path.exists(os.path.join("research", "PERPETUAL_N1_W168_PREREG.md")), \
    "W168 per-wave prereg missing on disk"

# materializer chain now 138..W167row (n=30)
n2 = io.open(N1, encoding="utf-8", newline="").read()
w2 = n2.find("# --- W168 materializer face")
t3 = n2.find("# --- T-141 s2 lane face", w2)
blk2 = n2[w2:t3]
chain_rows2 = re.findall(r"assert pf\.N1_BANDS\[(\d+)\]",
                         blk2[blk2.find("assert pf.N1_BANDS[138]"):
                              blk2.find("# prior-wave disjointness")])
assert chain_rows2 == [str(x) for x in range(138, 168)], chain_rows2

# r773 pit law leg 3: full-file start>end malformed-window scans on BOTH files
for path in (PF, N1):
    txt = io.open(path, encoding="utf-8", newline="").read()
    bad = [m.group() for m in re.finditer(r"(\d{3})_(\d{3})\.\.(\d{3})_(\d{3})", txt)
           if int(m.group(3)) < int(m.group(1))]
    assert not bad, f"malformed windows remain in {path}: {bad[:4]}"

# W169 projection prose present in the new W168 blocks (gate leg3 verbatim)
pf2 = io.open(PF, encoding="utf-8", newline="").read()
assert f"# {W169p_A} CLEAN hops=0 / B first-clean {W169p_B}" in pf2, "pf W169p prose missing"
assert "W169 A window; W169 freezer MUST re-derive on the post-W168" in pf2, \
    "pf W169 freezer prose missing"
# r776 fragment-needle law: the freezer prose in the n1 entry is split
# across python-string fragments -- a contiguous needle is a false-negative
# (r775/r781 law); assert the within-fragment shapes instead.
assert '"W169 A window; W169 freezer MUST re-derive on the "' in n2, "n1 W169 freezer fragment missing"
assert '"W168 B band 386_404..386_603 will refuse the naive "' in n2, "n1 W168-band refuse fragment missing"
assert f"A first-clean {W169p_A} " in n2 and f"B first-clean {W169p_B} CLEAN" in n2, \
    "n1 W169p prose missing"
# honesty faces landed (self-ack already-landed TRUTH + 3-item payload +
# direct-FF delivery + anti-drift registered-row citation)
assert "move already landed pre-freeze (bm-c r650 consumed-archived the" in pf2, "pf self-ack fixup missing"
assert "fleet/inbox/processed at 03:27:53 -- honest state);" in pf2, "pf self-ack tail fixup missing"
assert "move already landed pre-freeze (bm-c r650 consumed-archived the" in n2, "mat self-ack fixup missing"
assert "fleet/inbox/processed at 03:27:53 -- honest state)." in n2, "mat self-ack tail missing"
assert "payload = seat MSG + pre-seat probe + probe receipt;" in pf2, "pf 3-item payload fixup missing"
assert '"seat MSG + pre-seat probe + probe receipt; "' in n2, "entry 3-item payload fixup missing"
assert "= seat MSG + pre-seat probe + probe receipt;" in n2, "mat 3-item payload fixup missing"
assert "r806 pre-seat" in pf2 and "r806 pre-seat" in n2, "push session r806 face missing"
assert "direct fast-forward behind-0" in pf2 and "direct fast-forward behind-0" in n2, \
    "direct-FF delivery face missing"
# r776 fragment-needle law: the registered-row citation is split across
# python string fragments -- assert the within-fragment shapes
assert '"number law after the REGISTERED W167 row bm-a r805 freeze "' in n2, \
    "W167 row citation frag1 missing"
assert '"f61835690, SINGLE STATE zero seat gap W2..W167 all "' in n2, \
    "W167 row citation frag2 missing"
assert '"finalize one-pass bm-a r806, net chain head 772,812, "' in n2, \
    "W167 finalize one-pass frag missing"
# r781 fragment law: the contiguous logical string 'W167 finalize one-pass
# bm-a r806' physically splits across python string fragments -- count the
# within-fragment shapes instead (mat 1 + entry tail 1 == 2)
assert n2.count("finalize one-pass bm-a r806") == 2, "W167 finalize one-pass count drift"
assert "bm-a r805 freeze f61835690" in n2, "mat header registered-row citation missing"
assert "c2d6c5e14" not in blk2, "stale W166 sha residue in new W168 block"
assert "finalize one-pass bm-a r809" not in n2, "stale r809 finalize residue"
# the NEW W168 claim carries the rolled session attribution (the W167
# claim's r805 attribution was correct -- healed lineage; r307 keeps the
# W167 frozen claim's own tail untouched)
assert '"r809 bm-a] "' in n2, "W168 claim r809 attribution missing"
# no stale round/seat/number leftovers in the NEW W168 blocks only (the
# frozen W167/W166 faces legitimately retain their historical citations;
# the mat CHAIN rows are verbatim prior-wave pinned constants (r307) --
# historical band values there are legitimate, so the mat scan covers
# only the freshly vmap'd pre (header) + post (band-facts) faces)
i2 = pf2.find("    # W168 (bm-a r809 freeze")
j2 = pf2.find(EO, i2) + len(EO)
newpfblk = pf2[i2:j2]
k2 = n2.find('168: {"batch"')
m2 = n2.find(EO, k2) + len(EO)
newentry = n2[k2:m2]
cs2 = n2.find('"+ W168 materializer face')
ce2 = n2.find('"r809 bm-a] "', cs2) + len('"r809 bm-a] "')
newclaim = n2[cs2:ce2]
ci2 = blk2.find("assert pf.N1_BANDS[138]")
cj2 = blk2.find("# prior-wave disjointness")
mat_new_faces = blk2[:ci2] + blk2[cj2:]
assert i2 > 0 and k2 > 0 and cs2 > 0, "new W168 block anchors missing"
for tag, seg in (("pf", newpfblk), ("entry", newentry),
                 ("mat", mat_new_faces), ("claim", newclaim)):
    for stale in ("r793 gate", "r796 sec8", "r797 gate", "r799 sec8",
                  "r797 pre-seat", "r801 pre-seat", "W166 (bm-a r799",
                  "W167 (bm-a r805", "bm-a r795 freeze", "r795 bm-a freeze",
                  "bm-a r799 freeze", "r799 bm-a freeze",
                  "MSG-2026-10-06-223x", "MSG-2026-10-07-0056", "982424c5f",
                  "d1dc12117", "bma-w166-seat", "bma-w167-seat", "MSG-223x",
                  "MSG-0056", "seat MSG-0056 tail", "merge-absorb",
                  "gate-derived r797", "gate-derived r801",
                  "move deferred to the W169",
                  "379_804", "380_004", "380_003", "380_203", "381_803",
                  "382_003", "382_004", "382_203", "382_204", "382_403",
                  "384_003", "384_203", "768,412", "360,920", "770,612",
                  "363,120", "aebb94d2d", "c2d6c5e14", "f7d34e5a7",
                  "18231a529", "764cd882a", "678a07d4f", "6957f509e",
                  "6ee1207bb", "ee04482a2",
                  "twenty-fourth", "twenty-fifth", "twenty-sixth",
                  "seventy-ninth", "eightieth", "eighty-first", "eighty-second",
                  "ONE HUNDRED-AND-FIFTY-FIFTH", "ONE HUNDRED-AND-FIFTY-SIXTH",
                  "ONE HUNDRED-AND-FIFTY-SEVENTH", "engine_owner rows 154",
                  "engine_owner rows 155", "engine_owner rows 156",
                  "rows 80 + candidate", "rows 81 + candidate", "rows 82 + candidate",
                  "n1w165", "n1_w165", "n1w166", "n1_w166", "n1w167", "n1_w167",
                  "PERPETUAL-N1-W165", "PERPETUAL_N1_W165",
                  "PERPETUAL-N1-W166", "PERPETUAL_N1_W166",
                  "PERPETUAL-N1-W167", "PERPETUAL_N1_W167",
                  "r789 gate", "r790 sec8", "r785 gate", "r786 sec8",
                  "facts helper", "arc generator"):
        assert stale not in seg, f"stale {stale!r} residue in new W168 {tag} block"
        # 384_204/384_403/384_404/384_603/386_203/386_403/386_404/386_603 are
        # NOT in the stale set: they legitimately appear in the new W168
        # blocks as the W167 B band citation (prior-B refusal band), the
        # own-wave A/B starts-ends and the naive-A/B starts-ends (r787
        # 371_004-precedent note; r793 379_804-precedent note)
# corrupted historical faces must remain eradicated from both files
for path in (PF, N1):
    txt = io.open(path, encoding="utf-8", newline="").read()
    assert "362_204..362_003" not in txt and "362_404..360_403" not in txt, \
        f"r772 malformed-window residue in {path}"
# the W168 B-assert prose cites the W168 jump target 386_404 via the @JB@
# token (the r787/r793/r805 heal lineage: SINGLE-LIVE materializer face
# migrates to the newest wave each freeze; git history carries the record)
assert "own-wave A window reserved jumps to 386_404, first-clean " in blk2, \
    "W168 healed-fragment face missing"
assert "own-wave A window reserved jumps to 384_204, first-clean" not in blk2, \
    "vmap-leak residue in new block"

print("post-edit structural assertions PASS: N1_BANDS 166 rows tail W168, "
      "W167 row intact, WAVE_CONFIGS[168] seeded, chain 138..167 n=30, "
      "W169p prose == r806 gate leg3 verbatim, honesty faces landed "
      "(self-ack already-landed TRUTH / 3-item payload / direct-FF "
      "delivery / anti-drift registered-row cite / @CLMS@ claim r809 "
      "attribution), full-file malformed-window scans CLEAN on both files, "
      "same-window FIXUPS applied (W168 seat consumed-archived bm-c r650 "
      "03:27:53 pre-freeze)")
