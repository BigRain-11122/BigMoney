# r1241 / E214 — the off-book thick-name effect, read across every era the panel covers

**Face:** `results/e44_midmonth/OFFBOOK-ERA-20261028.json` (study `e214_offbook_liquidity_era_stability`)
**Runner:** `python scripts/e39_panel_census.py offbookera` (new CLI mode; re-uses the E60 leg rather than re-deriving it)
**Method card:** E214 · **Chain:** S6 leg `offbookera` (24/24 rc=0 this round)

## Why

E60 (r1240) split the off-book bucket by liquidity tercile and published an era table, then said the
thick-name penalty "is not stable in sign across eras either" on the strength of **two** readings:
2021_2023 thick gap −1.584 pp against 2024_now +3.774 pp. One forward and one reverse is a difference,
not a flip. The panel starts 2012-05-28, so the span can be carried back far enough to buy a third era.

## What this leg does

`run_offbookera` calls `run_offbookliq` with a wider start (`--span-start`, default 2017-01-01) so the
era table covers 2017_2020 in addition to 2021_2023 and 2024_now, then adds a cross-era classifier
`_offbook_liq_era_stability` that answers the question two readings cannot: how many counted eras agree
on the sign of the thick-bucket calendar gap, and how big is the worst disagreement.

Nothing is re-priced and no threshold is re-tuned: the tercile cuts, the bucket definition and the
per-swap readings come from the E60 code path unchanged.

## Reading

| era | thick gap (mean) | thick gap (median) | thick priced slots | counted? |
|---|---|---|---|---|
| 2017_2020 | +4.288 | +2.301 | 15 | **no** — below the 20-slot floor |
| 2021_2023 | −1.626 | −1.435 | 84 | yes |
| 2024_now | +3.601 | +1.547 | 113 | yes |

Verdict, both aggregators: `thick_gap_sign_flips_across_eras` (spread 5.227 pp on means, 2.982 on
medians; `measured_eras=2`).

Two things are load-bearing:

1. **The era that disagrees is 2021_2023, not the early panel.** The newly reached 2017_2020 window
   prints on the *same* side as the newest era (+4.288). The E60 sentence implied the effect drifted
   over time; what the wider span shows is one disagreeing window sandwiched between two agreeing ones.
2. **That window still does not get a vote.** Its thick disjoint cell holds only 15 priced entrants, so
   it is published under `excluded_eras` with its reading intact. Counting it would have let a 15-name
   cell decide the verdict; dropping it silently would have hidden the strongest hint about the shape.
   At the floor it buys the third era nothing — `measured_eras` stays 2.

## Caveats

- The tercile cuts are re-computed on the wider pooled distribution, so these per-era gaps (−1.626 /
  +3.601) are **not** the E60 face's numbers (−1.584 / +3.774) and must not be joined across faces.
  The face carries this in its `honest` block.
- `fwd_pct` is the raw decision-to-decision return of the name: no weighting, no cost, no cash leg.
- One mid-month date (day 15) against one month-end date: the calendars are fixed, not swept.
- Descriptive census only: no gate, no strategy verdict, no prereg, no trial count.