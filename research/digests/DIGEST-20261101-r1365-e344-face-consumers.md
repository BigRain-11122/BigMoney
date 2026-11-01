# DIGEST 2026-11-01 r1365 (bm-b) -- E344: who consumes the names only the census family publishes

Card: `knowledge/METHODOLOGY_ASSETS.md` E344.
Face: `results/state_tilt/CONSUMERCENSUS-2026-11-01.json` (+ `consumercensus_latest.json`).
Study: `scripts/e344_face_consumer_census.py` (selftest 32/32, verify 0 problems, ~167s).

## Question

E341 published that at its pin fifteen face stems lose every *writer* when the sixteen-file census
family is excluded; E340 published that twenty-two permission-shaped fields are read back by their
own producer. Both are statements about producers. E344 asks the consumer question: for each of
those names, who reads the face -- inside the family, outside it, or nobody -- and what does an
outside reader take off the number.

## Two channels, because they fail differently

| channel | reading | population |
|---|---|---|
| named | the stem appears inside a string literal; it is a *load* only when that literal (or a name bound to it) reaches `open`/`load`/`loads`/`read_json`/`read_text` | every `.py` in scripts/Tools/live/monitor/firm at the pin (2,232 sources) |
| unnamed | a source enumerates the face directory (glob/listdir/walk/iterdir/scandir) and loads JSON; the pattern is matched against the published filename with module constants folded in | the same corpus, five declared readers with cited evidence |

## Result

- **0 of 13** family-only names is loaded by a source outside the family. Every non-family
  occurrence of these names is a literal that is compared or printed -- a name census reports zero
  readers and that is a fact about writers.
- **13 of 13** names are read anyway, by **five** directory censuses that never name the file:

| reader | faces | takes | evidence |
|---|---|---|---|
| `scripts/e298_replay_control_census.py` | 13 | measures_shape | `glob.join(outdir, "*.json")` then "control containers and leaf witnesses" |
| `scripts/e302_universe_switch_backfill.py` | 13 | **carries** | `row["published_verdict"] = face.get("verdict")` |
| `scripts/e307_undated_face_vintage.py` | 13 | envelope_only | `vintage._parse(face.get("generated"))` |
| `scripts/e317_print_coverage_census.py` | 13 | measures_shape | `os.walk(RESULTS)` + `all_leaves` |
| `scripts/e319_census_self_inclusion_sweep.py` | 13 | declarations | `study = doc["study"]`, declared lists |

- **5 further sweepers** enumerate `results/**` and load JSON (`Tool/_r788bmc_w17_freeze_facts`,
  `scripts/attrition_ledger_guard`, `scripts/e340_...`, `scripts/e97_routing`,
  `scripts/wild_route_lab`). They read these faces by construction; what they take lives inside
  their own filters, so they are listed and **not classed** rather than guessed at.
- Verdict: `no_source_outside_the_family_names_these_faces_but_five_directory_censuses_read_every_published_face_and_one_of_them_carries_a_published_verdict_forward`.

## Population drift, published rather than absorbed

E341's fifteen names were taken at `444d3be`; this census is at `90c1fa8`. Two names left the list
because a source outside the family now *mentions* them (E341 spells stems in its own selftest);
neither is loaded. The face publishes both counts (`drift_vs_e341`), because reporting "13 names"
alone would silently swap one study's population for another's.

## Defects caught in this study's own drafts

1. **`fnmatch` is not path-aware.** `results/*.json` matched `results/state_tilt/X.json`, so six
   top-level sweepers were counted as face readers. Replaced with a segment-wise matcher (`**`
   allowed to skip directories; bare patterns matched against the filename only).
2. **One pass of constant folding drops `GLOB = PREFIX + "*"`.** The prefix-filtered censuses were
   then reported as `*` sweeps. Folding now repeats until nothing new resolves.
3. **`os.path.join(ROOT, "results", "state_tilt")` resolved to nothing**, because `ROOT` is a
   runtime path -- and that is why the first burn found **zero** directory readers. The trailing
   components are what name the directory.
4. **`int(summary.get(k) or -1)` is not a missing-value guard when 0 is legal** (E341's lesson,
   repeated in this study's own leg: an outside-loader count of 0 read as -1).

## Limits (published in the face)

- The class per reader is a **cited** row (quoted code re-checked at the pin), not a dataflow proof.
- A census that enumerates `results` and filters *after* loading is admitted here; that is the
  reading its own docstring takes.
- `measurement_keys_named` (the key-name overlap) is a coarse signal and is published beside the
  class, not instead of it: a reader that names `verdict` for an unrelated purpose shows 1+.