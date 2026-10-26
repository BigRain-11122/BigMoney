# DIGEST 2026-10-26 — E81 leg 4: the 18-cell robust grid's floor was a split print

Tool: `python scripts\etf_robust_pf.py --repair`
Twin (E81 rule, published face never rewritten in place):
`results/etf_robust_pf_repair.json` beside the untouched `results/etf_robust_pf.json`
Repaired prints: 168 (identical count to the production-book audit's `prints_reported_now`)

## What the published grid said

`etf_robust_pf.json` is the 18-cell robustness face of the composite ETF book
(hold 3/5/8 × rebalance 10/20/40 × cost 5/10 bp, next-open execution). It reads
5.80 % – 10.13 % CAGR, every one of the 18 cells positive — the number the card quotes
as "no grid cell loses money".

## What the repair does to it

Same code, same universe, same score builder; the only change is
`etf_equity_alpha.repair_flips` on the price panel (single-bar move past 35 % → 0 %
return, both faces rescaled). Fourteen of the eighteen cells reproduce **bit-identically**.
Exactly four move:

| cell | CAGR pub → rep | Δ pp | Sharpe pub → rep | Δ | maxDD Δ |
|---|---|---|---|---|---|
| N8_R20_5bp | 8.66 → 9.70 | +1.04 | 0.847 → 0.953 | +0.106 | 0.00 |
| N8_R20_10bp | 7.85 → 8.88 | +1.03 | 0.776 → 0.881 | +0.105 | 0.00 |
| N8_R40_5bp | 6.20 → 7.21 | +1.01 | 0.619 → 0.718 | +0.099 | 0.00 |
| N8_R40_10bp | 5.80 → 6.81 | +1.01 | 0.584 → 0.683 | +0.099 | 0.00 |

Grid floor 5.80 → 6.81 %; ceiling unchanged at 10.13 %; total negative years unchanged at 13.

## Reading

1. **The pollution is a function of book width × holding period, not of the signal.**
   All four movers are the widest (8-name) and slowest (20/40-day) cells — the only books
   that carry a defensive name (bond/currency) across a split-print bar long enough to be
   charged at 1/n. Every N3/N5 cell and every R10 cell is byte-identical: those books
   never held the affected names across the flip.
2. **The claim survives, and gets stronger where it was weakest.** "18/18 positive" holds
   on both panels; the repair lifts the floor by ~1 pp and leaves the rebalance/widening
   trade-off shape (max drawdown 10.02 % – 15.91 %, monotone in hold size) untouched.
3. **The production cell is not implicated.** The card's live config sits on the N5/N10
   fast-rebalance side, which is bit-identical between the two faces — consistent with
   `etf_book_split_audit`, which prices the repair at +2001.32 bp on the *published*
   12-name card and asserts card agreement (repair = data fix, not a knob).
4. Same asymmetry as E81 legs 2–3: only the wide book moves. Third instance in one day
   of "screened faces move only where the wide book turns over".

## Honesty

- The screen can only remove prints the panel shows as integer-ratio jumps; a print the
  source never published is unrecoverable.
- Cost is the engine constant (5/10 bp/side), not a measured schedule.
- Descriptive census: no gate, no verdict, no prereg, no trial count. The published face
  is untouched; the twin is additive.