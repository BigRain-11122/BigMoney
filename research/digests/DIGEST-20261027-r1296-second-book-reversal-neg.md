# E139 — The second book is not short-horizon reversal (and book A has to be the shipped book)

Round r1296, bm-c, 2026-10-27. Tool: `scripts/etf_book_pair.py` (selftest 5/5),
face: `results/etf_book_pair.json`, evidence_cutoff 2026-10-26.

## The question

The capacity study (r1280/r1295) closed the "make the same book bigger" door: at 1% of
ADV the shipped book holds ~1.5M CNY, at 5% ~7.6M, and buying that 5x costs 0.64pp of
CAGR. The one lever left on the table was *a second, low-correlated book* — two books that
trade different names do not queue behind each other's ADV, so capital adds.

This round measured the most natural candidate on the same panel: a **short-horizon
reversal book** (rank on −5d return, 10 names, 10-bar cadence, same 8% vol target, same
10bp/side, same open-to-open execution).

## What came back

| book | CAGR | Sharpe | maxDD | OOS CAGR | turnover |
|---|---|---|---|---|---|
| A — shipped trend, 12 names / R20 / VT8 | **+9.49%** | **0.980** | −11.77% | +18.10% | 0.93 |
| B — reversal, 10 names / R10 / VT8 | **−3.67%** | **−0.373** | −33.59% | −1.67% | 0.65 |
| 50/50 blend (daily rebalanced) | +2.84% | 0.393 | −16.16% | +7.95% | — |

Correlation of daily returns: **0.461 full / 0.612 in-sample / 0.252 out-of-sample**.
Decision-day name overlap: **6 of 83 days (7.2%)**.

So the candidate is shaped exactly right — it is genuinely a different book, it trades a
different set of names, and it de-correlates further out of sample — and it still loses
money in every period. At 50/50 the blend is worse than book A alone on all four metrics.
Diversification into a negative-expectancy leg is just slower losing.

Verdict: **short-horizon cross-sectional reversal on the ETF panel is closed as a
second-book candidate.** The second-book search stays open; reversal is not the answer.

## The mistake worth keeping

The first cut of this measurement built book A from `E.build_panel()` — the full universe,
bonds and money-market funds included — and priced it at **6.74% / Sharpe 0.896 / maxDD
−9.45%**. The shipped book is priced through `etf_book_production.prep_panel()`: class
restricted to equity + commodity + convertible, with the 168 split-print cells repaired.
Same code, same factors, same cadence — a **2.75pp** difference in CAGR.

Nothing errored. The comparison was internally consistent and the correlation number
(0.345) was plausible. The only thing wrong was that "book A" was a book nobody runs, and
every downstream statement ("the blend delivers 6.14% OOS", "correlation 0.345") inherited
that error. Any A/B claim about adding or removing a structure has to start by proving the
control arm is the shipped configuration — here that meant importing the production
panel builder rather than rebuilding a panel that looks similar.

## Reproduction

```
python scripts/etf_book_pair.py --selftest   # 5/5
python scripts/etf_book_pair.py              # ~90s, writes results/etf_book_pair.json
```

Selftest legs guard the two ways this measurement can silently lie: L2 that the reversal
score at *t* does not see *t+1*, and L4/L5 that the blend is not a no-op (a 50/50 blend of
identical legs must reproduce the leg; an uncorrelated blend must cut vol).