# 选股腿的地板：每一条轴都推到头了（2026-11-19）

**把 座数、成对去相关选股、对冲排名自身倾斜 各推到头，选股腿的地板从 8.74pp 最窄只到 **6.87pp**（30 座）（座数 6.87pp；成对去相关选股 6.98pp；对冲排名自身倾斜 7.95pp）——**没有一条路把 5.0pp 以下拿到手**。最快那条要付 2.76pp 年化。按这格自己的尺子，把 8.74pp 压到 5.0pp 要 5,077 根 bar（现 1,662 根）——这条路要再攒 3,415 根。**

| 轴 | 基线 | 最窄 | 挪动 | 代价 | 判词 | 出处（cutoff） |
|---|---|---|---|---|---|---|
| 座数（2~30 座全扫） | 8.74pp | 6.87pp | +1.87pp | 年化让掉 +2.76pp | SEAT_TARGET_NOT_REACHED | results/etf_book_seat_mde.json（2026-11-13） |
| 成对去相关选股 | 8.74pp | 6.98pp | +1.76pp | 年化让掉 +4.25pp | CORR_MOVES_FLOOR | results/etf_book_corr_select.json（2026-11-13） |
| 对冲排名自身倾斜 | 8.72pp | 7.95pp | +0.78pp | 让掉的 alpha +1.79pp | TILT_NOT_THE_AXIS | results/etf_book_tilt_neutral.json（2026-11-16） |
| 历史宽度（名册 vs 深度） | — | — | — | — | NAMES_AND_DEPTH_OPPOSE | results/etf_book_era_roster.json（2026-11-19） |

## 这张面的边界

- 每个数来自测它的那张面，本面只搬不重算；cutoff 印在旁边。
- 名册那一条没有单一地板读数：「名字涨、深度跌」是它自己的判词，硬塞一个 pp 数就是本面替它发明量尺。
- bar 数来自尺子面 5 座那行自带的 `bars_needed_for_target`，不是本面用 SE 反推的。
