# the carry sleeve's sizing ruler: adopted, with the roads not taken still priced

evidence cutoff: **2026-11-17** | source: `results/idx_fut_carry_capital_ladder.json` | decided 2026-11-17 in bm-c round 1779 | generated 2026-11-17T17:36:00+08:00

**Adopted: `A_keep_target_raise_capital`, target 8%, read as hard_cap_vol_le_target.**

> 8% is a RISK DIAL and not a fit (results/etf_vol_target_sweep.json, book n5: target 8% prints 11.49% CAGR / -10.56% maxDD / Sharpe 1.13 against 15.56% / -16.04% / 1.00 with no target -- Sharpe moves 0.08 while return and drawdown scale together, so the target sets the size of the drawdown, not the return). Raising it to 9% to make one contract fit would spend 1pp of drawdown tolerance for no return; the capital is the free variable and the risk number is a preference

The rule a reader can recompute:

> lots = floor(target_pct/100 * capital / ann_vol_of_one_lot_hedged); one lot needs ann_vol_of_one_lot_hedged / (target_pct/100) CNY of capital

What this decision does not change: the vol of the sleeve (no new measurement); the desk's recommended lots (an input, printed and marked, never rewritten); the 8% target itself (road B is printed with its price and not adopted).

## IC

| capital | target | vol of 1 lot (hedged) | budget at target | lots the ruler allows |
|---|---|---|---|---|
| 1,000,000 CNY | 8% | 89,823 CNY | 80,000 CNY | **0** (0.8906) |

**ONE_LOT_IS_NOT_A_SMALL_ALLOCATION.** One lot is 89,823 CNY of annual vol -- more than this book's 80,000 CNY budget, so the rule buys nothing here. The first executable rung is **1,122,782 CNY** (+122,782); holding the desk's 4 lots inside the target would take 4,491,130 CNY.

- the desk's ticket: **4 lot(s)**, `OUT_OF_RULER` against this ruler, 4.4911x the budget
- A keep 8%, raise the capital: 0 lot(s) now, 1 lot at 1,122,782 CNY -- **ADOPTED**
- B keep 1,000,000 CNY, lower the target: 1 lot needs 8.9823% (that target buys 1 lot(s) here) -- not adopted
- C keep both: 0 lot(s) -- not adopted (this is what A reads at today's capital, not a separate road)

| capital rung | multiple of the book | lots |
|---|---|---|
| 1,000,000 | 1.0000x | 0 |
| 1,122,782 | 1.1228x | 1 |
| 2,245,565 | 2.2456x | 2 |

## IM

| capital | target | vol of 1 lot (hedged) | budget at target | lots the ruler allows |
|---|---|---|---|---|
| 1,000,000 CNY | 8% | 92,018 CNY | 80,000 CNY | **0** (0.8694) |

**ONE_LOT_IS_NOT_A_SMALL_ALLOCATION.** One lot is 92,018 CNY of annual vol -- more than this book's 80,000 CNY budget, so the rule buys nothing here. The first executable rung is **1,150,230 CNY** (+150,230); holding the desk's 4 lots inside the target would take 4,600,922 CNY.

- the desk's ticket: **4 lot(s)**, `OUT_OF_RULER` against this ruler, 4.6009x the budget
- A keep 8%, raise the capital: 0 lot(s) now, 1 lot at 1,150,230 CNY -- **ADOPTED**
- B keep 1,000,000 CNY, lower the target: 1 lot needs 9.2018% (that target buys 1 lot(s) here) -- not adopted
- C keep both: 0 lot(s) -- not adopted (this is what A reads at today's capital, not a separate road)

| capital rung | multiple of the book | lots |
|---|---|---|
| 1,000,000 | 1.0000x | 0 |
| 1,150,230 | 1.1502x | 1 |
| 2,300,461 | 2.3005x | 2 |

Fractions of a lot are arithmetic; `lots` is what could be held. Nothing here re-derives volatility -- the per-lot numbers come from the ladder face, which takes them from `SIZING.json`.
