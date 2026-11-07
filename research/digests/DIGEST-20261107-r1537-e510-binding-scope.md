# DIGEST 2026-11-07 r1537 bm-b -- E510: scope the binding table, and see which
ambiguity was the resolver's own

**Card**: E510-WHICH-OF-THE-42-AMBIGUOUS-RESIDUALS-BECOME-SINGLE-ORIGIN-WHEN-THE-BINDING-TABLE-IS-SCOPED
**Face**: `results/state_tilt/SCOPEDBINDING-2026-11-07.json` (+ `scopedbinding_latest.json`)
**Script**: `scripts/e510_binding_scope.py` (selftest 20/20, S6 leg `binding_scope` rc0)

## What was asked

E507 published 42 pairs whose date symbol reads as "more than one origin", using a table in
which every assignment anywhere in the module can reach every site in it. The card asks the
obvious follow-up: re-read those pairs with a scoped table and say which of them stop being
ambiguous -- so what remains can be called a real symbol collision.

## Reading

| arm | mixed | data | clock | unknown |
|---|---|---|---|---|
| module-wide (E507) | 13 | 0 | 0 | 0 |
| scoped (this study) | 4 | 7 | 0 | 2 |

- The 42 pairs sit on **13 pair sites** (the other 29 rows are the same site named by several
  members). Counting rows overstates the population by 3.2x.
- **7 pair sites collapse to a single origin** -- all of them data. The manufactured ones were
  selftest fixtures and other functions' locals carrying the same name.
- **1 collapse to caller-supplied**: `asof` inside `card(ticket, mk, sched, asof, ...)`; the
  module-wide table had merged it with two other functions' `asof`.
- **4 stay ambiguous**: `idx` in `etf_book_cash_ladder.main` and `asof` in
  `etf_book_order.run_card` (3 sites). Both writers are reachable from the site's own scope.
- **1 needs the module-wide fallback**: `cutoff` in `stagestyle_combo_p1_backtest.cmd_run`
  binds in scope to `str(idx[hi].date())`, but `idx` binds in another function. Scoping alone
  reads this as unreadable, which is a loss, not a result.
- 13 binding locations on 10 sites are dropped by the scope: that is the mechanical evidence
  for "part of the bucket was the resolver's".

## Three reusable lessons

1. **Breadth is not depth.** Deduplicate pairs by (source, expression, line) before quoting a
   count of "ambiguous places".
2. **Stricter is not more.** A scoped table both collapses real ambiguity and loses a case where
   the operand lives in another scope. Name the two classes separately (`no binding` vs
   `operand out of scope`) and publish which arm decided each site, instead of declaring one
   table the winner.
3. **A resolver cache must be keyed by the table.** `_res`'s key has no table in it; sharing the
   cache between arms answers one table with the other's result (first version did exactly that
   on `_cal`: one binding in scope, four in the answer).

## Pit hit this window

`smoke_test.py` reads no argv (r1499): calling it with `--only E510` ran the whole suite, and the
call was cancelled after five minutes of silence. Single-leg recheck has to be its own script
(`_r1537_leg510.py`, bad=[]).
