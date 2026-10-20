# DIGEST 2026-10-21 — E42: the spread is size exposure, and the calendar band is not a fee

Three legs burned in one pass (r1117, bm-b). Script: `scripts/e39_panel_census.py`
(`spreadsize` / `tiltera` / `calcost`, selftest 36/36). Faces:
`results/e42_spread_size_neutral/NEUTRAL-20261020.json`,
`results/e42_tilt_era/TILT-ERA-20261020.json`,
`results/e42_calendar_cost/COST-20261020.json`. Cutoff 2026-10-20, 1,265 members,
ladder5 vs wide_top9999, one rank cache, cost x1 unless stated. Descriptive only:
zero prereg, zero judgement, zero ledger booking, trial_count 0.

## 1. The newest era's thin spread is the size leg, not the selection

Monthly (wide − ladder) gap regressed on the monthly small-minus-large tilt
(the E40 series, same 20% corporate-action guard):

| era | months | raw spread (additive) | size-neutral (alpha×12) | size component | beta | R² | share from size |
|---|---|---|---|---|---|---|---|
| 2021-2023 | 36 | +251.1 bp | **+326.4 bp** | −75.3 bp | −0.124 | 25.0% | −30% |
| 2024-now | 34 | **−35.1 bp** | **+181.2 bp** | **−216.3 bp** | −0.289 | 59.5% | +616% |
| full | 71 | +138.2 bp | +270.7 bp | −132.5 bp | −0.216 | 44.3% | −96% |

Reading: with the size leg flat, the wide book keeps a **+326bp then +181bp**
advantage — both eras positive, range only 145bp. What flipped in the newest era
is the size exposure: small caps lead by ~748bp/yr there (below), and the wide
book is loaded the other way, so a +181bp selection edge is handed back as
−216bp of tilt. The raw number is not the strategy decaying; it is the
environment turning against its size loading.

E41's `+89bp` for the same era is the **geometric** annualised difference of the
two curves. The additive monthly mean is `−35.1bp`. Both are in the face
(`engine_ann_diff_bp` / `arithmetic_vs_geometric_gap_bp`); the gap reaches
**124bp**, so the convention must be stated in every quote. The decomposition is
additive by construction; it does not restate the geometric column.

`pre2017` and `2017-2020` carry 0 and 1 usable months — the tilt needs all five
members' marks and sh588000 only starts 2020-11-13. Those eras are skipped, not
measured; E43-TILT-4MEMBER-HISTORY is seeded to reach back on the four-member
sub-ladder.

## 2. The tilt does not decay like the spread does

| era | months | tilt annualised | tilt sd | ladder beta on tilt | R² | ladder mean month |
|---|---|---|---|---|---|---|
| 2021-2023 | 36 | +609.2 bp | 538 bp | 0.116 | 2.0% | −0.78% |
| 2024-now | 34 | **+748.1 bp** | 616 bp | **1.031** | **66.9%** | +1.08% |
| full | 71 | +611.9 bp | 571 bp | 0.615 | 31.4% | +0.16% |

The newest era is the tilt's **peak**, and the ladder now tracks it almost one
for one (beta 1.03, R² 67% vs 2% in 2021-2023, where the ladder barely moved
with the size spread while both books fell). The E41 "spread decays 4.7x"
headline is therefore a denominator effect: the baseline got more small-cap
exposed exactly when small caps paid.

## 3. The calendar band is not a fee artefact

Four decision calendars (month-end−1 / month-end / month-end+1 / first session
on-or-after the 15th), identical universe, ranks and calendar, cost ×1 and ×3:

| cost | spread min | spread max | band | spread at month-end | ladder fee/yr | wide fee/yr |
|---|---|---|---|---|---|---|
| ×1 | 109 bp | 135 bp | **26.0 bp** | 129 bp | 4.9 bp | 7.7 bp |
| ×3 | 103 bp | 128 bp | **25.0 bp** | 123 bp | 14.6 bp | 23.1 bp |

Tripling the fee triples the annual cost and leaves the band at 25bp (−1bp);
every cell stays positive. Turnover is only 0.374/yr (ladder) and 0.591/yr
(wide), so a turnover story has no room to act either. The 26bp band is a
session-choice effect, not a cost effect — and it is small next to the 145bp
size-neutral era range from §1.

## What this changes

- Any quoted vs-ladder spread now has three columns: raw, size-neutral, and the
  convention (additive mean vs geometric difference). Quote them together.
- The wide book's own size loading is the live question (E43-WIDE-SIZE-COMPOSITION):
  the −0.216 beta is inferred, not yet measured from holdings.
- The +181bp size-neutral edge has survived neither a fee stress nor a calendar
  shift (E43-NEUTRAL-ROBUSTNESS).