# ETF book: the gate is only on the way in

**Question.** Every name this book holds passed a 20-bar median turnover gate of 2000 万元 on the bar it was ranked. Nothing checks the same number on the bar it is sold. How often is the book asked to exit into a name it would not be allowed to buy, how long does the queue last, and what is the wait worth?

**Panel.** 1515 funds x 5275 bars, 2005-02-23..2026-11-06, 169 quote flips repaired (the production panel's own repair, imported not copied).

**Arm.** declared fill (score held one bar back, close t -> open t+1); as-coded not measured.

## Reading

| phase | start | holds | positions | exit below gate | no bar | deferred | outside cap | share below | mean defer (bars) | drag (pp/yr) |
|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 2020-01-02 | 82 | 984 | 39 | 0 | 14 | 25 | 3.96% | 10.57 | +0.435 |
| 1 | 2020-01-09 | 82 | 984 | 46 | 0 | 18 | 28 | 4.67% | 6.83 | +0.128 |
| 2 | 2020-01-16 | 82 | 984 | 46 | 0 | 13 | 33 | 4.67% | 7.69 | +0.014 |
| 3 | 2020-01-23 | 82 | 984 | 35 | 0 | 12 | 23 | 3.56% | 10.33 | +0.295 |

Totals over 3936 positions: 166 exits below the buy gate (4.22%), 0 with no bar at all, 109 that never found a qualifying bar inside 20 bars.

**Verdict: `MIXED_ACROSS_PHASES`** (mean share below gate 0.0421, mean drag 0.2177 pp/yr, range 0.014..0.4346).

The two readings behind that verdict, printed separately because the frozen rule requires both to be small (or both to be large) before it names a side:

- **incidence**: 4.21% of held positions must be sold on a bar where the name would not pass the buy gate -- above the no-constraint line (2%), below the real-gate line (5%);
- **price**: the wait is worth +0.22 pp/yr on average and every phase sits inside +-0.57 pp of zero, so the queue is real but the money is not in it;
- **the censored tail**: 109 of 3936 positions (2.77%) never found a qualifying bar inside 20 bars at all and are counted as outside_cap, not as a zero return -- those are forced holds, and they are the half of this face the panel cannot price.

## 它量的是什么，不是什么

- the deferral is weight x (open[t']/open[exit] - 1): an attribution of stuck capital, not a re-priced equity curve
- a position that never clears the gate inside 20 bars is outside_cap, never 0
- drag_pp_per_year = 100 x summed contribution / that phase's own span in years
- the gate is read off the same `amt` panel the ranking uses (imported from `etf_composite_pf.MIN_AMT`, not retyped), so a reader can check the two faces cut at the same number;
- a below-gate reading is not a death: the name can come back, and the deferral prices exactly that wait instead of assuming a total loss;
- what is NOT measured here: the size of the order relative to turnover (impact), the bid-ask spread, and any name that stopped existing inside the hold -- the panel has no dead funds (E352 prices that half as a budget).

## 复跑

```
python scripts/etf_book_exit_liquidity.py run
python scripts/etf_book_exit_liquidity.py --check
python scripts/etf_book_exit_liquidity.py --selftest
```
