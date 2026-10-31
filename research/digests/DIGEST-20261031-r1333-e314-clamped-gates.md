# DIGEST 2026-10-31 r1333 (bm-b) -- E314: a clamp that never engages

**Study** `E314_clamped_gate_census` · face `results/state_tilt/GATECLAMP-2026-10-31.json` ·
verdict `a_clamp_that_never_engages_still_hides_the_tolerance_in_the_quantitys_own_units`

## What was asked

E313 (r1332) published that three of thirty gates are multiplied by a clamped scale
(`tol * max(1.0, x)`) and one divides the quantity by a fixed `100.0` before comparing. Both shapes
were published as one number. The pool card asked the follow-up: **where does the form switch, what
is the tolerance in each regime in both units, and can a consumer of the face reproduce either
regime without reading the producer?**

## What was measured

Partition of the same thirty rows by *tolerance as a function of the gated quantity*:

| regime | rows | meaning |
| --- | --- | --- |
| `piecewise_floor` | 3 | `tol * floor` below the switch, `tol * x` above it |
| `linear_in_the_quantity` | 2 | `tol * x` everywhere, and exact equality at `x = 0` |
| `constant_after_normalisation` | 1 | one number, but only in the unit the divisor created |
| `constant_absolute` | 24 | one number, no dependence on the quantity |

The three clamped rows are all the same gate: `results/state_tilt/bandarrival_latest.json`
`frozen_spec.tolerance = 1e-12`, multiplied by `max(1.0, prev)` at `scripts/e260_band_endpoint_arrival.py:132`
and by `max(1.0, target)` at `:115/:120`. Numbers in both units, published per row:

* switch point `1.0` (the floor, in the scale's own unit);
* below the switch: **absolute `1e-12`, relative `tol * floor / x`** — unbounded as `x -> 0`;
* above the switch: **absolute `tol * x`, relative `1e-12`**;
* the two regimes meet exactly at the switch (`1e-12 * 1.0 = 1e-12` on both sides) — published as a
  continuity identity, so the "two forms" are one band with one kink rather than two bands;
* half-unit crossing **`0.5 / tol = 5e11`**: a `tol * x` gate cannot separate neighbours of a
  quantity below that magnitude.

At the largest number its own face publishes (1,920 draws) the tolerance is **1.92e-9 draws** —
about 5e-10 of one draw. So on this domain the clamp never engages (the whole face sits above the
floor) and the upper regime never reaches half a unit either: the gate is **exact equality in
disguise**. That is a statement about the domain, not about the clamp.

The fixed-normalisation row is `scripts/e288_below_floor_narrowing.py:151`,
`abs(1.0 - pct / 100.0) > TOL`: one gate, two numbers — `1e-12` in the fraction unit it is compared
in, **`1e-10` percentage points** in the unit the variable is named in.

## Reproducibility (the sharp part)

**0 of 30 rows can be reproduced from their own face.** For the clamped rows the face carries
`frozen_spec.tolerance` and nothing else: the string `scale` does not appear in the face JSON at all
(5 rows), and no clamp token (`max(`, `"floor"`, `clamp`) appears on 26 of 30 faces. A reader who
takes `1e-12` as "the tolerance" gets the *relative* number above the floor and the *absolute* number
below it and cannot tell which one applies. `face_publishes` records this per row as three
booleans, so "not published" is a measurement rather than an opinion.

Along the way: one of the thirty rows names its face as `results/state_tilt/REPRO-%s.json` — an
unformatted template with no `%` operand. It is published as `face_state: absent`, not dropped and
not given a guessed maximum (E302's rule).

## Pitfalls (added to the card)

1. **A check that raises is a check no mutation can fail.** The first selftest draft crashed with
   `TypeError: float(None)` on the "switch point removed" mutation instead of failing that leg — a
   guard that returns `False` is the only version that can be tested.
2. **Mutate the block the consumer reads.** My first mutation harness edited `rows` while the smoke
   leg reads `clamped_rows`; every mutation "passed" and the leg looked broken. Both interpretations
   of the face exist and the mutation has to land in the one under test.
3. **A magnitude taken from "the largest number on the face" is a bound, not the gated quantity.**
   One row's face maximum is `20261130.0` — a date. Constant gates were nearly reported as "growing"
   because the arithmetic followed `tol * x` instead of the row's own regime class. Tolerance is now
   computed model-aware, and a constant gate is asserted not to move with an unrelated large number.
4. **Count is a label, not a magnitude** (E207 family, repeated here): `bools are labels` and
   `two absolute numbers need no scale` are both selftest fixtures rather than comments.

## Product

* `scripts/e314_clamped_gate_census.py` — `run` / `verify` (0 problems) / `selftest` (37/37)
* `results/state_tilt/GATECLAMP-2026-10-31.json` + `gateclamp_latest.json` (14/14 identity checks)
* `Tools/s6_chain_bmb.py` leg `clamped_gate_census` (verify, 0.10s, rc=0)
* `smoke_test.py` leg E314 (extracted verbatim, run standalone: PASS; **7/7 mutations caught**,
  bytes restored exactly)
* `knowledge/METHODOLOGY_ASSETS.md` card E315
* pool: E314 done with `result_ref`; one successor seeded

## Next

Seed card: the four non-constant gates now have their regimes printed, but the legs that consume
them still compare with a single epsilon. The next question is whether any leg's epsilon falls
*inside* the gate's flat regime (where the gate is looser than the leg) or outside it (where the
leg is looser), using the published switch points rather than re-reading the producers.