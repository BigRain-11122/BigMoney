# DIGEST · r1455 bm-c · 许可写入执行件（the sheet a desk executes now carries the permission）

- 轮次：1455（开轮 state round_no=1454）｜时间 2026-11-09 01:5x–02:1x ｜部门 dept:交易/工程
- 产品面：`results/etf_book_order/ORDER-2026-11-06.md` 新增「这张单按谁的额度下单」一节；`results/etf_book_cut_order_gap.json` 新增 `permission_enforcers`；两份面由同一处 `trim_legs()` 算术生成。

## 本轮问的问题

r1450 发布了许可（下限 k=0.393073 / 上限 0.544424），r1451 量出票面照旧按 k=0.460253 下单且「没人读许可」，r1453 把三张收据并成一行决策。可是**执行件本身**（人拿着去下单的 `ORDER-*.md`）从头到尾没变过：它印 444/426/794/571/805 手，与「批准额度」那张纸毫无关系。所以本轮问：把许可写进执行件，会改变什么？

## 读数

| 项 | 值 |
|---|---|
| 票面将下单 | k=0.460253（风险腿 ¥460,253） |
| 额度下限 | k=0.393073（¥393,073）｜超出 ¥67,180（6.72pp） |
| 按额度执行（本窗印进票面） | 卖出 65/62/116/84/118 = **445 手 / ¥67,289**，取整后 **k=0.392964** |
| 未采用的读数（票面同印） | window 0.412669（-4.76pp，path）／universe 0.432195（-2.81pp，path）／denominator 0.544424（+8.42pp，static） |
| 审计面判词 | `ORDER_EXCEEDS_PERMISSION_BUT_WIRED`：3 个模块读许可，**其中 1 个真的用它裁剪**（`etf_book_order.py`） |

## 三条发现

1. **「有人读」被当成了「有人做」。** 收据原先把 `permission_readers` 非空直接翻成 `BUT_WIRED`（"the cut is enforced by X"）。可 r1451 之后新增的两个读者 `etf_book_cut_gate_pass` / `etf_book_decision_line` 都是**打印器**：它们读数字是为了写审计面，下单量一分没动。修法=增 `permission_enforcers`（判据=是否调用共用裁剪 `trim_legs`），句子改成「N 个读，其中 M 个用它裁剪」，M=0 时明写 *reading it does not bind the order*。
2. **审计件与执行件必须是同一份算术。** 裁剪原本只存在于审计脚本里，执行面照做就得抄一份（E289 家族）。本窗提成 `trim_legs()` 单实现，两边 import 同一函数；新增 smoke 腿从两份**已发布面**反查（页面与收据的手数/下限不一致即红）。
3. **同一个数在两份面上各有一个名字，读者随手一挑就会读到「未知」。** 第一版读 `etf_book_size_rulers_decision.json` 的 `k_floor`（那份确实有），而真正被审计面消费的是 `etf_book_rebalance_permission.json` 的 `permitted_k`——票面当场印出「缺 k_floor，额度无从对照」。正法=主读被消费的那份，另一份只做交叉校验，不一致印 `PERMISSION_FACES_CONFLICT` 并拒绝宣称「按额度执行」。

## 验证

- `scripts/etf_book_order.py --selftest` **98/98**（新增 leg49a–49f：超额度必印裁剪表且取整后不越界／未采用读数恰为三条且不含额度与现值／额度内无事可卖／缺件=无法核验非合规／小节确实上页面且缺席时不印／两面矛盾印 CONFLICT）
- `scripts/etf_book_cut_order_gap.py --selftest` **12/12**、`--check` **7/7**（新增 L8b 打印器≠执行者、L11 句子不得把打印器称执行者）
- `scripts/etf_book_cut_gate_pass.py --check` 15/15、`scripts/etf_book_decision_line.py --check` 4 字段重算 OK
- S6 定向 8 腿全 rc0：`etf_book_order` 55.2s / `cut_order_gap` / `cut_gate_pass` / `decision_line` / `wrapper_year_gate` / `dualrun`（ZERO-DRIFT 744 entries streak 51）/ `compute_audit` / `py_watermark`
- smoke 新增 2 腿（自检腿 + 已发布面交叉腿），逐条手工执行判据全 True；完整 smoke 未在本窗跑完（下一窗续）

## 未测 / 边界

- 11-11 决策 bar 会**重选名字**，裁剪比例在袖级别成立、逐腿行只对 11-06 选票有效（票面已标 basis）。
- 现金腿只用一个观测到的 GC001 收盘价折算年化，节假日跨期会多计天数。
- 合格判据（年度闸）对裁剪后账簿仍未重跑：k 更小不等于书更好（r1452 已证不改判词）。

正身：`scripts/etf_book_order.py`、`scripts/etf_book_cut_order_gap.py`、方法论卡 E461。