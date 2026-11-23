# 开这本书要多少钱——四臂基差 carry 组合的资金线

generated 2026-11-23T17:39:34+08:00 | cutoff 2026-11-20 | verdict **FOUR_ARM_BOOK_NOT_OPENABLE_AT_BOOK_CAPITAL**

The four-arm book is priced at 7.938%/yr, Sharpe 3.412 on 2.246% vol, and it cannot be opened on the 1,000,000 CNY book: IC is 124,479 CNY short of its first lot (target 8.0%); IM is 152,596 CNY short of its first lot (target 8.0%). Holding one lot of every measured arm needs at least 2,277,075 CNY, so this book is a number about a larger account until the capital arrives. That floor covers only the arms with a capital line (IC, IM); IF, IH have none, so the true opening cost is higher and this face will not guess it.

## 已测臂（有资金线的两臂）

| 臂 | 开一手所需（元） | 本书资金（元） | 本书资金下可下单手数 | 差额（元） |
|---|---|---|---|---|
| IC | 1,124,479 | 1,000,000 | 0 | 124,479 |
| IM | 1,152,596 | 1,000,000 | 0 | 152,596 |

组合面出处：`results/idx_fut_carry_portfolio.json`（generated 2026-11-23T17:25:58+08:00，cutoff 2026-11-20，判词 FOUR_ARMS_DO_DISPERSIFY）。
资金面出处：`results/idx_fut_carry_sizing_spec.json`（generated 2026-11-23T14:36:13+08:00，cutoff 2026-11-20）。
上面两行是各自面自带的时点，本节不重算它们——本面比它们晚一趟。

## 未测臂（名字要点出来）

无资金线的臂：**IF, IH**。所以「开仓下限 2,277,075 元」只是已测臂之和，不是这本书的总成本；缺面不许印成 0。

## 下一步

Give IF and IH the same capital line the hedged arms have (per-lot vol at the 8% target): only then can the four-arm opening cost be stated instead of floored.

## 账

```
C1_measured_arms_cannot_even_hold_one_lot: True
C2_every_measured_arm_has_a_rung: True
C3_floor_is_not_printed_as_the_total: True
C4_floor_exceeds_book_capital: True
```
