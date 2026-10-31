# DIGEST 2026-10-31 r1335 (bm-b) -- E316: what a face would have to print before a reader could evaluate its gate

**Study** `E316_gate_print_requirements` · face `results/state_tilt/GATEPRINT-2026-10-31.json` ·
verdict `the_reader_set_is_on_no_face_and_the_two_faces_fail_for_opposite_reasons_...`

## What was asked

E315 (r1334) showed that the quantity each gate is normalised by is not a key on either face: 0 of 5
rows publish it, so the two-regime arithmetic is only readable by someone holding the producer. That
is a statement about what is missing. The pool card asked the constructive version: **per row, what
is the smallest set of additional keys the face would have to print before a reader with no producer
access could compute the gate's tolerance at one magnitude of the quantity it is rated in -- and is
any of that set already on the face under another name?**

## What was measured

The reader set is derived from E314's regime model, never from a per-face list: identifier + unit +
one magnitude + the scale expression, plus the floor where the gate is piecewise. Five rows, two
faces, 23 required elements, 3 present, 20 absent:

| element | required on | present | absent |
| --- | --- | --- | --- |
| quantity identifier | 5 | 0 | 5 |
| quantity unit | 5 | 3 | 2 |
| one magnitude of the quantity | 5 | 0 | 5 |
| scale expression | 5 | 0 | 5 |
| floor (piecewise only) | 3 | 0 | 3 |

**0 of 5 rows lets a reader compute its own gate.** The minimal added set is 20 keys across the five
rows (four per row, three on the piecewise rows plus the floor).

The two faces fail for **opposite reasons**, and the split is the finding:

* `bandarrival_latest.json` (3 rows, `prev`, toleranced by `tol * max(1.0, prev)`) is a **schema
  gap**. It publishes 57 numbers in the gated quantity's own unit -- `base_draws`, `top_draws`,
  `frozen_spec.grid`, `cross_check.arms[*].base_draws` -- and **none of them is the quantity**. The
  unit is present under another name (`draws`), the quantity is not. Those numbers are *decoys*: a
  reader who substitutes one gets a tolerance that spans **1.5 orders of magnitude** (6e-11 at the
  smallest published count of 60, 1.92e-09 at the largest of 1,920). A decoy is worse than an
  absence because it invites substitution and produces a plausible number.
* `t35_open_fill_verify.json` (2 rows, `session_open`, `rel = |cost - open| / open` against 0.002) is
  a **day on which nothing was compared**. Three outcome counters (`matched`, `dropped`, `breach`)
  are all zero and all six per-trader `detail` lists are empty, so the face has no magnitude to print
  and no number a reader could substitute. Its emptiness is the day, not the schema -- and on that
  face the identifier **is** already a quoted payload key in the producer
  (`scripts/t35_open_fill_verify.py:214`), so the requirement is met for any day that carries a
  comparison.

Neither face prints the scale (`max(1.0, prev)` / `session_open`), the floor (`1.0`), or a magnitude
of the gated quantity.

## Why it is not a restatement of E315

1. E315 said "quantity_not_published_on_the_face 5/5". Two of those five are **not a publication
   gap at all** -- they are an empty day, where absence is what a correct face looks like. Reporting
   them together over-states the defect by 40 percent.
2. A unit word is not a quantity. `base_draws` names the unit of `prev` and is not a magnitude of it;
   counting it would repeat, on the reader side, the writer-side error that a name is a measurement
   (E207/E208 family). The study therefore counts decoys **separately** from magnitudes and prices
   the substitution instead of counting it.
3. The required set is **derived from the regime model** (floor only for `piecewise_floor`, scale
   only where a scale exists), so a future row with a different gate class gets the right list
   without a new table.

## Two pits found while building it

1. **The census cited itself as the producer.** The first pass reported that `session_open` is a
   quoted payload key at `scripts/e316_gate_print_requirements.py:87` -- line 87 is this study's own
   unit vocabulary. The scan now excludes its own source, and prefers a script that *binds* the face
   name (a writer) over one that merely mentions it; the citation is published with its tier so the
   artefact cannot come back silently (E310 family).
2. **A counter named after the absence un-made the empty day.** `counters.zero_pending_traders = 6`
   is a positive number, so the first empty-day rule ("no positive number outside the tolerance")
   classified the t35 face as a schema gap. The rule now reads the outcome counters (`matched`,
   `dropped`, `breach`) and excludes counters whose own name says *zero / no / missing*; a face that
   publishes no outcome counter at all is never declared empty.

## Product

* `scripts/e316_gate_print_requirements.py` -- `run` / `verify` (0 problems) / `selftest` 42/42
* `results/state_tilt/GATEPRINT-2026-10-31.json` + `gateprint_latest.json` (26 identity checks green)
* `Tools/s6_chain_bmb.py` leg `gate_print_requirements` (verify, 0.28 s, rc=0)
* `smoke_test.py` leg (executed standalone against the published face: PASS)
* `knowledge/METHODOLOGY_ASSETS.md` card E317