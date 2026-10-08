# -*- coding: utf-8 -*-
"""r878 bm-a W185 freeze pre-TOK empirical probe, stage-1 dump (r773 pit
law leg 1: full string-face inventory BEFORE writing TOK; r776 law:
needles taken from PHYSICAL fragment shapes). Dumps the four W184
faces (pf comment block+row / n1 WAVE_CONFIGS entry / n1 materializer
block / n1 PASS claim) to receipt files. Bloodline: r819/r822/r826/
r830/r834/r843/r845/r849/r852/r863/r867/r869/r874 face-probe machinery
rolled one generation; W185 facts:
  - pre-seat probe results/_r875bma_w185_probe_receipt.json rc0 ADMIT
    (leg0 registry 182 rows tail W184 ordinal 175 / bma_ordinal 101;
    leg1 A 421_804..423_803 staircase FORTY-FIFTH instance E36 hops=1
    past the registered W184 B band 421_604..421_803; B 423_804..424_003
    own-A mutual exclusion W141 leg2 hops=1, naive 421_804..422_003;
    leg2 conflicts 0; leg3 origin vacancy True; leg4 W186+ projection
    A 423_804..425_803 / B 424_004..424_203, B inside A);
  - seat MSG-2026-10-08-1032-bma-w185-seat published (r875 pre-seat
    push; r565 law: on origin BEFORE this freeze commit);
  - registered W184 freeze sha machine-derived = 7e791a87f (git log
    origin/main --grep "W184 FREEZE"); W184 finalize landed r875
    one-pass SAME-window (results/perpetual_faces/
    n1_w184_results.json: merged K=402,720, ledger head 812,128);
    W184 sec7/sec8 settle backfill landed the r875 SAME window;
  - W185 prereg freeze-candidate landed r877 commit e9a70187b
    (21,522B, banned gate ADMIT at r877 build)."""
import io
import json
import re

PF = r"scripts/perpetual_faces.py"
N1 = r"scripts/perpetual_faces_n1.py"
EO = '"engine_owner": "bm-a"},'

pfsrc = io.open(PF, encoding="utf-8", newline="").read()
n1src = io.open(N1, encoding="utf-8", newline="").read()

# face 1: pf W184 comment block + row
i1 = pfsrc.find("    # W184 (bm-a r874 freeze")
assert i1 > 0, "pf W184 comment block not found"
r1 = pfsrc.find('184: {"a": (419_604', i1)
assert r1 > i1, "pf W184 row not after comment block"
j1 = pfsrc.find(EO, r1) + len(EO)
blk_pf = pfsrc[i1:j1]
io.open(r"results\_r878bma_w185_probe_pf_block.txt", "w", encoding="utf-8", newline="").write(blk_pf)

# face 2: n1 WAVE_CONFIGS W184 entry
k = n1src.find('184: {"batch"')
assert k > 0, "n1 W184 entry not found"
m = n1src.find(EO, k) + len(EO)
entry184 = n1src[k:m]
io.open(r"results\_r878bma_w185_probe_n1_entry.txt", "w", encoding="utf-8", newline="").write(entry184)

# face 3: n1 W184 materializer block
w = n1src.find("# --- W184 materializer face")
t2 = n1src.find("# --- T-141 s2 lane face", w)
assert 0 < w < t2, "materializer anchors missing"
blk_mat = n1src[w:t2]
io.open(r"results\_r878bma_w185_probe_n1_mat.txt", "w", encoding="utf-8", newline="").write(blk_mat)

# face 4: n1 PASS snippet claim (r776 physical-shape law: the W184 claim
# trailing session marker is "r874 bm-a] " -- the actual r874 freeze
# session attribution; the W185 tool rolls it to the new session)
cs = n1src.find('"+ W184 materializer face')
ce = n1src.find('"r874 bm-a] "', cs) + len('"r874 bm-a] "')
assert 0 < cs < ce, "W184 claim anchors missing"
claim184 = n1src[cs:ce]
io.open(r"results\_r878bma_w185_probe_n1_claim.txt", "w", encoding="utf-8", newline="").write(claim184)

receipt = {
    "probe": "r878 W185 freeze pre-TOK string-face inventory (stage-1 dump)",
    "faces": {
        "pf_block_len": len(blk_pf), "n1_entry_len": len(entry184),
        "mat_block_len": len(blk_mat), "claim_len": len(claim184),
    },
    "pf_block_eol_crlf": blk_pf.count("\r\n"),
    "n1_entry_eol_crlf": entry184.count("\r\n"),
    "mat_block_eol_crlf": blk_mat.count("\r\n"),
    "claim_eol_crlf": claim184.count("\r\n"),
    "mat_chain_rows": re.findall(r"assert pf\.N1_BANDS\[(\d+)\]",
                                 blk_mat[blk_mat.find("assert pf.N1_BANDS[138]"):
                                         blk_mat.find("# prior-wave disjointness")]),
}
io.open(r"results\_r878bma_w185_probe_stage1.json", "w", encoding="utf-8").write(
    json.dumps(receipt, indent=1, ensure_ascii=False))
print("probe stage-1 rc0: pf_blk", len(blk_pf), "entry", len(entry184),
      "mat", len(blk_mat), "claim", len(claim184),
      "chain_n", len(receipt["mat_chain_rows"]),
      "chain_tail", receipt["mat_chain_rows"][-3:])
