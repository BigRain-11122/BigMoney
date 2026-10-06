# -*- coding: utf-8 -*-
"""r809 bm-a W168 freeze pre-TOK empirical probe (r773 pit law leg 1:
full string-face inventory BEFORE writing TOK; r776 law: needles taken
from PHYSICAL fragment shapes). Dumps the four W167 faces (pf comment
block+row / n1 WAVE_CONFIGS entry / n1 materializer block / n1 PASS
claim) to receipt files + counts every needle the W168 freeze uses.
Bloodline: r803 _r803bma_w167_face_probe.py machinery verbatim; W168 facts:
  - band gate results/_r806bma_w168_band_gate.json rc0 ADMIT
    (A 384_404..386_403 staircase TWENTY-SEVENTH instance E36 hops=1 past
    the registered W167 B band; naive 384_204..386_203 refused at its own
    start by the registered W167 B band 384_204..384_403; B 386_404..386_603
    own-A mutual exclusion hops=1, naive 384_404..384_603);
  - pre-seat probe results/_r806bma_w168_probe_receipt.json ADMIT
    (dual-window parity True);
  - seat MSG-2026-10-07-0259-bma-w168-seat published ceaf58908 (r806
    pre-seat push, r565 law: on origin BEFORE this freeze commit)."""
import io
import json
import re

PF = r"scripts/perpetual_faces.py"
N1 = r"scripts/perpetual_faces_n1.py"
EO = '"engine_owner": "bm-a"},'

pfsrc = io.open(PF, encoding="utf-8", newline="").read()
n1src = io.open(N1, encoding="utf-8", newline="").read()

# face 1: pf W167 comment block + row
i1 = pfsrc.find("    # W167 (bm-a r805 freeze")
assert i1 > 0, "pf W167 comment block not found"
r1 = pfsrc.find('167: {"a": (382_204', i1)
assert r1 > i1, "pf W167 row not after comment block"
j1 = pfsrc.find(EO, r1) + len(EO)
blk_pf = pfsrc[i1:j1]
io.open(r"results\_r809bma_w168_probe_pf_block.txt", "w", encoding="utf-8", newline="").write(blk_pf)

# face 2: n1 WAVE_CONFIGS W167 entry
k = n1src.find('167: {"batch"')
assert k > 0, "n1 W167 entry not found"
m = n1src.find(EO, k) + len(EO)
entry167 = n1src[k:m]
io.open(r"results\_r809bma_w168_probe_n1_entry.txt", "w", encoding="utf-8", newline="").write(entry167)

# face 3: n1 W167 materializer block
w = n1src.find("# --- W167 materializer face")
t2 = n1src.find("# --- T-141 s2 lane face", w)
assert 0 < w < t2, "materializer anchors missing"
blk_mat = n1src[w:t2]
io.open(r"results\_r809bma_w168_probe_n1_mat.txt", "w", encoding="utf-8", newline="").write(blk_mat)

# face 4: n1 PASS snippet claim (r776 physical-shape law: the W167 claim
# trailing session marker is "r805 bm-a] " -- correct attribution this
# generation (r805 was the actual W167 freeze session; the r803-probe
# disclosure was healed via @CLMS@); the W168 tool rolls it to the new
# session via @CLMS@ and discloses here)
cs = n1src.find('"+ W167 materializer face')
ce = n1src.find('"r805 bm-a] "', cs) + len('"r805 bm-a] "')
assert 0 < cs < ce, "W167 claim anchors missing"
claim167 = n1src[cs:ce]
io.open(r"results\_r809bma_w168_probe_n1_claim.txt", "w", encoding="utf-8", newline="").write(claim167)

receipt = {
    "probe": "r809 W168 freeze pre-TOK string-face inventory",
    "faces": {
        "pf_block_len": len(blk_pf), "n1_entry_len": len(entry167),
        "mat_block_len": len(blk_mat), "claim_len": len(claim167),
    },
    "pf_block_eol_crlf": blk_pf.count("\r\n"),
    "n1_entry_eol_crlf": entry167.count("\r\n"),
    "mat_block_eol_crlf": blk_mat.count("\r\n"),
    "claim_eol_crlf": claim167.count("\r\n"),
    "mat_chain_rows": re.findall(r"assert pf\.N1_BANDS\[(\d+)\]",
                                 blk_mat[blk_mat.find("assert pf.N1_BANDS[138]"):
                                         blk_mat.find("# prior-wave disjointness")]),
    "needles": {},
}
needles = [
    # row + entry carriers
    '167: {"a": (382_204, 384_203), "b_exit": (384_204, 384_403),',
    '167: {"batch"',
    # seed-base rows (entry comment face)
    '"a_seed_base": 382_204,',
    '"b_exit_seed_base": 384_204,',
    # dotted bands (W167 geometry)
    "382_004..384_003", "382_004..382_203", "382_204..384_203",
    "382_204..382_403", "384_204..384_403",
    # W168 projection prose inside W167 blocks (physical fragment shape)
    "384_204..386_203", "384_404..384_603",
    "W168 A window; W168 freezer MUST re-derive on the post-W167",
    # identity strings
    "PERPETUAL_N1_W167_PREREG.md", "PERPETUAL-N1-W167", "n1_w167_results.json",
    "n1_w167", "n1w167", "_r801bma", "MSG-2026-10-07-0056", "982424c5f",
    "770,612", "363,120", "ONE HUNDRED-AND-FIFTY-SEVENTH",
    "engine_owner rows 156", "rows 82 + candidate", "eighty-second",
    "twenty-sixth", "r805", "r801", "r799", "W167", "W166", "167", "166",
    # set() asserts
    "set(range(382_204, 384_204))", "set(range(384_204, 384_404))",
    "== 382_204 == 382_203 + 1", "== 384_204 == 384_203 + 1",
    "382_203+1", "384_203+1",
    # seat delivery / self-ack prose (honesty faces)
    "move deferred to the W168 finalize window",
    "W167 seat still in",
    # registered-row sha citations
    "bm-a r799 freeze c2d6c5e14",
    "W166 row bm-a r799 freeze",
    "c2d6c5e14, SINGLE STATE zero seat gap W2..W166 all",
    # jump phrases (healed fragment carried via @JB@)
    "own-wave A window reserved jumps to 384_204, first-clean ",
    "jumps to 384_204, first-clean 384_204..384_403 hops=1",
    # freeze-session / prior-finalize / receipt / gate-session composites
    "bm-a r805 freeze", "r805 bm-a freeze",
    "W166 finalize landed same-window r799",
    "W166 finalize one-pass bm-a r799", "W166 bm-a r799 one-pass",
    "_r801bma_w167_probe_receipt.json", "_r801bma_w167_band_gate.json",
    "r797 gate leg3", "r797 gate", "r799 sec8 succession", "r799 sec8",
    "gate-derived r801", "r801 pre-seat push",
    # seat tokens
    "bma-w167-seat", "MSG-0056",
    # pf / mat jump-phrase fragment shapes
    "jumps to 384_204 -> 384_204..384_403,",
    "384_204 and lands 384_204..384_403",
]
for n in needles:
    receipt["needles"][n] = {
        "pf": pfsrc.count(n), "n1": n1src.count(n),
        "pf_blk": blk_pf.count(n), "entry": entry167.count(n),
        "mat": blk_mat.count(n), "claim": claim167.count(n),
    }
io.open(r"results\_r809bma_w168_face_probe_receipt.json", "w", encoding="utf-8").write(
    json.dumps(receipt, indent=1, ensure_ascii=False))
print("probe rc0: pf_blk", len(blk_pf), "entry", len(entry167),
      "mat", len(blk_mat), "claim", len(claim167),
      "chain", receipt["mat_chain_rows"][:3], "..", receipt["mat_chain_rows"][-3:])
