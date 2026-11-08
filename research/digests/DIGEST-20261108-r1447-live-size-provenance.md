# r1447 — which rule sizes the money that is about to be traded

**Question (r1446's open item).** r1446 established that the caliber dispute cannot move
the money: the executed book `nobond_vt08_adopted` reads CONDITIONAL under all three
calibers. It left a second question standing, and it is the one that lands on 2026-11-11:
the weight in force is 0.460253, but the year gate adjudicates a book that sizes itself
with an 8% volatility target. Two numbers that happen to agree today are not the same
number, and a size nobody graded is not a graded size.

**Face.** `scripts/etf_book_live_size_provenance.py` — one question only: at the ticket's
own decision bar, on the ticket's own panel, do the beta rule and the vol target put the
same fraction of capital at risk, and do they hold the same names? It does not re-price
returns for the gate, does not change any rule, does not touch the ledger.

**Reading (published in `results/etf_book_live_size_provenance/SIZE-PROVENANCE.json`).**

| leg | value |
|---|---|
| decision bar | 2026-10-14 (the ticket's own `book_decided_at`) |
| priced bar | 2026-11-06 |
| beta rule k (reproduces the ticket) | 0.460253 |
| vol rule k at the same bar | 0.648195 |
| gap | **−18.79pp of NAV** |
| money at 999,008 NAV | 459,797 (beta) vs 647,552 (vol) = **−187,755 CNY** |
| names | 4 of 5 differ (only 159263 shared) |
| classes of the ticket's 5 names | 4 × `crossborder`, 1 × `equity` |
| graded card's universe | equity / commodity / convertible |

**Verdict `DIFFERENT_BOOK_AND_SIZE`** — with all five identity legs green: the beta-rule
k reproduces the ticket's 0.460253 exactly, its five names are the ticket's five names, the
cited constant still equals the module's, the priced bar and the decision bar both match.

So the answer to r1447 is no: the weight in force was not set by the rule of the book that
was graded. And the second half is the sharper one — **four of the five names the money is
in belong to a class the graded card never prices** (`crossborder`; r1438 recorded the
vocabulary mismatch without a count). A book that is smaller than the graded one but holds
names the graded one never prices is not "the same exposure, sized down": the two sizes are
not comparable and neither 0.46 nor 0.65 can be argued from the other.

**Self-catches.**
1. The first run of this face published `IDENTITY_FAIL` and read the *wrong* decision bar
   (2026-10-23, the engine's own re-decision phase from `k_schedule`) and the wrong names
   (the panel's last bar). r1229 already fixed the ticket onto the fixed 2020-01-01 20-bar
   grid; this face had rebuilt the second clock instead of reading the ticket's. Caught by
   the leg that compares derived names to the ticket's — a construction difference was
   wearing the costume of a ticket defect, and the honest thing to do was fix the reader,
   not the ticket. `ticket_grid_bar()` is now one function with four selftest legs.
2. The money leg first failed on 0.45 CNY: `nav × k` is the counterfactual target, the
   ticket's `book_amount` is what whole lots can actually buy. Rather than loosen silently,
   the leg now prints both residuals (0.4500 / −0.1188 CNY) and bounds them at 0.1% of NAV.

**Not claimed.** The wrapper's yearly shape (r1440 already read it), any size change for
2026-11-11 (that needs a caliber prereg, r1446), and the bet that `crossborder` exposure is
unsafe — it is recorded as ungraded, not as bad.

Card: `knowledge/METHODOLOGY_ASSETS.md` E452.