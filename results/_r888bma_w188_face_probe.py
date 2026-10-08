# -*- coding: utf-8 -*-
"""r888 bm-a W188 freeze pre-TOK empirical probe, stage-1 dump (r773 pit
law leg 1: full string-face inventory BEFORE writing TOK; r776 law:
needles taken from PHYSICAL fragment shapes). Dumps the four W187
faces (pf comment block+row / n1 WAVE_CONFIGS entry / n1 materializer
block / n1 PASS claim) to receipt files. Bloodline: r819/r822/r826/
r830/r834/r843/r845/r849/r852/r863/r867/r869/r874/r878/r881/r882/
r885 face-probe machinery rolled one generation; W188 facts:
  - pre-seat probe results/_r887bma_w188_probe_receipt.json rc0 ADMIT
    (leg0 registry 185 rows tail W187 ordinal 178 / bma_ordinal 104;
    leg1 A 428_404..430_403 staircase FORTY-EIGHTH instance E36 hops=1
    past the registered W187 B band 428_204..428_403; B 430_404..430_603
    own-A mutual exclusion W141 leg2 hops=1, naive 428_404..428_603;
    leg2 conflicts 0; leg3 origin vacancy True; leg4 W189+ projection
    A 430_404..432_403 / B 430_604..430_803, B inside A);
  - seat MSG-2026-10-08-1717-bma-w188-seat published (r887 seat push
    943967370; r565 law: on origin BEFORE this freeze commit; self-ack
    archive landed the r887 window -- same-machine consume, disclosed);
  - registered W187 freeze sha machine-derived = 79c9a567c (git log
    origin/main --grep "W187 FREEZE"); W187 finalize landed r887
    one-pass (results/perpetual_faces/n1_w187_results.json: merged
    K=409,320, ledger head 818,728); W187 sec7/sec8 settle backfill
    landed the r888 window (this window, first leg)."""
import io
import json
import re

PF = r"scripts/perpetual_faces.py"
N1 = r"scripts/perpetual_faces_n1.py"
EO = '"engine_owner": "bm-a"},'

pfsrc = io.open(PF, encoding="utf-8", newline="").read()
n1src = io.open(N1, encoding="utf-8", newline="").read()

# face 1: pf W187 comment block + row
i1 = pfsrc.find("    # W187 (bm-a r885 freeze")
assert i1 > 0, "pf W187 comment block not found"
r1 = pfsrc.find('187: {"a": (426_204', i1)
assert r1 > i1, "pf W187 row not after comment block"
j1 = pfsrc.find(EO, r1) + len(EO)
blk_pf = pfsrc[i1:j1]
io.open(r"results\_r888bma_w188_probe_pf_block.txt", "w", encoding="utf-8", newline="").write(blk_pf)

# face 2: n1 WAVE_CONFIGS W187 entry
k = n1src.find('187: {"batch"')
assert k > 0, "n1 W187 entry not found"
m = n1src.find(EO, k) + len(EO)
entry187 = n1src[k:m]
io.open(r"results\_r888bma_w188_probe_n1_entry.txt", "w", encoding="utf-8", newline="").write(entry187)

# face 3: n1 W187 materializer block
w = n1src.find("# --- W187 materializer face")
t2 = n1src.find("# --- T-141 s2 lane face", w)
assert 0 < w < t2, "materializer anchors missing"
blk_mat = n1src[w:t2]
io.open(r"results\_r888bma_w188_probe_n1_mat.txt", "w", encoding="utf-8", newline="").write(blk_mat)

# face 4: n1 PASS snippet claim (r776 physical-shape law: the W187 claim
# trailing session marker is "r885 bm-a] " -- the r885-emitted freeze
# tool session attribution; the W188 tool rolls it to the new session)
cs = n1src.find('"+ W187 materializer face')
ce = n1src.find('"r885 bm-a] "', cs) + len('"r885 bm-a] "')
assert 0 < cs < ce, "W187 claim anchors missing"
claim187 = n1src[cs:ce]
io.open(r"results\_r888bma_w188_probe_n1_claim.txt", "w", encoding="utf-8", newline="").write(claim187)

receipt = {
    "probe": "r888 W188 freeze pre-TOK string-face inventory (stage-1 dump)",
    "faces": {
        "pf_block_len": len(blk_pf), "n1_entry_len": len(entry187),
        "mat_block_len": len(blk_mat), "claim_len": len(claim187),
    },
    "pf_block_eol_crlf": blk_pf.count("\r\n"),
    "n1_entry_eol_crlf": entry187.count("\r\n"),
    "mat_block_eol_crlf": blk_mat.count("\r\n"),
    "claim_eol_crlf": claim187.count("\r\n"),
    "mat_chain_rows": re.findall(r"assert pf\.N1_BANDS\[(\d+)\]",
                                 blk_mat[blk_mat.find("assert pf.N1_BANDS[138]"):
                                         blk_mat.find("# prior-wave disjointness")]),
}
io.open(r"results\_r888bma_w188_probe_stage1.json", "w", encoding="utf-8").write(
    json.dumps(receipt, indent=1, ensure_ascii=False))
print("probe stage-1 rc0: pf_blk", len(blk_pf), "entry", len(entry187),
      "mat", len(blk_mat), "claim", len(claim187),
      "chain_n", len(receipt["mat_chain_rows"]),
      "chain_tail", receipt["mat_chain_rows"][-3:])
