# DIGEST · r1415 · 候选的第二阶门（年度轴）

- 日期: 2026-11-08
- 机器: bm-c
- 产品件: `scripts/candidate_year_gate.py`（selftest 15/15）+ `results/admission/CANDIDATES.json`
- 卡片: `knowledge/METHODOLOGY_ASSETS.md` E420
- smoke 腿: `product: a candidate that only works in two of its seven years is not a rate`

## 问题

r1414 用四道**单数门**（x1 CAGR≥8% / 12 相位全正 / x3 CAGR≥5% / 一日容量≥2,000 万）判 20 名小盘书
ADOPT_AS_CANDIDATE，全部通过。但同一份 receipt 的 `by_year` 是
`+41.9 / +35.7 / +3.5 / -7.6 / +48.9 / +75.9 / -18.7`：头条由 2024+2025 扛，当年在亏。
r1411 又出现了镜像现象——同一本书会死在 r1411 的相位差门（4.74pp）却活过 r1414 的门（17.20pp），
两条冻结判据合法相反。缺的不是阈值，是**日历轴**和**冲突的显式输出**。

## 做法

第二阶门，只重读已发布 receipt，不做新定价（判据跑前冻结，写入 receipt 的 `rule` 块并受 smoke 腿
钉住防漂移）：

| 检查 | 冻结线 |
|---|---|
| Y1 正年占比 | ≥ 70% |
| Y2 年度中位 | > 0 |
| Y3 最差年 | ≥ –15.0 pp |
| Y4 top-2 年占年度和 | ≤ 70% |
| C1 一日 5% 参与容量 | ≥ 20,000,000 CNY（r1414 冻结值） |

判决：C1 为 False → `CAPACITY_LIMITED`；四条年度检查全过 → `ADMIT`；恰三条 → `CONDITIONAL`；
两条及以下 → `REFUSE`。`C1 = null`（receipt 不发布容量面）记「未检验」，**不得读成通过**。

两个 schema 都被适配：`smallcap_book`（`by_year` 百分比 + 容量面）与 `breadth_book`
（`per_year` 分数 + 单 ALL 臂、无容量面）。

## 读数

| 候选 | published | 年度门 | 失败项 | 关键数 |
|---|---|---|---|---|
| smallcap_book n20 | ADOPT_AS_CANDIDATE | **CONDITIONAL** | Y3 | 2026 部分年 –18.71pp（2 队列≈5.7 个月）；top-2 占比 69.5%（压线通过） |
| breadth_book ALL | REFUSE_AS_CANDIDATE | CONDITIONAL | Y4 | top-2 占比 79.3%；最差年 –12.50pp（通过） |

`pool_ready = []`：供给地板 0/3 第一次有了不同于「没货」的解释——**货的日历不合格**。

规则冲突被打印成字段而不是被选择（`gate_conflict.rules_disagree = true`：17.2pp 相位差在
r1411 门死、在年度门活）。两条都说，谁也不退役。

## 自抓的两个坑

1. **部分年不得年化**：2 队列 × 60 bar 线性外推得 –112%，写进披露栏就是邀请别人引用。改为
   只印 cohorts 与 ≈月数（`approx_months_of_evidence`）。门槛本身用原始部分年值（当年已实现的亏
   是真亏），并把「仅整年」的孪生数（`worst_full_only` / `top2_share_full_only`）并排印，避免两数混用。
2. **两条自检断言是我先写错的预期**（不是代码缺陷）：r1414 的 top-2 占比其实是 69.5%（0.6951）
   而非 0.6952；单年书按 Y4（top2=1.0）只能到 CONDITIONAL。**改断言不改阈值**——把 70% 线挪到
   69% 就会把一个真实发现改成一个绿的检查。

## 下一步

- 把 `pool_ready` 接进泊位/供给选择器（当前 0 条，选择器应据实报「无合格候选」而不是空转）。
- 年度轴作为**新宽度候选的前置门**（1414 遗留指针的一半已完成）。
- 剩余未烧泊位：#87 净新高宽度（可用 astock_daily 面板直接算）、#89 协方差收缩（需 core48）、
  #84 拥挤度投票。