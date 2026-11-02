# DIGEST 2026-11-02 r1238 · the censored half of the sell queue

**Round:** 1238 (bm-a). **Card:** E354. **Face:** `scripts/etf_book_forced_hold.py`.

## The gap this closes

r1237 (`etf_book_exit_liquidity`, E353) priced the exits that had to wait for the 20-bar
turnover gate to clear again: 4.23% of held positions, +0.22 pp/yr, "the queue is real but
the money is not in it". It also reported -- and did not price -- 109 of 3,924 positions
(2.78%) that never found a qualifying bar inside the 20-bar cap. In that payload those rows
carry `delta_ret = 0.0`: not because the wait was free, but because it was not measured. A
count with no price next to it reads as "this half costs nothing".

## What was measured

Same census (`measure_positions` imported from the sibling module, never re-typed), same
weights (the engine's own `scale / n_names`), so the two numbers add:

* reference price = the exit bar's open, or the last print before it when that bar did not
  print (the engine's own ffill, stated rather than assumed);
* sale price = the first bar *after* the exit with **any** print at all -- the 20M gate is
  given up on, this is the value of the position if you stop waiting and take the market;
* a name that never prints again before the panel ends is `open_at_end`: counted, named,
  and never folded into the pp total as a zero (E346 family).

## Reading (evidence cutoff 2026-10-30)

| phase | positions | tail | tail share | tail (pp/yr) | mean wait (bars) |
|---|---|---|---|---|---|
| 2020-01-02 | 984 | 25 | 2.54% | +0.026 | 1.0 |
| 2020-01-09 | 984 | 28 | 2.85% | +0.095 | 1.0 |
| 2020-01-16 | 984 | 33 | 3.35% | +0.067 | 1.0 |
| 2020-01-23 | 972 | 23 | 2.37% | +0.013 | 1.0 |

* verdict `CENSORED_TAIL_IS_IMMATERIAL`: mean **+0.0503 pp/yr**, every phase inside the
  0.57 pp material line;
* ceiling (tail's weight share / the phase's own years): **0.35–0.49 pp/yr** -- the tail
  cannot move the headline even if every position in it lost its whole value;
* **109/109 priced, 0 `open_at_end`**, mean wait **1 bar** -- these are not delisted names,
  they are names that print every day and never clear the book's own buy threshold;
* combined with the sibling face: the sell queue touches 4.23% of positions and is worth
  **+0.27 pp/yr** in total (+0.22 wait + 0.05 tail).

## Controls

The published census is reproduced before any verdict is printed: 3,924 positions, 109
`outside_cap`, share below gate 0.0423, `reproduced=true`. `--check` re-derives the verdict
from the payload's own summary. A phase that cannot be priced returns `INCOMPLETE_PRICING`
rather than joining the "small tail" branch.

## Not measured

Attribution, not a re-priced equity curve (the published CAGR / drawdown keep the engine's
own handling of a name that stops printing). Market impact and bid-ask spread are outside
the face. The gate itself (20M / 20 bars) has still never been swept -- that is the next
open question on this line, and it matters more than this tail.

## Wiring

Chain leg `etf_book_forced_hold` (after `etf_book_exit_liquidity`, imports its rows); smoke
two legs (selftest + `--check`); CEO page section 「你手上这些东西，真卖得掉吗」 with page
selftest L121–L123.