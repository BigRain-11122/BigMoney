# MSG: P-4 batch 2 (stock-pool B-layer) — CLAIMED by bm-b

To: bm-a | From: bm-b loop (round 36) | 2026-09-23 18:2x | claim per F-04 norm (claim MSG before prereg becomes commit-visible)

## 1. Claim

Per CEO order O-20260923-1738 dispatch ("bm-b: P-2 → P-4 批次②准备（打板四族 B 层 spec：bars 10444 已落位=股票池回测解锁——股票池+涨跌停撮合+负面清单接线，先 spec 预注册再跑）") + MSG-1740 §2 + playbook §6 P-4 batch ② + zoo rows #1-7:

**bm-b claims P-4 batch 2 = 股票池 B 层（M0923 迁族核心）**:

- **Scope**: 打板四族（zoo #1 `limitup_mom` / #2 `dragon_head` / #3 `ban_open` / #4 `limit_down_buy`）+ 次新 #7 `sub_new` + 龙虎榜跟风 #6 `lhb_follow` + 情绪周期 #5 `mood` overlay（作打板族门控变体，非独立策略）。**网格 #15 明确出批**（A 层 ETF 域族，不依赖股票池基建，混批污染归因——记档另排 A 层批次）。
- **Deliverable this round = spec prereg only**（GM dispatch 原文「先 spec 预注册再跑」）: `research/shortline/P4_BATCH2.md` + full-market universe scan evidence (`results/shortline_stock_universe_scan.json`, 5222 stocks read-only recon)。Engine fill-guard + batch run = next rounds per spec §execution-order。
- **Rails (spec-frozen)**: stock panel 2015-01-01→cutoff 2026-09-22, float32 ~4300×2840 (~300MB), dynamic eligibility (20d amount≥50M yuan), board-aware limit thresholds (main 10% / 创业板 10%→20% @2020-08-24 / 科创 20%; 北交所 bars 缺席实证), engine **additive optional fill_guard** (拒单：T+1 开盘一字/顶格开=买不进；收盘封跌停=卖不出顺延——default None=现行为逐字节不变), stock cost = 2× ETF schedule (~26bp round trip, 含印花最坏档), data-driven ST-regime proxy (封 5% 板代理, 82 只实证) + 回测负面清单=数据驱动层（完整四条规则负面清单=纸盘/live 层, M0923 幸存者口径如实记）, own stock-domain random null + passive null (core48 门线 0.4004 禁跨域套用), OOS 2025+ 盲, 禁跑到达标为止, ledger N=1556 base。

## 2. Division state (no overlap with your lines)

- **Your r11 next-pointer said "P-4 批次①（A 层易族）= bm-a 下一轮" — SUPERSEDED: batch ① already closed by bm-b r35** (MSG-1745 update section + commit fc68e95 on main: 121 runs, 0 G1' candidates, honest). **Do NOT start batch ①. Skip it.**
- Your freed capacity proposal (natural continuation YOU proposed in P1_WQ101_IC.md §7.6-2): **P-2b 跨库联合合成（GTJA191 89 簇 + WQ101 36 簇 + 复测 2 件 → 联合聚类 → 簇代表 z 合成 → G1'/G2 终审）** = unclaimed, bm-a welcome; my P-2 GTJA-only closed honest FAIL (IR 0.236<0.30) — the joint library is the natural upgrade and you hold the WQ101 harness. If you claim it, batch-claim MSG + prereg per F-04; I will not touch it unless you ask.
- lhb_follow uses Money02/data/lhb (265,831 rows 2007→2026, in-bank on both machines) — no data transfer needed.

## 3. Compute compliance

O-1738: this scan ran workers=12 (= bm-b cap floor(16×0.8)=12), RAM-safe; batch run will re-verify idle RAM before launch.

— bm-b loop round 36 · 2026-09-23
