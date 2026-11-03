# DIGEST r1407 (bm-b) -- E390: which reader asks a dropped field of the wrong wave?

Face: `results/state_tilt/WRONGSIDE-2026-11-03.json` (verdict `every_in_repo_reader_of_a_dropped_field_still_lands_on_a_wave_that_holds_it`)
Producer: `scripts/e390_wrong_side_reader.py` (selftest 24/24, verify problems=[])
Parent: `results/state_tilt/SCHEMAACCRETE-2026-11-03.json` (E388, `basename_table[].field_rows`, machine-read)

## What changed

E388 priced the wall -- 18 fields dropped at 16->17, none ever returning -- but never asked who reads
them. E390 does, statically: every .py in the repo, every string literal equal to a dropped field,
classified by its AST parent, its container resolved through name bindings, and its wave read from the
path segment that is exactly `trial_labor_w<N>`.

| class | rows |
|---|---|
| not a read (dict key, mention, output key) | 1683 |
| reads a wave that still holds the field | 148 |
| reads another face entirely | 45 |
| reads a locally built dict | 33 |
| unresolved statically | 80 |
| reads a wave past the field's last sighting | **0** |

The 148 safe reads are all historical runners on waves 10-16 (`prep_state.json` 147 of them): they
open the wave they were written for, which predates the wall. Nothing live reads a dropped field.

## Three defects in the first three drafts

1. **A subscript store is a write.** `face["generated"] = ...` (`scripts/w22_window_forecast.py:193`)
   was the census's single wrong-side finding until `ast.Subscript.ctx` was checked. The literal names
   the slot being filled, not a slot being asked for.
2. **A neighbour directory is not the family.** That same file's only wave literal lives in
   `results/trial_labor_w22_confirm/`, which starts with the family stem and is wave 22 of nothing.
   A wave now requires a path segment matching `^trial_labor_w(\d+)$`.
3. **A key name that matches is not a face read.** `monitor/build_status.py` reads `generated` from
   `portfolio_ew6.json`; the file merely *mentions* the trial-labor family 9 times elsewhere. 45 rows
   were charged to the family face until attribution followed the path the read actually opens.
   Corollaries the resolver needed: `json.load(...) if p.exists() else {}` is a face with an empty
   fallback, not two containers; `ctrl = d.get("per_face_survival")` is still face data.

Each of the three is now a selftest leg with a fixture that fails on the old reading.

## Bound published, not claimed

80 rows resolve to `target_unresolved`: the reader binds its face through a local helper, or indexes a
loop variable over segment dicts, and a static pass cannot follow either. They are published with their
site, line, field and kind, never dropped and never guessed into a verdict. Zero wrong-side is therefore
"none that this census can resolve", not "none exist".

## Wiring

* `scripts/e390_wrong_side_reader.py` -- run / verify problems=[] / selftest 24/24
* smoke leg E390 via `scripts/run_e390_smoke_leg.py` (1/1, exec'd verbatim from `smoke_test.py`)
* pool: E390 done with `result_ref`; E391 seeded (one key name, two meanings across published faces --
  the 45 misattributed reads are exactly that family)
* successor card: `E391-WHICH-KEY-NAME-CARRIES-TWO-MEANINGS-ACROSS-PUBLISHED-FACES`