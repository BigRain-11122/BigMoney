# DIGEST 2026-11-09 r1617 bm-b — E590: what an unquoted cash step is worth, and whether "8 bars stale" is one fact

**Round**: 1617 (bm-b). **Card**: E590, closed. **Face**: `results/etf_book_order/CASHSILENCE.json`.
**Script**: `scripts/e590_cash_silence.py` (selftest 17/17, check/verify problems=[], standalone
smoke leg PASS and 1/1 red under `--doctor`). **S6 leg**: `cash_silence` (rc0, 0.58s).

## Question

E589 (r1616) made the ticket's `cash_leg` block name the window it averages and disclose that the
repo panel behind it ends before the book's own bar. On the 2026-11-06 ticket: window
2020-01-02..2026-11-06, **1,658 bars**, GC001 stops on **2026-10-27**, the quote printed beside the
window is **8 bars old**, and **7 bar-steps of the window carry no quote at all** (accrued as 0).
Both numbers were disclosed and neither was priced. Two questions follow: what are those steps
worth, and is "8 bars stale" one fact or a moving one?

## Reading

| arm | value |
|---|---|
| published tickets on disk | 5 (+1 `-card` twin, excluded) |
| tickets with an unquoted step | **1** — the 2026-11-06 ticket |
| unquoted bar-steps in its window | **7** (of 1,658 bars, 1,650 quoted) |
| cash on that ticket | **529,072.20 CNY** (nav 1,000,000; cash weight 52.85%) |
| forfeited at the nearest prior quote (1.09%) | **142.20 CNY** |
| forfeited at the window mean (2.079%) | **271.25 CNY** |
| as basis points of the idle cash | **2.69 bp** |
| bars the book has processed since the panel ends | **8** (2026-10-28..2026-11-06) |
| quote age across those bars | **1, 2, 3, 4, 5, 6, 7, 8** bars — monotone, never flat |
| steps that accrue nothing among them | **7 of 8** (the first, 10-27→10-28, still prices at 10-27's 1.09%) |
| tickets whose published `missing_bar_steps` the rebuild reproduces | **5 of 5** |
| tickets whose published `window_bars` the book calendar reproduces | **1 of 1** (1658 == 1658) |

The step rows are 15.80 CNY each on a one-day step and 47.40 on the three-day weekend step
(2026-10-30 → 2026-11-02), which is the whole of the 142.20.

## What "8 bars stale" actually says

The disclosure is exact on the ticket's own bar and wrong as a summary of the window: on
2026-10-28 the quote was **1** bar old, on 2026-11-02 it was **4**, and only on 2026-11-06 is it
**8**. The fallback rate is the same number on all eight bars (1.09% from 2026-10-27), so a reader
told "8 bars stale" cannot tell whether the panel is frozen (rate constant) or indexing badly. The
face publishes both facts separately: `age_is_the_same_on_every_bar = false`,
`the_fallback_rate_is_the_same_on_every_bar = true`.

## Three lessons

- **A silence has to be priced, not counted.** "7 steps" and "142.20 CNY" are different products:
  the first tells a reader nothing about severity, the second ties the number to the cash the
  ticket actually holds.
- **A monotone quantity cannot be published as one scalar.** Collapsing 1..8 into "8 bars old"
  reports the worst bar as if it were the window's fact. Publish the table and let the summary
  carry a re-derivable `flat=false`.
- **The accrual rule looks at the PRIOR bar**, so the step that crosses the panel's last quote is
  still priced and the silence starts at the next one. Counting "bars with no quote of their own"
  would have said 8 steps and booked a step that actually accrued.

## Self-caught

The first selftest fixture asserted a two-day forfeit on a one-day step (the step's gap is
`bar - prev_bar`, not the window's calendar span), and — more usefully — doctoring the *summary's*
flat-age claim was **accepted** by the guard: it only read the table. The guard now cross-checks
the four readings the summary repeats from the table (`book_bars_past_the_panel`,
`quote_age_is_the_same_on_every_bar_past_the_panel`, `quote_age_bars_at_the_newest_book_bar`,
`repo_panel_last_bar`). A duplicated reading is where a table and its headline drift apart.

## Limits

- The calendar is the wide-base daily panel (`data/daily/sh510300.csv`), not a stored index of the
  backtester's panel; the only claim made about it is that it reproduces the ticket's own
  `window_bars` (1658), published per ticket.
- The forfeit assumes the cash sat at GC001 for the whole step. Production rolls the three-rung
  ladder, so this is a reference reading, not the book's own carry.
- Only the 2026-11-06 ticket publishes its window; the four earlier tickets are read against the
  writer's own constant (2020-01-02 .. ticket bar) and each block says
  `reconstructed_from_the_writers_constant`.
- Read-only: no ticket, ledger row, panel or state face was written.

## What it opens

Reading the ledger for the next card shows the two cash faces behave differently on the very same
bars: the ticket's GC001 leg accrues nothing there, while the forward ledger books carry on all
eight (1.10e-05 .. 3.34e-05 per bar) because its ladder panel is not the GC001 panel. Seeded as
**E591**.