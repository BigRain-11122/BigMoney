# QA · carry-three-lines-common-window · r2192 (bm-c)

日期：2026-11-27 23:5x +08:00 · 审判面：`results/carry_three_lines_common_window.json`
页面：`research/CARRY_THREE_LINES_COMMON_WINDOW.md` · 脚本：`scripts/carry_three_lines_common_window.py`

## 判据清单

| # | 判据 | 证据 | 结果 |
|---|---|---|---|
| 1 | 面可生成（rc0） | `python scripts\carry_three_lines_common_window.py` → `ORDERING_HOLDS_ON_ONE_CALENDAR` / `THE_EXTRA_DAYS_DO_NOT_BUY_THE_SHARPE`，rc0 | PASS |
| 2 | 自检全绿 | `--selftest` → **22/22 passed** | PASS |
| 3 | 漂移守卫可用 | `--check` → `{"ok": true, "notes": []}` rc0 | PASS |
| 4 | **复现腿 1（同尺证明）** | basis 在父面窗口 2017-01-18..2026-11-25 重放 → 2.972 / 10.069 / 3.2463 / -1.8896 / 2390 bar，逐位 = 已发布 `products.IC.baseline` | MATCH |
| 5 | **复现腿 2（同尺证明）** | 两臂在 2018-10-22..2026-11-20 重放 → 对冲 1.4162、点位 0.5057，逐位 = 已发布 `cells` | MATCH |
| 6 | 复现失败即不发布 | selftest 腿：复现腿失配 → `UNREADABLE`；主程序遇 `UNREADABLE` → exit 2 且不写面 | PASS |
| 7 | 漂移会说 STALE（行为腿） | selftest：改共同窗 Sharpe → rc3 含 `STALE`；改 delta 判词 → rc3 点名 `delta_verdict` | PASS |
| 8 | 自相矛盾不带 STALE（行为腿） | selftest：改 `lines[2].sharpe_at_252` → rc3 含 `CHECK FAILED`、无 `STALE` | PASS |
| 9 | 名次判词有负控 | selftest：basis 压到 0.2 → `ORDERING_FLIPS_WHEN_THE_CALENDAR_MATCHES` | PASS |
| 10 | delta 判词三段有边界腿 | selftest：0.05 / 0.10(边界) / 0.20 / 0.30 / 缺数 五腿 | PASS |
| 11 | 缺数不编 | selftest：<60 bar → `None`；delta 缺 Sharpe → `UNREADABLE` | PASS |
| 12 | 切片两端都含 | selftest：`slice_rows` 逐日均含首尾 | PASS |
| 13 | 点数→% 不造分母 | 只借 `idx_fut_carry_capacity_lots.capital_per_lot_cny`(1,137,862.5) 与 `one_lot_ruler` 每跳金额反推的乘数(200 元/点)；借不到只印点数 | PASS |
| 14 | 零网络零回测 | 只跑本地面板重放（`CS.replay` / `CP.per_lot_daily`），无网络调用 | PASS |
| 15 | 不改任何已发布面 | 新面只写 `results/carry_three_lines_common_window.json` + 本节页面 | PASS |

## 本轮新读数（共同窗 2018-10-22..2026-11-20）

| 线 | bar | Sharpe(252) | Sharpe(244) | 年化均值 | 年化波动 | 回撤 |
|---|---|---|---|---|---|---|
| basis_nominal | 1962 | 3.0693 | **3.0202** | 10.3116% | 3.2677% | -1.8896% |
| excess_hedged | 1961 | **1.4162** | 1.3936 | 503.05 点 | 355.20 点 | -364.16 点（-6.40% 资本） |
| carry_unhedged | 1961 | **0.5057** | 0.4976 | 735.72 点 | 1454.81 点 | -2655.00 点（-46.67% 资本） |

- 被剪掉的 2017-01-18..2018-10-19（425 bar）：Sharpe **2.8072**、CAGR 9.0802%、回撤 -1.201%
- 去掉锚日切片（1961 bar，与两臂同口径）：basis Sharpe **3.0045**
- 年化天数口径不一致：basis 244 天、两臂 252 天，比值 1.0163

## 结论（三条）

1. r2191 的混窗是**呈现缺陷，不是数字缺陷**：剪到共同窗后 basis 反而是 3.02 > 2.972，多出的 425 bar 自己也有 2.81，既没抬也没压。
2. 三条读数现在同一天历，名次 basis > 对冲 > 点位 不变（`ORDERING_HOLDS_ON_ONE_CALENDAR`）。
3. **对冲买的是什么**第一次有了数：不带对冲的每手回撤 -2655 点（-46.67% 一手资本），对冲后 -364 点（-6.40%）——用年化均值从 735.7 点降到 503.1 点换来的。

## 已知未覆盖（如实）

1. **无链腿、无冒烟腿** —— 本轮 `repo_write_contention` rc=3 CONTENTION（对端 interactive pid 30500 自 21:54 存活），禁改 `Tools/s6_chain_bmc.py` / `smoke_test.py`；挂账进 carrier_debt。
2. 全量冒烟与 S6 链本轮未跑（同上，且对端 22:5x 已在跑一套 `results/_smoke_r2191.*`）。
3. 两臂仍无 CAGR（点数→复合增长需要一个账户与不中断滚仓的假设，本面不代读者假定）。
4. `open_capital` 印的 `per_lot_vol_cny_hedged`=91,029 与本面 71,040 不同窗，已并列披露，未仲裁。
