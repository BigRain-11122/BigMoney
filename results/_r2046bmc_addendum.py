# -*- coding: utf-8 -*-
"""r2046 addendum: delivery self-proof row + heartbeat state after push."""
import io
import sys

sys.stdout.reconfigure(encoding="utf-8")

ROW = (
    "| 2026-11-24T12:58+0800 | r2046 addendum | 送达自证：commit **508329098c** 已推 origin/main"
    "（3aa010257e..508329098c），fetch 后 **AHEAD=0 / BEHIND=0**，git ls-tree -r origin/main 六件新面全在位"
    "（scripts/cash_shelf_year_by_year.py / results/cash_shelf_year_by_year.json / research/CASH_SHELF_YEAR_BY_YEAR.md / "
    "负控 results/_r2046bmc_year_negative.py / 收口 _r2046bmc_closeout.py、_r2046bmc_hb_fields.json）"
    "→ **本地未达 origin commit 数=0**。两枚自捕：①**窗口级「每天超额」误用整窗 bar 数**——把 2,134 元/年除以 1,488 根"
    "得到 1.43 元/bar，于是 511360 印成 116.2 天；正法=按 r2045 的尺子用 `index_bars / 窗口年数`（242.0），得 18.9 天；"
    "这个错在自检里有腿（L12 派生的每年 bar 数）却没被窗口级复算腿接住，属「页面对了、旁边的数错了」同类。"
    "②**负控把「预算放宽」用例写成调 cmd_run**——它顺手重写了已发布的页面，N8 逐字节断言当场抓住，"
    "正法=直接 build()+json.dump 到临时路径，不碰发布件。"
    "| 记账：本行 1 处（轮报告 addendum）+ state 1 处 + 心跳 1 处 = 与正文合计 5 处，在每轮 ≤5 处预算内。 |\n"
)

PATH = "fleet/round_reports-bm-c.md"
text = io.open(PATH, encoding="utf-8").read()
if "r2046 addendum" in text:
    print("ALREADY PRESENT")
else:
    io.open(PATH, "a", encoding="utf-8", newline="\n").write(ROW)
    print("appended %d chars" % len(ROW))
