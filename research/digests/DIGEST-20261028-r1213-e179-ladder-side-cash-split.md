# E179 — the ladder side's zero, cut into its five members and the cash residual (r1213 bm-b, 2026-10-28)

Face: `results/e43_tilt_4member/LADDERSIDECASH-20261027.json`
Leg: `python scripts\e39_panel_census.py tilt3laddersplit` (e39 selftest 578 -> 590)
Pool: E179-LADDER-SIDE-CASH-SPLIT (claimed r1213, done this round)
Card: E179 in `knowledge/METHODOLOGY_ASSETS.md`

## Question

E176 published `ladder_book_delta_bp = 0.0` in every era and used it to say "the fixed leg
never moves, the whole engine delta is the wide book". That number is a **sum** over the five
fixed members plus the `__cash__` residual the leg books. A zero sum is three different
claims: every holding stayed put; two holdings moved in opposite directions and cancelled; or
none of the holdings was in the repair set. Only the first is evidence about the strategy.

## Findings

1. **The zero is per holding, not merely net.** `gross_abs_delta_bp = 0.0` in all five eras,
   so `classification = flat_per_holding` and `eras_cancelling = []`. Every published holding
   reads `raw_level_bp == screened_level_bp` to three decimals, which is the amplification of
   E178's membership fact down to the holding: the repair touched 67 names at this cutoff and
   none of them is a ladder member (`ladder_members_neutralised: []`).
2. **"The fixed book is five names" is era-dependent.** pre2017 holds three members
   (510050 / 510300 / 510500), 2017_2020 holds four (adds 512100), and only 2021_2023 onward
   holds all five (adds 588000). The face publishes `members_missing` per era rather than
   weighting an absent member to zero, so a reader quoting "the five-name ladder" for 2014 is
   quoting a book that did not exist.
3. **The cash residual is a warm-up artifact, and its size is published.** `__cash__` books in
   exactly 15 months of the panel (2012-05 … 2013-07), all before the month the whole fixed
   book could first be held (2021-12, derived from member coverage). Two eras overlap those
   months: pre2017 and full carry 3.00% and 1.39% of the ladder level as cash. The residual is
   labelled `cash_residual` / `is_security = false` so no reader can mistake it for a holding.
4. **The levels are also the interesting disclosure.** The ladder side's own level is not flat
   across eras: pre2017 +1018.2bp on three names with 510500 alone carrying 61.9% of it,
   2017_2020 +1004.8bp on four, 2021_2023 -923.5bp on five (588000 -298.6bp, i.e. 32% of the
   level), 2024_now +1088.6bp (588000 +447.9bp, 41%). The per-holding shares are the audit
   trail for any later "the ladder lost 2021_2023" sentence.
5. **The net side joins the E176 face on disk.** `e176_join_max_abs_diff_bp = 0.005`, which is
   the print quantum between E176's 2dp and this face's 3dp — the split is the same
   computation, not a second engine pass.

## What this does not say

- It says nothing about the wide book. E176 already established that every moved era is
  `wide_only`; this face only refuses to let a net zero stand in for five holdings.
- The per-holding LEVELS sit apart from the compounded published levels by the E177 offset;
  they are quoted for their shares, never as an engine level.

## Reproduce

```
python scripts\e39_panel_census.py tilt3laddersplit
python scripts\e39_panel_census.py selftest      # 590/590
```

Two consecutive runs produced byte-identical faces
(sha256 prefix `fe8b68219fea608d`, 63,389 bytes).