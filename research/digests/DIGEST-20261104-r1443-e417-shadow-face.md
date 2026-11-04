# DIGEST 2026-11-04 r1443 bm-b -- E417: the E415 shadow shape does not generalise, but the names are now billed

**Card.** E417-WHICH-READER-WOULD-FIND-A-FOREIGN-COPY-OF-ITS-FACE (pool, cpu-only, ready 2026-11-04)
**Product.** `scripts/e417_shadow_face.py` + `results/state_tilt/SHADOWFACE-2026-11-04.json`
(+ `shadowface_latest.json`), smoke leg `# E417 (r1443 bm-b)`, S6 leg `shadow_face`,
methodology card E425.

## What was asked

E415 priced the two bare-path reads in the durable corpus: one of them would open a *different*
document of the same basename depending on the launch directory. E417 widens the unit from the call
to the name, over the 208 faces E411 priced: for each face, does any directory a reader could be
started from hold a same-named file with different bytes?

Candidate directories: the repo root, every directory in the repo holding a `*latest.json` pointer
(the launcher convention, found by walk and not by a list), the CLI home (`.codely-cli`, `memory`),
and the fleet root plus its siblings. One level only -- a bare read can only land on a file directly
inside the launch directory, so deeper copies are not shadows for this shape.

## What was found

| reading | value |
| --- | --- |
| faces in population | 208 (194 literal, 14 templates excluded) |
| faces on disk | 187 |
| faces with a same-named copy of *different* bytes | 10 |
| ...on a generic basename (`latest.json`, 6 faces share it) | 6 |
| ...on a name only one face carries | 4 |
| exposed names actually read as a bare literal in `smoke_test.py` | 0 |

The 4 specific-name cases are `gateclamp_latest.json`, `gateoperands_latest.json`,
`gateprint_latest.json`, `legeps_latest.json`, each copied once into `results/_e312_verify/`..
`results/_e316_verify/` and each with the **same top-level keys** as the original -- what a verify
fixture is supposed to look like. The `latest.json` cluster is a naming habit: six faces in six
directories, each reporting a different top-level key set, so any reader that resolved the name by
search would get a document of the wrong shape.

**Verdict:** foreign copies exist but every exposed name is read with a directory component
(`foreign_copies_exist_but_every_name_is_read_with_a_directory_component`). The E415 accident is a
property of one call shape in the durable corpus, not of this tree's naming.

## Three rules worth keeping

1. **A string constant is not a read.** The first draft joined bare literals over every
   `ast.Constant` equal to the basename and reported 159 of 194 faces as "read bare", because a
   generic name like `latest.json` appears in suffix tests and globs. Requiring the literal to be
   the path argument of `open`/`load`/`read_*` moved the count to 0 -- the honest number. The
   published face carries the call-argument rule in its `method_limits`.
2. **Split generic from specific by measurement.** A basename shared by several faces in the
   population (counted, never word-listed) produces "copies" that are other faces. Publishing one
   total would have read as "10 shadowed faces"; the actionable population is 4, and 0 of those is
   read bare.
3. **Growing-corpus counts go in the declaration.** Every results directory that gains a
   `*latest.json` pointer adds a candidate, so `faces_with_a_foreign_copy` and the split move on an
   honest rebuild. They are declared through `population_keys` (E424) and the readings are still
   compared byte-equal -- the leg has no room to widen the gate.

## Evidence

- `python scripts/e417_shadow_face.py run` -> verdict above, summary published in the face.
- `python scripts/e417_shadow_face.py verify` -> `{"problems": []}`.
- `python scripts/e417_shadow_face.py selftest` -> 13/13 (classifiers, templated faces, the
  generic/specific split, verdict as a function of rows).
- `python scripts/run_e417_smoke_leg.py` -> leg extracted verbatim from `smoke_test.py`, 1/1.
- `python scripts/run_e417_smoke_leg.py --doctor` -> red on a doctored tally, face restored
  byte-identically.
- `python Tools/s6_chain_bmb.py shadow_face` -> rc 0.

Read-only: no face, census or reader was edited by this study.