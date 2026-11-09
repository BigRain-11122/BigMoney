# ETF 复合书 · 打印的单，和账上的书

会话 `2026-11-06`｜票 `TICKET-2026-11-06.json`｜上游 `results/etf_book_swap_stack.json`

**照这张单打字，账上还剩 ¥67,289 的票没卖**——不是估值差，是打印出来的动作行本身没覆盖这张单自己声明的账。

## 打印行漏了哪几笔（手数与钱）

| 代码 | 票面起点 | 打印动作之后 | 声明的账 | 差 | 价 | 差多少钱 |
|---|---|---|---|---|---|---|
| 159263 | 805 | 805 | 687 | **+118 手** | 1.143 | **¥13,487** |
| 159501 | 444 | 65 | 0 | **+65 手** | 2.069 | **¥13,448** |
| 159577 | 571 | 571 | 487 | **+84 手** | 1.612 | **¥13,541** |
| 513100 | 426 | 62 | 0 | **+62 手** | 2.158 | **¥13,380** |
| 513690 | 794 | 794 | 678 | **+116 手** | 1.158 | **¥13,433** |

- 合计 **¥67,289**（0 行没有当日价，未计入金额）。
- 读法：净额单只印了换票的那两笔卖和一笔合并买；额度裁剪表自己那五腿的卖出（65/62/116/84/118 手）从来没有变成动作行。顺序没错、算术没错，但**打字的人少打五笔**。

## 下一张单从哪本账起算

- 已写下的执行后账：bar `2026-11-06`｜风险腿 ¥392,401｜现金 ¥607,599｜持仓 4 只

## 把账本改回票面的样子，要再打多少

| 代码 | 目标手数 | 从票面起算的动作 | 从账本起算的动作 | 价 | 差多少钱 |
|---|---|---|---|---|---|
| 159263 | 805 | 不动 | 买 118 | 1.143 | **¥13,487** |
| 159501 | 444 | 不动 | 买 444 | 2.069 | **¥91,864** |
| 159513 | 0 | 不动 | 卖 920 | 1.705 | **¥156,860** |
| 159577 | 571 | 不动 | 买 84 | 1.612 | **¥13,541** |
| 513100 | 426 | 不动 | 买 426 | 2.158 | **¥91,931** |
| 513690 | 794 | 不动 | 买 116 | 1.158 | **¥13,433** |

- 合计 **¥381,115**：换票一执行，票面与账本说的就不再是同一批票（票面还写着卖出前的两只，账本里那两只已经清零、换成了合并后的兄弟票）。这个数不是下一张单的大小，而是**把账本按票面修回去要再打出去的钱**——所以下一张单只能从账本起算。
- 「从票面起算」一列全是「不动」不是巧合：目标权重取自这张票自己，票面当然与自己一致。这一节量的是底座差，不是选股，也不是下一轮的预测。

## 不能从这张面读出来的

- the reconciliation compares two documents, not two accounts: it says what the printed rows leave behind relative to the book the same face declares, and it cannot see whether the broker actually filled those lots
- the base divergence holds the target weights of THIS ticket fixed on purpose -- it isolates the starting-book effect. What the next decision bar selects is a different question and is not answered here
- prices are the sheet's own bar closes; a real execution will move both the share counts and the cash leg

- 出处：`scripts/etf_book_positions.py`；执行后账在 `results/etf_book_positions/LEDGER.json`（按决策 bar 一行，同一 bar 重跑只更新不重复）。
