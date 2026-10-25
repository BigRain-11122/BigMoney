# DIGEST 2026-10-26 — E81: the calendar band was never contaminated, the calendar LEVEL was

**Leg**: `python scripts\e39_panel_census.py screencalc` (mode added this round)
**Face**: `results/e42_calendar_cost/COST-20261023-screened.json` (72 delta cells, 37 non-zero)
**Untouched twin**: `results/e42_calendar_cost/COST-20261023.json` (published face, never rewritten)
**Spec**: E42 calendar band (ladder5 vs wide_top9999), four calendars `me_m1 / me / me_p1 / mid15`,
cost x1 and x3, start 2020-01-01, cutoff 2026-10-23.

## Why this leg exists

E79's screen matrix found 33 census modes reading the per-name loader with no raw hook,
so any equal-weight number they publish still charges unadjusted share-split prints at
weight 1/n. The era twin (E76 `screenreg`) covered the era spread; the calendar-cost face
that carries the fee-channel conclusion had no screened twin until now.

## The screen, in one line

`panel_screen.screen_universe` over 1269 names / 3500 sessions:

| arm | names touched | events repaired | note |
|---|---|---|---|
| `neutralise_int` | 65 | 65 | only prints whose price ratio lands on an integer |
| `neutralise` | 129 | 135 | every adjacent print past the 30% screen |

Gapped prints are deliberately left alone (33 on this panel) — a resumption after a
suspension can be a real market print.

## What moved

| arm | band x1 | band x3 | level at `me` x1 | level at `mid15` x1 | ladder ann range |
|---|---|---|---|---|---|
| unscreened | 24bp | 26bp | +117bp | +99bp | 53bp |
| `neutralise_int` | 20bp | 22bp | +213bp | +200bp | 53bp |
| `neutralise` | 17bp | 18bp | +321bp | +311bp | 52bp |

Two readable facts:

1. **The level triples, the band shrinks.** All four calendars move up together
   (+96bp / +204bp at x1), so `max − min` compresses 24 → 20 → 17bp. The widest single
   correction is the `mid15 / cost_x1` spread cell: 99bp unscreened vs 204bp
   (`neutralise_int`) vs 316bp (`neutralise`) — a 217bp move on one cell.
2. **The fee-channel reading survives.** `band_delta_top_vs_base_bp` stays positive in
   every arm (unscreened 2.0, `neutralise_int` 2.0, `neutralise` 1.0) and the spread is
   positive in all four calendars of every arm. E42's turnover reading is therefore not an
   artefact of the bad prints; only its magnitude is.

The ladder leg's ann range is unchanged (53bp) in every arm — the same reason E76 gave:
both ladder5 corporate actions sit behind a suspension bar, which the screen does not touch.

## Reading rule this leg establishes

A band statistic (max − min over arms) is **blind to a common shift**. So "the calendar
band is only 24bp" was never evidence that the calendar choice is cheap in level terms —
it only says the four calendars are close *to each other*. Any published band must be read
beside its level column, and any screened band beside the unscreened one.

## Honest limits

- Repairing an integer-ratio print is a sensitivity, not a correction: an ETF whose daily
  limit differs from the 10%/20% stock band can print >30% for real.
- 37 of 72 cells move, so this is not a small perturbation of one column.
- Descriptive census only: no gate, no verdict, no ledger booking, trial 0.