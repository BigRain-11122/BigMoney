# 下一根决策 bar 是哪一天

```json
{
 "artifact": "etf_book_next_decision",
 "calendar_last": "2026-12-31",
 "calendar_source": "data/exchange_calendar.csv",
 "caveats": [
  "网格只回答「下一次重排是哪一天」，它对此外的事（触发面、过路费、折扣兑现）一无所知，也不替它们作证。",
  "相位取自已发布的 last_decision_bar（别人已经落账的事实），不是本面自选；官方日历原点的同相位只是交叉核对，两者不一致时以锚点为准并披露。",
  "账本里 k 的变动只作行为样本列出：它动在哪一天，不等于那一天该决策（也可能是规则内的风控改档），本面不据此判对错。",
  "日历里没有的日期一律不印；读不出的面列 unreadable，不按 0 或最近日期顶替。"
 ],
 "claims": [
  {
   "agrees": true,
   "bars_from_sheet": 19,
   "face": "results/etf_book_production/latest.json",
   "key": "sheet.bars_until_next_decision",
   "name": "production_sheet",
   "note": "2026-11-12 起第 19 根（面自己写的 bars_until_next_decision）",
   "on_grid": true,
   "printed": "2026-12-09",
   "sheet": {
    "as_of_bar": "2026-11-12",
    "bars_until_next_decision": 19,
    "is_grid_decision_bar": false,
    "last_decision_bar": "2026-11-11"
   }
  },
  {
   "agrees": true,
   "bars_from_sheet": 19,
   "face": "results/etf_book_rebalance_permission.json",
   "key": "decision_date",
   "name": "cut_permission",
   "note": "权限面自己签的决策日",
   "on_grid": true,
   "printed": "2026-12-09"
  },
  {
   "agrees": true,
   "bars_from_sheet": 19,
   "face": "results/etf_book_swap_units.json",
   "grid": 20,
   "key": "next_decision_bar.bar",
   "name": "swap_section",
   "note": "换票节自己算的（grid=20，来源=anchor）",
   "on_grid": true,
   "printed": "2026-12-09"
  }
 ],
 "evidence_cutoff": "2026-11-12",
 "grid": {
  "anchor_bar": "2026-11-11",
  "anchor_on_calendar": true,
  "anchor_source": "results/etf_book_production/latest.json#sheet.last_decision_bar",
  "as_of": "2026-11-12",
  "bars_away": 19,
  "crosscheck": {
   "agrees": true,
   "next_bar": "2026-12-09",
   "note": "面板起点与日历原点同相位",
   "rule": "official calendar origin mod rebal == 0"
  },
  "grid_source": "import",
  "next_bar": "2026-12-09",
  "phase": 0,
  "rebal": 20,
  "why": ""
 },
 "ledger_trace": {
  "bars": [
   "2026-06-26",
   "2026-07-24",
   "2026-08-21",
   "2026-09-18",
   "2026-10-26",
   "2026-11-02"
  ],
  "first": "2024-01-02",
  "last": "2026-11-12",
  "n_moves": 35,
  "off_grid": [
   "2026-06-26",
   "2026-07-24",
   "2026-08-21",
   "2026-09-18",
   "2026-10-26",
   "2026-11-02"
  ]
 },
 "off_grid_claims": [],
 "sentence": "下一根决策 bar = 2026-12-09（锚点 2026-11-11 起每 20 根，距 2026-11-12 19 根）。票面上三个面都这么说。",
 "verdict": "AGREE",
 "worst_gap_bars": null,
 "wrong_claims": []
}
```


## 下一根决策 bar 是哪一天（r1536）
- 下一根决策 bar：**2026-12-09**（距 2026-11-12 19 个交易日；锚点 `last_decision_bar` = 2026-11-11，每 20 根）。

| 面 | 它印的 | 距本单票面 | 落在网格上 | 一致 |
|---|---|---|---|---|
| production_sheet | 2026-12-09 | +19 根 | 是 | 是 |
| cut_permission | 2026-12-09 | +19 根 | 是 | 是 |
| swap_section | 2026-12-09 | +19 根 | 是 | 是 |
- 交叉核对：official calendar origin mod rebal == 0 → 2026-12-09（一致）。
- 账本自己的 k 最近动在这几根：2026-06-26、2026-07-24、2026-08-21、2026-09-18、2026-10-26、2026-11-02（共 35 次，其中不在网格上 6 次）——这是行为样本，不是判据。
- 判词：**AGREE**
- 下一根决策 bar = 2026-12-09（锚点 2026-11-11 起每 20 根，距 2026-11-12 19 根）。票面上三个面都这么说。

