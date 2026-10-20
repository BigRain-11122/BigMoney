# DIGEST 2026-10-20 — seasonal calendar census (A-share calendar windows)

**Artifact**: `scripts/seasonal_calendar_census.py` (selftest 14/14) →
`results/seasonal_calendar_census/CENSUS-2026-10-19.json` + `by_variant.csv` +
`latest.json` (sha-stable rerun, exit 0, 11.6s).
**Panel**: `data/cache/p1c_local` (local numpy build of the T-87 forward
panel; 5,225 symbols × 8,745 dates, cutoff **2026-10-19**; priced cells
16,715,356, usable obs 16,583,153 = **99.21%**).
**Baseline**: pooled equal-weight close-to-close daily mean **+4.89bp/bar**,
win 47.73%.
**Exclusions (frozen)**: non-positive prices, suspension-resume transitions,
one-price bars, |r| ≥ 75% artifacts.
**Variants enumerated**: 23 (6 turn-of-month, 4 holiday, 12 month, 5 weekday);
zero multiplicity correction.

## Headline readings (excess vs baseline, per bar)

| variant | n | excess | win | years above/below | cost verdict (per year) |
|---|---|---|---|---|---|
| **tom_start1** (month's first trading day) | 817,187 | **+41.8bp** | 56.7% | 24/36 | **COST_POSITIVE +1.89%** |
| hol_post1 (first day after a long break) | 409,580 | **+35.3bp** | 57.0% | 20/35 | +0.32% |
| hol_pre1 (last day before a long break) | 411,784 | +30.7bp | 51.8% | 23/35 | +0.16% |
| m02 (February) | 1,096,325 | +30.5bp | 53.8% | 28/35 | n/a (label) |
| tom_end1 (last trading day) | 823,254 | +19.1bp | 51.6% | 20/36 | -0.84% |
| **tom_end2** | 823,458 | **-28.9bp** | 43.7% | 8/36 | **-6.60%** |
| dow_thu (Thursday) | 3,352,729 | **-14.0bp** | 44.5% | 7/36 | n/a (label) |
| m01 (January) | 1,287,785 | -14.7bp | 46.6% | 16/36 | n/a (label) |

## Reading

1. **The folk claim is narrow, not general.** "Month-end effect" splits: the
   *last* day is mildly positive (+19bp) but the *second-to-last* is solidly
   negative (-29bp, only 8/36 years above baseline, -6.6%/yr after costs).
   What actually carries the money is the **first trading day of the month**
   (+41.8bp, 24/36 years, cost-positive at 12 events/yr).
2. **Long-break edges survive cost but are thin.** Post-holiday +35.3bp and
   pre-holiday +30.7bp clear the round-trip toll at ~3.5 events/yr, but the
   net (+0.32% / +0.16% per year) is small enough that execution slippage and
   the holiday-definition rule (calendar gap ≥ 4 days, 182 breaks detected)
   can eat it.
3. **February is the strong month (+30.5bp, 28/35 years); January and
   Thursday are the bleed.** These are conditioning labels, not switches.
4. **Honesty**: the printed t values (30–109) are inflated by cross-sectional
   correlation — observations are stock-days, not independent draws. Read the
   win rate and the year-stability columns as the strength signal. This face
   is descriptive: zero prereg, zero judged claim, zero pool write, zero cost
   model beyond the reported round-trip arithmetic.

## Consumers

- **Seasonal family supply line**: this is the cheap screen a next trial-labor
  wave would need before drafting `tom_start` / holiday-window entry masks
  (same role E21 leg-3 played for W21). No family is opened by this digest.
- **Paper-lane marking timing** (P4 DCA, grid marking, daily_report context):
  "why does this week look different" now has a measured reference.
- **CEO research-orientation law (O-20260928-1522)**: a domestic folk calendar
  claim is now a numeric face instead of an anecdote.

## Follow-ups (not started here)

- A judged seasonal batch would need a frozen prereg with an explicit exit
  axis and a D6 correlation check against the funding/dividend families
  (`fund_divlowvol`, `rev_osc`), plus a PIT-safe calendar definition.
- Month-end *turnover* and the T+1 execution reality of the first-of-month
  edge are untested here (both would be separate legs).