# DIGEST 2026-10-21 — E51 livespan sixths (parts=6, x0 and x3)

Descriptive census on the unchanged census leg (`scripts/e39_panel_census.py livespan --parts 6`).
Zero prereg, zero judgement, zero ledger booking, `trial_count 0`.

## Faces

| face | path |
|---|---|
| x0 | `results/e46_live_span/LIVESPAN-20261020-x0-p6.json` |
| x3 | `results/e46_live_span/LIVESPAN-20261020-x3-p6.json` |

## x0 sixths (era bp / six parts bp / band)

| era | era_bp | parts | band | widest part |
|---|---|---|---|---|
| pre2017 | 239 | 0, 373, 394, -649, 182, 460 | 1109 | 6 |
| 2017_2020 | 423 | -242, 555, 717, 29, 501, 641 | 959 | 3 |
| 2021_2023 | 247 | 194, -280, 520, 737, 419, -93 | 1017 | 4 |
| 2024_now | 93 | 627, -348, 520, 77, -424, -185 | 1051 | 1 |

**All four eras flip internally at sixths** — the first cut in the series where the count saturates at 4/4.

## x3 sixths

210/349-style re-read at triple fees:

pre2017 230 (0, 363, 377, -641, 166, 456) band 1097 ·
2017_2020 410 (-248, 557, 707, 13, 485, 609) band 955 ·
2021_2023 237 (169, -275, 495, 733, 404, -87) band 1008 ·
2024_now 81 (621, -363, 512, 59, -436, -198) band 1057.

Identical flip set, every part inside 13bp of x0, bands move <= 12bp, era levels -8..-12bp
(239/423/247/93 -> 230/410/237/81). Fees are not the deciding axis at this granularity —
consistent with quarters and fifths.

## Cross-cut read (flip count and membership)

| cut | flip count | flip set |
|---|---|---|
| halves | 1 | {2024_now} |
| thirds | 3 | {pre2017, 2021_2023, 2024_now} |
| quarters | 3 | {pre2017, 2017_2020, 2024_now} |
| fifths | 3 | {pre2017, 2017_2020, 2024_now} |
| sixths | 4 | all four |

Count is non-decreasing but plateaus at 3 for two cuts before jumping to 4; membership is not
monotone either. **Correction to r1126:** the claim "the flip set settles at the two finest cuts
{pre2017, 2017_2020, 2024_now}" is withdrawn — one more cut added 2021_2023, so "settles" was a
two-point coincidence. What survives: `pre2017` and `2024_now` flip at every cut >= 2.

## Band law

`2021_2023` band across cuts: 195 / 637 / 512 / 346 / 1017 (halves .. sixths) — still not
monotone (r1125's monotone claim was already withdrawn at r1126). No band law exists; any
"era is stable" statement must name its cut and its band.

## Carry-forward live reading

- `2024_now`'s +93bp mean is its first part (+627 at sixths, +511 at fifths) — the last two
  parts of the era are negative (-424, -185). The era's positive mean is an opening-stretch effect.
- `2021_2023` is the only era whose parts were all positive at fifths; at sixths its first and
  last parts turn negative (-280 / -93), i.e. the mid-era is the only clean stretch in the book.
- `pre2017`'s dead first sixth is still 0.0bp (259-session burn-in, both legs byte-identical,
  maxDD 0.0), sits inside the live range and neither creates the flip nor widens the band; it
  puts a fake flat stretch in the parts series.

## Pool

2 units closed with result_ref (`E51-PARTS-P6`, `E51-PARTS-P6-COST-X3`), 2 seeded
(`E52-PARTS-P7`, `E52-PARTS-P7-COST-X3`) — ready 3 (incl. the still authoring-blocked
`E44-MIDMONTH-WEAKNESS`), floor met.