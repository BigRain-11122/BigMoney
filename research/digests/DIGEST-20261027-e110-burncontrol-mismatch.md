# E110 -- the burncontrol MISMATCH was a stale control face, not a bad burn

Tool: `scripts/e110_burncontrol_close.py` (selftest 4/4)
Face: `results/e44_midmonth/BURNCONTROL-CLOSE-20261027.json`
Guard: `scripts/e39_panel_census.py` `run_burncontrol` (status `mismatch_across_cutoffs`)

## The question

`burncontrol` (E88) joins the published churn-robust face against the interval
face and against an earlier-start twin, cell by cell on
`(book, universe|mode, era)`, and demands exact equality. On the E109 sweep it
exited rc=1 with `status=MISMATCH`, 11 of 56 shared cells, **in both arms**.
The ticket read that as "so the mismatch is not the repair factor".

## The answer

It *is* the repair factor, seen from the other side. `burncontrol` recomputes
nothing: it reads three faces off disk. The 2013-start twin on disk was
`CHURNROBUST-20261022-s2013.json`, burned 2026-10-22 -- i.e. **before** the
E108 fix to `panel_screen.split_events` (landed 2026-10-27 08:49). Comparing a
pre-fix face with a post-fix face disagrees no matter which arm the *current*
leg is run in, which is exactly what "both arms" looked like. The two-arm
observation was evidence that the control is arm-invariant, not that the factor
was innocent.

Re-derived the twin at the current cutoff (`CHURNROBUST-20261026-s2013.json`,
25s) and re-ran the control: **56/56 cells agree, 0 mismatched**, status
`identical_on_this_face`.

## The 11 cells, attributed

Same-panel same-start burn with only the factor flipped (legacy vs fixed) moves
**4** cells; the other 7 move only because the old twin is four days older.

| what moved | cells | reason |
|---|---|---|
| `mid15 x neutralise \| neutralise_int x 2024_now` (levels and deltas) | 4 | the E108 factor, Δ 369.6bp on every one: `-364.7 -> +4.9` and `-241.0 -> +128.6` |
| `me x {unscreened, neutralise, neutralise_int, drop} x 2024_now` levels | 4 | panel arrival, +13.2..14.7bp |
| `me x {drop, neutralise, neutralise_int} x 2024_now` deltas | 3 | panel arrival, -35.2 -> -33.9 and 5.1 -> 4.9 |

The split is a clean two-way identification, not a tie: **the factor moves only
the screened arms of the mid book** (the `me` columns do not move at all when
the factor is flipped), while **panel arrival moves the unscreened arm**
(which the factor cannot touch). The Δ 369.6bp is identical in levels and in
deltas, as it must be when a single repair relabels one window's price read.

## Mechanism fix

A control that reads faces off disk can never be green against a twin burned at
an older cutoff, so a bare `MISMATCH` was unreadable -- it indicted the burn
when the fault was the control's own input. `run_burncontrol` now reports the
three face cutoffs, names the `stale_twins`, and returns
`status=mismatch_across_cutoffs` with a confound line whenever a mismatched twin
disagrees on cutoff. Verified both ways: current faces -> `identical_on_this_face`
(stale_twins `[]`); an isolated directory holding only the 2026-10-22 twin ->
`mismatch_across_cutoffs`, stale_twins `["churnrobust_s2013"]`, 11 mismatches
reproduced. e39 selftest 320/320, panel_screen 35/35.

## Pit

**"It fails in both arms" is a claim about the instrument, not about the
cause.** When a control reads its inputs from disk, arm-invariance is automatic;
the tell is that the failure is bit-identical across arms. Ask what the control
reads before asking what it measures. Sibling (birth-station): a comparison face
carries an implicit version -- its cutoff and the code that burned it -- and
neither is checked by an exact-equality join, so the check happily compares two
different experiments and calls the difference a defect.