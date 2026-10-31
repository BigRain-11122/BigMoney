# DIGEST 2026-10-31 r1334 (bm-b) -- E315: the leg epsilon that meets a two-regime gate

**Study** `E315_leg_epsilon_vs_flat_regime` · face `results/state_tilt/LEGEPS-2026-10-31.json` ·
verdict `four_of_five_quantity_dependent_legs_demand_exact_equality_so_the_gate_is_looser_at_every_magnitude_the_face_publishes`

## What was asked

E314 (r1333) turned each clamped gate into a model: where the form switches, the tolerance in each
regime, the scale it is normalised by. Five of the thirty rows carry a tolerance that depends on the
gated quantity. But a gate only ever governs a *comparison*, and the comparison belongs to a leg
carrying its own epsilon. The pool card asked: **how many leg epsilons fall inside the gate's flat
regime (gate looser than the leg) and how many outside it?**

## What was measured

The five quantity-dependent rows, joined to their legs, with the crossover `eps / tol` computed from
two published numbers:

| face | gate | regime | leg epsilon | flat tolerance | crossover | class |
| --- | --- | --- | --- | --- | --- | --- |
| `bandarrival_latest.json` ×3 | `1e-12` | clamped at `1.0` | **`0.0`** | `1e-12` | `0.0` | exact equality |
| `t35_open_fill_verify.json` | `0.002` | linear on `session_open` | **`0.0`** | `0.0` | `0.0` | exact equality |
| `t35_open_fill_verify.json` | `0.002` | linear on `session_open` | `1e-09` | `0.0` | **`5e-07`** | exact at the zero end |

Four legs publish `0.0`. An epsilon of zero is **exact equality**, not a very small tolerance: no
gate tolerance can ever be as tight, so the leg is the binding test at every magnitude and the
gate's "flat regime" is only the loosest place the gate ever gets — it rescues nothing. At one unit
of the gated quantity the gate's tolerance is `1e-12` (band-arrival) and `0.002` (open fill) against
a leg that rejects any non-zero difference.

The fifth leg publishes `1e-09` against a `0.002` gate: relative, so `tol * session_open`. The
crossover is `1e-09 / 0.002 = 5e-07` **units of session_open** — five ten-millionths of a yuan. A
share price is never that small, so the gate is looser than the leg across every plausible value:
at one unit the gate is `6.3` orders of magnitude looser. The gate is stricter than the leg only at
`session_open = 0`, a single point nobody measures at.

## The measurement that is not one (the sharp part)

My first pass counted **every numeric leaf** on the faces: 1,975 magnitudes, 1,963 of them "gate
looser than the leg", 240 "inside the flat regime". That reading was junk. The leak set includes
`frozen_spec.tolerance = 1e-12` itself, so a tolerance constant was being counted as a magnitude of
the quantity the tolerance gates, and "240 magnitudes sit in the flat regime" was an artefact of the
gate's own number.

The corrected join asks whether the quantity the gate is rated in is attributable at all. It is not:
the quantity identifier is `prev` for the band-arrival rows and `session_open` for the open-fill
rows, and **neither is a key anywhere on its face** — 5 of 5 rows unattributable, 0 attributable
magnitudes. The measurement is published as a status (`quantity_not_published_on_the_face`) with
zero magnitudes, not as a count of unrelated numbers. So the regime the arithmetic describes cannot
be exercised by reading the face, and the only reading left is the crossover, which is below one
unit for every row.

## Pitfalls (added to the card)

1. **A zero epsilon is exact equality, and `log10(tol/0)` is not a big number.** The ratio is
   published as `null` with a separate class, not as `1e12`; manufacturing a finite ratio would be
   the same mistake as printing a tolerance for an exact test.
2. **A leaf set is not a domain.** Counting every number on a face puts the tolerance constant, the
   sample size and the version stamp in the same bucket as a measurement (E207/E208 family, third
   contact). Attribution must key on the identifier the producer itself uses for the quantity.
3. **A mutation leg must be able to fail.** Two mutation legs initially passed against a defect:
   doubling a crossover of `0.0` is still `0.0` (no change to catch), and the one-unit ratio had no
   identity check at all while the face-maximum ratio did. Both were fixed by making the mutation
   land on a row where the number moves and by adding the missing check.
4. **The card's declared deliverable name is a contract.** The card said `REGIMECOMPARE-<cutoff>`;
   the face is published as `LEGEPS-<cutoff>` because it measures an epsilon against a regime and
   does not compare regimes. The rename is disclosed in the pool entry rather than silently
   satisfied by a twin file.

## Product

* `scripts/e315_leg_epsilon_vs_flat_regime.py` — `run` / `verify` (0 problems) / `selftest` (PASS,
  with 12 mutation legs)
* `results/state_tilt/LEGEPS-2026-10-31.json` + `legeps_latest.json` (18/18 identity checks)
* `Tools/s6_chain_bmb.py` leg `leg_epsilon_vs_flat_regime` (verify, 0.05s, rc=0)
* `smoke_test.py` leg E315 (extracted verbatim, run standalone: PASS)
* `knowledge/METHODOLOGY_ASSETS.md` card E316
* pool: E315 done with `result_ref`; `E316-CLAMP-THRESHOLD-FROM-THE-FACE` seeded ready

## Next

The gate cannot be evaluated at any magnitude of the quantity it is rated in, because that quantity
is not on the face. The next question is the smallest set of keys a face would have to print
(identifier, unit, one magnitude, floor) before a reader with no producer access can compute the
tolerance — and whether that set already exists on the producer's face under another name.