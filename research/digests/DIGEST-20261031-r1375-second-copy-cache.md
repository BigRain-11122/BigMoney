# DIGEST — r1375 (bm-c, 2026-10-31): the same defect, one file over

**Question.** r1374 fixed the per-tier stress replay cache and wrote the rule down as
`stress_inputs_digest`. A rule written down is not a rule applied. Does the same pattern —
"cache the answer, key it on the date" — still live in a second copy, and did anyone ever
run the suite that would have said so?

## What was found

**1. The CEO page kept its own replay, keyed on the bar alone.**
`etf_book_ceo_page.build_stress` replays today's weights over the whole panel and caches the
worst-window answer under `results/etf_book_stress/STRESS-<priced_bar>.json`. Its cache hit was
guarded by capital equality only. Two inputs move while the date stands still:

- a flip repair inside the panel rewrites the worst N-day window on an unchanged bar;
- a re-priced ticket rescales the weights on the very same bar.

Either one leaves the reader quoted last world's drawdown with today's date printed beside it.

**2. The suite that would have caught it had been red for weeks, unharvested.**
`etf_book_ceo_page.py selftest` died before printing a count:

```
File ... etf_book_ceo_page.py, line 1473, in selftest
    _cy = cash_yield(100000.0, panel_dir=_td)
  File ... etf_book_ceo_page.py, line 231, in cash_yield
    "panel": os.path.relpath(os.path.join(panel_dir, "%s.csv" % symbol), ROOT)
ValueError: path is on mount 'C:', start on mount 'K:'
```

The selftest pins its fixtures under `%TEMP%` (C:) while the repo sits on K:; a display string
aborted the run. Same family as `pool_deliverable_audit._under` in r1371 — a second copy of that
lesson too, this time in the opposite direction (there it crashed the audit, here it hid 49 legs).
E1 note: the red leg was found by running the suite, not by reading it.

## What was changed

- `etf_book_ceo_page.panel_fingerprint(close)` — one implementation of the panel content hash
  (shape + `hash_pandas_object` over the values).
- `etf_book_ceo_page.stress_cache_digest(...)` — keys a replay on bar + capital + windows +
  every weight + the panel fingerprint. A pre-digest cache file has no `inputs_sha256` and is a
  **MISS**, not a hit.
- `build_stress` resolves the panel *before* the cache probe (so the probe can hash what it would
  actually use), and publishes `priced_bar` / `inputs_sha256` with the cached body.
- `etf_book_beta_menu.stress_inputs_digest` now **imports** `panel_fingerprint` instead of
  hashing the panel itself — the copy is what the next defect grows from.
- `etf_book_ceo_page._rel()` — repository-relative when both paths share a drive, absolute
  otherwise. All seven `os.path.relpath(..., ROOT)` call sites route through it.

## Evidence

- `etf_book_ceo_page.py selftest` **49/49 PASS** after the `_rel` fix (it previously printed
  nothing at all), **52/52** with the three new legs:
  - L51 same bar + same weights + same panel → same key (a hit is still a hit);
  - L52 re-pricing the ticket on the SAME bar → different key;
  - L53 a repaired print, same shape, same date → different key.
- `etf_book_beta_menu --selftest` **27/27 PASS** after switching to the shared `panel_fingerprint`.
- Chain legs `etf_book_ceo_page` and `etf_book_beta_menu`: **2/2 rc0** — both are honest no-ops on
  this host (writer = bm-a), so the live faces are unchanged by this round; the cache rule takes
  effect on bm-a's next run.

## What this does not fix

The same question has not been asked of every face on this host that caches a live value across
ticks. The sweep was rule-led inside the etf_book family, not exhaustive across the repo.