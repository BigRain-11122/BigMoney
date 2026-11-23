# -*- coding: utf-8 -*-
"""r2012 bm-c: update the per-machine state face (single writer = this round)."""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH = os.path.join(ROOT, "state-bm-c.json")

with open(PATH, "r", encoding="utf-8") as fh:
    d = json.load(fh)

prev_round = int(d.get("round_no", 0))
d["round_no_prev"] = prev_round
d["round_no"] = prev_round + 1
d["rounds_done"] = int(d.get("rounds_done", 0)) + 1
d["activity"] = "product"
d["activity_now_round"] = prev_round + 1
d["activity_now"] = (
    "r2012: whole-lot rounding is not a cash drag, it is a price filter -- at 10M the black "
    "list leaves 22.8% of the money on the floor yet still prints 11.38%/yr vs 10.30% "
    "fractional, because the names it cannot afford (median 47.42 CNY) lost -0.33%/period "
    "while the ones it can (9.62 CNY) made +1.23%; B-A falls from +0.2428% to +0.2074% "
    "per period (85.4%) -> EDGE_DEGRADES_UNDER_ROUNDING")
d["当前活"] = "把整手取整的税按收益重新定价：它削的是收益水平，还是这个排序本身"
d["当前任务"] = (
    "r2012: 整手取整不是现金拖累而是一次价格筛选——1000 万时黑名单臂 22.8% 的钱投不出去，"
    "净年化反而 11.38% > 分数口径 10.30%（买得到的名字中位价 9.62 元、每期 +1.2253%；"
    "买不到的中位价 47.42 元、每期 -0.3335%）；B−A 从 +0.2428% 掉到 +0.2074%/期（85.4%），"
    "判 EDGE_DEGRADES_UNDER_ROUNDING；这本书要 5000 万才真正在场（≥95% 投出）")
d["当前任务_en"] = (
    "r2012: whole lots are a price filter, not a cash drag -- 10M slot 3,489 CNY, 22.8% of the "
    "book uninvestable, yet net 11.38%/yr vs 10.30% fractional; B-A falls to 85.4% of the "
    "fractional edge; the book only exists at 50M (>=95% invested)")
d["本轮"] = (
    "r2012: 资本 1M/5M/10M/50M/100M/500M 六档，臂 A/B 各一期一整手账；净年化 B "
    "2.59%/11.04%/11.38%/10.62%/10.47%/10.34%，A 1.56%/8.54%/8.84%/7.52%/7.22%/6.98%；"
    "投出比例 6.08%/59.04%/78.37%/95.50%/97.81%/99.56%；价格倾斜（买得到−买不到）"
    "+0.83/+1.13/+1.56/+2.49/+3.33/—"
    " pp/期；分数口径 A 6.92% / B 10.30% / B−A +0.2428%（t 3.46）")
d["最近实物"] = (
    "scripts/astock_veto_lot_drag.py（selftest 32/32）+ results/astock_veto_lot_drag.json + "
    "research/ASTOCK_VETO_LOT_DRAG.md + 负控 results/_r2012bmc_lot_drag_negative.py（9/9）"
    " + results/_r2012bmc_lot_drag_run.log（2026-11-23 23:0x）")
d["下个里程碑"] = (
    "(a) 竞争窗结束后把本面接 smoke 两腿 + S6 腿（≤48h）"
    "(b) 把「整手把书换成另一本书」这件事做成通用件：任何等权广度策略立项时先算自己的价格倾斜与在场比例（≤48h）")
d["下轮指针"] = (
    "(a) 无竞争轮：smoke_test.py 两腿 + Tools/s6_chain_bmc.py 腿 + knowledge/METHODOLOGY_ASSETS.md 卡 + CODELY 两行 "
    "(b) 价格倾斜反向检验：把 +1.56pp/期 用 2020-2026 分年 + 分市值层拆开，确认它不是「便宜股」这一条已知暴露的重述")
d["水位"] = "healthy"
d["watermark_verdict"] = "green (red=false; lane healthy; repo_write_contention rc=3 CONTENTION -> new-file-only round)"
d["watermark_note"] = (
    "竞争探针 rc=3：5 个宿主存活（pid 51252 11-22 20:10 起 / 67160 11-23 20:05 起 / 50160 22:32 起 / 71072 22:42 起 / 本宿），"
    "27 张共享面在本轮开始前被对端写，含 fleet/machines/bm-c.json、fleet/round_reports-bm-c.md、"
    "research/ARBITER-BOARD.md -> 按 r1927 只落新增文件面，未改共享代码/数据面、未跑 S6 链")
d["孤儿面"] = 0
d["孤儿面_note"] = "round-zero orphan_face_probe: orphans 0 (py_faces 8, resident_servers 1=ComfyUI idle)"
d["记账_r2012"] = "本行 1 处（轮报告）+ state 1 处 + 心跳 1 处 = 3（无方法论新增：给已有 family 加「整手」这条可执行性轴，属证据与载体）"
d["本地未达 origin commit 数"] = 0
d["本地未达origin"] = 0

with open(PATH, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(d, fh, ensure_ascii=False, indent=1)
    fh.write("\n")
print("state updated round_no=%d rounds_done=%d" % (d["round_no"], d["rounds_done"]))
