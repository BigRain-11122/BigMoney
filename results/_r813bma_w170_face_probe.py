# -*- coding: utf-8 -*-
"""r813 bm-a W170 freeze pre-TOK empirical probe (r773 pit law leg 1:
full string-face inventory BEFORE writing TOK; r776 law: needles taken
from PHYSICAL fragment shapes). Dumps the four W169 faces (pf comment
block+row / n1 WAVE_CONFIGS entry / n1 materializer block / n1 PASS
claim) to receipt files + counts every needle the W170 freeze uses.
Bloodline: r811 _r811bma_w169_face_probe.py machinery verbatim; W170 facts:
  - pre-seat probe results/_r812bma_w170_probe_receipt.json rc0 ADMIT
    (A 388_804..390_803 staircase TWENTY-NINTH instance E36 hops=1 past
    the registered W169 B band 388_604..388_803; naive 388_604..390_603
    refused at its own start by the registered W169 B band; B 390_804..391_003
    own-A mutual exclusion hops=1, naive 388_804..389_003);
  - W170 has ONE receipt (r812 merged the gate legs INTO the probe:
    leg0 registry / leg1 bands+hops+semantics / leg2 conflicts /
    leg3 origin vacancy / leg4 W171+ projection) -- no separate band-gate
    file this wave, single-window parity N/A honest note;
  - seat MSG-2026-10-07-0738-bma-w170-seat published (r812 seat push
    0f00fa424, r565 law: on origin BEFORE this freeze commit; seat MSG
    still in fleet/inbox/ at freeze time = honest deferred state,
    self-ack move deferred to the W170 finalize window, NO landed-state
    fixup direction this window);
  - registered W169 freeze sha machine-derived = 9c2271baf (git log
    origin/main --grep W169 FREEZE; the r812 probe-script header
    carried stale pre-rebase sha 2ea58d762 -- honest note, the rebase
    preserved 9c2271baf)."""
import io
import json
import re

PF = r"scripts/perpetual_faces.py"
N1 = r"scripts/perpetual_faces_n1.py"
EO = '"engine_owner": "bm-a"},'

pfsrc = io.open(PF, encoding="utf-8", newline="").read()
n1src = io.open(N1, encoding="utf-8", newline="").read()

# face 1: pf W169 comment block + row
i1 = pfsrc.find("    # W169 (bm-a r811 freeze")
assert i1 > 0, "pf W169 comment block not found"
r1 = pfsrc.find('169: {"a": (386_604', i1)
assert r1 > i1, "pf W169 row not after comment block"
j1 = pfsrc.find(EO, r1) + len(EO)
blk_pf = pfsrc[i1:j1]
io.open(r"results\_r813bma_w170_probe_pf_block.txt", "w", encoding="utf-8", newline="").write(blk_pf)

# face 2: n1 WAVE_CONFIGS W169 entry
k = n1src.find('169: {"batch"')
assert k > 0, "n1 W169 entry not found"
m = n1src.find(EO, k) + len(EO)
entry169 = n1src[k:m]
io.open(r"results\_r813bma_w170_probe_n1_entry.txt", "w", encoding="utf-8", newline="").write(entry169)

# face 3: n1 W169 materializer block
w = n1src.find("# --- W169 materializer face")
t2 = n1src.find("# --- T-141 s2 lane face", w)
assert 0 < w < t2, "materializer anchors missing"
blk_mat = n1src[w:t2]
io.open(r"results\_r813bma_w170_probe_n1_mat.txt", "w", encoding="utf-8", newline="").write(blk_mat)

# face 4: n1 PASS snippet claim (r776 physical-shape law: the W169 claim
# trailing session marker is "r811 bm-a] " -- the actual r811 freeze
# session attribution; the W170 tool rolls it to the new session via
# @CLMS@ and discloses here)
cs = n1src.find('"+ W169 materializer face')
ce = n1src.find('"r811 bm-a] "', cs) + len('"r811 bm-a] "')
assert 0 < cs < ce, "W169 claim anchors missing"
claim169 = n1src[cs:ce]
io.open(r"results\_r813bma_w170_probe_n1_claim.txt", "w", encoding="utf-8", newline="").write(claim169)

receipt = {
    "probe": "r813 W170 freeze pre-TOK string-face inventory",
    "faces": {
        "pf_block_len": len(blk_pf), "n1_entry_len": len(entry169),
        "mat_block_len": len(blk_mat), "claim_len": len(claim169),
    },
    "pf_block_eol_crlf": blk_pf.count("\r\n"),
    "n1_entry_eol_crlf": entry169.count("\r\n"),
    "mat_block_eol_crlf": blk_mat.count("\r\n"),
    "claim_eol_crlf": claim169.count("\r\n"),
    "mat_chain_rows": re.findall(r"assert pf\.N1_BANDS\[(\d+)\]",
                                 blk_mat[blk_mat.find("assert pf.N1_BANDS[138]"):
                                         blk_mat.find("# prior-wave disjointness")]),
    "needles": {},
}
needles = [
    # row + entry carriers
    '169: {"a": (386_604, 388_603), "b_exit": (388_604, 388_803),',
    '169: {"batch"',
    # seed-base rows (entry comment face)
    '"a_seed_base": 386_604,',
    '"b_exit_seed_base": 388_604,',
    # dotted bands (W169 geometry)
    "386_404..388_403", "386_404..386_603", "386_604..388_603",
    "386_604..386_803", "388_604..388_803",
    # W170 projection prose inside W169 blocks (physical fragment shape)
    "388_604..390_603", "388_804..389_003",
    "W170 A window; W170 freezer MUST re-derive on the post-W169",
    # identity strings
    "PERPETUAL_N1_W169_PREREG.md", "PERPETUAL-N1-W169", "n1_w169_results.json",
    "n1_w169", "n1w169", "_r810bma", "MSG-2026-10-07-0547", "bcd6e4392",
    "777,212", "369,720", "ONE HUNDRED-AND-FIFTY-NINTH",
    "engine_owner rows 158", "rows 84 + candidate", "eighty-fourth",
    "twenty-eighth", "r811", "r810", "r806", "r809", "W169", "W168", "W170",
    "169", "168", "167",
    # set() asserts
    "set(range(386_604, 388_604))", "set(range(388_604, 388_804))",
    "== 386_604 == 386_603 + 1", "== 388_604 == 388_603 + 1",
    "386_603+1", "388_603+1",
    # seat delivery / self-ack prose (honesty faces)
    "move deferred to the W170 finalize window",
    "W169 seat still in",
    "bm-b r798 consumed-archived the",
    "06:02:52",
    # registered-row sha citations
    "bm-a r809 freeze 8d8842b61",
    "W168 row bm-a r809 freeze",
    "8d8842b61, SINGLE STATE zero seat gap W2..W168 all",
    "8d8842b61",
    "9c2271baf", "2ea58d762",
    # jump phrases (healed fragment carried via @JB@)
    "own-wave A window reserved jumps to 388_604, first-clean ",
    "jumps to 388_604, first-clean 388_604..388_803 hops=1",
    # freeze-session / prior-finalize / receipt / gate-session composites
    "bm-a r811 freeze", "r811 bm-a freeze", "r811 bm-a] ",
    "W168 finalize landed same-window r809",
    "W168 finalize one-pass bm-a r809", "W168 bm-a r809 one-pass",
    "finalize one-pass bm-a r809",
    "_r810bma_w169_probe_receipt.json", "_r810bma_w169_band_gate.json",
    "r806 gate leg3", "r806 gate", "r811 sec8 succession", "r811 sec8",
    "gate-derived r810", "r810 pre-seat push",
    # seat tokens
    "bma-w169-seat", "MSG-0547",
    # pf / mat jump-phrase fragment shapes
    "jumps to 388_604 -> 388_604..388_803,",
    "388_604 and lands 388_604..388_803",
    # payload faces
    "payload = seat MSG + pre-seat probe + probe receipt;",
    "direct fast-forward behind-0",
]
for n in needles:
    receipt["needles"][n] = {
        "pf": pfsrc.count(n), "n1": n1src.count(n),
        "pf_blk": blk_pf.count(n), "entry": entry169.count(n),
        "mat": blk_mat.count(n), "claim": claim169.count(n),
    }
io.open(r"results\_r813bma_w170_face_probe_receipt.json", "w", encoding="utf-8").write(
    json.dumps(receipt, indent=1, ensure_ascii=False))
print("probe rc0: pf_blk", len(blk_pf), "entry", len(entry169),
      "mat", len(blk_mat), "claim", len(claim169),
      "chain_n", len(receipt["mat_chain_rows"]),
      "chain_tail", receipt["mat_chain_rows"][-3:])
