import json
r = json.load(open(r"results\_r822bma_w173_face_probe_receipt.json", encoding="utf-8"))
print("eol crlf:", r["pf_block_eol_crlf"], r["n1_entry_eol_crlf"],
      r["mat_block_eol_crlf"], r["claim_eol_crlf"])
n = r["needles"]
keys = [
    '172: {"a": (393_204, 395_203), "b_exit": (395_204, 395_403),',
    '"a_seed_base": 393_204,', '"b_exit_seed_base": 395_204,',
    '395_204..397_203', '395_404..395_603',
    'W173 A window; W173 freezer MUST re-derive on the post-W172',
    'r819 bm-a] ', 'jumps to 395_204 -> 395_204..395_403,',
    'own-wave A window reserved jumps to 395_204, first-clean ',
    'set(range(393_204, 395_204))', 'set(range(395_204, 395_404))',
    '== 393_204 == 393_203 + 1', '== 395_204 == 395_203 + 1',
    '456f3affc', '59fde9319', 'r814 probe leg4', 'r819 sec8 succession',
    'MSG-2026-10-07-1012', '01a7480e1', '781,612', '374,120',
    'ONE HUNDRED-AND-SIXTY-SECOND', 'eighty-seventh', 'thirty-first',
    '(3-item; the W171 finalize product already on origin since r816',
    'move DEFERRED to the W172 finalize window',
    'single-window derive (r812 merged the gate legs INTO the',
    'payload = seat MSG + pre-seat probe script + probe receipt',
]
for k in keys:
    v = n[k]
    print("pf=%d n1=%d pfblk=%d entry=%d mat=%d claim=%d | %s"
          % (v["pf"], v["n1"], v["pf_blk"], v["entry"], v["mat"], v["claim"], k[:58]))
