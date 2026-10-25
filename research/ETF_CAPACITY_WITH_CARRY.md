# ETF book capacity, re-priced with the cash leg on (r1269)

Answers r1268's open question: *does the repo ladder move the capacity ladder's
break-even NAV?*

Short answer: **yes, but only for the book that actually holds cash.** The 5-name
book the r1260 ladder priced is invested 94.7% of the time (avg cash 5.3%), so the
carry is worth +0.10pp/yr at every scale and break-even stays at 50M. The 12-name
production book (r1263/r1267 config) runs 6.9% average cash after the 8% vol target
and keeps a fatter defensive sleeve, so carry is worth +0.13~0.15pp/yr and
**break-even moves 50M -> 100M**, i.e. the same book can carry 2x the money before it
loses to the pool.

## Ladders (k = 10bp per 1% ADV20 participation, next-open, 20-bar cadence, pooled EW = 2.12%/yr)

| book | carry | 1M | 10M | 50M | 100M | 500M | break-even vs EW |
|---|---|---|---|---|---|---|---|
| 5 names, always invested | off | 6.97% | 5.58% | 3.11% | 1.29% | -6.08% | 50M |
| 5 names, always invested | on  | 6.97% | 5.58% | 3.11% | 1.29% | -6.08% | 50M |
| 5 names, 8% vol target | off | 5.90% | 4.67% | 2.47% | 0.85% | -5.73% | 50M |
| 5 names, 8% vol target | on  | 6.01% | 4.77% | 2.57% | 0.95% | -5.63% | 50M |
| 12 names, always invested | off | 5.09% | 5.09% | 3.48% | 2.00%* | -2.19%* | 100M |
| 12 names, 8% vol target | off | 5.34% | 4.56% | 3.16% | 2.12% | -2.16% | 50M |
| 12 names, 8% vol target | on  | 5.49% | 4.70% | 3.30% | 2.26% | -2.03% | **100M** |

(*invested-12 row printed from the same run; the always-invested book barely de-levers,
so its carry is ~0 as expected -- the mechanism is the vol target, not the ETF.)

## What this is and is not

- Impact model, cost interface, decision grid, bar basis: unchanged from r1260/r1267 —
  one `swappable` difference (the cash leg), so the numbers are comparable per row.
- The repo rate is the ladder3 rolling contract (GC007/GC014/GC028 equal rungs,
  exchange commission charged), 1.88%/yr mean over the window — the same leg the
  production ledger now accrues.
- Not a promotion: exploratory face, no prereg, no verdict, no ledger booking.
- Survivorship is unchanged from r1260 (live-code universe) and still only disclosable.

## Engineering

`scripts/etf_book_forward.py` now accepts a **callable** cost model
`cost(prev_book, new_book, d) -> per-side rate`, which is the `ImpactCost` contract of
the capacity ladder; the scalar path is bit-identical (selftest leg + maxdiff 0.00e+00
against `run_next_open`), so the forward state machine and the capacity ladder can now
be priced by the same object instead of two parallel cost implementations.

Evidence: `results/etf_book_capacity_carry.json` (5 names),
`results/etf_book_capacity_carry_n12.json` (12 names),
`scripts/etf_book_capacity_carry.py --selftest 8/8`.
