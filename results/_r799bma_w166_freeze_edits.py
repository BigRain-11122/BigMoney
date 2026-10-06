# -*- coding: utf-8 -*-
"""r799 bm-a W166 freeze edits: four insertions (pf N1_BANDS[166] row +
n1 WAVE_CONFIGS[166] entry + n1 W166 materializer block refresh +
n1 PASS snippet claim insertion).

Bloodline: r789 _r789bma_w163_freeze_edits.py machinery (r773 pit law
freeze-editor compliance + r776 fragment-needle law + r781
verify-separation law), W166 facts live-registry-driven:
  - band gate results/_r797bma_w166_band_gate.json rc0 ADMIT
    (A 380_004..382_003 staircase TWENTY-FIFTH instance E36 hops=1 past
    the W165 B band; naive 379_804..381_803 refused at its own start by
    the registered W165 B band 379_804..380_003; B 382_004..382_203
    own-A mutual exclusion hops=1, naive 380_004..380_203);
  - pre-seat probe results/_r797bma_w166_probe_receipt.json ADMIT,
    dual-window parity True (gate leg1 parity_with_probe);
  - seat MSG-2026-10-06-223x-bma-w166-seat published d1dc12117
    (r797 pre-seat push, direct fast-forward behind-0; r565 law: on
    origin BEFORE this freeze commit);
  - per-wave prereg research/PERPETUAL_N1_W166_PREREG.md (r799 session,
    banned gate ADMIT 0);
  - W165 finalize one-pass r796: ledger head 768,412, merged pool
    K=360,920 (n1_w165_results.json machine-read);
  - W165 freeze r795 sha aebb94d2d (the REGISTERED W165 row citation);
  - W167+ projection (gate leg3 verbatim): A first-clean 382_004..384_003
    / B first-clean 382_204..382_403, naive-B-inside-naive-A, the
    registered W166 B band will refuse the naive W167 A window.

r773 pit law compliance:
  (1) full string-face inventory empirically probed BEFORE TOK
      (_r799bma_w166_face_probe.py -- four face dumps + needle-count
      receipt, rc0);
  (2) composite band strings tokenized WHOLE (no bare-seed-prefix
      tokens; every dotted band / seed-base row / jump phrase /
      round-sha composite is a single token; bare 165/164 run LAST);
  (3) post-edit full-file start>end malformed-window regex scan on BOTH
      touched files;
  (4) every projection value re-derived FROM the on-disk gate receipts
      (r587 never-transcribe law);
  (5) r776 fragment-needle law: all needles taken from the PHYSICAL
      probe-dumped shapes (python-string fragments / comment lines,
      CRLF-exact);
  (6) NO same-window heal needed: the W165 source faces carry no
      vmap-leak residue (r795 6-value honest-fix lineage landed clean;
      the W166 jump target 382_004 rides the @JB@ token);
  (7) anti-drift composite @REGROW@ (bm-a r795 freeze aebb94d2d) runs
      BEFORE the freeze-session token so the registered-prior-row sha
      pairing can never be torn by the session map.

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
gate = json.load(open("results/_r797bma_w166_band_gate.json", encoding="utf-8"))
leg1, leg3 = gate["legs"]["leg1"], gate["legs"]["leg3"]
assert gate["verdict"] == "ADMIT", gate["verdict"]
assert leg1["A"] == [380004, 382003] and leg1["B"] == [382004, 382203], leg1
assert leg1["hops_A"] == 1 and leg1["hops_B"] == 1
assert leg1["ARITH_A"] == [379804, 381803], leg1["ARITH_A"]
assert leg1["B_naive_first_clean"] == [380004, 380203], leg1["B_naive_first_clean"]
assert leg1["parity_with_probe"] is True
probe = json.load(open("results/_r797bma_w166_probe_receipt.json", encoding="utf-8"))
assert probe["verdict"] == "ADMIT" and probe["bands"] == {"A": "380004_382003", "B": "382004_382203"}, probe
w165res = json.load(open("results/perpetual_faces/n1_w165_results.json", encoding="utf-8"))
assert w165res["null_pool_cumulative"]["merged"]["n_values"] == 360920, "W165 merged K drift"
assert w165res["null_pool_cumulative"]["merged"]["n_values"] + 2200 == 363120, "W166 K projection arithmetic"
leg0 = gate["legs"]["leg0"]
assert leg0["rows"] == 163 and leg0["tail"] == "W165" and leg0["ordinal"] == 156 \
    and leg0["bma_ordinal"] == 82, leg0


def u(s):  # "382004..384003" -> "382_004..384_003"
    def g(part):
        return re.sub(r"(\d)(?=(\d{3})+$)", r"\1_", part)
    a, b = s.split("..")
    return f"{g(a)}..{g(b)}"


W167p_A = u(leg3["W167p_A"])
W167p_B = u(leg3["W167p_B"])
assert W167p_A == "382_004..384_003" and W167p_B == "382_204..382_403", (W167p_A, W167p_B)
assert leg3["W167p_B_lands_inside_W167p_A"] is True

# --- ordered value-map (tokens first, then back-substitution) ---------------
TOK = [
    # whole-line seed-base rows (entry face; bands + ordinal carried WHOLE)
    ('"a_seed_base": 377_804,        # law sec.4 W165 A: 377_804..379_803 (FIRST-CLEAN past the registered W164 B band; arithmetic 377_604..379_603 REFUSED at own start by the W164 B band; hops=1; A-hops-prior-B staircase twenty-fourth instance, E36 card)', "@ASROW@"),
    ('"b_exit_seed_base": 379_804,   # law sec.4 W165 B: 379_804..380_003 (FIRST-CLEAN past the own-wave A window; arithmetic 377_804..378_003 lands inside own-A, same-freeze mutual exclusion W141 precedent; reserved walk hops=1; B base == own-A tail+1)', "@BSROW@"),
    # row + entry carriers
    ('165: {"a": (377_804, 379_803), "b_exit": (379_804, 380_003),', "@RROW@"),
    ('165: {"batch"', "@RENTRY@"),
    # registered-prior-row citations (machine-verified sha pairing; the
    # anti-drift composite -- MUST precede every session/round token)
    ('W164 row bm-a r792 freeze', "@PROW1@"),
    ('f7d34e5a7, SINGLE STATE zero seat gap W2..W164 all', "@PROW2@"),
    ('bm-a r792 freeze f7d34e5a7', "@REGROW@"),
    # freeze-session composites
    ('bm-a r795 freeze', "@FZH@"),
    ('r795 bm-a freeze', "@MFZH@"),
    # prior-finalize citations (W164 finalize r793 -> W165 finalize r796;
    # FRAGMENT form per r781/r776 law: the entry tail physically splits
    # 'W164 ' (prior fragment) + CRLF + 'finalize one-pass bm-a r793, ...'
    # (within-fragment) -- the contiguous logical needle would count=0)
    ('W164 finalize landed same-window r793', "@FW@"),
    ('finalize one-pass bm-a r793', "@FOPM2@"),
    ('W164 bm-a r793 one-pass', "@FOP@"),
    # gate / probe receipt citations (W165 gate/probe session r793)
    ('_r793bma_w165_probe_receipt.json', "@PRC@"),
    ('_r793bma_w165_band_gate.json', "@BGR@"),
    # prior gate / sec8 session refs (W164 gate r792 -> W165 gate r793;
    # W164 sec8 r793 -> W165 sec8 r796)
    ('r792 gate leg3', "@GATE@"),
    ('r792 gate', "@GATEP@"),
    ('r793 sec8 succession', "@SEC8@"),
    ('r793 sec8', "@SEC8M@"),
    # own-wave gate-session prose + pre-seat push session (r793 -> r797)
    ('gate-derived r793', "@GDR@"),
    ('r793 pre-seat push', "@PSP@"),
    # seat tokens
    ('MSG-2026-10-06-205x', "@SEAT@"),
    ('bma-w165-seat', "@SEATW@"),
    ('MSG-205x', "@MSGS@"),
    ('4bdf63090', "@SEATSHA@"),
    # W167 projection bands (gate leg3 verbatim, whole; BEFORE all band
    # tokens and seed backstops -- r773 pit law)
    ('379_804..381_803', "@PA@"),
    ('380_004..380_203', "@PB@"),
    # jump phrases (longest first; fragment-safe; BEFORE @BB@ which
    # shares the B-band substring)
    ('jumps to 379_804, first-clean 379_804..380_003 hops=1', "@JN@"),
    ('jumps to 379_804 -> 379_804..380_003,', "@JP@"),
    ('379_804 and lands 379_804..380_003', "@JAND@"),
    # the W165 B-assert jump fragment (rides the @JB@ token; W166 target
    # 382_004 -- the r787/r793 heal lineage, leak class killed at source)
    ('own-wave A window reserved jumps to 379_804, first-clean ', "@JB@"),
    # assert composites
    ('== 377_804 == 377_803 + 1', "@ASB@"),
    ('== 379_804 == 379_803 + 1', "@BSB@"),
    ('set(range(377_804, 379_804))', "@ARITHA@"),
    ('set(range(379_804, 380_004))', "@ARB@"),
    # dotted band geometry
    ('377_604..379_603', "@NA@"),
    ('377_604..377_803', "@OB@"),
    ('377_804..379_803', "@AB@"),
    ('377_804..378_003', "@NB@"),
    ('379_804..380_003', "@BB@"),
    # base-relation composites
    ('377_803+1', "@ABASE@"),
    ('379_803+1', "@BBASE@"),
    # identity / stats / ordinals
    ('PERPETUAL_N1_W165_PREREG.md', "@PF@"),
    ('PERPETUAL-N1-W165', "@B@"),
    ('n1_w165_results.json', "@OD@"),
    ('n1_w165', "@SD@"),
    ('n1w165', "@SD2@"),
    ('766,212', "@LEDG@"),
    ('358,720', "@K1@"),
    ('ONE HUNDRED-AND-FIFTY-FIFTH', "@ORDW@"),
    ('engine_owner rows 154', "@R154@"),
    ('rows 80 + candidate', "@ROWS80@"),
    ('eightieth', "@SVN@"),
    ('twenty-fourth', "@ST24@"),
    # wave numbers (higher first: W166 projection -> W167; then W165->W166,
    # W164->W165)
    ('W166', "@WN2@"),
    ('W165', "@WN@"),
    ('W164', "@W@"),
    # bare round backstop (r776 fragment law: the physical W165 faces
    # break 'r793 pre-seat' + CRLF + '# push' across comment lines -- the
    # exact-phrase TOK above cannot match it; every other r793 face is
    # already carried by composite tokens, so the bare roll r793->r797
    # is safe; runs BEFORE the bare numerals)
    ('r793', "@RB@"),
    # bare numerals LAST (every longer carrier tokenized above; 165 before
    # 164 so the 164->165 output is never re-mapped)
    ('165', "@IDX@"),
    ('164', "@IDX2@"),
]
BACK = [
    ("@ASROW@", '"a_seed_base": 380_004,        # law sec.4 W166 A: 380_004..382_003 (FIRST-CLEAN past the registered W165 B band; arithmetic 379_804..381_803 REFUSED at own start by the W165 B band; hops=1; A-hops-prior-B staircase twenty-fifth instance, E36 card)'),
    ("@BSROW@", '"b_exit_seed_base": 382_004,   # law sec.4 W166 B: 382_004..382_203 (FIRST-CLEAN past the own-wave A window; arithmetic 380_004..380_203 lands inside own-A, same-freeze mutual exclusion W141 precedent; reserved walk hops=1; B base == own-A tail+1)'),
    ("@RROW@", '166: {"a": (380_004, 382_003), "b_exit": (382_004, 382_203),'),
    ("@RENTRY@", '166: {"batch"'),
    ("@PROW1@", "W165 row bm-a r795 freeze"),
    ("@PROW2@", "aebb94d2d, SINGLE STATE zero seat gap W2..W165 all"),
    ("@REGROW@", "bm-a r795 freeze aebb94d2d"),
    ("@FZH@", "bm-a r799 freeze"),
    ("@MFZH@", "r799 bm-a freeze"),
    ("@FW@", "W165 finalize landed same-window r796"),
    ("@FOPM2@", "finalize one-pass bm-a r796"),
    ("@FOP@", "W165 bm-a r796 one-pass"),
    ("@PRC@", "_r797bma_w166_probe_receipt.json"),
    ("@BGR@", "_r797bma_w166_band_gate.json"),
    ("@GATE@", "r793 gate leg3"),
    ("@GATEP@", "r793 gate"),
    ("@SEC8@", "r796 sec8 succession"),
    ("@SEC8M@", "r796 sec8"),
    ("@GDR@", "gate-derived r797"),
    ("@PSP@", "r797 pre-seat push"),
    ("@SEAT@", "MSG-2026-10-06-223x"),
    ("@SEATW@", "bma-w166-seat"),
    ("@MSGS@", "MSG-223x"),
    ("@SEATSHA@", "d1dc12117"),
    ("@PA@", "382_004..384_003"),
    ("@PB@", "382_204..382_403"),
    ("@JN@", "jumps to 382_004, first-clean 382_004..382_203 hops=1"),
    ("@JP@", "jumps to 382_004 -> 382_004..382_203,"),
    ("@JAND@", "382_004 and lands 382_004..382_203"),
    ("@JB@", "own-wave A window reserved jumps to 382_004, first-clean "),
    ("@ASB@", "== 380_004 == 380_003 + 1"),
    ("@BSB@", "== 382_004 == 382_003 + 1"),
    ("@ARITHA@", "set(range(380_004, 382_004))"),
    ("@ARB@", "set(range(382_004, 382_204))"),
    ("@NA@", "379_804..381_803"),
    ("@OB@", "379_804..380_003"),
    ("@AB@", "380_004..382_003"),
    ("@NB@", "380_004..380_203"),
    ("@BB@", "382_004..382_203"),
    ("@ABASE@", "380_003+1"),
    ("@BBASE@", "382_003+1"),
    ("@PF@", "PERPETUAL_N1_W166_PREREG.md"),
    ("@B@", "PERPETUAL-N1-W166"),
    ("@OD@", "n1_w166_results.json"),
    ("@SD@", "n1_w166"),
    ("@SD2@", "n1w166"),
    ("@LEDG@", "768,412"),
    ("@K1@", "360,920"),
    ("@ORDW@", "ONE HUNDRED-AND-FIFTY-SIXTH"),
    ("@R154@", "engine_owner rows 155"),
    ("@ROWS80@", "rows 81 + candidate"),
    ("@SVN@", "eighty-first"),
    ("@ST24@", "twenty-fifth"),
    ("@WN2@", "W167"),
    ("@WN@", "W166"),
    ("@W@", "W165"),
    ("@IDX@", "166"),
    ("@IDX2@", "165"),
    ("@RB@", "r797"),
]


def vmap(s: str) -> str:
    for a, b in TOK:
        s = s.replace(a, b)
    for a, b in BACK:
        s = s.replace(a, b)
    return s


# --- per-kind fragment-level fixups (r776 law: needles taken from the
# PHYSICAL probe-dumped shapes; applied AFTER vmap) ---------------------------
# W165 source faces are clean (r795 6-value honest-fix landed pre-freeze;
# payload prose already 3-item; no facts-helper residue): NO fixups needed
# this window -- FIXUPS empty, vmap_fix == vmap for all kinds.
FIXUPS = {}


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

# face-source zero-drift gate vs the r799 probe dumps
EO = '"engine_owner": "bm-a"},'
i1 = pfsrc.find("    # W165 (bm-a r795 freeze")
assert i1 > 0, "pf W165 comment block not found"
r1 = pfsrc.find('165: {"a": (377_804', i1)
assert r1 > i1, "pf W165 row not after comment block"
j1 = pfsrc.find(EO, r1) + len(EO)
block165_pf = pfsrc[i1:j1]
assert block165_pf == io.open(r"results\_r799bma_w166_probe_pf_block.txt",
                             encoding="utf-8", newline="").read(), "pf face drift vs probe"
assert block165_pf.count("engine_owner") == 1 and "f7d34e5a7" not in block165_pf
assert "379_804..381_803 CLEAN hops=0 / B first-clean 380_004..380_203" in block165_pf

# --- a1: pf.py W165 comment block + row -> append W166 comment block + row ----
a1 = block165_pf + CRLF + "}"
r1n = block165_pf + CRLF + vmap_fix(block165_pf, "pf") + CRLF + "}"

# --- a2: n1.py WAVE_CONFIGS entry ----------------------------------------------
k = n1src.find('165: {"batch"')
assert k > 0, "n1 W165 entry not found"
m = n1src.find(EO, k) + len(EO)
entry165 = n1src[k:m]
assert entry165 == io.open(r"results\_r799bma_w166_probe_n1_entry.txt",
                          encoding="utf-8", newline="").read(), "entry face drift vs probe"
a2 = entry165 + CRLF + "                       }"
r2 = entry165 + CRLF + "                       " + vmap_fix(entry165, "n1entry") + CRLF + "                       }"

# --- a3: materializer block (chain split-verbatim + one-row extension) --------
w = n1src.find("# --- W165 materializer face")
t2 = n1src.find("# --- T-141 s2 lane face", w)
assert 0 < w < t2, "materializer anchors missing"
block = n1src[w:t2]
assert block == io.open(r"results\_r799bma_w166_probe_n1_mat.txt",
                        encoding="utf-8", newline="").read(), "mat face drift vs probe"
ci = block.find("assert pf.N1_BANDS[138]")
cj = block.find("# prior-wave disjointness")
assert 0 < ci < cj, "chain boundaries missing"
pre, chain, post = block[:ci], block[ci:cj], block[cj:]
chain_rows = re.findall(r"assert pf\.N1_BANDS\[(\d+)\]", chain)
assert chain_rows == [str(x) for x in range(138, 165)], chain_rows
w165row = ('assert pf.N1_BANDS[165] == {"a": (377_804, 379_803),' + CRLF +
           '                                    "b_exit": (379_804, 380_003),' + CRLF +
           '                                    "engine_owner": "bm-a"}, \\' + CRLF +
           '            "registered W165 row parity drift (r307; bm-a r795)"' + CRLF +
           "        ")
# delivery/payload prose lives ONLY in the mat pre (header comment face);
# the post (disjointness/band-facts/assert face) passes through plain vmap
block166 = vmap_fix(pre, "mat") + chain + w165row + vmap(post)
a3 = block + "# --- T-141 s2 lane face"
r3 = block166 + "# --- T-141 s2 lane face"

# --- a4: PASS snippet claim insertion ------------------------------------------
cs = n1src.find('"+ W165 materializer face')
assert cs > 0, "W165 claim start not found"
ce = n1src.find('"r795 bm-a] "', cs) + len('"r795 bm-a] "')
assert 0 < cs < ce, "W165 claim end not found"
claim165 = n1src[cs:ce]
assert claim165 == io.open(r"results\_r799bma_w166_probe_n1_claim.txt",
                           encoding="utf-8", newline="").read(), "claim face drift vs probe"
a4 = '"r795 bm-a] "' + CRLF + '          "+ T-141 s2 "'
r4 = '"r795 bm-a] "' + CRLF + "          " + vmap_fix(claim165, "claim") + CRLF + '          "+ T-141 s2 "'

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
assert sorted(pf.N1_BANDS)[-1] == 166 and len(pf.N1_BANDS) == 164, \
    "pf N1_BANDS row-count drift after W166 insert"
assert pf.N1_BANDS[166] == {"a": (380_004, 382_003),
                            "b_exit": (382_004, 382_203),
                            "engine_owner": "bm-a"}, "W166 row face drift"
assert pf.N1_BANDS[165] == {"a": (377_804, 379_803),
                            "b_exit": (379_804, 380_003),
                            "engine_owner": "bm-a"}, "W165 row survived (r560 no-replace law)"
import perpetual_faces_n1 as n1mod
importlib.reload(n1mod)
assert n1mod.WAVE_CONFIGS[166]["a_seed_base"] == 380_004 and \
    n1mod.WAVE_CONFIGS[166]["b_exit_seed_base"] == 382_004, "W166 seed bases drift"
assert n1mod.WAVE_CONFIGS[166]["shard_subdir"] == "n1_w166" and \
    n1mod.WAVE_CONFIGS[166]["out_name"] == "n1_w166_results.json", "W166 path drift"
assert n1mod.WAVE_CONFIGS[166]["prereg"].startswith("research/PERPETUAL_N1_W166_PREREG.md"), \
    "W166 per-wave prereg citation drift"
assert os.path.exists(os.path.join("research", "PERPETUAL_N1_W166_PREREG.md")), \
    "W166 per-wave prereg missing on disk"

# materializer chain now 138..W165row (n=28)
n2 = io.open(N1, encoding="utf-8", newline="").read()
w2 = n2.find("# --- W166 materializer face")
t3 = n2.find("# --- T-141 s2 lane face", w2)
blk2 = n2[w2:t3]
chain_rows2 = re.findall(r"assert pf\.N1_BANDS\[(\d+)\]",
                         blk2[blk2.find("assert pf.N1_BANDS[138]"):
                              blk2.find("# prior-wave disjointness")])
assert chain_rows2 == [str(x) for x in range(138, 166)], chain_rows2

# r773 pit law leg 3: full-file start>end malformed-window scans on BOTH files
for path in (PF, N1):
    txt = io.open(path, encoding="utf-8", newline="").read()
    bad = [m.group() for m in re.finditer(r"(\d{3})_(\d{3})\.\.(\d{3})_(\d{3})", txt)
           if int(m.group(3)) < int(m.group(1))]
    assert not bad, f"malformed windows remain in {path}: {bad[:4]}"

# W167 projection prose present in the new W166 blocks (gate leg3 verbatim)
pf2 = io.open(PF, encoding="utf-8", newline="").read()
assert f"# {W167p_A} CLEAN hops=0 / B first-clean {W167p_B}" in pf2, "pf W167p prose missing"
assert "W167 A window; W167 freezer MUST re-derive on the post-W166" in pf2, \
    "pf W167 freezer prose missing"
# r776 fragment-needle law: the freezer prose in the n1 entry is split
# across python-string fragments -- a contiguous needle is a false-negative
# (r775/r781 law); assert the within-fragment shapes instead.
assert '"W167 A window; W167 freezer MUST re-derive on the "' in n2, "n1 W167 freezer fragment missing"
assert '"W166 B band 382_004..382_203 will refuse the naive "' in n2, "n1 W166-band refuse fragment missing"
assert f"A first-clean {W167p_A} " in n2 and f"B first-clean {W167p_B} CLEAN" in n2, \
    "n1 W167p prose missing"
# honesty faces landed (self-ack deferred + 3-item payload +
# direct-FF delivery + anti-drift registered-row citation)
assert "move deferred to the W167 finalize window" in pf2, "pf self-ack fixup missing"
assert "fleet/inbox at freeze time -- honest state);" in pf2, "pf self-ack tail fixup missing"
assert "move deferred to the W167 finalize window" in n2, "mat self-ack fixup missing"
assert "fleet/inbox at freeze time -- honest state)." in n2, "mat self-ack tail missing"
assert "payload = seat MSG + pre-seat probe + probe receipt;" in pf2, "pf 3-item payload fixup missing"
assert '"seat MSG + pre-seat probe + probe receipt; "' in n2, "entry 3-item payload fixup missing"
assert "= seat MSG + pre-seat probe + probe receipt;" in n2, "mat 3-item payload fixup missing"
assert "r797 pre-seat" in pf2 and "r797 pre-seat" in n2, "push session r797 face missing"
assert "direct fast-forward behind-0" in pf2 and "direct fast-forward behind-0" in n2, \
    "direct-FF delivery face missing"
# r776 fragment-needle law: the registered-row citation is split across
# python string fragments -- assert the within-fragment shapes
assert '"number law after the REGISTERED W165 row bm-a r795 freeze "' in n2, \
    "W165 row citation frag1 missing"
assert '"aebb94d2d, SINGLE STATE zero seat gap W2..W165 all "' in n2, \
    "W165 row citation frag2 missing"
assert '"finalize one-pass bm-a r796, net chain head 768,412, "' in n2, \
    "W165 finalize one-pass frag missing"
assert '"finalize one-pass bm-a r796, net chain head 768,412, "' in n2, \
    "W165 finalize one-pass frag missing"
# r781 fragment law: the contiguous logical string 'W165 finalize one-pass
# bm-a r796' physically splits across python string fragments -- count the
# within-fragment shapes instead (mat pre 1 + entry tail 1 == 2)
assert n2.count("finalize one-pass bm-a r796") == 2, "W165 finalize one-pass count drift"
assert "bm-a r795 freeze aebb94d2d" in n2, "mat header registered-row citation missing"
assert "f7d34e5a7" not in blk2, "stale W164 sha residue in new W166 block"
assert "finalize one-pass bm-a r799" not in n2, "stale r799 finalize residue"
# no stale round/seat/number leftovers in the NEW W166 blocks only (the
# frozen W165/W164 faces legitimately retain their historical citations;
# the mat CHAIN rows are verbatim prior-wave pinned constants (r307) --
# historical band values there are legitimate, so the mat scan covers
# only the freshly vmap'd pre (header) + post (band-facts) faces)
i2 = pf2.find("    # W166 (bm-a r799 freeze")
j2 = pf2.find(EO, i2) + len(EO)
newpfblk = pf2[i2:j2]
k2 = n2.find('166: {"batch"')
m2 = n2.find(EO, k2) + len(EO)
newentry = n2[k2:m2]
cs2 = n2.find('"+ W166 materializer face')
ce2 = n2.find('"r799 bm-a] "', cs2) + len('"r799 bm-a] "')
newclaim = n2[cs2:ce2]
ci2 = blk2.find("assert pf.N1_BANDS[138]")
cj2 = blk2.find("# prior-wave disjointness")
mat_new_faces = blk2[:ci2] + blk2[cj2:]
assert i2 > 0 and k2 > 0 and cs2 > 0, "new W166 block anchors missing"
for tag, seg in (("pf", newpfblk), ("entry", newentry),
                 ("mat", mat_new_faces), ("claim", newclaim)):
    for stale in ("r792 gate", "r793 sec8", "r793 pre-seat", "r792 bm-a freeze",
                  "bm-a r792 freeze", "MSG-2026-10-06-205x", "4bdf63090", "bma-w165-seat",
                  "MSG-205x", "merge-absorb", "377_604", "377_804", "377_803",
                  "378_003", "379_603", "379_803", "766,212", "358,720", "f7d34e5a7",
                  "678a07d4f", "6957f509e", "6ee1207bb", "ee04482a2",
                  "twenty-third", "twenty-fourth", "seventy-ninth", "eightieth",
                  "ONE HUNDRED-AND-FIFTY-FIFTH", "engine_owner rows 154",
                  "rows 80 + candidate", "n1w165", "n1_w165",
                  "PERPETUAL-N1-W165", "PERPETUAL_N1_W165",
                  "gate-derived r793"):
        assert stale not in seg, f"stale {stale!r} residue in new W166 {tag} block"
        # 379_804/380_003/380_203/381_803 are NOT in the stale set: they
        # legitimately appear in the new W166 blocks as the naive-A/B
        # starts-ends and the W165 B band start (r787 371_004-precedent
        # note; r793 379_804-precedent note)
# corrupted historical faces must remain eradicated from both files
for path in (PF, N1):
    txt = io.open(path, encoding="utf-8", newline="").read()
    assert "362_204..362_003" not in txt and "362_404..360_403" not in txt, \
        f"r772 malformed-window residue in {path}"
# the W166 B-assert prose cites the W166 jump target 382_004 via the @JB@
# token (the r787/r793 heal lineage: SINGLE-LIVE materializer face
# migrates to the newest wave each freeze; git history carries the record)
assert "own-wave A window reserved jumps to 382_004, first-clean " in blk2, \
    "W166 healed-fragment face missing"
assert "own-wave A window reserved jumps to 379_804, first-clean" not in blk2, \
    "vmap-leak residue in new block"

print("post-edit structural assertions PASS: N1_BANDS 164 rows tail W166, "
      "W165 row intact, WAVE_CONFIGS[166] seeded, chain 138..165 n=28, "
      "W167p prose == r797 gate leg3 verbatim, honesty faces landed "
      "(self-ack deferred / 3-item payload / direct-FF delivery / "
      "anti-drift registered-row cite), full-file malformed-window scans "
      "CLEAN on both files, no same-window heal needed this window")
