# DIGEST 2026-10-21 — broad equal-weight book, post-2020 slice (E36-BROAD-EQ-2020)

Unit: `E36-BROAD-EQ-2020` (pool, bm-b r1109). Result face:
`results/e36_broad_eq_2020/UNIV-4170ac-s20200101-xsh511-20261021.json`
(evidence_cutoff 2026-10-20, bars 1645, 6.53y, universe 1243, excluded prefix `sh511`,
cost 13.041 bp/side, cost x1).

## Question

r1106 read the broad book on 2018+ and got +265.9 bp/yr at t=1.29, but 1.5y of that
window is the 2018 drawdown. Does the sign survive on the cleanest recent window
(2020-01-02 onward)?

## Answer

Yes — sign holds, strength does not.

| scheme | ann % | vol % | sharpe | rebal | cost bp/yr |
|---|---|---|---|---|---|
| ladder5 (frozen five) | -0.43 | 18.75 | 0.071 | 69 | 4.9 |
| top9999 (all eligible equity ETFs, equal weight) | +1.60 | 16.55 | 0.179 | 69 | 8.9 |

Gap: **+215.5 bp/yr**, monthly mean +17.69 bp over 82 months, **t = 0.89** (not significant).
The book also runs *lower* vol than the frozen five (16.55 vs 18.75) while paying 8.9 bp/yr
of turnover cost.

The 2018+ run gave +265.9 bp/yr (t 1.29); post-2020 gives +215.5 bp/yr (t 0.89). Same sign,
roughly two-thirds the magnitude, both short of significance — so the earlier read is not a
2018-drawdown artefact, but neither read is strong enough to call an effect.

## Era detail (monthly gap vs ladder5)

| era | months | mean bp/month |
|---|---|---|
| 2017-2020 (pre-window months inside the 82) | 12 | 0.00 |
| 2021-2023 | 36 | +18.10 |
| 2024-now | 34 | +23.49 |

The monthly gap rises monotonically across eras with no sign flip. Twelve months of
pre-window borrowing at 0.00 is the constitution of the panel, not a measurement.

## What this does and does not license

- Does: supports the r1106 statement that breadth is not a bond-leg or 2018 artefact; the
  next honest test is the concentration cut (N=10) already burned as `E36-CONCENTRATION-N`.
- Does not: license any registration. t = 0.89 on the cleanest window; three N values read
  in sequence is a multiple-comparison surface (see the `E36-CONCENTRATION-N` note).
- Coverage caveat stands (r1106 / E30): the live-mark line goes eligible 0 (2020) -> 491
  (2023) -> 468 (2026); the 2020-2022 book is thinner than today's, and the panel refresh
  leg only became real on 2026-10-20. Sign consistency across the ladder is the claim; the
  absolute level is not.

Descriptive measurement only: zero prereg, zero judgement, zero ledger booking, trial_count 0.

## Companion unit: E36-CONCENTRATION-N (same round)

Unit E36-CONCENTRATION-N (N=10 tightest book, 2018-01-02, 8.46y, 106 months), result face

esults/e36_concentration_n10/UNIV-b1d578-s20180101-xsh511-20261021.json:

| scheme | ann % | vol % | sharpe | cost bp/yr |
|---|---|---|---|---|
| ladder5 | 5.48 | 19.64 | 0.370 | 4.1 |
| top10 | 3.52 | 20.00 | 0.273 | 18.3 |

Gap **-173.7 bp/yr**, monthly mean -11.81 bp, t = -0.48. Era split (monthly gap vs ladder5):
2017-2020 -44.91 (36m), 2021-2023 +1.25 (36m), 2024-now +9.39 (34m).

So the wide book is not a handful-of-names effect: at N=10 the sign is *negative* over the full
window and only mildly positive in the recent era, while the 1231-name book is +265.9 bp/yr
(2018+) and +215.5 bp/yr (2020+). The 2024-now monthly gradient runs 0 (N=5) -> +9.39 (N=10) ->
+23.49 (N=all) bp/month, i.e. monotone in breadth. That gradient is the finding worth carrying;
no single N is significant on its own and reading three in sequence is a multiple-comparison
surface.


## Third unit: E36-XSH511-SENS (same round) -- what the sh511 exclusion is worth

Unit `E36-XSH511-SENS` re-ran the 2018+ wide book with the sh511 money/bond block INCLUDED
(universe 1289 vs 1231). Result face
`results/e36_xsh511_included/UNIV-4170ac-s20180101-20261021.json`:

| 2018-01-02, 8.46y | ladder5 ann % | top9999 ann % | vol % | gap bp/yr | t |
|---|---|---|---|---|---|
| sh511 EXCLUDED (E35-BROAD-EQ-2018) | 5.48 | 8.04 | 16.55 | +265.9 | 1.29 |
| sh511 INCLUDED (this unit) | 5.48 | 7.44 | 16.26 | +199.3 | 0.95 |

The exclusion is worth about 66 bp/yr: the bond/money block supplies roughly a quarter of the
wide-book gap and none of its significance. So the effect is not a bond-leg artefact, but a
non-trivial slice of it is a duration/cash carry that would not behave the same in a different
rate regime -- worth keeping the exclusion as the honest default and pricing it every time the
window changes (queued as `E37-XSH511-POST2020`).

## Supply floor refilled (r1109)

All three E36 units are closed; three E37 units seeded off these readings:

- `E37-BREADTH-LADDER` -- sweep N in {5,10,25,50,100,250,all} inside ONE run on one window
  (2021-01-01+), so the breadth gradient is a single readable family instead of three runs.
- `E37-XSH511-POST2020` -- the included/excluded pair on the clean post-2020 slice.
- `E37-BREADTH-COST-X3` -- post-2020 wide book at cost x3, before anyone treats +215.5 bp/yr
  as real.
