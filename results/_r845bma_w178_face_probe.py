# -*- coding: utf-8 -*-
"""r845 bm-a W178 freeze pre-TOK empirical probe (r773 pit law leg 1:
full string-face inventory BEFORE writing TOK; r776 law: needles taken
from PHYSICAL fragment shapes). Dumps the four W177 faces (pf comment
block+row / n1 WAVE_CONFIGS entry / n1 materializer block / n1 PASS
claim) to receipt files. Bloodline: r819/r822/r826/r830/r834/r843
face-probe machinery; W178 facts:
  - pre-seat probe results/_r844bma_w178_probe_receipt.json rc0 ADMIT
    (leg0 registry 175 rows tail W177 ordinal 168 / bma_ordinal 94;
    leg1 A 406_404..408_403 staircase THIRTY-EIGHTH instance E36
    hops=1 past the registered W177 B band 406_204..406_403; naive
    406_204..408_203 refused at its own start by the W177 B band --
    receipt A_semantics machine-cites 'W177 seat MSG leg4 + r841 probe
    leg4 anticipated + MANDATED this re-derive' (W177 sec5.5 prose
    anticipated 38th -- projection and receipt ordinals MATCH, no
    divergence face this wave); B 408_404..408_603 own-A mutual
    exclusion hops=1, naive 406_404..406_603; leg2 conflicts 0;
    leg3 origin vacancy True; leg4 W179+ projection A
    408_404..410_403 hops=0 / B 408_604..408_803 hops=0, B inside A);
  - seat MSG-2026-10-07-2157-bma-w178-seat published (r845 pre-seat
    push 5b9284c79 path-derived TRUE landed sha per r812 precedent;
    r565 law: on origin BEFORE this freeze commit; seat MSG self-ack
    inbox->processed move landed the r845 same window);
  - registered W177 freeze sha machine-derived = c06cc230f (git log
    origin/main --grep "W177 FREEZE"); W177 finalize landed r844
    dead-tail adopted (results/perpetual_faces/n1_w177_results.json:
    merged K=387,320, ledger head 795,305)."""
import io
import json
import re

PF = r"scripts/perpetual_faces.py"
N1 = r"scripts/perpetual_faces_n1.py"
EO = '"engine_owner": "bm-a"},'

pfsrc = io.open(PF, encoding="utf-8", newline="").read()
n1src = io.open(N1, encoding="utf-8", newline="").read()

# face 1: pf W177 comment block + row
i1 = pfsrc.find("    # W177 (bm-a r843 freeze")
assert i1 > 0, "pf W177 comment block not found"
r1 = pfsrc.find('177: {"a": (404_204', i1)
assert r1 > i1, "pf W177 row not after comment block"
j1 = pfsrc.find(EO, r1) + len(EO)
blk_pf = pfsrc[i1:j1]
io.open(r"results\_r845bma_w178_probe_pf_block.txt", "w", encoding="utf-8", newline="").write(blk_pf)

# face 2: n1 WAVE_CONFIGS W177 entry
k = n1src.find('177: {"batch"')
assert k > 0, "n1 W177 entry not found"
m = n1src.find(EO, k) + len(EO)
entry177 = n1src[k:m]
io.open(r"results\_r845bma_w178_probe_n1_entry.txt", "w", encoding="utf-8", newline="").write(entry177)

# face 3: n1 W177 materializer block
w = n1src.find("# --- W177 materializer face")
t2 = n1src.find("# --- T-141 s2 lane face", w)
assert 0 < w < t2, "materializer anchors missing"
blk_mat = n1src[w:t2]
io.open(r"results\_r845bma_w178_probe_n1_mat.txt", "w", encoding="utf-8", newline="").write(blk_mat)

# face 4: n1 PASS snippet claim (r776 physical-shape law: the W177 claim
# trailing session marker is "r843 bm-a] " -- the actual r843 freeze
# session attribution; the W178 tool rolls it to the new session)
cs = n1src.find('"+ W177 materializer face')
ce = n1src.find('"r843 bm-a] "', cs) + len('"r843 bm-a] "')
assert 0 < cs < ce, "W177 claim anchors missing"
claim177 = n1src[cs:ce]
io.open(r"results\_r845bma_w178_probe_n1_claim.txt", "w", encoding="utf-8", newline="").write(claim177)

receipt = {
    "probe": "r845 W178 freeze pre-TOK string-face inventory",
    "faces": {
        "pf_block_len": len(blk_pf), "n1_entry_len": len(entry177),
        "mat_block_len": len(blk_mat), "claim_len": len(claim177),
    },
    "pf_block_eol_crlf": blk_pf.count("\r\n"),
    "n1_entry_eol_crlf": entry177.count("\r\n"),
    "mat_block_eol_crlf": blk_mat.count("\r\n"),
    "claim_eol_crlf": claim177.count("\r\n"),
    "mat_chain_rows": re.findall(r"assert pf\.N1_BANDS\[(\d+)\]",
                                 blk_mat[blk_mat.find("assert pf.N1_BANDS[138]"):
                                         blk_mat.find("# prior-wave disjointness")]),
    "needles": {},
}
needles = [
    # row + entry carriers
    '177: {"a": (404_204, 406_203), "b_exit": (406_204, 406_403),',
    '177: {"batch"',
    # seed-base rows (entry comment face)
    '"a_seed_base": 404_204,',
    '"b_exit_seed_base": 406_204,',
    # dotted bands (W177 geometry)
    "404_204..406_203", "406_204..406_403",
    # W178 projection prose inside W177 blocks (physical fragment shape)
    "406_204..408_203", "406_404..406_603",
    "W178 A window; W178 freezer MUST re-derive on the post-W177",
    # identity strings
    "PERPETUAL_N1_W177_PREREG.md", "PERPETUAL-N1-W177", "n1_w177_results.json",
    "n1_w177", "n1w177", "_r841bma", "MSG-2026-10-07-2031", "15ec44ea6",
    "780a0cd30", "793,105", "385,120", "ONE HUNDRED-AND-SIXTY-SEVENTH",
    "engine_owner rows 166", "rows 92 + candidate", "ninety-third",
    "THIRTY-SEVENTH", "thirty-seventh", "r843", "r841", "r839", "r844", "r842", "W177", "W176", "W178",
    "176", "177", "178",
    # set() asserts
    "set(range(404_204, 406_204))", "set(range(406_204, 406_404))",
    "== 404_204 == 404_203 + 1", "== 406_204 == 406_203 + 1",
    "404_203+1", "406_203+1",
    # seat delivery / self-ack prose (honesty faces)
    "self-ack inbox->processed archive ALREADY LANDED",
    "r841 same-window self-ack move",
    "the W177 seat MSG sits in",
    # registered-row sha citations
    "bm-a r834 freeze db42a0d46",
    "W176 row bm-a r834 freeze",
    "f3fca4055, SINGLE STATE zero seat gap W2..W176 all",
    "15ec44ea6", "c06cc230f",
    # jump phrases (physical fragment shapes)
    "own-wave A window reserved jumps to 406_204, first-clean ",
    "jumps to 406_204, first-clean 406_204..406_403 hops=1",
    "jumps to 406_204 -> 406_204..406_403,",
    "406_204 and lands 406_204..406_403",
    # freeze-session / prior-finalize / receipt / gate-session composites
    "bm-a r843 freeze", "r843 bm-a freeze", "r843 bm-a] ",
    "W176 finalize landed same-window r827",
    "W176 finalize one-pass bm-a r839", "W176 bm-a r839 one-pass",
    "finalize one-pass bm-a r839",
    "_r841bma_w177_probe_receipt.json",
    "r841 pre-seat push", "r832 probe leg4",
    # seat tokens
    "bma-w177-seat", "MSG-2030",
    # payload faces
    "payload = seat MSG + pre-seat probe script + probe receipt",
    "(3-item; the W176 finalize product already on origin since r839",
    "direct fast-forward behind-0",
    # single-window derive faces
    "single-window derive (r812 merged the gate legs INTO the",
    # sec8 succession face (r839 settle -- cited by W177)
    "r839 sec8 succession",
]
for n in needles:
    receipt["needles"][n] = {
        "pf": pfsrc.count(n), "n1": n1src.count(n),
        "pf_blk": blk_pf.count(n), "entry": entry177.count(n),
        "mat": blk_mat.count(n), "claim": claim177.count(n),
    }
io.open(r"results\_r845bma_w178_face_probe_receipt.json", "w", encoding="utf-8").write(
    json.dumps(receipt, indent=1, ensure_ascii=False))
print("probe rc0: pf_blk", len(blk_pf), "entry", len(entry177),
      "mat", len(blk_mat), "claim", len(claim177),
      "chain_n", len(receipt["mat_chain_rows"]),
      "chain_tail", receipt["mat_chain_rows"][-3:])
