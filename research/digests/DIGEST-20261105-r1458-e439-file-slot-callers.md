# Digest r1458 -- E439: the file-slot class is empty at the call slot, because the temp marker is already a file path

Face: `results/state_tilt/FILESLOT-2026-11-04.json` (+ `fileslot_latest.json`).
Card: `knowledge/METHODOLOGY_ASSETS.md` E439. Study: `scripts/e439_file_slot_callers.py` (built by
the dead r1458 window, re-derived and closed this window).

## What was done

E438 graded 203 temp-supplying call rows by following the write inside each callee and published
56 that land on a **file-path parameter** -- the class behind the "directory handed to a file slot"
defect. That count was keyed by callee *name* (`dump`/`save`/`write_json`/`_write_csv`/...), and a
name-keyed index counts every `lst.append(x)` as a call to a wrapper named `append`. E439 prices the
same class at the call slot with attribution (the caller must be the defining module or import it)
and grades the argument shape.

## What it measured (cutoff 2026-11-04; 3,454 sources, 310 parameter sites, 27,791 call rows)

| reading | value |
|---|---|
| wrappers confirmed live in the tree | **11 / 11** |
| rows the name index attributes to a wrapper | 24,931 |
| rows kept after reachability attribution | **40** (24,891 dropped) |
| of the 40, rows that hand a **directory** | **0** (share 0.0) |
| argument shapes kept | 22 compose a name onto a base, 12 literal file path, 6 runtime expression |
| E438's 56 rows re-priced | **17 attributed**, 39 dropped by reachability, 0 handing a directory |

Verdict, re-derived by the gate: `no_call_row_hands_a_directory_to_a_file_path_wrapper`.

## The three readings worth keeping

1. **A name index overstates by 99.8%, and the drop is not random.** 24,891 of 24,931 rows go to
   same-name calls on different objects; `write` accounts for 16 of the 56 E438 rows, `save` 8,
   `_write_csv` 4, `dump`/`run`/`write_json` 2 each, `write_face` 3, `append` 2. The correction is
   *reachability*, not re-grading: the surviving rows keep E438's grading.
2. **The defect is empty for a structural reason, not a data accident.** Every surviving call row
   that reaches a file-path wrapper already composes a *name* onto its base (22 of 40; the other
   12 pass a literal file path). So "a directory handed to a file slot" cannot occur at this slot:
   the temp marker is joined into a file name before the call. That is why E438's temp rows and
   E439's call rows are different populations, not a contradiction between them.
3. **The re-pricing is published beside the original number.** 56 -> 17 and 0 directories, on the
   same face as the 24,931-row index, so a reader cannot take the 56 without its attribution bill.

## Bound published

- Attribution is "caller file is the defining module or a module that imports it" -- a conservative
  reading; 33 rows sit under an ambiguous wrapper name and are counted in the kept set only when
  the callee resolves.
- 6 of the 40 kept rows are runtime expressions whose argument text does not resolve to one
  expression; they are kept as `unknown`, never as directories.
- The population is the wrapper set E438 confirmed live (11); a wrapper that disappears from the
  tree refuses the chain rather than leaving a stale tally.

## Wiring

- `scripts/e439_file_slot_callers.py` -- `run` / `verify` (`problems=[]` after re-deriving on the
  live corpus) / `selftest`.
- `Tools/s6_chain_bmb.py` leg `file_slot_callers` (verify).
- `smoke_test.py` leg E439.
- `results/runnable_pool.json`: E439 done with `result_ref`.
## Pit (in-window)

A census whose population is the corpus cannot be verified after the corpus grows. This face re-derives `rows_kept`/`rows_dropped` live, so adding two scratch scripts and a new leg runner after the build moved the attribution and verify refused it twice (`the live attribution drop differs from the published face`). The honest unit is: the face is a statement about a fixed tree, so `run` must be the LAST write after every .py addition, and a face that is verified only before its own round adds code is not verified at all.
