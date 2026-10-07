# -*- coding: utf-8 -*-
"""r830 bm-a W175 freeze pre-TOK empirical probe (r773 pit law leg 1:
full string-face inventory BEFORE writing TOK; r776 law: needles taken
from PHYSICAL fragment shapes). Dumps the four W174 faces (pf comment
block+row / n1 WAVE_CONFIGS entry / n1 materializer block / n1 PASS
claim) to receipt files + counts every needle the W175 freeze uses.
Bloodline: r819/r822/r826 face-probe machinery; W175 facts:
  - pre-seat probe results/_r828bma_w175_probe_receipt.json rc0 ADMIT
    (A 399_804..401_803 staircase THIRTY-FIFTH instance E36 hops=1
    past the registered W174 B band 399_604..399_803; naive
    399_604..401_603 refused at its own start by the W174 B band --
    receipt A_semantics machine-cites 'W174 prereg sec5 item5 + W174
    seat MSG leg4 + r823 probe leg4' anticipation + MANDATE; B
    401_804..402_003 own-A mutual exclusion hops=1, naive
    399_804..400_003);
  - ordinal convergence: W174 sec5.5 prose anticipated 35th, r828
    receipt machine-read THIRTY-FIFTH -- no divergence this wave;
  - W175 has ONE receipt (merged-gate probe structure inherited from
    r812/r814/r818/r820/r823/r828: leg0 registry / leg1 bands+hops+
    semantics / leg2 conflicts / leg3 origin vacancy / leg4 W176+
    projection);
  - seat MSG-2026-10-07-1434-bma-w175-seat published (r828 pre-seat
    push 25c414e95 path-derived TRUE landed sha per r812 precedent;
    r565 law: on origin BEFORE this freeze commit; seat MSG self-ack
    inbox->processed move landed the r828 same window);
  - registered W174 freeze sha machine-derived = db42a0d46 (git log
    origin/main --grep "W174 FREEZE"); W174 finalize one-pass landed
    r827: ledger head 788,212, merged pool K=380,720."""
import io
import json
import re

PF = r"scripts/perpetual_faces.py"
N1 = r"scripts/perpetual_faces_n1.py"
EO = '"engine_owner": "bm-a"},'

pfsrc = io.open(PF, encoding="utf-8", newline="").read()
n1src = io.open(N1, encoding="utf-8", newline="").read()

# face 1: pf W174 comment block + row
i1 = pfsrc.find("    # W174 (bm-a r826 freeze")
assert i1 > 0, "pf W174 comment block not found"
r1 = pfsrc.find('174: {"a": (397_604', i1)
assert r1 > i1, "pf W174 row not after comment block"
j1 = pfsrc.find(EO, r1) + len(EO)
blk_pf = pfsrc[i1:j1]
io.open(r"results\_r830bma_w175_probe_pf_block.txt", "w", encoding="utf-8", newline="").write(blk_pf)

# face 2: n1 WAVE_CONFIGS W174 entry
k = n1src.find('174: {"batch"')
assert k > 0, "n1 W174 entry not found"
m = n1src.find(EO, k) + len(EO)
entry174 = n1src[k:m]
io.open(r"results\_r830bma_w175_probe_n1_entry.txt", "w", encoding="utf-8", newline="").write(entry174)

# face 3: n1 W174 materializer block
w = n1src.find("# --- W174 materializer face")
t2 = n1src.find("# --- T-141 s2 lane face", w)
assert 0 < w < t2, "materializer anchors missing"
blk_mat = n1src[w:t2]
io.open(r"results\_r830bma_w175_probe_n1_mat.txt", "w", encoding="utf-8", newline="").write(blk_mat)

# face 4: n1 PASS snippet claim (r776 physical-shape law: the W174 claim
# trailing session marker is "r826 bm-a] " -- the actual r826 freeze
# session attribution; the W175 tool rolls it to the new session)
cs = n1src.find('"+ W174 materializer face')
ce = n1src.find('"r826 bm-a] "', cs) + len('"r826 bm-a] "')
assert 0 < cs < ce, "W174 claim anchors missing"
claim174 = n1src[cs:ce]
io.open(r"results\_r830bma_w175_probe_n1_claim.txt", "w", encoding="utf-8", newline="").write(claim174)

receipt = {
    "probe": "r830 W175 freeze pre-TOK string-face inventory",
    "faces": {
        "pf_block_len": len(blk_pf), "n1_entry_len": len(entry174),
        "mat_block_len": len(blk_mat), "claim_len": len(claim174),
    },
    "pf_block_eol_crlf": blk_pf.count("\r\n"),
    "n1_entry_eol_crlf": entry174.count("\r\n"),
    "mat_block_eol_crlf": blk_mat.count("\r\n"),
    "claim_eol_crlf": claim174.count("\r\n"),
    "mat_chain_rows": re.findall(r"assert pf\.N1_BANDS\[(\d+)\]",
                                 blk_mat[blk_mat.find("assert pf.N1_BANDS[138]"):
                                         blk_mat.find("# prior-wave disjointness")]),
    "needles": {},
}
needles = [
    # row + entry carriers
    '174: {"a": (397_604, 399_603), "b_exit": (399_604, 399_803),',
    '174: {"batch"',
    # seed-base rows (entry comment face)
    '"a_seed_base": 397_604,',
    '"b_exit_seed_base": 399_604,',
    # dotted bands (W174 geometry)
    "397_604..399_603", "399_604..399_803", "397_404..399_403",
    "397_604..397_803",
    # W175 projection prose inside W174 blocks (physical fragment shape)
    "399_604..401_603", "399_804..400_003",
    "W175 A window; W175 freezer MUST re-derive on the post-W174",
    # identity strings
    "PERPETUAL_N1_W174_PREREG.md", "PERPETUAL-N1-W174", "n1_w174_results.json",
    "n1_w174", "n1w174", "_r823bma", "MSG-2026-10-07-1247", "9b0e1cb29",
    "786,012", "378,520", "ONE HUNDRED-AND-SIXTY-FOURTH",
    "engine_owner rows 163", "rows 89 + candidate", "ninetieth",
    "THIRTY-FOURTH", "thirty-fourth", "r826", "r823", "r828", "W174", "W173", "W175",
    "174", "173", "175",
    # set() asserts
    "set(range(397_604, 399_604))", "set(range(399_604, 399_804))",
    "== 397_604 == 397_603 + 1", "== 399_604 == 399_603 + 1",
    "397_603+1", "399_603+1",
    # seat delivery / self-ack prose (honesty faces)
    "self-ack inbox->processed archive ALREADY LANDED",
    "r823 same-window self-ack move",
    "the W174 seat MSG sits in",
    # registered-row sha citations
    "bm-a r822 freeze 04e95748a",
    "W173 row bm-a r822 freeze",
    "04e95748a, SINGLE STATE zero seat gap W2..W173 all",
    "04e95748a", "db42a0d46",
    # jump phrases (physical fragment shapes)
    "own-wave A window reserved jumps to 399_604, first-clean ",
    "jumps to 399_604, first-clean 399_604..399_803 hops=1",
    "jumps to 399_604 -> 399_604..399_803,",
    "399_604 and lands 399_604..399_803",
    # freeze-session / prior-finalize / receipt / gate-session composites
    "bm-a r826 freeze", "r826 bm-a freeze", "r826 bm-a] ",
    "W173 finalize landed same-window r823",
    "W173 finalize one-pass bm-a r823", "W173 bm-a r823 one-pass",
    "finalize one-pass bm-a r823",
    "_r823bma_w174_probe_receipt.json",
    "r823 pre-seat push", "r820 probe leg4",
    # seat tokens
    "bma-w174-seat", "MSG-1247",
    # payload faces (3-item truth landed at r828)
    "payload = seat MSG + pre-seat probe script + probe receipt",
    "(3-item; the W173 finalize product already on origin since r823",
    "direct fast-forward behind-0",
    # single-window derive faces
    "single-window derive (r812 merged the gate legs INTO the",
    # sec8 succession face (r826 settle -- cited again by W175 because
    # the W174 sec8 succession notes landed r826)
    "r823 sec8 succession",
]
for n in needles:
    receipt["needles"][n] = {
        "pf": pfsrc.count(n), "n1": n1src.count(n),
        "pf_blk": blk_pf.count(n), "entry": entry174.count(n),
        "mat": blk_mat.count(n), "claim": claim174.count(n),
    }
io.open(r"results\_r830bma_w175_face_probe_receipt.json", "w", encoding="utf-8").write(
    json.dumps(receipt, indent=1, ensure_ascii=False))
print("probe rc0: pf_blk", len(blk_pf), "entry", len(entry174),
      "mat", len(blk_mat), "claim", len(claim174),
      "chain_n", len(receipt["mat_chain_rows"]),
      "chain_tail", receipt["mat_chain_rows"][-3:])
