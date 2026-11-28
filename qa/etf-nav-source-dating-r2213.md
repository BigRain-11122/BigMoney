# qa — NAV 定日面：判词与自己的表打架（r2213 bm-c）

## 本轮修的缺陷

`scripts/etf_nav_source_dating.py`（上一窗 11:36 落盘、未收口）判词与自己的表相互矛盾：

- 判词印 `ALL: ... both sit on today's path for the majority (511/512 board, 414/512 sina)`
- 同一张面的计数表印 `board SAME 489 / PREV 1`、`sina SAME 398 / PREV 34`

根因：`_verdict_one()` 把 `OVERSHOOT`（越过当日涨跌）**加进**「在当日路径上」的分子，而
`OVERSHOOT` 按定义就不是当日路径。同一处还把 sina 的 `OVERSHOOT` 计入「滞后」数。
这正是 r2157 族（聚合判词只量了其中一维）：读者拿到一个数字，无法与表对上。

## 修法与新增

1. 判词只把 `SAME_SESSION` 算作「在当日路径上」；越界行按「两源是否互相同意」分三栏
   印数量（`CAPPED_BY_LIMIT` / `AGREED_BEYOND` / `SOURCES_DISAGREE`），逐行入面。
2. 逐行印 `board_t` / `sina_t`（净值在当日价格路径上的位移），并把距最近判据线 <0.05 的
   行单列：513630 在 2026-11-27 的 `t=0.33` 距 `PREV_LINE=0.35` 只有 0.02，标签在这一行
   上做了决定，读者要能看见这个切。
3. `check` 逐行重算 label / 越界桶 / `t`（容差 1e-9），并核对两个分组块与判词都由自己的行
   重新派生；STALE 文案保留（链 `run_leg` 靠这个词付钱补写）。

## 判据与验收

| 检查 | 命令 | 结果 |
|---|---|---|
| 自检（23 腿，含 6 条新行为腿 L14-L19、L21-L23） | `python scripts/etf_nav_source_dating.py selftest` | **23/23 PASS** |
| 全票池重跑 | `python scripts/etf_nav_source_dating.py run --sample 0` | rc0，1,673 行有价 / 1,439 行可判日（42 请求 0 批失败） |
| 面重派生 | `python scripts/etf_nav_source_dating.py check` | **CHECK_OK rows=1673 decidable=1439 board_same=1371 board_prev=8 sina_prev=115 gap_set_rows=53** |
| 判词与表一致 | 同上（`verdict_of` 由行重算后比对） | 通过——判词本次印 `board 1371/1439 ... 115/1439 昨收 ... 59 越界(44 同意/15 不同意)` |
| 链腿注册 | `Tools/s6_chain_bmc.py` 导入 | LEGS=416，末腿 `etf_nav_source_dating`（probe=check / writer=run） |
| 冒烟腿注册 | `smoke_test.py` 语法 + 模块直调 | `ast.parse` OK；`verify()` 直调返回 rc0 |

## 读数的钱面结论

用每只标的自己的价格路径判日（2026-11-27，1,439 只可判）：板面 1,371 站在当日、**8 只站在昨收**；
sina 自印日期的那一面 1,157 当日、**115 只站在昨收**。所以 r2212 的「分母只取带日期源」会把 115 个
陈旧分母装进账本——本轮据此**不采纳**该建议。板面站在昨收的 8 只里 5 只是跨境/商品品种（sina 值比
昨收还旧 1-2 日），其中 **513630 就在 2026-11-27 的票面上**。

## 未验/未做（如实）

- 票面 11 腿里 3 腿（159655 / 513650 / 513500）**板面没有净值行**，本面对不存在的数无从判日；
  要查板面覆盖，不是判据。
- 板面 8 行跨境品种的定日语义要不要在下游溢价面披露成 `nav-cross-date`：本面只提供 `t` 与两源值，
  不改定价（与 r2211 的 159489/159519 修法同族，未接线）。
- 链当前在飞的是 09:04 起的旧腿表（415 腿），新腿（416）要下一次整跑才生效；冒烟腿在板面推进后
  会红到下一次链跑补写为止——这是 r1850 要求的形状（漂移文案自称 STALE），不是缺陷。
- 全量 `smoke_test.py` 未跑（链在飞，~950s）；`knowledge/METHODOLOGY_ASSETS.md` L18125 的 0x08
  仍被 `treasure_guard prescan` 硬拒（rc3），判例卡未能落进去。
