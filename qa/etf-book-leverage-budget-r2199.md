# QA — etf_book_leverage_budget (r2199 · bm-c)

轮次：r2199 · 机：bm-c · 时间：2026-11-28 02:3x（+08:00）
产物：`scripts/etf_book_leverage_budget.py` · `results/etf_book_leverage_budget.json` ·
`research/ETF_BOOK_LEVERAGE_BUDGET.md`

## 这轮回答的问题

r2198 的 CEO 面写了一句话：「6.12% 的波动要补到 8%，得 1.31 倍杠杆」。读者会顺着问：
那为什么不用杠杆？本面把这句话拆成两半并各自定价。

## 验收清单

| 项 | 判据 | 实测 | 结论 |
|---|---|---|---|
| 与父面逐位对账 | cap=1.00 序列与 `book_pair_blend.load_etf()` 最大绝对差 = 0 | 0.0 | PASS |
| 自检 | 离线腿全过 | 15/15 | PASS |
| check | rc0 且不印 STALE | rc0，`4 arms, THE_BOOK_ALREADY_RUNS_ABOVE_ITS_TARGET (vol gap -2.47 pp)` | PASS |
| check 漂移语义 | 面缺 → rc2（STALE），不是 rc1 | 自检第 15 腿 + check 代码路径 | PASS |
| 判词由计数决定 | verdict 由 vol 缺口/净 Sharpe 计数分支，不硬写 | `verdict_of` 三支 + mix 三支，自检覆盖三支 | PASS |
| 臂上限不被突破 | 每臂 max scale ≤ 该臂 cap | 四臂 `max_scale_never_exceeds_cap=true` | PASS |
| 融资成本符号 | 杠杆臂净 CAGR 不得高于毛 CAGR | 四臂 `financing_cost_pp ≥ 0` | PASS |
| 毛收益随 cap 单调 | 更宽的 cap 不得毛收益更低 | 递增 | PASS |
| 上游一致性 | mix 节算术与判词词面一致（1e-6 内） | check 重算 `net_cagr`/`net_sharpe`/`sharpe_change` 三项 | PASS |
| 页面与面一致 | 页面印面自带 verdict + 标记块 | 有标记块、有 verdict | PASS |

## 结论（三行）

1. **ETF 单本交付 10.47% 波动，比 8% 目标高 2.47pp** —— 目标是"名义的"，规则只能降不能升，
   波动上升期 60 日估计偏低时它无法纠正。
2. **放宽 cap 到 1.25/1.50/2.00 几乎无效**：最高 1.50x（2.00x 从未触到，故两行完全相同），
   只 15.6% 的日子加杠杆；净 CAGR +0.11pp，净 Sharpe 从 0.962 掉到 0.955，最大回撤四臂相同。
3. **r2198 的 1.31x 是混合钱包的**：按父面自己印的 8.59%（毛）扣 1.84pp 融资后 6.75%，
   Sharpe 1.060 → 0.843（−0.217）。**借来的那一块波动，比它买到的收益贵。**

## 诚实线（未做 / 近似）

- 融资成本是假定 6%/yr 的线性扣减，不是实测；券商真实有保证金比例与展期规则，本面不建模。
- 回撤四臂相同这一事实**未定位到具体日期**，页面只陈述事实，不给因果。
- 面板仍是现存 ETF（幸存者偏差），与父面同源同病；杠杆不能修这个。
- 中间行（父面 8.5856%）与 `6.5078% × 1.3065` 差 0.08pp，是父面自身的算术，本面照印并标注。

## 未接线（承 r2195-r2198 欠账，本轮 CONTENTION 不可动）

链腿 / 冒烟腿 / CEO 一页纸小节 / CODELY 判例卡 / 方法论资产卡 —— 全为共享面，
`repo_write_contention` rc=3（对端 interactive pid 30500 自 2026-11-27T21:54:41 存活）。
