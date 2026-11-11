# ETF 复合书 · 打印的单，和账上的书

会话 `2026-11-11`｜票 `TICKET-2026-11-11.json`｜上游 `results/etf_book_swap_stack.json`

**打印的动作能把声明的账一本本复原**：没有漏印的腿，也没有多印的手数。

## 下一张单从哪本账起算

- 已写下的执行后账：bar `2026-11-11`｜风险腿 ¥392,673｜现金 ¥607,327｜持仓 5 只｜这一行是**执行行**

## 这本书每天的账

- **没有一天的账可记**：执行 bar `2026-11-11` 与面板最新 bar 是同一天（2026-11-11）——不是算不出来，是那天之后还没有收盘价。

- 现金腿按 1 日回购计息（周五→周一算三天）：最近报价 **1.165%**（2026-11-10），cash ¥607,327 每个交易日挣 **¥19.38**，跨周末一格 **¥58.15**——不记这一行，现金就只是躺在账上的数字。

## 这一根 bar 能不能记估值（价格面板）

- bar `2026-11-11` 全腿都有收盘价：执行与估值都记在这一根上。

## 引擎体检：同一批票往前 20 个 bar

- 从 bar `2026-10-14` 到执行 bar：持仓按面板收盘逐日重估、现金按 1 日回购计息（缺回购报价 1 个 bar，有票停牌/缺价 0 个 bar）。
- 腿市值 ￥387,817 → ￥392,673（**+1.25%**），现金利息 **￥521.68**。
- 恒等腿：最后一行算出的腿市值与账本行自己记的腿金额差 **￥0.00**（通过）——同一批手数、同一批收盘价，引擎必须把账本写下的钱算回来。
- **这不是这本书的盈亏**：账本从执行 bar 才开始，这一段是同一批持仓的历史回放，只证明引擎在真面板上走得通，不给这本书记任何收益。

## 票面背后还有一本账（引擎账 vs 执行账）

- 造这张单的脚本自己维护一本归一化账（`results/etf_book_order/ledger.jsonl`，最新 bar `2026-11-11`）：k=0.4603。
- 执行账（这张面写下的那本）：k=0.3927，NAV ¥1,000,000。
- 差 **6.76pp = ¥67,580 名义暴露**。两本账各自都没错：引擎账是**裁剪前**的策略暴露，执行账是额度允许的暴露。但这意味着**下一张单从哪本账起算，会差这么多钱**——所以「从账本起算」必须是执行账，不是引擎账。

## 这一根 bar 有没有被改写过

- **这本账没有记到这根 bar 的改述**——但记录是从本轮才开始写的，**之前改写过的 bar 这里看不到**：没有记录不等于没被改过。
- 页面停在 bar `2026-11-10`，与这根 bar 不同天：不拿两天的账互相校验。

## 不能从这张面读出来的

- the reconciliation compares two documents, not two accounts: it says what the printed rows leave behind relative to the book the same face declares, and it cannot see whether the broker actually filled those lots
- the base divergence holds the target weights of THIS ticket fixed on purpose -- it isolates the starting-book effect. What the next decision bar selects is a different question and is not answered here
- prices are the sheet's own bar closes; a real execution will move both the share counts and the cash leg

- 出处：`scripts/etf_book_positions.py`；执行后账在 `results/etf_book_positions/LEDGER.json`（按决策 bar 一行）。同一 bar 重跑若数值不变=保持；真的变了会记一条改述并在上面印出两组数。
