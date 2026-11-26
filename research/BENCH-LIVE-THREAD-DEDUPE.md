# 还有几条活口：判词册的 6 条 CANDIDATE 去重后剩下几条，以及被收益门扔掉的那条臂

generated 2026-11-26T16:59:58+08:00 | evidence_cutoff 2026-11-25 | 卡片 39 · 臂 85 | 活口行 4 + 卡级活口 2 → **distinct 测量 4**

读法：一条「活口」= 一个测量（同一面板上的同一年化/夏普/回撤）。两张卡片印出逐位相同的读数时，它们证明的是跑了同一条规则同一个面板，**不是独立复算，不能当两次证据**。

## 一、还活着的测量（去重后）

### 1a 有臂的卡片（按臂去重）

| 卡 | 臂 | 年化 | 夏普 | 回撤 | 波动 | 换手/年 | 样本外年化 | 判词 |
|---|---|---|---|---|---|---|---|---|
| census_commodity / robust_tsmom_commodity | 120d / tsmom\|{'lookback': 120, 'skip': 21}\|ls | 5.01 | 0.626 | -21.74 | 8.37 | 6.51 | 9.44 | GO |
| census_commodity / robust_tsmom_commodity | 250d / tsmom\|{'lookback': 250, 'skip': 21}\|ls | 5.24 | 0.671 | -18.88 | 8.11 | 4.83 | 7.9 | GO |

### 1b 卡级活口（这些卡没有 arms[]，只有一句判词 → 分母会少算）

| 卡 | 判词 | 截止 | 逐品种读数 |
|---|---|---|---|
| basis_timing_perm | SIGNIFICANT | 2026-11-25 | IC 10.07 年化 / 回撤 — / 2390 bar；IM 9.35 年化 / 回撤 — / 1052 bar |
| basis_timing_size | GO | 2026-11-25 | IC 10.07 年化 / 回撤 -1.89 / 2391 bar；IM 9.35 年化 / 回撤 -3.05 / 1053 bar |

这一节存在的理由：只读 `arms[]` 的审计会把这两条活口读成不存在——**缺面不是零**。它们的形状与 1a 不同，所以不能并进同一张表，也不能假装它们已经被算进去。

## 二、同一测量被两张卡片各印一次

| 卡 | 臂 | 面板 | 年化 | 夏普 | 回撤 |
|---|---|---|---|---|---|
| census_commodity / robust_tsmom_commodity | 60d / tsmom\|{'lookback': 60, 'skip': 21}\|ls | AU+RB+SC × 4597 bar @ 2026-11-24 | 1.53 | 0.221 | -20.51 |
| census_commodity / robust_tsmom_commodity | 120d / tsmom\|{'lookback': 120, 'skip': 21}\|ls | AU+RB+SC × 4597 bar @ 2026-11-24 | 5.01 | 0.626 | -21.74 |
| census_commodity / robust_tsmom_commodity | 250d / tsmom\|{'lookback': 250, 'skip': 21}\|ls | AU+RB+SC × 4597 bar @ 2026-11-24 | 5.24 | 0.671 | -18.88 |
| census_index_futures / robust_donchian_index | 20_10 / donchian\|{'entry': 20, 'exit': 10}\|long / donchian\|{'entry': 20, 'exit': 10}\|ls | IC+IF+IH+IM × 2389 bar @ 2026-11-23 | -4.14 | -0.227 | -46.89 |
| census_index_futures / robust_donchian_index | 40_15 / donchian\|{'entry': 40, 'exit': 15}\|long / donchian\|{'entry': 40, 'exit': 15}\|ls | IC+IF+IH+IM × 2389 bar @ 2026-11-23 | -4.22 | -0.235 | -47.33 |
| census_index_futures / robust_donchian_index | 55_20 / donchian\|{'entry': 55, 'exit': 20}\|long / donchian\|{'entry': 55, 'exit': 20}\|ls | IC+IF+IH+IM × 2389 bar @ 2026-11-23 | -3.92 | -0.215 | -47.06 |
| census_index_futures / robust_ma_index | 50_100 / ma_cross\|{'fast': 50, 'slow': 100}\|ls | IC+IF+IH+IM × 2389 bar @ 2026-11-23 | 5.31 | 0.479 | -25.51 |
| census_index_futures / robust_ma_index | 50_200 / ma_cross\|{'fast': 50, 'slow': 200}\|ls | IC+IF+IH+IM × 2389 bar @ 2026-11-23 | 6.58 | 0.586 | -17.6 |

这不是「两个独立来源互相印证」，是同一笔读数被记账两次；把 6 当 6 条活口汇报，等于把同一件事卖两遍。

## 三、被自己卡片的收益门扔掉、但风险两项都更好的臂

判据：同一张卡片里，判词不是活的臂，夏普**和**回撤**同时**优于一条活臂。

| 卡 | 被扔掉的臂 | 判词 | 年化 | 夏普 | 回撤 | 换手 | 对比被选中的臂 | 差（年化/夏普/回撤） | 拒收的门 |
|---|---|---|---|---|---|---|---|---|---|
| census_commodity | tsmom\|{'lookback': 250, 'skip': 21}\|long | NO_EDGE | 4.56 | 0.754 | -13.7 | 2.49 | tsmom\|{'lookback': 250, 'skip': 21}\|ls (5.24/0.671/-18.88) | -0.68pp / +0.083 / +5.18pp | target_edge_pp=5 |
| census_commodity | tsmom\|{'lookback': 120, 'skip': 21}\|long | NO_EDGE | 4.42 | 0.714 | -16.13 | 3.31 | tsmom\|{'lookback': 250, 'skip': 21}\|ls (5.24/0.671/-18.88) | -0.82pp / +0.043 / +2.75pp | target_edge_pp=5 |

这些臂**不是更优**，是风险预算不同（少一条空头腿、换手更低）。问题只有一个：读者从来没被告诉它存在过——卡片的门只量收益，于是「用 0.6pp 年化换 0.09 夏普和 5pp 回撤」这个交换在页面上根本没有出现。

## 四、读不懂的判词词面（原样列出，不猜测）

`BASELINE_REFERENCE`, `FLIPS_WITH_LOOKBACK`, `NO_EDGE_REPACKAGES_BETA`, `UNINFORMATIVE_AT_TARGET`

## 五、诚实边界

1. 去重靠「面板 + 三个数逐位相同」，所以**同一条规则跑在两个不完全相同的面板上会被算成两条**；反过来，两条不同规则碰巧给出同样的三个数，会被并成一条（本册里前者更可能，因为它带着同一份 4,597 bar）。
2. 只读各卡片自己的 `arms[].common_window` 与 `criteria`，不重算任何收益、不重判任何门。
3. 「被扔掉的臂」只做双轴（夏普与回撤同时更好）筛选，不构成推荐；要变成推荐必须补敞口口径、成本口径与样本外一致性，那是另开票的事。
4. 本册不回答「该做哪条」，只回答「现在有几件事是真的、有几件被印了两遍、有几件没被印出来」。

