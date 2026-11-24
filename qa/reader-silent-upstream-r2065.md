# QA evidence — r2065 reader-silent-upstream (bm-c)

Run: `python results/_r2065bmc_reader_silent_upstream.py` (also `--check`, which proves without writing)

Result: **13/13 legs PASS**. Face `results/reader_silent_upstream.json`;
patch `patches/r2065-reader-silent-upstream.patch` (4 hunks / 3 files, `git apply --check` rc0).

## Legs

- PASS patch generation is deterministic (two builds byte-identical)
- PASS the patch is four hunks over three files (one per defect + one per guard)
- PASS `git apply --check` accepts the patch against the current tree
- PASS patched `scripts/etf_book_permission_persistence.py` parses
- PASS patched `scripts/etf_book_cash_roll_today.py` parses
- PASS patched `smoke_test.py` parses
- PASS harness: the UNVERIFIED branch precedes the loop's own `check()` call
- PASS patched `--check` on a silent receipt exits 3 and says `UPSTREAM_SILENT`
- PASS that sentence does not contain `STALE` (the chain must not pay a rebuild for it)
- PASS with a readable receipt the same code reaches the rebuild (guard is not a mute)
- PASS **control**: unpatched `--check` still raises `KeyError 'gap_k'` on the same fixture
- PASS patched `--selftest` passes with `read_inputs` poisoned (it is offline now)
- PASS **control**: unpatched `--selftest` still dies with `KeyError 'cash_cny'` on a silent face

## What this does NOT verify

- The patch is **not applied**. This round ran inside a contention window (another host was
  writing shared faces), so only new files were landed. Nothing here says the two smoke legs
  are green today.
- The full smoke suite was **not** run (11th consecutive round); the red set is still the
  2026-11-24T20:12:28 reading in `logs/smoke_legs.json`.
- The S6 chain was **not** run (contention window).
- The live product faces are untouched: `results/etf_book_permission_persistence.json` and
  `results/etf_book_cash_roll_today.json` still carry their pre-round bytes.

## What the live tree said when this was priced

- the cut receipt answers `verdict = UNREADABLE`, `upstream.permitted_k = null` → no `gap_k`
- the published persistence face still carries `slack_k = 0.0` (a real zero — the last readable
  trim was a zero cut, which is why every drop counts as an event on that face)
- the published cash-roll face still carries `verdict = ROLL_GC007_TODAY` (its own last readable day)
