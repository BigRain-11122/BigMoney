# E255 — the quoted digit has a resolution: the iid arm and the week arm are one number

r1349 · bm-c · 2026-10-30 · face `results/etf_book_bootstrap/NOISE-2026-10-29.json`
(gate: `python scripts/etf_book_quantile_floor.py --check` — every percentile, interval,
permutation p and verdict re-derived from the eight block arms' own 2,000 rows) · card E255.

## Why

The book-envelope family published a distribution (E246), priced the block length across eight
arms (E248) and added the independence zero point (E251). Every sentence in that family is a
percentile of 2,000 resamples, and E251's own honest limit had to say "the p5 estimate is noisy at
~0.1pp, so the 0.30pp gap between block 1 and block 5 is above that but only just". That is a
noise claim that was never measured — and it was load-bearing: it decides whether the ladder's
rungs are an *ordering* or *one number stated eight times*.

## What

Two aggregators, because a single noise model is also a ruler too:

* **distribution-free interval** — the binomial ranks of the quantile, so no density and no
  symmetry assumption enters the bound (the upper end is the mirrored lower one, `n − X ~ Bin(n,1−p)`);
* **spacing-estimator SE** — `f(q) = (k2−k1)/(n·(x_k2−x_k1))`, `SE = sqrt(q(1−q)/n)/f`, the
  density-based reading of the same width;
* **permutation test** on each comparison, 1,000 pool-and-relabel draws, statistic = difference of
  the sample quantile (null = the block length does not change the resampled distribution, which
  is exactly what the ladder claims to test);
* **resolution arithmetic** — `n_needed = n·(z·se_diff/gap)²` (the E162 reader-horizon law applied
  to a quantile instead of to a t-test), so every "not settled" comes with a price.

## Reading (2026-10-29 bar, 8 arms × 2,000 resamples)

| comparison | gap | settled? | note |
|---|---|---|---|
| iid (block 1) vs week (block 5), maxDD p5 | 0.29pp | **no** | needs 28,737 resamples |
| iid vs year (block 250), maxDD p5 | 7.64pp | yes | perm p 0.001 |
| adjacent-ladder gaps, maxDD p5 | — | **4 of 7** | the other 3 are inside the ruler |
| median (p50) gaps | — | **1 of 13** | the median is the *least* resolvable column |

Two pairs (`10→20` and `120→250` on CAGR p5) separate under one aggregator and not the other and
are published as `aggregators_disagree_on`, never resolved. `ladder_is_one_reading: false`: the
ladder is a real band, but only its large rungs are measurements — so the family may say "block
length matters" and may NOT say "block 10 is calmer than block 20".

## Wiring

`--check` rides the S6 chain (r1290 class: a face nobody re-derives describes a table that may
have moved) with its refresh declared, plus a smoke leg on the selftest contract (interval,
permutation on both sides, and the rule that an aggregator disagreement is published).

## Yield note (what this round did NOT ship, and why)

The dead bm-c window that wrote this face had also written an ultra-tail rung (E254) and a
volatility-overlay tail face (E255 as first drafted). Both landed upstream first, by two other
machines, and the rebase surfaced them:

* the p1/p99 rung — upstream `scripts/etf_book_nav_envelope.py` already carries it on the same
  arms (E252 "a percentile you did not publish may already be in the rows you kept");
* the overlay's tail — upstream `voltail` mode prices it on a paired bootstrap (r1157:
  "+6.04pp middle vs +1.26pp p1", and it is on the chain as `etf_book_voltarget_tail`).

Both local drafts were dropped rather than merged into a second implementation of the same
measurement. The one piece of this window's own work that was neither duplicated nor already
upstream is the **resolution face** above; the second is a one-word mechanism fix recorded below.

## Mechanism fix (a gate was red for a whole chain record)

`etf_book_nav_envelope --check` reported a face written under older CRITERIA as "criteria echo
*differs* from the frozen constants", while the S6 runner pays a leg's declared refresh **only
when the probe output contains "stale"** (r1345/E237). The refresh was declared and never spent,
so the leg sat red through a complete chain record this morning. The criteria-echo branch is now
worded as *stale*; a number that disagrees with its own rows stays worded as a disagreement, so a
tampered digit can never trigger a silent regeneration.