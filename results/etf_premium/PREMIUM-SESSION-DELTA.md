# 同一张单的入场摩擦，两块板面之间挪了多少

快照口径：两块 ETF 现货板分别在 **2026-11-18** 与 **2026-11-19** 收盘后各读一次；IOPV 是实时估值，不是公布净值。

**合计：4,959.91 → 4,998.43，挪了 38.52 元（+0.01 个百分点）**——占这张单 1.15% → 1.16%。

| 代码 | 计划金额 | 溢价率（2026-11-18） | 溢价率（2026-11-19） | 挪动 | 这次多付/少付 ￥ |
|---|---|---|---|---|---|
| 159519 | ￥86,322.30 | -1.04% | -1.01% | +0.04pp | 34.01 |
| 159655 | ￥86,374.50 | +7.51% | +8.85% | +1.34pp | 1,156.12 |
| 510760 | ￥86,403.00 | -0.10% | -0.23% | -0.14pp | -117.85 |
| 512040 | ￥86,375.80 | -0.16% | -0.13% | +0.03pp | 28.24 |
| 513690 | ￥86,404.80 | -0.47% | -1.70% | -1.23pp | -1,062.00 |
| — | **合计** | | | | **38.52** |

## 这一面答不了什么

- two boards, two readings: IOPV is a realtime estimate and a cross-border leg's premium moves with a timezone the local close does not see
- legs one face could not price are named and excluded, never counted as zero
- if the two faces priced different order sizes, the move is recomputed on the newer sheet only -- a sizing change is not a market move
- a leg whose denominator belongs to another session, or whose board reads a different convention, is named with both dates and stays out of the money (r1606)
- 两块板不是一条序列：这里只印「挪了多少」，不印「现在这个水平算高还是低」——那个问题要等板面自己攒够观测（另一个面在管）。

判词由数字派生：**PREMIUM_FLAT**（平坦带 ±0.30pp）。

口径自证：本面在 2026-11-19 那张单上重算的合计 **￥4,998.43**，与那面自己发布的「相对净值多付」**￥4,998.45** 差 **￥-0.02**——差在 1 元内才准发布，否则这一面拒绝出件。
