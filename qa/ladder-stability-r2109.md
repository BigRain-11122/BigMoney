# QA — 梯子两个风险常数的稳定性面（r2109）

面 `results/idx_fut_carry_ladder_stability.json` · 页面 `research/IDX_FUT_CARRY_LADDER_STABILITY.md`
脚本 `scripts/idx_fut_carry_ladder_stability.py` · 负控 `results/_r2109bmc_ladder_stability_negative.py`

## 这一轮验证了什么

| 项 | 命令 | 结果 |
|---|---|---|
| 自检 | `python scripts/idx_fut_carry_ladder_stability.py --selftest` | **21/21 PASS** |
| 面自洽 | `python scripts/idx_fut_carry_ladder_stability.py check` | **CHECK_OK**（面与输入一致） |
| 负控 | `python results/_r2109bmc_ladder_stability_negative.py` | **10/10 ALL_CONTROLS_PASS** |
| 重生幂等 | `run` 连跑两次 | 数字逐位相同（唯一漂移=generated 时间戳） |

## 发布读数（证据截止 2022-07-25 → 2026-11-25，1052 个共同交易日）

* 声明块波动 **8.963%**（梯子 `L2_CARRY_VOL=4.0` × (1.154+1.087)）；全样本实测 **13.636%**，少报 **4.67 pp**。
* 120 日滚动：相关 5%→95% 跨 **0.239**（RHO_RANGE_WIDE）；块波动中位 **11.69%**、95% **24.55%**、最大 **24.70%**；**70.4%** 的窗高于声明数。
* 压力下不分散：95% 块波动 / 中位 = **2.10 倍**，95% 相关比中位高 **0.116**（DIVERSIFICATION_DISAPPEARS_IN_STRESS，最同向窗收在 2024-02-07，相关 0.966）。
* 逐年：2023 **6.51%**（在声明数以内）、2024 **21.72%**（声明数的 2.4 倍）、2025 10.97%、2026 12.92%。

## 跨面

`results/idx_fut_carry_ladder_risk.json` 同一档（1/1）的 `l2_vol_measured_pct` = **13.636%**，与本面 `block_vol_full_pct` 逐位相同 → `CROSS_FACE_MATCHES`。兄弟面那一档印的 **10.46%** 已含权益袖；本面的 8.96% 只是期货块，两者不是同一问题的两个答案（已写进页面，读者不会被两个声明数同时告知而无解释）。

## 本轮自捕（两枚）

1. 负控第一版把「荒谬声明数」这条腿写错：`judge()` 的覆盖面读数由 `summarize()` 里算好，测试却先用 0.5 的 summary 再传 1e6 的声明数——是断言错，不是判据错；改成用对应声明数重新 summarize 后转绿。**先跑负控再宣称**再次起作用。
2. 页面第二节表头是无格式化的 `add()`，却写了转义 `%%`，渲染成 `5%%`——页面上肉眼可见的 `%%` 就是「这行不走 % 格式化」的信号。

## 未做（如实）

* 未改梯子常数（`scripts/policy_return_lattice.py` 为共享面，竞争窗禁写）。
* 未接进 `Tools/s6_chain_bmc.py` 与 `smoke_test.py`（两者均为对端未提交脏面；本面暂为 check-only 独立腿）。
* 未覆盖权益袖/融资/保证金/成本（留在 `idx_fut_carry_ladder_risk.json`）。
* 未跑全量冒烟（570+ 腿，竞争窗）。
* `state-bm-c.json` / 心跳未写（多宿主共写态面，对端持有）。
