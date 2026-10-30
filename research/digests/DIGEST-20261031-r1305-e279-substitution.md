# DIGEST 2026-10-31 · r1305 · E279 — is "read the other tail" a sound substitute?

**Question (E279 card, seeded by r1303).** E278 published a minimum-spread policy: when a group's
tail spread is exactly 0, publish that tail as unmeasurable and "read the other tail". That
substitution had never been tested. Every measured row publishes a reading at both tails, so the
test is: does the substitute ever contradict the instruction a reader needs?

**Rule, declared before any number was read (frozen into the face).**
- D1 `flip_direction` / `flip_multiplier` are **row** fields, not tail fields. No substitution can
  contradict a direction — this is structural, reported as such and not as evidence.
- D2 the conclusion is `reachable`: the flip multiplier inside that tail's published
  `[multiplier_min, multiplier_max]`, both ends inclusive. **Re-derived** from the published ranges;
  never copied from E272's boolean.
- D3 `stranded` = `spread_pct == 0` **and** the tail's multiplier range is degenerate
  (`min == max`) **and** the group has more than one cell. A degenerate range means the tail cannot
  express any movement.
- D4 `sound` = the substitute is measurable **and** it does not deflate the conclusion. Only a
  deflation is a contradiction; an inflation is a scope problem.
- D5 an agreement produced by a degenerate stranded range is **vacuous** and is not counted as
  evidence.
- D6 no calibrated threshold may be claimed off two rows.

**Measured (16 published rows, 12 with a flip multiplier, 4 without; 4 `(leg, base)` groups).**

- Directions are 10 `widening_reenters` / 2 `narrowing_escapes`; the two stranded rows are both
  widening.
- Exactly **2 rows carry a stranded tail** (indices 1 and 12, `cross:200` tight — the group E278
  flagged). **2 substitution events, 0 deflations, 2 inflations, 2 vacuous agreements.**
- Both events agree — and both agree **vacuously**: the stranded tail publishes `min == max == 1.0`,
  so it is mechanically unable to reach anything. Its "unreachable" is not a reading that the
  substitute could have contradicted. The substitute reads those rows as **2.03 and 2.70 spreads**
  away (raw gaps 63.0% and 69.3%).
- Where the two tails genuinely differ, they differ on **2 rows** (indices 9 and 13 —
  `cross|era_2025_now` and `star_lag1_residual|era_2023_2024`), and on both the dominant tail's
  normalised gap is exactly **0.0**: the substitute sits on the flip.
- The swap view names **the same 2 rows in both directions** — reading tight then substituting wide
  adds the claim on 2 of 12 rows; the reverse substitution removes it on the same 2. A reversal,
  not two events. `wide_dominates_tight_violations = []`, so the relation is monotone.
- Identities: our reachability reproduces E272's published boolean on **24/24** tail readings; our
  stranded set equals E278's flagged groups (`["cross:200"]`).

**Verdict.** `the_substitute_agrees_only_where_agreement_is_vacuous`.

Substitution is sound as an **upper bound** — it can only ever add a "this row can move" — and it is
**unproven as a reading**: it never establishes that a row cannot move. The 2 rows that actually
needed the substitution carry no evidence at all. The E278 policy should therefore be scoped to
*"substitute only to prove a row CAN move, never to conclude it cannot."*

**Scope bracket (published as an interval, `calibrated = false`).** The substitute was observed to
agree at normalised gaps 2.03 and 2.70, and the two tails disagree where the dominant tail sits at
0.0. So a threshold `X` must sit in `(0.0, 2.0327]`. That bracket is **not** a calibration: it rests
on n=2 agree and n=2 disagree. It is published so nobody reads "X = 1.0" as validated.

**Two reusable lessons.**

1. **An agreement you cannot avoid is not evidence.** When one side of a comparison is degenerate
   (`min == max`), it cannot disagree, so agreement on those rows measures nothing. A soundness test
   must separate *vacuously agreeing* rows from *informatively agreeing* rows and report both
   counts — otherwise a policy that has never been exercised is read as a policy that has passed.
   Sibling: a test that only ever fires on rows where the answer is forced finds **the same shape**
   as r1261's trivially-passing equivalence leg.
2. **A substituted reading is an upper bound, and one-sidedness is a property you can measure.**
   Swapping tails moved the answer on exactly 2 of 12 rows, and the two swap directions named the
   same rows — monotone, so the substitution can only widen a claim. Publishing "inflations = 2 /
   deflations = 2" without the row-set identity invites the false reading of two independent
   events; publishing the row set makes the monotonicity checkable. Scope is then a bracket, not a
   point.

**Pointers.** `scripts/e279_substitution_soundness.py` (selftest 26/26),
`results/state_tilt/BANDSUBSTITUTE-2026-10-29.json`, S6 leg `substitution_soundness` (0.15s),
smoke leg `product: reading the other tail never contradicts ...`, methodology card E281.