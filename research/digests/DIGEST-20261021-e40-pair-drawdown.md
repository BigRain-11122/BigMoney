# E40 pair drawdown — the vs-ladder spread read on the drawdown path

Run: `python scripts/e39_panel_census.py pair` (offline, deterministic, engine import only)
Face: `results/e40_pair_drawdown/PAIR-20261020.json` · panel cutoff 2026-10-20
Spec: ladder5 vs `wide_top9999` (top-N of the eligible universe), start 2020-01-01 and
2018-01-01, cost x1 (13.041bp/side), exclude prefix `sh511`, one shared rank cache.
Descriptive census: no gate, no verdict, no prereg, no trial count.

## What was open

Every wide-book number in E34–E38 is quoted as a spread over ladder5, and the ladder
denominator itself was only described last round (ann −0.43%, maxDD −42.72%, 1,046
underwater sessions from 2020). A mean-only spread says nothing about the path the
holder actually sits through. This leg profiles both legs and the spread itself.

## Numbers (2020-01-01 window, 1,645 bars)

| profile | ann % | max drawdown | dd span | longest underwater | worst month |
|---|---|---|---|---|---|
| ladder5 | −0.43 | −42.72% | 2021-09-10 → 2024-02-05 | 1,046 sessions | 2026-07 −14.82% |
| wide book (top9999) | +0.86 | −36.55% | 2021-02-19 → 2024-02-05 | **1,094 sessions** | 2024-01 −11.53% |
| spread (wide/ladder ratio) | +1.29 | −13.04% | 2025-07-24 → 2026-06-30 | 298 sessions | 2026-06 −7.49% |

2018-01-01 window (2,132 bars) moves only the annualised column: +5.48 / +7.44 /
+1.86 %/yr. Drawdown, underwater and worst-month figures are identical to the table —
the dominant drawdown event lives after 2020 in both windows, so the path read is a
post-2020 fact rather than a window artefact.

## Read

1. **The wide book is shallower but slower to recover.** −36.55% vs −42.72% is a real
   6.17pp relief, but the underwater run is **48 sessions longer** (1,094 vs 1,046).
   A vs-ladder number quoted as annualised bp hides that trade.
2. **The spread itself is not a straight line.** The ratio curve draws down −13.04%
   across 298 underwater sessions and its worst month (2026-06, −7.49%) is a
   *different* month from the ladder's worst (2026-07, −14.82%). Whoever holds the
   spread wears a cu
   ‑year-scale cycle of its own, uncorrelated with the legs' bad months.
3. **Worst months do not line up.** `worst_month_same_month = false` in both windows:
   the July 2026 small-cap move hammered the ladder, while the wide book's worst month
   was January 2024. Any "the spread protects you in the bad month" claim needs the
   month identity checked, not just the sign.

## Honest limits

- The ratio curve is a ratio of equity curves, not a tradable sleeve: it prices the
  claim, it does not add a portfolio.
- Both legs come from the E24/E27 engine via module import on one calendar and one rank
  cache; no cost is charged on the ratio itself.
- Drawdown is measured on daily equity; months are month-end marks.