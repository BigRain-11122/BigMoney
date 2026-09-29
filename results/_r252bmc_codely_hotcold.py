# -*- coding: utf-8 -*-
"""r252 bm-c CODELY hot-cold reorg (v2: line-extracted verbatim, no hand-copy).
Migrate r240 (line 5) + r249 (line 34) entries to archive, leave pointers, append r252 pit."""
import os
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

CODELY = "CODELY.md"
ARCHIVE = "research/memory-archive/202609.md"

hot_lines = open(CODELY, encoding="utf-8").read().splitlines()
arc = open(ARCHIVE, encoding="utf-8").read()

# locate by content markers, assert uniqueness
idx240 = [i for i, ln in enumerate(hot_lines) if "r240 bm-c" in ln and "2026-09-29" in ln]
idx249 = [i for i, ln in enumerate(hot_lines) if ln.startswith("- [2026-09-30 03:2x r249 bm-c]")]
assert len(idx240) == 1 and len(idx249) == 1, (idx240, idx249)
e240 = hot_lines[idx240[0]]
e249 = hot_lines[idx249[0]]
assert e240.startswith("### [2026-09-29 21:4x r240") and e249.startswith("- [2026-09-30 03:2x r249")

assert e240 not in arc and e249 not in arc, "already archived (non-idempotent guard)"

tag = "## 热冷整编 2026-09-30 r252 bm-c 窗批"
assert tag not in arc, "section already exists"
new_sec = ("\n" + tag + "\n\n> r252 W13 撞带让路窗热冷整编（水位 9,946B+新条将超 10,240B 硬线当窗即办·行级零丢失 "
            "moved 2/lost 0·迁移件=bm-c 本机旧律 r240/r249·活跃度=接续律已 r244/r249/r250/r252 四用稳定+"
            "to_csv 律已 W5 runner selftest 惯例承载；r240 条原文以 ### 头起如实 verbatim 保留）。\n\n"
            + e240 + "\n" + e249 + "\n")
arc_new = arc + new_sec

ptr240 = ("- 冷层指针：r240 tick 时限强杀零 commit 接续律（adopt-verify-close 取证三步+禁盲目重跑）全文 verbatim="
          "archive 202609.md『热冷整编 2026-09-30 r252 bm-c 窗批』节（r244/r249/r250/r252 四用稳定·死轮接续首查指针）。")
ptr249 = ("- 冷层指针：r249 pandas to_csv 浮点回读非逐位坑全文 verbatim=archive 202609.md『热冷整编 2026-09-30 "
          "r252 bm-c 窗批』节（法面=W5 runner selftest 读回帧锚惯例承载）。")
hot_lines[idx240[0]] = ptr240
hot_lines[idx249[0]] = ptr249

pit = ("- [2026-09-30 04:5x r252 bm-c] 泊位/冻结步开工前 inbox 零未读腿坑（W13 撞带让路实弹）：供给类开工三查漏 "
       "inbox 面——04:37 pull 已带入 bm-a 03:56 泊位声明 MSG 而 04:50 起草窗未读→draft/catalog 写完才发现撞带"
       "（幸零 commit 零 push=零外泄窗口自愈·r232 让路范式处置）。正法=泊位/冻结/认领类动作前置检查单三查扩四查："
       "job_list+fleet\\tasks+fetch 标题扫+**fleet\\inbox 未读清零**；死轮接续窗尤甚（取证三步注意力占满=漏 inbox 面）。"
       "How to apply：任何供给步开工前先做 inbox 差集（processed basename 全名比），有未读=先读后动再写。")
hot_lines.append(pit)

hot_new = "\n".join(hot_lines) + "\n"
arc_write = arc_new

# zero-loss verification BEFORE write
assert e240 in arc_new and e249 in arc_new
assert e240 not in hot_new and e249 not in hot_new
assert ptr240 in hot_new and ptr249 in hot_new and pit in hot_new

open(ARCHIVE, "w", encoding="utf-8", newline="").write(arc_write)
open(CODELY, "w", encoding="utf-8", newline="").write(hot_new)

chk_hot = open(CODELY, encoding="utf-8").read()
chk_arc = open(ARCHIVE, encoding="utf-8").read()
print("CODELY size:", os.path.getsize(CODELY), "| archive size:", os.path.getsize(ARCHIVE))
print("verbatim-in-archive:", e240 in chk_arc, e249 in chk_arc)
print("gone-from-hot:", e240 not in chk_hot, e249 not in chk_hot)
print("pointers+pits in hot:", ptr240 in chk_hot, ptr249 in chk_hot, pit in chk_hot)
