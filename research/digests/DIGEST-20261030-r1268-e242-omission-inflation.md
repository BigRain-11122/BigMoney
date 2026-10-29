# E242 -- which published family slopes are inflated by omitting the other members?

Round r1268 (bm-b), 2026-10-30. Evidence cutoff 2026-10-29. Book: equal-weight five-ETF
basket, common grid of 1,328 sessions. Face: `results/state_tilt/OMISSION-2026-10-29.json`.

## The question

E240 priced one omission inside one design: a pair regression of a member's move on its own
turnover increment plus a **single** counterparty's increment leaves three members out, and the
resulting cross slope came in at 0.325 against an identified 0.183 -- factor 1.89 at
rho = 0.424, matching the closed form `(1 + (k-1)rho - k rho^2) / (1 - rho^2)`.

Every design in this family whose regressor set leaves a member out inherits *some* factor. The
family has been quoting such designs for several rounds. This round walks the published slopes,
classifies each by how many of the other four members it omits, re-prices them on one identified
grid, and states whether each published verdict survives.

## Four nested regressor sets on the same y and the same own regressor

| set | regressors | members omitted |
|---|---|---|
| S0 | own only | 4 |
| S1 | own + ONE counterparty (E239 / E240) | 3 |
| S2 | own + one + SUM of the other three (E240's identified form) | 0 |
| S3 | own + each of the other four | 0 |

S2 reproduces E240's published identified gap to **0.0** (`diff_one_vs_rest3`), so the sweep is
running the family's own arithmetic rather than a look-alike.

## What the omission actually costs

| reading | naive (omit 3) | identified | factor |
|---|---|---|---|
| cross level, vs S3 | 0.3248 | 0.2121 | **x1.53** |
| cross level, vs S2 | 0.3248 | 0.1830 | **x1.78** |
| closed form at rho 0.424 | -- | -- | x1.89 |
| own level (own-only, omit 4) | 1.1748 | 0.8641 | x1.36 |
| own level (own + one) | 1.0519 | 0.8641 | x1.22 |

Two things follow.

1. **The factor is only defined against a named identified form.** S2 and S3 disagree by 14% on
   the same grid (0.183 vs 0.212) because the sum is a constrained combination of four collinear
   coefficients. So "x1.53" and "x1.78" are both true statements about different comparators,
   and E240's 1.89 sits at the top of that range. A factor quoted without its comparator is not
   a number.
2. **The own channel is inflated too**, and by less than the cross channel at the same nesting
   (1.22 vs 1.53). Any face that quotes an own slope from an omitting design carries this.

## What the omission does NOT cost: the paired difference

E239's published verdict rests on `b_own - b_cross` = 0.4837 [0.4077, 0.5597].

| | value | interval |
|---|---|---|
| published (per-pair intersections) | 0.4837 | [0.4077, 0.5597] |
| same naive design, common grid | 0.7270 | -- |
| identified (own + all four, member FE) | **0.6675** | **[0.4978, 0.8373]** |

The omission moves the difference by **0.060**; the *grid* moves it by **0.243** -- four times
more. And the reason the omission barely moves it is structural, not luck: the omitted block
loads on the own and on the cross regressor alike, and the pooled design runs every ordered pair
in **both directions**, so the two biases cancel in the difference. Two selftest fixtures pin
it (exchangeable increments; and one counterparty deliberately decoupled from the common factor
-- the cancellation survives).

So the family's verdict vocabulary is safe exactly where it rests on a **difference**, and at
risk where it rests on a **level**. The face publishes the level's `gate_window` -- the interval
a magnitude bar must sit in for the reading to change side -- which is what turns "which verdicts
are at risk" into a measurement.

## Verdicts

| face | published verdict | re-priced | outcome |
|---|---|---|---|
| E239 | own_exceeds_a_single_counterparty | own_exceeds_a_single_counterparty (0.6675 [0.4978, 0.8373]) | **survives**, strengthens |
| E240 | rest_channel_is_additive | not re-priceable (already identified) | control reproduces at 0.0 |
| E236 | unresolved_magnitude_disagreement | not re-priceable (own share + aggregate: no member omitted) | unaffected |
| E233 | mixture | not re-priceable (own + aggregate gamma) | unaffected |

15 published slopes were read, 7 re-priceable; **no verdict flips**.

## Levels at risk (published -> identified)

| face.key | published | grid | same-grid naive | identified | factor |
|---|---|---|---|---|---|
| E239.mean_cross | 0.3562 | per-pair | 0.3248 | 0.2121 | x1.68 |
| E239.pooled_cross | 0.3136 | per-pair | 0.2622 | 0.1799 | x1.74 |
| E239.pooled_own | 0.7973 | per-pair | 0.9892 | 0.8474 | x0.94 |
| E240.naive_cross | 0.3248 | common | 0.3248 | 0.1830 | x1.78 |
| own_only.b_own | 1.1748 | common | -- | 0.8641 | x1.36 |
| own_plus_sum (control) | 0.1830 | common | -- | 0.2121 | x0.86 |

`E239.pooled_own` is the interesting row: the omission pushes it **up** (same grid x1.17) while
the per-pair grid pushes it **down**, and the two nearly cancel (x0.94). A face can therefore be
"safe" on its published number for two reason s that contradict each other -- which is why the
grid and the omission are published as separate columns rather than one factor.

## How to apply

1. A factor is defined only against a **named** identified form. Publish the comparator's
   coefficient beside the factor, and publish the factor for every identified form you can
   build; if they disagree, say so rather than picking one.
2. Omission inflation moves **levels**, and cancels in a **paired difference** whenever the
   omitted block loads on both retained regressors and the pooling runs both directions. Before
   re-pricing a verdict, ask which of the two it consumes.
3. The **grid** can be a bigger lever than the omitted variables. Here it moves E239's published
   difference by 0.243 against the omission's 0.060; an effect attributed to omission without a
   same-grid recomputation is a guess.
4. A magnitude gate's exposure is an **interval**: publish the window between the published and
   the identified level, not a verdict.

## Artefacts

- `scripts/e242_omission_inflation_sweep.py` -- run / selftest 14/14, deterministic (two runs
  byte-identical apart from the envelope timestamp).
- `results/state_tilt/OMISSION-2026-10-29.json` + `omission_latest.json` +
  `omission_pairs_2026-10-29.csv`.
- `Tools/s6_chain_bmb.py` leg `omission_inflation` (after `pair_reproduction`);
  `smoke_test.py` leg on the face shape.
- `knowledge/METHODOLOGY_ASSETS.md` card E242.
- Pool: E242 done with result_ref.

No charge, no adoption, no arm moved.