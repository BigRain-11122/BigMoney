# -*- coding: utf-8 -*-
"""r787 bm-a W162 freeze edits: four insertions (pf N1_BANDS[162] row +
n1 WAVE_CONFIGS[162] entry + n1 W162 materializer block refresh +
n1 PASS snippet claim insertion).

Bloodline: r785 _r785bma_w161_freeze_edits.py machinery (r773 pit law
freeze-editor compliance + r776 fragment-needle law + r781
verify-separation law), W162 facts live-registry-driven:
  - band gate results/_r787bma_w162_band_gate.json rc0 ADMIT
    (A 371_204..373_203 staircase TWENTY-FIRST instance E36 hops=1 past
    the W161 B band; naive 371_004..373_003 refused at its own start by
    the registered W161 B band 371_004..371_203; B 373_204..373_403
    own-A mutual exclusion hops=1, naive 371_204..371_403);
  - pre-seat probe results/_r787bma_w162_probe_receipt.json ADMIT,
    dual-window parity True (gate leg1 parity_with_probe);
  - seat MSG-2026-10-06-175x-bma-w162-seat published 1d43d7906
    (r787 pre-seat push, direct fast-forward behind-0; r565 law: on
    origin BEFORE this freeze commit);
  - per-wave prereg research/PERPETUAL_N1_W162_PREREG.md (r787 session,
    banned gate ADMIT 0);
  - W161 finalize one-pass r786: ledger head 759,612, merged pool
    K=352,120 (n1_w161_results.json machine-read);
  - W161 freeze r785 sha 678a07d4f (the REGISTERED W161 row citation);
  - W163+ projection (gate leg3 verbatim): A first-clean 373_204..375_203
    / B first-clean 373_404..373_603, naive-B-inside-naive-A, the
    registered W162 B band will refuse the naive W163 A window.

r773 pit law compliance:
  (1) full string-face inventory empirically probed BEFORE TOK
      (_r787bma_w162_face_probe.py -- four face dumps + needle-count
      receipt; probe run AFTER the same-window W161 prose heal so the
      dumps match the on-disk healed face);
  (2) composite band strings tokenized WHOLE (no bare-seed-prefix
      tokens; every dotted band / seed-base row / jump phrase /
      round-sha composite is a single token; bare 161/160 run LAST);
  (3) post-edit full-file start>end malformed-window regex scan on BOTH
      touched files;
  (4) every projection value re-derived FROM the on-disk gate receipts
      (r587 never-transcribe law);
  (5) r776 fragment-needle law: all fixup needles taken from the
      PHYSICAL probe-dumped shapes (python-string fragments / comment
      lines, CRLF-exact);
  (6) SAME-WINDOW HEAL disclosed (r783-heal precedent class THIRD
      instance, landed pre-probe by _r787bma_w162_w161prose_heal.py):
      the frozen W161 materializer B-assert prose carried a vmap leak
      "own-wave A window reserved jumps to 368_804, first-clean" -- the
      honest W161 jump target per the r785 gate receipt is 371_004;
      healed to the machine-verified value; needle whole-file count==1;
      the healed fragment is carried through this vmap as the @JB@
      token (W162 target 373_204), killing the leak class at source;
  (7) anti-drift composite @REGROW@ (bm-a r785 freeze 678a07d4f) runs
      BEFORE the freeze-session token so the registered-prior-row sha
      pairing can never be torn by the session map (r785 heal-1 class
      eradicated at source).

EOL-adaptive (r370 law: CRLF-dominant blocks written CRLF);
needle count==1 (r745); insert-after-last-registered-row (r560);
anchor = predecessor full lines (r580/r781); AST gate after every
edit batch (r580/r781)."""
import ast
import io
import json
import re
import os

PF = r"scripts/perpetual_faces.py"
N1 = r"scripts/perpetual_faces_n1.py"
CRLF = "\r\n"

# --- machine-derived facts (r587: read from on-disk receipts) ----------------
gate = json.load(open("results/_r787bma_w162_band_gate.json", encoding="utf-8"))
leg1, leg3 = gate["legs"]["leg1"], gate["legs"]["leg3"]
assert gate["verdict"] == "ADMIT", gate["verdict"]
assert leg1["A"] == [371204, 373203] and leg1["B"] == [373204, 373403], leg1
assert leg1["hops_A"] == 1 and leg1["hops_B"] == 1
assert leg1["ARITH_A"] == [371004, 373003], leg1["ARITH_A"]
assert leg1["B_naive_first_clean"] == [371204, 371403], leg1["B_naive_first_clean"]
assert leg1["parity_with_probe"] is True
probe = json.load(open("results/_r787bma_w162_probe_receipt.json", encoding="utf-8"))
assert probe["verdict"] == "ADMIT" and probe["bands"] == {"A": "371204_373203", "B": "373204_373403"}, probe
w161res = json.load(open("results/perpetual_faces/n1_w161_results.json", encoding="utf-8"))
assert w161res["null_pool_cumulative"]["merged"]["n_values"] == 352120, "W161 merged K drift"
assert w161res["null_pool_cumulative"]["merged"]["n_values"] + 2200 == 354320, "W162 K projection arithmetic"


def u(s):  # "373204..375203" -> "373_204..375_203"
    def g(part):
        return re.sub(r"(\d)(?=(\d{3})+$)", r"\1_", part)
    a, b = s.split("..")
    return f"{g(a)}..{g(b)}"


W163p_A = u(leg3["W163p_A"])
W163p_B = u(leg3["W163p_B"])
assert W163p_A == "373_204..375_203" and W163p_B == "373_404..373_603", (W163p_A, W163p_B)
assert leg3["W163p_B_lands_inside_W163p_A"] is True

# --- ordered value-map (tokens first, then back-substitution) ---------------
TOK = [
    # whole-line seed-base rows (entry face; bands + ordinal carried WHOLE)
    ('"a_seed_base": 369_004,        # law sec.4 W161 A: 369_004..371_003 (FIRST-CLEAN past the registered W160 B band; arithmetic 368_804..370_803 REFUSED at own start by the W160 B band; hops=1; A-hops-prior-B staircase twentieth instance, E36 card)', "@ASROW@"),
    ('"b_exit_seed_base": 371_004,   # law sec.4 W161 B: 371_004..371_203 (FIRST-CLEAN past the own-wave A window; arithmetic 369_004..369_203 lands inside own-A, same-freeze mutual exclusion W141 precedent; reserved walk hops=1; B base == own-A tail+1)', "@BSROW@"),
    # row + entry carriers
    ('161: {"a": (369_004, 371_003), "b_exit": (371_004, 371_203),', "@RROW@"),
    ('161: {"batch"', "@RENTRY@"),
    # registered-prior-row citations (machine-verified sha pairing; the
    # anti-drift composite -- MUST precede every session/round token)
    ('W160 row bm-a r783 freeze', "@PROW1@"),
    ('ee04482a2, SINGLE STATE zero seat gap W2..W160 all', "@PROW2@"),
    ('bm-a r783 freeze ee04482a2', "@REGROW@"),
    # freeze-session composites
    ('bm-a r785 freeze', "@FZH@"),
    ('r785 bm-a freeze', "@MFZH@"),
    # prior-finalize citations (W160 finalize r784 -> W161 finalize r786)
    ('W160 finalize landed same-window r784', "@FW@"),
    ('W160 finalize one-pass bm-a r784', "@FOPM2@"),
    ('W160 bm-a r784 one-pass', "@FOP@"),
    # gate / probe receipt citations (probe r787, gate r787)
    ('_r785bma_w161_probe_receipt.json', "@PRC@"),
    ('_r785bma_w161_band_gate.json', "@BGR@"),
    # prior gate / sec8 session refs (W160 gate r783 -> W161 gate r785;
    # W160 finalize sec8 r784 -> W161 finalize sec8 r786)
    ('r783 gate leg3', "@GATE@"),
    ('r783 gate', "@GATEP@"),
    ('r784 sec8 succession', "@SEC8@"),
    ('r784 sec8', "@SEC8M@"),
    # seat tokens
    ('MSG-2026-10-06-165x', "@SEAT@"),
    ('bma-w161-seat', "@SEATW@"),
    ('MSG-165x', "@MSGS@"),
    ('0371f2093', "@SEATSHA@"),
    # W163 projection bands (gate leg3 verbatim, whole; BEFORE all band
    # tokens and seed backstops -- r773 pit law)
    ('371_004..373_003', "@PA@"),
    ('371_204..371_403', "@PB@"),
    # jump phrases (longest first; fragment-safe; BEFORE @BB@ which
    # shares the B-band substring)
    ('jumps to 371_004, first-clean 371_004..371_203 hops=1', "@JN@"),
    ('jumps to 371_004 -> 371_004..371_203,', "@JP@"),
    ('371_004 and lands 371_004..371_203', "@JAND@"),
    # the healed W161 B-assert fragment (r787 same-window heal; the W162
    # target jump value rides this token)
    ('own-wave A window reserved jumps to 371_004, first-clean ', "@JB@"),
    # assert composites
    ('== 369_004 == 369_003 + 1', "@ASB@"),
    ('== 371_004 == 371_003 + 1', "@BSB@"),
    ('set(range(369_004, 371_004))', "@ARITHA@"),
    ('set(range(371_004, 371_204))', "@ARB@"),
    # dotted band geometry
    ('368_804..370_803', "@NA@"),
    ('368_804..369_003', "@OB@"),
    ('369_004..371_003', "@AB@"),
    ('369_004..369_203', "@NB@"),
    ('371_004..371_203', "@BB@"),
    # base-relation composites
    ('369_003+1', "@ABASE@"),
    ('371_003+1', "@BBASE@"),
    # rounds (composites above; then own-session bare; then prior-session
    # bares -- 'r785'->'r787' FIRST so the r783->r785 backstop output is
    # never re-mapped)
    ('r785', "@RW@"),
    ('r783', "@PRW@"),
    ('r784', "@FRW@"),
    # identity / stats / ordinals
    ('PERPETUAL_N1_W161_PREREG.md', "@PF@"),
    ('PERPETUAL-N1-W161', "@B@"),
    ('n1_w161_results.json', "@OD@"),
    ('n1_w161', "@SD@"),
    ('n1w161', "@SD2@"),
    ('757,412', "@LEDG@"),
    ('349,920', "@K1@"),
    ('ONE HUNDRED-AND-FIFTY-FIRST', "@ORDW@"),
    ('engine_owner rows 150', "@R151@"),
    ('rows 76 + candidate', "@ROWS76@"),
    ('seventy-seventh', "@SVN77@"),
    ('twentieth', "@ST21@"),
    # wave numbers (higher first: W162 projection -> W163; then W161->W162,
    # W160->W161)
    ('W162', "@WN2@"),
    ('W161', "@WN@"),
    ('W160', "@W@"),
    # bare numerals LAST (every longer carrier tokenized above; 161 before
    # 160 so the 160->161 output is never re-mapped)
    ('161', "@IDX@"),
    ('160', "@IDX2@"),
]
BACK = [
    ("@ASROW@", '"a_seed_base": 371_204,        # law sec.4 W162 A: 371_204..373_203 (FIRST-CLEAN past the registered W161 B band; arithmetic 371_004..373_003 REFUSED at own start by the W161 B band; hops=1; A-hops-prior-B staircase twenty-first instance, E36 card)'),
    ("@BSROW@", '"b_exit_seed_base": 373_204,   # law sec.4 W162 B: 373_204..373_403 (FIRST-CLEAN past the own-wave A window; arithmetic 371_204..371_403 lands inside own-A, same-freeze mutual exclusion W141 precedent; reserved walk hops=1; B base == own-A tail+1)'),
    ("@RROW@", '162: {"a": (371_204, 373_203), "b_exit": (373_204, 373_403),'),
    ("@RENTRY@", '162: {"batch"'),
    ("@PROW1@", "W161 row bm-a r785 freeze"),
    ("@PROW2@", "678a07d4f, SINGLE STATE zero seat gap W2..W161 all"),
    ("@REGROW@", "bm-a r785 freeze 678a07d4f"),
    ("@FZH@", "bm-a r787 freeze"),
    ("@MFZH@", "r787 bm-a freeze"),
    ("@FW@", "W161 finalize landed same-window r786"),
    ("@FOPM2@", "W161 finalize one-pass bm-a r786"),
    ("@FOP@", "W161 bm-a r786 one-pass"),
    ("@PRC@", "_r787bma_w162_probe_receipt.json"),
    ("@BGR@", "_r787bma_w162_band_gate.json"),
    ("@GATE@", "r785 gate leg3"),
    ("@GATEP@", "r785 gate"),
    ("@SEC8@", "r786 sec8 succession"),
    ("@SEC8M@", "r786 sec8"),
    ("@SEAT@", "MSG-2026-10-06-175x"),
    ("@SEATW@", "bma-w162-seat"),
    ("@MSGS@", "MSG-175x"),
    ("@SEATSHA@", "1d43d7906"),
    ("@PA@", "373_204..375_203"),
    ("@PB@", "373_404..373_603"),
    ("@JN@", "jumps to 373_204, first-clean 373_204..373_403 hops=1"),
    ("@JP@", "jumps to 373_204 -> 373_204..373_403,"),
    ("@JAND@", "373_204 and lands 373_204..373_403"),
    ("@JB@", "own-wave A window reserved jumps to 373_204, first-clean "),
    ("@ASB@", "== 371_204 == 371_203 + 1"),
    ("@BSB@", "== 373_204 == 373_203 + 1"),
    ("@ARITHA@", "set(range(371_204, 373_204))"),
    ("@ARB@", "set(range(373_204, 373_404))"),
    ("@NA@", "371_004..373_003"),
    ("@OB@", "371_004..371_203"),
    ("@AB@", "371_204..373_203"),
    ("@NB@", "371_204..371_403"),
    ("@BB@", "373_204..373_403"),
    ("@ABASE@", "371_203+1"),
    ("@BBASE@", "373_203+1"),
    ("@RW@", "r787"),
    ("@PRW@", "r785"),
    ("@FRW@", "r786"),
    ("@PF@", "PERPETUAL_N1_W162_PREREG.md"),
    ("@B@", "PERPETUAL-N1-W162"),
    ("@OD@", "n1_w162_results.json"),
    ("@SD@", "n1_w162"),
    ("@SD2@", "n1w162"),
    ("@LEDG@", "759,612"),
    ("@K1@", "352,120"),
    ("@ORDW@", "ONE HUNDRED-AND-FIFTY-SECOND"),
    ("@R151@", "engine_owner rows 151"),
    ("@ROWS76@", "rows 77 + candidate"),
    ("@SVN77@", "seventy-eighth"),
    ("@ST21@", "twenty-first"),
    ("@WN2@", "W163"),
    ("@WN@", "W162"),
    ("@W@", "W161"),
    ("@IDX@", "162"),
    ("@IDX2@", "161"),
]


def vmap(s: str) -> str:
    for a, b in TOK:
        s = s.replace(a, b)
    for a, b in BACK:
        s = s.replace(a, b)
    return s


# --- per-kind fragment-level fixups (r776 law: needles taken from the
# PHYSICAL probe-dumped shapes; applied AFTER vmap) ---------------------------
FIXUPS = {
    "pf": [
        # self-ack honesty: the W162 seat is still in fleet/inbox at freeze
        # time (published minutes before the freeze) -- honest deferred face
        ("move landed (bm-b r779 read-only-observer processed, a2d002357);",
         "move deferred to the W163 finalize window (W162 seat still in" + CRLF +
         "    # fleet/inbox at freeze time -- honest state);"),
        # payload honesty: the r787 pre-seat payload's 4th item is the
        # facts helper (not an arc generator)
        ("W162 arc generator", "facts helper"),
    ],
    "n1entry": [
        ("W162 arc generator", "facts helper"),
    ],
    "mat": [
        # self-ack honesty (mat pre, 2-line physical shape)
        ("move landed (bm-b" + CRLF +
         "    #     r779 read-only-observer processed, a2d002357).",
         "move deferred to the W163 finalize window (W162 seat still in" + CRLF +
         "    #     fleet/inbox at freeze time -- honest state)."),
        ("W162 arc generator", "facts helper"),
    ],
}


def vmap_fix(s: str, kind: str) -> str:
    s = vmap(s)
    if kind == "claim":
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

# face-source zero-drift gate vs the r787 probe dumps (run AFTER the
# same-window W161 prose heal -- dumps match the healed face)
EO = '"engine_owner": "bm-a"},'
i1 = pfsrc.find("    # W161 (bm-a r785 freeze")
assert i1 > 0, "pf W161 comment block not found"
r1 = pfsrc.find('161: {"a": (369_004', i1)
assert r1 > i1, "pf W161 row not after comment block"
j1 = pfsrc.find(EO, r1) + len(EO)
block161_pf = pfsrc[i1:j1]
assert block161_pf == io.open(r"results\_r787bma_w162_probe_pf_block.txt",
                             encoding="utf-8", newline="").read(), "pf face drift vs probe"
assert block161_pf.count("engine_owner") == 1 and "ee04482a2" not in block161_pf
assert "371_004..373_003 CLEAN hops=0 / B first-clean 371_204..371_403" in block161_pf

# --- a1: pf.py W161 comment block + row -> append W162 comment block + row ----
a1 = block161_pf + CRLF + "}"
r1n = block161_pf + CRLF + vmap_fix(block161_pf, "pf") + CRLF + "}"

# --- a2: n1.py WAVE_CONFIGS entry ----------------------------------------------
k = n1src.find('161: {"batch"')
assert k > 0, "n1 W161 entry not found"
m = n1src.find(EO, k) + len(EO)
entry161 = n1src[k:m]
assert entry161 == io.open(r"results\_r787bma_w162_probe_n1_entry.txt",
                           encoding="utf-8", newline="").read(), "entry face drift vs probe"
a2 = entry161 + CRLF + "                       }"
r2 = entry161 + CRLF + "                       " + vmap_fix(entry161, "n1entry") + CRLF + "                       }"

# --- a3: materializer block (chain split-verbatim + one-row extension) --------
w = n1src.find("# --- W161 materializer face")
t2 = n1src.find("# --- T-141 s2 lane face", w)
assert 0 < w < t2, "materializer anchors missing"
block = n1src[w:t2]
assert block == io.open(r"results\_r787bma_w162_probe_n1_mat.txt",
                        encoding="utf-8", newline="").read(), "mat face drift vs probe"
ci = block.find("assert pf.N1_BANDS[138]")
cj = block.find("# prior-wave disjointness")
assert 0 < ci < cj, "chain boundaries missing"
pre, chain, post = block[:ci], block[ci:cj], block[cj:]
chain_rows = re.findall(r"assert pf\.N1_BANDS\[(\d+)\]", chain)
assert chain_rows == [str(x) for x in range(138, 161)], chain_rows
w161row = ('assert pf.N1_BANDS[161] == {"a": (369_004, 371_003),' + CRLF +
           '                                    "b_exit": (371_004, 371_203),' + CRLF +
           '                                    "engine_owner": "bm-a"}, \\' + CRLF +
           '            "registered W161 row parity drift (r307; bm-a r785)"' + CRLF +
           "        ")
# delivery/self-ack/payload prose lives ONLY in the mat pre (header
# comment face); the post (disjointness/band-facts/assert face) passes
# through plain vmap
block162 = vmap_fix(pre, "mat") + chain + w161row + vmap(post)
a3 = block + "# --- T-141 s2 lane face"
r3 = block162 + "# --- T-141 s2 lane face"

# --- a4: PASS snippet claim insertion ------------------------------------------
cs = n1src.find('"+ W161 materializer face')
assert cs > 0, "W161 claim start not found"
ce = n1src.find('"r785 bm-a] "', cs) + len('"r785 bm-a] "')
assert 0 < cs < ce, "W161 claim end not found"
claim161 = n1src[cs:ce]
assert claim161 == io.open(r"results\_r787bma_w162_probe_n1_claim.txt",
                           encoding="utf-8", newline="").read(), "claim face drift vs probe"
a4 = '"r785 bm-a] "' + CRLF + '          "+ T-141 s2 "'
r4 = '"r785 bm-a] "' + CRLF + "          " + vmap_fix(claim161, "claim") + CRLF + '          "+ T-141 s2 "'

# --- apply the four edits -------------------------------------------------------
edit(PF, [(a1, r1n)])
edit(N1, [(a2, r2), (a3, r3), (a4, r4)])

# --- post-edit structural assertions --------------------------------------------
import sys
sys.path.insert(0, ".")
sys.path.insert(0, "scripts")
import importlib
import perpetual_faces as pf
importlib.reload(pf)
assert sorted(pf.N1_BANDS)[-1] == 162 and len(pf.N1_BANDS) == 160, \
    "pf N1_BANDS row-count drift after W162 insert"
assert pf.N1_BANDS[162] == {"a": (371_204, 373_203),
                            "b_exit": (373_204, 373_403),
                            "engine_owner": "bm-a"}, "W162 row face drift"
assert pf.N1_BANDS[161] == {"a": (369_004, 371_003),
                            "b_exit": (371_004, 371_203),
                            "engine_owner": "bm-a"}, "W161 row survived (r560 no-replace law)"
import perpetual_faces_n1 as n1mod
importlib.reload(n1mod)
assert n1mod.WAVE_CONFIGS[162]["a_seed_base"] == 371_204 and \
    n1mod.WAVE_CONFIGS[162]["b_exit_seed_base"] == 373_204, "W162 seed bases drift"
assert n1mod.WAVE_CONFIGS[162]["shard_subdir"] == "n1_w162" and \
    n1mod.WAVE_CONFIGS[162]["out_name"] == "n1_w162_results.json", "W162 path drift"
assert n1mod.WAVE_CONFIGS[162]["prereg"].startswith("research/PERPETUAL_N1_W162_PREREG.md"), \
    "W162 per-wave prereg citation drift"
assert os.path.exists(os.path.join("research", "PERPETUAL_N1_W162_PREREG.md")), \
    "W162 per-wave prereg missing on disk"

# materializer chain now 138..W161row (n=24)
n2 = io.open(N1, encoding="utf-8", newline="").read()
w2 = n2.find("# --- W162 materializer face")
t3 = n2.find("# --- T-141 s2 lane face", w2)
blk2 = n2[w2:t3]
chain_rows2 = re.findall(r"assert pf\.N1_BANDS\[(\d+)\]",
                         blk2[blk2.find("assert pf.N1_BANDS[138]"):
                              blk2.find("# prior-wave disjointness")])
assert chain_rows2 == [str(x) for x in range(138, 162)], chain_rows2

# r773 pit law leg 3: full-file start>end malformed-window scans on BOTH files
for path in (PF, N1):
    txt = io.open(path, encoding="utf-8", newline="").read()
    bad = [m.group() for m in re.finditer(r"(\d{3})_(\d{3})\.\.(\d{3})_(\d{3})", txt)
           if int(m.group(3)) < int(m.group(1))]
    assert not bad, f"malformed windows remain in {path}: {bad[:4]}"

# W163 projection prose present in the new W162 blocks (gate leg3 verbatim)
pf2 = io.open(PF, encoding="utf-8", newline="").read()
assert f"# {W163p_A} CLEAN hops=0 / B first-clean {W163p_B}" in pf2, "pf W163p prose missing"
assert "W163 A window; W163 freezer MUST re-derive on the post-W162" in pf2, \
    "pf W163 freezer prose missing"
# r776 fragment-needle law: the freezer prose in the n1 entry is split
# across python-string fragments -- a contiguous needle is a false-negative
# (r775/r781 law); assert the within-fragment shapes instead.
assert '"W163 A window; W163 freezer MUST re-derive on the "' in n2, "n1 W163 freezer fragment missing"
assert '"W162 B band 373_204..373_403 will refuse the naive "' in n2, "n1 W162-band refuse fragment missing"
assert f"A first-clean {W163p_A} " in n2 and f"B first-clean {W163p_B} CLEAN" in n2, \
    "n1 W163p prose missing"
# honesty faces landed (self-ack deferred + payload facts helper +
# direct-FF delivery + anti-drift registered-row citation)
assert "move deferred to the W163 finalize window" in pf2, "pf self-ack fixup missing"
assert "fleet/inbox at freeze time -- honest state);" in pf2, "pf self-ack tail fixup missing"
assert "move deferred to the W163 finalize window" in n2, "mat self-ack fixup missing"
assert "fleet/inbox at freeze time -- honest state)." in n2, "mat self-ack tail missing"
assert "facts helper" in pf2 and "facts helper" in n2, "payload facts-helper fixup missing"
assert "r787 pre-seat" in pf2 and "r787 pre-seat" in n2, "push session r787 face missing"
assert "direct fast-forward behind-0" in pf2 and "direct fast-forward behind-0" in n2, \
    "direct-FF delivery face missing"
# r776 fragment-needle law: the registered-row citation is split across
# python string fragments -- assert the within-fragment shapes
assert '"number law after the REGISTERED W161 row bm-a r785 freeze "' in n2, \
    "W161 row citation frag1 missing"
assert '"678a07d4f, SINGLE STATE zero seat gap W2..W161 all "' in n2, \
    "W161 row citation frag2 missing"
assert '"finalize one-pass bm-a r786, net chain head 759,612, "' in n2, \
    "W161 finalize one-pass frag missing"
assert n2.count("W161 finalize one-pass bm-a r786") == 1, "W161 finalize one-pass count drift"
assert "W161 bm-a r786 one-pass" in n2, "COP face missing"
assert "bm-a r785 freeze 678a07d4f" in n2, "mat header registered-row citation missing"
assert "ee04482a2" not in blk2, "stale W160 sha residue in new W162 block"
assert "finalize one-pass bm-a r787" not in n2, "stale r787 finalize residue"
# no stale round/seat/number leftovers in the NEW W162 blocks only (the
# frozen W161/W160 faces legitimately retain their historical citations;
# the mat CHAIN rows are verbatim prior-wave pinned constants (r307) --
# historical band values there are legitimate, so the mat scan covers
# only the freshly vmap'd pre (header) + post (band-facts) faces)
i2 = pf2.find("    # W162 (bm-a r787 freeze")
j2 = pf2.find(EO, i2) + len(EO)
newpfblk = pf2[i2:j2]
k2 = n2.find('162: {"batch"')
m2 = n2.find(EO, k2) + len(EO)
newentry = n2[k2:m2]
cs2 = n2.find('"+ W162 materializer face')
ce2 = n2.find('"r787 bm-a] "', cs2) + len('"r787 bm-a] "')
newclaim = n2[cs2:ce2]
ci2 = blk2.find("assert pf.N1_BANDS[138]")
cj2 = blk2.find("# prior-wave disjointness")
mat_new_faces = blk2[:ci2] + blk2[cj2:]
assert i2 > 0 and k2 > 0 and cs2 > 0, "new W162 block anchors missing"
for tag, seg in (("pf", newpfblk), ("entry", newentry),
                 ("mat", mat_new_faces), ("claim", newclaim)):
    for stale in ("r783 gate", "r784 sec8", "r785 pre-seat", "r785 bm-a freeze",
                  "bm-a r783 freeze", "MSG-2026-10-06-165x", "0371f2093", "bma-w161-seat",
                  "MSG-165x", "merge-absorb", "369_004", "368_804", "369_003",
                  "371_003", "757,412", "349,920", "ee04482a2", "6957f509e",
                  "bm-b r779", "a2d002357", "twentieth", "seventy-seventh",
                  "ONE HUNDRED-AND-FIFTY-FIRST", "engine_owner rows 150",
                  "rows 76 + candidate", "W161 arc generator"):
        assert stale not in seg, f"stale {stale!r} residue in new W162 {tag} block"
        # 371_004/371_204/371_403 are NOT in the stale set: they
        # legitimately appear in the new W162 blocks as the naive-A/B
        # starts and the W161 B band start (r785 368_804-precedent note)
# corrupted historical faces must remain eradicated from both files
for path in (PF, N1):
    txt = io.open(path, encoding="utf-8", newline="").read()
    assert "362_204..362_003" not in txt and "362_404..360_403" not in txt, \
        f"r772 malformed-window residue in {path}"
# the W161 same-window heal (pre-probe) is carried into the new block via
# the @JB@ token: the W162 B-assert prose cites the W162 jump target
# 373_204. The materializer face is SINGLE-LIVE (migrates to the newest
# wave each freeze -- the healed W161 prose was consumed by this vmap,
# which is the heal's purpose: kill the leak before propagation; heal
# receipt + git history carry the record)
assert "own-wave A window reserved jumps to 373_204, first-clean " in blk2, \
    "W162 healed-fragment face missing"
assert "own-wave A window reserved jumps to 368_804, first-clean" not in blk2, \
    "vmap-leak residue in new block"

print("post-edit structural assertions PASS: N1_BANDS 160 rows tail W162, "
      "W161 row intact, WAVE_CONFIGS[162] seeded, chain 138..161 n=24, "
      "W163p prose == r787 gate leg3 verbatim, honesty fixups landed "
      "(self-ack deferred / facts-helper payload / direct-FF delivery / "
      "anti-drift registered-row cite), full-file malformed-window scans "
      "CLEAN on both files, W161 same-window heal disclosed+carried")
