# DIGEST 2026-11-10 r1508 (bm-c) — the threshold is money; what the money buys is another book

**Product.** r1507 put a second floor under "how much money does this book need" (one lot = 100
units → 188,624 CNY). That is a threshold on a *continuous* weight path. Orders arrive in whole
lots, so at that money the account does not hold the weights the rule asked for — it holds fewer
names' worth of exposure. This round measures the shortfall instead of caveating it, and prints it
on the same page, under the threshold it qualifies.

**Reading (2026-11-09 weight path, 12 names, 1,658 decision bars).**

| capital | names targeted | names actually held | targets that cannot buy one lot | money never invested | share of target |
|---|---|---|---|---|---|
| 10,000 | 12.0 | 2.53 | 9 | 5,020 | 78.9% |
| 50,000 | 12.0 | 4.41 | 7 | 20,115 | 63.2% |
| 200,000 | 12.0 | 8.63 | 3 | 35,719 | 28.1% |
| 400,000 | 12.0 | 10.17 | 0 | 38,847 | 15.3% |
| 10,000,000 | 12.0 | 11.92 | 0 | 42,021 | 0.7% |

- at the threshold itself (188,624 CNY): **7.73 of 12 names**, 4 targets unbuyable, **42,722 CNY
  never invested**, verdict `ROUNDING_EATS_A_NAME_OR_MORE`
- flooring is **one-way by construction** (never models rounding *up*: an over-weight lot is a
  weight the rule never asked for, and printing it would conflate venue granularity with a rule
  change) — so the shortfall is always "you hold less", never "you hold more"
- **the residue does not shrink to zero as capital grows**: it is ≈ half a lot per name
  (`lot × price / 2 × n`), which is ~40k CNY at every rung. What shrinks is the *share* (78.9% →
  0.7%), not the money. A reader told "this only bites small accounts" would be told half the
  truth: at 10M CNY the book still leaves ~42k of intended exposure unbought.

**Implementation.** `etf_book_min_capital.lot_rounding()` walks the same weight path and the same
prices as the ladder: target units `w*NAV/price` → `floor(units/lot)*lot`, per capital rung,
recording `names_effective`, `names_short`, `residue_cny`, `under_pct`. The published row is a
closed form on the medians (`names_effective = names_target × (1-under_pct)`,
`residue = capital × weight_sum × under_pct`), so a reader and `--check` can re-derive it from two
printed numbers; the cell-wise medians ride beside it because median-of-products ≠
product-of-medians. `_rounding_verdict()` is derived from the anchor row. The block is anchored on
`lot_nav_median`, so the threshold and the holdings can never describe different capitals.
`etf_book_ceo_page.capital_face()` refuses a rounding block that no longer closes (order broken,
holds more names than targets, share disagrees with its own counts, anchor off the threshold,
verdict disagreeing with its anchor row); `capital_block()` prints the sentence, the eight-column
table and the verdict. selftest **35/35** (+4 L32-L35), `--check` OK, page selftest **189/189**
(+3 L136-L138), page rewritten with the section in place.

**Why a second face instead of a footnote.** "You need 188,624 CNY" answers *when the position
stops being zero*. "At 188,624 CNY you hold 7.73 of 12 names, and 42,722 CNY of the intended
exposure buys nothing" answers *what you own* — and they are different numbers about different
books. Threshold + holdings must be printed together, with the direction of the rounding stated,
or the reader will assume the first number is the second.

**Inheritance note.** Both the producer diff and the page diff were found uncommitted in the tree
when this round opened (a dead window's edits, 14:47 and 14:54). Per the r1213 law the work was
re-verified on the final tree — the selftests, `--check`, the rebuilt page and the inline
re-derivation of the new smoke leg's assertions were all re-run here — before landing. Console
mojibake on those diffs was a rendering artefact only: the file decodes as strict UTF-8 and reads
correctly.