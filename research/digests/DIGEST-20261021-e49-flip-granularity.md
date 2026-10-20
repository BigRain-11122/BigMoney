# DIGEST 2026-10-21 — E49: the flip count is a cut artefact, not a property of the eras

**Faces**: `results/e46_live_span/LIVESPAN-20261020-x0-p4.json`,
`results/e46_live_span/LIVESPAN-20261020-x3-p4.json`
**Runner**: `python scripts/e39_panel_census.py livespan --cost {0,3} --parts 4` (evidence cutoff 2026-10-20)
**Chain**: E41 era decay → E45 burn-in → E46 halves → E47 zero-cost halves → E48 zero-cost thirds → **E49 quarters**

## What was asked

E48 read "3 of 4 eras flip internally at zero-cost thirds" and E47/r1124 read "1 of 4 at
halves". E49 asked whether the flip count only tracks the number of cuts taken, and whether
the quarters cut at real fees (x3) removes any of those flips.

## What came back

| era | parts at cost x0 | flip | parts at cost x3 | flip |
|---|---|---|---|---|
| pre2017 | 211, 366, -398, 533 | yes | 210, 349, -408, 525 | yes |
| 2017_2020 | -27, 734, 196, 586 | **yes** | -26, 724, 181, 558 | **yes** |
| 2021_2023 | 78, 267, 579, 67 | **no** | 59, 253, 570, 69 | **no** |
| 2024_now | 555, 47, -196, -161 | yes | 548, 34, -210, -173 | yes |

Era levels (bp): 239 / 423 / 247 / 93 at x0, 230 / 410 / 237 / 81 at x3 — an 8–13bp shift,
exactly the fee scale E48 measured at thirds.

## Verdict (honest)

1. **Fees are irrelevant to the flip structure.** x3 reproduces the x0 parts to within ~10bp
   and never changes a sign inside an era. Whatever the internal instability is, turnover did
   not buy or cause it.
2. **The flip count is a coincidence of the cut, not a property of the eras.** Both thirds and
   quarters give 3 of 4, but the *set* is different: 2021_2023 flips at thirds and not at
   quarters; 2017_2020 does the opposite. Only `pre2017` and `2024_now` flip at every cut of
   2 or more. Reporting "3 of 4 eras flip" as a structural fact would have been wrong.
3. **Part band grows with granularity**, so bands are not comparable across cuts:
   pre2017 41 → 403 → 931 bp, 2017_2020 30 → 353 → 761, 2021_2023 195 → 637 → 512,
   2024_now 595 → 670 → 751 (halves → thirds → quarters). Any "era is stable/unstable" claim
   must name its cut.
4. **The newest era's strength is its opening quarter**: 2024_now parts read +555, +47, -196,
   -161, so the era's +93bp mean is carried by the first quarter alone and the rest of the era
   is negative. That is a live reading worth its own unit (seeded as E50/LIVESPAN p5 legs).

## Consumption

Pool units `E49-FLIP-GRANULARITY-P4` and `E49-FLIP-GRANULARITY-P4-X3` closed by r1125 bm-b.
Ready floor refilled to 3 with `E44-MIDMONTH-WEAKNESS` (needs a runner), `E50-PARTS-P5`,
`E50-PARTS-P5-COST-X3`.