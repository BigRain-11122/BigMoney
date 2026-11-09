# DIGEST 2026-11-10 r1483 (bm-c) — 一根没有收盘价的 bar，没有恒等可以验

## 现状
`state/queue/tech.md` T29：2026-11-09 盘后，执行账写下了一根 `2026-11-09` 的执行行，
而 ETF 价格面板当时只到 `2026-11-06`。回放（replay）只能用旧收盘价把同一批手数标到 11-06，
「引擎恒等腿」于是印出 **-194.20 CNY / 20 bar** 的差，读起来像引擎算错，smoke 腿
`etf_book_positions check` 转红。

## 做法
`scripts/etf_book_positions.py` 新增记账边界：
- `priced_boundary()`＝「全腿都有收盘价的最后一根 bar」。面板的日是**任一腿**有打印的并集，
  所以停牌/缺数的一腿会被上一根收盘顶着走——那不是估值，是把停牌价当成了当日价。
- 执行行照旧写在执行 bar（手数 + 成交价，合法）；**估值行不许越过边界**。
- 执行 bar 自己没价时不出恒等判词：`identity_status=UNPRICED_BAR`、`identity_holds=null`，
  并点名缺哪几腿、最后能标到哪天。
- 收盘价到齐后补记，若数变了走既有改述通道（`restatements`，前后两组数 + 时间戳）。
- 人面新节「这一根 bar 能不能记估值（价格面板）」印出被截的 bar、缺的腿与原因；
  `check()` 用 `settlement_*` 一族从产物重算，禁手写。

## 读数（两条腿，同一批真产物）
| 情形 | 面板最后全腿收盘 | 执行 bar | 面说什么 |
|---|---|---|---|
| 历史事故复现（面板截到 11-06） | 2026-11-06 | 2026-11-09 | `priced=false`、记账停在 11-06、`UNPRICED_BAR`、缺 159263/159513/159577/513690、差 ¥545.80 明确标为「成交价与旧收盘的距离，不是引擎算错」 |
| 今天（面板已到 11-09） | 2026-11-09 | 2026-11-09 | `priced=true`、估值记到 11-09、恒等腿差 **0.00**（通过） |

附带产品增量：发布面 asof 从 **2026-11-06 推进到 2026-11-09**，账本两根 bar 与票面 k 对齐
（k=0.392587），`check` 全绿。

## 验证
- `python scripts/etf_book_positions.py selftest` → **63/63**（新增 8 腿：边界取全腿交集、
  只打印一腿的面板不出边界、缺价 bar 不出判词、priced bar 才给判词、缺面板的书
  `NO_PRICED_BAR`、人面印出不能记的 bar）。
- `python scripts/etf_book_positions.py run` → `PRINTED_ROWS_REBUILD_THE_BOOK`，
  `check` → **CHECK_OK**（settlement/accrual/replay 三面与新鲜重算一致）。
- `python Tools/s6_chain_bmc.py --only positions_unpriced_bar` → rc0（1.1s）。

## 坑
- 第一版把「边界」当成一条线直接卡死 accrual，但如果执行 bar 自己没价、下一根却有价，
  第一行的当日收益就会变成「成交价→收盘价」的缺口冒充日收益。正法＝执行 bar 没价时整段
  不出估值（`NO_PRICED_BAR`），而不是从更晚的有价 bar 起算。
- 自检夹具先写错了期望：`A{06,09,10} B{06,10}` 的「最后全腿收盘日」是 **11-10** 不是 11-06
  （中间那根 11-09 才是缺口）。夹具与断言同时错的时候两条腿一起绿——这次靠先算边界再写
  断言才没踩。