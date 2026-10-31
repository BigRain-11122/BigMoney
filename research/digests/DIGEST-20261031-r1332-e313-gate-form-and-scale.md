# E313 — gate form and scale (r1332, bm-b)

**Verdict:** `a_shared_name_does_not_carry_a_shared_unit_so_every_relative_gate_has_to_name_its_scale`

E312 (r1331) left one band standing: the `t35` open-fill pair, where the face publishes
`rel_tol = 0.002` and the producer compares `rel = abs(cost - session_open) / session_open >
REL_TOL`. The leg that reads the same face compares `abs(_px - r["session_open"]) > 1e-09` — the
same *names*, a different *unit*. A relative tolerance cannot entitle an absolute difference
unless a scale is named, so this study prices that question across all 30 rows.

## What was read, and where

The form is read at the **producer's own comparison line** — the one E312 already published per
operand row — never from the face's `gate_units` label, which is `unspecified` on **28 of 30**
rows. The gate is tried under every alias E312's chain resolved (`TOL` → `tol` through a
parameter default), because the producer writes the parameter at the comparison.

## Readings (30 rows)

| comparability class | rows | what it means |
|---|---:|---|
| `same_form` | 14 | both sides absolute on the same quantity — no scale needed |
| `same_form_after_a_fixed_normalisation` | 1 | the producer divides by a constant first (100.0, percent→fraction), so the gate is absolute *in the normalised unit* |
| `scale_required` | 1 | a free scale is needed and it is named (below) |
| `no_multiplicative_scale` | 7 | a count leg cannot be joined to a tolerance by any scale |
| `exactness_is_not_a_tolerance` | 7 | the leg demands `==` on a float; no tolerance entitles it either way |

Gate form observed: relative 5, absolute 4, multi-site 21 (the same gate is compared at several
sites with different shapes — published as the set, never averaged).

## The three readings worth keeping

**1. The surviving band needs a scale, and the scale is a price.** `t35` open-fill —
`gate_absolute_equivalent = 0.002 × |session_open|`, leg `= 1e-09`, breakeven
`session_open = 5e-07`. For any session_open above five ten-millionths the leg's epsilon is the
tighter of the two; below it the gate is. The leg reads `session_open` itself, so the scale is
available to it — the pair is comparable, but only once somebody writes the multiplication down.

**2. A gate multiplied by a clamped scale is two gates.** `bandarrival`'s `frozen_spec.tolerance`
(1e-12, declared `unspecified`) is used as `tol * scale` with `scale = max(1.0, target)` and as
`TOL * max(1.0, prev)`. Above 1.0 it is relative; below 1.0 the clamp makes it a flat 1e-12. The
face publishes one number for both regimes, and the legs paired with it compare **counts** and
**exact float equality** — neither can be joined to either regime by a scale.

**3. A fixed divisor is not a free scale.** `bandfloormirror` compares `abs(1.0 - pct / 100.0) >
TOL`: the producer normalises percent to fraction by a constant 100.0, so the gate is absolute in
the fraction unit and equals `1e-10` in percent units. Reading the `/` as "relative" would have
been the wrong answer — a literal divisor does not vary with the data, so it needs no estimate.

## Method notes (why this is not a count of wrong rows)

- the published quantity is the **scale at which two numbers meet** and the transformation that
  turns one into the other; the census counts classes, and never calls a row wrong;
- a count marker must be a whole token: the first version's `"n_"` substring matched
  `session_open` and turned a price into a count (E208 on the writer side);
- `divider()` returns `(kind, value)` so a numeric divisor (`100.0`) is normalisation, not a scale;
- a scale read off the comparison line outranks a ratio found one hop away, because the line is
  what runs.

## Files

- `scripts/e313_gate_form_and_scale.py` (`run` / `verify` 0 problems / `selftest` 31/31)
- `results/state_tilt/GATEFORM-2026-10-31.json` + `gateform_latest.json`
- `Tools/s6_chain_bmb.py` leg `gate_form_and_scale` (verify)
- `knowledge/METHODOLOGY_ASSETS.md` card E313
- pool: `E313` done with `result_ref`; `E314-CLAMPED-GATE-CENSUS` seeded ready