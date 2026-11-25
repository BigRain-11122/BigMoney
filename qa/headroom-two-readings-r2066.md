# QA — etf_book_headroom_two_readings (r2066, bm-c)

## What was verified

| check | result | evidence |
|---|---|---|
| `selftest` | **19/19 OK** | `python scripts\etf_book_headroom_two_readings.py selftest` |
| `run` (write) | rc 0 | face + doc written |
| `check` on the just-written face | **CHECK OK**, rc 0 | `python scripts\etf_book_headroom_two_readings.py check` |
| negative control: one-field edit | rc 1, says `CHECK FAILED`, does **not** carry the chain's drift word | `python results\_r2066bmc_headroom_negctl.py` |
| negative control: missing face | rc 3, says `STALE` (so the chain will pay to rebuild) | same |
| negative control: restore | byte-identical, restored face checks green | same |
| negctl total | **7/7 OK** | same |

## The two numbers, as published

| reading | path | k | headroom to add (pp) | CNY |
|---|---|---|---|---|
| printed permitting floor (`permitted_k = min(paths)`) | universe | 0.435003 | 0.50 | 5,000 |
| loosest supporter (`keep_allowed = any(path >= k_now - tol)`) | window | 0.747086 | 31.7083 | 317,083 |

- size in force: `k_now = 0.435003` on 1,000,000 CNY (ticket `TICKET-2026-11-24.json`)
- measured flip point (real `decide()` calls, step 0.05pp): **k = 0.752503**, i.e. **31.75pp**
  above the size in force
- ratio loose/strict: **63.4x**

## A defect the negative control caught in this face's own wording

The first draft printed `CHECK FAILED: ... (no STALE prefix: ...)`. That sentence *contains*
the chain's rebuild word, so a chain leg reading this output would have paid for a rebuild on
every genuine disagreement (r1850). The negctl leg `and it does not claim STALE` failed, the
wording was rewritten to `(same inputs, different numbers -- a disagreement, not drift)`, and
the control went green. Recorded here because the failure was found by the control, not by
review.

## Honest limits

- the r2063 one-line patch (identity leg anchored on `base_bar`) is **not applied on disk**;
  the patched cell was built in memory from the published schedule (base bar 2026-11-20,
  k = 0.458463422). On-disk `etf_book_size_rulers_decision` still answers IDENTITY_BROKEN, so
  `etf_book_rebalance_permission` as published today says UNREADABLE — this face's numbers are
  what the same functions say **after** that patch;
- no repricing, no schedule rebuild, no panel read;
- this face does not decide which reading should govern a size increase;
- a falling k never costs the size its permission under this branch, so the strict number is a
  ceiling on *adding*, not a trigger for selling;
- `check` re-derives from live receipts, so it goes red if the ticket or the rulers table moves
  under it (that is intended: a moved ticket is a different question).
