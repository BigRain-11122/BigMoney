"""r243 repair: un-glue reorg header from previous last archive line
(cold file lacked trailing newline; append glued header onto it)."""
import io

P = "research/memory-archive/202609.md"
MARK = " - [2026-09-26 11:5x] 热冷整编执行记录"
txt = io.open(P, encoding="utf-8").read()
lines = txt.splitlines()
fixed, n_glued = [], 0
for l in lines:
    if MARK in l and not l.startswith(MARK):
        i = l.find(MARK)
        fixed.append(l[:i].rstrip())
        fixed.append(l[i:])
        n_glued += 1
    else:
        fixed.append(l)
assert n_glued == 1, n_glued
io.open(P, "w", encoding="utf-8", newline="").write("\n".join(fixed) + "\n")
back = io.open(P, encoding="utf-8").read().splitlines()
assert MARK.strip() in [x.strip() for x in back if MARK.strip() in x]
print("unglued 1 line; archive lines now:", len(back))
print("repair OK")
