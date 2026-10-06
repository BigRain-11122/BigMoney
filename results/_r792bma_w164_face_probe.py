# -*- coding: utf-8 -*-
"""r792 bm-a W164 freeze pre-TOK empirical probe (r773 pit law leg 1:
full string-face inventory BEFORE writing TOK; r776 law: projection-prose
old strings taken from PHYSICAL fragment shapes). Dumps the four W163
faces (pf comment block+row / n1 WAVE_CONFIGS entry / n1 materializer
block / n1 PASS claim) to receipt files + counts every needle the
freeze script will use.
Bloodline: r789 _r789bma_w163_face_probe.py machinery verbatim."""
import io
import json
import re

PF = r"scripts/perpetual_faces.py"
N1 = r"scripts/perpetual_faces_n1.py"
EO = '"engine_owner": "bm-a"},'

pfsrc = io.open(PF, encoding="utf-8", newline="").read()
n1src = io.open(N1, encoding="utf-8", newline="").read()

# face 1: pf W163 comment block + row
i1 = pfsrc.find("    # W163 (bm-a r789 freeze")
assert i1 > 0, "pf W163 comment block not found"
r1 = pfsrc.find('163: {"a": (373_404', i1)
assert r1 > i1, "pf W163 row not after comment block"
j1 = pfsrc.find(EO, r1) + len(EO)
blk_pf = pfsrc[i1:j1]
io.open(r"results\_r792bma_w164_probe_pf_block.txt", "w", encoding="utf-8", newline="").write(blk_pf)

# face 2: n1 WAVE_CONFIGS W163 entry
k = n1src.find('163: {"batch"')
assert k > 0, "n1 W163 entry not found"
m = n1src.find(EO, k) + len(EO)
entry163 = n1src[k:m]
io.open(r"results\_r792bma_w164_probe_n1_entry.txt", "w", encoding="utf-8", newline="").write(entry163)

# face 3: n1 W163 materializer block
w = n1src.find("# --- W163 materializer face")
t2 = n1src.find("# --- T-141 s2 lane face", w)
assert 0 < w < t2, "materializer anchors missing"
blk_mat = n1src[w:t2]
io.open(r"results\_r792bma_w164_probe_n1_mat.txt", "w", encoding="utf-8", newline="").write(blk_mat)

# face 4: n1 PASS snippet claim
cs = n1src.find('"+ W163 materializer face')
ce = n1src.find('"r789 bm-a] "', cs) + len('"r789 bm-a] "')
assert 0 < cs < ce, "W163 claim anchors missing"
claim163 = n1src[cs:ce]
io.open(r"results\_r792bma_w164_probe_n1_claim.txt", "w", encoding="utf-8", newline="").write(claim163)

receipt = {
    "probe": "r792 W164 freeze pre-TOK string-face inventory",
    "faces": {
        "pf_block_len": len(blk_pf), "n1_entry_len": len(entry163),
        "mat_block_len": len(blk_mat), "claim_len": len(claim163),
    },
    "pf_block_eol_crlf": blk_pf.count("\r\n"),
    "n1_entry_eol_crlf": entry163.count("\r\n"),
    "mat_block_eol_crlf": blk_mat.count("\r\n"),
    "claim_eol_crlf": claim163.count("\r\n"),
    "mat_chain_rows": re.findall(r"assert pf\.N1_BANDS\[(\d+)\]",
                                 blk_mat[blk_mat.find("assert pf.N1_BANDS[138]"):
                                         blk_mat.find("# prior-wave disjointness")]),
    "needles": {},
}
needles = [
    # row + entry carriers
    '163: {"a": (373_404, 375_403), "b_exit": (375_404, 375_603),',
    '163: {"batch"',
    # seed-base rows (n1 entry face)
    '"a_seed_base": 373_404,',
    '"b_exit_seed_base": 375_404,',
    # dotted bands
    "373_204..375_203", "373_404..373_603", "373_404..375_403",
    "375_404..375_603", "373_204..373_403",
    # W164 projection prose inside W163 blocks (physical fragment shape)
    "375_404..377_403", "375_604..375_803",
    "W164 A window; W164 freezer MUST re-derive on the post-W163",
    '"W164 A window; W164 freezer MUST re-derive on the "',
    '"W163 B band 375_404..375_603 will refuse the naive "',
    "A first-clean 375_404..377_403 ", "B first-clean 375_604..375_803 CLEAN",
    # identity strings
    "PERPETUAL_N1_W163_PREREG.md", "PERPETUAL-N1-W163", "n1_w163_results.json",
    "n1_w163", "_r789bma", "MSG-2026-10-06-183x", "189157de8",
    "761,812", "354,320", "ONE HUNDRED-AND-FIFTY-THIRD",
    "engine_owner rows 152", "rows 78 + candidate", "seventy-ninth",
    "twenty-second", "r789", "r788", "r787", "W163", "W162", "163", "162",
    # set() asserts
    "set(range(373_404, 375_404))", "set(range(375_404, 375_604))",
    "== 373_404 == 373_403 + 1", "== 375_404 == 375_403 + 1",
    # seat delivery / self-ack prose (honesty faces)
    "move deferred to the W163 finalize window",
    "fleet/inbox at freeze time -- honest state",
    "payload = seat MSG + pre-seat probe + probe receipt;",
    '"seat MSG + pre-seat probe + probe receipt; "',
    "= seat MSG + pre-seat probe + probe receipt;",
    "facts helper",
    # registered-row sha citations
    "bm-a r787 freeze 764cd882a",
    "W162 row bm-a r787 freeze",
    "764cd882a, SINGLE STATE zero seat gap W2..W162 all",
    '"number law after the REGISTERED W162 row bm-a r787 freeze "',
    '"764cd882a, SINGLE STATE zero seat gap W2..W162 all "',
    '"finalize one-pass bm-a r788, net chain head 761,812, "',
    # jump phrases (healed fragment carried via @JB@)
    "own-wave A window reserved jumps to 375_404, first-clean ",
    "jumps to 375_404, first-clean 375_404..375_603 hops=1",
    "jumps to 375_404 -> 375_404..375_603,",
    "375_404 and lands 375_404..375_603",
    # freeze-session / prior-finalize / receipt / gate-session composites
    "bm-a r789 freeze", "r789 bm-a freeze",
    "W162 finalize landed same-window r788",
    "W162 finalize one-pass bm-a r788", "W162 bm-a r788 one-pass",
    "_r789bma_w163_probe_receipt.json", "_r789bma_w163_band_gate.json",
    "r787 gate leg3", "r787 gate", "r788 sec8 succession", "r788 sec8",
    # seat tokens
    "bma-w163-seat", "MSG-183x",
    # base-relation composites
    "373_403+1", "375_403+1",
    # shard identity
    "n1w163",
    # delivery-window prose
    "direct fast-forward behind-0",
    "r789 pre-seat",
    # stale-residue sentinels (must stay ABSENT from W163 faces)
    "362_204..362_003", "362_404..360_403", "371_004", "371_204", "371_403",
    "371_203", "369_004", "678a07d4f", "6957f509e", "twentieth", "twenty-first",
    "seventy-seventh", "seventy-eighth", "ONE HUNDRED-AND-FIFTY-SECOND",
    "engine_owner rows 151", "rows 77 + candidate", "759,612", "352,120",
    "1d43d7906", "MSG-2026-10-06-175x", "bma-w162-seat", "MSG-175x",
    "r785 gate", "r786 sec8", "merge-absorb", "bm-b r779",
]
for n in needles:
    receipt["needles"][n] = {
        "pf": pfsrc.count(n), "n1": n1src.count(n),
        "pf_blk": blk_pf.count(n), "entry": entry163.count(n),
        "mat": blk_mat.count(n), "claim": claim163.count(n),
    }
io.open(r"results\_r792bma_w164_face_probe_receipt.json", "w", encoding="utf-8").write(
    json.dumps(receipt, indent=1, ensure_ascii=False))
print("probe rc0: pf_blk", len(blk_pf), "entry", len(entry163),
      "mat", len(blk_mat), "claim", len(claim163),
      "chain n=", len(receipt["mat_chain_rows"]),
      "tail", receipt["mat_chain_rows"][-3:])
