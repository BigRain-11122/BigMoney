# DIGEST 2026-10-31 r1325 (bm-b) -- E302: what a universe switch costs, and whether it changes anything

Study: `scripts/e302_universe_switch_backfill.py` (run / verify / selftest 41/41 / measure <script>)
Face: `results/state_tilt/BANDSWITCH-2026-10-30.json` + `bandswitch_latest.json`
Chain leg: `Tools/s6_chain_bmb.py --only universe_switch_backfill` (verify, 2.3s, rc=0)
Smoke leg: `smoke_test.py` E302 (executed standalone: PASS; 6/6 mutations caught on the dated face
and 6/6 on the mirror, bytes restored exactly)

## The question

E294 re-derived every directory-censusing study in the BAND family twice -- once against the vintage
it published, once against the live directory -- and reported three studies as `not_measurable`
because their `build()` takes no argument at all. For those three (E290, E291, E292) the universe
question was **unasked**, not answered. E302 prices the switch and then asks the question.

## How the switch was priced

The universe reaches each study through a module-level directory global (`OUTDIR`, copied study by
study down an import chain: `e290 -> e286 -> e272 -> e262 -> ...`). So a switch can be simulated with
zero source edits -- redirect every module binding of that global at a staged directory and call
`build()` -- and the cost becomes a **measured** number.

- **31 module bindings** must move (the union across the three studies, deduplicated, excluding this
  study's own module and `__main__`; the price is order-independent, which is a selftest leg).
- A durable `outdir=` parameter would instead touch **6 functions** (`_universe`/`write_face` in
  E290 and E292, `census_names`/`write_face` in E291), **10 `load()` calls** that fall back to the
  module default, and **3 module-level assignments** -- both prices are published side by side
  because a cheap simulation is not a fix.

## The answer

All three now have a switch, all three **reproduce their published verdict**, and **none flips**:

| study | published face | staged | live | verdict |
|---|---|---|---|---|
| e290 | BANDSELFAUDIT-2026-10-29 | 118 (115 + 3 named) | 170 | reproduces_and_stable |
| e291 | BANDAMBIENT-2026-10-29 | 120 (117 + 3 named) | 170 | reproduces_and_stable |
| e292 | BANDSCOPEFIX-2026-10-29 | 132 (129 + 3 named) | 170 | reproduces_and_stable |

Face verdict: `no_published_verdict_moves_with_the_universe` -- the same sentence E294 reached for
the nine studies it could vary. The family's 12 directory-censusing studies are now all asked.

## The three rules this round produced

1. **A staging that is not narrower than the live directory is a tautology, not a stable verdict.**
   Every row publishes both counts and a row whose staging is not narrower is `not_measurable`.
   This is E294's documented trap, promoted from a warning in a docstring into a published field the
   smoke leg asserts.
2. **A vintage may only be witnessed by a stamp the face publishes.** The freeze helper falls back to
   the file mtime for a face with no `generated` field, so a re-run can read a different universe
   with nothing published changing -- observed here as e292's staged universe reading 163 and then
   132 across two runs. E302 uses a stamp-only rule (an undated face is kept, never dropped), and a
   leg pins that touching an undated file does not move the frozen universe. One face in the
   directory is undated today (`ERAPOWER-20261029.json`); the two rules agree right now, so the
   difference is a property of the rule and not of today's numbers.
3. **The cost of a switch and its effect are two findings.** 31 bindings to redirect is cheap;
   "none of them flips" is the answer to the question. Publishing them in one number would let either
   hide the other.

## Incident found and fixed in passing

`e_band_family_vintage.selftest()` leg V2 was **date-dependent**: its fixture writes an undated face
and the mtime fallback makes that fixture always later than the frozen fixture cutoff, so the leg
rots once the wall clock passes 2026-10-31T06:31. It failed on this round's first run (E294 inherits
the same legs, so E294's selftest would have gone red too). Fixed by pinning the fixture mtime with
`os.utime` -- the leg now tests the rule, not today's date.

## Discipline

Published faces are re-read only; the staged universe is a temporary directory removed after each
row; the real directory's mtimes are asserted unchanged around every measurement (all rows publish
`published_files_touched: []`). No draw stream, no band rebuild, no engine, no network. No file under
`scripts/` is edited by the measurement, which is what makes the price a reading of the code as
published.