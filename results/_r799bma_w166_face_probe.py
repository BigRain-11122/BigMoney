# -*- coding: utf-8 -*-
"""r799 bm-a W166 freeze pre-TOK empirical probe (r773 pit law leg 1:
full string-face inventory BEFORE writing TOK; r776 law: projection-prose
old strings taken from PHYSICAL fragment shapes). Dumps the four W165
faces (pf comment block+row / n1 WAVE_CONFIGS entry / n1 materializer
block / n1 PASS claim) to receipt files + counts every needle the
freeze script will use.
Bloodline: r789 _r789bma_w163_face_probe.py machinery verbatim (W163 era),
r795 W165-face precedent; W166 facts:
  - band gate results/_r797bma_w166_band_gate.json rc0 ADMIT
    (A 380_004..382_003 staircase TWENTY-FIFTH instance E36 hops=1 past
    the W165 B band; naive 379_804..381_803 refused at its own start by
    the registered W165 B band 379_804..380_003; B 382_004..382_203
    own-A mutual exclusion hops=1, naive 380_004..380_203);
  - pre-seat probe results/_r797bma_w166_probe_receipt.json ADMIT;
  - seat MSG-2026-10-06-223x-bma-w166-seat published d1dc12117 (r797
    pre-seat push, r565 law: on origin BEFORE this freeze commit)."""
import io
import json
import re

PF = r"scripts/perpetual_faces.py"
N1 = r"scripts/perpetual_faces_n1.py"
EO = '"engine_owner": "bm-a"},'

pfsrc = io.open(PF, encoding="utf-8", newline="").read()
n1src = io.open(N1, encoding="utf-8", newline="").read()

# face 1: pf W165 comment block + row
i1 = pfsrc.find("    # W165 (bm-a r795 freeze")
assert i1 > 0, "pf W165 comment block not found"
r1 = pfsrc.find('165: {"a": (377_804', i1)
assert r1 > i1, "pf W165 row not after comment block"
j1 = pfsrc.find(EO, r1) + len(EO)
blk_pf = pfsrc[i1:j1]
io.open(r"results\_r799bma_w166_probe_pf_block.txt", "w", encoding="utf-8", newline="").write(blk_pf)

# face 2: n1 WAVE_CONFIGS W165 entry
k = n1src.find('165: {"batch"')
assert k > 0, "n1 W165 entry not found"
m = n1src.find(EO, k) + len(EO)
entry165 = n1src[k:m]
io.open(r"results\_r799bma_w166_probe_n1_entry.txt", "w", encoding="utf-8", newline="").write(entry165)

# face 3: n1 W165 materializer block
w = n1src.find("# --- W165 materializer face")
t2 = n1src.find("# --- T-141 s2 lane face", w)
assert 0 < w < t2, "materializer anchors missing"
blk_mat = n1src[w:t2]
io.open(r"results\_r799bma_w166_probe_n1_mat.txt", "w", encoding="utf-8", newline="").write(blk_mat)

# face 4: n1 PASS snippet claim
cs = n1src.find('"+ W165 materializer face')
ce = n1src.find('"r795 bm-a] "', cs) + len('"r795 bm-a] "')
assert 0 < cs < ce, "W165 claim anchors missing"
claim165 = n1src[cs:ce]
io.open(r"results\_r799bma_w166_probe_n1_claim.txt", "w", encoding="utf-8", newline="").write(claim165)

receipt = {
    "probe": "r799 W166 freeze pre-TOK string-face inventory",
    "faces": {
        "pf_block_len": len(blk_pf), "n1_entry_len": len(entry165),
        "mat_block_len": len(blk_mat), "claim_len": len(claim165),
    },
    "pf_block_eol_crlf": blk_pf.count("\r\n"),
    "n1_entry_eol_crlf": entry165.count("\r\n"),
    "mat_block_eol_crlf": blk_mat.count("\r\n"),
    "claim_eol_crlf": claim165.count("\r\n"),
    "mat_chain_rows": re.findall(r"assert pf\.N1_BANDS\[(\d+)\]",
                                 blk_mat[blk_mat.find("assert pf.N1_BANDS[138]"):
                                         blk_mat.find("# prior-wave disjointness")]),
    "needles": {},
}
needles = [
    # row + entry carriers
    '165: {"a": (377_804, 379_803), "b_exit": (379_804, 380_003),',
    '165: {"batch"',
    # seed-base rows (entry comment face)
    '"a_seed_base": 377_804,',
    '"b_exit_seed_base": 379_804,',
    # dotted bands (W165 geometry)
    "377_604..379_603", "377_604..377_803", "377_804..379_803",
    "377_804..378_003", "379_804..380_003",
    # W166 projection prose inside W165 blocks (physical fragment shape)
    "379_804..381_803", "380_004..380_203",
    "W166 A window; W166 freezer MUST re-derive on the post-W165",
    # identity strings
    "PERPETUAL_N1_W165_PREREG.md", "PERPETUAL-N1-W165", "n1_w165_results.json",
    "n1_w165", "n1w165", "_r793bma", "MSG-2026-10-06-205x", "4bdf63090",
    "766,212", "358,720", "ONE HUNDRED-AND-FIFTY-FIFTH",
    "engine_owner rows 154", "rows 80 + candidate", "eightieth",
    "twenty-fourth", "r795", "r793", "r792", "W165", "W164", "165", "164",
    # set() asserts
    "set(range(377_804, 379_804))", "set(range(379_804, 380_004))",
    "== 377_804 == 377_803 + 1", "== 379_804 == 379_803 + 1",
    "377_803+1", "379_803+1",
    # seat delivery / self-ack prose (honesty faces)
    "move deferred to the W166 finalize window",
    "W165 seat still in",
    # registered-row sha citations
    "bm-a r792 freeze f7d34e5a7",
    "W164 row bm-a r792 freeze",
    "f7d34e5a7, SINGLE STATE zero seat gap W2..W164 all",
    # jump phrases (healed fragment carried via @JB@)
    "own-wave A window reserved jumps to 379_804, first-clean ",
    "jumps to 379_804, first-clean 379_804..380_003 hops=1",
    # freeze-session / prior-finalize / receipt / gate-session composites
    "bm-a r795 freeze", "r795 bm-a freeze",
    "W164 finalize landed same-window r793",
    "W164 finalize one-pass bm-a r793", "W164 bm-a r793 one-pass",
    "_r793bma_w165_probe_receipt.json", "_r793bma_w165_band_gate.json",
    "r792 gate leg3", "r792 gate", "r793 sec8 succession", "r793 sec8",
    "gate-derived r793", "r793 pre-seat push",
    # seat tokens
    "bma-w165-seat", "MSG-205x",
    # pf / mat jump-phrase fragment shapes
    "jumps to 379_804 -> 379_804..380_003,",
    "379_804 and lands 379_804..380_003",
]
for n in needles:
    receipt["needles"][n] = {
        "pf": pfsrc.count(n), "n1": n1src.count(n),
        "pf_blk": blk_pf.count(n), "entry": entry165.count(n),
        "mat": blk_mat.count(n), "claim": claim165.count(n),
    }
io.open(r"results\_r799bma_w166_face_probe_receipt.json", "w", encoding="utf-8").write(
    json.dumps(receipt, indent=1, ensure_ascii=False))
print("probe rc0: pf_blk", len(blk_pf), "entry", len(entry165),
      "mat", len(blk_mat), "claim", len(claim165),
      "chain", receipt["mat_chain_rows"][:3], "..", receipt["mat_chain_rows"][-3:])
