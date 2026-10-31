# E308 -- a face-level tolerance gate cannot be paired to a leg by face alone

**Round** r1330 bm-b · **Face** `results/state_tilt/GATETOL-2026-10-31.json` · **Cutoff** 2026-10-31
**Verdict** `bands_stand_only_where_the_producer_is_seen_comparing_with_the_gate`

## Why this was asked

Three rounds in a row had been pricing the same neighbourhood from different angles: r1316 repaired
one leg comparing two copies at 1e-9 (E233), r1324 counted how many legs compare finer than a field
is *printed* (E299), r1327 priced the rows E299 could only bound at face level (E305). Pricing the
last of those surfaced the guess this study tests: pricing a row flagged that the open-fill leg
compares two `session_open` values at 1e-9 absolute while the face it reads publishes `rel_tol=0.002`
as its own gate. If the producer is allowed a difference up to G and the leg refuses anything above
L, then with L < G there is a band of differences the producer may legitimately contain and the leg
would call a breach.

## What was measured

326 legs in `smoke_test.py`, 93 comparison sites, 55 distinct face files named by those sites (all
55 resolve on disk). Eleven of them publish a real tolerance **gate**:

| face | gate | value | units |
|---|---|---|---|
| `t35_open_fill_verify.json` | `rel_tol` | 0.002 | relative |
| `repro_latest.json` | `reproduction.tolerance` | 0.005 | unspecified |
| `bandexp_latest.json` | `verdict_inputs.tol` | 0.1 | unspecified |
| band family (`bandarrival`, `bandflipbudget`, `bandfloormirror`, `bandgapceiling`, `bandtight`, `bandtransfer`) | `frozen_spec.tolerance` | 1e-12 | unspecified |

Paired against the legs that read them: 30 (leg, gate) pairs -- 17 where the leg is arithmetically
tighter, 1 exact equality (the widest band possible), 12 looser or equal.

## The reading that changes the answer

A band is only a finding if the gate is a gate **for the quantity the leg compares**. The study
therefore reads the writers: for each face, the scripts that name it are scanned for the gate's key,
and a line carrying a comparison operator is the evidence that the gate is used as one. Evidence
lines are published verbatim on the row.

- 1 pair sits on a gate the producer is **seen comparing with** (`verdict_inputs.tol` in
  `scripts/e254_band_exponent_inside_cell.py`).
- 28 pairs sit on gates that are **declared but never compared** anywhere in the writers that name
  the face -- including all six band `frozen_spec.tolerance` faces, whose 0.0-slack legs compare
  counts and percentages, not the fitted band scalars the tolerance governs.
- 1 pair has no writer found at all.

So **1 of the 18 nominal bands survives**, and that survivor is name-fragile: `verdict_inputs.tol`
holds 0.1, exactly the value the exclusion rule removes under its other name `frozen_spec.gamma_tol`
on the same face. The study publishes those twins on the gate row rather than resolving them
(`gates_with_an_excluded_twin = 1`).

## What it means for the family

1. **A tolerance gate is scoped to a question, not to a face.** `frozen_spec.tolerance = 1e-12` is a
   parameter of the producer's fitting, and the legs reading that face compare counts, verdicts and
   percentages. Pairing by face manufactures 17 bands that no reader would defend.
2. **"The face publishes a tolerance" is not "the producer applies a tolerance."** Of the 11 gated
   faces, one writer compares with the gate. A declaration in a face is a claim about the producer;
   only the producer's own source can say whether the claim is used.
3. **The gate/exclusion partition is not stable under renaming** (E207/E208 on the writer side).
   `gamma_tol` and `tol` hold the same 0.1 on the same face; one is excluded as a measurement, the
   other accepted as a gate.
4. **The honest census of this shape is 1, and it is a question about a fitted parameter, not a
   defect.** Nothing was repaired here and nothing should be: the study publishes the pairing, the
   evidence line and the gap, and refuses to name a broken leg.

## Guards

- Exclusions are published with their reason (35 rows: `required_tolerance_pct`,
  `edge_tolerance_pct`, `tolerance_fraction`, `flat_rel_tol`, `gamma_tol`) so a tolerance-named
  measurement cannot be silently invisible -- the first build dropped them without a trace.
- The study's own source is excluded from the producer scan: its docstring and selftest name face
  files, so it answered "who compares with this gate" with itself until the exclusion went in.
- 11 identity checks (pair partition, face partition, scope partition, standing ⊆ tighter, standing
  rows all carry evidence, excluded keys never appear as gates, values inside the unit interval,
  relative rows carry a threshold, no self face) -- `selftest` 19/19 with 5 mutation legs.