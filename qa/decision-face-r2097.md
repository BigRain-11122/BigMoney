# QA — carry 决定面 r2097 (bm-c)

**件**：`scripts/idx_fut_carry_decision_face.py` / `results/idx_fut_carry_decision_face.json` /
`research/IDX_FUT_CARRY_DECISION_FACE.md`
**窗**：2026-11-25 19:0x +08:00，证据截止 2026-11-23

## 一、本面要回答什么

四张面上周各自回答了一个子问题（值多少钱 / 能做多大 / 移仓日算不算 carry / 开仓要多少钱），
没有一张回答「今天这本书做什么、什么数会让答案变」。本面把决定写在唯一一处，其余各面只读它。

## 二、本面唯一的新推理：尺子准入

r2094 报了三把尺子 6.92pp 的分歧并诚实拒绝挑一把；r2096 随后证明 IC 的移仓日台阶是**后付**
（次日回吐比 0.170/0.159，移仓后 8 日比前 8 日低 3.96/5.29pp，p=0.026/0.030）。因此把台阶记成
当日收益的尺子不是「最差的一把」，而是**错的一把**；把它平均进区间正是「利率看起来被尺子绑住」的成因。

准入规则（冻结在脚本常量里）：`verdict == COST_BOOKED_BY_LATER_CARRY` 才可报。

| 品种 | 采信 | 不采信 | 可报区间 | 准入前 |
| --- | --- | --- | --- | --- |
| IC | calendar 9.65% / strictest 9.68% | published (DATA_BLOCKED) | **9.65–9.68%（差 0.03pp）** | 2.76–9.68%（6.92pp） |
| IM | 无 | calendar PARTIAL_REVERSAL / strictest REAL_COST / published DATA_BLOCKED | **无可报数** | 5.74–11.96%（6.22pp） |

## 三、判词

`NO_ORDER_ON_BOTH_LEGS`

- **IC** `NO_ORDER_CAPITAL_BELOW_FIRST_RUNG`：口径已定，一档 1,129,565.88 元 vs 账面 1,000,000 元，
  差 **129,566 元（12.96%）**。补上后每年净超额（扣掉停车收益）**113,698–114,059 元**，只能报区间。
- **IM** `NO_ORDER_ACCOUNTING_UNSETTLED`：两把有样本的尺子给出**不同种类**的解释（部分回吐 / 真成本），
  样本量不是瓶颈（51/60 对已过 min_pairs=30），所以**加钱也不动这道门**。

先决次序（声明式）：accounting > capital > liquidity > order。会计有争议的书不能写成「资金到位即可下单」。

## 四、证据

| 项 | 命令 | 结果 |
| --- | --- | --- |
| 自检 | `python scripts\idx_fut_carry_decision_face.py --selftest` | **26/26 PASS** |
| 一致性 | `python scripts\idx_fut_carry_decision_face.py check` | **CHECK_OK rc0**（cutoff 2026-11-23，verdict NO_ORDER_ON_BOTH_LEGS） |
| 负控 | `python results\_r2097bmc_decision_face_negative.py` | **11/11 PASS** |

负控覆盖的谎话：手改数字→CHECK FAILED（且不含 STALE 字样，词是合同）／输入动→STALE／
缺面→DATA_BLOCKED 不默认为 0／IC 会计翻面→连区间都没有／补足本金→IC 过资本门但 IM 仍卡会计／
0.4 手→流动性门／发布面绝不给无口径品种一个数。

## 五、未做（如实）

- 本面**尚无 S6 链腿、无冒烟腿**：接线要改 `Tools/s6_chain_bmc.py` 与 `smoke_test.py`，两件在本轮开工时
  都是**他宿主留下的未提交脏面**（对端交互宿主 pid 93460 于 18:48 写过 s6_chain_bmc.py 后死亡），
  按轮首脏规只落新文件面，禁把半成品一起提交。
- IM 的结算要靠它自己出现（或长期不出现），不是靠再跑一次。
- 一手以上的收益衰减仍未测（容量面只答「吞得下」，不答「吞下去之后利率掉多少」）。
