# E141 — Trend in ETFs is not a second book either: the blend test is a Sharpe test

Round r1299, bm-c, 2026-10-27. Tool: `scripts/etf_book_tsmom.py` (selftest 13/13).
Face: `results/etf_book_tsmom.json`. evidence_cutoff 2026-10-26.

## The question this round answers

r1297 screened five **cross-sectional** ETF mechanisms and rejected all five; r1298 then
killed the futures trend sleeve for a reason unrelated to the signal (CNY 8.08M capital
floor, 17% of target notional achievable at CNY 1M). Between them they left one gap: is
**time-series** trend in an instrument with no capital floor (ETFs, 100-share lots) a
usable second book? Book A ranks ETFs against each other and holds the top 12; this
measurement asks, of each ETF independently, "is this instrument in an uptrend?", holds
whatever says yes, and sizes the whole book to the same 8% vol target.

Same panel the production card prices (1,499 names, 168 split prints repaired), same
open-to-open execution, same 10bp/side, same 8% vol target. Control arm **is** the shipped
book: computed 9.49% vs the published card 9.49% (delta 0.0pp, tolerance 0.5pp pinned).

## Results — four variants, all rejected

| variant | CAGR | Sharpe | maxDD | OOS CAGR | corr vs A | cash days | avg names | equal-risk blend | verdict |
|---|---|---|---|---|---|---|---|---|---|
| tsmom60_e (60d sign, equal wt) | +0.92% | 0.15 | −28.5% | +5.60% | 0.678 | **0.0%** | 150 | +5.33% / SR 0.63 | blend loses to A |
| tsmom120_e (120d sign, equal wt) | +1.13% | 0.18 | −25.3% | +6.09% | 0.672 | **0.0%** | 162 | +5.44% / SR 0.64 | blend loses to A |
| tsmom60_iv (60d sign, inverse vol) | +1.74% | 0.24 | −25.4% | +6.92% | 0.724 | 0.0% | 150 | +5.79% / SR 0.67 | same trade (corr ≥ 0.70) |
| tsmom120_iv (120d sign, inverse vol) | +1.63% | 0.23 | −24.1% | +7.40% | 0.712 | 0.0% | 162 | +5.70% / SR 0.66 | same trade (corr ≥ 0.70) |

## Two readings that outlive the table

**1. Breadth trend on a broad ETF universe never goes to cash.** `cash days = 0.0%` on all
four arms: across 1,499 instruments there is always a triple-digit number of ETFs whose
trailing return is positive, so the "defensive switch" the trend filter is supposed to give
you never triggers. The book holds ~150–162 names at all times, i.e. it is a diluted
long-equity book with an 8% vol cap, not a risk-managed trend system. A trend filter needs
an **index-level or single-instrument** signal to produce a flat state; breadth over a
permissive universe produces beta.

**2. At equal risk, the 50/50 blend is a Sharpe test, not a correlation test.** Both legs
were scaled to the same realised vol before mixing (r1291/r1297: fixed weights are a
leverage decision). The second leg runs 0.15–0.24 Sharpe against book A's 0.98, so mixing
it in halves the return no matter how decorrelated it is: +5.3% to +5.8% vs A alone at
9.49%. Being a *different trade* is necessary and nowhere near sufficient — the candidate
has to earn a Sharpe comparable to the incumbent.

Correlation 0.67–0.72 despite a completely different construction (per-name trend vs
cross-sectional rank, 150 names vs 12, inverse-vol vs equal weight) is the same finding
from another angle: in one asset class, long-only, the directional exposure dominates.

## Where the second book has to come from

Three rounds now close the ETF panel as a second-book source from three directions
(reversal r1296, five cross-sections r1297, time-series trend r1299) and close futures on
capital grounds (r1298). The remaining candidates all require something this firm does not
have yet, and each one should be named as such rather than screened again:

* a **sub-million-capital** instrument class with genuine orthogonal drivers — the futures
  sleeve re-expressed as ETFs (commodity/gold/bond ETFs) is measurable on the existing
  panel and is the cheapest next test;
* a **different holding period** on the same instruments (the shipped book rebalances
  every 20 days at 8% vol — an intraday or multi-month book is a different risk premia);
* **carry/flow** rather than price, which needs data the panel does not hold
  (r1297 already noted carry is unmodelled).

## Reproduction

```
python scripts/etf_book_tsmom.py --selftest   # 13/13
python scripts/etf_book_tsmom.py              # ~2 min, writes results/etf_book_tsmom.json
```