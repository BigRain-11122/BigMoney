# r1305 — the book's edge is a 2020+ regime, and breadth is only a second contributor

Every number this company publishes for the ETF composite book lives inside
2020-01..2026-10, on a panel whose eligible cross-section grows from single digits (2013)
to ~720 names (2026). Two different stories produce that same chart: the six-factor
composite, or a universe that is mostly made of funds which only exist *because* the
industry grew. `scripts/etf_book_pre2020.py` separates them by pricing the **same engine,
same file panel, same cost**, on the 224 ETFs whose first bar is on or before 2020-01-01 —
over a window no published number has ever covered.

Grid: N in {3,5,8} x R in {10,20}, primary N5/R20, 10bp per side, decide at close t, fill
at open t+1, eligible = 20d median amount >= 20M CNY and >= 120 bars of history.

| cell | universe | window | book CAGR | EW CAGR | excess | null p |
|---|---|---|---|---|---|---|
| A | U_pre (224) | 2015-01-01..2019-12-31 | **-4.97%** | +3.89% | **-8.86pp** | 0.96 |
| B | U_pre (224) | 2020-01-01..2026-10-26 | **+6.86%** | +3.87% | **+2.99pp** | 0.10 |
| C | U_all (1608) | 2020-01-01..2026-10-26 | **+7.29%** | +2.00% | **+5.29pp** | 0.06 |

A vs B holds the universe fixed and moves the period. B vs C holds the period fixed and
moves the universe. Reading one without the other is how "the edge is real" and "the
cross-section is the edge" both get published off the same numbers.

**What the split says.**

1. **The period is the binding term, not the cross-section.** On the identical 224 names,
   the composite's excess is +2.99pp/yr in 2020+ and **-8.86pp/yr in 2015-2019**, worse in
   **6/6** grid cells (-5.81..-8.86pp). Random-score null p=0.96, i.e. the factor ranking
   sat at the *bottom* of its own permutation distribution: picking ETFs at random in
   2015-2019 beat the composite 96% of the time. This is not noise at the edge of zero.
2. **Breadth is real but additive, not the source.** Same period, widening 224 -> 1608 names
   lifts excess from +2.99pp to +5.29pp (+2.30pp). So the wider universe is worth something
   — but cell B already has positive excess with no breadth help, and cell A has none with a
   universe that was *not* smaller in any way that matters (30-31 eligible names per
   decision, min 14, versus 98-99 in B).
3. **The published 9.49% card is therefore a single-regime number.** It is not
   contradicted, but it has no out-of-period support: the same code on the same panel,
   asked about the preceding five years, loses money. Any expectation band built off
   2024-2026 (OOS 2024+ is where most of the return sits) is extrapolating one regime.

**Control.** The published N5/R20 next-open arm re-prices at 7.62% vs 7.61% printed
(-0.01pp), on a panel three trading days longer than the published cutoff — so the arm
compared above is the arm that was published, and the delta is extra data, not code.

**Carried limits.** The panel holds no delisted funds, so U_pre is survival-filtered too: a
pre-period that *fails* while filtered is a stronger negative than the same number on a
complete universe would be, but a pre-period that *passes* would be weaker evidence than it
looks. Dead names are forward-filled at zero return rather than at liquidation value. The
N8 cells are thin (7 and 4 of 122 decisions had fewer than 2*n_hold eligible names in A), so
N5/N3 carry the read. No preregistration, no verdict, no ledger booking.

**Where it lands.** `scripts/etf_book_production.py` now reads this artifact and prints the
verdict on the card as the first caveat, with two selftest legs (present -> disclosed,
absent -> production face still runs). The measurement is not allowed to live only here.
Artifact: `results/etf_book_pre2020.json` (schema `etf_book_pre2020/v1`).