# QA — idx_fut_carry_vol_sized_lots（r2110 bm-c）

面名：`results/idx_fut_carry_vol_sized_lots.json`
页面：`research/IDX_FUT_CARRY_VOL_SIZED_LOTS.md`
脚本：`scripts/idx_fut_carry_vol_sized_lots.py`
负控：`results/_r2110bmc_vol_sized_negative.py`

## 1. 问题与答案

**问**：给定 8 % 的风险预算，1 个「1 手 IC + 1 手 IM」价差块需要多少资本？100 万的书实际能开几块？

**答**（evidence cutoff 2026-11-25）：

| 尺子 | 块波动 % | 1 块需要资本（元） | 100 万能开（块） |
|---|---|---|---|
| 声明（ladder 的 4 % / 单位名义） | 8.963 | 1,120,375 | 0.8926 |
| 全样本实测 | 13.636 | 1,704,500 | 0.5867 |
| 120 日滚动中位 | 11.691 | 1,461,375 | 0.6843 |
| 120 日滚动 p95 | 24.546 | 3,068,250 | 0.3259 |
| 120 日滚动 max | 24.704 | 3,088,000 | 0.3238 |

**判词**：`DECLARATION_UNDERSTATES_RISK` / `PRESSURE_BENCHES_THE_BOOK` / `TICKET_EXCEEDS_BUDGET_AT_EVERY_RULER`

**可执行结论**：桌面那张 4 块票，在最乐观的声明尺子上也花 **4.48 倍**预算，压力窗下 **12.27 倍**。历史上 933 个 120 日滚动窗里，只有 **27.97 %** 开得起整 1 块，**0 %** 开得起 2 块——这本书从来没有开满 2 块。

## 2. 清单（charter）

- [x] 有实物：脚本可跑 + JSON 面 + 页面 + 负控，四件入库
- [x] 可复算：`run` 生成、`check` 复算（CHECK_OK 5 rulers / 933 windows）
- [x] 漂移与缺陷用不同词：输入字节变 = STALE（可重建）；同输入数字不符 = CHECK FAILED（不带 STALE）
- [x] 负控全过：`NEGATIVE 20/20 ALL_CONTROLS_PASS`
  - 手改 ruler 数 → rc3 且 CHECK FAILED 且**无** STALE
  - 手改 history → CHECK FAILED
  - 翻判词 → CHECK FAILED
  - 改 inputs sha → rc3 且 STALE 且**无** CHECK FAILED
  - 页面必须印三个判词与跨面状态（面自洽 ≠ 读者可读）
  - 恒等式 `blocks × block_vol == target` 逐尺子成立（8.0004 / 8.0002 / 8.0002 / 7.9995 / 7.9992，容差 1e-3）
  - 复原后字节恒等
- [x] 自检：`--selftest` 15/15 ALL_PASS（腿数为动态计数，r2043 判例）
- [x] 不重建既有量：波动序列 import 自 `idx_fut_carry_ladder_stability`，8 % 目标与 4 块票读自 `idx_fut_carry_sizing_spec`（r1779：选择落成唯一一处数据）
- [x] 跨面对账：stability 面 full-sample 13.636 % 逐位相同（CROSS_FACE_MATCHES）；sizing 面 1 手 1,132,145 元是**另一本书**（IC 用 IF 对冲的残差），已点名不取平均
- [x] 口径边界印在面上：期货块之外（权益袖 / 融资 / 保证金 / 交易成本）不重算，指向 `idx_fut_carry_ladder_risk.json`

## 3. 本轮自捕

1. **页面表头的 `%` 没转义**：`"| 尺子 | 块波动 % | ... | %d 块票 |" % ticket` 直接 `ValueError: unsupported format character '|' at index 13`。r2109 已犯过一次（无格式化 `add()` 里写 `%%`），本窗是它的镜像——**同一张页面上，`%` 的写法取决于这一行走不走格式化**。修法：表头行 `%` 改 `%%`。
2. **自检腿数硬编码**：首版打印 `12/12` 而实际断言 15 条（pin 12 + 三条手写检查）。r2043 判例「腿数报小了也是假读数」——改成动态计数 `state["legs"]`。

## 4. 未做（如实）

- 未接进 `Tools/s6_chain_bmc.py` 与 `smoke_test.py`（两者均为对端未提交脏面，本轮 CONTENTION 禁改共享面）
- 未改 8 % 目标 / 未改桌面票（选择面在 sizing 面，本面只读）
- 未写 state / 心跳（多宿主共写态面，对端持有）
