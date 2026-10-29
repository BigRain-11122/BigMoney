# E235 — does a five-sleeve book pay five concave charges or one aggregate charge?

Round r1261 (bm-b), 2026-10-30. Entry card: `results/runnable_pool.json`
`E235-CHARGE-GRANULARITY`. Face: `results/state_tilt/GRANULARITY-2026-10-29.json`.
Runner: `scripts/e235_charge_granularity.py` (selftest 18/18).

## Why the question is first-order

E234 separated two channels inside the book bill: moving from one linear charge to five
per-member charges multiplies the bill 1.6x..3.5x, and almost all of that is the SPLIT
(+1289 / +2193 / +4015 bp) while the mixture term is small (-305 / -319 / +289 bp). Whether
a five-sleeve book *should* be charged that way was never asked: if the market prices a
sleeve's move against the BOOK's turnover, the per-sleeve sum overstates the bill by the
split term; if it prices against that sleeve's own turnover, the split is the correct bill.

## What was measured

For each of the five basket sleeves, session by session (`data/daily/<sym>.csv`):

    y  = log |open-to-close return|
    lo = log own turnover,          la = log book (sum of the five) turnover

fitted jointly, HAC lag 20, with the volatility-clustering control `y_{t-1}`, written in
identified coordinates: with `share = lo - la`, the pair (share, la) spans the same space as
(lo, la) but the level pair is numerically the same regressor twice. Then

    coefficient on share  = b_own      (own turnover moves, book held)
    coefficient on la     = g_scaling  (the book moves, shares held) = b_own + b_agg

so `b_agg = g_scaling - b_own`, with its error bar taken from the coefficient covariance
(selftest pins that covariance against `e233.ols_hac`'s published standard errors).

## What came back

| sleeve | b_own [95%] | b_agg [95%] |
|---|---|---|
| sh510300 | +0.452 [+0.325, +0.578] | -0.201 [-0.313, -0.089] |
| sh510050 | +0.734 [+0.651, +0.818] | -0.487 [-0.545, -0.429] |
| sh510500 | -0.122 [-0.155, -0.089] | +0.302 [+0.226, +0.377] |
| sh512100 | -0.147 [-0.180, -0.114] | +0.638 [+0.533, +0.743] |
| sh588000 | +0.188 [+0.054, +0.322] | +0.258 [+0.028, +0.488] |
| pooled (5 member intercepts) | +0.029 [+0.010, +0.048] | +0.039 [+0.009, +0.069] |

Bar: t = 2.87 (two-sided 5% over 12 coefficient tests).

**Two of five sleeves price their OWN turnover with a NEGATIVE elasticity.** A move is
priced *smaller* when that sleeve's own turnover is larger. No impact story produces that
sign; it is the signature of a level regression in which own turnover and book turnover
absorb each other's variation, and the signs move in lock-step across sleeves (510300/510050
own-positive + aggregate-negative, 510500/512100 own-negative + aggregate-positive).

Consequence: the pooled book-scaling elasticity is 0.068 against the family's single-regressor
exponent 0.622. That 5.5x attenuation is not a new measurement of concavity — it is the
cancellation of the two channels inside one pooled average.

## The spec-adequacy check that decided the verdict

E233's `B_controlled` control block carries lagged own turnover and lagged aggregate
turnover. On these panels the aggregate turnover level is 0.936..0.968 autocorrelated, i.e.
`la` and `la_lag` are the same regressor: the full block inverts only on 2 of 5 sleeves
(510050, 510500) and those two disagree with the identified block about the SIGN of every
channel. Published as `spec_stable: false`, `pooled_spec_stable: null`, and the verdict reads
`unresolved_spec_inadequate` rather than `own_dominates` or `aggregate_dominates`.

## Re-pricing (levels re-read, no verdict touched)

| arm | linear | one aggregate charge (g = 0.068) | five per-sleeve charges | split / aggregate |
|---|---|---|---|---|
| binary_low | 1538.8 bp | 1538.8 bp | 5193.2 bp | 3.375 |
| tilt_step | 1610.6 bp | 3002.5 bp | 9364.3 bp | 3.119 |
| tilt_linear | 1706.0 bp | 10729.9 bp | 29458.0 bp | 2.745 |

`binary_low` is *exactly* invariant (1538.8 both ways) because a 0/1 gate's move is
`|dw| = 1` and `c * 1**g = c` for every exponent — the same artefact E232 recorded. That
invariance is stated on the face (`gate_invariance_note`), not reported as robustness.

## What this changes, and what it does not

* No arm is re-adopted, no bill is applied: E226..E234's verdicts stand and their level is
  still carried as an unresolved price.
* The measurement says the granularity question **cannot be answered in levels**. The next
  card (E236, seeded) has to ask it on a share-and-difference design, where the regressor is
  stationary and the two channels cannot trade places.
* The one thing that *is* settled: the family's single exponent is a mixture of two
  offsetting channels, not a property of the book — which is exactly what E234 suspected when
  it published the split and the mixture separately.

## Reproduction

    python scripts/e235_charge_granularity.py selftest   # 18/18
    python scripts/e235_charge_granularity.py run        # writes the face + latest pointer

Evidence cutoff 2026-10-29. S6 leg `charge_granularity` sits after `per_member_gamma`;
smoke leg "product: the price of a sleeve move is measured against own and book turnover
before the book is charged".