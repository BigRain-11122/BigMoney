# -*- coding: utf-8 -*-
"""r785 bm-a W161 freeze edits: four insertions (pf N1_BANDS[161] row +
n1 WAVE_CONFIGS[161] entry + n1 W161 materializer block refresh +
n1 PASS snippet claim insertion).

Bloodline: r783 _r783bma_w160_freeze_edits.py machinery (r773 pit law
freeze-editor compliance + r776 fragment-needle law + r781
verify-separation law), W161 facts live-registry-driven:
  - band gate results/_r785bma_w161_band_gate.json rc0 ADMIT
    (A 369_004..371_003 staircase TWENTIETH instance E36 hops=1 past the
    W160 B band; naive 368_804..370_803 refused at its own start by the
    registered W160 B band 368_804..369_003; B 371_004..371_203 own-A
    mutual exclusion hops=1, naive 369_004..369_203);
  - pre-seat probe results/_r785bma_w161_probe_receipt.json ADMIT,
    dual-window parity True (gate leg1 parity_with_probe);
  - seat MSG-2026-10-06-165x-bma-w161-seat published 0371f2093
    (r785 pre-seat push, direct fast-forward; r565 law: on origin
    BEFORE this freeze commit);
  - per-wave prereg research/PERPETUAL_N1_W161_PREREG.md (r785 session,
    banned gate ADMIT 0);
  - W160 finalize one-pass r784: ledger head 757,412, merged pool
    K=349,920 (n1_w160_results.json machine-read);
  - W160 freeze r783 sha ee04482a2 (the REGISTERED W160 row citation);
  - W162+ projection (gate leg3 verbatim): A first-clean 371_004..373_003
    / B first-clean 371_204..371_403, naive-B-inside-naive-A, the
    registered W161 B band will refuse the naive W162 A window.

r773 pit law compliance:
  (1) full string-face inventory empirically probed BEFORE TOK
      (_r785bma_w161_face_probe.py -- four face dumps + needle-count
      receipt);
  (2) composite band strings tokenized WHOLE (no bare-seed-prefix
      tokens; every dotted band / seed-base row / jump phrase / round-sha
      composite is a single token; bare 160/159 run LAST);
  (3) post-edit full-file start>end malformed-window regex scan on BOTH
      touched files;
  (4) every projection value re-derived FROM the on-disk gate receipts
      (r587 never-transcribe law);
  (5) r776 fragment-needle law: all fixup needles taken from the
      PHYSICAL probe-dumped shapes (python-string fragments / comment
      lines, CRLF-exact);
  (6) honesty fixups: W160 seat self-ack inbox->processed move LANDED
      (bm-a r784 finalize window; seat physically in
      fleet/inbox/processed/ -- verified this window); W161 pre-seat
      delivery was a DIRECT fast-forward (no merge-absorb window);
      mat-header registered-row drift face (source cited W159 row as
      "bm-a r775 freeze 6957f509e" = the W158 sha, r783-heal class
      second instance) healed with the machine-verified fact
      (W160 row = bm-a r783 freeze ee04482a2).

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
gate = json.load(open("results/_r785bma_w161_band_gate.json", encoding="utf-8"))
leg1, leg3 = gate["legs"]["leg1"], gate["legs"]["leg3"]
assert gate["verdict"] == "ADMIT", gate["verdict"]
assert leg1["A"] == [369004, 371003] and leg1["B"] == [371004, 371203], leg1
assert leg1["hops_A"] == 1 and leg1["hops_B"] == 1
assert leg1["ARITH_A"] == [368804, 370803], leg1["ARITH_A"]
assert leg1["B_naive_first_clean"] == [369004, 369203], leg1["B_naive_first_clean"]
assert leg1["parity_with_probe"] is True
probe = json.load(open("results/_r785bma_w161_probe_receipt.json", encoding="utf-8"))
assert probe["verdict"] == "ADMIT" and probe["bands"] == {"A": "369004_371003", "B": "371004_371203"}, probe
w160res = json.load(open("results/perpetual_faces/n1_w160_results.json", encoding="utf-8"))
assert w160res["null_pool_cumulative"]["merged"]["n_values"] == 349920, "W160 merged K drift"
assert w160res["null_pool_cumulative"]["merged"]["n_values"] + 2200 == 352120, "W161 K projection arithmetic"


def u(s):  # "371004..373003" -> "371_004..373_003"
    def g(part):
        return re.sub(r"(\d)(?=(\d{3})+$)", r"\1_", part)
    a, b = s.split("..")
    return f"{g(a)}..{g(b)}"


W162p_A = u(leg3["W162p_A"])
W162p_B = u(leg3["W162p_B"])
assert W162p_A == "371_004..373_003" and W162p_B == "371_204..371_403", (W162p_A, W162p_B)
assert leg3["W162p_B_lands_inside_W162p_A"] is True

# --- ordered value-map (tokens first, then back-substitution) ---------------
TOK = [
    # whole-line / long-fragment tokens (longest first; bands carried WHOLE
    # inside these tokens -- r773 pit law: no bare-seed-prefix tearing)
    ('"a_seed_base": 366_804,        # law sec.4 W160 A: 366_804..368_803 (FIRST-CLEAN past the registered W159 B band; arithmetic 366_604..368_603 REFUSED at own start by the W159 B band; hops=1; A-hops-prior-B staircase nineteenth instance, E36 card)', "@ASROW@"),
    ('"b_exit_seed_base": 368_804,   # law sec.4 W160 B: 368_804..369_003 (FIRST-CLEAN past the own-wave A window; arithmetic 366_804..367_003 lands inside own-A, same-freeze mutual exclusion W141 precedent; reserved walk hops=1; B base == own-A tail+1)', "@BSROW@"),
    ('160: {"a": (366_804, 368_803), "b_exit": (368_804, 369_003),', "@RROW@"),
    # round+sha composites (must precede the bare round/wave tokens)
    # -- @PROW1@/@PROW2@ carry the registered-prior-row citation (the W160
    # row = bm-a r783 freeze ee04482a2, machine-verified via git history)
    ('W159 row bm-a r781 freeze', "@PROW1@"),
    ('6ee1207bb, SINGLE STATE zero seat gap W2..W159 all', "@PROW2@"),
    # -- @MATROW@ heals the mat-header drift face (source cited the W159
    # row with the W158 sha "bm-a r775 freeze 6957f509e"; r783-heal class
    # second instance; healed with the machine-verified fact)
    ('bm-a r775 freeze 6957f509e', "@MATROW@"),
    ('bm-a r783 freeze', "@FZH@"),
    ('r783 bm-a freeze', "@MFZH@"),
    # W160 finalize citation composites (before bare rounds/ledger numbers)
    ('W159 finalize landed same-window r782', "@FW@"),
    ('W159 finalize one-pass bm-a r782', "@FOPM2@"),
    ('finalize one-pass bm-a r782, net chain head 755,212', "@FOPT@"),
    ('net chain head 755,212 = W159 bm-a r782 one-pass', "@COP@"),
    ('W159 bm-a r782 one-pass, K=347,720', "@CLMOP@"),
    # gate / probe receipt citations (probe r785, gate r785)
    ('_r782bma_w160_probe_receipt.json', "@PRC@"),
    ('_r783bma_w160_band_gate.json', "@BGR@"),
    # seat tokens
    ('MSG-2026-10-06-162x', "@SEAT@"),
    ('566ec5f86', "@SEATSHA@"),
    ('bma-w160-seat', "@SEATW@"),
    ('MSG-162x', "@MSGS@"),
    # W162 projection bands (gate leg3 verbatim, whole)
    ('368_804..370_803', "@PA@"),
    ('369_004..369_203', "@PB@"),
    # jump phrases (longest first; fragment-safe)
    ('jumps to 368_804, first-clean 368_804..369_003 hops=1', "@JN@"),
    ('jumps to 368_804 -> 368_804..369_003,', "@JP@"),
    ('368_804 and lands 368_804..369_003', "@JAND@"),
    # assert composites
    ('== 366_804 == 366_803 + 1', "@ASB@"),
    ('== 368_804 == 368_803 + 1', "@BSB@"),
    ('set(range(366_804, 368_804))', "@ARITHA@"),
    ('set(range(368_804, 369_004))', "@ARB@"),
    # dotted band geometry
    ('366_604..368_603', "@NA@"),
    ('366_604..366_803', "@OB@"),
    ('366_804..368_803', "@AB@"),
    ('366_804..367_003', "@NB@"),
    ('368_804..369_003', "@BB@"),
    ('366_803+1', "@ABASE@"),
    ('368_803+1', "@BBASE@"),
    # rounds (composite citations first, then bare; @GATE@ before @GATEP@;
    # @SEC8@ contiguous before @SEC8M@ line-broken fragment form)
    ('r779 gate leg3', "@GATE@"),
    ('r783 sec8 succession', "@SEC8@"),
    ('r783 sec8', "@SEC8M@"),
    ('r779 sec8 succession', "@SEC8B@"),
    ('r779 gate', "@GATEP@"),
    ('r782', "@PUSHR@"),
    ('r783', "@RW@"),
    ('r779', "@PRW@"),
    # identity / stats / ordinals
    ('PERPETUAL_N1_W160_PREREG.md', "@PF@"),
    ('PERPETUAL-N1-W160', "@B@"),
    ('n1_w160_results.json', "@OD@"),
    ('n1_w160', "@SD@"),
    ('n1w160', "@SD2@"),
    ('755,212', "@LEDG@"),
    ('347,720', "@K1@"),
    ('ONE HUNDRED-AND-FIFTIETH', "@ORDW@"),
    ('engine_owner rows 149', "@R149@"),
    ('rows 75 + candidate', "@ROWS76@"),
    ('seventy-sixth', "@SVN77@"),
    ('nineteenth', "@ST20@"),
    # wave numbers (W161 before W160 before W159)
    ('W161', "@WN@"),
    ('W160', "@W@"),
    ('W159', "@WP@"),
    # bare numerals LAST (every longer carrier tokenized above)
    ('160', "@IDX@"),
    ('159', "@IDX2@"),
]
BACK = [
    ("@ASROW@", '"a_seed_base": 369_004,        # law sec.4 W161 A: 369_004..371_003 (FIRST-CLEAN past the registered W160 B band; arithmetic 368_804..370_803 REFUSED at own start by the W160 B band; hops=1; A-hops-prior-B staircase twentieth instance, E36 card)'),
    ("@BSROW@", '"b_exit_seed_base": 371_004,   # law sec.4 W161 B: 371_004..371_203 (FIRST-CLEAN past the own-wave A window; arithmetic 369_004..369_203 lands inside own-A, same-freeze mutual exclusion W141 precedent; reserved walk hops=1; B base == own-A tail+1)'),
    ("@RROW@", '161: {"a": (369_004, 371_003), "b_exit": (371_004, 371_203),'),
    ("@PROW1@", "W160 row bm-a r783 freeze"),
    ("@PROW2@", "ee04482a2, SINGLE STATE zero seat gap W2..W160 all"),
    ("@MATROW@", "bm-a r783 freeze ee04482a2"),
    ("@FZH@", "bm-a r785 freeze"),
    ("@MFZH@", "r785 bm-a freeze"),
    ("@FW@", "W160 finalize landed same-window r784"),
    ("@FOPM2@", "W160 finalize one-pass bm-a r784"),
    ("@FOPT@", "finalize one-pass bm-a r784, net chain head 757,412"),
    ("@COP@", "net chain head 757,412 = W160 bm-a r784 one-pass"),
    ("@CLMOP@", "W160 bm-a r784 one-pass, K=349,920"),
    ("@PRC@", "_r785bma_w161_probe_receipt.json"),
    ("@BGR@", "_r785bma_w161_band_gate.json"),
    ("@SEAT@", "MSG-2026-10-06-165x"),
    ("@SEATSHA@", "0371f2093"),
    ("@SEATW@", "bma-w161-seat"),
    ("@MSGS@", "MSG-165x"),
    ("@PA@", "371_004..373_003"),
    ("@PB@", "371_204..371_403"),
    ("@JN@", "jumps to 371_004, first-clean 371_004..371_203 hops=1"),
    ("@JP@", "jumps to 371_004 -> 371_004..371_203,"),
    ("@JAND@", "371_004 and lands 371_004..371_203"),
    ("@ASB@", "== 369_004 == 369_003 + 1"),
    ("@BSB@", "== 371_004 == 371_003 + 1"),
    ("@ARITHA@", "set(range(369_004, 371_004))"),
    ("@ARB@", "set(range(371_004, 371_204))"),
    ("@NA@", "368_804..370_803"),
    ("@OB@", "368_804..369_003"),
    ("@AB@", "369_004..371_003"),
    ("@NB@", "369_004..369_203"),
    ("@BB@", "371_004..371_203"),
    ("@ABASE@", "369_003+1"),
    ("@BBASE@", "371_003+1"),
    ("@GATE@", "r783 gate leg3"),
    ("@SEC8@", "r784 sec8 succession"),
    ("@SEC8M@", "r784 sec8"),
    ("@SEC8B@", "r784 sec8 succession"),
    ("@GATEP@", "r783 gate"),
    ("@PUSHR@", "r785"),
    ("@RW@", "r785"),
    ("@PRW@", "r783"),
    ("@PF@", "PERPETUAL_N1_W161_PREREG.md"),
    ("@B@", "PERPETUAL-N1-W161"),
    ("@OD@", "n1_w161_results.json"),
    ("@SD@", "n1_w161"),
    ("@SD2@", "n1w161"),
    ("@LEDG@", "757,412"),
    ("@K1@", "349,920"),
    ("@ORDW@", "ONE HUNDRED-AND-FIFTY-FIRST"),
    ("@R149@", "engine_owner rows 150"),
    ("@ROWS76@", "rows 76 + candidate"),
    ("@SVN77@", "seventy-seventh"),
    ("@ST20@", "twentieth"),
    ("@WN@", "W162"),
    ("@W@", "W161"),
    ("@WP@", "W160"),
    ("@IDX@", "161"),
    ("@IDX2@", "160"),
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
        # delivery window: the W161 pre-seat push was a DIRECT fast-forward
        # (56947f82e..0371f2093, behind-0 at fetch; no merge-absorb window)
        ("= merge-absorb behind-delivery at fetch (r785 pre-seat" + CRLF +
         "    # push via merge-absorb window), zero --no-verify; self-ack inbox->processed",
         "= direct fast-forward behind-0 at fetch (r785 pre-seat" + CRLF +
         "    # push), zero merge, zero --no-verify; self-ack inbox->processed"),
        # self-ack honesty: W160 seat move LANDED (bm-a r784 finalize window;
        # seat physically in fleet/inbox/processed/ -- verified this window)
        ("move deferred to the W161 finalize window (seat still in" + CRLF +
         "    # fleet/inbox at freeze time -- honest state);",
         "move landed (bm-a r784 finalize window; seat in" + CRLF +
         "    # fleet/inbox/processed/);"),
    ],
    "n1entry": [
        ("delivery window = merge-absorb behind-delivery",
         "delivery window = direct fast-forward behind-0"),
        ("at fetch (r785 pre-seat push via merge-absorb window), zero",
         "at fetch (r785 pre-seat push), zero merge, zero"),
    ],
    "mat": [
        # delivery window (mat pre, 3-line physical shape) + self-ack landed
        ("delivery window = merge-absorb" + CRLF +
         "    #     behind-delivery at fetch (r785 pre-seat push via merge-absorb" + CRLF +
         "    #     window), zero --no-verify; self-ack inbox->processed move deferred to the",
         "delivery window = direct fast-forward behind-0" + CRLF +
         "    #     at fetch (r785 pre-seat push), zero merge, zero" + CRLF +
         "    #     --no-verify; self-ack inbox->processed move landed (bm-a"),
        ("W161 finalize window (seat still in fleet/inbox at freeze" + CRLF +
         "    #     time -- honest state).",
         "r784 finalize window; seat in fleet/inbox/processed/)."),
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

# face-source zero-drift gate vs the r785 probe dumps
EO = '"engine_owner": "bm-a"},'
i1 = pfsrc.find("    # W160 (bm-a r783 freeze")
assert i1 > 0, "pf W160 comment block not found"
r1 = pfsrc.find('160: {"a": (366_804', i1)
assert r1 > i1, "pf W160 row not after comment block"
j1 = pfsrc.find(EO, r1) + len(EO)
block160_pf = pfsrc[i1:j1]
assert block160_pf == io.open(r"results\_r785bma_w161_probe_pf_block.txt",
                              encoding="utf-8", newline="").read(), "pf face drift vs probe"
assert block160_pf.count("engine_owner") == 1 and "ee04482a2" not in block160_pf
assert "368_804..370_803 CLEAN hops=0 / B first-clean 369_004..369_203" in block160_pf

# --- a1: pf.py W160 comment block + row -> append W161 comment block + row --
a1 = block160_pf + CRLF + "}"
r1n = block160_pf + CRLF + vmap_fix(block160_pf, "pf") + CRLF + "}"

# --- a2: n1.py WAVE_CONFIGS entry ----------------------------------------------
k = n1src.find('160: {"batch"')
assert k > 0, "n1 W160 entry not found"
m = n1src.find(EO, k) + len(EO)
entry160 = n1src[k:m]
assert entry160 == io.open(r"results\_r785bma_w161_probe_n1_entry.txt",
                           encoding="utf-8", newline="").read(), "entry face drift vs probe"
a2 = entry160 + CRLF + "                       }"
r2 = entry160 + CRLF + "                       " + vmap_fix(entry160, "n1entry") + CRLF + "                       }"

# --- a3: materializer block (chain split-verbatim + one-row extension) --------
w = n1src.find("# --- W160 materializer face")
t2 = n1src.find("# --- T-141 s2 lane face", w)
assert 0 < w < t2, "materializer anchors missing"
block = n1src[w:t2]
assert block == io.open(r"results\_r785bma_w161_probe_n1_mat.txt",
                        encoding="utf-8", newline="").read(), "mat face drift vs probe"
ci = block.find("assert pf.N1_BANDS[138]")
cj = block.find("# prior-wave disjointness")
assert 0 < ci < cj, "chain boundaries missing"
pre, chain, post = block[:ci], block[ci:cj], block[cj:]
chain_rows = re.findall(r"assert pf\.N1_BANDS\[(\d+)\]", chain)
assert chain_rows == [str(x) for x in range(138, 160)], chain_rows
w160row = ('assert pf.N1_BANDS[160] == {"a": (366_804, 368_803),' + CRLF +
           '                                    "b_exit": (368_804, 369_003),' + CRLF +
           '                                    "engine_owner": "bm-a"}, \\' + CRLF +
           '            "registered W160 row parity drift (r307; bm-a r783)"' + CRLF +
           "        ")
# delivery/self-ack prose lives ONLY in the mat pre (header comment face);
# the post (disjointness/band-facts/assert face) passes through plain vmap
block161 = vmap_fix(pre, "mat") + chain + w160row + vmap(post)
a3 = block + "# --- T-141 s2 lane face"
r3 = block161 + "# --- T-141 s2 lane face"

# --- a4: PASS snippet claim insertion ------------------------------------------
cs = n1src.find('"+ W160 materializer face')
assert cs > 0, "W160 claim start not found"
ce = n1src.find('"r783 bm-a] "', cs) + len('"r783 bm-a] "')
assert 0 < cs < ce, "W160 claim end not found"
claim160 = n1src[cs:ce]
assert claim160 == io.open(r"results\_r785bma_w161_probe_n1_claim.txt",
                           encoding="utf-8", newline="").read(), "claim face drift vs probe"
a4 = '"r783 bm-a] "' + CRLF + '          "+ T-141 s2 "'
r4 = '"r783 bm-a] "' + CRLF + "          " + vmap_fix(claim160, "claim") + CRLF + '          "+ T-141 s2 "'

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
assert sorted(pf.N1_BANDS)[-1] == 161 and len(pf.N1_BANDS) == 159, \
    "pf N1_BANDS row-count drift after W161 insert"
assert pf.N1_BANDS[161] == {"a": (369_004, 371_003),
                            "b_exit": (371_004, 371_203),
                            "engine_owner": "bm-a"}, "W161 row face drift"
assert pf.N1_BANDS[160] == {"a": (366_804, 368_803),
                            "b_exit": (368_804, 369_003),
                            "engine_owner": "bm-a"}, "W160 row survived (r560 no-replace law)"
import perpetual_faces_n1 as n1mod
importlib.reload(n1mod)
assert n1mod.WAVE_CONFIGS[161]["a_seed_base"] == 369_004 and \
    n1mod.WAVE_CONFIGS[161]["b_exit_seed_base"] == 371_004, "W161 seed bases drift"
assert n1mod.WAVE_CONFIGS[161]["shard_subdir"] == "n1_w161" and \
    n1mod.WAVE_CONFIGS[161]["out_name"] == "n1_w161_results.json", "W161 path drift"
assert n1mod.WAVE_CONFIGS[161]["prereg"].startswith("research/PERPETUAL_N1_W161_PREREG.md"), \
    "W161 per-wave prereg citation drift"
assert os.path.exists(os.path.join("research", "PERPETUAL_N1_W161_PREREG.md")), \
    "W161 per-wave prereg missing on disk"

# materializer chain now 138..W160row (n=23)
n2 = io.open(N1, encoding="utf-8", newline="").read()
w2 = n2.find("# --- W161 materializer face")
t3 = n2.find("# --- T-141 s2 lane face", w2)
blk2 = n2[w2:t3]
chain_rows2 = re.findall(r"assert pf\.N1_BANDS\[(\d+)\]",
                         blk2[blk2.find("assert pf.N1_BANDS[138]"):
                              blk2.find("# prior-wave disjointness")])
assert chain_rows2 == [str(x) for x in range(138, 161)], chain_rows2

# r773 pit law leg 3: full-file start>end malformed-window scans on BOTH files
for path in (PF, N1):
    txt = io.open(path, encoding="utf-8", newline="").read()
    bad = [m.group() for m in re.finditer(r"(\d{3})_(\d{3})\.\.(\d{3})_(\d{3})", txt)
           if int(m.group(3)) < int(m.group(1))]
    assert not bad, f"malformed windows remain in {path}: {bad[:4]}"

# W162 projection prose present in the new W161 blocks (gate leg3 verbatim)
pf2 = io.open(PF, encoding="utf-8", newline="").read()
assert f"# {W162p_A} CLEAN hops=0 / B first-clean {W162p_B}" in pf2, "pf W162p prose missing"
assert "W162 A window; W162 freezer MUST re-derive on the post-W161" in pf2, \
    "pf W162 freezer prose missing"
# r776 fragment-needle law: the freezer prose in the n1 entry is split
# across python-string fragments -- a contiguous 'refuse the naive W162 A
# window' needle is a false-negative (r775/r781 law); assert the
# within-fragment shapes instead.
assert '"W162 A window; W162 freezer MUST re-derive on the "' in n2, "n1 W162 freezer fragment missing"
assert '"W161 B band 371_004..371_203 will refuse the naive "' in n2, "n1 W161-band refuse fragment missing"
assert f"A first-clean {W162p_A} " in n2 and f"B first-clean {W162p_B} CLEAN" in n2, \
    "n1 W162p prose missing"
# honesty faces landed (self-ack landed r784 + direct-FF delivery + drift-heal)
assert "move landed (bm-a r784 finalize window; seat in" in pf2, "pf self-ack fixup missing"
assert "fleet/inbox/processed/);" in pf2, "pf self-ack tail fixup missing"
assert "self-ack inbox->processed move landed (bm-a" in n2, "mat self-ack fixup missing"
assert "r784 finalize window; seat in fleet/inbox/processed/)." in n2, "mat self-ack tail missing"
assert "r785 pre-seat" in pf2 and "r785 pre-seat" in n2, "push session r785 face missing"
assert "direct fast-forward behind-0" in pf2 and "direct fast-forward behind-0" in n2, \
    "direct-FF delivery face missing"
# r776 fragment-needle law: the registered-row citation is split across
# python string fragments -- assert the within-fragment shapes
assert '"number law after the REGISTERED W160 row bm-a r783 freeze "' in n2, \
    "W160 row citation frag1 heal missing"
assert '"ee04482a2, SINGLE STATE zero seat gap W2..W160 all "' in n2, \
    "W160 row citation frag2 heal missing"
assert '"finalize one-pass bm-a r784, net chain head 757,412, "' in n2, \
    "W160 finalize one-pass frag heal missing"
assert n2.count("W160 finalize one-pass bm-a r784") == 1, "W160 finalize one-pass mat-header heal count drift"
assert "W160 bm-a r784 one-pass" in n2, "COP face missing"
assert "bm-a r783 freeze ee04482a2" in n2, "mat header registered-row drift heal missing"
assert "6957f509e" not in n2[w2:t3], "mat header stale W158 sha residue in new block"
assert "finalize one-pass bm-a r785" not in n2, "stale r785 finalize residue"
# no stale round/seat leftovers in the NEW W161 blocks only (the frozen
# W160/W159 faces legitimately retain their historical citations; scope
# the scan to the freshly appended blocks)
i2 = pf2.find("    # W161 (bm-a r785 freeze")
j2 = pf2.find(EO, i2) + len(EO)
newpfblk = pf2[i2:j2]
k2 = n2.find('161: {"batch"')
m2 = n2.find(EO, k2) + len(EO)
newentry = n2[k2:m2]
cs2 = n2.find('"+ W161 materializer face')
ce2 = n2.find('"r785 bm-a] "', cs2) + len('"r785 bm-a] "')
newclaim = n2[cs2:ce2]
assert i2 > 0 and k2 > 0 and cs2 > 0, "new W161 block anchors missing"
for tag, seg in (("pf", newpfblk), ("entry", newentry),
                 ("mat", n2[w2:t3]), ("claim", newclaim)):
    for stale in ("r779 gate", "r779 sec8", "r782", "MSG-2026-10-06-162x", "566ec5f86",
                  "merge-absorb", "366_604", "366_804", "362_404", "755,212",
                  "347,720", "r781 freeze", "6ee1207bb"):
        assert stale not in seg, f"stale {stale!r} residue in new W161 {tag} block"
        # 368_804 is NOT in the stale set: it legitimately appears in the
        # new W161 blocks as the naive-A start and the W160 B band start
# corrupted historical faces must remain eradicated from both files
for path in (PF, N1):
    txt = io.open(path, encoding="utf-8", newline="").read()
    assert "362_204..362_003" not in txt and "362_404..360_403" not in txt, \
        f"r772 malformed-window residue in {path}"

print("post-edit structural assertions PASS: N1_BANDS 159 rows tail W161, "
      "W160 row intact, WAVE_CONFIGS[161] seeded, chain 138..160 n=23, "
      "W162p prose == r785 gate leg3 verbatim, honesty fixups landed "
      "(self-ack landed r784 / direct-FF delivery / drift-heal), "
      "full-file malformed-window scans CLEAN on both files")
