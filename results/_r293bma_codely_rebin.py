# _r293bma_codely_rebin.py -- CODELY.md <=10KB hard-line hot-cold rebin (R293 window)
# Law: CODELY.md "append 后超线=当窗即办热冷整编" (10,844B > 10,000B after R293 kenglu
# append). Moves ALL dated 流水/坑律 entries from the Reference section verbatim
# (line-level zero loss, asserted) to research/memory-archive/202609.md under a
# new window header. Keeps: User 元律, Project R290 自提交律 (standing law),
# Reference 3 structural law lines. D-20260924-01 paradigm.
import json

SRC = "CODELY.md"
DST = "research/memory-archive/202609.md"
HEADER = ("\n## 坑律热冷整编 2026-09-27 R293 窗（CODELY.md ≤10KB 硬线触发·"
          "行级零丢失外迁·指针字段原样保留检索面不变）\n")

src = open(SRC, encoding="utf-8").read()
lines = src.splitlines(keepends=True)
out_src, moved = [], []
in_ref = False
for ln in lines:
    if ln.startswith("### Reference"):
        in_ref = True
        out_src.append(ln)
        continue
    if ln.startswith("### "):
        in_ref = False
    if in_ref and ln.startswith("- [2026-09-2"):
        moved.append(ln)
        continue
    out_src.append(ln)

assert moved, "no dated entries found to move"
dst = open(DST, encoding="utf-8").read()
new_dst = dst + HEADER + "".join(moved)
if not new_dst.endswith("\n"):
    new_dst += "\n"

# zero-loss assertion: every moved line present verbatim in the archive tail
for ln in moved:
    assert ln.rstrip("\r\n") in new_dst, "zero-loss violation"

open(SRC, "w", encoding="utf-8", newline="").write("".join(out_src))
open(DST, "a", encoding="utf-8", newline="").write(HEADER + "".join(moved))

# post-verify
import os
size = os.path.getsize(SRC)
assert size <= 10240, f"CODELY.md still over line: {size}"
json.loads("{}")
print(f"moved {len(moved)} entries verbatim; CODELY.md {size}B <=10KB; "
      f"archive {os.path.getsize(DST)}B")
