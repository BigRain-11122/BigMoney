# -*- coding: utf-8 -*-
"""r785 bm-a W161 freeze pre-TOK empirical probe (r773 pit law leg 1:
full string-face inventory BEFORE writing TOK; r776 law: projection-prose
old strings taken from PHYSICAL fragment shapes). Dumps the four W160
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

# face 1: pf W160 comment block + row
i1 = pfsrc.find("    # W160 (bm-a r783 freeze")
assert i1 > 0, "pf W160 comment block not found"
r1 = pfsrc.find('160: {"a": (366_804', i1)
assert r1 > i1, "pf W160 row not after comment block"
j1 = pfsrc.find(EO, r1) + len(EO)
blk_pf = pfsrc[i1:j1]
io.open(r"results\_r785bma_w161_probe_pf_block.txt", "w", encoding="utf-8", newline="").write(blk_pf)

# face 2: n1 WAVE_CONFIGS W160 entry
k = n1src.find('160: {"batch"')
assert k > 0, "n1 W160 entry not found"
m = n1src.find(EO, k) + len(EO)
entry160 = n1src[k:m]
io.open(r"results\_r785bma_w161_probe_n1_entry.txt", "w", encoding="utf-8", newline="").write(entry160)

# face 3: n1 W160 materializer block
w = n1src.find("# --- W160 materializer face")
t2 = n1src.find("# --- T-141 s2 lane face", w)
assert 0 < w < t2, "materializer anchors missing"
blk_mat = n1src[w:t2]
io.open(r"results\_r785bma_w161_probe_n1_mat.txt", "w", encoding="utf-8", newline="").write(blk_mat)

# face 4: n1 PASS snippet claim
cs = n1src.find('"+ W160 materializer face')
ce = n1src.find('"r783 bm-a] "', cs) + len('"r783 bm-a] "')
assert 0 < cs < ce, "W160 claim anchors missing"
claim160 = n1src[cs:ce]
io.open(r"results\_r785bma_w161_probe_n1_claim.txt", "w", encoding="utf-8", newline="").write(claim160)

receipt = {
    "probe": "r785 W161 freeze pre-TOK string-face inventory",
    "faces": {
        "pf_block_len": len(blk_pf), "n1_entry_len": len(entry160),
        "mat_block_len": len(blk_mat), "claim_len": len(claim160),
    },
    "pf_block_eol_crlf": blk_pf.count("\r\n"),
    "n1_entry_eol_crlf": entry160.count("\r\n"),
    "mat_block_eol_crlf": blk_mat.count("\r\n"),
    "claim_eol_crlf": claim160.count("\r\n"),
    "mat_chain_rows": re.findall(r"assert pf\.N1_BANDS\[(\d+)\]",
                                 blk_mat[blk_mat.find("assert pf.N1_BANDS[138]"):
                                         blk_mat.find("# prior-wave disjointness")]),
    # needle counts the freeze TOK must satisfy (count==1 in the source faces)
    "needles": {},
}
needles = [
    # row + entry carriers
    '160: {"a": (366_804, 368_803), "b_exit": (368_804, 369_003),',
    '160: {"batch"',
    # seed-base rows (pf comment face)
    '"a_seed_base": 366_804,',
    '"b_exit_seed_base": 368_804,',
    # dotted bands
    "366_604..366_803", "366_604..368_603", "366_804..368_803",
    "366_804..367_003", "368_804..369_003",
    # W161 projection prose inside W160 blocks (physical fragment shape)
    "368_804..370_803", "369_004..369_203",
    "W161 A window; W161 freezer MUST re-derive on the post-W160",
    # identity strings
    "PERPETUAL_N1_W160_PREREG.md", "PERPETUAL-N1-W160", "n1_w160_results.json",
    "n1_w160", "_r783bma", "MSG-2026-10-06-162x", "566ec5f86",
    "755,212", "347,720", "ONE HUNDRED-AND-FIFTIETH",
    "engine_owner rows 149", "rows 75 + candidate", "seventy-sixth",
    "nineteenth", "r783", "r782", "W160", "W159", "160", "159",
    # set() asserts
    "set(range(366_804, 368_804))", "set(range(368_804, 369_004))",
    "== 366_804 == 366_803 + 1", "== 368_804 == 368_803 + 1",
    # seat delivery / self-ack prose (honesty fixup needles)
    "self-ack inbox->processed move deferred to",
    "move deferred to the W160 finalize window",
]
for n in needles:
    receipt["needles"][n] = {
        "pf": pfsrc.count(n), "n1": n1src.count(n),
        "pf_blk": blk_pf.count(n), "entry": entry160.count(n),
        "mat": blk_mat.count(n), "claim": claim160.count(n),
    }
io.open(r"results\_r785bma_w161_face_probe_receipt.json", "w", encoding="utf-8").write(
    json.dumps(receipt, indent=1, ensure_ascii=False))
print("probe rc0: pf_blk", len(blk_pf), "entry", len(entry160),
      "mat", len(blk_mat), "claim", len(claim160),
      "chain", receipt["mat_chain_rows"][:3], "..", receipt["mat_chain_rows"][-3:])
