# DIGEST 2026-11-09 r1612 bm-b -- E583: re-issue every published ticket on the bar its file names

Card: `knowledge/METHODOLOGY_ASSETS.md` E583
Face: `results/state_tilt/REPRICEDTICKETS-2026-11-06.json` (+ `repricedtickets_latest.json`)
Tool: `scripts/e583_ticket_repricing.py` (selftest 29/29, build rc0, check problems=[], verify identical)
Wiring: smoke leg `# E583` + `scripts/run_e583_smoke_leg.py` (1/1 green, `--doctor` refused),
`Tools/s6_chain_bmb.py` leg `ticket_repricing` (rc0 0.10s)

## The question

r1611 fixed the producer so a ticket dated B can be priced at B and closed with "the error turns
out to live in the share counts". That answers the next ticket, not the ones already published.
Every ticket file is *named* after a bar; this study asks whether the money printed on it was
priced on that bar.

## The reading

| file | named bar | decision bar | class | issued | same shares on its own bar | same weights, re-lotted |
|---|---|---|---|---|---|---|
| TICKET-2026-10-23.json | 2026-10-23 | 2026-10-14 | priced_on_an_earlier_bar | 606,115.1 | 577,886.9 (**-2.82% NAV**) | -0.019% |
| TICKET-2026-10-26.json | 2026-10-26 | 2026-10-14 | priced_on_an_earlier_bar | 471,225.5 | 449,728.1 (**-2.15%**) | -0.042% |
| TICKET-2026-10-27.json | 2026-10-27 | 2026-10-14 | priced_on_an_earlier_bar | 471,225.5 | 451,539.7 (**-1.97%**) | +0.007% |
| TICKET-2026-10-28.json | 2026-10-28 | 2026-10-14 | priced_on_an_earlier_bar | 471,225.5 | 458,780.2 (**-1.24%**) | -0.026% |
| TICKET-2026-10-28-card.json | 2026-10-28 | -- | no_order_sheet | -- | -- | -- |
| TICKET-2026-11-06.json | 2026-11-06 | 2026-10-14 | priced_on_the_bar_it_names | 470,927.8 | 470,927.8 (0.00%) | 0.00% |

Population: 6 ticket files, 5 order sheets, 25 legs. Legs on the decision bar 20, on the named bar
5, on both (coincidence, uninformative) 0, on neither 0. Sheets that declare a pricing bar at all:
**1** (the one r1611 emitted).

Total money in the "same shares, correct bar" arm across the four stale sheets: **-81,856.7 CNY**.

## The two arms are the finding

Collapsing them yields two opposite wrong answers. Re-lotting the same weights on the right bar
moves the total by a few hundred CNY, so the sheets "look fine"; executing the sheet's own share
counts on the bar it names moves 1.24%-2.82% of NAV, so the sheets "look worthless". Both are
true of different quantities: the weights were never stale, the whole-lot counts were computed on a
nine-day-old close. The gap lives entirely in shares (=3,900 / +18,000 depending on the arm; the
10-23 sheet's 18,000 share overshoot is the number r1611 already flagged).

## The pitfall worth keeping

A price is a weak witness. 159263 printed 1.148 on the 2026-10-23 sheet and that same 4dp price
also appears on 2026-01-27, 2026-08-11 and 2026-11-04 -- "the newest bar whose close equals this
price" would date the leg to a bar five days *after* the ticket. **17 of 25 legs** share their
price with at least one other bar. Adjudication therefore uses only the file's own fields (the
name carries the ticket bar, `book_decided_at` carries the decision bar) and the coincidence count
is published as its own column (same family as E506's "a compact date inside a longer token is not
a witness").

## Honest walls

- The full smoke suite was **not** launched this window (no leg filter, ~20 min, r1499); the new
  leg ran standalone in both arms.
- Read-only over ticket files and the panel: no ticket rewritten, no ledger row booked, no claim
  about the book's returns.
- The panel is the on-disk one (survivorship), and the named-bar closes are its closes.
- Whether a ticket *should* be priced at its own bar is a product decision (r1611 settled it);
  this study only measures which bar the money already on those sheets came from.