# DIGEST 2026-10-26 — E81 leg 2: the size-neutral spread grew when the split prints left

**Leg**: `python scripts\e39_panel_census.py screenspread` (mode added this round)
**Face**: `results/e42_spread_size_neutral/NEUTRAL-20261023-screened.json`
**Untouched twin**: `results/e42_spread_size_neutral/NEUTRAL-20261023.json` (published face, never rewritten)
**Spec**: E42 spread-size decomposition (`spread_m = alpha + beta*tilt_m`), month-end decision
calendar, `pick_n` 9999, cost x1, cutoff 2026-10-23, eras pre2017 / 2017_2020 / 2021_2023 /
2024_now. Arms: `unscreened`, `neutralise_int` (integer-ratio prints only), `neutralise`
(every adjacent print past the 30% screen).

## Why this leg exists

E42's surviving claim is a size-neutral number: "the vs-ladder spread is a size tilt, and what
is left over is positive". That number is equal-weight and read from the **as-traded** panel,
so a share-split print inside the wide book is charged at weight 1/n — the exact defect E81
screened out of the calendar face last round (r1276). This leg rebuilds the *whole* monthly
core per arm — the two engine curves **and** the member tilt series — so the regression and its
regressor move together and the arms differ only in the closes handed in.

## What moved (bp per year)

| era | column | unscreened | `neutralise_int` | `neutralise` |
|---|---|---|---|---|
| 2021_2023 | raw spread | +251.1 | +298.2 | +389.9 |
| 2021_2023 | size component | -75.3 | -73.4 | -77.4 |
| 2021_2023 | **size-neutral (alpha)** | **+326.4** | **+371.6** | **+467.3** |
| 2024_now | raw spread | **-58.5** | +126.2 | +278.9 |
| 2024_now | size component | -220.0 | -214.0 | -211.1 |
| 2024_now | **size-neutral (alpha)** | **+161.5** | **+340.2** | **+490.0** |
| full | size-neutral (alpha) | +260.6 | +369.2 | +489.5 |

Four readable facts:

1. **The size component does not move; the raw spread does.** -220.0 / -214.0 / -211.1 across
   arms — the tilt story is untouched by the screen (9bp of 220). Everything the screen moves
   lands in the alpha term, because the raw spread and the alpha are the same leg.
2. **"The newest-era raw spread is negative" was an artefact.** -58.5 → +278.9bp, a 337bp
   move at the strict arm. The published reading ("raw negative, tilt explains it, +161bp left
   over") had the sign of the first term wrong, so the *share of the spread explained by size*
   (376% unscreened) was never a real ratio.
3. **The surviving claim survives, at roughly twice the size.** Alpha stays positive in every
   era of every arm, and the arithmetic identity `raw = neutral + size` holds in all three
   (±0.25bp). Newest-era alpha 161.5 → 490.0bp; full 260.6 → 489.5bp.
4. **The band collapses while the level doubles** — same shape as the calendar leg: max−min
   over eras 164.9 → 31.4 → 22.7bp because all eras move up together. Mean level 243.9 →
   355.9 → 478.6bp. Read the level beside the band or the shift hides.

## The contamination is concentrated, and it is nameable

Repaired prints by era (`neutralise`, 135 events): pre2017 0, 2017_2020 2, 2021_2023 24,
**2024_now 109** — 81% of the repair sits in the live era, which is exactly where the headline
lives. Integer-ratio only (`neutralise_int`, 65 events): 9 in 2021_2023, **56 in 2024_now**.
Sample of the live-era names (full list in the face): `sh510100` 2025-03-10 +100.0% (2:1),
`sh510310` 2024-09-23 +100.9% (2:1), `sh510580` 2024-09-02 +295.5% (4:1), `sh512000`
2025-08-04 -49.7% (1:2), `sh512480` 2026-07-03 -50.7%, `sh512760` 2026-03-27 -49.8%,
`sh512800` 2025-07-07 -49.7%, `sh512810` 2025-06-23 -49.2%.

## Reading rule this leg confirms

E81's rule — a band statistic is blind to a common shift — reproduces on a second face, one
round apart, with the same direction (level up, band down). Any published "the eras are
within Xbp of each other" must be accompanied by the level, and any screened band by its
unscreened twin.

## Honest limits

- Only two eras carry data: the four-member tilt skin cannot price pre2017 / 2017_2020, so the
  band is a two-point spread, not a four-point one.
- The screen repairs both the wide book **and** the tilt members, so a moved alpha is net of
  both legs and cannot be attributed to one of them.
- Repairing an integer-ratio print is a sensitivity, not a correction: an ETF whose daily limit
  differs from the 10%/20% stock band can print >30% for real.
- The unscreened arm is rebuilt in this leg rather than copied from the published file. It is
  the same code path on the same panel — the default path was proved byte-identical against
  `HEAD` before the new mode ran (`spreadsize` output identical), and the run is idempotent.
- Descriptive census only: no gate, no verdict, no ledger booking, trial 0.