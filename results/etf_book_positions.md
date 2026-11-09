# ETF 复合书 · 打印的单，和账上的书

会话 `2026-11-06`｜票 `TICKET-2026-11-06.json`｜上游 `results/etf_book_swap_stack.json`

**打印的动作能把声明的账一本本复原**：没有漏印的腿，也没有多印的手数。

## 下一张单从哪本账起算

- 已写下的执行后账：bar `2026-11-06`｜风险腿 ¥390,144｜现金 ¥609,856｜持仓 4 只

## 把账本改回票面的样子，要再打多少

| 代码 | 目标手数 | 从票面起算的动作 | 从账本起算的动作 | 价 | 差多少钱 |
|---|---|---|---|---|---|
| 159501 | 377 | 不动 | 买 377 | 2.069 | **¥78,001** |
| 159513 | 0 | 不动 | 卖 915 | 1.705 | **¥156,008** |
| 513100 | 362 | 不动 | 买 362 | 2.158 | **¥78,120** |

- 合计 **¥312,128**：换票一执行，票面与账本说的就不再是同一批票（票面还写着卖出前的两只，账本里那两只已经清零、换成了合并后的兄弟票）。这个数不是下一张单的大小，而是**把账本按票面修回去要再打出去的钱**——所以下一张单只能从账本起算。
- 「从票面起算」一列全是「不动」不是巧合：目标权重取自这张票自己，票面当然与自己一致。这一节量的是底座差，不是选股，也不是下一轮的预测。

## 这本书每天的账

- **没有一天的账可记**：执行 bar `2026-11-06` 与面板最新 bar 是同一天（2026-11-06）——不是算不出来，是那天之后还没有收盘价。

- 现金腿按 1 日回购计息（周五→周一算三天）：最近报价 **1.185%**（2026-11-06），cash ¥609,856 每个交易日挣 **¥19.80**，跨周末一格 **¥59.40**——不记这一行，现金就只是躺在账上的数字。

## 引擎体检：同一批票往前 20 个 bar

- 从 bar `2026-10-09` 到执行 bar：持仓按面板收盘逐日重估、现金按 1 日回购计息（缺回购报价 0 个 bar，有票停牌/缺价 0 个 bar）。
- 腿市值 ￥415,048 → ￥390,144（**-6.00%**），现金利息 **￥565.91**。
- 恒等腿：最后一行算出的腿市值与账本行自己记的腿金额差 **￥0.00**（通过）——同一批手数、同一批收盘价，引擎必须把账本写下的钱算回来。
- **这不是这本书的盈亏**：账本从执行 bar 才开始，这一段是同一批持仓的历史回放，只证明引擎在真面板上走得通，不给这本书记任何收益。

## 票面背后还有一本账（引擎账 vs 执行账）

- 造这张单的脚本自己维护一本归一化账（`results/etf_book_order/ledger.jsonl`，最新 bar `2026-11-06`）：k=0.4603。
- 执行账（这张面写下的那本）：k=0.3901，NAV ¥1,000,000。
- 差 **7.01pp = ¥70,109 名义暴露**。两本账各自都没错：引擎账是**裁剪前**的策略暴露，执行账是额度允许的暴露。但这意味着**下一张单从哪本账起算，会差这么多钱**——所以「从账本起算」必须是执行账，不是引擎账。

## 不能从这张面读出来的

- the reconciliation compares two documents, not two accounts: it says what the printed rows leave behind relative to the book the same face declares, and it cannot see whether the broker actually filled those lots
- the base divergence holds the target weights of THIS ticket fixed on purpose -- it isolates the starting-book effect. What the next decision bar selects is a different question and is not answered here
- prices are the sheet's own bar closes; a real execution will move both the share counts and the cash leg

- 出处：`scripts/etf_book_positions.py`；执行后账在 `results/etf_book_positions/LEDGER.json`（按决策 bar 一行，同一 bar 重跑只更新不重复）。
