# DIGEST 2026-11-09 r1476 — 账本 k 喂回票面是一台只降不升的泵（已封）

正身：`scripts/etf_book_order.py::sizing_level`（selftest 114/114，新增 leg51j/51k/51l/51m）
+ `smoke_test.py` 腿「the executable sheet is sized from the account it will trade」
+ `knowledge/METHODOLOGY_ASSETS.md` E483

## 缺陷（r1475 自抓，本轮封口）

r1471 让票面按**执行账**的 k 定规模（不再按引擎那条从没被额度裁过的书）。方向对，但漏了一种
情形：当执行账的那一行正是**本次定价 bar 自己的票**写下的，它是这张票的**结果**，不是它的
**输入**。于是：

```
票面要 k -> 整手向下取整 -> 执行账记下更小的 k -> 下一圈票面按更小的 k 要 ... 
2026-11-06 实测：0.389744 -> 0.389298 -> 0.388680（每圈约 -0.0006，永不收敛）
```

r1474 那天的「票面 k = 账本 k = 0.389744」不是机制保证，是两个数恰好在某一点相遇。

## 修法（三件，缺一不可）

1. `bar == asof` 时拒绝回灌，k 退回规则口径；跨 bar 的执行账仍然是起算基准（那本书真的存在）。
2. 授权口径一次算净：`k = min(规则 k, 额度)`。先按 0.460253 下单再印裁剪表，会让桌面读到
   「卖掉它从来没有的仓位」；改后票面 k 直接 = 0.393073，范围内无裁剪表。
3. 票面必须**印出**本轮用的是哪一条（`rule_same_bar_outcome` / `executed`），并说明为什么。

## 证据（live chain，连跑两圈）

| 圈 | swap_stack k_after | ticket k | ledger k | 结论 |
|---|---|---|---|---|
| 第 1 圈 | 0.392401 | 0.393073 | 0.392401 | — |
| 第 2 圈 | 0.392401 | 0.393073 | 0.392401（kept） | **逐字相等** |

自检腿固定这件事：leg51k 连跑三次同一 bar，k 恒为 `[0.393073, 0.393073, 0.393073]`
（用假账本模拟地板每圈 -0.0006，仍然必须收敛到同一个数）。

## 下游重跑（按链序，全部复绿）

order -> swap_stack -> positions -> rebalance_permission -> cut_order_gap -> cut_gate_pass
-> floor_ledger -> permission_persistence -> decision_line -> live_size_provenance

- positions `--check`：CHECK_OK，unexplained 0 行（改前 PRINTED_ROWS_UNDERSELL_THE_BOOK 3,670.5）
- cut_order_gap `--check` 7/7；live_size_provenance `--check` 8/8；size_rulers_decision
  7 fields 0 mismatch；decision_line：NO_CUT_OWED（k=0.393073 恰在额度上）

## 未验证/未跑

- 全量 smoke：本轮起跑的那套（`results/_smoke_r1476.out`）跑在**改动前**的树上，
  466/475 PASS / 9 FAIL——其中 4 条是别机车道（moneyflow 认证尾巴 / fund_statements 法定期 /
  marks 成因表 / etf_panel+minute_feed 双属主）、3 条是本轮改动的面重跑前读到的旧数（两条已
  由上面的 `--check` 复绿、一条是本轮改写的 smoke 腿本身）。**不宣称全绿**，终态面上重跑
  交由下一轮/S6 链。
- CEO 页（bm-a 执笔）尚未重生，页上现金三档与票面的差属他机车道。