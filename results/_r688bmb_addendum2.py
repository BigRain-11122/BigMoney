# -*- coding: utf-8 -*-
"""r688 bm-b addendum #2: paren incident honest disclosure (bytes append,
marker-count==0 gate; run-verify-then-commit per r657-iii)."""
import os
from datetime import datetime, timedelta, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RR = os.path.join(ROOT, "logs", "iteration-loop", "round_reports.md")

CST = timezone(timedelta(hours=8))
ts = datetime.now(CST).isoformat(timespec="seconds")

marker = "| round 688 addendum-2 (bm-b) ".encode("utf-8")
data = open(RR, "rb").read()
pre = data.count(marker)
assert pre == 0, f"addendum-2 marker already present count={pre}"
if data.endswith(b"\r\n"):
    prefix, eol = b"", b"\r\n"
elif data.endswith(b"\n"):
    prefix, eol = b"", b"\n"
else:
    prefix, eol = b"\n", b"\n"
line = (
    f"{ts} | round 688 addendum-2 (bm-b) | 笔误披露（对 addendum-1「笔误披露：无」的即时勘正）"
    f"：addendum-1 追加脚本首版 __import__ 嵌套括号未闭合=SyntaxError→append 未执行，"
    f"但同窗 ; 链继续 add+commit=把坏 .py 单件推上 origin（74655bf5a·RR 零变化）；"
    f"当窗自愈=正规 import 重写+复跑 ADDENDUM_OK post_marker=1+补推 DELIVERED "
    f"74655bf5a..ad9d649a1（commit message 已如实披露）。定性=r657-③ 已知律重犯"
    f"（手术步与 add/commit 禁 ; 链耦联——自抓自愈零 origin 伤害零数据损失）；"
    f"非新坑不立新律，本行即执法记录：后续 append 类脚本一律分步执行（跑毕验 sentinel "
    f"再 add/commit）。本地未达 origin commit 数=0（ad9d649a1 push 后 fetch+rev-list 0/0）")
with open(RR, "ab") as f:
    f.write(prefix + line.encode("utf-8") + eol)
post = open(RR, "rb").read().count(marker)
assert post == 1, f"post marker count={post}"
print("ADDENDUM2_OK post_marker=1")
