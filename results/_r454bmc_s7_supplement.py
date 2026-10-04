# -*- coding: utf-8 -*-
"""r454 bm-c S7-supplement report line append (push-race closeout receipt)."""
import datetime
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLOCK = datetime.datetime.now().astimezone().isoformat(timespec="seconds")

LINE = (
    CLOCK + "｜r454 bm-c S7-supplement｜closeout push-race 收口（r450/r453 同型）："
    "round commit 4b2118b9f 首推被拒（bm-a r664 wave 在途 5 commits·non-FF·非爪拦）→"
    "r437 净路序=先 absorb 本机 daemon 面（bf5619f46·satengine tick 08:29）→"
    "merge origin/main 撞 3 UU（全=同日确定性再生面）→"
    "survey receipt results/_r454bmc_merge_resolve.py 逐面 stage2/3 ts 诚实比较："
    "REPORT json ours 08:20:38>theirs 08:17:23·prospect summary ours 08:20:26>08:17:06·"
    "t35 verify ours 08:20:25>08:17:05→3/3 take-ours（零信息损失·零 marker+JSON reparse "
    "双证 PASS）→merge d123c8bfb→push 过爪（删除集空）→push_verify DELIVERED"
    "（tip==remote d123c8bfb·ahead=0·behind=0）｜本地未达 origin commit 数=0"
    "（push_verify 三证·r436 单源律）｜S7 双扫复核：orders 154/154 零未回执·"
    "T-2026-10-04-165-P1=done(bm-a) 零本机动作·inbox 0｜fleet/machines/bm-c.json 与 "
    "state-bm-c.json 皆 ours（每机只写自己文件律零违）")

rp = os.path.join(ROOT, "round_reports-bm-c.md")
with open(rp, "rb") as f:
    raw = f.read()
eol = b"\r\n" if b"\r\n" in raw[-400:] else b"\n"
addition = LINE.encode("utf-8") + eol
if not raw.endswith(b"\n"):
    addition = eol + addition
with open(rp, "ab") as f:
    f.write(addition)
with open(rp, "rb") as f:
    back = f.read()
assert LINE.encode("utf-8") in back
print("SUPPLEMENT_OK clock=" + CLOCK + " bytes=" + str(len(addition)))
