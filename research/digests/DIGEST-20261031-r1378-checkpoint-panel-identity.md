# DIGEST 2026-10-31 r1378 — a stamp is not a panel, and a memo is not a cache

Machine: bm-c. Round: 1378. Card: E296 (E295 was taken by bm-a r1180 on origin while this push was in flight).

## What was asked

r1377 closed one row of the sweep r1376 published: `alloc_backtest.run_cell_faces` keyed its
checkpoint on the rule and not on the panel. Its closing note handed this round the rest of the
list — twelve rows of `results/live_value_cache_audit.json`, starting with
`etf_book_ceo_page.selftest`, "which may be a false positive of the scanner".

## What the reading found

The first row was a false positive, and so were most of the others, and not for a reason the tool
could see. Two shapes accounted for six of the twelve:

* `cache = {}` filled and read inside one call. Nothing crosses the process boundary, so it cannot
  serve a stale value to a later tick — it is the function's own scratch. Five rows
  (`cn_mkneutral mask_cache`, `e39 _caches`, `innovation pos_cache` x2, `fund_avail` memo).
* `stress_cache_digest` — a name that carries a cache word because it FINGERPRINTS a cache. The
  ruler is not the thing measured, and the row was `etf_book_ceo_page.selftest` calling it.

Both are now rules in the scanner (`_memo_names`, `_ruler_names`) and both are counted in the
summary: 45 memo names and 6 rulers dropped, 16 decisions become 12. The remaining twelve were read
one by one and published with a class and the sentence that justifies it; anything unread is
published as `unread` and counted, so the work still owed cannot hide inside a total. Faces that
leave the list are named in `closed_by_reading` — a row that disappears and a row that was fixed
must not look the same.

## The one that was real

`cn_mkneutral_p1` gates its panel on four facts about the file: the asset meta stamp, the last bar
date, the shape, and a universe re-derive against a frozen probe face. A repaired print inside the
window moves none of them — that is the E289 flip class, a price rewritten with the date left
alone. Eleven cell checkpoints (`cells/<cell>_<face>.json|.npy`) plus the null shard pools and the
sobol shard pools resumed on the CELL NAME alone, so the batch could finish on a mix of two worlds
and publish the result as one. (The module's own null/sobol shards were not in the audit row at
all; they were found by following the same `os.path.exists(path)` shape downward.)

Fix: `panel_digest(P)` over the numbers `simulate()`/`null_draw()` consume — joint calendar, close,
amount, the IC close/open pair, the SSE bridge and its MA200, the EW passive leg, the IC bar mask —
carried in the cell JSON as `panel_sha` and in one `_panel.json` sidecar per shard directory.
Legacy checkpoints carry no digest and read as MISS; the cost of having been wrong is one
recompute, not a silent mixture.

Two negative controls make it falsifiable: a repaired print must move the digest, and two spellings
of NaN must not (a payload built by a different route must not move it, or every run would look
like a repair).

## What was NOT changed, with reasons (published, not implied)

* `member_reinforce_p1.cmd_run` — `guarded`: G-ANCHOR re-runs the anchor backtest on the LIVE panel
  and refuses on drift before the cell cache is read (line ~458 vs ~495). A moved panel stops the
  run; the cell key only decides resume-vs-recompute.
* `p1e_turnover_derive.main`, `t73_mktcap_sidecar.main` — the `.npy` "cache" is the INPUT panel they
  derive from, and their stored-vs-derived recon gate raises on disagreement.
* `fund_avail_notice.status` — counts which period files exist to publish coverage; it never reads a
  stored value back as today's answer.
* `etf_book_commodity_split.run`, `regime_p0_slice5.run` — refuse on mismatch already.

## Verify

* `Tools/live_value_cache_audit.py selftest` 19 → 24 legs PASS (memo dropped, memo beside a
  persisted cache still a row, ruler dropped, classes add up, closed-by-reading names the fix).
* `scripts/cn_mkneutral_p1.py selftest` 51/51 PASS (8 new legs: digest determinism, one repaired
  print moves it, NaN spelling does not, cell resumes on the same panel, cell MISS on a moved panel,
  cell MISS when the checkpoint has no digest, shard stamp reuse/miss/no-stamp).
* `results/live_value_cache_audit.json` republished: 699 files, 12 decisions, 9 serve on a key with
  no digest, `read_by_class` {fixed 1, not_a_cache 9, refuses 2}, `rows_still_unread` 0,
  `closed_by_reading` 4.
* full smoke run this round; see the round receipt for the count.

## Next

The list is closed at twelve. What it no longer covers is written on the page as a limit: the
scanner reads syntax, so a checkpoint named `ck` (as in `cn_mkneutral`) was only ever found by
reading. A future pass should ask the same question of `np.save`/`json.dump` pairs that have no
cache word in any name.