# -*- coding: utf-8 -*-
"""r794 bm-a W165 freeze pre-TOK empirical probe (r773 pit law leg 1:
full string-face inventory BEFORE writing TOK; r776 law: projection-prose
old strings taken from PHYSICAL fragment shapes). Dumps the four W164
faces (pf comment block+row / n1 WAVE_CONFIGS entry / n1 materializer
block / n1 PASS claim) to receipt files + counts every needle the
freeze script will use.
Bloodline: r792 _r792bma_w164_face_probe.py machinery verbatim."""
import io
import json
import re

PF = r"scripts/perpetual_faces.py"
N1 = r"scripts/perpetual_faces_n1.py"
EO = '"engine_owner": "bm-a"},'

pfsrc = io.open(PF, encoding="utf-8", newline="").read()
n1src = io.open(N1, encoding="utf-8", newline="").read()

# face 1: pf W164 comment block + row
i1 = pfsrc.find("    # W164 (bm-a r792 freeze")
assert i1 > 0, "pf W164 comment block not found"
r1 = pfsrc.find('164: {"a": (375_604', i1)
assert r1 > i1, "pf W164 row not after comment block"
j1 = pfsrc.find(EO, r1) + len(EO)
blk_pf = pfsrc[i1:j1]
io.open(r"results\_r794bma_w165_probe_pf_block.txt", "w", encoding="utf-8", newline="").write(blk_pf)

# face 2: n1 WAVE_CONFIGS W164 entry
k = n1src.find('164: {"batch"')
assert k > 0, "n1 W164 entry not found"
m = n1src.find(EO, k) + len(EO)
entry163 = n1src[k:m]
io.open(r"results\_r794bma_w165_probe_n1_entry.txt", "w", encoding="utf-8", newline="").write(entry163)

# face 3: n1 W164 materializer block
w = n1src.find("# --- W164 materializer face")
t2 = n1src.find("# --- T-141 s2 lane face", w)
assert 0 < w < t2, "materializer anchors missing"
blk_mat = n1src[w:t2]
io.open(r"results\_r794bma_w165_probe_n1_mat.txt", "w", encoding="utf-8", newline="").write(blk_mat)

# face 4: n1 PASS snippet claim
cs = n1src.find('"+ W164 materializer face')
ce = n1src.find('"r792 bm-a] "', cs) + len('"r792 bm-a] "')
assert 0 < cs < ce, "W164 claim anchors missing"
claim163 = n1src[cs:ce]
io.open(r"results\_r794bma_w165_probe_n1_claim.txt", "w", encoding="utf-8", newline="").write(claim163)

receipt = {
    "probe": "r794 W165 freeze pre-TOK string-face inventory",
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
    '164: {"a": (375_604, 377_603), "b_exit": (377_604, 377_803),',
    '164: {"batch"',
    # seed-base rows (n1 entry face)
    '"a_seed_base": 375_604,',
    '"b_exit_seed_base": 377_604,',
    # dotted bands
    "375_404..377_403", "375_604..375_803", "375_604..377_603",
    "377_604..377_803", "375_404..375_603",
    # W165 projection prose inside W164 blocks (physical fragment shape)
    "377_604..379_603", "377_804..378_003",
    "W165 A window; W165 freezer MUST re-derive on the post-W164",
    '"W165 A window; W165 freezer MUST re-derive on the "',
    '"W164 B band 377_604..377_803 will refuse the naive "',
    "A first-clean 377_604..379_603 ", "B first-clean 377_804..378_003 CLEAN",
    # identity strings
    "PERPETUAL_N1_W164_PREREG.md", "PERPETUAL-N1-W164", "n1_w164_results.json",
    "n1_w164", "_r792bma", "MSG-2026-10-06-194x", "469d40896",
    "764,012", "356,520", "ONE HUNDRED-AND-FIFTY-FOURTH",
    "engine_owner rows 153", "rows 79 + candidate", "seventy-ninth",
    "twenty-third", "r792", "r790", "r789", "W164", "W163", "164", "162",
    # set() asserts
    "set(range(375_604, 377_604))", "set(range(377_604, 377_804))",
    "== 375_604 == 375_603 + 1", "== 377_604 == 377_603 + 1",
    # seat delivery / self-ack prose (honesty faces)
    "move deferred to the W164 finalize window",
    "fleet/inbox at freeze time -- honest state",
    "payload = seat MSG + pre-seat probe + probe receipt;",
    '"seat MSG + pre-seat probe + probe receipt; "',
    "= seat MSG + pre-seat probe + probe receipt;",
    "facts helper",
    # registered-row sha citations
    "bm-a r789 freeze 18231a529",
    "W163 row bm-a r789 freeze",
    "18231a529, SINGLE STATE zero seat gap W2..W163 all",
    '"number law after the REGISTERED W163 row bm-a r789 freeze "',
    '"18231a529, SINGLE STATE zero seat gap W2..W163 all "',
    '"finalize one-pass bm-a r790, net chain head 764,012, "',
    # jump phrases (healed fragment carried via @JB@)
    "own-wave A window reserved jumps to 377_604, first-clean ",
    "jumps to 377_604, first-clean 377_604..377_803 hops=1",
    "jumps to 377_604 -> 377_604..377_803,",
    "377_604 and lands 377_604..377_803",
    # freeze-session / prior-finalize / receipt / gate-session composites
    "bm-a r792 freeze", "r792 bm-a freeze",
    "W163 finalize landed same-window r790",
    "W163 finalize one-pass bm-a r790", "W163 bm-a r790 one-pass",
    "_r794bma_w165_probe_receipt.json", "_r794bma_w165_band_gate.json",
    "r789 gate leg3", "r789 gate", "r790 sec8 succession", "r790 sec8",
    # seat tokens
    "bma-w164-seat", "MSG-183x",
    # base-relation composites
    "375_603+1", "377_603+1",
    # shard identity
    "n1w164",
    # delivery-window prose
    "direct fast-forward behind-0",
    "r792 pre-seat",
    # stale-residue sentinels (must stay ABSENT from W164 faces)
    "364_404..364_203", "364_604..362_603", "373_204", "373_404", "373_603",
    "373_403", "371_204", "678a07d4f", "6957f509e", "twentieth", "twenty-first",
    "seventy-seventh", "seventy-eighth", "ONE HUNDRED-AND-FIFTY-THIRD",
    "engine_owner rows 151", "rows 78 + candidate", "761,812", "354,320",
    "1d43d7906", "MSG-2026-10-06-175x", "bma-w163-seat", "MSG-175x",
    "r785 gate", "r786 sec8", "merge-absorb", "bm-b r779",
]
for n in needles:
    receipt["needles"][n] = {
        "pf": pfsrc.count(n), "n1": n1src.count(n),
        "pf_blk": blk_pf.count(n), "entry": entry163.count(n),
        "mat": blk_mat.count(n), "claim": claim163.count(n),
    }
io.open(r"results\_r794bma_w165_face_probe_receipt.json", "w", encoding="utf-8").write(
    json.dumps(receipt, indent=1, ensure_ascii=False))
print("probe rc0: pf_blk", len(blk_pf), "entry", len(entry163),
      "mat", len(blk_mat), "claim", len(claim163),
      "chain n=", len(receipt["mat_chain_rows"]),
      "tail", receipt["mat_chain_rows"][-3:])
