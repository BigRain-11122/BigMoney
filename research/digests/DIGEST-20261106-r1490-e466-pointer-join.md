# r1490 bm-b -- E466: a key named `face` is a pointer in 18 of 206 faces, and nobody follows it

**Card** E466 (passed as E465 in the pool: the pointer question card was seeded as
`E465-DOES-A-FACE-POINTER-RESOLVE-AND-IS-IT-THE-JOIN-ANYONE-USES`, but card number E465 was already
taken by the name-collide study written in r1488).

**Face** `results/state_tilt/pointerjoin_latest.json` + `POINTERJOIN-2026-11-06.json`
(367,544 bytes, evidence_cutoff `2026-11-06`).

## What was asked

E464 measured four faces and found every one of them carries a pointer key beside its identity
keys. Tree-wide nobody had asked whether those values name a file at all, whether they resolve, and
whether any source outside the producer turns one into a path.

## What was measured

Three layers, published apart:

| layer | reading |
|---|---|
| form | 252 instances on 252 faces: `face` 206, `source_face` 42, `face_path` 4 |
| `face` as a path | **18 of 206**; 7 stems that name a face on disk, 145 tokens that name no face, 36 free-text labels |
| `source_face` / `face_path` as a path | 42 / 42 and 4 / 4 |
| resolution | 64 path-form pointers, **64 resolve on disk**; 0 in git history only, 0 never existed |
| base required | 27 repo root, **33 only from the pointing face's own directory**, 4 only as an absolute path |
| spelling | 33 bare, 25 forward, 2 backslash, 4 absolute -- **6 of 64 would fail on a POSIX reader** |
| block-valued keys | 24 further faces carry `source_face` as a dict (`sha256`, `population`) |
| readers (key name) | 262 sources / 1,220 sites (`face` 257, `source_face` 5, `face_path` 2) |
| followers | 30 sources turn a `face` value into a path; **0 turn a `source_face` or `face_path` value into a path** |
| weak matches | 1,001 exact-string namers (three shared metronome faces dominate), 38 basename-only |

## Verdict

`only_the_generic_face_key_flows_into_a_path_and_every_candidate_read_site_names_a_row_the_source_built_itself`

## Pits recorded

1. A label that contains a slash is not a path -- the first draft let `<word>/<word>` be a pointer,
   and nine sentences ("EXPLORATION/NEIGHBORHOOD deep-scan ...") were published as pointers to
   files that never existed, driving the verdict.
2. Naming a target is not joining it: exact-string matching gave 1,001 outside readers, dominated
   by `results/compute_audit.json` (1,746 mentions) -- shared faces are named by every census.
3. Reading the key is not following it: `smoke_test.py` reads `source_face` and then asks it for
   `sha256` (a provenance block, not a path).
4. `face` is the sources' own row schema: in the two hand-checked followers the dict is the
   source's own inventory of faces, not an upstream pointer field.

## Wiring

* `scripts/e466_pointer_join.py` -- `run` rc0, `check` problems=[], `verify` problems=[] against the
  live tree, `selftest 46/46`.
* S6 leg `pointer_join` (`Tools/s6_chain_bmb.py`), run alone: rc=0, 0.06s.
* Methodology card E466; pool card closed with this study as `result_ref`, E468 seeded.
* Not run this window: the full smoke suite and the full S6 chain (wall budget) -- stated, not
  claimed.

**Next** E467 (is the card in a producer's docstring ever read) or E468 (the seeded card) within 48h.