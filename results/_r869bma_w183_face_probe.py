# -*- coding: utf-8 -*-
"""r869 bm-a W183 freeze pre-TOK empirical probe (r773 pit law leg 1:
full string-face inventory BEFORE writing TOK; r776 law: needles taken
from PHYSICAL fragment shapes). Dumps the four W182 faces (pf comment
block+row / n1 WAVE_CONFIGS entry / n1 materializer block / n1 PASS
claim) to receipt files. Bloodline: r819/r822/r826/r830/r834/r843/
r845/r849/r852/r863/r867 face-probe machinery rolled one generation;
W183 facts:
  - pre-seat probe results/_r868bma_w183_probe_receipt.json rc0 ADMIT
    (leg0 registry 180 rows tail W182 ordinal 173 / bma_ordinal 99;
    leg1 A 417_404..419_403 staircase FORTY-THIRD instance E36 hops=1
    past the registered W182 B band 417_204..417_403; naive
    417_204..419_203 refused at its own start by the W182 B band --
    receipt A_semantics machine-cites 'r865 W182 probe leg4
    anticipated + MANDATED this re-derive' (W182 sec5.5 prose
    anticipated 43rd -- projection and receipt ordinals MATCH, no
    divergence face this wave); B 419_404..419_603 own-A mutual
    exclusion hops=1, naive 417_404..417_603; leg2 conflicts 0;
    leg3 origin vacancy True; leg4 W184+ projection A
    419_404..421_403 hops=0 / B 419_604..419_803 hops=0, B inside A);
  - seat MSG-2026-10-08-0741-bma-w183-seat published (r868 pre-seat
    push ccd18034e path-derived TRUE landed sha per r812 precedent;
    r565 law: on origin BEFORE this freeze commit; seat MSG self-ack
    inbox->processed move landed the bm-c r741 window -- processed/
    path live-verified this window);
  - registered W182 freeze sha machine-derived = 385dbafd8 (git log
    origin/main --grep "W182 FREEZE"); W182 finalize landed r868
    one-pass SAME-window (results/perpetual_faces/
    n1_w182_results.json: merged K=398,320, ledger head 806,718);
    W182 sec7/sec8 settle backfill landed the r868 SAME window
    (r864 lesson welded into process -- no heal window needed)."""
import io
import json
import re

PF = r"scripts/perpetual_faces.py"
N1 = r"scripts/perpetual_faces_n1.py"
EO = '"engine_owner": "bm-a"},'

pfsrc = io.open(PF, encoding="utf-8", newline="").read()
n1src = io.open(N1, encoding="utf-8", newline="").read()

# face 1: pf W182 comment block + row
i1 = pfsrc.find("    # W182 (bm-a r867 freeze")
assert i1 > 0, "pf W182 comment block not found"
r1 = pfsrc.find('182: {"a": (415_204', i1)
assert r1 > i1, "pf W182 row not after comment block"
j1 = pfsrc.find(EO, r1) + len(EO)
blk_pf = pfsrc[i1:j1]
io.open(r"results\_r869bma_w183_probe_pf_block.txt", "w", encoding="utf-8", newline="").write(blk_pf)

# face 2: n1 WAVE_CONFIGS W182 entry
k = n1src.find('182: {"batch"')
assert k > 0, "n1 W182 entry not found"
m = n1src.find(EO, k) + len(EO)
entry182 = n1src[k:m]
io.open(r"results\_r869bma_w183_probe_n1_entry.txt", "w", encoding="utf-8", newline="").write(entry182)

# face 3: n1 W182 materializer block
w = n1src.find("# --- W182 materializer face")
t2 = n1src.find("# --- T-141 s2 lane face", w)
assert 0 < w < t2, "materializer anchors missing"
blk_mat = n1src[w:t2]
io.open(r"results\_r869bma_w183_probe_n1_mat.txt", "w", encoding="utf-8", newline="").write(blk_mat)

# face 4: n1 PASS snippet claim (r776 physical-shape law: the W182 claim
# trailing session marker is "r867 bm-a] " -- the actual r867 freeze
# session attribution; the W183 tool rolls it to the new session)
cs = n1src.find('"+ W182 materializer face')
ce = n1src.find('"r867 bm-a] "', cs) + len('"r867 bm-a] "')
assert 0 < cs < ce, "W182 claim anchors missing"
claim182 = n1src[cs:ce]
io.open(r"results\_r869bma_w183_probe_n1_claim.txt", "w", encoding="utf-8", newline="").write(claim182)

receipt = {
    "probe": "r869 W183 freeze pre-TOK string-face inventory",
    "faces": {
        "pf_block_len": len(blk_pf), "n1_entry_len": len(entry182),
        "mat_block_len": len(blk_mat), "claim_len": len(claim182),
    },
    "pf_block_eol_crlf": blk_pf.count("\r\n"),
    "n1_entry_eol_crlf": entry182.count("\r\n"),
    "mat_block_eol_crlf": blk_mat.count("\r\n"),
    "claim_eol_crlf": claim182.count("\r\n"),
    "mat_chain_rows": re.findall(r"assert pf\.N1_BANDS\[(\d+)\]",
                                 blk_mat[blk_mat.find("assert pf.N1_BANDS[138]"):
                                         blk_mat.find("# prior-wave disjointness")]),
    "needles": {},
}
needles = [
    # row + entry carriers
    '182: {"a": (415_204, 417_203), "b_exit": (417_204, 417_403),',
    '182: {"batch"',
    # seed-base rows (entry comment face)
    '"a_seed_base": 415_204,',
    '"b_exit_seed_base": 417_204,',
    # dotted bands (W182 geometry)
    "415_204..417_203", "417_204..417_403",
    # W183 projection prose inside W182 blocks (physical fragment shape)
    "417_204..419_203", "417_404..417_603",
    "W183 A window; W183 freezer MUST re-derive on the post-W182",
    # identity strings
    "PERPETUAL_N1_W182_PREREG.md", "PERPETUAL-N1-W182", "n1_w182_results.json",
    "n1_w182", "n1w182", "_r865bma", "MSG-2026-10-08-0603", "de699e8cd",
    "df062c5c1", "804,518", "396,120", "ONE HUNDRED-AND-SEVENTY-SECOND",
    "engine_owner rows 171", "rows 97 + candidate", "ninety-eighth",
    "FORTY-SECOND", "forty-second", "r867", "r865", "r863", "r864", "r862", "W182", "W181", "W183",
    "181", "182", "183", "180",
    # set() asserts
    "set(range(415_204, 417_204))", "set(range(417_204, 417_404))",
    "== 415_204 == 415_203 + 1", "== 417_204 == 417_203 + 1",
    "415_203+1", "417_203+1",
    # seat delivery / self-ack prose (honesty faces)
    "self-ack inbox->processed archive ALREADY LANDED",
    "bm-c r737-window self-ack move",
    "the W182 seat MSG sits in",
    # registered-row sha citations
    "bm-a r863 freeze de699e8cd",
    "W181 row bm-a r863 freeze",
    "W181 finalize landed same-window r827",
    "W181 finalize one-pass bm-a r864", "W181 bm-a r864 one-pass",
    "finalize one-pass bm-a r864",
    "_r865bma_w182_probe_receipt.json",
    "r865 pre-seat push", "r862 probe leg4",
    # seat tokens
    "bma-w182-seat", "MSG-0603",
    # payload faces
    "payload = seat MSG + pre-seat probe script + probe receipt",
    "(3-item; the W181 finalize product already on origin since r864",
    "direct fast-forward behind-0",
    # single-window derive faces
    "single-window derive (r812 merged the gate legs INTO the",
    "single-window derive -- r812 merged the gate",
    # sec8 succession face (r867 heal -- cited by W182)
    "r867 sec8 heal succession",
    # jump phrases (physical fragment shapes)
    "own-wave A window reserved jumps to 417_204 -> ",
    "jumps to 417_204 -> 417_204..417_403,",
    "417_204 and lands 417_204..417_403",
    "hops=1 -> 415_204..417_203",
]
for n in needles:
    receipt["needles"][n] = {
        "pf": pfsrc.count(n), "n1": n1src.count(n),
        "pf_blk": blk_pf.count(n), "entry": entry182.count(n),
        "mat": blk_mat.count(n), "claim": claim182.count(n),
    }
io.open(r"results\_r869bma_w183_face_probe_receipt.json", "w", encoding="utf-8").write(
    json.dumps(receipt, indent=1, ensure_ascii=False))
print("probe rc0: pf_blk", len(blk_pf), "entry", len(entry182),
      "mat", len(blk_mat), "claim", len(claim182),
      "chain_n", len(receipt["mat_chain_rows"]),
      "chain_tail", receipt["mat_chain_rows"][-3:])
