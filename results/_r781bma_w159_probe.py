# -*- coding: utf-8 -*-
"""r781 bm-a W159 freeze pre-TOK empirical probe (r773 pit law leg 1:
full string-face inventory BEFORE writing TOK; r776 law: projection-prose
old strings taken from PHYSICAL fragment shapes). Dumps the four W158
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

# face 1: pf W158 comment block + row
i1 = pfsrc.find("    # W158 (bm-a r773 freeze")
assert i1 > 0, "pf W158 comment block not found"
r1 = pfsrc.find('158: {"a": (362_404, 364_403)', i1)
assert r1 > i1, "pf W158 row not after comment block"
j1 = pfsrc.find(EO, r1) + len(EO)
blk_pf = pfsrc[i1:j1]
io.open(r"results\_r781bma_w159_probe_pf_block.txt", "w", encoding="utf-8", newline="").write(blk_pf)

# face 2: n1 WAVE_CONFIGS W158 entry
k = n1src.find('158: {"batch"')
assert k > 0, "n1 W158 entry not found"
m = n1src.find(EO, k) + len(EO)
entry158 = n1src[k:m]
io.open(r"results\_r781bma_w159_probe_n1_entry.txt", "w", encoding="utf-8", newline="").write(entry158)

# face 3: n1 W158 materializer block
w = n1src.find("# --- W158 materializer face")
t2 = n1src.find("# --- T-141 s2 lane face", w)
assert 0 < w < t2, "materializer anchors missing"
blk_mat = n1src[w:t2]
io.open(r"results\_r781bma_w159_probe_n1_mat.txt", "w", encoding="utf-8", newline="").write(blk_mat)

# face 4: n1 PASS snippet claim
cs = n1src.find('"+ W158 materializer face')
ce = n1src.find('"r773 bm-a] "', cs) + len('"r773 bm-a] "')
assert 0 < cs < ce, "W158 claim anchors missing"
claim158 = n1src[cs:ce]
io.open(r"results\_r781bma_w159_probe_n1_claim.txt", "w", encoding="utf-8", newline="").write(claim158)

receipt = {
    "probe": "r781 W159 freeze pre-TOK string-face inventory",
    "faces": {
        "pf_block_len": len(blk_pf), "n1_entry_len": len(entry158),
        "mat_block_len": len(blk_mat), "claim_len": len(claim158),
    },
    "pf_block_eol_crlf": blk_pf.count("\r\n"),
    "n1_entry_eol_crlf": entry158.count("\r\n"),
    "mat_block_eol_crlf": blk_mat.count("\r\n"),
    "claim_eol_crlf": claim158.count("\r\n"),
    "mat_chain_rows": re.findall(r"assert pf\.N1_BANDS\[(\d+)\]",
                                 blk_mat[blk_mat.find("assert pf.N1_BANDS[138]"):
                                         blk_mat.find("# prior-wave disjointness")]),
    # needle counts the freeze TOK must satisfy (count==1 in the source faces)
    "needles": {},
}
needles = [
    # pf row + n1 row carriers
    '158: {"a": (362_404, 364_403), "b_exit": (364_404, 364_603),',
    '158: {"batch"',
    # seed-base rows (pf comment face)
    '"a_seed_base": 362_404,',
    '"b_exit_seed_base": 364_404,',
    # dotted bands
    "362_204..362_403", "362_204..364_203", "362_404..364_403",
    "362_404..362_603", "364_404..364_603",
    # W159 projection prose inside W158 blocks (physical fragment shape)
    "364_404..366_403", "364_604..364_803",
    "W159 A window; W159 freezer MUST re-derive on the post-W158",
    "refuse the naive W159 A window; W159 freezer",
    # identity strings
    "PERPETUAL_N1_W158_PREREG.md", "PERPETUAL-N1-W158", "n1_w158_results.json",
    "n1_w158", "_r773bma", "MSG-2026-10-06-120x", "24aff72f5",
    "741,411", "343,320", "ONE HUNDRED-AND-FORTY-EIGHTH",
    "engine_owner rows 147", "rows 73 + candidate", "seventy-fourth",
    "seventeenth", "r773", "r772", "W158", "W157", "158", "157",
    # set() asserts
    "set(range(362_404, 364_404))", "set(range(364_404, 364_604))",
    "== 362_404 == 362_403 + 1", "== 364_404 == 364_403 + 1",
]
for n in needles:
    receipt["needles"][n] = {
        "pf": pfsrc.count(n), "n1": n1src.count(n),
        "pf_blk": blk_pf.count(n), "entry": entry158.count(n),
        "mat": blk_mat.count(n), "claim": claim158.count(n),
    }
io.open(r"results\_r781bma_w159_probe_receipt.json", "w", encoding="utf-8").write(
    json.dumps(receipt, indent=1, ensure_ascii=False))
print("probe rc0: pf_blk", len(blk_pf), "entry", len(entry158),
      "mat", len(blk_mat), "claim", len(claim158),
      "chain", receipt["mat_chain_rows"][:3], "..", receipt["mat_chain_rows"][-3:])
