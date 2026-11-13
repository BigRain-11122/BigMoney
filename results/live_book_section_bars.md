# CEO 页面：这一页是哪一天的（r1533）

*由 `scripts/live_book_section_bars.py` 生成；判据见文件头。*

页面头部写着按 2026-11-12 定价，但 48 个带日期的节里只有 42 节真在这一天；另外 8 节根本没有日期——它们不是同一根 bar 上的数，读的时候不能互相加减。反过来有 6 节比页头更新（admission、cash_handshake、cash_ladder、cash_yield、live_quote、sample_window 已到 2026-11-13）：它们读的车道已经走完当天，而这本书自己的面板还停在前一根 bar 上——这两组数同样不能相减，也不能拿新的那组去替这本书定价。

页面逐节 bar：头部声明 **2026-11-12**，48 个带日期的节里 **42** 节在这一天，其余 0 节在别的 bar 上（其中 6 节比页头新）。

| 节 | 它已经走到哪根 bar | 比页头新（交易日） |
|---|---|---|
| admission | 2026-11-13 | 1 |
| cash_handshake | 2026-11-13 | 1 |
| cash_ladder | 2026-11-13 | 1 |
| cash_yield | 2026-11-13 | 1 |
| live_quote | 2026-11-13 | 1 |
| sample_window | 2026-11-13 | 1 |

这几节比页头**新**：它们读的车道已经跑完当天，而这本书自己的日线面板还停在页头那根 bar 上。所以它们不是「落后」，是**另一个方向的不一致**——同样不能与页头上的数相加减，也不能拿它们去替这本书定价（书的 bar 由书自己的面板决定，升级要等那条车道到货）。

这 8 节没有任何日期字段，本面**不替它们认领**任何一根 bar：backtest_band, agreement, sources, priced_faces, research_arc, permission, sibling_gap, authority。
