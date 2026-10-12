# -*- coding: utf-8 -*-
# W219 freeze-prep step 1: replay-extract the 46 W218-face prereg blocks via
# the committed lineage chain (W216 derive PAIRS literal -> W217 derive SUB
# -> W218 derive SUB), materialized for W219 SUB-map construction.
# Zero transcription; same replay lineage the W218 derive itself used.
import ast, sys

sys.stdout.reconfigure(encoding="utf-8")

def extract_lit(path, varname, expect):
    src = open(path, encoding="utf-8").read()
    val = None
    for node in ast.walk(ast.parse(src)):
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == varname:
            try:
                cand = ast.literal_eval(node.value)
            except Exception:
                cand = None
            if cand:
                val = cand
                break
    assert val and len(val) == expect, f"{varname} extract failed: {len(val) if val else 0}"
    return val

pairs216 = extract_lit(r"results\_w216bmc_prereg_derive.py", "PAIRS", 46)
SUB17 = extract_lit(r"results\_w217bmc_prereg_derive.py", "SUB", 46)
SUB18 = extract_lit(r"results\_w218bmc_prereg_derive.py", "SUB", 46)

OLD16 = [b.replace("@L14@", "214").replace("@T15@", "15") for _, b in pairs216]
OLD17 = []
for i, old in enumerate(OLD16):
    new = old
    for find, repl in SUB17[i]:
        c = new.count(find)
        assert c == 1, f"replay SUB17[{i}] count {c} != 1 for: {find[:60]}..."
        new = new.replace(find, repl, 1)
    OLD17.append(new.replace("@L14@", "214").replace("@L15@", "215").replace("@T16@", "16"))
OLD = []
for i, old in enumerate(OLD17):
    new = old
    for find, repl in SUB18[i]:
        c = new.count(find)
        assert c == 1, f"replay SUB18[{i}] count {c} != 1 for: {find[:60]}..."
        new = new.replace(find, repl, 1)
    OLD.append(new.replace("@L14@", "214").replace("@L15@", "215").replace("@L16@", "216").replace("@T17@", "17"))

out = []
for i, block in enumerate(OLD):
    out.append(f"===== BLOCK[{i}] len={len(block)} =====")
    out.append(block)
open(r"results\_w219bmc_pairs_replay_dump.txt", "w", encoding="utf-8").write("\n".join(out))
print("dumped 46 W218-face blocks -> results/_w219bmc_pairs_replay_dump.txt")
print("total bytes:", sum(len(b) for b in OLD))
