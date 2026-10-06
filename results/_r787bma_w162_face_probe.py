# -*- coding: utf-8 -*-
"""r787 bm-a W162 freeze pre-TOK empirical probe (r773 pit law leg 1:
full string-face inventory BEFORE writing TOK; r776 law: projection-prose
old strings taken from PHYSICAL fragment shapes). Dumps the four W161
faces (pf comment block+row / n1 WAVE_CONFIGS entry / n1 materializer
block / n1 PASS claim) to receipt files + counts every needle the
freeze script will use."""
import io
import json
import re

PF = r"scripts/perpetual_faces.py"
N1 = r"scripts/perpetual_faces_n1.py"
EO = '"engine_owner": "bm-a"},'

pfsrc = io.open(PF, encoding="utf-8", newline="").read()
n1src = io.open(N1, encoding="utf-8", newline="").read()

# face 1: pf W161 comment block + row
i1 = pfsrc.find("    # W161 (bm-a r785 freeze")
assert i1 > 0, "pf W161 comment block not found"
r1 = pfsrc.find('161: {"a": (369_004', i1)
assert r1 > i1, "pf W161 row not after comment block"
j1 = pfsrc.find(EO, r1) + len(EO)
blk_pf = pfsrc[i1:j1]
io.open(r"results\_r787bma_w162_probe_pf_block.txt", "w", encoding="utf-8", newline="").write(blk_pf)

# face 2: n1 WAVE_CONFIGS W161 entry
k = n1src.find('161: {"batch"')
assert k > 0, "n1 W161 entry not found"
m = n1src.find(EO, k) + len(EO)
entry161 = n1src[k:m]
io.open(r"results\_r787bma_w162_probe_n1_entry.txt", "w", encoding="utf-8", newline="").write(entry161)

# face 3: n1 W161 materializer block
w = n1src.find("# --- W161 materializer face")
t2 = n1src.find("# --- T-141 s2 lane face", w)
assert 0 < w < t2, "materializer anchors missing"
blk_mat = n1src[w:t2]
io.open(r"results\_r787bma_w162_probe_n1_mat.txt", "w", encoding="utf-8", newline="").write(blk_mat)

# face 4: n1 PASS snippet claim
cs = n1src.find('"+ W161 materializer face')
ce = n1src.find('"r785 bm-a] "', cs) + len('"r785 bm-a] "')
assert 0 < cs < ce, "W161 claim anchors missing"
claim161 = n1src[cs:ce]
io.open(r"results\_r787bma_w162_probe_n1_claim.txt", "w", encoding="utf-8", newline="").write(claim161)

receipt = {
    "probe": "r787 W162 freeze pre-TOK string-face inventory",
    "faces": {
        "pf_block_len": len(blk_pf), "n1_entry_len": len(entry161),
        "mat_block_len": len(blk_mat), "claim_len": len(claim161),
    },
    "pf_block_eol_crlf": blk_pf.count("\r\n"),
    "n1_entry_eol_crlf": entry161.count("\r\n"),
    "mat_block_eol_crlf": blk_mat.count("\r\n"),
    "claim_eol_crlf": claim161.count("\r\n"),
    "mat_chain_rows": re.findall(r"assert pf\.N1_BANDS\[(\d+)\]",
                                 blk_mat[blk_mat.find("assert pf.N1_BANDS[138]"):
                                         blk_mat.find("# prior-wave disjointness")]),
    # needle counts the freeze TOK must satisfy (count==1 in the source faces)
    "needles": {},
}
needles = [
    # row + entry carriers
    '161: {"a": (369_004, 371_003), "b_exit": (371_004, 371_203),',
    '161: {"batch"',
    # seed-base rows (pf comment face)
    '"a_seed_base": 369_004,',
    '"b_exit_seed_base": 371_004,',
    # dotted bands
    "368_804..370_803", "369_004..369_203", "369_004..371_003",
    "369_004..371_003", "371_004..371_203",
    # W162 projection prose inside W161 blocks (physical fragment shape)
    "371_004..373_003", "371_204..371_403",
    "W162 A window; W162 freezer MUST re-derive on the post-W161",
    # identity strings
    "PERPETUAL_N1_W161_PREREG.md", "PERPETUAL-N1-W161", "n1_w161_results.json",
    "n1_w161", "_r785bma", "MSG-2026-10-06-165x", "0371f2093",
    "757,412", "349,920", "ONE HUNDRED-AND-FIFTY-FIRST",
    "engine_owner rows 150", "rows 76 + candidate", "seventy-seventh",
    "twentieth", "r785", "r784", "r783", "W161", "W160", "161", "160",
    # set() asserts
    "set(range(369_004, 371_004))", "set(range(371_004, 371_204))",
    "== 369_004 == 369_003 + 1", "== 371_004 == 371_003 + 1",
    # seat delivery / self-ack prose (honesty fixup needles)
    "self-ack inbox->processed move landed",
    "read-only-observer processed",
    "bm-a r784 finalize window",
]
for n in needles:
    receipt["needles"][n] = {
        "pf": pfsrc.count(n), "n1": n1src.count(n),
        "pf_blk": blk_pf.count(n), "entry": entry161.count(n),
        "mat": blk_mat.count(n), "claim": claim161.count(n),
    }
io.open(r"results\_r787bma_w162_face_probe_receipt.json", "w", encoding="utf-8").write(
    json.dumps(receipt, indent=1, ensure_ascii=False))
print("probe rc0: pf_blk", len(blk_pf), "entry", len(entry161),
      "mat", len(blk_mat), "claim", len(claim161),
      "chain", receipt["mat_chain_rows"][:3], "..", receipt["mat_chain_rows"][-3:])
