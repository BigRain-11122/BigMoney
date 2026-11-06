# E464 -- which identity does a producer intend when it writes two names?

**Round** r1487 bm-b | **dept** research+engineering | **card**
E464-WHICH-IDENTITY-A-PRODUCER-INTENDS-WHEN-IT-WRITES-TWO-NAMES | **lane** cpu-only (static AST)
**Face** `results/state_tilt/PRODUCERINTENT-2026-11-06.json` (+ `producerintent_latest.json`)
**Verdict** `some_producers_write_both_voices_while_others_carry_one_from_upstream`

## What E463 left open

E463 established that the only consumer of the four multi-value faces is `smoke_test.py`, and that
no producer of the cards the two voices name mentions those faces. So one producer writes both keys.
Which identity did it mean?

## The measurement

Population = the parent face's four multi-value rows. Producers = that face's own producer list,
re-measured against the live corpus (`e451.walk_py`, this family's instruments excluded). Per
producer: does it **write** this face (path-expression data flow), what **kind** of expression it
writes under each identity key, and whether the value **matches** the payload exactly or only as a
slug prefix.

| face pair | producer | writes it | `card` | `study` | `source_study` |
|---|---|---|---|---|---|
| NAMERESOLVE (+latest twin) | `e421_strong_basis_resolution.py` | yes | E413 (prefix) | E421 (prefix) | carried |
| SELFRES (+latest twin) | `e253_self_row_resolution.py` | yes | - | E253 (exact, `STUDY`) | carried from upstream |
| SELFRES (+latest twin) | `e254_band_exponent_inside_cell.py` | **no** | - | - | - |

`e254` names the face and writes a different one; E462's producer list is a claim, not a
measurement.

## What changed about the parent's frame

* 10 identity-key instances over **3** names (`card`, `study`, `source_study`), and **2 of 4 faces
  carry an identity key E462 never graded** (`source_study = E406_blob_vs_tree_readers` on both
  NAMERESOLVE faces). The "two voices" census saw a three-voice face.
* 4 of 4 faces also carry a **pointer** key (`source_face`), and on NAMERESOLVE the pointer is the
  only **exact** match: every study voice is a slug. A distance-based identity matcher prefers the
  pointer to the card. Pointers are published apart (10 producer instances write one).

## Reading

Two different things were being called "two identities". `e421` declares both voices (the card it
answers, the study that owns the face) in inline slug literals -- one intention, two labels, no
arbitration. `e253` declares exactly one identity (`STUDY = "E253"`) and **forwards** the second
value from the upstream payload; that field is provenance, not a claim. So the fix is not "pick one
of the two values" but "say which key is the identity and which is the upstream".

## Pits

* `face_stem` must slice the basename before stripping `%s`/dates: `results/x/SELFRES-%s.json`
  became `results/x/selfress`, every writer read as a non-writer, and all four faces reported
  "no writer" until the bug was fixed (the selftest leg that caught it was the carry leg).
* Pointer keys in the identity vocabulary inflated the census: 14 instances / 4 faces writing an
  unpublished identity key became 10 / 0 once `source_face`/`face` were split out.
* A keyword value read as a literal: `"study": STUDY` yields `None` unless the AST name is resolved
  against module constants; the first key-site reader returned "name with no value", so a constant
  looked like a carried value.

## Wiring

`scripts/e464_producer_intent.py` (run rc0, verify problems=[], check problems=[], selftest 39/39);
faces `PRODUCERINTENT-2026-11-06.json` + `producerintent_latest.json`; S6 leg `producer_intent`;
smoke leg `e464 which identity a producer intends when it writes two names (r1487 bm-b)` plus
`scripts/run_e464_smoke_leg.py` (red-proved on a doctored face, restored byte-identical); pool E464
done, E465 seeded to keep the floor of 3.

## Bound

Refutation only over the parent's producer list; write detection resolves module assignments and
tuple loops only; intent is read from dict literals and constant-key subscripts.
