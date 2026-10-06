# -*- coding: utf-8 -*-
"""r803 bm-a W167 freeze pre-TOK empirical probe (r773 pit law leg 1:
full string-face inventory BEFORE writing TOK; r776 law: needles taken
from PHYSICAL fragment shapes). Dumps the four W166 faces (pf comment
block+row / n1 WAVE_CONFIGS entry / n1 materializer block / n1 PASS
claim) to receipt files + counts every needle the freeze script uses.
Bloodline: r799 _r799bma_w166_face_probe.py machinery verbatim; W167 facts:
  - band gate results/_r801bma_w167_band_gate.json rc0 ADMIT
    (A 382_204..384_203 staircase TWENTY-SIXTH instance E36 hops=1 past
    the W166 B band; naive 382_004..384_003 refused at its own start by
    the registered W166 B band 382_004..382_203; B 384_204..384_403
    own-A mutual exclusion hops=1, naive 382_204..382_403);
  - pre-seat probe results/_r801bma_w167_probe_receipt.json ADMIT;
  - seat MSG-2026-10-07-0056-bma-w167-seat published 982424c5f (r801
    pre-seat push, r565 law: on origin BEFORE this freeze commit)."""
import io
import json
import re

PF = r"scripts/perpetual_faces.py"
N1 = r"scripts/perpetual_faces_n1.py"
EO = '"engine_owner": "bm-a"},'

pfsrc = io.open(PF, encoding="utf-8", newline="").read()
n1src = io.open(N1, encoding="utf-8", newline="").read()

# face 1: pf W166 comment block + row
i1 = pfsrc.find("    # W166 (bm-a r799 freeze")
assert i1 > 0, "pf W166 comment block not found"
r1 = pfsrc.find('166: {"a": (380_004', i1)
assert r1 > i1, "pf W166 row not after comment block"
j1 = pfsrc.find(EO, r1) + len(EO)
blk_pf = pfsrc[i1:j1]
io.open(r"results\_r803bma_w167_probe_pf_block.txt", "w", encoding="utf-8", newline="").write(blk_pf)

# face 2: n1 WAVE_CONFIGS W166 entry
k = n1src.find('166: {"batch"')
assert k > 0, "n1 W166 entry not found"
m = n1src.find(EO, k) + len(EO)
entry166 = n1src[k:m]
io.open(r"results\_r803bma_w167_probe_n1_entry.txt", "w", encoding="utf-8", newline="").write(entry166)

# face 3: n1 W166 materializer block
w = n1src.find("# --- W166 materializer face")
t2 = n1src.find("# --- T-141 s2 lane face", w)
assert 0 < w < t2, "materializer anchors missing"
blk_mat = n1src[w:t2]
io.open(r"results\_r803bma_w167_probe_n1_mat.txt", "w", encoding="utf-8", newline="").write(blk_mat)

# face 4: n1 PASS snippet claim (r776 physical-shape law: the W166 claim
# trailing session marker leaked as "r795 bm-a] " -- the r799 freeze TOK
# lacked that needle; frozen face stays (r307), the W167 tool fixes the
# attribution in the NEW claim via @CLMS@ and discloses here)
cs = n1src.find('"+ W166 materializer face')
ce = n1src.find('"r795 bm-a] "', cs) + len('"r795 bm-a] "')
assert 0 < cs < ce, "W166 claim anchors missing"
claim166 = n1src[cs:ce]
io.open(r"results\_r803bma_w167_probe_n1_claim.txt", "w", encoding="utf-8", newline="").write(claim166)

receipt = {
    "probe": "r803 W167 freeze pre-TOK string-face inventory",
    "faces": {
        "pf_block_len": len(blk_pf), "n1_entry_len": len(entry166),
        "mat_block_len": len(blk_mat), "claim_len": len(claim166),
    },
    "pf_block_eol_crlf": blk_pf.count("\r\n"),
    "n1_entry_eol_crlf": entry166.count("\r\n"),
    "mat_block_eol_crlf": blk_mat.count("\r\n"),
    "claim_eol_crlf": claim166.count("\r\n"),
    "mat_chain_rows": re.findall(r"assert pf\.N1_BANDS\[(\d+)\]",
                                 blk_mat[blk_mat.find("assert pf.N1_BANDS[138]"):
                                         blk_mat.find("# prior-wave disjointness")]),
    "needles": {},
}
needles = [
    # row + entry carriers
    '166: {"a": (380_004, 382_003), "b_exit": (382_004, 382_203),',
    '166: {"batch"',
    # seed-base rows (entry comment face)
    '"a_seed_base": 380_004,',
    '"b_exit_seed_base": 382_004,',
    # dotted bands (W166 geometry)
    "379_804..381_803", "379_804..380_003", "380_004..382_003",
    "380_004..380_203", "382_004..382_203",
    # W167 projection prose inside W166 blocks (physical fragment shape)
    "382_004..384_003", "382_204..382_403",
    "W167 A window; W167 freezer MUST re-derive on the post-W166",
    # identity strings
    "PERPETUAL_N1_W166_PREREG.md", "PERPETUAL-N1-W166", "n1_w166_results.json",
    "n1_w166", "n1w166", "_r797bma", "MSG-2026-10-06-223x", "d1dc12117",
    "768,412", "360,920", "ONE HUNDRED-AND-FIFTY-SIXTH",
    "engine_owner rows 155", "rows 81 + candidate", "eighty-first",
    "twenty-fifth", "r799", "r797", "r793", "W166", "W165", "166", "165",
    # set() asserts
    "set(range(380_004, 382_004))", "set(range(382_004, 382_204))",
    "== 380_004 == 380_003 + 1", "== 382_004 == 382_003 + 1",
    "380_003+1", "382_003+1",
    # seat delivery / self-ack prose (honesty faces)
    "move deferred to the W167 finalize window",
    "W166 seat still in",
    # registered-row sha citations
    "bm-a r795 freeze aebb94d2d",
    "W165 row bm-a r795 freeze",
    "aebb94d2d, SINGLE STATE zero seat gap W2..W165 all",
    # jump phrases (healed fragment carried via @JB@)
    "own-wave A window reserved jumps to 382_004, first-clean ",
    "jumps to 382_004, first-clean 382_004..382_203 hops=1",
    # freeze-session / prior-finalize / receipt / gate-session composites
    "bm-a r799 freeze", "r799 bm-a freeze",
    "W165 finalize landed same-window r796",
    "W165 finalize one-pass bm-a r796", "W165 bm-a r796 one-pass",
    "_r797bma_w166_probe_receipt.json", "_r797bma_w166_band_gate.json",
    "r793 gate leg3", "r793 gate", "r796 sec8 succession", "r796 sec8",
    "gate-derived r797", "r797 pre-seat push",
    # seat tokens
    "bma-w166-seat", "MSG-223x",
    # pf / mat jump-phrase fragment shapes
    "jumps to 382_004 -> 382_004..382_203,",
    "382_004 and lands 382_004..382_203",
]
for n in needles:
    receipt["needles"][n] = {
        "pf": pfsrc.count(n), "n1": n1src.count(n),
        "pf_blk": blk_pf.count(n), "entry": entry166.count(n),
        "mat": blk_mat.count(n), "claim": claim166.count(n),
    }
io.open(r"results\_r803bma_w167_face_probe_receipt.json", "w", encoding="utf-8").write(
    json.dumps(receipt, indent=1, ensure_ascii=False))
print("probe rc0: pf_blk", len(blk_pf), "entry", len(entry166),
      "mat", len(blk_mat), "claim", len(claim166),
      "chain", receipt["mat_chain_rows"][:3], "..", receipt["mat_chain_rows"][-3:])
