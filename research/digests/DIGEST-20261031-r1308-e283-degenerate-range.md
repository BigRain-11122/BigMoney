# DIGEST 2026-10-31 r1308 bm-b — E283: can the deflation branch ever fire?

**Question.** E279 declared the contradiction branch *sound unless the substitute deflates the
conclusion*, and reported `events_with_deflation = 0` over two substitution events. E281 noted every
stranded tail publishes a **degenerate** multiplier range. This round turns that into the quantity the
zero implies: what shape would a firing row have to have, and what tolerance would it take?

**Face.** `results/state_tilt/BANDDEFLATE-2026-10-29.json` (+ `banddeflate_latest.json`),
runner `scripts/e283_degenerate_range_reachable.py` (selftest 16/16, `run`/`verify` green).

## Scope (measured, mirrors dropped by name)

| item | value |
|---|---|
| dated BAND faces scanned | 29 |
| `*_latest` mirrors dropped | 28 |
| qualifying faces (publish both tails' range + flip) | **1** (`BANDFLIPBUDGET-2026-10-29`) |
| rows censused | 12 |
| tail readings censused | 24 |
| degenerate readings | **2** (both `cross:200` / `tight`, value `1.0`) |
| E279-deflatable readings (stranded + measurable substitute) | **2** |

## Reading

* **The branch is a single point in multiplier space.** A degenerate range `[v, v]` reduces
  reachability (E272's contract, imported not copied) to `flip == v` at the published tolerance.
  The two candidates' flips are **2.7046** and **3.2544** against `v = 1.0`, i.e. `2.70x` / `3.25x`
  away; neither reaches, and this is re-derived, not copied.
* **The tolerance band that would reach them is `[63.03 pct, +inf)`** (`tau_r = gap_pct/100`), with
  `cross|200|1@tight` binding. At the published tolerance (`1e-12 pct`) the branch is `False`.
* **At that band the instrument stops discriminating.** Applying the *same* loosened rule to every
  published reading calls **21 of 24** reachable, against **2 of 24** published (87.5 pct). The test
  that fires the branch is not the test that published the family — so D4's contradiction branch has
  never been run, and cannot be run without replacing the reading scheme.
* **Identity.** 24/24 published tail booleans re-derive from their own ranges (0 mismatches);
  the stranded set and the stranded pairs both equal E279's census.

## Verdict

`the_branch_needs_a_tolerance_that_erases_the_reading` — 0 of 2 candidates reach at the published
tolerance; the nearest needs 63.03 pct; at that tolerance 21 of 24 readings read reachable.

## Reusable lesson (card E286)

A "reachability threshold" is only a threshold while the population still splits: publish the split
*at the threshold you are proposing*, not only the number. A failure mode that needs a tolerance which
declares 87.5 pct of the family reachable is not a test that can fail.

## Pits (this round)

1. My first selftest assertion said the gap for `flip = 2.0` vs `v = 1.0` was `> 50.0`; the published
   formula returns exactly `50.0`. Assertion wrong, code right (r1281 shape) — fixed the leg.
2. Borrowing E282's `scope_census` made this face's **own** publication appear in its own scope on
   the second run (`scope does not re-derive`): the E180/E209 self-inclusion family. Fixed by scanning
   with this face's own excluded-name list and publishing `self_faces_excluded`.
3. PowerShell has no heredocs and treats backtick as an escape — the card append and the
   heading-spacing fix both went through script files (5th sighting in this family).

## Next

Pool head `E285-INTERRANGE-GAP-CEILING` (rows that sit inside the tight..wide gap and are reachable
by neither tail).