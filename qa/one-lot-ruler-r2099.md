# QA — 一手资本的跨面核对面（r2099 bm-c）

对象：`scripts/idx_fut_carry_one_lot_ruler.py`
产物：`results/idx_fut_carry_one_lot_ruler.json`、`research/IDX_FUT_CARRY_ONE_LOT_RULER.md`
负控：`results/_r2099bmc_one_lot_ruler_negative.py`

## 1. 问题是否真存在（不是自己造的）

| 面 | 生成时点 | 印的 IC 一手 | 印的 IM 一手 |
|---|---|---|---|
| sizing_spec / open_capital / always_on_price | 2026-11-25T20:30 | 1,132,145.38 | 1,161,161.25 |
| decision_face / capacity_lots | 2026-11-25T20:30 | 1,132,145.38 | 1,161,161.25 |
| forward_clock | 2026-11-23T06:49 | 1,124,479.00 | 1,152,596.00 |
| portfolio_capital | 2026-11-23T17:39 | 1,124,479.00 | 1,152,596.00 |
| tradeable_hedge_capital | 2026-11-23T19:44 | 1,124,478.99 | 1,152,595.98 |

差额：IC 7,666.38 元/手、IM 8,565.25 元/手。读者在两页上看到「差 124,479 元」与「差 129,566 元」——
同一句话、两个数，两页都没说自己属于哪一代。**这是钱数级的面代差，不是文风问题。**

## 2. 判据是否可机械执行

- 归因按**生成时刻**：consumer.generated < authority.generated 且数不同 → `STALE_BY_GENERATION`；
  不早于权威面仍不同 → `DISAGREE`（同输入两答案，需人）。
- 金额容差 0.01 元（这些面存到分；1e-9 会让自家面先红，r1935 教训）。
- 缺面/缺字段 → `DATA_BLOCKED`，不默认为 0（r98 族）。
- 只有 STALE 分支说 "STALE" 这个词（r1850/r1934 链腿合同：链只在这个词上付重建费）。

## 3. 证据

| 项目 | 命令 | 结果 |
|---|---|---|
| 自检 | `python scripts\idx_fut_carry_one_lot_ruler.py --selftest` | **11/11 PASS** |
| 负控 | `python results\_r2099bmc_one_lot_ruler_negative.py` | **12/12 PASS** |
| 自查 | `python scripts\idx_fut_carry_one_lot_ruler.py check` | **CHECK_OK rc0**（10 consumers, CONSUMERS_ONE_GENERATION_BEHIND） |
| 首次发布 | `python scripts\idx_fut_carry_one_lot_ruler.py run --write` | verdict CONSUMERS_ONE_GENERATION_BEHIND、重建清单 3 件 |

负控覆盖：手改数字（CHECK FAILED 且不含 STALE）／输入字节动（STALE）／verdict 翻面／
丢一行消费者／页面块被手改（rc3）／权威面差 1 元（点名到品种）／差 0.005 元不报警／
`+08:00` 与 `+0800` 两种时间戳解析相等／投影只做算术／重建清单与实际 stale 面逐一相等。

## 4. 本轮没做（如实）

- **没有重生那三张 11-23 的面**：本轮竞争探针 rc3 CONTENTION（三个 interactive 宿主在动共享面、
  工作树脏 1,946 件），按 r1907 律只落新增文件面。重生是下一步（本面的 rebuild_list 就是工单）。
- 没有接线到 `Tools/s6_chain_bmc.py` 或 `smoke_test.py`——两者都是对端未提交脏面。
  本面目前是一条 **check-only 的独立腿**，下一无冲突轮再接（≤48h）。
- 投影（floor 2,277,075 → 2,293,306.63；IC 一手 P&L 占比 −8.4128% → −8.3555%）标注
  `arithmetic_only`，不是重算面；重生后应以新面逐字核对。
