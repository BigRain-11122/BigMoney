# QA — r2114 等风险重配的整手地板与 ADV 上限（bm-c）

日期 2026-11-26 | 面 `results/idx_fut_carry_rebudget_floor.json` | 页 `research/IDX_FUT_CARRY_REBUDGET_FLOOR.md` | 脚本 `scripts/idx_fut_carry_rebudget_floor.py`

## 这一面回答什么

r2113 判「等风险重配会让夏普 +0.208」，但没说那套权重能不能被持有。本面把两个端点都算出来：

- **下限**＝每条带权重的期货腿能持有一整手的 NAV（`每手名义额 / 权重`）；
- **上限**＝权益袖权重碰到 1% ADV 线时的 NAV（`容量线资本 / 权益权重`）。

两个数来自既有的两张面（`idx_fut_carry_margin` 的每手名义额、`etf_book_capacity_edge` 的 60 个 session 容量读数），本面不重算它们。

## 读数（2026-11-25 收盘口径）

| 权重集（档 1/1） | 权益袖 | 下限 NAV | 上限 NAV（今日 / 中位 / 最差） | 判决 |
|---|---:|---:|---|---|
| 现在这套 | 0.4347 | 1,000,000 | 2,401,198 / 1,142,112 / 784,076 | WINDOW_OPEN |
| 等风险重配 | 1.0000 | **2,789,167**（约束腿 IM） | **1,043,801** / 496,476 / 340,838 | **FLOOR_ABOVE_CAPACITY** |

- 重配的下限是今日上限的 **2.67 倍**：两条期货腿要 2.79M 才够各开 1 手，而权益袖 1.000×NAV 在 1.04M 就已经顶到 1% ADV 线。
- 同一资本上把窗口打开的最小改动：权益袖权重压到 **≤ 0.3742×NAV**。
- 权益袖那一端的历史分布很宽：同样的「满仓权益」在 60 个 session 里能装的资本从 34.1 万到 104.4 万（中位 49.6 万），所以窗口的上端不是一个常数。

## 证据

- `python scripts/idx_fut_carry_rebudget_floor.py --selftest` → **19 legs, 0 failed**
- `python scripts/idx_fut_carry_rebudget_floor.py check` → **CHECK_OK**（输入 sha 漂移说 STALE；同输入数字不符说 CHECK FAILED 且不带 STALE；页面不能从发布面重渲染也说 STALE）
- `python results/_r2114bmc_floor_negative.py` → **25 controls, ALL_CONTROLS_PASS**（含：手改窗口数字→CHECK FAILED 无 STALE／改输入 sha→STALE／改页面→STALE／复原→绿／页面无字面 `%%`／每手名义额与保证金面逐位相同／中位口径与容量面同为「上中位」）
- 页面经 `python Tools/page_fmt_guard.py scan`：本文件零命中（仓内其它面的 31 处历史 `%%` 仍是欠账）

## 跨面对账

- 容量面摘要 vs 本面从 `sessions` 重算：**CROSS_FACE_MATCHES**（中位 496,476 = 496,476，最差 340,838 = 340,838）。
- `idx_fut_carry_open_capital` 的首档（IC 1,132,145 / IM 1,161,161）读的是「每手波动 ÷ 8% 预算」这把尺子，与每手名义额（1,153,800 / 1,086,880）比值 0.9812 / 1.0683 —— **DIFFERENT_RULER_NAMED**，两个数不取平均。

## 本轮自捕两枚

1. 中位数首版用「两个中间值的平均」（492,295.89），而容量面自己用的是**上中位**（496,475.93）——同一批 60 个 session 上两个估计量会印成两个答案（r1911 族）。改成沿用上游定义并在源码注释里写清来历。
2. 自检里断言页面报红时输出含 "page"，而实际文案是 "does not re-render from the published face"——是断言写错不是判据错，改断言不放松判据。

## 未做（如实）

- 未接进 `Tools/s6_chain_bmc.py` 与 `smoke_test.py`：`Tools/s6_chain_bmc.py` 在本窗开工时已是**对端未提交的脏面**（+45 行新腿），本窗不改共享面。
- 未改 r2113 的重配权重（选择在 r2113 那面），本面只回答「能不能持有」。
- 权益容量只覆盖容量面自己的五个名字；更宽的票池会抬高上限，本面只声明方向不猜数值。
- 全量冒烟未跑（本窗时长），如实记未验证。
