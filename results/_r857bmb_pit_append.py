# -*- coding: utf-8 -*-
# r857 bm-b S4: pit direct-write to pit-encoding.md (r666 direct-write exception,
# main CODELY.md at 30,510B red-line headroom 210B). Byte-face append per r838/r839.
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, "research", "pit-encoding.md")
b = open(P, "rb").read()
crlf = b.count(b"\r\n")
lf = b.count(b"\n")
eol = b"\r\n" if crlf * 2 > lf else b"\n"   # dominant-EOL convention of the target file
entry = ("- [2026-10-11 03:20 r857 bm-b] **专用 replace 工具=文本写面，对混态 EOL 件全文归一（r857 实弹：round_reports.md 主 CRLF 1508/1510+2 个 LF 行，replace 尾部追加把 r854/r855 两 LF 行归一成 CRLF→git diff 假 2+/2- 文本恒等假改；姊妹面=replace old_string 非行唯一时命中行内前缀即拆行污染——r857 首追加误吃 r856 addendum 行头，自检捕获→git checkout 恢复（该件零其他本地脏）→锚定尾部字节面重追加→python rb/wb per-line 恢复两 LF 行→git diff -U0 恰 1+/0- 收口）**。How to apply：混态/敏感 EOL 件（round_reports.md、CODELY.md、pit-* 族）的追加/手术一律 python rb/wb 字节面（r838/r839 律的工具面扩展——专用 replace 工具不是字节面例外）；术后自检=git diff -U0 恰=意图行数+diff 行文本恒等但记改=EOL 被翻译红旗。").encode("utf-8")
if not b.endswith(eol):
    b += eol
b += entry + eol
open(P, "wb").write(b)
print("pit-encoding.md appended: pre_crlf=%d pre_lf=%d used_eol=%s new_bytes=%d total=%d" % (crlf, lf, "CRLF" if eol == b"\r\n" else "LF", len(entry), len(b)))
