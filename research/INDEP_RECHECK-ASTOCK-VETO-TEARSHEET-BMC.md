# 独立复算：astock_veto 风险面（第二套实现）

generated 2026-11-24T00:5x+08:00 | 机器 bm-c | evidence_cutoff 2026-11-20
被检面：`results/astock_veto_tearsheet.json`　｜　一手序列：`results/astock_veto_lot_drag.json :: rows[]`（77 期）

## 一句话

**用另一套实现（不 import 被检脚本）从父面每期收益重算 12 项风险指标，与已发布数字最大差 1.1e-16，读者页 24 个印出的数字全部对得上 → `INDEP_RECHECK_PASS`。**

## 复算到的东西

| 面 | 口径 | 重算项 | 最大绝对差 |
|---|---|---|---|
| A 分数 | 净收益序列 | 期数/均值/标准差/几何年化/年化波动/夏普/最大回撤/Calmar/胜率/最差期/最好期/最差 6 期/水下占比 | 1.11e-16 |
| B 分数 | 同上 | 同上 | 1.11e-16 |
| A 整手@1千万 | 同上 | 同上 | 0.0 |
| B 整手@1千万 | 同上 | 同上 | 0.0 |

派生边（B−A）：`mean_per_period` = +0.0024283、配对 t = 3.4612、夏普差 = +0.11557、回撤差 = +0.037882 —— 与发布面逐位一致。
辅助恒等式（独立从 rows 重算）：换手均值 A 5.54% / B 23.95%、毛收益均值、每期成本均值 —— 全部对得上。
读者页引用核对：24/24 个印出的数字（夏普 0.38/0.49、回撤 −29.71%/−25.92%、波动 27.61%/27.34%、胜率 55.8%/58.4%、水下 76.6%/74.0%、毛边 +0.2723%、净边 +0.2428%、税占比 10.8%、归零点 73.9bp …）都能从 JSON 派生出来。

## 本轮没做的事（边界）

- **没有重跑选股/否决**：残差排名、top20% 剔除、票池资格都是父面的**输入**，本检查把它们当作给定，只审算术与引用。声称"选股也被独立验证"是不实的。
- 只覆盖 20 交易日一期的**期间净值**，不是日频 mark-to-market（家族从未记日频权重）。
- 现金腿（r2013/r2014 的 GC001 定价）不进本面：它是独立的两张面，本检查不与风险面混算。

## 为什么这值得做

这个家族 r2008–r2015 的 13 张面由同一宿、同一套代码连发，`--selftest` 与负控都是**自证**。R5（独立审计）要求被引用的绝对收益数至少被第二套实现重算过一次——本面第一次做到：同一个数从另一条代码路径走出来，且读者页印的每个数都能回指到产出面（E685 族：打印的数要对到产出那个数的面）。

## 复跑

```
python scripts\indep_recheck_astock_veto_tearsheet_bmc.py --selftest   # 15/15 PASS
python scripts\indep_recheck_astock_veto_tearsheet_bmc.py run          # rc0 → INDEP_RECHECK_PASS
python scripts\indep_recheck_astock_veto_tearsheet_bmc.py check        # 判据不漂移
python scripts\indep_recheck_astock_veto_tearsheet_bmc.py --negative   # 6/6 PASS（篡改一个数必红）
```
证据：`results/indep_recheck_astock_veto_tearsheet.json`

## 未验证（如实）

1. 未接 S6 链腿与冒烟两腿（竞争窗：`Tools/s6_chain_bmc.py`、`smoke_test.py`、`logs/smoke_legs.json` 均是对端在写的共享面）。
2. 未改任何共享面、未递增 state 轮号（本窗为第三宿，对端在跑 r2015 收口）。
3. 容差 1e-9；实测最大差 1.1e-16 是浮点求和顺序噪声，不是口径分歧。
