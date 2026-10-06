# -*- coding: utf-8 -*-
"""r783 bm-a W160 freeze pre-TOK empirical probe (r773 pit law leg 1:
full string-face inventory BEFORE writing TOK; r776 law: projection-prose
old strings taken from PHYSICAL fragment shapes). Dumps the four W159
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

# face 1: pf W159 comment block + row
i1 = pfsrc.find("    # W159 (bm-a r779 freeze")
assert i1 > 0, "pf W159 comment block not found"
r1 = pfsrc.find('159: {"a": (364_604, 366_603)', i1)
assert r1 > i1, "pf W159 row not after comment block"
j1 = pfsrc.find(EO, r1) + len(EO)
blk_pf = pfsrc[i1:j1]
io.open(r"results\_r783bma_w160_probe_pf_block.txt", "w", encoding="utf-8", newline="").write(blk_pf)

# face 2: n1 WAVE_CONFIGS W159 entry
k = n1src.find('159: {"batch"')
assert k > 0, "n1 W159 entry not found"
m = n1src.find(EO, k) + len(EO)
entry159 = n1src[k:m]
io.open(r"results\_r783bma_w160_probe_n1_entry.txt", "w", encoding="utf-8", newline="").write(entry159)

# face 3: n1 W159 materializer block
w = n1src.find("# --- W159 materializer face")
t2 = n1src.find("# --- T-141 s2 lane face", w)
assert 0 < w < t2, "materializer anchors missing"
blk_mat = n1src[w:t2]
io.open(r"results\_r783bma_w160_probe_n1_mat.txt", "w", encoding="utf-8", newline="").write(blk_mat)

# face 4: n1 PASS snippet claim
cs = n1src.find('"+ W159 materializer face')
ce = n1src.find('"r779 bm-a] "', cs) + len('"r779 bm-a] "')
assert 0 < cs < ce, "W159 claim anchors missing"
claim159 = n1src[cs:ce]
io.open(r"results\_r783bma_w160_probe_n1_claim.txt", "w", encoding="utf-8", newline="").write(claim159)

receipt = {
    "probe": "r783 W160 freeze pre-TOK string-face inventory",
    "faces": {
        "pf_block_len": len(blk_pf), "n1_entry_len": len(entry159),
        "mat_block_len": len(blk_mat), "claim_len": len(claim159),
    },
    "pf_block_eol_crlf": blk_pf.count("\r\n"),
    "n1_entry_eol_crlf": entry159.count("\r\n"),
    "mat_block_eol_crlf": blk_mat.count("\r\n"),
    "claim_eol_crlf": claim159.count("\r\n"),
    "mat_chain_rows": re.findall(r"assert pf\.N1_BANDS\[(\d+)\]",
                                 blk_mat[blk_mat.find("assert pf.N1_BANDS[138]"):
                                         blk_mat.find("# prior-wave disjointness")]),
    # needle counts the freeze TOK must satisfy (count==1 in the source faces)
    "needles": {},
}
needles = [
    # row + entry carriers
    '159: {"a": (364_604, 366_603), "b_exit": (366_604, 366_803),',
    '159: {"batch"',
    # seed-base rows (pf comment face)
    '"a_seed_base": 364_604,',
    '"b_exit_seed_base": 366_604,',
    # dotted bands
    "364_404..364_603", "364_404..366_403", "364_604..366_603",
    "364_604..364_803", "366_604..366_803",
    # W160 projection prose inside W159 blocks (physical fragment shape)
    "366_604..368_603", "366_804..367_003",
    "W160 A window; W160 freezer MUST re-derive on the post-W159",
    "refuse the naive W160 A window; W160 freezer",
    # identity strings
    "PERPETUAL_N1_W159_PREREG.md", "PERPETUAL-N1-W159", "n1_w159_results.json",
    "n1_w159", "_r779bma", "MSG-2026-10-06-142x", "7b60d09da",
    "753,012", "345,520", "ONE HUNDRED-AND-FORTY-NINTH",
    "engine_owner rows 148", "rows 74 + candidate", "seventy-fifth",
    "eighteenth", "r779", "r773", "W159", "W158", "159", "158",
    # set() asserts
    "set(range(364_604, 366_604))", "set(range(366_604, 366_804))",
    "== 364_604 == 364_603 + 1", "== 366_604 == 366_603 + 1",
    # seat delivery / self-ack prose (honesty fixup needles)
    "direct fast-forward",
    "behind-0 at fetch (r779 pre-seat push), zero merge, zero ",
    "self-ack inbox->processed move deferred to",
]
for n in needles:
    receipt["needles"][n] = {
        "pf": pfsrc.count(n), "n1": n1src.count(n),
        "pf_blk": blk_pf.count(n), "entry": entry159.count(n),
        "mat": blk_mat.count(n), "claim": claim159.count(n),
    }
io.open(r"results\_r783bma_w160_probe_receipt.json", "w", encoding="utf-8").write(
    json.dumps(receipt, indent=1, ensure_ascii=False))
print("probe rc0: pf_blk", len(blk_pf), "entry", len(entry159),
      "mat", len(blk_mat), "claim", len(claim159),
      "chain", receipt["mat_chain_rows"][:3], "..", receipt["mat_chain_rows"][-3:])
