"""r189 bm-c CODELY.md hot-cold reorganization (water-level law: union result
10,573B > 10,240B hard line -> same-window reorg, D-20260924-01 pattern).

Moves the five 09-28 流水/坑律 entries verbatim into
research/memory-archive/202609.md under a new section, replaces them with
one cold-layer pointer line, verifies line-level zero loss + size.
"""
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CODELY = os.path.join(ROOT, "CODELY.md")
ARCHIVE = os.path.join(ROOT, "research", "memory-archive", "202609.md")

MOVE_PREFIXES = (
    "- [2026-09-28 21:5x] r183 bm-c 坑律六十七批",
    "- [2026-09-28 22:1x] r184 bm-c 坑律六十八批",
    "- [2026-09-28 22:41] r403 bm-a 执行记录",
    "- [2026-09-28 23:3x] r187 bm-c 判定回执",
    "- [2026-09-28 23:3x] r187 bm-c 坑律六十九批",
)

codely = io.open(CODELY, encoding="utf-8").read()
lines = codely.splitlines(keepends=True)
moved, kept = [], []
for ln in lines:
    if any(ln.startswith(p) for p in MOVE_PREFIXES):
        moved.append(ln)
    else:
        kept.append(ln)
assert len(moved) == 5, "expected 5 movable entries, got %d" % len(moved)

SECTION = (
    "\n## 坑律归档 2026-09-29 r189 bm-c 窗批\n\n"
    "（r189 bm-c 窗水位律当窗整编：CODELY.md union 面超 ≤10KB 硬线〔r400 bm-b 条目"
    "并入后 10,573B〕→六十七批/六十八批/r403 执行记录/r187 双条共 5 条 verbatim 归档"
    "本节·行级零丢失校验见轮报告 r189·热层保留 r400 bm-b 与七十批两条本窗新鲜教训。）\n"
)
arch = io.open(ARCHIVE, encoding="utf-8").read()
arch_new = arch.rstrip("\n") + "\n" + SECTION + "\n" + "".join(moved)
if not arch_new.endswith("\n"):
    arch_new += "\n"
io.open(ARCHIVE, "w", encoding="utf-8", newline="\n").write(arch_new)

POINTER = (
    "冷层指针：坑律正典 2026-09-28 六十七/六十八批+r403 bm-a 执行记录+r187 判定回执+"
    "六十九批（共 5 条·r189 bm-c 窗水位律当窗整编·行级零丢失校验）全文 verbatim="
    "archive 202609.md『坑律归档 2026-09-29 r189 bm-c 窗批』节。\n"
)
# insert pointer where the moved block used to start (after the last kept
# line preceding the moved region = keep positional continuity)
codely_new = "".join(kept)
codely_new = codely_new.replace(
    "### Reference\n",
    "### Reference\n" + POINTER, 1)
io.open(CODELY, "w", encoding="utf-8", newline="\n").write(codely_new)

# verification: zero line loss (each moved line present verbatim in archive)
arch_check = io.open(ARCHIVE, encoding="utf-8").read()
lost = [ln for ln in moved if ln.rstrip("\n") not in arch_check]
assert not lost, "LINE LOSS: %d lines missing verbatim" % len(lost)
size = len(codely_new.encode("utf-8"))
print("reorg OK: moved=5 lines, zero loss verified, CODELY bytes =", size,
      "(hard line 10240)")
if size > 10240:
    print("STILL OVER HARD LINE")
    sys.exit(3)
print("archive bytes =", len(arch_new.encode("utf-8")))
