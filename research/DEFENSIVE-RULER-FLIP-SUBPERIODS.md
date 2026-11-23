# 防御尺子修好之后的翻面：过得了样本外吗

generated 2026-11-23T09:02:01 | evidence_cutoff 2026-11-20 | 窗 2020-01-02..2026-11-19（1667 bar·IS 至 2023-12-31）

## 一句话

- **翻面判词：`FLIP_IS_IN_SAMPLE_ONLY`** —— 书 `nobond_vt08` 在风险调整后**只在样本内落后，2024 起又回到书更好**。
- **尺子修复本身的判词：`RULER_REPAIR_EFFECT_IS_SEGMENT_SPECIFIC:out_of_sample_only`** —— 修好后的篮子在两段里对旧尺子的夏普增益 0.000 / 0.772。
- 缺口在哪一段：全窗差 **-0.332** 是两段的混合——样本内 **-0.768**、样本外 **0.119**（符号在这两段里是反的）。
- 为什么样本内与尺子无关：all but 2 of the 33 names whose re-label changes the basket have no price before 2023-12-31; the 2 that do are measured in `is_precision`, not assumed away。
- 全窗那一行（r1975 的结论）照旧印在 `verdict.full_window_flip_from_r1975`，本面不改它。

## 两段并排（同一窗、同一口径、同一段首归一）

| 段 | 书 年化 | 书 夏普 | 书 回撤 | 篮子 年化 | 篮子 波动 | 篮子 夏普 | 篮子 回撤 | 夏普差（书-篮） | 回撤倍数 |
|---|---|---|---|---|---|---|---|---|---|
| 全窗 | 11.16% | 1.101 | -10.56% | 1.28% | 0.93% | 1.433 | -1.35% | -0.332 | 7.82x |
| IS ≤2023-12-31 | 5.81% | 0.621 | -8.80% | 0.82% | 0.61% | 1.389 | -1.19% | -0.768 | 7.39x |
| OOS >2023-12-31 | 19.04% | 1.743 | -10.56% | 1.94% | 1.24% | 1.624 | -1.35% | 0.119 | 7.82x |

书那几列全部来自书自己的面（`results/etf_nobond_vt.json::runs[nobond_vt08]`，含 `cagr_is/sharpe_is/maxdd_is` 与 `_oos` 六格），本面不重算书——重算一次就是第二个答案。

## 尺子修复在每段里做了什么

| 段 | 旧尺子夏普 | 新尺子夏普 | 夏普增益 | 波动降低 | 年化变化 | 回撤减轻 |
|---|---|---|---|---|---|---|
| 全窗 | 0.861 | 1.433 | 0.572 | 0.51 pp | 0.1 pp | 2.51 pp |
| IS | 1.389 | 1.389 | 0.000 | 0.0 pp | 0.0 pp | 0.0 pp |
| OOS | 0.852 | 1.624 | 0.772 | 0.86 pp | 0.23 pp | 2.51 pp |

旧尺子成员 109 名、新尺子 76 名（同一块面板 5285 行 × 1637 列，翻转抹平 169 处）。

### 为什么样本内两把尺子给出的篮子一模一样

整块面板上被改动标签的名字共 **316 只**（commodity->equity 26、equity->commodity 4、equity->crossborder 239、money->bond 14、money->equity 33），但其中只有 **33 只**会改变「债+货币」这只篮子的成员（`money->bond` 在并集内两边都算，`equity->crossborder` 两边都在并集外）。这 33 只的最早一根 bar 落在 **2015-08-04 .. 2026-07-08**；在 2023-12-31 之前就有价格的有 **2 只**。

所以 `THE_REPAIR_MOVES_NAMES_THAT_EXISTED_IN_IS`：all but 2 of the 33 names whose re-label changes the basket have no price before 2023-12-31; the 2 that do are measured in `is_precision`, not assumed away。

实测差异（样本内两把尺子的篮子，970 bar，不取整）：年化 **+0.00000 pp**、波动 **+0.00000 pp**、夏普 **+0.00000**、回撤 **+0.00000 pp**；单日收益最大差 **0.000000 pp**，有差异的日子 **0 天**。

读法：这不是「两把尺子碰巧一样」，而是**能改变篮子的名字在样本内要么还没上市、要么过不了流动性门**，所以样本内这一段拿旧尺子或新尺子算出来的都是同一只篮子——它只能回答「书 vs 一只没被污染的篮子」，回答不了「尺子修好之后翻不翻」。

那 2 只在 2023-12-31 之前就有价格的名字，在臂窗（2020-01-02..2023-12-31）里的实际资格：

| 代码 | 改法 | 最早 bar | 臂窗内有资格的交易日 | 臂窗成交额中位（百万元） | 门（百万元） |
|---|---|---|---|---|---|
| 511770 | money->equity | 2017-04-10 | 0 | 0.04 | 20.0 |
| 159005 | money->equity | 2015-08-04 | 0 | 2.38 | 20.0 |

0 天有资格 = 它们在这段里从来没进过篮子，所以两条曲线逐日完全相同（上表 0 天有差异）。

## 逐年在做什么（篮子，两把尺子）

| 年 | 旧尺子年化 | 新尺子年化 | 年化差 | 新尺子回撤 |
|---|---|---|---|---|
| 2020 | -0.00% | -0.00% | 0.0 pp | -1.19% |
| 2021 | 1.09% | 1.09% | 0.0 pp | -0.17% |
| 2022 | 0.31% | 0.31% | 0.0 pp | -0.72% |
| 2023 | 1.82% | 1.82% | 0.0 pp | -0.46% |
| 2024 | 4.40% | 4.40% | 0.0 pp | -0.94% |
| 2025 | 0.54% | -0.76% | -1.3 pp | -1.35% |
| 2026 | -0.47% | 2.30% | 2.77 pp | -0.84% |

篮子是收盘价口径，分红不在收益里——这低估了篮子的真实总收益与夏普，三个段都是对篮子不利方向的保守读数。

两把尺子只在 **2025、2026** 这两年读出不同的年化（其余年份 0.0pp），也就是被旧尺子算成现金的那批股票 ETF 进入样本之后才分叉：2025 年旧尺子 0.54% / 新尺子 -0.76%；2026 年旧尺子 -0.47% / 新尺子 2.30%。

## 没印的东西（以及为什么不印）

- `每段的钱`：needed CAGR = basket Sharpe x book vol, and the book face publishes no per-segment vol; the money line is withheld rather than approximated.
- `篮子不是这本书`：the book is a bond-free 5-name rotating composite with an 8% vol target; the basket is an equal-weight holding of every bond+money ETF. A Sharpe comparison is a metric comparison.
- `分段年化口径`：both sides are renormalised off each segment's own first level (etf_equity_alpha.stats2), never off the global base.
- `幸存者`：the basket is drawn from ETFs that exist today.

## 复跑

```
python scripts/defensive_ruler_flip_subperiods.py            # 重算并写面（控制臂不过即拒绝发布）
python scripts/defensive_ruler_flip_subperiods.py check      # 重 derive 逐字段对账（源面字节动=STALE rc3）
python scripts/defensive_ruler_flip_subperiods.py selftest   # 离线腿
```
