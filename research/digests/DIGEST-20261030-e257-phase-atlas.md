# DIGEST 2026-10-30 r1350 bm-c -- the phase atlas: a cell is not a cell until it beats its calendar

Face: `results/etf_book_phase_atlas.json` | prose: `research/ETF_BOOK_PHASE_ATLAS.md` |
card: `knowledge/METHODOLOGY_ASSETS.md#E257` | runner: `scripts/etf_book_phase_atlas.py`

## The question

Every published number of this book comes off ONE decision calendar: the engine decides every
`rebal` bars from the first bar >= 2020-01-03. r1325 measured what that costs once -- one buffer
arm, five books, four phases -- and found its own phase IQR (0.53pp) larger than the effect being
tested. The production config is a CELL in a 3x3 grid (names x cadence) chosen by comparing those
same single-calendar numbers, so the same objection applies to the choice of the cell itself.

## What was run

- 12 cells: n_hold in (3,5,8,12) x rebal in (10,20,40).
- Each cell on EVERY decision origin inside one rebalance cycle: 10 / 20 / 40 origins -> 280 engine
  runs through the production engine (10bp/side, 8% vol target, buffer k=0), 8 ProcessPool workers
  via `scripts/parallel_runner.run_cells_parallel` (the same runner the pool's law-1 gate requires).
- A cell's **band** = p95-p5 of its CAGR across its own cycle. The grid's **spread** = max-min of
  the cells' median CAGR. Both in pp/yr, both frozen before the run and echoed into the face.

## Reading

**CONFIG_ORDER_WITHIN_PHASE_NOISE** -- between-cell spread 5.22pp < median cell band 6.68pp.

| n_hold | rebal | median CAGR | band | min..max over the cycle | Sharpe |
|---|---|---|---|---|---|
| 3 | 10 | +10.93pp | 4.22pp | +8.51..+13.87 | 1.089 |
| 3 | 20 | +8.71pp | 6.94pp | +2.76..+12.48 | 0.830 |
| 3 | 40 | +6.78pp | 12.41pp | +0.45..+14.05 | 0.639 |
| 5 | 10 | +11.51pp | 3.50pp | +9.34..+13.69 | 1.137 |
| 5 | 20 | +9.13pp | 6.25pp | +4.35..+13.56 | 0.893 |
| 5 | 40 | +8.32pp | 9.55pp | +1.93..+13.34 | 0.795 |
| 8 | 10 | +12.00pp | 3.32pp | +9.99..+13.85 | 1.192 |
| 8 | 20 | +10.13pp | 6.49pp | +5.74..+13.29 | 1.021 |
| 8 | 40 | +8.30pp | 8.41pp | +2.02..+12.11 | 0.750 |
| 12 | 10 | +11.63pp | 2.77pp | +9.84..+12.94 | 1.173 |
| 12 | 20 | +9.64pp | 7.87pp | +5.28..+13.46 | 0.961 |
| 12 | 40 | +7.55pp | 6.88pp | +2.82..+12.17 | 0.695 |

Three consequences, in the order they change what can be said:

1. **The width is the wrong knob to be arguing about.** Inside a fixed cadence, moving 3 -> 12 names
   moves the median by ~1.1pp while the cell's own band is 2.8-7.9pp. The 12-name card and the
   5-name ticket (9.64pp vs 9.13pp, read from their own artifacts) are one number on this evidence.
2. **The cadence is the knob that survives.** R10 cells: 10.9-12.0pp with 2.8-4.2pp bands. R40
   cells: 6.8-8.3pp with 6.9-12.4pp bands. Fewer decisions in a fixed window -> each decision
   carries more path dependence. That is a mechanism, not a coincidence of this grid.
3. **The "best cell" is 5 different cells on 10 calendars** (N3R10, N3R20, N5R10, N8R10, N12R20)
   while the overall ordering stays broadly stable (Spearman 0.58-0.90 vs slot 0). So the ranking
   is informative at the level of "short cadence beats long cadence" and not at the level of "this
   cell beats that cell".

## Cross-check the face carries

The N5/R20 median in the atlas is **9.13pp**, which is the published executable ticket's number on
the engine's own calendar -- the atlas reproduces the production path rather than a re-implementation
of it (activity precondition asserted: the 10/20/40 origins produce distinct decision-calendar
signatures, r1261 lesson).

## Honest limits

- The aligned-slot ranking uses offsets 0..9 (present for every cell), so the 20- and 40-bar cycles
  contribute a subsample there; the per-cell bands use the full cycle.
- This is a descriptive face: no judgment line on alpha was moved, no cost model changed.
- Surviving survivorship/panel caveats are inherited from the production panel, not introduced here.

## Cost

8 workers, 280 cells, ~1.6 min wall including 8 panel loads (the panel load dominates: 50s/worker,
1.3s/cell). Chain leg is `--check` (0.9s).