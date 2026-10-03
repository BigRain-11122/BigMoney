# -*- coding: utf-8 -*-
# r409 bm-c: surgical repair of the born-mojibake r407 pit entry in repo-root CODELY.md
# (state next-pointer item (c); prefix-match whole-line replace, BOM+newline preserving)
import io, sys

P = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\CODELY.md"
PREFIX = "[2026-10-03 09:1x r407 bm-c] CLI replace"

NEW = "- [2026-10-03 09:1x r407 bm-c]（r409 事实重建注记：本条原版当窗生而 mojibake——replace 落盘通道编码事故 CJK 全灭为 '?'，CODELY 本行与 round_reports-bm-c.md r407 行同窗双面中毒·commit 53b96bdcb 即坏·git 无干净原版，以下按幸存 ASCII 锚与提交物证重建）坑面①（代码手术）=CLI replace 大块手术 monthly_exam_prep.py criteria 子命令时未逐字保留相邻不动行→一个 def 被吃→python 首跑 NameError（'... not defined'）·^def 对账定位缺失 def 修复（幸存锚：4/def/NameError/^def）——GM 侧 r281/r280 邻行吞噬坑本仓实弹复发。坑面②（写入通道）=当窗 replace 落盘把全部 CJK 替换为 '?'（ASCII 段完好+CJK 位灭失=编码替换型损坏非乱序型）。How to apply：python 件 replace 跨度>30 行改用 write_file 整文件重写，或事后必跑 py_compile+读回自检；遇 NameError 先 ^def 对账函数清单勿先疑机制；CJK 件任何 replace/落盘后必读回抽查 '?' 串，发现 mojibake 即以事实重建+标注重建禁留坏面入正典。"

with open(P, "rb") as f:
    raw = f.read()
bom = raw.startswith(b"\xef\xbb\xbf")
text = raw.decode("utf-8-sig")
nl = "\r\n" if "\r\n" in text else "\n"
lines = text.split(nl)
hits = [i for i, ln in enumerate(lines) if ln.startswith(PREFIX)]
if len(hits) != 1:
    print("ABORT prefix_hits=%d" % len(hits))
    sys.exit(2)
i = hits[0]
old = lines[i]
if "???" not in old:
    print("ABORT guard: target line has no mojibake ??? run")
    sys.exit(2)
lines[i] = NEW
out = nl.join(lines)
data = out.encode("utf-8")
if bom:
    data = b"\xef\xbb\xbf" + data
with open(P, "wb") as f:
    f.write(data)
print("REPAIRED line_index=%d old_len=%d new_len=%d bom=%s nl=%r" % (i, len(old), len(lines[i]), bom, nl))
print("NEW_HEAD=" + lines[i][:60])
print("QUESTION_RUN_CHECK=" + ("MOJIBAKE_STILL" if "???????" in lines[i] else "CLEAN"))
