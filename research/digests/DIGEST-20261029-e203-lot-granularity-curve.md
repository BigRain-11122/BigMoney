# E203 — the lot granularity cost is a CURVE, and its yuan amount does not shrink (r1334 bm-c)

**Card:** E203 in `knowledge/METHODOLOGY_ASSETS.md`.
**Artifacts:** `results/etf_book_order/LOTCURVE-2026-10-28-card.json` (re-emitted every chain run by
the existing `etf_book_order_card` leg) + the new section of `results/etf_book_order/ORDER-2026-10-28-card.md`.
**Code:** `scripts/etf_book_order.py` — `lot_point()` / `lot_curve()` / `lot_curve_md()`, selftest 33→39.

## The question r1333 left open

r1333 issued the executable ticket from the production card's own sheet and published one number:
at 1M CNY the 12-leg book spends 0.13% NAV less than the card's target amount column. One number
answers "is today's ticket executable". It does not answer the question an operator actually has:
**how small may this book be before the ticket stops being the book?**

## What was measured (same card, same weights and prices, only the stated capital changes)

Capital grid 50k → 20M, whole lots, buys floored (the ticket's own accounting — nothing new is
modelled here):

| capital | max leg weight drift | legs below one lot | cash above the card's row |
|---|---|---|---|
| 50,000 | 1.103pp | 0 | 1,282 |
| 100,000 | 1.103pp | 0 | 1,710 |
| 200,000 | 0.511pp | 0 | 1,606 |
| 300,000 | 0.314pp | 0 | 1,870 |
| 500,000 | 0.156pp | 0 | 1,640 |
| 750,000 | 0.156pp | 0 | 2,203 |
| 1,000,000 | 0.037pp | 0 | 1,279 |
| 2,000,000 | 0.037pp | 0 | 1,590 |
| 3,000,000 | 0.037pp | 0 | 1,949 |
| 5,000,000 | 0.014pp | 0 | 1,709 |
| 10,000,000 | 0.002pp | 0 | 961 |
| 20,000,000 | 0.002pp | 0 | 1,108 |

Derived thresholds, read off the curve rather than asserted: drift ≤1.00pp needs **≥200k**,
≤0.50pp needs **≥300k**. One-lot floor (most expensive lot ÷ smallest weight, i.e. the capital
below which some leg cannot be bought at all) = **20,277 CNY** for this book — far below any
capital this book would be run at, so "you cannot execute it" is not the real risk here.

## The two readings disagree about direction, and that is the finding

- **Weight drift is monotone non-increasing in capital** (1.103 → 0.002pp). It is a percentage
  cost of small books and it behaves.
- **The cash shortfall is NOT monotone — it is a sawtooth**: 1,282 → 1,710 → 1,607 → 1,870 →
  1,640 → 2,203 → 1,280 → ... Each point depends on how far each leg happens to sit above a whole
  lot at that capital, which is a residue, not a scale effect.

The bound explains it: each leg can leave at most one lot unspent, so the shortfall is bounded by
**Σ price × 100** = **3,102.29 CNY** for this book, and the measured maximum over the grid is
2,203.36 (at 750k). Under that bound the yuan amount is essentially **fixed**; only its share of NAV falls
(2.56% at 50k → 0.006% at 20M). So "the ticket can only spend less than target" is a **fixed
small desk cost**, not a size-dependent tax — and the card's cash row is wrong by a stable
1-2k CNY no matter how big the book gets.

*Numbers above are read back from `LOTCURVE-2026-10-28-card.json` after the artifact was re-derived in
this window (scratch figures in the first draft of this digest quoted a fixture bound of 1,853.79 /
1,498.96 and an off-by-one cash column; the artifact was regenerated and the text rebuilt from it, so
the page a human reads and the JSON agree — determinism was checked by a byte-identical re-run).*

## Why this is on the operator's page and not in a research file

`run_card()` now writes `LOTCURVE-<bar>-card.json` and appends the table + both thresholds +
the bound to the same ORDER sheet a human reads, so the cash row the operator sees and the cash
the desk gets are reconciled on one page. The leg is already on the S6 chain (`etf_book_order_card`),
so this face cannot silently go stale (r1290 class).

## Caveats

- Reference prices only (the card's own sheet), no impact cost, no gap risk, no T+1 slippage; the
  curve prices lot granularity and nothing else.
- The card is an exploratory face: no prereg, no verdict, not in the scorecard.
- The 12-name book's own weights come from the card; if the card's bar rolls, the curve rolls with
  it (it is derived, never stored as a constant).