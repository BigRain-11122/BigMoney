# 同一张单的入场摩擦，两块板面之间挪了多少

快照口径：两块 ETF 现货板分别在 **2026-11-13** 与 **2026-11-16** 收盘后各读一次；IOPV 是实时估值，不是公布净值。

**两张面价的不是一样大的单**：2026-11-13 那张 **￥431,875.80**、2026-11-16 那张 **￥431,727.80**（额度在地板之间裁过）。费率是按份额算的，所以下面的挪动是**两种费率套到同一张单（2026-11-16，￥431,727.80）上**重算的——不是把两张单的金额相减（那答的是「我的单变了多少」，不是「市场要的价变了多少」）。

**合计：5,150.75 → 4,406.68，挪了 -744.07 元（-0.17 个百分点）**——占这张单 1.19% → 1.02%。

| 代码 | 计划金额 | 溢价率（2026-11-13） | 溢价率（2026-11-16） | 挪动 | 这次多付/少付 ￥ |
|---|---|---|---|---|---|
| 159519 | ￥86,324.30 | -1.34% | -0.75% | +0.59pp | 508.62 |
| 159655 | ￥86,286.00 | +8.22% | +6.75% | -1.47pp | -1,270.91 |
| 510760 | ￥86,400.60 | -0.45% | -0.31% | +0.14pp | 120.36 |
| 512040 | ￥86,351.90 | +0.02% | -0.22% | -0.24pp | -208.19 |
| 513690 | ￥86,365.00 | -0.48% | -0.36% | +0.12pp | 106.06 |
| — | **合计** | | | | **-744.07** |

## 这一面答不了什么

- two boards, two readings: IOPV is a realtime estimate and a cross-border leg's premium moves with a timezone the local close does not see
- legs one face could not price are named and excluded, never counted as zero
- if the two faces priced different order sizes, the move is recomputed on the newer sheet only -- a sizing change is not a market move
- a leg whose denominator belongs to another session, or whose board reads a different convention, is named with both dates and stays out of the money (r1606)
- 两块板不是一条序列：这里只印「挪了多少」，不印「现在这个水平算高还是低」——那个问题要等板面自己攒够观测（另一个面在管）。

判词由数字派生：**PREMIUM_FLAT**（平坦带 ±0.30pp）。

口径自证：本面在 2026-11-16 那张单上重算的合计 **￥4,406.68**，与那面自己发布的「相对净值多付」**￥4,406.69** 差 **￥-0.01**——差在 1 元内才准发布，否则这一面拒绝出件。
