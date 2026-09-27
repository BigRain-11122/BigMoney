# -*- coding: utf-8 -*-
"""r356 bm-b: CODELY.md hot-cold re-archive (O-20260927-0230 <=10KB hard line, append-triggered).
Moves the 9 storm-window pit entries verbatim to research/memory-archive/202609.md
section '坑律归档 2026-09-28 二十六批', replaces them with one cold-pointer line,
appends the new r356 pit entry (PS env-prefix face). Line-level zero-loss verified."""
import io, os, sys

CODELY = "CODELY.md"
ARCHIVE = "research/memory-archive/202609.md"

codely_src = io.open(CODELY, encoding="utf-8").read()
lines = codely_src.split("\n")

# 1) identify the 9 storm entries: lines starting with "- [2026-09-28 02:"
storm = [l for l in lines if l.startswith("- [2026-09-28 02:")]
print("storm entries found:", len(storm))
assert len(storm) == 9, "expected exactly 9 storm entries (r123/r370/r352x2/r353/r354/r125/r373/r355)"
for l in storm:
    print("  ", l[:60])

# 2) new pit entry (r356, hot - stays in CODELY.md)
new_entry = ("- [2026-09-28 03:4x r356 bm-b] 坑律：**PowerShell 无 bash 式 `VAR=x cmd` 环境变量前缀语法**——"
 "`GIT_EDITOR=true git rebase --continue` 在 PS=CommandNotFoundException，rebase --continue 根本没跑（无 git 输出无副作用），"
 "易误归因为 git 拒发（真拒发面另有 r368 bm-a 已录「You must edit all merge conflicts」EDITOR 傻终端族，本机 r356 实弹再证）；"
 "正典=PS 下先 `$env:GIT_EDITOR='true'` 再裸调命令；rebase-continue 拒发窗收尾一律走 r355-addendum 直连 workaround"
 "（commit -F→rebase --quit→update-ref→checkout）。How to apply：bash 命令带 env 前缀抄进 PS 前先拆两步；"
 "诊断「git 命令失败」先确认命令真的跑过。指针=results/_r356bmb_resolve.py。")

# 3) pointer line replacing the storm block
pointer = ("冷层指针：坑律正典 2026-09-28 风暴窗九条（r123/r370/r352×2/r353/r354/r125/r373/r355）"
 "已 verbatim 整编至 research/memory-archive/202609.md『坑律归档 2026-09-28 二十六批』节"
 "（r356 bm-b 窗·行级零丢失校验）。")

# 4) build new CODELY.md: drop storm lines, insert pointer after the 二十五批 pointer line, append new entry
out_lines = []
storm_set = set(storm)
inserted_pointer = False
for l in lines:
    if l in storm_set:
        if not inserted_pointer:
            out_lines.append(pointer)
            inserted_pointer = True
        continue
    out_lines.append(l)
out_lines.append(new_entry)
new_codely = "\n".join(out_lines)

# 5) archive: append section + verbatim storm entries
arch_src = io.open(ARCHIVE, encoding="utf-8").read()
header = "## 坑律归档 2026-09-28 二十六批（r356 bm-b 窗·O-20260927-0230 ≤10KB 硬线·当窗整编·行级零丢失校验）"
if not arch_src.endswith("\n"):
    arch_src += "\n"
arch_new = arch_src + "\n" + header + "\n\n" + "\n".join(storm) + "\n"

# 6) line-level zero-loss verification: every storm line byte-identical inside archive_new
for l in storm:
    assert ("\n" + l + "\n") in ("\n" + arch_new + "\n"), "ZERO-LOSS VIOLATION: " + l[:50]
print("zero-loss verify: 9/9 lines verbatim in archive PASS")

# 7) parse sanity + size gates
assert pointer in new_codely and new_entry in new_codely
for l in storm:
    assert l not in new_codely.split("\n"), "storm line still in CODELY: " + l[:50]
size_c = len(new_codely.encode("utf-8"))
print("CODELY.md new size:", size_c, "bytes (hard line 10240)")
assert size_c <= 10240, "CODELY.md still over 10KB hard line"
size_a = len(arch_new.encode("utf-8"))
print("archive new size:", size_a)

io.open(CODELY, "w", encoding="utf-8", newline="").write(new_codely)
io.open(ARCHIVE, "a", encoding="utf-8", newline="").write("\n" + header + "\n\n" + "\n".join(storm) + "\n")

# 8) post-write re-verify from disk
c2 = io.open(CODELY, encoding="utf-8").read()
a2 = io.open(ARCHIVE, encoding="utf-8").read()
ok = all(("\n" + l + "\n") in ("\n" + a2 + "\n") for l in storm) and new_entry in c2 and len(c2.encode("utf-8")) <= 10240
print("post-write re-verify:", "PASS" if ok else "FAIL")
print("REARCHIVE_OK")
