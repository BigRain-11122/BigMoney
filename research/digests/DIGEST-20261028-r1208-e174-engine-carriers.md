# E174 — who carries the engine column's repair move (r1208 bm-b, 2026-10-28)

Face: `results/e43_tilt_4member/TILT3SIGNNAMES-20261027.json`
Leg: `python scripts/e39_panel_census.py tilt3signnames` (e39 selftest 552 -> 558)
Pool: E174-TILT3SIGN-ENGINE-MOVE-NAMES (done, this round)
Card: E175 in `knowledge/METHODOLOGY_ASSETS.md`

## Question

E171 published that the split-event repair moves the ENGINE column (wide book
minus ladder book) and not the tilt column, and that 2024_now's era sign verdict
flips from disagree to agree as a result (+46.7bp on the engine level). An era
delta on a 4-of-17-month reading is not auditable: the engine column is a
difference of two held books, so it can in principle rest on ONE name-month.
E174 decomposes it and asks whether the flip survives dropping its biggest
carrier.

## Method (mechanism, not a second implementation)

`e27.simulate` gained an optional `contrib` sink that books each day's `w * r`
under `(YYYY-MM, symbol)`; the un-invested residual is booked under `__cash__`.
`_monthly_core(contrib=True)` therefore carries BOTH books' per-name arithmetic,
and the engine series' decomposition is just `wide - ladder` per (month, name).
Every number below is in annualised bp of its era (mean monthly x 12 x 1e4), the
same scale the published engine column uses. `contrib=None` (the default) costs
nothing and leaves every existing face untouched.

## Findings

1. **Only three of five rows moved, and that is the first answer.** pre2017 and
   2017_2020 read `engine_bp_delta = 0.0` exactly: the repair does not touch the
   engine level there at all, so those two eras have no delta to attribute and
   the face publishes `carriers: []` with the reason instead of naming a "top
   carrier" beside a zero.
2. **The surviving moves are spread, not one name.** 2021_2023 (+29.3bp) needs 2
   names for 50% and 3 for 80%; its top carrier `sz159806` is 8.72bp = 29.8%.
   2024_now (+46.7bp) needs 3 names for 50% and 6 for 80%; its top carrier
   `sh510580` is -14.51bp = -31.1%. `eras_where_delta_is_one_name = []` on the
   published 50% rule.
3. **Each carrier is a single repair month.** `sh510580` earns its whole -14.51bp
   in 2024-09 alone (`sh510310` -6.18bp in the same month, `sz159925` -5.56bp in
   2024-01, `sh510100` -4.58bp in 2025-03, `sh561980` +4.14bp in 2026-06). The
   era delta is a handful of split-event months, not a persistent tilt.
4. **The 2024_now flip does not survive dropping its top carrier.** Removing
   `sh510580` from both arms leaves raw +14.86bp vs screened +78.97bp -- both
   positive, verdict agrees, flip gone. Removing the top five re-creates the
   disagreement (raw -4.48 vs screened +72.08). So the flip is not "a book
   property that survives attribution"; it is a composition-dependent reading of
   a few repaired months, and the two drop sizes disagree with each other. The
   honest headline is: **the 2024_now era verdict is not robust to which carriers
   are in the set**, which is a stronger statement than E171's "the repair flips
   the verdict".
5. **Arithmetic residual is quoted, not zeroed.** 2024_now's carriers sum to
   49.6bp against a 46.7bp delta (-2.90bp residual), 2021_2023 -0.90bp, full
   -0.82bp; the gap is intra-month compounding, which is not additive, and the
   face publishes the max residual so a reader can see the attribution is tight
   rather than assumed.

## What a reader should now say differently

E171's "the repair flips 2024_now's verdict" should be read as "the repair moves
2024_now's engine level by +46.7bp, spread over six names whose carrier set
decides whether the era signs agree". Anything quoting the era comparison as a
stable fact about the books is quoting a data-repair composition.