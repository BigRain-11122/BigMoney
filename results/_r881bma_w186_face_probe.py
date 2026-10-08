# -*- coding: utf-8 -*-
"""r881 bm-a W186 freeze pre-TOK empirical probe, stage-1 dump (r773 pit
law leg 1: full string-face inventory BEFORE writing TOK; r776 law:
needles taken from PHYSICAL fragment shapes). Dumps the four W185
faces (pf comment block+row / n1 WAVE_CONFIGS entry / n1 materializer
block / n1 PASS claim) to receipt files. Bloodline: r819/r822/r826/
r830/r834/r843/r845/r849/r852/r863/r867/r869/r874/r878 face-probe
machinery rolled one generation; W186 facts:
  - pre-seat probe results/_r880bma_w186_probe_receipt.json rc0 ADMIT
    (leg0 registry 183 rows tail W185 ordinal 176 / bma_ordinal 102;
    leg1 A 424_004..426_003 staircase FORTY-SIXTH instance E36 hops=1
    past the registered W185 B band 423_804..424_003; B 426_004..426_203
    own-A mutual exclusion W141 leg2 hops=1, naive 424_004..424_203;
    leg2 conflicts 0; leg3 origin vacancy True; leg4 W187+ projection
    A 426_004..428_003 / B 426_204..426_403, B inside A);
  - seat MSG-2026-10-08-1354-bma-w186-seat published (r880 pre-seat
    push dd362c690; r565 law: on origin BEFORE this freeze commit;
    self-ack archive landed the r880 closeout window 4c0cfabc3 --
    same-window as the push, disclosed);
  - registered W185 freeze sha machine-derived = beb4b5abd (git log
    origin/main --grep "W185 FREEZE"); W185 finalize landed r879
    adopted-window one-pass (results/perpetual_faces/
    n1_w185_results.json: merged K=404,920, ledger head 814,328);
    W185 sec7/sec8 settle backfill landed the r879 SAME window as
    the finalize;
  - W186 prereg freeze-candidate landed r881 commit baa5b36ea
    (21,605B, banned gate ADMIT at r881 build; two-face src
    disclosure in the r881 buildgen)."""
import io
import json
import re

PF = r"scripts/perpetual_faces.py"
N1 = r"scripts/perpetual_faces_n1.py"
EO = '"engine_owner": "bm-a"},'

pfsrc = io.open(PF, encoding="utf-8", newline="").read()
n1src = io.open(N1, encoding="utf-8", newline="").read()

# face 1: pf W185 comment block + row
i1 = pfsrc.find("    # W185 (bm-a r878 freeze")
assert i1 > 0, "pf W185 comment block not found"
r1 = pfsrc.find('185: {"a": (421_804', i1)
assert r1 > i1, "pf W185 row not after comment block"
j1 = pfsrc.find(EO, r1) + len(EO)
blk_pf = pfsrc[i1:j1]
io.open(r"results\_r881bma_w186_probe_pf_block.txt", "w", encoding="utf-8", newline="").write(blk_pf)

# face 2: n1 WAVE_CONFIGS W185 entry
k = n1src.find('185: {"batch"')
assert k > 0, "n1 W185 entry not found"
m = n1src.find(EO, k) + len(EO)
entry185 = n1src[k:m]
io.open(r"results\_r881bma_w186_probe_n1_entry.txt", "w", encoding="utf-8", newline="").write(entry185)

# face 3: n1 W185 materializer block
w = n1src.find("# --- W185 materializer face")
t2 = n1src.find("# --- T-141 s2 lane face", w)
assert 0 < w < t2, "materializer anchors missing"
blk_mat = n1src[w:t2]
io.open(r"results\_r881bma_w186_probe_n1_mat.txt", "w", encoding="utf-8", newline="").write(blk_mat)

# face 4: n1 PASS snippet claim (r776 physical-shape law: the W185 claim
# trailing session marker is "r878 bm-a] " -- the actual r878 freeze
# session attribution; the W186 tool rolls it to the new session)
cs = n1src.find('"+ W185 materializer face')
ce = n1src.find('"r878 bm-a] "', cs) + len('"r878 bm-a] "')
assert 0 < cs < ce, "W185 claim anchors missing"
claim185 = n1src[cs:ce]
io.open(r"results\_r881bma_w186_probe_n1_claim.txt", "w", encoding="utf-8", newline="").write(claim185)

receipt = {
    "probe": "r881 W186 freeze pre-TOK string-face inventory (stage-1 dump)",
    "faces": {
        "pf_block_len": len(blk_pf), "n1_entry_len": len(entry185),
        "mat_block_len": len(blk_mat), "claim_len": len(claim185),
    },
    "pf_block_eol_crlf": blk_pf.count("\r\n"),
    "n1_entry_eol_crlf": entry185.count("\r\n"),
    "mat_block_eol_crlf": blk_mat.count("\r\n"),
    "claim_eol_crlf": claim185.count("\r\n"),
    "mat_chain_rows": re.findall(r"assert pf\.N1_BANDS\[(\d+)\]",
                                 blk_mat[blk_mat.find("assert pf.N1_BANDS[138]"):
                                         blk_mat.find("# prior-wave disjointness")]),
}
io.open(r"results\_r881bma_w186_probe_stage1.json", "w", encoding="utf-8").write(
    json.dumps(receipt, indent=1, ensure_ascii=False))
print("probe stage-1 rc0: pf_blk", len(blk_pf), "entry", len(entry185),
      "mat", len(blk_mat), "claim", len(claim185),
      "chain_n", len(receipt["mat_chain_rows"]),
      "chain_tail", receipt["mat_chain_rows"][-3:])
