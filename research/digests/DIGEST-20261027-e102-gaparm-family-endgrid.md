# DIGEST 2026-10-27 — E102: the five published arms under one end grid

Source face: `results/e44_midmonth/GAPARM-FAMILY-ENDGRID-20261026-s20180101.json`
Runner: `python scripts\e39_panel_census.py gaparmfamily --start 2018-01-01` (selftest 292/292, +6 legs)
Evidence cutoff: **2026-10-26** · one panel read, deterministic, **18.5s** burn (CPU only)
Predecessors: E99 `MID-20261026-s20180101-armed.json` (five arm levels), E101
`GAPARM-ENDGRID-20261026-s20180101.json` (one arm under the grid)

## What was open

E99 published **five** arms (`unscreened`, `neutralise_int`, `neutralise_gap1/2/5`) as
whether the print repair moves the churn level. E101 then put **one** of them (gap1)
under the end grid and found its 2017_2020 `me` delta is a *one-transition step*: 11 of
12 ends read exactly `0.0` and the twelfth (the era's own last end) carries the whole
`-745.9bp`. But E99 also published `gap1 = gap2 = gap5 = -745.9` to 0.1bp on that same
cell. A family that agrees to the decimal is either five measurements of the same thing
or five names for one thing — and only running the grid on all of them tells you which.

## Per arm, per book: how many ends read exactly zero

Every grid is the era's last 12 month-end decision sessions; every end is priced through
the **next** decision of the same book (an era's own last transition needs a forward leg).

| era | book | arm | zero ends | non-zero ends (bp) | delta span | level spans (arm / unscreened) | verdict |
|---|---|---|---|---|---|---|---|
| 2017_2020 | me | neutralise_int | **11/12** | 52.5 | 52.5 | 1825.9 / 1773.4 | step · delta_stable_levels_fragile |
| 2017_2020 | me | gap1 = gap2 = gap5 | **11/12** | -745.9 | 745.9 | 1526.1 / 1773.4 | step · delta_moves_with_the_end |
| 2017_2020 | mid | all four | **12/12** | – | 0.0 | 1890.3 / 1890.3 | no effect at any end |
| 2021_2023 | me | neutralise_int | **12/12** | – | 0.0 | 407.3 / 407.3 | no effect at any end |
| 2021_2023 | me | gap1 = gap2 = gap5 | **0/12** | -1347.9 … -1098.3 | 249.6 | 157.7 / 407.3 | delta_moves_with_the_end |
| 2021_2023 | mid | neutralise_int | **12/12** | – | 0.0 | 535.5 / 535.5 | no effect at any end |
| 2021_2023 | mid | gap1 = gap2 = gap5 | **0/12** | -1408.6 … -1117.2 | 291.4 | 244.1 / 535.5 | delta_moves_with_the_end |
| 2024_now | me | all four | **8/12** | 5.3 / 5.1 / 4.9 / 4.9 | 5.3 | 78.9 / 78.9 | delta_stable_levels_fragile |
| 2024_now | mid | all four | **0/12** | -348.1 … -241.0 | 107.1 | 194.8 / 89.2 | delta_moves_with_the_end |

`pre2017` is skipped: fewer than 3 decision ends fall inside it (same as E101).

## The answer to E102's question: two objects, not five

1. **Three of the five published arms are one object.** `gap1`, `gap2` and `gap5` agree on
   all six era-book cells and on the whole per-end series, not just at the latest end
   (`screen_max_minus_min = 0.0` everywhere). The root cause is visible one layer below
   the deltas: all five arms keep **the same 1,271 names** (the screens repair prints,
   they do not drop tickers), gap1 and gap2 edit the *same* 74 symbols, and gap1 vs gap5
   differs on **exactly one** of 1,271 symbols — a name whose prints never reach a
   published cell. So the gap limit (1 / 2 / 5 sessions) is **not identified by this
   panel**: it is a parameter three published columns cannot distinguish.

2. **`neutralise_int` is a genuinely different object** (65 edited symbols vs 74), and it
   reads differently in both directions: on 2017_2020 `me` it is a *small positive* step
   (`+52.5bp`, span only 3% of its level pair) where the gap family is a *large negative*
   step (`-745.9bp`, span 49% of its levels); on 2021_2023 it is **zero at all twelve
   ends on both books** where the gap family walks 249.6 / 291.4bp.

3. **A zero is a reading too.** Four of the six measurable cells are 12/12 zeros, i.e. the
   arm does not touch that cell at any end — not "touches it slightly". Quoting a `0.0`
   delta without its zero count would let a no-effect cell look like a measured null.

## The control: 24 of 24 published deltas reproduce exactly

Every (era, book, arm) published delta is reproduced by this grid's own latest end at
`abs_diff 0.0` — 24 cells, zero mismatches. That is the proof the grid cuts the
*evaluation end* and nothing else: no re-burn, no re-screen, no re-timestamp of a
full-window reading. It also means E102 adds a frame around E99's numbers rather than
restating them.

## How to cite this from now on

- Never write "the gap repair lowers the 2017_2020 churn level by 745.9bp". Write **"one
  month-end transition carries -745.9bp; the other eleven ends read 0.0"** (E101 rule) and
  note that `gap2`/`gap5` are **the same reading**, not corroboration.
- `neutralise_int` may not be pooled with the gap arms: different edits, different signs,
  and on two era-book cells a different verdict (step vs zero vs movement).
- Any future "N arms agree" claim in this family must state the **edit counts** beside the
  deltas — agreement at the cell level is compatible with one object under several names.

## Honest limits

- Descriptive census only: no gate, no verdict on the strategy, no prereg, no trial count.
- All five arms share the calendar, the rank cache and the fee ladder; the arms are
  universe repairs, not different strategies.
- Identical deltas across gap1/gap2/gap5 mean *the gap limit does not bind on this panel*;
  it does not mean the three screens are the same code path.
- The churn level is a name-level mean over swapped pairs, not a portfolio return: these
  deltas move a reading, not money.
- `E100` (naming the transitions that carry the two large moves) remains open and is the
  next required step before any of these numbers is cited outside the census.