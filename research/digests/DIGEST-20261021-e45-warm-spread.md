# DIGEST 2026-10-21 — E45 warm spread: the newest era is not a burn-in artefact, and its live span is negative

Round r1122, bm-b. Script `scripts/e39_panel_census.py` (`warmspread` leg, selftest 65/65).
Face `results/e45_warm_spread/WARMSPREAD-20261020.json`. Evidence cutoff 2026-10-20.
Same spec as E41/E42: wide book = top9999 over the de-duplicated panel with `sh511*` excluded,
ladder5 = the E24 five, cost x1 (13.041bp/side), 250-bar eligibility, month-end decisions.

Two quotes of the same quantity are compared per era:

- **warm** — one pair of curves built on the whole calendar (from 2012-05-28) and sliced per era,
  so the 250-bar burn-in is paid on bars *before* the measured span;
- **cold** — a fresh pair started at the era's own first bar, measured over the same era span
  (the convention a backtest gets when it is told "measure 2024 onward").

## Warm reproduces E41 to 0.1bp, so every published era number is a warm quote

| era | warm spread | cold spread | warm − cold | cold dead block | cash accrued in the block |
|---|---|---|---|---|---|
| pre2017 | **+236.0 bp** | +236.0 bp | 0.0 | 262 bars (23.4 %) | +3.69 % |
| 2017-2020 | **+419.0 bp** | +404.0 bp | +15.0 | 265 bars (27.2 %) | +4.36 % |
| 2021-2023 | **+243.0 bp** | +179.0 bp | +64.0 | 261 bars (36.0 %) | +2.46 % |
| 2024-now | **+89.0 bp** | **−77.0 bp** | +166.0 | 259 bars (38.4 %) | +2.02 % |

The warm column lands exactly on the E41 spread-era face (+236 / +419 / +243 / +89), which is the
check that the E34-E44 family has been quoting the warm convention all along. Nothing in that
line needs restating — but the convention now has a name, and the cold column shows what it is
worth: **up to 166bp of the quote**.

## The dead block is a fixed ~260 sessions, so its share of a window grows as the window gets shorter

259 / 262 / 265 / 261 sessions in the four cold windows — the 250-bar rule plus the month-end
snap. Because the block is nearly constant while the windows are not, the share climbs
monotonically with recency: 23.4 % → 27.2 % → 36.0 % → **38.4 %** of a 2024-start window is spent
un-investable, against 7.7 % on a 2013 start in the r1120 face. Both books carry cash at weight
1.0 through it, so the block contributes a *near-identical* +2.0…+4.4 % to both legs. A shared,
nearly equal additive term cannot create a spread — it can only dilute one, in proportion to how
much of the window it eats.

## The newest era is the thinnest in both readings — but only just, and the sign is the story

`newest_era_is_thinnest_warm = true`, `newest_era_is_thinnest_cold = true`. The E41 ranking's
headline survives the burn-in test, so "the newest era is the thin one" is not an artefact.

The rest of the ordering does not survive: on a cold start 2021-2023 (179bp) drops *below*
pre2017 (236bp), while warm it sits above it. `ordering_preserved = false`. Middle-era ranks are
therefore a naming decision about where the measurement starts, and only the extremes are robust.

## The +89bp is carried by 2024, and the live span is negative

A cold 2024 book first holds anything on **2025-02-05**. Sliding the warm curve forward to that
same bar (identical weights from there on, so it is the same market):

| window | ladder ann | wide ann | spread |
|---|---|---|---|
| 2024-01-01 → 2026-10-20 (warm, 675 bars) | +11.08 %/yr | +11.97 %/yr | **+89 bp** |
| 2025-02-05 → 2026-10-20 (415 bars) | +12.16 %/yr | +10.87 %/yr | **−129 bp** |

The wide book's entire era edge — and more — was earned in the thirteen months before the
eligibility gate would let a cold-start book hold a single name. Over the 415 sessions actually
available to a cold book, it lags the ladder by 129bp/yr. So the honest statement of the newest
era is not "positive but thin": it is **positive only if the book was already running in 2024,
and negative on the span a fresh window can see.**

## What this changes downstream

- E41/E42/E43/E44 era spreads are warm quotes; a cold quote is up to 166bp lower (this face now
  supplies both columns so the label never has to be inferred).
- The newest-era drawdown/ratio story is unaffected (the engine path is the engine path), but any
  forward claim ("the spread still pays 89bp") must quote the live-window number, −129bp.
- The mid-month weakness in E43's robustness grid is measured on 2020+ windows where the dead
  block is 16 % — the calendar cells that lose the most bars to it are the ones most exposed to
  this dilution, which is exactly what E44-MIDMONTH-WEAKNESS should price next.

Descriptive census only: no gate, no verdict, no prereg, no trial count, zero ledger booking.