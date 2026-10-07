# -*- coding: utf-8 -*-
"""r819 bm-a W172 freeze pre-TOK empirical probe (r773 pit law leg 1:
full string-face inventory BEFORE writing TOK; r776 law: needles taken
from PHYSICAL fragment shapes). Dumps the four W171 faces (pf comment
block+row / n1 WAVE_CONFIGS entry / n1 materializer block / n1 PASS
claim) to receipt files + counts every needle the W172 freeze uses.
Bloodline: r815 _r815bma_w171_face_probe.py machinery; W172 facts:
  - pre-seat probe results/_r818bma_w172_probe_receipt.json rc0 ADMIT
    (A 393_204..395_203 staircase THIRTY-FIRST instance E36 hops=1 past
    the registered W171 B band 393_004..393_203; naive 393_004..395_003
    refused at its own start by the W171 B band; B 395_204..395_403
    own-A mutual exclusion hops=1, naive 393_204..393_403);
  - W172 has ONE receipt (the merged-gate probe structure inherited
    from r812/r814: leg0 registry / leg1 bands+hops+semantics / leg2
    conflicts / leg3 origin vacancy / leg4 W173+ projection) -- no
    separate band-gate file this wave, single-window parity N/A honest
    note;
  - seat MSG-2026-10-07-1012-bma-w172-seat published (r818 seat push,
    r565 law: on origin BEFORE this freeze commit; seat MSG still in
    fleet/inbox/ at freeze time = honest deferred state, self-ack move
    deferred to the W172 finalize window);
  - registered W171 freeze sha machine-derived = 456f3affc (git log
    origin/main --grep "W171 FREEZE", live-verified this window)."""
import io
import json
import re

PF = r"scripts/perpetual_faces.py"
N1 = r"scripts/perpetual_faces_n1.py"
EO = '"engine_owner": "bm-a"},'

pfsrc = io.open(PF, encoding="utf-8", newline="").read()
n1src = io.open(N1, encoding="utf-8", newline="").read()

# face 1: pf W171 comment block + row
i1 = pfsrc.find("    # W171 (bm-a r815 freeze")
assert i1 > 0, "pf W171 comment block not found"
r1 = pfsrc.find('171: {"a": (391_004', i1)
assert r1 > i1, "pf W171 row not after comment block"
j1 = pfsrc.find(EO, r1) + len(EO)
blk_pf = pfsrc[i1:j1]
io.open(r"results\_r819bma_w172_probe_pf_block.txt", "w", encoding="utf-8", newline="").write(blk_pf)

# face 2: n1 WAVE_CONFIGS W171 entry
k = n1src.find('171: {"batch"')
assert k > 0, "n1 W171 entry not found"
m = n1src.find(EO, k) + len(EO)
entry171 = n1src[k:m]
io.open(r"results\_r819bma_w172_probe_n1_entry.txt", "w", encoding="utf-8", newline="").write(entry171)

# face 3: n1 W171 materializer block
w = n1src.find("# --- W171 materializer face")
t2 = n1src.find("# --- T-141 s2 lane face", w)
assert 0 < w < t2, "materializer anchors missing"
blk_mat = n1src[w:t2]
io.open(r"results\_r819bma_w172_probe_n1_mat.txt", "w", encoding="utf-8", newline="").write(blk_mat)

# face 4: n1 PASS snippet claim (r776 physical-shape law: the W171 claim
# trailing session marker is "r815 bm-a] " -- the actual r815 freeze
# session attribution; the W172 tool rolls it to the new session via
# @CLMS@ and discloses here)
cs = n1src.find('"+ W171 materializer face')
ce = n1src.find('"r815 bm-a] "', cs) + len('"r815 bm-a] "')
assert 0 < cs < ce, "W171 claim anchors missing"
claim171 = n1src[cs:ce]
io.open(r"results\_r819bma_w172_probe_n1_claim.txt", "w", encoding="utf-8", newline="").write(claim171)

receipt = {
    "probe": "r819 W172 freeze pre-TOK string-face inventory",
    "faces": {
        "pf_block_len": len(blk_pf), "n1_entry_len": len(entry171),
        "mat_block_len": len(blk_mat), "claim_len": len(claim171),
    },
    "pf_block_eol_crlf": blk_pf.count("\r\n"),
    "n1_entry_eol_crlf": entry171.count("\r\n"),
    "mat_block_eol_crlf": blk_mat.count("\r\n"),
    "claim_eol_crlf": claim171.count("\r\n"),
    "mat_chain_rows": re.findall(r"assert pf\.N1_BANDS\[(\d+)\]",
                                 blk_mat[blk_mat.find("assert pf.N1_BANDS[138]"):
                                         blk_mat.find("# prior-wave disjointness")]),
    "needles": {},
}
needles = [
    # row + entry carriers
    '171: {"a": (391_004, 393_003), "b_exit": (393_004, 393_203),',
    '171: {"batch"',
    # seed-base rows (entry comment face)
    '"a_seed_base": 391_004,',
    '"b_exit_seed_base": 393_004,',
    # dotted bands (W171 geometry)
    "390_804..392_803", "390_804..391_003", "391_004..393_003",
    "391_004..391_203", "393_004..393_203",
    # W172 projection prose inside W171 blocks (physical fragment shape)
    "393_004..395_003", "393_204..393_403",
    "W172 A window; W172 freezer MUST re-derive on the post-W171",
    # identity strings
    "PERPETUAL_N1_W171_PREREG.md", "PERPETUAL-N1-W171", "n1_w171_results.json",
    "n1_w171", "n1w171", "_r814bma", "MSG-2026-10-07-0843", "3290e586b",
    "779,412", "371,920", "ONE HUNDRED-AND-SIXTY-FIRST",
    "engine_owner rows 160", "rows 86 + candidate", "eighty-sixth",
    "thirtieth", "r815", "r814", "r813", "r812", "W171", "W170", "W172",
    "171", "170", "172",
    # set() asserts
    "set(range(391_004, 393_004))", "set(range(393_004, 393_204))",
    "== 391_004 == 391_003 + 1", "== 393_004 == 393_003 + 1",
    "391_003+1", "393_003+1",
    # seat delivery / self-ack prose (honesty faces)
    "move DEFERRED to the W171 finalize window",
    "W171 seat MSG sits in fleet/inbox/ at freeze time",
    # registered-row sha citations
    "bm-a r813 freeze cb7314d64",
    "W170 row bm-a r813 freeze",
    "cb7314d64, SINGLE STATE zero seat gap W2..W170 all",
    "cb7314d64", "456f3affc",
    # jump phrases (healed fragment carried via @JB@)
    "own-wave A window reserved jumps to 393_004, first-clean ",
    "jumps to 393_004, first-clean 393_004..393_203 hops=1",
    # freeze-session / prior-finalize / receipt / gate-session composites
    "bm-a r815 freeze", "r815 bm-a freeze", "r815 bm-a] ",
    "W170 finalize landed same-window r813",
    "W170 finalize one-pass bm-a r813", "W170 bm-a r813 one-pass",
    "finalize one-pass bm-a r813",
    "_r814bma_w171_probe_receipt.json",
    "r814 pre-seat push", "r812 probe leg4",
    # seat tokens
    "bma-w171-seat", "MSG-0843",
    # pf / mat jump-phrase fragment shapes
    "jumps to 393_004 -> 393_004..393_203,",
    "393_004 and lands 393_004..393_203",
    # payload faces (3-item truth landed at r815)
    "payload = seat MSG + pre-seat probe script + probe receipt",
    "(3-item; the W170 finalize product already on origin since r813",
    "direct fast-forward behind-0",
    # single-window derive faces
    "single-window derive (r812 merged the gate legs INTO the",
    # sec8 succession face (r819 settle, this window)
    "r813 sec8 succession",
]
for n in needles:
    receipt["needles"][n] = {
        "pf": pfsrc.count(n), "n1": n1src.count(n),
        "pf_blk": blk_pf.count(n), "entry": entry171.count(n),
        "mat": blk_mat.count(n), "claim": claim171.count(n),
    }
io.open(r"results\_r819bma_w172_face_probe_receipt.json", "w", encoding="utf-8").write(
    json.dumps(receipt, indent=1, ensure_ascii=False))
print("probe rc0: pf_blk", len(blk_pf), "entry", len(entry171),
      "mat", len(blk_mat), "claim", len(claim171),
      "chain_n", len(receipt["mat_chain_rows"]),
      "chain_tail", receipt["mat_chain_rows"][-3:])
