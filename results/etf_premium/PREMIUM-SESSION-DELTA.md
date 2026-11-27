# 同一张单的入场摩擦，两块板面之间挪了多少

快照口径：两块 ETF 现货板分别在 **2026-11-25** 与 **2026-11-26** 收盘后各读一次；IOPV 是实时估值，不是公布净值。

**两张面价的不是一样大的单**：2026-11-25 那张 **￥434,723.80**、2026-11-26 那张 **￥434,684.00**（额度在地板之间裁过）。费率是按份额算的，所以下面的挪动是**两种费率套到同一张单（2026-11-26，￥434,684.00）上**重算的——不是把两张单的金额相减（那答的是「我的单变了多少」，不是「市场要的价变了多少」）。

**合计：4,454.40 → 5,925.04，挪了 1,470.64 元（+0.34 个百分点）**——占这张单 1.02% → 1.36%。

| 代码 | 计划金额 | 溢价率（2026-11-25） | 溢价率（2026-11-26） | 挪动 | 这次多付/少付 ￥ |
|---|---|---|---|---|---|
| 159519 | ￥86,866.00 | -0.84% | -0.44% | +0.40pp | 349.46 |
| 159655 | ￥86,907.20 | +6.95% | +7.32% | +0.37pp | 322.95 |
| 510760 | ￥86,927.10 | -0.04% | -0.18% | -0.14pp | -122.05 |
| 512040 | ￥86,992.40 | -0.03% | -0.24% | -0.21pp | -179.12 |
| 513690 | ￥86,991.30 | -0.91% | +0.35% | +1.26pp | 1,099.40 |
| — | **合计** | | | | **1,470.64** |

## 这一面答不了什么

- two boards, two readings: IOPV is a realtime estimate and a cross-border leg's premium moves with a timezone the local close does not see
- legs one face could not price are named and excluded, never counted as zero
- if the two faces priced different order sizes, the move is recomputed on the newer sheet only -- a sizing change is not a market move
- a leg whose denominator belongs to another session, or whose board reads a different convention, is named with both dates and stays out of the money (r1606)
- 两块板不是一条序列：这里只印「挪了多少」，不印「现在这个水平算高还是低」——那个问题要等板面自己攒够观测（另一个面在管）。

判词由数字派生：**PREMIUM_WIDENED**（平坦带 ±0.30pp）。

口径自证：本面在 2026-11-26 那张单上重算的合计 **￥-439.08**，与那面自己发布的「相对净值多付」**￥-439.08** 差 **￥0.00**——差在 1 元内才准发布，否则这一面拒绝出件。
