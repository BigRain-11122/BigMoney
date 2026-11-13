# 同一张单的入场摩擦，两块板面之间挪了多少

快照口径：两块 ETF 现货板分别在 **2026-11-12** 与 **2026-11-13** 收盘后各读一次；IOPV 是实时估值，不是公布净值。

**合计：-2,085.61 → -1,941.85，挪了 143.76 元（+0.04 个百分点）**——占这张单 -0.60% → -0.56%。

| 代码 | 计划金额 | 溢价率（2026-11-12） | 溢价率（2026-11-13） | 挪动 | 这次多付/少付 ￥ |
|---|---|---|---|---|---|
| 159519 | ￥86,403.20 | -1.16% | -1.34% | -0.17pp | -150.60 |
| 510760 | ￥86,377.20 | -0.21% | -0.45% | -0.24pp | -205.40 |
| 512040 | ￥86,413.60 | -0.01% | +0.02% | +0.03pp | 21.78 |
| 513690 | ￥86,325.00 | -1.03% | -0.48% | +0.55pp | 477.98 |
| — | **合计** | | | | **143.76** |

**1 只的分母不属于本场，不进任何钱数**（价格是对的，比的不是同一场）：

| 代码 | 溢价率（2026-11-12） | 溢价率（2026-11-13） | 为什么比不了 |
|---|---|---|---|
| 159655 | +7.80% | +8.22% | 2026-11-12 那侧是 2026-11-13 的净值 |

## 这一面答不了什么

- two boards, two readings: IOPV is a realtime estimate and a cross-border leg's premium moves with a timezone the local close does not see
- legs one face could not price are named and excluded, never counted as zero
- if the two faces priced different order sizes, the move is recomputed on the newer sheet only -- a sizing change is not a market move
- a leg whose denominator belongs to another session, or whose board reads a different convention, is named with both dates and stays out of the money (r1606)
- 两块板不是一条序列：这里只印「挪了多少」，不印「现在这个水平算高还是低」——那个问题要等板面自己攒够观测（另一个面在管）。

判词由数字派生：**PREMIUM_FLAT**（平坦带 ±0.30pp）。

口径自证：本面在 2026-11-13 那张单上重算的合计 **￥5,155.81**，与那面自己发布的「相对净值多付」**￥5,155.91** 差 **￥-0.10**——差在 1 元内才准发布，否则这一面拒绝出件。
