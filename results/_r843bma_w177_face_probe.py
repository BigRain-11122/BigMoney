# -*- coding: utf-8 -*-
"""r843 bm-a W177 freeze pre-TOK empirical probe (r773 pit law leg 1:
full string-face inventory BEFORE writing TOK; r776 law: needles taken
from PHYSICAL fragment shapes). Dumps the four W176 faces (pf comment
block+row / n1 WAVE_CONFIGS entry / n1 materializer block / n1 PASS
claim) to receipt files + counts every needle the W177 freeze uses.
Bloodline: r819/r822/r826/r830/r834 face-probe machinery; W177 facts:
  - pre-seat probe results/_r841bma_w177_probe_receipt.json rc0 ADMIT
    (leg0 registry 174 rows tail W176 ordinal 167 / bma_ordinal 93;
    leg1 A 404_204..406_203 staircase THIRTY-SEVENTH instance E36
    hops=1 past the registered W176 B band 404_004..404_203; naive
    404_004..406_003 refused at its own start by the W176 B band --
    receipt A_semantics machine-cites 'W176 seat MSG leg4 + r832 probe
    leg4 anticipated + MANDATED this re-derive' (W176 sec5.5 prose
    anticipated 37th -- projection and receipt ordinals MATCH, no
    divergence face this wave); B 406_204..406_403 own-A mutual
    exclusion hops=1, naive 404_204..404_403; leg2 conflicts 0;
    leg3 origin vacancy True; leg4 W178+ projection A
    406_204..408_203 hops=0 / B 406_404..406_603 hops=0, B inside A);
  - W177 has ONE receipt (merged-gate probe structure inherited from
    r812/r814/r818/r820/r823/r828/r832/r841: leg0 registry / leg1
    bands+hops+semantics / leg2 conflicts / leg3 origin vacancy /
    leg4 W178+ projection);
  - seat MSG-2026-10-07-2031-bma-w177-seat published (r841 pre-seat
    push 780a0cd30 path-derived TRUE landed sha per r812 precedent;
    r565 law: on origin BEFORE this freeze commit; seat MSG self-ack
    inbox->processed move landed the r841 same window);
  - registered W176 freeze sha machine-derived = 15ec44ea6 (git log
    origin/main --grep "W176 FREEZE"); W176 finalize one-pass landed
    r839 (results/perpetual_faces/n1_w176_results.json: merged
    K=385,120, ledger head 793,105)."""
import io
import json
import re

PF = r"scripts/perpetual_faces.py"
N1 = r"scripts/perpetual_faces_n1.py"
EO = '"engine_owner": "bm-a"},'

pfsrc = io.open(PF, encoding="utf-8", newline="").read()
n1src = io.open(N1, encoding="utf-8", newline="").read()

# face 1: pf W176 comment block + row
i1 = pfsrc.find("    # W176 (bm-a r834 freeze")
assert i1 > 0, "pf W176 comment block not found"
r1 = pfsrc.find('176: {"a": (402_004', i1)
assert r1 > i1, "pf W176 row not after comment block"
j1 = pfsrc.find(EO, r1) + len(EO)
blk_pf = pfsrc[i1:j1]
io.open(r"results\_r843bma_w177_probe_pf_block.txt", "w", encoding="utf-8", newline="").write(blk_pf)

# face 2: n1 WAVE_CONFIGS W176 entry
k = n1src.find('176: {"batch"')
assert k > 0, "n1 W176 entry not found"
m = n1src.find(EO, k) + len(EO)
entry176 = n1src[k:m]
io.open(r"results\_r843bma_w177_probe_n1_entry.txt", "w", encoding="utf-8", newline="").write(entry176)

# face 3: n1 W176 materializer block
w = n1src.find("# --- W176 materializer face")
t2 = n1src.find("# --- T-141 s2 lane face", w)
assert 0 < w < t2, "materializer anchors missing"
blk_mat = n1src[w:t2]
io.open(r"results\_r843bma_w177_probe_n1_mat.txt", "w", encoding="utf-8", newline="").write(blk_mat)

# face 4: n1 PASS snippet claim (r776 physical-shape law: the W176 claim
# trailing session marker is "r834 bm-a] " -- the actual r834 freeze
# session attribution; the W177 tool rolls it to the new session)
cs = n1src.find('"+ W176 materializer face')
ce = n1src.find('"r834 bm-a] "', cs) + len('"r834 bm-a] "')
assert 0 < cs < ce, "W176 claim anchors missing"
claim176 = n1src[cs:ce]
io.open(r"results\_r843bma_w177_probe_n1_claim.txt", "w", encoding="utf-8", newline="").write(claim176)

receipt = {
    "probe": "r843 W177 freeze pre-TOK string-face inventory",
    "faces": {
        "pf_block_len": len(blk_pf), "n1_entry_len": len(entry176),
        "mat_block_len": len(blk_mat), "claim_len": len(claim176),
    },
    "pf_block_eol_crlf": blk_pf.count("\r\n"),
    "n1_entry_eol_crlf": entry176.count("\r\n"),
    "mat_block_eol_crlf": blk_mat.count("\r\n"),
    "claim_eol_crlf": claim176.count("\r\n"),
    "mat_chain_rows": re.findall(r"assert pf\.N1_BANDS\[(\d+)\]",
                                 blk_mat[blk_mat.find("assert pf.N1_BANDS[138]"):
                                         blk_mat.find("# prior-wave disjointness")]),
    "needles": {},
}
needles = [
    # row + entry carriers
    '176: {"a": (402_004, 404_003), "b_exit": (404_004, 404_203),',
    '176: {"batch"',
    # seed-base rows (entry comment face)
    '"a_seed_base": 402_004,',
    '"b_exit_seed_base": 404_004,',
    # dotted bands (W176 geometry)
    "402_004..404_003", "404_004..404_203", "401_804..403_803",
    "402_004..402_203",
    # W177 projection prose inside W176 blocks (physical fragment shape)
    "404_004..406_003", "404_204..404_403",
    "W177 A window; W177 freezer MUST re-derive on the post-W176",
    # identity strings
    "PERPETUAL_N1_W176_PREREG.md", "PERPETUAL-N1-W176", "n1_w176_results.json",
    "n1_w176", "n1w176", "_r832bma", "MSG-2026-10-07-1630", "16a8ea982",
    "790,412", "382,920", "ONE HUNDRED-AND-SIXTY-SIXTH",
    "engine_owner rows 165", "rows 91 + candidate", "ninety-second",
    "THIRTY-SIXTH", "thirty-sixth", "r834", "r832", "r831", "r839", "r833", "W176", "W175", "W177",
    "175", "176", "177",
    # set() asserts
    "set(range(402_004, 404_004))", "set(range(404_004, 404_204))",
    "== 402_004 == 402_003 + 1", "== 404_004 == 404_003 + 1",
    "402_003+1", "404_003+1",
    # seat delivery / self-ack prose (honesty faces)
    "self-ack inbox->processed archive ALREADY LANDED",
    "r833 same-window self-ack move",
    "the W176 seat MSG sits in",
    # registered-row sha citations
    "bm-a r830 freeze db42a0d46",
    "W175 row bm-a r830 freeze",
    "f3fca4055, SINGLE STATE zero seat gap W2..W175 all",
    "f3fca4055", "15ec44ea6",
    # jump phrases (physical fragment shapes)
    "own-wave A window reserved jumps to 404_004, first-clean ",
    "jumps to 404_004, first-clean 404_004..404_203 hops=1",
    "jumps to 404_004 -> 404_004..404_203,",
    "404_004 and lands 404_004..404_203",
    # freeze-session / prior-finalize / receipt / gate-session composites
    "bm-a r834 freeze", "r834 bm-a freeze", "r834 bm-a] ",
    "W175 finalize landed same-window r831",
    "W175 finalize one-pass bm-a r831", "W175 bm-a r831 one-pass",
    "finalize one-pass bm-a r831",
    "_r832bma_w176_probe_receipt.json",
    "r832 pre-seat push", "r828 probe leg4",
    # seat tokens
    "bma-w176-seat", "MSG-1630",
    # payload faces (3-item truth landed at r832)
    "payload = seat MSG + pre-seat probe script + probe receipt",
    "(3-item; the W175 finalize product already on origin since r831",
    "direct fast-forward behind-0",
    # single-window derive faces
    "single-window derive (r812 merged the gate legs INTO the",
    # sec8 succession face (r831 settle -- cited by W176 because the
    # W175 sec8 succession notes landed r831; W176 sec8 settled
    # r839 one-pass per the r842 prereg facts)
    "r831 sec8 succession",
]
for n in needles:
    receipt["needles"][n] = {
        "pf": pfsrc.count(n), "n1": n1src.count(n),
        "pf_blk": blk_pf.count(n), "entry": entry176.count(n),
        "mat": blk_mat.count(n), "claim": claim176.count(n),
    }
io.open(r"results\_r843bma_w177_face_probe_receipt.json", "w", encoding="utf-8").write(
    json.dumps(receipt, indent=1, ensure_ascii=False))
print("probe rc0: pf_blk", len(blk_pf), "entry", len(entry176),
      "mat", len(blk_mat), "claim", len(claim176),
      "chain_n", len(receipt["mat_chain_rows"]),
      "chain_tail", receipt["mat_chain_rows"][-3:])
