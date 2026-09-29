#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""r253 bm-c: CODELY hot-cold reorg NOW (merged 10297B > 10240B hard line).
Move r455 bm-a S5-orphan-pit entry verbatim -> archive new r253 section, leave cold ptr."""
import os, subprocess, sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CODELY = os.path.join(ROOT, "CODELY.md")
ARCH = os.path.join(ROOT, "research", "memory-archive", "202609.md")

with open(CODELY, "rb") as f:
    data = f.read()
lines = data.splitlines(keepends=True)
def dec(b): return b.decode("utf-8", "replace")

hits = [i for i, l in enumerate(lines) if dec(l).startswith("- [2026-09-30 03:1x r455 bm-a] S5 轮报告路径孤儿坑")]
assert len(hits) == 1, "r455 entry not unique: %r" % hits
idx = hits[0]
entry = lines[idx]
ptr = ("- 冷层指针：r455 S5 轮报告路径孤儿坑全文 verbatim=archive 202609.md『热冷整编 2026-09-30 r253 bm-c 窗批』节"
       "（法面=S5 正典位路径已入轮 prompt 常量+孤儿 verbatim 并回正典惯例承载）。\n").encode("utf-8")
lines[idx] = ptr
out = b"".join(lines)
if not out.endswith(b"\n"):
    out += b"\n"
with open(CODELY, "wb") as f:
    f.write(out)

sec = "\n## 热冷整编 2026-09-30 r253 bm-c 窗批\n\n".encode("utf-8") + \
      "> r253 rebase 撞批收口窗热冷整编（r446/r252 双侧合并后 10,297B 超 10,240B 硬线当窗即办·moved 1/lost 0·行级零丢失校验）。\n\n".encode("utf-8") + \
      entry
with open(ARCH, "ab") as f:
    f.write(sec)

subprocess.run(["git", "add", "--", "CODELY.md", "research/memory-archive/202609.md"], cwd=ROOT, check=True)
print("CODELY now %dB (entry moved %dB, ptr %dB)" % (len(out), len(entry), len(ptr)))
print("archive + section %dB" % len(sec))
