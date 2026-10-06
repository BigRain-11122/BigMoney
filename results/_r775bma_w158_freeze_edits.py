# -*- coding: utf-8 -*-
"""r775 bm-a W158 freeze edits: four insertions (pf N1_BANDS[158] row +
n1 WAVE_CONFIGS[158] entry + n1 W158 materializer block refresh +
n1 PASS snippet claim insertion), SAME-WINDOW after the pf.py W157-block
prose heal (_r775bma_w157_pf_prose_heal.py, r774 closeout directive).

Bloodline: r772 _r772bma_w157_freeze_edits.py machinery, W158 facts
live-registry-driven (band gate results/_r773bma_w158_band_gate.json
rc0 ADMIT; pre-seat probe _r773bma_w158_probe_receipt.json; seat
24aff72f5 on origin; W158 prereg research/PERPETUAL_N1_W158_PREREG.md
landed r773; W157 finalize r773 one-pass, ledger head 741,411,
K=343,320 merged pool).

r773 pit law compliance (frozen-editor vmap partial-tokenization
malformed-window face):
  (1) full string-face inventory empirically probed BEFORE writing TOK
      (probe4/5/6/7 + anchor1/2/3: entry/pre/post/chain/claim/pf-block
      full dumps + needle counts, results/_r775bma_w158_* files);
  (2) composite band strings tokenized WHOLE (no bare-seed-prefix
      tokens anywhere -- @JN@/@JFT@/@JP@/@JAND@/@ASROW@/@BSROW@ carry
      their bands inside whole-string tokens; bare 157/156 run LAST
      only after every longer carrier is already tokenized);
  (3) post-edit full-file start>end malformed-window regex scan on
      BOTH touched files (r773 entry-integrity probe extension);
  (4) every projection value re-derived FROM the on-disk gate receipts
      (r587 never-transcribe law; W159p targets from
      _r773bma_w158_band_gate.json leg3 machine values).

EOL-adaptive (r370 law: CRLF-dominant blocks written CRLF);
needle count==1 (r745); insert-after-last-registered-row (r560);
anchor = predecessor full lines (r580/r581); AST gate after every
edit batch (r580/r581)."""
import ast
import io
import json
import re
import os

PF = r"scripts/perpetual_faces.py"
N1 = r"scripts/perpetual_faces_n1.py"
CRLF = "\r\n"

# --- machine-derived facts (r587: read from on-disk receipts) ----------------
gate158 = json.load(open("results/_r773bma_w158_band_gate.json", encoding="utf-8"))
leg1, leg3 = gate158["legs"]["leg1"], gate158["legs"]["leg3"]
assert gate158["verdict"] == "ADMIT", gate158["verdict"]
assert leg1["A"] == [362404, 364403] and leg1["B"] == [364404, 364603], leg1
assert leg1["hops_A"] == 1 and leg1["hops_B"] == 1
assert leg1["ARITH_A"] == [362204, 364203], leg1["ARITH_A"]
assert leg1["B_naive_first_clean"] == [362404, 362603], leg1["B_naive_first_clean"]


def u(s):  # "364404..366403" -> "364_404..366_403"
    def g(part):
        return re.sub(r"(\d)(?=(\d{3})+$)", r"\1_", part)
    a, b = s.split("..")
    return f"{g(a)}..{g(b)}"


W159p_A = u(leg3["W159p_A"])
W159p_B = u(leg3["W159p_B"])
assert W159p_A == "364_404..366_403" and W159p_B == "364_604..364_803", (W159p_A, W159p_B)
assert leg3["W159p_B_lands_inside_W159p_A"] is True

# --- ordered value-map (tokens first, then back-substitution) ---------------
TOK = [
    # whole-line / long-fragment tokens (longest first; bands carried WHOLE
    # inside these tokens -- r773 pit law: no bare-seed-prefix tearing)
    ('"a_seed_base": 360_204,        # law sec.4 W157 A: 360_204..362_203 (FIRST-CLEAN past the registered W156 B band; arithmetic 360_004..362_003 REFUSED at own start by the W156 B band; hops=1; A-hops-prior-B staircase sixteenth instance, E36 card)', "@ASROW@"),
    ('"b_exit_seed_base": 362_204,   # law sec.4 W157 B: 362_204..362_403 (FIRST-CLEAN past the own-wave A window; arithmetic 360_204..360_403 lands inside own-A, same-freeze mutual exclusion W141 precedent; reserved walk hops=1; B base == own-A tail+1)', "@BSROW@"),
    ('157: {"a": (360_204, 362_203), "b_exit": (362_204, 362_403),', "@RROW@"),
    ("jumps to 362_204, first-clean 362_204..362_403 hops=1", "@JN@"),
    ("jumps to 362_204, first-clean", "@JFT@"),
    ("jumps to 362_204 -> 362_204..362_403,", "@JP@"),
    ("362_204 and lands", "@JAND@"),
    ("== 360_204 == 360_203 + 1", "@ASB@"),
    ("== 362_204 == 362_203 + 1", "@BSB@"),
    ("set(range(360_204, 362_204))", "@ARITHA@"),
    ("set(range(362_204, 362_404))", "@ARB@"),
    # dotted band geometry
    ("360_004..360_203", "@PB@"),
    ("360_004..362_003", "@NA@"),
    ("360_204..362_203", "@AB@"),
    ("360_204..360_403", "@NB@"),
    ("362_204..362_403", "@OB@"),
    ("360_203+1", "@ABASE@"),
    ("362_203+1", "@BBASE@"),
    # identity / stats / ordinals
    ("PERPETUAL_N1_W157_PREREG.md", "@PF@"),
    ("PERPETUAL-N1-W157", "@B@"),
    ("n1_w157_results.json", "@OD@"),
    ("n1_w157", "@SD@"),
    ("_r772bma", "@RD@"),
    ("MSG-2026-10-06-113x", "@SEAT@"),
    ("4af40c72d", "@SEATSHA@"),
    ("13c989ba0", "@PSHA@"),
    ("MSG-1009", "@MSGS@"),
    ("739,211", "@LEDG@"),
    ("341,120", "@K1@"),
    ("ONE HUNDRED-AND-FORTY-SEVENTH", "@ORDW@"),
    ("engine_owner rows 146", "@R145@"),
    ("rows 72 + candidate", "@OWN72@"),
    ("seventy-third", "@OWN73@"),
    ("sixteenth", "@F16@"),
    ("r772", "@RW@"),
    ("r771", "@PRW@"),
    ("W157", "@W@"),
    ("W156", "@WP@"),
    # bare numerals LAST (every longer carrier tokenized above)
    ("157", "@IDX@"),
    ("156", "@IDX2@"),
]
BACK = [
    ("@ASROW@", '"a_seed_base": 362_404,        # law sec.4 W158 A: 362_404..364_403 (FIRST-CLEAN past the registered W157 B band; arithmetic 362_204..364_203 REFUSED at own start by the W157 B band; hops=1; A-hops-prior-B staircase seventeenth instance, E36 card)'),
    ("@BSROW@", '"b_exit_seed_base": 364_404,   # law sec.4 W158 B: 364_404..364_603 (FIRST-CLEAN past the own-wave A window; arithmetic 362_404..362_603 lands inside own-A, same-freeze mutual exclusion W141 precedent; reserved walk hops=1; B base == own-A tail+1)'),
    ("@RROW@", '158: {"a": (362_404, 364_403), "b_exit": (364_404, 364_603),'),
    ("@JN@", "jumps to 364_404, first-clean 364_404..364_603 hops=1"),
    ("@JFT@", "jumps to 364_404, first-clean"),
    ("@JP@", "jumps to 364_404 -> 364_404..364_603,"),
    ("@JAND@", "364_404 and lands"),
    ("@ASB@", "== 362_404 == 362_403 + 1"),
    ("@BSB@", "== 364_404 == 364_403 + 1"),
    ("@ARITHA@", "set(range(362_404, 364_404))"),
    ("@ARB@", "set(range(364_404, 364_604))"),
    ("@PB@", "362_204..362_403"),
    ("@NA@", "362_204..364_203"),
    ("@AB@", "362_404..364_403"),
    ("@NB@", "362_404..362_603"),
    ("@OB@", "364_404..364_603"),
    ("@ABASE@", "362_403+1"),
    ("@BBASE@", "364_403+1"),
    ("@PF@", "PERPETUAL_N1_W158_PREREG.md"),
    ("@B@", "PERPETUAL-N1-W158"),
    ("@OD@", "n1_w158_results.json"),
    ("@SD@", "n1_w158"),
    ("@RD@", "_r773bma"),
    ("@SEAT@", "MSG-2026-10-06-120x"),
    ("@SEATSHA@", "24aff72f5"),
    ("@PSHA@", "aed41df3e"),
    ("@MSGS@", "MSG-120x"),
    ("@LEDG@", "741,411"),
    ("@K1@", "343,320"),
    ("@ORDW@", "ONE HUNDRED-AND-FORTY-EIGHTH"),
    ("@R145@", "engine_owner rows 147"),
    ("@OWN72@", "rows 73 + candidate"),
    ("@OWN73@", "seventy-fourth"),
    ("@F16@", "seventeenth"),
    ("@RW@", "r773"),
    ("@PRW@", "r772"),
    ("@W@", "W158"),
    ("@WP@", "W157"),
    ("@IDX@", "158"),
    ("@IDX2@", "157"),
]


def vmap(s: str) -> str:
    for a, b in TOK:
        s = s.replace(a, b)
    for a, b in BACK:
        s = s.replace(a, b)
    return s


def vmap_fix(s: str, kind: str) -> str:
    """vmap + W159-projection semantic fixups (wave-number honesty for the
    NEXT freezer reader; values machine-derived from the r773 gate leg3).
    Only the pf block and the n1 entry carry projection prose; pre/post/
    claim fragments pass through plain vmap() (no projection fixups)."""
    s = vmap(s)
    if kind == "pf":
        old1 = "362_204..364_203 CLEAN hops=0 / B first-clean 362_404..362_603"
        new1 = f"{W159p_A} CLEAN hops=0 / B first-clean {W159p_B}"
        old2 = "W158 A window; W158 freezer MUST re-derive on the post-W158"
        new2 = "W159 A window; W159 freezer MUST re-derive on the post-W158"
    elif kind == "n1entry":
        old1 = "A first-clean 362_204..364_203 "
        new1 = f"A first-clean {W159p_A} "
        old2 = "B first-clean 362_404..362_603 CLEAN"
        new2 = f"B first-clean {W159p_B} CLEAN"
        # fragment-broken freezer line: 'refuse the naive' ends the previous
        # python string fragment; the wave-number fix targets this fragment
        old3 = "W158 A window; W158 freezer"
        new3 = "W159 A window; W159 freezer"
        assert s.count(old3) == 1, ("n1 proj freezer fix", s.count(old3))
        s = s.replace(old3, new3)
    else:
        return s
    assert s.count(old1) == 1, (kind, "proj A", s.count(old1))
    assert s.count(old2) == 1, (kind, "proj B", s.count(old2))
    return s.replace(old1, new1).replace(old2, new2)


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

# --- a1: pf.py W157 comment block + row -> append W158 comment block + row --
i1 = pfsrc.find("    # W157 (bm-a r772 freeze")
assert i1 > 0, "pf W157 comment block not found"
r157 = pfsrc.find('157: {"a": (360_204, 362_203)', i1)
assert r157 > i1, "pf W157 row not after comment block"
j1 = pfsrc.find('"engine_owner": "bm-a"},', r157) + len('"engine_owner": "bm-a"},')
block157_pf = pfsrc[i1:j1]
assert block157_pf.count("engine_owner") == 1 and "aed41df3e" not in block157_pf
assert "362_204..364_203 CLEAN hops=0" in block157_pf, "healed proj face missing"
a1 = block157_pf + CRLF + "}"
r1 = block157_pf + CRLF + vmap_fix(block157_pf, "pf") + CRLF + "}"

# --- a2: n1.py WAVE_CONFIGS entry ----------------------------------------------
k = n1src.find('157: {"batch"')
assert k > 0, "n1 W157 entry not found"
m = n1src.find('"engine_owner": "bm-a"},', k) + len('"engine_owner": "bm-a"},')
entry157 = n1src[k:m]
a2 = entry157 + CRLF + "                       }"
r2 = entry157 + CRLF + "                       " + vmap_fix(entry157, "n1entry") + CRLF + "                       }"

# --- a3: materializer block (chain split-verbatim + one-row extension) --------
w = n1src.find("# --- W157 materializer face")
t2 = n1src.find("# --- T-141 s2 lane face", w)
assert 0 < w < t2, "materializer anchors missing"
block = n1src[w:t2]
ci = block.find("assert pf.N1_BANDS[138]")
cj = block.find("# prior-wave disjointness")
assert 0 < ci < cj, "chain boundaries missing"
pre, chain, post = block[:ci], block[ci:cj], block[cj:]
chain_rows = re.findall(r"assert pf\.N1_BANDS\[(\d+)\]", chain)
assert chain_rows == [str(x) for x in range(138, 157)], chain_rows
w157row = ('assert pf.N1_BANDS[157] == {"a": (360_204, 362_203),' + CRLF +
           '                                    "b_exit": (362_204, 362_403),' + CRLF +
           '                                    "engine_owner": "bm-a"}, \\' + CRLF +
           '            "registered W157 row parity drift (r307; bm-a r772)"' + CRLF +
           "        ")
block158 = vmap(pre) + chain + w157row + vmap(post)
a3 = block + "# --- T-141 s2 lane face"
r3 = block158 + "# --- T-141 s2 lane face"

# --- a4: PASS snippet claim insertion ------------------------------------------
cs = n1src.find('"+ W157 materializer face')
assert cs > 0, "W157 claim start not found"
ce = n1src.find('"r772 bm-a] "', cs) + len('"r772 bm-a] "')
claim157 = n1src[cs:ce]
a4 = '"r772 bm-a] "' + CRLF + '          "+ T-141 s2 "'
r4 = '"r772 bm-a] "' + CRLF + "          " + vmap(claim157) + CRLF + '          "+ T-141 s2 "'

# --- apply the four edits -------------------------------------------------------
edit(PF, [(a1, r1)])
edit(N1, [(a2, r2), (a3, r3), (a4, r4)])

# --- post-edit structural assertions --------------------------------------------
import sys
sys.path.insert(0, ".")
sys.path.insert(0, "scripts")
import importlib
import perpetual_faces as pf
importlib.reload(pf)
assert sorted(pf.N1_BANDS)[-1] == 158 and len(pf.N1_BANDS) == 156, \
    "pf N1_BANDS row-count drift after W158 insert"
assert pf.N1_BANDS[158] == {"a": (362_404, 364_403),
                            "b_exit": (364_404, 364_603),
                            "engine_owner": "bm-a"}, "W158 row face drift"
assert pf.N1_BANDS[157] == {"a": (360_204, 362_203),
                            "b_exit": (362_204, 362_403),
                            "engine_owner": "bm-a"}, "W157 row survived (r560 no-replace law)"
import perpetual_faces_n1 as n1mod
importlib.reload(n1mod)
assert n1mod.WAVE_CONFIGS[158]["a_seed_base"] == 362_404 and \
    n1mod.WAVE_CONFIGS[158]["b_exit_seed_base"] == 364_404, "W158 seed bases drift"
assert n1mod.WAVE_CONFIGS[158]["shard_subdir"] == "n1_w158" and \
    n1mod.WAVE_CONFIGS[158]["out_name"] == "n1_w158_results.json", "W158 path drift"
assert n1mod.WAVE_CONFIGS[158]["prereg"].startswith("research/PERPETUAL_N1_W158_PREREG.md"), \
    "W158 per-wave prereg citation drift"
assert os.path.exists(os.path.join("research", "PERPETUAL_N1_W158_PREREG.md")), \
    "W158 per-wave prereg missing on disk"

# materializer chain now 138..W157row (n=20)
n2 = io.open(N1, encoding="utf-8", newline="").read()
w2 = n2.find("# --- W158 materializer face")
t3 = n2.find("# --- T-141 s2 lane face", w2)
blk2 = n2[w2:t3]
chain_rows2 = re.findall(r"assert pf\.N1_BANDS\[(\d+)\]",
                         blk2[blk2.find("assert pf.N1_BANDS[138]"):
                              blk2.find("# prior-wave disjointness")])
assert chain_rows2 == [str(x) for x in range(138, 158)], chain_rows2

# r773 pit law leg 3: full-file start>end malformed-window scans on BOTH files
for path in (PF, N1):
    txt = io.open(path, encoding="utf-8", newline="").read()
    bad = [m.group() for m in re.finditer(r"(\d{3})_(\d{3})\.\.(\d{3})_(\d{3})", txt)
           if int(m.group(3)) < int(m.group(1))]
    assert not bad, f"malformed windows remain in {path}: {bad[:4]}"

# W159 projection prose present in the new W158 blocks (gate leg3 verbatim)
assert f"A first-clean\n    # {W159p_A} CLEAN hops=0 / B first-clean {W159p_B}" in n2 or \
    f"{W159p_A} CLEAN hops=0 / B first-clean {W159p_B}" in n2, "pf/entry W159p prose missing"
pf2 = io.open(PF, encoding="utf-8", newline="").read()
assert f"# {W159p_A} CLEAN hops=0 / B first-clean {W159p_B}" in pf2, "pf W159p prose missing"
assert "W159 A window; W159 freezer MUST re-derive on the post-W158" in pf2, \
    "pf W159 freezer prose missing"
assert "refuse the naive W159 A window; W159 freezer" in n2, "n1 W159 freezer prose missing"
# corrupted r772 faces must remain eradicated from both files
for path in (PF, N1):
    txt = io.open(path, encoding="utf-8", newline="").read()
    assert "362_204..362_003" not in txt and "362_404..360_403" not in txt, \
        f"r772 malformed-window residue in {path}"

print("post-edit structural assertions PASS: N1_BANDS 156 rows tail W158, "
      "W157 row intact, WAVE_CONFIGS[158] seeded, chain 138..157 n=20, "
      "W159p prose == r773 gate leg3 verbatim, full-file malformed-window "
      "scans CLEAN on both files")
