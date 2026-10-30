# r1347 — the buffer does not pay at a size the book can run

Evidence cutoff 2026-10-29. Parent face `results/etf_book_hysteresis_paths.json` (inherited,
verified not trusted), new face `results/etf_book_buffer_price_of_size.json`.

## What this window found

1. **The inherited face could not re-judge itself.** `--check` died on
   `KeyError: 'share_cagr_ok'`: the arm publisher's field whitelist dropped exactly the three
   scalars the frozen rule reads, so the face shipped verdicts whose inputs were gone. And even
   with the fields present it fed *stored* scalars back into the rule — a hand-edited median
   would have been judged as printed. Fixed by publishing the inputs and rebuilding the summary
   from the per-cell rows through the single `B.summarize` (no second copy of the formulas),
   then comparing every published scalar against the rebuild. Selftest 23 -> 28 legs.
2. **A breakeven in bp is not a size.** New face inverts the published sqrt cost law
   (`ImpactCost`: `base + k*sqrt(participation/1%)`) to the capital at which each cell's
   saving covers its loss, and compares that crossing to the capacity ceiling.

## Reading

Cost curve from the published ladder: cost_ref **20.26 bp/side at 10M** (median over the 83
priced decisions), i.e. 11.88 bp at 1M, 16.67 at 5M, 29.23 at 30M, 46.77 at 100M.

| k | parent verdict | median crossing NAV | share crossed @1M | @100M | pays at |
|---|---|---|---|---|---|
| 0.05 | REJECT | 121.72M | 30% | 55% | nowhere on the grid |
| 0.10 | COST_KNOB_ONLY | 0.00M (median cell gains return) | 60% | 70% | nowhere on the grid |
| 0.20 | COST_KNOB_ONLY | 0.00M | 60% | 95% | 30M and above |
| 0.35 | REJECT | 0.00M | 65% | 90% | 5M and above |

The p90 trade is already 1% of ADV at **0.94M** of capital. Every arm that pays at all starts
paying 5x (k=0.35) to 32x (k=0.20) above the size at which the book breaks its own participation
cap. **No buffer setting pays at a size the book can be run at.**

Honest bound: the curve is the N5 book's, and the wide buffer cells split the same money over
more names, so their real participation — and their real bill — is lower. The crossings here are
therefore a *generous* reading: if the buffer does not pay at this cost, it does not pay at the
real one either.

## Two smaller things

* `state-bm-c.json` said round 1343 while HEAD said 1346 at open (dead-window family, r1330).
  The round number is read off the commit chain.
* Pool supply attempt: a row for this face was **REFUSED by the law-1 multicore gate**
  ("single-thread runners are banned from the pool"). A two-file aggregation cannot be pool
  supply by construction, so the 48h supply gap needs a *multicore batch*, not a cheap face.

## Files

* `scripts/etf_book_hysteresis_paths.py` — rebuild_summary + recompute_verdicts, selftest 28
* `scripts/etf_book_buffer_price_of_size.py` — new, selftest 24, `--check` recomputes every
  crossing and every pays-at flag
* `results/etf_book_hysteresis_paths.json` (regenerated on the 2026-10-29 bar, 100 cells),
  `results/etf_book_buffer_price_of_size.json`, `research/ETF_BOOK_BUFFER_PRICE_OF_SIZE.md`
* cards E240 (verdict must be re-derivable from its published inputs) and E241 (a cost
  threshold is not a size), both appended to `knowledge/METHODOLOGY_ASSETS.md`
* S6 legs `etf_book_hysteresis_paths` and `etf_book_buffer_price_of_size`; two smoke legs