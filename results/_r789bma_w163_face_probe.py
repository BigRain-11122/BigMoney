# -*- coding: utf-8 -*-
"""r789 bm-a W163 freeze pre-TOK empirical probe (r773 pit law leg 1:
full string-face inventory BEFORE writing TOK; r776 law: projection-prose
old strings taken from PHYSICAL fragment shapes). Dumps the four W162
faces (pf comment block+row / n1 WAVE_CONFIGS entry / n1 materializer
block / n1 PASS claim) to receipt files + counts every needle the
freeze script will use.
Bloodline: r787 _r787bma_w162_face_probe.py machinery verbatim."""
import io
import json
import re

PF = r"scripts/perpetual_faces.py"
N1 = r"scripts/perpetual_faces_n1.py"
EO = '"engine_owner": "bm-a"},'

pfsrc = io.open(PF, encoding="utf-8", newline="").read()
n1src = io.open(N1, encoding="utf-8", newline="").read()

# face 1: pf W162 comment block + row
i1 = pfsrc.find("    # W162 (bm-a r787 freeze")
assert i1 > 0, "pf W162 comment block not found"
r1 = pfsrc.find('162: {"a": (371_204', i1)
assert r1 > i1, "pf W162 row not after comment block"
j1 = pfsrc.find(EO, r1) + len(EO)
blk_pf = pfsrc[i1:j1]
io.open(r"results\_r789bma_w163_probe_pf_block.txt", "w", encoding="utf-8", newline="").write(blk_pf)

# face 2: n1 WAVE_CONFIGS W162 entry
k = n1src.find('162: {"batch"')
assert k > 0, "n1 W162 entry not found"
m = n1src.find(EO, k) + len(EO)
entry162 = n1src[k:m]
io.open(r"results\_r789bma_w163_probe_n1_entry.txt", "w", encoding="utf-8", newline="").write(entry162)

# face 3: n1 W162 materializer block
w = n1src.find("# --- W162 materializer face")
t2 = n1src.find("# --- T-141 s2 lane face", w)
assert 0 < w < t2, "materializer anchors missing"
blk_mat = n1src[w:t2]
io.open(r"results\_r789bma_w163_probe_n1_mat.txt", "w", encoding="utf-8", newline="").write(blk_mat)

# face 4: n1 PASS snippet claim
cs = n1src.find('"+ W162 materializer face')
ce = n1src.find('"r787 bm-a] "', cs) + len('"r787 bm-a] "')
assert 0 < cs < ce, "W162 claim anchors missing"
claim162 = n1src[cs:ce]
io.open(r"results\_r789bma_w163_probe_n1_claim.txt", "w", encoding="utf-8", newline="").write(claim162)

receipt = {
    "probe": "r789 W163 freeze pre-TOK string-face inventory",
    "faces": {
        "pf_block_len": len(blk_pf), "n1_entry_len": len(entry162),
        "mat_block_len": len(blk_mat), "claim_len": len(claim162),
    },
    "pf_block_eol_crlf": blk_pf.count("\r\n"),
    "n1_entry_eol_crlf": entry162.count("\r\n"),
    "mat_block_eol_crlf": blk_mat.count("\r\n"),
    "claim_eol_crlf": claim162.count("\r\n"),
    "mat_chain_rows": re.findall(r"assert pf\.N1_BANDS\[(\d+)\]",
                                 blk_mat[blk_mat.find("assert pf.N1_BANDS[138]"):
                                         blk_mat.find("# prior-wave disjointness")]),
    # needle counts the freeze TOK must satisfy (count==1 in the source faces)
    "needles": {},
}
needles = [
    # row + entry carriers
    '162: {"a": (371_204, 373_203), "b_exit": (373_204, 373_403),',
    '162: {"batch"',
    # seed-base rows (pf comment face)
    '"a_seed_base": 371_204,',
    '"b_exit_seed_base": 373_204,',
    # dotted bands
    "371_004..373_003", "371_204..371_403", "371_204..373_203",
    "373_204..373_403",
    # W163 projection prose inside W162 blocks (physical fragment shape)
    "373_204..375_203", "373_404..373_603",
    "W163 A window; W163 freezer MUST re-derive on the post-W162",
    # identity strings
    "PERPETUAL_N1_W162_PREREG.md", "PERPETUAL-N1-W162", "n1_w162_results.json",
    "n1_w162", "_r787bma", "MSG-2026-10-06-175x", "1d43d7906",
    "759,612", "352,120", "ONE HUNDRED-AND-FIFTY-SECOND",
    "engine_owner rows 151", "rows 77 + candidate", "seventy-eighth",
    "twenty-first", "r787", "r786", "r785", "W162", "W161", "162", "161",
    # set() asserts
    "set(range(371_204, 373_204))", "set(range(373_204, 373_404))",
    "== 371_204 == 371_203 + 1", "== 373_204 == 373_203 + 1",
    # seat delivery / self-ack prose (honesty fixup needles)
    "move deferred to the W163 finalize window",
    "W162 seat still in",
    "facts helper",
    # registered-row sha citations
    "bm-a r785 freeze 678a07d4f",
    "W161 row bm-a r785 freeze",
    "678a07d4f, SINGLE STATE zero seat gap W2..W161 all",
    # jump phrases (healed fragment carried via @JB@)
    "own-wave A window reserved jumps to 373_204, first-clean ",
    "jumps to 373_204, first-clean 373_204..373_403 hops=1",
    # freeze-session / prior-finalize / receipt / gate-session composites
    "bm-a r787 freeze", "r787 bm-a freeze",
    "W161 finalize landed same-window r786",
    "W161 finalize one-pass bm-a r786", "W161 bm-a r786 one-pass",
    "_r787bma_w162_probe_receipt.json", "_r787bma_w162_band_gate.json",
    "r785 gate leg3", "r785 gate", "r786 sec8 succession", "r786 sec8",
    # seat tokens
    "bma-w162-seat", "MSG-175x",
    # pf / mat jump-phrase fragment shapes
    "jumps to 373_204 -> 373_204..373_403,",
    "373_204 and lands 373_204..373_403",
    # base-relation composites
    "371_203+1", "373_203+1",
    # shard identity
    "n1w162",
]
for n in needles:
    receipt["needles"][n] = {
        "pf": pfsrc.count(n), "n1": n1src.count(n),
        "pf_blk": blk_pf.count(n), "entry": entry162.count(n),
        "mat": blk_mat.count(n), "claim": claim162.count(n),
    }
io.open(r"results\_r789bma_w163_face_probe_receipt.json", "w", encoding="utf-8").write(
    json.dumps(receipt, indent=1, ensure_ascii=False))
print("probe rc0: pf_blk", len(blk_pf), "entry", len(entry162),
      "mat", len(blk_mat), "claim", len(claim162),
      "chain", receipt["mat_chain_rows"][:3], "..", receipt["mat_chain_rows"][-3:])
