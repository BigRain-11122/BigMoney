# DIGEST 2026-10-26 · bm-a · accrual 的单季隔离（YTD → 单期）

结论一行：**YTD 累计 accrual 的横截面排名有一半是「期间长度」而不是「应计」**——把流量拆成单季之后，与 YTD 排名的中位秩相关只有 0.6424、Top 十分位重合度中位 0.5019（中位 259 只股票被换出）；24 个月末中有 16 个相关 < 0.9。

## 为什么做这一件

r1113 自己在诚实缺口里留了一句「应计面仍用 YTD 累计未做单季隔离」。这不是文档问题：一季度报表的净利润/经营现金流是从年初累计 3 个月，年报是 12 个月，二者直接做横截面排名等于在排「谁的报告期长」。r1112 的 5,239 只三表交集、r1113 的可用性溯源都没有解决这一层。

## 做了什么（产件，不是散文）

代码面 `scripts/fund_pit_crossface_factor.py`（selftest 14 → 19 腿）：

- `_isolate()`：Q1（3 月期）本身就是单季；其后各期 = 本期累计 − **同一财年**上一份累计；上一份不可得（缺季）或跨年（跳过年报）→ 不做差、标 `quarter_isolated=False`、留 NaN，禁把 6 个月流量当 12 个月。
- `add_quarterly()`：面板每行新增 `q_np` / `q_cf` / `q_prev_period_end` / `quarter_isolated` / `accrual_q` / `accrual_q_rank_pct`。
- `quarter_isolation_grid()`：按「一次模拟多种切法」（r1133 切法轴律）在已建面板上重切，不出第二遍烧录。

## 实测（200 月网格 / 24 月末面板窗口）

| 面 | 读数 |
|---|---|
| 可隔离份额 | 中位 **0.9988**，最低 0.9842（面板 124,681 行里 99.68% 可比） |
| 期间跨度 | 中位 **3.005 个月**（124,265 行 = 3 个月；262 行 12 个月、124 行 6 个月、30 行 9 个月） |
| YTD vs 单季 秩相关 | 中位 **0.6424**，最低 0.583，**24 个月末无一 ≥ 0.9**（16 个 < 0.9） |
| Top 十分位重合 | 中位 **0.5019**，最低 0.4269；中位 **259** 只换出（最多 294） |

读法：可隔离率几乎 100%，所以这不是「数据不够」的问题，而是**旧口径默认把不同跨度放进同一个排名**。任何基于 YTD accrual 的历史读法（含 r1112/r1113 的判词）都应理解为「包含跨度效应的排名」，不应直接当作应计质量排序。禁据此改任何已发布数字（历史不改），只能在新批次用单季列。

## 诚实边界

1. 分母仍用期末总资产（不是期初期末均值）——单季流量配期末存量会有分母错配，未在本轮处理，下一刀候选。
2. `accrual_q` 只在 income 与 cashflow 两侧都可差时非空（124,278/124,681 行）；单侧缺前驱的行留 NaN 并计数，不补。
3. 这是描述性面板，不是新宣称：trial 0、无判据、无 prereg、sample-外盲不变。
4. 12 个月跨度那 262 行的 `q_prev_period_end` 指向跨年前驱，属于「不可差」集合，读 span 分布时必须带 `quarter_isolated` 一起看。

## 复跑

```
python scripts\fund_pit_crossface_factor.py selftest   # 19/19
python scripts\fund_pit_crossface_factor.py run        # -> results\fund_pit_crossface_factor.json
```

产物：`results/fund_pit_crossface_factor.json`（`quarter_isolation.summary` + `.grid`）、`data/fund_statement_export/pit_avail/pit_crossface_monthly.parquet`（gitignored 数据道）。