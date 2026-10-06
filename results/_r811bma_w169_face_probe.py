# -*- coding: utf-8 -*-
"""r811 bm-a W169 freeze pre-TOK empirical probe (r773 pit law leg 1:
full string-face inventory BEFORE writing TOK; r776 law: needles taken
from PHYSICAL fragment shapes). Dumps the four W168 faces (pf comment
block+row / n1 WAVE_CONFIGS entry / n1 materializer block / n1 PASS
claim) to receipt files + counts every needle the W169 freeze uses.
Bloodline: r809 _r809bma_w168_face_probe.py machinery verbatim; W169 facts:
  - band gate results/_r810bma_w169_band_gate.json rc0 ADMIT
    (A 386_604..388_603 staircase TWENTY-EIGHTH instance E36 hops=1 past
    the registered W168 B band; naive 386_404..388_403 refused at its own
    start by the registered W168 B band 386_404..386_603; B 388_604..388_803
    own-A mutual exclusion hops=1, naive 386_604..386_803);
  - pre-seat probe results/_r810bma_w169_probe_receipt.json ADMIT
    (dual-window parity True);
  - seat MSG-2026-10-07-0547-bma-w169-seat published e51edfcbc (r810
    pre-seat push, r565 law: on origin BEFORE this freeze commit;
    seat MSG still in fleet/inbox/ at freeze time = honest deferred state,
    NO fixup needed this window)."""
import io
import json
import re

PF = r"scripts/perpetual_faces.py"
N1 = r"scripts/perpetual_faces_n1.py"
EO = '"engine_owner": "bm-a"},'

pfsrc = io.open(PF, encoding="utf-8", newline="").read()
n1src = io.open(N1, encoding="utf-8", newline="").read()

# face 1: pf W168 comment block + row
i1 = pfsrc.find("    # W168 (bm-a r809 freeze")
assert i1 > 0, "pf W168 comment block not found"
r1 = pfsrc.find('168: {"a": (384_404', i1)
assert r1 > i1, "pf W168 row not after comment block"
j1 = pfsrc.find(EO, r1) + len(EO)
blk_pf = pfsrc[i1:j1]
io.open(r"results\_r811bma_w169_probe_pf_block.txt", "w", encoding="utf-8", newline="").write(blk_pf)

# face 2: n1 WAVE_CONFIGS W168 entry
k = n1src.find('168: {"batch"')
assert k > 0, "n1 W168 entry not found"
m = n1src.find(EO, k) + len(EO)
entry168 = n1src[k:m]
io.open(r"results\_r811bma_w169_probe_n1_entry.txt", "w", encoding="utf-8", newline="").write(entry168)

# face 3: n1 W168 materializer block
w = n1src.find("# --- W168 materializer face")
t2 = n1src.find("# --- T-141 s2 lane face", w)
assert 0 < w < t2, "materializer anchors missing"
blk_mat = n1src[w:t2]
io.open(r"results\_r811bma_w169_probe_n1_mat.txt", "w", encoding="utf-8", newline="").write(blk_mat)

# face 4: n1 PASS snippet claim (r776 physical-shape law: the W168 claim
# trailing session marker is "r809 bm-a] " -- the actual r809 freeze
# session attribution; the W169 tool rolls it to the new session via
# @CLMS@ and discloses here)
cs = n1src.find('"+ W168 materializer face')
ce = n1src.find('"r809 bm-a] "', cs) + len('"r809 bm-a] "')
assert 0 < cs < ce, "W168 claim anchors missing"
claim168 = n1src[cs:ce]
io.open(r"results\_r811bma_w169_probe_n1_claim.txt", "w", encoding="utf-8", newline="").write(claim168)

receipt = {
    "probe": "r811 W169 freeze pre-TOK string-face inventory",
    "faces": {
        "pf_block_len": len(blk_pf), "n1_entry_len": len(entry168),
        "mat_block_len": len(blk_mat), "claim_len": len(claim168),
    },
    "pf_block_eol_crlf": blk_pf.count("\r\n"),
    "n1_entry_eol_crlf": entry168.count("\r\n"),
    "mat_block_eol_crlf": blk_mat.count("\r\n"),
    "claim_eol_crlf": claim168.count("\r\n"),
    "mat_chain_rows": re.findall(r"assert pf\.N1_BANDS\[(\d+)\]",
                                 blk_mat[blk_mat.find("assert pf.N1_BANDS[138]"):
                                         blk_mat.find("# prior-wave disjointness")]),
    "needles": {},
}
needles = [
    # row + entry carriers
    '168: {"a": (384_404, 386_403), "b_exit": (386_404, 386_603),',
    '168: {"batch"',
    # seed-base rows (entry comment face)
    '"a_seed_base": 384_404,',
    '"b_exit_seed_base": 386_404,',
    # dotted bands (W168 geometry)
    "384_204..386_203", "384_204..384_403", "384_404..386_403",
    "384_404..384_603", "386_404..386_603",
    # W169 projection prose inside W168 blocks (physical fragment shape)
    "386_404..388_403", "386_604..386_803",
    "W169 A window; W169 freezer MUST re-derive on the post-W168",
    # identity strings
    "PERPETUAL_N1_W168_PREREG.md", "PERPETUAL-N1-W168", "n1_w168_results.json",
    "n1_w168", "n1w168", "_r806bma", "MSG-2026-10-07-0259", "ceaf58908",
    "772,812", "365,320", "ONE HUNDRED-AND-FIFTY-EIGHTH",
    "engine_owner rows 157", "rows 83 + candidate", "eighty-third",
    "twenty-seventh", "r809", "r806", "r801", "r805", "W168", "W167", "W169",
    "168", "167", "166",
    # set() asserts
    "set(range(384_404, 386_404))", "set(range(386_404, 386_604))",
    "== 384_404 == 384_403 + 1", "== 386_404 == 386_403 + 1",
    "384_403+1", "386_403+1",
    # seat delivery / self-ack prose (honesty faces)
    "move deferred to the W169 finalize window",
    "W168 seat still in",
    # registered-row sha citations
    "bm-a r805 freeze f61835690",
    "W167 row bm-a r805 freeze",
    "f61835690, SINGLE STATE zero seat gap W2..W167 all",
    "f61835690",
    # jump phrases (healed fragment carried via @JB@)
    "own-wave A window reserved jumps to 386_404, first-clean ",
    "jumps to 386_404, first-clean 386_404..386_603 hops=1",
    # freeze-session / prior-finalize / receipt / gate-session composites
    "bm-a r809 freeze", "r809 bm-a freeze", "r809 bm-a] ",
    "W167 finalize landed same-window r806",
    "W167 finalize one-pass bm-a r806", "W167 bm-a r806 one-pass",
    "finalize one-pass bm-a r806",
    "_r806bma_w168_probe_receipt.json", "_r806bma_w168_band_gate.json",
    "r801 gate leg3", "r801 gate", "r806 sec8 succession", "r806 sec8",
    "gate-derived r806", "r806 pre-seat push",
    # seat tokens
    "bma-w168-seat", "MSG-0259",
    # pf / mat jump-phrase fragment shapes
    "jumps to 386_404 -> 386_404..386_603,",
    "386_404 and lands 386_404..386_603",
]
for n in needles:
    receipt["needles"][n] = {
        "pf": pfsrc.count(n), "n1": n1src.count(n),
        "pf_blk": blk_pf.count(n), "entry": entry168.count(n),
        "mat": blk_mat.count(n), "claim": claim168.count(n),
    }
io.open(r"results\_r811bma_w169_face_probe_receipt.json", "w", encoding="utf-8").write(
    json.dumps(receipt, indent=1, ensure_ascii=False))
print("probe rc0: pf_blk", len(blk_pf), "entry", len(entry168),
      "mat", len(blk_mat), "claim", len(claim168),
      "chain_n", len(receipt["mat_chain_rows"]),
      "chain_tail", receipt["mat_chain_rows"][-3:])
