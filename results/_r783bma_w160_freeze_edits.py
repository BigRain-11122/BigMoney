# -*- coding: utf-8 -*-
"""r783 bm-a W160 freeze edits: four insertions (pf N1_BANDS[160] row +
n1 WAVE_CONFIGS[160] entry + n1 W160 materializer block refresh +
n1 PASS snippet claim insertion).

Bloodline: r781 _r781bma_w159_freeze_edits.py machinery (r773 pit law
freeze-editor compliance + r776 fragment-needle law + r781
verify-separation law), W160 facts live-registry-driven:
  - band gate results/_r783bma_w160_band_gate.json rc0 ADMIT
    (A 366_804..368_803 staircase NINETEENTH instance E36 hops=1 past the
    W159 B band; naive 366_604..368_603 refused at its own start by the
    registered W159 B band 366_604..366_803; B 368_804..369_003 own-A
    mutual exclusion hops=1, naive 366_804..367_003);
  - pre-seat probe results/_r782bma_w160_probe_receipt.json ADMIT,
    dual-window parity True (gate leg1 parity_with_probe);
  - seat MSG-2026-10-06-162x-bma-w160-seat published 566ec5f86
    (r782 pre-seat push via merge-absorb window, r565 law: on origin
    BEFORE this freeze commit);
  - per-wave prereg research/PERPETUAL_N1_W160_PREREG.md (r783 session,
    banned gate ADMIT 0);
  - W159 finalize one-pass r782: ledger head 755,212, merged pool
    K=347,720 (n1_w159_results.json machine-read);
  - W159 freeze r781 sha 6ee1207bb (the REGISTERED W159 row citation);
  - W161+ projection (gate leg3 verbatim): A first-clean 368_804..370_803
    / B first-clean 369_004..369_203, naive-B-inside-naive-A, the
    registered W160 B band will refuse the naive W161 A window.

r773 pit law compliance:
  (1) full string-face inventory empirically probed BEFORE TOK
      (_r783bma_w160_probe.py -- four face dumps + needle-count receipt);
  (2) composite band strings tokenized WHOLE (no bare-seed-prefix
      tokens; every dotted band / seed-base row / jump phrase / round-sha
      composite is a single token; bare 159/158 run LAST);
  (3) post-edit full-file start>end malformed-window regex scan on BOTH
      touched files;
  (4) every projection value re-derived FROM the on-disk gate receipts
      (r587 never-transcribe law);
  (5) r776 fragment-needle law: all fixup needles taken from the
      PHYSICAL probe-dumped shapes (python-string fragments / comment
      lines, CRLF-exact);
  (6) honesty fixups: W160 seat self-ack inbox->processed move DEFERRED
      to the W160 finalize window (seat still in fleet/inbox at freeze
      time -- honest state, unlike W159's landed face); drift-heal
      composites carry machine-verified facts (W159 row = r781 freeze
      6ee1207bb; W159 finalize one-pass = r782).

EOL-adaptive (r370 law: CRLF-dominant blocks written CRLF);
needle count==1 (r745); insert-after-last-registered-row (r560);
anchor = predecessor full lines (r580/r781); AST gate after every
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
gate = json.load(open("results/_r783bma_w160_band_gate.json", encoding="utf-8"))
leg1, leg3 = gate["legs"]["leg1"], gate["legs"]["leg3"]
assert gate["verdict"] == "ADMIT", gate["verdict"]
assert leg1["A"] == [366804, 368803] and leg1["B"] == [368804, 369003], leg1
assert leg1["hops_A"] == 1 and leg1["hops_B"] == 1
assert leg1["ARITH_A"] == [366604, 368603], leg1["ARITH_A"]
assert leg1["B_naive_first_clean"] == [366804, 367003], leg1["B_naive_first_clean"]
assert leg1["parity_with_probe"] is True
probe = json.load(open("results/_r782bma_w160_probe_receipt.json", encoding="utf-8"))
assert probe["verdict"] == "ADMIT" and probe["bands"] == {"A": "366804_368803", "B": "368804_369003"}, probe
w159res = json.load(open("results/perpetual_faces/n1_w159_results.json", encoding="utf-8"))
assert w159res["null_pool_cumulative"]["merged"]["n_values"] == 347720, "W159 merged K drift"
assert w159res["null_pool_cumulative"]["merged"]["n_values"] + 2200 == 349920, "W160 K projection arithmetic"


def u(s):  # "368804..370803" -> "368_804..370_803"
    def g(part):
        return re.sub(r"(\d)(?=(\d{3})+$)", r"\1_", part)
    a, b = s.split("..")
    return f"{g(a)}..{g(b)}"


W161p_A = u(leg3["W161p_A"])
W161p_B = u(leg3["W161p_B"])
assert W161p_A == "368_804..370_803" and W161p_B == "369_004..369_203", (W161p_A, W161p_B)
assert leg3["W161p_B_lands_inside_W161p_A"] is True

# --- ordered value-map (tokens first, then back-substitution) ---------------
TOK = [
    # whole-line / long-fragment tokens (longest first; bands carried WHOLE
    # inside these tokens -- r773 pit law: no bare-seed-prefix tearing)
    ('"a_seed_base": 364_604,        # law sec.4 W159 A: 364_604..366_603 (FIRST-CLEAN past the registered W158 B band; arithmetic 364_404..366_403 REFUSED at own start by the W158 B band; hops=1; A-hops-prior-B staircase eighteenth instance, E36 card)', "@ASROW@"),
    ('"b_exit_seed_base": 366_604,   # law sec.4 W159 B: 366_604..366_803 (FIRST-CLEAN past the own-wave A window; arithmetic 364_604..364_803 lands inside own-A, same-freeze mutual exclusion W141 precedent; reserved walk hops=1; B base == own-A tail+1)', "@BSROW@"),
    ('159: {"a": (364_604, 366_603), "b_exit": (366_604, 366_803),', "@RROW@"),
    # round+sha composites (must precede the bare round/wave tokens)
    # -- @FZT@ heals the r781-vmap drift face (source W159 entry cites the
    # W158 row as "bm-a r773 freeze aed41df3e"; the machine-verified fact
    # per gate leg0 + git history: W159 row = bm-a r781 freeze 6ee1207bb)
    ("bm-a r773 freeze aed41df3e", "@FZT@"),
    ("W158 finalize landed same-window r778", "@FW@"),
    ("W158 finalize one-pass bm-a r778", "@FOPM@"),
    # FOPT fragment form (r776 law): the source tail is split across
    # python string fragments -- '...ALL LANDED (W158 "' ends one
    # fragment; 'finalize one-pass bm-a r779, net chain head 753,012, "'
    # starts the next. The contiguous 'W158 finalize one-pass bm-a r779'
    # needle is a silent zero-match (r781 latent-defect class, settled
    # r783 via _r783bma_w160_fopt_heal.py).
    ("finalize one-pass bm-a r779, net chain head 753,012", "@FOPT@"),
    ("W158 bm-a r778 one-pass", "@COP@"),
    # gate / probe receipt citations (probe ran r782, gate ran r783)
    ("_r779bma_w159_probe_receipt.json", "@PRC@"),
    ("_r779bma_w159_band_gate.json", "@BGR@"),
    ("_r779bma", "@RD@"),
    # pre-seat push session (r782, NOT the freeze session r783)
    ("r779 pre-seat", "@PUSH@"),
    # jump phrases (longest first; fragment-broken variants last)
    ("jumps to 366_604, first-clean 366_604..366_803 hops=1", "@JN@"),
    ("jumps to 366_604 -> 366_604..366_803,", "@JP@"),
    ("366_604 and lands", "@JAND@"),
    ("jumps to 366_604, first-clean", "@JFT@"),
    # assert composites
    ("== 364_604 == 364_603 + 1", "@ASB@"),
    ("== 366_604 == 366_603 + 1", "@BSB@"),
    ("set(range(364_604, 366_604))", "@ARITHA@"),
    ("set(range(366_604, 366_804))", "@ARB@"),
    # dotted band geometry
    ("364_404..364_603", "@PB@"),
    ("364_404..366_403", "@NA@"),
    ("364_604..366_603", "@AB@"),
    ("364_604..364_803", "@NB@"),
    ("366_604..366_803", "@OB@"),
    ("364_603+1", "@ABASE@"),
    ("366_603+1", "@BBASE@"),
    # identity / stats / ordinals
    ("PERPETUAL_N1_W159_PREREG.md", "@PF@"),
    ("PERPETUAL-N1-W159", "@B@"),
    ("n1_w159_results.json", "@OD@"),
    ("n1_w159", "@SD@"),
    ("MSG-2026-10-06-142x", "@SEAT@"),
    ("7b60d09da", "@SEATSHA@"),
    ("MSG-142x", "@MSGS@"),
    ("753,012", "@LEDG@"),
    ("345,520", "@K1@"),
    ("ONE HUNDRED-AND-FORTY-NINTH", "@ORDW@"),
    ("engine_owner rows 148", "@R145@"),
    ("rows 74 + candidate", "@OWN72@"),
    ("seventy-fifth", "@OWN73@"),
    ("eighteenth", "@F16@"),
    ("r779", "@RW@"),
    ("r773", "@PRW@"),
    ("W159", "@W@"),
    ("W158", "@WP@"),
    # bare numerals LAST (every longer carrier tokenized above)
    ("159", "@IDX@"),
    ("158", "@IDX2@"),
]
BACK = [
    ("@ASROW@", '"a_seed_base": 366_804,        # law sec.4 W160 A: 366_804..368_803 (FIRST-CLEAN past the registered W159 B band; arithmetic 366_604..368_603 REFUSED at own start by the W159 B band; hops=1; A-hops-prior-B staircase nineteenth instance, E36 card)'),
    ("@BSROW@", '"b_exit_seed_base": 368_804,   # law sec.4 W160 B: 368_804..369_003 (FIRST-CLEAN past the own-wave A window; arithmetic 366_804..367_003 lands inside own-A, same-freeze mutual exclusion W141 precedent; reserved walk hops=1; B base == own-A tail+1)'),
    ("@RROW@", '160: {"a": (366_804, 368_803), "b_exit": (368_804, 369_003),'),
    ("@FZT@", "bm-a r781 freeze 6ee1207bb"),
    ("@FW@", "W159 finalize landed same-window r782"),
    ("@FOPM@", "W159 finalize one-pass bm-a r782"),
    ("@FOPT@", "finalize one-pass bm-a r782, net chain head 755,212"),
    ("@COP@", "W159 bm-a r782 one-pass"),
    ("@PRC@", "_r782bma_w160_probe_receipt.json"),
    ("@BGR@", "_r783bma_w160_band_gate.json"),
    ("@RD@", "_r783bma"),
    ("@PUSH@", "r782 pre-seat"),
    ("@JN@", "jumps to 368_804, first-clean 368_804..369_003 hops=1"),
    ("@JP@", "jumps to 368_804 -> 368_804..369_003,"),
    ("@JAND@", "368_804 and lands"),
    ("@JFT@", "jumps to 368_804, first-clean"),
    ("@ASB@", "== 366_804 == 366_803 + 1"),
    ("@BSB@", "== 368_804 == 368_803 + 1"),
    ("@ARITHA@", "set(range(366_804, 368_804))"),
    ("@ARB@", "set(range(368_804, 369_004))"),
    ("@PB@", "366_604..366_803"),
    ("@NA@", "366_604..368_603"),
    ("@AB@", "366_804..368_803"),
    ("@NB@", "366_804..367_003"),
    ("@OB@", "368_804..369_003"),
    ("@ABASE@", "366_803+1"),
    ("@BBASE@", "368_803+1"),
    ("@PF@", "PERPETUAL_N1_W160_PREREG.md"),
    ("@B@", "PERPETUAL-N1-W160"),
    ("@OD@", "n1_w160_results.json"),
    ("@SD@", "n1_w160"),
    ("@SEAT@", "MSG-2026-10-06-162x"),
    ("@SEATSHA@", "566ec5f86"),
    ("@MSGS@", "MSG-162x"),
    ("@LEDG@", "755,212"),
    ("@K1@", "347,720"),
    ("@ORDW@", "ONE HUNDRED-AND-FIFTIETH"),
    ("@R145@", "engine_owner rows 149"),
    ("@OWN72@", "rows 75 + candidate"),
    ("@OWN73@", "seventy-sixth"),
    ("@F16@", "nineteenth"),
    ("@RW@", "r783"),
    ("@PRW@", "r779"),
    ("@W@", "W160"),
    ("@WP@", "W159"),
    ("@IDX@", "160"),
    ("@IDX2@", "159"),
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
        # W161+ projection bands (gate leg3 verbatim; single comment line)
        ("366_604..368_603 CLEAN hops=0 / B first-clean 366_804..367_003",
         f"{W161p_A} CLEAN hops=0 / B first-clean {W161p_B}"),
        # freezer wave-numbers (post-vmap uniform line)
        ("W160 A window; W160 freezer MUST re-derive on the post-W160",
         "W161 A window; W161 freezer MUST re-derive on the post-W160"),
        # self-ack honesty: W160 seat still in fleet/inbox at freeze time --
        # move DEFERRED to the W160 finalize window (W159's landed face does
        # NOT carry over; physical shape CRLF-exact from the probe dump)
        ("zero --no-verify; self-ack inbox->processed" + CRLF +
         "    # move landed (bm-c r625 read-only-observer processed, e203e96c7);",
         "zero --no-verify; self-ack inbox->processed" + CRLF +
         "    # move deferred to the W160 finalize window (seat still in" + CRLF +
         "    # fleet/inbox at freeze time -- honest state);"),
    ],
    "n1entry": [
        # W161+ projection values (gate leg3 verbatim; physical fragments)
        ("A first-clean 366_604..368_603 ", f"A first-clean {W161p_A} "),
        ("B first-clean 366_804..367_003 CLEAN", f"B first-clean {W161p_B} CLEAN"),
        # fragment-broken freezer line: 'refuse the naive' ends the previous
        # python string fragment; the wave-number fix targets this fragment
        ("W160 A window; W160 freezer", "W161 A window; W161 freezer"),
    ],
    "mat": [
        # self-ack honesty (comment face, 4-space-extra indent; the ONE
        # HUNDRED-AND-FIFTIETH tail line is untouched past the needle end)
        ("self-ack inbox->processed move landed" + CRLF +
         "    #     (bm-c r625 read-only-observer processed, e203e96c7).",
         "self-ack inbox->processed move deferred to the" + CRLF +
         "    #     W160 finalize window (seat still in fleet/inbox at freeze" + CRLF +
         "    #     time -- honest state)."),
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

# face-source zero-drift gate vs the r783 probe dumps
EO = '"engine_owner": "bm-a"},'
i1 = pfsrc.find("    # W159 (bm-a r779 freeze")
assert i1 > 0, "pf W159 comment block not found"
r1 = pfsrc.find('159: {"a": (364_604, 366_603)', i1)
assert r1 > i1, "pf W159 row not after comment block"
j1 = pfsrc.find(EO, r1) + len(EO)
block159_pf = pfsrc[i1:j1]
assert block159_pf == io.open(r"results\_r783bma_w160_probe_pf_block.txt",
                              encoding="utf-8", newline="").read(), "pf face drift vs probe"
assert block159_pf.count("engine_owner") == 1 and "6ee1207bb" not in block159_pf
assert "366_604..368_603 CLEAN hops=0 / B first-clean 366_804..367_003" in block159_pf

# --- a1: pf.py W159 comment block + row -> append W160 comment block + row --
a1 = block159_pf + CRLF + "}"
r1n = block159_pf + CRLF + vmap_fix(block159_pf, "pf") + CRLF + "}"

# --- a2: n1.py WAVE_CONFIGS entry ----------------------------------------------
k = n1src.find('159: {"batch"')
assert k > 0, "n1 W159 entry not found"
m = n1src.find(EO, k) + len(EO)
entry159 = n1src[k:m]
assert entry159 == io.open(r"results\_r783bma_w160_probe_n1_entry.txt",
                           encoding="utf-8", newline="").read(), "entry face drift vs probe"
a2 = entry159 + CRLF + "                       }"
r2 = entry159 + CRLF + "                       " + vmap_fix(entry159, "n1entry") + CRLF + "                       }"

# --- a3: materializer block (chain split-verbatim + one-row extension) --------
w = n1src.find("# --- W159 materializer face")
t2 = n1src.find("# --- T-141 s2 lane face", w)
assert 0 < w < t2, "materializer anchors missing"
block = n1src[w:t2]
assert block == io.open(r"results\_r783bma_w160_probe_n1_mat.txt",
                        encoding="utf-8", newline="").read(), "mat face drift vs probe"
ci = block.find("assert pf.N1_BANDS[138]")
cj = block.find("# prior-wave disjointness")
assert 0 < ci < cj, "chain boundaries missing"
pre, chain, post = block[:ci], block[ci:cj], block[cj:]
chain_rows = re.findall(r"assert pf\.N1_BANDS\[(\d+)\]", chain)
assert chain_rows == [str(x) for x in range(138, 159)], chain_rows
w159row = ('assert pf.N1_BANDS[159] == {"a": (364_604, 366_603),' + CRLF +
           '                                    "b_exit": (366_604, 366_803),' + CRLF +
           '                                    "engine_owner": "bm-a"}, \\' + CRLF +
           '            "registered W159 row parity drift (r307; bm-a r781)"' + CRLF +
           "        ")
# delivery/self-ack prose lives ONLY in the mat pre (header comment face);
# the post (disjointness/band-facts/assert face) passes through plain vmap
block160 = vmap_fix(pre, "mat") + chain + w159row + vmap(post)
a3 = block + "# --- T-141 s2 lane face"
r3 = block160 + "# --- T-141 s2 lane face"

# --- a4: PASS snippet claim insertion ------------------------------------------
cs = n1src.find('"+ W159 materializer face')
assert cs > 0, "W159 claim start not found"
ce = n1src.find('"r779 bm-a] "', cs) + len('"r779 bm-a] "')
assert 0 < cs < ce, "W159 claim end not found"
claim159 = n1src[cs:ce]
assert claim159 == io.open(r"results\_r783bma_w160_probe_n1_claim.txt",
                           encoding="utf-8", newline="").read(), "claim face drift vs probe"
a4 = '"r779 bm-a] "' + CRLF + '          "+ T-141 s2 "'
r4 = '"r779 bm-a] "' + CRLF + "          " + vmap_fix(claim159, "claim") + CRLF + '          "+ T-141 s2 "'

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
assert sorted(pf.N1_BANDS)[-1] == 160 and len(pf.N1_BANDS) == 158, \
    "pf N1_BANDS row-count drift after W160 insert"
assert pf.N1_BANDS[160] == {"a": (366_804, 368_803),
                            "b_exit": (368_804, 369_003),
                            "engine_owner": "bm-a"}, "W160 row face drift"
assert pf.N1_BANDS[159] == {"a": (364_604, 366_603),
                            "b_exit": (366_604, 366_803),
                            "engine_owner": "bm-a"}, "W159 row survived (r560 no-replace law)"
import perpetual_faces_n1 as n1mod
importlib.reload(n1mod)
assert n1mod.WAVE_CONFIGS[160]["a_seed_base"] == 366_804 and \
    n1mod.WAVE_CONFIGS[160]["b_exit_seed_base"] == 368_804, "W160 seed bases drift"
assert n1mod.WAVE_CONFIGS[160]["shard_subdir"] == "n1_w160" and \
    n1mod.WAVE_CONFIGS[160]["out_name"] == "n1_w160_results.json", "W160 path drift"
assert n1mod.WAVE_CONFIGS[160]["prereg"].startswith("research/PERPETUAL_N1_W160_PREREG.md"), \
    "W160 per-wave prereg citation drift"
assert os.path.exists(os.path.join("research", "PERPETUAL_N1_W160_PREREG.md")), \
    "W160 per-wave prereg missing on disk"

# materializer chain now 138..W159row (n=22)
n2 = io.open(N1, encoding="utf-8", newline="").read()
w2 = n2.find("# --- W160 materializer face")
t3 = n2.find("# --- T-141 s2 lane face", w2)
blk2 = n2[w2:t3]
chain_rows2 = re.findall(r"assert pf\.N1_BANDS\[(\d+)\]",
                         blk2[blk2.find("assert pf.N1_BANDS[138]"):
                              blk2.find("# prior-wave disjointness")])
assert chain_rows2 == [str(x) for x in range(138, 160)], chain_rows2

# r773 pit law leg 3: full-file start>end malformed-window scans on BOTH files
for path in (PF, N1):
    txt = io.open(path, encoding="utf-8", newline="").read()
    bad = [m.group() for m in re.finditer(r"(\d{3})_(\d{3})\.\.(\d{3})_(\d{3})", txt)
           if int(m.group(3)) < int(m.group(1))]
    assert not bad, f"malformed windows remain in {path}: {bad[:4]}"

# W161 projection prose present in the new W160 blocks (gate leg3 verbatim)
pf2 = io.open(PF, encoding="utf-8", newline="").read()
assert f"# {W161p_A} CLEAN hops=0 / B first-clean {W161p_B}" in pf2, "pf W161p prose missing"
assert "W161 A window; W161 freezer MUST re-derive on the post-W160" in pf2, \
    "pf W161 freezer prose missing"
# r776 fragment-needle law: the freezer prose in the n1 entry is split
# across python-string fragments -- a contiguous 'refuse the naive W161 A
# window' needle is a false-negative (r775/r781 law); assert the
# within-fragment shapes instead.
assert '"W161 A window; W161 freezer MUST re-derive on the "' in n2, "n1 W161 freezer fragment missing"
assert '"W160 B band 368_804..369_003 will refuse the naive "' in n2, "n1 W160-band refuse fragment missing"
assert f"A first-clean {W161p_A} " in n2 and f"B first-clean {W161p_B} CLEAN" in n2, \
    "n1 W161p prose missing"
# honesty faces landed (self-ack deferred + drift-heal + push session r782)
assert "move deferred to the W160 finalize window (seat still in" in pf2, "pf self-ack fixup missing"
assert "self-ack inbox->processed move deferred to the" in n2, "mat self-ack fixup missing"
assert "W160 finalize window (seat still in fleet/inbox at freeze" in n2, "mat self-ack tail missing"
assert "r782 pre-seat" in pf2 and "r782 pre-seat" in n2, "push session r782 face missing"
# r776 fragment-needle law: the W159-row freeze citation is split across
# python string fragments -- the contiguous 'bm-a r781 freeze 6ee1207bb'
# needle is a false-negative (this exact defect class is why the r781
# @FZ@ zero-match produced the W159 entry drift face); assert the
# within-fragment shapes instead (post-@FZT@-heal physical form).
assert '"number law after the REGISTERED W159 row bm-a r781 freeze "' in n2, \
    "W159 row citation frag1 drift-heal missing"
assert '"6ee1207bb, SINGLE STATE zero seat gap W2..W159 all "' in n2, \
    "W159 row citation frag2 drift-heal missing"
assert '"finalize one-pass bm-a r782, net chain head 755,212, "' in n2, \
    "W159 finalize one-pass frag heal missing"
assert n2.count("W159 finalize one-pass bm-a r782") == 1, "W159 finalize one-pass mat-header heal count drift"
# corrupted historical faces must remain eradicated from both files
for path in (PF, N1):
    txt = io.open(path, encoding="utf-8", newline="").read()
    assert "362_204..362_003" not in txt and "362_404..360_403" not in txt, \
        f"r772 malformed-window residue in {path}"

print("post-edit structural assertions PASS: N1_BANDS 158 rows tail W160, "
      "W159 row intact, WAVE_CONFIGS[160] seeded, chain 138..159 n=22, "
      "W161p prose == r783 gate leg3 verbatim, honesty fixups landed "
      "(self-ack deferred / drift-heal / r782 push session), "
      "full-file malformed-window scans CLEAN on both files")
