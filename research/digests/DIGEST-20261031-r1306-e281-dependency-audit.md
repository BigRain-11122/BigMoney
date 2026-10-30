# DIGEST 2026-10-31 · r1306 · E281 — does any published conclusion depend on a stranded tail?

**Question (E281 card, seeded by bm-b r1305).** E279 scoped the E278 substitution policy to
*"substitute only to prove a row CAN move, never to conclude it cannot"*, and its own two events agreed
vacuously. The open question that scoping leaves: does any **already-published** conclusion in the BAND
family actually depend on a stranded tail to say "cannot"? A family with 0 dependent conclusions makes
the policy harmless; any dependent conclusion must be re-read as an upper bound or withdrawn.

**Rule, declared before any number was read (frozen into the face).**

- D1 the **claim unit** is `(face, row, tail)` where a face publishes a reachability boolean for
  **both** tails; extraction is structural (the tail pair), never a bare `reachable` key.
- D2 **polarity** is the published boolean, re-derived from the published multiplier range and required
  to agree. A "cannot" is `reachable == False`.
- D3 **dependent** = a "cannot" whose own tail is stranded per E279 D3 (spread 0 AND degenerate range
  AND >1 cell).
- D4 **load-bearing** = the face text names that tail AND carries a negative marker AND publishes no
  "can" on that same tail.
- D5 **self-disclosure** (inert / dead by construction / untested / "not because … safe") pre-empts the
  dependency: recorded verbatim, no action.
- D6 verdict order: contradicted > undisclosed > vacuous-but-disclosed > no dependency.
- D7 a defect found in a published face is **disclosed and seeded**, never repaired in the round that
  found it.

**Measured (27 dated BAND faces; `_latest` twins excluded by construction).**

- Only **1 face** publishes reachability booleans for both tails (`BANDFLIPBUDGET-2026-10-29`): **24
  claims**, of which **22 are "cannot"** and 2 are "can". The other 26 faces speak in prose — they are
  *disclosure-only* and cannot be dependency-checked at all.
- Exactly **2 "cannot"s rest on a stranded tail** (`cross|all_five|1` and `star_lag1_residual|all_five|12`,
  both `cross:200` tight). Both substitutes are measurable and both **agree vacuously**; **none would
  add** the claim.
- **Load-bearing = 0.** The one face holding those claims already says the tight end is *inert because
  the population never publishes a narrowing multiplier, not because the tight tail is safe*; three
  faces independently publish the same vacuity (`inert`, `dead by construction`, `untested rather than
  safe`).
- Where the two tails genuinely disagree: **2 cells** — `cross|era_2025_now|9` and
  `star_lag1_residual|era_2023_2024|13` — reproduced exactly from E279's census.
- Identities: **24/24** tail booleans re-derived; stranded set agrees; disagreement set agrees.

**Verdict.** `every_dependent_cannot_is_vacuous_and_disclosed`.

No published conclusion has to be withdrawn. But the sharper reading stands: a "cannot" on a stranded
tail is **never a measurement**, and the policy is load-bearing only where the family already said so.

**Defect found in the face it audits (disclosed under D7, repair seeded).** E279's summary field
`rows_where_tails_disagree_on_reachability` publishes `["cross", "star_lag1_residual"]` — **group
labels**, while the disagreement is **cell-scoped**: each group has 4 cells and exactly **1** disagreeing
cell. The field is not wrong about which groups contain a disagreement; it over-claims at group scope,
and the cells are unrecoverable from it. r1305's digest wrote the cells correctly; only the
machine-readable projection is lossy. Seeded as **E284-DISAGREEMENT-FIELD-SCOPE**.

**Two reusable lessons.**

1. Once a policy has been *scoped*, "is it sound?" is the wrong question. Ask **"does anything already
   published depend on it?"** — a dependency audit is a scope test over conclusions, and it costs faces,
   not draws: 27 faces, 24 claims, 0.19 s.
2. The most valuable product of a cell-by-cell identity check is a defect in the face under audit.
   Agreement (24/24) is what makes the audit believable; the one place the projection loses information
   is what makes it worth running. Publish both, and keep the repair in a separate round so the finding
   round is never also the verifying round.

**Pointers.** `scripts/e281_substitution_dependency_audit.py` (selftest 18/18, `run`/`verify` green),
`results/state_tilt/BANDSUBSTITUTEAUDIT-2026-10-29.json` (+ `bandsubstituteaudit_latest.json`), S6 leg
`substitution_dependency_audit` (0.19 s), smoke leg `product: a cannot on a stranded tail needs no
withdrawal here ...` (verbatim harness PASS), methodology card E282, repair card
E284-DISAGREEMENT-FIELD-SCOPE.