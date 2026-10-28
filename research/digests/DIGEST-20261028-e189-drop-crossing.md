# DIGEST 2026-10-28 · E189 drop-curve crossing and the carrier-removal test (r1220 bm-b)

**Question.** E186 measured that four (era, drop) pairs reverse sign between the
summed and the compounded reading while no single month disagrees in sign, and
named for each pair the month carrying the largest share of the |gap|. Does that
reversal survive removing the month the study itself called its carrier?

**Deliverable.** `results/e43_tilt_4member/LADDERDROPCROSS-20261027.json`
(mode `tilt3ladderdropcross`, `scripts/e39_panel_census.py`, selftest 644->651,
panel_screen 39/39). Reads the published E186 month rows and rebuilds both era
effects from them (join max |diff| 8.8e-05bp, so the face is reproduced, not
re-burnt).

**Finding.** All four reversals are carrier artefacts.

| era | drop | carrier | arith bp (before -> after) | comp bp (before -> after) | reversal after removal |
|---|---|---|---|---|---|
| 2024_now | sh510050 | 2026-07 | 73.16 -> 204.25 | -34.01 -> 141.93 | no |
| full | sh510050 | 2014-12 | 0.07 -> 44.89 | -38.20 -> 1.63 | no |
| pre2017 | sh510300 | 2016-01 | -32.57 -> -103.85 | 6.18 -> -95.56 | no |
| pre2017 | sh510500 | 2014-12 | 36.58 -> -197.98 | -9.66 -> -203.73 | no |

Three secondary reads:

1. **The crossing month is never the carrier (0/4).** Where the two cumulative
   paths turn past each other (2013-09 / 2013-09 / 2014-05) is a different event
   from the month that carries the |gap| (2026-07 / 2014-12 / 2016-01 / 2014-12),
   so neither can be reported as the other.
2. **One pair reverses with no crossing at all.** 2024_now sh510050 ends with a
   +296.5bp path gap that never changes sign: E186's `comp` is the difference of
   two annualised levels while `cum_link` compounds the ratio steps, so the sign
   disagreement lives in the annualisation. Published in
   `reversals_without_path_crossing` so the crossing count cannot imply a turning
   point that does not exist.
3. **E186's dispersion labels did not predict fragility.** Carrier share
   0.118-0.358 and 5.45-25.36 effective months read as "spread", yet every pair
   dies at k=1. Concentration is not the same measurement as fragility.

**Consequence.** "The drop effect reverses at era level" is withdrawn for all four
pairs; each is one month wearing an era verdict. The follow-up that measures how
much trimming a pair tolerates (k=1..8 by |gap|, by |delta_sum|, and by era edge)
is seeded as pool row `E190-DROP-FRAGILITY-SWEEP`.

**Reusable.** Card E189 in `knowledge/METHODOLOGY_ASSETS.md`: re-run a published
reversal without its declared carrier; keep crossing month and carrier month as
separate objects; give sign-disagreement-without-crossing its own bucket.