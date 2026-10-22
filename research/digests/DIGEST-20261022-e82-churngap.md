# DIGEST 2026-10-22 — E82: who carries the mid-month churn-gap amplification?

Face: `results/e44_midmonth/CHURNGAP-20261021.json` (evidence_cutoff 2026-10-21)
Runner: `scripts/e39_panel_census.py churngap` (new leg; `run_midmonth(full_churn=True)` opt-in)
Selftest: 178/178 (9 new hermetic legs)
Pool: E82 (bm-b lane, cpu-only) closed with result_ref

## What was asked

E80 (r1150) left an asymmetry: under the split screen the newest-era churn alpha gap (mid −
month-end) widened from −211 to −457bp **per swap**, while under drop it collapsed to −24bp.
The open question was mechanical: is that widening accumulated over many transitions whose
swapped names hold a repaired print, or is it a few events (or one) doing all the work?

E82 joins every churn transition to the raw print-event list on the same panel calendar and
splits the delta into **hit** (a swapped name carries a print event inside the priced window,
`decision date < event date ≤ next decision date`) and **clean** (no swapped name does).

## Numbers

Screen size on the 2020-01-01 window: 1,265 universe members, 156 print events indexed.
neutralise_int touches 65 names / 65 events; neutralise and drop each 129 names / 135 events.

2024_now, per-transition delta versus the unscreened twin (bp per swap):

| book | mode | transitions | hit | Δ mean all | Δ mean hit | Δ mean clean | hit share of Δ |
|---|---|---|---|---|---|---|---|
| month-end | neutralise_int | 27 | 1 (3.7%) | +5.1 | **+137.2** | 0.0 | 100% |
| mid15 | neutralise_int | 27 | 2 (7.4%) | −241.0 | **−3253.4** | 0.0 | 100% |
| month-end | drop | 27 | 1 | −35.2 | +125.6 | −41.4 | −13.2% |
| mid15 | drop | 27 | 2 | +151.7 | +1838.2 | +16.7 | 89.8% |

The two hit transitions in the mid-month newest era are **2024-01-15 (−6614.2bp,
sz159925)** and **2026-07-15 (+107.4bp, sh588920)**. The month-end single hit transition is
2026-07-31 (+137.2bp, sh588920) — the same repaired name, opposite sign, because the two
books hold it in different windows.

Era 2021_2023 under neutralise: 13–15 hit transitions out of 25–29, **every delta exactly
0.0bp** — i.e. the repaired prints there do not touch the swapped names' sleeve at all,
consistent with E80's bit-identical 318.9 churn gap for that era.

`neutralise_int` and `neutralise` produce bit-identical churn rows in every cell of this
burn (they differ only in screen size: 65 vs 129 names), so the second universe buys nothing
for the sleeve.

## Reading

1. **The amplification is one swap.** The −457bp mid-month churn gap is a single transition
   (2024-01-15, sz159925, −6,614bp) averaged over 27 rows. Remove it and the mid-month sleeve
   moves by about +107bp in total instead of −6,507bp. E80's own label ("a sensitivity
   bound") was right for the right reason, and the bound is now attributable: one repaired
   print, one month, one name.
2. **Clean transitions are exactly untouched** (0.0bp in every neutralise cell), which is the
   structural control: the screen only rewrites bars, so a transition with no event in its
   window cannot move. That control passing is what makes the hit column readable at all.
3. **Drop mode is a different animal** and must never be read beside neutralise cell-for-cell:
   it removes 129 names, so both buckets move (clean −41.4bp month-end, +16.7bp mid) purely
   from composition. The sign of the month-end clean column even flips versus the hit column.
4. **Do not promote the churn magnitude to an era property.** The direction of E44's claim
   (month-end swaps better than mid-month in the newest era) survives, as E80 showed; the
   *magnitude* lives in a handful of transitions and, in this window, in one.

## Pit

The churn rows returned by `_churn_stats` carry no tickers, so a join needs an opt-in
(`with_names=True`) — and the first burn of this leg died twice before that: `run_midmonth`
reads `arms["x0"/"x1"/"x3"]` unconditionally, so passing a single cost multiplier raises
`KeyError: 'x1'`, and a two-cost list raises it on `'x3'`. The sibling lesson is the same one
E76 taught: a leg that only needs one arm still has to be fed the cost set the shared era
table expects, or the table has to be made tolerant — here the cheaper fix was to keep the
standard triple because the x1 turnover control is part of the evidence.

## Honest scope

Descriptive census only: no gate, no verdict, no prereg, no trial booking. A hit transition
means a print event sits inside the priced window — it does not mean the book traded that
name on that bar. The sleeve is an equal-weight mean over swapped names, so one large print
can move a transition by more than a clean year. Transitions are counted, not weighted.