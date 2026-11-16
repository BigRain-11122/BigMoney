# 隔夜差：同一根 bar 上，这页动了哪些数（r1761）

- 比较：`LIVE-BOOK-20261115.json` → `LIVE-BOOK-20261116.json`
- 价格依据：2026-11-16（前一天 2026-11-13）｜数据截止：2026-11-16（前一天 2026-11-13）
- 判决：**DATA_ADVANCED**

## 一句话
两天**不是同一根 bar**（2026-11-13 → 2026-11-16），数据推进了，先分不清“数据动”和“口径动”；这一面在数据日推进的隔夜不给任何指控，只记录 **81** 个位移与 **84** 个新增叶子。

## 动的数（全部 81 个）

| 数字 | 昨天 | 今天 | 判读 | 依据 |
|---|---|---|---|---|
| `/admission/capacity_cny` | 39783633.0 | 27645948.0 | DATA_ADVANCED |  |
| `/admission/margin_to_line` | -0.0039 | -0.0084 | DATA_ADVANCED |  |
| `/admission/top2_share` | 0.7039 | 0.7084 | DATA_ADVANCED |  |
| `/admission/worst` | 2.6828 | 2.1656 | DATA_ADVANCED |  |
| `/authority/owner_silent_h` | 41.4 | 65.7 | CLOCK |  |
| `/backtest_band/12 名·8% 波动目标（生产卡片口径）/full/cagr_pct` | 9.59 | 9.51 | DATA_ADVANCED |  |
| `/backtest_band/12 名·8% 波动目标（生产卡片口径）/full/sharpe` | 0.99 | 0.98 | DATA_ADVANCED |  |
| `/backtest_band/12 名·8% 波动目标（生产卡片口径）/oos/cagr_pct` | 18.2 | 17.97 | DATA_ADVANCED |  |
| `/backtest_band/12 名·8% 波动目标（生产卡片口径）/oos/sharpe` | 1.72 | 1.7 | DATA_ADVANCED |  |
| `/backtest_band/5 名·beta 覆盖/full/cagr_pct` | 15.67 | 15.55 | DATA_ADVANCED |  |
| `/backtest_band/5 名·beta 覆盖/full/sharpe` | 1.01 | 1.0 | DATA_ADVANCED |  |
| `/backtest_band/5 名·beta 覆盖/oos/cagr_pct` | 23.76 | 23.42 | DATA_ADVANCED |  |
| `/backtest_band/5 名·beta 覆盖/oos/sharpe` | 1.49 | 1.48 | DATA_ADVANCED |  |
| `/book_amount_cny` | 431769.6 | 431727.8 | DATA_ADVANCED |  |
| `/cash_amount_cny` | 568230.4 | 568272.2 | DATA_ADVANCED |  |
| `/cash_handshake/cash_amount_cny` | 568230.4 | 568272.2 | DATA_ADVANCED |  |
| `/cash_handshake/worst_case_annual_cny` | 6904.0 | 6905.0 | DATA_ADVANCED |  |
| `/cash_ladder/cash_amount_cny` | 568230.4 | 568272.2 | DATA_ADVANCED |  |
| `/cash_ladder/tenors/0/annual_cny_spot` | 7188.0 | 7189.0 | DATA_ADVANCED |  |
| `/cash_ladder/tenors/1/annual_cny_realized_1y` | 6385.0 | 6386.0 | DATA_ADVANCED |  |
| `/cash_ladder/tenors/1/annual_cny_spot` | 6904.0 | 6905.0 | DATA_ADVANCED |  |
| `/cash_ladder/tenors/2/annual_cny_realized_1y` | 8011.0 | 8012.0 | DATA_ADVANCED |  |
| `/cash_ladder/tenors/2/annual_cny_spot` | 7813.0 | 7814.0 | DATA_ADVANCED |  |
| `/cash_ladder/tenors/3/annual_cny_spot` | 7813.0 | 7814.0 | DATA_ADVANCED |  |
| `/cash_ladder/tenors/4/annual_cny_spot` | 7813.0 | 7814.0 | DATA_ADVANCED |  |
| `/cash_ladder/tenors/5/annual_cny_realized_1y` | 8133.0 | 8134.0 | DATA_ADVANCED |  |
| `/cash_money/block/book_rate/annual_cny` | 10075.0 | 10076.0 | DATA_ADVANCED |  |
| `/cash_money/block/cash_amount_cny` | 568230.4 | 568272.2 | DATA_ADVANCED |  |
| `/cash_money/block/mean_tail/annual_cny` | 7681.0 | 7682.0 | DATA_ADVANCED |  |
| `/cash_money/block/spot/annual_cny` | 7188.0 | 7189.0 | DATA_ADVANCED |  |
| `/cash_money/block/spread_vs_window_cny` | -4640.0 | -4643.0 | DATA_ADVANCED |  |
| `/cash_money/block/window/annual_cny` | 11828.0 | 11831.0 | DATA_ADVANCED |  |
| `/cash_money/block/window/pct` | 2.0816 | 2.082 | DATA_ADVANCED |  |
| `/cash_money/forward/cash_amount_cny` | 568230.4 | 568272.2 | DATA_ADVANCED |  |
| `/cash_money/forward/gap_bp` | 50.81 | 77.79 | DATA_ADVANCED |  |
| `/cash_money/forward/gap_cny` | 182.0 | 279.0 | DATA_ADVANCED |  |
| `/cash_yield/annual_cny` | 7188.0 | 7189.0 | DATA_ADVANCED |  |
| `/causal_rebuild/elapsed_sec` | 116.0 | 95.9 | CLOCK |  |
| `/excess_pp` | 9.8 | 9.81 | DATA_ADVANCED |  |
| `/fleet/rows/0/age_h` | 40.52 | 64.34 | CLOCK |  |
| `/fleet/rows/1/age_h` | 387.0 | 410.82 | CLOCK |  |
| `/fleet/rows/2/age_h` | 0.17 | 0.06 | CLOCK |  |
| `/gap/elapsed_sec` | 102.4 | 85.0 | CLOCK |  |
| `/money_cny/benchmark_annual_cny` | 27900.0 | 27300.0 | DATA_ADVANCED |  |
| `/money_cny/excess_annual_cny` | 98000.0 | 98100.0 | DATA_ADVANCED |  |
| `/money_cny/expected_annual_cny` | 125900.0 | 125400.0 | DATA_ADVANCED |  |
| `/next_decision_bars` | 18 | 17 | DATA_ADVANCED |  |
| `/order/0/amount_cny` | 86389.2 | 86400.6 | DATA_ADVANCED |  |
| `/order/0/lots` | 684 | 689 | DATA_ADVANCED |  |
| `/order/0/price` | 1.263 | 1.254 | DATA_ADVANCED |  |
| `/order/0/shares` | 68400 | 68900 | DATA_ADVANCED |  |
| `/order/1/amount_cny` | 86321.4 | 86351.9 | DATA_ADVANCED |  |
| `/order/1/lots` | 726 | 719 | DATA_ADVANCED |  |
| `/order/1/price` | 1.189 | 1.201 | DATA_ADVANCED |  |
| `/order/1/shares` | 72600 | 71900 | DATA_ADVANCED |  |
| `/order/2/amount_cny` | 86372.4 | 86286.0 | DATA_ADVANCED |  |
| `/order/2/lots` | 431 | 438 | DATA_ADVANCED |  |
| `/order/2/price` | 2.004 | 1.97 | DATA_ADVANCED |  |
| `/order/2/shares` | 43100 | 43800 | DATA_ADVANCED |  |
| `/order/3/amount_cny` | 86333.0 | 86365.0 | DATA_ADVANCED |  |
| `/order/3/lots` | 754 | 751 | DATA_ADVANCED |  |
| `/order/3/price` | 1.145 | 1.15 | DATA_ADVANCED |  |
| `/order/3/shares` | 75400 | 75100 | DATA_ADVANCED |  |
| `/order/4/amount_cny` | 86353.6 | 86324.3 | DATA_ADVANCED |  |
| `/order/4/lots` | 496 | 493 | DATA_ADVANCED |  |
| `/order/4/price` | 1.741 | 1.751 | DATA_ADVANCED |  |
| `/order/4/shares` | 49600 | 49300 | DATA_ADVANCED |  |
| `/positions/accrual/rf_missing_bars` | 0 | 1 | DATA_ADVANCED |  |
| `/positions/accrual/rows` | 0 | 1 | DATA_ADVANCED |  |
| `/positions/accrual/written` | 0 | 1 | DATA_ADVANCED |  |
| `/positions/engine_book/tail/nav_units` | 1.46744585 | 1.4670029 | DATA_ADVANCED |  |
| `/positions/engine_book/tail/rf` | 0.0 | 0.00010397 | DATA_ADVANCED |  |
| `/positions/next_order_base/risk_book_cny` | 431769.6 | 431432.8 | DATA_ADVANCED |  |
| `/same_beta_benchmark/bars` | 693 | 694 | DATA_ADVANCED |  |
| `/same_beta_benchmark/cagr` | 0.0279 | 0.0273 | DATA_ADVANCED |  |
| `/same_beta_benchmark/sharpe` | 0.737 | 0.722 | DATA_ADVANCED |  |
| `/stress/n_days` | 5280 | 5281 | DATA_ADVANCED |  |
| `/ticket_book/bars` | 693 | 694 | DATA_ADVANCED |  |
| `/ticket_book/cagr` | 0.1259 | 0.1254 | DATA_ADVANCED |  |
| `/ticket_book/sharpe` | 1.705 | 1.699 | DATA_ADVANCED |  |
| `/ticket_book/vol` | 0.0739 | 0.0738 | DATA_ADVANCED |  |

## 今天没有了的数（1 个，列前 40）

- `/positions/next_order_base/arrival_actions`

## 今天新出现的数（84 个）落在这几块上

- `/cash_money/block`
- `/cash_money/forward`
- `/entry_gate/gates`
- `/entry_gate/shipped_median_names`
- `/entry_gate/shipped_min_names`
- `/entry_gate/thinnest_day_names`
- `/idle_cash/arm_gap`
- `/idle_cash/arms`
- `/positions/accrual`

## 怎么读

- `CLOCK`＝钟面（`age_h`/`silent_h`/`lag_days` 这类）：没有新 bar 也该走，不构成问题；但它的存在说明「哪些数允许自己走」是**名单制**的，名单写在本脚本顶部，不由数据推出来。
- `DATA_ADVANCED`＝数据推进了，所有定价读数都允许动。
- `RECOVERED_OLD_VALUE`＝昨天那个数今天还在页上，只是换了名字——那是**改名**不是重算；读的人必须知道这一点，否则会把「口径换了」读成「今天变了」。
- `DECLARED_RULER`＝同一块里的口径句（`ruler`/`basis`/`convention`）改了，位移由它自己声明；句子改了而读者没看见，等于数被悄悄换了定义。
- `UNEXPLAINED`＝既没有旧值留存、也没有口径声明——**这一档非零就是本面要报的事**。

## 未验证（如实）

- 只比**相邻两天**：更早的口径变更若在两页之前发生，本面看不见（可手工指定更多日页，未做）。
- 「旧值仍在」靠数值相等判定（相对 1e-9）：两个无关的数恰好相等的概率不低，所以 `RECOVERED_OLD_VALUE` 是**线索**不是证明，行里同时印出它在哪个键上，供人核。
- 钟面名单是写死的：新出现的钟面字段会被算成 `MOVED`，本面会如实报（宁可多报）。
- 本面不判「这个改动是否合理」，也不碰任何生产件；它只读已发布日页。
