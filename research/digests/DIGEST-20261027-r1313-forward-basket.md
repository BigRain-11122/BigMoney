# DIGEST 2026-10-27 r1313 bm-c -- the track record gets a rival on its own bars

**The question r1312 left open.** The four-beta regression said the book's intercept is a 2020-2026 property,
but that is an annual, window-shaped answer. The live forward ledger, seeded 2026-10-23, recorded only the book's
own nav -- so a reader asking "are we beating just holding the four exposures" had nowhere to look except back
into the regression.

**What shipped.** `scripts/etf_book_forward.py` now accrues a second arm: the same equal-weight four-ETF basket
that the annual spanning study uses (gold 518880 / Nasdaq QDII 513100 / CSI300 510300 / bond 511010), priced on
the book's decision grid, filled at the book's next open, costed on its own turnover, rebased to the same seed
bar. Every ledger bar carries `nav / book_nav / excess`, and `benchmark.latest.excess_pp` is the one-number
answer. The S6 leg prints it every run, and `scripts/etf_book_ceo_page.py` lifts it into the CEO one-pager.

**First reading** (2026-10-27, 3 bars from the 2026-10-23 seed): book 1.00400 vs basket 0.99649 -> **+0.75pp**.
Three bars is not a track record and the page says so in the same line.

**What was caught before canon.**
- The basket started un-invested, so until the first grid decision it published a flat 1.0 line and passed every
  identity leg -- the r1261 "prove the mechanism ran" class, caught by a dedicated movement assertion.
- Excess computed as a difference (1.05 - 1.02 = 3.00pp) instead of a ratio (2.94%) flatters the book by the
  basket's own move; pinned by a hand-checkable leg.
- The engine convention charges weight-drift rebalancing on neither arm, so the basket's drift turnover is
  published as friction (~1.8 bp/yr if charged) rather than quietly booked against one side; a cost-sweep
  identity leg pins that.
- Published basket bars now join the ledger's drift gate: a basket bar that stops reproducing freezes the ledger
  (exit 3) exactly like the book's own marks.

**Known limit.** The CEO one-pager is single-writer on bm-a (`writer_allowed('bm-a')`), so this host wired and
tested the line but could not render the page; the next bm-a render will carry it. Disclosed, not worked around.

Evidence: `results/etf_book_forward/LEDGER.json` (benchmark block), `scripts/etf_book_forward.py`
(selftest 33 legs, 9 new), `scripts/etf_book_ceo_page.py` (selftest 28, 2 new), methodology card E155.