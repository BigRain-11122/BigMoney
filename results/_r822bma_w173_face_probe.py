# -*- coding: utf-8 -*-
"""r822 bm-a W173 freeze pre-TOK empirical probe (r773 pit law leg 1:
full string-face inventory BEFORE writing TOK; r776 law: needles taken
from PHYSICAL fragment shapes). Dumps the four W172 faces (pf comment
block+row / n1 WAVE_CONFIGS entry / n1 materializer block / n1 PASS
claim) to receipt files + counts every needle the W173 freeze uses.
Bloodline: r819 _r819bma_w172_face_probe.py machinery; W173 facts:
  - pre-seat probe results/_r820bma_w173_probe_receipt.json rc0 ADMIT
    (A 395_404..397_403 staircase THIRTY-THIRD instance E36 hops=1 past
    the registered W172 B band 395_204..395_403; naive 395_204..397_203
    refused at its own start by the W172 B band -- receipt A_semantics
    machine-cites 'r818 probe leg4' anticipation; B 397_404..397_603
    own-A mutual exclusion hops=1, naive 395_404..395_603);
  - ordinal divergence disclosed (W172 sec5.5 prose anticipated 32nd,
    r820 receipt machine-read THIRTY-THIRD, carried per r587);
  - prereg citation slip disclosed: PERPETUAL_N1_W173_PREREG.md prose
    cites 'r820 probe leg4' in the anticipation triple (frozen at
    d76ce93d5, not edited; the NEW W173 freeze faces carry the machine
    receipt citation 'r818 probe leg4' per r587 never-transcribe law);
  - W173 has ONE receipt (merged-gate probe structure inherited from
    r812/r814/r818: leg0 registry / leg1 bands+hops+semantics / leg2
    conflicts / leg3 origin vacancy / leg4 W174+ projection);
  - seat MSG-2026-10-07-1122-bma-w173-seat published (r820 pre-seat
    push 9cd8af3af path-derived TRUE landed sha per r812 precedent --
    r820 closeout prose 014b4ede5 = stale pre-rebase artifact,
    honesty-noted r821; r565 law: on origin BEFORE this freeze commit;
    seat MSG self-ack inbox->processed move deferred to the W173
    finalize window);
  - registered W172 freeze sha machine-derived = 59fde9319 (git log
    origin/main --grep "W172 FREEZE", live-verified this window)."""
import io
import json
import re

PF = r"scripts/perpetual_faces.py"
N1 = r"scripts/perpetual_faces_n1.py"
EO = '"engine_owner": "bm-a"},'

pfsrc = io.open(PF, encoding="utf-8", newline="").read()
n1src = io.open(N1, encoding="utf-8", newline="").read()

# face 1: pf W172 comment block + row
i1 = pfsrc.find("    # W172 (bm-a r819 freeze")
assert i1 > 0, "pf W172 comment block not found"
r1 = pfsrc.find('172: {"a": (393_204', i1)
assert r1 > i1, "pf W172 row not after comment block"
j1 = pfsrc.find(EO, r1) + len(EO)
blk_pf = pfsrc[i1:j1]
io.open(r"results\_r822bma_w173_probe_pf_block.txt", "w", encoding="utf-8", newline="").write(blk_pf)

# face 2: n1 WAVE_CONFIGS W172 entry
k = n1src.find('172: {"batch"')
assert k > 0, "n1 W172 entry not found"
m = n1src.find(EO, k) + len(EO)
entry172 = n1src[k:m]
io.open(r"results\_r822bma_w173_probe_n1_entry.txt", "w", encoding="utf-8", newline="").write(entry172)

# face 3: n1 W172 materializer block
w = n1src.find("# --- W172 materializer face")
t2 = n1src.find("# --- T-141 s2 lane face", w)
assert 0 < w < t2, "materializer anchors missing"
blk_mat = n1src[w:t2]
io.open(r"results\_r822bma_w173_probe_n1_mat.txt", "w", encoding="utf-8", newline="").write(blk_mat)

# face 4: n1 PASS snippet claim (r776 physical-shape law: the W172 claim
# trailing session marker is "r819 bm-a] " -- the actual r819 freeze
# session attribution; the W173 tool rolls it to the new session via
# @CLMS@ and discloses here)
cs = n1src.find('"+ W172 materializer face')
ce = n1src.find('"r819 bm-a] "', cs) + len('"r819 bm-a] "')
assert 0 < cs < ce, "W172 claim anchors missing"
claim172 = n1src[cs:ce]
io.open(r"results\_r822bma_w173_probe_n1_claim.txt", "w", encoding="utf-8", newline="").write(claim172)

receipt = {
    "probe": "r822 W173 freeze pre-TOK string-face inventory",
    "faces": {
        "pf_block_len": len(blk_pf), "n1_entry_len": len(entry172),
        "mat_block_len": len(blk_mat), "claim_len": len(claim172),
    },
    "pf_block_eol_crlf": blk_pf.count("\r\n"),
    "n1_entry_eol_crlf": entry172.count("\r\n"),
    "mat_block_eol_crlf": blk_mat.count("\r\n"),
    "claim_eol_crlf": claim172.count("\r\n"),
    "mat_chain_rows": re.findall(r"assert pf\.N1_BANDS\[(\d+)\]",
                                 blk_mat[blk_mat.find("assert pf.N1_BANDS[138]"):
                                         blk_mat.find("# prior-wave disjointness")]),
    "needles": {},
}
needles = [
    # row + entry carriers
    '172: {"a": (393_204, 395_203), "b_exit": (395_204, 395_403),',
    '172: {"batch"',
    # seed-base rows (entry comment face)
    '"a_seed_base": 393_204,',
    '"b_exit_seed_base": 395_204,',
    # dotted bands (W172 geometry)
    "393_204..395_203", "395_204..395_403", "393_004..393_203",
    # W173 projection prose inside W172 blocks (physical fragment shape)
    "395_204..397_203", "395_404..395_603",
    "W173 A window; W173 freezer MUST re-derive on the post-W172",
    # identity strings
    "PERPETUAL_N1_W172_PREREG.md", "PERPETUAL-N1-W172", "n1_w172_results.json",
    "n1_w172", "n1w172", "_r818bma", "MSG-2026-10-07-1012", "01a7480e1",
    "781,612", "374,120", "ONE HUNDRED-AND-SIXTY-SECOND",
    "engine_owner rows 161", "rows 87 + candidate", "eighty-seventh",
    "thirty-first", "r819", "r818", "r816", "r812", "W172", "W171", "W173",
    "172", "171", "173",
    # set() asserts
    "set(range(393_204, 395_204))", "set(range(395_204, 395_404))",
    "== 393_204 == 393_203 + 1", "== 395_204 == 395_203 + 1",
    "393_203+1", "395_203+1",
    # seat delivery / self-ack prose (honesty faces)
    "move DEFERRED to the W172 finalize window",
    "W172 seat MSG sits in fleet/inbox/ at freeze time",
    # registered-row sha citations
    "bm-a r815 freeze 456f3affc",
    "W171 row bm-a r815 freeze",
    "456f3affc, SINGLE STATE zero seat gap W2..W171 all",
    "456f3affc", "59fde9319",
    # jump phrases (physical fragment shapes)
    "own-wave A window reserved jumps to 395_204, first-clean ",
    "jumps to 395_204, first-clean 395_204..395_403 hops=1",
    "jumps to 395_204 -> 395_204..395_403,",
    "395_204 and lands 395_204..395_403",
    # freeze-session / prior-finalize / receipt / gate-session composites
    "bm-a r819 freeze", "r819 bm-a freeze", "r819 bm-a] ",
    "W171 finalize landed same-window r816",
    "W171 finalize one-pass bm-a r816", "W171 bm-a r816 one-pass",
    "finalize one-pass bm-a r816",
    "_r818bma_w172_probe_receipt.json",
    "r818 pre-seat push", "r814 probe leg4",
    # seat tokens
    "bma-w172-seat", "MSG-1012",
    # payload faces (3-item truth landed at r819)
    "payload = seat MSG + pre-seat probe script + probe receipt",
    "(3-item; the W171 finalize product already on origin since r816",
    "direct fast-forward behind-0",
    # single-window derive faces
    "single-window derive (r812 merged the gate legs INTO the",
    # sec8 succession face (r819 settle -- cited again by W173 because
    # the W172 sec8 succession notes ALSO landed r819)
    "r819 sec8 succession",
]
for n in needles:
    receipt["needles"][n] = {
        "pf": pfsrc.count(n), "n1": n1src.count(n),
        "pf_blk": blk_pf.count(n), "entry": entry172.count(n),
        "mat": blk_mat.count(n), "claim": claim172.count(n),
    }
io.open(r"results\_r822bma_w173_face_probe_receipt.json", "w", encoding="utf-8").write(
    json.dumps(receipt, indent=1, ensure_ascii=False))
print("probe rc0: pf_blk", len(blk_pf), "entry", len(entry172),
      "mat", len(blk_mat), "claim", len(claim172),
      "chain_n", len(receipt["mat_chain_rows"]),
      "chain_tail", receipt["mat_chain_rows"][-3:])
