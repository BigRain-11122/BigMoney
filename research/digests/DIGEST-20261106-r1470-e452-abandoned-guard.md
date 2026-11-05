# DIGEST r1470 bm-b -- E452: a truncated reading is not a missing file

Card: **E452** (follow-up to E447 / r1469). Face:
`results/state_tilt/abandonedguard_latest.json` (`ABANDONEDGUARD-2026-11-06.json`).

## Question

E447 published 23 face-home bases with no write site in the corpus, 7 of which are still read by code
a harness launches. A harness that opens a file nobody writes is safe in exactly two worlds: the open
is guarded (a try/except, an existence test, a default), or the artifact it opens still exists. E452
asks, per site, which world it is in -- and therefore which of E447's reads would raise today.

## Method

Static AST over the reader files E447 named, plus one `os.path.exists` per resolved target. No
execution, no writes outside `results/state_tilt`.

* **population** = E447's `abandoned_but_still_read` bases that have at least one live reader,
  re-walked from the live corpus with E447's own scan (so E452 is not limited by E447's 25-site
  publication cap);
* **liveness** is E447's `reader_class` verbatim (`smoke_leg`, `chain_leg`, `task_referenced`,
  `runnable_script`); face-writing censuses and unlaunched libraries are out of population;
* **guard shapes**: `try_except` (call in a try body), `existence_test_in_the_enclosing_test`
  (if/if-exp/boolean test names an `exists()` of the same expression, polarity matched to the branch
  the call sits in), `conditional_default` (call is the body of an if-exp with an else), and
  `existence_test_earlier_in_the_enclosing_function` (a negative existence test on the same
  expression appears lexically earlier in the same function);
* **presence** = `os.path.exists` on the resolved repo-relative target, today.

## Readings

| class | sites |
|---|---|
| unguarded and the artifact is gone | **0** |
| unguarded but the artifact is present | **4** |
| guarded so a missing artifact is announced | **8** |
| target not statically resolvable | 0 |

Verdict (re-derived by the gate from the site rows):
`every_unguarded_harness_open_still_finds_its_artifact`.

Guard shapes: 4 `try_except`, 4 `existence_test_in_the_enclosing_test`, 2
`existence_test_earlier_in_the_enclosing_function`, 0 conditional defaults (two sites carry two
shapes). Presence: 11 of 12 targets exist; the single missing one is
`results/bond_w3a/conn_fuse.json`, opened inside a positive existence test, so its absence is
announced rather than raised.

## The pitfall this face was built to catch

Three sites read

```python
CENSUS_PRODUCT = os.path.join(ROOT, "results", "t23_census", f"CENSUS-{CUTOFF_PIN}.json")
with open(CENSUS_PRODUCT, encoding="utf-8") as f:
```

The shared resolver (E446's, reused verbatim) stops at the f-string head and returns
`results/t23_census/CENSUS-`, which is not a path. Probing that with `os.path.exists` reports "gone"
for a file that is on disk under its pinned date. Published as-is, this study would have claimed
three broken harness opens in the smoke-suite family.

The fix is provenance, not a better guess: a value that came from an early-stopped composition is not
a path, so the site publishes `resolution` (`shared_resolver` / `completed_fstring` / `unresolved`),
`shared_resolver_path`, and the value actually probed. 3 sites are `completed_fstring` (every part of
the f-string names a module constant), 9 are `shared_resolver`, 0 unresolved. `check` refuses a
`shared_resolver` row whose probed value differs from the shared reading, so a completion can never
be passed off as a shared one.

## Population honesty

E447 counted 7 bases with a live consumer; the live re-walk also finds 7, but
`results/overnight_gap_census` now has no site whose reader is live, so it keeps a row with zero
sites and is named in `summary.bases_where_e447_live_reader_is_not_live_now` rather than dropped.

## Wiring

* producer `scripts/e452_abandoned_guard.py` -- selftest 27/27, `run` rc0, `check problems=[]`,
  `verify problems=[]` (the verify re-walks the corpus and re-probes the disk);
* S6 leg `abandoned_guard` = `verify` (one corpus walk plus E447's face scan, ~60 s);
* smoke leg `e452 abandoned base harness guard (r1470 bm-b)`, proven standalone 1/1 green and 1/1 red
  on a doctored tally with the face restored byte-identically (`scripts/run_e452_smoke_leg.py`).

## What this does NOT say

A guard is not a producer. All 8 guarded sites still open bytes no producer in the corpus writes;
the reading is "a missing artifact would be announced", not "these reads are safe forever". Whether
to add a producer, retire the reader, or let the base stay frozen belongs to the lane host that owns
each base, and that decision is not in this face.