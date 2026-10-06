# -*- coding: utf-8 -*-
"""r781 bm-a W159 freeze edits: four insertions (pf N1_BANDS[159] row +
n1 WAVE_CONFIGS[159] entry + n1 W159 materializer block refresh +
n1 PASS snippet claim insertion).

Bloodline: r775 _r775bma_w158_freeze_edits.py machinery (r773 pit law
freeze-editor compliance + r776 fragment-needle law), W159 facts
live-registry-driven:
  - band gate results/_r779bma_w159_band_gate.json rc0 ADMIT
    (A 364_604..366_603 staircase EIGHTEENTH instance E36 hops=1 past the
    W158 B band; naive 364_404..366_403 refused at its own start by the
    registered W158 B band 364_404..364_603; B 366_604..366_803 own-A
    mutual exclusion hops=1, naive 364_604..364_803);
  - pre-seat probe results/_r779bma_w159_probe_receipt.json ADMIT,
    dual-window parity True (leg1 parity_with_probe);
  - seat MSG-2026-10-06-142x-bma-w159-seat published 7b60d09da
    (r779 pre-seat push via merge-absorb window, parents bf059816d +
    c12271292, zero --no-verify; r565 published=reserved law: on origin
    BEFORE this freeze commit);
  - per-wave prereg research/PERPETUAL_N1_W159_PREREG.md (r779 session
    xform, preserved by the r780 recovery commit 94eca751b -- landed in
    the freeze window per the r511 tail-lock, pre-run zero results);
  - W158 finalize one-pass r778: ledger head 753,012, merged pool
    K=345,520 (prereg-anchored, no fork face);
  - W158 freeze r775 sha 6957f509e (the REGISTERED W158 row citation);
  - W160+ projection (gate leg3 verbatim): A first-clean 366_604..368_603
    / B first-clean 366_804..367_003, naive-B-inside-naive-A, the
    registered W159 B band will refuse the naive W160 A window.

r773 pit law compliance:
  (1) full string-face inventory empirically probed BEFORE TOK
      (_r781bma_w159_probe.py -- four face dumps + needle-count receipt
      _r781bma_w159_probe_receipt.json; byte-identical to the r779
      session dumps -- zero drift, _r781bma_w159_settle.py);
  (2) composite band strings tokenized WHOLE (no bare-seed-prefix
      tokens; every dotted band / seed-base row / jump phrase / round-sha
      composite is a single token; bare 158/157 run LAST);
  (3) post-edit full-file start>end malformed-window regex scan on BOTH
      touched files;
  (4) every projection value re-derived FROM the on-disk gate receipts
      (r587 never-transcribe law);
  (5) r776 fragment-needle law: all vmap_fix needles taken from the
      PHYSICAL probe-dumped shapes (python-string fragments / comment
      lines, CRLF-exact);
  (6) honesty fixups: W159 seat delivery = merge-absorb window (NOT the
      W157/W158 direct fast-forward), self-ack move = landed (bm-c r625
      read-only-observer processed, e203e96c7).

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
gate = json.load(open("results/_r779bma_w159_band_gate.json", encoding="utf-8"))
leg1, leg3 = gate["legs"]["leg1"], gate["legs"]["leg3"]
assert gate["verdict"] == "ADMIT", gate["verdict"]
assert leg1["A"] == [364604, 366603] and leg1["B"] == [366604, 366803], leg1
assert leg1["hops_A"] == 1 and leg1["hops_B"] == 1
assert leg1["ARITH_A"] == [364404, 366403], leg1["ARITH_A"]
assert leg1["B_naive_first_clean"] == [364604, 364803], leg1["B_naive_first_clean"]
assert leg1["parity_with_probe"] is True
probe = json.load(open("results/_r779bma_w159_probe_receipt.json", encoding="utf-8"))
assert probe["verdict"] == "ADMIT" and probe["bands"] == {"A": "364604_366603", "B": "366604_366803"}, probe


def u(s):  # "366604..368603" -> "366_604..368_603"
    def g(part):
        return re.sub(r"(\d)(?=(\d{3})+$)", r"\1_", part)
    a, b = s.split("..")
    return f"{g(a)}..{g(b)}"


W160p_A = u(leg3["W160p_A"])
W160p_B = u(leg3["W160p_B"])
assert W160p_A == "366_604..368_603" and W160p_B == "366_804..367_003", (W160p_A, W160p_B)
assert leg3["W160p_B_lands_inside_W160p_A"] is True

# --- ordered value-map (tokens first, then back-substitution) ---------------
TOK = [
    # whole-line / long-fragment tokens (longest first; bands carried WHOLE
    # inside these tokens -- r773 pit law: no bare-seed-prefix tearing)
    ('"a_seed_base": 362_404,        # law sec.4 W158 A: 362_404..364_403 (FIRST-CLEAN past the registered W157 B band; arithmetic 362_204..364_203 REFUSED at own start by the W157 B band; hops=1; A-hops-prior-B staircase seventeenth instance, E36 card)', "@ASROW@"),
    ('"b_exit_seed_base": 364_404,   # law sec.4 W158 B: 364_404..364_603 (FIRST-CLEAN past the own-wave A window; arithmetic 362_404..362_603 lands inside own-A, same-freeze mutual exclusion W141 precedent; reserved walk hops=1; B base == own-A tail+1)', "@BSROW@"),
    ('158: {"a": (362_404, 364_403), "b_exit": (364_404, 364_603),', "@RROW@"),
    # round+sha composites (must precede the bare round/wave tokens)
    ("bm-a r772 freeze aed41df3e", "@FZ@"),
    ("W157 finalize landed same-window r773", "@FW@"),
    ("W157 finalize one-pass bm-a r773", "@FOP@"),
    ("W157 bm-a r773 one-pass", "@COP@"),
    # jump phrases (longest first; fragment-broken variant last)
    ("jumps to 364_404, first-clean 364_404..364_603 hops=1", "@JN@"),
    ("jumps to 364_404 -> 364_404..364_603,", "@JP@"),
    ("364_404 and lands", "@JAND@"),
    ("jumps to 364_404, first-clean", "@JFT@"),
    # assert composites
    ("== 362_404 == 362_403 + 1", "@ASB@"),
    ("== 364_404 == 364_403 + 1", "@BSB@"),
    ("set(range(362_404, 364_404))", "@ARITHA@"),
    ("set(range(364_404, 364_604))", "@ARB@"),
    # dotted band geometry
    ("362_204..362_403", "@PB@"),
    ("362_204..364_203", "@NA@"),
    ("362_404..364_403", "@AB@"),
    ("362_404..362_603", "@NB@"),
    ("364_404..364_603", "@OB@"),
    ("362_403+1", "@ABASE@"),
    ("364_403+1", "@BBASE@"),
    # identity / stats / ordinals
    ("PERPETUAL_N1_W158_PREREG.md", "@PF@"),
    ("PERPETUAL-N1-W158", "@B@"),
    ("n1_w158_results.json", "@OD@"),
    ("n1_w158", "@SD@"),
    ("_r773bma", "@RD@"),
    ("MSG-2026-10-06-120x", "@SEAT@"),
    ("24aff72f5", "@SEATSHA@"),
    ("MSG-120x", "@MSGS@"),
    ("741,411", "@LEDG@"),
    ("343,320", "@K1@"),
    ("ONE HUNDRED-AND-FORTY-EIGHTH", "@ORDW@"),
    ("engine_owner rows 147", "@R145@"),
    ("rows 73 + candidate", "@OWN72@"),
    ("seventy-fourth", "@OWN73@"),
    ("seventeenth", "@F16@"),
    ("r773", "@RW@"),
    ("r772", "@PRW@"),
    ("W158", "@W@"),
    ("W157", "@WP@"),
    # bare numerals LAST (every longer carrier tokenized above)
    ("158", "@IDX@"),
    ("157", "@IDX2@"),
]
BACK = [
    ("@ASROW@", '"a_seed_base": 364_604,        # law sec.4 W159 A: 364_604..366_603 (FIRST-CLEAN past the registered W158 B band; arithmetic 364_404..366_403 REFUSED at own start by the W158 B band; hops=1; A-hops-prior-B staircase eighteenth instance, E36 card)'),
    ("@BSROW@", '"b_exit_seed_base": 366_604,   # law sec.4 W159 B: 366_604..366_803 (FIRST-CLEAN past the own-wave A window; arithmetic 364_604..364_803 lands inside own-A, same-freeze mutual exclusion W141 precedent; reserved walk hops=1; B base == own-A tail+1)'),
    ("@RROW@", '159: {"a": (364_604, 366_603), "b_exit": (366_604, 366_803),'),
    ("@FZ@", "bm-a r775 freeze 6957f509e"),
    ("@FW@", "W158 finalize landed same-window r778"),
    ("@FOP@", "W158 finalize one-pass bm-a r778"),
    ("@COP@", "W158 bm-a r778 one-pass"),
    ("@JN@", "jumps to 366_604, first-clean 366_604..366_803 hops=1"),
    ("@JP@", "jumps to 366_604 -> 366_604..366_803,"),
    ("@JAND@", "366_604 and lands"),
    ("@JFT@", "jumps to 366_604, first-clean"),
    ("@ASB@", "== 364_604 == 364_603 + 1"),
    ("@BSB@", "== 366_604 == 366_603 + 1"),
    ("@ARITHA@", "set(range(364_604, 366_604))"),
    ("@ARB@", "set(range(366_604, 366_804))"),
    ("@PB@", "364_404..364_603"),
    ("@NA@", "364_404..366_403"),
    ("@AB@", "364_604..366_603"),
    ("@NB@", "364_604..364_803"),
    ("@OB@", "366_604..366_803"),
    ("@ABASE@", "364_603+1"),
    ("@BBASE@", "366_603+1"),
    ("@PF@", "PERPETUAL_N1_W159_PREREG.md"),
    ("@B@", "PERPETUAL-N1-W159"),
    ("@OD@", "n1_w159_results.json"),
    ("@SD@", "n1_w159"),
    ("@RD@", "_r779bma"),
    ("@SEAT@", "MSG-2026-10-06-142x"),
    ("@SEATSHA@", "7b60d09da"),
    ("@MSGS@", "MSG-142x"),
    ("@LEDG@", "753,012"),
    ("@K1@", "345,520"),
    ("@ORDW@", "ONE HUNDRED-AND-FORTY-NINTH"),
    ("@R145@", "engine_owner rows 148"),
    ("@OWN72@", "rows 74 + candidate"),
    ("@OWN73@", "seventy-fifth"),
    ("@F16@", "eighteenth"),
    ("@RW@", "r779"),
    ("@PRW@", "r773"),
    ("@W@", "W159"),
    ("@WP@", "W158"),
    ("@IDX@", "159"),
    ("@IDX2@", "158"),
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
        # W160+ projection bands (gate leg3 verbatim; single comment line)
        ("364_404..366_403 CLEAN hops=0 / B first-clean 364_604..364_803",
         f"{W160p_A} CLEAN hops=0 / B first-clean {W160p_B}"),
        # freezer wave-numbers (post-vmap uniform line)
        ("W159 A window; W159 freezer MUST re-derive on the post-W159",
         "W160 A window; W160 freezer MUST re-derive on the post-W159"),
        # delivery-window honesty: W159 seat went via merge-absorb (7b60d09da
        # merge commit, parents bf059816d + c12271292), zero --no-verify;
        # self-ack move landed (bm-c r625 read-only-observer processed)
        ("= direct fast-forward behind-0 at fetch (r779 pre-seat" + CRLF +
         "    # push), zero merge, zero --no-verify; self-ack inbox->processed" + CRLF +
         "    # move deferred to the W159 finalize window;",
         "= merge-absorb behind-delivery at fetch (r779 pre-seat" + CRLF +
         "    # push via merge-absorb window), zero --no-verify; self-ack inbox->processed" + CRLF +
         "    # move landed (bm-c r625 read-only-observer processed, e203e96c7);"),
    ],
    "n1entry": [
        # W160+ projection values (gate leg3 verbatim; physical fragments)
        ("A first-clean 364_404..366_403 ", f"A first-clean {W160p_A} "),
        ("B first-clean 364_604..364_803 CLEAN", f"B first-clean {W160p_B} CLEAN"),
        # fragment-broken freezer line: 'refuse the naive' ends the previous
        # python string fragment; the wave-number fix targets this fragment
        ("W159 A window; W159 freezer", "W160 A window; W160 freezer"),
        # delivery-window honesty (two physical fragments)
        ("delivery window = direct fast-forward ",
         "delivery window = merge-absorb behind-delivery "),
        ("behind-0 at fetch (r779 pre-seat push), zero merge, zero ",
         "at fetch (r779 pre-seat push via merge-absorb window), zero "),
    ],
    "mat": [
        # delivery-window + self-ack honesty (comment face, 4-space-extra
        # indent; the ONE HUNDRED-AND-FORTY-NINTH tail line is untouched
        # past the needle end)
        ("direct fast-forward" + CRLF +
         "    #     behind-0 at fetch (r779 pre-seat push), zero merge, zero" + CRLF +
         "    #     --no-verify; self-ack inbox->processed move deferred to" + CRLF +
         "    #     the W159 finalize window).",
         "merge-absorb" + CRLF +
         "    #     behind-delivery at fetch (r779 pre-seat push via merge-absorb" + CRLF +
         "    #     window), zero --no-verify; self-ack inbox->processed move landed" + CRLF +
         "    #     (bm-c r625 read-only-observer processed, e203e96c7)."),
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

# face-source zero-drift gate vs the r781 probe dumps (and those are
# byte-identical to the r779 session dumps -- _r781bma_w159_settle.py)
EO = '"engine_owner": "bm-a"},'
i1 = pfsrc.find("    # W158 (bm-a r773 freeze")
assert i1 > 0, "pf W158 comment block not found"
r1 = pfsrc.find('158: {"a": (362_404, 364_403)', i1)
assert r1 > i1, "pf W158 row not after comment block"
j1 = pfsrc.find(EO, r1) + len(EO)
block158_pf = pfsrc[i1:j1]
assert block158_pf == io.open(r"results\_r781bma_w159_probe_pf_block.txt",
                              encoding="utf-8", newline="").read(), "pf face drift vs probe"
assert block158_pf.count("engine_owner") == 1 and "6957f509e" not in block158_pf
assert "364_404..366_403 CLEAN hops=0 / B first-clean 364_604..364_803" in block158_pf

# --- a1: pf.py W158 comment block + row -> append W159 comment block + row --
a1 = block158_pf + CRLF + "}"
r1n = block158_pf + CRLF + vmap_fix(block158_pf, "pf") + CRLF + "}"

# --- a2: n1.py WAVE_CONFIGS entry ----------------------------------------------
k = n1src.find('158: {"batch"')
assert k > 0, "n1 W158 entry not found"
m = n1src.find(EO, k) + len(EO)
entry158 = n1src[k:m]
assert entry158 == io.open(r"results\_r781bma_w159_probe_n1_entry.txt",
                           encoding="utf-8", newline="").read(), "entry face drift vs probe"
a2 = entry158 + CRLF + "                       }"
r2 = entry158 + CRLF + "                       " + vmap_fix(entry158, "n1entry") + CRLF + "                       }"

# --- a3: materializer block (chain split-verbatim + one-row extension) --------
w = n1src.find("# --- W158 materializer face")
t2 = n1src.find("# --- T-141 s2 lane face", w)
assert 0 < w < t2, "materializer anchors missing"
block = n1src[w:t2]
assert block == io.open(r"results\_r781bma_w159_probe_n1_mat.txt",
                        encoding="utf-8", newline="").read(), "mat face drift vs probe"
ci = block.find("assert pf.N1_BANDS[138]")
cj = block.find("# prior-wave disjointness")
assert 0 < ci < cj, "chain boundaries missing"
pre, chain, post = block[:ci], block[ci:cj], block[cj:]
chain_rows = re.findall(r"assert pf\.N1_BANDS\[(\d+)\]", chain)
assert chain_rows == [str(x) for x in range(138, 158)], chain_rows
w158row = ('assert pf.N1_BANDS[158] == {"a": (362_404, 364_403),' + CRLF +
           '                                    "b_exit": (364_404, 364_603),' + CRLF +
           '                                    "engine_owner": "bm-a"}, \\' + CRLF +
           '            "registered W158 row parity drift (r307; bm-a r775)"' + CRLF +
           "        ")
# delivery/self-ack prose lives ONLY in the mat pre (header comment face);
# the post (disjointness/band-facts/assert face) passes through plain vmap
block159 = vmap_fix(pre, "mat") + chain + w158row + vmap(post)
a3 = block + "# --- T-141 s2 lane face"
r3 = block159 + "# --- T-141 s2 lane face"

# --- a4: PASS snippet claim insertion ------------------------------------------
cs = n1src.find('"+ W158 materializer face')
assert cs > 0, "W158 claim start not found"
ce = n1src.find('"r773 bm-a] "', cs) + len('"r773 bm-a] "')
assert 0 < cs < ce, "W158 claim end not found"
claim158 = n1src[cs:ce]
assert claim158 == io.open(r"results\_r781bma_w159_probe_n1_claim.txt",
                           encoding="utf-8", newline="").read(), "claim face drift vs probe"
a4 = '"r773 bm-a] "' + CRLF + '          "+ T-141 s2 "'
r4 = '"r773 bm-a] "' + CRLF + "          " + vmap_fix(claim158, "claim") + CRLF + '          "+ T-141 s2 "'

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
assert sorted(pf.N1_BANDS)[-1] == 159 and len(pf.N1_BANDS) == 157, \
    "pf N1_BANDS row-count drift after W159 insert"
assert pf.N1_BANDS[159] == {"a": (364_604, 366_603),
                            "b_exit": (366_604, 366_803),
                            "engine_owner": "bm-a"}, "W159 row face drift"
assert pf.N1_BANDS[158] == {"a": (362_404, 364_403),
                            "b_exit": (364_404, 364_603),
                            "engine_owner": "bm-a"}, "W158 row survived (r560 no-replace law)"
import perpetual_faces_n1 as n1mod
importlib.reload(n1mod)
assert n1mod.WAVE_CONFIGS[159]["a_seed_base"] == 364_604 and \
    n1mod.WAVE_CONFIGS[159]["b_exit_seed_base"] == 366_604, "W159 seed bases drift"
assert n1mod.WAVE_CONFIGS[159]["shard_subdir"] == "n1_w159" and \
    n1mod.WAVE_CONFIGS[159]["out_name"] == "n1_w159_results.json", "W159 path drift"
assert n1mod.WAVE_CONFIGS[159]["prereg"].startswith("research/PERPETUAL_N1_W159_PREREG.md"), \
    "W159 per-wave prereg citation drift"
assert os.path.exists(os.path.join("research", "PERPETUAL_N1_W159_PREREG.md")), \
    "W159 per-wave prereg missing on disk"

# materializer chain now 138..W158row (n=21)
n2 = io.open(N1, encoding="utf-8", newline="").read()
w2 = n2.find("# --- W159 materializer face")
t3 = n2.find("# --- T-141 s2 lane face", w2)
blk2 = n2[w2:t3]
chain_rows2 = re.findall(r"assert pf\.N1_BANDS\[(\d+)\]",
                         blk2[blk2.find("assert pf.N1_BANDS[138]"):
                              blk2.find("# prior-wave disjointness")])
assert chain_rows2 == [str(x) for x in range(138, 159)], chain_rows2

# r773 pit law leg 3: full-file start>end malformed-window scans on BOTH files
for path in (PF, N1):
    txt = io.open(path, encoding="utf-8", newline="").read()
    bad = [m.group() for m in re.finditer(r"(\d{3})_(\d{3})\.\.(\d{3})_(\d{3})", txt)
           if int(m.group(3)) < int(m.group(1))]
    assert not bad, f"malformed windows remain in {path}: {bad[:4]}"

# W160 projection prose present in the new W159 blocks (gate leg3 verbatim)
pf2 = io.open(PF, encoding="utf-8", newline="").read()
assert f"# {W160p_A} CLEAN hops=0 / B first-clean {W160p_B}" in pf2, "pf W160p prose missing"
assert "W160 A window; W160 freezer MUST re-derive on the post-W159" in pf2, \
    "pf W160 freezer prose missing"
# r776 fragment-needle law: the freezer prose in the n1 entry is split
# across python-string fragments ('...will refuse the naive "' ends one
# fragment; '"W160 A window; W160 freezer ...' starts the next) -- a
# contiguous 'refuse the naive W160 A window' needle is a false-negative
# (r775 bloodline L310 latent defect, settled r781); assert the
# within-fragment shapes instead.
assert '"W160 A window; W160 freezer MUST re-derive on the "' in n2, "n1 W160 freezer fragment missing"
assert '"W159 B band 366_604..366_803 will refuse the naive "' in n2, "n1 W159-band refuse fragment missing"
assert f"A first-clean {W160p_A} " in n2 and f"B first-clean {W160p_B} CLEAN" in n2, \
    "n1 W160p prose missing"
# honesty faces landed
assert "merge-absorb behind-delivery at fetch (r779 pre-seat" in pf2, "pf delivery fixup missing"
assert "bm-c r625 read-only-observer processed, e203e96c7" in pf2, "pf self-ack fixup missing"
assert "delivery window = merge-absorb behind-delivery " in n2, "n1 delivery fixup missing"
assert "bm-c r625 read-only-observer processed, e203e96c7" in n2, "n1 entry self-ack face"
# corrupted historical faces must remain eradicated from both files
for path in (PF, N1):
    txt = io.open(path, encoding="utf-8", newline="").read()
    assert "362_204..362_003" not in txt and "362_404..360_403" not in txt, \
        f"r772 malformed-window residue in {path}"

print("post-edit structural assertions PASS: N1_BANDS 157 rows tail W159, "
      "W158 row intact, WAVE_CONFIGS[159] seeded, chain 138..158 n=21, "
      "W160p prose == r779 gate leg3 verbatim, honesty fixups landed, "
      "full-file malformed-window scans CLEAN on both files")
