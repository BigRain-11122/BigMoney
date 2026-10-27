# r1312 — the alpha lives in the boom window, and the book lost to four ETFs before it

Window: 2026-10-27 18:0x (bm-c). Machine anchored from `fleet/machine.json` first; state
`round_no=1310` at open while the chain already carried r1311 (`bedf2e9e42`, committed
17:41 by a window that died before closeout) — absorbed per the r1219 order (read
`git log` before `state`), closeout written for r1311, this window executes r1312.

## The question, and why it had to be asked

r1310 asked what is left of the book after the four exposures an account could hold
instead (gold 518880 / Nasdaq QDII 513100 / CSI300 510300 / bond 511010): intercept
+5.85 %/yr, t=1.94, i.e. "not distinguishable from a fixed loadings mix". r1311 put the
staggered 6+6 book through the same regression: +6.77 %/yr, t=2.36.

Both answers were computed on 2020-01..2026-10 — the window in which the ETF panel grew
from a handful of funds to ~1,500 and in which this book made all of its money. A
regression that only holds inside the window it was fitted in is a description, not an
edge. So the same test was run on the pre-boom window, which the published work has never
looked at for spans: 2015-01-07..2019-12-31, U_pre = the 193 ETFs that already existed.

## What was built (nothing re-implemented)

`scripts/etf_book_spanning_pre2020.py` (selftest 15/15):
- panel / universe mask / truncation / both engines = `etf_book_pre2020_wf`'s own call
  path (production gate → U_pre → truncate to 2019-12-31 → score rebuilt on the 193 names);
- regression = `etf_book_spanning.arm_from_returns`, the repo's single regression path,
  given a new `is_end` argument so this window uses its own split (2015-2017 / 2018-2019)
  instead of the 2020+ face's 2023 split. Default keeps every existing caller identical;
- control before any quotation: the single-sleeve arm must reproduce the published
  pre-2020 N12 overlay cell (`etf_book_pre2020_wf.json:full_window_arm_stats.fixed_n12_vt`)
  within 0.5 pp — **measured delta 0.13 pp**, so the arm is the published book.

## Result — a negative that changes how the headline may be used

| arm (2015-2019, 193-name universe) | CAGR | Sharpe | maxDD | intercept | t | R² |
|---|---|---|---|---|---|---|
| single sleeve N12/R20 + 8 % overlay | 5.12 % | 0.70 | −16.7 % | +2.03 %/yr | **1.04** | 0.70 |
| staggered 6+6, offset 10 bars | 4.26 % | 0.57 | −17.6 % | +1.00 %/yr | **0.48** | 0.68 |
| equal-weight four ETFs, same grid/cost | 8.64 % | 0.97 | −13.0 % | — | — | — |

Three readings, published together:
1. **No intercept survives.** Neither arm clears 2σ outside 2020-2026, and the OOS half
   (2018-2019) prints t=−0.39 / −0.77 — the intercept does not merely weaken, it inverts.
2. **R² is higher, not lower** (0.70/0.68 vs 0.43 on the 2020+ window): in the small
   pre-2020 cross-section the four betas explain *more* of the book, so this is not a
   noisy-window excuse — the exposures were doing the work.
3. **The rotation cost money there**: a static equal-weight basket of the same four ETFs
   returned 8.64 %/yr at a shallower drawdown than the book's 5.12 %. The negative is not
   only a failed t-test.

Both windows together now say: 2020+ the book is within 0.5 pp of buy-and-hold with an
unproven +5.9 %/yr intercept; 2015-2019 it is behind buy-and-hold with no intercept. The
9-10 % headline is a window property and must not be scaled on.

## Wiring — the number has to land where the reader is

Card section added (`scripts/etf_book_production.py`): **"Does any of it survive outside
2020-2026?"**, fed by `spanning_pre2020_support()` off the artefact (soft-fails to a
disclosure line, never a crash). The section prints both arms' t, the OOS t, the basket
row and the "rotation cost money" sentence; a passing alpha suppresses the negative
sentence (selftest leg). Smoke leg added so the period test stays callable
(`product: etf_book_spanning_pre2020 period test`, exit-code contract).

## Honest limits carried in the artefact

- U_pre is itself survival-filtered (dead funds absent) — a pass would be weaker evidence
  than it looks, a failure stronger;
- the pre-2020 cross-section is small; eligible-name counts travel in the panel block;
- no HAC correction (same basis as the 2020+ face);
- exploratory: no preregistration, no verdict booking, no member file touched.

Artifacts: `results/etf_book_spanning_pre2020.json` (schema v1), `results/etf_book_production/CARD.md`,
`smoke_test.py` (+1 leg), `scripts/etf_book_spanning.py` (`is_end`, default unchanged).