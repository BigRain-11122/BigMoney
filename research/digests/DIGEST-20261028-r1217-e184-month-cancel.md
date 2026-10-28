# Where the wide book's thin net comes from (r1217, bm-b, 2026-10-28)

## What was published before

E182 (`results/e43_tilt_4member/WIDESIDEGROSS-20261027.json`) measured the
rotating wide book's repair delta per holding and published one net per era
beside one gross: 2024_now +49.6bp net over 113.1bp gross, `net_over_gross`
0.4387. The face could say the net is thin. It could not say *where* the
movement went, and two very different mechanisms produce exactly that shape:

* **within-month cancellation** — two holdings repaired opposite ways at the
  same rebalance (a membership / weight artefact), or
* **across-month disagreement** — one month repairs up, another repairs down
  (the era averages away a signal that is really time-varying).

Those imply opposite follow-ups, so the ratio was not yet a statement.

## What this round adds

`run_tilt3widesplitmonth()` / `_month_cancel_verdict()` in
`scripts/e39_panel_census.py` (CLI mode `tilt3widesplitmonth`, deliverable
`results/e43_tilt_4member/WIDEMONTHCANCEL-20261027.json`, selftest 617→628)
keeps the delta per decision month and then splits the loss exactly:

    |sum_m net_m| / sum_m gross_m
        = (sum_m |net_m| / sum_m gross_m) x (|sum_m net_m| / sum_m |net_m|)

The first factor is the share of motion surviving **within-month** cancellation,
the second the share surviving **across-month** sign disagreement. The two
removed amounts add up to `gross - |net|` by construction, so a reader is never
shown more cancellation than the book had.

| era | months | path gross | net | net/gross | within keep | across keep | verdict |
|---|---|---|---|---|---|---|---|
| pre2017 | 44 | 0.0 | 0.0 | – | – | – | flat_per_month |
| 2017_2020 | 48 | 0.0 | 0.0 | – | – | – | flat_per_month |
| 2021_2023 | 36 | 131.9 | 90.6 | 0.687 | 0.969 | 0.709 | across months |
| 2024_now | 34 | 341.6 | 140.5 | 0.411 | 0.872 | 0.472 | across months |
| full | 162 | 473.5 | 231.1 | 0.488 | 0.899 | 0.543 | across months |

*(bp, sums of monthly contributions; net and gross are annualised for the join
below, which is why the 2024_now net reads 49.6 there and 140.5 as a path sum.)*

**Answer: across-month disagreement.** On 2024_now, 87.2% of the monthly motion
survives inside its own month but only 47.2% of what survives then survives the
between-month signs. Across every measured era, at most 47.67bp is removed
inside months while up to 194.70bp is removed between them — 4.1x.

## Consequence for how the number travels

"+49.6bp net" is not a small steady gain; it is the residual of a path that
carried 140.5bp of monthly net motion and reversed on itself. The repair's
monthly delta is **time-varying and era-averaged**, so it must not be quoted as
an edge, a level, or a reason to hold the wide book — only as a description of
what the repair did to this window.

## The measurement basis trap this round also closes

E182's gross is formed *after* netting each holding over the whole era, so a
name that repairs +X and then -X inside the era contributes |0| to it while the
path carried the motion twice. The face now publishes both bases and their
ratio: the path gross is 1.037x / 1.067x / 1.060x the name-level gross on
2021_2023 / 2024_now / full. Name-level gross is not the width of the movement,
and `net/gross` computed on it understates the cancellation the book actually
experienced (2024_now: 0.4387 named-level vs 0.4114 path-level).

The two nets agree to **0.000416bp** (annualised), so this is the same
computation read two ways and not a second engine pass.

## Honest limits

* The monthly net is the repair's contribution in that decision month; it is
  not a tradable month return and no single month is a statement on its own.
* pre2017 / 2017_2020 are exactly flat, so those eras say nothing about the
  mechanism — the classification is `flat_per_month`, not "within-month".
* `months_net_against_total` is empty when an era's net is inside tolerance: a
  zero net has no direction to oppose.
* Descriptive census only: no gate, no prereg, no trial count.