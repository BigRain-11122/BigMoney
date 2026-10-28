# DIGEST 2026-10-29 — E201 — the executable ticket was a different book

Round r1333 (bm-c). Face: `results/etf_book_order/ORDER-2026-10-28-card.md` +
`results/etf_book_order/TICKET-2026-10-28-card.json` (mode `card` in
`scripts/etf_book_order.py`, selftest 26→33).
Upstream: `results/etf_book_production/latest.json` (the card) and
`results/etf_book_forward/LEDGER.json` (the live ledger).

## The question

Three faces called themselves "the production book": the card (12 names, 8% vol
target, 1M CNY sheet), the forward ledger (same config, live since 2026-10-23) and
the executable order ticket (5 names, fixed beta 0.20). r1290 had already made the
two production faces name each other and print a width/rule disclosure — but the
ticket was still *re-ranked at its own width*, so the disclosure was a paragraph
explaining that the operator holds a book nobody published a risk record for.

## What was built

`etf_book_order.py card` issues the ticket **from the card's own sheet**: names,
weights and the risk scale are read, never re-derived; the stated capital only
re-prices whole lots. The sheet then prints a three-face table and recomputes each
card lot count from price × weight, publishing mismatches instead of trusting them.

Live reading (2026-10-28 bar, NAV 1,000,000, k=0.7008):

| face | names | rule | scale | bar |
|---|---|---|---|---|
| production card | 12 | vol 8% | 0.7008 | priced 2026-10-28 |
| forward ledger | 12 | vol 8% | 0.7008 | book 2026-10-14, last 2026-10-28 |
| this ticket | 12 | vol 8% | 0.7008 | 2026-10-28 |

names 一致 / scale 一致 / config 一致, and 0 lot-recount mismatches.

## Two findings the disclosure paragraph could not carry

1. **The card's amount column is a target, not an executable amount.** Targets are
   weight × capital (sum 700,776); the whole-lot rows can only spend 699,520. The
   card's cash row (299,225) therefore overstates money at work by 1,255 CNY
   (0.13% NAV). The card already carries `actual_amount_cny` per leg but prints the
   target; the ticket books the difference to cash and says so. Root fix belongs in
   `etf_book_production.py`'s sheet renderer — deferred, disclosed here.
2. **Scale comparison must be at the published precision.** Card prints 0.7008,
   ledger keeps 0.700775: a bitwise check reports "different book" every round
   (observed on the first real run). Compared at 4 dp, as printed.

Also: the card's `lots_100` field is a **share count** rounded to 100 (159501: 26,600
shares × 2.194 = 58,360 actual), not a lot count — the 100× trap the recount leg
exists to catch.

## Honest limits

- Exploratory: no prereg, no verdict, nothing enters the scorecard.
- ETF pool is survivorship-filtered; prices are the card's reference prices at the
  pricing bar (no impact cost, no limit-up/limit-down).
- Cash leg is GC001 single tenor rolling at zero fee.
- The 8% label is a historical estimate and only de-levers: the published book
  delivered 10.2% over the full window.
- The 5-name beta book is still a published alternative arm — it is now labelled a
  different book rather than the executable face of this one.