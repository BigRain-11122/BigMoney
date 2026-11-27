# 两本书同窗对账（research）

面 `book_same_window` ｜ 生成 2026-11-27T22:48:44+08:00 ｜ cutoff 2026-11-26

## 为什么要这张面

r2188 的钱包阶梯回答的是「100 万该开哪一本」，它用的两个年化收益来自两本**各自**的整段历史：转债自 2007-07（19.3 年），ETF 自 2020-01（6.9 年）。这两个数字本身没错，但它们不是同一段日历上的数——拿它们相减，差里混进了「转债在那 12 年独有历史上表现怎样」。这张面把那 12 年切掉，只留两本同时存在的 1671 根日线。

## 读数

- **A**：ETF +10.89%、转债 +7.35%，差 +3.54pp
- **B**：ETF +9.86%、转债 +6.29%，差 +3.57pp
- **C**：ETF +10.89%、转债 +6.29%，差 +4.60pp

判词 `SAME_WINDOW_GAP_IS_UNCHANGED_AND_THE_RISK_COLUMNS_AGREE_AND_THE_WALLET_GAP_IS_LARGER_14406_VS_11626_CNY`；按各自整段历史（转债 2007-07-12 起、ETF 2020-01-03 起），ETF 年化 10.89%、转债 7.35%，差 +3.54 个百分点；把两本放到同一段日历（2020-01-03..2026-11-26）、同一把 244 天时钟、同一种次日成交，ETF 9.86%、转债 6.29%，差 +3.57 个百分点（比面世尺 +0.03）；100 万钱包里单开 ETF 年 76885 元、单开转债年 62478 元，差 14406 元（面世尺是 11626 元）。

## 口径（读这张面之前先读这段）

- `series`：book_pair_blend.load_cb() / load_etf() -- the same two parent legs the book family uses
- `cb_execution`：signal at close t, filled at close t+1
- `etf_execution`：decide at close t, own from the open of t+1 (entry_lag=1)
- `ann_days_same_window`：244.0
- `ann_days_full_history`：cb 244 / etf 252 (each face's own clock, as published)
- `same_window_base`：the first shared bar's level is the entry level (no return before you could own it)
- `yearly`：year = previous year-end level -> this year-end level; first year starts at the first shared bar
- `wallet`：single book at a time; the rest of the 1,000,000 rolls at the cash leg; deployment caps come from results/cb_union_lens.json
- `what_this_face_does_not_do`：it does not re-run either book's rules and it does not re-price anything; it slices two published daily series and restates them on one ruler

## 已知缺口

- the two books carry different universes, different cost models and different turnover; this face aligns dates and clocks, not mechanics
- the etf book runs a volatility target (it de-levers), the cb book does not -- the gap in raw CAGR therefore mixes return with risk budget; the sharpe/maxdd columns are there to read it both ways
- the cb book is quoted on 244 days and the etf face on 252; the full-history rows keep each face's own clock and are therefore not directly subtractable from each other

