# DIGEST — r1377 (bm-c, 2026-10-31): the first row of the sweep, and the scanner that could not see it (card E292)

**Question.** r1376 published the reading list and closed with one name: `alloc_backtest.run_cell_faces`
— the only row that both serves a live value and already has a digest machinery elsewhere in its
module. Does its checkpoint actually answer "is this the same world", or only "is this the same rule"?

**Answer: only the rule.** `config_sha` hashed `(weights, mode, p2, capital, start, cutoff)`. The panel
it was computed from — `dates`, `prices`, `adv20_map`, `cash_ret` (which includes the repo rate panel)
— never entered the key. So every way a panel moves without the rule moving left the old cell serving:

- a quote-flip repair inside the batch window (the E289 defect, the same one that produced the
  `etf_book_flip_contamination` face);
- a late bar landing inside the window after a run;
- a repaired repo-rate print, which changes the cash leg only.

The deliverable is a number a reader acts on (ALLOC-P1..P6 cell faces feed the paper book), so this
was the half of the family that was not a research gate.

## What changed

**1. `scripts/alloc_backtest.py` — the checkpoint is now rule x data.**
`panel_sha(dates, prices, adv20_map, cash_ret)` hashes exactly the inputs the simulation consumes
(`repr()` of a float round-trips, so a repaired print moves the digest and nothing else does).
`config_sha` takes it as `data_sha`; the cell record publishes `panel_sha`; `load_valid_cell` asks the
data question *first* and returns a MISS with a named reason (`panel digest moved <a> -> <b>`) rather
than a silent resume. A cell written before this change stores no digest at all — **unreadable is
never clean**, so it is a MISS, not a hit. That is a one-time recompute of the seven live cells on the
lane owner (bm-b), and it is the intended cost of having been wrong.

Five legs, 21 -> 26, and they are the confirmation the audit's own limits demand:
`F9-a` the cell records its digest; `F9-b` the same panel resumes; **`F9-c` the rule key alone does not
serve a new panel**; `F9-d` the repaired panel recomputes and the main face actually differs
(0.127721 -> 0.12759); `F9-e` a legacy cell with no digest is a MISS.

**2. `Tools/live_value_cache_audit.py` — the scanner could not see the fix.**
Re-running r1376's audit after the change left the row reading `module_has_digest_key_does_not`, because
it only looked at *literal keys* (`cached.get("bar")`). This face passes the digest as an **argument**
(`cached = load_valid_cell(name, sha, data_sha)`), so a keys-only read says "no digest" about a cache that
can no longer serve a stale panel. A scanner that under-reports regenerates the same work next round, so
it gained a third evidence class: `digest_argument_to_cache_read`, published with the names it saw, and
**not** folded into `digest_in_key` — a name in a call is a clue, not a proof (E207's lesson). The
headline stays the conservative total and now prints the split:

    698 files | 16 cache decisions | 13 serve on a key with no digest
                (1 of them hands a digest to the call that reads the cache ...) | 2 refuse on mismatch

Legs 14 -> 19: `L15` the argument verdict exists; `L16` the names are published; `L17` the row stays in
the conservative total; `L18` a cache read with **no** digest in the call stays a defect; `L19` the live
`alloc_backtest` row now carries `data_sha` (a leg that fails if the fix is reverted).

## What is still open (named, not claimed)

The remaining 12 rows are unread. The next candidate is `etf_book_ceo_page.selftest`, whose cache
decision is a reading of `panel_fingerprint()` outputs rather than a served value — i.e. it may be a
false positive of the scanner rather than a defect, which is exactly the "prove safe" half of the task.

## Verify

- `python -m scripts.alloc_backtest selftest` → 26 legs, ALL PASS (5 new).
- `python Tools/live_value_cache_audit.py selftest` → 19/19 legs PASS; `run` deterministic, face republished.
- Live lanes untouched on this host: `alloc_paper run` is bm-b-owned → honest no-op in 0.7s; the
  checkpoint change takes effect on bm-b's next run.
- smoke: see the round report row (full suite, detached with file redirect).