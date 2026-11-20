# 那条 1% 的线是拒绝，不是价格：装不进去的钱去哪了

证据截止 2026-11-19 · 门 1M · 每名 200,000 元 · 槽位 5 · 调仓 20 日

## 判词：CAPACITY_BINDS_AND_COSTS

同一本书、同样五个名字：按「1% ADV 装得下多少就买多少，剩下留现金」重读，在 84 次调仓里有 14 次装不满（占 16.7%），平均只能投出 97.0% 的钱，最差一次只剩 27.9%。

| 臂 | 年化 | 夏普 | 回撤 | 换手 |
|---|---:|---:|---:|---:|
| A 全额成交（所有在印面） | 11.38% | 1.122 | -10.56% | 1.082 |
| B 按线缩仓 + 现金 0% | 10.36% | 0.453 | -72.37% | 1.082 |

守规矩的代价：**-1.02 pp/年**（B 减 A）。现金那一半按 0% 计，所以这是下界——r1269 已量过本书记载的回购腿值 +0.10~0.15pp/年。

## 装不下的那几天

| 调仓日 | 容量（元） | 能投出的比例 f |
|---|---:|---:|
| 2025-04-17 | 278,452 | 27.8% |
| 2024-10-21 | 434,863 | 43.5% |
| 2024-02-21 | 574,296 | 57.4% |
| 2021-10-29 | 810,291 | 81.0% |
| 2023-12-18 | 844,996 | 84.5% |
| 2021-03-03 | 874,692 | 87.5% |
| 2025-07-16 | 914,279 | 91.4% |
| 2021-01-27 | 923,255 | 92.3% |

## 诚实边界

- the overlay is arithmetic on the published series, not a re-run of the engine: scaling the slate by f also scales the vol-target overlay that fitted it, so B's vol is f times A's and its sharpe is not simply A's sharpe
- the idle cash earns 0 in arm B; r1269 already measured the repo ladder's worth at +0.10~0.15pp/yr on this book, so B is the LOWER bound and arm C is left absent rather than silently equated to B
- entry_lag=0 is the published behaviour, kept so arm A reproduces every printed face
- capacity is read from the same 40-bar ruler as every other capacity face, so this face inherits their survivors-sweep bias
- nothing here is adopted: this prices the ruler, it does not change the book
