# -*- coding: utf-8 -*-
"""r834 bm-a W176 freeze pre-TOK empirical probe (r773 pit law leg 1:
full string-face inventory BEFORE writing TOK; r776 law: needles taken
from PHYSICAL fragment shapes). Dumps the four W175 faces (pf comment
block+row / n1 WAVE_CONFIGS entry / n1 materializer block / n1 PASS
claim) to receipt files + counts every needle the W176 freeze uses.
Bloodline: r819/r822/r826/r830 face-probe machinery; W176 facts:
  - pre-seat probe results/_r832bma_w176_probe_receipt.json rc0 ADMIT
    (A 402_004..404_003 staircase THIRTY-SIXTH instance E36 hops=1
    past the registered W175 B band 401_804..402_003; naive
    401_804..403_803 refused at its own start by the W175 B band --
    receipt A_semantics machine-cites 'W175 sec5.5 anticipated 36th'
    (projection and receipt ordinals MATCH, no divergence); B
    404_004..404_203 own-A mutual exclusion hops=1, naive
    402_004..402_203);
  - W176 has ONE receipt (merged-gate probe structure inherited from
    r812/r814/r818/r820/r823/r828/r832: leg0 registry / leg1 bands+hops+
    semantics / leg2 conflicts / leg3 origin vacancy / leg4 W177+
    projection);
  - seat MSG-2026-10-07-1630-bma-w176-seat published (r832 pre-seat
    push 16a8ea982 path-derived TRUE landed sha per r812 precedent;
    r565 law: on origin BEFORE this freeze commit; seat MSG self-ack
    inbox->processed move landed the r833 same window);
  - registered W175 freeze sha machine-derived = f3fca4055 (git log
    origin/main --grep "W175 FREEZE"); W175 finalize one-pass landed
    r831: ledger head 790,412, merged pool K=382,920."""
import io
import json
import re

PF = r"scripts/perpetual_faces.py"
N1 = r"scripts/perpetual_faces_n1.py"
EO = '"engine_owner": "bm-a"},'

pfsrc = io.open(PF, encoding="utf-8", newline="").read()
n1src = io.open(N1, encoding="utf-8", newline="").read()

# face 1: pf W175 comment block + row
i1 = pfsrc.find("    # W175 (bm-a r830 freeze")
assert i1 > 0, "pf W175 comment block not found"
r1 = pfsrc.find('175: {"a": (399_804', i1)
assert r1 > i1, "pf W175 row not after comment block"
j1 = pfsrc.find(EO, r1) + len(EO)
blk_pf = pfsrc[i1:j1]
io.open(r"results\_r834bma_w176_probe_pf_block.txt", "w", encoding="utf-8", newline="").write(blk_pf)

# face 2: n1 WAVE_CONFIGS W175 entry
k = n1src.find('175: {"batch"')
assert k > 0, "n1 W175 entry not found"
m = n1src.find(EO, k) + len(EO)
entry175 = n1src[k:m]
io.open(r"results\_r834bma_w176_probe_n1_entry.txt", "w", encoding="utf-8", newline="").write(entry175)

# face 3: n1 W175 materializer block
w = n1src.find("# --- W175 materializer face")
t2 = n1src.find("# --- T-141 s2 lane face", w)
assert 0 < w < t2, "materializer anchors missing"
blk_mat = n1src[w:t2]
io.open(r"results\_r834bma_w176_probe_n1_mat.txt", "w", encoding="utf-8", newline="").write(blk_mat)

# face 4: n1 PASS snippet claim (r776 physical-shape law: the W175 claim
# trailing session marker is "r830 bm-a] " -- the actual r830 freeze
# session attribution; the W176 tool rolls it to the new session)
cs = n1src.find('"+ W175 materializer face')
ce = n1src.find('"r830 bm-a] "', cs) + len('"r830 bm-a] "')
assert 0 < cs < ce, "W175 claim anchors missing"
claim175 = n1src[cs:ce]
io.open(r"results\_r834bma_w176_probe_n1_claim.txt", "w", encoding="utf-8", newline="").write(claim175)

receipt = {
    "probe": "r834 W176 freeze pre-TOK string-face inventory",
    "faces": {
        "pf_block_len": len(blk_pf), "n1_entry_len": len(entry175),
        "mat_block_len": len(blk_mat), "claim_len": len(claim175),
    },
    "pf_block_eol_crlf": blk_pf.count("\r\n"),
    "n1_entry_eol_crlf": entry175.count("\r\n"),
    "mat_block_eol_crlf": blk_mat.count("\r\n"),
    "claim_eol_crlf": claim175.count("\r\n"),
    "mat_chain_rows": re.findall(r"assert pf\.N1_BANDS\[(\d+)\]",
                                 blk_mat[blk_mat.find("assert pf.N1_BANDS[138]"):
                                         blk_mat.find("# prior-wave disjointness")]),
    "needles": {},
}
needles = [
    # row + entry carriers
    '175: {"a": (399_804, 401_803), "b_exit": (401_804, 402_003),',
    '175: {"batch"',
    # seed-base rows (entry comment face)
    '"a_seed_base": 399_804,',
    '"b_exit_seed_base": 401_804,',
    # dotted bands (W175 geometry)
    "399_804..401_803", "401_804..402_003", "399_604..401_603",
    "399_804..400_003",
    # W176 projection prose inside W175 blocks (physical fragment shape)
    "401_804..403_803", "402_004..402_203",
    "W176 A window; W176 freezer MUST re-derive on the post-W175",
    # identity strings
    "PERPETUAL_N1_W175_PREREG.md", "PERPETUAL-N1-W175", "n1_w175_results.json",
    "n1_w175", "n1w175", "_r828bma", "MSG-2026-10-07-1434", "25c414e95",
    "788,212", "380,720", "ONE HUNDRED-AND-SIXTY-FIFTH",
    "engine_owner rows 164", "rows 90 + candidate", "ninety-first",
    "THIRTY-FIFTH", "thirty-fifth", "r830", "r828", "r831", "r833", "W175", "W174", "W176",
    "175", "174", "176",
    # set() asserts
    "set(range(399_804, 401_804))", "set(range(401_804, 402_004))",
    "== 399_804 == 399_803 + 1", "== 401_804 == 401_803 + 1",
    "399_803+1", "401_803+1",
    # seat delivery / self-ack prose (honesty faces)
    "self-ack inbox->processed archive ALREADY LANDED",
    "r828 same-window self-ack move",
    "the W175 seat MSG sits in",
    # registered-row sha citations
    "bm-a r826 freeze db42a0d46",
    "W174 row bm-a r826 freeze",
    "db42a0d46, SINGLE STATE zero seat gap W2..W174 all",
    "db42a0d46", "f3fca4055",
    # jump phrases (physical fragment shapes)
    "own-wave A window reserved jumps to 401_804, first-clean ",
    "jumps to 401_804, first-clean 401_804..402_003 hops=1",
    "jumps to 401_804 -> 401_804..402_003,",
    "401_804 and lands 401_804..402_003",
    # freeze-session / prior-finalize / receipt / gate-session composites
    "bm-a r830 freeze", "r830 bm-a freeze", "r830 bm-a] ",
    "W174 finalize landed same-window r827",
    "W174 finalize one-pass bm-a r827", "W174 bm-a r827 one-pass",
    "finalize one-pass bm-a r827",
    "_r828bma_w175_probe_receipt.json",
    "r828 pre-seat push", "r823 probe leg4",
    # seat tokens
    "bma-w175-seat", "MSG-1434",
    # payload faces (3-item truth landed at r832)
    "payload = seat MSG + pre-seat probe script + probe receipt",
    "(3-item; the W174 finalize product already on origin since r827",
    "direct fast-forward behind-0",
    # single-window derive faces
    "single-window derive (r812 merged the gate legs INTO the",
    # sec8 succession face (r826 settle -- cited again by W175 because
    # the W174 sec8 succession notes landed r826; W175 sec8 settled
    # r831 one-pass per the r833 prereg facts)
    "r826 sec8 succession",
]
for n in needles:
    receipt["needles"][n] = {
        "pf": pfsrc.count(n), "n1": n1src.count(n),
        "pf_blk": blk_pf.count(n), "entry": entry175.count(n),
        "mat": blk_mat.count(n), "claim": claim175.count(n),
    }
io.open(r"results\_r834bma_w176_face_probe_receipt.json", "w", encoding="utf-8").write(
    json.dumps(receipt, indent=1, ensure_ascii=False))
print("probe rc0: pf_blk", len(blk_pf), "entry", len(entry175),
      "mat", len(blk_mat), "claim", len(claim175),
      "chain_n", len(receipt["mat_chain_rows"]),
      "chain_tail", receipt["mat_chain_rows"][-3:])
