# -*- coding: utf-8 -*-
"""r885 bm-a W187 freeze pre-TOK empirical probe, stage-1 dump (r773 pit
law leg 1: full string-face inventory BEFORE writing TOK; r776 law:
needles taken from PHYSICAL fragment shapes). Dumps the four W186
faces (pf comment block+row / n1 WAVE_CONFIGS entry / n1 materializer
block / n1 PASS claim) to receipt files. Bloodline: r819/r822/r826/
r830/r834/r843/r845/r849/r852/r863/r867/r869/r874/r878/r881/r882
face-probe machinery rolled one generation; W187 facts:
  - pre-seat probe results/_r885bma_w187_probe_receipt.json rc0 ADMIT
    (leg0 registry 184 rows tail W186 ordinal 177 / bma_ordinal 103;
    leg1 A 426_204..428_203 staircase FORTY-SEVENTH instance E36 hops=1
    past the registered W186 B band 426_004..426_203; B 428_204..428_403
    own-A mutual exclusion W141 leg2 hops=1, naive 426_204..426_403;
    leg2 conflicts 0; leg3 origin vacancy True; leg4 W188+ projection
    A 428_204..430_203 / B 428_404..428_603, B inside A);
  - seat MSG-2026-10-08-1626-bma-w187-seat published (r885 pre-seat
    push d176af598; r565 law: on origin BEFORE this freeze commit;
    self-ack archive landed the r885 same window -- same-machine
    consume, disclosed);
  - registered W186 freeze sha machine-derived = git log origin/main
    --grep "W186 FREEZE"; W186 finalize landed r884 one-pass (results/
    perpetual_faces/n1_w186_results.json: merged K=407,120, ledger
    head 816,528); W186 sec7/sec8 settle backfill landed the r884
    SAME window as the finalize."""
import io
import json
import re

PF = r"scripts/perpetual_faces.py"
N1 = r"scripts/perpetual_faces_n1.py"
EO = '"engine_owner": "bm-a"},'

pfsrc = io.open(PF, encoding="utf-8", newline="").read()
n1src = io.open(N1, encoding="utf-8", newline="").read()

# face 1: pf W186 comment block + row
i1 = pfsrc.find("    # W186 (bm-a r882 freeze")
assert i1 > 0, "pf W186 comment block not found"
r1 = pfsrc.find('186: {"a": (424_004', i1)
assert r1 > i1, "pf W186 row not after comment block"
j1 = pfsrc.find(EO, r1) + len(EO)
blk_pf = pfsrc[i1:j1]
io.open(r"results\_r885bma_w187_probe_pf_block.txt", "w", encoding="utf-8", newline="").write(blk_pf)

# face 2: n1 WAVE_CONFIGS W186 entry
k = n1src.find('186: {"batch"')
assert k > 0, "n1 W186 entry not found"
m = n1src.find(EO, k) + len(EO)
entry186 = n1src[k:m]
io.open(r"results\_r885bma_w187_probe_n1_entry.txt", "w", encoding="utf-8", newline="").write(entry186)

# face 3: n1 W186 materializer block
w = n1src.find("# --- W186 materializer face")
t2 = n1src.find("# --- T-141 s2 lane face", w)
assert 0 < w < t2, "materializer anchors missing"
blk_mat = n1src[w:t2]
io.open(r"results\_r885bma_w187_probe_n1_mat.txt", "w", encoding="utf-8", newline="").write(blk_mat)

# face 4: n1 PASS snippet claim (r776 physical-shape law: the W186 claim
# trailing session marker is "r882 bm-a] " -- the actual r882 freeze
# session attribution; the W187 tool rolls it to the new session)
cs = n1src.find('"+ W186 materializer face')
ce = n1src.find('"r882 bm-a] "', cs) + len('"r882 bm-a] "')
assert 0 < cs < ce, "W186 claim anchors missing"
claim186 = n1src[cs:ce]
io.open(r"results\_r885bma_w187_probe_n1_claim.txt", "w", encoding="utf-8", newline="").write(claim186)

receipt = {
    "probe": "r885 W187 freeze pre-TOK string-face inventory (stage-1 dump)",
    "faces": {
        "pf_block_len": len(blk_pf), "n1_entry_len": len(entry186),
        "mat_block_len": len(blk_mat), "claim_len": len(claim186),
    },
    "pf_block_eol_crlf": blk_pf.count("\r\n"),
    "n1_entry_eol_crlf": entry186.count("\r\n"),
    "mat_block_eol_crlf": blk_mat.count("\r\n"),
    "claim_eol_crlf": claim186.count("\r\n"),
    "mat_chain_rows": re.findall(r"assert pf\.N1_BANDS\[(\d+)\]",
                                 blk_mat[blk_mat.find("assert pf.N1_BANDS[138]"):
                                         blk_mat.find("# prior-wave disjointness")]),
}
io.open(r"results\_r885bma_w187_probe_stage1.json", "w", encoding="utf-8").write(
    json.dumps(receipt, indent=1, ensure_ascii=False))
print("probe stage-1 rc0: pf_blk", len(blk_pf), "entry", len(entry186),
      "mat", len(blk_mat), "claim", len(claim186),
      "chain_n", len(receipt["mat_chain_rows"]),
      "chain_tail", receipt["mat_chain_rows"][-3:])
