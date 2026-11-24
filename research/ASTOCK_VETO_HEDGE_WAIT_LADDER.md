<!-- BEGIN:ASTOCK-VETO-HEDGE-WAIT-LADDER -->
# 等待的价格取决于你留多少对冲

`THE_CEILING_IS_A_RATIO_NOT_A_WAIT` · `PARTIAL_HEDGING_DOES_NOT_MAKE_THE_WAIT_CHEAP` · `THE_POINT_ESTIMATE_IS_THE_WORST_OF_THREE_BETAS` · `YOU_MUST_ALREADY_HOLD_MOST_OF_THE_HEDGE`

generated 2026-11-24T09:19:21+0800 | evidence_cutoff **2026-11-20** | machine `bm-c`

## 1. 一句话

- 把等待按「等待期保留多少对冲」重新定价：r2038 的裸等价格（k=0）复现为每年 16.580pp；k=0.65（BUDGET 规则 A）仍要每年 2.724pp（27242 元/百万），是它买到的东西的 225 倍；要对冲比例到 k=0.8986（3907 手）等待才不再比带宽本身更贵。而等待追的那个 0.124pp 天花板，其实今天把比例挪到 1.0 就已经拿到（10.639% 对 10.763%）——掉下来的这部分是一个比例，不是一段等待；顺带，部署用的点估计在这三个 beta 里残差最差。

## 2. 为什么这一面存在

r2038 给等待开了一张价签：如果等带宽收窄的这 10.24 年里账本裸着，每年多扛 16.580pp，而等到的东西只有 0.124pp——1367 倍。它自己在边界里写明：

> 一个跑部分对冲（比如 BUDGET 面规则 A 的 k=0.65）的读者付的等待费比这里少，本面价的是**完全不对冲**的等待。

本面把这句话做成一张阶梯表。用的不是新数据，是 band 面自己印的五条残差行——
它们不是五个独立测量，而是同一个二次型的五个点：

```
R(k)^2 = Var(book) - 2k*Cov(book, hedge) + k^2*Var(hedge)
```

五个点、三个参数，多出来的两行就是检查。

## 3. 先把身份核对上

| 项目 | 本面从五条残差行反解 | band 面自己印的 | 差 |
|---|---|---|---|
| 账本年化波动 | 27.3433% | 27.3433% | 0.000000 pp |
| 残差最小点 k | 0.970652 | 全窗 beta 0.970652 | 1.29e-12 |

五条行逐点复现的最大误差 **5.96e-14**（波动 pp）。也就是说：面里的「残差行」和「全窗 beta」不是两套数，是同一个二次型的两张脸。

## 4. 阶梯：等待期留多少对冲，每年付多少

参考臂是 r2038 的**部署**（k=0.9013，3919 手），成本 = R(k) − R(参考)。

| 等待期对冲 k | 手数 | 残差年化波动 | 每年多扛 | 元/百万/年 | 10.24 年总价 | 倍率 |
|---|---|---|---|---|---|---|
| 0.0000 | 0 | 27.343% | 16.580 pp | 165,803 | 169.75 pp | 1366.5 |
| 0.2500 | 1087 | 21.509% | 10.746 pp | 107,464 | 110.02 pp | 885.7 |
| 0.5000 | 2174 | 16.184% | 5.421 pp | 54,207 | 55.50 pp | 446.8 |
| 0.6500 | 2826 | 13.487% | 2.724 pp | 27,242 | 27.89 pp | 224.5 |
| 0.7500 | 3261 | 12.059% | 1.296 pp | 12,960 | 13.27 pp | 106.8 |
| 0.8500 | 3696 | 11.064% | 0.301 pp | 3,011 | 3.08 pp | 24.8 |
| 0.9000 | 3913 | 10.769% | 0.006 pp | 58 | 0.06 pp | 0.5 |
| 0.9500 | 4130 | 10.625% | -0.138 pp | -1,380 | -1.41 pp | -11.4 |
| 1.0000 | 4348 | 10.639% | -0.124 pp | -1,242 | -1.27 pp | -10.2 |
| 1.0263 | 4462 | 10.709% | -0.054 pp | -536 | -0.55 pp | -4.4 |

- **打平带**：k ∈ [0.8986, 1.0427]（3907 .. 4534 手）——在这个带内，等待每年多扛的波动不到它买到的东西。
- **低边界 0.8986** 就是这道题的答案：对冲至少要上到部署量的 99.7%，把剩下的留到带宽变窄之后才不亏。
- 规则 A 的 k=0.65 落在带外很远：每年 2.724 pp（27,242 元/百万），是天花板 225 倍。

> 判词 `YOU_MUST_ALREADY_HOLD_MOST_OF_THE_HEDGE` 的理由：the hedge has to be at least 99.7% of the deployed one before the wait stops costing more than it buys。

## 5. 天花板是一个比例，不是一段等待

r2038 把残差从 10.763% 降到 10.639% 记作「等待的收益」。但 10.639% 正是 **k=1.0** 那一行——也就是今天就能拿到的残差。等带宽收窄并没有创造出这个数，它只是让一个估计收敛到它；
而比例是你现在就能选的。

| 用什么 beta | k | 残差年化波动 | 相对部署 |
|---|---|---|---|
| 点估计（部署） | 0.9013 | 10.763% | +0.000 pp |
| 单位 beta | 1.0000 | 10.639% | -0.124 pp |
| 样本外 beta | 1.0263 | 10.709% | -0.054 pp |

> 判词 `THE_CEILING_IS_A_RATIO_NOT_A_WAIT`：moving the hedge to unit beta removes as much residual volatility as the wait is waiting for。

> 判词 `THE_POINT_ESTIMATE_IS_THE_WORST_OF_THREE_BETAS`：on the window the face evaluates them on, both the unit-beta and the out-of-sample beta leave less residual volatility than the deployed one。

## 6. 本面不说的

- 不说该选哪个 k。本面只给「等」定价，不定「对冲多少」。
- 不说 k=1.0 比点估计「更对」——单位 beta 只是在这张残差表自己的窗口上更好；换窗口重选比例就是又在窗口上挑数。
- 不说这 52/77 期代表未来 regime（r2037 已明说不等于样本公平）。
- 台阶假设等待期内 k 恒定、不随波动调整；运行中调比例会产生换手成本，本面没算。
- 口径是每 1,000,000 元的镜头，与票面 13.041bp/边的成本腿不是同一个量，两者不相加。

## 7. 复现

```
python scripts/astock_veto_hedge_wait_ladder.py selftest
python scripts/astock_veto_hedge_wait_ladder.py run
python scripts/astock_veto_hedge_wait_ladder.py check
```

Machine `bm-c`, generated 2026-11-24T09:19:21+0800.
<!-- END:ASTOCK-VETO-HEDGE-WAIT-LADDER -->
