# 货币 ETF 的「收益」里有一半是溢价

> 面 ID：`money_premium_carry_audit/v1`
> 正身：`scripts/money_premium_carry_audit.py` · 数据面：`results/money_premium_carry_audit.json`
> 上游：`results/cash_shelf_flip_census.json`（r2048 命名的 11 只）· `results/cash_shelf_year_by_year.json`（五货架）
> 窗口：2020-07-16 .. 2026-11-20（r2048 自己的窗口）

## 一、为什么要有这一面

r2048 的翻转普查给「11 只真货币 ETF 日 σ 25-55bp（货币基金应在 1-2bp）」打了一个标签
`MONEY_SERIES_CARRIES_UNCAUGHT_JUMPS`，但没有定价。r2049 把它记成欠账。这一面就是那笔账。

形状不是 r2046 的那一对。r2046 修的是「一根深跌 + 几天回到原价」——而现行的货币读器
`etf_book_cash_vehicle.consolidation_returns` 已经把所有跌幅超过 50bp 的 bar 记成零，
**向下的打印是被抓住的**。没被抓住的是它的镜像：

511770 在 2025-02-10 / 02-11 / 02-12 连续打印 110.000 / 118.900 / 107.010（面值 100），
02-13 回到 100.007。三根 7%-19% 的溢价 bar 里，**只有结束这一段的那根被读器归零**，
溢价本身留在序列里当成了收益。

所以问题不是「有没有坏打印」，而是：**一个 carry 口径欠它多少**——停现金的人不会去收 19% 的溢价，
货币基金也不会三个交易日赚 19%。

## 二、口径（跑之前就冻结）

| 项 | 取法 |
|---|---|
| 窗口 | r2048 的 `window.start .. window.end` |
| 面板与读器 | `etf_book_cash_vehicle.load_etf` + `consolidation_returns`（>50bp 跌幅归零，溢价 bar 保留） |
| 年化 / σ | `cash_shelf_flip_census.cagr_from_rets` / `sigma_bp`（r2048 发布时用的同两个函数） |
| 宇宙 | r2048 的 `universe.money_sigma_over_25bp`，逐只复现（σ 差 > 0.1bp 即拒绝出面） |
| **局部水平**（本面新增） | 收盘价的 20 日滚动中位数，最少 10 根 |
| **BAND_PCT = 1.0%**（本面新增） | 货币基金每天约 accrual 0.008%，1% ≈ 125 个交易日的 carry；离自己的局部水平这么远的 bar 不是这只标的的 carry |
| 修复 | 越界 bar 的收益记成恰好零；结束一段的那根通常已经跌 > 50bp 被读器归零，所以一段净额归零而不是凭空多出一笔 |

本面**不计建仓成本、不主张任何可交易收益**，也不改动任何已发布的货架数字。

## 三、判词（机械）

- `PREMIUM_IS_NOT_CARRY`：配对中位的 carry 缩减 ≥ 1.00pp/年
- `CARRY_IS_MILDLY_INFLATED`：0.25 ≤ 缩减 < 1.00pp/年
- `CARRY_IS_A_CARRY`：缩减 < 0.25pp/年

标签（与判词并列印，不折进判词）：
`THE_BOOK_LEGS_ARE_CLEAN`（五货架的货币/债券腿全都 < 0.25pp 缩减 → 已发布的货架数字站得住）·
`EVERY_NAMED_INSTRUMENT_BREACHES` · `EPISODES_ARE_MULTI_BAR` ·
`A_BREACH_CAN_MULTIPLE_THE_CARRY`（最大缩减 ≥ 修复后的 carry 本身）。

## 四、读数

<!-- PREMIUM-TABLE:BEGIN -->
| code | name | bars | episodes | breach bars | max dev | printed %/yr | repaired %/yr | carry lost (pp) | sigma printed -> repaired (bp) |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| 511600 | 华安日日鑫ETF | 1537 | 5 | 5 | 7.99% | 3.25 | 0.34 | 2.91 | 25.6 -> 5.4 |
| 511620 | 货币ETF国泰 | 1364 | 4 | 4 | 9.99% | 2.45 | -0.02 | 2.47 | 27.3 -> 4.1 |
| 511670 | 华泰天天金ETF | 1207 | 5 | 8 | 17.00% | 5.63 | 0.04 | 5.59 | 40.4 -> 5.2 |
| 511770 | 金鹰增益货币ETF | 1204 | 7 | 10 | 18.90% | 8.44 | 0.62 | 7.83 | 54.7 -> 9.5 |
| 511820 | 鹏华添利ETF | 1382 | 3 | 3 | 9.86% | 2.48 | 0.72 | 1.76 | 29.5 -> 12.3 |
| 511910 | 融通货币ETF | 1045 | 3 | 4 | 9.55% | 3.07 | 0.40 | 2.67 | 30.5 -> 7.7 |
| 511920 | 货币ETF广发 | 1461 | 3 | 5 | 9.01% | 4.34 | 1.88 | 2.46 | 36.9 -> 26.6 |
| 511930 | 货币ETF国联 | 1193 | 4 | 7 | 9.98% | 5.41 | 2.65 | 2.76 | 39.2 -> 31.4 |
| 511950 | 添利货币ETF广发 | 1190 | 10 | 10 | 9.95% | 5.08 | 1.36 | 3.72 | 34.8 -> 12.4 |
| 511960 | 货币ETF嘉实 | 1228 | 5 | 10 | 14.53% | 4.76 | 0.54 | 4.23 | 35.0 -> 7.0 |
| 511970 | 国寿货币ETF | 1053 | 4 | 7 | 13.76% | 5.25 | 0.73 | 4.52 | 45.2 -> 9.4 |

Book legs (control) — `carry` says whether the band ruler applies to this leg:

| code | class | carry | name | episodes | max dev | printed %/yr | repaired %/yr | carry lost (pp) |
|---|---|---|---|---:|---:|---:|---:|---:|
| 511380 | convertible | NO | 可转债ETF博时 | 135 | 9.16% | 50.57 | 18.22 | 32.35 |
| 511180 | convertible | NO | 可转债ETF海富通 | 118 | 6.70% | 27.12 | 12.35 | 14.77 |
| 511880 | money | yes | 银华日利ETF | 6 | 1.99% | 1.53 | 1.50 | 0.03 |
| 511360 | money | yes | 短融ETF海富通 | 1 | 1.03% | 2.32 | 2.32 | 0.00 |
| 511010 | bond | yes | 国债ETF国泰 | 3 | 1.08% | 2.62 | 2.53 | 0.09 |
<!-- PREMIUM-TABLE:END -->

## 五、怎么读

1. **先看书腿**：五货架自己的货币腿（511880 / 511360）与债券腿（511010）缩减都远小于 0.25pp——
   r2042 起的「几天还本」表建在干净的腿上，那批数字不需要重算。这是本面最重要的一句，
   因为它是「不用重做」的结论。
2. **再看被点名的 11 只**：它们不是货架成员，但它们是同一家族里被拿来做现金腿的候选。
   谁把其中任意一只当 carry 用，谁就继承了 2-6 倍的假收益。
3. **σ 前后一起印**：25-55bp 的 σ 在修复后不是掉到 1-2bp 就完事——剩下的方差说明
   还有别的形状（多段阶梯、慢回复）没被两条规则抓住，这一点本面只点明，不宣称已清。

## 六、不主张（如实）

1. 面板分不清「真的溢价挤压」和「坏打印」——两者都是「离水平很远又回来」。对 carry 口径它们是同一个问题，
   本面不宣称能区分。
2. 溢价不可收获（没有先见之明），所以本面不算任何可交易收益。
3. 不改 r2048 的分类器：28 只「现金流 ETF」被判成货币这件事仍记在 r2048 名下。
4. 只覆盖「离局部水平 > 1% 的连续段」一种形状；慢回复、单边漂移不在射程。

## 七、复跑

```bash
python scripts/money_premium_carry_audit.py run        # 重建面 + 渲染本页表格
python scripts/money_premium_carry_audit.py --check    # 重 derive 对账（漂移自称 STALE）
python scripts/money_premium_carry_audit.py --selftest # 10 条离线自检
```
