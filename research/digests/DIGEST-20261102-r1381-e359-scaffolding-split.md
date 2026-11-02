# E359 / r1381 -- how much of the field census is selftest scaffolding

**Card:** `knowledge/METHODOLOGY_ASSETS.md` E359
**Face:** `results/state_tilt/SCAFFOLD-2026-11-02.json` (+ `scaffold_latest.json`)
**Runner:** `scripts/e359_census_scaffolding_split.py` (selftest 23/23, verify `problems=[]`)
**Wiring:** S6 leg `census_scaffolding_split` (after `subject_resolution`); smoke leg E359;
standalone runner `run_e359_smoke_leg.py`

## The question

E353 (r1375) recorded a suspicion in a caveat rather than a measurement: part of E350's
131 *unwritten guards* names files that only a **selftest** writes (`FZ.json`,
`_chunk_.json`, `json`), so the published population mixes production defence with test
scaffolding. This study prices it with E350's own instrument -- the same corpus walker,
the same face-binding resolver, the same branch classifier -- plus one new question at
each read site: *which function owns this line?*

## Two readings, one published (the wider one decides)

| reading | read sites | fields | guard fields | unwritten guards | scaffolding-only faces |
|---|---|---|---|---|---|
| whole corpus | 5,444 | 2,322 | 230 | 138 | -- |
| name-only | 5,256 / 188 | 2,206 / 116 | 221 / 9 | 129 / 9 | 23 |
| name + caller closure | 5,241 / 203 | 2,200 / 128 | 221 / 10 | **129 / 10** | 24 |

Scaffolding is **3.73 %** of read sites and **7.19 %** of the unwritten-guard population.
E350's headline (131) reproduces at **129** on the production population -- 98.5 % of it
survives the split; the corpus grew from 2,343 to 2,367 sources since E350's pin
(5,398 -> 5,444 reads, 2,289 -> 2,322 fields, 131 -> 138 unwritten guards), so the
E350-vs-today difference is corpus drift and is published as its own axis.

**The scaffolding population is real but small; the suspicion does not extend to the headline.**

## What scaffolding actually is (24 faces, named individually)

Not the three names E353 guessed. The scaffolding-only faces are:

* **fixture directories**: `results/trial_labor_w16|w17|w1|w14/*.json` (44 reads),
  `results/autofill_state.json.tmp/*`, `results/t36_stale_takeover_drill.json.tmp/evidence.json`,
  `results/sentiment_axes/_selftest_tmp.json`, `results/_quarantine/*/manifest.json`;
* **short-name copies of REAL status faces**: `update_status.json`, `runnable_pool.bm-a.json`,
  `runnable_pool.bm-b.json`, `results/heat_update_status.json`, `lhb_thermo_summary.json`,
  `census.json`, `o2.json`, `p2_calibration.json`, `n2_w15_prep_state.json`.

The second group is the one that matters for reading a census: a selftest that reads
`runnable_pool.bm-b.json` by short name makes that *name* look like a live dependency of
the corpus. Counting them as production would be a type error -- no production reader
exists.

## The three names E353 guessed are NOT scaffolding

`FZ.json` (9 reads), `_chunk_.json` (21), the bare face `json` (49) stay **production**
under both rules, because their reads sit in ordinarily-named functions
(`_cap_worker`, `cmd_run`, `_load_t54_axis`). Two different reasons were measured:

1. **`f8`/`ck`-style nested fixtures**: a `selftest()` that defines `def f8(): ...` and
   dispatches `ck("F8 ...", f8)` never *calls* `f8` by name, so a caller-closure rule
   cannot promote it. The under-detection is one-directional: it can only understate
   scaffolding. 845 helpers were promoted by the closure.
2. **Binding leak**: E350's resolver is **file-scoped**, so a variable name reused in a
   second function inherits the first function's face. That is why a production backtest
   helper "reads" `FZ.json` at line 119.

The leak is measured, not assumed: **1,277 of 5,444 reads (23.46 %)** report a face whose
name is written as a literal neither inside their own function nor at module level, and
**146 faces** have *every* read leaked (top: bare `json` 49, `o1600_market_fit.json` 22,
`_chunk_.json` 21, `bandfields_latest.json` 18, `bandexp_latest.json` 17).

## Additivity is published, not assumed

Read-**site** counts partition exactly (`production + scaffolding == total`). Distinct-key
counts do **not**: a `(face, field)` pair read in both populations appears in both, so
`fields` sums to 2,328 against a union of 2,322. Every delta row carries
`production / scaffolding / sum / union / additive`, and the smoke leg refuses a row whose
union is smaller than either arm.

## Pits (caught in-window, each pinned)

1. **File-scoped bindings make a fixture name leak into production.** The first build
   reused `fh`/`doc` in two functions of one fixture file and every production read
   inherited the selftest's face -- the exact defect the study is about, reproduced in its
   own fixture. Fixtures now use distinct handle names, and the leak axis exists because
   of it.
2. **A caller name is not a function name.** Building the closure from every callee token
   promoted `open`, `load`, `json` and inflated the "helpers promoted" count to 4,177.
   Restricted to names the file defines: 845.
3. **The pruned-AST route was the wrong instrument.** Pruning scaffolding defs and
   re-unparsing every file stalled the build past five minutes; the tagged write walker
   replaced it, and a selftest leg asserts its pair set equals `e350._write_sites` on the
   same tree -- so the reuse is checked, not claimed.
4. **An equivalence leg with no activity passes.** The first write-site leg compared two
   empty sets (the fixture had no store into a loaded variable) and printed PASS. It now
   asserts a non-empty production arm first (r1261 family).

## How to apply

* When a census counts *readers*, ask which population the reader lives in before quoting
  the count: a fixture-only face and a status face are not the same evidence.
* Anything that resolves bindings per file must publish how much of its population is
  name-leaked, or a fixture path will be read as a production dependency.
* A name-based classifier can only be checked against a second, wider rule; publishing
  both (and letting the wider one decide) is cheaper than arguing about the rule.