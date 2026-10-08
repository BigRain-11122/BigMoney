# -*- coding: utf-8 -*-
# r894-adoption probe: apply s90 to the four physical dumps and check every
# remaining spot-check assertion string in physical-byte form.
import ast, io, sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
src = io.open(r"results/_r894bma_w191_freeze_buildgen.py", encoding="utf-8").read()
tree = ast.parse(src)
ns = {"NL": "\r\n"}
for node in tree.body:
    if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "S90":
        ns["S90"] = ast.literal_eval(node.value)
    if isinstance(node, ast.FunctionDef) and node.name == "s90":
        exec(compile(ast.Module([node], []), "<s90>", "exec"), ns)
s90 = ns["s90"]

DUMPS = {
    "EN": io.open(r"results/_r893bma_w191_probe_n1_entry.txt", encoding="utf-8", newline="").read(),
    "MAT": io.open(r"results/_r893bma_w191_probe_n1_mat.txt", encoding="utf-8", newline="").read(),
    "CL": io.open(r"results/_r893bma_w191_probe_n1_claim.txt", encoding="utf-8", newline="").read(),
    "PF": io.open(r"results/_r893bma_w191_probe_pf_block.txt", encoding="utf-8", newline="").read(),
}

checks = {
    "EN": [
        ('"a_seed_base": 435_004,', "seed A"),
        ('"b_exit_seed_base": 437_004,', "seed B"),
        ('"batch": "PERPETUAL-N1-W191",', "batch"),
        ("ONE HUNDRED-AND-NINETY-FIRST ENGINE-OWNED WAVE", "ordinal"),
        ("engine_owner rows 180 + candidate", "rows"),
        ("W1..W190 finalize ALL LANDED (W190 finalize one-pass bm-a r892, net chain head 825,328", "finalize citation (idealized)"),
        ("W1..W190 finalize ALL LANDED (W190 ", "finalize citation frag1"),
        ("finalize one-pass bm-a r892, net chain head 825,328, ", "finalize citation frag2"),
        ("W192+ projection ", "next-wave proj"),
    ],
    "MAT": [
        ('"registered W190 row parity drift (r307; bm-a r892)"', "last parity stamp"),
        ('"registered W189 row parity drift (r307; bm-a r882)"', "stale quirk stamp"),
        ('assert pf.N1_BANDS[187] == {"a": (426_204, 428_203),', "parity tuple"),
        ("_set_wave(191)", "set_wave new"),
        ("_set_wave(190)", "set_wave old (must be ABSENT)"),
        ("arith_a190 = set(range(435_004, 437_004))", "arith A"),
        ("arith_b190 = set(range(437_004, 437_204))", "arith B"),
        ("range(17, 191)", "dep range"),
    ],
    "CL": [
        ('"r894 bm-a] "', "claim stamp"),
        ("one-hundred-seventh owned claim", "claim ordinal"),
    ],
    "PF": [
        ("bm-a r892-closeout-window archive move (the W191", "archive prose (fixed)"),
        ("seat MSG sits in fleet/inbox/processed/ at freeze time", "archive prose frag2"),
    ],
}

for face, lst in checks.items():
    rolled = s90(DUMPS[face])
    for needle, label in lst:
        present = needle in rolled
        want = not (face == "MAT" and label.startswith("set_wave old"))
        status = "OK " if present == want else "FAIL"
        print("%s %s [%s] present=%s" % (status, face, label, present))
