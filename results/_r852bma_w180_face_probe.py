# -*- coding: utf-8 -*-
"""r852 bm-a W180 freeze pre-TOK empirical probe (r773 pit law leg 1:
full string-face inventory BEFORE writing TOK; r776 law: needles taken
from PHYSICAL fragment shapes). Dumps the four W179 faces (pf comment
block+row / n1 WAVE_CONFIGS entry / n1 materializer block / n1 PASS
claim) to receipt files. Bloodline: r819/r822/r826/r830/r834/r843/
r845/r849 face-probe machinery; W180 facts:
  - pre-seat probe results/_r851bma_w180_probe_receipt.json rc0 ADMIT
    (leg0 registry 177 rows tail W179 ordinal 170 / bma_ordinal 96;
    leg1 A 410_804..412_803 staircase FORTIETH instance E36 hops=1
    past the registered W179 B band 410_604..410_803; naive
    410_604..412_603 refused at its own start by the W179 B band --
    receipt A_semantics machine-cites 'r848 W179 probe leg4
    anticipated + MANDATED this re-derive' (W179 sec5.5 prose
    anticipated 40th -- projection and receipt ordinals MATCH, no
    divergence face this wave); B 412_804..413_003 own-A mutual
    exclusion hops=1, naive 410_804..411_003; leg2 conflicts 0;
    leg3 origin vacancy True; leg4 W181+ projection A
    412_804..414_803 hops=0 / B 413_004..413_203 hops=0, B inside A);
  - seat MSG-2026-10-08-0030-bma-w180-seat published (r851 pre-seat
    push d3b0737fe path-derived TRUE landed sha per r812 precedent;
    r565 law: on origin BEFORE this freeze commit; seat MSG self-ack
    inbox->processed move landed the r851 same window, e069782f7);
  - registered W179 freeze sha machine-derived = ef540bf8f (git log
    origin/main --grep "W179 FREEZE"); W179 finalize landed r850
    one-pass adoption closeout (results/perpetual_faces/
    n1_w179_results.json: merged K=391,720, ledger head 799,705)."""
import io
import json
import re

PF = r"scripts/perpetual_faces.py"
N1 = r"scripts/perpetual_faces_n1.py"
EO = '"engine_owner": "bm-a"},'

pfsrc = io.open(PF, encoding="utf-8", newline="").read()
n1src = io.open(N1, encoding="utf-8", newline="").read()

# face 1: pf W179 comment block + row
i1 = pfsrc.find("    # W179 (bm-a r849 freeze")
assert i1 > 0, "pf W179 comment block not found"
r1 = pfsrc.find('179: {"a": (408_604', i1)
assert r1 > i1, "pf W179 row not after comment block"
j1 = pfsrc.find(EO, r1) + len(EO)
blk_pf = pfsrc[i1:j1]
io.open(r"results\_r852bma_w180_probe_pf_block.txt", "w", encoding="utf-8", newline="").write(blk_pf)

# face 2: n1 WAVE_CONFIGS W179 entry
k = n1src.find('179: {"batch"')
assert k > 0, "n1 W179 entry not found"
m = n1src.find(EO, k) + len(EO)
entry179 = n1src[k:m]
io.open(r"results\_r852bma_w180_probe_n1_entry.txt", "w", encoding="utf-8", newline="").write(entry179)

# face 3: n1 W179 materializer block
w = n1src.find("# --- W179 materializer face")
t2 = n1src.find("# --- T-141 s2 lane face", w)
assert 0 < w < t2, "materializer anchors missing"
blk_mat = n1src[w:t2]
io.open(r"results\_r852bma_w180_probe_n1_mat.txt", "w", encoding="utf-8", newline="").write(blk_mat)

# face 4: n1 PASS snippet claim (r776 physical-shape law: the W179 claim
# trailing session marker is "r849 bm-a] " -- the actual r849 freeze
# session attribution; the W180 tool rolls it to the new session)
cs = n1src.find('"+ W179 materializer face')
ce = n1src.find('"r849 bm-a] "', cs) + len('"r849 bm-a] "')
assert 0 < cs < ce, "W179 claim anchors missing"
claim179 = n1src[cs:ce]
io.open(r"results\_r852bma_w180_probe_n1_claim.txt", "w", encoding="utf-8", newline="").write(claim179)

receipt = {
    "probe": "r852 W180 freeze pre-TOK string-face inventory",
    "faces": {
        "pf_block_len": len(blk_pf), "n1_entry_len": len(entry179),
        "mat_block_len": len(blk_mat), "claim_len": len(claim179),
    },
    "pf_block_eol_crlf": blk_pf.count("\r\n"),
    "n1_entry_eol_crlf": entry179.count("\r\n"),
    "mat_block_eol_crlf": blk_mat.count("\r\n"),
    "claim_eol_crlf": claim179.count("\r\n"),
    "mat_chain_rows": re.findall(r"assert pf\.N1_BANDS\[(\d+)\]",
                                 blk_mat[blk_mat.find("assert pf.N1_BANDS[138]"):
                                         blk_mat.find("# prior-wave disjointness")]),
    "needles": {},
}
needles = [
    # row + entry carriers
    '179: {"a": (408_604, 410_603), "b_exit": (410_604, 410_803),',
    '179: {"batch"',
    # seed-base rows (entry comment face)
    '"a_seed_base": 408_604,',
    '"b_exit_seed_base": 410_604,',
    # dotted bands (W179 geometry)
    "408_604..410_603", "410_604..410_803",
    # W180 projection prose inside W179 blocks (physical fragment shape)
    "410_604..412_603", "410_804..411_003",
    "W180 A window; W180 freezer MUST re-derive on the post-W179",
    # identity strings
    "PERPETUAL_N1_W179_PREREG.md", "PERPETUAL-N1-W179", "n1_w179_results.json",
    "n1_w179", "n1w179", "_r848bma", "MSG-2026-10-07-2320", "de4716da2",
    "4c645c95f", "797,505", "389,520", "ONE HUNDRED-AND-SIXTY-NINTH",
    "engine_owner rows 168", "rows 94 + candidate", "ninety-fifth",
    "THIRTY-NINTH", "thirty-ninth", "r849", "r848", "r845", "r850", "r846", "W179", "W178", "W180",
    "178", "179", "180", "177",
    # set() asserts
    "set(range(408_604, 410_604))", "set(range(410_604, 410_804))",
    "== 408_604 == 408_603 + 1", "== 410_604 == 410_603 + 1",
    "408_603+1", "410_603+1",
    # seat delivery / self-ack prose (honesty faces)
    "self-ack inbox->processed archive ALREADY LANDED",
    "r848 same-window self-ack move",
    "the W179 seat MSG sits in",
    # registered-row sha citations
    "bm-a r845 freeze de4716da2",
    "W178 row bm-a r845 freeze",
    "W178 finalize landed same-window r827",
    "W178 finalize one-pass bm-a r846", "W178 bm-a r846 one-pass",
    "finalize one-pass bm-a r846",
    "_r848bma_w179_probe_receipt.json",
    "r848 pre-seat push", "r844 probe leg4",
    # seat tokens
    "bma-w179-seat", "MSG-2320",
    # payload faces
    "payload = seat MSG + pre-seat probe script + probe receipt",
    "(3-item; the W178 finalize product already on origin since r846",
    "direct fast-forward behind-0",
    # single-window derive faces
    "single-window derive (r812 merged the gate legs INTO the",
    "single-window derive -- r812 merged the gate",
    # sec8 succession face (r850 settle -- cited by W180)
    "r846 sec8 succession",
    # jump phrases (physical fragment shapes)
    "own-wave A window reserved jumps to 410_604 -> ",
    "jumps to 410_604 -> 410_604..410_803,",
    "410_604 and lands 410_604..410_803",
    "hops=1 -> 410_804..412_803",
]
for n in needles:
    receipt["needles"][n] = {
        "pf": pfsrc.count(n), "n1": n1src.count(n),
        "pf_blk": blk_pf.count(n), "entry": entry179.count(n),
        "mat": blk_mat.count(n), "claim": claim179.count(n),
    }
io.open(r"results\_r852bma_w180_face_probe_receipt.json", "w", encoding="utf-8").write(
    json.dumps(receipt, indent=1, ensure_ascii=False))
print("probe rc0: pf_blk", len(blk_pf), "entry", len(entry179),
      "mat", len(blk_mat), "claim", len(claim179),
      "chain_n", len(receipt["mat_chain_rows"]),
      "chain_tail", receipt["mat_chain_rows"][-3:])
