# E422 — the bare-basename defect is one census of four, and it costs no row

Round r1440, bm-b. Card `E422-WHICH-OTHER-CENSUS-RECORDS-A-BARE-BASENAME`.
Face `results/state_tilt/BASENAMECENSUS-2026-11-03.json` (+`basenamecensus_latest.json`).

## The question, and why it was worth asking

E421 ended on a mechanism: E406 recorded 32 of its 33 unresolved names as a bare basename with no
directory, and a bare basename cannot resolve to a file. That makes the defect look structural —
something about how this firm's censuses write down a face — so the next question is whether the
other basename-keyed censuses do the same, and whether rejoining a directory puts any row back.

## The reading

276 rows across four censuses. 70 carry a bare name (E402 52 + E404 18); 206 spell a directory
(E409 2 + E411 204). Exactly one census stores a bare name with no directory anywhere in the row —
**E402, 52 of 52**, 12 of them with no directory field at all. Rejoining changes **0 rows**:

| measurement | rows |
|---|---|
| bare names the python corpus spells a directory for | 55 |
| ... with a literal head (a place on disk) | 7 |
| ... whose join exists | 0 |
| bare names that exist anywhere in the repo | 0 |
| **rows whose published reading changes if rejoined** | **0** |

So the E402 names are design names, selftest fixtures, and pieces of computed names — not faces the
tree lost. The defect E421 found is real but not systemic, and where it does exist it costs nothing.

The control arm is what turns the zero into a measurement: the same instrument applied to the 206
path-spelled rows finds 189 whose file is on disk. A blind instrument would report 0 there too.

## Incidental, published not counted

11 of E404's 18 rows put a **file path** in a field named `resolved_directory`. A reader that joins
the field with the row's name composes `<face>.json/<face>.json` — 11 of 11 would double the name,
and 0 of those joins exist. That is a semantic defect in a field name, not a missing face, so it is
published as `incidental.named_directory_field_holding_a_file_path` and seeded as card E423.

## Pits

1. A directory is spelled as `join()` arguments as often as it is spelled as one literal. The first
   burn read only `'results/sample/x.json'` and missed `os.path.join('results','sample','x.json')`;
   the join-chain walk is what makes 55 spellings visible where the literal-only reading saw 4.
2. A spelling with a variable head is not a place on disk: 48 of 55 name a fixture base
   (`fx/results/grid_paper`). Published as its own column so "55 rows have a directory" is not read
   as 55 resolvable locations.
3. Parse the corpus **once**. A per-name `ast.parse` over 2.5k modules was killed at 5 minutes; the
   one-pass index costs 18 s for the whole study (E419's `get_source_segment` lesson, same shape).
4. Growing the corpus moved two pinned summaries in this window — E421's and E419's — which is
   E420's law for the third time. Both producers were re-derived rather than the assertions
   loosened, and this study's own leg compares everything except the three corpus-count keys; those
   are re-derived from the row list carried inside the same face instead of from the live tree.
5. A parameter that shadows a module function (`repo_index`) fails only on the real run, not in the
   selftest, because the selftest passes the argument in. The rename to `repo_file_index` is why the
   first real burn was a `TypeError` and not a wrong number.

## Delivered

`scripts/e422_basename_census_audit.py` (run / verify problems=0 / selftest 16/16) →
`results/state_tilt/BASENAMECENSUS-2026-11-03.json` + `basenamecensus_latest.json`; smoke leg
`# E422 (r1440 bm-b)` 1/1, proved red on a doctored summary and then restored; S6 leg
`basename_census` rc=0 (18.4 s); card E422 in `knowledge/METHODOLOGY_ASSETS.md`; pool E422 done with
`result_ref`, E423 seeded. Read-only: no census, face or reader edited.