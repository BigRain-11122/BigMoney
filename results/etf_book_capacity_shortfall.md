# 那条 1% 的线是拒绝，不是价格：装不进去的钱去哪了

证据截止 2026-11-19 · 门 1M · 每名 200,000 元 · 槽位 5 · 调仓 20 日

## 判词：CAPACITY_BINDS_AT_NEGLIGIBLE_COST

同一本书、同样五个名字：按「1% ADV 装得下多少就买多少，剩下留现金」重读，在 84 次调仓里有 14 次装不满（占 16.7%），平均只能投出 97.0% 的钱，最差一次只剩 27.9%。

| 臂 | 年化 | 夏普 | 回撤 | 换手 |
|---|---:|---:|---:|---:|
| A 全额成交（所有在印面） | 11.38% | 1.122 | -10.56% | 1.082 |
| B 按线缩仓 + 现金 0% | 11.34% | 1.137 | -10.56% | 1.082 |

守规矩的代价：**-0.04 pp/年**（B 减 A）。现金那一半按 0% 计，所以这是下界——r1269 已量过本书记载的回购腿值 +0.10~0.15pp/年。

### 更正（本版修复）

r1877 在同一个面上发布过 -1.02 pp/年，并把 B 的回撤印成 -72.37%。那不是书的回撤，是叠加层的算术错误：引擎给的是一条**净值曲线**，旧代码直接把它乘以 f，于是「72% 的钱在现金里」被读成「亏了 72%」。本版先把净值还原成日收益再缩放重建，回撤回到 -10.56%（与 A 同基准），1M 镜片下的代价也随之从 -1.02pp 收到 -0.04 pp。

f 列与「装不满的次数」不受影响：那些是容量读数，不是收益读数。

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

## 换个规模再读一遍：代价随规模怎么变

同一本书、同一批名字、同一条 1% ADV 的线，只把资金换成不同镜片。判词：**MONOTONE_STEEPER**，从 100万 的 -0.04 pp/年 到 3000万 的 -10.53 pp/年，跨度 -10.49 pp。

| 资金 | 每名 | 装不满的调仓 | 平均能投出 | 最差一次 | 年化（按线缩仓） | 代价 vs 全额 |
|---:|---:|---:|---:|---:|---:|---:|
| 全额成交（对照） | — | — | — | — | 11.38% | — |
| 100万 | 200,000 | 16.7% | 97.0% | 27.9% | 11.34% | -0.04 pp |
| 300万 | 600,000 | 85.7% | 52.7% | 9.3% | 7.21% | -4.17 pp |
| 1000万 | 2,000,000 | 100.0% | 18.6% | 2.8% | 2.57% | -8.81 pp |
| 3000万 | 6,000,000 | 100.0% | 6.2% | 0.9% | 0.85% | -10.53 pp |

第一行是所有在印面的全额成交臂（不动，只作对照）。阶梯各档都是「按线缩仓 + 现金 0%」，所以每一行都与全额臂比。

读法提醒：夏普在 3M 反而比 1M 高（1.282 对 1.137）——那是「一半钱躺在 0% 现金里」把波动压掉的结果，不是「更大的书更好」；收益列才是规模的价钱。

## 诚实边界

- the overlay compounds the book's own daily returns at f; the engine curve is a LEVEL series, and scaling a level by f would print a fake drawdown (r1877's -72.37% was exactly that: '72% in cash' read as a 72% loss)
- r1877's arms.B (10.36% / -72.37%) was computed on that level-scaling error and is superseded by this run's compounded arm B; the f column and the binding counts are unchanged, only the return path is
- scaling the slate by f also scales the vol-target overlay that fitted it, so B's vol is f times A's and its sharpe is not simply A's sharpe
- the idle cash earns 0 in arm B; r1269 already measured the repo ladder's worth at +0.10~0.15pp/yr on this book, so B is the LOWER bound and arm C is left absent rather than silently equated to B
- entry_lag=0 is the published behaviour, kept so arm A reproduces every printed face
- capacity is read from the same 40-bar ruler as every other capacity face, so this face inherits their survivors-sweep bias
- the ladder rungs are multiples of the gate's own lens, frozen before the read; a rung beyond 10M sits almost entirely in cash, so its return is the cash curve, not a bigger book
- nothing here is adopted: this prices the ruler, it does not change the book
