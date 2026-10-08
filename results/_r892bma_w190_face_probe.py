# -*- coding: utf-8 -*-
"""r892 bm-a W190 freeze pre-TOK empirical probe, stage-1 dump (r773 pit
law leg 1: full string-face inventory BEFORE writing TOK; r776 law:
needles taken from PHYSICAL fragment shapes). Dumps the four W189
faces (pf comment block+row / n1 WAVE_CONFIGS entry / n1 materializer
block / n1 PASS claim) to receipt files. Bloodline: r819/r822/r826/
r830/r834/r843/r845/r849/r852/r863/r867/r869/r874/r878/r881/r882/
r885/r888/r890 face-probe machinery rolled one generation; W190 facts:
  - pre-seat probe results/_r891bma_w190_probe_receipt.json rc0 ADMIT
    (leg0 registry 187 rows tail W189 ordinal 180 / bma_ordinal 106;
    leg1 A 432_804..434_803 staircase FIFTIETH instance E36 hops=1
    past the registered W189 B band 432_604..432_803; B 434_804..435_003
    own-A mutual exclusion W141 leg2 hops=1, naive 432_804..433_003;
    leg2 conflicts 0; leg3 origin vacancy True; leg4 W191+ projection
    A 434_804..436_803 / B 435_004..435_203, B inside A);
  - seat MSG-2026-10-08-2035-bma-w190-seat published (r891 seat push
    c177bf73b; r565 law: on origin BEFORE this freeze commit);
  - registered W189 five-face registration sha machine-derived =
    8addea3eb (rode the r890 round closeout commit -- no standalone
    anchored subject, content-anchored -S derivation, disclosed);
    W189 finalize landed r891 one-pass (results/perpetual_faces/
    n1_w189_results.json: merged K=413,720, ledger head 823,128);
    W189 sec7/sec8 settle backfill landed the r892 window (this
    window, first leg)."""
import io
import json
import re

PF = r"scripts/perpetual_faces.py"
N1 = r"scripts/perpetual_faces_n1.py"
EO = '"engine_owner": "bm-a"},'

pfsrc = io.open(PF, encoding="utf-8", newline="").read()
n1src = io.open(N1, encoding="utf-8", newline="").read()

# face 1: pf W189 comment block + row
i1 = pfsrc.find("    # W189 (bm-a r890 freeze")
assert i1 > 0, "pf W189 comment block not found"
r1 = pfsrc.find('189: {"a": (430_604', i1)
assert r1 > i1, "pf W189 row not after comment block"
j1 = pfsrc.find(EO, r1) + len(EO)
blk_pf = pfsrc[i1:j1]
io.open(r"results\_r892bma_w190_probe_pf_block.txt", "w", encoding="utf-8", newline="").write(blk_pf)

# face 2: n1 WAVE_CONFIGS W189 entry
k = n1src.find('189: {"batch"')
assert k > 0, "n1 W189 entry not found"
m = n1src.find(EO, k) + len(EO)
entry189 = n1src[k:m]
io.open(r"results\_r892bma_w190_probe_n1_entry.txt", "w", encoding="utf-8", newline="").write(entry189)

# face 3: n1 W189 materializer block
w = n1src.find("# --- W189 materializer face")
t2 = n1src.find("# --- T-141 s2 lane face", w)
assert 0 < w < t2, "materializer anchors missing"
blk_mat = n1src[w:t2]
io.open(r"results\_r892bma_w190_probe_n1_mat.txt", "w", encoding="utf-8", newline="").write(blk_mat)

# face 4: n1 PASS snippet claim (r776 physical-shape law: the W189 claim
# trailing session marker is "r890 bm-a] " -- the r890-emitted freeze
# tool session attribution; the W190 tool rolls it to the new session)
cs = n1src.find('"+ W189 materializer face')
ce = n1src.find('"r890 bm-a] "', cs) + len('"r890 bm-a] "')
assert 0 < cs < ce, "W189 claim anchors missing"
claim189 = n1src[cs:ce]
io.open(r"results\_r892bma_w190_probe_n1_claim.txt", "w", encoding="utf-8", newline="").write(claim189)

receipt = {
    "probe": "r892 W190 freeze pre-TOK string-face inventory (stage-1 dump)",
    "faces": {
        "pf_block_len": len(blk_pf), "n1_entry_len": len(entry189),
        "mat_block_len": len(blk_mat), "claim_len": len(claim189),
    },
    "pf_block_eol_crlf": blk_pf.count("\r\n"),
    "n1_entry_eol_crlf": entry189.count("\r\n"),
    "mat_block_eol_crlf": blk_mat.count("\r\n"),
    "claim_eol_crlf": claim189.count("\r\n"),
    "mat_chain_rows": re.findall(r"assert pf\.N1_BANDS\[(\d+)\]",
                                 blk_mat[blk_mat.find("assert pf.N1_BANDS[138]"):
                                         blk_mat.find("# prior-wave disjointness")]),
}
io.open(r"results\_r892bma_w190_probe_stage1.json", "w", encoding="utf-8").write(
    json.dumps(receipt, indent=1, ensure_ascii=False))
print("probe stage-1 rc0: pf_blk", len(blk_pf), "entry", len(entry189),
      "mat", len(blk_mat), "claim", len(claim189),
      "chain_n", len(receipt["mat_chain_rows"]),
      "chain_tail", receipt["mat_chain_rows"][-3:])
