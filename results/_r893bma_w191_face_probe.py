# -*- coding: utf-8 -*-
"""r893 bm-a W191 freeze pre-TOK empirical probe, stage-1 dump (r773 pit
law leg 1: full string-face inventory BEFORE writing TOK; r776 law:
needles taken from PHYSICAL fragment shapes). Dumps the four W190
faces (pf comment block+row / n1 WAVE_CONFIGS entry / n1 materializer
block / n1 PASS claim) to receipt files. Bloodline: r819/r822/r826/
r830/r834/r843/r845/r849/r852/r863/r867/r869/r874/r878/r881/r882/
r885/r888/r890/r892 face-probe machinery rolled one generation; W191
facts:
  - pre-seat probe results/_r892bma_w191_probe_receipt.json rc0 ADMIT
    (leg0 registry 188 rows tail W190 owner_rows 180 / bma_rows 106,
    ordinal 181 / bma_ordinal 107; w190 ledger head 825,328 registered
    burn-complete finalize-LANDED same-window r892-continuation
    one-pass; leg1 A 435_004..437_003 staircase FIFTY-FIRST instance
    E36 hops=1 past the registered W190 B band 434_804..435_003; B
    437_004..437_203 own-A mutual exclusion W141 leg2 hops=1, naive
    435_004..435_203; leg2 conflicts 0; leg3 origin vacancy True;
    leg4 W192+ projection A 437_004..439_003 / B 437_204..437_403,
    B inside A);
  - seat MSG-2026-10-08-2130-bma-w191-seat published on origin at
    1c28dd21d (r892 seat push 21:19; r565 law: on origin BEFORE this
    freeze commit); self-ack archive landed the r892 closeout window
    (adeaab565 21:49:57, cross-window consume disclosed);
  - registered W190 five-face registration sha machine-derived =
    0cce3c47e (content-anchored git log -S '190: {"a": (432_804' --
    scripts/perpetual_faces.py, r812 path-derived precedent); W190
    finalize landed r892 one-pass (results/perpetual_faces/
    n1_w190_results.json: merged K=415,920, ledger head 825,328);
    W190 sec7/sec8 settle backfill landed the r893 window (this
    window, first leg 6cc28b65b);
  - per-wave prereg research/PERPETUAL_N1_W191_PREREG.md built r893
    (buildgen r892-bloodline; DRY 50/50; frozen ea42ee94a r893; on
    origin, verified live below)."""
import io
import json
import re

PF = r"scripts/perpetual_faces.py"
N1 = r"scripts/perpetual_faces_n1.py"
EO = '"engine_owner": "bm-a"},'

pfsrc = io.open(PF, encoding="utf-8", newline="").read()
n1src = io.open(N1, encoding="utf-8", newline="").read()

# face 1: pf W190 comment block + row
i1 = pfsrc.find("    # W190 (bm-a r892 freeze")
assert i1 > 0, "pf W190 comment block not found"
r1 = pfsrc.find('190: {"a": (432_804', i1)
assert r1 > i1, "pf W190 row not after comment block"
j1 = pfsrc.find(EO, r1) + len(EO)
blk_pf = pfsrc[i1:j1]
io.open(r"results\_r893bma_w191_probe_pf_block.txt", "w", encoding="utf-8", newline="").write(blk_pf)

# face 2: n1 WAVE_CONFIGS W190 entry
k = n1src.find('190: {"batch"')
assert k > 0, "n1 W190 entry not found"
m = n1src.find(EO, k) + len(EO)
entry190 = n1src[k:m]
io.open(r"results\_r893bma_w191_probe_n1_entry.txt", "w", encoding="utf-8", newline="").write(entry190)

# face 3: n1 W190 materializer block
w = n1src.find("# --- W190 materializer face")
t2 = n1src.find("# --- T-141 s2 lane face", w)
assert 0 < w < t2, "materializer anchors missing"
blk_mat = n1src[w:t2]
io.open(r"results\_r893bma_w191_probe_n1_mat.txt", "w", encoding="utf-8", newline="").write(blk_mat)

# face 4: n1 PASS snippet claim (r776 physical-shape law: the W190 claim
# trailing session marker is "r892 bm-a] " -- the r892-emitted freeze
# tool session attribution; the W191 tool rolls it to the new session)
cs = n1src.find('"+ W190 materializer face')
ce = n1src.find('"r892 bm-a] "', cs) + len('"r892 bm-a] "')
assert 0 < cs < ce, "W190 claim anchors missing"
claim190 = n1src[cs:ce]
io.open(r"results\_r893bma_w191_probe_n1_claim.txt", "w", encoding="utf-8", newline="").write(claim190)

receipt = {
    "probe": "r893 W191 freeze pre-TOK string-face inventory (stage-1 dump)",
    "faces": {
        "pf_block_len": len(blk_pf), "n1_entry_len": len(entry190),
        "mat_block_len": len(blk_mat), "claim_len": len(claim190),
    },
    "pf_block_eol_crlf": blk_pf.count("\r\n"),
    "n1_entry_eol_crlf": entry190.count("\r\n"),
    "mat_block_eol_crlf": blk_mat.count("\r\n"),
    "claim_eol_crlf": claim190.count("\r\n"),
    "mat_chain_rows": re.findall(r"assert pf\.N1_BANDS\[(\d+)\]",
                                 blk_mat[blk_mat.find("assert pf.N1_BANDS[138]"):
                                         blk_mat.find("# prior-wave disjointness")]),
}
io.open(r"results\_r893bma_w191_probe_stage1.json", "w", encoding="utf-8").write(
    json.dumps(receipt, indent=1, ensure_ascii=False))
print("probe stage-1 rc0: pf_blk", len(blk_pf), "entry", len(entry190),
      "mat", len(blk_mat), "claim", len(claim190),
      "chain_n", len(receipt["mat_chain_rows"]),
      "chain_tail", receipt["mat_chain_rows"][-3:])
