# -*- coding: utf-8 -*-
"""r890 bm-a W189 freeze pre-TOK empirical probe, stage-1 dump (r773 pit
law leg 1: full string-face inventory BEFORE writing TOK; r776 law:
needles taken from PHYSICAL fragment shapes). Dumps the four W188
faces (pf comment block+row / n1 WAVE_CONFIGS entry / n1 materializer
block / n1 PASS claim) to receipt files. Bloodline: r819/r822/r826/
r830/r834/r843/r845/r849/r852/r863/r867/r869/r874/r878/r881/r882/
r885/r888 face-probe machinery rolled one generation; W189 facts:
  - pre-seat probe results/_r888bma_w189_probe_receipt.json rc0 ADMIT
    (leg0 registry 186 rows tail W188 ordinal 179 / bma_ordinal 105;
    leg1 A 430_604..432_603 staircase FORTY-NINTH instance E36 hops=1
    past the registered W188 B band 430_404..430_603; B 432_604..432_803
    own-A mutual exclusion W141 leg2 hops=1, naive 430_604..430_803;
    leg2 conflicts 0; leg3 origin vacancy True; leg4 W190+ projection
    A 432_604..434_603 / B 432_804..433_003, B inside A);
  - seat MSG-2026-10-08-1815-bma-w189-seat published (r888 seat push
    744de26ef; r565 law: on origin BEFORE this freeze commit);
  - registered W188 freeze sha machine-derived = b66117659 (five-face
    freeze commit r888 window); W188 finalize landed r889 one-pass
    (results/perpetual_faces/n1_w188_results.json: merged K=411,520,
    ledger head 820,928); W188 sec7/sec8 settle backfill landed the
    r890 window (this window, first leg)."""
import io
import json
import re

PF = r"scripts/perpetual_faces.py"
N1 = r"scripts/perpetual_faces_n1.py"
EO = '"engine_owner": "bm-a"},'

pfsrc = io.open(PF, encoding="utf-8", newline="").read()
n1src = io.open(N1, encoding="utf-8", newline="").read()

# face 1: pf W188 comment block + row
i1 = pfsrc.find("    # W188 (bm-a r888 freeze")
assert i1 > 0, "pf W188 comment block not found"
r1 = pfsrc.find('188: {"a": (428_404', i1)
assert r1 > i1, "pf W188 row not after comment block"
j1 = pfsrc.find(EO, r1) + len(EO)
blk_pf = pfsrc[i1:j1]
io.open(r"results\_r890bma_w189_probe_pf_block.txt", "w", encoding="utf-8", newline="").write(blk_pf)

# face 2: n1 WAVE_CONFIGS W188 entry
k = n1src.find('188: {"batch"')
assert k > 0, "n1 W188 entry not found"
m = n1src.find(EO, k) + len(EO)
entry188 = n1src[k:m]
io.open(r"results\_r890bma_w189_probe_n1_entry.txt", "w", encoding="utf-8", newline="").write(entry188)

# face 3: n1 W188 materializer block
w = n1src.find("# --- W188 materializer face")
t2 = n1src.find("# --- T-141 s2 lane face", w)
assert 0 < w < t2, "materializer anchors missing"
blk_mat = n1src[w:t2]
io.open(r"results\_r890bma_w189_probe_n1_mat.txt", "w", encoding="utf-8", newline="").write(blk_mat)

# face 4: n1 PASS snippet claim (r776 physical-shape law: the W188 claim
# trailing session marker is "r888 bm-a] " -- the r888-emitted freeze
# tool session attribution; the W189 tool rolls it to the new session)
cs = n1src.find('"+ W188 materializer face')
ce = n1src.find('"r888 bm-a] "', cs) + len('"r888 bm-a] "')
assert 0 < cs < ce, "W188 claim anchors missing"
claim188 = n1src[cs:ce]
io.open(r"results\_r890bma_w189_probe_n1_claim.txt", "w", encoding="utf-8", newline="").write(claim188)

receipt = {
    "probe": "r890 W189 freeze pre-TOK string-face inventory (stage-1 dump)",
    "faces": {
        "pf_block_len": len(blk_pf), "n1_entry_len": len(entry188),
        "mat_block_len": len(blk_mat), "claim_len": len(claim188),
    },
    "pf_block_eol_crlf": blk_pf.count("\r\n"),
    "n1_entry_eol_crlf": entry188.count("\r\n"),
    "mat_block_eol_crlf": blk_mat.count("\r\n"),
    "claim_eol_crlf": claim188.count("\r\n"),
    "mat_chain_rows": re.findall(r"assert pf\.N1_BANDS\[(\d+)\]",
                                 blk_mat[blk_mat.find("assert pf.N1_BANDS[138]"):
                                         blk_mat.find("# prior-wave disjointness")]),
}
io.open(r"results\_r890bma_w189_probe_stage1.json", "w", encoding="utf-8").write(
    json.dumps(receipt, indent=1, ensure_ascii=False))
print("probe stage-1 rc0: pf_blk", len(blk_pf), "entry", len(entry188),
      "mat", len(blk_mat), "claim", len(claim188),
      "chain_n", len(receipt["mat_chain_rows"]),
      "chain_tail", receipt["mat_chain_rows"][-3:])
