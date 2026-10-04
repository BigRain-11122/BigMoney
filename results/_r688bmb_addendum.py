# -*- coding: utf-8 -*-
"""r688 bm-b addendum append: S7 closeout push-race record (bytes append,
r679 marker-count==0 gate; ASCII-safe stdout)."""
from datetime import datetime, timedelta, timezone

import os
from datetime import datetime, timedelta, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RR = os.path.join(ROOT, "logs", "iteration-loop", "round_reports.md")

CST = timezone(timedelta(hours=8))
ts = datetime.now(CST).isoformat(timespec="seconds")

marker = "| round 688 addendum (bm-b) ".encode("utf-8")
data = open(RR, "rb").read()
pre = data.count(marker)
assert pre == 0, f"addendum marker already present count={pre}"
if data.endswith(b"\r\n"):
    prefix, eol = b"", b"\r\n"
elif data.endswith(b"\n"):
    prefix, eol = b"", b"\n"
else:
    prefix, eol = b"\n", b"\n"
line = (
    f"{ts} | round 688 addendum (bm-b) | S7 收口实录：首推被 pre-push 爪正确拦"
    f"（删除集 results/_r490bmc_s6_log.txt=陈旧基座假象——origin 中窗前进 2 commit"
    f"=bm-c r490 收口波 r370/r392 律正统先集成再推，零 --no-verify）→ fetch 实核 "
    f"165b9a3b3 → merge 净路（r437-iv treadmill 下 merge 合法）14 UU 全 S6 共享再生面"
    f"→ r686 正典 resolver 血统复跑（r456 side_pick 回退腿在位已核·r682 宣称≠实态律）"
    f"：12 ours 19:04:33 新鲜胜 / 1 theirs compute_audit / token_usage per-key union "
    f"picks ours5-theirs0 断言过 → marker 行首判定=0（4 处子串命中=九月历史轮报告行"
    f"合法收口叙述字面量 r657-③ 分判）→ round_reports 联集自证（r687/r688 各恰 1·"
    f"r490 行在 bm-c 侧文件=S5 分文件律）+ state/hb round688 + epoch int 三自证 + "
    f"trio_eta 19:03:53 + pool_dualrun 尾 50 行零 marker → 复推 DELIVERED "
    f"165b9a3b3..bed2dc005 + fetch+rev-list 0/0 送达自证回填。笔误披露：无。"
    f"坑例新增：0（mid-round push-race 首拦=陈旧基座删除集假象·r686 同型正统先集成；"
    f"resolver/行首分判/联集自证全链既有正典复用零新坑）| 本地未达 origin commit 数=0"
    f"（收口全量 push 后 fetch+rev-list 0/0+tip==origin 自证）")
with open(RR, "ab") as f:
    f.write(prefix + line.encode("utf-8") + eol)
post = open(RR, "rb").read().count(marker)
assert post == 1, f"post marker count={post}"
print("ADDENDUM_OK post_marker=1")
