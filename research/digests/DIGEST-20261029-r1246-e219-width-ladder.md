# DIGEST 2026-10-29 r1246 bm-b — E219: the width ladder, and the gap that is not the same gap

Card: E219-WIDTH-LADDER-RESOLUTION (entered r1245, closed this round).
Face: `results/e44_midmonth/WIDTHLADDER-20261028.json` (cutoff 2026-10-28).
Runner: `scripts/e39_panel_census.py` mode `sharedbookwidthladder`.
Selftest 796 → 803. Chain leg wired after `sharedbookwidth` and idempotent on the cutoff.

## What E218 left open

E218 re-read E61's mid-month vs month-end gap (+18.0bp full width) with both calendars choosing
from one seeded draw of the same size, and found the control's own spread (402-529bp/yr) so wide
that 18bp would need 3,454 draws. A ten-name draw is the noisiest control the book can produce, so
the question became: is this family measurable at **any** width this book actually runs.

## What the ladder says

Same seeded experiment, four rungs, 5 draws each, cost x0:

| pick_n | control sd | draws needed (local gap) | gap at that width | matched reading | resolvable | verdict |
|---|---|---|---|---|---|---|
| 10 | 528.9bp | 3,454 | +18.0 | −92.4 | no | unresolvable |
| 25 | 237.3bp | 91 | −50.0 | −8.8 | no | unresolvable |
| 50 | 124.8bp | 3 | −161.0 | +7.6 | **yes** | `sign_flips_across_draws` |
| 100 | 97.3bp | 19 | −45.0 | −22.8 | no | unresolvable |

Control noise falls monotonically with width, exactly as it should — so the ladder works. The first
rung whose control can decide anything is 50, and at 50 the matched reading is **+7.6bp against a
−161.0bp gap**: the calendar gap does not reproduce where it finally becomes measurable.

## The finding that matters more than the verdict

The gap is **not width-invariant**. The same specification puts it at +18.0, −50.0, −161.0 and −45.0
as width goes 10 → 25 → 50 → 100: spread 179.0bp against the tightest control standard error of
43.5bp (`gap_is_width_invariant=false`, `gap_sign_stable_across_widths=false`). So the E61 "18bp"
was a width-10 number, and a rung that resolves the ladder decides only **that rung's** number. The
selection decomposition moves with width too: −66.0bp of selection at width 10 becomes +27.0bp at
width 50, still carried by pool identity.

Read together: the calendar question is answerable at width 50 and up, and where it is answerable
the answer is "no" — the 18bp the project has been discussing does not exist at widths the book
could actually run.

## Honest edges

- A wider book is a risk knob, not a better strategy; this face only asks at which width the
  question becomes answerable.
- `draws_needed` assumes independent draws — correlated draws (the same month-end book recurring)
  would need more, so the numbers are floors.
- At width 100 the rung is unresolvable again because the gap shrank to −45.0, not because the
  control got worse; that is the invariance failure showing up as a resolution failure.
- No cost arm re-derived, no gate, no prereg, no trial count: descriptive census.

## Treasure / methodology

Methodology card E219 appended (the rule: prove invariance before calling a rung a resolution).
No new treasure-registry entry — this batch is measurement, and its product is a negative
resolution rather than a candidate.