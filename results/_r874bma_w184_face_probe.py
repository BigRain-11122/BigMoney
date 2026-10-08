# -*- coding: utf-8 -*-
"""r874 bm-a W184 freeze pre-TOK empirical probe (r773 pit law leg 1:
full string-face inventory BEFORE writing TOK; r776 law: needles taken
from PHYSICAL fragment shapes). Dumps the four W183 faces (pf comment
block+row / n1 WAVE_CONFIGS entry / n1 materializer block / n1 PASS
claim) to receipt files. Bloodline: r819/r822/r826/r830/r834/r843/
r845/r849/r852/r863/r867/r869 face-probe machinery rolled one
generation; W184 facts:
  - pre-seat probe results/_r870bma_w184_probe_receipt.json rc0 ADMIT
    (leg0 registry 181 rows tail W183 ordinal 174 / bma_ordinal 100;
    leg1 A 419_604..421_603 staircase FORTY-FOURTH instance E36 hops=1
    past the registered W183 B band 419_404..419_603; naive
    419_404..421_403 refused at its own start by the W183 B band --
    receipt A_semantics machine-cites 'r868 W183 probe leg4 + W183
    seat MSG leg4 + W183 prereg sec5.5/sec8 anticipated and MANDATED
    this re-derive'; B 421_604..421_803 own-A mutual exclusion hops=1,
    naive 419_604..419_803; leg2 conflicts 0; leg3 origin vacancy
    True; leg4 W185+ projection A 421_604..423_603 hops=0 / B
    421_804..422_003 hops=0, B inside A);
  - seat MSG-2026-10-08-0826-bma-w184-seat published (r870 pre-seat
    push d1f15ebf9 path-derived TRUE landed sha per r812 precedent;
    r565 law: on origin BEFORE this freeze commit; seat MSG self-ack
    inbox->processed move landed the bm-c r745 window (1ec9800ae,
    08:24:24, machine-read this window -- the W184 prereg's r741
    citation is a stale session number, superseded by machine-read
    git history, honest; processed/ path live-verified this window);
  - registered W183 freeze sha machine-derived = 481da4d78 (git log
    origin/main --grep "W183 FREEZE"); W183 finalize landed r870
    one-pass SAME-window (results/perpetual_faces/
    n1_w183_results.json: merged K=400,520, ledger head 808,918);
    W183 sec7/sec8 settle backfill landed the r870 SAME window
    (r864 lesson 2nd consecutive)."""
import io
import json
import re

PF = r"scripts/perpetual_faces.py"
N1 = r"scripts/perpetual_faces_n1.py"
EO = '"engine_owner": "bm-a"},'

pfsrc = io.open(PF, encoding="utf-8", newline="").read()
n1src = io.open(N1, encoding="utf-8", newline="").read()

# face 1: pf W183 comment block + row
i1 = pfsrc.find("    # W183 (bm-a r869 freeze")
assert i1 > 0, "pf W183 comment block not found"
r1 = pfsrc.find('183: {"a": (417_404', i1)
assert r1 > i1, "pf W183 row not after comment block"
j1 = pfsrc.find(EO, r1) + len(EO)
blk_pf = pfsrc[i1:j1]
io.open(r"results\_r874bma_w184_probe_pf_block.txt", "w", encoding="utf-8", newline="").write(blk_pf)

# face 2: n1 WAVE_CONFIGS W183 entry
k = n1src.find('183: {"batch"')
assert k > 0, "n1 W183 entry not found"
m = n1src.find(EO, k) + len(EO)
entry183 = n1src[k:m]
io.open(r"results\_r874bma_w184_probe_n1_entry.txt", "w", encoding="utf-8", newline="").write(entry183)

# face 3: n1 W183 materializer block
w = n1src.find("# --- W183 materializer face")
t2 = n1src.find("# --- T-141 s2 lane face", w)
assert 0 < w < t2, "materializer anchors missing"
blk_mat = n1src[w:t2]
io.open(r"results\_r874bma_w184_probe_n1_mat.txt", "w", encoding="utf-8", newline="").write(blk_mat)

# face 4: n1 PASS snippet claim (r776 physical-shape law: the W183 claim
# trailing session marker is "r869 bm-a] " -- the actual r869 freeze
# session attribution; the W184 tool rolls it to the new session)
cs = n1src.find('"+ W183 materializer face')
ce = n1src.find('"r869 bm-a] "', cs) + len('"r869 bm-a] "')
assert 0 < cs < ce, "W183 claim anchors missing"
claim183 = n1src[cs:ce]
io.open(r"results\_r874bma_w184_probe_n1_claim.txt", "w", encoding="utf-8", newline="").write(claim183)

receipt = {
    "probe": "r874 W184 freeze pre-TOK string-face inventory",
    "faces": {
        "pf_block_len": len(blk_pf), "n1_entry_len": len(entry183),
        "mat_block_len": len(blk_mat), "claim_len": len(claim183),
    },
    "pf_block_eol_crlf": blk_pf.count("\r\n"),
    "n1_entry_eol_crlf": entry183.count("\r\n"),
    "mat_block_eol_crlf": blk_mat.count("\r\n"),
    "claim_eol_crlf": claim183.count("\r\n"),
    "mat_chain_rows": re.findall(r"assert pf\.N1_BANDS\[(\d+)\]",
                                 blk_mat[blk_mat.find("assert pf.N1_BANDS[138]"):
                                         blk_mat.find("# prior-wave disjointness")]),
    "needles": {},
}
needles = [
    # row + entry carriers
    '183: {"a": (417_404, 419_403), "b_exit": (419_404, 419_603),',
    '183: {"batch"',
    # seed-base rows (entry comment face)
    '"a_seed_base": 417_404,',
    '"b_exit_seed_base": 419_404,',
    # dotted bands (W183 geometry)
    "417_404..419_403", "419_404..419_603",
    # W184 projection prose inside W183 blocks (physical fragment shape)
    "419_404..421_403", "419_604..419_803",
    "W184 A window; W184 freezer MUST re-derive on the post-W183",
    # identity strings
    "PERPETUAL_N1_W183_PREREG.md", "PERPETUAL-N1-W183", "n1_w183_results.json",
    "n1_w183", "n1w183", "_r868bma", "MSG-2026-10-08-0741", "481da4d78",
    "ccd18034e", "806,718", "398,320", "ONE HUNDRED-AND-SEVENTY-THIRD",
    "engine_owner rows 172", "rows 98 + candidate", "ninety-ninth",
    "FORTY-THIRD", "forty-third", "r869", "r868", "r867", "r870", "r865", "W183", "W182", "W184",
    "182", "183", "184", "181",
    # set() asserts
    "set(range(417_404, 419_404))", "set(range(419_404, 419_604))",
    "== 417_404 == 417_403 + 1", "== 419_404 == 419_403 + 1",
    "417_403+1", "419_403+1",
    # seat delivery / self-ack prose (honesty faces)
    "self-ack inbox->processed archive ALREADY LANDED",
    "bm-c r741-window self-ack move",
    "the W183 seat MSG sits in",
    # registered-row sha citations
    "bm-a r867 freeze 385dbafd8",
    "W182 row bm-a r867 freeze",
    "W182 finalize landed same-window r827",
    "W182 finalize one-pass bm-a r868", "W182 bm-a r868 one-pass",
    "finalize one-pass bm-a r868",
    "_r868bma_w183_probe_receipt.json",
    "r868 pre-seat push", "r865 probe leg4",
    # seat tokens
    "bma-w183-seat", "MSG-0741",
    # payload faces
    "payload = seat MSG + pre-seat probe script + probe receipt",
    "(3-item; the W182 finalize product already on origin since r868",
    "direct fast-forward behind-0",
    # single-window derive faces
    "single-window derive (r812 merged the gate legs INTO the",
    "single-window derive -- r812 merged the gate",
    # sec8 succession face (r870 same-window -- cited by W183)
    "r868 sec8 same-window succession",
    # jump phrases (physical fragment shapes)
    "own-wave A window reserved jumps to 419_404 -> ",
    "jumps to 419_404 -> 419_404..419_603,",
    "419_404 and lands 419_404..419_603",
    "hops=1 -> 417_404..419_403",
]
for n in needles:
    receipt["needles"][n] = {
        "pf": pfsrc.count(n), "n1": n1src.count(n),
        "pf_blk": blk_pf.count(n), "entry": entry183.count(n),
        "mat": blk_mat.count(n), "claim": claim183.count(n),
    }
io.open(r"results\_r874bma_w184_face_probe_receipt.json", "w", encoding="utf-8").write(
    json.dumps(receipt, indent=1, ensure_ascii=False))
print("probe rc0: pf_blk", len(blk_pf), "entry", len(entry183),
      "mat", len(blk_mat), "claim", len(claim183),
      "chain_n", len(receipt["mat_chain_rows"]),
      "chain_tail", receipt["mat_chain_rows"][-3:])
