# QA — 面判词值不值得再烧（r2224）

取证时间 2026-11-28T20:1x+08:00 · 机器 bm-c

## 本条要回答的问题

r2223 把答案簿的「今天卡在：面判词」搬上了 CEO 一页纸。读者接着会问的唯一花得起钱的问题：

> 这一关值得再烧一次吗？

## 本轮的答案（可复跑）

`python scripts/bench_face_verdict_cost.py`

- 17 张已发布的面判词，**17 张不值得再烧同一条配方、0 张值得、0 张本面定不了价**。
- 其中 **1 张根本不是反对证据**：`census_commodity` 的面词 `CENSUS_LEANS_POSITIVE` 被它自己的臂支撑
  （14 臂 2 GO），矛盾面 `bench_census_arm_contradiction.json` 判 `AGREES` —— 缺的是一张票，不是证据。
- `robust_tsmom_commodity` 的 `UNSTABLE_ACROSS_PARAMS` 是真障碍，但它的最弱格 60d 年化 1.52%
  而自己的分辨率线 3.86pp **已细于目标 5pp** —— 测得够，却没有 edge；再烧一遍只会得到第二个负数。
- `census_bond_futures` 是唯一「面比臂乐观」的：headline 说偏正，臂 0/5 GO（矛盾面 `LEANS_WITHOUT_A_PASS`）。
- `census_index_futures` 面与臂一致（`CENSUS_UNPOWERED`，0/20 GO）—— 空间是空的，不是判词打架。
- 只有 2 张面词在算术上「等得起」（`pair_bond_curve_60d` 14.8 年、`trend_single_IC_long` 9.9 年），
  但两者都是 `NO_EDGE`，答案簿已判 EXHAUSTED —— 等数据不是复验计划，所以判词仍为「不值得」。

## 落点

- 新面 `results/bench_face_verdict_cost.json` + `research/BENCH-FACE-VERDICT-COST.md`
- 答案簿「脸级判词」行尾追加一句「复验的价：…」并自印出处（r1781）
- CEO 一页纸 ⑪ 节自动带出（读答案簿），实锚见 `docs/live_usage/LIVE-2026-11-28.md` ⑪
- S6 链新腿 `bench_face_verdict_cost`（在 `bench_verdict_book` **之前**，因为书读它）

## 验证

| 项 | 结果 |
|---|---|
| 新面 selftest | **18/18 PASS** |
| 新面 `--verify` | OK（逐字节，modulo generated） |
| 答案簿 selftest | **41/41 PASS**（+2 腿：带价必须印出处 / 无价不得静默当免费） |
| 链腿族 `--only=bench_face_verdict_cost,bench_verdict_book,ceo_page_answer_book` | **3/3 rc0** |
| 链自检 | 17/17 PASS |
| CEO 页谓词 `ceo_page_answer_book_problems()` | `[]`；负控两条发声（掉价 / blocker 移动） |
| attrition | CLEAN（4 账本 3 历史缩行 healed） |
| 双跑对账 | ZERO-DRIFT 747 条 streak 51 |
| 孤儿面 / 竞争探针 | 0 / CLEAN 单宿主 |

## 诚实边界

- 不复算任何臂、不改任何既有判词；读数全部取自面自己已发布的 `ann_pct` / `mde_pp` / `checks`。
- `years_to_resolve` 是 1/sqrt(T) 的算术外推，前提是数据质量与 edge 不变。
- 二十年计划窗（`MAX_WAIT_YEARS=20`）是本司设定的门槛，不是统计量。
- 「不值得再烧」只针对同一配方；换参数区间是新问题，须另行预注册。
