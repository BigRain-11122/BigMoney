# E463 -- which study does a face join when two read names disagree?

**Round** r1486 bm-b · **dept** research+engineering · **card**
E463-WHICH-STUDY-A-FACE-JOINS-WHEN-TWO-READ-NAMES-DISAGREE · **lane** cpu-only (static AST)
**Face** `results/state_tilt/IDENTITYSPLIT-2026-11-06.json` (+ `identitysplit_latest.json`)
**Verdict** `consumers_of_one_face_bind_it_to_two_different_studies`

## What E462 left open

E462 published that 4 faces (2 file pairs) carry more than one identity value, and that 89 of the
526 graded faces declare both `card` and `study`. Where the two values agree the second name is a
synonym. Where they disagree the face is joined to whichever study the consumer's chosen name
points at, and the payload arbitrates nothing:

| face | `card` | `study` |
|---|---|---|
| `NAMERESOLVE-2026-11-04.json` (+ latest twin) | E413 | E421 |
| `SELFRES-2026-10-29.json` (+ latest twin) | — (`source_study` E252) | E253 |

## The measurement

Population is machine-read from E462's own face (the 4 multi-value rows), consumers are re-derived
from the live `.py` corpus (`e451.walk_py` minus this family's instruments), non-producer namers
only, and a consumer binds a face to the value the face declares under the name that consumer reads.

| reading | number |
|---|---|
| both-name faces in the population (`card` + `study`) | 89 |
| of those, whose values agree | 87 |
| faces declaring >= 2 distinct identity values | 4 |
| faces whose two read voices disagree | 2 (+2 latest twins) |
| consumers outside the producer | 4 (one per face: `smoke_test.py`) |
| consumers per name | `card` 2 · `study` 4 · `source_study` 0 |
| consumers that read BOTH names and must choose | 2 |
| faces a consumer binds to two different studies | 2 (the NAMERESOLVE pair) |
| cards whose producer names the face at all | 0 of 4 |

## Reading

1. **The split is real and it is the test suite's.** For `NAMERESOLVE`, `smoke_test.py` reads both
   `card` and `study` on the same face, so the same consumer holds two bindings at once: E413
   through one name, E421 through the other. Nothing in the payload or the consumer orders them --
   the smoke leg passes because both lookups succeed, not because one is correct.
2. **`SELFRES` is not a split under a consumer's eyes.** Its second voice (`source_study`) is read
   by nobody (E462), so every consumer binds E253 only. A never-read voice is a disagreement no
   consumer can reach -- the exact hazard E462 measured, now priced on the consumer side: 0.
3. **Neither side is aware.** The producers of E413 and E421 never carry the face's stem, so the
   face joins two studies neither of which claims it. The join exists only in the payload's field
   names.
4. **87 of 89 both-name faces agree**, so the synonymous shape is a convention and the disagreeing
   4 are a defect in the *writer*, not in the reader: one producer wrote two labels and meant one
   study.

## Pits (both in-window)

* **A fixture stem must be the stem the code computes.** The first selftest written the face as
  `SPLIT-2026-11-06.json` and keyed the fixture corpus on `split20261106`; `norm_stem` strips the
  date tail, so the real key is `split` and four legs failed on a fixture that never met its own
  selector. A fixture that keys the index by hand is testing the key, not the code.
* **A breadth map computed over the whole corpus cannot be handed a subset.** `bind_consumers`
  looks every namer up in `by_rel`; passing `sources[:1]` with the full breadth raised `KeyError`
  instead of returning "no consumers". Both sides must be cut from the same corpus.
* **A gate is only proven by a face that is consistent.** Two fixture summaries were internally
  inconsistent (a split count above zero beside rows that bind one study, a per-name total that did
  not add up), so the "gate accepts a consistent face" leg failed for the *fixture's* arithmetic --
  which is the gate working, on the wrong patient.

## Wiring

* `scripts/e463_identity_split.py` -- `run` / `verify` problems=[] / `check` problems=[] /
  **selftest 21/21**
* faces `results/state_tilt/identitysplit_latest.json` + `IDENTITYSPLIT-2026-11-06.json`
* S6 leg `identity_split` (`Tools/s6_chain_bmb.py`, `check`)
* smoke leg `e463 a face with two read names binds two studies (r1486 bm-b)` +
  `scripts/run_e463_smoke_leg.py` (extracted verbatim, 1/1 PASS)
* pool: E463 closed with `result_ref`; E464 (which identity a producer *intends* when it writes two
  names) seeded, ready back to the floor of 3

## Bounds

Static only: a consumer is a source that names the face stem **and** reads a declared name by
dict-key site, so a consumer that reaches the name through a computed key is invisible and a
consumer that hard-codes a study id is counted in `values_carried`, not `binds_to`. Producer
detection for a card is a filename prefix or a literal equal to the card id, so a producer naming
its card only in prose is missed -- which is why the `card_producers` column is published beside
the zero rather than only the zero.