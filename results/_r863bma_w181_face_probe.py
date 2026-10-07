# -*- coding: utf-8 -*-
"""r863 bm-a W181 freeze pre-TOK empirical probe (r773 pit law leg 1:
full string-face inventory BEFORE writing TOK; r776 law: needles taken
from PHYSICAL fragment shapes). Dumps the four W180 faces (pf comment
block+row / n1 WAVE_CONFIGS entry / n1 materializer block / n1 PASS
claim) to receipt files. Bloodline: r819/r822/r826/r830/r834/r843/
r845/r849/r852 face-probe machinery rolled one generation; W181 facts:
  - pre-seat probe results/_r862bma_w181_probe_receipt.json rc0 ADMIT
    (leg0 registry 178 rows tail W180 ordinal 171 / bma_ordinal 97;
    leg1 A 413_004..415_003 staircase FORTY-FIRST instance E36 hops=1
    past the registered W180 B band 412_804..413_003; naive
    412_804..414_803 refused at its own start by the W180 B band --
    receipt A_semantics machine-cites 'r851 W180 probe leg4
    anticipated + MANDATED this re-derive' (W180 sec5.5 prose
    anticipated 41st -- projection and receipt ordinals MATCH, no
    divergence face this wave); B 415_004..415_203 own-A mutual
    exclusion hops=1, naive 413_004..413_203; leg2 conflicts 0;
    leg3 origin vacancy True; leg4 W182+ projection A
    415_004..417_003 hops=0 / B 415_204..415_403 hops=0, B inside A);
  - seat MSG-2026-10-08-0505-bma-w181-seat published (r862 pre-seat
    push 971316069 path-derived TRUE landed sha per r812 precedent;
    r565 law: on origin BEFORE this freeze commit; seat MSG self-ack
    inbox->processed move landed the r863 same window, 61ab7d60a);
  - registered W180 freeze sha machine-derived = 568848aa4 (git log
    origin/main --grep "W180 FREEZE"); W180 finalize landed r854
    one-pass same-window (results/perpetual_faces/
    n1_w180_results.json: merged K=393,920, ledger head 801,905)."""
import io
import json
import re

PF = r"scripts/perpetual_faces.py"
N1 = r"scripts/perpetual_faces_n1.py"
EO = '"engine_owner": "bm-a"},'

pfsrc = io.open(PF, encoding="utf-8", newline="").read()
n1src = io.open(N1, encoding="utf-8", newline="").read()

# face 1: pf W180 comment block + row
i1 = pfsrc.find("    # W180 (bm-a r852 freeze")
assert i1 > 0, "pf W180 comment block not found"
r1 = pfsrc.find('180: {"a": (410_804', i1)
assert r1 > i1, "pf W180 row not after comment block"
j1 = pfsrc.find(EO, r1) + len(EO)
blk_pf = pfsrc[i1:j1]
io.open(r"results\_r863bma_w181_probe_pf_block.txt", "w", encoding="utf-8", newline="").write(blk_pf)

# face 2: n1 WAVE_CONFIGS W180 entry
k = n1src.find('180: {"batch"')
assert k > 0, "n1 W180 entry not found"
m = n1src.find(EO, k) + len(EO)
entry180 = n1src[k:m]
io.open(r"results\_r863bma_w181_probe_n1_entry.txt", "w", encoding="utf-8", newline="").write(entry180)

# face 3: n1 W180 materializer block
w = n1src.find("# --- W180 materializer face")
t2 = n1src.find("# --- T-141 s2 lane face", w)
assert 0 < w < t2, "materializer anchors missing"
blk_mat = n1src[w:t2]
io.open(r"results\_r863bma_w181_probe_n1_mat.txt", "w", encoding="utf-8", newline="").write(blk_mat)

# face 4: n1 PASS snippet claim (r776 physical-shape law: the W180 claim
# trailing session marker is "r852 bm-a] " -- the actual r852 freeze
# session attribution; the W181 tool rolls it to the new session)
cs = n1src.find('"+ W180 materializer face')
ce = n1src.find('"r852 bm-a] "', cs) + len('"r852 bm-a] "')
assert 0 < cs < ce, "W180 claim anchors missing"
claim180 = n1src[cs:ce]
io.open(r"results\_r863bma_w181_probe_n1_claim.txt", "w", encoding="utf-8", newline="").write(claim180)

receipt = {
    "probe": "r863 W181 freeze pre-TOK string-face inventory",
    "faces": {
        "pf_block_len": len(blk_pf), "n1_entry_len": len(entry180),
        "mat_block_len": len(blk_mat), "claim_len": len(claim180),
    },
    "pf_block_eol_crlf": blk_pf.count("\r\n"),
    "n1_entry_eol_crlf": entry180.count("\r\n"),
    "mat_block_eol_crlf": blk_mat.count("\r\n"),
    "claim_eol_crlf": claim180.count("\r\n"),
    "mat_chain_rows": re.findall(r"assert pf\.N1_BANDS\[(\d+)\]",
                                 blk_mat[blk_mat.find("assert pf.N1_BANDS[138]"):
                                         blk_mat.find("# prior-wave disjointness")]),
    "needles": {},
}
needles = [
    # row + entry carriers
    '180: {"a": (410_804, 412_803), "b_exit": (412_804, 413_003),',
    '180: {"batch"',
    # seed-base rows (entry comment face)
    '"a_seed_base": 410_804,',
    '"b_exit_seed_base": 412_804,',
    # dotted bands (W180 geometry)
    "410_804..412_803", "412_804..413_003",
    # W181 projection prose inside W180 blocks (physical fragment shape)
    "412_804..414_803", "413_004..413_203",
    "W181 A window; W181 freezer MUST re-derive on the post-W180",
    # identity strings
    "PERPETUAL_N1_W180_PREREG.md", "PERPETUAL-N1-W180", "n1_w180_results.json",
    "n1_w180", "n1w180", "_r851bma", "MSG-2026-10-08-0030", "ef540bf8f",
    "d3b0737fe", "799,705", "391,720", "ONE HUNDRED-AND-SEVENTIETH",
    "engine_owner rows 169", "rows 95 + candidate", "ninety-sixth",
    "FORTIETH", "fortieth", "r852", "r851", "r849", "r854", "r850", "W180", "W179", "W181",
    "179", "180", "181", "178",
    # set() asserts
    "set(range(410_804, 412_804))", "set(range(412_804, 413_004))",
    "== 410_804 == 410_803 + 1", "== 412_804 == 412_803 + 1",
    "410_803+1", "412_803+1",
    # seat delivery / self-ack prose (honesty faces)
    "self-ack inbox->processed archive ALREADY LANDED",
    "r851 same-window self-ack move",
    "the W180 seat MSG sits in",
    # registered-row sha citations
    "bm-a r849 freeze ef540bf8f",
    "W179 row bm-a r849 freeze",
    "W179 finalize landed same-window r827",
    "W179 finalize one-pass bm-a r850", "W179 bm-a r850 one-pass",
    "finalize one-pass bm-a r850",
    "_r851bma_w180_probe_receipt.json",
    "r851 pre-seat push", "r848 probe leg4",
    # seat tokens
    "bma-w180-seat", "MSG-0030",
    # payload faces
    "payload = seat MSG + pre-seat probe script + probe receipt",
    "(3-item; the W179 finalize product already on origin since r850",
    "direct fast-forward behind-0",
    # single-window derive faces
    "single-window derive (r812 merged the gate legs INTO the",
    "single-window derive -- r812 merged the gate",
    # sec8 succession face (r854 settle -- cited by W181)
    "r850 sec8 succession",
    # jump phrases (physical fragment shapes)
    "own-wave A window reserved jumps to 412_804 -> ",
    "jumps to 412_804 -> 412_804..413_003,",
    "412_804 and lands 412_804..413_003",
    "hops=1 -> 413_004..415_003",
]
for n in needles:
    receipt["needles"][n] = {
        "pf": pfsrc.count(n), "n1": n1src.count(n),
        "pf_blk": blk_pf.count(n), "entry": entry180.count(n),
        "mat": blk_mat.count(n), "claim": claim180.count(n),
    }
io.open(r"results\_r863bma_w181_face_probe_receipt.json", "w", encoding="utf-8").write(
    json.dumps(receipt, indent=1, ensure_ascii=False))
print("probe rc0: pf_blk", len(blk_pf), "entry", len(entry180),
      "mat", len(blk_mat), "claim", len(claim180),
      "chain_n", len(receipt["mat_chain_rows"]),
      "chain_tail", receipt["mat_chain_rows"][-3:])
