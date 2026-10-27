# E123 — the pair leg's drawdown SHAPE does not survive the print repair (r1196 bm-b)

Face: `results/e40_pair_drawdown/PAIRSCREEN-20261027.json` (new),
per-arm checkpoints `PAIR-arm-raw-20261027.json` / `PAIR-arm-neutralise_int-20261027.json`.
Base face: E40 `run_pair` (ladder5 vs wide book, three profiles per window: the two books
and the ratio of their curves). Screen arm: `panel_screen.screen_universe(mode=neutralise_int)`.
Cutoff 2026-10-27. Selftest `e39` 427 -> 442; `e97` routing re-derived: covered_twin 19 -> 20,
uncovered 5 -> 4.

## What moved

75 cells compared, 30 move, max |delta| 140 (sessions). Attribution, complete:
14 wide book / 8 spread ratio / 8 derived answers / **0 ladder** / 0 other.

The zero on the ladder is the licence to attribute: the five-name ladder is a constant list,
so a moved ladder cell would name a defect in the join or the rank cache, not an effect.
The repair reaches the wide book and everything derived from it.

## The levels barely move; the reading does

| window | ladder ann | wide ann | ann spread | maxdd ladder | maxdd wide | maxdd delta |
|---|---|---|---|---|---|---|
| 2020-01-01 raw | -1.03 | 0.32 | +1.35 | -42.72 | -36.55 | +6.17 |
| 2020-01-01 screened | -1.03 | 0.68 | +1.71 | -42.72 | -36.13 | +6.59 |
| 2018-01-01 raw | 4.98 | 6.99 | +2.01 | -42.72 | -36.55 | +6.17 |
| 2018-01-01 screened | 4.98 | 7.28 | +2.30 | -42.72 | -36.13 | +6.59 |

Every one of those deltas is under 0.5pp. But the *drawdown-shape* answers are not:

- wide book longest underwater run: **1094 -> 954 sessions** (-140, the worst cell);
- `underwater_delta_sessions` (wide minus ladder): **+48 -> -92** — a **sign flip** on a cell
  that moved by 140 sessions while its percent neighbours moved by 0.4pp;
- worst-month identity (both books losing their worst month in the same month): **False on
  both arms** — unchanged, and it is a claim, not a number.

So: the wide book's **drawdown ADVANTAGE** survives (it still draws down less than the ladder:
maxdd delta stays +6.17 -> +6.59, same sign, same order), and its **underwater TIMING** does
not (it used to spend 48 more sessions underwater than the ladder; repaired prints make it 92
fewer). Those are two different sentences and E40 publishes them as one profile.

## Controls

- same arm vs itself: **0 of 75** cells, 0 claims — the harness is arm-invariant.
- cutoff control (published `PAIR-20261020` raw vs today's raw, arm held fixed): **28 cells,
  max 5**. That is the same order of magnitude as the repair's 30 — unlike E122, where the
  repair dominated the refresh 3.6x. Same family, opposite ordering: **in this family the
  panel refresh and the print repair are not separable by size**, and neither face may be
  quoted without both.

## The defect this leg hit on its first live burn (fixed in-window)

The arrow layer listed the spread sign and the drawdown-delta sign but **not** the
underwater-delta sign — the exact cell that flipped. The face therefore printed
`arrows_survive_the_repair: true` beside `underwater_delta_sessions: +48 -> -92`. "Arrows"
must cover every answer read as a direction, so `_pair_arrows` is now module-level with an
explicit `_PAIR_ARROW_COLUMNS`, and three selftest legs pin it (the column set, the values,
and the flip). This is the E94 family's fourth recurrence: a label narrower than its evidence.

## Method card

E162 in `knowledge/METHODOLOGY_ASSETS.md`.

## Honest

Descriptive census, no gate, no verdict on the strategy, no prereg, no trial count, no ledger
booking. `spread_ratio` is a ratio of curves, not a tradable sleeve. Both windows share the
same ladder drawdown (-42.72) and the same wide drawdown (-36.55) because the deepest path
sits in the span both windows contain; the window-to-window difference therefore shows up in
the annualised columns, not in the drawdown columns.