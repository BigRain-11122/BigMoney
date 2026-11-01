# DIGEST 2026-11-01 r1368 bm-b — E347 where a published number actually decides

E344 answered *who reads* a face: nothing outside the census family names those 13 family-only
names, and five directory censuses read every published face without naming it. That is a
statement about reading. "We publish this number" and "this number decides something" are
different sentences, and only the second one prices the wall time a face costs.

This study follows every dated face under `results/` from its load site to the comparison that
consumes it, at pin `90c1fa8`, over 2,232 sources and 191 dated faces in 32 directories.

## Headline

**191 dated faces. 15 are ever loaded by name (12 of those by a source outside the census
family); 176 are reachable only through a directory sweep. 12 reach a comparison. Zero open an
operational decision.**

The operational answer is the sharp one: asked for the gate whose hand-edited bound would change
what a lane does, the census returns **none**. The only operational comparison reached from a face
directory is a null guard (`if d is None:` in `scripts/monthly_exam_prep.py`), which tests presence,
not the value.

| class | gates | what it is |
|---|---|---|
| `scientific` | 16 | verdict-vocabulary and re-derivation checks inside the studies |
| `report` | 53 | study-internal shaping, filters and prints-on-condition |
| `selftest_fixture` | 25 | asserts inside `cmd_selftest` -- they gate the study, not the firm |
| `operational` | 1 | a null guard; published, and excluded from the decision count |

`null_guard` is its own kind (10 rows). A presence test is not a test of the value, and folding it
into `comparison` is how "12 faces decide something" becomes true of a number nobody compares.

## What the numbers mean

**93.7% of published dated faces are read only as population** -- loaded (by a sweep), never
compared. That is not a defect: the census family is *supposed* to read populations. What it means
is that a dated face is a record, not a control surface, and the firm's live decisions are made on
`results/runnable_pool.json`, `regime_state.json`, `call_latest.json` and the `*_latest` mirrors,
which this card excludes by construction.

The 12 faces that do reach a comparison all reach it inside the study that produced them --
`e258`/`e261`/`e273`/`e298`/`e299`/`e305`/`e328`/`e329`/`e331` compare a face's `verdict` to a
freshly re-derived one, or to a frozen `VERDICT_VOCAB`. That is self-agreement, and it is worth
exactly what a re-derivation gate is worth; it is not a decision about capital, admission or
freezing.

## Rules this study had to learn to be honest

1. **"results" in a path is not a target.** The first build reported 403 comparison sites and named
   `compute_audit.py:457` (`if e.get("status") != "ready"`) as the one operational gate -- but that
   reads `results/runnable_pool.json`, a live state file, inside a `glob(results/*.json)` that
   admits **no dated face at all**. An enumeration is a face reader only once a published dated
   face matches its scope; the scope is (dir + pattern + recursion), folded out of the call's own
   arguments. After the fix: 17 enumeration loads, and 403 -> 95 comparison sites.
2. **A comparison inside a selftest is a fixture.** 25 of 95 gates are asserts inside
   `cmd_selftest`; counting them as firm gates inflates "decides something" by a quarter.
3. **A store is not a read** (E343, re-measured here as a selftest leg) and **a citation is not a
   load** (E341/E344). Both were legs before the census ran, and both would have added rows.
4. **An empty scan domain may never read as clean** (D-20261101-20). `scan_domain` publishes
   sources / faces / load sites / comparison sites and a verdict of `empty_scan_domain`; the smoke
   leg refuses a face whose domain carries a zero in any of those counts.
5. **A negative answer has to be stated, not left as a null.** `the_one_gate: null` alone reads as
   "not measured"; the face carries `no_operational_gate_note` saying what was asked and why the
   answer is none, and the smoke leg refuses a null without the note.
6. **Constant folding has to survive `os.path.join`.** `RESULTS = os.path.join(ROOT, "results")`
   folds to nothing under a literal-only reader, which made every enumeration scope unresolvable
   and reported **zero** sweepers over the face population.

## Bound

The card's population excludes `*_latest` mirrors and live state files, which is exactly where
operational reads are expected to live. Measuring that channel is the follow-up (E349), and until
it exists this verdict says "no dated face decides an operation", not "no operational decision is
gated by a published number".

Evidence: `scripts/e347_published_number_gate_census.py` (selftest 17/17, verify 0 problems) ->
`results/state_tilt/DECIDEGATE-2026-11-01.json` + `decidegate_latest.json`; S6 leg
`published_number_gates`; smoke leg E347 (also runnable standalone via
`scripts/run_e347_smoke_leg.py`).