# QA — idx_fut_carry_roll_step_reversal (r2096 bm-c)

日期 2026-11-25 · 机 bm-c · 窗：竞争窗（对端 interactive 宿主 pid 93460 在写共享面）

## 完成判据（本司清单）

| 项 | 结果 | 证据 |
|---|---|---|
| 脚本可跑且确定性（同输入同输出） | PASS | `--check` rc0（见下） |
| 自检覆盖判词正反两面 | PASS | `--selftest` **12/12**，含 JUMP / REAL_COST / BOOKED_LATER 三条判词腿与 `give` 边界腿 |
| 判据在跑之前冻结 | PASS | 判据写在脚本 docstring 与 `criteria` 字段，未看数后改 |
| 缺数据不崩、诚实报 BLOCKED | PASS | published 掩码 22/18 对 → `DATA_BLOCKED`（未放宽 30 对门槛） |
| 零分布方法本身经自检 | PASS | 「置换 p 在噪声上不假阳」腿；跨样本零分布被台阶后位移污染 → 改配对符号翻转（首版实测 -0.38pp 自我抵消，已废弃） |
| 复用原件不重实现 | PASS | `idx_fut_basis`（basis/spread/roll）+ `idx_fut_roll_gap.calendar_rolls`；权重/曲线一律未碰 |
| 只读、不写共享面 | PASS | 仅写新面 `results/idx_fut_carry_roll_step_reversal.json` + 本文档 |
| 结论可查 | PASS | 每个判词带 pairs / give / T / p / after-before / p 六项读数 |

## 实跑

```
python scripts/idx_fut_carry_roll_step_reversal.py
VERDICT MIXED_BY_PRODUCT  cutoff=2026-11-24
  IC/published: DATA_BLOCKED (drop=22)
  IC/calendar : T=+21.685pp p=0.0026 give=0.170 after-before=-3.964pp p=0.026 → COST_BOOKED_BY_LATER_CARRY
  IC/strictest: T=+17.315pp p=0.0024 give=0.159 after-before=-5.287pp p=0.030 → COST_BOOKED_BY_LATER_CARRY
  IM/published: DATA_BLOCKED (drop=18)
  IM/calendar : T=+38.014pp p=0.0020 give=0.218 after-before=-1.756pp p=0.607 → PARTIAL_REVERSAL
  IM/strictest: T=+1.888pp  p=0.4213 give=0.073 after-before=-5.569pp p=0.252 → REAL_COST
```

## 已知限制

- IM 只有 1,051 根 bar（51-60 个移仓日），后前差 p 不显著 → 判词 `MIXED_BY_PRODUCT` 读作"IM 未测够"。
- 后付窗固定 8 日（21 日窗在每月移仓节奏下前后互叠，实测自抵消 −0.38pp）。
- 无链腿、无冒烟腿（竞争窗禁改 `Tools/s6_chain_bmc.py` 与 `smoke_test.py`）。
