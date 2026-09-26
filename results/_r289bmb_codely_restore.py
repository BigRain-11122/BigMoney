# -*- coding: utf-8 -*-
"""r289 bm-b: fix CODELY.md resurrection (my rebase union reverted bm-a's
group-order compaction 8a00f514 O-20260927-0230).
- extract my post-base appends (r287+r288 law entries) from current face
- append them line-lossless to research/memory-archive/202609.md (LF, tail-nl)
- append new r289 kenglu entry (union-resurrection law)
- restore CODELY.md = byte-exact compacted face from 8a00f514 blob
- verify <=10KB hard line (group order criterion)
"""
import subprocess

def show(ref):
    return subprocess.run(["git", "show", ref], capture_output=True).stdout

base = show("25adaf8d:CODELY.md")
compacted = show("8a00f514:CODELY.md")
cur = open("CODELY.md", "rb").read()

assert cur.startswith(base), "current face not base+append -- abort"
assert len(cur) >= len(base)
mine = cur[len(base):]
assert mine[:1] in (b"[", b"-"), "append boundary not at entry start -- abort"
base_ends_nl = base.endswith(b"\n")
assert base_ends_nl, "base lacks trailing newline -- boundary risk"

arch_path = "research/memory-archive/202609.md"
arch = open(arch_path, "rb").read()
assert arch.endswith(b"\n") and b"\r\n" not in arch[-200:], "archive face probe fail"
arch_new = arch + mine if mine.endswith(b"\n") else arch + mine + b"\n"

k289 = (
    "- [2026-09-27 02:5x] 坑律（bm-b r289·rebase CODELY 复活面·r281 base 锚 union 律新参·E1 push 后自捕）："
    "**base 锚字节 union 的两侧必须全长前缀断言（len(side)>=len(base) 且 startswith(base) 全量）——"
    "对侧执行热冷整编把件缩到 base 以下时，startswith(base[:400]) 头部探针照过而 suffix=b2[len(b1):]=空"
    "=整编面被静默丢弃+旧面复活（实弹：bm-a 8a00f514 集团令 O-20260927-0230 把 CODELY.md 50.8KB->1.8KB，"
    "本机 rebase union 复活 49KB 面并已 push=集团令判据红）；正律=①union 前探两侧 len 与全前缀恒等，"
    "违者=compact/rewrite 形态落手工配方面（take-side 或重建），禁头部 N 字节探针代理全长断言"
    "②集团令判据（<=10KB 硬线）验收=push 后复测字节面③复活事故修复=对侧正典面 byte-exact 恢复"
    "+自家 append 迁 archive+诚实留痕。指针=results/_r289bmb_resolve.py 修正段+r289 轮报告**\n"
).encode("utf-8")
arch_new += k289

open(arch_path, "wb").write(arch_new)
open("CODELY.md", "wb").write(compacted)

c_bytes = len(compacted)
a_bytes = len(arch_new)
assert c_bytes <= 10 * 1024, "compacted face over 10KB hard line"
lines_before = arch.decode("utf-8-sig").count("\n")
lines_after = arch_new.decode("utf-8-sig").count("\n")
print("CODELY.md restored: %dB (<=10KB line OK)" % c_bytes)
print("archive: %d -> %dB, lines %d -> %d (append-only +%d)"
      % (len(arch), a_bytes, lines_before, lines_after,
         lines_after - lines_before))
print("my appends migrated: %dB" % len(mine))
