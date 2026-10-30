# E272 -- is one tail closer to mattering than the other, on one ruler?

**Face** `results/state_tilt/BANDFLIPBUDGET-2026-10-29.json` (+ `bandflipbudget_latest.json`)
**Runner** `scripts/e272_flip_budget_two_tails.py` (run / verify 0 problems / selftest 39/39)
**Source** E259's published arms (p05 **and** p95 per window/leg/base), E262's 12 measured row
records, E269's published per-row flip gaps. No band rebuilt, no shuffle drawn, no panel, no bill.

## The question

E269 measured the tight half's draw budget and found the nearest flip 13.5% outside the widest p05
swing its own group publishes. The wide half's budget was never put on the same ruler: E262's two
wide moves say the wide end is *sometimes* reachable, but nothing published said how far the other
ten rows sit from it. If the wide end is also nearly inert, then "the tight end is inert" was never
a tail finding at all -- it would be a statement about a screen that cannot move anything either way.

## The ruler

One number per row, imported from E269 rather than re-implemented: `m_flip`, the multiplier at which
the row's verdict flips. Both tails are placed on it:

* tight availability = the range of `p05` across windows sharing the row's (leg, base count)
* wide availability = the same range of `p95`
* gap = distance from `m_flip` to that range (0 = some published arm is at/past the flip)
* **normalised gap = gap / that tail's own spread** -- "how many spreads of draw budget before this
  tail could move this row"

Polarity is published, not assumed: a flip above 1 needs a **larger** multiplier (widening = the
wide tail); below 1 needs a smaller one (narrowing = the tight tail).

## Answer

| reading | tight tail (p05) | wide tail (p95) |
|---|---|---|
| rows reachable now (a published multiplier strictly past the flip) | **0** | **2** (rows 9, 13) |
| gap median, % of the flip | 53.95% | 13.69% |
| normalised-gap median (gap / own spread) | **5.14 spreads** | **1.22 spreads** |
| rows where this tail is the closer one | 2 | 10 |
| rows whose tail spread is 0 (unmeasurable) | 2 | 0 |

**The two rows the wide tail reaches are exactly the two rows E262 published as moved** -- row 9
(`era_2025_now` cross:60, `rejection lost`) and row 13 (`era_2023_2024` cross:60, `rejection lost`),
re-derived here from the face, not copied. `verify` asserts the reachable set equals E262's moved
set and fails if they diverge.

## Why the tight end is inert -- and why that is not "safe"

10 of 12 flips need a multiplier **larger** than 1 (the rows sit outside their band) and every
published `p05` in the whole family is **>= 1.0000**. A smaller multiplier can only push such a row
further out. So no published p05 can re-enter any row: the tight tail is inert because the
population never publishes a narrowing multiplier, not because the tight end has been shown to be
harmless. The two rows that *do* need narrowing (`era_2025_now self:60` at 0.889, `early_three
self:60` at 0.630) sit 13.51% and 60.14% below the lowest published p05 -- they are unreachable
too, which is why the tight tail's "closer" wins on those two rows are not wins in practice.

## What this changes

1. **Draw budget goes to the wide tail.** The wide end is genuinely fragile (2 rows sit at a
   published p95, one of them within 3.5% of it, another at 4.4%), the tight end is inert. A future
   resolution budget aimed at the tight tail would buy nothing measurable on this population.
2. **"The tight end transfers cleanly" is retired as a reading.** E269's verdict already said
   *inert, not safe*; E272 supplies the mechanism -- the tight end cannot move these rows by
   construction of the published multipliers.
3. **A zero gap is necessary but not sufficient for a move.** `e257.outside` is strict, so a flip
   sitting exactly on a published end is still INSIDE. The face therefore publishes
   `reachable` and `reachable_strict` separately, and only the strict set is used for the verdict.

## Where this could still be wrong

* The normalised ruler divides by a spread as small as 0.0% (`cross:200` publishes `p05 = 1.0000` on
  all four windows). Those tails are reported **unmeasurable, not infinite** -- 2 of 12 rows, and
  for both the wide tail is the only measurable one, which is disclosed in `closer_note`.
* The gap == moved equality is a fact about *this* population (the moving donor is also the group's
  p95 maximum). It is asserted as soundness (moved => reachable) and the equality is disclosed, not
  relied on.
* 4 of 16 rows remain unjudgeable upstream (no coefficient or no band, `pre2020_four` /
  `era_2020_2022` cells). They are carried in the population count, never scored.