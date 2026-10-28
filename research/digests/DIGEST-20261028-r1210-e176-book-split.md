# E176 — which BOOK moved, not which name (r1210 bm-b, 2026-10-28)

Face: `results/e43_tilt_4member/TILT3SIGNBOOKSPLIT-20261027.json`
Leg: `python scripts\e39_panel_census.py tilt3booksplit` (e39 selftest 567 -> 573)
Pool: E176-TILT3SIGN-BOOK-SPLIT (claimed r1210, done this round)
Card: E176 in `knowledge/METHODOLOGY_ASSETS.md`

## Question

E174 named the carriers of the engine column's repair delta, but that column is
`wide book - ladder book`, so every carrier it prints is a mix of "the wide book
changed" and "the fixed ladder leg changed". If the repair re-priced the ladder,
then "the wide book won 2024_now" is the wrong sentence while every number in it
is right. The engine delta is rebuilt as `wide_delta - ladder_delta` here, with
each book's own contrib sink annualised separately.

## Findings

1. **The ladder book does not move at all.** `ladder_book_delta_bp = 0.0` in all
   five rows, to the last digit. Every moved era is `wide_only`:
   2021_2023 +30.20bp wide, 2024_now +49.60bp wide, full +17.12bp wide, ladder
   side zero. So the whole `+46.7bp` headline is the wide book's own re-pricing,
   and E174's ("the wide book lost 2024_now") sentence survives attribution.
2. **The zero is structural, not lucky — and the face derives that.** 67 events
   were neutralised across the panel and **none of them is a ladder member**
   (`ladder_members_neutralised: []`, derived from `screen_report.names` x
   `base.LADDER`, published as `ladder_book_untouched_is_structural: true`). A
   fixed five-name leg built from 510050/510300/510500/512100/588000 simply has
   no integer split events to repair, so a zero there is a property of the
   universe, not of the burn.
3. **The two zero-delta eras are a real control.** pre2017 and 2017_2020 read 0.0
   on the published engine column AND 0.0 on both books
   (`zero_delta_eras_flat_on_both_books: true`). A book that moved there would
   mean the split was reading noise.
4. **The residual is the same compounding residual E174 quoted, not a second
   error.** Engine delta reproduced from the books lands 0.90bp below the
   published 2021_2023 delta, 2.90bp below 2024_now, 0.82bp below full. The
   residual is the daily-compounding term, and it is published per era.
5. **The LEVELS are still not usable, and the offset is worse than the delta.**
   Decomposition level minus published level: -25.4/-26.9bp in the untouched
   eras, +4.8/+5.7 in 2021_2023, **+52.9/+55.8 in 2024_now**, -2.8/-2.0 on full.
   That reproduces E175's 52.9bp finding from a second direction and is why this
   leg asserts the DELTA only. The offset is disclosed and left unexplained —
   E177 owns it.

## Reading rule

A two-book spread's delta has two axes a name-level table cannot separate:
"which name" and "which book". Publish both, because they answer different
sentences — a carrier table can be perfectly audited while the sentence built on
it ("the wide book moved") is false. And when one book reads exactly zero, say
whether that is a measured zero or a structural one: here the ladder leg has no
repaired member at all, which is a different claim from "the ladder was
unaffected after adjustment".

## Wiring

- `run_tilt3booksplit` reuses `_tilt3signname_burn` (one load, both arms) and
  `_era_side_bp` (the same annualisation E174 uses); no second engine pass and no
  second join.
- selftest +6 legs (573/573) pinning: each book annualised on its own, a name held
  by both books listed under the book that moved, `ladder_only` as a published
  verdict word, the tolerance that keeps 0.04bp from being a cause, and the sign
  a flat wide book gives when the ladder side moves (-6.0bp engine).
- Pool hygiene: **E173-TILT3-REPAIR-DRIVERS closed as superseded by E174** — the
  same engine delta (+46.7bp on 2024_now) had already been attributed name-by-
  name on the E171 face, and re-burning it on the E170 face would have produced a
  second table of the same numbers.