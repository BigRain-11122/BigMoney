# Does the hedge still work when the beta cannot see the future?

`HONEST_BETA_KEEPS_ITS_REMOVAL` · `ONE_UNIT_TIES_THE_FITTED_BETA` · `HEDGE_TRADES_DRAWDOWN_FOR_RETURN`

Evidence cutoff **2026-11-20** (last period ends **2026-11-11**).  Book and hedge leg come from `results/astock_veto_hedgeable_beta.json`; nothing is refitted for trading here.

## 1. The short version

- Refitted before every period on prior rows only, the beta removes **61.9%** of the book's annualised volatility (29.89% -> 11.38%) over 57 periods.
- The look-ahead arm -- one beta for the whole window, the way the parents read it -- removes **62.7%**; the gap is **0.23 pp** (`LOOKAHEAD_BUYS_MORE_THAN_A_TIE`).
- Beta = 1.00 with no fitting at all sits **-0.22 pp** from the honest arm (`ONE_UNIT_TIES_THE_FITTED_BETA`).
- The control: an unhedged book of the honest arm's own volatility draws down **-9.74%** at worst against the hedge's **-13.39%** (a **-3.65 pp** gap, `HEDGE_TRADES_DRAWDOWN_FOR_RETURN`) while earning **5.23%** against the hedge's **11.17%** -- so `HEDGE_TRADES_DRAWDOWN_FOR_RETURN` is a trade, not a defeat.

held honestly, the hedge removes 61.9% of the book's annualised volatility (29.89% -> 11.38%) and the look-ahead arm removes 62.7% -- a gap of 0.23 pp; beta = 1.00 without any fitting sits 0.22 pp above the honest arm; against an unhedged book of the same volatility it earns 11.2% against 5.2% (0.98 vs 0.46 per unit of volatility) but draws down -13.39% against -9.74%.

## 2. The sample, and why every arm shares it

| periods in the parent | evaluated | warm-up | trainings that could not be fitted |
|---|---|---|---|
| 77 | 57 | 20 | 0 |

The first walk-forward beta sees 20 periods; the last sees 76.  Every arm below is measured on those same 57 periods, so no arm gets a longer or kinder window.

## 3. How much the beta moves when it is refitted

| reading | value |
|---|---|
| first refitted beta | 0.9082 |
| last refitted beta | 0.9710 |
| range across refits | 0.8644 .. 1.0121 |
| mean / sd | 0.9525 / 0.0526 |
| mean absolute step between refits | 0.0076 |
| largest single step | 0.0439 |
| one beta on all periods (look-ahead) | 0.9707 |
| beta published by r2022/r2029 | 0.9013 |
| 95% band published by r2029 | 0.7950 .. 1.0076 |
| refits that land OUTSIDE that band | 9 of 57 |

A refitted beta is not a constant with a wobble around it: the honest series spends 9 of its 57 refits outside the band r2029 printed around the frozen one.

## 4. Six arms, one sample

| arm | k | periods | annualised vol | removed | per unit of vol | mean / yr | worst period | down periods | cumulative | worst drawdown |
|---|---|---|---|---|---|---|---|---|---|
| no hedge | 0 | 57 | 29.89% | n/a | 0.46 | 13.74% | -17.18% | 24 | 53.21% | -25.92% |
| beta = 1.00 (mechanical) | 1.00 | 57 | 11.15% | 62.7% | 1.08 | 12.06% | -8.22% | 20 | 67.45% | -13.34% |
| one beta on every period (look-ahead) | 0.9707 | 57 | 11.15% | 62.7% | 1.09 | 12.11% | -8.48% | 20 | 67.82% | -13.39% |
| beta frozen at 2023-12-31 (0.9013) | 0.9013 | 57 | 11.38% | 61.9% | 1.07 | 12.23% | -9.09% | 18 | 68.50% | -13.53% |
| beta refitted on prior rows (honest) | refitted | 57 | 11.38% | 61.9% | 0.98 | 11.17% | -9.09% | 20 | 60.68% | -13.39% |
| no hedge, scaled to the honest arm's volatility | 0 (scaled) | 57 | 11.38% | 61.9% | 0.46 | 5.23% | -6.54% | 24 | 23.11% | -9.74% |

The last row is not a hedge.  It is the same book, held smaller, at exactly the volatility the honest hedge delivers -- the control that decides whether any of the risk removal above is more than leverage.

## 5. The three questions a reader asks, answered on the same numbers

**Does the honest beta keep the claim?** HONEST_BETA_KEEPS_ITS_REMOVAL -- 61.9% of the volatility gone, against 62.7% with the look-ahead beta.

**Is the fitting worth it?** ONE_UNIT_TIES_THE_FITTED_BETA -- the mechanical beta = 1.00 is -0.22 pp away (positive means fitting helped).  On this sample the refits were not paid for: beta = 1.00 ends at 67.45% against the honest arm's 60.68%, with a shallower worst period (-8.22% vs -9.09%).  Refitting pays for information it does not get to keep.

**Is it more than leverage?** HEDGE_TRADES_DRAWDOWN_FOR_RETURN.  At equal volatility the hedge earns **11.17%** a year (0.98 per unit of volatility) and the de-levered book earns **5.23%** (0.46).  The hedge therefore is not merely leverage -- it roughly doubles the return per unit of risk.  But it does not give the shallowest hole: the de-levered book bottoms at -9.74% against the hedge's -13.39%.  A holder whose constraint is a drawdown budget (r2023, r2026) is buying the *worse* of the two on that axis and the better one on the return axis; both are printed here because the choice depends on which of the two he cannot breach.

Period by period, hedging shrank the move in **82.5%** of the 57 evaluated periods.

## 6. What this face does not say

- It does not re-choose a size, a budget or a cost: those are r2022-r2029's numbers, quoted.
- The book is still priced at its last mark (2026-11-11) and the prices in the ticket faces are later; that dating gap belongs to r2028 and is not repaired here.
- The evaluation sample is one history.  A volatility claim on 57 periods carries its own sampling error, which this face prints as the arms' spread rather than as a single number.
- Only the ETF hedge leg (512100) is walked forward.  The IM arm was shown by r2027 to be unable to express the beta at small capital, so it is not re-walked here.
- No cost is charged to the refits beyond what the parent book already carries: a real account re-hedging every period pays turnover this face does not model.

## 7. Reproduction

```
python scripts/astock_veto_hedge_walkforward.py selftest
python scripts/astock_veto_hedge_walkforward.py run
python scripts/astock_veto_hedge_walkforward.py check
```
