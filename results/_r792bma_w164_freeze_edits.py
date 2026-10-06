# -*- coding: utf-8 -*-
"""r792 bm-a W164 freeze edits: four insertions (pf N1_BANDS[164] row +
n1 WAVE_CONFIGS[164] entry + n1 W164 materializer block refresh +
n1 PASS snippet claim insertion).

Bloodline: r789 _r789bma_w163_freeze_edits.py machinery (r773 pit law
freeze-editor compliance + r776 fragment-needle law + r781
verify-separation law), W164 facts live-registry-driven:
  - band gate results/_r792bma_w164_band_gate.json rc0 ADMIT
    (A 375_604..377_603 staircase TWENTY-THIRD instance E36 hops=1 past
    the W163 B band; naive 375_404..377_403 refused at its own start by
    the registered W163 B band 375_404..375_603; B 377_604..377_803
    own-A mutual exclusion hops=1, naive 375_604..375_803);
  - pre-seat probe results/_r792bma_w164_probe_receipt.json ADMIT,
    dual-window parity True (gate leg1 parity_with_probe);
  - seat MSG-2026-10-06-194x-bma-w164-seat published 469d40896
    (r792 pre-seat push, direct fast-forward behind-0; r565 law: on
    origin BEFORE this freeze commit);
  - per-wave prereg research/PERPETUAL_N1_W164_PREREG.md (r792 session,
    banned gate ADMIT 0);
  - W163 finalize one-pass r790: ledger head 764,012, merged pool
    K=356,520 (n1_w163_results.json machine-read);
  - W163 freeze r789 sha 18231a529 (the REGISTERED W163 row citation);
  - W165+ projection (gate leg3 verbatim): A first-clean 377_604..379_603
    / B first-clean 377_804..378_003, naive-B-inside-naive-A, the
    registered W164 B band will refuse the naive W165 A window.

r773 pit law compliance:
  (1) full string-face inventory empirically probed BEFORE TOK
      (_r792bma_w164_face_probe.py -- four face dumps + needle-count
      receipt);
  (2) composite band strings tokenized WHOLE (no bare-seed-prefix
      tokens; every dotted band / seed-base row / jump phrase / sha
      composite is a single token; bare 163/162 run LAST);
  (3) post-edit full-file start>end malformed-window regex scan on BOTH
      touched files;
  (4) every projection value re-derived FROM the on-disk gate receipts
      (r587 never-transcribe law);
  (5) r776 fragment-needle law: all needles taken from the PHYSICAL
      probe-dumped shapes (python-string fragments / comment lines,
      CRLF-exact);
  (6) NO fixups this window: the W163 source faces carry the 3-item
      payload prose already (r789 honesty fixup lineage) and the r792
      delivery window is a 3-file direct-FF push -- all prose faces stay
      true under wave/session/band shifts alone;
  (7) anti-drift composites (@REGROW@/@PROW@ family: bm-a r789 freeze
      18231a529) run BEFORE the session tokens so the registered-prior-
      row sha pairing can never be torn (r785 heal-1 class eradicated
      at source);
  (8) MSG-183x dual-face discipline: the N3-R1 ruling citation
      ('used-seed band 70_000..70_005 (MSG-183x)') is a HISTORICAL
      CONSTANT protected whole BEFORE any seat-token pass; only the
      seat-shaped 'seat MSG-183x tail' shifts to the W164 seat.

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
gate = json.load(open("results/_r792bma_w164_band_gate.json", encoding="utf-8"))
leg1, leg3 = gate["legs"]["leg1"], gate["legs"]["leg3"]
assert gate["verdict"] == "ADMIT", gate["verdict"]
assert leg1["A"] == [375604, 377603] and leg1["B"] == [377604, 377803], leg1
assert leg1["hops_A"] == 1 and leg1["hops_B"] == 1
assert leg1["ARITH_A"] == [375404, 377403], leg1["ARITH_A"]
assert leg1["B_naive_first_clean"] == [375604, 375803], leg1["B_naive_first_clean"]
assert leg1["parity_with_probe"] is True
probe = json.load(open("results/_r792bma_w164_probe_receipt.json", encoding="utf-8"))
assert probe["verdict"] == "ADMIT" and probe["bands"] == {"A": "375604_377603", "B": "377604_377803"}, probe
w163res = json.load(open("results/perpetual_faces/n1_w163_results.json", encoding="utf-8"))
assert w163res["null_pool_cumulative"]["merged"]["n_values"] == 356520, "W163 merged K drift"
assert w163res["null_pool_cumulative"]["merged"]["n_values"] + 2200 == 358720, "W164 K projection arithmetic"


def u(s):  # "377604..379603" -> "377_604..379_603"
    def g(part):
        return re.sub(r"(\d)(?=(\d{3})+$)", r"\1_", part)
    a, b = s.split("..")
    return f"{g(a)}..{g(b)}"


W165p_A = u(leg3["W165p_A"])
W165p_B = u(leg3["W165p_B"])
assert W165p_A == "377_604..379_603" and W165p_B == "377_804..378_003", (W165p_A, W165p_B)
assert leg3["W165p_B_lands_inside_W165p_A"] is True

# --- ordered value-map (tokens first, then back-substitution) ---------------
TOK = [
    # whole-line seed-base rows (entry face; bands + ordinal carried WHOLE)
    ('"a_seed_base": 373_404,        # law sec.4 W163 A: 373_404..375_403 (FIRST-CLEAN past the registered W162 B band; arithmetic 373_204..375_203 REFUSED at own start by the W162 B band; hops=1; A-hops-prior-B staircase twenty-second instance, E36 card)', "@ASROW@"),
    ('"b_exit_seed_base": 375_404,   # law sec.4 W163 B: 375_404..375_603 (FIRST-CLEAN past the own-wave A window; arithmetic 373_404..373_603 lands inside own-A, same-freeze mutual exclusion W141 precedent; reserved walk hops=1; B base == own-A tail+1)', "@BSROW@"),
    # row + entry carriers
    ('163: {"a": (373_404, 375_403), "b_exit": (375_404, 375_603),', "@RROW@"),
    ('163: {"batch"', "@RENTRY@"),
    # registered-prior-row citations (machine-verified sha pairing; the
    # anti-drift composites -- MUST precede every session/round token)
    ('W162 row bm-a r787 freeze', "@PROW1@"),
    ('764cd882a, SINGLE STATE zero seat gap W2..W162 all', "@PROW2@"),
    ('bm-a r787 freeze 764cd882a', "@REGROW@"),
    # freeze-session composites
    ('bm-a r789 freeze', "@FZH@"),
    ('r789 bm-a freeze', "@MFZH@"),
    # prior-finalize citations (W162 finalize r788 -> W163 finalize r790)
    ('W162 finalize landed same-window r788', "@FW@"),
    ('W162 finalize one-pass bm-a r788', "@FOPM2@"),
    ('W162 bm-a r788 one-pass', "@FOP@"),
    # gate / probe receipt citations (probe r792, gate r792)
    ('_r789bma_w163_probe_receipt.json', "@PRC@"),
    ('_r789bma_w163_band_gate.json', "@BGR@"),
    # prior gate / sec8 session refs (W162 gate r787 -> W163 gate r789;
    # W162 finalize sec8 r788 -> W163 finalize sec8 r790)
    ('r787 gate leg3', "@GATE@"),
    ('r787 gate', "@GATEP@"),
    ('r788 sec8 succession', "@SEC8@"),
    ('r788 sec8', "@SEC8M@"),
    # seat tokens
    ('MSG-2026-10-06-183x', "@SEAT@"),
    ('bma-w163-seat', "@SEATW@"),
    ('189157de8', "@SEATSHA@"),
    # N3-R1 ruling citation = HISTORICAL CONSTANT (protects the MSG-183x
    # face that collides with the W163 seat shorthand; whole-phrase pin)
    ('used-seed band 70_000..70_005 (MSG-183x)', "@N3R1C@"),
    # seat-shaped MSG-183x fragment (mat block; the ONLY shiftable one)
    ('seat MSG-183x tail', "@SEATTAIL@"),
    # W165 projection bands (gate leg3 verbatim, whole; BEFORE all band
    # tokens and seed backstops -- r773 pit law)
    ('375_404..377_403', "@PA@"),
    ('375_604..375_803', "@PB@"),
    # jump phrases (longest first; fragment-safe; BEFORE @BB@ which
    # shares the B-band substring)
    ('jumps to 375_404, first-clean 375_404..375_603 hops=1', "@JN@"),
    ('jumps to 375_404 -> 375_404..375_603,', "@JP@"),
    ('375_404 and lands 375_404..375_603', "@JAND@"),
    # the W163 B-assert jump fragment (rides the @JB@ token; W164 target
    # 377_604 -- SINGLE-LIVE materializer face migration lineage)
    ('own-wave A window reserved jumps to 375_404, first-clean ', "@JB@"),
    # assert composites
    ('== 373_404 == 373_403 + 1', "@ASB@"),
    ('== 375_404 == 375_403 + 1', "@BSB@"),
    ('set(range(373_404, 375_404))', "@ARITHA@"),
    ('set(range(375_404, 375_604))', "@ARB@"),
    # dotted band geometry
    ('373_204..375_203', "@NA@"),
    ('373_204..373_403', "@OB@"),
    ('373_404..375_403', "@AB@"),
    ('373_404..373_603', "@NB@"),
    ('375_404..375_603', "@BB@"),
    # base-relation composites (the pf band-facts comment AND the mat
    # assert prose BOTH carry the prior-B-tail+1 face '373_403+1' -- the
    # blanket fires twice in the mat face, both correctly; verified by
    # grep never eyeball, r781 lesson)
    ('373_403+1', "@ABASE@"),
    ('375_403+1', "@BBASE@"),
    # rounds (composites above; then own-session bare; then prior-session
    # bares -- 'r789'->'r792' FIRST so the r787->r789 backstop output is
    # never re-mapped)
    ('r789', "@RW@"),
    ('r788', "@FRW@"),
    ('r787', "@PRW@"),
    # identity / stats / ordinals
    ('PERPETUAL_N1_W163_PREREG.md', "@PF@"),
    ('PERPETUAL-N1-W163', "@B@"),
    ('n1_w163_results.json', "@OD@"),
    ('n1_w163', "@SD@"),
    ('n1w163', "@SD2@"),
    ('761,812', "@LEDG@"),
    ('354,320', "@K1@"),
    ('ONE HUNDRED-AND-FIFTY-THIRD', "@ORDW@"),
    ('engine_owner rows 152', "@R151@"),
    ('rows 78 + candidate', "@ROWS76@"),
    ('seventy-ninth', "@SVN77@"),
    ('twenty-second', "@ST21@"),
    # wave numbers (higher first: W164 projection -> W165; then W163->W164,
    # W162->W163)
    ('W164', "@WN2@"),
    ('W163', "@WN@"),
    ('W162', "@W@"),
    # bare numerals LAST (every longer carrier tokenized above; 163 before
    # 162 so the 162->163 output is never re-mapped)
    ('163', "@IDX@"),
    ('162', "@IDX2@"),
]
BACK = [
    ("@ASROW@", '"a_seed_base": 375_604,        # law sec.4 W164 A: 375_604..377_603 (FIRST-CLEAN past the registered W163 B band; arithmetic 375_404..377_403 REFUSED at own start by the W163 B band; hops=1; A-hops-prior-B staircase twenty-third instance, E36 card)'),
    ("@BSROW@", '"b_exit_seed_base": 377_604,   # law sec.4 W164 B: 377_604..377_803 (FIRST-CLEAN past the own-wave A window; arithmetic 375_604..375_803 lands inside own-A, same-freeze mutual exclusion W141 precedent; reserved walk hops=1; B base == own-A tail+1)'),
    ("@RROW@", '164: {"a": (375_604, 377_603), "b_exit": (377_604, 377_803),'),
    ("@RENTRY@", '164: {"batch"'),
    ("@PROW1@", "W163 row bm-a r789 freeze"),
    ("@PROW2@", "18231a529, SINGLE STATE zero seat gap W2..W163 all"),
    ("@REGROW@", "bm-a r789 freeze 18231a529"),
    ("@FZH@", "bm-a r792 freeze"),
    ("@MFZH@", "r792 bm-a freeze"),
    ("@FW@", "W163 finalize landed same-window r790"),
    ("@FOPM2@", "W163 finalize one-pass bm-a r790"),
    ("@FOP@", "W163 bm-a r790 one-pass"),
    ("@PRC@", "_r792bma_w164_probe_receipt.json"),
    ("@BGR@", "_r792bma_w164_band_gate.json"),
    ("@GATE@", "r789 gate leg3"),
    ("@GATEP@", "r789 gate"),
    ("@SEC8@", "r790 sec8 succession"),
    ("@SEC8M@", "r790 sec8"),
    ("@SEAT@", "MSG-2026-10-06-194x"),
    ("@SEATW@", "bma-w164-seat"),
    ("@SEATSHA@", "469d40896"),
    ("@N3R1C@", "used-seed band 70_000..70_005 (MSG-183x)"),
    ("@SEATTAIL@", "seat MSG-194x tail"),
    ("@PA@", "377_604..379_603"),
    ("@PB@", "377_804..378_003"),
    ("@JN@", "jumps to 377_604, first-clean 377_604..377_803 hops=1"),
    ("@JP@", "jumps to 377_604 -> 377_604..377_803,"),
    ("@JAND@", "377_604 and lands 377_604..377_803"),
    ("@JB@", "own-wave A window reserved jumps to 377_604, first-clean "),
    ("@ASB@", "== 375_604 == 375_603 + 1"),
    ("@BSB@", "== 377_604 == 377_603 + 1"),
    ("@ARITHA@", "set(range(375_604, 377_604))"),
    ("@ARB@", "set(range(377_604, 377_804))"),
    ("@NA@", "375_404..377_403"),
    ("@OB@", "375_404..375_603"),
    ("@AB@", "375_604..377_603"),
    ("@NB@", "375_604..375_803"),
    ("@BB@", "377_604..377_803"),
    ("@ABASE@", "375_603+1"),
    ("@BBASE@", "377_603+1"),
    ("@RW@", "r792"),
    ("@FRW@", "r790"),
    ("@PRW@", "r789"),
    ("@PF@", "PERPETUAL_N1_W164_PREREG.md"),
    ("@B@", "PERPETUAL-N1-W164"),
    ("@OD@", "n1_w164_results.json"),
    ("@SD@", "n1_w164"),
    ("@SD2@", "n1w164"),
    ("@LEDG@", "764,012"),
    ("@K1@", "356,520"),
    ("@ORDW@", "ONE HUNDRED-AND-FIFTY-FOURTH"),
    ("@R151@", "engine_owner rows 153"),
    ("@ROWS76@", "rows 79 + candidate"),
    ("@SVN77@", "eightieth"),
    ("@ST21@", "twenty-third"),
    ("@WN2@", "W165"),
    ("@WN@", "W164"),
    ("@W@", "W163"),
    ("@IDX@", "164"),
    ("@IDX2@", "163"),
]


def vmap(s: str) -> str:
    for a, b in TOK:
        s = s.replace(a, b)
    for a, b in BACK:
        s = s.replace(a, b)
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

# face-source zero-drift gate vs the r792 probe dumps
EO = '"engine_owner": "bm-a"},'
i1 = pfsrc.find("    # W163 (bm-a r789 freeze")
assert i1 > 0, "pf W163 comment block not found"
r1 = pfsrc.find('163: {"a": (373_404', i1)
assert r1 > i1, "pf W163 row not after comment block"
j1 = pfsrc.find(EO, r1) + len(EO)
block163_pf = pfsrc[i1:j1]
assert block163_pf == io.open(r"results\_r792bma_w164_probe_pf_block.txt",
                              encoding="utf-8", newline="").read(), "pf face drift vs probe"
assert block163_pf.count("engine_owner") == 1 and "764cd882a" not in block163_pf
assert "375_404..377_403 CLEAN hops=0 / B first-clean 375_604..375_803" in block163_pf

# --- a1: pf.py W163 comment block + row -> append W164 comment block + row ----
a1 = block163_pf + CRLF + "}"
r1n = block163_pf + CRLF + vmap(block163_pf) + CRLF + "}"

# --- a2: n1.py WAVE_CONFIGS entry ----------------------------------------------
k = n1src.find('163: {"batch"')
assert k > 0, "n1 W163 entry not found"
m = n1src.find(EO, k) + len(EO)
entry163 = n1src[k:m]
assert entry163 == io.open(r"results\_r792bma_w164_probe_n1_entry.txt",
                          encoding="utf-8", newline="").read(), "entry face drift vs probe"
a2 = entry163 + CRLF + "                       }"
r2 = entry163 + CRLF + "                       " + vmap(entry163) + CRLF + "                       }"

# --- a3: materializer block (chain split-verbatim + one-row extension) --------
w = n1src.find("# --- W163 materializer face")
t2 = n1src.find("# --- T-141 s2 lane face", w)
assert 0 < w < t2, "materializer anchors missing"
block = n1src[w:t2]
assert block == io.open(r"results\_r792bma_w164_probe_n1_mat.txt",
                        encoding="utf-8", newline="").read(), "mat face drift vs probe"
ci = block.find("assert pf.N1_BANDS[138]")
cj = block.find("# prior-wave disjointness")
assert 0 < ci < cj, "chain boundaries missing"
pre, chain, post = block[:ci], block[ci:cj], block[cj:]
chain_rows = re.findall(r"assert pf\.N1_BANDS\[(\d+)\]", chain)
assert chain_rows == [str(x) for x in range(138, 163)], chain_rows
w163row = ('assert pf.N1_BANDS[163] == {"a": (373_404, 375_403),' + CRLF +
           '                                    "b_exit": (375_404, 375_603),' + CRLF +
           '                                    "engine_owner": "bm-a"}, \\' + CRLF +
           '            "registered W163 row parity drift (r307; bm-a r789)"' + CRLF +
           "        ")
# payload/delivery prose lives ONLY in the mat pre (header comment face);
# the post (disjointness/band-facts/assert face) passes through plain vmap
block164 = vmap(pre) + chain + w163row + vmap(post)
a3 = block + "# --- T-141 s2 lane face"
r3 = block164 + "# --- T-141 s2 lane face"

# --- a4: PASS snippet claim insertion ------------------------------------------
cs = n1src.find('"+ W163 materializer face')
assert cs > 0, "W163 claim start not found"
ce = n1src.find('"r789 bm-a] "', cs) + len('"r789 bm-a] "')
assert 0 < cs < ce, "W163 claim end not found"
claim163 = n1src[cs:ce]
assert claim163 == io.open(r"results\_r792bma_w164_probe_n1_claim.txt",
                           encoding="utf-8", newline="").read(), "claim face drift vs probe"
a4 = '"r789 bm-a] "' + CRLF + '          "+ T-141 s2 "'
r4 = '"r789 bm-a] "' + CRLF + "          " + vmap(claim163) + CRLF + '          "+ T-141 s2 "'

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
assert sorted(pf.N1_BANDS)[-1] == 164 and len(pf.N1_BANDS) == 162, \
    "pf N1_BANDS row-count drift after W164 insert"
assert pf.N1_BANDS[164] == {"a": (375_604, 377_603),
                            "b_exit": (377_604, 377_803),
                            "engine_owner": "bm-a"}, "W164 row face drift"
assert pf.N1_BANDS[163] == {"a": (373_404, 375_403),
                            "b_exit": (375_404, 375_603),
                            "engine_owner": "bm-a"}, "W163 row survived (r560 no-replace law)"
import perpetual_faces_n1 as n1mod
importlib.reload(n1mod)
assert n1mod.WAVE_CONFIGS[164]["a_seed_base"] == 375604 and \
    n1mod.WAVE_CONFIGS[164]["b_exit_seed_base"] == 377604, "W164 seed bases drift"
assert n1mod.WAVE_CONFIGS[164]["shard_subdir"] == "n1_w164" and \
    n1mod.WAVE_CONFIGS[164]["out_name"] == "n1_w164_results.json", "W164 path drift"
assert n1mod.WAVE_CONFIGS[164]["prereg"].startswith("research/PERPETUAL_N1_W164_PREREG.md"), \
    "W164 per-wave prereg citation drift"
assert os.path.exists(os.path.join("research", "PERPETUAL_N1_W164_PREREG.md")), \
    "W164 per-wave prereg missing on disk"

# materializer chain now 138..W163row (n=26)
n2 = io.open(N1, encoding="utf-8", newline="").read()
w2 = n2.find("# --- W164 materializer face")
t3 = n2.find("# --- T-141 s2 lane face", w2)
blk2 = n2[w2:t3]
chain_rows2 = re.findall(r"assert pf\.N1_BANDS\[(\d+)\]",
                         blk2[blk2.find("assert pf.N1_BANDS[138]"):
                              blk2.find("# prior-wave disjointness")])
assert chain_rows2 == [str(x) for x in range(138, 164)], chain_rows2

# r773 pit law leg 3: full-file start>end malformed-window scans on BOTH files
for path in (PF, N1):
    txt = io.open(path, encoding="utf-8", newline="").read()
    bad = [m.group() for m in re.finditer(r"(\d{3})_(\d{3})\.\.(\d{3})_(\d{3})", txt)
           if int(m.group(3)) < int(m.group(1))]
    assert not bad, f"malformed windows remain in {path}: {bad[:4]}"

# W165 projection prose present in the new W164 blocks (gate leg3 verbatim)
pf2 = io.open(PF, encoding="utf-8", newline="").read()
assert f"# {W165p_A} CLEAN hops=0 / B first-clean {W165p_B}" in pf2, "pf W165p prose missing"
assert "W165 A window; W165 freezer MUST re-derive on the post-W164" in pf2, \
    "pf W165 freezer prose missing"
# r776 fragment-needle law: the freezer prose in the n1 entry is split
# across python-string fragments -- a contiguous needle is a false-negative
# (r775/r781 law); assert the within-fragment shapes instead.
assert '"W165 A window; W165 freezer MUST re-derive on the "' in n2, "n1 W165 freezer fragment missing"
assert '"W164 B band 377_604..377_803 will refuse the naive "' in n2, "n1 W164-band refuse fragment missing"
assert f"A first-clean {W165p_A} " in n2 and f"B first-clean {W165p_B} CLEAN" in n2, \
    "n1 W165p prose missing"
# honesty faces landed (self-ack deferred to W165 finalize + 3-item payload +
# direct-FF delivery + anti-drift registered-row citation)
assert "move deferred to the W165 finalize window" in pf2, "pf self-ack face missing"
assert "fleet/inbox at freeze time -- honest state);" in pf2, "pf self-ack tail missing"
assert "move deferred to the W165 finalize window" in n2, "mat self-ack face missing"
assert "fleet/inbox at freeze time -- honest state)." in n2, "mat self-ack tail missing"
assert "payload = seat MSG + pre-seat probe + probe receipt;" in pf2, "pf 3-item payload face missing"
assert '"seat MSG + pre-seat probe + probe receipt; "' in n2, "entry 3-item payload face missing"
assert "= seat MSG + pre-seat probe + probe receipt;" in n2, "mat 3-item payload face missing"
assert "r792 pre-seat" in pf2 and "r792 pre-seat" in n2, "push session r792 face missing"
assert "direct fast-forward behind-0" in pf2 and "direct fast-forward behind-0" in n2, \
    "direct-FF delivery face missing"
# r776 fragment-needle law: the registered-row citation is split across
# python string fragments -- assert the within-fragment shapes
assert '"number law after the REGISTERED W163 row bm-a r789 freeze "' in n2, \
    "W163 row citation frag1 missing"
assert '"18231a529, SINGLE STATE zero seat gap W2..W163 all "' in n2, \
    "W163 row citation frag2 missing"
assert '"finalize one-pass bm-a r790, net chain head 764,012, "' in n2, \
    "W163 finalize one-pass frag missing"
assert n2.count("W163 finalize one-pass bm-a r790") == 1, "W163 finalize one-pass count drift"
assert "W163 bm-a r790 one-pass" in n2, "COP face missing"
assert "bm-a r789 freeze 18231a529" in n2, "mat header registered-row citation missing"
assert "764cd882a" not in blk2, "stale W162 sha residue in new W164 block"
assert "finalize one-pass bm-a r792" not in n2, "stale r792 finalize residue"
# mat assert-prose base shape migrated (the @ABASE@ face fired twice:
# band-facts comment AND assert prose, both 'B band tail 375_603+1')
assert '"W163 B band tail 375_603+1 (arithmetic continuation "' in blk2, \
    "mat A-base assert prose missing"
# N3-R1 ruling constant survived the MSG-183x dual-face discipline
assert "used-seed band 70_000..70_005 (MSG-183x)" in blk2, "N3-R1 ruling constant damaged"
assert "seat MSG-194x tail" in blk2, "seat-tail shift missing"
# no stale round/seat/number leftovers in the NEW W164 blocks only (the
# frozen W163/W162 faces legitimately retain their historical citations;
# the mat CHAIN rows are verbatim prior-wave pinned constants (r307) --
# historical band values there are legitimate, so the mat scan covers
# only the freshly vmap'd pre (header) + post (band-facts) faces)
i2 = pf2.find("    # W164 (bm-a r792 freeze")
j2 = pf2.find(EO, i2) + len(EO)
newpfblk = pf2[i2:j2]
k2 = n2.find('164: {"batch"')
m2 = n2.find(EO, k2) + len(EO)
newentry = n2[k2:m2]
cs2 = n2.find('"+ W164 materializer face')
ce2 = n2.find('"r792 bm-a] "', cs2) + len('"r792 bm-a] "')
newclaim = n2[cs2:ce2]
ci2 = blk2.find("assert pf.N1_BANDS[138]")
cj2 = blk2.find("# prior-wave disjointness")
mat_new_faces = blk2[:ci2] + blk2[cj2:]
assert i2 > 0 and k2 > 0 and cs2 > 0, "new W164 block anchors missing"
for tag, seg in (("pf", newpfblk), ("entry", newentry),
                 ("mat", mat_new_faces), ("claim", newclaim)):
    for stale in ("r787 gate", "r788 sec8", "r789 pre-seat", "W163 (bm-a r789",
                  "bm-a r789 freeze, seat", "MSG-2026-10-06-183x", "189157de8",
                  "bma-w163-seat", "seat MSG-183x tail", "MSG-175x", "bma-w162-seat",
                  "merge-absorb", "373_204..375_203", "373_204..373_403",
                  "373_404..375_403", "373_404..373_603", "371_004", "371_204",
                  "371_403", "371_203", "369_004", "373_003", "373_203", "373_204",
                  "373_404", "373_603", "375_203", "761,812", "354,320", "759,612",
                  "352,120", "ee04482a2", "678a07d4f", "6957f509e", "764cd882a",
                  "1d43d7906", "bm-b r779", "a2d002357", "twentieth",
                  "twenty-first", "twenty-second", "seventy-seventh",
                  "seventy-eighth", "seventy-ninth",
                  "ONE HUNDRED-AND-FIFTY-SECOND", "ONE HUNDRED-AND-FIFTY-THIRD",
                  "engine_owner rows 151", "engine_owner rows 152",
                  "rows 77 + candidate", "rows 78 + candidate", "facts helper",
                  "arc generator", "163: {", "r785 gate", "r786 sec8"):
        assert stale not in seg, f"stale {stale!r} residue in new W164 {tag} block"
        # 375_404 is NOT in the stale set: it legitimately appears in the
        # new W164 blocks as the naive-A start == the registered W163 B
        # band start and the prior-B-band value (373_204-precedent note
        # in the r789 lineage)
# corrupted historical faces must remain eradicated from both files
for path in (PF, N1):
    txt = io.open(path, encoding="utf-8", newline="").read()
    assert "362_204..362_003" not in txt and "362_404..360_403" not in txt, \
        f"r772 malformed-window residue in {path}"
# the W164 B-assert prose cites the W164 jump target 377_604 via the @JB@
# token (SINGLE-LIVE materializer face migrates to the newest wave each
# freeze; heal receipt + git history carry the record)
assert "own-wave A window reserved jumps to 377_604, first-clean " in blk2, \
    "W164 healed-fragment face missing"
assert "own-wave A window reserved jumps to 375_404, first-clean" not in blk2, \
    "vmap-leak residue in new block"

print("post-edit structural assertions PASS: N1_BANDS 162 rows tail W164, "
      "W163 row intact, WAVE_CONFIGS[164] seeded, chain 138..163 n=26, "
      "W165p prose == r792 gate leg3 verbatim, honesty faces landed "
      "(self-ack deferred to W165 / 3-item payload / direct-FF delivery / "
      "anti-drift registered-row cite / N3-R1 MSG-183x constant protected), "
      "full-file malformed-window scans CLEAN on both files, "
      "no same-window heal needed this window")
