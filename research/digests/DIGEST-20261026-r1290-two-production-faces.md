# r1290 — two production faces, one of them a day behind

Context: the ETF book is sold to an operator through two artefacts. `CARD.md` is the
headline face (config, backtest window table, today's target book) and
`ORDER-<bar>.md` / `TICKET-<bar>.json` is the executable one. Both call themselves
"the production book".

## What was found

At 21:2x tonight, on the same host and the same panel:

| face | priced bar | feed verdict | decision bar |
|---|---|---|---|
| `results/etf_book_production/CARD.md` (built 17:43) | 2026-10-23 | `stale_feed`, lag 1 | 2026-10-14 |
| `results/etf_book_order/ORDER-2026-10-26.md` (built 20:48) | 2026-10-26 | `current`, lag 0 | 2026-10-14 |

The card was telling its reader the book was a day behind the market while the ticket
beside it was current — and neither face said anything about the other's bar.

Cause is structural, not a slip: only `etf_book_forward` and `etf_book_order` were wired
into the S6 chain (`Tools/s6_chain_bmc.py`). `etf_book_production` was hand-run only, so
the headline face refreshed whenever a session remembered it. That is exactly the orphan
face class r1257 caught for the wide panel (a leg that never got wired) and r1275 caught
for the width numbers (a difference measured but never put where the decision is made).

## What was measured before claiming harm

Refreshing the card on the 2026-10-26 bar and diffing the two cards:

* names: identical 12 symbols
* weights: identical (max |Δw| = 0.0000)
* risk scale / cash slot: identical (0.7008 / 29.9%)
* realised 60d book vol: identical (11.4%)

So on a **non-grid day** the book does not move — the vol overlay sizes at the decision
bar, not daily — and the disagreement was confined to the feed line and fourth-decimal
backtest drift (full-window CAGR 9.47% -> 9.49%). The damage is therefore not "the card
was wrong about the book", it is "the card was wrong about the day", plus the standing
risk that a card refreshed *before* a grid decision and a ticket refreshed *after* it
describe two different books with nothing on either face saying so.

## What was changed

1. `Tools/s6_chain_bmc.py`: `etf_book_production` is now a chain leg, placed before
   `etf_book_order` (the ticket reads the card back for its agreement block).
   Chain: 45/45 rc0.
2. `scripts/etf_book_order.py`: `card_book()` now carries the card's **priced bar** and
   its feed status, not just its decision bar; the ticket's `card_agreement` block grows
   `card_priced_bar` / `ticket_priced_bar` / `same_priced_bar` / `card_feed_status`; and
   `ORDER-<bar>.md` gained a "两张生产面是不是同一天" section that is always printed and
   escalates to a warning when the two bars differ. selftest 24 -> 26 legs.
3. `smoke_test.py`: the chain-wiring leg now requires `etf_book_production` too, so an
   unwired headline face fails smoke instead of reading as current to everything
   downstream. smoke 72/72.

## Live face after the fix

`ORDER-2026-10-26.md`:

```
## 两张生产面是不是同一天
- 决策 bar：卡片 2026-10-14 ｜ 本单 2026-10-14 ｜ 一致=True
- 定价 bar：卡片 2026-10-26（current）｜ 本单 2026-10-26（current）｜ 一致=True
```

## Limits

* One bar of agreement proves nothing about tomorrow; the leg is what makes it repeat.
* `same_priced_bar` is only as good as the card's `sheet.as_of_bar` — both faces derive
  that from the panel's last bar, so a panel that itself lags is reported by the
  `feed_status` field (E137), not by this comparison.
* The width audit behind the 5-vs-12 name disclosure still carries cutoff 2026-10-23;
  it is a backtest face, not a live one, and was left alone.