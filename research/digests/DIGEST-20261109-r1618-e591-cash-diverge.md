# DIGEST 2026-11-09 r1618 bm-b — E591: the same stale panel, forward-filled on one cash face and zeroed on the other

**Round**: 1618 (bm-b). **Card**: E591, closed. **Face**: `results/etf_book_order/CASHDIVERGE.json`.
**Script**: `scripts/e591_cash_diverge.py` (selftest 29/29, check/verify problems=[], standalone
smoke leg PASS and 1/1 red under `--doctor`). **S6 leg**: `cash_diverge` (rc0, 0.65s).

## Question

E590 (r1617) priced the ticket's silence: 7 bar-steps accrue nothing because the GC001 panel stops
on 2026-10-27. Reading the forward ledger for the same stretch shows the opposite treatment — the
ledger books carry on **all eight** bars past the panel. So: do the two cash faces accrue on the
same bars when the repo panel is short, and by how much do they part on one cash base?

## Reading

| arm | value |
|---|---|
| repo panels on disk | **11** (GC001/003/004/007/014/028/091/182, R-001/003/007) |
| last real quote on **every** panel | **2026-10-27** (the panels stop together) |
| book bars past the panel | **8** (2026-10-28 .. 2026-11-06) |
| bars on which the ledger posts carry | **8 of 8** |
| bars on which the ticket books | **1 of 8** (2026-10-28, whose prior bar still quotes 1.09%) |
| ledger carry on the ticket's cash | **161.13 CNY** |
| ticket's actual accrual | **0.00 CNY** |
| gap | **161.13 CNY = 3.046 bp** of the 529,072.20 CNY cash |
| what the ticket's own rule would have booked | **15.80 CNY** |
| ledger ladder rate per bar (un-weighted from carry/cash) | 1.3467% .. 1.3583%/yr (one bar **−0.4683%**) |
| printed `carry` is cash-weighted | yes — cash share **0.299225**, so a repricing on the ticket's cash is **×3.342** |
| negative-carry bars | **1** (2026-11-05, −6.79 CNY on the ticket's cash) |
| clean-phase replay reproducing the ledger's rate within 0.5% | **4 of 8** |

## What the divergence is made of

Both faces read the *same* panel and the same last quote. The difference is the missing-value
policy: `etf_book_cash_ladder.load_panel(bars=...)` reindexes onto the book's bars and **ffills**, so
every bar past 2026-10-27 earns 2026-10-27's quote; the ticket's `repo_daily_cash` treats an
unquoted prior bar as **zero** and counts it. One face invents no rate, the other invents no
accrual — and neither says which it does.

Two reading traps sit between the two numbers:

* the published `carry` is `cash × ladder_rate`, so applying it to a different cash base understates
  the ledger by the ratio of the cash shares (×3.342 here). The face publishes the factor;
* a rolling ladder is **stateful**. A clean-phase replay of the shipped `ladder3` matches 4 of the
  8 bars and misses 4 (one by +82%, one by −46%, one sign-flipped, one by −0.61%), so the ledger's
  own carry cannot be re-derived from the panel plus the published face — the contract phase is
  unpublished state. That is seeded as E592.

## A face that contradicts itself

`results/etf_book_forward/LEDGER.json` carries the caveat *"Cash earns 0 in the marks, so a
de-levered book under-reports its true carry"* while all 11 of its own bars post a non-zero `carry`.
The reading is published as `summary.ledger_caveat_claims_cash_earns_zero = true` beside
`ledger_bars_posting_carry = 8`, so the contradiction is on the page instead of in someone's memory.

## Guard

`face_problems` re-derives every ladder rate from the published carry/cash pair, every CNY from the
ticket's own cash, every annualised column from that bar's calendar gap, the rule's accrual from the
prior-bar quote, the `ticket_books_this_bar` flag from that quote, the gap from the ledger total
minus what the ticket actually booked, the basis points from the gap, and the replay verdict from
its own relative gap. The smoke leg additionally refuses a measured bar the ledger does not
publish, and a published gap with a ticket said to book nothing.

**Boundaries**: cash base is the publishing ticket's own `cash_amount`; the annualised column is a
reading aid, not a ticket figure; the replay is a phase-changing substitute, not proof of the
ledger's internals; read-only — no ticket, ledger row, panel or state face is written.

**Next**: E592 (ready, cpu-only) — whether the ledger's carry is reproducible once the roll phase is
inferred from its own bars.