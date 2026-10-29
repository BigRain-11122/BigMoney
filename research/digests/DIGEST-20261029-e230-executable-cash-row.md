# E230 — the card's amount column is now the executable one, so the two production faces reconcile to the yuan (r1342 bm-c)

**Card:** E230 in `knowledge/METHODOLOGY_ASSETS.md`.
**Code:** `scripts/etf_book_production.py` (sheet keys + card renderer + 5 new selftest
legs, 49 PASS), `scripts/etf_book_order.py` (card consumer + leg38/39, 41 PASS).
**Faces:** `results/etf_book_production/{CARD.md,latest.json}`,
`results/etf_book_order/ORDER-2026-10-29-card.md` + `TICKET-2026-10-29-card.json`.

## The defect this closes

E201 (r1333) built the executable ticket *from* the production card and measured a
standing disagreement of **0.13% NAV (1,255 CNY)** between the two faces on the same bar.
The cause was not an arithmetic bug in either script: the card printed **targets**
(`weight × capital`) and a cash row of `(1 - scale) × capital`, while an order can only
be placed in whole 100-share lots. So the card's amount column described money the desk
could not actually spend, and any reader wiring it into an order came up short every
single round. E201 recorded the root fix as belonging in the renderer, and paid for it
with a disclosure paragraph on the ticket.

## What changed

The sheet now publishes **both** readings and says which one is an order:

| key | meaning |
|---|---|
| `book_target_cny` | `Σ weight × capital` — the sizing intent |
| `book_executable_cny` | `Σ lots_100 × ref_price` — what can be placed |
| `lot_residual_cny` | target − executable — the price of lot granularity |
| `cash_amount_cny` | **unchanged** `(1 - scale) × capital` — the risk scale's own slot, kept because other faces already consume it |
| `cash_executable_cny` | `capital − executable` — the money that actually cannot be invested |

The card prints `target (CNY) | executable (CNY)` side by side, prints the cash row with
both readings, and states in words that the executable column is the order and the
residue is the price of granularity rather than a position. The ticket now reads
`cash_executable_cny` when it exists and falls back to the legacy target row (with the old
disclosure paragraph) when it does not, so the fix cannot silently reinterpret an older
card.

## Live reading (2026-10-29 bar, NAV 1,000,000, scale 0.7008, 12 names)

- target book 700,776 / executable 698,808 / residue **1,968 CNY = 0.197% NAV**;
- cash: risk-scale slot 299,225, executable 301,192;
- card vs ticket cash gap: **301,192 vs 301,192.94 = 0.94 CNY**, i.e. the integer yuan
  printed on the card and nothing else — versus 1,255 CNY before this round;
- the ticket's legacy "card cash row is only a target" paragraph is **absent**, because
  the condition that produced it (gap ≥ 1 CNY) is no longer true.

## Gates added

Five legs in `etf_book_production --selftest`, one per way the fix can rot: legs are lot ×
price rather than weight × capital; the executable book never exceeds its target; the
published executable number equals what the legs actually spend; executable cash is
capital minus that spend; the target cash row still equals the risk scale's slot while the
executable row does not. Two legs in `etf_book_order --selftest` prove both directions on
one fixture — an executable cash row closes the gap to the yuan, and a legacy target row
is still called out (a one-sided assertion would have passed on the old renderer too).

## Naming collision, recorded

Two implementations of this fix existed in the worktree when r1342 opened: the face
committed at HEAD published `book_target_cny / book_executable_cny / lot_residual_cny /
cash_executable_cny` and the committed smoke leg asserted exactly those keys plus the card
sentence "Which column is money"; the uncommitted script edit used a second set
(`target_book_amount_cny / executable_book_amount_cny / lot_residue_cny`) and a different
sentence. The committed contract won — the smoke leg is a gate and the published face is
what other faces already read — so the script was renamed to match rather than the gate
loosened. The r1315 lesson: when two sides of one round disagree on a field name, the
side that a gate already asserts is the contract.