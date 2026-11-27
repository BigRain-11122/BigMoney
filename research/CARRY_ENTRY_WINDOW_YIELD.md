# carry 一年期起点分布 · 研究记录（r2196 · bm-c）

问的是：**同一本书，我对不同的日子上车，一年后的答案会差多少？** 而 r2192 的排序是不是日历给的？

读数面（机器可读）：`results/carry_entry_window_yield.json`

读者面（人可读，含全部表）：`results/carry_entry_window_yield.md`


## 一句话结论

- THE_CARRY_BOOK_CARES_LESS_ABOUT_WHEN_YOU_START_THAN_THE_ETF_BOOK
- 同一把尺（p90-p10 除中位）: carry 对冲臂 1.31x vs ETF vt08 3.56x；绝对跨度 11.25pp vs 32.34pp （绝对值跨书不可比：两本书的波动不同）
- r2192 的排序只在一本日历上验过一次；现在在 1717 个一年窗里按**同一量**（窗内 Sharpe）排：basis>对冲残差>不带对冲 占 83.46%（判词 THE_LINE_ORDER_MOSTLY_HOLDS_BUT_FLIPS_ON_SOME_STARTS）——按**钱**排则是 24.34%（判词 THE_LINE_ORDER_DEPENDS_ON_WHEN_YOU_START），两个量给出相反答案，因为不带对冲那条的波动是另两条的约四倍

## 口径与律

- 一年 = 244 根 bar；起点收盘决策、下一根 bar 起持有（与 r2195 的 ETF 面同一口径）。
- 三条线统一换成「一手资本的日分数」才可比：basis=名义额收益率，两臂=点数×200÷1,137,862.5。
- 求和口径为头条（一手不可分割，P&L 线性可加）；basis 的复利读数并列印出，禁混用排序。
- 重叠窗口不是独立样本：另印不重叠整年块作独立证据，不声称 p 值。
- 复现腿先跑：basis 在父面窗口逐位复现 + 两臂 Sharpe 逐位复现，任一失配 exit 2 不发布。

## 自捕与留账

- 本面不改任何已发布面；链腿/冒烟腿未接（竞争窗，见轮报告）。
- 未测：IM 腿、两臂自己的标空成本重估、显著性。
