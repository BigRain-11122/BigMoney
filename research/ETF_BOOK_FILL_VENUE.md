# Where do you fill it? The missing bar is not a fill price

Face: `results/etf_book_fill_venue.json` (evidence cutoff 2026-10-30, 1653 bars, 24.2 s).

Same signal, same panel, same 20-bar grid, same 10bp/side, same 8% vol overlay.
The card and close fills differ ONLY in the price series the book is filled and marked
at -- same names, same dates. The next-open fill is the same rule read one bar earlier,
which is what the executable ledger does.

| fill | where | CAGR | Sharpe | maxDD | turnover/fill |
|---|---|---|---|---|---|
| card | open of bar d (published, not achievable) | 9.60% | 0.99 | -11.77% | 0.934 |
| next_open | open of bar d+1 (the ledger) | 8.46% | 0.87 | -16.56% | 0.953 |
| close | close of bar d (closing auction) | 8.43% | 0.89 | -13.08% | 0.923 |
| close_i2 | close + 2 bp/side extra | 8.19% | 0.87 | -13.27% | 0.923 |
| close_i5 | close + 5 bp/side extra | 7.83% | 0.83 | -13.54% | 0.923 |
| close_i10 | close + 10 bp/side extra | 7.23% | 0.77 | -14.01% | 0.923 |
| close_i15 | close + 15 bp/side extra | 6.63% | 0.71 | -14.47% | 0.923 |
| close_i20 | close + 20 bp/side extra | 6.04% | 0.66 | -14.93% | 0.923 |
| close_i30 | close + 30 bp/side extra | 4.86% | 0.54 | -15.84% | 0.923 |

## The money ladder (what each convention is worth)

| convention | what it is | CAGR |
|---|---|---|
| card | fill at open[d] with the close[d] signal | 9.60% |
| close | same signal, fill at close[d] (closing auction) | 8.43% |
| next_open | same rule, one bar earlier, fill at open[d] | 8.46% |
| ledger_no_carry | the executable ledger, no repo carry | 8.53% |
| ledger_carry | the executable ledger, with repo carry | 9.12% |

- switching the **fill venue** (close vs next open) moves the book by **-0.03 pp/yr**
- switching the **marking basis** (open-to-open accrual vs the ledger's close-marked book) moves it by **+0.07 pp/yr**
- the part of the headline that is **not in the executable book at all**: **+1.07 pp/yr**
- headline vs the executable book **including repo carry**: **+0.48 pp/yr**

So the honest split of the 1.14pp is: 0.00pp of it is a fill choice, 0.07pp of it is
how the book is priced, and 1.07pp of it is a bar that is not tradable. The ledger
already earns the executable number (9.12% with carry) -- nothing an operator can do
at the venue recovers the rest.

## Verdict

- **INFORMATION_DOMINATES**
- one-bar gap (card - next_open): **+1.14 pp/yr**
- recovered by filling at the close: **-0.03 pp/yr (share -0.0263)**
- execution budget at the close: **none -- even a free closing fill does not reach the causal book**

Reading: the two fills an operator can actually get -- the closing auction and the
next open -- land within 0.03 pp/yr of each other, so the venue is not the lever.
The card's extra bar is not purchasable at any venue: it is spent between the open
and the close of the bar whose close produced the ranking. What does change the
money is the executable book's own carry (repo rungs), already inside the ledger.

## What this is not

- not a claim that a closing fill is free: the extra-cost grid prices auction impact
  and the rank-vs-fill price gap together, it does not separate them
- not a re-statement of the look-ahead finding: the card arm and the causal arm here
  must reproduce `results/etf_book_lookahead_audit.json` to 1e-6 pp or the face refuses
  to publish (cross-artifact gate, see `cross_artifact.agrees`)
- not an instruction to change production: the ledger already fills at the next open;
  switching to closing-auction fills is an adoption decision with its own freeze

Reproduce: `python scripts/etf_book_fill_venue.py run|--check|--selftest`.
