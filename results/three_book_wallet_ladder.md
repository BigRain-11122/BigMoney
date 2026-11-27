# Three books, one wallet — the ladder of capital

面：`results/three_book_wallet_ladder.json` · 脚本：`scripts/three_book_wallet_ladder.py` · 证据截止：2026-11-26（1670 根 bar，2020-01-06 → 2026-11-26）

> 父面那只 100 万的钱包拿不到 carry，Sharpe 1.060。第一手 IC 合约要多掏 137,862 元才买得起（多 13.79% 资本），可到了那一档，一手合约正好吃掉整个 8% 预算——所以 1,137,862 元的钱包能拿到的最好答案是把整本书压在 carry 一本上：Sharpe 1.445，跳升 0.384，一口气吃掉门总价 0.784 里的 49%。网格真正想要的权重是 50%，那个权重要到 2,275,725 元才装得下，是第一档的 2.00x。这两档之间不是斜坡而是台阶：每一级台阶买回来的是重新分散的权利。

## 1. 父面留在桌上的那一半

`three_book_wallet` 回答的是 1,000,000 元这一只钱包：三本书、一个钱包、carry 因为一手 IC 合约吃掉 80,000 元波动预算里的 91,029 元而拿到权重 0.00，门的价格 0.784 夏普。它把这一半答案印得很诚实，然后停住了——因为递给它的钱包只有 100 万。

本面把同一个网格按**资本**重读一遍：不重算任何一本书，只问「到多少钱，第三本书才进得去；进去之后门还收多少」。

## 2. 机制：一手合约是不可分割的

| 量 | 值 |
|---|---|
| 一手 IC 合约吃掉的年化波动预算 | 91,029 元 |
| 在 8% 预算下，一手合约需要的资本 | 1,137,862 元 |
| 钱包 W 能表达的 carry 权重（合法带） | `[1137862.50 / W, 1]`，低于 1,137,862.5 元时只有 0 |
| 第三本书第一次能进的最小资本 | **1,137,862 元** |
| 那一刻它能拿到的权重 | **100.00%**（只能是 100%） |
| 钱包第一次能同时持有两本书 | 1,197,750 元 |
| 网格真正想要的 carry 权重 | 50.00% |
| 那个权重需要的最小资本 | **2,275,725 元** |
| 想要 / 第一档 | **2.00x** |

所以曲线不是一条斜线，而是一级台阶：`one IC lot is indivisible: the affordable carry weights at W form the half-line [1137862.50 / W, 1]. At W = 1137862 that half-line is the single point {1.00}, so the best the wallet can do is hold the carry book ALONE; the diversifiers come back only as W grows and the band's left edge falls.`

## 3. 台阶里的那一跳

| 量 | 值 |
|---|---|
| 100 万时的最好组合 | Sharpe 1.060（carry 权重 0.00） |
| 第一档前 1 元 | Sharpe 1.060 |
| 第一档（1,137,862 元） | Sharpe 1.445（100% carry） |
| 这一跳 | **+0.384 夏普** |
| 这一跳吃掉了门总价的 | **49%** |
| 为这一跳要多掏的资本 | 137,862 元（占 100 万钱包的 13.79%） |
| 门的总价（无门最优 1.844 − 100 万实得 1.060） | 0.784 |

## 4. 每一档的账

| 钱包（元） | 出处 | carry 权重 | 可表达的最小 carry 权重 | 最好组合 Sharpe | CAGR | 波动 | 回撤 | 门还收 | 比上一档多花的钱买到的夏普/百万 |
|---|---|---|---|---|---|---|---|---|---|
| 400,000 | round rung | 0.00% | 只有 0 | 1.060 | 6.51% | 6.12% | -6.72% | 0.784 | — |
| 750,000 | round rung | 0.00% | 只有 0 | 1.060 | 6.51% | 6.12% | -6.72% | 0.784 | 0.00 |
| 1,000,000 | round rung | 0.00% | 只有 0 | 1.060 | 6.51% | 6.12% | -6.72% | 0.784 | 0.00 |
| 1,137,862 | first lot: ONE IC contract is 100% of this wallet's 8% budget | 100.00% | 100.00% | 1.445 | 11.89% | 8.00% | -7.35% | 0.400 | 2.79 |
| 1,197,750 | first two-book mix: 95% carry still leaves room for one other book | 95.00% | 95.00% | 1.497 | 11.71% | 7.59% | -6.99% | 0.348 | 0.87 |
| 1,250,000 | round rung | 95.00% | 91.03% | 1.497 | 11.71% | 7.59% | -6.99% | 0.348 | 0.00 |
| 1,500,000 | round rung | 80.00% | 75.86% | 1.652 | 11.14% | 6.53% | -5.98% | 0.193 | 0.62 |
| 1,750,000 | round rung | 70.00% | 65.02% | 1.742 | 10.57% | 5.87% | -4.90% | 0.102 | 0.36 |
| 2,000,000 | round rung | 60.00% | 56.89% | 1.815 | 9.99% | 5.32% | -3.90% | 0.029 | 0.29 |
| 2,275,725 | wanted weight: carry can finally sit at the weight the ungated grid picks (50%) | 50.00% | 50.00% | 1.844 | 9.40% | 4.94% | -4.12% | 0.000 | 0.11 |
| 2,500,000 | round rung | 50.00% | 45.51% | 1.844 | 9.40% | 4.94% | -4.12% | 0.000 | 0.00 |
| 3,000,000 | round rung | 50.00% | 37.93% | 1.844 | 9.40% | 4.94% | -4.12% | 0.000 | 0.00 |
| 5,000,000 | round rung | 50.00% | 22.76% | 1.844 | 9.40% | 4.94% | -4.12% | 0.000 | 0.00 |
| 10,000,000 | round rung | 50.00% | 11.38% | 1.844 | 9.40% | 4.94% | -4.12% | 0.000 | 0.00 |
| 20,000,000 | round rung | 50.00% | 5.69% | 1.844 | 9.40% | 4.94% | -4.12% | 0.000 | 0.00 |

逐档看：carry 权重从 100% 一路退到 50%，因为钱包越大，一手合约占预算的比例越小，另一本书才有位置。

## 5. 这些是夏普，不是钱

| 钱包（元） | 自实现波动 | 要加多少杠杆才到 8% | 8%×Sharpe 的资本收益（父面恒等式） | 按自身波动算的年钱 |
|---|---|---|---|---|
| 400,000 | 6.12% | 1.31x | 8.48% | 26,031 元 |
| 750,000 | 6.12% | 1.31x | 8.48% | 48,808 元 |
| 1,000,000 | 6.12% | 1.31x | 8.48% | 65,078 元 |
| 1,137,862 | 8.00% | 1.00x | 11.56% | 135,290 元 |
| 1,197,750 | 7.59% | 1.05x | 11.97% | 140,229 元 |
| 1,250,000 | 7.59% | 1.05x | 11.97% | 146,346 元 |
| 1,500,000 | 6.53% | 1.23x | 13.21% | 167,112 元 |
| 1,750,000 | 5.87% | 1.36x | 13.94% | 184,966 元 |
| 2,000,000 | 5.32% | 1.50x | 14.52% | 199,790 元 |
| 2,275,725 | 4.94% | 1.62x | 14.76% | 213,941 元 |
| 2,500,000 | 4.94% | 1.62x | 14.76% | 235,025 元 |
| 3,000,000 | 4.94% | 1.62x | 14.76% | 282,030 元 |
| 5,000,000 | 4.94% | 1.62x | 14.76% | 470,050 元 |
| 10,000,000 | 4.94% | 1.62x | 14.76% | 940,100 元 |
| 20,000,000 | 4.94% | 1.62x | 14.76% | 1,880,200 元 |

最后两列必须一起读：`8%×Sharpe` 是父面的恒等式（把组合按杠杆放大到 8% 波动后的资本收益），它不是本面测出来的；本面测到的只有各档自己在原始波动下的钱。杠杆不是免费的——r2199 对 ETF 书最后 1.88pp 波动实测的融资价是 **-0.217 夏普**，这里不重复摊销。

## 5b. 同一级台阶，换一只波动旋钮

台阶的高度是 8% 这个旋钮定的，不是市场定的。把旋钮拧一下，每一档都跟着移动：

把旋钮拧到 **9.10%**，现在这只 100 万的钱包就正好装得下一手合约（100% 权重）——所以「要 228 万」这句话只在 8% 这一档成立，它同时也可以读成「8% 对这个钱包太紧了」。

| 目标波动 | 第一手合约需要的资本 | 网格想要的权重需要的资本 |
|---|---|---|
| 5% | 1,820,580 元 | 3,641,160 元 |
| 6% | 1,517,150 元 | 3,034,300 元 |
| 8% | 1,137,862 元 | 2,275,725 元 |
| 10% | 910,290 元 | 1,820,580 元 |
| 12% | 758,575 元 | 1,517,150 元 |

## 6. 诚实条款

- weights are quantised at 0.05, so a band edge is reported as the grid weight it can actually reach, never as the exact real number
- carry is the hedged EXCESS, gross of the hedge leg's cost; a real hedge needs a second account (parent's caliber, not re-estimated)
- the mix's realised vol is usually below 8%, so this is a Sharpe ladder, not a money ladder: money_cny_per_year is printed at each rung's own realised vol, and leverage_to_8pct is printed beside it with r2199's measured financing price (-0.217 Sharpe for the ETF book's last 1.88pp of vol) named rather than amortised
- within-sample statement on the three books' own published series, 2020-2026; the Sharpe ordering is not a forecast
- the 1,000,000 rung is asserted equal to the parent's own best_inside_gate: if it is not, this face is quoting a different ruler and goes red
- Sharpe is compared ACROSS rungs, but every rung also prints its own vol: the first rung sits at 8.00% against 6.12% at 1,000,000, so part of the jump is a shift in the risk taken, not only in the odds
- the rungs are the 8%% target's arithmetic, not a law: moving the target moves every rung in proportion (see entry.target_sensitivity, and section 5b of the page)

## 7. 复跑与守卫

```
python scripts\three_book_wallet_ladder.py run       # 重算并写面
python scripts\three_book_wallet_ladder.py check     # 输入动了=STALE(rc3)；自相矛盾=CHECK FAILED(rc2)
python scripts\three_book_wallet_ladder.py selftest  # 离线自检
```

`check` 的三件事：①任何上游面（父面 / ETF / 转债 / IC 面板 / 指数面板 / sizing spec）字节或 mtime 变了 → `STALE`；②阶梯自身单调性与可行性重算不通 → `CHECK FAILED`（不带 STALE 字样）；③100 万那一档必须等于父面自己发布的 `best_inside_gate`，不等 = 引用了另一把尺子。

