# -*- coding: utf-8 -*-
# r554 bm-c S4: CODELY.md pit append (bytes, EOL-preserving per r503 law).
# Four-question gate passed: long-term value (lineage copy discipline,
# assertion-layer family), not covered elsewhere (r531 = command paths;
# this = copy driver replacement double-apply), lesson-first, one-matter.
import os

P = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\CODELY.md"
entry = (u"- [2026-10-05 15:5x r554 bm-c] **lineage 复制替换链 double-apply→legdiff 自比较空转假 PASS"
         u"（断言层假阳性族 r419/r549 新面·r554 实弹修复）**：r553 lineage_copy 对 legdiff 的替换组"
         u"（\"_r550bmc_s6_chain.py\"→\"_r552bmc_s6_chain.py\"）+（\"_r552bmc_s6_chain.py\"→\"_r553bmc_s6_chain.py\"）"
         u"顺序全文 str.replace——第一步产物新增的第 2 处 \"_r552bmc_s6_chain.py\" 被第二步一并改名"
         u"→r553 legdiff OLD=NEW=同一文件=自比较恒 PASS（收据谎报「vs r552 lineage」未发生的比较·"
         u"真门=lineage_copy 内 LEGS 块恒等断言当时在位才零漏检·代码注释「must not double-apply」"
         u"自身未被执行=声明与实现脱节）。正法=①legdiff 血统替换只改 NEW 行路径（OLD 钉前轮真文件）"
         u"②复制器替换组禁前后件重叠（old_i 后件=new_{i+1} 前件=红旗·r554 复制器已加 assert old not in news）"
         u"③收据禁引用未发生的比较。How to apply：复制 legdiff/对账器血统先核 OLD/NEW 两行指向不同真文件；"
         u"见「CMD_IDENTICAL=True」先查比较对象是否同一文件。")

raw = open(P, "rb").read()
eol = b"\r\n" if b"\r\n" in raw[-4000:] else b"\n"
assert b"r554 bm-c] **lineage" not in raw, "entry already present"
assert raw.rstrip(eol).decode("utf-8", "replace").endswith(u"禁盲目重推。"), "tail not the r553 entry"
entry_b = entry.encode("utf-8")
if eol == b"\r\n":
    entry_b = entry_b.replace(b"\n", b"\r\n")
if not raw.endswith(eol):
    raw += eol
raw += eol + entry_b + eol
open(P, "wb").write(raw)
check = open(P, "rb").read()
assert check.count("r554 bm-c] **lineage \u590d\u5236\u66ff\u6362\u94fe".encode("utf-8")) == 1
print("CODELY appended %dB, EOL=%r, count=1" % (len(entry_b), eol))
