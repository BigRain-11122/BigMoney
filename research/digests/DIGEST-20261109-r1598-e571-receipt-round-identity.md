# DIGEST r1598 bm-b · E571 回执轮号身份

**卡**：E571-WHICH-ROUND-A-RECEIPT-BELONGS-TO-WHEN-ITS-ROUND-FIELD-DISAGREES-WITH-ITS-NAME
**面**：results/state_tilt/RECEIPTROUNDCONF-2026-11-08.json + receiptroundconf_latest.json
**代码**：scripts/e571_receipt_round_identity.py（build/check/verify/selftest 7/7）
**接线**：S6 腿 `receipt_round_identity`（rc=0 0.13s）+ smoke 腿 scripts/run_e571_smoke_leg.py（--doctor 拒改）

## 回答

E561 数出 17 份回执的 `round` 字段与文件名里的轮号不一致。本轮把它拆开：

| 项 | 值 |
|---|---|
| 回执总数 | 328 |
| 写了轮号字段 | 243 |
| **值不一致** | **0** |
| 值一致（归一后） | 238 |
| 值不可归一 | 5 |
| 无轮号字段 | 61 |

方言分布：`int`=12、十进制字符串=210、`rNNNN` 标签=16、自由文本=5。
**231/243 会被「按 int 查表」的读者漏掉。**

自由文本 5 份：`round='r848 bm-a'`、`'r1483leg'`、`'run'`、`'spread_floor'`、`'verify'` —— 后三份是写进活目录的临时测试件（`_rrunbmb`、`_rspread_floorbmb`、`_rverifybmb`），与 E562 的「测试轮号写真实回执」同族。

## 结论

那 17 份「不一致」在值层面是 0，**全是类型方言**。方言不需要 ts/commit 见证（没有真相之争），所以卡里那条「用 payload 的 ts 对照候选轮的提交时间」的臂诚实地没有跑：需见证的人群=0。

## 同窗修复（红色项）

链每跑一次就往 `results/` 追加一份回执，而 E569 的 `check` 拿「全目录」比「发布面」，因此 r1596/r1597 各自写了一份之后它每轮必红——**本轮开局实测 `chain_numerator` CHECK FAIL**。E570 的卡在 r1596 已写下这条规律（「回执目录是活的，check 只门增长不门恒等」），但没有接进那条更老的腿。

正法（本轮落地两份）：`check` 按**文件名钉住发布人口**，只对发布面里的文件重新导数；新到的回执记 note（重建再扩），消失才是故障。E569 同法修复 → red 变 green（328 份 / 227 写计数 / 227 全对 / 38 join / 35 相等 3 不等）。

## 方法学记录

E571 卡（knowledge/METHODOLOGY_ASSETS.md）：①「不一致」必须带单位（值 vs 类型，同一批 17 份两种判法）；②只有值分歧才需要外部见证；③方言分布必须与一致率同时发布；④测人口的腿会被人口写红——规律写进卡不等于接进代码。