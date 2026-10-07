# -*- coding: utf-8 -*-
"""r849 bm-a W179 freeze pre-TOK empirical probe (r773 pit law leg 1:
full string-face inventory BEFORE writing TOK; r776 law: needles taken
from PHYSICAL fragment shapes). Dumps the four W178 faces (pf comment
block+row / n1 WAVE_CONFIGS entry / n1 materializer block / n1 PASS
claim) to receipt files. Bloodline: r819/r822/r826/r830/r834/r843/r845
face-probe machinery; W179 facts:
  - pre-seat probe results/_r848bma_w179_probe_receipt.json rc0 ADMIT
    (leg0 registry 176 rows tail W178 ordinal 169 / bma_ordinal 95;
    leg1 A 408_604..410_603 staircase THIRTY-NINTH instance E36
    hops=1 past the registered W178 B band 408_404..408_603; naive
    408_404..410_403 refused at its own start by the W178 B band --
    receipt A_semantics machine-cites 'r844 W178 probe leg4
    anticipated + MANDATED this re-derive' (W178 sec5.5 prose
    anticipated 39th -- projection and receipt ordinals MATCH, no
    divergence face this wave); B 410_604..410_803 own-A mutual
    exclusion hops=1, naive 408_604..408_803; leg2 conflicts 0;
    leg3 origin vacancy True; leg4 W180+ projection A
    410_604..412_603 hops=0 / B 410_804..411_003 hops=0, B inside A);
  - seat MSG-2026-10-07-2320-bma-w179-seat published (r848 pre-seat
    push 4c645c95f path-derived TRUE landed sha per r812 precedent;
    r565 law: on origin BEFORE this freeze commit; seat MSG self-ack
    inbox->processed move landed the r848 same window);
  - registered W178 freeze sha machine-derived = de4716da2 (git log
    origin/main --grep "W178 FREEZE"); W178 finalize landed r846
    one-pass adoption closeout (results/perpetual_faces/
    n1_w178_results.json: merged K=389,520, ledger head 797,505)."""
import io
import json
import re

PF = r"scripts/perpetual_faces.py"
N1 = r"scripts/perpetual_faces_n1.py"
EO = '"engine_owner": "bm-a"},'

pfsrc = io.open(PF, encoding="utf-8", newline="").read()
n1src = io.open(N1, encoding="utf-8", newline="").read()

# face 1: pf W178 comment block + row
i1 = pfsrc.find("    # W178 (bm-a r845 freeze")
assert i1 > 0, "pf W178 comment block not found"
r1 = pfsrc.find('178: {"a": (406_404', i1)
assert r1 > i1, "pf W178 row not after comment block"
j1 = pfsrc.find(EO, r1) + len(EO)
blk_pf = pfsrc[i1:j1]
io.open(r"results\_r849bma_w179_probe_pf_block.txt", "w", encoding="utf-8", newline="").write(blk_pf)

# face 2: n1 WAVE_CONFIGS W178 entry
k = n1src.find('178: {"batch"')
assert k > 0, "n1 W178 entry not found"
m = n1src.find(EO, k) + len(EO)
entry178 = n1src[k:m]
io.open(r"results\_r849bma_w179_probe_n1_entry.txt", "w", encoding="utf-8", newline="").write(entry178)

# face 3: n1 W178 materializer block
w = n1src.find("# --- W178 materializer face")
t2 = n1src.find("# --- T-141 s2 lane face", w)
assert 0 < w < t2, "materializer anchors missing"
blk_mat = n1src[w:t2]
io.open(r"results\_r849bma_w179_probe_n1_mat.txt", "w", encoding="utf-8", newline="").write(blk_mat)

# face 4: n1 PASS snippet claim (r776 physical-shape law: the W178 claim
# trailing session marker is "r845 bm-a] " -- the actual r845 freeze
# session attribution; the W179 tool rolls it to the new session)
cs = n1src.find('"+ W178 materializer face')
ce = n1src.find('"r845 bm-a] "', cs) + len('"r845 bm-a] "')
assert 0 < cs < ce, "W178 claim anchors missing"
claim178 = n1src[cs:ce]
io.open(r"results\_r849bma_w179_probe_n1_claim.txt", "w", encoding="utf-8", newline="").write(claim178)

receipt = {
    "probe": "r849 W179 freeze pre-TOK string-face inventory",
    "faces": {
        "pf_block_len": len(blk_pf), "n1_entry_len": len(entry178),
        "mat_block_len": len(blk_mat), "claim_len": len(claim178),
    },
    "pf_block_eol_crlf": blk_pf.count("\r\n"),
    "n1_entry_eol_crlf": entry178.count("\r\n"),
    "mat_block_eol_crlf": blk_mat.count("\r\n"),
    "claim_eol_crlf": claim178.count("\r\n"),
    "mat_chain_rows": re.findall(r"assert pf\.N1_BANDS\[(\d+)\]",
                                 blk_mat[blk_mat.find("assert pf.N1_BANDS[138]"):
                                         blk_mat.find("# prior-wave disjointness")]),
    "needles": {},
}
needles = [
    # row + entry carriers
    '178: {"a": (406_404, 408_403), "b_exit": (408_404, 408_603),',
    '178: {"batch"',
    # seed-base rows (entry comment face)
    '"a_seed_base": 406_404,',
    '"b_exit_seed_base": 408_404,',
    # dotted bands (W178 geometry)
    "406_404..408_403", "408_404..408_603",
    # W179 projection prose inside W178 blocks (physical fragment shape)
    "408_404..410_403", "408_604..408_803",
    "W179 A window; W179 freezer MUST re-derive on the post-W178",
    # identity strings
    "PERPETUAL_N1_W178_PREREG.md", "PERPETUAL-N1-W178", "n1_w178_results.json",
    "n1_w178", "n1w178", "_r844bma", "MSG-2026-10-07-2157", "c06cc230f",
    "5b9284c79", "795,305", "387,320", "ONE HUNDRED-AND-SIXTY-EIGHTH",
    "engine_owner rows 167", "rows 93 + candidate", "ninety-fourth",
    "THIRTY-EIGHTH", "thirty-eighth", "r845", "r844", "r843", "r846", "r842", "W178", "W177", "W179",
    "177", "178", "179", "176",
    # set() asserts
    "set(range(406_404, 408_404))", "set(range(408_404, 408_604))",
    "== 406_404 == 406_403 + 1", "== 408_404 == 408_403 + 1",
    "406_403+1", "408_403+1",
    # seat delivery / self-ack prose (honesty faces)
    "self-ack inbox->processed archive ALREADY LANDED",
    "r845 same-window self-ack move",
    "the W178 seat MSG sits in",
    # registered-row sha citations
    "bm-a r843 freeze c06cc230f",
    "W177 row bm-a r843 freeze",
    "W177 finalize landed same-window r827",
    "W177 finalize one-pass bm-a r844", "W177 bm-a r844 one-pass",
    "finalize one-pass bm-a r844",
    "_r844bma_w178_probe_receipt.json",
    "r844 pre-seat push", "r841 probe leg4",
    # seat tokens
    "bma-w178-seat", "MSG-2150",
    # payload faces
    "payload = seat MSG + pre-seat probe script + probe receipt",
    "(3-item; the W177 finalize product already on origin since r844",
    "direct fast-forward behind-0",
    # single-window derive faces
    "single-window derive (r812 merged the gate legs INTO the",
    "single-window derive -- r812 merged the gate",
    # sec8 succession face (r846 settle -- cited by W179)
    "r844 sec8 succession",
    # jump phrases (physical fragment shapes)
    "own-wave A window reserved jumps to 408_404 -> ",
    "jumps to 408_404 -> 408_404..408_603,",
    "408_404 and lands 408_404..408_603",
    "hops=1 -> 408_604..410_603",
]
for n in needles:
    receipt["needles"][n] = {
        "pf": pfsrc.count(n), "n1": n1src.count(n),
        "pf_blk": blk_pf.count(n), "entry": entry178.count(n),
        "mat": blk_mat.count(n), "claim": claim178.count(n),
    }
io.open(r"results\_r849bma_w179_face_probe_receipt.json", "w", encoding="utf-8").write(
    json.dumps(receipt, indent=1, ensure_ascii=False))
print("probe rc0: pf_blk", len(blk_pf), "entry", len(entry178),
      "mat", len(blk_mat), "claim", len(claim178),
      "chain_n", len(receipt["mat_chain_rows"]),
      "chain_tail", receipt["mat_chain_rows"][-3:])
