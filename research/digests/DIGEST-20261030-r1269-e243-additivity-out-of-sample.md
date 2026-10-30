# E243 -- the additivity verdict was carried by its aggregator, not by the data

Round r1269 (bm-b), 2026-10-30. Card: `knowledge/METHODOLOGY_ASSETS.md` E243.
Face: `results/state_tilt/ADDOS-2026-10-29.json` (+ `addos_latest.json`).
Runner: `scripts/e243_additivity_out_of_sample.py` (run / selftest 14/14 / artifact).

## What was asked

E240 published `rest_channel_is_additive` from one window (five members, 1328 sessions from
2020-11-17): one counterparty 0.183 vs the sum of the other three 0.175, difference
+0.008 [-0.012, +0.022]. The card asked whether that survives its own neighbourhood: the
pre-2020 members, era splits, and leave-one-member-out.

## What the grid says

Ten decided cells, plus one labelled k=3 degenerate cell (`early_three`, where "the sum of the
other three" is the single remaining member and the difference is therefore not an aggregation
reading). **Not one cell supports additivity**, and the reason is not a date:

| cell | sessions | mean diff | interval | pairs vs zero |
|---|---|---|---|---|
| all_five (E240 replay) | 1328 | +0.0079 | [-0.316, +0.332] | 9 / 20 |
| pre2020_four | 892 | +0.0885 | [-0.229, +0.406] | 5 / 12 |
| era_2020_2022 | 474 | -0.0002 | [-0.520, +0.520] | 5 / 20 |
| era_2023_2024 | 446 | +0.0026 | [-0.503, +0.508] | 8 / 20 |
| era_2025_now | 408 | +0.0264 | [-0.626, +0.679] | 5 / 20 |
| loo_drop_sh510300 | 1343 | +0.0405 | [-0.299, +0.380] | 5 / 12 |
| loo_drop_sh510050 | 1351 | +0.0188 | [-0.331, +0.368] | 6 / 12 |
| loo_drop_sh510500 | 1337 | -0.0021 | [-0.341, +0.336] | 5 / 12 |
| loo_drop_sh512100 | 1350 | +0.0109 | [-0.338, +0.360] | 5 / 12 |
| loo_drop_sh588000 | 2262 | +0.0313 | [-0.198, +0.260] | 7 / 12 |

Rollup verdict: **`additivity_only_in_the_mean`**. The mean difference covers zero; the pairs do
not agree. Nine of twenty ordered pairs in the headline cell have their own interval clear of
zero, with both signs -- so some counterparties carry more than an equal share of the "rest"
channel and others carry less, and the mean is their cancellation.

## Three findings, in order of how much they change the family's reading

1. **E240's interval was the wrong object.** [+/-0.012, +0.022] is the spread of 20
   heterogeneous pair estimates divided by sqrt(20). That is the standard error of a MEAN of
   heterogeneously-identified quantities; it measures how well the mean is pinned, not whether
   the difference is identified. Each pair's own HAC interval is +/-0.13 (E240's own `cases`
   block) and the five-member cell's conservative interval is +/-0.32. A cell whose interval is
   wider than `RESOLUTION_MAX = 0.10` is published as `unresolved_interval_too_wide`, never as
   additive (E199's NOT-ASSESSED rule, applied to a verdict rather than to a block).

2. **The pooled aggregator reports exactly zero, always.** E240 published
   `pooled.diff = -4.1e-15` next to the pair mean, and that zero corroborated the verdict. It is
   an artifact. The pooled stack replicates one member's response vector across its k-1
   counterfactual "one counterparty" blocks; the direction that separates `b_one` from
   `b_rest3` is annihilated by that replication and the solver returns the symmetric split.
   `pooled_split_is_an_artifact` proves it on every run: three fixtures whose truths differ by
   +0.88, -0.55 and 0.00, and the pooled difference is at most 3.2e-15 in all three while the
   pair design reads the gap. A design that cannot see a regressor must publish
   `identifies: false`, never a number (E239 family, E236's date-FE sibling).

3. **The per-pair statistic is not a pair.** `b_one - b_rest` prices ONE member against the SUM
   of k-2 others, so its sign and size are properties of the sum's composition, not of the
   counterparty. That is why 9/20 pairs disagree with mixed signs: the design has no single
   difference to estimate when the rest channel is heterogeneous. Seeded as **E244**: regress
   each member on every other member separately (full slope matrix, no sum regressor) and test
   whether its rows are equal (a coherent rest channel) or concentrated (a star structure).

## What did not change

No bill, no charge, no adoption. The face re-prices a published VERDICT, not a price. `no_bill:
permitted: false` is on the face and the smoke leg asserts it.

## Reproduce

    python scripts/e243_additivity_out_of_sample.py selftest   # 14/14
    python scripts/e243_additivity_out_of_sample.py run        # ~16s
    python scripts/e243_additivity_out_of_sample.py artifact   # the pooled proof alone