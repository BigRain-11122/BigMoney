# DIGEST 2026-10-31 · r1307 · E282 — are the two disagreeing tails a rounding artefact?

**Question (E282 card, seeded by bm-b r1305).** E279 could only bracket the substitution threshold as
`(0.0, 2.0327]` from 2 agreeing and 2 disagreeing rows, and both disagreeing rows sat at a
**dominant-tail normalised gap of exactly 0.0**. The seed read that as *"the substitute lands on the
flip"* and asked whether every disagreement is a boundary artefact of the rounding rather than a
distance effect. If so, the threshold question collapses into "does the substitute sit exactly on the
flip".

**Rule, declared before any number was read (frozen into the face).**

- **D1** scope is **measured, not presumed**: every published `BAND*` face is classified qualifying /
  excluded-with-reason, and the `_latest` twins are dropped **by name** (one publication, one census).
- **D2** a disagreement is **cell-scoped**: one record per cell whose two tails' re-derived
  reachability differs; `reachable` = flip inside `[min, max]`, re-derived, never copied.
- **D3** **the gap field is clamped**: upstream returns `gap 0.0` for **any** flip inside the range, so
  `normalised_gap == 0` is not a position. The test uses `p = (flip − lo)/(hi − lo)` instead, and D3
  is itself measured on the data rather than asserted.
- **D4** a **boundary tie** = the non-reaching tail's gap inside `TOL`, computed per cell, never
  inferred from a gap of 0.
- **D5** hypothesis **refuted** iff a cell is strictly interior on the reaching tail while the
  non-reaching tail's gap exceeds `TOL`.
- **D6** no false precision: counts plus per-cell arithmetic, `calibrated: false`.

**Measured (55 `BAND*` files → 1 qualifying face, 12 censused rows).**

- **1 of 55** faces carries both tails' ranges plus a flip (`BANDFLIPBUDGET-2026-10-29`); **54 excluded**
  (mirror twins, prose-only faces). The census is therefore 12 rows / 4 groups, not "the whole family".
- **2 disagreement cells**, reproduced cell by cell against E279: `cross|60|9` and `cross|60|13`
  (24/24 tail booleans re-derived, 0 mismatches).
- On both, the flip sits **strictly interior** to the reaching (wide) range at **p = 0.696** and
  **p = 0.519**, while the non-reaching (tight) tail is **48.5 / 49.9 pct** away — four orders of
  magnitude beyond `TOL = 1e-12`.
- **The gap reads 0.0 on 2 of 2 reaching readings** *and would read 0.0 on any interior reading at
  all*: the field is clamped, so the seed's "gap 0 ⇒ on the flip" is a fallback masquerading as a
  measurement (r1288 family).
- **A boundary-only disagreement is impossible here by contract**: `reachable` is defined as
  `gap ≤ TOL`, so a non-reaching tail's gap is strictly greater than `TOL` by construction. The
  hypothesis has **two independent** grounds to fail, not one.

**Verdict.** `the_disagreement_is_a_range_difference_not_a_boundary_tie`.

The two tails' ranges are **disjoint intervals**, not nested ones (tight `[1.000, 1.101]` vs wide
`[1.968, 2.296]` on `cross:60`), so a disagreement means the flip landed in the wide band and not the
tight one — a **range position**, and "a boundary artefact of the rounding" cannot describe it. What
the same face *does* say, and what the next card asks, is that the wide band is not a sweep: two rows
(`cross|60|11` at 1.803, `cross|60|15` at 1.884) sit **inside the inter-range gap** and are unreachable
by **both** tails, so widening spends headroom without resolving them.

Evidence: `scripts/e282_substitution_disagreement_census.py` (selftest 23/23, run/verify green),
`results/state_tilt/BANDDISAGREE-2026-10-29.json` (+`banddisagree_latest.json`), S6 leg
`substitution_disagreement_census` (0.17s, rc=0), smoke leg `product: the two disagreeing tails are a
RANGE difference …`, methodology card **E283**, next card
`E285-INTERRANGE-GAP-CEILING` (seeded, pool ready 3).