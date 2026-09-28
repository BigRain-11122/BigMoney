# r396 bm-a: hot/cold recompile (watermark law) - archive r394 pit entry verbatim (batch 42,
# 41 taken by bm-c r127 window in quant-mirror CODELY), add cold pointer, append new r396 entry.
import io

CODELY = "CODELY.md"
ARCHIVE = "research/memory-archive/202609.md"

r394_marker = "- [2026-09-28 08:5x r394 bm-a] 坑律："
r150_marker = "- [2026-09-28 09:0x r150 bm-c] 坑律："
pointer_40_marker = "冷层指针：坑律正典 2026-09-28 四十批"

with io.open(CODELY, encoding="utf-8") as fh:
    lines = fh.read().splitlines(keepends=True)

# locate r394 entry (single line)
idx394 = [i for i, l in enumerate(lines) if l.startswith(r394_marker)]
assert len(idx394) == 1, f"r394 entry count {len(idx394)}"
i = idx394[0]
r394_line = lines[i].rstrip("\r\n")
# capture full logical line (entries are single lines)
r394_verbatim = r394_line

idx40 = [j for j, l in enumerate(lines) if l.startswith(pointer_40_marker)]
assert len(idx40) == 1, f"pointer40 count {len(idx40)}"

pointer_42 = ("冷层指针：坑律正典 2026-09-28 四十二批（r396 bm-a 窗·水位律当窗整编：新坑律 append 后超 ≤10KB 硬线）："
               "r394 MSG 声明盲窗同窗双实现撞车 一条全文 verbatim=archive 202609.md『坑律归档 2026-09-28 四十二批』节"
               "（行级零丢失校验）。（四十一批=bm-c r127 窗在 quant 镜像 CODELY 面在册·本仓 archive 未见其节——本批取四十二批避撞）\n")

new_entry = ("- [2026-09-28 09:3x r396 bm-a] 坑律：**跨机 inbox ALL 件归档竞态——他机先归档同件至 processed/ 并推 origin 后，"
             "本机 untracked 归档副本挡 pull checkout（untracked working tree files would be overwritten by merge）；"
             "且 origin 侧副本常为同内容异形态（他机归档重排/换行/编码致字节不同、长度可更长）**（r396 实弹：MSG-0908 bmb→ALL "
             "双机同窗各自归档；bma 本地 Move-Item 副本挡 pull；fc /b 全文差异但原文语义恒等=他机处置注记版）。How to apply："
             "①挡检先 git show origin:<path> 与本地副本内容比对（处置注记/换行形态差异属正常·原文全含=语义等价）→删本地 untracked "
             "副本让 origin 版落地（README §4 commit 时序后到让路族）；②stash 不含 untracked=stash-push 后 untracked processed 副本仍挡 "
             "pull，勿反复 stash-pop 打转；③删本地后 pull 若撞 rename/delete UD=保 HEAD 侧（origin 归档已达成同意图）git add 收口+stash drop。"
             "指针=本窗 33e129dd 拉齐序。\n")

# remove r394 line
del lines[i]
# pointer_42 inserted right after pointer_40 line (recompute index after deletion)
idx40 = [j for j, l in enumerate(lines) if l.startswith(pointer_40_marker)][0]
lines.insert(idx40 + 1, pointer_42)
# append new entry at end
if lines and not lines[-1].endswith("\n"):
    lines[-1] += "\n"
lines.append(new_entry)

with io.open(CODELY, "w", encoding="utf-8", newline="") as fh:
    fh.write("".join(lines))

# archive append (verbatim containment)
section = ("\n## 坑律归档 2026-09-28 四十二批（r396 bm-a 窗·水位律当窗整编：新坑律 append 后超 ≤10KB 硬线）\n\n"
           + r394_verbatim + "\n")
with io.open(ARCHIVE, "a", encoding="utf-8", newline="") as fh:
    fh.write(section)

# containment verify: r394 text present in archive, absent from CODELY hot layer
with io.open(ARCHIVE, encoding="utf-8") as fh:
    arch = fh.read()
assert r394_verbatim in arch, "archive containment FAIL"
with io.open(CODELY, encoding="utf-8") as fh:
    hot = fh.read()
assert r394_verbatim not in hot, "CODELY still carries r394 hot"
import os
print("recompile OK; CODELY bytes:", os.path.getsize(CODELY), "<= 10240:", os.path.getsize(CODELY) <= 10240)
