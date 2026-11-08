# DIGEST 2026-11-09 r1615 bm-b — E587: the two cash faces of the book use different repo windows

**Round**: 1615 (bm-b). **Card**: E587, closed. **Face**: `results/etf_book_order/CASHWINDOW.json`
(+ `CASHWINDOW-latest.json`). **Script**: `scripts/e587_cash_window.py` (selftest 13/13).

## Question

E585 (r1613) measured what the ticket's `cash_leg` block prints: the mean of GC001 over
2020-01-01..cutoff at 252, not the rate on the bar the ticket names. The other cash face of the
same book is the forward ledger (`results/etf_book_forward/LEDGER.json`), which accrues the
three-rung repo ladder (GC007/GC014/GC028, commission charged) bar by bar at 244. Do the two come
from the same window? And does the ledger's `carry` column reproduce from the panel at all?

## Reading

| arm | value |
|---|---|
| ledger ladder3 annualised over its own 11 bars (2026-10-23..11-06) | **0.850%/yr** |
| same ladder with commission waived | 1.146%/yr |
| GC001 mean over exactly those 11 bars | 1.040% |
| GC001 mean over 2020-01-01..2026-11-06 (1650 bars) | 1.982% |
| what the 5 tickets print | **2.079%..2.090%/yr** |

Arithmetic split of the printed-minus-accrued gap (**+1.237pp**):
window **+0.942pp**, instrument **+0.190pp**, unexplained **+0.105pp** (a split, not an
attribution).

Faces naming the window they used: **0 of 7** (5 tickets + the ticket block + the ledger). The
ledger names its *leg* ("ladder3 (GC007/GC014/GC028) commission charged") but not its window.

## The ledger's carry column, rebuilt under seven rules

| rule | within 1e-4 | within 1% | rows with a reading | worst rel diff |
|---|---|---|---|---|
| ladder3 at this row's cash | 0 | **7** | 11 | 1.347 |
| ladder3 at the previous row's cash | 0 | 7 | 11 | 1.347 |
| ladder3 at the next bar's quote | 0 | 5 | 10 | 2.015 |
| ladder3 gross of commission | 0 | 8 | 10 | 1.347 |
| GC001 prior-bar quote, one day | 0 | 0 | 3 | 2.980 |
| GC001 prior-bar quote, calendar gap | 0 | 0 | 3 | 0.327 |
| GC001 same-bar quote, one day | 0 | 0 | 3 | 2.980 |

Row classes: ladder-within-1% **7**, neighbour bar's ladder **1**, gross-only **1**, no rule **2**,
exact **0**. So E584's `rows_reproducing_the_ladder = 0/11` is not "the record is wrong end to
end": nothing reproduces *exactly*, four rows miss in four different ways, and one of those ways
(a row carrying the next bar's ladder) is the fingerprint of an alignment slip.

**The card's own hypothesis was wrong**: it asked whether the ledger's `rf` comes from the prior
bar's GC001 quote. All three GC001 rules reproduce **0 of 3** rows. The ledger accrues the ladder.

## Money

On the ticket's cash_amount of 529,072 CNY, one bar of carry at 2.08%/yr is ~43.7 CNY and at
0.85%/yr ~17.8 CNY — the printed rate is ~2.4x the accrued one on the same cash.

## Wiring

- S6 leg `cash_window` (`python Tools/s6_chain_bmb.py 1615 --only cash_window` → rc0, 0.04s).
- Smoke block `# E587` in `smoke_test.py` (refuses a ladder diff that does not re-derive, a class
  that does not follow from its own numbers, a split that does not add to the gap, and a verdict
  that does not follow from the summary). Exercised standalone via `_r1615_legcheck.py`
  (problems=[]), removed in-window; the full suite was **not** launched (no leg filter, r1499).

## Next

E589 (seeded, cpu-only): make the `cash_leg` block publish `window_start / window_bars /
day_count / repo_panel_last_bar` beside the ticket-bar quote, and re-issue one ticket to show the
shape — the defect E585/E587 measured is a disclosure gap, and the fix is one block.