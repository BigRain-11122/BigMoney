# -*- coding: utf-8 -*-
# Verify all 46 W220 SUB find-counts against the replayed OLD blocks.
import sys
sys.stdout.reconfigure(encoding="utf-8")
src = open(r"results\_w220bmc_prereg_derive.py", encoding="utf-8").read()
head = src.split("# ---------- build + apply W220 pairs ----------")[0]
ns = {}
exec(compile(head, "head", "exec"), ns)
OLD = ns["OLD"]
sub_src = src
start = sub_src.index("SUB = {")
end = sub_src.index("# ---------- build + apply W220 pairs ----------")
ns2 = {"RAM_GB": "~0.8", "RAM_REPLAY": ns["RAM_REPLAY"]}
exec(compile("RAM_GB = '~0.8'\n" + sub_src[start:end], "sub", "exec"), ns2)
SUB = ns2["SUB"]
bad = 0
for i in range(46):
    for j, (find, repl) in enumerate(SUB[i]):
        c = OLD[i].count(find)
        if c != 1:
            bad += 1
            print(f"BAD block[{i}].{j} count={c}: {find[:80]!r}")
print("total bad:", bad)
