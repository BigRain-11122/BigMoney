# -*- coding: utf-8 -*-
"""r150 bm-c CODELY hot-cold integration (S4 water-line law).

Append new r150 pitlaw entry -> size over <=10KB hard line -> archive
the three existing hot entries (r392/r149/r368) verbatim to
research/memory-archive/202609.md batch 39 -> pointer line back in hot
-> line-level zero-loss verification."""
import io

CODELY = "CODELY.md"
ARCHIVE = "research/memory-archive/202609.md"
HARD = 10240

new_entry = (
    "- [2026-09-28 09:0x r150 bm-c] 坑律：**池文件全幅 UU 的冲突界切在 JSON 顶层"
    "对象内部——三段（ours/base/theirs）各缺共享尾的顶层闭括号 `}`，单独解析必"
    " JSONDecodeError；共享尾（`>>>>>>>` 之后）恰为该括号**（r150 实弹："
    "runnable_pool.json 撞 bm-b tick keepalive 整文件冲突，ours 段尾=entries `]` "
    "止、顶层 `}` 在 >>>>>>> 后公共区；误按完整段解析= Expecting ',' delimiter 假"
    "象勿据此判侧）。How to apply：解析器按标记行切三段后各补 `\\n}` 才是完整 "
    "JSON；断言共享尾 strip 后恒等 `}`（异样=冲突界形态变体须重判勿套用）；union "
    "后按完整顶层 dict 序列化写回，禁分段拼接。指针=results/_r150bmc_resolve_pool."
    "py（三断言护栏）+commit 5010fc0b。\n")

hot = io.open(CODELY, "r", encoding="utf-8", newline="").read()
lines = hot.split("\n")

# hot entry lines to archive (the three existing pitlaw entries)
entry_prefixes = ("- [2026-09-28 08:2x r392 bm-a] 坑律：",
                  "- [2026-09-28 08:3x r149 bm-c] 坑律：",
                  "- [2026-09-28 08:3x r368 bm-b] 坑律：")
idx = [i for i, ln in enumerate(lines)
       if ln.startswith(entry_prefixes)]
assert len(idx) == 3, f"expected 3 hot entries, found {len(idx)}"
moved = [lines[i] for i in idx]

# 1) append new entry at end (keep trailing newline shape)
assert hot.endswith("\n"), "hot file must end with newline"
hot2 = hot + new_entry
assert len(hot2.encode('utf-8')) > HARD, "integration trigger missing"

# 2) archive: append batch section verbatim (multiset move)
arch = io.open(ARCHIVE, "r", encoding="utf-8", newline="").read()
assert all(m in arch for m in [moved[0]]) is False or True  # dup guard below
batch_header = "\n## 坑律归档 2026-09-28 三十九批（r150 bm-c 窗·水位律当窗整编）\n\n"
for m in moved:
    assert m not in arch, f"dup-drag: entry already archived: {m[:40]}"
arch2 = arch + batch_header + "\n".join(moved) + "\n"
io.open(ARCHIVE, "w", encoding="utf-8", newline="\n").write(arch2)

# 3) hot: remove the three entries, insert pointer after batch-38 pointer
lines2 = [ln for i, ln in enumerate(lines) if i not in set(idx)]
pointer = ("冷层指针：坑律正典 2026-09-28 三十九批（r150 bm-c 窗·水位律当窗整编"
           "：r150 新坑律 append 后 10,513B 超 ≤10KB 硬线）：r392 认领幽灵面 "
           "staged-only 阻塞 / r149 rebase replay untracked 提取件挡 pick / "
           "r368 rebase-continue 第三拒发面（EDITOR unset）三条全文 verbatim"
           "=archive 202609.md『坑律归档 2026-09-28 三十九批』节（行级零丢失校"
           "验）。\n")
# find the batch-38 pointer line to insert after
p38 = next(i for i, ln in enumerate(lines2) if ln.startswith(
    "冷层指针：坑律正典 2026-09-28 三十八批"))
lines2.insert(p38 + 1, pointer)
hot3 = "\n".join(lines2)
if not hot3.endswith("\n"):
    hot3 += "\n"
io.open(CODELY, "w", encoding="utf-8", newline="\n").write(hot3)

# 4) zero-loss verification: every moved line present verbatim in archive
arch_check = io.open(ARCHIVE, "r", encoding="utf-8", newline="").read()
hot_check = io.open(CODELY, "r", encoding="utf-8", newline="").read()
for m in moved:
    assert m in arch_check, f"archived line missing: {m[:40]}"
    assert m not in hot_check, f"hot still holds archived line: {m[:40]}"
assert new_entry.strip() in hot_check, "new entry lost"
assert "三十九批" in hot_check, "pointer missing"
sz_hot = len(hot_check.encode('utf-8'))
sz_arch = len(arch_check.encode('utf-8'))
print(f"hot={sz_hot}B (line={HARD}: {'UNDER' if sz_hot <= HARD else 'OVER'})")
print(f"archive={sz_arch}B; moved={len(moved)} entries; zero-loss verified")
