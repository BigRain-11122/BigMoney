# r1175 bm-a — the book's worst day was not a market day

**Date** 2026-10-31 · **Round** 1175 · **Machine** bm-a · **Dept** 研究/风控

## What the round set out to answer

Every face of the ETF book publishes an annual return and a maximum drawdown over years.
None answered the question an operator asks the night before a bad open: *if the index
opens -5%, what does my account lose?* Two numbers get confused there -- the book is
~47% deployed and that sleeve is scaled to a beta target of 0.20, so "market -5%" is
emphatically not "-5% × 47%".

`scripts/etf_book_shock_day.py` (selftest 19/19) answers it by measurement:

| reading | value |
| --- | --- |
| realized beta to 510300, full history (1,525 bars) | **0.12** |
| realized beta, last 250 bars | **0.21** |
| mean book / index return on the 20 worst index days | **-0.47% / -3.87%** (ratio 0.121) |
| book finished *up* on those days | 15% |
| index -3% / -5% / -8% at today's ticket | **-3,599 / -5,998 / -9,597 CNY** |
| the naive "shock × deployed share" | -14,145 / -23,574 / -37,719 CNY |

The last row is the point: the arithmetic an operator does by hand overstates the loss
by roughly the inverse of the beta scaling, i.e. by about 4x here.

## What it found on the way

The face's own worst-day line read **-4.70% on 2025-07-07** while the index moved
-0.02% that day. A 0.2-beta book cannot lose 4.7% on a flat index day, so the number had
to be either a real crash in a single holding or a data defect. It was the second: 512800
prints 0.894 after 1.777 on 2025-07-07 and never comes back -- a unit change read as a
-49.7% day.

The panel-wide census (`scripts/etf_book_flip_contamination.py`, selftest 15/15): **168
flip prints** across 158 of 1,613 symbols on 125 distinct days. `etf_equity_alpha.repair_flips`
has existed since the cash-ladder work and the production path never called it, so every
published number of the book is computed on contaminated prices. The same rule on the same
dates, repaired prices only:

| window | | CAGR | Sharpe | max drawdown | worst day |
| --- | --- | --- | --- | --- | --- |
| full history (1,525 bars) | raw | 6.54% | 1.056 | -6.91% | -4.70% (07-07) |
| | clean | 7.71% | 1.342 | -5.78% | -2.88% (04-23) |
| since inception (555 bars) | raw | 17.32% | 1.042 | -13.06% | -9.66% (07-07) |
| | clean | 22.85% | 1.401 | -13.06% | -6.07% (04-23) |

Verdict **MATERIAL** against a band frozen before the run (0.50pp CAGR / 0.50pp drawdown /
0.10 Sharpe). Nothing in the production path was changed: the repair moves every published
number of the book at once, so it is a deliberate decision for a later round, not a
side-effect of this one.

## What is wired

* `Tools/s6_chain_bmc.py` (the single leg list both bm-a and bm-c import): contamination
  **before** shock, because the shock face quotes the contamination face rather than
  recomputing it (one reader, E270). ~35s + ~21s, no network.
* `smoke_test.py`, both product tables: each face's exit-code contract, plus a cross-face
  leg that re-prices every shock from the shock face's own beta and ticket NAV and requires
  the quoted clean worst day to equal the contamination face's published one.
* The shock page carries a **Price quality** block; when the contamination artifact is
  missing it says *unverified*, never *clean*.

## Next

* The CEO live-book page's own stress block (`stress_stats`: today's weights replayed over
  history) reads the same raw panel and will therefore quote the same phantom worst day.
  It is the next consumer to re-derive on repaired prices.
* Repricing the whole book (ticket, card, ledger, ceo page) on repaired prices is a
  one-shot decision that must be taken together, or the faces will disagree about the
  same book.