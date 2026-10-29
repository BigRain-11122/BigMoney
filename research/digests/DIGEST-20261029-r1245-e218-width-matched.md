# DIGEST 2026-10-29 r1245 (bm-b) — E218: the E61 calendar split at matched candidate width

Face: `results/e44_midmonth/SHAREDBOOK-WIDTH-20261028.json`
Mode: `python scripts/e39_panel_census.py sharedbookwidth` (S6 leg `sharedbookwidth`)
Card: E218 A matched-width control is a distribution (`knowledge/METHODOLOGY_ASSETS.md`)

## Question

E61 (r1242) split the mid-month vs month-end gap into timing and selection. Its timing arm chose
from the month-end book (<=10 names) while both full arms chose from ~1,274 names, so the
"selection" part also carried a width change. Re-read the split with the candidate width matched:
each calendar chooses from the SAME seeded draw, sized to the month-end book at that session.

## Arms

| arm | calendar | candidate pool |
|---|---|---|
| `me` | month-end | whole eligible universe (~1,274) |
| `mid` | mid-month (day 15) | whole eligible universe |
| `mid_shared` | mid-month | month-end book's holdings (E61) |
| `me_matched` | month-end | seeded draw, same size as that book |
| `mid_matched` | mid-month | the same seeded draw |

Width is exactly matched (`widths.matched_width_exact = true`, book pool median 10, `pool_binds`
true for the first sessions where the month-end book is still empty). Five draws are burned
(seeds published in `spec.draw_seeds`); every matched term is a mean with its sd beside it.

## Reading — the split does not resolve

- selection **-66.0bp** = width **+189.4bp** (sd 402.4) + pool identity **-255.4bp** (sd 402.4),
  residual 0.0. The published term is the small difference of two terms about six times its size,
  each carrying about 4 percentage points of draw noise.
- calendar full **+18.0bp** vs matched **-92.4bp** (sd 528.9, n=5, SE 236.5, same-side share 0.4).
  18bp sits far inside 2 SE, so the family is **unresolvable at this width**: the face publishes
  **3,454 draws** as the count it would take to resolve 18bp with this control.
- per era: 2021_2023 and 2024_now both unresolvable; 2017_2020 is a degenerate cash slice; pre2017
  is unmeasured. `verdict.label = calendar_unresolvable_at_matched_width`.

So E61's identity is arithmetic, not measurement: at book width 10 a random-draw control cannot
separate the two parts. The honest conclusion is that the *magnitude* of the mid-month timing gain
is not established — the direction carried over from the full-width arms is unchanged.

## Two defects this run caught in itself

1. One seeded draw was the first design. A ten-name book's own spread (402–529bp/yr) dwarfs the
   18bp gap, so a single draw answers with noise; the control is now a distribution and a verdict
   may be `None` (unresolvable) instead of a boolean.
2. The first survival rule was "|matched| >= 0.5 * |full|", which a 20x enlargement satisfies —
   2021_2023 was briefly called a survival on a reading 20x the size of the one being confirmed.
   Resolution now gates before the sign/size/share gates.

Housekeeping: the e39 selftest printed its total before ~50 later legs existed, so the printed
number under-reported while the exit code was honest; the print now sits after the last leg
(selftest 796/796).

## Not re-derived

Costs stay at x0 on every arm (the cost question was answered on this family), no gate, no prereg,
no trial count. The random arm is a control, not a book.