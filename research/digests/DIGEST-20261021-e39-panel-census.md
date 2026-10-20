# DIGEST 2026-10-21 · E39 panel census (stale two / refresh wave / ladder denominator)

Round r1112 (bm-b), one new script `scripts/e39_panel_census.py` (selftest 10/10), three
descriptive legs. Zero prereg, zero judgement, zero ledger booking, trial_count 0.

## 1. The last two non-current panels are not refresh failures

The coverage face counts 1,723 of 1,725 panels current and cannot tell a dead listing
from a stale file. Reading the rows on disk settles it:

| file | last bar | bars behind calendar | class | evidence |
|---|---|---|---|---|
| `510880_t73.csv` | 2026-09-22 | 14 | **PINNED_SLOT_COPY** | 4,784 common dates with `sh510880.csv`, **4,784 identical closes** — a frozen snapshot of the same series, tagged slot copy, not a universe member |
| `sh512390.csv` | 2026-09-04 | 26 | **SOURCE_SIDE_GAP** | tail-20 median volume 33,500 — it was still trading when it stopped; the 2026-09-22 bulk import could not advance it either, so the source never offered later rows |

Consequence for the coverage denominator: drop the slot copy (it is a duplicate, not a
panel) and stop counting `sh512390` as a refresh obligation. Our own defect count on the
panel face is **zero**, not two.

## 2. The refresh wave, sized

1,725 files, 1,604,427 bars, 90.4 MB on disk. Rewritten since 2026-10-17:

- mtime histogram: **2 files on 10-17, 53 on 10-20, 1,670 on 10-21** (first 09:07:10 on
  10-17, last 03:47:16 on 10-21)
- **24,116 bars** dated after the 2026-09-22 bulk import were carried in — the panel went
  from one bulk snapshot to a live two-month tail in about 30 hours
- 1,723 files now advanced past the bulk date, 1 stopped exactly at it (the slot copy),
  1 behind it (`sh512390`)

So "the panel moved" is now a byte/row figure, and the r1110/r1111 drift (+82.7 → +138.9 →
+133.7 bp/yr on the same spec) is explained by a 24k-bar arrival, not by a spec change.

## 3. The ladder5 denominator, described

Every wide-book spread in E34/E36/E37/E38 is quoted "vs ladder5", but the denominator had
only ever been ann/vol/Sharpe. Curve taken from the E24/E27 engine by module import (no
re-implementation); window 2020-01-02..2026-10-20, 1,644 bars, 81 month marks:

| quantity | value |
|---|---|
| ann return | **-0.43%/yr** (total -2.76%) |
| ann vol | 18.75% |
| Sharpe | 0.071 |
| max drawdown | **-42.72%** (peak 2021-09-10 → trough 2024-02-05) |
| longest underwater run | **1,046 sessions** (~64% of the window) |
| worst month | 2026-07 **-14.82%** |
| best month | 2024-09 +25.88% |
| monthly win rate | 55.6% (45 of 81) |
| turnover cost | 4.9 bp/yr |
| cash leg | 12.71% of bars (sh588000 has no price before 2020-11-13), repo 1.98%/yr |

2018-start window for context: +5.48%/yr, vol 19.64%, Sharpe 0.37, **same** -42.72%
drawdown and the same 1,046-session underwater run, cash leg 32.66% of bars at 2.20%.

Read together: a "+134bp/yr vs ladder5" is a spread over a denominator that lost 42.7%
peak-to-trough and spent most of the 2020s below its own high. In absolute terms the wide
book is roughly +0.9%/yr on a window where the ladder is -0.43%/yr — both are noise-level,
and the drawdown path, not the spread, is what any sleeve decision has to be made on.

## 4. The worst month is real, not a data defect (E40-WORST-MONTH-ATTRIB, burned same round)

July 2026 is the ladder's worst month at -14.82%. Rows say it is a market move:

| member | July 2026 |
|---|---|
| sh510300 (300) | -7.29% |
| sh510050 (50) | -1.62% |
| sh510500 (500) | -18.43% |
| sh512100 (1000) | -19.93% |
| sh588000 (STAR50) | -26.28% |

Equal weight at the entry mark: **-14.71%** (the engine's -14.82% differs only by intra-month
drift and the month-end mark). Zero zero-volume days, zero missing bars, and the single
>10% bar is a **+11.07% bounce on 2026-07-21** — inside the loss, not causing it. So the
denominator's worst month needs no data fix; it needs a style note: five equal weights
across the size ladder are not a neutral baseline, they are a large small-cap bet (the
300 leg lost 7% while the 1000 leg lost 20%).

## 5. What this changes downstream

- E30/E38 coverage and drift faces: denominator = 1,723 files; the two exceptions are
  classified and need no refresh action.
- Any future wide-book statement must carry the denominator's drawdown next to the spread.
- E40 candidates seeded: pair drawdown (ladder vs wide book), the cash-leg drag of the
  pre-listing share, and the ladder's size tilt (the July attribution pointed at it);
  the July attribution itself was burned this round.

## Honest notes

- classification reads rows on disk only: no vendor metadata, no listing notices, so
  SOURCE_SIDE_GAP is an inference from turnover, not a confirmed delisting;
- mtime is a disk fact, not provenance: a rewrite that changed no row is invisible here;
- cash-leg share is the share of bars with a missing ladder member price, not a
  discretionary cash position;
- descriptive census only: no gate, no verdict, no prereg, no trial count.