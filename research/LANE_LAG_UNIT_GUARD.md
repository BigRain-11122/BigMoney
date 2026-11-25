# 车道落后：板上的数字和日历上的事实差在哪一个单位

`scripts/lane_lag_unit_guard.py` · 只描述不修板（板是共享面，竞争窗内禁改）。

读数由 `run` 渲染进下面的 marker 块，`--check` 逐字比对面；手改一位即 rc3。
<!-- BEGIN lane_lag_unit_guard -->
generated 2026-11-25T04:04:32 | verdict **TOLERANCE_IS_IN_THE_WRONG_UNIT**

| 块 | 车道 | 尾部 bar | 应到 bar | 板印的日历日 | 日历说的交易日 | 板判 | 诚实态 | 分类 |
|---|---|---|---|---|---|---|---|---|
| D1_fut_daily | futures | 2026-11-24 | 2026-11-24 | 1 | 0 | GREEN | CURRENT | **AGREE_CURRENT** |
| D2_index_daily | — | 2026-11-23 | 2026-11-24 | 2 | 1 | GREEN | PENDING_TODAY | **AGREE_PENDING** |
| D3_etf_daily | etf_panel | 2026-11-23 | 2026-11-24 | 2 | 1 | GREEN | PENDING_TODAY | **AGREE_PENDING** |
| D4_astock_daily | astock_daily | 2026-11-24 | 2026-11-24 | 1 | 0 | GREEN | CURRENT | **AGREE_CURRENT** |
| D6_cash_rate | repo | 2026-11-20 | 2026-11-24 | 5 | 2 | RED | LATE | **AGREE_LATE** |

同一条款按不同星期几跑，结果如下（k = 真实缺的交易日数）：

| 缺 k 日 | 板算出的日历差 | 两个方向都出现过? |
|---|---|---|
| 1 | 1–3 | 否 |
| 2 | 2–4 | 否 |
| 3 | 3–5 | **是（同一个缺口红绿两色）** |
| 4 | 4–6 | **是（同一个缺口红绿两色）** |
| 5 | 7–7 | 否 |

**读数**：5 条里 2 条当前、2 条源还没发布（合法第三态）、1 条真落后；**5 条的日历差都不是交易日差**。
- D2_index_daily 的生产者已经说过：vendor has not published past 2026-11-23

- 真落后那条 = **D6_cash_rate**：板印「modal bar 2026-11-20 is 5d behind last weekday 2026-11-25」，日历事实「2 trading day(s) missing: 2026-11-23, 2026-11-24」。

- 同一个缺口在不同星期几红绿不同：缺 3 / 4 个交易日时，板算出的日历差分别是 3–5 / 4–6 —— 一个死了三天的车道，周一周二显示绿的。
<!-- END lane_lag_unit_guard -->

## 它不声称什么

- this face does not fix the board: block_board.py is a shared face and another host is writing (r1907). The patch stays proven-not-applied until a clean window
- the expected bar is the last OFFICIAL day whose bar must exist by the 15:30 accept time; the board's reference is 'last Mon-Fri', which is 11-25 today even though no 11-25 bar can exist before 15:30
- a trading-day gap of 0 means the lane is current; it says nothing about the lane being correct, only about it having written its bar
- holidays are taken from data/exchange_calendar.csv (the same file the rest of the chain imports); a wrong calendar moves every row together

## 补丁（已证未落）

- 文件：`scripts/block_board.py`
- 形状：expected/allow must both be in trading days: replace expected_last_weekday() with exchange_calendar_audit.expected_last_day(calendar, now) and compare len(trading_gap(...)) against holiday_allow_days; keep the printed string in trading days
- 状态：`PROVEN_NOT_APPLIED`
