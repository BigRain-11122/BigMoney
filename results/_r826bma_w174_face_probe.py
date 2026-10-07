# -*- coding: utf-8 -*-
"""r826 bm-a W174 freeze pre-TOK empirical probe (r773 pit law leg 1:
full string-face inventory BEFORE writing TOK; r776 law: needles taken
from PHYSICAL fragment shapes). Dumps the four W173 faces (pf comment
block+row / n1 WAVE_CONFIGS entry / n1 materializer block / n1 PASS
claim) to receipt files + counts every needle the W174 freeze uses.
Bloodline: r819/r822 face-probe machinery; W174 facts:
  - pre-seat probe results/_r823bma_w174_probe_receipt.json rc0 ADMIT
    (A 397_604..399_603 staircase THIRTY-FOURTH instance E36 hops=1
    past the registered W173 B band 397_404..397_603; naive
    397_404..399_403 refused at its own start by the W173 B band --
    receipt A_semantics machine-cites 'W173 prereg sec5 item5 + W173
    seat MSG leg4 + r820 probe leg4' anticipation + MANDATE; B
    399_604..399_803 own-A mutual exclusion hops=1, naive
    397_604..397_803);
  - ordinal convergence: W173 sec5.5 prose anticipated 34th, r823
    receipt machine-read THIRTY-FOURTH -- no divergence this wave;
  - W174 has ONE receipt (merged-gate probe structure inherited from
    r812/r814/r818/r820/r823: leg0 registry / leg1 bands+hops+
    semantics / leg2 conflicts / leg3 origin vacancy / leg4 W175+
    projection);
  - seat MSG-2026-10-07-1247-bma-w174-seat published (r823 pre-seat
    push 9b0e1cb29 path-derived TRUE landed sha per r812 precedent;
    r565 law: on origin BEFORE this freeze commit; seat MSG self-ack
    inbox->processed move landed the r823 same window);
  - registered W173 freeze sha machine-derived = 04e95748a (git log
    origin/main --grep "W173 FREEZE"); W173 finalize one-pass landed
    r823: ledger head 786,012, merged pool K=378,520."""
import io
import json
import re

PF = r"scripts/perpetual_faces.py"
N1 = r"scripts/perpetual_faces_n1.py"
EO = '"engine_owner": "bm-a"},'

pfsrc = io.open(PF, encoding="utf-8", newline="").read()
n1src = io.open(N1, encoding="utf-8", newline="").read()

# face 1: pf W173 comment block + row
i1 = pfsrc.find("    # W173 (bm-a r822 freeze")
assert i1 > 0, "pf W173 comment block not found"
r1 = pfsrc.find('173: {"a": (395_404', i1)
assert r1 > i1, "pf W173 row not after comment block"
j1 = pfsrc.find(EO, r1) + len(EO)
blk_pf = pfsrc[i1:j1]
io.open(r"results\_r826bma_w174_probe_pf_block.txt", "w", encoding="utf-8", newline="").write(blk_pf)

# face 2: n1 WAVE_CONFIGS W173 entry
k = n1src.find('173: {"batch"')
assert k > 0, "n1 W173 entry not found"
m = n1src.find(EO, k) + len(EO)
entry173 = n1src[k:m]
io.open(r"results\_r826bma_w174_probe_n1_entry.txt", "w", encoding="utf-8", newline="").write(entry173)

# face 3: n1 W173 materializer block
w = n1src.find("# --- W173 materializer face")
t2 = n1src.find("# --- T-141 s2 lane face", w)
assert 0 < w < t2, "materializer anchors missing"
blk_mat = n1src[w:t2]
io.open(r"results\_r826bma_w174_probe_n1_mat.txt", "w", encoding="utf-8", newline="").write(blk_mat)

# face 4: n1 PASS snippet claim (r776 physical-shape law: the W173 claim
# trailing session marker is "r822 bm-a] " -- the actual r822 freeze
# session attribution; the W174 tool rolls it to the new session)
cs = n1src.find('"+ W173 materializer face')
ce = n1src.find('"r822 bm-a] "', cs) + len('"r822 bm-a] "')
assert 0 < cs < ce, "W173 claim anchors missing"
claim173 = n1src[cs:ce]
io.open(r"results\_r826bma_w174_probe_n1_claim.txt", "w", encoding="utf-8", newline="").write(claim173)

receipt = {
    "probe": "r826 W174 freeze pre-TOK string-face inventory",
    "faces": {
        "pf_block_len": len(blk_pf), "n1_entry_len": len(entry173),
        "mat_block_len": len(blk_mat), "claim_len": len(claim173),
    },
    "pf_block_eol_crlf": blk_pf.count("\r\n"),
    "n1_entry_eol_crlf": entry173.count("\r\n"),
    "mat_block_eol_crlf": blk_mat.count("\r\n"),
    "claim_eol_crlf": claim173.count("\r\n"),
    "mat_chain_rows": re.findall(r"assert pf\.N1_BANDS\[(\d+)\]",
                                 blk_mat[blk_mat.find("assert pf.N1_BANDS[138]"):
                                         blk_mat.find("# prior-wave disjointness")]),
    "needles": {},
}
needles = [
    # row + entry carriers
    '173: {"a": (395_404, 397_403), "b_exit": (397_404, 397_603),',
    '173: {"batch"',
    # seed-base rows (entry comment face)
    '"a_seed_base": 395_404,',
    '"b_exit_seed_base": 397_404,',
    # dotted bands (W173 geometry)
    "395_404..397_403", "397_404..397_603", "395_204..397_203",
    "395_404..395_603",
    # W174 projection prose inside W173 blocks (physical fragment shape)
    "397_404..399_403", "397_604..397_803",
    "W174 A window; W174 freezer MUST re-derive on the post-W173",
    # identity strings
    "PERPETUAL_N1_W173_PREREG.md", "PERPETUAL-N1-W173", "n1_w173_results.json",
    "n1_w173", "n1w173", "_r820bma", "MSG-2026-10-07-1122", "9cd8af3af",
    "783,812", "376,320", "ONE HUNDRED-AND-SIXTY-THIRD",
    "engine_owner rows 162", "rows 88 + candidate", "eighty-ninth",
    "THIRTY-THIRD", "thirty-second", "r822", "r820", "r823", "W173", "W172", "W174",
    "173", "172", "174",
    # set() asserts
    "set(range(395_404, 397_404))", "set(range(397_404, 397_604))",
    "== 395_404 == 395_403 + 1", "== 397_404 == 397_403 + 1",
    "395_403+1", "397_403+1",
    # seat delivery / self-ack prose (honesty faces)
    "self-ack inbox->processed archive ALREADY LANDED",
    "bm-c r672 inbox sweep observed-archived",
    "the W173 seat MSG sits in",
    # registered-row sha citations
    "bm-a r819 freeze 59fde9319",
    "W172 row bm-a r819 freeze",
    "59fde9319, SINGLE STATE zero seat gap W2..W172 all",
    "59fde9319", "04e95748a",
    # jump phrases (physical fragment shapes)
    "own-wave A window reserved jumps to 397_404, first-clean ",
    "jumps to 397_404, first-clean 397_404..397_603 hops=1",
    "jumps to 397_404 -> 397_404..397_603,",
    "397_404 and lands 397_404..397_603",
    # freeze-session / prior-finalize / receipt / gate-session composites
    "bm-a r822 freeze", "r822 bm-a freeze", "r822 bm-a] ",
    "W172 finalize landed same-window r819",
    "W172 finalize one-pass bm-a r819", "W172 bm-a r819 one-pass",
    "finalize one-pass bm-a r819",
    "_r820bma_w173_probe_receipt.json",
    "r820 pre-seat push", "r818 probe leg4",
    # seat tokens
    "bma-w173-seat", "MSG-1122",
    # payload faces (3-item truth landed at r823)
    "payload = seat MSG + pre-seat probe script + probe receipt",
    "(3-item; the W172 finalize product already on origin since r819",
    "direct fast-forward behind-0",
    # single-window derive faces
    "single-window derive (r812 merged the gate legs INTO the",
    # sec8 succession face (r823 settle -- cited again by W174 because
    # the W173 sec8 succession notes landed r823)
    "r819 sec8 succession",
]
for n in needles:
    receipt["needles"][n] = {
        "pf": pfsrc.count(n), "n1": n1src.count(n),
        "pf_blk": blk_pf.count(n), "entry": entry173.count(n),
        "mat": blk_mat.count(n), "claim": claim173.count(n),
    }
io.open(r"results\_r826bma_w174_face_probe_receipt.json", "w", encoding="utf-8").write(
    json.dumps(receipt, indent=1, ensure_ascii=False))
print("probe rc0: pf_blk", len(blk_pf), "entry", len(entry173),
      "mat", len(blk_mat), "claim", len(claim173),
      "chain_n", len(receipt["mat_chain_rows"]),
      "chain_tail", receipt["mat_chain_rows"][-3:])
