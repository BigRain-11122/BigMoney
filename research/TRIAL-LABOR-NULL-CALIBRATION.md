# TRIAL-LABOR 四波 null 校准审计

> 生成：`scripts/trial_labor_null_calibration.py run` ｜ 证据截止：2026-09-22 ｜ 判词：**BAND_AND_BAR_MEASURE_DIFFERENT_NULLS**

## 一句话

W20 的及格线（0.417438）和它的预测带（[0.50,0.53]）量的不是同一个零假设：带子的值是 **641/1253 = 0.511572**——一个从不交易的仓位；线子是一个真在交易的随机入场 null。两者之间差的 9.4pp 不是校准失败，是 null 自己的换手成本。

## 五条读数

| 波 | null 行 | beat6m 不同取值 | 众数占比 | 众数值 | 发行 p95 | 带内 | 格中位换手 | 格数 | 存活 |
|---|---|---|---|---|---|---|---|---|---|
| w17 | 200 | 3 | 0.985 | 0.511572 | 0.511572 | True | 10 | 1384 | 332 |
| w18 | 200 | 7 | 0.965 | 0.511572 | 0.511572 | True | 10 | 692 | 152 |
| w19 | 200 | 6 | 0.965 | 0.511572 | 0.511572 | True | 6 | 346 | 70 |
| w20 | 200 | 165 | 0.020 | 0.141261 | 0.417438 | False | 929 | 31 | 14 |

对照臂（重派生每条已发布存活数，4/4 逐位相等）：w17 332==332；w18 152==152；w19 70==70；w20 14==14

1. **`null_p95_band_hit=true` 在 W17..W19 结构上不可能为假。** 200 个 null 里 197/193/193 个落在同一个值上，p95 就等于那个值；而那个值是面板常数（k/n），换哪一波都不动。
2. **W20 是第一次 null 真在交易。** 165 个不同取值、换手 1162..2134、均值 0.2678；代价曲线 beat6m ≈ 0.5498 -17.1pp/千次换手（corr -0.729）。
3. **同一个 31 格，两条线两个答案。** 对着 band 自己的 null，存活 6/31 = 19.4%（**落在预注册的 15..40% 带内**）；对着已发布的线，14/31 = 45.2%。
4. **14 个存活里有 12 个站在 null 没有覆盖的换手区间。** null 换手 1162..2134，31 格里只有 11 格在区间内（另 19 格低于下沿、1 格高于上沿）；存活者的分布是 区间内 2 / 区间下 12。
5. **这不是阈值噪声。** 重抽 200 个 null 2000 次，p95 只有 0.4046..0.4233，诱导存活数 11..16；落进预注册 cell 带的占比 **1.1%**——45.2% 稳定地站在带外，所以问题在线本身，不在抽样抖动。

## 族级两面

| fn 族 | 格数 | 已发布线（0.417438） | band 自己的线（0.511572） | 两线都过 |
|---|---|---|---|---|
| dd_rung_entry | 13 | 6 | 5 | 5 |
| near_52w_high | 6 | 6 | 1 | 1 |
| turnover_regime | 12 | 2 | 0 | 0 |

`near_52w_high` 在已发布面里是 6/6 = 100%，对着 band 自己的那条线只剩 1/6——「完美命中」是线的产物，不是族的本事。

## 阈值阶梯（同一批 31 格）

| 线 | 阈值 | 存活 | 存活率 | 在预注册 cell 带内 |
|---|---|---|---|---|
| observed_null_p95 | 0.417438 | 14 | 0.4516 | False |
| observed_null_p99 | 0.449346 | 10 | 0.3226 | True |
| observed_null_max | 0.460495 | 10 | 0.3226 | True |
| prereg_band_lo | 0.500000 | 6 | 0.1935 | True |
| do_nothing_rate | 0.511572 | 6 | 0.1935 | True |
| prereg_band_mid | 0.515000 | 6 | 0.1935 | True |
| prereg_band_hi | 0.530000 | 6 | 0.1935 | True |

## 换手匹配读数（只在实测区间里下判断）

| 区域 | 格数 | 匹配线过 | 已发布线过 |
|---|---|---|---|
| 实测区间（1162..2134） | 11 | 3 | 2 |
| 外推区间（< 1162） | 19 | 12 | 12 |

外推区间没有实测线，唯一诚实的下界取最低换手那端 25 个 null 的 p95 = **0.433998**（已发布线 0.417438），斜率符号说明真值还应更高；所以那一区的 12 个存活不能被当成已验证。

近邻匹配（k=25 个最近换手的 null）翻面的格：

- `W20-B-0023`（turnover_regime，换手 1857，rate 0.3320）：本地线 0.2742 → LOCAL_PASS_POOLED_FAIL

## 阈值噪声（重抽 200 个 null，2000 次）

p95 的 5%/50%/95% 分位 = 0.4046 / 0.4174 / 0.4233；诱导存活数 min 11 / p05 14 / p50 14 / p95 15 / max 16；落在预注册 cell 带内的重抽占比 **1.1%**，存活数 ≥ 已发布 14 的重抽占比 **96.2%**。

## 为什么重要

the W20 bar and the W20 band are two different nulls: the band is 641/1253 (a position that never trades) and the bar is a random-entry null that pays cost. Beat rate falls 17.1 pp per 1000 trades (corr -0.73), so a bar measured on nulls trading 1162..2134 is not the bar a cell trading 929 should clear. Against the band's own null W20 keeps 6/31 = 19.4% (inside the prereg's 15..40% band); against the published bar it keeps 14/31 = 45.2%. 12 of the 14 survivors live below the nulls' smallest turnover, i.e. where the bar is extrapolated and -- by the sign of the cost curve -- too lenient.

## 没有测的事（如实）

- the nulls do not exist below 1162 trades, so no turnover-matched bar can be measured for 19 of 31 cells -- this face names the gap instead of extrapolating a verdict from it
- beat6m is a window count, not money: nothing here says which survivor would earn anything
- the reform gate that admitted W20-A-0003 / W20-B-0019 is a separate face (TRIAL-LABOR-DIRECTION-AUDIT.md); both fail both bars here

## 输入面（字节门）

- `results/trial_labor_w17/w17_screen_cells.csv` sha256_16=e9f41f3ae9efbe44
- `results/trial_labor_w17/w17_screen.json` sha256_16=386651a5b51e745e
- `results/trial_labor_w18/w18_screen_cells.csv` sha256_16=de94b0eaa34c7a52
- `results/trial_labor_w18/w18_screen.json` sha256_16=67fe7541a184906b
- `results/trial_labor_w19/w19_screen_cells.csv` sha256_16=3584caac0fa791c9
- `results/trial_labor_w19/w19_screen.json` sha256_16=d2b4f79eeb211a1a
- `results/trial_labor_w20/w20_screen_cells.csv` sha256_16=45d30813e1a5f720
- `results/trial_labor_w20/w20_screen.json` sha256_16=86f1a64e8b4987f3

