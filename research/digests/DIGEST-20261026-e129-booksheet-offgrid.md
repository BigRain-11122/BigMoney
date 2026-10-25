# DIGEST 2026-10-26 — the order sheet was re-ranked every round, off the decision grid

**Faces**: `results/etf_book_production/latest.json` (card), `results/etf_book_order/TICKET-2026-10-23.json`
(ticket), `results/etf_book_forward/LEDGER.json` (forward ledger)
**Cutoff**: 2026-10-23 panel bar; book in force decided 2026-10-14
**Trials**: 0. No preregistration, no verdict, no ledger booking.

## What was wrong

Three artefacts all published as "the production book" disagreed on **which names the book
holds**:

| face | book it printed | names |
|---|---|---|
| card (`sheet.legs`) | top-12 of the **2026-10-23** score | 515450, 515300, 511180, 510760, 511380, … |
| ticket (`ticket.order`) | top-5 of the **2026-10-23** score | 515450, 515300, 510760, … |
| ledger (`book_in_force`) | the **2026-10-14** decision | 159501, 513100, 513690, 159577, 159263, … |

Card vs ledger shared **one name of twelve** (159307) while the card's own header said
`HOLD: 13 bars until the next decision point`.

Root cause is one line in each writer: both ranked `masked.index[-1]` / `slip.index[-1]`
— the panel's **last bar** — instead of the last bar of the engine's every-20-bars
decision grid. The grid was already computed, but only to print the label; the *picks*
never read it. That is the E128-family shape again: a computed verdict with no consumer.

Consequence for a human: following the card or the ticket meant buying 11 of 12 (resp.
5 of 5) names the engine did not hold, on a bar labelled HOLD, and paying the round-trip
every round the chain regenerated the sheet. The size of that is not a rounding error —
the ledger's book carried scale 0.7008 (29.9% cash) while the card printed scale 1.0
(0% cash), because the two were sizing two different books on two different bars.

## Fix

Both writers now take the book from the engine itself:

- card: `R.open_to_open_equity(..., diag=[])`; `picks = diag[-1]["book"]`,
  `scale = diag[-1]["scale"]`, `dec_bar = diag[-1]["date"]`. The scores shown per leg are
  the ones that actually picked (decision-bar row), and `book_decided_at` is on the sheet.
- ticket: the last grid point `dates[(len(dates)-1)//REBAL*REBAL]`, same engine grid.

Verification on the live artefacts after the fix:

```
card    decided_at 2026-10-14  scale 0.7008  cash 0.2992  n=12
ledger  bar        2026-10-14  scale 0.700775                      names match: True
ticket  decided_at 2026-10-14  5-name prefix of the card's book: True
```

## The reading rule

A trading artefact may only print a book that the engine would actually hold **at a bar the
engine decides on**. If a face re-ranks "today", it silently rebalances off-grid, and every
downstream number (scale, cash, costs, marks) is about a different portfolio. Rank on the
grid, or do not print an order.

## Gates added

- `scripts/etf_book_production.py` selftest 11 → 14 legs: the sheet must equal
  `diag[-1]["book"]` and `book_decided_at == diag[-1]["date"]`, plus an **activity** leg
  (the off-grid ranking really does differ on the fixture, so the assertion cannot pass on
  the old behaviour) and a cash/scale conservation leg.
- `scripts/etf_book_order.py` selftest 16 → 19 legs: the ticket ranks on the last grid
  decision bar (with the off-grid bar shown to differ), `card_book()` reads the held book
  off the card pointer chain, and the ticket's names must be a prefix of it.
- The ticket now publishes `book_decided_at` and `card_agreement`
  (`same_decision_bar`, `ticket_is_prefix_of_card`) and prints one line per run.

## Honest limits

- The ticket is still a 5-name beta-0.2 overlay account, the card a 12-name vol-target
  book: same decision bar, different width. That difference is priced in
  `results/etf_book_width_audit.json` (+1.52pp/yr, −0.207 Sharpe, −1.84pp maxDD at
  5 names) and disclosed on the ticket; it is not removed by this fix.
- The forward ledger's marks remain nav 1.0 at the seed bar: nothing in this window is a
  track record, and the 2026-10-26 close had not printed when this ran.