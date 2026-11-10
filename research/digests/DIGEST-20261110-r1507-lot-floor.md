# DIGEST 2026-11-10 r1507 (bm-c) — one lot is the second floor under "how much money"

**Product.** The CEO page's cost section answered *"how much money before the 8bp/10bp model is
honest"*. It never answered the question that bites first: *can the book be held at all*. A lot is
100 units, so a position whose target weight implies fewer than one lot cannot be bought at that
weight — the reader ends up holding a different book, not a cheaper one.

**Reading (2026-11-09 path, 12 names, 19,890 name-days).**
- median position weight 5.30%, median unit price **100.00 CNY** (bond ETFs dominate the book's
  unit prices; p10 = 1.46 on the equity legs)
- one lot = 10,000 CNY of position → **188,624 CNY** to hold the median position in whole lots,
  **291,701 CNY** so that 90% of name-days are representable
- the fee floor at the rate the ticket pays (10bp) is **162,405 CNY** → the lot constraint is the
  **larger** one, i.e. below ~163k the reader is already buying another basket
- holdable share of name-days: 1万 29.6% / 2万 38.5% / 5万 42.2% / 10万 42.2% / 20万 70.8% /
  40万 99.2% / ≥100万 100%

**Implementation.** `etf_book_min_capital`: `LOT_UNITS`, `lot_nav(price, weight)`,
`lot_dependence()` (same weight path and prices as the ladder), `_lot_verdict()`, `lot` block in the
artifact; selftest 31/31, `--check` re-derives the threshold and the verdict, asserts
`holdable_share` monotone and p90 ≥ median. `etf_book_ceo_page.capital_face()` refuses a lot block
that no longer recomputes from its own published medians; `capital_block()` prints the threshold,
the price it comes from, which constraint bites first, and the holdable table (selftest 186/186).
New smoke leg re-derives the closed form and demands both the number and the paragraph on the page.

**Why the closed form is the published one.** `lot_nav` is `lot × price / weight` on two published
medians, so any reader (and `--check`) can reproduce it; the cell-wise median is published beside it
because median-of-ratios ≠ ratio-of-medians and that gap is the honest width of the reading.

**Encoding note.** The Chinese character 元 written into source and md is correct at byte level
(`e5 85 83`); the console rendering showed `Ԫ` in both directions — judge encoding on bytes.
