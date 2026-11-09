# DIGEST 2026-11-09 r1638 bm-b -- E617: the live sweep's census has no consumer

**Question.** E615 (r1637) graded every glob call the live chain runs and found the one sweeper
that runs every round (`scripts/e396_face_basename_suffix.py`) in the `name_only` class: it
enumerates face names and never opens one. That is harmless only if the names it collects are
never read. E617 asks that one hop out, over the census that module publishes.

**Reading** (`results/state_tilt/SWEEPCONSUMER.json`, cutoff 2026-11-09):

* the two name lists `json_faces()` returns are reduced by `len()`/`set()` inside
  `basename_census()` before anything could store one name -- no individual face name survives;
* of the 10 counts the module publishes, 1 is asserted (`basename_suffix_pairs >= 1` in `verify`),
  2 are only printed by `run`, and **7 are written into the face and read by nothing**;
* **0 modules outside the producer** index any of those keys (the test that re-derives them is
  published separately and is not a consumer);
* `derive_verdict` carries a dead reader line: `census = m["basename_census"]`, never read again.

**Three self-caught defects** (all in this window, all fixed before the face was published):

1. a bare key name is not a reader -- `witness`/`sample` are ordinary words and a substring scan
   credited 1,169 modules; the reader rule tightened to "names the published face *and* indexes
   the key or calls `.get()` on it";
2. the module's own `smoke_test.py` reader fell in the same bucket -- now published as
   `test_readers`, and a value reached only by its own test is still "read by nothing";
3. the first ancestor walk treated the **body** of an `if` as a comparison, so two counts that
   are only printed were graded `asserted` (caught by a leg asserting the print case).

**Limits.** One hop only; a caller is graded by the census keys its body names, not by following
the census into its own callers. External readers are found by pattern, not by resolution.

**Law.** Ask "who reads this" in the form of the read (index / `.get`), never as a mention of the
name; never let the producer's own test count as a reader; and publish each moved key's own line
so the verdict is recomputed by a gate rather than written by hand. Card E618.

Evidence: `scripts/e617_sweep_consumer.py` (selftest 23/23), `results/state_tilt/SWEEPCONSUMER.json`,
`scripts/run_e617_smoke_leg.py` (PASS; `--doctor` 1/1 red, face byte-restored), smoke leg E617,
S6 leg `sweep_consumer`, pool E617 done -> E619 seeded.
