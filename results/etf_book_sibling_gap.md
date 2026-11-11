# ETF book -- the sibling premium gap: a price today, or a rule?

session `2026-11-10` | ticket `TICKET-2026-11-11.json` | source `results\etf_book_sibling_entry.json`

**no pair carries both a premium gap and a local price history**

| leg | sibling | index | today gap | history mean | sd | days | percentile | verdict |
|---|---|---|---|---|---|---|---|---|

## legs the sibling face could not price

- 510760: label 上证指数ETF names no other live ticker on this board (no sibling group)
- 512040: label 价值ETF names no other live ticker on this board (no sibling group)
- 159655: label 标普500ETF names no other live ticker on this board (no sibling group)
- 513690: label 港股红利ETF names no other live ticker on this board (no sibling group)
- 159519: label 港股国企ETF names no other live ticker on this board (no sibling group)

## caveats

- the reconstructed gap is anchored on ONE session's IOPV pair; every earlier value inherits the assumption that the two funds' NAV-per-unit ratio has not moved, and steps are published as the evidence against that assumption
- closes are as-traded, not total-return: a distribution to one fund only lands as a step and is flagged, not corrected
- same index, not same basket: tracking difference, fee, size, quotation width and FX-hedge policy are NOT priced here
- premium history from our own board starts at one session; this face uses the price ratio for history precisely because it is the only long series we have
- a step is a flag, not an error: the level after a step is still the level a buyer would pay today
