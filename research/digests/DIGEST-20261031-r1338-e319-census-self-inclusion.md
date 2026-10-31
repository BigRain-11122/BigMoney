# E319 -- every census in this programme counts other censuses, and no declared guard can say so

Round r1338 (bm-b), evidence cutoff 2026-10-31. Face:
`results/state_tilt/SELFINCLUSION-2026-10-31.json` (+ `selfinclusion_latest.json`).
Runner: `scripts/e319_census_self_inclusion_sweep.py` (run / verify = 0 problems /
selftest 25/25).

## Where this comes from

E318 closed on: *68 of the 69 surviving zero-tolerance gates sit on four earlier study
faces, because E317's exclusion list was written after those faces existed*. That is a
symptom. The mechanism is that a census's guard is `self_faces_excluded` -- a list of
**file names** -- and the property that decides whether a face belongs in the population
is what the face **does**, which no file name can express. E319 measures the whole
population instead of one constant.

## Frozen rules (stated before any number was read)

| rule | definition |
| --- | --- |
| study face | `results/**/*.json` with a top-level `study` matching `^E\d+_` |
| **row** pointer | a `.json` string whose immediate parent key is in `{face, faces, path, source, src, file, face_path, source_face, face_file, face_name}`, or whose parent container key contains `face` |
| prose | every other `.json` mention -- published in `prose_only_targets`, **never counted** |
| canonical face | one per study: the `*_latest` twin is dropped, then the greatest dated basename wins (discovery order is not a version rule) |
| self | dropped in the loader by **study identity** (E310), not by filename |

## Numbers

- **45** study faces; **31** are censuses (69%).
- **256** row edges; **120** of them census -> census.
- **0** of the 120 is covered by any declared exclusion list.
- **10** censuses declare anything: **8** declare only their own two filenames, **1** a
  glob (`BANDFIELDS*.json`), **1** a hand-typed family-prefix window
  (`GATEFORM-`, `GATECLAMP-`, `LEGEPS-`, `GATEPRINT-`).
- **19** censuses that count other censuses declare **nothing at all**.
- E317 is the only family-prefix face and it still counts **7** censuses outside its list.
- **22** censuses are counted as rows by a *later* census.
- Max in-degree **14** (one face's rows appear in 14 censuses); max transitive closure
  **37** (one census transitively ingests 82% of the programme's rows).
- Vintage audit over all 256 arcs: **207 backward, 32 INDETERMINATE, 16 unknown, 1 forward**.

## The four findings

1. **A filename list cannot express "is this a census".** 19 of 31 censuses do not even
   try; the 8 that do guard only themselves; the single family list is a copy of the
   writer's recent window and still misses 7 censuses it counts. The guard has to be a
   derived property of the face, published with the rule that generated it.

2. **Prose is not a row.** Resolving *every* `.json` mention produced a different graph
   from the structured-pointer pass. A mention inside `notes` is a citation. The pointer
   rule is frozen above, prose targets are published separately, and a mutation leg pins
   that folding prose into rows changes the edge count exactly once (25/25 legs).

3. **Discovery order is not a version rule -- and it moved the population.** The first
   implementation preferred "the dated build over `*_latest`" but let `os.walk` order
   break ties between two dated builds: the same disk produced 270 and then 301 edges.
   Canonical selection is now the greatest dated basename, stated in the face.

4. **Filenames are not versions, so a census's population is not recoverable from its
   arc.** A row names a *file*, and that file is rewritten in place. One arc points
   forward in time: `E298_replay_control_census` built at 15:30:39 resolves to the
   current content of `E299_rounded_vs_tolerance_census`, rebuilt at 22:16:03 the same
   day. And granularity matters: comparing `2026-10-31` against `2026-10-31T04:10:24` as
   strings manufactures **34** phantom forward edges out of 306. The audit therefore
   compares at the coarser granularity of each pair and reports same-day date-vs-timestamp
   as INDETERMINATE, never as forward.

## Self-inclusion, caught in this study

The first run counted its own freshly written face (104 face docs / 46 studies) because
`load_docs` filtered nothing and the identity leg checked `startswith("SELFINCLUSION-")`
while the canonical pick had silently selected the lowercase `selfinclusion_latest.json`.
That is exactly the defect being measured. The loader now drops this study by identity and
the face declares `self_faces_excluded` for both of its own files.

## Consumption

- Chain leg `census_self_inclusion` in `Tools/s6_chain_bmb.py` (`verify`, deterministic).
- Smoke leg: *"every census in this programme counts other censuses and no declared guard
  reaches any of those arcs"*.
- Methodology card **E319** in `knowledge/METHODOLOGY_ASSETS.md`.
- Pool: `E319-CENSUS-SELF-INCLUSION-SWEEP` -> `done`; `E320-DECOY-IS-THE-GATED-QUANTITY`
  remains `ready` as the next head.