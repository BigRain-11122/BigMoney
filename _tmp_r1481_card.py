#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""One-shot: append card E491 to knowledge/METHODOLOGY_ASSETS.md (r1481)."""
import io
import os

ROOT = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(ROOT, "knowledge", "METHODOLOGY_ASSETS.md")

CARD = """
### E491 · 政策均值不是单张票的价格（r1481 bm-c）

E490 把「每张票都晚一格」定价了（1.87pp/年），但桌面手上只有**一张**票，问的是
「今天下不了、明天补，这一张值多少」。政策数字是 83 个决定之和，在不知道这个和是不是
由 83 个小价格拼成之前，它不能转让给单张票（E238 族：成员与聚合是两个对象）。

**三律**

1. **单事件价格要单独量，不要拿政策数除以事件数**。晚一格的局部价格恰好是**一根 bar 的
   收益差**：控制路径在决策 bar 把 `old` 换成 `new`，晚一格则那一根仍持 `old`、下一根才换
   `new`，之后完全相同。vt08 臂 415 个事件（5 相位 × 83）：中位 **-932 CNY**（决策时点 NAV
   按 1,000,000 本金）、p10..p90 -10,347..+5,907、均值 -12.2bps、t=-4.61。
2. **均值可判 ≠ 单张可判**。同一批事件里 **41% 晚一点反而更好**。所以正确的话是：「纪律在
   预算上成立（每张预留约 932 CNY），在单张上不成立（不知道这一次是赚还是亏）」。只印均值
   的单张价格是误导；印「每张亏 932」而不印 41% 也是。
3. **局部与聚合的关系必须测，不能假设**。同一相位网格实跑聚合臂（`replay(lag=1)`），把
   `sum(delta_log)` 与 `log(晚/准)` 相比：残差 **5e-15**（vt08）／**3e-15**（base）——严格
   可加（两张票之间路径相同，晚一格只替换一根 bar）。残差入面、入 check 腿，超 15% 时判决
   降级为 `LOCALS_DO_NOT_ADD_UP` 且拒绝提供单张报价。

**判据**：任何「这一步/这张票值多少」的问题，答案必须是单事件价格，并同时印离散度与反向
占比；局部与聚合的可加性要实测入面。

**落地**：决策行第二态。票面本次不欠裁剪时，原句只剩「无需裁剪」，读者会读成「什么都不欠」；
实际欠的是准时——`results/etf_book_decision_line.json` 的 `late_sheet` 块现在把「晚一格
932 CNY、41% 反向、t=-4.61」印在同一条句子里，缺面一律 UNKNOWN（绝不 0.00）。

**正身**：scripts/etf_book_late_sheet_price.py（selftest 10/10：tape 复现引擎、事件落在 20
根网格上、不换书就没有价格、平盘价格恒为 0、真换书有价格、符号约定一致、一根 bar 的替换
严格可加、常量样本没有 t、空样本不是 0）+ results/etf_book_late_sheet_price.json
（evidence_cutoff 2026-11-06，两臂各 83×5 事件，控制臂差 0.0）+ S6 腿 late_sheet_price
（check 10/10）+ research/ETF_BOOK_LATE_SHEET_PRICE.md + 卡片本行。
"""

with io.open(PATH, "a", encoding="utf-8", newline="") as fh:
    fh.write(CARD)
print("appended", len(CARD), "chars")

# read back the tail to prove it landed
with io.open(PATH, "r", encoding="utf-8") as fh:
    lines = fh.read().splitlines()
print("last line:", lines[-1][:60])
print("cards:", sum(1 for l in lines if l.startswith("### E")))