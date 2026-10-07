# -*- coding: utf-8 -*-
"""r867 bm-a W182 freeze pre-TOK empirical probe (r773 pit law leg 1:
full string-face inventory BEFORE writing TOK; r776 law: needles taken
from PHYSICAL fragment shapes). Dumps the four W181 faces (pf comment
block+row / n1 WAVE_CONFIGS entry / n1 materializer block / n1 PASS
claim) to receipt files. Bloodline: r819/r822/r826/r830/r834/r843/
r845/r849/r852/r863 face-probe machinery rolled one generation; W182
facts:
  - pre-seat probe results/_r865bma_w182_probe_receipt.json rc0 ADMIT
    (leg0 registry 179 rows tail W181 ordinal 172 / bma_ordinal 98;
    leg1 A 415_204..417_203 staircase FORTY-SECOND instance E36 hops=1
    past the registered W181 B band 415_004..415_203; naive
    415_004..417_003 refused at its own start by the W181 B band --
    receipt A_semantics machine-cites 'r862 W181 probe leg4
    anticipated + MANDATED this re-derive' (W181 sec5.5 prose
    anticipated 42nd -- projection and receipt ordinals MATCH, no
    divergence face this wave); B 417_204..417_403 own-A mutual
    exclusion hops=1, naive 415_204..415_403; leg2 conflicts 0;
    leg3 origin vacancy True; leg4 W183+ projection A
    417_204..419_203 hops=0 / B 417_404..417_603 hops=0, B inside A);
  - seat MSG-2026-10-08-0603-bma-w182-seat published (r865 pre-seat
    push df062c5c1 path-derived TRUE landed sha per r812 precedent;
    r565 law: on origin BEFORE this freeze commit; seat MSG self-ack
    inbox->processed move landed the r866 window -- processed/ path
    live-verified this window);
  - registered W181 freeze sha machine-derived = de699e8cd (git log
    origin/main --grep "W181 FREEZE"); W181 finalize landed r864
    one-pass same-window (results/perpetual_faces/
    n1_w181_results.json: merged K=396,120, ledger head 804,518);
    W181 sec7/sec8 settle backfill landed the r867 HEAL window
    (r864 miss disclosed, W159/W168/W169/W180 delayed-window
    precedent family)."""
import io
import json
import re

PF = r"scripts/perpetual_faces.py"
N1 = r"scripts/perpetual_faces_n1.py"
EO = '"engine_owner": "bm-a"},'

pfsrc = io.open(PF, encoding="utf-8", newline="").read()
n1src = io.open(N1, encoding="utf-8", newline="").read()

# face 1: pf W181 comment block + row
i1 = pfsrc.find("    # W181 (bm-a r863 freeze")
assert i1 > 0, "pf W181 comment block not found"
r1 = pfsrc.find('181: {"a": (413_004', i1)
assert r1 > i1, "pf W181 row not after comment block"
j1 = pfsrc.find(EO, r1) + len(EO)
blk_pf = pfsrc[i1:j1]
io.open(r"results\_r867bma_w182_probe_pf_block.txt", "w", encoding="utf-8", newline="").write(blk_pf)

# face 2: n1 WAVE_CONFIGS W181 entry
k = n1src.find('181: {"batch"')
assert k > 0, "n1 W181 entry not found"
m = n1src.find(EO, k) + len(EO)
entry181 = n1src[k:m]
io.open(r"results\_r867bma_w182_probe_n1_entry.txt", "w", encoding="utf-8", newline="").write(entry181)

# face 3: n1 W181 materializer block
w = n1src.find("# --- W181 materializer face")
t2 = n1src.find("# --- T-141 s2 lane face", w)
assert 0 < w < t2, "materializer anchors missing"
blk_mat = n1src[w:t2]
io.open(r"results\_r867bma_w182_probe_n1_mat.txt", "w", encoding="utf-8", newline="").write(blk_mat)

# face 4: n1 PASS snippet claim (r776 physical-shape law: the W181 claim
# trailing session marker is "r863 bm-a] " -- the actual r863 freeze
# session attribution; the W182 tool rolls it to the new session)
cs = n1src.find('"+ W181 materializer face')
ce = n1src.find('"r863 bm-a] "', cs) + len('"r863 bm-a] "')
assert 0 < cs < ce, "W181 claim anchors missing"
claim181 = n1src[cs:ce]
io.open(r"results\_r867bma_w182_probe_n1_claim.txt", "w", encoding="utf-8", newline="").write(claim181)

receipt = {
    "probe": "r867 W182 freeze pre-TOK string-face inventory",
    "faces": {
        "pf_block_len": len(blk_pf), "n1_entry_len": len(entry181),
        "mat_block_len": len(blk_mat), "claim_len": len(claim181),
    },
    "pf_block_eol_crlf": blk_pf.count("\r\n"),
    "n1_entry_eol_crlf": entry181.count("\r\n"),
    "mat_block_eol_crlf": blk_mat.count("\r\n"),
    "claim_eol_crlf": claim181.count("\r\n"),
    "mat_chain_rows": re.findall(r"assert pf\.N1_BANDS\[(\d+)\]",
                                 blk_mat[blk_mat.find("assert pf.N1_BANDS[138]"):
                                         blk_mat.find("# prior-wave disjointness")]),
    "needles": {},
}
needles = [
    # row + entry carriers
    '181: {"a": (413_004, 415_003), "b_exit": (415_004, 415_203),',
    '181: {"batch"',
    # seed-base rows (entry comment face)
    '"a_seed_base": 413_004,',
    '"b_exit_seed_base": 415_004,',
    # dotted bands (W181 geometry)
    "413_004..415_003", "415_004..415_203",
    # W182 projection prose inside W181 blocks (physical fragment shape)
    "415_004..417_003", "415_204..415_403",
    "W182 A window; W182 freezer MUST re-derive on the post-W181",
    # identity strings
    "PERPETUAL_N1_W181_PREREG.md", "PERPETUAL-N1-W181", "n1_w181_results.json",
    "n1_w181", "n1w181", "_r862bma", "MSG-2026-10-08-0505", "568848aa4",
    "971316069", "801,905", "393,920", "ONE HUNDRED-AND-SEVENTY-FIRST",
    "engine_owner rows 170", "rows 96 + candidate", "ninety-seventh",
    "FORTY-FIRST", "forty-first", "r863", "r862", "r852", "r854", "r850", "W181", "W180", "W182",
    "180", "181", "182", "179",
    # set() asserts
    "set(range(413_004, 415_004))", "set(range(415_004, 415_204))",
    "== 413_004 == 413_003 + 1", "== 415_004 == 415_003 + 1",
    "413_003+1", "415_003+1",
    # seat delivery / self-ack prose (honesty faces)
    "self-ack inbox->processed archive ALREADY LANDED",
    "r863 same-window self-ack move",
    "the W181 seat MSG sits in",
    # registered-row sha citations
    "bm-a r852 freeze 568848aa4",
    "W180 row bm-a r852 freeze",
    "W180 finalize landed same-window r827",
    "W180 finalize one-pass bm-a r854", "W180 bm-a r854 one-pass",
    "finalize one-pass bm-a r854",
    "_r862bma_w181_probe_receipt.json",
    "r862 pre-seat push", "r851 probe leg4",
    # seat tokens
    "bma-w181-seat", "MSG-0505",
    # payload faces
    "payload = seat MSG + pre-seat probe script + probe receipt",
    "(3-item; the W180 finalize product already on origin since r854",
    "direct fast-forward behind-0",
    # single-window derive faces
    "single-window derive (r812 merged the gate legs INTO the",
    "single-window derive -- r812 merged the gate",
    # sec8 succession face (r854 settle -- cited by W181)
    "r854 sec8 succession",
    # jump phrases (physical fragment shapes)
    "own-wave A window reserved jumps to 415_004 -> ",
    "jumps to 415_004 -> 415_004..415_203,",
    "415_004 and lands 415_004..415_203",
    "hops=1 -> 413_004..415_003",
]
for n in needles:
    receipt["needles"][n] = {
        "pf": pfsrc.count(n), "n1": n1src.count(n),
        "pf_blk": blk_pf.count(n), "entry": entry181.count(n),
        "mat": blk_mat.count(n), "claim": claim181.count(n),
    }
io.open(r"results\_r867bma_w182_face_probe_receipt.json", "w", encoding="utf-8").write(
    json.dumps(receipt, indent=1, ensure_ascii=False))
print("probe rc0: pf_blk", len(blk_pf), "entry", len(entry181),
      "mat", len(blk_mat), "claim", len(claim181),
      "chain_n", len(receipt["mat_chain_rows"]),
      "chain_tail", receipt["mat_chain_rows"][-3:])
