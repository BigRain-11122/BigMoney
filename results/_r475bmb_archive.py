"""r475 bm-b: hot-cold archival (CODELY.md >10KB hard line -> same-window archival).
Moves three closed pitlaw entries verbatim to research/memory-archive/202609.md
under a new window-batch section, replaces them with one cold pointer line
(r444 pointer-merge paradigm), then verifies line-level zero loss."""
import io

CODELY = r"CODELY.md"
ARCHIVE = r"research\memory-archive\202609.md"
PREFIXES = (
    "- [2026-09-30 r472 bm-b]",
    "- [2026-09-30 r473 bm-b]",
    "- [2026-09-30 18:2x r485 bm-a]",
)
POINTER = ("- 冷层指针（r475 合并·指针合并归档 r444 范式）：r472 冻结探针事实消费三坑"
           "（W14 runner 门键名口径/面前缀/CSV 新列）+r473 同轮双 rebase 撞车窗三坑"
           "（ours-theirs 逐轮翻转/r261 幻影拒走双面/GIT_EDITOR 同调用）"
           "+r485 sina ETF 节前发布滞后四腿探针定谳——三条全文 verbatim="
           "archive 202609.md『热冷整编 2026-09-30 r475 bm-b 窗批』节。\n")
SECTION = "\n### 热冷整编 2026-09-30 r475 bm-b 窗批\n（CODELY.md 10KB 硬线当窗整编·r472/r473/r485 三条 verbatim 迁入；行级零丢失校验见轮报告 r475）\n\n"

lines = io.open(CODELY, encoding="utf-8").read().splitlines(keepends=True)
moved, kept, replaced = [], [], False
for ln in lines:
    if any(ln.startswith(p) for p in PREFIXES):
        moved.append(ln)
        if not replaced:
            kept.append(POINTER)
            replaced = True
    else:
        kept.append(ln)
assert len(moved) == 3, f"expected 3 entries, got {len(moved)}"
io.open(CODELY, "w", encoding="utf-8", newline="").write("".join(kept))

arch = io.open(ARCHIVE, encoding="utf-8").read()
if not arch.endswith("\n"):
    arch += "\n"
arch += SECTION + "".join(moved)
io.open(ARCHIVE, "w", encoding="utf-8", newline="").write(arch)

# line-level zero-loss verification
arch_now = io.open(ARCHIVE, encoding="utf-8").read()
lost = [m[:40] for m in moved if m.rstrip("\r\n") not in arch_now]
codely_now = io.open(CODELY, encoding="utf-8").read()
import os
print("moved:", len(moved), "| lost:", lost)
print("CODELY.md new size:", os.path.getsize(CODELY), "bytes (limit 10240)")
assert not lost and os.path.getsize(CODELY) <= 10240
print("zero-loss verified + under line OK")
