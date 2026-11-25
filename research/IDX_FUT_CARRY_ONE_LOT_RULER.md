# 一手到底要多少钱：一个数，还是两个读者都拿不住数

同一件事在桌面上有两条腿在印：11-25 那一代（sizing_spec / open_capital / always_on_price / decision_face / capacity_lots）说 IC 一手 1,132,145.38 元、IM 一手 1,161,161.25 元；11-23 那一代（forward_clock / portfolio_capital / tradeable_hedge_capital）仍印 1,124,479.00 / 1,152,596.00。差 7,666.38 与 8,565.25 元/手，两边都用同样的语气说话，任何一页都不说自己属于哪一代。

这一页不重算任何人的数，只问一句话：**你印的这个数，是不是今天真的那个**；如果不是，你是早了一代（重生即可），还是我们有两把同时在用的尺子（真缺陷）。归因按生成时刻，不按口味：比权威面早、数不同=STALE；不早于权威面还不同=DISAGREE。

<!-- one-lot-ruler:begin -->

generated 2026-11-25T20:45:51+08:00 | verdict **CONSUMERS_ONE_GENERATION_BEHIND** | evidence cutoff 2026-11-25

## What one legal lot costs today

| product | sizing_spec | open_capital | always_on_price |
|---|---|---|---|
| IC | 1,132,145.38 | 1,132,145.38 | 1,132,145.38 |
| IM | 1,161,161.25 | 1,161,161.25 | 1,161,161.25 |

## Every face that prints it

| face | product | prints | today | delta | written | status |
|---|---|---|---|---|---|---|
| forward_clock | IC | 1,124,479.00 | 1,132,145.38 | -7,666.38 | 2026-11-23 | **STALE_BY_GENERATION** |
| forward_clock | IM | 1,152,596.00 | 1,161,161.25 | -8,565.25 | 2026-11-23 | **STALE_BY_GENERATION** |
| portfolio_capital | IC | 1,124,479.00 | 1,132,145.38 | -7,666.38 | 2026-11-23 | **STALE_BY_GENERATION** |
| portfolio_capital | IM | 1,152,596.00 | 1,161,161.25 | -8,565.25 | 2026-11-23 | **STALE_BY_GENERATION** |
| tradeable_hedge_capital | IC | 1,124,478.99 | 1,132,145.38 | -7,666.39 | 2026-11-23 | **STALE_BY_GENERATION** |
| tradeable_hedge_capital | IM | 1,152,595.98 | 1,161,161.25 | -8,565.27 | 2026-11-23 | **STALE_BY_GENERATION** |
| decision_face | IC | 1,132,145.38 | 1,132,145.38 | 0.00 | 2026-11-25 | **FRESH** |
| decision_face | IM | 1,161,161.25 | 1,161,161.25 | 0.00 | 2026-11-25 | **FRESH** |
| capacity_lots | IC | 1,132,145.38 | 1,132,145.38 | 0.00 | 2026-11-25 | **FRESH** |
| capacity_lots | IM | 1,161,161.25 | 1,161,161.25 | 0.00 | 2026-11-25 | **FRESH** |

## If the stale faces are rebuilt (arithmetic only)

- opening one lot of every measured arm: 2,277,075.00 -> 2,260,843.37 (delta -16,231.63)
  - arithmetic_only: sum of the two per-lot deltas added to the published floor; the face itself must still be rebuilt
- IC one lot P&L on its first rung: -8.4128% -> -8.3558% (shift 0.057 pp)
- IM one lot P&L on its first rung: -12.6879% -> -12.5943% (shift 0.0936 pp)
  - arithmetic_only: same P&L per lot, denominator moved to today's ruler

## Rebuild these, in this order

- `results/idx_fut_carry_forward_clock.json` (forward_clock, written 2026-11-23) -- STALE_BY_GENERATION
- `results/idx_fut_carry_portfolio_capital.json` (portfolio_capital, written 2026-11-23) -- STALE_BY_GENERATION
- `results/idx_fut_carry_tradeable_hedge_capital.json` (tradeable_hedge_capital, written 2026-11-23) -- STALE_BY_GENERATION

`--check` re-reads every one of these faces and re-derives the table; a face that moved says STALE, a number that moved with the same inputs says CHECK FAILED.

<!-- one-lot-ruler:end -->

## 为什么这页值得存在

那三张 11-23 的面没有任何链腿会自动重生它们——它们的上游在一小时前刚被链推过，于是「差多少钱才够开一手」这个 CEO 会读的数字在两张页面上差 16,231.63 元。把这个问题变成一条 check-only 的腿，比记住「记得重生那三张」可靠。

## 这页没有回答的

- the per-lot capital itself (results/idx_fut_carry_sizing_spec.json and its two peers)
- any downstream income, Sharpe or floor: this face only prices the gap
