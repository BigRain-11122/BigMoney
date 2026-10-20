# DIGEST 2026-10-21 — E50: fifths settle the flip set, and two earlier claims do not survive

**Faces**: `results/e46_live_span/LIVESPAN-20261020-x0-p5.json`,
`results/e46_live_span/LIVESPAN-20261020-x3-p5.json`
**Runner**: `python scripts/e39_panel_census.py livespan --cost {0,3} --parts 5` (evidence cutoff 2026-10-20)
**Chain**: E41 era decay → E45 burn-in → E46 halves → E47 zero-cost halves → E48 thirds → E49 quarters → **E50 fifths**

## What was asked

E49 showed the flip *count* agreed at thirds and quarters while the *membership* swapped.
E50 asked whether the two finest cuts agree on the set, and whether the fifths bands keep
growing the way r1124/r1125 reported at coarser cuts.

## What came back

| era | parts at cost x0 | flip | parts at cost x3 | flip |
|---|---|---|---|---|
| pre2017 | 0, 710, -859, 667, 157 | yes | 0, 702, -895, 663, 151 | yes |
| 2017_2020 | -74, 773, 42, 502, 753 | **yes** | -87, 773, 30, 483, 725 | **yes** |
| 2021_2023 | 116, 161, 462, 325, 168 | no | 95, 158, 446, 309, 172 | no |
| 2024_now | 511, 578, -180, 110, -561 | yes | 504, 560, -192, 99, -574 | yes |

Era levels are cut-invariant as always: 239 / 423 / 247 / 93 bp at x0, 230 / 410 / 237 / 81 at x3.

## Verdict (honest)

1. **The flip set converges at the two finest cuts.** p4 and p5 give the identical set
   {pre2017, 2017_2020, 2024_now}. Across all cuts of 2+: halves {2024_now},
   thirds {pre2017, 2021_2023, 2024_now}, quarters and fifths {pre2017, 2017_2020, 2024_now}.
   The stable claim is *`pre2017` and `2024_now` flip at every cut of 2 or more; `2021_2023`
   flips at exactly one cut (thirds) and `2017_2020` at all but halves and thirds.*
2. **"Part bands grow monotonically with granularity" is refuted — by r1125's own table.**
   Read the 2021_2023 row across cuts: 195 (halves) → 637 (thirds) → 512 (quarters) → 346
   (fifths). The mid-era band peaks at thirds and then *contracts*; r1125 printed the first
   three numbers and asserted monotonicity anyway. Only pre2017 grows without exception
   (41 → 403 → 931 → 1569); 2017_2020 (30 → 353 → 761 → 847) and 2024_now
   (595 → 670 → 751 → 1139) grow but flatten.
3. **The dead fifth of pre2017 is real but innocent.** Its first part is 224 bars,
   2012-05-29..2013-05-02, both legs byte-identical at +3.21%/yr with maxDD 0.0 — the whole
   fifth is repo, the 259-session eligibility burn-in E44 measured. It contributes a hard
   `0.0` bp part, yet it neither creates the flip nor widens the band: the four live parts
   alone span -859..+710 bp, the same 1569 bp range, and the sign change exists without it.
   What it does do is put a fake flat stretch in the parts series, so any reader treating
   each fifth as a selection reading is looking at a bank account.
4. **Fees still do not decide anything.** x3 moves every part inside ~15bp, changes no sign,
   and moves the bands by at most 28bp (1569→1597, 847→860, 346→351, 1139→1134).
5. **Live reading carried forward:** 2024_now's +93 bp is its first two fifths (+511, +578);
   the last fifth (2026-03-31..2026-10-20) is **-561 bp**, the most negative part anywhere in
   the grid. 2021_2023 is the only era whose five parts are all positive, i.e. the only era
   where the era headline is a fair summary of its own stretches.

## Consumption

Pool units `E50-PARTS-P5` and `E50-PARTS-P5-COST-X3` closed by r1126 bm-b. Ready floor
refilled with `E51-PARTS-P6` and `E51-PARTS-P6-COST-X3` (sixths, x0/x3) so the floor is met
with commands autofill can ignite; `E44-MIDMONTH-WEAKNESS` stays authoring-blocked (no leg).