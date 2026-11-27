# 一本书，一张决定面

四张面各自回答了一个子问题，没有一张回答「今天这本书做什么」。本面把决定写在唯一一处，
其余各面只读它（r1266：没有字面消费面的裁决不算裁决）。

> 本文件由 `python scripts/idx_fut_carry_decision_face.py run` 生成，**不要手改**。生成时刻 2026-11-27T02:33:51+0800，证据截止 2026-11-24。

## 判词

`NO_ORDER_ON_BOTH_LEGS`

**NO_ORDER_ON_BOTH_LEGS -- IC 口径已定（9.65-9.68%）但本金差 137,862 元；IM 无口径（无可采信尺子）**

## 尺子准入（本面唯一的新东西）

a ruler may be quoted only if the roll-step face says its roll-day accounting is supported (COST_BOOKED_BY_LATER_CARRY)

### IC -- `NO_ORDER_CAPITAL_BELOW_FIRST_RUNG`

- 为什么：会计口径已定，但本金买不到一手首档
- 可报区间：**9.65% – 9.68%** 年化（区间内差 0.030pp）
- 相对停车的净超额：**109,278 – 109,625 元/年**
- 本金：一档 1,137,862 元，账面 1,000,000 元，差 137,862 元
- 容量：468.45 手（1% ADV 线）
- 准入前那张面给的区间：2.76% – 9.68%，差 6.92 pp

| 尺子 | 判词 | 年化 |
| --- | --- | --- |
| calendar | 采信 | 9.65% |
| strictest | 采信 | 9.68% |
| published | DATA_BLOCKED（不采信） | — |

- 会改判的条件：capital at the first executable rung
    - today_cny: 1,000,000.00
    - needed_cny: 1,137,862.50
    - gap_cny: 137,862.50
    - gap_pct_of_book: 13.79

### IM -- `NO_ORDER_ACCOUNTING_UNSETTLED`

- 为什么：这个品种没有任何一把尺子的移仓日会计被采信，所以连一个年化都不该报
- 可报区间：**无可报数**（口径未定）
- 相对停车的净超额：不报（无口径）
- 本金：一档 1,165,749 元，账面 1,000,000 元，差 165,749 元
- 容量：752.15 手（1% ADV 线）
- 准入前那张面给的区间：5.74% – 11.96%，差 6.22 pp

| 尺子 | 判词 | 年化 |
| --- | --- | --- |
| calendar | PARTIAL_REVERSAL（不采信） | — |
| published | DATA_BLOCKED（不采信） | — |
| strictest | REAL_COST（不采信） | — |

- 会改判的条件：this product needs at least one ruler whose roll-day accounting is supported
    - needed: COST_BOOKED_BY_LATER_CARRY
    - today: calendar=PARTIAL_REVERSAL; published=DATA_BLOCKED; strictest=REAL_COST
    - note: the sample is not the problem (calendar=51 pairs, strictest=60 pairs clear the face's own min_pairs=30); what has to change is the reading itself, which is why no amount of money today moves this gate
- 会改判的条件：capital at the first executable rung
    - today_cny: 1,000,000.00
    - needed_cny: 1,165,749.12
    - gap_cny: 165,749.12
    - gap_pct_of_book: 16.57

## 本面不重算的东西

- every rate, every CNY figure and every lots figure (they belong to the four faces)
- the roll-step verdicts themselves (results/idx_fut_carry_roll_step_reversal.json)
- the desk ticket and the withdrawal decision (results/idx_fut_carry_open_capital.json)

## 输入面

- price: `results/idx_fut_carry_always_on_price.json` (digest 2c8655a90cb1c0cb)
- capacity: `results/idx_fut_carry_capacity_lots.json` (digest 71795b1553652f66)
- roll: `results/idx_fut_carry_roll_step_reversal.json` (digest d9cae2d574a9dde7)
- open_capital: `results/idx_fut_carry_open_capital.json` (digest 1ffffdc26d8dfc4b)
