# -*- coding: utf-8 -*-
"""r805 bm-a W167 freeze edits: four insertions (pf N1_BANDS[167] row +
n1 WAVE_CONFIGS[167] entry + n1 W167 materializer block refresh +
n1 PASS snippet claim insertion).

Bloodline: r799 _r799bma_w166_freeze_edits.py machinery (r773 pit law
freeze-editor compliance + r776 fragment-needle law + r781
verify-separation law), W167 facts live-registry-driven:
  - band gate results/_r801bma_w167_band_gate.json rc0 ADMIT
    (A 382_204..384_203 staircase TWENTY-SIXTH instance E36 hops=1 past
    the registered W166 B band; naive 382_004..384_003 refused at its
    own start by the registered W166 B band 382_004..382_203; B
    384_204..384_403 own-A mutual exclusion hops=1, naive
    382_204..382_403);
  - pre-seat probe results/_r801bma_w167_probe_receipt.json ADMIT,
    dual-window parity True (gate leg1 parity_with_probe);
  - seat MSG-2026-10-07-0056-bma-w167-seat published 982424c5f
    (r801 pre-seat push, direct fast-forward behind-0; r565 law: on
    origin BEFORE this freeze commit);
  - per-wave prereg research/PERPETUAL_N1_W167_PREREG.md (r804 session,
    banned gate ADMIT 0);
  - W166 finalize one-pass r799: ledger head 770,612, merged pool
    K=363,120 (n1_w166_results.json machine-read);
  - W166 freeze r799 sha c2d6c5e14 (the REGISTERED W166 row citation);
  - W168+ projection (gate leg3 verbatim): A first-clean 384_204..386_203
    / B first-clean 384_404..384_603, naive-B-inside-naive-A, the
    registered W167 B band will refuse the naive W168 A window.

r773 pit law compliance:
  (1) full string-face inventory empirically probed BEFORE TOK
      (_r803bma_w167_face_probe.py -- four face dumps + needle-count
      receipt, rc0; dead-r803 session build adopted per r804 takeover);
  (2) composite band strings tokenized WHOLE (no bare-seed-prefix
      tokens; every dotted band / seed-base row / jump phrase /
      round-sha composite is a single token; bare 166/165 run LAST);
  (3) post-edit full-file start>end malformed-window regex scan on BOTH
      touched files;
  (4) every projection value re-derived FROM the on-disk gate receipts
      (r587 never-transcribe law);
  (5) r776 fragment-needle law: all needles taken from the PHYSICAL
      probe-dumped shapes (python-string fragments / comment lines,
      CRLF-exact);
  (6) NO same-window heal needed: the W166 source faces carry no
      vmap-leak residue EXCEPT the W166 claim trailing session marker
      ("r795 bm-a] " -- the r799 freeze TOK lacked that needle,
      disclosed at the r803 face probe); the frozen W166 claim stays
      (r307), the NEW W167 claim carries the correct r805 attribution
      via the @CLMS@ token;
  (7) anti-drift composite @REGROW@ (bm-a r799 freeze c2d6c5e14) runs
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
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
PF = r"scripts/perpetual_faces.py"
N1 = r"scripts/perpetual_faces_n1.py"
CRLF = "\r\n"

# --- machine-derived facts (r587: read from on-disk receipts) ----------------
gate = json.load(open("results/_r801bma_w167_band_gate.json", encoding="utf-8"))
leg1, leg3 = gate["legs"]["leg1"], gate["legs"]["leg3"]
assert gate["verdict"] == "ADMIT", gate["verdict"]
assert leg1["A"] == [382204, 384203] and leg1["B"] == [384204, 384403], leg1
assert leg1["hops_A"] == 1 and leg1["hops_B"] == 1
assert leg1["ARITH_A"] == [382004, 384003], leg1["ARITH_A"]
assert leg1["B_naive_first_clean"] == [382204, 382403], leg1["B_naive_first_clean"]
assert leg1["parity_with_probe"] is True
probe = json.load(open("results/_r801bma_w167_probe_receipt.json", encoding="utf-8"))
assert probe["verdict"] == "ADMIT" and probe["bands"] == {"A": "382204_384203", "B": "384204_384403"}, probe
w166res = json.load(open("results/perpetual_faces/n1_w166_results.json", encoding="utf-8"))
assert w166res["null_pool_cumulative"]["merged"]["n_values"] == 363120, "W166 merged K drift"
assert w166res["null_pool_cumulative"]["merged"]["n_values"] + 2200 == 365320, "W167 K projection arithmetic"
leg0 = gate["legs"]["leg0"]
assert leg0["rows"] == 164 and leg0["tail"] == "W166" and leg0["ordinal"] == 157 \
    and leg0["bma_ordinal"] == 83, leg0


def u(s):  # "384204..386203" -> "384_204..386_203"
    def g(part):
        return re.sub(r"(\d)(?=(\d{3})+$)", r"\1_", part)
    a, b = s.split("..")
    return f"{g(a)}..{g(b)}"


W168p_A = u(leg3["W168p_A"])
W168p_B = u(leg3["W168p_B"])
assert W168p_A == "384_204..386_203" and W168p_B == "384_404..384_603", (W168p_A, W168p_B)
assert leg3["W168p_B_lands_inside_W168p_A"] is True

# --- ordered value-map (tokens first, then back-substitution) ---------------
TOK = [
    # whole-line seed-base rows (entry face; bands + ordinal carried WHOLE)
    ('"a_seed_base": 380_004,        # law sec.4 W166 A: 380_004..382_003 (FIRST-CLEAN past the registered W165 B band; arithmetic 379_804..381_803 REFUSED at own start by the W165 B band; hops=1; A-hops-prior-B staircase twenty-fifth instance, E36 card)', "@ASROW@"),
    ('"b_exit_seed_base": 382_004,   # law sec.4 W166 B: 382_004..382_203 (FIRST-CLEAN past the own-wave A window; arithmetic 380_004..380_203 lands inside own-A, same-freeze mutual exclusion W141 precedent; reserved walk hops=1; B base == own-A tail+1)', "@BSROW@"),
    # row + entry carriers
    ('166: {"a": (380_004, 382_003), "b_exit": (382_004, 382_203),', "@RROW@"),
    ('166: {"batch"', "@RENTRY@"),
    # registered-prior-row citations (machine-verified sha pairing; the
    # anti-drift composite -- MUST precede every session/round token)
    ('W165 row bm-a r795 freeze', "@PROW1@"),
    ('aebb94d2d, SINGLE STATE zero seat gap W2..W165 all', "@PROW2@"),
    ('bm-a r795 freeze aebb94d2d', "@REGROW@"),
    # freeze-session composites (this window: bm-a r805 freeze)
    ('bm-a r799 freeze', "@FZH@"),
    ('r799 bm-a freeze', "@MFZH@"),
    # claim-tail session attribution (r803 probe disclosure: the W166
    # claim tail leaked as 'r795 bm-a] ' -- the r799 freeze TOK lacked
    # that needle; the frozen W166 claim stays (r307), the NEW W167
    # claim carries the correct r805 attribution via this token)
    ('r795 bm-a] ', "@CLMS@"),
    # prior-finalize citations (W165 finalize r796 -> W166 finalize r799;
    # FRAGMENT form per r781/r776 law: the entry tail physically splits
    # 'W166 ' (prior fragment) + CRLF + 'finalize one-pass bm-a r799, ...'
    # (within-fragment) -- the contiguous logical needle would count=0)
    ('W165 finalize landed same-window r796', "@FW@"),
    ('finalize one-pass bm-a r796', "@FOPM2@"),
    ('W165 bm-a r796 one-pass', "@FOP@"),
    # gate / probe receipt citations (W167 receipts)
    ('_r797bma_w166_probe_receipt.json', "@PRC@"),
    ('_r797bma_w166_band_gate.json', "@BGR@"),
    # prior gate / sec8 session refs (W165 gate r793 -> W166 gate r797;
    # W165 sec8 r796 -> W166 sec8 r799)
    ('r793 gate leg3', "@GATE@"),
    ('r793 gate', "@GATEP@"),
    ('r796 sec8 succession', "@SEC8@"),
    ('r796 sec8', "@SEC8M@"),
    # own-wave gate-session prose + pre-seat push session (r797 -> r801)
    ('gate-derived r797', "@GDR@"),
    ('r797 pre-seat push', "@PSP@"),
    # seat tokens (W166 seat 223x/d1dc12117 -> W167 seat 0056/982424c5f)
    ('MSG-2026-10-06-223x', "@SEAT@"),
    ('bma-w166-seat', "@SEATW@"),
    ('MSG-223x', "@MSGS@"),
    ('d1dc12117', "@SEATSHA@"),
    # W168 projection bands (gate leg3 verbatim, whole; BEFORE all band
    # tokens and seed backstops -- r773 pit law)
    ('382_004..384_003', "@PA@"),
    ('382_204..382_403', "@PB@"),
    # jump phrases (longest first; fragment-safe; BEFORE @BB@ which
    # shares the B-band substring)
    ('jumps to 382_004, first-clean 382_004..382_203 hops=1', "@JN@"),
    ('jumps to 382_004 -> 382_004..382_203,', "@JP@"),
    ('382_004 and lands 382_004..382_203', "@JAND@"),
    # the W167 B-assert jump fragment (rides the @JB@ token; W167 target
    # 384_204 -- the r787/r793 heal lineage, leak class killed at source)
    ('own-wave A window reserved jumps to 382_004, first-clean ', "@JB@"),
    # assert composites
    ('== 380_004 == 380_003 + 1', "@ASB@"),
    ('== 382_004 == 382_003 + 1', "@BSB@"),
    ('set(range(380_004, 382_004))', "@ARITHA@"),
    ('set(range(382_004, 382_204))', "@ARB@"),
    # dotted band geometry
    ('379_804..381_803', "@NA@"),
    ('379_804..380_003', "@OB@"),
    ('380_004..382_003', "@AB@"),
    ('380_004..380_203', "@NB@"),
    ('382_004..382_203', "@BB@"),
    # base-relation composites
    ('380_003+1', "@ABASE@"),
    ('382_003+1', "@BBASE@"),
    # identity / stats / ordinals
    ('PERPETUAL_N1_W166_PREREG.md', "@PF@"),
    ('PERPETUAL-N1-W166', "@B@"),
    ('n1_w166_results.json', "@OD@"),
    ('n1_w166', "@SD@"),
    ('n1w166', "@SD2@"),
    ('768,412', "@LEDG@"),
    ('360,920', "@K1@"),
    ('ONE HUNDRED-AND-FIFTY-SIXTH', "@ORDW@"),
    ('engine_owner rows 155', "@R154@"),
    ('rows 81 + candidate', "@ROWS80@"),
    ('eighty-first', "@SVN@"),
    ('twenty-fifth', "@ST24@"),
    # wave numbers (higher first: W167 projection -> W168; then W166->W167,
    # W165->W166)
    ('W167', "@WN2@"),
    ('W166', "@WN@"),
    ('W165', "@W@"),
    # bare round backstop (r776 fragment law: the physical W166 faces
    # break 'r797 pre-seat' + CRLF + '# push' across comment lines in the
    # pf block -- the exact-phrase TOK above cannot match it; every other
    # r797 face is already carried by composite tokens, so the bare roll
    # r797->r801 is safe; runs BEFORE the bare numerals)
    ('r797', "@RB@"),
    # bare numerals LAST (every longer carrier tokenized above; 166 before
    # 165 so the 165->166 output is never re-mapped)
    ('166', "@IDX@"),
    ('165', "@IDX2@"),
]
BACK = [
    ("@ASROW@", '"a_seed_base": 382_204,        # law sec.4 W167 A: 382_204..384_203 (FIRST-CLEAN past the registered W166 B band; arithmetic 382_004..384_003 REFUSED at own start by the W166 B band; hops=1; A-hops-prior-B staircase twenty-sixth instance, E36 card)'),
    ("@BSROW@", '"b_exit_seed_base": 384_204,   # law sec.4 W167 B: 384_204..384_403 (FIRST-CLEAN past the own-wave A window; arithmetic 382_204..382_403 lands inside own-A, same-freeze mutual exclusion W141 precedent; reserved walk hops=1; B base == own-A tail+1)'),
    ("@RROW@", '167: {"a": (382_204, 384_203), "b_exit": (384_204, 384_403),'),
    ("@RENTRY@", '167: {"batch"'),
    ("@PROW1@", "W166 row bm-a r799 freeze"),
    ("@PROW2@", "c2d6c5e14, SINGLE STATE zero seat gap W2..W166 all"),
    ("@REGROW@", "bm-a r799 freeze c2d6c5e14"),
    ("@FZH@", "bm-a r805 freeze"),
    ("@MFZH@", "r805 bm-a freeze"),
    ("@CLMS@", "r805 bm-a] "),
    ("@FW@", "W166 finalize landed same-window r799"),
    ("@FOPM2@", "finalize one-pass bm-a r799"),
    ("@FOP@", "W166 bm-a r799 one-pass"),
    ("@PRC@", "_r801bma_w167_probe_receipt.json"),
    ("@BGR@", "_r801bma_w167_band_gate.json"),
    ("@GATE@", "r797 gate leg3"),
    ("@GATEP@", "r797 gate"),
    ("@SEC8@", "r799 sec8 succession"),
    ("@SEC8M@", "r799 sec8"),
    ("@GDR@", "gate-derived r801"),
    ("@PSP@", "r801 pre-seat push"),
    ("@SEAT@", "MSG-2026-10-07-0056"),
    ("@SEATW@", "bma-w167-seat"),
    ("@MSGS@", "MSG-0056"),
    ("@SEATSHA@", "982424c5f"),
    ("@PA@", "384_204..386_203"),
    ("@PB@", "384_404..384_603"),
    ("@JN@", "jumps to 384_204, first-clean 384_204..384_403 hops=1"),
    ("@JP@", "jumps to 384_204 -> 384_204..384_403,"),
    ("@JAND@", "384_204 and lands 384_204..384_403"),
    ("@JB@", "own-wave A window reserved jumps to 384_204, first-clean "),
    ("@ASB@", "== 382_204 == 382_203 + 1"),
    ("@BSB@", "== 384_204 == 384_203 + 1"),
    ("@ARITHA@", "set(range(382_204, 384_204))"),
    ("@ARB@", "set(range(384_204, 384_404))"),
    ("@NA@", "382_004..384_003"),
    ("@OB@", "382_004..382_203"),
    ("@AB@", "382_204..384_203"),
    ("@NB@", "382_204..382_403"),
    ("@BB@", "384_204..384_403"),
    ("@ABASE@", "382_203+1"),
    ("@BBASE@", "384_203+1"),
    ("@PF@", "PERPETUAL_N1_W167_PREREG.md"),
    ("@B@", "PERPETUAL-N1-W167"),
    ("@OD@", "n1_w167_results.json"),
    ("@SD@", "n1_w167"),
    ("@SD2@", "n1w167"),
    ("@LEDG@", "770,612"),
    ("@K1@", "363,120"),
    ("@ORDW@", "ONE HUNDRED-AND-FIFTY-SEVENTH"),
    ("@R154@", "engine_owner rows 156"),
    ("@ROWS80@", "rows 82 + candidate"),
    ("@SVN@", "eighty-second"),
    ("@ST24@", "twenty-sixth"),
    ("@WN2@", "W168"),
    ("@WN@", "W167"),
    ("@W@", "W166"),
    ("@IDX@", "167"),
    ("@IDX2@", "166"),
    ("@RB@", "r801"),
]


def vmap(s: str) -> str:
    for a, b in TOK:
        s = s.replace(a, b)
    for a, b in BACK:
        s = s.replace(a, b)
    return s


# --- per-kind fragment-level fixups (r776 law: needles taken from the
# PHYSICAL probe-dumped shapes; applied AFTER vmap) ---------------------------
# W166 source faces carry ONE disclosed vmap-leak artifact: the W166
# claim trailing session marker ("r795 bm-a] " -- disclosed at the r803
# face probe, handled via the @CLMS@ TOK entry so the NEW W167 claim
# carries the correct r805 attribution).  Beyond that the W166 faces
# are clean: FIXUPS empty, vmap_fix == vmap for all kinds.
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

# face-source zero-drift gate vs the r803 probe dumps
EO = '"engine_owner": "bm-a"},'
i1 = pfsrc.find("    # W166 (bm-a r799 freeze")
assert i1 > 0, "pf W166 comment block not found"
r1 = pfsrc.find('166: {"a": (380_004', i1)
assert r1 > i1, "pf W166 row not after comment block"
j1 = pfsrc.find(EO, r1) + len(EO)
block166_pf = pfsrc[i1:j1]
assert block166_pf == io.open(r"results\_r803bma_w167_probe_pf_block.txt",
                             encoding="utf-8", newline="").read(), "pf face drift vs probe"
assert block166_pf.count("engine_owner") == 1 and "aebb94d2d" not in block166_pf
assert "379_804..381_803 REFUSED at its own start by the W165 B band" in block166_pf

# pre-edit live registry parity (the W166 registered row must be intact
# before we append the W167 row -- r560 no-replace law)
sys.path.insert(0, ".")
sys.path.insert(0, "scripts")
import perpetual_faces as pfpre
assert pfpre.N1_BANDS[166] == {"a": (380_004, 382_003),
                               "b_exit": (382_004, 382_203),
                               "engine_owner": "bm-a"}, "pre-edit W166 row drift"
assert sorted(pfpre.N1_BANDS)[-1] == 166 and len(pfpre.N1_BANDS) == 164, "pre-edit row count"

# --- a1: pf.py W166 comment block + row -> append W167 comment block + row ----
a1 = block166_pf + CRLF + "}"
r1n = block166_pf + CRLF + vmap_fix(block166_pf, "pf") + CRLF + "}"

# --- a2: n1.py WAVE_CONFIGS entry ----------------------------------------------
k = n1src.find('166: {"batch"')
assert k > 0, "n1 W166 entry not found"
m = n1src.find(EO, k) + len(EO)
entry166 = n1src[k:m]
assert entry166 == io.open(r"results\_r803bma_w167_probe_n1_entry.txt",
                          encoding="utf-8", newline="").read(), "entry face drift vs probe"
a2 = entry166 + CRLF + "                       }"
r2 = entry166 + CRLF + "                       " + vmap_fix(entry166, "n1entry") + CRLF + "                       }"

# --- a3: materializer block (chain split-verbatim + one-row extension) --------
w = n1src.find("# --- W166 materializer face")
t2 = n1src.find("# --- T-141 s2 lane face", w)
assert 0 < w < t2, "materializer anchors missing"
block = n1src[w:t2]
assert block == io.open(r"results\_r803bma_w167_probe_n1_mat.txt",
                        encoding="utf-8", newline="").read(), "mat face drift vs probe"
ci = block.find("assert pf.N1_BANDS[138]")
cj = block.find("# prior-wave disjointness")
assert 0 < ci < cj, "chain boundaries missing"
pre, chain, post = block[:ci], block[ci:cj], block[cj:]
chain_rows = re.findall(r"assert pf\.N1_BANDS\[(\d+)\]", chain)
assert chain_rows == [str(x) for x in range(138, 166)], chain_rows
w166row = ('assert pf.N1_BANDS[166] == {"a": (380_004, 382_003),' + CRLF +
           '                                    "b_exit": (382_004, 382_203),' + CRLF +
           '                                    "engine_owner": "bm-a"}, \\' + CRLF +
           '            "registered W166 row parity drift (r307; bm-a r799)"' + CRLF +
           "        ")
# delivery/payload prose lives ONLY in the mat pre (header comment face);
# the post (disjointness/band-facts/assert face) passes through plain vmap
block167 = vmap_fix(pre, "mat") + chain + w166row + vmap(post)
a3 = block + "# --- T-141 s2 lane face"
r3 = block167 + "# --- T-141 s2 lane face"

# --- a4: PASS snippet claim insertion ------------------------------------------
cs = n1src.find('"+ W166 materializer face')
assert cs > 0, "W166 claim start not found"
ce = n1src.find('"r795 bm-a] "', cs) + len('"r795 bm-a] "')
assert 0 < cs < ce, "W166 claim end not found"
claim166 = n1src[cs:ce]
assert claim166 == io.open(r"results\_r803bma_w167_probe_n1_claim.txt",
                           encoding="utf-8", newline="").read(), "claim face drift vs probe"
a4 = '"r795 bm-a] "' + CRLF + '          "+ T-141 s2 "'
r4 = '"r795 bm-a] "' + CRLF + "          " + vmap_fix(claim166, "claim") + CRLF + '          "+ T-141 s2 "'

# --- apply the four edits -------------------------------------------------------
edit(PF, [(a1, r1n)])
edit(N1, [(a2, r2), (a3, r3), (a4, r4)])

# --- post-edit structural assertions --------------------------------------------
import importlib
import perpetual_faces as pf
importlib.reload(pf)
assert sorted(pf.N1_BANDS)[-1] == 167 and len(pf.N1_BANDS) == 165, \
    "pf N1_BANDS row-count drift after W167 insert"
assert pf.N1_BANDS[167] == {"a": (382_204, 384_203),
                            "b_exit": (384_204, 384_403),
                            "engine_owner": "bm-a"}, "W167 row face drift"
assert pf.N1_BANDS[166] == {"a": (380_004, 382_003),
                            "b_exit": (382_004, 382_203),
                            "engine_owner": "bm-a"}, "W166 row survived (r560 no-replace law)"
import perpetual_faces_n1 as n1mod
importlib.reload(n1mod)
assert n1mod.WAVE_CONFIGS[167]["a_seed_base"] == 382_204 and \
    n1mod.WAVE_CONFIGS[167]["b_exit_seed_base"] == 384_204, "W167 seed bases drift"
assert n1mod.WAVE_CONFIGS[167]["shard_subdir"] == "n1_w167" and \
    n1mod.WAVE_CONFIGS[167]["out_name"] == "n1_w167_results.json", "W167 path drift"
assert n1mod.WAVE_CONFIGS[167]["prereg"].startswith("research/PERPETUAL_N1_W167_PREREG.md"), \
    "W167 per-wave prereg citation drift"
assert os.path.exists(os.path.join("research", "PERPETUAL_N1_W167_PREREG.md")), \
    "W167 per-wave prereg missing on disk"

# materializer chain now 138..W166row (n=29)
n2 = io.open(N1, encoding="utf-8", newline="").read()
w2 = n2.find("# --- W167 materializer face")
t3 = n2.find("# --- T-141 s2 lane face", w2)
blk2 = n2[w2:t3]
chain_rows2 = re.findall(r"assert pf\.N1_BANDS\[(\d+)\]",
                         blk2[blk2.find("assert pf.N1_BANDS[138]"):
                              blk2.find("# prior-wave disjointness")])
assert chain_rows2 == [str(x) for x in range(138, 167)], chain_rows2

# r773 pit law leg 3: full-file start>end malformed-window scans on BOTH files
for path in (PF, N1):
    txt = io.open(path, encoding="utf-8", newline="").read()
    bad = [m.group() for m in re.finditer(r"(\d{3})_(\d{3})\.\.(\d{3})_(\d{3})", txt)
           if int(m.group(3)) < int(m.group(1))]
    assert not bad, f"malformed windows remain in {path}: {bad[:4]}"

# W168 projection prose present in the new W167 blocks (gate leg3 verbatim)
pf2 = io.open(PF, encoding="utf-8", newline="").read()
assert f"# {W168p_A} CLEAN hops=0 / B first-clean {W168p_B}" in pf2, "pf W168p prose missing"
assert "W168 A window; W168 freezer MUST re-derive on the post-W167" in pf2, \
    "pf W168 freezer prose missing"
# r776 fragment-needle law: the freezer prose in the n1 entry is split
# across python-string fragments -- a contiguous needle is a false-negative
# (r775/r781 law); assert the within-fragment shapes instead.
assert '"W168 A window; W168 freezer MUST re-derive on the "' in n2, "n1 W168 freezer fragment missing"
assert '"W167 B band 384_204..384_403 will refuse the naive "' in n2, "n1 W167-band refuse fragment missing"
assert f"A first-clean {W168p_A} " in n2 and f"B first-clean {W168p_B} CLEAN" in n2, \
    "n1 W168p prose missing"
# honesty faces landed (self-ack deferred + 3-item payload +
# direct-FF delivery + anti-drift registered-row citation)
assert "move deferred to the W168 finalize window" in pf2, "pf self-ack fixup missing"
assert "fleet/inbox at freeze time -- honest state);" in pf2, "pf self-ack tail fixup missing"
assert "move deferred to the W168 finalize window" in n2, "mat self-ack fixup missing"
assert "fleet/inbox at freeze time -- honest state)." in n2, "mat self-ack tail missing"
assert "payload = seat MSG + pre-seat probe + probe receipt;" in pf2, "pf 3-item payload fixup missing"
assert '"seat MSG + pre-seat probe + probe receipt; "' in n2, "entry 3-item payload fixup missing"
assert "= seat MSG + pre-seat probe + probe receipt;" in n2, "mat 3-item payload fixup missing"
assert "r801 pre-seat" in pf2 and "r801 pre-seat" in n2, "push session r801 face missing"
assert "direct fast-forward behind-0" in pf2 and "direct fast-forward behind-0" in n2, \
    "direct-FF delivery face missing"
# r776 fragment-needle law: the registered-row citation is split across
# python string fragments -- assert the within-fragment shapes
assert '"number law after the REGISTERED W166 row bm-a r799 freeze "' in n2, \
    "W166 row citation frag1 missing"
assert '"c2d6c5e14, SINGLE STATE zero seat gap W2..W166 all "' in n2, \
    "W166 row citation frag2 missing"
assert '"finalize one-pass bm-a r799, net chain head 770,612, "' in n2, \
    "W166 finalize one-pass frag missing"
# r781 fragment law: the contiguous logical string 'W166 finalize one-pass
# bm-a r799' physically splits across python string fragments -- count the
# within-fragment shapes instead (mat pre 1 + entry tail 1 == 2)
assert n2.count("finalize one-pass bm-a r799") == 2, "W166 finalize one-pass count drift"
assert "bm-a r799 freeze c2d6c5e14" in n2, "mat header registered-row citation missing"
assert "aebb94d2d" not in blk2, "stale W165 sha residue in new W167 block"
assert "finalize one-pass bm-a r805" not in n2, "stale r805 finalize residue"
# the NEW W167 claim carries the corrected session attribution (r803
# probe disclosure: @CLMS@ -- the frozen W166 claim stays stale per r307)
assert '"r805 bm-a] "' in n2, "W167 claim r805 attribution missing"
# no stale round/seat/number leftovers in the NEW W167 blocks only (the
# frozen W166/W165 faces legitimately retain their historical citations;
# the mat CHAIN rows are verbatim prior-wave pinned constants (r307) --
# historical band values there are legitimate, so the mat scan covers
# only the freshly vmap'd pre (header) + post (band-facts) faces)
i2 = pf2.find("    # W167 (bm-a r805 freeze")
j2 = pf2.find(EO, i2) + len(EO)
newpfblk = pf2[i2:j2]
k2 = n2.find('167: {"batch"')
m2 = n2.find(EO, k2) + len(EO)
newentry = n2[k2:m2]
cs2 = n2.find('"+ W167 materializer face')
ce2 = n2.find('"r805 bm-a] "', cs2) + len('"r805 bm-a] "')
newclaim = n2[cs2:ce2]
ci2 = blk2.find("assert pf.N1_BANDS[138]")
cj2 = blk2.find("# prior-wave disjointness")
mat_new_faces = blk2[:ci2] + blk2[cj2:]
assert i2 > 0 and k2 > 0 and cs2 > 0, "new W167 block anchors missing"
for tag, seg in (("pf", newpfblk), ("entry", newentry),
                 ("mat", mat_new_faces), ("claim", newclaim)):
    for stale in ("r793 gate", "r796 sec8", "r797 pre-seat", "W166 (bm-a r799",
                  "bm-a r795 freeze", "r795 bm-a freeze", "MSG-2026-10-06-223x", "d1dc12117",
                  "bma-w166-seat", "MSG-223x", "merge-absorb", "379_804", "380_004",
                  "380_003", "380_203", "381_803", "382_003", "768,412", "360,920",
                  "aebb94d2d", "f7d34e5a7", "18231a529", "764cd882a", "678a07d4f",
                  "6957f509e", "6ee1207bb", "ee04482a2",
                  "twenty-fourth", "twenty-fifth", "seventy-ninth", "eightieth",
                  "eighty-first", "ONE HUNDRED-AND-FIFTY-FIFTH",
                  "ONE HUNDRED-AND-FIFTY-SIXTH", "engine_owner rows 154",
                  "engine_owner rows 155", "rows 80 + candidate", "rows 81 + candidate",
                  "n1w165", "n1_w165", "n1w166", "n1_w166",
                  "PERPETUAL-N1-W165", "PERPETUAL_N1_W165",
                  "PERPETUAL-N1-W166", "PERPETUAL_N1_W166",
                  "gate-derived r793", "gate-derived r797",
                  "r789 gate", "r790 sec8", "r785 gate", "r786 sec8",
                  "facts helper", "arc generator"):
        assert stale not in seg, f"stale {stale!r} residue in new W167 {tag} block"
        # 382_004/384_003/382_204/382_403/382_203 are NOT in the stale set:
        # they legitimately appear in the new W167 blocks as the naive-A/B
        # starts-ends and the W166 B band start (r787 371_004-precedent
        # note; r793 379_804-precedent note)
# corrupted historical faces must remain eradicated from both files
for path in (PF, N1):
    txt = io.open(path, encoding="utf-8", newline="").read()
    assert "362_204..362_003" not in txt and "362_404..360_403" not in txt, \
        f"r772 malformed-window residue in {path}"
# the W167 B-assert prose cites the W167 jump target 384_204 via the @JB@
# token (the r787/r793 heal lineage: SINGLE-LIVE materializer face
# migrates to the newest wave each freeze; git history carries the record)
assert "own-wave A window reserved jumps to 384_204, first-clean " in blk2, \
    "W167 healed-fragment face missing"
assert "own-wave A window reserved jumps to 382_004, first-clean" not in blk2, \
    "vmap-leak residue in new block"

print("post-edit structural assertions PASS: N1_BANDS 165 rows tail W167, "
      "W166 row intact, WAVE_CONFIGS[167] seeded, chain 138..166 n=29, "
      "W168p prose == r801 gate leg3 verbatim, honesty faces landed "
      "(self-ack deferred / 3-item payload / direct-FF delivery / "
      "anti-drift registered-row cite / @CLMS@ claim attribution), "
      "full-file malformed-window scans CLEAN on both files, "
      "no same-window heal needed this window")
