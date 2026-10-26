# DIGEST 2026-10-27 — E101: the E99 arm delta under the E98 end grid

Source face: `results/e44_midmonth/GAPARM-ENDGRID-20261026-s20180101.json`
Runner: `scripts/e39_panel_census.py gaparmendgrid --start 2018-01-01` (selftest 286/286, +10 legs)
Evidence cutoff: **2026-10-26** · one panel read, deterministic, 9s burn
Predecessors: E99 `MID-20261026-s20180101-armed.json` (arm levels) and E98 `ENDCHOICE-ALLERAS-20261026.json` (end grid)

## What was open

E99 published the gap arm's effect as a **difference of LEVELs** — `-745.9bp` on the
2017_2020 `me` level and `-1098.3bp` on 2021_2023. E98 then showed the tilt LEVEL is
end-fragile on every era the panel reaches. A difference of two fragile numbers is not
automatically fragile: if both arms move together the delta survives, and the repair is a
measurement even where the level is not quotable. E101 runs the identical 12-end grid on
**both** arms and prints the two levels beside their delta at every end.

## The grid, per era and book

| era | book | level span unscreened | level span gap1 | delta min → max (bp) | delta span | delta / level span | verdict |
|---|---|---|---|---|---|---|---|
| 2017_2020 | me | 1773.4 | 1526.1 | 0.0 → **-745.9** | 745.9 | 0.49 | delta_moves_with_the_end |
| 2017_2020 | mid | 1890.3 | 1890.3 | 0.0 → 0.0 | 0.0 | 0.00 | delta_stable_levels_fragile |
| 2021_2023 | me | 407.3 | 157.7 | -1347.9 → **-1098.3** | 249.6 | 1.58 | delta_moves_with_the_end |
| 2021_2023 | mid | 535.5 | 244.1 | -1408.6 → -1117.2 | 291.4 | 1.19 | delta_moves_with_the_end |
| 2024_now | me | 78.9 | 78.9 | 0.0 → 4.9 | 5.3 | 0.07 | delta_stable_levels_fragile |
| 2024_now | mid | 89.2 | 194.8 | -348.1 → -241.0 | 107.1 | 1.20 | delta_moves_with_the_end |

`pre2017` is skipped: fewer than 3 decision ends fall inside it (the panel's `me` book only
starts producing era-2017_2020 decisions in 2020-01, so 2017_2020 itself is swept on its
own 2020 ends and `pre2017` has none).

## Three readings worth keeping

1. **The 2017_2020 me delta is ONE transition, not an arm effect.** Eleven of twelve ends
   read exactly `0.0`; the single non-zero end is the era's own last one (`2020-12-31`,
   priced through `2021-01-29`), and it carries the entire published `-745.9bp`. Whatever
   the repair did to the 2017_2020 `me` level, it did inside one month-end transition —
   so `-745.9bp` is a transition's size, not a rate. E100 (naming that transition) is now
   mandatory before the number is cited anywhere, and the number may never be quoted
   without its "1 of 12 ends" qualifier.

2. **Where the delta is large it moves with the end; where it is stable it is zero.**
   2021_2023 `me` walks `-1347.9 → -1098.3` across its own twelve ends (249.6bp of slack,
   1.58x the smaller level span), and the newest era's `mid` book walks 107.1bp against a
   89.2bp level span. The two "stable" cells are stable for the least interesting reason:
   2017_2020 `mid` is untouched by this repair at every end (delta ≡ 0.0), and 2024_now
   `me` is a 5.3bp wobble. **No cell in this grid is a stable, large arm effect.**

3. **The repair also changes how much the level itself moves.** In 2021_2023 the
   unscreened `me` level spans 407.3bp across ends while the repaired one spans 157.7bp —
   the repair does not just shift the level, it removes more than half of its end
   sensitivity. That is a second-order product of the repair and it points the opposite
   way from the delta: repaired levels are *more* repeatable, not less.

## Instrument note (caught by the control, in-window)

The first burn truncated each end hard and the published control failed loudly: 2017_2020
`me` read `0.0` against the published `-745.9`. A hard cut drops the era's own last
transition, because `_churn_stats` needs a following decision to price a forward leg —
and that dropped transition was the whole 745.9. Every end is now **priced through the
next decision of the same book**, which keeps the era cell's meaning constant across ends
and reproduces all six published `(era, book)` deltas exactly (`abs_diff = 0.0` on
2024_now `me`/`mid`, 2021_2023 `me`/`mid`, 2017_2020 `me`/`mid`). The exact-zero control is
the proof that the grid cuts the evaluation end and nothing else.

## Cost and discipline

Two arms, one panel load, deterministic 9s burn, no network. Descriptive census only —
zero prereg, zero gate, zero judgement on the strategy, zero ledger booking, trial_count 0.
The ten new selftest legs pin the four properties that must hold before any delta is
quotable: a grid end is read on the session date (not on a decision ordinal), an era grid
never borrows a session from another era, spans ignore null cells, and the delta verdict
is a mechanical function of the two spans (with a frozen-level pair named rather than
divided by zero).

## Next (seeded as E102)

E99 published **five** arms; E101 tested two. If the gap1 delta is a one-transition step,
the other arms' deltas must be asked the same question before the published arm family is
read as a monotone ladder: run the same end grid on `neutralise_int`, `neutralise_gap2`
and `neutralise_gap5` for the two eras that carry the level moves, and report for each arm
the number of ends that read exactly zero beside its delta span.