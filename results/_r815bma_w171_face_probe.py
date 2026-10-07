# -*- coding: utf-8 -*-
"""r815 bm-a W171 freeze pre-TOK empirical probe (r773 pit law leg 1:
full string-face inventory BEFORE writing TOK; r776 law: needles taken
from PHYSICAL fragment shapes). Dumps the four W170 faces (pf comment
block+row / n1 WAVE_CONFIGS entry / n1 materializer block / n1 PASS
claim) to receipt files + counts every needle the W171 freeze uses.
Bloodline: r813 _r813bma_w170_face_probe.py machinery; W171 facts:
  - pre-seat probe results/_r814bma_w171_probe_receipt.json rc0 ADMIT
    (A 391_004..393_003 staircase THIRTIETH instance E36 hops=1 past
    the registered W170 B band 390_804..391_003; naive 390_804..392_803
    refused at its own start by the registered W170 B band; B 393_004..393_203
    own-A mutual exclusion hops=1, naive 391_004..391_203);
  - W171 has ONE receipt (the merged-gate probe structure inherited
    from r812: leg0 registry / leg1 bands+hops+semantics / leg2 conflicts /
    leg3 origin vacancy / leg4 W172+ projection) -- no separate band-gate
    file this wave, single-window parity N/A honest note;
  - seat MSG-2026-10-07-0843-bma-w171-seat published (r814 seat push,
    r565 law: on origin BEFORE this freeze commit; seat MSG still in
    fleet/inbox/ at freeze time = honest deferred state, self-ack move
    deferred to the W171 finalize window);
  - registered W170 freeze sha machine-derived = cb7314d64 (git log
    origin/main --grep "W170 FREEZE", live-verified this window)."""
import io
import json
import re

PF = r"scripts/perpetual_faces.py"
N1 = r"scripts/perpetual_faces_n1.py"
EO = '"engine_owner": "bm-a"},'

pfsrc = io.open(PF, encoding="utf-8", newline="").read()
n1src = io.open(N1, encoding="utf-8", newline="").read()

# face 1: pf W170 comment block + row
i1 = pfsrc.find("    # W170 (bm-a r813 freeze")
assert i1 > 0, "pf W170 comment block not found"
r1 = pfsrc.find('170: {"a": (388_804', i1)
assert r1 > i1, "pf W170 row not after comment block"
j1 = pfsrc.find(EO, r1) + len(EO)
blk_pf = pfsrc[i1:j1]
io.open(r"results\_r815bma_w171_probe_pf_block.txt", "w", encoding="utf-8", newline="").write(blk_pf)

# face 2: n1 WAVE_CONFIGS W170 entry
k = n1src.find('170: {"batch"')
assert k > 0, "n1 W170 entry not found"
m = n1src.find(EO, k) + len(EO)
entry170 = n1src[k:m]
io.open(r"results\_r815bma_w171_probe_n1_entry.txt", "w", encoding="utf-8", newline="").write(entry170)

# face 3: n1 W170 materializer block
w = n1src.find("# --- W170 materializer face")
t2 = n1src.find("# --- T-141 s2 lane face", w)
assert 0 < w < t2, "materializer anchors missing"
blk_mat = n1src[w:t2]
io.open(r"results\_r815bma_w171_probe_n1_mat.txt", "w", encoding="utf-8", newline="").write(blk_mat)

# face 4: n1 PASS snippet claim (r776 physical-shape law: the W170 claim
# trailing session marker is "r813 bm-a] " -- the actual r813 freeze
# session attribution; the W171 tool rolls it to the new session via
# @CLMS@ and discloses here)
cs = n1src.find('"+ W170 materializer face')
ce = n1src.find('"r813 bm-a] "', cs) + len('"r813 bm-a] "')
assert 0 < cs < ce, "W170 claim anchors missing"
claim170 = n1src[cs:ce]
io.open(r"results\_r815bma_w171_probe_n1_claim.txt", "w", encoding="utf-8", newline="").write(claim170)

receipt = {
    "probe": "r815 W171 freeze pre-TOK string-face inventory",
    "faces": {
        "pf_block_len": len(blk_pf), "n1_entry_len": len(entry170),
        "mat_block_len": len(blk_mat), "claim_len": len(claim170),
    },
    "pf_block_eol_crlf": blk_pf.count("\r\n"),
    "n1_entry_eol_crlf": entry170.count("\r\n"),
    "mat_block_eol_crlf": blk_mat.count("\r\n"),
    "claim_eol_crlf": claim170.count("\r\n"),
    "mat_chain_rows": re.findall(r"assert pf\.N1_BANDS\[(\d+)\]",
                                 blk_mat[blk_mat.find("assert pf.N1_BANDS[138]"):
                                         blk_mat.find("# prior-wave disjointness")]),
    "needles": {},
}
needles = [
    # row + entry carriers
    '170: {"a": (388_804, 390_803), "b_exit": (390_804, 391_003),',
    '170: {"batch"',
    # seed-base rows (entry comment face)
    '"a_seed_base": 388_804,',
    '"b_exit_seed_base": 390_804,',
    # dotted bands (W170 geometry)
    "388_604..390_603", "388_604..388_803", "388_804..390_803",
    "388_804..389_003", "390_804..391_003",
    # W171 projection prose inside W170 blocks (physical fragment shape)
    "390_804..392_803", "391_004..391_203",
    "W171 A window; W171 freezer MUST re-derive on the post-W170",
    # identity strings
    "PERPETUAL_N1_W170_PREREG.md", "PERPETUAL-N1-W170", "n1_w170_results.json",
    "n1_w170", "n1w170", "_r812bma", "MSG-2026-10-07-0738", "0f00fa424",
    "779,412", "371,920", "ONE HUNDRED-AND-SIXTIETH",
    "engine_owner rows 159", "rows 85 + candidate", "eighty-fifth",
    "twenty-ninth", "r813", "r812", "r811", "r810", "W170", "W169", "W171",
    "170", "169", "168",
    # set() asserts
    "set(range(388_804, 390_804))", "set(range(390_804, 391_004))",
    "== 388_804 == 388_803 + 1", "== 390_804 == 390_803 + 1",
    "388_803+1", "390_803+1",
    # seat delivery / self-ack prose (honesty faces)
    "move DEFERRED to the W170 finalize window",
    "W170 seat MSG sits in fleet/inbox/ at freeze time",
    # registered-row sha citations
    "bm-a r811 freeze 9c2271baf",
    "W169 row bm-a r811 freeze",
    "9c2271baf, SINGLE STATE zero seat gap W2..W169 all",
    "9c2271baf", "cb7314d64",
    # jump phrases (healed fragment carried via @JB@)
    "own-wave A window reserved jumps to 390_804, first-clean ",
    "jumps to 390_804, first-clean 390_804..391_003 hops=1",
    # freeze-session / prior-finalize / receipt / gate-session composites
    "bm-a r813 freeze", "r813 bm-a freeze", "r813 bm-a] ",
    "W169 finalize landed same-window r812",
    "W169 finalize one-pass bm-a r812", "W169 bm-a r812 one-pass",
    "finalize one-pass bm-a r812",
    "_r812bma_w170_probe_receipt.json",
    "r812 pre-seat push", "r810 gate leg3",
    # seat tokens
    "bma-w170-seat", "MSG-0738",
    # pf / mat jump-phrase fragment shapes
    "jumps to 390_804 -> 390_804..391_003,",
    "390_804 and lands 390_804..391_003",
    # payload faces
    "payload = seat MSG + pre-seat probe script + probe receipt + the",
    "direct fast-forward behind-0",
    # single-window derive faces
    "single-window derive (r812 merged the gate legs INTO the",
]
for n in needles:
    receipt["needles"][n] = {
        "pf": pfsrc.count(n), "n1": n1src.count(n),
        "pf_blk": blk_pf.count(n), "entry": entry170.count(n),
        "mat": blk_mat.count(n), "claim": claim170.count(n),
    }
io.open(r"results\_r815bma_w171_face_probe_receipt.json", "w", encoding="utf-8").write(
    json.dumps(receipt, indent=1, ensure_ascii=False))
print("probe rc0: pf_blk", len(blk_pf), "entry", len(entry170),
      "mat", len(blk_mat), "claim", len(claim170),
      "chain_n", len(receipt["mat_chain_rows"]),
      "chain_tail", receipt["mat_chain_rows"][-3:])
