# QA · policy_trigger_audit · r2103（bm-c）

面：`scripts/policy_trigger_audit.py` → `results/policy_trigger_audit.json`
文档：`research/POLICY_TRIGGER_AUDIT.md`
负控：`results/_r2103bmc_trigger_audit_negative.py`

## 命令与读数

| 检查 | 命令 | 读数 |
|---|---|---|
| 自检 | `python scripts\policy_trigger_audit.py --selftest` | **11/11 PASS**，rc0 |
| 生成 | `python scripts\policy_trigger_audit.py` | verdict=4_TRIGGER_CONTRACT_FINDINGS，rc0 |
| 复查（幂等） | `python scripts\policy_trigger_audit.py --check` | OK，rc0（同一输入→同一判决） |
| 负控 | `python results\_r2103bmc_trigger_audit_negative.py` | **9/9 PASS**，rc0 |

## 负控每条腿证明什么

| 腿 | 污染 | 期望 |
|---|---|---|
| baseline_reports_four | 无 | 基线 4 条发现 |
| single_vol_silences_vol_finding | 文档 §3 的 9% 改成 7% | 目标冲突消失 |
| single_vol_keeps_the_rest | 同上 | 另外三条发现原样保留 |
| wide_cap_silences_notional_finding | 引擎上限 2.5→5.0 | 名义发现消失 |
| composite_feed_silences_drawdown_finding | 阶梯改吃组合净值 | 回撤错量发现消失 |
| quiet_leg_prices_a_smaller_trip_rate | 两条腿波动降到 0.5% | 误伤率 <0.1% |
| written_line_is_priced_at_its_own_number | 无（静腿跑） | 定价用的是文档写的 −2pp，不是缺省值 |
| looser_written_line_silences_finding | 文档线 −2pp → −4.5pp | 太紧发现消失 |
| ic_sigma_by_hand | 无 | σ60 = 年化波动×√(60/252)，手算对齐 |

## 算术复核（手算）

- σ60(IC) = 5.87 × √(60/252) = 5.87 × 0.48795 = **2.864pp**（面里 2.864）
- 漂移(IC) = 8.462 × 60/252 = **2.015pp**（面里 2.015）
- 命中率(−2pp, IC) = Φ((−2 − 2.015)/2.864) = Φ(−1.401) = **0.0805**（面里 0.0805）
- 2.5% 尾线(IC) = 2.015 − 1.959964 × 2.864 = **−3.60pp**（面里 −3.6）
- 合并波动 ρ=0.1：√(4.6²+3.5²+2×0.1×4.6×3.5) = √36.63 = **6.05%**（面里 6.05）
- 名义目标：2,500,000 + 2,258,250 = 4,758,250 ÷ 1,000,000 = **4.758×**（面里 4.7583）

## 诚实边界

1. 文档用正则读：某条改词后变成 `MISSING`（明确红），不会静默通过——但同义词改写也会变成 MISSING，属误报方向。
2. 暂停线的价格是噪声算术（正态、漂移=同窗样本均值），不含移仓/换手路径差，不评估「停一次值多少钱」。
3. 名义发现针对**目标**；今日 lot 受保证金降档保护，实际 2.241× 未越限。
4. 回撤发现只说明阶梯喂的是哪条腿，不重算引擎行为。
5. 相关性取自上游面的 `corr_with_book`，未独立复算日序列。
6. 本面只读：未改策略文档、引擎、`POLICY.json` 或任何共享面。

## 本窗自捕

把文档里的 `−2pp`（U+2212）在 GBK 控制台读成 `?2pp`，先按「占位符」写了一版结论；
负控跑红时用 `ascii()` 核对字节，确认原文是负号。结论由「没写」改判为「写了但太紧」。
